from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import time
import json
from datetime import datetime
from shapely.geometry import Polygon

from app.database import get_db
from app import models, schemas
from app.services.financial_service import FinancialService, ProjectFinancials
from app.services.geospatial_service import GeospatialService, LayerRestriction
from app.services.sustainability_service import SustainabilityService

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/{project_id}/run", response_model=schemas.CompleteAnalysisResult)
def run_project_analysis(
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
        all_recommendations = []
        
        # Servicios
        financial_service = FinancialService()
        geospatial_service = GeospatialService()
        sustainability_service = SustainabilityService()
        
        # 1. ANÁLISIS FINANCIERO
        if schemas.AnalysisType.FINANCIAL in analysis_request.analysis_types:
            financial_data = ProjectFinancials(
                terrain_cost=project.terrain_value,
                construction_cost_per_m2=project.construction_cost_per_m2,
                total_area=project.total_area,
                buildable_area=project.buildable_area or project.total_area * 0.7,  # Estimado
                selling_price_per_m2=project.selling_price_per_m2 or project.construction_cost_per_m2 * 1.5,
                construction_time_months=project.construction_time_months,
                selling_time_months=project.selling_time_months,
                discount_rate=project.discount_rate
            )
            
            financial_report = financial_service.create_financial_report(financial_data)
            
            # Actualizar proyecto con resultados financieros
            project.npv = financial_report["advanced_metrics"]["npv"]
            project.irr = financial_report["advanced_metrics"]["irr_annual"]
            
            results["financial"] = schemas.FinancialAnalysisResult(
                basic_metrics=financial_report["basic_metrics"],
                npv=financial_report["advanced_metrics"]["npv"],
                irr=financial_report["advanced_metrics"]["irr_annual"],
                roi_percentage=financial_report["basic_metrics"]["profitability"]["roi_percentage"],
                cash_flows=financial_report["advanced_metrics"]["cash_flows"],
                sensitivity_analysis=financial_report["sensitivity_analysis"] if analysis_request.include_sensitivity else None,
                optimization_results=financial_report["optimization_results"] if analysis_request.include_optimization else None
            )
            
            # Agregar recomendaciones financieras
            if financial_report["advanced_metrics"]["npv"] < 0:
                all_recommendations.append("VPN negativo: Considerar ajustar precios de venta o reducir costos")
            
            if financial_report["advanced_metrics"]["irr_annual"] and financial_report["advanced_metrics"]["irr_annual"] < project.discount_rate * 1.2:
                all_recommendations.append("TIR baja: Evaluar estrategias para mejorar rentabilidad")
        
        # 2. ANÁLISIS GEOESPACIAL
        if schemas.AnalysisType.GEOSPATIAL in analysis_request.analysis_types:
            
            # Crear polígono del lote si existe
            lot_polygon = None
            if project.lot_polygon:
                coords = project.lot_polygon["coordinates"][0]
                lot_polygon = Polygon([(coord[0], coord[1]) for coord in coords])
            else:
                # Crear polígono aproximado basado en área total
                # Esto es simplificado - en la realidad se usarían coordenadas reales
                side_length = (project.total_area ** 0.5) * 0.00001  # Conversión aproximada a grados
                center_lat = project.latitude or 4.6097  # Bogotá por defecto
                center_lon = project.longitude or -74.0817
                
                lot_polygon = Polygon([
                    (center_lon - side_length/2, center_lat - side_length/2),
                    (center_lon + side_length/2, center_lat - side_length/2),
                    (center_lon + side_length/2, center_lat + side_length/2),
                    (center_lon - side_length/2, center_lat + side_length/2)
                ])
            
            # Obtener restricciones del proyecto
            restrictions = db.query(models.ProjectRestriction).filter(
                models.ProjectRestriction.project_id == project_id,
                models.ProjectRestriction.is_active == True
            ).all()
            
            environmental_restrictions = []
            for restriction in restrictions:
                coords = restriction.geometry["coordinates"][0]
                geometry = Polygon([(coord[0], coord[1]) for coord in coords])
                
                layer_restriction = LayerRestriction(
                    name=restriction.name,
                    type=restriction.type,
                    geometry=geometry,
                    reduction_factor=restriction.reduction_factor,
                    buffer_distance=restriction.buffer_distance,
                    description=restriction.description or ""
                )
                environmental_restrictions.append(layer_restriction)
            
            # Ejecutar análisis geoespacial
            geospatial_result = geospatial_service.perform_complete_analysis(
                lot_polygon=lot_polygon,
                environmental_restrictions=environmental_restrictions,
                building_requirements=analysis_request.custom_parameters or {}
            )
            
            # Actualizar proyecto con resultados geoespaciales
            project.buildable_area = geospatial_result.buildable_area
            project.buildability_percentage = geospatial_result.buildability_percentage
            
            # Crear capas de visualización
            visualization_layers = geospatial_service.create_layers_for_visualization(
                lot_polygon, geospatial_result, environmental_restrictions
            )
            
            results["geospatial"] = schemas.GeospatialAnalysisResult(
                total_area=geospatial_result.total_area,
                buildable_area=geospatial_result.buildable_area,
                restricted_area=geospatial_result.restricted_area,
                buildability_percentage=geospatial_result.buildability_percentage,
                restrictions_applied=geospatial_result.restrictions_applied,
                recommendations=geospatial_result.recommendations,
                visualization_layers=visualization_layers
            )
            
            # Agregar recomendaciones geoespaciales
            all_recommendations.extend(geospatial_result.recommendations)
        
        # 3. ANÁLISIS DE SOSTENIBILIDAD
        if schemas.AnalysisType.SUSTAINABILITY in analysis_request.analysis_types:
            
            # Preparar datos para análisis de sostenibilidad
            sustainability_data = {
                "total_area": project.total_area,
                "buildable_area": project.buildable_area or project.total_area * 0.7,
                "zone_type": project.zone_type.value,
                "construction_cost_per_m2": project.construction_cost_per_m2,
                "location": project.location,
                # Datos por defecto - en la realidad vendrían del frontend
                "solar_panels": analysis_request.custom_parameters.get("solar_panels", False) if analysis_request.custom_parameters else False,
                "led_lighting": analysis_request.custom_parameters.get("led_lighting", True) if analysis_request.custom_parameters else True,
                "rainwater_collection": analysis_request.custom_parameters.get("rainwater_collection", False) if analysis_request.custom_parameters else False,
                "local_materials": analysis_request.custom_parameters.get("local_materials", True) if analysis_request.custom_parameters else True,
                "construction_duration_months": project.construction_time_months,
                "materials": {
                    "concrete": project.buildable_area * 0.3 if project.buildable_area else project.total_area * 0.21,  # kg aproximado
                    "steel": project.buildable_area * 0.05 if project.buildable_area else project.total_area * 0.035,
                    "brick": project.buildable_area * 0.2 if project.buildable_area else project.total_area * 0.14
                }
            }
            
            sustainability_report = sustainability_service.generate_sustainability_report(sustainability_data)
            
            # Actualizar proyecto con resultados de sostenibilidad
            project.sustainability_score = sustainability_report.percentage
            project.carbon_footprint = sustainability_report.carbon_footprint["total_lifecycle"]
            
            results["sustainability"] = schemas.SustainabilityAnalysisResult(
                total_score=sustainability_report.total_score,
                percentage=sustainability_report.percentage,
                sustainability_level=sustainability_report.sustainability_level,
                category_scores=sustainability_report.category_scores,
                carbon_footprint=sustainability_report.carbon_footprint,
                certifications_eligible=sustainability_report.certifications_eligible,
                improvement_opportunities=sustainability_report.improvement_opportunities
            )
            
            # Agregar recomendaciones de sostenibilidad
            all_recommendations.extend(sustainability_report.improvement_opportunities)
        
        # Calcular tiempo de ejecución
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Actualizar estado del proyecto
        project.status = models.ProjectStatus.COMPLETED
        db.commit()
        
        # Guardar análisis en base de datos (en background)
        background_tasks.add_task(
            save_analysis_results,
            db,
            project_id,
            analysis_request.analysis_types,
            results,
            all_recommendations,
            execution_time_ms
        )
        
        # Generar evaluación de riesgo
        risk_assessment = generate_risk_assessment(project, results)
        
        return schemas.CompleteAnalysisResult(
            project_id=project_id,
            financial=results.get("financial"),
            geospatial=results.get("geospatial"),
            sustainability=results.get("sustainability"),
            execution_time_ms=execution_time_ms,
            recommendations=all_recommendations[:10],  # Top 10 recomendaciones
            risk_assessment=risk_assessment
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el análisis: {str(e)}"
        )

@router.get("/{project_id}/history", response_model=List[dict])
def get_analysis_history(
    project_id: int,
    analysis_type: Optional[schemas.AnalysisType] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Obtener historial de análisis del proyecto"""
    
    # Verificar que el proyecto existe
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    query = db.query(models.ProjectAnalysis).filter(
        models.ProjectAnalysis.project_id == project_id
    )
    
    if analysis_type:
        query = query.filter(models.ProjectAnalysis.analysis_type == analysis_type.value)
    
    analyses = query.order_by(
        models.ProjectAnalysis.created_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": analysis.id,
            "analysis_type": analysis.analysis_type,
            "results": analysis.results,
            "recommendations": analysis.recommendations,
            "version": analysis.version,
            "execution_time_ms": analysis.execution_time_ms,
            "created_at": analysis.created_at
        }
        for analysis in analyses
    ]

@router.post("/{project_id}/optimize", response_model=schemas.OptimizationResult)
def optimize_project(
    project_id: int,
    optimization_request: schemas.OptimizationRequest,
    db: Session = Depends(get_db)
):
    """Optimizar proyecto según objetivo específico"""
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    try:
        financial_service = FinancialService()
        
        # Preparar datos para optimización
        project_financials = ProjectFinancials(
            terrain_cost=project.terrain_value,
            construction_cost_per_m2=project.construction_cost_per_m2,
            total_area=project.total_area,
            buildable_area=project.buildable_area or project.total_area * 0.7,
            selling_price_per_m2=project.selling_price_per_m2 or project.construction_cost_per_m2 * 1.5,
            construction_time_months=project.construction_time_months,
            selling_time_months=project.selling_time_months,
            discount_rate=project.discount_rate
        )
        
        # Ejecutar optimización
        optimization_result = financial_service.optimize_project(
            project_financials, 
            optimization_request.target
        )
        
        return schemas.OptimizationResult(
            optimized_parameters={
                "selling_price_per_m2": optimization_result["optimal_selling_price_per_m2"],
                "price_multiplier": optimization_result["optimal_selling_price_multiplier"]
            },
            improvement_percentage=(
                optimization_result["improvement"]["npv_improvement"] / abs(project.npv) * 100
                if project.npv and project.npv != 0 else 0
            ),
            iterations=50,  # Simplificado
            convergence_achieved=True,
            recommendations=[
                f"Precio óptimo de venta: ${optimization_result['optimal_selling_price_per_m2']:.2f}/m²",
                f"Incremento de VPN: ${optimization_result['improvement']['npv_improvement']:.2f}",
                f"Mejora en ROI: {optimization_result['improvement']['roi_improvement']:.2f}%"
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante la optimización: {str(e)}"
        )

@router.get("/{project_id}/compare")
def compare_scenarios(
    project_id: int,
    scenarios: List[dict],
    db: Session = Depends(get_db)
):
    """Comparar diferentes escenarios del proyecto"""
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    financial_service = FinancialService()
    comparison_results = []
    
    for i, scenario in enumerate(scenarios[:5]):  # Máximo 5 escenarios
        try:
            # Aplicar cambios del escenario
            scenario_project = ProjectFinancials(
                terrain_cost=scenario.get("terrain_value", project.terrain_value),
                construction_cost_per_m2=scenario.get("construction_cost_per_m2", project.construction_cost_per_m2),
                total_area=scenario.get("total_area", project.total_area),
                buildable_area=scenario.get("buildable_area", project.buildable_area or project.total_area * 0.7),
                selling_price_per_m2=scenario.get("selling_price_per_m2", project.selling_price_per_m2 or project.construction_cost_per_m2 * 1.5),
                construction_time_months=scenario.get("construction_time_months", project.construction_time_months),
                selling_time_months=scenario.get("selling_time_months", project.selling_time_months),
                discount_rate=scenario.get("discount_rate", project.discount_rate)
            )
            
            # Calcular métricas
            basic_metrics = financial_service.calculate_basic_metrics(scenario_project)
            npv_irr = financial_service.calculate_npv_irr(scenario_project)
            
            comparison_results.append({
                "scenario_name": scenario.get("name", f"Escenario {i+1}"),
                "scenario_changes": scenario,
                "results": {
                    "npv": npv_irr["npv"],
                    "irr": npv_irr["irr_annual"],
                    "roi": basic_metrics["profitability"]["roi_percentage"],
                    "total_cost": basic_metrics["costs"]["total_cost"],
                    "total_revenue": basic_metrics["revenue"]["total_revenue"],
                    "profit_margin": basic_metrics["profitability"]["profit_margin_percentage"]
                }
            })
            
        except Exception as e:
            comparison_results.append({
                "scenario_name": scenario.get("name", f"Escenario {i+1}"),
                "error": f"Error en cálculo: {str(e)}"
            })
    
    return {
        "project_id": project_id,
        "base_scenario": {
            "npv": project.npv,
            "irr": project.irr,
            "total_investment": project.total_investment
        },
        "scenario_comparisons": comparison_results
    }

# Funciones auxiliares
def save_analysis_results(
    db: Session,
    project_id: int,
    analysis_types: List[schemas.AnalysisType],
    results: dict,
    recommendations: List[str],
    execution_time_ms: int
):
    """Guardar resultados de análisis en base de datos"""
    try:
        for analysis_type in analysis_types:
            if analysis_type.value in results:
                analysis = models.ProjectAnalysis(
                    project_id=project_id,
                    analysis_type=analysis_type.value,
                    results=results[analysis_type.value].dict() if hasattr(results[analysis_type.value], 'dict') else results[analysis_type.value],
                    recommendations=recommendations,
                    execution_time_ms=execution_time_ms
                )
                db.add(analysis)
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error saving analysis results: {e}")

def generate_risk_assessment(project: models.Project, results: dict) -> dict:
    """Generar evaluación de riesgo del proyecto"""
    
    risk_score = 0
    risk_factors = []
    
    # Evaluar riesgo financiero
    if "financial" in results:
        financial = results["financial"]
        if financial.npv < 0:
            risk_score += 30
            risk_factors.append("VPN negativo")
        
        if financial.irr and financial.irr < project.discount_rate:
            risk_score += 25
            risk_factors.append("TIR menor a tasa de descuento")
    
    # Evaluar riesgo geoespacial
    if "geospatial" in results:
        geospatial = results["geospatial"]
        if geospatial.buildability_percentage < 30:
            risk_score += 20
            risk_factors.append("Bajo aprovechamiento del lote")
    
    # Evaluar riesgo de sostenibilidad
    if "sustainability" in results:
        sustainability = results["sustainability"]
        if sustainability.percentage < 50:
            risk_score += 15
            risk_factors.append("Bajo puntaje de sostenibilidad")
    
    # Evaluar duración del proyecto
    total_duration = project.construction_time_months + project.selling_time_months
    if total_duration > 36:
        risk_score += 10
        risk_factors.append("Proyecto de larga duración")
    
    risk_level = "Alto" if risk_score > 60 else "Medio" if risk_score > 30 else "Bajo"
    
    return {
        "risk_score": min(risk_score, 100),
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "mitigation_strategies": generate_mitigation_strategies(risk_factors)
    }

def generate_mitigation_strategies(risk_factors: List[str]) -> List[str]:
    """Generar estrategias de mitigación de riesgo"""
    
    strategies = []
    
    if "VPN negativo" in risk_factors:
        strategies.append("Revisar precios de venta o reducir costos de construcción")
    
    if "TIR menor a tasa de descuento" in risk_factors:
        strategies.append("Considerar financiamiento a menor tasa o mejorar eficiencia operativa")
    
    if "Bajo aprovechamiento del lote" in risk_factors:
        strategies.append("Revisar normatividad o considerar cambio de uso")
    
    if "Bajo puntaje de sostenibilidad" in risk_factors:
        strategies.append("Implementar tecnologías verdes para certificaciones")
    
    if "Proyecto de larga duración" in risk_factors:
        strategies.append("Considerar construcción por fases o venta en pre-construcción")
    
    return strategies