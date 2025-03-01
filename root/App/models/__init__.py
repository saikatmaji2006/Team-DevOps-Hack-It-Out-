"""
Models package for the ML Training API.

This package contains all the data models used throughout the application,
including request/response models, database models, and domain models.
"""

# Import models from base module
from .base import APIModel, TimestampMixin

# Import models from location module
from .location import Coordinates

# Import models from weather module
from .weather import (
    WeatherData,
    WeatherForecast,
    WeatherParameters,
    WeatherSource,
    WeatherAlert
)

# Import models from energy module
from .energy import (
    EnergySource,
    EnergyUnit,
    TrainingRequest,
    TrainingStatus,
    TrainingResponse,
    EnergyPrediction,
    SolarForecastRequest,
    WindForecastRequest,
    EnergyForecastResponse,
    SolarForecastResponse,
    WindForecastResponse,
    HistoricalEnergyData,
    EnergySystemEfficiency
)

# Import models from forecast module
from .forecast import (
    ForecastRequest,
    ForecastResponse,
    DetailedForecastResponse,
    ForecastPeriod,
    ForecastAccuracy
)

# Import models for error handling
from .errors import (
    ErrorResponse,
    ErrorDetail,
    ValidationError
)

# Import models for caching
from .cache import (
    CacheInfo,
    CacheItem,
    CacheStats
)

# Import models for authentication and authorization
from .auth import (
    User,
    Role,
    Permission,
    APIKey
)

# Export all models
__all__ = [
    # Base models
    'APIModel',
    'TimestampMixin',
    
    # Location models
    'Coordinates',
    
    # Weather models
    'WeatherData',
    'WeatherForecast',
    'WeatherParameters',
    'WeatherSource',
    'WeatherAlert',
    
    # Energy models
    'EnergySource',
    'EnergyUnit',
    'TrainingRequest',
    'TrainingStatus',
    'TrainingResponse',
    'EnergyPrediction',
    'SolarForecastRequest',
    'WindForecastRequest',
    'EnergyForecastResponse',
    'SolarForecastResponse',
    'WindForecastResponse',
    'HistoricalEnergyData',
    'EnergySystemEfficiency',
    
    # Forecast models
    'ForecastRequest',
    'ForecastResponse',
    'DetailedForecastResponse',
    'ForecastPeriod',
    'ForecastAccuracy',
    
    # Error models
    'ErrorResponse',
    'ErrorDetail',
    'ValidationError',
    
    # Cache models
    'CacheInfo',
    'CacheItem',
    'CacheStats',
    
    # Auth models
    'User',
    'Role',
    'Permission',
    'APIKey'
]