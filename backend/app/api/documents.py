"""NFM-X V4 Document Management API - CRUD operations for uploaded documents"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Form
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime, timezone

from backend.app.models.document import (
    UploadedDocument,
    UploadedDocumentCreate,
    UploadedDocumentUpdate,
    UploadedDocumentResponse,
    DocumentListResponse,
    DocumentStatus,
    DocumentType
)
from backend.app.config import get_config

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

documents_db = {}


@router.post("/upload", response_model=UploadedDocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    tags: Optional[List[str]] = Form(None),
    metadata: Optional[str] = Form(None)
):
    config = get_config()
    content = await file.read()
    file_size = len(content)
    
    max_size = config.upload.max_file_size_mb * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {config.upload.max_file_size_mb}MB")
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in config.upload.allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File type not allowed")
    
    file_type = get_document_type(file_ext)
    upload_dir = config.upload.upload_dir
    os.makedirs(upload_dir, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}{file_ext}")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    metadata_dict = {}
    if metadata:
        try:
            import json
            metadata_dict = json.loads(metadata)
        except:
            metadata_dict = {"raw": metadata}
    
    document = UploadedDocument(
        document_id=file_id,
        filename=f"{file_id}{file_ext}",
        original_filename=file.filename,
        file_path=file_path,
        file_type=file_type,
        file_extension=file_ext,
        size_bytes=file_size,
        mime_type=file.content_type,
        status=DocumentStatus.PENDING,
        metadata=metadata_dict,
        tags=tags or []
    )
    
    documents_db[file_id] = document
    
    return UploadedDocumentResponse(
        document_id=document.document_id,
        filename=document.filename,
        original_filename=document.original_filename,
        file_path=document.file_path,
        file_type=document.file_type.value,
        file_extension=document.file_extension,
        size_bytes=document.size_bytes,
        mime_type=document.mime_type,
        status=document.status.value,
        uploaded_at=document.uploaded_at.isoformat(),
        metadata=document.metadata,
        tags=document.tags
    )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    file_type: Optional[DocumentType] = Query(None),
    status: Optional[DocumentStatus] = Query(None),
    tags: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None)
):
    filtered = list(documents_db.values())
    
    if file_type:
        filtered = [d for d in filtered if d.file_type == file_type]
    if status:
        filtered = [d for d in filtered if d.status == status]
    if tags:
        filtered = [d for d in filtered if any(tag in d.tags for tag in tags)]
    if search:
        search_lower = search.lower()
        filtered = [d for d in filtered if search_lower in d.filename.lower() or search_lower in d.original_filename.lower()]
    
    filtered.sort(key=lambda d: d.uploaded_at, reverse=True)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]
    
    return DocumentListResponse(
        documents=[UploadedDocumentResponse(
            document_id=d.document_id,
            filename=d.filename,
            original_filename=d.original_filename,
            file_path=d.file_path,
            file_type=d.file_type.value,
            file_extension=d.file_extension,
            size_bytes=d.size_bytes,
            mime_type=d.mime_type,
            status=d.status.value,
            uploaded_at=d.uploaded_at.isoformat(),
            processed_at=d.processed_at.isoformat() if d.processed_at else None,
            metadata=d.metadata,
            tags=d.tags,
            ocr_result=d.ocr_result
        ) for d in paginated],
        total=len(filtered),
        page=page,
        page_size=page_size
    )


@router.get("/{document_id}", response_model=UploadedDocumentResponse)
async def get_document(document_id: str):
    document = documents_db.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    return UploadedDocumentResponse(
        document_id=document.document_id,
        filename=document.filename,
        original_filename=document.original_filename,
        file_path=document.file_path,
        file_type=document.file_type.value,
        file_extension=document.file_extension,
        size_bytes=document.size_bytes,
        mime_type=document.mime_type,
        status=document.status.value,
        uploaded_at=document.uploaded_at.isoformat(),
        processed_at=document.processed_at.isoformat() if document.processed_at else None,
        metadata=document.metadata,
        tags=document.tags,
        ocr_result=document.ocr_result
    )


@router.put("/{document_id}", response_model=UploadedDocumentResponse)
async def update_document(document_id: str, request: UploadedDocumentUpdate):
    document = documents_db.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    if request.filename is not None:
        document.filename = request.filename
    if request.metadata is not None:
   
     document.metadata.update(request.metadata)
    if request.tags is not None:
        document.tags = request.tags
    if request.status is not None:
        document.status = request.status
    
    documents_db[document_id] = document
    
    return UploadedDocumentResponse(
        document_id=document.document_id,
        filename=document.filename,        original_filename=document.original_filename,
        file_path=document.file_path,
        file_type=document.file_type.value,
        file_extension=document.file_extension,
        size_bytes=document.size_bytes,
        mime_type=document.mime_type,
        status=document.status.value,
        uploaded_at=document.uploaded_at.isoformat(),
        processed_at=document.processed_at.isoformat() if document.processed_at else None,
        metadata=document.metadata,
        tags=document.tags,
        ocr_result=document.ocr_result
    )


@router.delete("/{document_id}", status_code=200)
async def delete_document(document_id: str):
    document = documents_db.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    del documents_db[document_id]
    return {"message": f"Document {document_id} deleted successfully"}


@router.post("/{document_id}/process", response_model=UploadedDocumentResponse, status_code=202)
async def process_document(document_id: str, languages: Optional[List[str]] = Query(None), extract_tables: Optional[bool] = Query(None)):
    from backend.app.ocr.engine import OCREngine
    document = documents_db.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    
    document.status = DocumentStatus.PROCESSING
    documents_db[document_id] = document
    
    ocr_engine = OCREngine()
    await ocr_engine.initialize()
    result = await ocr_engine.process_file(document.file_path, languages=languages, extract_tables=extract_tables)
    
    document.ocr_result = result.to_dict()
    document.status = DocumentStatus.COMPLETED if result.success else DocumentStatus.FAILED
    document.processed_at = datetime.now(timezone.utc)
    documents_db[document_id] = document
    
    return UploadedDocumentResponse(
        document_id=document.document_id,
        filename=document.filename,
        original_filename=document.original_filename,
        file_path=document.file_path,
        file_type=document.file_type.value,
        file_extension=document.file_extension,
        size_bytes=document.size_bytes,
        mime_type=document.mime_type,
        status=document.status.value,
        uploaded_at=document.uploaded_at.isoformat(),
        processed_at=document.processed_at.isoformat(),
        metadata=document.metadata,
        tags=document.tags,
        ocr_result=document.ocr_result
    )


@router.get("/{document_id}/download")
async def download_document(document_id: str):
    from fastapi.responses import FileResponse
    document = documents_db.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(document.file_path, filename=document.original_filename)


@router.get("/stats")
async def get_document_stats():
    total = len(documents_db)
    total_size = sum(d.size_bytes for d in documents_db.values())
    type_counts = {}
    for d in documents_db.values():
        type_key = d.file_type.value
        type_counts[type_key] = type_counts.get(type_key, 0) + 1
    status_counts = {}
    for d in documents_db.values():
        status_key = d.status.value
        status_counts[status_key] = status_counts.get(status_key, 0) + 1
    return {
        "total_documents": total,
        "total_size_bytes": total_size,
      
  "total_size_mb": round(total_size / (1024 * 1024), 2),
        "by_type": type_counts,
        "by_status": status_counts,
        "processed_count": sum(1 for d in documents_db.values() if d.status == DocumentStatus.COMPLETED),
        "pending_count": sum(1 for d in documents_db.values() if d.status == DocumentStatus.PENDING)
    }


def get_document_type(file_ext: str) -> DocumentType:
    image_exts = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"]
    archive_exts = [".zip", ".tar", ".tar.gz", ".gz", ".rar", ".7z"]
    text_exts = [".txt", ".json", ".xml", ".csv", ".md", ".html"]
    if file_ext.lower() == ".pdf":
        return DocumentType.PDF
    elif file_ext.lower() in image_exts:
        return DocumentType.IMAGE
    elif file_ext.lower() in text_exts:
        return DocumentType.TEXT
    elif file_ext.lower() in archive_exts:
        return DocumentType.ZIP if file_ext.lower() == ".zip" else DocumentType.TAR
    else:
        return DocumentType.OTHER