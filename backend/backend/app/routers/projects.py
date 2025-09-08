from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import time

from app.database import get_db
from app import models, schemas
from app.services.financial_service import FinancialService, ProjectFinancials
from app.services.geospatial_service import GeospatialService, LayerRestriction
from app.services.sustainability_service import SustainabilityService

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo proyecto"""
    try:
        # Calcular inversión total básica
        total_investment = project.terrain_value + (project.total_area * project.construction_cost_per_m2)
        
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
            longitude=project.longitude,
            total_investment=total_investment,
            lot_polygon=project.lot_polygon.dict() if project.lot_polygon else None,
            image_bounds=project.image_bounds.dict() if project.image_bounds else None
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear el proyecto: {str(e)}"
        )

@router.get("/", response_model=schemas.ProjectListResponse)
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    zone_type: Optional[schemas.ZoneType] = None,
    status: Optional[schemas.ProjectStatus] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar proyectos con filtros opcionales"""
    
    query = db.query(models.Project)
    
    # Aplicar filtros
    if zone_type:
        query = query.filter(models.Project.zone_type == zone_type)
    
    if status:
        query = query.filter(models.Project.status == status)
    
    if search:
        query = query.filter(
            models.Project.name.ilike(f"%{search}%") |
            models.Project.location.ilike(f"%{search}%")
        )
    
    # Contar total
    total = query.count()
    
    # Aplicar paginación
    projects = query.offset(skip).limit(limit).all()
    
    # Calcular número de páginas
    pages = (total + limit - 1) // limit
    
    return schemas.ProjectListResponse(
        items=projects,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=pages
    )

@router.get("/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Obtener un proyecto específico"""
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    return project

@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int,
    project_update: schemas.ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un proyecto existente"""
    
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
        
        # Recalcular inversión total si es necesario
        if any(field in update_data for field in ['terrain_value', 'total_area', 'construction_cost_per_m2']):
            db_project.total_investment = (
                db_project.terrain_value + 
                (db_project.total_area * db_project.construction_cost_per_m2)
            )
        
        db.commit()
        db.refresh(db_project)
        return db_project
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar el proyecto: {str(e)}"
        )

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Eliminar un proyecto"""
    
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    try:
        # Eliminar análisis relacionados
        db.query(models.ProjectAnalysis).filter(
            models.ProjectAnalysis.project_id == project_id
        ).delete()
        
        # Eliminar restricciones relacionadas
        db.query(models.ProjectRestriction).filter(
            models.ProjectRestriction.project_id == project_id
        ).delete()
        
        # Eliminar proyecto
        db.delete(db_project)
        db.commit()
        
        return {"message": "Proyecto eliminado exitosamente"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar el proyecto: {str(e)}"
        )

@router.get("/{project_id}/summary")
def get_project_summary(project_id: int, db: Session = Depends(get_db)):
    """Obtener resumen ejecutivo del proyecto"""
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Obtener últimos análisis
    latest_analyses = {}
    for analysis_type in ["financial", "geospatial", "sustainability"]:
        analysis = db.query(models.ProjectAnalysis).filter(
            models.ProjectAnalysis.project_id == project_id,
            models.ProjectAnalysis.analysis_type == analysis_type
        ).order_by(models.ProjectAnalysis.created_at.desc()).first()
        
        if analysis:
            latest_analyses[analysis_type] = analysis.results
    
    # Calcular indicadores clave
    key_indicators = {
        "total_investment": project.total_investment,
        "npv": project.npv,
        "irr": project.irr,
        "buildability_percentage": project.buildability_percentage,
        "sustainability_score": project.sustainability_score,
        "carbon_footprint": project.carbon_footprint
    }
    
    # Generar recomendaciones generales
    recommendations = []
    
    if project.npv and project.npv < 0:
        recommendations.append("VPN negativo - Revisar viabilidad económica")
    elif project.npv and project.npv > 0:
        recommendations.append("Proyecto económicamente viable")
    
    if project.buildability_percentage and project.buildability_percentage < 30:
        recommendations.append("Bajo aprovechamiento del lote - Revisar restricciones")
    elif project.buildability_percentage and project.buildability_percentage > 70:
        recommendations.append("Excelente aprovechamiento del terreno")
    
    if project.sustainability_score and project.sustainability_score < 60:
        recommendations.append("Considerar mejoras en sostenibilidad")
    elif project.sustainability_score and project.sustainability_score > 80:
        recommendations.append("Proyecto altamente sostenible")
    
    return {
        "project_info": {
            "id": project.id,
            "name": project.name,
            "location": project.location,
            "status": project.status,
            "zone_type": project.zone_type,
            "total_area": project.total_area
        },
        "key_indicators": key_indicators,
        "latest_analyses": latest_analyses,
        "recommendations": recommendations,
        "last_updated": project.updated_at
    }

@router.get("/{project_id}/restrictions", response_model=List[schemas.Restriction])
def get_project_restrictions(project_id: int, db: Session = Depends(get_db)):
    """Obtener restricciones del proyecto"""
    
    # Verificar que el proyecto existe
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    restrictions = db.query(models.ProjectRestriction).filter(
        models.ProjectRestriction.project_id == project_id,
        models.ProjectRestriction.is_active == True
    ).all()
    
    return restrictions

@router.post("/{project_id}/restrictions", response_model=schemas.Restriction)
def add_project_restriction(
    project_id: int,
    restriction: schemas.RestrictionCreate,
    db: Session = Depends(get_db)
):
    """Agregar restricción al proyecto"""
    
    # Verificar que el proyecto existe
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    try:
        db_restriction = models.ProjectRestriction(
            project_id=project_id,
            name=restriction.name,
            type=restriction.type,
            geometry=restriction.geometry.dict(),
            reduction_factor=restriction.reduction_factor,
            buffer_distance=restriction.buffer_distance,
            description=restriction.description,
            source=restriction.source
        )
        
        db.add(db_restriction)
        db.commit()
        db.refresh(db_restriction)
        
        return db_restriction
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al agregar restricción: {str(e)}"
        )

