"""
Script para ejecutar GeoProfit Analytics API
"""
import uvicorn
import os
from app.config import settings

if __name__ == "__main__":
    # Configuración por defecto para desarrollo
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    print("🚀 Iniciando GeoProfit Analytics API...")
    print(f"📍 Entorno: {settings.environment}")
    print(f"🌐 Servidor: http://{host}:{port}")
    print(f"📚 Documentación: http://{host}:{port}/docs")
    print("="*50)
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )