from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    return {"message": "Projects router working"}
