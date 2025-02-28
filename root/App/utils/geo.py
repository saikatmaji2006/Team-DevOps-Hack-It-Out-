import math
from typing import Tuple, Union, Optional
from pydantic import BaseModel, validator, Field
from functools import lru_cache

class Coordinates(BaseModel):
    latitude: float = Field(..., description="Latitude in degrees (-90 to 90)")
    longitude: float = Field(..., description="Longitude in degrees (-180 to 180)")

    @validator('latitude')
    def validate_latitude(cls, v: float) -> float:
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        return round(v, 6)  
    @validator('longitude')
    def validate_longitude(cls, v: float) -> float:
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")
        return round(v, 6)  
    class Config:
        frozen = True  

@lru_cache(maxsize=1024)
def parse_coordinates(location: str) -> Optional[Tuple[float, float]]:
    """
    Parse a string containing latitude and longitude coordinates.
    Caches results for improved performance.
    
    Args:
        location: String in format "latitude,longitude" or "lat,lon"
        
    Returns:
        Tuple of (latitude, longitude) if valid, None otherwise
    
    Examples:
        >>> parse_coordinates("51.5074,-0.1278")
        (51.5074, -0.1278)
        >>> parse_coordinates("invalid")
        None
    """
    try:
        if ',' not in location:
            return None
            
        lat_str, lon_str = location.split(',')
        latitude = float(lat_str.strip())
        longitude = float(lon_str.strip())
        
        if is_valid_coordinates(latitude, longitude):
            return round(latitude, 6), round(longitude, 6)
        return None
        
    except (ValueError, TypeError):
        return None

def is_valid_coordinates(latitude: float, longitude: float) -> bool:
    """
    Check if the given coordinates are valid.
    
    Args:
        latitude: Latitude in degrees (-90 to 90)
        longitude: Longitude in degrees (-180 to 180)
        
    Returns:
        bool: True if coordinates are valid, False otherwise
    
    Examples:
        >>> is_valid_coordinates(51.5074, -0.1278)
        True
        >>> is_valid_coordinates(91, 0)
        False
    """
    try:
        Coordinates(latitude=latitude, longitude=longitude)
        return True
    except ValueError:
        return False

def haversine_distance(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float, 
    unit: str = 'km'
) -> float:
    """
    Calculate the great circle distance between two points on Earth using the Haversine formula.
    
    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees
        unit: Unit of distance ('km' for kilometers, 'mi' for miles)
        
    Returns:
        Distance between points in specified unit
    
    Raises:
        ValueError: If coordinates are invalid
    
    Examples:
        >>> haversine_distance(51.5074, -0.1278, 48.8566, 2.3522)  # London to Paris
        343.47
    """
    if not (is_valid_coordinates(lat1, lon1) and is_valid_coordinates(lat2, lon2)):
        raise ValueError("Invalid coordinates provided")

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    r = 6371.0088  

    distance = c * r
    
    if unit.lower() == 'mi':
        distance *= 0.621371
        
    return round(distance, 2)

def get_bounding_box(
    latitude: float, 
    longitude: float, 
    radius_km: float
) -> Tuple[float, float, float, float]:
    """
    Calculate a bounding box around a point given a radius in kilometers.
    Uses a spherical Earth model for calculations.
    
    Args:
        latitude: Center point latitude in degrees
        longitude: Center point longitude in degrees
        radius_km: Radius in kilometers
        
    Returns:
        Tuple of (min_lat, min_lon, max_lat, max_lon)
    
    Raises:
        ValueError: If coordinates are invalid or radius is negative
    
    Examples:
        >>> get_bounding_box(51.5074, -0.1278, 10)
        (51.4177, -0.2634, 51.5971, 0.0078)
    """
    if not is_valid_coordinates(latitude, longitude):
        raise ValueError("Invalid coordinates provided")
    if radius_km <= 0:
        raise ValueError("Radius must be positive")
    
    earth_radius = 6371.0088
    
    angular_radius = radius_km / earth_radius
    
    lat_rad = math.radians(latitude)
    lon_rad = math.radians(longitude)
    
    min_lat = lat_rad - angular_radius
    max_lat = lat_rad + angular_radius
    
    if min_lat > -math.pi/2 and max_lat < math.pi/2:
        delta_lon = math.asin(math.sin(angular_radius) / math.cos(lat_rad))
        min_lon = lon_rad - delta_lon
        max_lon = lon_rad + delta_lon
    else:
        min_lat = max(-math.pi/2, min_lat)
        max_lat = min(math.pi/2, max_lat)
        min_lon = -math.pi
        max_lon = math.pi
    return tuple(map(lambda x: round(math.degrees(x), 6), 
                    (min_lat, min_lon, max_lat, max_lon)))