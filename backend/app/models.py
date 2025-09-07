from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
import datetime
from app.database import Base  # Importación absoluta desde app.database

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    area = Column(Float)  # m²
    terrain_value = Column(Float)  # USD
    construction_cost = Column(Float)  # USD/m²
    investment_horizon = Column(Integer)  # años
    zone_type = Column(String)  # residential, commercial, mixed, industrial
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
