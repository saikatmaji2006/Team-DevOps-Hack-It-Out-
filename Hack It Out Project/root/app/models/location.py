import geopy.distance
from mongoengine import StringField, FloatField, BooleanField, ListField, DictField, DateTimeField, GeoPointField
from app.models.base import BaseDocument

class LocationType(StringField):
    SOLAR_FARM = "solar_farm"
    WIND_FARM = "wind_farm"
    HYBRID = "hybrid"
    MONITORING_STATION = "monitoring_station"
    GRID_CONNECTION = "grid_connection"

class Location(BaseDocument):
    name = StringField(required=True, max_length=255)
    slug = StringField(required=True, max_length=255, unique=True)
    coordinates = GeoPointField(required=True)
    
    location_type = StringField(choices=[
        LocationType.SOLAR_FARM,
        LocationType.WIND_FARM,
        LocationType.HYBRID,
        LocationType.MONITORING_STATION,
        LocationType.GRID_CONNECTION
    ], default=LocationType.MONITORING_STATION)
    
    country = StringField(required=True, max_length=100)
    region = StringField(max_length=100)
    city = StringField(max_length=100)
    postal_code = StringField(max_length=20)
    address = StringField(max_length=255)
    
    timezone = StringField(default="UTC", max_length=50)
    elevation = FloatField()
    terrain_type = StringField(max_length=100)
    
    is_active = BooleanField(default=True)
    is_public = BooleanField(default=False)
    
    capacity_kw = FloatField(min_value=0)
    commissioned_date = DateTimeField()
    decommissioned_date = DateTimeField()
    
    tags = ListField(StringField(max_length=50))
    metadata = DictField()
    
    owner_id = StringField()
    access_control = ListField(StringField())
    
    meta = {
        'indexes': [
            {'fields': ['name']},
            {'fields': ['slug'], 'unique': True},
            {'fields': ['coordinates'], 'geo': True},
            {'fields': [('country', 1), ('region', 1), ('city', 1)]},
            {'fields': ['location_type']},
            {'fields': ['is_active']},
            {'fields': ['owner_id']},
            {'fields': ['tags']},
        ],
        'ordering': ['name']
    }
    
    @property
    def latitude(self):
        return self.coordinates[1] if self.coordinates else None
    
    @property
    def longitude(self):
        return self.coordinates[0] if self.coordinates else None
    
    @classmethod
    def find_nearby(cls, lat, lng, radius_km=10, only_active=True):
        query = {
            'coordinates': {
                '$nearSphere': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [lng, lat]
                    },
                    '$maxDistance': radius_km * 1000
                }
            }
        }
        
        if only_active:
            query['is_active'] = True
            
        return cls.objects(__raw__=query)
    
    def distance_to(self, other_location):
        if not self.coordinates or not other_location.coordinates:
            return None
            
        return geopy.distance.geodesic(
            (self.latitude, self.longitude),
            (other_location.latitude, other_location.longitude)
        ).kilometers
    
    def to_geojson(self):
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude]
            },
            "properties": {
                "id": self.id,
                "name": self.name,
                "type": self.location_type,
                "country": self.country,
                "capacity_kw": self.capacity_kw,
                "is_active": self.is_active
            }
        }
    
    def get_weather_stations(self, max_distance_km=50):
        from app.models.weather import WeatherStation
        return WeatherStation.find_nearby(self.latitude, self.longitude, radius_km=max_distance_km)
    
    def get_grid_connections(self, max_distance_km=100):
        return Location.find_nearby(
            self.latitude, 
            self.longitude, 
            radius_km=max_distance_km
        ).filter(location_type=LocationType.GRID_CONNECTION)
    
    def calculate_solar_potential(self):
        if self.location_type not in [LocationType.SOLAR_FARM, LocationType.HYBRID]:
            return None
            
        from app.services.solar import calculate_solar_potential
        return calculate_solar_potential(self.latitude, self.longitude, self.elevation)
    
    def calculate_wind_potential(self):
        if self.location_type not in [LocationType.WIND_FARM, LocationType.HYBRID]:
            return None
            
        from app.services.wind import calculate_wind_potential
        return calculate_wind_potential(self.latitude, self.longitude, self.elevation, self.terrain_type)
    
    def __repr__(self):
        return f"<Location {self.name} ({self.latitude}, {self.longitude})>"

class WeatherStation(Location):
    station_id = StringField(required=True, unique=True)
    provider = StringField()
    equipment_type = StringField()
    measurement_height = FloatField()
    calibration_date = DateTimeField()
    sampling_rate = StringField()
    accuracy = DictField()
    
    meta = {
        'indexes': [
            {'fields': ['station_id'], 'unique': True},
            {'fields': ['provider']}
        ]
    }
    
    def __init__(self, *args, **kwargs):
        kwargs['location_type'] = LocationType.MONITORING_STATION
        super().__init__(*args, **kwargs)