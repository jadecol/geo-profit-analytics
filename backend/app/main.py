from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import os

from app import models, schemas
from app.database import engine, get_db
from app.config import settings

# Importar todos los routers
from app.routers import projects, analysis, reports, satellite

# Crear tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GeoProfit Analytics API", 
    version="0.1.0",
    description="Sistema de análisis de viabilidad de proyectos inmobiliarios",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Configurar CORS
origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Registrar todos los routers
app.include_router(projects.router)
app.include_router(analysis.router)
app.include_router(reports.router)
app.include_router(satellite.router)

# Middleware para manejo de errores
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error en la base de datos"}
    )

@app.get("/")
def read_root():
    return {
        "message": "GeoProfit Analytics API",
        "version": "0.1.0",
        "environment": settings.environment,
        "status": "running",
        "features": [
            "Financial Analysis (NPV, IRR)",
            "Geospatial Analysis",
            "Sustainability Assessment",
            "Satellite Image Integration",
            "Report Generation"
        ],
        "endpoints": {
            "documentation": "/docs",
            "health": "/health",
            "projects": "/projects",
            "analysis": "/analysis",
            "reports": "/reports",
            "satellite": "/satellite"
        }
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Probar conexión a la base de datos
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)}
        )

@app.get("/api/info")
def api_info():
    """Información completa sobre la API"""
    return {
        "api_name": "GeoProfit Analytics",
        "version": "0.1.0",
        "description": "Plataforma integral de análisis de viabilidad para proyectos urbano-arquitectónicos",
        "features": {
            "financial": {
                "npv": "Net Present Value calculation",
                "irr": "Internal Rate of Return",
                "sensitivity": "Sensitivity analysis",
                "optimization": "Project optimization"
            },
            "geospatial": {
                "restrictions": "Environmental and urban restrictions",
                "buildability": "Buildability analysis",
                "terrain": "Terrain suitability assessment"
            },
            "sustainability": {
                "environmental": "Environmental impact assessment",
                "social": "Social impact evaluation",
                "economic": "Economic sustainability metrics",
                "certifications": ["LEED", "BREEAM", "CASA Colombia", "EDGE"]
            },
            "satellite": {
                "providers": ["Mapbox", "Google Maps"],
                "upload": "Custom image upload support",
                "georeferencing": "GeoTIFF support"
            }
        },
        "endpoints": {
            "projects": {
                "base": "/projects",
                "operations": ["GET", "POST", "PUT", "DELETE"],
                "features": ["CRUD", "Filtering", "Pagination", "Duplication"]
            },
            "analysis": {
                "base": "/analysis",
                "types": ["financial", "geospatial", "sustainability"],
                "operations": ["run", "optimize", "compare", "history"]
            },
            "reports": {
                "base": "/reports",
                "formats": ["JSON", "HTML", "PDF"],
                "types": ["executive_summary", "financial_dashboard", "sustainability_report"]
            },
            "satellite": {
                "base": "/satellite",
                "sources": ["mapbox", "google", "upload"],
                "operations": ["fetch", "upload", "download", "search"]
            }
        },
        "authentication": "JWT (pending implementation)",
        "rate_limiting": "Not implemented yet",
        "caching": "Redis support (pending)",
        "database": "PostgreSQL with SQLAlchemy ORM",
        "external_integrations": {
            "maps": ["Mapbox API", "Google Maps API"],
            "future": ["Catastro Colombia", "IGAC", "Weather APIs"]
        }
    }
