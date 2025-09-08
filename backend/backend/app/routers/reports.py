from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
import os
import uuid
import json
from datetime import datetime, timedelta
from jinja2 import Template

from app.database import get_db
from app import models, schemas
from app.services.financial_service import FinancialService
from app.services.geospatial_service import GeospatialService
from app.services.sustainability_service import SustainabilityService

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/{project_id}/generate", response_model=schemas.ReportResponse)
def generate_project_report(
    project_id: int,
    report_request: schemas.ReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generar reporte completo del proyecto"""
    
    # Verificar que el proyecto existe
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    try:
        # Generar ID único para el reporte
        report_id = str(uuid.uuid4())
        
        # Crear directorio de reportes si no existe
        reports_dir = "static/reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Recopilar datos del proyecto
        report_data = compile_project_data(project, db)
        
        # Generar reporte según formato solicitado
        if report_request.format == "json":
            filename = f"report_{report_id}.json"
            file_path = os.path.join(reports_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        elif report_request.format == "html":
            filename = f"report_{report_id}.html"
            file_path = os.path.join(reports_dir, filename)
            
            # Generar HTML usando template
            html_content = generate_html_report(report_data, report_request.sections, report_request.language)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        elif report_request.format == "pdf":
            # Para PDF, primero generar HTML y luego convertir
            filename = f"report_{report_id}.pdf"
            file_path = os.path.join(reports_dir, filename)
            
            # Generar PDF en background task
            background_tasks.add_task(
                generate_pdf_report,
                report_data,
                report_request.sections,
                report_request.language,
                file_path
            )
        
        # Calcular tamaño del archivo
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        return schemas.ReportResponse(
            report_id=report_id,
            download_url=f"/reports/{report_id}/download",
            expires_at=datetime.now() + timedelta(hours=24),
            file_size_bytes=file_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar reporte: {str(e)}"
        )

@router.get("/{report_id}/download")
def download_report(report_id: str):
    """Descargar reporte generado"""
    
    # Buscar archivo de reporte
    reports_dir = "static/reports"
    possible_files = [
        f"report_{report_id}.json",
        f"report_{report_id}.html", 
        f"report_{report_id}.pdf"
    ]
    
    file_path = None
    for filename in possible_files:
        potential_path = os.path.join(reports_dir, filename)
        if os.path.exists(potential_path):
            file_path = potential_path
            break
    
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte no encontrado o expirado"
        )
    
    # Determinar tipo de contenido
    if file_path.endswith('.pdf'):
        media_type = 'application/pdf'
    elif file_path.endswith('.html'):
        media_type = 'text/html'
    else:
        media_type = 'application/json'
    
    filename = os.path.basename(file_path)
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )

@router.get("/{project_id}/executive-summary")
def get_executive_summary(project_id: int, db: Session = Depends(get_db)):
    """Obtener resumen ejecutivo del proyecto"""
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Recopilar métricas clave
    summary = {
        "project_overview": {
            "name": project.name,
            "location": project.location,
            "total_area": project.total_area,
            "zone_type": project.zone_type.value,
            "status": project.status.value,
            "created_at": project.created_at
        },
        "financial_highlights": {
            "total_investment": project.total_investment,
            "npv": project.npv,
            "irr": project.irr,
            "expected_return": f"{(project.irr * 100):.1f}%" if project.irr else "N/A"
        },
        "technical_highlights": {
            "buildable_area": project.buildable_area,
            "buildability_percentage": project.buildability_percentage,
            "construction_timeline": f"{project.construction_time_months} meses"
        },
        "sustainability_highlights": {
            "sustainability_score": project.sustainability_score,
            "carbon_footprint": project.carbon_footprint,
            "sustainability_level": get_sustainability_level(project.sustainability_score)
        }
    }
    
    # Generar recomendaciones clave
    key_recommendations = []
    
    if project.npv and project.npv < 0:
        key_recommendations.append({
            "category": "Financiero",
            "priority": "Alta",
            "recommendation": "VPN negativo - Revisar viabilidad económica del proyecto"
        })
    
    if project.buildability_percentage and project.buildability_percentage < 40:
        key_recommendations.append({
            "category": "Técnico", 
            "priority": "Alta",
            "recommendation": "Bajo aprovechamiento del lote - Evaluar restricciones normativas"
        })
    
    if project.sustainability_score and project.sustainability_score < 60:
        key_recommendations.append({
            "category": "Sostenibilidad",
            "priority": "Media",
            "recommendation": "Implementar estrategias de sostenibilidad para mejorar competitividad"
        })
    
    summary["key_recommendations"] = key_recommendations
    
    return summary

@router.get("/{project_id}/financial-dashboard")
def get_financial_dashboard(project_id: int, db: Session = Depends(get_db)):
    """Dashboard financiero del proyecto"""
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Obtener último análisis financiero
    latest_analysis = db.query(models.ProjectAnalysis).filter(
        models.ProjectAnalysis.project_id == project_id,
        models.ProjectAnalysis.analysis_type == "financial"
    ).order_by(models.ProjectAnalysis.created_at.desc()).first()
    
    dashboard = {
        "key_metrics": {
            "total_investment": project.total_investment,
            "npv": project.npv,
            "irr": project.irr,
            "construction_cost": project.total_area * project.construction_cost_per_m2,
            "expected_revenue": project.buildable_area * project.selling_price_per_m2 if project.buildable_area and project.selling_price_per_m2 else None
        },
        "cash_flow_projection": [],
        "risk_indicators": {
            "financial_risk": "Medio",  # Calculado dinámicamente
            "market_risk": "Bajo",
            "regulatory_risk": "Medio"
        },
        "benchmarks": {
            "sector_average_irr": 0.15,
            "sector_average_margin": 0.25,
            "market_discount_rate": 0.12
        }
    }
    
    # Agregar datos del análisis si existe
    if latest_analysis and latest_analysis.results:
        analysis_data = latest_analysis.results
        if "cash_flows" in analysis_data:
            dashboard["cash_flow_projection"] = analysis_data["cash_flows"]
    
    return dashboard

@router.get("/{project_id}/sustainability-report")
def get_sustainability_report(project_id: int, db: Session = Depends(get_db)):
    """Reporte detallado de sostenibilidad"""
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Obtener último análisis de sostenibilidad
    latest_analysis = db.query(models.ProjectAnalysis).filter(
        models.ProjectAnalysis.project_id == project_id,
        models.ProjectAnalysis.analysis_type == "sustainability"
    ).order_by(models.ProjectAnalysis.created_at.desc()).first()
    
    report = {
        "overview": {
            "total_score": project.sustainability_score,
            "sustainability_level": get_sustainability_level(project.sustainability_score),
            "carbon_footprint": project.carbon_footprint
        },
        "category_breakdown": {},
        "certifications": [],
        "improvement_opportunities": [],
        "environmental_impact": {
            "carbon_reduction_potential": calculate_carbon_reduction_potential(project),
            "water_efficiency_rating": "B",  # Simplificado
            "energy_efficiency_rating": "A-",
            "waste_reduction_score": 75
        }
    }
    
    # Agregar datos del análisis si existe
    if latest_analysis and latest_analysis.results:
        analysis_data = latest_analysis.results
        report["category_breakdown"] = analysis_data.get("category_scores", {})
        report["certifications"] = analysis_data.get("certifications_eligible", [])
        report["improvement_opportunities"] = analysis_data.get("improvement_opportunities", [])
    
    return report

@router.post("/{project_id}/presentation")
def generate_presentation(
    project_id: int,
    presentation_config: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Generar presentación para inversionistas"""
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Configuración por defecto de la presentación
    default_slides = [
        "cover",
        "executive_summary", 
        "location_analysis",
        "financial_projections",
        "risk_assessment",
        "sustainability",
        "timeline",
        "investment_opportunity"
    ]
    
    slides_to_include = presentation_config.get("slides", default_slides)
    theme = presentation_config.get("theme", "professional")
    language = presentation_config.get("language", "es")
    
    # Recopilar datos para la presentación
    presentation_data = {
        "project": project,
        "slides": slides_to_include,
        "theme": theme,
        "language": language,
        "generated_at": datetime.now(),
        "key_metrics": {
            "investment": project.total_investment,
            "npv": project.npv,
            "irr": project.irr,
            "area": project.total_area,
            "buildability": project.buildability_percentage
        }
    }
    
    # En una implementación real, aquí se generaría un PowerPoint o PDF
    # Por ahora, retornamos la estructura de datos
    
    return {
        "presentation_id": str(uuid.uuid4()),
        "slides_count": len(slides_to_include),
        "estimated_duration": f"{len(slides_to_include) * 2} minutos",
        "data": presentation_data,
        "download_url": f"/reports/{project_id}/presentation/download"
    }

# Funciones auxiliares
def compile_project_data(project: models.Project, db: Session) -> Dict[str, Any]:
    """Recopilar todos los datos del proyecto para reportes"""
    
    # Obtener análisis más recientes
    analyses = {}
    for analysis_type in ["financial", "geospatial", "sustainability"]:
        analysis = db.query(models.ProjectAnalysis).filter(
            models.ProjectAnalysis.project_id == project.id,
            models.ProjectAnalysis.analysis_type == analysis_type
        ).order_by(models.ProjectAnalysis.created_at.desc()).first()
        
        if analysis:
            analyses[analysis_type] = analysis.results
    
    # Obtener restricciones
    restrictions = db.query(models.ProjectRestriction).filter(
        models.ProjectRestriction.project_id == project.id,
        models.ProjectRestriction.is_active == True
    ).all()
    
    return {
        "project_info": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "location": project.location,
            "status": project.status.value,
            "zone_type": project.zone_type.value,
            "created_at": project.created_at,
            "updated_at": project.updated_at
        },
        "technical_specs": {
            "total_area": project.total_area,
            "buildable_area": project.buildable_area,
            "buildability_percentage": project.buildability_percentage,
            "construction_time_months": project.construction_time_months,
            "selling_time_months": project.selling_time_months
        },
        "financial_data": {
            "terrain_value": project.terrain_value,
            "construction_cost_per_m2": project.construction_cost_per_m2,
            "selling_price_per_m2": project.selling_price_per_m2,
            "total_investment": project.total_investment,
            "discount_rate": project.discount_rate,
            "npv": project.npv,
            "irr": project.irr
        },
        "sustainability_data": {
            "sustainability_score": project.sustainability_score,
            "carbon_footprint": project.carbon_footprint
        },
        "location_data": {
            "latitude": project.latitude,
            "longitude": project.longitude,
            "satellite_image_url": project.satellite_image_url
        },
        "analyses": analyses,
        "restrictions": [
            {
                "name": r.name,
                "type": r.type,
                "description": r.description,
                "reduction_factor": r.reduction_factor,
                "buffer_distance": r.buffer_distance
            }
            for r in restrictions
        ],
        "generated_at": datetime.now()
    }

