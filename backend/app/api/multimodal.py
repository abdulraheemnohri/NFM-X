from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

from ..multimodal.processor import MultimodalProcessor

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), agent_id: Optional[str] = Form(None)):
    processor = MultimodalProcessor()
    return await processor.process_file(file, agent_id)

@router.post("/extract-memory")
async def extract_memory_from_file(file: UploadFile = File(...), agent_id: Optional[str] = Form(None),
                                    memory_type: Optional[str] = Form("semantic")):
    processor = MultimodalProcessor()
    processed = await processor.process_file(file, agent_id)
    texts = []
    if processed["type"] == "pdf":
        for page in processed.get("pages", []):
            texts.append(page["text"])
    elif processed["type"] in ("document", "image"):
        texts.append(processed.get("text", ""))
    combined = "\n\n".join(texts)
    return {"document_id": processed["document_id"], "extracted_text": combined[:5000],
            "word_count": len(combined.split()), "suggested_memory_type": memory_type, "status": "extracted"}
