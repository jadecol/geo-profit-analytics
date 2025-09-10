"""
Script para probar la conexión a la base de datos
Ejecutar desde: geo-profit-analytics/backend/
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import test_connection, SQLALCHEMY_DATABASE_URL

def main():
    print("🔧 Probando conexión a base de datos...")
    print(f"📍 URL (sin credenciales): {SQLALCHEMY_DATABASE_URL.split('@')[1] if '@' in SQLALCHEMY_DATABASE_URL else 'URL inválida'}")
    
    if test_connection():
        print("✅ ¡Conexión exitosa! La base de datos está lista.")
        return True
    else:
        print("❌ Error de conexión. Verifica:")
        print("   - Que PostgreSQL esté corriendo")
        print("   - Que la base de datos 'geoprofit' exista")
        print("   - Que el usuario 'geoprofit_user' tenga permisos")
        return False

if __name__ == "__main__":
    main()