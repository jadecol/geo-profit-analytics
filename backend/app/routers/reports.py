from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import json

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/{project_id}/generate", response_model=schemas.ReportResponse)
def generate_project_report(
    project_id: int,
    report_request: schemas.ReportRequest,
    db: Session = Depends(get_db)
):
    """Generar reporte del proyecto"""
    
    # Verificar que el proyecto existe
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    try:
        # Obtener análisis más recientes
        latest_analyses = {}
        for analysis_type in ["financial", "geospatial", "sustainability"]:
            analysis = db.query(models.ProjectAnalysis).filter(
                models.ProjectAnalysis.project_id == project_id,
                models.ProjectAnalysis.analysis_type == analysis_type
            ).order_by(models.ProjectAnalysis.created_at.desc()).first()
            
            if analysis:
                latest_analyses[analysis_type] = analysis.results
        
        # Generar contenido del reporte
        report_content = {
            "project_info": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "location": project.location,
                "zone_type": project.zone_type.value,
                "total_area": project.total_area,
                "status": project.status.value,
                "created_at": project.created_at.isoformat()
            },
            "executive_summary": _generate_executive_summary(project, latest_analyses),
            "financial_analysis": latest_analyses.get("financial", {}),
            "geospatial_analysis": latest_analyses.get("geospatial", {}),
            "sustainability_analysis": latest_analyses.get("sustainability", {}),
            "recommendations": _generate_recommendations(latest_analyses),
            "generated_at": datetime.now().isoformat(),
            "language": report_request.language,
            "format": report_request.format
        }
        
        # En una implementación real, aquí se generaría el PDF/HTML
        report_id = f"report_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Por ahora, devolvemos el JSON y una URL simulada
        return schemas.ReportResponse(
            report_id=report_id,
            download_url=f"/reports/download/{report_id}",
            expires_at=datetime.now(),
            file_size_bytes=len(json.dumps(report_content))
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando reporte: {str(e)}"
        )

@router.get("/{project_id}/summary")
def get_project_summary(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Obtener resumen ejecutivo del proyecto"""
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "location": project.location,
            "total_area": project.total_area,
            "status": project.status.value,
            "total_investment": project.total_investment
        },
        "key_metrics": {
            "npv": project.npv,
            "irr": project.irr,
            "buildability_percentage": project.buildability_percentage,
            "sustainability_score": project.sustainability_score
        }
    }

def _generate_executive_summary(project: models.Project, analyses: Dict[str, Any]) -> Dict[str, Any]:
    """Generar resumen ejecutivo basado en los análisis"""
    
    summary = {
        "project_overview": f"Proyecto {project.name} ubicado en {project.location}",
        "investment_required": project.total_investment,
        "key_findings": [],
        "viability_assessment": "Pendiente de análisis completo"
    }
    
    # Agregar hallazgos financieros
    if "financial" in analyses:
        financial = analyses["financial"]
        if financial.get("npv", 0) > 0:
            summary["key_findings"].append(f"VPN positivo: ")
            summary["viability_assessment"] = "Proyecto financieramente viable"
    
    return summary

def _generate_recommendations(analyses: Dict[str, Any]) -> list:
    """Generar recomendaciones basadas en los análisis"""
    
    recommendations = []
    
    # Recomendaciones financieras
    if "financial" in analyses:
        financial = analyses["financial"]
        npv = financial.get("npv", 0)
        
        if npv < 0:
            recommendations.append("Considerar reducir costos de construcción")
        else:
            recommendations.append("Proyecto financieramente viable")
    
    if not recommendations:
        recommendations.append("Ejecutar análisis completo para obtener recomendaciones")
    
    return recommendations
