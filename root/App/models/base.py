from typing import Optional, Dict, Any, Union, Type, TypeVar, List, Generic
from pydantic import (
    BaseModel,
    Field,
    validator,
    root_validator,
    Extra,
    constr,
    conlist,
    ValidationError,
)
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4
import re
from functools import cached_property

T = TypeVar("T")

class ModelStatus(str, Enum):
    """Enumeration of common model statuses."""
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    IN_PROGRESS = "in_progress"

class TimestampMixin(BaseModel):
    """Mixin for adding timestamp fields to models."""
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the record was created",
        alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the record was last updated",
        alias="updatedAt"
    )

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }

class APIModel(BaseModel):
    """
    Base model for API responses and requests.
    Adds common fields and validation logic.
    """
    id: Optional[Union[str, UUID]] = Field(
        None,
        description="Unique identifier for the record",
        validate_default=True,
        alias="id"
    )
    description: Optional[str] = Field(
        None,
        description="Human-readable description of the record",
        min_length=3,
        max_length=500
    )
    status: ModelStatus = Field(
        ModelStatus.DRAFT,
        description="Current status of the record"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata associated with the record"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="List of tags associated with the record",
        max_items=10
    )

    @validator("id", pre=True, always=True)
    def validate_id(cls, v: Union[str, UUID, None]) -> Union[str, UUID]:
        """Validate and format the ID field."""
        if v is None:
            return str(uuid4())
        if isinstance(v, UUID):
            return v
        if not isinstance(v, str):
            raise ValueError("ID must be a string or UUID")
        if len(v) < 3:
            raise ValueError("ID must be at least 3 characters long")
        if not re.match(r'^[a-zA-Z0-9-]+$', v):
            raise ValueError("ID can only contain letters, numbers, and hyphens")
        return v

    @validator("tags")
    def validate_tags(cls, v):
        """Validate that tags are unique and properly formatted."""
        if v is not None:
            if len(v) < 1:
                raise ValueError("At least one tag must be provided")
            if len(v) > 10:
                raise ValueError("Maximum of 10 tags allowed")
            if len(set(v)) != len(v):
                raise ValueError("Tags must be unique")
            for tag in v:
                if not re.match(r'^[a-zA-Z0-9-_]+$', tag):
                    raise ValueError(f"Tag '{tag}' contains invalid characters")
        return v

    @cached_property
    def is_active(self) -> bool:
        """Determine if the record is active based on its status."""
        return self.status in {
            ModelStatus.PUBLISHED,
            ModelStatus.IN_PROGRESS
        }

    @classmethod
    def get_example(cls) -> Dict[str, Any]:
        """Generate an example dictionary for the model."""
        return {
            "id": "example-id-123",
            "description": "Example record description",
            "status": ModelStatus.PUBLISHED.value,
            "metadata": {
                "key": "value"
            },
            "tags": ["example", "test"]
        }

    class Config:
        """Pydantic configuration for the model."""
        extra = Extra.forbid
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            UUID: lambda u: str(u),
            ModelStatus: lambda s: s.value
        }
        schema_extra = {
            "example": {
                "id": "example-id-123",
                "description": "Example record description",
                "status": "published",
                "metadata": {"key": "value"},
                "tags": ["example", "test"]
            }
        }

class PaginatedResponse(Generic[T], BaseModel):
    """
    Base model for paginated API responses.
    """
    data: List[T] = Field(..., description="List of records")
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of records per page")
    pages: int = Field(..., description="Total number of pages")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }

class APIError(BaseModel):
    """
    Base model for API error responses.
    """
    status: int = Field(..., description="HTTP status code")
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details"
    )
    trace_id: Optional[str] = Field(
        None,
        description="Unique identifier for the error occurrence"
    )

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }

class APIResponse(BaseModel):
    """
    Base model for API success responses.
    """
    success: bool = Field(True, description="Indicates if the request was successful")
    data: Optional[Any] = Field(
        None,
        description="Response data if the request was successful"
    )
    errors: Optional[List[APIError]] = Field(
        None,
        description="List of errors if the request was unsuccessful"
    )

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }

class BaseFilter(BaseModel):
    """
    Base model for API filter parameters.
    """
    page: int = Field(1, description="Page number for pagination", ge=1)
    per_page: int = Field(10, description="Number of items per page", ge=1, le=100)
    sort_by: Optional[str] = Field(
        None,
        description="Field to sort results by"
    )
    sort_order: Optional[str] = Field(
        "asc",
        description="Sort order (asc or desc)",
        regex=r"^(asc|desc)$"
    )
    filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Dictionary of filter parameters"
    )

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }

class BaseUpdate(BaseModel):
    """
    Base model for update operations.
    """
    updated_fields: Dict[str, Any] = Field(
        ...,
        description="Dictionary of fields to update and their new values"
    )
    version: Optional[int] = Field(
        None,
        description="Version number for optimistic concurrency control"
    )

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }

class BaseCreate(BaseModel):
    """
    Base model for create operations.
    """
    data: Dict[str, Any] = Field(
        ...,
        description="Dictionary of initial field values"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata to include with the new record"
    )

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }