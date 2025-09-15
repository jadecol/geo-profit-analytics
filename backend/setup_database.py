import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import engine
from app.models import Base
from sqlalchemy import text

def setup_database():
    print("Configurando base de datos...")
    
    try:
        # Crear enums primero
        with engine.connect() as conn:
            # Crear enum ZoneType
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'zonetype') THEN
                        CREATE TYPE zonetype AS ENUM ('residential', 'commercial', 'mixed', 'industrial');
                    END IF;
                END
                $$;
            """))
            
            # Crear enum ProjectStatus
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'projectstatus') THEN
                        CREATE TYPE projectstatus AS ENUM ('draft', 'analysis', 'completed', 'archived');
                    END IF;
                END
                $$;
            """))
            
            conn.commit()
            print("Enums creados correctamente")
    
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas correctamente")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    setup_database()
