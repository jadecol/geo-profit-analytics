# backend/scripts/seed_data_fixed.py
"""
Script profesional corregido para generar datos de prueba
Uso: python scripts/seed_data_fixed.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, engine
from app.models import Base, Project, ProjectAnalysis, ProjectRestriction, ProjectStatus, ZoneType
from sqlalchemy.orm import Session
import random
from datetime import datetime

# Datos de prueba realistas para Colombia
SAMPLE_PROJECTS = [
    {
        "name": "Torres del Parque Metropolitano",
        "description": "Desarrollo residencial de lujo con 3 torres de 25 pisos c/u",
        "location": "Zona Rosa, Bogotá",
        "zone_type": ZoneType.RESIDENTIAL,
        "total_area": 8500.0,
        "terrain_value": 2500000.0,
        "construction_cost_per_m2": 1800.0,
        "investment_horizon": 4,
        "selling_price_per_m2": 2800.0
    },
    {
        "name": "Centro Comercial Andino Plaza",
        "description": "Mall regional con tiendas ancla y área de entretenimiento",
        "location": "Chía, Cundinamarca",
        "zone_type": ZoneType.COMMERCIAL,
        "total_area": 15000.0,
        "terrain_value": 4200000.0,
        "construction_cost_per_m2": 2200.0,
        "investment_horizon": 6,
        "selling_price_per_m2": 3500.0
    },
    {
        "name": "Conjunto Residencial Valle Verde",
        "description": "Urbanización de casas unifamiliares con zonas verdes",
        "location": "Cajicá, Cundinamarca",
        "zone_type": ZoneType.RESIDENTIAL,
        "total_area": 12000.0,
        "terrain_value": 1800000.0,
        "construction_cost_per_m2": 1200.0,
        "investment_horizon": 5,
        "selling_price_per_m2": 1900.0
    },
    {
        "name": "Distrito Empresarial Norte",
        "description": "Complejo de oficinas clase A con certificación LEED",
        "location": "Zona Norte, Bogotá",
        "zone_type": ZoneType.COMMERCIAL,
        "total_area": 6800.0,
        "terrain_value": 3100000.0,
        "construction_cost_per_m2": 2500.0,
        "investment_horizon": 3,
        "selling_price_per_m2": 4200.0
    },
    {
        "name": "Edificio Mixto Chapinero",
        "description": "Torre mixta: comercio en primeros pisos, oficinas arriba",
        "location": "Chapinero, Bogotá",
        "zone_type": ZoneType.MIXED,
        "total_area": 4200.0,
        "terrain_value": 1950000.0,
        "construction_cost_per_m2": 2100.0,
        "investment_horizon": 4,
        "selling_price_per_m2": 3400.0
    },
    {
        "name": "Parque Industrial Sostenible",
        "description": "Complejo industrial con tecnologías verdes",
        "location": "Tocancipá, Cundinamarca",
        "zone_type": ZoneType.INDUSTRIAL,
        "total_area": 25000.0,
        "terrain_value": 3800000.0,
        "construction_cost_per_m2": 1500.0,
        "investment_horizon": 7,
        "selling_price_per_m2": 2200.0
    }
]

def clear_existing_data_safe(db: Session):
    """Limpiar datos existentes respetando llaves foráneas"""
    print("🧹 Limpiando datos existentes...")
    
    # Contar registros
    project_count = db.query(Project).count()
    analysis_count = db.query(ProjectAnalysis).count()
    
    print(f"   📊 Proyectos actuales: {project_count}")
    print(f"   📊 Análisis actuales: {analysis_count}")
    
    if project_count > 0 and project_count < 20:
        try:
            # Eliminar en orden correcto (FK primero)
            print("   🗑️  Eliminando análisis...")
            db.query(ProjectAnalysis).delete()
            
            print("   🗑️  Eliminando restricciones...")
            db.query(ProjectRestriction).delete()
            
            print("   🗑️  Eliminando proyectos...")
            db.query(Project).delete()
            
            db.commit()
            print(f"   ✅ {project_count} proyectos y {analysis_count} análisis eliminados")
            
        except Exception as e:
            print(f"   ⚠️  Error eliminando datos: {e}")
            db.rollback()
            print("   🔄 Continuando con los datos existentes...")
    else:
        print(f"   ℹ️  Manteniendo datos existentes ({project_count} proyectos)")

def calculate_metrics(project_data: dict) -> dict:
    """Calcular métricas financieras básicas"""
    total_construction = project_data["total_area"] * project_data["construction_cost_per_m2"]
    total_investment = project_data["terrain_value"] + total_construction
    
    # Simular buildable area (70-90% del total)
    buildable_percentage = random.uniform(0.7, 0.9)
    buildable_area = project_data["total_area"] * buildable_percentage
    
    # Calcular ingresos estimados
    total_revenue = buildable_area * project_data["selling_price_per_m2"]
    
    # NPV simplificado (sin descuento temporal por simplicidad)
    npv = total_revenue - total_investment
    
    # IRR estimado basado en rentabilidad
    if total_investment > 0:
        annual_return = (total_revenue - total_investment) / project_data["investment_horizon"]
        irr = annual_return / total_investment
    else:
        irr = 0
    
    # Añadir variabilidad realista
    irr_variation = random.uniform(0.8, 1.2)  # ±20% variación
    irr *= irr_variation
    
    return {
        "total_investment": total_investment,
        "buildable_area": buildable_area,
        "buildability_percentage": buildable_percentage * 100,
        "npv": npv,
        "irr": max(-0.2, min(irr, 0.8))  # IRR entre -20% y 80%
    }

def create_sample_projects(db: Session):
    """Crear proyectos de muestra con datos realistas"""
    print("🏗️  Creando proyectos de muestra...")
    
    created_projects = []
    
    for i, project_data in enumerate(SAMPLE_PROJECTS):
        # Verificar si ya existe un proyecto con el mismo nombre
        existing = db.query(Project).filter(Project.name == project_data["name"]).first()
        if existing:
            print(f"   ⚠️  {project_data['name']} ya existe, saltando...")
            continue
        
        # Calcular métricas
        metrics = calculate_metrics(project_data)
        
        # Crear proyecto
        project = Project(
            name=project_data["name"],
            description=project_data["description"],
            location=project_data["location"],
            zone_type=project_data["zone_type"],
            status=ProjectStatus.DRAFT,
            total_area=project_data["total_area"],
            terrain_value=project_data["terrain_value"],
            construction_cost_per_m2=project_data["construction_cost_per_m2"],
            investment_horizon=project_data["investment_horizon"],
            selling_price_per_m2=project_data["selling_price_per_m2"],
            construction_time_months=12,
            selling_time_months=18,
            discount_rate=0.12,
            # Métricas calculadas
            total_investment=metrics["total_investment"],
            buildable_area=metrics["buildable_area"],
            buildability_percentage=metrics["buildability_percentage"],
            npv=metrics["npv"],
            irr=metrics["irr"],
            # Coordenadas de ejemplo (Bogotá y alrededores)
            latitude=4.6097 + random.uniform(-0.1, 0.1),
            longitude=-74.0817 + random.uniform(-0.1, 0.1),
            # Puntajes de sostenibilidad simulados
            sustainability_score=random.uniform(6.0, 9.5),
            carbon_footprint=random.uniform(800, 1500)
        )
        
        db.add(project)
        created_projects.append(project)
        
        print(f"   ✅ {project.name}")
        print(f"      💰 NPV: ${metrics['npv']:,.0f}")
        print(f"      📈 IRR: {metrics['irr']:.1%}")
        print(f"      📐 Área construible: {metrics['buildable_area']:.0f} m²")
    
    try:
        db.commit()
        print(f"\n🎉 {len(created_projects)} proyectos creados exitosamente!")
        return created_projects
    except Exception as e:
        print(f"❌ Error creando proyectos: {e}")
        db.rollback()
        return []

def display_summary(db: Session):
    """Mostrar resumen de todos los proyectos en la base de datos"""
    print("\n📊 RESUMEN DE PROYECTOS EN BASE DE DATOS:")
    print("=" * 70)
    
    projects = db.query(Project).all()
    
    if not projects:
        print("   ⚠️  No hay proyectos en la base de datos")
        return
    
    print(f"📈 Total de proyectos: {len(projects)}")
    print()
    
    for project in projects:
        status_color = "🟢" if project.npv and project.npv > 0 else "🔴"
        npv_display = f"${project.npv:,.0f}" if project.npv else "No calculado"
        irr_display = f"{project.irr:.1%}" if project.irr else "No calculado"
        
        print(f"{status_color} {project.name}")
        print(f"   📍 {project.location}")
        print(f"   💰 NPV: {npv_display} | IRR: {irr_display}")
        print(f"   📐 {project.total_area:,.0f} m² | 🏗️ {project.zone_type.value if hasattr(project.zone_type, 'value') else project.zone_type}")
        print()

def main():
    """Función principal"""
    print("🚀 GENERADOR PROFESIONAL DE DATOS DE PRUEBA - VERSIÓN CORREGIDA")
    print("=" * 65)
    print("Este script creará proyectos de muestra para desarrollo y testing.")
    print("Maneja correctamente las restricciones de base de datos.")
    print()
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Limpiar datos existentes de forma segura
        clear_existing_data_safe(db)
        
        # Crear proyectos de muestra
        created_projects = create_sample_projects(db)
        
        # Mostrar resumen completo
        display_summary(db)
        
        if created_projects:
            print("✅ Proceso completado exitosamente!")
        else:
            print("ℹ️  No se crearon nuevos proyectos (pueden ya existir)")
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Ejecutar: python run.py (en terminal backend)")
        print("2. Ejecutar: npm start (en terminal frontend)")
        print("3. Ir a Dashboard → Comparar Proyectos")
        print("4. Seleccionar múltiples proyectos y comparar")
        
    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()