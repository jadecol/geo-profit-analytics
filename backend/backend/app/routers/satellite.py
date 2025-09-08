from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from datetime import datetime, timedelta
import io

from app.database import get_db
from app import models, schemas
from app.services.satellite_service import SatelliteImageService
from app.config import settings

router = APIRouter(prefix="/satellite", tags=["satellite"])

@router.post("/mapbox", response_model=schemas.SatelliteImage)
async def get_mapbox_satellite_image(
    request: schemas.SatelliteImageRequest,
    db: Session = Depends(get_db)
):
    """Obtener imagen satelital de Mapbox"""
    
    satellite_service = SatelliteImageService()
    
    try:
        # Obtener imagen de Mapbox
        image_data = await satellite_service.get_mapbox_satellite_image(
            latitude=request.latitude,
            longitude=request.longitude,
            zoom=request.zoom,
            width=request.width,
            height=request.height
        )
        
        if not image_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo obtener la imagen satelital de Mapbox"
            )
        
        # Generar nombre único para el archivo
        filename = f"mapbox_{uuid.uuid4()}.jpg"
        file_path = os.path.join("static", "satellite_images", filename)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Guardar imagen
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        # Calcular resolución aproximada
        bounds = [
            request.longitude - 0.01,  # Aproximación
            request.latitude - 0.01,
            request.longitude + 0.01,
            request.latitude + 0.01
        ]
        
        resolution_info = satellite_service.calculate_image_resolution(
            request.width, request.height, tuple(bounds)
        )
        
        # Guardar en base de datos
        db_image = models.SatelliteImage(
            latitude=request.latitude,
            longitude=request.longitude,
            bounds=bounds,
            source="mapbox",
            zoom_level=request.zoom,
            width=request.width,
            height=request.height,
            resolution_m_per_pixel=resolution_info["average_resolution"],
            image_path=file_path,
            image_url=f"/static/satellite_images/{filename}",
            file_size_bytes=len(image_data)
        )
        
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        return db_image
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener imagen satelital: {str(e)}"
        )

@router.post("/google", response_model=schemas.SatelliteImage)
async def get_google_satellite_image(
    request: schemas.SatelliteImageRequest,
    db: Session = Depends(get_db)
):
    """Obtener imagen satelital de Google Maps"""
    
    satellite_service = SatelliteImageService()
    
    try:
        # Obtener imagen de Google Maps
        image_data = await satellite_service.get_google_satellite_image(
            latitude=request.latitude,
            longitude=request.longitude,
            zoom=request.zoom,
            size=f"{request.width}x{request.height}"
        )
        
        if not image_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo obtener la imagen satelital de Google Maps"
            )
        
        # Generar nombre único para el archivo
        filename = f"google_{uuid.uuid4()}.jpg"
        file_path = os.path.join("static", "satellite_images", filename)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Guardar imagen
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        # Calcular bounds aproximados
        bounds = [
            request.longitude - 0.01,
            request.latitude - 0.01,
            request.longitude + 0.01,
            request.latitude + 0.01
        ]
        
        resolution_info = satellite_service.calculate_image_resolution(
            request.width, request.height, tuple(bounds)
        )
        
        # Guardar en base de datos
        db_image = models.SatelliteImage(
            latitude=request.latitude,
            longitude=request.longitude,
            bounds=bounds,
            source="google",
            zoom_level=request.zoom,
            width=request.width,
            height=request.height,
            resolution_m_per_pixel=resolution_info["average_resolution"],
            image_path=file_path,
            image_url=f"/static/satellite_images/{filename}",
            file_size_bytes=len(image_data)
        )
        
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        return db_image
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener imagen satelital: {str(e)}"
        )

