from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
import json

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=schemas.ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[schemas.ProjectStatus] = None,
    zone_type: Optional[schemas.ZoneType] = None,
    db: Session = Depends(get_db)
):
    """Listar proyectos con paginación y filtros"""
    
    query = db.query(models.Project)
    
    # Aplicar filtros
    if status:
        query = query.filter(models.Project.status == status)
    if zone_type:
        query = query.filter(models.Project.zone_type == zone_type)
    
    # Contar total
    total = query.count()
    
    # Aplicar paginación
    offset = (page - 1) * size
    projects = query.order_by(models.Project.created_at.desc()).offset(offset).limit(size).all()
    
    # Calcular número de páginas
    pages = (total + size - 1) // size
    
    return schemas.ProjectListResponse(
        items=[schemas.Project.from_orm(p) for p in projects],
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@router.post("/", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo proyecto"""
    
    try:
        # Crear instancia del modelo
        db_project = models.Project(
            name=project.name,
            description=project.description,
            location=project.location,
            zone_type=project.zone_type,
            total_area=project.total_area,
            terrain_value=project.terrain_value,
            construction_cost_per_m2=project.construction_cost_per_m2,
            investment_horizon=project.investment_horizon,
            selling_price_per_m2=project.selling_price_per_m2,
            construction_time_months=project.construction_time_months,
            selling_time_months=project.selling_time_months,
            discount_rate=project.discount_rate,
            latitude=project.latitude,
            longitude=project.longitude
        )
        
        # Procesar geometría del lote si se proporciona
        if project.lot_polygon:
            db_project.lot_polygon = project.lot_polygon.dict()
        
        # Procesar bounds de imagen si se proporciona
        if project.image_bounds:
            db_project.image_bounds = [
                project.image_bounds.min_x,
                project.image_bounds.min_y,
                project.image_bounds.max_x,
                project.image_bounds.max_y
            ]
        
        # Calcular métricas básicas
        db_project.total_investment = project.terrain_value + (project.total_area * project.construction_cost_per_m2)
        
        # Guardar en base de datos
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        return schemas.Project.from_orm(db_project)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando proyecto: {str(e)}"
        )

@router.get("/{project_id}", response_model=schemas.Project)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Obtener proyecto por ID"""
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    return schemas.Project.from_orm(project)

@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int,
    project_update: schemas.ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar proyecto existente"""
    
    # Buscar proyecto
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    try:
        # Actualizar campos proporcionados
        update_data = project_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_project, field, value)
        
        # Recalcular total_investment si se modificaron valores relevantes
        if any(field in update_data for field in ['terrain_value', 'total_area', 'construction_cost_per_m2']):
            db_project.total_investment = db_project.terrain_value + (db_project.total_area * db_project.construction_cost_per_m2)
        
        db.commit()
        db.refresh(db_project)
        
        return schemas.Project.from_orm(db_project)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando proyecto: {str(e)}"
        )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar proyecto"""
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    try:
        db.delete(project)
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando proyecto: {str(e)}"
        )

@router.post("/{project_id}/duplicate", response_model=schemas.Project)
def duplicate_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Duplicar proyecto existente"""
    
    original_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    if not original_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    try:
        # Crear copia del proyecto
        project_data = {
            column.name: getattr(original_project, column.name)
            for column in original_project.__table__.columns
            if column.name not in ['id', 'created_at', 'updated_at']
        }
        
        # Modificar nombre
        project_data['name'] = f"{project_data['name']} (Copia)"
        project_data['status'] = models.ProjectStatus.DRAFT
        
        # Crear nueva instancia
        new_project = models.Project(**project_data)
        
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        return schemas.Project.from_orm(new_project)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error duplicando proyecto: {str(e)}"
        )
