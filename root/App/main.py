import time
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, Header, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.status import HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS

from .config import get_settings, Settings
from .models import (
    ForecastRequest, 
    ForecastResponse, 
    DetailedForecastResponse,
    SolarForecastRequest,
    WindForecastRequest,
    ErrorResponse,
    CacheInfo
)
from .services.weather import WeatherService
from .services.model import ModelService
from .services.cache import CacheService
from .services.auth import validate_api_key
from .exceptions import (
    WeatherAPIException, 
    ModelException, 
    LocationNotFoundException,
    RateLimitExceededException
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api.log")
    ]
)
logger = logging.getLogger(__name__)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

RATE_LIMIT_DURATION = 60
RATE_LIMIT_REQUESTS = 30
rate_limit_store: Dict[str, List[float]] = {}


def create_application() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="API for predicting renewable energy generation based on weather data",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        responses={
            403: {"model": ErrorResponse, "description": "Forbidden - Invalid API Key"},
            429: {"model": ErrorResponse, "description": "Too Many Requests - Rate limit exceeded"},
            500: {"model": ErrorResponse, "description": "Internal Server Error"},
            503: {"model": ErrorResponse, "description": "Service Unavailable - Dependent service error"}
        }
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    @app.exception_handler(WeatherAPIException)
    async def weather_exception_handler(request: Request, exc: WeatherAPIException):
        logger.error(f"Weather API error: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "type": "weather_api_error"}
        )
    
    @app.exception_handler(ModelException)
    async def model_exception_handler(request: Request, exc: ModelException):
        logger.error(f"Model error: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "type": "model_error"}
        )
    
    @app.exception_handler(LocationNotFoundException)
    async def location_not_found_handler(request: Request, exc: LocationNotFoundException):
        logger.warning(f"Location not found: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "type": "location_not_found"}
        )
    
    @app.exception_handler(RateLimitExceededException)
    async def rate_limit_handler(request: Request, exc: RateLimitExceededException):
        return JSONResponse(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            content={"error": exc.detail, "type": "rate_limit_exceeded", "retry_after": exc.retry_after}
        )
    
    return app


app = create_application()
settings = get_settings()
weather_service = WeatherService()
model_service = ModelService()
cache_service = CacheService()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Processing Time: {process_time:.4f}s - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    return response


async def get_api_key(
    api_key: str = Depends(api_key_header),
    settings: Settings = Depends(get_settings)
) -> str:
    if settings.REQUIRE_API_KEY:
        if not api_key:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, 
                detail="API key is missing"
            )
        
        if not validate_api_key(api_key, settings):
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, 
                detail="Invalid API key"
            )
        
        now = time.time()
        if api_key not in rate_limit_store:
            rate_limit_store[api_key] = []
        
        rate_limit_store[api_key] = [
            ts for ts in rate_limit_store[api_key] 
            if now - ts < RATE_LIMIT_DURATION
        ]
        
        if len(rate_limit_store[api_key]) >= RATE_LIMIT_REQUESTS:
            oldest_timestamp = min(rate_limit_store[api_key])
            retry_after = int(RATE_LIMIT_DURATION - (now - oldest_timestamp))
            raise RateLimitExceededException(
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                retry_after=retry_after
            )
        
        rate_limit_store[api_key].append(now)
    
    return api_key


async def retrain_model_task(sample_data: Dict[str, Any]):
    logger.info("Starting model retraining task")
    try:
        await model_service.collect_training_sample(sample_data)
        logger.info("Model training sample collected successfully")
    except Exception as e:
        logger.error(f"Error in model retraining task: {str(e)}")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "description": "Advanced API for predicting renewable energy generation based on weather data",
        "endpoints": {
            "forecast": "/forecast",
            "forecast/solar": "/forecast/solar",
            "forecast/wind": "/forecast/wind",
            "docs": "/docs",
            "health": "/health",
            "cache/info": "/cache/info",
            "cache/clear": "/cache/clear"
        }
    }


@app.get("/health")
async def health_check(api_key: str = Depends(get_api_key)):
    weather_service_status = "healthy"
    try:
        weather_service.test_connection()
    except Exception as e:
        weather_service_status = f"unhealthy: {str(e)}"
    
    model_status = "healthy" if model_service.is_loaded else "unhealthy: model not loaded"
    
    cache_status = "healthy" if cache_service.is_available() else "unhealthy"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "healthy",
            "weather_service": weather_service_status,
            "model_service": model_status,
            "cache_service": cache_status
        },
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }


