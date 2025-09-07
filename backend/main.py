# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from dotenv import load_dotenv
from . import models, schemas
from .database import engine, get_db
from sqlalchemy.orm import Session

# Cargar variables de entorno
load_dotenv()

# Crear tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GeoProfit Analytics API", 
    version="0.1.0",
    description="Sistema de análisis de viabilidad de proyectos inmobiliarios"
)

# Configurar CORS desde variables de entorno
origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not origins or origins == [""]:
    origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "GeoProfit Analytics API",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    # Lógica para crear proyecto
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects