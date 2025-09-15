from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import time
import json
from datetime import datetime

from app.database import get_db
from app import models, schemas
from app.services.financial_service import FinancialService, ProjectFinancials
from app.services.geospatial_service import GeospatialService
from app.services.sustainability_service import SustainabilityService

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/{project_id}/financial", response_model=schemas.FinancialAnalysisResult)
def run_financial_analysis(
    project_id: int,
    include_sensitivity: bool = False,
    include_optimization: bool = False,
    db: Session = Depends(get_db)
):
    """Ejecutar análisis financiero del proyecto"""
    
    start_time = time.time()
    
    # Verificar que el proyecto existe
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    try:
        # Crear objeto de datos financieros
        project_financials = ProjectFinancials(
            terrain_cost=project.terrain_value,
            construction_cost_per_m2=project.construction_cost_per_m2,
            total_area=project.total_area,
            buildable_area=project.buildable_area or project.total_area * 0.7,  # Asumimos 70% si no está calculado
            selling_price_per_m2=project.selling_price_per_m2 or project.construction_cost_per_m2 * 1.5,  # Default markup
            construction_time_months=project.construction_time_months,
            selling_time_months=project.selling_time_months,
            discount_rate=project.discount_rate
        )
        
        # Ejecutar análisis
        financial_service = FinancialService()
        
        # Métricas básicas
        basic_metrics = financial_service.calculate_basic_metrics(project_financials)
        
        # NPV e IRR
        npv_irr = financial_service.calculate_npv_irr(project_financials)
        
        result = {
            "basic_metrics": basic_metrics,
            "npv": npv_irr["npv"],
            "irr": npv_irr["irr_annual"],
            "roi_percentage": basic_metrics["profitability"]["roi_percentage"],
            "cash_flows": npv_irr["cash_flows"]
        }
        
        # Análisis de sensibilidad (opcional)
        if include_sensitivity:
            sensitivity = financial_service.perform_sensitivity_analysis(project_financials)
            result["sensitivity_analysis"] = sensitivity
        
        # Optimización (opcional)
        if include_optimization:
            optimization = financial_service.optimize_project(project_financials)
            result["optimization_results"] = optimization
        
        # Guardar resultados en base de datos
        analysis_record = models.ProjectAnalysis(
            project_id=project_id,
            analysis_type="financial",
            results=result,
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
        
        db.add(analysis_record)
        
        # Actualizar proyecto con resultados
        project.npv = result["npv"]
        project.irr = result["irr"]
        
        db.commit()
        
        return schemas.FinancialAnalysisResult(**result)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el análisis financiero: {str(e)}"
        )

@router.post("/{project_id}/geospatial", response_model=schemas.GeospatialAnalysisResult)
def run_geospatial_analysis(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Ejecutar análisis geoespacial del proyecto"""
    
    start_time = time.time()
    
    # Verificar que el proyecto existe
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    try:
        geospatial_service = GeospatialService()
        
        # Por ahora, análisis simplificado
        # En una implementación completa, se usaría la geometría real del lote
        
        total_area = project.total_area
        
        # Aplicar restricciones típicas
        setback_reduction = 0.15  # 15% por retiros
        environmental_reduction = 0.05  # 5% por restricciones ambientales
        
        restricted_area = total_area * (setback_reduction + environmental_reduction)
        buildable_area = total_area - restricted_area
        buildability_percentage = (buildable_area / total_area) * 100
        
        result = {
            "total_area": total_area,
            "buildable_area": buildable_area,
            "restricted_area": restricted_area,
            "buildability_percentage": buildability_percentage,
            "restrictions_applied": [
                "Retiros obligatorios",
                "Restricciones ambientales básicas"
            ],
            "recommendations": [
                "Considerar optimización del diseño",
                "Evaluar opciones de mayor altura si la normativa lo permite"
            ],
            "visualization_layers": {
                "buildable_zone": {
                    "type": "polygon",
                    "area": buildable_area,
                    "percentage": buildability_percentage
                }
            }
        }
        
        # Guardar resultados
        analysis_record = models.ProjectAnalysis(
            project_id=project_id,
            analysis_type="geospatial",
            results=result,
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
        
        db.add(analysis_record)
        
        # Actualizar proyecto
        project.buildable_area = buildable_area
        project.buildability_percentage = buildability_percentage
        
        db.commit()
        
        return schemas.GeospatialAnalysisResult(**result)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el análisis geoespacial: {str(e)}"
        )

@router.post("/{project_id}/sustainability", response_model=schemas.SustainabilityAnalysisResult)
def run_sustainability_analysis(
    project_id: int,
    project_parameters: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Ejecutar análisis de sostenibilidad del proyecto"""
    
    start_time = time.time()
    
    # Verificar que el proyecto existe
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    try:
        sustainability_service = SustainabilityService()
        
        # Datos del proyecto para análisis
        project_data = {
            "total_area": project.total_area,
            "buildable_area": project.buildable_area or project.total_area * 0.7,
            "zone_type": project.zone_type.value,
            "construction_cost_per_m2": project.construction_cost_per_m2,
            # Valores por defecto para demo
            "solar_panels": False,
            "led_lighting": True,
            "rainwater_collection": False,
            "local_materials": True,
            "construction_duration_months": project.construction_time_months
        }
        
        # Agregar parámetros adicionales si se proporcionan
        if project_parameters:
            project_data.update(project_parameters)
        
        # Ejecutar análisis completo
        sustainability_report = sustainability_service.generate_sustainability_report(project_data)
        
        result = {
            "total_score": sustainability_report.total_score,
            "percentage": sustainability_report.percentage,
            "sustainability_level": sustainability_report.sustainability_level,
            "category_scores": sustainability_report.category_scores,
            "carbon_footprint": sustainability_report.carbon_footprint,
            "certifications_eligible": sustainability_report.certifications_eligible,
            "improvement_opportunities": sustainability_report.improvement_opportunities
        }
        
        # Guardar resultados
        analysis_record = models.ProjectAnalysis(
            project_id=project_id,
            analysis_type="sustainability",
            results=result,
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
        
        db.add(analysis_record)
        
        # Actualizar proyecto
        project.sustainability_score = sustainability_report.percentage
        project.carbon_footprint = sustainability_report.carbon_footprint["total_lifecycle"]
        
        db.commit()
        
        return schemas.SustainabilityAnalysisResult(**result)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el análisis de sostenibilidad: {str(e)}"
        )

@router.post("/{project_id}/complete", response_model=schemas.CompleteAnalysisResult)
def run_complete_analysis(
    project_id: int,
    analysis_request: schemas.AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Ejecutar análisis completo del proyecto"""
    
    start_time = time.time()
    
    # Verificar que el proyecto existe
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    try:
        results = {}
        recommendations = []
        
        # Ejecutar análisis según lo solicitado
        if schemas.AnalysisType.FINANCIAL in analysis_request.analysis_types:
            financial_result = run_financial_analysis(
                project_id, 
                analysis_request.include_sensitivity,
                analysis_request.include_optimization,
                db
            )
            results["financial"] = financial_result
            
        if schemas.AnalysisType.GEOSPATIAL in analysis_request.analysis_types:
            geospatial_result = run_geospatial_analysis(project_id, db)
            results["geospatial"] = geospatial_result
            recommendations.extend(geospatial_result.recommendations)
            
        if schemas.AnalysisType.SUSTAINABILITY in analysis_request.analysis_types:
            sustainability_result = run_sustainability_analysis(
                project_id, 
                analysis_request.custom_parameters,
                db
            )
            results["sustainability"] = sustainability_result
            recommendations.extend(sustainability_result.improvement_opportunities[:3])
        
        # Evaluación de riesgo simplificada
        risk_assessment = {
            "risk_level": "Medio",
            "risk_factors": ["Análisis preliminar", "Requiere validación de mercado"],
            "risk_score": 50
        }
        
        execution_time = int((time.time() - start_time) * 1000)
        
        return schemas.CompleteAnalysisResult(
            project_id=project_id,
            financial=results.get("financial"),
            geospatial=results.get("geospatial"),
            sustainability=results.get("sustainability"),
            execution_time_ms=execution_time,
            recommendations=recommendations,
            risk_assessment=risk_assessment
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el análisis completo: {str(e)}"
        )

@router.get("/{project_id}/history")
def get_analysis_history(
    project_id: int,
    analysis_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtener historial de análisis de un proyecto"""
    
    query = db.query(models.ProjectAnalysis).filter(
        models.ProjectAnalysis.project_id == project_id
    )
    
    if analysis_type:
        query = query.filter(models.ProjectAnalysis.analysis_type == analysis_type)
    
    analyses = query.order_by(models.ProjectAnalysis.created_at.desc()).all()
    
    return {
        "project_id": project_id,
        "total_analyses": len(analyses),
        "analyses": [
            {
                "id": analysis.id,
                "type": analysis.analysis_type,
                "created_at": analysis.created_at,
                "execution_time_ms": analysis.execution_time_ms,
                "version": analysis.version
            }
            for analysis in analyses
        ]
    }