@app.post("/forecast", response_model=ForecastResponse)
async def get_forecast(
    request: ForecastRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
    settings: Settings = Depends(get_settings)
) -> ForecastResponse:
    cache_key = f"forecast:{request.location}"
    cached_result = cache_service.get(cache_key)
    
    if cached_result and not request.bypass_cache:
        logger.info(f"Cache hit for location: {request.location}")
        return ForecastResponse(**cached_result)
    
    weather_data = weather_service.get_weather_data(request.location)

    features = [
        [
            weather_data.temperature,
            weather_data.wind_speed,
            weather_data.sunlight_intensity
        ]
    ]

    prediction = model_service.predict(features)
    
    response = ForecastResponse(
        location=request.location,
        weather=weather_data,
        predicted_energy_output=float(prediction[0])
    )
    
    if settings.ENABLE_CACHING:
        cache_service.set(
            cache_key, 
            response.dict(), 
            ttl=settings.FORECAST_CACHE_TTL
        )
    
    if settings.COLLECT_TRAINING_DATA:
        background_tasks.add_task(
            retrain_model_task, 
            {
                "features": features[0],
                "location": request.location,
                "timestamp": datetime.now().isoformat(),
                "prediction": float(prediction[0])
            }
        )
    
    return response


@app.post("/forecast/detailed", response_model=DetailedForecastResponse)
async def get_detailed_forecast(
    request: ForecastRequest,
    api_key: str = Depends(get_api_key)
) -> DetailedForecastResponse:
    basic_forecast = await get_forecast(request, BackgroundTasks(), api_key)
    
    weather_data = basic_forecast.weather
    
    total_energy = basic_forecast.predicted_energy_output
    
    solar_factor = min(1.0, max(0.1, weather_data.sunlight_intensity / 1000))
    wind_factor = min(1.0, max(0.1, weather_data.wind_speed / 10))
    
    total_factor = solar_factor + wind_factor
    solar_normalized = solar_factor / total_factor
    wind_normalized = wind_factor / total_factor
    
    solar_output = total_energy * solar_normalized
    wind_output = total_energy * wind_normalized
    
    hourly_forecasts = []
    base_time = datetime.now().replace(minute=0, second=0, microsecond=0)
    
    for hour in range(24):
        forecast_time = base_time + timedelta(hours=hour)
        
        hour_of_day = forecast_time.hour
        
        if 6 <= hour_of_day <= 18:
            time_factor = 1.0 - abs(hour_of_day - 12) / 6
            adjusted_solar = solar_output * time_factor
        else:
            adjusted_solar = 0.0
        
        wind_variation = 0.8 + 0.4 * ((hour % 12) / 12)
        adjusted_wind = wind_output * wind_variation
        
        hourly_forecasts.append({
            "timestamp": forecast_time.isoformat(),
            "total": adjusted_solar + adjusted_wind,
            "solar": adjusted_solar,
            "wind": adjusted_wind
        })
    
    return DetailedForecastResponse(
        location=request.location,
        weather=weather_data,
        predicted_energy_output=total_energy,
        solar_output=solar_output,
        wind_output=wind_output,
        confidence_interval_lower=total_energy * 0.9,
        confidence_interval_upper=total_energy * 1.1,
        hourly_forecast=hourly_forecasts
    )


@app.post("/forecast/solar", response_model=ForecastResponse)
async def get_solar_forecast(
    request: SolarForecastRequest,
    api_key: str = Depends(get_api_key)
) -> ForecastResponse:
    weather_data = weather_service.get_weather_data(request.location)
    
    features = [
        [
            weather_data.temperature,
            0.0,  
            weather_data.sunlight_intensity
        ]
    ]
    
    prediction = model_service.predict_solar(features)
    
    return ForecastResponse(
        location=request.location,
        weather=weather_data,
        predicted_energy_output=float(prediction[0])
    )


@app.post("/forecast/wind", response_model=ForecastResponse)
async def get_wind_forecast(
    request: WindForecastRequest,
    api_key: str = Depends(get_api_key)
) -> ForecastResponse:
    weather_data = weather_service.get_weather_data(request.location)
    
    features = [
        [
            weather_data.temperature,
            weather_data.wind_speed,
            0.0  
        ]
    ]
    
    prediction = model_service.predict_wind(features)
    
    return ForecastResponse(
        location=request.location,
        weather=weather_data,
        predicted_energy_output=float(prediction[0])
    )


@app.get("/cache/info", response_model=CacheInfo)
async def get_cache_info(api_key: str = Depends(get_api_key)):
    if not settings.ENABLE_CACHING:
        return CacheInfo(
            enabled=False,
            size=0,
            max_size=0,
            ttl=0,
            hit_rate=0.0
        )
    
    cache_stats = cache_service.get_stats()
    
    return CacheInfo(
        enabled=True,
        size=cache_stats["size"],
        max_size=cache_stats["max_size"],
        ttl=settings.FORECAST_CACHE_TTL,
        hit_rate=cache_stats["hit_rate"]
    )


@app.post("/cache/clear")
async def clear_cache(api_key: str = Depends(get_api_key)):
    if not settings.ENABLE_CACHING:
        return {"status": "cache not enabled"}
    
    cache_service.clear()
    return {"status": "cache cleared"}


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )