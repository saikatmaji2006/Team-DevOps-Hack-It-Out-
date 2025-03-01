from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator


class WeatherData(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius")
    wind_speed: float = Field(..., description="Wind speed in meters/second")
    sunlight_intensity: float = Field(..., description="Sunlight intensity in W/m²")
    humidity: Optional[float] = Field(None, description="Humidity percentage")
    cloud_cover: Optional[float] = Field(None, description="Cloud cover percentage")
    precipitation: Optional[float] = Field(None, description="Precipitation in mm")
    pressure: Optional[float] = Field(None, description="Atmospheric pressure in hPa")
    
    @validator('temperature')
    def temperature_range(cls, v):
        if v < -100 or v > 100:
            raise ValueError("Temperature must be between -100 and 100 Celsius")
        return v
    
    @validator('wind_speed')
    def wind_speed_range(cls, v):
        if v < 0 or v > 200:
            raise ValueError("Wind speed must be between 0 and 200 m/s")
        return v
    
    @validator('sunlight_intensity')
    def sunlight_intensity_range(cls, v):
        if v < 0 or v > 1500:
            raise ValueError("Sunlight intensity must be between 0 and 1500 W/m²")
        return v


class ForecastRequest(BaseModel):
    location: str = Field(..., description="City name or location identifier")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    bypass_cache: bool = Field(False, description="Force fresh data instead of using cache")
    
    @validator('location')
    def location_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Location cannot be empty")
        return v.strip()
    
    @validator('latitude')
    def latitude_range(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError("Latitude must be between -90 and 90 degrees")
        return v
    
    @validator('longitude')
    def longitude_range(cls, v):
        if v is not None and (v < -180 or v > 180):
            raise ValueError("Longitude must be between -180 and 180 degrees")
        return v


class SolarForecastRequest(ForecastRequest):
    panel_capacity: Optional[float] = Field(None, description="Solar panel capacity in kW")
    panel_efficiency: Optional[float] = Field(None, description="Solar panel efficiency percentage")
    panel_angle: Optional[float] = Field(None, description="Solar panel tilt angle in degrees")
    
    @validator('panel_capacity')
    def panel_capacity_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Panel capacity must be positive")
        return v
    
    @validator('panel_efficiency')
    def panel_efficiency_range(cls, v):
        if v is not None and (v <= 0 or v > 100):
            raise ValueError("Panel efficiency must be between 0 and 100 percent")
        return v


class WindForecastRequest(ForecastRequest):
    turbine_height: Optional[float] = Field(None, description="Wind turbine height in meters")
    turbine_capacity: Optional[float] = Field(None, description="Wind turbine capacity in kW")
    turbine_cut_in_speed: Optional[float] = Field(None, description="Wind speed at which turbine starts generating power")
    turbine_cut_out_speed: Optional[float] = Field(None, description="Wind speed at which turbine stops for safety")
    
    @validator('turbine_height')
    def turbine_height_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Turbine height must be positive")
        return v
    
    @validator('turbine_capacity')
    def turbine_capacity_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Turbine capacity must be positive")
        return v


class ForecastResponse(BaseModel):
    location: str = Field(..., description="Location for which forecast was generated")
    weather: WeatherData = Field(..., description="Current weather data")
    predicted_energy_output: float = Field(..., description="Predicted energy output in kWh")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the forecast")
    model_version: Optional[str] = Field(None, description="Version of the model used for prediction")


class HourlyForecast(BaseModel):
    timestamp: str = Field(..., description="ISO format timestamp for the hourly forecast")
    total: float = Field(..., description="Total predicted energy output in kWh")
    solar: float = Field(..., description="Solar energy component in kWh")
    wind: float = Field(..., description="Wind energy component in kWh")


class DetailedForecastResponse(ForecastResponse):
    solar_output: float = Field(..., description="Solar energy component of total output")
    wind_output: float = Field(..., description="Wind energy component of total output")
    confidence_interval_lower: float = Field(..., description="Lower bound of confidence interval")
    confidence_interval_upper: float = Field(..., description="Upper bound of confidence interval")
    hourly_forecast: List[Union[HourlyForecast, Dict[str, Any]]] = Field(..., description="Hour-by-hour forecast")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp when the error occurred")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retrying (for rate limit errors)")


class CacheInfo(BaseModel):
    enabled: bool = Field(..., description="Whether caching is enabled")
    size: int = Field(..., description="Current number of items in cache")
    max_size: int = Field(..., description="Maximum cache size")
    ttl: int = Field(..., description="Time-to-live for cache items in seconds")
    hit_rate: float = Field(..., description="Cache hit rate (0.0-1.0)")