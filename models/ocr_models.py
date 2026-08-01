""" Pydantic models for OCR objects """

from pydantic import BaseModel, Field
from typing import Optional, List, Any


class OCRRegion(BaseModel):
    x: int
    y: int
    width: int
    height: int
    text: str
    confidence: float = 1.0


class OCRDocument(BaseModel):
    document_id: str
    page: int
    language: str
    text: str
    confidence: float
    regions: List[OCRRegion] = Field(default_factory=list)
    tables: List[Any] = Field(default_factory=list)


class OCRResult(BaseModel):
    document: OCRDocument
    processing_timestamp: str
    ocr_engine: str
    ocr_model: str
    metadata: dict = Field(default_factory=dict)