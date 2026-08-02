"""
NFM-X V4 Enhanced OCR Engine
Supports multiple OCR backends: EasyOCR, Tesseract, Cloud (Azure/Google)
With table extraction and multi-language support
"""

import os
import tempfile
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import asyncio

from backend.app.config import get_config

logger = logging.getLogger(__name__)


class OCREngineType(str, Enum):
    EASYOCR = "easyocr"
    TESSERACT = "tesseract"
    AZURE = "azure"
    GOOGLE = "google"


class OCRResult:
    """Result of OCR processing"""
    
    def __init__(self):
        self.text: str = ""
        self.languages: List[str] = []
        self.confidence: float = 0.0
        self.tables: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        self.processing_time_ms: float = 0.0
        self.success: bool = False
        self.error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "languages": self.languages,
            "confidence": self.confidence,
            "tables": self.tables,
            "metadata": self.metadata,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "success": self.success,
            "error": self.error
        }


@dataclass
class OCRJob:
    """Represents an OCR processing job"""
    job_id: str
    file_path: str
    engine: OCREngineType
    languages: List[str]
    extract_tables: bool
    status: str = "pending"
    progress: float = 0.0
    result: Optional[OCRResult] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result_dict = {
            "job_id": self.job_id,
            "file_path": self.file_path,
            "engine": self.engine.value,
            "languages": self.languages,
            "extract_tables": self.extract_tables,
            "status": self.status,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
        }
        if self.completed_at:
            result_dict["completed_at"] = self.completed_at.isoformat()
        if self.result:
            result_dict["result"] = self.result.to_dict()
        if self.error:
            result_dict["error"] = self.error
        return result_dict


