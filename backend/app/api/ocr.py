"""
NFM-X V4 OCR API
Enhanced OCR with multiple backends, table extraction, and batch processing
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime

from backend.app.ocr.engine import OCREngine, OCRResult, OCRJob, OCREngineType
from backend.app.config import get_config

router = APIRouter(prefix="/api/v1/ocr", tags=["OCR"])


# Initialize OCR engine
ocr_engine = OCREngine()


class OCRRequest(BaseModel):
    languages: Optional[List[str]] = None
    extract_tables: Optional[bool] = None
    engine: Optional[str] = None  # Override default engine


class OCRResponse(BaseModel):
    text: str
    languages: List[str]
    confidence: float
    tables: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    processing_time_ms: float
    success: bool
    error: Optional[str] = None


class OCRJobResponse(BaseModel):
    job_id: str
    file_path: str
    engine: str
    languages: List[str]
    extract_tables: bool
    status: str
    progress: float
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[OCRResponse] = None
    error: Optional[str] = None


class BatchOCRRequest(BaseModel):
    files: List[str]  # List of file paths
    languages: Optional[List[str]] = None
    extract_tables: Optional[bool] = None


class BatchOCRResponse(BaseModel):
    job_ids: List[str]
    message: str


class OCRConfigResponse(BaseModel):
    engine: str
    languages: List[str]
    table_extraction: bool
    enabled: bool


@router.post("/process", response_model=OCRResponse)
async def process_file(
    file: UploadFile = File(...),
    languages: Optional[List[str]] = Query(None),
    extract_tables: Optional[bool] = Query(None),
    engine: Optional[str] = Query(None)
):
    """
    Process a single file with OCR
    
    Supports: PDF, PNG, JPG, JPEG
    Engines: easyocr, tesseract, azure, google
    """
    # Save uploaded file temporarily
    temp_dir = "./temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}{file_ext}")
    
    try:
        # Save file
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # Process with OCR
        if engine:
            # Temporarily override engine
            original_engine = ocr_engine.config.engine
            ocr_engine.config.engine = engine
        
        result = await ocr_engine.process_file(
            temp_path,
            languages=languages,
            extract_tables=extract_tables
        )
        
        if engine:
            # Restore original engine
            ocr_engine.config.engine = original_engine
        
        # Convert to response model
        response = OCRResponse(
            text=result.text,
            languages=result.languages,
            confidence=result.confidence,
            tables=result.tables,
            metadata=result.metadata,
            processing_time_ms=result.processing_time_ms,
            success=result.success,
            error=result.error
        )
        
        return response
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/process-async", response_model=OCRJobResponse, status_code=202)
async def process_file_async(
    file: UploadFile = File(...),
    languages: Optional[List[str]] = Query(None),
    extract_tables: Optional[bool] = Query(None)
):
    """
    Process a file asynchronously
    Returns a job ID that can be used to track progress
    """
    # Save uploaded file
    upload_dir = get_config().upload.upload_dir
    os.makedirs(upload_dir, exist_ok=True)
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}{file_ext}")
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Create async job
    job = await ocr_engine.process_file_async(
        file_path=file_path,
        job_id=None,  # Auto-generate
        languages=languages,
        extract_tables=extract_tables
    )
    
    # Convert to response model
    return OCRJobResponse(
        job_id=job.job_id,
        file_path=job.file_path,
        engine=job.engine.value,
        languages=job.languages,
        extract_tables=job.extract_tables,
        status=job.status,
        progress=job.progress,
        created_at=job.created_at.isoformat(),
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        result=OCRResponse(
            text=job.result.text if job.result else "",
            languages=job.result.languages if job.result else [],
            confidence=job.result.confidence if job.result else 0.0,
            tables=job.result.tables if job.result else [],
            metadata=job.result.metadata if job.result else {},
            processing_time_ms=job.result.processing_time_ms if job.result else 0.0,
            success=job.result.success if job.result else False,
            error=job.result.error
        ) if job.result else None,
        error=job.error
    )


@router.get("/jobs/{job_id}", response_model=OCRJobResponse)
async def get_job_status(job_id: str):
    """
    Get status of an OCR job
    """
    job = ocr_engine.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return OCRJobResponse(
        job_id=job.job_id,
        file_path=job.file_path,
        engine=job.engine.value,
        languages=job.languages,
        extract_tables=job.extract_tables,
        status=job.status,
        progress=job.progress,
        created_at=job.created_at.isoformat(),
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        result=OCRResponse(
            text=job.result.text if job.result else "",
            languages=job.result.languages if job.result else [],
            confidence=job.result.confidence if job.result else 0.0,
            tables=job.result.tables if job.result else [],
            metadata=job.result.metadata if job.result else {},
            processing_time_ms=job.result.processing_time_ms if job.result else 0.0,
            success=job.result.success if job.result else False,
            error=job.result.error
        ) if job.result else None,
        error=job.error
    )


@router.get("/jobs", response_model=List[OCRJobResponse])
async def list_jobs():
    """
    List all OCR jobs
    """
    jobs = ocr_engine.list_jobs()
    return [
        OCRJobResponse(
            job_id=job.job_id,
            file_path=job.file_path,
            engine=job.engine.value,
            languages=job.languages,
            extract_tables=job.extract_tables,
            status=job.status,
            progress=job.progress,
            created_at=job.created_at.isoformat(),
            completed_at=job.completed_at.isoformat() if job.completed_at else None,
            error=job.error
        )
        for job in jobs
    ]


@router.post("/batch", response_model=BatchOCRResponse, status_code=202)
async def batch_process(
    request: BatchOCRRequest
):
    """
    Process multiple files in batch
    Returns list of job IDs
    """
    job_ids = []
    upload_dir = get_config().upload.upload_dir
    os.makedirs(upload_dir, exist_ok=True)
    
    for file_path in request.files:
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File {file_path} not found")
        
        # Create async job for each file
        job = await ocr_engine.process_file_async(
            file_path=file_path,
            job_id=None,
            languages=request.languages,
            extract_tables=request.extract_tables
        )
        job_ids.append(job.job_id)
    
    return BatchOCRResponse(
        job_ids=job_ids,
        message=f"Created {len(job_ids)} OCR jobs"
    )


@router.get("/config", response_model=OCRConfigResponse)
async def get_ocr_config():
    """
    Get OCR configuration
    """
    config = get_config().ocr
    return OCRConfigResponse(
        engine=config.engine,
        languages=config.languages,
        table_extraction=config.table_extraction,
        enabled=config.enabled
    )


@router.post("/extract-tables", response_model=OCRResponse)
async def extract_tables(
    file: UploadFile = File(...),
    languages: Optional[List[str]] = Query(None)
):
    """
    Extract tables from a PDF file
    Uses table extraction mode
    """
    # Save uploaded file temporarily
    temp_dir = "./temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext != ".pdf":
        raise HTTPException(status_code=400, detail="Table extraction only supports PDF files")
    
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}{file_ext}")
    
    try:
        # Save file
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # Process with table extraction enabled
        result = await ocr_engine.process_file(
            temp_path,
            languages=languages,
            extract_tables=True
        )
        
        # Convert to response model
        return OCRResponse(
            text=result.text,
            languages=result.languages,
            confidence=result.confidence,
            tables=result.tables,
            metadata=result.metadata,
            processing_time_ms=result.processing_time_ms,
            success=result.success,
            error=result.error
        )
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/engines")
async def list_engines():
    """
    List available OCR engines
    """
    return [
        {"name": "easyocr", "description": "EasyOCR - CPU/GPU based OCR", "installed": is_easyocr_installed()},
        {"name": "tesseract", "description": "Tesseract - Open source OCR", "installed": is_tesseract_installed()},
        {"name": "azure", "description": "Azure Form Recognizer", "installed": is_azure_installed()},
        {"name": "google", "description": "Google Cloud Vision", "installed": is_google_installed()}
    ]


def is_easyocr_installed() -> bool:
    try:
        import easyocr
        return True
    except ImportError:
        return False


def is_tesseract_installed() -> bool:
    try:
        import pytesseract
        return True
    except ImportError:
        return False


def is_azure_installed() -> bool:
    try:
        from azure.ai.formrecognizer import DocumentAnalysisClient
        return True
    except ImportError:
        return False


def is_google_installed() -> bool:
    try:
        from google.cloud import vision
        return True
    except ImportError:
        return False