import os
import joblib
import logging
import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List, Union, Tuple, Callable, ContextManager
from datetime import datetime, timedelta
from pathlib import Path
from pydantic import BaseModel, Field, validator
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import threading
from contextlib import nullcontext
import torch
import warnings

# Correct scikit-learn imports
from sklearn.base import BaseEstimator
from sklearn.exceptions import NotFittedError
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

logger = logging.getLogger(__name__)
class ModelFeatures(BaseModel):
    """Expected features for the energy forecasting model with validation."""
    temperature: float = Field(..., ge=-50, le=60, description="Temperature in Celsius")
    wind_speed: float = Field(..., ge=0, le=100, description="Wind speed in meters/second")
    wind_direction: float = Field(..., ge=0, le=360, description="Wind direction in degrees")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity percentage")
    pressure: float = Field(..., ge=800, le=1200, description="Atmospheric pressure in hPa")
    cloud_cover: float = Field(..., ge=0, le=100, description="Cloud coverage percentage")
    solar_radiation: float = Field(..., ge=0, le=1400, description="Solar radiation in W/m²")
    
    @validator('wind_direction')
    def normalize_wind_direction(cls, v):
        """Normalize wind direction to 0-360 range."""
        return v % 360
    
    class Config:
        frozen = True

class ModelPrediction(BaseModel):
    """Enhanced model prediction output with uncertainty estimates."""
    solar_output: float = Field(..., description="Predicted solar energy output in kWh")
    wind_output: float = Field(..., description="Predicted wind energy output in kWh")
    total_output: float = Field(..., description="Total predicted energy output in kWh")
    timestamp: datetime = Field(default_factory=datetime.now)
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence score")
    uncertainty: float = Field(..., ge=0, description="Prediction uncertainty estimate")
    prediction_interval: Tuple[float, float] = Field(..., description="95% prediction interval")

class ModelMetrics(BaseModel):
    """Model performance metrics."""
    mse: float
    rmse: float
    mae: float
    r2: float
    last_updated: datetime

