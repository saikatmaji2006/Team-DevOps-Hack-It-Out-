import logging
import time
from contextlib import asynccontextmanager
from typing import Callable

import prometheus_client
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import (
    PROJECT_NAME, 
    PROJECT_DESCRIPTION, 
    PROJECT_VERSION, 
    API_V1_PREFIX,
    LOG_LEVEL,
    LOG_FORMAT,
    ENABLE_METRICS,
    RATE_LIMIT_ENABLED
)
from app.api.endpoints import weather, forecast, train
from app.services.cache import get_cache_service, close_cache_connection
from app.services.model import load_models, unload_models
from app.utils.exceptions import setup_exception_handlers

import structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger(__name__)

if ENABLE_METRICS:
    REQUEST_TIME = prometheus_client.Summary('request_processing_seconds', 'Time spent processing request')
    REQUEST_COUNT = prometheus_client.Counter('request_count', 'Total count of requests', ['method', 'endpoint', 'status_code'])
    ACTIVE_REQUESTS = prometheus_client.Gauge('active_requests', 'Number of active requests')

limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"]) if RATE_LIMIT_ENABLED else None

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        if ENABLE_METRICS:
            ACTIVE_REQUESTS.inc()
            
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            if ENABLE_METRICS:
                REQUEST_TIME.observe(process_time)
                REQUEST_COUNT.labels(
                    method=request.method, 
                    endpoint=request.url.path,
                    status_code=response.status_code
                ).inc()
                
            response.headers["X-Process-Time"] = str(process_time)
            
            logger.info(
                "request_processed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=process_time,
                client_ip=request.client.host if request.client else None
            )
            
            return response
        except Exception as e:
            logger.exception(
                "request_failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                client_ip=request.client.host if request.client else None
            )
            raise
        finally:
            if ENABLE_METRICS:
                ACTIVE_REQUESTS.dec()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Renewable Energy Forecasting API", version=PROJECT_VERSION)
    
    await get_cache_service()
    await load_models()
    
    yield
    
    logger.info("Shutting down Renewable Energy Forecasting API")
    
    await close_cache_connection()
    await unload_models()

app = FastAPI(
    title=PROJECT_NAME,
    description=PROJECT_DESCRIPTION,
    version=PROJECT_VERSION,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(MetricsMiddleware)

if RATE_LIMIT_ENABLED:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

setup_exception_handlers(app)

app.include_router(
    weather.router,
    prefix=f"{API_V1_PREFIX}/weather",
    tags=["Weather"]
)
app.include_router(
    forecast.router,
    prefix=f"{API_V1_PREFIX}/forecast",
    tags=["Forecast"]
)
app.include_router(
    train.router,
    prefix=f"{API_V1_PREFIX}/train",
    tags=["Training"]
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "message": "Renewable Energy Forecasting API is running",
        "version": PROJECT_VERSION,
        "environment": "production" if not __debug__ else "development"
    }

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{PROJECT_NAME} - API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
        swagger_ui_parameters={"defaultModelsExpandDepth": -1, "syntaxHighlight.theme": "monokai"}
    )

@app.get("/metrics", include_in_schema=False)
async def metrics():
    if not ENABLE_METRICS:
        return JSONResponse(
            status_code=404,
            content={"detail": "Metrics collection is disabled"}
        )
    
    return Response(
        content=prometheus_client.generate_latest(),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_config=None
    )