def generate_html_report(data: Dict[str, Any], sections: list, language: str) -> str:
    """Generar reporte en formato HTML"""
    
    # Template HTML básico
    html_template = """
    <!DOCTYPE html>
    <html lang="{{ language }}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reporte - {{ project_name }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            .header { border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px; }
            .section { margin-bottom: 30px; }
            .metric-card { background: #f8fafc; padding: 15px; border-left: 4px solid #2563eb; margin: 10px 0; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .table { width: 100%; border-collapse: collapse; }
            .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .table th { background-color: #f2f2f2; }
            .highlight { color: #2563eb; font-weight: bold; }
            .warning { color: #dc2626; }
            .success { color: #16a34a; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{{ project_name }}</h1>
            <p><strong>Ubicación:</strong> {{ location }}</p>
            <p><strong>Fecha de generación:</strong> {{ generated_at }}</p>
        </div>
        
        {% if 'executive_summary' in sections %}
        <div class="section">
            <h2>Resumen Ejecutivo</h2>
            <div class="grid">
                <div class="metric-card">
                    <h4>Inversión Total</h4>
                    <p class="highlight">${{ "%.2f"|format(total_investment) }}</p>
                </div>
                <div class="metric-card">
                    <h4>VPN</h4>
                    <p class="{{ 'success' if npv > 0 else 'warning' }}">${{ "%.2f"|format(npv) }}</p>
                </div>
                <div class="metric-card">
                    <h4>TIR</h4>
                    <p class="{{ 'success' if irr > 0.12 else 'warning' }}">{{ "%.1f"|format(irr * 100) }}%</p>
                </div>
                <div class="metric-card">
                    <h4>Aprovechamiento</h4>
                    <p class="highlight">{{ "%.1f"|format(buildability_percentage) }}%</p>
                </div>
            </div>
        </div>
        {% endif %}
        
        {% if 'financial' in sections %}
        <div class="section">
            <h2>Análisis Financiero</h2>
            <table class="table">
                <tr><th>Concepto</th><th>Valor</th></tr>
                <tr><td>Valor del Terreno</td><td>${{ "%.2f"|format(terrain_value) }}</td></tr>
                <tr><td>Costo de Construcción/m²</td><td>${{ "%.2f"|format(construction_cost_per_m2) }}</td></tr>
                <tr><td>Precio de Venta/m²</td><td>${{ "%.2f"|format(selling_price_per_m2) }}</td></tr>
                <tr><td>Tiempo de Construcción</td><td>{{ construction_time_months }} meses</td></tr>
                <tr><td>Tiempo de Ventas</td><td>{{ selling_time_months }} meses</td></tr>
            </table>
        </div>
        {% endif %}
        
        {% if 'technical' in sections %}
        <div class="section">
            <h2>Especificaciones Técnicas</h2>
            <div class="grid">
                <div>
                    <h4>Área Total</h4>
                    <p>{{ "%.2f"|format(total_area) }} m²</p>
                </div>
                <div>
                    <h4>Área Construible</h4>
                    <p>{{ "%.2f"|format(buildable_area) }} m²</p>
                </div>
            </div>
            
            {% if restrictions %}
            <h4>Restricciones Aplicadas</h4>
            <ul>
                {% for restriction in restrictions %}
                <li><strong>{{ restriction.name }}:</strong> {{ restriction.description }}</li>
                {% endfor %}
            </ul>
            {% endif %}
        </div>
        {% endif %}
        
        {% if 'sustainability' in sections %}
        <div class="section">
            <h2>Sostenibilidad</h2>
            <div class="metric-card">
                <h4>Puntaje de Sostenibilidad</h4>
                <p class="highlight">{{ "%.1f"|format(sustainability_score) }}/100</p>
            </div>
            <div class="metric-card">
                <h4>Huella de Carbono</h4>
                <p>{{ "%.2f"|format(carbon_footprint) }} kg CO₂</p>
            </div>
        </div>
        {% endif %}
        
        <div class="section">
            <h2>Recomendaciones</h2>
            <ul>
                {% if npv < 0 %}
                <li class="warning">VPN negativo - Revisar viabilidad económica</li>
                {% endif %}
                {% if buildability_percentage < 40 %}
                <li class="warning">Bajo aprovechamiento - Evaluar restricciones</li>
                {% endif %}
                {% if sustainability_score < 60 %}
                <li>Considerar mejoras en sostenibilidad</li>
                {% endif %}
                {% if irr and irr > 0.15 %}
                <li class="success">Excelente rentabilidad proyectada</li>
                {% endif %}
            </ul>
        </div>
    </body>
    </html>
    """
    
    # Renderizar template con datos
    template = Template(html_template)
    
    # Preparar datos para el template
    template_data = {
        "language": language,
        "project_name": data["project_info"]["name"],
        "location": data["project_info"]["location"],
        "generated_at": data["generated_at"].strftime("%d/%m/%Y %H:%M"),
        "sections": sections,
        "total_investment": data["financial_data"]["total_investment"] or 0,
        "npv": data["financial_data"]["npv"] or 0,
        "irr": data["financial_data"]["irr"] or 0,
        "buildability_percentage": data["technical_specs"]["buildability_percentage"] or 0,
        "terrain_value": data["financial_data"]["terrain_value"] or 0,
        "construction_cost_per_m2": data["financial_data"]["construction_cost_per_m2"] or 0,
        "selling_price_per_m2": data["financial_data"]["selling_price_per_m2"] or 0,
        "construction_time_months": data["technical_specs"]["construction_time_months"] or 0,
        "selling_time_months": data["technical_specs"]["selling_time_months"] or 0,
        "total_area": data["technical_specs"]["total_area"] or 0,
        "buildable_area": data["technical_specs"]["buildable_area"] or 0,
        "sustainability_score": data["sustainability_data"]["sustainability_score"] or 0,
        "carbon_footprint": data["sustainability_data"]["carbon_footprint"] or 0,
        "restrictions": data["restrictions"]
    }
    
    return template.render(**template_data)

