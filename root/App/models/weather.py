from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
from .base import APIModel, TimestampMixin
from .location import Location

class WeatherSource(str, Enum):
    """Enumeration of supported weather data sources."""
    OPEN_WEATHER = "open_weather"
    WEATHER_API = "weather_api"
    NOAA = "noaa"
    ECMWF = "ecmwf"
    DARK_SKY = "dark_sky"
    METEOMATICS = "meteomatics"
    CUSTOM = "custom"

class WeatherUnit(str, Enum):
    """Enumeration of supported measurement units."""
    METRIC = "metric"  # Celsius, meters, etc.
    IMPERIAL = "imperial"  # Fahrenheit, miles, etc.
    STANDARD = "standard"  # Kelvin, meters, etc.

class WeatherCondition(str, Enum):
    """Enumeration of weather conditions."""
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    OVERCAST = "overcast"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"
    SLEET = "sleet"
    FOG = "fog"
    HAZE = "haze"
    DUST = "dust"
    SMOKE = "smoke"
    TORNADO = "tornado"
    HURRICANE = "hurricane"
    UNKNOWN = "unknown"

class WindDirection(str, Enum):
    """Enumeration of wind directions."""
    N = "N"
    NNE = "NNE"
    NE = "NE"
    ENE = "ENE"
    E = "E"
    ESE = "ESE"
    SE = "SE"
    SSE = "SSE"
    S = "S"
    SSW = "SSW"
    SW = "SW"
    WSW = "WSW"
    W = "W"
    WNW = "WNW"
    NW = "NW"
    NNW = "NNW"

class WeatherParameters(BaseModel):
    """Model representing weather parameters."""
    temperature: float = Field(..., description="Temperature in the specified unit")
    feels_like: Optional[float] = Field(None, description="'Feels like' temperature in the specified unit")
    humidity: Optional[float] = Field(None, description="Relative humidity in percentage", ge=0, le=100)
    pressure: Optional[float] = Field(None, description="Atmospheric pressure in hPa")
    wind_speed: Optional[float] = Field(None, description="Wind speed in the specified unit")
    wind_direction: Optional[Union[float, WindDirection]] = Field(
        None, description="Wind direction in degrees (0-360) or as a cardinal direction"
    )
    wind_gust: Optional[float] = Field(None, description="Wind gust speed in the specified unit")
    cloud_cover: Optional[float] = Field(None, description="Cloud cover percentage", ge=0, le=100)
    visibility: Optional[float] = Field(None, description="Visibility distance in the specified unit")
    precipitation: Optional[float] = Field(None, description="Precipitation amount in mm")
    precipitation_probability: Optional[float] = Field(
        None, description="Probability of precipitation in percentage", ge=0, le=100
    )
    uv_index: Optional[float] = Field(None, description="UV index")
    condition: Optional[WeatherCondition] = Field(None, description="Weather condition")
    condition_description: Optional[str] = Field(None, description="Detailed description of weather condition")
    condition_icon: Optional[str] = Field(None, description="Icon code for the weather condition")

    @validator('wind_direction')
    def validate_wind_direction(cls, v):
        if isinstance(v, float) and (v < 0 or v > 360):
            raise ValueError("Wind direction in degrees must be between 0 and 360")
        return v

    class Config:
        schema_extra = {
            "example": {
                "temperature": 22.5,
                "feels_like": 23.2,
                "humidity": 65,
                "pressure": 1013.2,
                "wind_speed": 5.7,
                "wind_direction": "NW",
                "wind_gust": 8.2,
                "cloud_cover": 25,
                "visibility": 10000,
                "precipitation": 0,
                "precipitation_probability": 10,
                "uv_index": 5.2,
                "condition": "partly_cloudy",
                "condition_description": "Partly cloudy skies",
                "condition_icon": "partly_cloudy_day"
            }
        }

class WeatherData(APIModel, TimestampMixin):
    """Model representing weather data for a specific location and time."""
    location: Location = Field(..., description="Location for which the weather data is provided")
    timestamp: datetime = Field(..., description="Timestamp of the weather data")
    source: WeatherSource = Field(..., description="Source of the weather data")
    unit: WeatherUnit = Field(WeatherUnit.METRIC, description="Unit system used for measurements")
    parameters: WeatherParameters = Field(..., description="Weather parameters")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw data from the weather provider")

    class Config:
        schema_extra = {
            "example": {
                "id": "weather-sf-20230615-120000",
                "location": {
                    "coordinates": {
                        "latitude": 37.7749,
                        "longitude": -122.4194
                    },
                    "name": "San Francisco",
                    "country": "US",
                    "region": "California",
                    "city": "San Francisco",
                    "timezone": "America/Los_Angeles"
                },
                "timestamp": "2023-06-15T12:00:00Z",
                "source": "open_weather",
                "unit": "metric",
                "parameters": {
                    "temperature": 22.5,
                    "feels_like": 23.2,
                    "humidity": 65,
                    "pressure": 1013.2,
                    "wind_speed": 5.7,
                    "wind_direction": "NW",
                    "cloud_cover": 25,
                    "condition": "partly_cloudy",
                    "condition_description": "Partly cloudy skies"
                },
                "created_at": "2023-06-15T12:05:00Z",
                "updated_at": "2023-06-15T12:05:00Z"
            }
        }

