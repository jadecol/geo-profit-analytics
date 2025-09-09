from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/satellite", tags=["satellite"])

@router.get("/")
def list_satellite(db: Session = Depends(get_db)):
    return {"message": "Satellite router working"}
