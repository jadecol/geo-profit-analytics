#!/usr/bin/env python3
"""
Script para reinicializar la base de datos completamente
Uso: python scripts/reset_database.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.database import engine, SQLALCHEMY_DATABASE_URL
from app.models import Base
from sqlalchemy import text
import re

def get_db_params(url):
    """Extraer parámetros de conexión de la URL"""
    pattern = r'postgresql\+psycopg2://(\w+):([^@]+)@([^:]+):(\d+)/(\w+)'
    match = re.match(pattern, url)
    if match:
        return {
            'user': match.group(1),
            'password': match.group(2),
            'host': match.group(3),
            'port': int(match.group(4)),
            'database': match.group(5)
        }
    return None

def reset_database():
    """Resetear base de datos completamente"""
    print("🔧 Reseteando base de datos...")
    
    try:
        # Obtener parámetros de conexión
        db_params = get_db_params(SQLALCHEMY_DATABASE_URL)
        if not db_params:
            print("❌ No se pudieron extraer parámetros de la URL")
            return False
        
        db_name = db_params['database']
        
        # Conectar a postgres para poder eliminar/crear la BD
        admin_conn = psycopg2.connect(
            host=db_params['host'],
            port=db_params['port'],
            database='postgres',
            user='postgres',
            password='postgres'
        )
        admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        admin_cursor = admin_conn.cursor()
        
        # Terminar conexiones activas
        admin_cursor.execute(f"""
            SELECT pg_terminate_backend(pid) 
            FROM pg_stat_activity 
            WHERE datname = '{db_name}' AND pid <> pg_backend_pid();
        """)
        
        # Eliminar y recrear base de datos
        admin_cursor.execute(f'DROP DATABASE IF EXISTS {db_name};')
        admin_cursor.execute(f'CREATE DATABASE {db_name} OWNER {db_params["user"]};')
        
        admin_cursor.close()
        admin_conn.close()
        print(f"✅ Base de datos '{db_name}' recreada")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Método 1 falló: {e}")
        print("🔄 Intentando método alternativo...")
        return reset_tables_only()

def reset_tables_only():
    """Método alternativo: solo resetear tablas y enums"""
    try:
        with engine.connect() as conn:
            # Eliminar tablas en orden correcto (FK primero)
            conn.execute(text('DROP TABLE IF EXISTS project_analyses CASCADE;'))
            conn.execute(text('DROP TABLE IF EXISTS project_restrictions CASCADE;'))
            conn.execute(text('DROP TABLE IF EXISTS satellite_images CASCADE;'))
            conn.execute(text('DROP TABLE IF EXISTS user_sessions CASCADE;'))
            conn.execute(text('DROP TABLE IF EXISTS projects CASCADE;'))
            
            # Eliminar enums
            conn.execute(text('DROP TYPE IF EXISTS zonetype CASCADE;'))
            conn.execute(text('DROP TYPE IF EXISTS projectstatus CASCADE;'))
            
            conn.commit()
            print("✅ Tablas y enums eliminados")
            
        return True
        
    except Exception as e:
        print(f"❌ Error en reset de tablas: {e}")
        return False

def create_schema():
    """Crear esquema de base de datos"""
    try:
        with engine.connect() as conn:
            # Crear enums
            conn.execute(text("CREATE TYPE zonetype AS ENUM ('residential', 'commercial', 'mixed', 'industrial');"))
            conn.execute(text("CREATE TYPE projectstatus AS ENUM ('draft', 'analysis', 'completed', 'archived');"))
            conn.commit()
            print("✅ Enums creados")
        
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas")
        return True
        
    except Exception as e:
        print(f"❌ Error creando schema: {e}")
        return False

def create_test_data():
    """Crear datos de prueba"""
    try:
        from app.models import Project, ZoneType, ProjectStatus
        from app.database import SessionLocal
        
        db = SessionLocal()
        
        # Limpiar datos existentes
        db.query(Project).delete()
        
        # Crear proyectos de prueba
        test_projects = [
            Project(
                name="Proyecto Residencial Demo",
                description="Proyecto de desarrollo residencial para pruebas",
                location="Bogotá, Colombia",
                zone_type=ZoneType.RESIDENTIAL,
                total_area=5000.0,
                terrain_value=500000.0,
                construction_cost_per_m2=800.0,
                investment_horizon=5,
                status=ProjectStatus.DRAFT
            ),
            Project(
                name="Centro Comercial Test",
                description="Proyecto comercial para pruebas",
                location="Medellín, Colombia",
                zone_type=ZoneType.COMMERCIAL,
                total_area=8000.0,
                terrain_value=1200000.0,
                construction_cost_per_m2=1200.0,
                investment_horizon=7,
                status=ProjectStatus.DRAFT
            )
        ]
        
        for project in test_projects:
            db.add(project)
        
        db.commit()
        db.close()
        print("✅ Datos de prueba creados")
        return True
        
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        return False

def main():
    """Ejecutar reset completo"""
    print("🚀 Iniciando reset de base de datos...")
    
    if not reset_database():
        print("❌ Falló el reset de base de datos")
        return False
    
    if not create_schema():
        print("❌ Falló la creación del schema")
        return False
    
    if not create_test_data():
        print("⚠️  Falló la creación de datos de prueba")
    
    print("🎉 Reset completado exitosamente!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)