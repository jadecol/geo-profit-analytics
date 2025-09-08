import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://geoprofit_user:password@localhost:5432/geoprofit"
    
    # Security
    secret_key: str = "change-this-in-production-with-a-secure-random-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # Application
    environment: str = "development"
    debug: bool = True
    allowed_origins: str = "http://localhost:3000"
    
    # API Keys
    mapbox_api_key: str = ""
    google_maps_api_key: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()