def generate_pdf_report(data: Dict[str, Any], sections: list, language: str, output_path: str):
    """Generar reporte en formato PDF (implementación simplificada)"""
    
    try:
        # En una implementación real, usarías librerías como weasyprint o reportlab
        # Por ahora, generamos un HTML y simulamos la conversión a PDF
        
        html_content = generate_html_report(data, sections, language)
        
        # Simular generación de PDF escribiendo HTML
        # En producción, aquí usarías weasyprint:
        # import weasyprint
        # weasyprint.HTML(string=html_content).write_pdf(output_path)
        
        # Por ahora, guardamos como HTML con extensión .pdf
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
    except Exception as e:
        print(f"Error generating PDF report: {e}")

def get_sustainability_level(score: float) -> str:
    """Convertir puntaje numérico a nivel de sostenibilidad"""
    
    if not score:
        return "No evaluado"
    
    if score >= 80:
        return "Excelente"
    elif score >= 70:
        return "Muy Bueno"
    elif score >= 60:
        return "Bueno"
    elif score >= 40:
        return "Regular"
    else:
        return "Deficiente"

def calculate_carbon_reduction_potential(project: models.Project) -> Dict[str, float]:
    """Calcular potencial de reducción de carbono"""
    
    base_footprint = project.carbon_footprint or 0
    
    # Estimaciones de reducción por implementar tecnologías verdes
    potential_reductions = {
        "solar_panels": base_footprint * 0.15,  # 15% reducción
        "led_lighting": base_footprint * 0.08,   # 8% reducción
        "efficient_hvac": base_footprint * 0.12, # 12% reducción
        "green_roof": base_footprint * 0.05,     # 5% reducción
        "rainwater_harvesting": base_footprint * 0.03  # 3% reducción
    }
    
    total_potential = sum(potential_reductions.values())
    
    return {
        "base_footprint": base_footprint,
        "potential_reductions": potential_reductions,
        "total_reduction_potential": total_potential,
        "percentage_reduction": (total_potential / base_footprint * 100) if base_footprint > 0 else 0
    }