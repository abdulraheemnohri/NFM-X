"""
NFM-X V4 Document Models
Database models for document management
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class DocumentType(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    ZIP = "zip"
    TAR = "tar"
    OTHER = "other"


class UploadedDocument(BaseModel):
    """Model for uploaded documents"""
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    original_filename: str
    file_path: str
    file_type: DocumentType
    file_extension: str
    size_bytes: int
    mime_type: Optional[str] = None
    status: DocumentStatus = DocumentStatus.PENDING
    uploaded_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    ocr_result: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "document_id": "doc_123",
                "filename": "document.pdf",
                "original_filename": "My Document.pdf",
                "file_path": "/uploads/document.pdf",
                "file_type": "pdf",
                "file_extension": ".pdf",
                "size_bytes": 1024000,
                "mime_type": "application/pdf",
                "status": "completed",
                "uploaded_at": "2026-08-02T10:00:00",
                "metadata": {"author": "user1"},
                "tags": ["important", "contract"]
            }
        }


class UploadedDocumentCreate(BaseModel):
    """Model for creating an uploaded document"""
    filename: str
    file_path: str
    file_type: Docu
mentType
    file_extension: str
    size_bytes: int
    mime_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class UploadedDocumentUpdate(BaseModel):
    """Model for updating an uploaded document"""
    filename: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    status: Optional[DocumentStatus] = None


class UploadedDocumentResponse(BaseModel):
    """Response model for uploaded documents"""
    document_id: str
    filename: str
    original_filename: str
    file_path: str
    file_type: str
    file_extension: str
    size_bytes: int
    mime_type: Optional[str]
    status: str
    uploaded_at: str
    processed_at: Optional[str] = None
    metadata: Dict[str, Any]
    tags: List[str]
    ocr_result: Optional[Dict[str, Any]] = None


class DocumentListResponse(BaseModel):
    """Response model for listing documents"""
    documents: List[UploadedDocumentResponse]
    total: int
    page: int
    page_size: int


class OCRJobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class OCRJob(BaseModel):
    """Model for OCR jobs"""
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    status: OCRJobStatus = OCRJobStatus.PENDING
    progress: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    engine: str
    languages: List[str]
    extract_tables: bool


class OCRJobResponse(BaseModel):
    """Response model for OCR jobs"""
    job_id: str
    document_id: str
    status: str
    progress: float
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    engine: str
    languages: Lis
t[str]
    extract_tables: bool


class CompressionRun(BaseModel):
    """Model for compression runs"""
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    memories_compressed: int = 0
    memories_archived: int = 0
    memories_skipped: int = 0
    total_bytes_saved: int = 0
    status: str = "running"
    error: Optional[str] = None


class CompressionRunResponse(BaseModel):
    """Response model for compression runs"""
    run_id: str
    started_at: str
    completed_at: Optional[str] = None
    memories_compressed: int
    memories_archived: int
    memories_skipped: int
    total_bytes_saved: int
    status: str
    error: Optional[str] = None