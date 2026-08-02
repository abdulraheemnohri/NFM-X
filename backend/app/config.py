"""
Configuration settings for NFM-X using Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    app_name: str = "NFM-X"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False)
    
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    
    database_url: str = Field(default="sqlite+aiosqlite:///./storage/nfm-x.db")
    
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    embedding_dimension: int = Field(default=384)
    
    faiss_index_path: str = Field(default="./storage/faiss_index")
    
    max_context_length: int = Field(default=4096)
    default_confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    default_importance: float = Field(default=0.5, ge=0.0, le=1.0)
    
    api_prefix: str = Field(default="/v1")
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8000")
    
    secret_key: str = Field(default="change-me-in-production")
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    @property
    def cors_origins_list(self) -> list[str]:
        return self.cors_origins if isinstance(self.cors_origins, list) else [self.cors_origins]


settings = Settings()
Path(settings.faiss_index_path).parent.mkdir(parents=True, exist_ok=True)
Path("./storage").mkdir(parents=True, exist_ok=True)