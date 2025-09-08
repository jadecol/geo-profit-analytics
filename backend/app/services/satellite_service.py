import httpx
import base64
from typing import Optional, Dict, Tuple
from PIL import Image
import io
import rasterio
from rasterio.transform import from_bounds
import numpy as np
from app.config import settings

class SatelliteImageService:
    
    def __init__(self):
        self.mapbox_api_key = settings.mapbox_api_key
        self.google_api_key = settings.google_maps_api_key
    
    async def get_mapbox_satellite_image(
        self, 
        latitude: float, 
        longitude: float, 
        zoom: int = 18,
        width: int = 1024,
        height: int = 1024
    ) -> Optional[bytes]:
        """Obtener imagen satelital de Mapbox"""
        if not self.mapbox_api_key:
            raise ValueError("Mapbox API key not configured")
        
        url = (
            f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
            f"{longitude},{latitude},{zoom}/{width}x{height}@2x"
            f"?access_token={self.mapbox_api_key}"
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.content
            return None
    
    async def get_google_satellite_image(
        self,
        latitude: float,
        longitude: float,
        zoom: int = 20,
        size: str = "1024x1024"
    ) -> Optional[bytes]:
        """Obtener imagen satelital de Google Maps"""
        if not self.google_api_key:
            raise ValueError("Google Maps API key not configured")
        
        url = (
            f"https://maps.googleapis.com/maps/api/staticmap?"
            f"center={latitude},{longitude}&zoom={zoom}&size={size}"
            f"&maptype=satellite&key={self.google_api_key}"
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.content
            return None
    
    def process_uploaded_image(
        self, 
        image_data: bytes,
        bounds: Optional[Tuple[float, float, float, float]] = None
    ) -> Dict:
        """Procesar imagen subida por el usuario"""
        try:
            # Abrir imagen con Pillow
            image = Image.open(io.BytesIO(image_data))
            
            # Obtener información básica
            width, height = image.size
            format_img = image.format
            
            # Convertir a base64 para frontend
            buffered = io.BytesIO()
            image.save(buffered, format=format_img or 'PNG')
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            result = {
                "width": width,
                "height": height,
                "format": format_img,
                "base64": img_base64,
                "has_georeference": False
            }
            
            # Si hay bounds, crear georreferenciación
            if bounds:
                result["bounds"] = bounds
                result["has_georeference"] = True
            
            return result
            
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
    
    def create_georeferenced_image(
        self,
        image_data: bytes,
        bounds: Tuple[float, float, float, float],  # (min_x, min_y, max_x, max_y)
        output_path: str
    ):
        """Crear imagen georreferenciada con rasterio"""
        try:
            # Abrir imagen con Pillow
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # Si es RGB, reorganizar canales
            if len(image_array.shape) == 3:
                image_array = np.transpose(image_array, (2, 0, 1))
            
            # Crear transformación geográfica
            transform = from_bounds(*bounds, image.width, image.height)
            
            # Guardar como GeoTIFF
            with rasterio.open(
                output_path,
                'w',
                driver='GTiff',
                height=image.height,
                width=image.width,
                count=image_array.shape[0] if len(image_array.shape) == 3 else 1,
                dtype=image_array.dtype,
                crs='EPSG:4326',  # WGS84
                transform=transform
            ) as dst:
                if len(image_array.shape) == 3:
                    for i in range(image_array.shape[0]):
                        dst.write(image_array[i], i + 1)
                else:
                    dst.write(image_array, 1)
            
            return True
            
        except Exception as e:
            raise ValueError(f"Error creating georeferenced image: {str(e)}")
    
    def calculate_image_resolution(
        self,
        image_width: int,
        image_height: int,
        bounds: Tuple[float, float, float, float]
    ) -> Dict[str, float]:
        """Calcular resolución de imagen en metros por píxel"""
        min_x, min_y, max_x, max_y = bounds
        
        # Calcular dimensiones en metros (aproximado)
        # Esta es una aproximación, para mayor precisión usar pyproj
        lat_center = (min_y + max_y) / 2
        
        # 1 grado de latitud ≈ 111,320 metros
        # 1 grado de longitud ≈ 111,320 * cos(latitud) metros
        lat_meters = (max_y - min_y) * 111320
        lon_meters = (max_x - min_x) * 111320 * np.cos(np.radians(lat_center))
        
        # Resolución en metros por píxel
        x_resolution = lon_meters / image_width
        y_resolution = lat_meters / image_height
        
        return {
            "x_resolution_m_per_pixel": x_resolution,
            "y_resolution_m_per_pixel": y_resolution,
            "average_resolution": (x_resolution + y_resolution) / 2
        }