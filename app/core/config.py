from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Case Study"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/casestudy"
    SECRET_KEY: str = "your-secret-key-change-me-in-production" # In real app, get from env
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    class Config:
        case_sensitive = True

settings = Settings()
