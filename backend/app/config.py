from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    NFM_HOST: str = "0.0.0.0"
    NFM_PORT: int = 8765
    NFM_DEBUG: bool = True
    NFM_LOG_LEVEL: str = "INFO"

    NFM_STORAGE_PATH: Path = Path("./storage")
    NFM_DB_PATH: Path = Path("./storage/nfm.db")
    NFM_VECTOR_PATH: Path = Path("./storage/vectors")

    NFM_DB_POOL_SIZE: int = 5
    NFM_DB_MAX_OVERFLOW: int = 10

    NFM_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    NFM_EMBEDDING_DIM: int = 384

    NFM_MAX_CONTEXT_MEMORIES: int = 20
    NFM_MIN_CONFIDENCE: float = 0.3
    NFM_DEFAULT_CONFIDENCE: float = 0.7
    NFM_MEMORY_EXPIRY_DAYS: int = 30

    NFM_SEMANTIC_WEIGHT: float = 0.7
    NFM_KEYWORD_WEIGHT: float = 0.3

    NFM_API_TOKEN: Optional[str] = None
    NFM_ENABLE_AUTH: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
