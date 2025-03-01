import logging
import requests
import math
import time
import asyncio
import aiohttp
import random
from typing import Dict, Any, Optional, List, Tuple, Union, Callable, TypeVar, Generic, cast
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from pydantic import BaseModel, Field, validator, root_validator
from contextlib import asynccontextmanager

from ..config import get_settings
from ..exceptions import (
    WeatherAPIException, 
    LocationNotFoundException, 
    RateLimitExceededException,
    ConfigurationException
)
from ..utils.geo import parse_coordinates, is_valid_coordinates

T = TypeVar('T')
logger = logging.getLogger("api.services.weather")

class Coordinates(BaseModel):
    lat: float
    lon: float

class LocationData(BaseModel):
    name: str
    country: str
    coordinates: Coordinates

class WeatherData(BaseModel):
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_direction: int
    clouds: int
    description: str
    icon: str
    timestamp: str
    location: LocationData

class ForecastData(BaseModel):
    timestamp: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_direction: int
    clouds: int
    description: str
    icon: str

class WeatherProvider(BaseModel):
    name: str
    base_url: str
    api_key_param: str = "appid"
    units_param: str = "units"
    units_value: str = "metric"
    rate_limit: int = 60
    timeout: int = 10
    priority: int = 1
    enabled: bool = True
    
    class Config:
        arbitrary_types_allowed = True
        
    @root_validator
    def validate_provider(cls, values):
        if not values.get("name") or not values.get("base_url"):
            raise ValueError("Provider must have a name and base URL")
        return values

class CacheEntry(BaseModel, Generic[T]):
    data: T
    timestamp: float
    ttl: int = 300
    
    def is_valid(self) -> bool:
        return time.time() - self.timestamp < self.ttl

