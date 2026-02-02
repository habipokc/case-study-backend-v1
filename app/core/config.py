from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Case Study"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/casestudy"
    SECRET_KEY: str = "your-secret-key-change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Pydantic v2 Settings Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

settings = Settings()
