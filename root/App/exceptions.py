from typing import Optional, Dict, Any, List, Union, Callable
from datetime import datetime
import traceback
import logging
import json
import uuid
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import (n
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE
)

logger = logging.getLogger("api.exceptions")

class BaseAPIException(HTTPException):
    def __init__(
        self, 
        status_code: int, 
        detail: str,
        error_code: str = None,
        error_details: Dict[str, Any] = None,
        request_id: str = None,
        docs_url: str = None,
        log_level: int = logging.ERROR,
        headers: Optional[Dict[str, str]] = None,
        exception: Exception = None
    ):
        self.error_code = error_code or f"ERR_{status_code}"
        self.timestamp = datetime.utcnow().isoformat()
        self.error_details = error_details or {}
        self.request_id = request_id or str(uuid.uuid4())
        self.docs_url = docs_url
        self.log_level = log_level
        self.original_exception = exception
        
        self.enhanced_detail = {
            "message": detail,
            "error_code": self.error_code,
            "timestamp": self.timestamp,
            "request_id": self.request_id
        }
        
        if error_details:
            self.enhanced_detail["details"] = error_details
            
        if docs_url:
            self.enhanced_detail["docs_url"] = docs_url
            
        standard_headers = {
            "X-Error-Code": self.error_code,
            "X-Request-ID": self.request_id
        }
            
        if headers:
            standard_headers.update(headers)
        
        self._log_exception(detail)
            
        super().__init__(
            status_code=status_code, 
            detail=self.enhanced_detail,
            headers=standard_headers
        )
    
    def _log_exception(self, message: str) -> None:
        log_data = {
            "error_code": self.error_code,
            "status_code": self.status_code,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "details": self.error_details
        }
        
        if self.original_exception:
            log_data["exception_type"] = type(self.original_exception).__name__
            log_data["exception_args"] = str(self.original_exception.args)
            log_data["traceback"] = traceback.format_exc()
        
        logger.log(
            self.log_level,
            f"{message} - {json.dumps(log_data)}"
        )
    
    def add_context(self, key: str, value: Any) -> "BaseAPIException":
        self.error_details[key] = value
        self.enhanced_detail.setdefault("details", {})
        self.enhanced_detail["details"][key] = value
        return self
    
    def with_request_id(self, request_id: str) -> "BaseAPIException":
        self.request_id = request_id
        self.enhanced_detail["request_id"] = request_id
        if self.headers:
            self.headers["X-Request-ID"] = request_id
        return self
    
    def with_docs_url(self, url: str) -> "BaseAPIException":
        self.docs_url = url
        self.enhanced_detail["docs_url"] = url
        return self
    
    def with_log_level(self, level: int) -> "BaseAPIException":
        self.log_level = level
        return self
    
    @classmethod
    def from_exception(
        cls, 
        exception: Exception, 
        status_code: int = HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = None,
        detail: str = None
    ) -> "BaseAPIException":
        return cls(
            status_code=status_code,
            detail=detail or str(exception),
            error_code=error_code or f"ERR_{status_code}",
            exception=exception,
            error_details={"exception_type": type(exception).__name__}
        )


class WeatherAPIException(BaseAPIException):
    def __init__(
        self, 
        detail: str = "Error fetching weather data",
        error_code: str = "WEATHER_API_ERROR",
        error_details: Dict[str, Any] = None,
        request_id: str = None,
        retry_after: Optional[int] = None,
        exception: Exception = None
    ):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
            
        super().__init__(
            status_code=HTTP_503_SERVICE_UNAVAILABLE, 
            detail=detail,
            error_code=error_code,
            error_details=error_details,
            request_id=request_id,
            docs_url="https://api.example.com/docs/errors/weather-api",
            headers=headers,
            exception=exception
        )


class ModelException(BaseAPIException):
    def __init__(
        self, 
        detail: str = "Error generating forecast",
        error_code: str = "MODEL_ERROR",
        model_name: str = None,
        model_version: str = None,
        error_details: Dict[str, Any] = None,
        request_id: str = None,
        exception: Exception = None
    ):
        details = error_details or {}
        if model_name:
            details["model_name"] = model_name
        if model_version:
            details["model_version"] = model_version
            
        super().__init__(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=detail,
            error_code=error_code,
            error_details=details,
            request_id=request_id,
            docs_url="https://api.example.com/docs/errors/model",
            exception=exception
        )


