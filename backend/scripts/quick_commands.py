#!/usr/bin/env python3
"""
Comandos rápidos para desarrollo
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def reset_and_restart():
    """Reset BD y mostrar comando para reiniciar backend"""
    os.system("python scripts/reset_database.py")
    print("\n" + "="*50)
    print("SIGUIENTE PASO:")
    print("1. En Terminal 1 (backend): Ctrl+C")
    print("2. Luego ejecutar: python run.py")
    print("3. Probar frontend en localhost:3000")
    print("="*50)

def show_projects():
    from app.database import SessionLocal
    from app.models import Project
    
    db = SessionLocal()
    projects = db.query(Project).all()
    
    if not projects:
        print("No hay proyectos")
    else:
        print(f"Proyectos ({len(projects)}):")
        for p in projects:
            print(f"  ID: {p.id} | {p.name} | {p.location}")
    db.close()

def test_analysis():
    """Probar análisis financiero en el primer proyecto"""
    from app.services.financial_service import FinancialService, ProjectFinancials
    
    financial_data = ProjectFinancials(
        terrain_cost=500000,
        construction_cost_per_m2=800,
        total_area=5000,
        buildable_area=3500,
        selling_price_per_m2=1200,
        construction_time_months=12,
        selling_time_months=12,
        discount_rate=0.12
    )
    
    service = FinancialService()
    result = service.calculate_npv_irr(financial_data)
    
    print("ANÁLISIS FINANCIERO DE PRUEBA:")
    print(f"NPV: ${result['npv']:,.2f}")
    print(f"IRR: {result['irr_annual']:.2%}" if result['irr_annual'] else "IRR: No calculable")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Comandos disponibles:")
        print("  reset     - Resetear base de datos")
        print("  show      - Mostrar proyectos")
        print("  test      - Probar análisis financiero")
        sys.exit(1)
    
    command = sys.argv[1]
    if command == "reset":
        reset_and_restart()
    elif command == "show":
        show_projects()
    elif command == "test":
        test_analysis()
    else:
        print(f"Comando desconocido: {command}")