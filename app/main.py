from fastapi import FastAPI

app = FastAPI(
    title="Python Backend Case Study",
    description="API for Case Study",
    version="1.0.0"
)

from sqlalchemy import text
from app.core.database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

@app.get("/")
async def root():
    return {"message": "Service is up and running"}

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Simple query to check DB connection
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
