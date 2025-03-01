from typing import Optional, Dict, Any
from datetime import datetime
import traceback
import logging
import json
import uuid
from fastapi import HTTPException
from starlette.status import (
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
logger.setLevel(logging.ERROR)

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
        self.headers = headers or {}  # Initialize headers
        
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
            
        if self.headers:
            standard_headers.update(self.headers)
        
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

class BadRequestError(BaseAPIException):
    def __init__(
        self,
        detail: str = "Bad request",
        error_code: str = "BAD_REQUEST",
        **kwargs
    ):
        super().__init__(
            status_code=HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code,
            **kwargs
        )

class UnauthorizedError(BaseAPIException):
    def __init__(
        self,
        detail: str = "Unauthorized",
        error_code: str = "UNAUTHORIZED",
        **kwargs
    ):
        super().__init__(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"},
            **kwargs
        )

class ForbiddenError(BaseAPIException):
    def __init__(
        self,
        detail: str = "Forbidden",
        error_code: str = "FORBIDDEN",
        **kwargs
    ):
        super().__init__(
            status_code=HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code,
            **kwargs
        )

class NotFoundError(BaseAPIException):
    def __init__(
        self,
        detail: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        **kwargs
    ):
        super().__init__(
            status_code=HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code,
            **kwargs
        )

class ValidationError(BaseAPIException):
    def __init__(
        self,
        detail: str = "Validation error",
        error_code: str = "VALIDATION_ERROR",
        **kwargs
    ):
        super().__init__(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code,
            **kwargs
        )

class RateLimitError(BaseAPIException):
    def __init__(
        self,
        detail: str = "Too many requests",
        error_code: str = "RATE_LIMIT_EXCEEDED",
        retry_after: int = None,
        **kwargs
    ):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        
        super().__init__(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code=error_code,
            headers=headers,
            **kwargs
        )

class InternalServerError(BaseAPIException):
    def __init__(
        self,
        detail: str = "Internal server error",
        error_code: str = "INTERNAL_SERVER_ERROR",
        **kwargs
    ):
        super().__init__(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code,
            **kwargs
        )

class ServiceUnavailableError(BaseAPIException):
    def __init__(
        self,
        detail: str = "Service temporarily unavailable",
        error_code: str = "SERVICE_UNAVAILABLE",
        retry_after: int = None,
        **kwargs
    ):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        
        super().__init__(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code=error_code,
            headers=headers,
            **kwargs
        )

class DatabaseError(InternalServerError):
    def __init__(
        self,
        detail: str = "Database error occurred",
        error_code: str = "DATABASE_ERROR",
        **kwargs
    ):
        super().__init__(
            detail=detail,
            error_code=error_code,
            **kwargs
        )

class ExternalServiceError(ServiceUnavailableError):
    def __init__(
        self,
        service_name: str,
        detail: str = None,
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        **kwargs
    ):
        detail = detail or f"Error communicating with {service_name}"
        super().__init__(
            detail=detail,
            error_code=error_code,
            **kwargs
        )
        self.add_context("service_name", service_name)