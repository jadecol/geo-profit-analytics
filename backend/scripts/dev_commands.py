#!/usr/bin/env python3
"""
Comandos útiles para desarrollo
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def show_projects():
    """Mostrar todos los proyectos en la BD"""
    from app.database import SessionLocal
    from app.models import Project
    
    db = SessionLocal()
    projects = db.query(Project).all()
    
    if not projects:
        print("📋 No hay proyectos en la base de datos")
    else:
        print(f"📋 Proyectos encontrados ({len(projects)}):")
        for p in projects:
            print(f"  • ID: {p.id} | {p.name} | {p.location} | {p.status.value}")
    
    db.close()

def clear_projects():
    """Eliminar todos los proyectos"""
    from app.database import SessionLocal
    from app.models import Project
    
    db = SessionLocal()
    count = db.query(Project).count()
    db.query(Project).delete()
    db.commit()
    db.close()
    
    print(f"🗑️  {count} proyectos eliminados")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/dev_commands.py <comando>")
        print("Comandos disponibles: show_projects, clear_projects")
        sys.exit(1)
    
    command = sys.argv[1]
    if command == "show_projects":
        show_projects()
    elif command == "clear_projects":
        clear_projects()
    else:
        print(f"Comando desconocido: {command}")