from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from pathlib import Path

from ..ocr.engine import OCREngine

router = APIRouter()

@router.post("/ocr/image")
async def ocr_image(file: UploadFile = File(...), language: Optional[str] = Form("en")):
    temp_path = f"./storage/temp/{file.filename}"
    Path("./storage/temp").mkdir(parents=True, exist_ok=True)
    content = await file.read()
    Path(temp_path).write_bytes(content)
    engine = OCREngine(languages=[language])
    return await engine.process_image(temp_path)

@router.post("/ocr/pdf")
async def ocr_pdf(file: UploadFile = File(...), language: Optional[str] = Form("en")):
    temp_path = f"./storage/temp/{file.filename}"
    Path("./storage/temp").mkdir(parents=True, exist_ok=True)
    content = await file.read()
    Path(temp_path).write_bytes(content)
    engine = OCREngine(languages=[language])
    return await engine.process_pdf(temp_path)
