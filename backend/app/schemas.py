from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class ZoneType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MIXED = "mixed"
    INDUSTRIAL = "industrial"

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ANALYSIS = "analysis"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class AnalysisType(str, Enum):
    FINANCIAL = "financial"
    GEOSPATIAL = "geospatial"
    SUSTAINABILITY = "sustainability"

# Schemas auxiliares
class GeoJSONGeometry(BaseModel):
    type: str
    coordinates: List[List[List[float]]]

class BoundsCoordinates(BaseModel):
    min_x: float = Field(..., description="Longitud mínima")
    min_y: float = Field(..., description="Latitud mínima")
    max_x: float = Field(..., description="Longitud máxima")
    max_y: float = Field(..., description="Latitud máxima")

class ProjectPreferences(BaseModel):
    theme: str = "light"
    language: str = "es"
    auto_save: bool = True
    notifications: bool = True

# Schemas para Proyectos
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    location: str = Field(..., min_length=1, max_length=500)
    zone_type: ZoneType
    
    # Datos básicos del lote
    total_area: float = Field(..., gt=0, description="Área total en m²")
    terrain_value: float = Field(..., gt=0, description="Valor del terreno en USD")
    construction_cost_per_m2: float = Field(..., gt=0, description="Costo de construcción por m²")
    investment_horizon: int = Field(..., gt=0, le=50, description="Horizonte de inversión en años")
    
    # Datos opcionales para análisis avanzado
    selling_price_per_m2: Optional[float] = Field(None, gt=0)
    construction_time_months: int = Field(12, gt=0, le=60)
    selling_time_months: int = Field(12, gt=0, le=120)
    discount_rate: float = Field(0.12, ge=0, le=1)
    
    # Coordenadas
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

class ProjectCreate(ProjectBase):
    lot_polygon: Optional[GeoJSONGeometry] = None
    image_bounds: Optional[BoundsCoordinates] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = Field(None, min_length=1, max_length=500)
    zone_type: Optional[ZoneType] = None
    status: Optional[ProjectStatus] = None
    
    total_area: Optional[float] = Field(None, gt=0)
    terrain_value: Optional[float] = Field(None, gt=0)
    construction_cost_per_m2: Optional[float] = Field(None, gt=0)
    selling_price_per_m2: Optional[float] = Field(None, gt=0)
    
    construction_time_months: Optional[int] = Field(None, gt=0, le=60)
    selling_time_months: Optional[int] = Field(None, gt=0, le=120)
    discount_rate: Optional[float] = Field(None, ge=0, le=1)

class Project(ProjectBase):
    id: int
    status: ProjectStatus = ProjectStatus.DRAFT
    
    # Datos calculados
    buildable_area: Optional[float] = None
    total_investment: Optional[float] = None
    buildability_percentage: Optional[float] = None
    npv: Optional[float] = None
    irr: Optional[float] = None
    sustainability_score: Optional[float] = None
    carbon_footprint: Optional[float] = None
    
    # URLs de imagen
    satellite_image_url: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para análisis
class AnalysisRequest(BaseModel):
    analysis_types: List[AnalysisType] = [AnalysisType.FINANCIAL]
    include_sensitivity: bool = False
    include_optimization: bool = False
    custom_parameters: Optional[Dict[str, Any]] = None

class FinancialAnalysisResult(BaseModel):
    basic_metrics: Dict[str, Any]
    npv: float
    irr: Optional[float]
    roi_percentage: float
    cash_flows: List[float]
    sensitivity_analysis: Optional[Dict[str, Any]] = None
    optimization_results: Optional[Dict[str, Any]] = None

class GeospatialAnalysisResult(BaseModel):
    total_area: float
    buildable_area: float
    restricted_area: float
    buildability_percentage: float
    restrictions_applied: List[str]
    recommendations: List[str]
    visualization_layers: Dict[str, Any]

class SustainabilityAnalysisResult(BaseModel):
    total_score: float
    percentage: float
    sustainability_level: str
    category_scores: Dict[str, float]
    carbon_footprint: Dict[str, Any]
    certifications_eligible: List[str]
    improvement_opportunities: List[str]

class CompleteAnalysisResult(BaseModel):
    project_id: int
    financial: Optional[FinancialAnalysisResult] = None
    geospatial: Optional[GeospatialAnalysisResult] = None
    sustainability: Optional[SustainabilityAnalysisResult] = None
    execution_time_ms: int
    recommendations: List[str]
    risk_assessment: Dict[str, Any]

# Schemas para restricciones
class RestrictionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    #type: str = Field(..., regex="^(exclusion|limitation|buffer)$")
    type: str = Field(..., pattern="^(exclusion|limitation|buffer)$")
    geometry: GeoJSONGeometry
    reduction_factor: float = Field(1.0, ge=0, le=1)
    buffer_distance: float = Field(0.0, ge=0)
    description: Optional[str] = None
    source: Optional[str] = None

class RestrictionCreate(RestrictionBase):
    pass

class Restriction(RestrictionBase):
    id: int
    project_id: int
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schemas para imágenes satelitales
class SatelliteImageRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    zoom: int = Field(18, ge=1, le=20)
    width: int = Field(1024, ge=256, le=2048)
    height: int = Field(1024, ge=256, le=2048)
    #source: str = Field("mapbox", regex="^(mapbox|google)$")
    source: str = Field("mapbox", pattern="^(mapbox|google)$")

class SatelliteImageUpload(BaseModel):
    bounds: BoundsCoordinates
    description: Optional[str] = None

class SatelliteImage(BaseModel):
    id: int
    latitude: float
    longitude: float
    bounds: Optional[List[float]] = None
    source: str
    zoom_level: Optional[int] = None
    width: int
    height: int
    resolution_m_per_pixel: Optional[float] = None
    image_url: str
    file_size_bytes: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schemas para respuestas
class APIResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None
    errors: Optional[List[str]] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

class ProjectListResponse(BaseModel):
    items: List[Project]
    total: int
    page: int = 1
    size: int = 10
    pages: int

# Validators
# @validator('lot_polygon')
def validate_polygon(cls, v):
    if v and v.type != "Polygon":
        raise ValueError('Geometry must be a Polygon')
    return v

# Schemas para optimización
class OptimizationRequest(BaseModel):
    #target: str = Field("npv", regex="^(npv|roi|sustainability)$")
    target: str = Field("npv", pattern="^(npv|roi|sustainability)$")
    constraints: Optional[Dict[str, Any]] = None
    max_iterations: int = Field(100, ge=10, le=1000)

class OptimizationResult(BaseModel):
    optimized_parameters: Dict[str, float]
    improvement_percentage: float
    iterations: int
    convergence_achieved: bool
    recommendations: List[str]

# Esquemas para reportes
class ReportRequest(BaseModel):
    project_id: int
    sections: List[str] = ["executive_summary", "financial", "technical", "sustainability"]
    #format: str = Field("pdf", regex="^(pdf|html|json)$")
    format: str = Field("pdf", pattern="^(pdf|html|json)$")
    #language: str = Field("es", regex="^(es|en)$")
    language: str = Field("es", pattern="^(es|en)$")

class ReportResponse(BaseModel):
    report_id: str
    download_url: str
    expires_at: datetime
    file_size_bytes: int
