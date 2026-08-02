"""
NFM-X Configuration Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = Field(default="NFM-X", env="APP_NAME")
    app_version: str = Field(default="1.5.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    database_url: str = Field(default="sqlite+aiosqlite:///./nfm.db", env="DATABASE_URL")
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8080", env="CORS_ORIGINS")
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    embedding_model_name: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    embedding_dimension: int = Field(default=384, env="EMBEDDING_DIMENSION")
    faiss_index_path: str = Field(default="./faiss_index", env="FAISS_INDEX_PATH")
    data_dir: Path = Field(default=Path("./data"), env="DATA_DIR")
    backup_dir: Path = Field(default=Path("./backups"), env="BACKUP_DIR")
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    max_memory_size: int = Field(default=1000000, env="MAX_MEMORY_SIZE")
    memory_batch_size: int = Field(default=100, env="MEMORY_BATCH_SIZE")
    consolidation_interval_hours: int = Field(default=1, env="CONSOLIDATION_INTERVAL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

# Ensure directories exist
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.backup_dir.mkdir(parents=True, exist_ok=True)
Path(settings.faiss_index_path).parent.mkdir(parents=True, exist_ok=True)