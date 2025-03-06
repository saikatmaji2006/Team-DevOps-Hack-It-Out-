import datetime
from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    String,
    CheckConstraint,
    ForeignKey,
    Index,
    func,
    and_,
    case,
    extract,
    text
)
from sqlalchemy.orm import declarative_base, validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.dialects.postgresql import JSONB
from typing import Dict, List, Optional, Tuple, Union

Base = declarative_base()

class Energy(Base):
    __tablename__ = 'energy_readings'
    __table_args__ = (
        CheckConstraint("value >= 0", name="ck_energy_value_nonnegative"),
        CheckConstraint("energy_type in ('consumption', 'production')", name="ck_energy_type_valid"),
        CheckConstraint("source in ('solar', 'grid', 'wind', 'battery', 'other')", name="ck_energy_source_valid"),
        Index('ix_energy_readings_timestamp', 'timestamp'),
        Index('ix_energy_readings_device_id', 'device_id'),
        Index('ix_energy_readings_energy_type', 'energy_type'),
        Index('ix_energy_readings_source', 'source'),
        Index('ix_energy_readings_composite', 'device_id', 'energy_type', 'timestamp'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    energy_type = Column(String(20), nullable=False, default='consumption')
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=True)
    cost = Column(Float, nullable=True)
    source = Column(String(20), nullable=True, default='grid')
    efficiency = Column(Float, nullable=True)
    metadata = Column(JSONB, nullable=True)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    
    def __repr__(self):
        return (
            f"<Energy(id={self.id}, value={self.value}, timestamp={self.timestamp}, "
            f"energy_type={self.energy_type}, device_id={self.device_id}, "
            f"source={self.source})>"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "value": self.value,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "energy_type": self.energy_type,
            "device_id": self.device_id,
            "energy_joules": self.energy_joules,
            "cost": self.cost,
            "source": self.source,
            "carbon_footprint": self.carbon_footprint,
            "efficiency": self.efficiency,
            "metadata": self.metadata,
            "location_id": self.location_id,
            "is_peak_hour": self.is_peak_hour(),
            "energy_category": self.energy_category
        }

    @hybrid_property
    def energy_joules(self):
        return self.value * 3.6e6
    
    @energy_joules.expression
    def energy_joules(cls):
        return cls.value * 3.6e6
    
    @hybrid_property
    def carbon_footprint(self):
        emissions_factor = {
            'grid': 0.5,
            'solar': 0.05,
            'wind': 0.02,
            'battery': 0.1,
            'other': 0.3
        }
        
        if self.energy_type == 'consumption':
            return self.value * emissions_factor.get(self.source, 0.3)
        else:
            return -1 * self.value * emissions_factor.get(self.source, 0.3)
    
    @carbon_footprint.expression
    def carbon_footprint(cls):
        return case(
            {
                'grid': 0.5,
                'solar': 0.05,
                'wind': 0.02,
                'battery': 0.1,
                'other': 0.3
            },
            value=cls.source,
            else_=0.3
        ) * case(
            [(cls.energy_type == 'consumption', cls.value)],
            else_=-cls.value
        )
    
    @hybrid_property
    def energy_category(self):
        if self.value < 10:
            return 'low'
        elif self.value < 50:
            return 'medium'
        else:
            return 'high'
    
    @energy_category.expression
    def energy_category(cls):
        return case(
            [(cls.value < 10, 'low'),
             (cls.value < 50, 'medium')],
            else_='high'
        )

    def calculate_cost(self, rate_per_kwh=0.15, peak_multiplier=1.5):
        if self.cost is not None:
            return self.cost
        
        base_rate = rate_per_kwh
        if self.is_peak_hour():
            base_rate *= peak_multiplier
            
        if self.energy_type == 'consumption':
            return self.value * base_rate
        else:
            return self.value * (base_rate * 0.8)

    @hybrid_method
    def is_peak_hour(self):
        hour = self.timestamp.hour
        return 7 <= hour <= 10 or 17 <= hour <= 21
    
    @is_peak_hour.expression
    def is_peak_hour(cls):
        hour = extract('hour', cls.timestamp)
        return or_(
            and_(hour >= 7, hour <= 10),
            and_(hour >= 17, hour <= 21)
        )

    @validates("value")
    def validate_value(self, key, value):
        if value < 0:
            raise ValueError("Energy value must be non-negative")
        return value

    @validates("energy_type")
    def validate_energy_type(self, key, energy_type):
        if energy_type not in ("consumption", "production"):
            raise ValueError("energy_type must be either 'consumption' or 'production'")
        return energy_type
    
    @validates("source")
    def validate_source(self, key, source):
        if source and source not in ("solar", "grid", "wind", "battery", "other"):
            raise ValueError("source must be one of: solar, grid, wind, battery, other")
        return source
    
    @validates("efficiency")
    def validate_efficiency(self, key, efficiency):
        if efficiency is not None and (efficiency < 0 or efficiency > 1):
            raise ValueError("Efficiency must be between 0 and 1")
        return efficiency

    @classmethod
    def query_by_date_range(cls, session, start_date, end_date):
        return session.query(cls).filter(cls.timestamp >= start_date, cls.timestamp < end_date).all()
    
    @classmethod
    def get_total_consumption(cls, session, start_date=None, end_date=None, device_id=None, source=None):
        query = session.query(func.sum(cls.value)).filter(cls.energy_type == 'consumption')
        
        if start_date:
            query = query.filter(cls.timestamp >= start_date)
        if end_date:
            query = query.filter(cls.timestamp < end_date)
        if device_id:
            query = query.filter(cls.device_id == device_id)
        if source:
            query = query.filter(cls.source == source)
            
        result = query.scalar()
        return result if result is not None else 0.0
    
    @classmethod
    def get_total_production(cls, session, start_date=None, end_date=None, device_id=None, source=None):
        query = session.query(func.sum(cls.value)).filter(cls.energy_type == 'production')
        
        if start_date:
            query = query.filter(cls.timestamp >= start_date)
        if end_date:
            query = query.filter(cls.timestamp < end_date)
        if device_id:
            query = query.filter(cls.device_id == device_id)
        if source:
            query = query.filter(cls.source == source)
            
        result = query.scalar()
        return result if result is not None else 0.0
    
    @classmethod
    def get_energy_balance(cls, session, start_date=None, end_date=None, device_id=None):
        production = cls.get_total_production(session, start_date, end_date, device_id)
        consumption = cls.get_total_consumption(session, start_date, end_date, device_id)
        return production - consumption
    
    @classmethod
    def get_hourly_aggregates(cls, session, date, device_id=None):
        query = session.query(
            extract('hour', cls.timestamp).label('hour'),
            func.sum(case([(cls.energy_type == 'consumption', cls.value)], else_=0)).label('consumption'),
            func.sum(case([(cls.energy_type == 'production', cls.value)], else_=0)).label('production')
        ).filter(
            func.date(cls.timestamp) == date
        ).group_by(
            extract('hour', cls.timestamp)
        ).order_by(
            extract('hour', cls.timestamp)
        )
        
        if device_id:
            query = query.filter(cls.device_id == device_id)
            
        return query.all()
    
    @classmethod
    def get_source_distribution(cls, session, start_date=None, end_date=None):
        query = session.query(
            cls.source,
            func.sum(cls.value).label('total_energy')
        ).group_by(
            cls.source
        )
        
        if start_date:
            query = query.filter(cls.timestamp >= start_date)
        if end_date:
            query = query.filter(cls.timestamp < end_date)
            
        return {row.source: row.total_energy for row in query.all()}
    
    @classmethod
    def calculate_efficiency_metrics(cls, session, device_id=None):
        subquery = session.query(
            cls.device_id,
            func.sum(case([(cls.energy_type == 'production', cls.value)], else_=0)).label('total_production'),
            func.sum(case([(cls.energy_type == 'consumption', cls.value)], else_=0)).label('total_consumption')
        ).group_by(
            cls.device_id
        )
        
        if device_id:
            subquery = subquery.filter(cls.device_id == device_id)
            
        subquery = subquery.subquery()
        
        query = session.query(
            subquery.c.device_id,
            subquery.c.total_production,
            subquery.c.total_consumption,
            (subquery.c.total_production / func.nullif(subquery.c.total_consumption, 0)).label('efficiency_ratio')
        )
        
        return query.all()
    
    @classmethod
    def detect_anomalies(cls, session, device_id, lookback_days=30, threshold=2.0):
        end_date = datetime.datetime.utcnow()
        start_date = end_date - datetime.timedelta(days=lookback_days)
        
        avg_query = session.query(
            func.avg(cls.value).label('avg_value'),
            func.stddev(cls.value).label('stddev_value')
        ).filter(
            cls.device_id == device_id,
            cls.timestamp >= start_date,
            cls.timestamp < end_date
        )
        
        avg_result = avg_query.first()
        if not avg_result or avg_result.avg_value is None:
            return []
        
        avg_value = avg_result.avg_value
        stddev_value = avg_result.stddev_value or 0.1  # Prevent division by zero
        
        anomaly_query = session.query(cls).filter(
            cls.device_id == device_id,
            cls.timestamp >= start_date,
            func.abs(cls.value - avg_value) > (threshold * stddev_value)
        ).order_by(cls.timestamp.desc())
        
        return anomaly_query.all()
    
    @classmethod
    def forecast_energy_usage(cls, session, device_id, days_ahead=7):
        today = datetime.datetime.utcnow().date()
        
        # Get historical data for the same weekday
        historical_data = []
        for i in range(4):  # Look at 4 weeks of historical data
            historical_date = today - datetime.timedelta(days=(7 * i))
            daily_total = cls.get_total_consumption(
                session, 
                start_date=datetime.datetime.combine(historical_date, datetime.time.min),
                end_date=datetime.datetime.combine(historical_date, datetime.time.max),
                device_id=device_id
            )
            historical_data.append(daily_total)
        
        # Simple average-based forecast
        if not historical_data:
            return []
            
        avg_consumption = sum(historical_data) / len(historical_data)
        
        forecast = []
        for i in range(1, days_ahead + 1):
            forecast_date = today + datetime.timedelta(days=i)
            forecast.append({
                'date': forecast_date.isoformat(),
                'forecasted_consumption': avg_consumption
            })
            
        return forecast

if __name__ == "__main__":
    sample_consumption = Energy(value=50.0, energy_type="consumption", device_id=1, source="grid", efficiency=0.85)
    sample_production = Energy(value=30.0, energy_type="production", device_id=2, source="solar", efficiency=0.92)
    
    print("=== Energy Model Demonstration ===")
    print(f"Consumption: {sample_consumption}")
    print(f"Production: {sample_production}")
    
    print("\n=== Energy Details ===")
    print(f"Consumption in Joules: {sample_consumption.energy_joules}")
    print(f"Production in Joules: {sample_production.energy_joules}")
    
    print("\n=== Carbon Footprint ===")
    print(f"Consumption carbon footprint: {sample_consumption.carbon_footprint} kg CO2")
    print(f"Production carbon footprint: {sample_production.carbon_footprint} kg CO2")
    
    print("\n=== Cost Calculation ===")
    print(f"Consumption cost: ${sample_consumption.calculate_cost():.2f}")
    print(f"Production value: ${sample_production.calculate_cost():.2f}")
    
    print("\n=== Energy Category ===")
    print(f"Consumption category: {sample_consumption.energy_category}")
    print(f"Production category: {sample_production.energy_category}")
    
    print("\n=== Peak Hour Detection ===")
    peak_hour_sample = Energy(
        value=75.0, 
        energy_type="consumption", 
        timestamp=datetime.datetime.now().replace(hour=18, minute=30)
    )
    off_peak_sample = Energy(
        value=25.0, 
        energy_type="consumption",
    print(f"Consumption category: {sample_consumption.energy_category}")
    print(f"Production category: {sample_production.energy_category}")
    
    print("\n=== Peak Hour Detection ===")
    peak_hour_sample = Energy(
        value=75.0, 
        energy_type="consumption", 
        timestamp=datetime.datetime.now().replace(hour=18, minute=30)
    )
    off_peak_sample = Energy(
        value=25.0, 
        energy_type="consumption", 
        timestamp=datetime.datetime.now().replace(hour=14, minute=15)
    )
    print(f"Peak hour sample (18:30): Is peak hour? {peak_hour_sample.is_peak_hour()}")
    print(f"Off-peak sample (14:15): Is peak hour? {off_peak_sample.is_peak_hour()}")
    print(f"Peak hour cost: ${peak_hour_sample.calculate_cost(rate_per_kwh=0.15, peak_multiplier=1.5):.2f}")
    print(f"Off-peak hour cost: ${off_peak_sample.calculate_cost(rate_per_kwh=0.15, peak_multiplier=1.5):.2f}")
    
    print("\n=== Energy Efficiency ===")
    print(f"Consumption efficiency: {sample_consumption.efficiency * 100:.1f}%")
    print(f"Production efficiency: {sample_production.efficiency * 100:.1f}%")
    
    print("\n=== Advanced Usage Examples ===")
    # Create samples with metadata
    metadata_sample = Energy(
        value=42.5,
        energy_type="consumption",
        source="grid",
        metadata={
            "voltage": 220,
            "current": 10.2,
            "power_factor": 0.95,
            "phase": "three-phase",
            "grid_stability": "stable"
        }
    )
    print(f"Sample with metadata: {metadata_sample}")
    print(f"Metadata fields: {', '.join(metadata_sample.metadata.keys())}")
    print(f"Voltage: {metadata_sample.metadata.get('voltage')}V")
    print(f"Current: {metadata_sample.metadata.get('current')}A")
    
    # Demonstrate time-based samples
    print("\n=== Time Series Data ===")
    now = datetime.datetime.now()
    time_series = [
        Energy(
            value=20 + i * 5,
            energy_type="consumption" if i % 3 != 0 else "production",
            source="grid" if i % 2 == 0 else "solar",
            timestamp=now - datetime.timedelta(hours=i)
        )
        for i in range(24)
    ]
    
    # Calculate daily totals
    consumption_total = sum(sample.value for sample in time_series if sample.energy_type == "consumption")
    production_total = sum(sample.value for sample in time_series if sample.energy_type == "production")
    balance = production_total - consumption_total
    
    print(f"24-hour consumption: {consumption_total:.1f} kWh")
    print(f"24-hour production: {production_total:.1f} kWh")
    print(f"Energy balance: {balance:.1f} kWh ({'surplus' if balance >= 0 else 'deficit'})")
    
    # Source distribution
    sources = {}
    for sample in time_series:
        sources[sample.source] = sources.get(sample.source, 0) + sample.value
    
    print("\n=== Energy Source Distribution ===")
    for source, total in sources.items():
        print(f"{source.capitalize()}: {total:.1f} kWh ({total/sum(sources.values())*100:.1f}%)")
    
    # Carbon footprint calculation
    total_footprint = sum(sample.carbon_footprint for sample in time_series)
    print(f"\nTotal carbon footprint: {total_footprint:.2f} kg CO2")
    
    # Demonstrate anomaly detection
    print("\n=== Anomaly Detection Simulation ===")
    normal_values = [50, 48, 52, 49, 51, 47, 53]
    anomaly_values = [50, 48, 120, 49, 51, 47, 53]  # 120 is an anomaly
    
    mean = sum(normal_values) / len(normal_values)
    stddev = (sum((x - mean) ** 2 for x in normal_values) / len(normal_values)) ** 0.5
    
    print(f"Normal values: {normal_values}")
    print(f"Anomaly values: {anomaly_values}")
    print(f"Mean: {mean:.2f}, Standard Deviation: {stddev:.2f}")
    
    threshold = 2.0
    for i, value in enumerate(anomaly_values):
        is_anomaly = abs(value - mean) > (threshold * stddev)
        print(f"Value {value}: {'ANOMALY DETECTED' if is_anomaly else 'normal'}")
    
    print("\n=== Energy Forecast Simulation ===")
    historical_data = [45, 48, 42, 46]  # kWh for past 4 same weekdays
    avg_consumption = sum(historical_data) / len(historical_data)
    
    print(f"Historical consumption data: {historical_data}")
    print(f"Average consumption: {avg_consumption:.2f} kWh")
    print("7-day forecast:")
    
    for i in range(1, 8):
        # Simple forecast with random variation
        variation = (datetime.datetime.now().microsecond % 20 - 10) / 100  # -10% to +10%
        forecast = avg_consumption * (1 + variation)
        forecast_date = (datetime.datetime.now() + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        print(f"  {forecast_date}: {forecast:.2f} kWh")
    