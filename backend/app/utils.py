"""
Utilidades generales para GeoProfit Analytics
"""
import os
import uuid
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import math

def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
    """Generar nombre único para archivos"""
    
    # Obtener extensión
    file_extension = ""
    if "." in original_filename:
        file_extension = "." + original_filename.split(".")[-1].lower()
    
    # Generar nombre único
    unique_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if prefix:
        return f"{prefix}_{timestamp}_{unique_id}{file_extension}"
    else:
        return f"{timestamp}_{unique_id}{file_extension}"

def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validar coordenadas geográficas"""
    return -90 <= latitude <= 90 and -180 <= longitude <= 180

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcular distancia entre dos puntos usando fórmula Haversine"""
    
    # Radio de la Tierra en kilómetros
    R = 6371
    
    # Convertir a radianes
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Diferencias
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Fórmula Haversine
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def format_currency(amount: float, currency: str = "USD") -> str:
    """Formatear cantidad como moneda"""
    
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "COP":
        return f"${amount:,.0f} COP"
    else:
        return f"{amount:,.2f} {currency}"

def format_area(area_m2: float) -> Dict[str, str]:
    """Formatear área en diferentes unidades"""
    
    return {
        "m2": f"{area_m2:,.2f} m²",
        "hectares": f"{area_m2/10000:.4f} ha",
        "acres": f"{area_m2*0.000247105:.4f} acres"
    }

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calcular cambio porcentual"""
    
    if old_value == 0:
        return 0
    
    return ((new_value - old_value) / abs(old_value)) * 100

def sanitize_filename(filename: str) -> str:
    """Sanitizar nombre de archivo"""
    
    # Caracteres permitidos
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    
    # Filtrar caracteres
    sanitized = "".join(c for c in filename if c in allowed_chars)
    
    # Limitar longitud
    if len(sanitized) > 100:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:90] + ext
    
    return sanitized

def create_file_hash(file_path: str) -> str:
    """Crear hash MD5 de un archivo"""
    
    hash_md5 = hashlib.md5()
    
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""

def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """División segura evitando división por cero"""
    
    if denominator == 0:
        return default
    
    return numerator / denominator

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncar texto a longitud máxima"""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def validate_email(email: str) -> bool:
    """Validación básica de email"""
    
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.match(pattern, email) is not None

def parse_boolean_string(value: str) -> bool:
    """Convertir string a boolean"""
    
    if isinstance(value, bool):
        return value
    
    return str(value).lower() in ['true', '1', 'yes', 'on', 'enabled']

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Fusionar múltiples diccionarios"""
    
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    
    return result

def get_file_size_mb(file_path: str) -> float:
    """Obtener tamaño de archivo en MB"""
    
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0

def create_directory_if_not_exists(directory_path: str) -> bool:
    """Crear directorio si no existe"""
    
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception:
        return False

def is_valid_json(json_string: str) -> bool:
    """Validar si un string es JSON válido"""
    
    try:
        json.loads(json_string)
        return True
    except (json.JSONDecodeError, TypeError):
        return False

def format_duration_minutes(minutes: int) -> str:
    """Formatear duración en minutos a formato legible"""
    
    if minutes < 60:
        return f"{minutes} minutos"
    elif minutes < 1440:  # 24 horas
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} {'hora' if hours == 1 else 'horas'}"
        else:
            return f"{hours}h {remaining_minutes}min"
    else:  # Días
        days = minutes // 1440
        remaining_hours = (minutes % 1440) // 60
        if remaining_hours == 0:
            return f"{days} {'día' if days == 1 else 'días'}"
        else:
            return f"{days}d {remaining_hours}h"

class Logger:
    """Logger simple para desarrollo"""
    
    @staticmethod
    def info(message: str):
        print(f"[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")
    
    @staticmethod
    def error(message: str):
        print(f"[ERROR] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")
    
    @staticmethod
    def warning(message: str):
        print(f"[WARNING] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

# Constantes útiles para Colombia
COLOMBIA_COORDS = {
    "BOGOTA": {"lat": 4.6097, "lon": -74.0817},
    "MEDELLIN": {"lat": 6.2442, "lon": -75.5812},
    "CALI": {"lat": 3.4516, "lon": -76.5320},
    "BARRANQUILLA": {"lat": 10.9639, "lon": -74.7964},
    "CARTAGENA": {"lat": 10.3910, "lon": -75.4794}
}

# Factores de conversión útiles
CONVERSION_FACTORS = {
    "M2_TO_HECTARES": 0.0001,
    "M2_TO_ACRES": 0.000247105,
    "KM_TO_MILES": 0.621371,
    "USD_TO_COP_APPROX": 4000  # Aproximado, usar API real en producción
}