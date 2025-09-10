import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://geoprofit_user:mi_clave_123@localhost:5432/geoprofit"
    
    # Database Pool Settings
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    
    # Security
    secret_key: str = "tu-clave-super-secreta-aqui-cambiar-en-produccion"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # Application
    environment: str = "development"
    debug: bool = True
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # API Keys
    mapbox_api_key: str = ""
    google_maps_api_key: str = ""
    
    class Config:
        env_file = ".env"
        # Permitir variables extra para flexibilidad
        extra = "ignore"

settings = Settings()