class ModelService:
    """Advanced service for managing and using the energy forecasting model."""
    
    def __init__(
        self,
        model_path: Union[str, Path],
        scaler_path: Optional[Union[str, Path]] = None,
        cache_size: int = 1024,
        n_jobs: int = -1,
        use_gpu: bool = True,
        uncertainty_estimation: str = 'bootstrap'
    ):
        """
        Initialize the enhanced model service.
        
        Args:
            model_path: Path to the saved model file
            scaler_path: Optional path to the feature scaler
            cache_size: Size of the prediction cache
            n_jobs: Number of parallel jobs (-1 for all cores)
            use_gpu: Whether to use GPU acceleration if available
            uncertainty_estimation: Method for uncertainty estimation
                ('bootstrap', 'dropout', or 'ensemble')
        """
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path) if scaler_path else None
        self.model = None
        self.scaler = None
        self.feature_names = None
        self._prediction_cache = {}
        self._cache_size = cache_size
        self._cache_lock = threading.Lock()
        self._n_jobs = n_jobs if n_jobs > 0 else os.cpu_count()
        self._use_gpu = use_gpu and torch.cuda.is_available()
        self._uncertainty_method = uncertainty_estimation
        self._thread_pool = ThreadPoolExecutor(max_workers=self._n_jobs)
        self._metrics = None
        self._load_model()
        
    def _load_model(self) -> None:
        """Load and initialize the model with advanced setup."""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            logger.info(f"Loading model from {self.model_path}")
            self.model = joblib.load(self.model_path)
            
            # Load scaler if available
            if self.scaler_path and self.scaler_path.exists():
                logger.info(f"Loading scaler from {self.scaler_path}")
                self.scaler = joblib.load(self.scaler_path)
            
            # Get feature names and validate model
            self._validate_model()
            
            # Move model to GPU if available and requested
            if self._use_gpu and hasattr(self.model, 'to'):
                self.model = self.model.to('cuda')
            
            # Initialize metrics
            self._initialize_metrics()
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise RuntimeError(f"Failed to load model: {str(e)}")
    
    def _validate_model(self) -> None:
        """Validate model compatibility and requirements."""
        if not isinstance(self.model, BaseEstimator):
            raise ValueError("Model must be a scikit-learn compatible estimator")
            
        self.feature_names = getattr(self.model, 'feature_names_in_', None)
        if self.feature_names is None:
            warnings.warn("Model does not provide feature names")
    
    def _initialize_metrics(self) -> None:
        """Initialize or load model metrics."""
        metrics_path = self.model_path.parent / "model_metrics.json"
        if metrics_path.exists():
            metrics_dict = pd.read_json(metrics_path).to_dict('records')[0]
            self._metrics = ModelMetrics(**metrics_dict)
    
    @lru_cache(maxsize=1024)
    def _preprocess_features(self, features: ModelFeatures) -> np.ndarray:
        """Preprocess features with advanced validation and normalization."""
        feature_dict = features.dict()
        
        # Validate feature names if available
        if self.feature_names:
            if not all(name in feature_dict for name in self.feature_names):
                raise ValueError(f"Missing required features: {set(self.feature_names) - set(feature_dict.keys())}")
        
        # Convert to array and reshape
        feature_array = np.array([
            feature_dict[name] for name in self.feature_names or feature_dict.keys()
        ]).reshape(1, -1)
        
        # Apply scaling if available
        if self.scaler:
            feature_array = self.scaler.transform(feature_array)
        
        # Move to GPU if needed
        if self._use_gpu:
            feature_array = torch.tensor(feature_array, device='cuda')
        
        return feature_array
    
    def _estimate_uncertainty(self, features: np.ndarray) -> Tuple[float, Tuple[float, float]]:
        """
        Estimate prediction uncertainty using the specified method.
        
        Returns:
            Tuple of (uncertainty_score, prediction_interval)
        """
        if self._uncertainty_method == 'bootstrap':
            return self._bootstrap_uncertainty(features)
        elif self._uncertainty_method == 'dropout':
            return self._dropout_uncertainty(features)
        else:  # ensemble
            return self._ensemble_uncertainty(features)
    
    def predict(self, features: ModelFeatures) -> ModelPrediction:
        """Generate energy production predictions with uncertainty estimates."""
        if self.model is None:
            raise RuntimeError("Model is not loaded")
            
        try:
            # Preprocess features
            X = self._preprocess_features(features)
            
            # Generate predictions
            with torch.no_grad() if self._use_gpu else nullcontext():
                predictions = self.model.predict(X)
            
            # Get prediction probabilities and uncertainty
            confidence = self._get_prediction_confidence(X)
            uncertainty, pred_interval = self._estimate_uncertainty(X)
            
            # Convert predictions to float
            if self._use_gpu:
                predictions = predictions.cpu().numpy()
            
            # Unpack predictions
            solar_output, wind_output = predictions[0]
            
            return ModelPrediction(
                solar_output=float(solar_output),
                wind_output=float(wind_output),
                total_output=float(solar_output + wind_output),
                confidence=float(confidence),
                uncertainty=float(uncertainty),
                prediction_interval=pred_interval
            )
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise RuntimeError(f"Failed to generate prediction: {str(e)}")
    
    async def predict_batch(
        self,
        features_batch: List[ModelFeatures],
        batch_size: int = 32
    ) -> List[ModelPrediction]:
        """
        Generate predictions for multiple feature sets with batching.
        
        Args:
            features_batch: List of feature sets
            batch_size: Size of batches for processing
            
        Returns:
            List of predictions
        """
        predictions = []
        
        # Process in batches
        for i in range(0, len(features_batch), batch_size):
            batch = features_batch[i:i + batch_size]
            
            # Process batch in parallel
            futures = [
                self._thread_pool.submit(self.predict, features)
                for features in batch
            ]
            
            # Collect results
            for future in futures:
                try:
                    prediction = future.result()
                    predictions.append(prediction)
                except Exception as e:
                    logger.error(f"Batch prediction error: {str(e)}")
                    predictions.append(None)
        
        return predictions
    
    def get_model_metrics(self) -> ModelMetrics:
        """Get current model performance metrics."""
        if self._metrics is None:
            raise ValueError("Model metrics not available")
        return self._metrics
    
    def update_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> None:
        """Update model performance metrics with new data."""
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        mse = mean_squared_error(y_true, y_pred)
        self._metrics = ModelMetrics(
            mse=float(mse),
            rmse=float(np.sqrt(mse)),
            mae=float(mean_absolute_error(y_true, y_pred)),
            r2=float(r2_score(y_true, y_pred)),
            last_updated=datetime.now()
        )
        
        # Save metrics
        metrics_path = self.model_path.parent / "model_metrics.json"
        pd.DataFrame([self._metrics.dict()]).to_json(metrics_path)
    
    def __del__(self):
        """Cleanup resources."""
        self._thread_pool.shutdown(wait=True)

# Example usage
if __name__ == "__main__":
    # Initialize the service
    model_service = ModelService(
        model_path="models/energy_forecast_model.pkl",
        scaler_path="models/feature_scaler.pkl",
        use_gpu=True,
        uncertainty_estimation='bootstrap'
    )

    # Create features
    features = ModelFeatures(
        temperature=25.0,
        wind_speed=5.0,
        wind_direction=180.0,
        humidity=65.0,
        pressure=1013.0,
        cloud_cover=30.0,
        solar_radiation=800.0
    )

    # Get prediction
    prediction = model_service.predict(features)
    print(f"Predicted energy output: {prediction.total_output:.2f} kWh")
    print(f"Confidence: {prediction.confidence:.2%}")
    print(f"Uncertainty: ±{prediction.uncertainty:.2f} kWh")
    print(f"95% Prediction Interval: {prediction.prediction_interval}")

    # Get model metrics
    try:
        metrics = model_service.get_model_metrics()
        print(f"\nModel Performance Metrics:")
        print(f"RMSE: {metrics.rmse:.2f}")
        print(f"R²: {metrics.r2:.2f}")
        print(f"Last Updated: {metrics.last_updated}")
    except ValueError as e:
        print(f"Metrics not available: {e}")