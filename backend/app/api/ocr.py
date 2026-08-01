"""
NFM-X OCR API Endpoints
========================

API endpoints for OCR functionality.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List, Optional, Dict, Any
import tempfile
import os

from ..models.ocr_models import OCRResultResponse, OCRDocumentResponse, OCRStatsResponse
from ..ocr import OCRProcessor

router = APIRouter(prefix="/api/ocr", tags=["OCR"])

_ocr_results = {}


@router.post("/document")
async def process_document(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            contents = await file.read()
            temp_file.write(contents)
        
        try:
            processor = OCRProcessor()
            result = processor.process_document(temp_path)
            document_id = result.document.document_id
            _ocr_results[document_id] = result
            return {"success": True, "document_id": document_id, "text": result.text}
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/engines")
async def list_engines():
    processor = OCRProcessor()
    return [{"name": e, "available": True} for e in processor.list_engines()]


@router.get("/documents")
async def list_documents(limit: int = 20, offset: int = 0):
    document_ids = list(_ocr_results.keys())[offset:offset + limit]
    return [{"document_id": doc_id, "file_name": _ocr_results[doc_id].document.file_name} for doc_id in document_ids]


# Urdu: NFM-X OCR API اینڈ پوانٹس