"""
NFM-X Configuration Management
Centralized configuration for all versions (V1-V4)
Loads from environment variables with sensible defaults
"""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class OCRConfig(BaseModel):
    """OCR Engine Configuration"""
    enabled: bool = Field(default=True, description="Enable OCR processing")
    engine: str = Field(default="easyocr", description="OCR engine: easyocr, tesseract, cloud")
    languages: List[str] = Field(default_factory=lambda: ["en"], description="List of OCR languages")
    table_extraction: bool = Field(default=False, description="Enable table extraction from PDFs")
    easyocr_model: str = Field(default="en", description="EasyOCR model to use")
    tesseract_path: Optional[str] = Field(default=None, description="Path to Tesseract executable")
    cloud_provider: str = Field(default="", description="Cloud OCR provider: azure, google")
    cloud_api_key: str = Field(default="", description="API key for cloud OCR")


class CompressionConfig(BaseModel):
    """Compression Configuration"""
    enabled: bool = Field(default=True, description="Enable automatic compression")
    age_days: int = Field(default=30, description="Compress memories older than N days")
    importance_threshold: float = Field(default=0.5, description="Only compress memories with importance below this")
    run_interval_hours: int = Field(default=24, description="Run compression every N hours")
    max_per_run: int = Field(default=100, description="Max memories to compress per run")
    archive_enabled: bool = Field(default=True, description="Enable archiving of old memories")
    archive_age_days: int = Field(default=90, description="Archive memories older than N days")


class SyncConfig(BaseModel):
    """Synchronization Configuration"""
    enabled: bool = Field(default=True, description="Enable synchronization")
    conflict_strategy: str = Field(default="ti
mestamp", description="Default conflict resolution strategy")
    auto_resolve: bool = Field(default=True, description="Auto-resolve conflicts when detected")
    sync_interval_seconds: int = Field(default=60, description="Sync interval in seconds")
    max_retries: int = Field(default=3, description="Max retries for failed syncs")


class MCPConfig(BaseModel):
    """Model Context Protocol Configuration"""
    enabled: bool = Field(default=False, description="Enable MCP server")
    host: str = Field(default="localhost", description="MCP server host")
    port: int = Field(default=8765, description="MCP server port")
    api_key: str = Field(default="", description="MCP API key for authentication")
    require_auth: bool = Field(default=False, description="Require API key for MCP access")


class CORSConfig(BaseModel):
    """CORS Configuration"""
    allow_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8765", "http://127.0.0.1:3000"],
        description="Allowed origins for CORS"
    )
    allow_credentials: bool = Field(default=True, description="Allow credentials in CORS")
    allow_methods: List[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        description="Allowed HTTP methods"
    )
    allow_headers: List[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed headers"
    )
    expose_headers: List[str] = Field(
        default_factory=lambda: ["*"],
        description="Exposed headers"
    )


class LoggingConfig(BaseModel):
    """Logging Configuration"""
    level: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR")
    file_enabled: bool = Field(default=False, description="Enable file logging")
    log_file: str = Field(default="/var/log/nfm-x/app.log", description="Path to log file")
    max_file_size_mb: int = Field(default=100, description="Max log file size in MB")
    backup
_count: int = Field(default=5, description="Number of backup log files")
    console_enabled: bool = Field(default=True, description="Enable console logging")


class RateLimitConfig(BaseModel):
    """Rate Limiting Configuration"""
    enabled: bool = Field(default=False, description="Enable rate limiting")
    requests_per_minute: int = Field(default=100, description="Max requests per minute")
    burst_requests: int = Field(default=10, description="Max burst requests")
    whitelist: List[str] = Field(
        default_factory=list,
        description="IP addresses to whitelist from rate limiting"
    )


class UploadConfig(BaseModel):
    """File Upload Configuration"""
    max_file_size_mb: int = Field(default=100, description="Max file upload size in MB")
    allowed_extensions: List[str] = Field(
        default_factory=lambda: [".pdf", ".png", ".jpg", ".jpeg", ".txt", ".json", ".zip", ".tar", ".tar.gz"],
        description="Allowed file extensions"
    )
    upload_dir: str = Field(default="./uploads", description="Directory to store uploads")
    batch_enabled: bool = Field(default=True, description="Enable batch uploads")
    max_batch_size: int = Field(default=10, description="Max files per batch upload")


class HealthCheckConfig(BaseModel):
    """Health Check Configuration"""
    check_db: bool = Field(default=True, description="Check database health")
    check_vector_store: bool = Field(default=True, description="Check vector store health")
    check_ocr: bool = Field(default=True, description="Check OCR engine health")
    check_storage: bool = Field(default=True, description="Check storage health")
    timeout_seconds: int = Field(default=5, description="Health check timeout")


class NFMXConfig(BaseSettings):
    """Main NFM-X Configuration"""
    app_name: str = Field(default="NFM-X", description="Application name")
    version: str = Field(default="4.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enabl
e debug mode")
    environment: str = Field(default="development", description="Environment: development, staging, production")
    
    # Sub-configurations
    ocr: OCRConfig = Field(default_factory=OCRConfig)
    compression: CompressionConfig = Field(default_factory=CompressionConfig)
    sync: SyncConfig = Field(default_factory=SyncConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    upload: UploadConfig = Field(default_factory=UploadConfig)
    health_check: HealthCheckConfig = Field(default_factory=HealthCheckConfig)
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/nfm-x.db",
        description="Database connection URL"
    )
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=4, description="Number of worker processes")
    
    # Security
    secret_key: str = Field(
        default="change-this-in-production",
        description="Secret key for JWT and security"
    )
    api_key: str = Field(default="", description="API key for authentication")
    
    # Storage
    storage_dir: str = Field(default="./storage", description="Storage directory")
    vector_store_dir: str = Field(default="./storage/vectors", description="Vector store directory")
    
    class Config:
        case_sensitive = False


@lru_cache()
def get_config() -> NFMXConfig:
    """Get configuration from environment variables"""
    return NFMXConfig()


def get_config_dict() -> Dict[str, Any]:
    """Get configuration as a dictionary"""
    config = get_config()
    return config.model_dump()def get_config_dict() -> Dict[str, Any]:
    """Get configuration as a dictionary"""
    config = get_config()
    return config.model_dump()


# Clear cache for testing
def reset_config_cache():
    get_config.cache_clear()