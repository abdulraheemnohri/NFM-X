"""
NFM-X OCR Models
=================

Pydantic models for OCR API responses and requests.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class OCRBoundingBox(BaseModel):
    x: int = Field(..., description="X coordinate")
    y: int = Field(..., description="Y coordinate")
    width: int = Field(..., description="Width")
    height: int = Field(..., description="Height")


class OCREntity(BaseModel):
    entity_type: str = Field(..., description="Type of entity")
    text: str = Field(..., description="Entity text")
    value: Optional[Any] = Field(None, description="Parsed value")
    start: int = Field(..., description="Start position")
    end: int = Field(..., description="End position")
    confidence: float = Field(default=1.0, description="Confidence score")


class OCRMemory(BaseModel):
    memory_id: str = Field(..., description="Memory ID")
    content: str = Field(..., description="Memory content")
    memory_type: str = Field(..., description="Memory type")
    confidence: float = Field(default=0.8, description="Confidence")
    language: str = Field(default="en", description="Language")
    entities: List[Dict] = Field(default_factory=list, description="Entities")
    source_type: str = Field(default="ocr", description="Source type")
    extracted_at: str = Field(..., description="Extracted at")


class OCRDocumentResponse(BaseModel):
    document_id: str = Field(..., description="Document ID")
    file_name: Optional[str] = Field(None, description="File name")
    file_type: Optional[str] = Field(None, description="File type")
    file_size: int = Field(default=0, description="File size")
    pages: int = Field(default=1, description="Number of pages")
    language: str = Field(default="en", description="Language")
    engine: str = Field(default="unknown", description="Engine")
    confidence: float = Field(default=1.0, description="Confidence")
    created_at: str = Field(..., description="Created at")
    processed_at: Optional[str] = Field(None, description="Processed at")


class OCRResultResponse(BaseModel):
    success: bool = Field(default=True, description="Success")
    document_id: str = Field(..., description="Document ID")
    text: str = Field(default="", description="Extracted text")
    language: str = Field(default="en", description="Language")
    confidence: float = Field(default=1.0, description="Confidence")
    entities: List[Dict] = Field(default_factory=list, description="Entities")
    memories: List[Dict] = Field(default_factory=list, description="Memories")
    engine: str = Field(default="unknown", description="Engine")
    pages: int = Field(default=1, description="Pages")
    file_name: Optional[str] = Field(None, description="File name")
    file_type: Optional[str] = Field(None, description="File type")
    file_size: int = Field(default=0, description="File size")
    processing_time: float = Field(default=0.0, description="Processing time")
    timestamp: str = Field(..., description="Timestamp")


class OCRStatsResponse(BaseModel):
    total_documents: int = Field(default=0, description="Total documents")
    total_pages: int = Field(default=0, description="Total pages")
    engines: Dict[str, int] = Field(default_factory=dict, description="Engines")
    languages: Dict[str, int] = Field(default_factory=dict, description="Languages")
    available_engines: List[str] = Field(default_factory=list, description="Available engines")


# Urdu: NFM-X OCR ماڈلز