class WeatherService:
    def __init__(self):
        self.settings = get_settings()
        self._lock = asyncio.Lock()
        self._request_cache: Dict[str, CacheEntry] = {}
        self._request_timestamps: List[float] = []
        self._session: Optional[aiohttp.ClientSession] = None
        self._retry_strategy = self._exponential_backoff
        self._providers = self._initialize_providers()
        
    def _initialize_providers(self) -> List[WeatherProvider]:
        providers = []
        
        if hasattr(self.settings, 'WEATHER_API_KEY') and self.settings.WEATHER_API_KEY:
            providers.append(
                WeatherProvider(
                    name="openweathermap",
                    base_url=self.settings.WEATHER_API_BASE_URL,
                    api_key_param="appid",
                    units_param="units",
                    units_value="metric",
                    rate_limit=60,
                    timeout=self.settings.WEATHER_API_TIMEOUT,
                    priority=1,
                    enabled=True
                )
            )
        
        if hasattr(self.settings, 'WEATHERBIT_API_KEY') and self.settings.WEATHERBIT_API_KEY:
            providers.append(
                WeatherProvider(
                    name="weatherbit",
                    base_url="https://api.weatherbit.io/v2.0",
                    api_key_param="key",
                    units_param="units",
                    units_value="M",
                    rate_limit=45,
                    timeout=15,
                    priority=2,
                    enabled=True
                )
            )
        
        enabled_providers = sorted([p for p in providers if p.enabled], key=lambda p: p.priority)
        
        if not enabled_providers:
            raise ConfigurationException(
                detail="No weather providers are enabled",
                config_key="WEATHER_API_KEY"
            )
            
        return enabled_providers

    @asynccontextmanager
    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": "RenewableEnergyForecastAPI/1.0.0"}
            )
        try:
            yield self._session
        finally:
            pass

    async def close_session(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    def _enforce_rate_limit(self) -> None:
        current_time = time.time()
        self._request_timestamps = [ts for ts in self._request_timestamps 
                                  if current_time - ts < 60]
        
        if len(self._request_timestamps) >= self.settings.API_RATE_LIMIT_REQUESTS:
            oldest_request = min(self._request_timestamps)
            retry_after = int(60 - (current_time - oldest_request))
            raise RateLimitExceededException(
                retry_after=retry_after,
                limit=self.settings.API_RATE_LIMIT_REQUESTS,
                current=len(self._request_timestamps)
            )

    async def get_weather_data(self, location: str, use_cache: bool = True) -> WeatherData:
        cache_key = f"weather_{location}"
        
        if use_cache and cache_key in self._request_cache:
            cache_entry = cast(CacheEntry[WeatherData], self._request_cache[cache_key])
            if cache_entry.is_valid():
                return cache_entry.data

        async with self._lock:
            self._enforce_rate_limit()
            self._request_timestamps.append(time.time())
        
        last_error = None
        
        async with self._get_session() as session:
            for provider in self._providers:
                try:
                    data = await self._fetch_weather_data(session, provider, location)
                    if use_cache:
                        self._request_cache[cache_key] = CacheEntry(
                            data=data,
                            timestamp=time.time(),
                            ttl=300
                        )
                    return data
                except LocationNotFoundException:
                    raise
                except Exception as e:
                    last_error = e
                    continue

        raise WeatherAPIException(
            detail="All weather providers failed",
            error_details={"location": location, "last_error": str(last_error)}
        )

    async def _fetch_weather_data(
        self, 
        session: aiohttp.ClientSession,
        provider: WeatherProvider,
        location: str
    ) -> WeatherData:
        url = f"{provider.base_url}/weather"
        params = {
            provider.api_key_param: self._get_api_key(provider.name),
            provider.units_param: provider.units_value,
        }
        
        if is_valid_coordinates(location):
            lat, lon = parse_coordinates(location)
            params["lat"] = lat
            params["lon"] = lon
        else:
            params["q"] = location

        for attempt in range(3):
            try:
                async with session.get(url, params=params, timeout=provider.timeout) as response:
                    if response.status == 404:
                        raise LocationNotFoundException(location=location)
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        raise RateLimitExceededException(retry_after=retry_after)
                    
                    response.raise_for_status()
                    data = await response.json()
                    return self._transform_weather_data(data)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == 2:
                    raise
                await self._retry_strategy(attempt)

    def _transform_weather_data(self, data: Dict[str, Any]) -> WeatherData:
        try:
            return WeatherData(
                temperature=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                humidity=data["main"]["humidity"],
                pressure=data["main"]["pressure"],
                wind_speed=data["wind"]["speed"],
                wind_direction=data["wind"].get("deg", 0),
                clouds=data["clouds"]["all"],
                description=data["weather"][0]["description"],
                icon=data["weather"][0]["icon"],
                timestamp=datetime.fromtimestamp(data["dt"]).isoformat(),
                location=LocationData(
                    name=data["name"],
                    country=data["sys"]["country"],
                    coordinates=Coordinates(
                        lat=data["coord"]["lat"],
                        lon=data["coord"]["lon"]
                    )
                )
            )
        except KeyError as e:
            raise WeatherAPIException(
                detail="Invalid weather data format",
                error_details={"missing_field": str(e)}
            )

    async def get_forecast(self, location: str, days: int = 5, use_cache: bool = True) -> List[ForecastData]:
        cache_key = f"forecast_{location}_{days}"
        
        if use_cache and cache_key in self._request_cache:
            cache_entry = cast(CacheEntry[List[ForecastData]], self._request_cache[cache_key])
            if cache_entry.is_valid():
                return cache_entry.data

        async with self._lock:
            self._enforce_rate_limit()
            self._request_timestamps.append(time.time())
        
        last_error = None
        
        async with self._get_session() as session:
            for provider in self._providers:
                try:
                    data = await self._fetch_forecast_data(session, provider, location, days)
                    if use_cache:
                        self._request_cache[cache_key] = CacheEntry(
                            data=data,
                            timestamp=time.time(),
                            ttl=1800  # 30 minutes for forecast data
                        )
                    return data
                except LocationNotFoundException:
                    raise
                except Exception as e:
                    last_error = e
                    continue

        raise WeatherAPIException(
            detail="All weather providers failed to fetch forecast",
            error_details={"location": location, "last_error": str(last_error)}
        )

    async def _fetch_forecast_data(
        self,
        session: aiohttp.ClientSession,
        provider: WeatherProvider,
        location: str,
        days: int
    ) -> List[ForecastData]:
        url = f"{provider.base_url}/forecast"
        params = {
            provider.api_key_param: self._get_api_key(provider.name),
            provider.units_param: provider.units_value,
            "cnt": min(days * 8, 40)  # 8 forecasts per day, max 5 days (40 timestamps)
        }
        
        if is_valid_coordinates(location):
            lat, lon = parse_coordinates(location)
            params["lat"] = lat
            params["lon"] = lon
        else:
            params["q"] = location

        for attempt in range(3):
            try:
                async with session.get(url, params=params, timeout=provider.timeout) as response:
                    if response.status == 404:
                        raise LocationNotFoundException(location=location)
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        raise RateLimitExceededException(retry_after=retry_after)
                    
                    response.raise_for_status()
                    data = await response.json()
                    return self._transform_forecast_data(data)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == 2:
                    raise
                await self._retry_strategy(attempt)

    def _transform_forecast_data(self, data: Dict[str, Any]) -> List[ForecastData]:
        try:
            forecast_items = []
            for item in data.get("list", []):
                forecast_items.append(ForecastData(
                    timestamp=datetime.fromtimestamp(item["dt"]).isoformat(),
                    temperature=item["main"]["temp"],
                    feels_like=item["main"]["feels_like"],
                    humidity=item["main"]["humidity"],
                    pressure=item["main"]["pressure"],
                    wind_speed=item["wind"]["speed"],
                    wind_direction=item["wind"].get("deg", 0),
                    clouds=item["clouds"]["all"],
                    description=item["weather"][0]["description"],
                    icon=item["weather"][0]["icon"]
                ))
            return forecast_items
        except KeyError as e:
            raise WeatherAPIException(
                detail="Invalid forecast data format",
                error_details={"missing_field": str(e)}
            )

    def _get_api_key(self, provider_name: str) -> str:
        if provider_name == "openweathermap":
            if not hasattr(self.settings, 'WEATHER_API_KEY') or not self.settings.WEATHER_API_KEY:
                raise ConfigurationException(
                    detail="OpenWeatherMap API key is not configured",
                    config_key="WEATHER_API_KEY"
                )
            return self.settings.WEATHER_API_KEY
        elif provider_name == "weatherbit":
            if not hasattr(self.settings, 'WEATHERBIT_API_KEY') or not self.settings.WEATHERBIT_API_KEY:
                raise ConfigurationException(
                    detail="Weatherbit API key is not configured",
                    config_key="WEATHERBIT_API_KEY"
                )
            return self.settings.WEATHERBIT_API_KEY
        raise ConfigurationException(
            detail=f"No API key configured for provider: {provider_name}"
        )

    async def _exponential_backoff(self, attempt: int) -> None:
        delay = min(300, (2 ** attempt) + random.uniform(0, 1))
        await asyncio.sleep(delay)

    @lru_cache(maxsize=128)
    def get_cached_locations(self) -> List[str]:
        return [k.split('_', 1)[1] for k in self._request_cache.keys() if k.startswith('weather_')]

    def invalidate_cache(self, pattern: Optional[str] = None) -> int:
        if pattern is None:
            count = len(self._request_cache)
            self._request_cache.clear()
            return count
            
        keys_to_remove = [k for k in self._request_cache.keys() if pattern in k]
        for k in keys_to_remove:
            del self._request_cache[k]
        return len(keys_to_remove)

    def get_cache_stats(self) -> Dict[str, Any]:
        current_time = time.time()
        valid_entries = [k for k, v in self._request_cache.items() 
                        if current_time - v.timestamp < v.ttl]
                        
        return {
            "total_entries": len(self._request_cache),
            "valid_entries": len(valid_entries),
            "providers": [p.name for p in self._providers],
            "entries": list(self._request_cache.keys())
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()