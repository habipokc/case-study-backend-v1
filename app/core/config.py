from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Case Study"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/casestudy"
    
    class Config:
        case_sensitive = True

settings = Settings()