@router.post("/upload", response_model=schemas.SatelliteImage)
async def upload_satellite_image(
    file: UploadFile = File(...),
    bounds: str = None,  # JSON string con bounds
    description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Subir imagen satelital propia"""
    
    # Validar tipo de archivo
    allowed_types = ["image/jpeg", "image/png", "image/tiff", "image/geotiff"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no permitido. Use JPEG, PNG o TIFF"
        )
    
    # Validar tamaño (máximo 50MB)
    max_size = 50 * 1024 * 1024  # 50MB
    file_size = 0
    
    try:
        satellite_service = SatelliteImageService()
        
        # Leer archivo
        file_data = await file.read()
        file_size = len(file_data)
        
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Archivo demasiado grande. Máximo 50MB"
            )
        
        # Procesar imagen
        bounds_coords = None
        if bounds:
            import json
            bounds_data = json.loads(bounds)
            bounds_coords = (
                bounds_data["min_x"],
                bounds_data["min_y"],
                bounds_data["max_x"],
                bounds_data["max_y"]
            )
        
        processed_image = satellite_service.process_uploaded_image(
            file_data, bounds_coords
        )
        
        # Generar nombre único
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        filename = f"uploaded_{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join("static", "satellite_images", filename)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Guardar archivo
        with open(file_path, "wb") as f:
            f.write(file_data)
        
        # Crear imagen georreferenciada si hay bounds
        if bounds_coords:
            georef_filename = f"georef_{uuid.uuid4()}.tif"
            georef_path = os.path.join("static", "satellite_images", georef_filename)
            
            try:
                satellite_service.create_georeferenced_image(
                    file_data, bounds_coords, georef_path
                )
            except Exception as e:
                print(f"Warning: Could not create georeferenced image: {e}")
        
        # Calcular coordenadas centrales si hay bounds
        center_lat = center_lon = None
        resolution = None
        
        if bounds_coords:
            center_lat = (bounds_coords[1] + bounds_coords[3]) / 2
            center_lon = (bounds_coords[0] + bounds_coords[2]) / 2
            
            resolution_info = satellite_service.calculate_image_resolution(
                processed_image["width"],
                processed_image["height"],
                bounds_coords
            )
            resolution = resolution_info["average_resolution"]
        
        # Guardar en base de datos
        db_image = models.SatelliteImage(
            latitude=center_lat,
            longitude=center_lon,
            bounds=list(bounds_coords) if bounds_coords else None,
            source="uploaded",
            zoom_level=None,
            width=processed_image["width"],
            height=processed_image["height"],
            resolution_m_per_pixel=resolution,
            image_path=file_path,
            image_url=f"/static/satellite_images/{filename}",
            file_size_bytes=file_size
        )
        
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        return db_image
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar imagen: {str(e)}"
        )

@router.get("/{image_id}", response_model=schemas.SatelliteImage)
def get_satellite_image(image_id: int, db: Session = Depends(get_db)):
    """Obtener información de imagen satelital"""
    
    image = db.query(models.SatelliteImage).filter(
        models.SatelliteImage.id == image_id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    return image

@router.get("/{image_id}/download")
def download_satellite_image(image_id: int, db: Session = Depends(get_db)):
    """Descargar imagen satelital"""
    
    image = db.query(models.SatelliteImage).filter(
        models.SatelliteImage.id == image_id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    if not os.path.exists(image.image_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo de imagen no encontrado"
        )
    
    def iterfile(file_path: str):
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk
    
    filename = os.path.basename(image.image_path)
    media_type = "image/jpeg" if filename.endswith('.jpg') else "image/png"
    
    return StreamingResponse(
        iterfile(image.image_path),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.delete("/{image_id}")
def delete_satellite_image(image_id: int, db: Session = Depends(get_db)):
    """Eliminar imagen satelital"""
    
    image = db.query(models.SatelliteImage).filter(
        models.SatelliteImage.id == image_id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    try:
        # Eliminar archivo físico
        if os.path.exists(image.image_path):
            os.remove(image.image_path)
        
        # Eliminar de base de datos
        db.delete(image)
        db.commit()
        
        return {"message": "Imagen eliminada exitosamente"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar imagen: {str(e)}"
        )

@router.get("/search/nearby")
def search_nearby_images(
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Buscar imágenes satelitales cercanas a una ubicación"""
    
    # Conversión aproximada de km a grados
    # 1 grado ≈ 111 km
    radius_degrees = radius_km / 111.0
    
    images = db.query(models.SatelliteImage).filter(
        models.SatelliteImage.latitude.between(
            latitude - radius_degrees,
            latitude + radius_degrees
        ),
        models.SatelliteImage.longitude.between(
            longitude - radius_degrees,
            longitude + radius_degrees
        )
    ).limit(limit).all()
    
    return {
        "search_center": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
        "results_count": len(images),
        "images": images
    }

@router.get("/stats/usage")
def get_satellite_usage_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas de uso de imágenes satelitales"""
    
    from sqlalchemy import func
    
    # Estadísticas por fuente
    source_stats = db.query(
        models.SatelliteImage.source,
        func.count(models.SatelliteImage.id).label('count'),
        func.sum(models.SatelliteImage.file_size_bytes).label('total_size')
    ).group_by(models.SatelliteImage.source).all()
    
    # Estadísticas generales
    total_images = db.query(func.count(models.SatelliteImage.id)).scalar()
    total_size = db.query(func.sum(models.SatelliteImage.file_size_bytes)).scalar() or 0
    
    # Imágenes recientes (último mes)
    one_month_ago = datetime.now() - timedelta(days=30)
    recent_images = db.query(func.count(models.SatelliteImage.id)).filter(
        models.SatelliteImage.created_at >= one_month_ago
    ).scalar()
    
    return {
        "total_images": total_images,
        "total_size_bytes": total_size,
        "total_size_mb": total_size / (1024 * 1024),
        "recent_images_30d": recent_images,
        "by_source": [
            {
                "source": stat.source,
                "count": stat.count,
                "size_bytes": stat.total_size or 0,
                "size_mb": (stat.total_size or 0) / (1024 * 1024)
            }
            for stat in source_stats
        ]
    }