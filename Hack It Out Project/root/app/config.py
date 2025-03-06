import os
from pathlib import Path
from typing import Dict, Any, List

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    ENV: str = Field(default="development", env="ENV")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Renewable Energy Forecasting API"
    PROJECT_DESCRIPTION: str = """
    AI-Powered Renewable Energy Forecasting system that predicts solar and wind energy generation 
    using historical weather data and machine learning models.
    """
    PROJECT_VERSION: str = "1.0.0"
    
    SECRET_KEY: str = Field(default="", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_URL: str = Field(default="sqlite:///./test.db", env="DATABASE_URL")
    
    MODEL_PATH: str = Field(default="./ml/training/model.pkl", env="MODEL_PATH")
    SOLAR_MODEL_PATH: str = Field(default="./ml/training/solar_model.pkl", env="SOLAR_MODEL_PATH")
    WIND_MODEL_PATH: str = Field(default="./ml/training/wind_model.pkl", env="WIND_MODEL_PATH")
    MODEL_VERSION: str = "1.0.0"
    
    WEATHER_API_KEY: str = Field(default="9083e4e505edc6666408d03c835134f8", env="WEATHER_API_KEY")
    WEATHER_API_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    WEATHER_API_TIMEOUT: int = 10
    
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    CACHE_TTL: int = 3600
    
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    SOLAR_FEATURES: List[str] = [
        "temperature", 
        "cloud_cover", 
        "solar_radiation", 
        "day_length", 
        "precipitation"
    ]
    
    WIND_FEATURES: List[str] = [
        "wind_speed", 
        "wind_direction", 
        "pressure", 
        "temperature", 
        "humidity"
    ]
    
    WORKERS_COUNT: int = Field(default=4, env="WORKERS_COUNT")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    
    TRAINING_DATA_PATH: str = Field(default="./ml/data/raw", env="TRAINING_DATA_PATH")
    PROCESSED_DATA_PATH: str = Field(default="./ml/data/processed", env="PROCESSED_DATA_PATH")
    TRAIN_TEST_SPLIT: float = 0.2
    RANDOM_STATE: int = 42
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

ENV = settings.ENV
DEBUG = settings.DEBUG
API_V1_PREFIX = settings.API_V1_PREFIX
PROJECT_NAME = settings.PROJECT_NAME
PROJECT_DESCRIPTION = settings.PROJECT_DESCRIPTION
PROJECT_VERSION = settings.PROJECT_VERSION
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
DATABASE_URL = settings.DATABASE_URL
MODEL_PATH = settings.MODEL_PATH
SOLAR_MODEL_PATH = settings.SOLAR_MODEL_PATH
WIND_MODEL_PATH = settings.WIND_MODEL_PATH
MODEL_VERSION = settings.MODEL_VERSION
WEATHER_API_KEY = settings.WEATHER_API_KEY
WEATHER_API_BASE_URL = settings.WEATHER_API_BASE_URL
WEATHER_API_TIMEOUT = settings.WEATHER_API_TIMEOUT
REDIS_URL = settings.REDIS_URL
CACHE_TTL = settings.CACHE_TTL
LOG_LEVEL = settings.LOG_LEVEL
LOG_FORMAT = settings.LOG_FORMAT
SOLAR_FEATURES = settings.SOLAR_FEATURES
WIND_FEATURES = settings.WIND_FEATURES
WORKERS_COUNT = settings.WORKERS_COUNT
ENABLE_METRICS = settings.ENABLE_METRICS
RATE_LIMIT_ENABLED = settings.RATE_LIMIT_ENABLED
TRAINING_DATA_PATH = settings.TRAINING_DATA_PATH
PROCESSED_DATA_PATH = settings.PROCESSED_DATA_PATH
TRAIN_TEST_SPLIT = settings.TRAIN_TEST_SPLIT
RANDOM_STATE = settings.RANDOM_STATE

def get_settings() -> Dict[str, Any]:
    return settings.dict()