class LocationNotFoundException(BaseAPIException):
    def __init__(
        self, 
        location: str,
        detail: str = None,
        error_code: str = "LOCATION_NOT_FOUND",
        request_id: str = None
    ):
        super().__init__(
            status_code=HTTP_404_NOT_FOUND, 
            detail=detail or f"Location '{location}' not found",
            error_code=error_code,
            error_details={"location": location},
            request_id=request_id,
            log_level=logging.WARNING
        )


class RateLimitExceededException(BaseAPIException):
    def __init__(
        self, 
        detail: str = "Rate limit exceeded",
        error_code: str = "RATE_LIMIT_EXCEEDED",
        retry_after: int = 60,
        request_id: str = None,
        limit: int = None,
        current: int = None
    ):
        details = {}
        if limit is not None:
            details["limit"] = limit
        if current is not None:
            details["current"] = current
        
        headers = {"Retry-After": str(retry_after)}
        
        super().__init__(
            status_code=HTTP_429_TOO_MANY_REQUESTS, 
            detail=detail,
            error_code=error_code,
            error_details=details,
            request_id=request_id,
            headers=headers,
            log_level=logging.INFO
        )
        self.retry_after = retry_after


class ValidationException(BaseAPIException):
    def __init__(
        self, 
        detail: str = "Validation error",
        error_code: str = "VALIDATION_ERROR",
        field_errors: Dict[str, str] = None,
        request_id: str = None
    ):
        super().__init__(
            status_code=HTTP_400_BAD_REQUEST, 
            detail=detail,
            error_code=error_code,
            error_details={"field_errors": field_errors} if field_errors else None,
            request_id=request_id,
            log_level=logging.WARNING
        )


class AuthenticationException(BaseAPIException):
    def __init__(
        self, 
        detail: str = "Authentication failed",
        error_code: str = "AUTHENTICATION_ERROR",
        request_id: str = None
    ):
        super().__init__(
            status_code=HTTP_401_UNAUTHORIZED, 
            detail=detail,
            error_code=error_code,
            request_id=request_id,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationException(BaseAPIException):
    def __init__(
        self, 
        detail: str = "Not authorized to perform this action",
        error_code: str = "AUTHORIZATION_ERROR",
        request_id: str = None,
        required_permissions: List[str] = None
    ):
        details = {}
        if required_permissions:
            details["required_permissions"] = required_permissions
            
        super().__init__(
            status_code=HTTP_403_FORBIDDEN, 
            detail=detail,
            error_code=error_code,
            error_details=details if details else None,
            request_id=request_id
        )


class DependencyException(BaseAPIException):
    def __init__(
        self, 
        dependency_name: str,
        detail: str = None,
        error_code: str = "DEPENDENCY_ERROR",
        request_id: str = None,
        retry_after: Optional[int] = None
    ):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
            
        super().__init__(
            status_code=HTTP_503_SERVICE_UNAVAILABLE, 
            detail=detail or f"Service dependency '{dependency_name}' unavailable",
            error_code=error_code,
            error_details={"dependency": dependency_name},
            request_id=request_id,
            headers=headers
        )


class ConfigurationException(BaseAPIException):
    def __init__(
        self, 
        detail: str = "Configuration error",
        error_code: str = "CONFIGURATION_ERROR",
        config_key: str = None,
        request_id: str = None
    ):
        details = {}
        if config_key:
            details["config_key"] = config_key
            
        super().__init__(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=detail,
            error_code=error_code,
            error_details=details if details else None,
            request_id=request_id
        )


def register_exception_handlers(app):
    @app.exception_handler(BaseAPIException)
    async def base_api_exception_handler(request: Request, exc: BaseAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.enhanced_detail,
            headers=exc.headers
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        content = {
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id
        }
        
        headers = dict(exc.headers) if exc.headers else {}
        headers["X-Request-ID"] = request_id
        
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=headers
        )
    
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc()
            }
        )
        
        content = {
            "message": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id
        }
        
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
            headers={"X-Request-ID": request_id}
        )