@router.delete("/{project_id}/restrictions/{restriction_id}")
def remove_project_restriction(
    project_id: int, 
    restriction_id: int, 
    db: Session = Depends(get_db)
):
    """Eliminar restricción del proyecto"""
    
    restriction = db.query(models.ProjectRestriction).filter(
        models.ProjectRestriction.id == restriction_id,
        models.ProjectRestriction.project_id == project_id
    ).first()
    
    if not restriction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restricción no encontrada"
        )
    
    try:
        # En lugar de eliminar, marcar como inactiva
        restriction.is_active = False
        db.commit()
        
        return {"message": "Restricción eliminada exitosamente"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar restricción: {str(e)}"
        )

@router.post("/{project_id}/duplicate", response_model=schemas.Project)
def duplicate_project(project_id: int, db: Session = Depends(get_db)):
    """Duplicar un proyecto existente"""
    
    original_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not original_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    try:
        # Crear copia del proyecto
        new_project = models.Project(
            name=f"{original_project.name} - Copia",
            description=original_project.description,
            location=original_project.location,
            zone_type=original_project.zone_type,
            total_area=original_project.total_area,
            terrain_value=original_project.terrain_value,
            construction_cost_per_m2=original_project.construction_cost_per_m2,
            investment_horizon=original_project.investment_horizon,
            selling_price_per_m2=original_project.selling_price_per_m2,
            construction_time_months=original_project.construction_time_months,
            selling_time_months=original_project.selling_time_months,
            discount_rate=original_project.discount_rate,
            latitude=original_project.latitude,
            longitude=original_project.longitude,
            total_investment=original_project.total_investment,
            lot_polygon=original_project.lot_polygon,
            image_bounds=original_project.image_bounds,
            status=models.ProjectStatus.DRAFT
        )
        
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        # Copiar restricciones activas
        restrictions = db.query(models.ProjectRestriction).filter(
            models.ProjectRestriction.project_id == project_id,
            models.ProjectRestriction.is_active == True
        ).all()
        
        for restriction in restrictions:
            new_restriction = models.ProjectRestriction(
                project_id=new_project.id,
                name=restriction.name,
                type=restriction.type,
                geometry=restriction.geometry,
                reduction_factor=restriction.reduction_factor,
                buffer_distance=restriction.buffer_distance,
                description=restriction.description,
                source=restriction.source
            )
            db.add(new_restriction)
        
        db.commit()
        
        return new_project
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al duplicar proyecto: {str(e)}"
        )