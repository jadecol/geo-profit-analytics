from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import io
import base64
from datetime import datetime

from app.database import get_db
from app import models, schemas
from app.services.satellite_service import SatelliteImageService

router = APIRouter(prefix="/satellite", tags=["satellite"])

@router.post("/mapbox", response_model=schemas.SatelliteImage)
async def get_mapbox_image(
    request: schemas.SatelliteImageRequest,
    db: Session = Depends(get_db)
):
    '''Obtener imagen satelital de Mapbox'''
    
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
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo obtener imagen de Mapbox"
            )
        
        # Calcular resolución aproximada
        bounds = [
            request.longitude - 0.01,  # Aproximación para zoom
            request.latitude - 0.01,
            request.longitude + 0.01,
            request.latitude + 0.01
        ]
        
        # Guardar en base de datos
        db_image = models.SatelliteImage(
            latitude=request.latitude,
            longitude=request.longitude,
            bounds=bounds,
            source=request.source,
            zoom_level=request.zoom,
            width=request.width,
            height=request.height,
            resolution_m_per_pixel=10.0,  # Valor aproximado
            image_url=f"/satellite/images/{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
            file_size_bytes=len(image_data)
        )
        
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        return schemas.SatelliteImage.from_orm(db_image)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo imagen satelital: {str(e)}"
        )

@router.post("/upload", response_model=schemas.SatelliteImage)
async def upload_satellite_image(
    file: UploadFile = File(...),
    latitude: float = 0,
    longitude: float = 0,
    min_x: float = 0,
    min_y: float = 0,
    max_x: float = 0,
    max_y: float = 0,
    db: Session = Depends(get_db)
):
    '''Subir imagen satelital propia'''
    
    try:
        # Validar archivo
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser una imagen"
            )
        
        # Leer archivo
        file_data = await file.read()
        
        # Guardar en base de datos
        db_image = models.SatelliteImage(
            latitude=latitude,
            longitude=longitude,
            bounds=[min_x, min_y, max_x, max_y] if any([min_x, min_y, max_x, max_y]) else None,
            source="uploaded",
            width=1024,  # Valor por defecto
            height=1024,
            resolution_m_per_pixel=1.0,
            image_url=f"/satellite/images/upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
            file_size_bytes=len(file_data)
        )
        
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        return schemas.SatelliteImage.from_orm(db_image)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error subiendo imagen: {str(e)}"
        )

@router.get("/images/{image_id}")
async def get_satellite_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    '''Obtener imagen satelital por ID'''
    
    image = db.query(models.SatelliteImage).filter(models.SatelliteImage.id == image_id).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    return schemas.SatelliteImage.from_orm(image)

@router.get("/list")
def list_satellite_images(
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    '''Listar imágenes satelitales disponibles'''
    
    query = db.query(models.SatelliteImage)
    
    if source:
        query = query.filter(models.SatelliteImage.source == source)
    
    images = query.order_by(models.SatelliteImage.created_at.desc()).limit(50).all()
    
    return {
        "total": len(images),
        "images": [schemas.SatelliteImage.from_orm(img) for img in images]
    }
