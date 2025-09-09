"""
Script para verificar las importaciones del proyecto GeoProfit
Ejecutar desde backend/
"""

import sys
import os

# Añadir el directorio actual al path
sys.path.insert(0, os.getcwd())

def check_imports():
    """Verificar todas las importaciones críticas"""
    
    print("🔍 Verificando importaciones...")
    print("=" * 50)
    
    # 1. Verificar configuración básica
    try:
        from app.config import settings
        print("✅ Configuración cargada correctamente")
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False
    
    # 2. Verificar base de datos
    try:
        from app.database import Base, get_db
        print("✅ Base de datos configurada")
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False
    
    # 3. Verificar modelos
    try:
        from app import models
        print("✅ Modelos cargados")
    except Exception as e:
        print(f"❌ Error en modelos: {e}")
        return False
    
    # 4. Verificar schemas
    try:
        from app import schemas
        print("✅ Schemas cargados")
    except Exception as e:
        print(f"❌ Error en schemas: {e}")
        return False
    
    # 5. Verificar servicios
    services_ok = True
    services = [
        "financial_service",
        "geospatial_service", 
        "satellite_service",
        "sustainability_service"
    ]
    
    for service in services:
        try:
            module = __import__(f"app.services.{service}", fromlist=[service])
            print(f"✅ Servicio {service} cargado")
        except Exception as e:
            print(f"❌ Error en servicio {service}: {e}")
            services_ok = False
    
    # 6. Verificar routers
    print("\n📂 Verificando routers...")
    
    # Verificar si el directorio routers existe
    routers_path = "app/routers"
    if not os.path.exists(routers_path):
        print(f"❌ Directorio {routers_path} no existe")
        return False
    
    # Verificar archivos de routers
    router_files = ["__init__.py", "analysis.py", "projects.py", "reports.py", "satellite.py"]
    
    for router_file in router_files:
        file_path = os.path.join(routers_path, router_file)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            if file_size > 100:  # Archivo con contenido real
                print(f"✅ {router_file} encontrado ({file_size} bytes)")
            else:
                print(f"⚠️ {router_file} encontrado pero muy pequeño ({file_size} bytes)")
        else:
            print(f"❌ {router_file} no encontrado")
    
    # 7. Intentar importar routers
    print("\n🔌 Intentando importar routers...")
    routers_ok = True
    router_names = ["analysis", "projects", "reports", "satellite"]
    
    for router_name in router_names:
        try:
            module = __import__(f"app.routers.{router_name}", fromlist=["router"])
            if hasattr(module, "router"):
                print(f"✅ Router {router_name} importado correctamente")
            else:
                print(f"⚠️ Router {router_name} importado pero sin objeto 'router'")
        except Exception as e:
            print(f"❌ Error importando router {router_name}: {e}")
            routers_ok = False
    
    # 8. Verificar main.py
    print("\n🚀 Verificando main.py...")
    try:
        from app.main import app
        print("✅ Aplicación FastAPI cargada correctamente")
    except Exception as e:
        print(f"❌ Error en main.py: {e}")
        return False
    
    print("\n" + "=" * 50)
    
    if services_ok and routers_ok:
        print("✅ TODAS LAS IMPORTACIONES FUNCIONAN CORRECTAMENTE")
        return True
    else:
        print("⚠️ HAY PROBLEMAS CON ALGUNAS IMPORTACIONES")
        print("\nPróximos pasos:")
        print("1. Verificar que todos los archivos de routers tengan contenido")
        print("2. Revisar las dependencias en requirements.txt")
        print("3. Verificar la configuración de la base de datos")
        return False

if __name__ == "__main__":
    # Cambiar al directorio backend si no estamos ahí
    if os.path.basename(os.getcwd()) != "backend":
        if os.path.exists("backend"):
            os.chdir("backend")
            print("📁 Cambiando al directorio backend/\n")
        else:
            print("❌ No se encuentra el directorio backend")
            sys.exit(1)
    
    success = check_imports()
    
    if success:
        print("\n🎉 ¡Todo listo para ejecutar el servidor!")
        print("\nEjecuta: python run.py")
    else:
        print("\n❌ Hay problemas que resolver antes de ejecutar el servidor")
        sys.exit(1)