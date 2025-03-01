from functools import lru_cache
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, validator, SecretStr


class Settings(BaseSettings):
    APP_NAME: str = "Renewable Energy Forecasting API"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"
    
    REQUIRE_API_KEY: bool = True
    API_KEYS: List[str] = []
    API_RATE_LIMIT_REQUESTS: int = 100
    API_RATE_LIMIT_PERIOD: int = 60
    
    CORS_ORIGINS: List[str] = []
    
    MODEL_PATH: str = "model.pkl"
    SOLAR_MODEL_PATH: Optional[str] = None
    WIND_MODEL_PATH: Optional[str] = None
    COLLECT_TRAINING_DATA: bool = False
    TRAINING_DATA_PATH: str = "training_data.jsonl"
    MODEL_VERSION: str = "1.0.0"
    
    WEATHER_API_KEY: SecretStr
    WEATHER_API_BASE_URL: str = "http://api.openweathermap.org/data/2.5"
    WEATHER_API_TIMEOUT: int = 10
    WEATHER_API_RETRY_ATTEMPTS: int = 3
    WEATHER_API_RETRY_BACKOFF: float = 0.5
    
    ENABLE_CACHING: bool = True
    FORECAST_CACHE_TTL: int = 1800
    MAX_CACHE_SIZE: int = 1000
    CACHE_BACKEND: str = "memory"
    REDIS_URL: Optional[str] = None
    
    HEALTH_CHECK_ENABLED: bool = True
    HEALTH_CHECK_INCLUDE_DETAILS: bool = False
    
    ENABLE_METRICS: bool = True
    METRICS_PREFIX: str = "energy_forecast_"
    
    @validator('CORS_ORIGINS', pre=True)
    def validate_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith('['):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('ENVIRONMENT')
    def validate_environment(cls, v):
        allowed_environments = ['development', 'testing', 'staging', 'production']
        if v.lower() not in allowed_environments:
            raise ValueError(f"Environment must be one of {allowed_environments}")
        return v.lower()
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.upper()
    
    def get_weather_api_key(self) -> str:
        return self.WEATHER_API_KEY.get_secret_value()
    
    def get_redis_settings(self) -> Dict[str, Any]:
        if self.CACHE_BACKEND != "redis" or not self.REDIS_URL:
            return {}
        
        return {"url": self.REDIS_URL}
    
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()