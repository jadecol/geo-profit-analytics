# backend/app/routers/projects.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.database import get_db
from app import models, schemas
import json
from datetime import datetime  # AGREGADO: Import que faltaba

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

# ============================================
# NUEVAS FUNCIONALIDADES DE COMPARACIÓN
# ============================================

@router.post("/compare")
def compare_projects(
    project_ids: List[int],
    db: Session = Depends(get_db)
):
    """Comparar múltiples proyectos"""
    
    projects = db.query(models.Project).filter(
        models.Project.id.in_(project_ids)
    ).all()
    
    if len(projects) < 2:
        raise HTTPException(
            status_code=400,
            detail="Se requieren al menos 2 proyectos para comparar"
        )
    
    comparison_data = []
    
    for project in projects:
        # Obtener análisis más recientes
        financial_analysis = db.query(models.ProjectAnalysis).filter(
            models.ProjectAnalysis.project_id == project.id,
            models.ProjectAnalysis.analysis_type == "financial"
        ).order_by(models.ProjectAnalysis.created_at.desc()).first()
        
        geospatial_analysis = db.query(models.ProjectAnalysis).filter(
            models.ProjectAnalysis.project_id == project.id,
            models.ProjectAnalysis.analysis_type == "geospatial"
        ).order_by(models.ProjectAnalysis.created_at.desc()).first()
        
        sustainability_analysis = db.query(models.ProjectAnalysis).filter(
            models.ProjectAnalysis.project_id == project.id,
            models.ProjectAnalysis.analysis_type == "sustainability"
        ).order_by(models.ProjectAnalysis.created_at.desc()).first()
        
        # Calcular puntuación general
        scores = []
        
        if project.npv:
            npv_score = min(10, max(0, (project.npv / 1000000) * 5 + 5))
            scores.append(npv_score)
        
        if project.irr:
            irr_score = min(10, max(0, (project.irr / 0.15) * 10))
            scores.append(irr_score)
        
        if project.sustainability_score:
            scores.append(project.sustainability_score / 10)
        
        overall_score = sum(scores) / len(scores) if scores else 5.0
        
        comparison_data.append({
            "project": {
                "id": project.id,
                "name": project.name,
                "location": project.location,
                "total_area": project.total_area,
                "zone_type": project.zone_type,
                "status": project.status
            },
            "metrics": {
                "financial": {
                    "npv": project.npv or 0,
                    "irr": project.irr or 0,
                    "roi": ((project.npv or 0) / (project.total_investment or 1)) * 100 if project.total_investment else 0,
                    "payback_period": financial_analysis.results.get("payback_period", 0) if financial_analysis else 0
                },
                "geospatial": {
                    "location_score": geospatial_analysis.results.get("location_score", 5) if geospatial_analysis else 5,
                    "accessibility_score": geospatial_analysis.results.get("accessibility_score", 5) if geospatial_analysis else 5,
                    "buildability_percentage": project.buildability_percentage or 70
                },
                "sustainability": {
                    "overall_score": project.sustainability_score or 5,
                    "carbon_footprint": project.carbon_footprint or 0,
                    "energy_efficiency": sustainability_analysis.results.get("energy_efficiency", 5) if sustainability_analysis else 5
                },
                "overall_score": overall_score
            }
        })
    
    # Calcular rankings
    rankings = calculate_rankings(comparison_data)
    
    return {
        "projects": comparison_data,
        "rankings": rankings,
        "comparison_date": datetime.now(),
        "total_projects": len(projects)
    }

@router.get("/ranking")
def get_project_rankings(
    criteria: str = Query("overall", pattern="^(overall|npv|irr|sustainability|location)$"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Obtener ranking de proyectos según criterio"""
    
    query = db.query(models.Project)
    
    # Ordenar según criterio
    if criteria == "npv":
        query = query.filter(models.Project.npv.isnot(None)).order_by(models.Project.npv.desc())
    elif criteria == "irr":
        query = query.filter(models.Project.irr.isnot(None)).order_by(models.Project.irr.desc())
    elif criteria == "sustainability":
        query = query.filter(models.Project.sustainability_score.isnot(None)).order_by(models.Project.sustainability_score.desc())
    elif criteria == "location":
        # Aquí podrías usar un campo de puntuación de ubicación si lo tienes
        query = query.order_by(models.Project.id.desc())
    else:  # overall
        # Ordenar por una combinación de métricas
        # Nota: Esta consulta puede ser optimizada según tu DBMS
        query = query.order_by(models.Project.id.desc())  # Simplificado para evitar errores de SQL
    
    projects = query.limit(limit).all()
    
    ranking_data = []
    for index, project in enumerate(projects, 1):
        ranking_data.append({
            "rank": index,
            "project_id": project.id,
            "project_name": project.name,
            "location": project.location,
            "metrics": {
                "npv": project.npv,
                "irr": project.irr,
                "sustainability_score": project.sustainability_score,
                "total_area": project.total_area
            },
            "change": 0  # Podrías implementar cambio vs periodo anterior
        })
    
    return {
        "criteria": criteria,
        "rankings": ranking_data,
        "generated_at": datetime.now()
    }

def calculate_rankings(comparison_data: List[Dict]) -> Dict:
    """Calcular rankings por diferentes criterios"""
    
    # Ordenar por NPV
    npv_ranking = sorted(
        comparison_data, 
        key=lambda x: x["metrics"]["financial"]["npv"], 
        reverse=True
    )
    
    # Ordenar por TIR
    irr_ranking = sorted(
        comparison_data, 
        key=lambda x: x["metrics"]["financial"]["irr"], 
        reverse=True
    )
    
    # Ordenar por sostenibilidad
    sustainability_ranking = sorted(
        comparison_data, 
        key=lambda x: x["metrics"]["sustainability"]["overall_score"], 
        reverse=True
    )
    
    # Ordenar por puntuación general
    overall_ranking = sorted(
        comparison_data, 
        key=lambda x: x["metrics"]["overall_score"], 
        reverse=True
    )
    
    return {
        "by_npv": [p["project"]["name"] for p in npv_ranking],
        "by_irr": [p["project"]["name"] for p in irr_ranking],
        "by_sustainability": [p["project"]["name"] for p in sustainability_ranking],
        "by_overall": [p["project"]["name"] for p in overall_ranking],
        "winner": overall_ranking[0]["project"]["name"] if overall_ranking else None
    }

@router.post("/compare/export")
def export_comparison(
    request: dict,  # {projectIds: List[int], format: str}
    db: Session = Depends(get_db)
):
    """Exportar comparación de proyectos en diferentes formatos"""
    
    project_ids = request.get("projectIds", [])
    export_format = request.get("format", "json")
    
    # Obtener datos de comparación
    comparison_data = compare_projects(project_ids, db)
    
    if export_format == "json":
        return comparison_data
    elif export_format == "pdf":
        # Aquí implementarías la generación de PDF
        # Por ahora retornamos los datos en JSON
        return {
            "message": "PDF export not implemented yet",
            "data": comparison_data
        }
    elif export_format == "excel":
        # Aquí implementarías la generación de Excel
        # Por ahora retornamos los datos en JSON
        return {
            "message": "Excel export not implemented yet",
            "data": comparison_data
        }
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de exportación no soportado: {export_format}"
        )