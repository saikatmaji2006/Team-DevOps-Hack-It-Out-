import math
import datetime
import requests
from typing import Dict, List, Tuple, Optional, Union, Any
from functools import lru_cache

EARTH_RADIUS_KM = 6371.0
EARTH_RADIUS_MI = 3958.8

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float, unit: str = 'km') -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    
    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees
        unit: Unit of distance ('km' for kilometers, 'mi' for miles)
        
    Returns:
        float: Distance between the points in specified unit
    """
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    # Choose radius based on unit
    radius = EARTH_RADIUS_KM if unit == 'km' else EARTH_RADIUS_MI
    distance = radius * c
    
    return distance

def get_bounding_box(lat: float, lon: float, distance_km: float) -> Tuple[float, float, float, float]:
    """
    Calculate a bounding box around a point given a distance in kilometers.
    
    Args:
        lat: Latitude of center point in degrees
        lon: Longitude of center point in degrees
        distance_km: Distance from center point in kilometers
        
    Returns:
        Tuple: (min_lat, min_lon, max_lat, max_lon) defining the bounding box
    """
    # Earth's radius in kilometers
    radius = EARTH_RADIUS_KM
    
    # Angular distance in radians
    angular_distance = distance_km / radius
    
    # Convert latitude and longitude from degrees to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    
    # Calculate min and max latitudes
    min_lat_rad = lat_rad - angular_distance
    max_lat_rad = lat_rad + angular_distance
    
    # Calculate min and max longitudes
    delta_lon = math.asin(math.sin(angular_distance) / math.cos(lat_rad))
    min_lon_rad = lon_rad - delta_lon
    max_lon_rad = lon_rad + delta_lon
    
    # Convert back to degrees
    min_lat = math.degrees(min_lat_rad)
    max_lat = math.degrees(max_lat_rad)
    min_lon = math.degrees(min_lon_rad)
    max_lon = math.degrees(max_lon_rad)
    
    return (min_lat, min_lon, max_lat, max_lon)

@lru_cache(maxsize=128)
def get_timezone_for_location(lat: float, lon: float) -> Optional[str]:
    """
    Get the timezone for a given latitude and longitude.
    Uses the TimeZoneDB API (requires API key).
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        
    Returns:
        str: Timezone name (e.g., 'America/New_York') or None if not found
    """
    try:
        # Replace with your actual API key
        api_key = "YOUR_TIMEZONEDB_API_KEY"
        url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={api_key}&format=json&by=position&lat={lat}&lng={lon}"
        
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data['status'] == 'OK':
            return data['zoneName']
        return None
    except Exception:
        return None

def get_local_time(timezone_name: str) -> Optional[datetime.datetime]:
    """
    Get the current local time for a given timezone.
    
    Args:
        timezone_name: Name of the timezone (e.g., 'America/New_York')
        
    Returns:
        datetime: Current local time in the specified timezone
    """
    try:
        import pytz
        timezone = pytz.timezone(timezone_name)
        return datetime.datetime.now(timezone)
    except Exception:
        return None

def get_solar_position(lat: float, lon: float, date: Optional[datetime.datetime] = None) -> Dict[str, float]:
    """
    Calculate the solar position (altitude and azimuth) for a given location and time.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        date: Datetime object (defaults to current UTC time)
        
    Returns:
        Dict: Contains 'altitude' and 'azimuth' in degrees
    """
    if date is None:
        date = datetime.datetime.utcnow()
    
    # Days since J2000.0 epoch
    days_since_j2000 = (date - datetime.datetime(2000, 1, 1, 12, 0, 0)).total_seconds() / 86400.0
    
    # Mean solar longitude
    mean_longitude = (280.460 + 0.9856474 * days_since_j2000) % 360
    
    # Mean anomaly
    mean_anomaly_rad = math.radians((357.528 + 0.9856003 * days_since_j2000) % 360)
    
    # Ecliptic longitude
    ecliptic_longitude_rad = math.radians(
        mean_longitude + 1.915 * math.sin(mean_anomaly_rad) + 0.020 * math.sin(2 * mean_anomaly_rad)
    )
    
    # Obliquity of the ecliptic
    obliquity_rad = math.radians(23.439 - 0.0000004 * days_since_j2000)
    
    # Right ascension
    right_ascension_rad = math.atan2(
        math.cos(obliquity_rad) * math.sin(ecliptic_longitude_rad),
        math.cos(ecliptic_longitude_rad)
    )
    
    # Declination
    declination_rad = math.asin(
        math.sin(obliquity_rad) * math.sin(ecliptic_longitude_rad)
    )
    
    # Local hour angle
    hour = date.hour + date.minute / 60.0 + date.second / 3600.0
    local_hour_angle_rad = math.radians(15.0 * (hour - 12.0) + lon)
    
    # Altitude
    lat_rad = math.radians(lat)
    altitude_rad = math.asin(
        math.sin(lat_rad) * math.sin(declination_rad) +
        math.cos(lat_rad) * math.cos(declination_rad) * math.cos(local_hour_angle_rad)
    )
    
    # Azimuth
    azimuth_rad = math.atan2(
        -math.sin(local_hour_angle_rad),
        math.tan(declination_rad) * math.cos(lat_rad) - math.sin(lat_rad) * math.cos(local_hour_angle_rad)
    )
    
    # Convert to degrees
    altitude = math.degrees(altitude_rad)
    azimuth = (math.degrees(azimuth_rad) + 180) % 360
    
    return {
        'altitude': altitude,
        'azimuth': azimuth
    }

def get_sunrise_sunset(lat: float, lon: float, date: Optional[datetime.date] = None) -> Dict[str, Optional[datetime.time]]:
    """
    Calculate sunrise and sunset times for a given location and date.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        date: Date object (defaults to current date)
        
    Returns:
        Dict: Contains 'sunrise' and 'sunset' as datetime.time objects
    """
    if date is None:
        date = datetime.datetime.utcnow().date()
    
    try:
        # Use sunrise-sunset.org API
        url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date.isoformat()}&formatted=0"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data['status'] == 'OK':
            sunrise_str = data['results']['sunrise']
            sunset_str = data['results']['sunset']
            
            sunrise = datetime.datetime.fromisoformat(sunrise_str.replace('Z', '+00:00')).time()
            sunset = datetime.datetime.fromisoformat(sunset_str.replace('Z', '+00:00')).time()
            
            return {
                'sunrise': sunrise,
                'sunset': sunset
            }
    except Exception:
        pass
    
    # Fallback calculation if API fails
    # This is a simplified calculation and may not be accurate
    # Day of year
    day_of_year = date.timetuple().tm_yday
    
    # Approximate solar declination
    declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
    declination_rad = math.radians(declination)
    
    # Sunrise/sunset hour angle
    lat_rad = math.radians(lat)
    hour_angle_rad = math.acos(
        -math.tan(lat_rad) * math.tan(declination_rad)
    )
    hour_angle = math.degrees(hour_angle_rad)
    
    # Convert to hours
    sunrise_hour = 12 - hour_angle / 15 - lon / 15
    sunset_hour = 12 + hour_angle / 15 - lon / 15
    
    # Adjust for UTC
    sunrise_hour = sunrise_hour % 24
    sunset_hour = sunset_hour % 24
    
    # Convert to time objects
    sunrise_h = int(sunrise_hour)
    sunrise_m = int((sunrise_hour - sunrise_h) * 60)
    sunset_h = int(sunset_hour)
    sunset_m = int((sunset_hour - sunset_h) * 60)
    
    return {
        'sunrise': datetime.time(sunrise_h, sunrise_m),
        'sunset': datetime.time(sunset_h, sunset_m)
    }

@lru_cache(maxsize=100)
def geocode_address(address: str) -> Optional[Dict[str, float]]:
    """
    Convert an address to latitude and longitude coordinates.
    Uses the Nominatim API (OpenStreetMap).
    
    Args:
        address: Address string to geocode
        
    Returns:
        Dict: Contains 'lat' and 'lon' as floats, or None if geocoding fails
    """
    try:
        # Use Nominatim API (please respect usage policy)
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'EnergyMonitoringApp/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        
        if data and len(data) > 0:
            return {
                'lat': float(data[0]['lat']),
                'lon': float(data[0]['lon'])
            }
        return None
    except Exception:
        return None

def reverse_geocode(lat: float, lon: float) -> Optional[Dict[str, str]]:
    """
    Convert latitude and longitude to an address.
    Uses the Nominatim API (OpenStreetMap).
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        
    Returns:
        Dict: Address components or None if reverse geocoding fails
    """
    try:
        # Use Nominatim API (please respect usage policy)
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json'
        }
        headers = {
            'User-Agent': 'EnergyMonitoringApp/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        
        if 'address' in data:
            return data['address']
        return None
    except Exception:
        return None

def get_solar_radiation(lat: float, lon: float, date: Optional[datetime.date] = None) -> Optional[float]:
    """
    Estimate solar radiation (insolation) for a given location and date.
    This is a simplified model and should be replaced with actual API data for production use.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        date: Date object (defaults to current date)
        
    Returns:
        float: Estimated solar radiation in kWh/m²/day
    """
    if date is None:
        date = datetime.datetime.utcnow().date()
    
    # Day of year
    day_of_year = date.timetuple().tm_yday
    
    # Solar declination
    declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
    declination_rad = math.radians(declination)
    
    # Sunrise/sunset hour angle
    lat_rad = math.radians(lat)
    cos_term = -math.tan(lat_rad) * math.tan(declination_rad)
    
    # Check if we're in polar day/night
    if cos_term < -1:  # Polar day
        day_length = 24
    elif cos_term > 1:  # Polar night
        day_length = 0
    else:
        hour_angle_rad = math.acos(cos_term)
        hour_angle = math.degrees(hour_angle_rad)
        day_length = 2 * hour_angle / 15
    
    # Solar constant
    solar_constant = 1367  # W/m²
    
    # Atmospheric transmittance (simplified)
    transmittance = 0.7
    
    # Extraterrestrial radiation
    extra_radiation = solar_constant * (1 + 0.033 * math.cos(math.radians((360 * day_of_year) / 365)))
    
    # Daily insolation
    if day_length > 0:
        insolation = (24 / math.pi) * extra_radiation * transmittance * (
            math.cos(lat_rad) * math.cos(declination_rad) * math.sin(math.radians(15 * day_length / 2
        )) + (math.pi * day_length / 180) * math.sin(lat_rad) * math.sin(declination_rad))
    else:
        insolation = 0
    def get_solar_radiation(lat: float, lon: float, date: Optional[datetime.date] = None) -> Optional[float]:
    """
    Estimate solar radiation (insolation) for a given location and date.
    This is a simplified model and should be replaced with actual API data for production use.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        date: Date object (defaults to current date)
        
    Returns:
        float: Estimated solar radiation in kWh/m²/day
    """
    if date is None:
        date = datetime.datetime.utcnow().date()
    
    # Day of year
    day_of_year = date.timetuple().tm_yday
    
    # Solar declination
    declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
    declination_rad = math.radians(declination)
    
    # Sunrise/sunset hour angle
    lat_rad = math.radians(lat)
    cos_term = -math.tan(lat_rad) * math.tan(declination_rad)
    
    # Check if we're in polar day/night
    if cos_term < -1:  # Polar day
        day_length = 24
    elif cos_term > 1:  # Polar night
        day_length = 0
    else:
        hour_angle_rad = math.acos(cos_term)
        hour_angle = math.degrees(hour_angle_rad)
        day_length = 2 * hour_angle / 15
    
    # Solar constant
    solar_constant = 1367  # W/m²
    
    # Atmospheric transmittance (simplified)
    transmittance = 0.7
    
    # Extraterrestrial radiation
    extra_radiation = solar_constant * (1 + 0.033 * math.cos(math.radians((360 * day_of_year) / 365)))
    
    # Daily insolation
    if day_length > 0:
        insolation = (24 / math.pi) * extra_radiation * transmittance * (
            math.cos(lat_rad) * math.cos(declination_rad) * math.sin(math.radians(15 * day_length / 2)) + 
            (math.pi * day_length / 24) * math.sin(lat_rad) * math.sin(declination_rad)
        )
        
        # Convert from W·h/m² to kWh/m²
        return insolation / 1000
    else:
        return 0.0

def calculate_optimal_panel_angle(lat: float, date: Optional[datetime.date] = None) -> float:
    """
    Calculate the optimal angle for solar panels at a given latitude and date.
    
    Args:
        lat: Latitude in degrees
        date: Date object (defaults to current date)
        
    Returns:
        float: Optimal tilt angle in degrees
    """
    if date is None:
        date = datetime.datetime.utcnow().date()
    
    # Day of year
    day_of_year = date.timetuple().tm_yday
    
    # Solar declination
    declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
    
    # Optimal angle is latitude minus declination
    optimal_angle = lat - declination
    
    # Ensure angle is between 0 and 90 degrees
    return max(0, min(90, optimal_angle))

def get_location_elevation(lat: float, lon: float) -> Optional[float]:
    """
    Get the elevation (altitude) for a given latitude and longitude.
    Uses the Open-Elevation API.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        
    Returns:
        float: Elevation in meters above sea level, or None if request fails
    """
    try:
        url = "https://api.open-elevation.com/api/v1/lookup"
        params = {
            'locations': f"{lat},{lon}"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'results' in data and len(data['results']) > 0:
            return data['results'][0]['elevation']
        return None
    except Exception:
        return None

def get_weather_data(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Get current weather data for a location.
    Uses the OpenWeatherMap API (requires API key).
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        
    Returns:
        Dict: Weather data or None if request fails
    """
    try:
        # Replace with your actual API key
        api_key = "YOUR_OPENWEATHERMAP_API_KEY"
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if response.status_code == 200:
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind']['deg'],
                'clouds': data['clouds']['all'],
                'weather_condition': data['weather'][0]['main'],
                'weather_description': data['weather'][0]['description'],
                'pressure': data['main']['pressure']
            }
        return None
    except Exception:
        return None

