# backend/scripts/seed_data_ultimate.py
"""
Script definitivo para generar datos de prueba
SOLUCION COMPLETA para problemas de enums y constraints
Uso: python scripts/seed_data_ultimate.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, engine
from app.models import Base, Project, ProjectAnalysis, ProjectRestriction
from sqlalchemy.orm import Session
from sqlalchemy import text
import random
from datetime import datetime

def create_enums_if_not_exist(db: Session):
    """Crear enums en PostgreSQL si no existen"""
    print("🔧 Verificando y creando enums...")
    
    try:
        # Crear enums si no existen
        db.execute(text("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'zonetype') THEN
                    CREATE TYPE zonetype AS ENUM ('residential', 'commercial', 'mixed', 'industrial');
                END IF;
            END $$;
        """))
        
        db.execute(text("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'projectstatus') THEN
                    CREATE TYPE projectstatus AS ENUM ('draft', 'analysis', 'completed', 'archived');
                END IF;
            END $$;
        """))
        
        db.commit()
        print("   ✅ Enums verificados/creados")
    except Exception as e:
        print(f"   ⚠️  Error con enums: {e}")
        db.rollback()

def clear_all_data_cascade(db: Session):
    """Limpiar todos los datos usando CASCADE"""
    print("🧹 Limpiando datos con CASCADE...")
    
    try:
        # Eliminar en orden correcto con CASCADE
        db.execute(text("DELETE FROM project_analyses CASCADE"))
        db.execute(text("DELETE FROM project_restrictions CASCADE"))
        db.execute(text("DELETE FROM satellite_images CASCADE"))
        db.execute(text("DELETE FROM user_sessions CASCADE"))
        db.execute(text("DELETE FROM projects CASCADE"))
        
        # Reset sequences
        db.execute(text("ALTER SEQUENCE projects_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE project_analyses_id_seq RESTART WITH 1"))
        
        db.commit()
        print("   ✅ Datos eliminados con CASCADE")
        
    except Exception as e:
        print(f"   ⚠️  Error limpiando: {e}")
        db.rollback()

def create_projects_direct_sql(db: Session):
    """Crear proyectos usando SQL directo para evitar problemas de ORM"""
    print("🏗️  Creando proyectos con SQL directo...")
    
    # Datos de proyectos
    projects_data = [
        {
            'name': 'Torres del Parque Metropolitano',
            'description': 'Desarrollo residencial de lujo con 3 torres de 25 pisos',
            'location': 'Zona Rosa, Bogotá',
            'zone_type': 'residential',
            'status': 'draft',
            'total_area': 8500.0,
            'terrain_value': 2500000.0,
            'construction_cost_per_m2': 1800.0,
            'investment_horizon': 4,
            'selling_price_per_m2': 2800.0,
            'npv': 8500000.0,
            'irr': 0.245
        },
        {
            'name': 'Centro Comercial Andino Plaza',
            'description': 'Mall regional con tiendas ancla y área de entretenimiento',
            'location': 'Chía, Cundinamarca',
            'zone_type': 'commercial',
            'status': 'draft',
            'total_area': 15000.0,
            'terrain_value': 4200000.0,
            'construction_cost_per_m2': 2200.0,
            'investment_horizon': 6,
            'selling_price_per_m2': 3500.0,
            'npv': 15200000.0,
            'irr': 0.321
        },
        {
            'name': 'Conjunto Residencial Valle Verde',
            'description': 'Urbanización de casas unifamiliares con zonas verdes',
            'location': 'Cajicá, Cundinamarca',
            'zone_type': 'residential',
            'status': 'draft',
            'total_area': 12000.0,
            'terrain_value': 1800000.0,
            'construction_cost_per_m2': 1200.0,
            'investment_horizon': 5,
            'selling_price_per_m2': 1900.0,
            'npv': 6400000.0,
            'irr': 0.189
        },
        {
            'name': 'Distrito Empresarial Norte',
            'description': 'Complejo de oficinas clase A con certificación LEED',
            'location': 'Zona Norte, Bogotá',
            'zone_type': 'commercial',
            'status': 'draft',
            'total_area': 6800.0,
            'terrain_value': 3100000.0,
            'construction_cost_per_m2': 2500.0,
            'investment_horizon': 3,
            'selling_price_per_m2': 4200.0,
            'npv': 11500000.0,
            'irr': 0.412
        },
        {
            'name': 'Edificio Mixto Chapinero',
            'description': 'Torre mixta: comercio en primeros pisos, oficinas arriba',
            'location': 'Chapinero, Bogotá',
            'zone_type': 'mixed',
            'status': 'draft',
            'total_area': 4200.0,
            'terrain_value': 1950000.0,
            'construction_cost_per_m2': 2100.0,
            'investment_horizon': 4,
            'selling_price_per_m2': 3400.0,
            'npv': 4650000.0,
            'irr': 0.234
        },
        {
            'name': 'Parque Industrial Sostenible',
            'description': 'Complejo industrial con tecnologías verdes',
            'location': 'Tocancipá, Cundinamarca',
            'zone_type': 'industrial',
            'status': 'draft',
            'total_area': 25000.0,
            'terrain_value': 3800000.0,
            'construction_cost_per_m2': 1500.0,
            'investment_horizon': 7,
            'selling_price_per_m2': 2200.0,
            'npv': 13500000.0,
            'irr': 0.156
        }
    ]
    
    created_count = 0
    
    for project in projects_data:
        try:
            # Calcular valores adicionales
            buildable_area = project['total_area'] * random.uniform(0.7, 0.9)
            total_investment = project['terrain_value'] + (project['total_area'] * project['construction_cost_per_m2'])
            buildability_percentage = (buildable_area / project['total_area']) * 100
            
            # Coordenadas de Bogotá con variación
            lat = 4.6097 + random.uniform(-0.1, 0.1)
            lng = -74.0817 + random.uniform(-0.1, 0.1)
            
            # SQL de inserción
            insert_sql = text("""
                INSERT INTO projects (
                    name, description, location, zone_type, status,
                    total_area, buildable_area, terrain_value, construction_cost_per_m2,
                    investment_horizon, selling_price_per_m2, construction_time_months,
                    selling_time_months, discount_rate, total_investment,
                    buildability_percentage, npv, irr, sustainability_score,
                    carbon_footprint, latitude, longitude, created_at
                ) VALUES (
                    :name, :description, :location, :zone_type, :status,
                    :total_area, :buildable_area, :terrain_value, :construction_cost_per_m2,
                    :investment_horizon, :selling_price_per_m2, :construction_time_months,
                    :selling_time_months, :discount_rate, :total_investment,
                    :buildability_percentage, :npv, :irr, :sustainability_score,
                    :carbon_footprint, :latitude, :longitude, :created_at
                )
            """)
            
            # Ejecutar inserción
            db.execute(insert_sql, {
                'name': project['name'],
                'description': project['description'],
                'location': project['location'],
                'zone_type': project['zone_type'],
                'status': project['status'],
                'total_area': project['total_area'],
                'buildable_area': buildable_area,
                'terrain_value': project['terrain_value'],
                'construction_cost_per_m2': project['construction_cost_per_m2'],
                'investment_horizon': project['investment_horizon'],
                'selling_price_per_m2': project['selling_price_per_m2'],
                'construction_time_months': 12,
                'selling_time_months': 18,
                'discount_rate': 0.12,
                'total_investment': total_investment,
                'buildability_percentage': buildability_percentage,
                'npv': project['npv'],
                'irr': project['irr'],
                'sustainability_score': random.uniform(6.0, 9.5),
                'carbon_footprint': random.uniform(800, 1500),
                'latitude': lat,
                'longitude': lng,
                'created_at': datetime.now()
            })
            
            created_count += 1
            print(f"   ✅ {project['name']}")
            print(f"      💰 NPV: ${project['npv']:,.0f}")
            print(f"      📈 IRR: {project['irr']:.1%}")
            
        except Exception as e:
            print(f"   ❌ Error creando {project['name']}: {e}")
    
    try:
        db.commit()
        print(f"\n🎉 {created_count} proyectos creados exitosamente!")
        return created_count
    except Exception as e:
        print(f"❌ Error en commit: {e}")
        db.rollback()
        return 0

def verify_projects(db: Session):
    """Verificar que los proyectos se crearon correctamente"""
    print("\n📊 VERIFICANDO PROYECTOS CREADOS:")
    print("=" * 60)
    
    try:
        # Contar proyectos
        result = db.execute(text("SELECT COUNT(*) FROM projects"))
        count = result.scalar()
        print(f"📈 Total de proyectos en BD: {count}")
        
        if count > 0:
            # Mostrar proyectos
            result = db.execute(text("""
                SELECT name, location, zone_type, npv, irr, total_area 
                FROM projects 
                ORDER BY npv DESC
            """))
            
            projects = result.fetchall()
            print("\n🏗️  Proyectos creados:")
            
            for project in projects:
                name, location, zone_type, npv, irr, area = project
                status_icon = "🟢" if npv > 0 else "🔴"
                print(f"{status_icon} {name}")
                print(f"   📍 {location} | 🏗️ {zone_type}")
                print(f"   💰 NPV: ${npv:,.0f} | 📈 IRR: {irr:.1%} | 📐 {area:,.0f} m²")
                print()
        
        return count > 0
        
    except Exception as e:
        print(f"❌ Error verificando: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 SCRIPT DEFINITIVO - GENERADOR DE DATOS DE PRUEBA")
    print("=" * 55)
    print("Este script resolverá todos los problemas de enums y constraints.")
    print()
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Paso 1: Crear enums
        create_enums_if_not_exist(db)
        
        # Paso 2: Limpiar datos
        clear_all_data_cascade(db)
        
        # Paso 3: Crear proyectos
        created_count = create_projects_direct_sql(db)
        
        # Paso 4: Verificar
        success = verify_projects(db)
        
        if success:
            print("✅ PROCESO COMPLETADO EXITOSAMENTE!")
            print("\n📋 PRÓXIMOS PASOS:")
            print("1. Ejecutar: python run.py (backend)")
            print("2. Ejecutar: npm start (frontend)")
            print("3. Ir a: localhost:3000/")
            print("4. Dashboard → Comparar Proyectos")
            print("5. ¡Probar la comparación con múltiples proyectos!")
        else:
            print("❌ PROCESO FALLÓ - Revisar errores arriba")
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()