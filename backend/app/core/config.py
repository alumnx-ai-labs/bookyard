"""Application configuration."""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Project Metadata
    PROJECT_NAME: str = "Bookyard API"
    DESCRIPTION: str = "FastAPI application for book management"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    
    # CORS - Accept both string and list
    ALLOWED_ORIGINS: Union[List[str], str] = Field(
        default="http://localhost:3000,http://localhost:5173"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/bookyard"
    )
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


settings = Settings()