class WeatherAlert(APIModel, TimestampMixin):
    """Model representing a weather alert or warning."""
    location: Location = Field(..., description="Location for which the alert is issued")
    source: WeatherSource = Field(..., description="Source of the weather alert")
    alert_type: str = Field(..., description="Type of alert (e.g., 'flood', 'storm', 'heat')")
    severity: Literal["minor", "moderate", "severe", "extreme"] = Field(
        ..., description="Severity level of the alert"
    )
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Detailed description of the alert")
    start_time: datetime = Field(..., description="Start time of the alert period")
    end_time: datetime = Field(..., description="End time of the alert period")
    instructions: Optional[str] = Field(None, description="Safety instructions or recommendations")
    url: Optional[str] = Field(None, description="URL for more information about the alert")

    @root_validator
    def validate_time_period(cls, values):
        start_time = values.get('start_time')
        end_time = values.get('end_time')
        if start_time and end_time and end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        return values

    class Config:
        schema_extra = {
            "example": {
                "id": "alert-sf-20230615-heat",
                "location": {
                    "coordinates": {
                        "latitude": 37.7749,
                        "longitude": -122.4194
                    },
                    "name": "San Francisco",
                    "country": "US",
                    "region": "California"
                },
                "source": "noaa",
                "alert_type": "heat",
                "severity": "moderate",
                "title": "Heat Advisory",
                "description": "Heat advisory in effect from 11 AM to 8 PM PDT",
                "start_time": "2023-06-15T11:00:00-07:00",
                "end_time": "2023-06-15T20:00:00-07:00",
                "instructions": "Drink plenty of fluids, stay in an air-conditioned room, stay out of the sun.",
                "url": "https://alerts.weather.gov/123456",
                "created_at": "2023-06-14T18:30:00Z",
                "updated_at": "2023-06-14T18:30:00Z"
            }
        }

class WeatherForecast(APIModel, TimestampMixin):
    """Model representing a weather forecast for a specific location and time period."""
    location: Location = Field(..., description="Location for which the forecast is provided")
    source: WeatherSource = Field(..., description="Source of the forecast data")
    unit: WeatherUnit = Field(WeatherUnit.METRIC, description="Unit system used for measurements")
    forecast_time: datetime = Field(..., description="Time when the forecast was generated")
    forecast_period: Literal["hourly", "daily", "weekly", "monthly"] = Field(
        ..., description="Forecast period type"
    )
    forecasts: List[Dict[str, Any]] = Field(..., description="List of forecast data points")
    alerts: Optional[List[WeatherAlert]] = Field(None, description="Weather alerts associated with this forecast")

    @validator('forecasts')
    def validate_forecasts(cls, v, values):
        if not v:
            raise ValueError("Forecasts list cannot be empty")

        # Validate structure based on forecast_period
        forecast_period = values.get('forecast_period')
        if forecast_period:
            for forecast in v:
                # Common required fields
                if 'timestamp' not in forecast:
                    raise ValueError("Each forecast must have a timestamp")
                if 'parameters' not in forecast:
                    raise ValueError("Each forecast must have parameters")

                # Period-specific validation could be added here
        return v

    class Config:
        schema_extra = {
            "example": {
                "id": "forecast-sf-20230615",
                "location": {
                    "coordinates": {
                        "latitude": 37.7749,
                        "longitude": -122.4194
                    },
                    "name": "San Francisco",
                    "country": "US"
                },
                "source": "open_weather",
                "unit": "metric",
                "forecast_time": "2023-06-15T06:00:00Z",
                "forecast_period": "daily",
                "forecasts": [
                    {
                        "timestamp": "2023-06-15T12:00:00Z",
                        "parameters": {
                            "temperature": 22.5,
                            "humidity": 65,
                            "wind_speed": 5.7,
                            "condition": "partly_cloudy"
                        }
                    },
                    {
                        "timestamp": "2023-06-16T12:00:00Z",
                        "parameters": {
                            "temperature": 24.1,
                            "humidity": 60,
                            "wind_speed": 4.2,
                            "condition": "clear"
                        }
                    }
                ],
                "created_at": "2023-06-15T06:05:00Z",
                "updated_at": "2023-06-15T06:05:00Z"
            }
        }
