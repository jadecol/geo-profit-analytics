from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/")
def list_reports(db: Session = Depends(get_db)):
    return {"message": "Reports router working"}