class OCREngine:
    """
    Main OCR Engine with multiple backend support
    """
    
    def __init__(self):
        self.config = get_config().ocr
        self.jobs: Dict[str, OCRJob] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the OCR engine"""
        if self._initialized:
            return
        
        logger.info(f"Initializing OCR engine: {self.config.engine}")
        
        # Initialize the configured engine
        if self.config.engine == OCREngineType.EASYOCR:
            await self._init_easyocr()
        elif self.config.engine == OCREngineType.TESSERACT:
            await self._init_tesseract()
        elif self.config.engine in [OCREngineType.AZURE, OCREngineType.GOOGLE]:
            await self._init_cloud()
        
        self._initialized = True
        logger.info(f"OCR engine initialized successfully")
    
    async def _init_easyocr(self) -> None:
        """Initialize EasyOCR"""
        try:
            import easyocr
            # Test that EasyOCR is available
            if self.config.easyocr_model:
                reader = easyocr.Reader([self.config.easyocr_model])
                del reader
            logger.info(f"EasyOCR initialized with model: {self.config.easyocr_model}")
        except ImportError:
            logger.error("EasyOCR not installed. Install with: pip install easyocr")
            raise
    
    async def _init_tesseract(self) -> None:
        """Initialize Tesseract"""
        try:
            import pytesseract
            if self.config.tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = self.config.tesseract_path
            logger.info(f"Tesseract initialized with path: {self.config.tesseract_path}")
        except ImportError:
            logger.error("Tesseract not installed. Install with: pip install pytesseract")
            raise
    
    async def _init_cloud(self) -> None:
        """Initialize Cloud OCR"""
        if not self.config.cloud_api_key:
            logger.error(f"Cloud API key not configured for {self.config.cloud_provider}")
            raise ValueError(f"Cloud API key required for {self.config.cloud_provider}")
        
        if self.config.cloud_provider == OCREngineType.AZURE:
            try:
                from azure.ai.formrecognizer import DocumentAnalysisClient
                logger.info("Azure Form Recognizer initialized")
            except ImportError:
                logger.error("Azure SDK not installed. Install with: pip install azure-ai-formrecognizer")
                raise
        elif self.config.cloud_provider == OCREngineType.GOOGLE:
            try:
                from google.cloud import vision
                logger.info("Google Vision initialized")
            except ImportError:
                logger.error("Google Cloud Vision not installed. Install with: pip install google-cloud-vision")
                raise
    
    async def process_file(
        self,
        file_path: str,
        languages: Optional[List[str]] = None,
        extract_tables: Optional[bool] = None
    ) -> OCRResult:
        """
        Process a file with OCR
        
        Args:
            file_path: Path to the file to process
            languages: List of languages to use (overrides config)
            extract_tables: Whether to extract tables (overrides config)
            
        Returns:
            OCRResult with extracted text, tables, and metadata
        """
        # Ensure engine is initialized
        if not self._initialized:
            await self.initialize()
        
        # Use provided parameters or fall back to config
        use_languages = languages or self.config.languages
        use_extract_tables = extract_tables if extract_tables is not None else self.config.table_extraction
        
        result = OCRResult()
        start_time = datetime.utcnow()
        
        try:
            # Determine file type and process accordingly
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == ".pdf":
                if use_extract_tables and self.config.table_extraction:
                    # Extract tables from PDF
                    result.tables = await self._extract_tables_from_pdf(file_path, use_languages)
                    result.text = "
".join([t.get("text", "") for t in result.tables])
                else:
                    # Extract text from PDF
                    result.text = await self._extract_text_from_pdf(file_path, use_languages)
            else:
                # Process image files
                result.text = await self._extract_text_from_image(file_path, use_languages)
            
            result.languages = use_languages
            result.success = True
            result.confidence = 0.95  # Placeholder - actual confidence depends on engine
            result.metadata = {
                "engine": self.config.engine,
                "file_type": file_ext,
                "table_extraction": use_extract_tables
            }
            
        except Exception as e:
            result.success = False
            result.error = str(e)
            logger.error(f"OCR processing failed: {str(e)}")
        
        result.processing_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        return result
    
    async def process_file_async(self, file_path: str, job_id: str, languages: Optional[List[str]] = None, extract_tables: Optional[bool] = None) -> OCRJob:
        """
        Process a file asynchronously
        Creates a job that can be tracked
        """
        import uuid
        
        job = OCRJob(
            job_id=job_id or str(uuid.uuid4()),
            file_path=file_path,
            engine=OCREngineType(self.config.engine),
            languages=languages or self.config.languages,
            extract_tables=extract_tables if extract_tables is not None else self.config.table_extraction,
            status="processing",
            progress=0.0
        )
        
        self.jobs[job.job_id] = job
        
        # Process in background
        asyncio.create_task(self._process_job_async(job))
        
        return job
    
    async def _process_job_async(self, job: OCRJob) -> None:
        """Process a job asynchronously"""
        try:
            job.status = "processing"
            job.progress = 10.0
            
            result = await self.process_file(
                job.file_path,
                job.languages,
                job.extract_tables
            )
            
            job.result = result
            job.status = "completed"
            job.progress = 100.0
            job.completed_at = datetime.utcnow()
            
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            logger.error(f"Job {job.job_id} failed: {str(e)}")
    
    async def _extract_text_from_pdf(self, file_path: str, languages: List[str]) -> str:
        """Extract text from PDF"""
        if self.config.engine == OCREngineType.EASYOCR:
            return await self._extract_text_pdf_easyocr(file_path, languages)
        elif self.config.engine == OCREngineType.TESSERACT:
            return await self._extract_text_pdf_tesseract(file_path, languages)
        elif self.config.engine == OCREngineType.AZURE:
            return await self._extract_text_pdf_azure(file_path, languages)
        elif self.config.engine == OCREngineType.GOOGLE:
            return await self._extract_text_pdf_google(file_path, languages)
        else:
            raise ValueError(f"Unsupported OCR engine: {self.config.engine}")
    
    async def _extract_text_from_image(self, file_path: str, languages: List[str]) -> str:
        """Extract text from image"""
        if self.config.engine == OCREngineType.EASYOCR:
            return await self._extract_text_image_easyocr(file_path, languages)
        elif self.config.engine == OCREngineType.TESSERACT:
            return await self._extract_text_image_tesseract(file_path, languages)
        elif self.config.engine == OCREngineType.AZURE:
            return await self._extract_text_image_azure(file_path, languages)
        elif self.config.engine == OCREngineType.GOOGLE:
            return await self._extract_text_image_google(file_path, languages)
        else:
            raise ValueError(f"Unsupported OCR engine: {self.config.engine}")
    
    async def _extract_tables_from_pdf(self, file_path: str, languages: List[str]) -> List[Dict[str, Any]]:
        """Extract tables from PDF"""
        tables = []
        
        if self.config.engine == OCREngineType.EASYOCR:
            # EasyOCR doesn not have built-in table extraction
            # Use camelot or tabula for table extraction
            try:
                import camelot
                tables_result = camelot.read_pdf(file_path, pages="all")
                for i, table in enumerate(tables_result):
                    tables.append({
                        "table_id": f"table_{i}",
                        "rows": table.df.values.tolist(),
                        "columns": table.df.columns.tolist(),
                        "text": str(table.df.to_string())
                    })
            except ImportError:
                logger.warning("Camelot not installed for table extraction. Install with: pip install camelot-py[cv]")
                # Fallback: return empty tables
        
        elif self.config.engine == OCREngineType.AZURE:
            # Azure Form Recognizer has built-in table extraction
            tables = await self._extract_tables_pdf_azure(file_path)
        
        return tables
    
    # EasyOCR implementations
    async def _extract_text_pdf_easyocr(self, file_path: str, languages: List[str]) -> str:
        """Extract text from PDF using EasyOCR"""
        import easyocr
        import fitz  # PyMuPDF
        
        reader = easyocr.Reader(languages)
        text = ""
        
        doc = fitz.open(file_path)
        for page in doc:
            # Convert page to image
            pix = page.get_pixmap()
            img_path = f"/tmp/nfm_x_page_{page.number}.png"
            pix.save(img_path)
            
            # Extract text from image
            results = reader.readtext(img_path, detail=0)
            text += "
".join(results)
            
            # Clean up
            os.remove(img_path)
        
        doc.close()
        return text
    
    async def _extract_text_image_easyocr(self, file_path: str, languages: List[str]) -> str:
        """Extract text from image using EasyOCR"""
        import easyocr
        reader = easyocr.Reader(languages)
        results = reader.readtext(file_path, detail=0)
        return "
".join(results)
    
    # Tesseract implementations
    async def _extract_text_pdf_tesseract(self, file_path: str, languages: List[str]) -> str:
        """Extract text from PDF using Tesseract"""
        import pytesseract
        import fitz  # PyMuPDF
        
        text = ""
        doc = fitz.open(file_path)
        for page in doc:
            pix = page.get_pixmap()
            img_path = f"/tmp/nfm_x_page_{page.number}.png"
            pix.save(img_path)
            
            lang = "+".join(languages) if languages else "eng"
            page_text = pytesseract.image_to_string(img_path, lang=lang)
            text += "
" + page_text
            
            os.remove(img_path)
        
        doc.close()
        return text
    
    async def _extract_text_image_tesseract(self, file_path: str, languages: List[str]) -> str:
        """Extract text from image using Tesseract"""
        import pytesseract
        lang = "+".join(languages) if languages else "eng"
        return pytesseract.image_to_string(file_path, lang=lang)
    
    # Azure implementations
    async def _extract_text_pdf_azure(self, file_path: str, languages: List[str]) -> str:
        """Extract text from PDF using Azure Form Recognizer"""
        from azure.ai.formrecognizer import DocumentAnalysisClient
        from azure.core.credentials import AzureKeyCredential
        
        endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
        key = self.config.cloud_api_key
        
        if not endpoint:
            raise ValueError("AZURE_FORM_RECOGNIZER_ENDPOINT environment variable not set")
        
        document_analysis_client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
        
        with open(file_path, "rb") as f:
            poller = document_analysis_client.begin_analyze_document("prebuilt-read", f.read())
        
        result = poller.result()
        text = ""
        for paragraph in result.paragraphs:
            text += paragraph.content + "
"
        
        return text
    
    async def _extract_text_image_azure(self, file_path: str, languages: List[str]) -> str:
        """Extract text from image using Azure Computer Vision"""
        from azure.cognitiveservices.vision.computervision import ComputerVisionClient
        from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
        from msrest.authentication import CognitiveServicesCredentials
        
        endpoint = os.getenv("AZURE_COMPUTER_VISION_ENDPOINT")
        key = self.config.cloud_api_key
        
        if not endpoint:
            raise ValueError("AZURE_COMPUTER_VISION_ENDPOINT environment variable not set")
        
        computervision_client = ComputerVisionClient(
            endpoint, CognitiveServicesCredentials(key)
        )
        
        with open(file_path, "rb") as image_stream:
            read_response = computervision_client.recognize_text_in_stream(image_stream)
        
        text = ""
        for line in read_response.recognition_result.lines:
            text += line.text + "
"
        
        return text
    
    async def _extract_tables_pdf_azure(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract tables from PDF using Azure Form Recognizer"""
        from azure.ai.formrecognizer import DocumentAnalysisClient
        from azure.core.credentials import AzureKeyCredential
        
        endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
        key = self.config.cloud_api_key
        
        if not endpoint:
            return []
        
        document_analysis_client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
        
        with open(file_path, "rb") as f:
            poller = document_analysis_client.begin_analyze_document("prebuilt-layout", f.read())
        
        result = poller.result()
        tables = []
        
        for i, table in enumerate(result.tables):
            table_data = {
                "table_id": f"table_{i}",
                "row_count": table.row_count,
                "column_count": table.column_count,
                "cells": []
            }
            
            for cell in table.cells:
                table_data["cells"].append({
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "text": cell.content,
                    "confidence": cell.confidence
                })
            
            tables.append(table_data)
        
        return tables
    
    # Google implementations
    async def _extract_text_pdf_google(self, file_path: str, languages: List[str]) -> str:
        """Extract text from PDF using Google Vision"""
        from google.cloud import vision
        
        client = vision.ImageAnnotatorClient()
        
        with open(file_path, "rb") as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        
        return response.full_text_annotation.text
    
    async def _extract_text_image_google(self, file_path: str, languages: List[str]) -> str:
        """Extract text from image using Google Vision"""
        from google.cloud import vision
        
        client = vision.ImageAnnotatorClient()
        
        with open(file_path, "rb") as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        
        text = ""
        for text_annotation in response.text_annotations:
            text += text_annotation.description + "
"
        
        return text
    
    def get_job(self, job_id: str) -> Optional[OCRJob]:
        """Get a job by ID"""
        return self.jobs.get(job_id)
    
    def list_jobs(self) -> List[OCRJob]:
        """List all jobs"""
        return list(self.jobs.values())
    
    def clear_jobs(self) -> None:
        """Clear completed jobs"""
        self.jobs = {jid: job for jid, job in self.jobs.items() if job.status != "completed"}