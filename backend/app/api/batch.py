"""
NFM-X V4 Batch Upload API
Process multiple files in a single request (ZIP/tar or list of files)
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uuid
import zipfile
import tarfile
from datetime import datetime, timezone
import asyncio

from backend.app.models.document import UploadedDocument, DocumentStatus, DocumentType
from backend.app.config import get_config
from backend.app.api.documents import documents_db, get_document_type

router = APIRouter(prefix="", tags=["Batch Upload"])


class BatchUploadRequest(BaseModel):
    files: List[str]  # List of file paths for existing files
    languages: Optional[List[str]] = None
    extract_tables: Optional[bool] = None


class BatchUploadResponse(BaseModel):
    job_id: str
    document_ids: List[str]
    total_files: int
    status: str
    message: str


class BatchJobStatus(BaseModel):
    job_id: str
    status: str
    progress: float
    processed_files: int
    total_files: int
    document_ids: List[str]
    errors: List[str]


# In-memory storage for batch jobs
batch_jobs: Dict[str, Dict] = {}


@router.post("/batch", response_model=BatchUploadResponse, status_code=202)
async def batch_upload(
    files: List[UploadFile] = File(...),
    languages: Optional[List[str]] = Form(None),
    extract_tables: Optional[bool] = Form(None)
):
    """
    Upload and process multiple files in a batch
    Accepts multiple files in a single request
    """
    config = get_config()
    
    # Check batch size limit
    if len(files) > config.upload.max_batch_size:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size exceeds limit. Max: {config.upload.max_batch_size} files"
        )
    
    job_id = str(uuid.uuid4())
    document_ids = []
    errors = []
    
    upload_dir = config.upload.upload_dir
    os.makedirs(upload_dir, exist_ok=True)
    
    for file in files:
        try:
            # Check file size
            content = await file.read()
            file_size = len(content)
            max_size = config.upload.max_file_size_mb * 1024 * 1024
            if file_size > max_size:
                errors.append(f"{file.filename}: File too large")
                continue
            
            # Check file extension
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in config.upload.allowed_extensions:
                errors.append(f"{file.filename}: File type not allowed")
                continue
            
            # Save file
            file_id = str(uuid.uuid4())
            file_path = os.path.join(upload_dir, f"{file_id}{file_ext}")
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Create document record
            file_type = get_document_type(file_ext)
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
                metadata={"batch_job_id": job_id},
                tags=["batch", job_id]
            )
            
            documents_db[file_id] = document
            document_ids.append(file_id)
            
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    # Store batch job
    batch_jobs[job_id] = {
        "job_id": job_id,
        "status": "completed",
        "progress": 100.0,
        "processed_files": len(document_ids),
        "total_files": len(files),
        "document_ids": document_ids,
        "errors": errors,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    return BatchUploadResponse(
        job_id=job_id,
        document_ids=document_ids,
        total_files=len(files),
        status="completed",
        message=f"Uploaded {len(document_ids)} files with {len(errors)} errors"
    )


@router.post("/batch-zip", response_model=BatchUploadResponse, status_code=202)
async def batch_upload_zip(
    file: UploadFile = File(...),
    languages: Optional[List[str]] = Form(None),
    extract_tables: Optional[bool] = Form(None)
):
    """
    Upload and extract a ZIP file, then process all files
    """
    import tempfile
    
    config = get_config()
    
    # Save ZIP file temporarily
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, file.filename)
    
    try:
        content = await file.read()
        with open(zip_path, "wb") as f:
            f.write(content)
        
        # Extract ZIP
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Get list of extracted files
        extracted_files = []
        for root, dirs, files_list in os.walk(extract_dir):
            for f in files_list:
                file_path = os.path.join(root, f)
                if os.path.isfile(file_path):
                    extracted_files.append(file_path)
        
        # Process each file
        job_id = str(uuid.uuid4())
        document_ids = []
        errors = []
        
        upload_dir = config.upload.upload_dir
        os.makedirs(upload_dir, exist_ok=True)
        
        for file_path in extracted_files:
            try:
                # Check file size
                file_size = os.path.getsize(file_path)
                max_size = config.upload.max_file_size_mb * 1024 * 1024
                if file_size > max_size:
                    errors.append(f"{os.path.basename(file_path)}: File too large")
                    continue
                
                # Check file extension
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in config.upload.allowed_extensions:
                    errors.append(f"{os.path.basename(file_path)}: File type not allowed")
                    continue
                
                # Move file to upload directory
                file_id = str(uuid.uuid4())
                new_file_path = os.path.join(upload_dir, f"{file_id}{file_ext}")
                os.rename(file_path, new_file_path)
                
                # Create document record
                file_type = get_document_type(file_ext)
                document = UploadedDocument(
                    document_id=file_id,
                    filename=f"{file_id}{file_ext}",
                    original_filename=os.path.basename(file_path),                    file_path=new_file_path,
                    file_type=file_type,
                    file_extension=file_ext,
                    size_bytes=file_size,
                    mime_type=None,
                    status=DocumentStatus.PENDING,
                    metadata={"batch_job_id": job_id, "source": "zip"},
                    tags=["batch", job_id, "zip"]
                )
                
                documents_db[file_id] = document
                document_ids.append(file_id)
                
            except Exception as e:
                errors.append(f"{os.path.basename(file_path)}: {str(e)}")
        
        # Store batch job
        batch_jobs[job_id] = {
            "job_id": job_id,
            "status": "completed",
            "progress": 100.0,
            "processed_files": len(document_ids),
            "total_files": len(extracted_files),
            "document_ids": document_ids,
            "errors": errors,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        return BatchUploadResponse(
            job_id=job_id,
            document_ids=document_ids,
            total_files=len(extracted_files),
            status="completed",
            message=f"Extracted and uploaded {len(document_ids)} files with {len(errors)} errors"
        )
        
    finally:
        # Clean up temp directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


@router.post("/batch-tar", response_model=BatchUploadResponse, status_code=202)
async def batch_upload_tar(
    file: UploadFile = File(...),
    languages: Optional[List[str]] = Form(None),
    extract_tables: Optional[bool] = Form(None)
):
    """
    Upload and extract a TAR file, then process all files
    """
    import tempfile
    
    config = get_config()
    
    # Save TAR file temporarily
    temp_dir = tempfile.mkdtemp()
    tar_path = os.path.join(temp_dir, file.filename)
    
    try:
        content = await file.read()
        with open(tar_path, "wb") as f:
            f.write(content)
        
        # Extract TAR
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        if file.filename.endswith(".tar.gz") or file.filename.endswith(".tgz"):
            mode = "r:gz"
        elif file.filename.endswith(".tar.bz2") or file.filename.endswith(".tbz2"):
            mode = "r:bz2"
        else:
            mode = "r"
        
        with tarfile.open(tar_path, mode) as tar_ref:
            tar_ref.extractall(extract_dir)
        
        # Get list of extracted files
        extracted_files = []
        for root, dirs, files_list in os.walk(extract_dir):
            for f in files_list:
                file_path = os.path.join(root, f)
                if os.path.isfile(file_path):
                    extracted_files.append(file_path)
        
        # Process each file
        job_id = str(uuid.uuid4())
        document_ids = []
        errors = []
        
        upload_dir = config.upload.upload_dir
        os.makedirs(upload_dir, exist_ok=True)
        
        for file_path in extracted_files:
            try:
                # Check file size
                file_size = os.path.getsize(file_path)
                max_size = config.upload.max_file_size_mb * 1024 * 1024
                if file_size > max_size:
                    errors.append(f"{os.path.basename(file_path)}: File too large")
                    continue
                
                # Check file extension
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in config.upload.allowed_extensions:
                    errors.append(f"{os.path.basename(file_path)}: File type not allowed")
                    continue
                
                # Move file to upload directory
                file_id = str(uuid.uuid4())
                new_file_path = os.path.join(upload_dir, f"{file_id}{file_ext}")
                os.rename(file_path, new_file_path)
                
                # Create document record
                file_type = get_document_type(file_ext)
                document = UploadedDocument(
                    document_id=file_id,
                    filename=f"{file_id}{file_ext}",
                    original_filename=os.path.basename(file_path),
                    file_path=new_file_path,
                    file_type=file_type,
                    file_extension=file_ext,
                    size_bytes=file_size,
                    mime_type=None,
                    status=DocumentStatus.PENDING,
                    metadata={"batch_job_id": job_id, "source": "tar"},
                    tags=["batch", job_id, "tar"]
                )
                
                documents_db[file_id] = document
                document_ids.append(file_id)
                
            except Exception as e:
                errors.append(f"{os.path.basename(file_path)}: {str(e)}")
        
        # Store batch job
        batch_jobs[job_id] = {
            "job_id": job_id,
            "status": "completed",
            "progress": 100.0,
            "processed_files": len(document_ids),
            "total_files": len(extracted_files),
            "document_ids": document_ids,
            "errors": errors,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        return BatchUploadResponse(
            job_id=job_id,            document_ids=document_ids,
            total_files=len(extracted_files),
            status="completed",
            message=f"Extracted and uploaded {len(document_ids)} files with {len(errors)} errors"
        )
        
    finally:
        # Clean up temp directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


@router.get("/batch/{job_id}/status", response_model=BatchJobStatus)
async def get_batch_job_status(job_id: str):
    """
    Get status of a batch job
    """
    job = batch_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Batch job {job_id} not found")
    
    return BatchJobStatus(
        job_id=job["job_id"],
        status=job["status"],
        progress=job["progress"],
        processed_files=job["processed_files"],
        total_files=job["total_files"],
        document_ids=job["document_ids"],
        errors=job["errors"]
    )


@router.get("/batch/{job_id}/documents", response_model=List[Dict])
async def get_batch_job_documents(job_id: str):
    """
    Get all documents from a batch job
    """
    job = batch_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Batch job {job_id} not found")
    
    documents = []
    for doc_id in job["document_ids"]:
        doc = documents_db.get(doc_id)
        if doc:
            documents.append({
                "document_id": doc.document_id,
                "filename": doc.filename,
                "original_filename": doc.original_filename,
                "status": doc.status.value,
                "uploaded_at": doc.uploaded_at.isoformat()
            })
    
    return documents


@router.delete("/batch/{job_id}", status_code=200)
async def delete_batch_job(job_id: str):
    """
    Delete a batch job and all its documents
    """
    job = batch_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Batch job {job_id} not found")
    
    # Delete all documents in the batch
    config = get_config()
    for doc_id in job["document_ids"]:
        doc = documents_db.get(doc_id)
        if doc and os.path.exists(doc.file_path):
            os.remove(doc.file_path)
        if doc_id in documents_db:
            del documents_db[doc_id]
    
    # Delete the batch job
    del batch_jobs[job_id]
    
    return {"message": f"Batch job {job_id} and its documents deleted successfully"}