from typing import Optional
from pydantic import BaseModel, Field, validator
from geopy.distance import geodesic
import re

class Coordinates(BaseModel):
    """Model representing geographical coordinates."""
    latitude: float = Field(..., description="Latitude in decimal degrees", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude in decimal degrees", ge=-180, le=180)

    def distance_to(self, other: 'Coordinates') -> float:
        """
        Calculate the distance in kilometers between this coordinate and another.

        Args:
            other: Another Coordinates object

        Returns:
            Distance in kilometers
        """
        return geodesic(
            (self.latitude, self.longitude),
            (other.latitude, other.longitude)
        ).kilometers

    def to_string(self) -> str:
        """
        Convert the coordinates to a string representation.

        Returns:
            String representation of the coordinates (e.g., "37.7749, -122.4194")
        """
        return f"{self.latitude}, {self.longitude}"

    class Config:
        schema_extra = {
            "example": {
                "latitude": 37.7749,
                "longitude": -122.4194
            }
        }

class Location(BaseModel):
    """Model representing a geographical location with additional metadata."""
    coordinates: Coordinates = Field(..., description="Geographical coordinates")
    name: Optional[str] = Field(None, description="Location name")
    country: Optional[str] = Field(None, description="Country code (ISO 3166-1 alpha-2)")
    region: Optional[str] = Field(None, description="Region or state")
    city: Optional[str] = Field(None, description="City name")
    postal_code: Optional[str] = Field(None, description="Postal or ZIP code", regex=r'^\d{5}(-\d{4})?$')
    timezone: Optional[str] = Field(None, description="Timezone identifier (e.g., 'America/New_York')")
    elevation: Optional[float] = Field(None, description="Elevation above sea level in meters", ge=0)

    @validator('timezone')
    def validate_timezone(cls, v):
        """Validate that the timezone is a valid IANA timezone identifier."""
        if v is not None:
            try:
                import pytz
                if v not in pytz.all_timezones:
                    raise ValueError(f"Invalid timezone: {v}")
            except ImportError:
                # If pytz is not available, skip validation
                pass
        return v

    def to_dict(self) -> dict:
        """
        Convert the location object to a dictionary representation.

        Returns:
            Dictionary representation of the location
        """
        return {
            "name": self.name,
            "country": self.country,
            "region": self.region,
            "city": self.city,
            "postal_code": self.postal_code,
            "timezone": self.timezone,
            "elevation": self.elevation,
            "coordinates": self.coordinates.to_string()
        }

    class Config:
        schema_extra = {
            "example": {
                "coordinates": {
                    "latitude": 37.7749,
                    "longitude": -122.4194
                },
                "name": "San Francisco",
                "country": "US",
                "region": "California",
                "city": "San Francisco",
                "postal_code": "94103",
                "timezone": "America/Los_Angeles",
                "elevation": 16.0
            }
        }
