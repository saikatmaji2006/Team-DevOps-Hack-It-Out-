from datetime import datetime
from typing import List, Dict, Optional, Union, Any
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator

from .base import APIModel, TimestampMixin


class EnergySource(str, Enum):
    """Enumeration of renewable energy sources."""
    SOLAR = "solar"
    WIND = "wind"
    HYDRO = "hydro"
    GEOTHERMAL = "geothermal"
    BIOMASS = "biomass"
    TIDAL = "tidal"
    COMBINED = "combined"


class EnergyUnit(str, Enum):
    """Enumeration of energy measurement units."""
    WATT_HOUR = "Wh"
    KILOWATT_HOUR = "kWh"
    MEGAWATT_HOUR = "MWh"
    GIGAWATT_HOUR = "GWh"
    JOULE = "J"
    KILOJOULE = "kJ"
    MEGAJOULE = "MJ"
    GIGAJOULE = "GJ"


class TrainingRequest(APIModel):
    """Model for requesting model training."""
    source: EnergySource = Field(..., description="Energy source type to train model for")
    location_id: Optional[str] = Field(None, description="Specific location ID to train for")
    start_date: Optional[datetime] = Field(None, description="Start date for training data")
    end_date: Optional[datetime] = Field(None, description="End date for training data")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional training parameters")
    force_retrain: bool = Field(False, description="Force retraining even if recent model exists")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validate that end_date is after start_date."""
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError("end_date must be after start_date")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "source": "solar",
                "location_id": "california-central",
                "start_date": "2022-01-01T00:00:00Z",
                "end_date": "2022-12-31T23:59:59Z",
                "parameters": {
                    "feature_selection": True,
                    "hyperparameter_tuning": True
                },
                "force_retrain": False
            }
        }


class TrainingStatus(str, Enum):
    """Enumeration of possible training statuses."""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TrainingResponse(APIModel, TimestampMixin):
    """Model for training response."""
    id: str = Field(..., description="Unique identifier for the training job")
    source: EnergySource = Field(..., description="Energy source type model is trained for")
    status: TrainingStatus = Field(..., description="Current status of the training job")
    progress: Optional[float] = Field(None, description="Training progress (0-100%)")
    started_at: Optional[datetime] = Field(None, description="When training started")
    completed_at: Optional[datetime] = Field(None, description="When training completed")
    model_version: Optional[str] = Field(None, description="Version of the trained model")
    metrics: Optional[Dict[str, float]] = Field(None, description="Training performance metrics")
    error_message: Optional[str] = Field(None, description="Error message if training failed")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "train-solar-20230615123456",
                "source": "solar",
                "status": "completed",
                "progress": 100.0,
                "started_at": "2023-06-15T12:30:00Z",
                "completed_at": "2023-06-15T13:45:00Z",
                "model_version": "solar-v1.2.3",
                "metrics": {
                    "mae": 0.15,
                    "rmse": 0.22,
                    "r2": 0.89
                },
                "error_message": None
            }
        }


class EnergyPrediction(APIModel):
    """Model representing an energy generation prediction."""
    source: EnergySource = Field(..., description="Energy source type")
    value: float = Field(..., description="Predicted energy generation value")
    unit: EnergyUnit = Field(..., description="Unit of measurement")
    confidence: Optional[float] = Field(None, description="Confidence level (0-1)")
    prediction_interval: Optional[List[float]] = Field(None, description="Prediction interval [lower, upper]")
    
    class Config:
        schema_extra = {
            "example": {
                "source": "solar",
                "value": 245.8,
                "unit": "kWh",
                "confidence": 0.92,
                "prediction_interval": [220.3, 271.2]
            }
        }


class SolarForecastRequest(APIModel):
    """Model for requesting solar energy forecasts."""
    location_id: str = Field(..., description="Location identifier")
    panel_capacity: float = Field(..., description="Solar panel capacity in kW")
    panel_efficiency: Optional[float] = Field(0.175, description="Solar panel efficiency (0-1)")
    panel_angle: Optional[float] = Field(None, description="Panel tilt angle in degrees")
    panel_azimuth: Optional[float] = Field(None, description="Panel azimuth angle in degrees")
    bypass_cache: bool = Field(False, description="Bypass cache and force new prediction")
    
    @validator('panel_efficiency')
    def validate_efficiency(cls, v):
        """Validate that efficiency is between 0 and 1."""
        if v <= 0 or v > 1:
            raise ValueError("panel_efficiency must be between 0 and 1")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "location_id": "california-central",
                "panel_capacity": 10.5,
                "panel_efficiency": 0.185,
                "panel_angle": 30,
                "panel_azimuth": 180,
                "bypass_cache": False
            }
        }


class WindForecastRequest(APIModel):
    """Model for requesting wind energy forecasts."""
    location_id: str = Field(..., description="Location identifier")
    turbine_capacity: float = Field(..., description="Wind turbine capacity in kW")
    hub_height: float = Field(..., description="Hub height in meters")
    rotor_diameter: float = Field(..., description="Rotor diameter in meters")
    cut_in_speed: Optional[float] = Field(3.5, description="Cut-in wind speed in m/s")
    cut_out_speed: Optional[float] = Field(25.0, description="Cut-out wind speed in m/s")
    rated_speed: Optional[float] = Field(12.0, description="Rated wind speed in m/s")
    bypass_cache: bool = Field(False, description="Bypass cache and force new prediction")
    
    class Config:
        schema_extra = {
            "example": {
                "location_id": "iowa-central",
                "turbine_capacity": 2000,
                "hub_height": 80,
                "rotor_diameter": 90,
                "cut_in_speed": 3.0,
                "cut_out_speed": 25.0,
                "rated_speed": 11.5,
                "bypass_cache": False
            }
        }


class EnergyForecastResponse(APIModel, TimestampMixin):
    """Base model for energy forecast responses."""
    location_id: str = Field(..., description="Location identifier")
    source: EnergySource = Field(..., description="Energy source type")
    prediction: EnergyPrediction = Field(..., description="Energy generation prediction")
    forecast_created_at: datetime = Field(default_factory=datetime.utcnow, description="When the forecast was created")
    forecast_period: str = Field(..., description="Forecast period (e.g., 'hourly', 'daily')")
    model_version: str = Field(..., description="Version of the model used for prediction")
    
    class Config:
        schema_extra = {
            "example": {
                "location_id": "california-central",
                "source": "solar",
                "prediction": {
                    "source": "solar",
                    "value": 245.8,
                    "unit": "kWh",
                    "confidence": 0.92,
                    "prediction_interval": [220.3, 271.2]
                },
                "forecast_created_at": "2023-06-15T12:30:00Z",
                "forecast_period": "daily",
                "model_version": "solar-v1.2.3"
            }
        }


class SolarForecastResponse(EnergyForecastResponse):
    """Model for solar energy forecast responses."""
    panel_details: Dict[str, Any] = Field(..., description="Details of the solar panel configuration")
    weather_factors: Dict[str, Any] = Field(..., description="Weather factors affecting the prediction")
    
    class Config:
        schema_extra = {
            "example": {
                "location_id": "california-central",
                "source": "solar",
                "prediction": {
                    "source": "solar",
                    "value": 245.8,
                    "unit": "kWh",
                    "confidence": 0.92,
                    "prediction_interval": [220.3, 271.2]
                },
                "forecast_created_at": "2023-06-15T12:30:00Z",
                "forecast_period": "daily",
                "model_version": "solar-v1.2.3",
                "panel_details": {
                    "capacity": 10.5,
                    "efficiency": 0.185,
                    "angle": 30,
                    "azimuth": 180
                },
                "weather_factors": {
                    "cloud_cover": 0.25,
                    "solar_radiation": 850,
                    "temperature": 28.5
                }
            }
        }


class WindForecastResponse(EnergyForecastResponse):
    """Model for wind energy forecast responses."""
    turbine_details: Dict[str, Any] = Field(..., description="Details of the wind turbine configuration")
    weather_factors: Dict[str, Any] = Field(..., description="Weather factors affecting the prediction")
    
    class Config:
        schema_extra = {
            "example": {
                "location_id": "iowa-central",
                "source": "wind",
                "prediction": {
                    "source": "wind",
                    "value": 1250.5,
                    "unit": "kWh",
                    "confidence": 0.88,
                    "prediction_interval": [1100.2, 1400.8]
                },
                "forecast_created_at": "2023-06-15T12:30:00Z",
                "forecast_period": "daily",
                "model_version": "wind-v2.1.0",
                "turbine_details": {
                    "capacity": 2000,
                    "hub_height": 80,
                    "rotor_diameter": 90
                },
                "weather_factors": {
                    "wind_speed": 8.5,
                    "wind_direction": 225,
                    "air_density": 1.225
                }
            }
        }


class HistoricalEnergyData(APIModel, TimestampMixin):
    """Model for historical energy generation data."""
    id: str = Field(..., description="Unique identifier for this data point")
    location_id: str = Field(..., description="Location identifier")
    source: EnergySource = Field(..., description="Energy source type")
    timestamp: datetime = Field(..., description="Time of the energy generation")
    value: float = Field(..., description="Actual energy generated")
    unit: EnergyUnit = Field(..., description="Unit of measurement")
    weather_conditions: Dict[str, Any] = Field(..., description="Weather conditions during generation")
    system_details: Dict[str, Any] = Field(..., description="Details of the energy system")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "hist-california-solar-20220615123000",
                "location_id": "california-central",
                "source": "solar",
                "timestamp": "2022-06-15T12:30:00Z",
                "value": 240.2,
                "unit": "kWh",
                "weather_conditions": {
                    "temperature": 29.5,
                    "cloud_cover": 0.15,
                    "solar_radiation": 900
                },
                "system_details": {
                    "panel_capacity": 10.5,
                    "panel_efficiency": 0.185,
                    "panel_age": 2.5
                }
            }
        }


class EnergySystemEfficiency(APIModel):
    """Model for energy system efficiency analysis."""
    system_id: str = Field(..., description="Unique identifier for the energy system")
    source: EnergySource = Field(..., description="Energy source type")
    efficiency: float = Field(..., description="Current system efficiency (0-1)")
    expected_efficiency: float = Field(..., description="Expected efficiency for system age and type")
    factors: Dict[str, float] = Field(..., description="Factors affecting efficiency")
    recommendations: List[str] = Field(..., description="Recommendations for improvement")
    
    class Config:
        schema_extra = {
            "example": {
                "system_id": "solar-system-123",
                "source": "solar",
                "efficiency": 0.165,
                "expected_efficiency": 0.180,
                "factors": {
                    "dust_accumulation": -0.015,
                    "panel_degradation": -0.005,
                    "shading": -0.010
                },
                "recommendations": [
                    "Clean solar panels to remove dust accumulation",
                    "Check for and remove new sources of shading",
                    "Inspect for damaged panels that may need replacement"
                ]
            }
        }