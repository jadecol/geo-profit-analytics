from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class ZoneType(enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MIXED = "mixed"
    INDUSTRIAL = "industrial"

class ProjectStatus(enum.Enum):
    DRAFT = "draft"
    ANALYSIS = "analysis"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text)
    location = Column(String(500), nullable=False)
    #status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    status = Column(String(50), default='draft')
    
    # Geometría del lote
    lot_polygon = Column(JSON)  # GeoJSON del polígono
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Datos del proyecto
    total_area = Column(Float, nullable=False)  # m²
    buildable_area = Column(Float)  # m² calculado
    terrain_value = Column(Float, nullable=False)  # USD
    construction_cost_per_m2 = Column(Float, nullable=False)  # USD/m²
    investment_horizon = Column(Integer, nullable=False)  # años
    #zone_type = Column(Enum(ZoneType), nullable=False)
    zone_type = Column(String(50), nullable=False)
    
    # Datos adicionales para análisis avanzado
    selling_price_per_m2 = Column(Float)  # USD/m²
    construction_time_months = Column(Integer, default=12)
    selling_time_months = Column(Integer, default=12)
    discount_rate = Column(Float, default=0.12)  # 12% anual
    
    # Imagen satelital
    satellite_image_url = Column(String(500))
    image_bounds = Column(JSON)  # [min_x, min_y, max_x, max_y]
    
    # Resultados calculados
    total_investment = Column(Float)
    buildability_percentage = Column(Float)
    npv = Column(Float)
    irr = Column(Float)
    sustainability_score = Column(Float)
    carbon_footprint = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    analyses = relationship("ProjectAnalysis", back_populates="project")
    restrictions = relationship("ProjectRestriction", back_populates="project")
    
    def __repr__(self):
        return f"<Project(name='{self.name}', status='{self.status}')>"

class ProjectAnalysis(Base):
    __tablename__ = "project_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    analysis_type = Column(String(50), nullable=False)  # 'financial', 'geospatial', 'sustainability'
    
    # Resultados del análisis
    results = Column(JSON)  # Almacenar resultados completos en JSON
    recommendations = Column(JSON)  # Lista de recomendaciones
    
    # Metadatos
    version = Column(String(20), default="1.0")
    execution_time_ms = Column(Integer)  # Tiempo de ejecución en ms
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación
    project = relationship("Project", back_populates="analyses")

class ProjectRestriction(Base):
    __tablename__ = "project_restrictions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Datos de la restricción
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # 'exclusion', 'limitation', 'buffer'
    geometry = Column(JSON)  # GeoJSON de la restricción
    reduction_factor = Column(Float, default=1.0)
    buffer_distance = Column(Float, default=0.0)
    description = Column(Text)
    
    # Metadatos
    source = Column(String(100))  # Fuente de la restricción
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación
    project = relationship("Project", back_populates="restrictions")

class SatelliteImage(Base):
    __tablename__ = "satellite_images"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Ubicación
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    bounds = Column(JSON)  # [min_x, min_y, max_x, max_y]
    
    # Metadatos de la imagen
    source = Column(String(50))  # 'mapbox', 'google', 'uploaded'
    zoom_level = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    resolution_m_per_pixel = Column(Float)
    
    # Almacenamiento
    image_path = Column(String(500))  # Ruta local del archivo
    image_url = Column(String(500))   # URL de acceso
    file_size_bytes = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SatelliteImage(source='{self.source}', lat={self.latitude}, lon={self.longitude})>"

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)
    
    # Datos de la sesión
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Configuraciones de usuario
    preferences = Column(JSON)  # Tema, idioma, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<UserSession(session_id='{self.session_id[:8]}...')>"