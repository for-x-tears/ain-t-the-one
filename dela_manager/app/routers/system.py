from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db

router = APIRouter(tags=["system"])

@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "unavailable"

    return {
        "status": "ok",
        "db": db_status,
        
        "minio": "not configured yet"
    }

@router.get("/info")
async def info():
    return {
        "version": "1.0.0",
        "environment": "development",
        "description": "Task Manager API"
    }