def calculate_distance_matrix(locations: List[Tuple[float, float]]) -> List[List[float]]:
    """
    Calculate a distance matrix between multiple locations.
    
    Args:
        locations: List of (latitude, longitude) tuples
        
    Returns:
        List[List[float]]: Matrix of distances in kilometers
    """
    n = len(locations)
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    
    for i in range(n):
        for j in range(i+1, n):
            lat1, lon1 = locations[i]
            lat2, lon2 = locations[j]
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            matrix[i][j] = distance
            matrix[j][i] = distance
    
    return matrix

def is_point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """
    Determine if a point is inside a polygon using the ray casting algorithm.
    
    Args:
        point: (latitude, longitude) tuple
        polygon: List of (latitude, longitude) tuples forming a polygon
        
    Returns:
        bool: True if point is inside polygon, False otherwise
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

def get_grid_carbon_intensity(country_code: str) -> Optional[float]:
    """
    Get the carbon intensity of the electricity grid for a given country.
    This is a simplified implementation - in production, use a real-time API.
    
    Args:
        country_code: ISO 3166-1 alpha-2 country code
        
    Returns:
        float: Carbon intensity in gCO2/kWh or None if not available
    """
    # Sample data - in production, use an API like Electricity Maps
    carbon_intensities = {
        'FR': 56,    # France (low due to nuclear)
        'DE': 350,   # Germany
        'US': 450,   # United States
        'CN': 620,   # China
        'IN': 700,   # India
        'AU': 550,   # Australia
        'GB': 280,   # United Kingdom
        'CA': 150,   # Canada
        'BR': 90,    # Brazil (low due to hydro)
        'SE': 30     # Sweden (low due to hydro and nuclear)
    }
    
    return carbon_intensities.get(country_code.upper())

def get_country_from_coordinates(lat: float, lon: float) -> Optional[str]:
    """
    Get the country code for a given latitude and longitude.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        
    Returns:
        str: ISO 3166-1 alpha-2 country code or None if not found
    """
    try:
        address = reverse_geocode(lat, lon)
        if address and 'country_code' in address:
            return address['country_code'].upper()
        return None
    except Exception:
        return None

def calculate_solar_potential(lat: float, lon: float, panel_area: float = 1.0, 
                             efficiency: float = 0.2) -> Dict[str, float]:
    """
    Calculate solar energy generation potential for a location.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        panel_area: Solar panel area in square meters
        efficiency: Solar panel efficiency (0-1)
        
    Returns:
        Dict: Contains daily, monthly, and annual generation potential in kWh
    """
    # Get current date
    today = datetime.datetime.utcnow().date()
    
    # Calculate for each month
    monthly_values = []
    for month in range(1, 13):
        # Middle of the month
        sample_date = datetime.date(today.year, month, 15)
        radiation = get_solar_radiation(lat, lon, sample_date)
        monthly_values.append(radiation * panel_area * efficiency * 30)  # Approximate days per month
    
    # Calculate daily (current day)
    daily = get_solar_radiation(lat, lon, today) * panel_area * efficiency
    
    # Calculate annual
    annual = sum(monthly_values)
    
    return {
        'daily_kwh': daily,
        'monthly_kwh': monthly_values,
        'annual_kwh': annual
    }