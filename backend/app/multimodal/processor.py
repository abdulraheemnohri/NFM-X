from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone
import uuid
from fastapi import UploadFile
from PIL import Image
import fitz
from io import BytesIO

class MultimodalProcessor:
    SUPPORTED_TYPES = {
        "image": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"],
        "pdf": [".pdf"],
        "document": [".txt", ".md", ".json", ".csv"],
        "audio": [".wav", ".mp3", ".m4a", ".ogg"],
    }

    def detect_type(self, filename: str) -> Optional[str]:
        ext = Path(filename).suffix.lower()
        for file_type, extensions in self.SUPPORTED_TYPES.items():
            if ext in extensions:
                return file_type
        return None

    async def process_file(self, file: UploadFile, agent_id: Optional[str] = None) -> Dict[str, Any]:
        file_type = self.detect_type(file.filename)
        if not file_type:
            raise ValueError(f"Unsupported file type: {file.filename}")
        content = await file.read()
        if file_type == "image":
            return await self._process_image(content, file.filename, agent_id)
        elif file_type == "pdf":
            return await self._process_pdf(content, file.filename, agent_id)
        elif file_type == "document":
            return await self._process_document(content, file.filename, agent_id)
        elif file_type == "audio":
            return await self._process_audio(content, file.filename, agent_id)
        return {"error": "Unknown file type"}

    async def _process_image(self, content, filename, agent_id):
        doc_id = f"IMG-{uuid.uuid4().hex[:8]}"
        storage_path = Path(f"./storage/objects/{doc_id}_{filename}")
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        storage_path.write_bytes(content)
        img = Image.open(BytesIO(content))
        return {"document_id": doc_id, "type": "image", "filename": filename,
                "file_path": str(storage_path), "dimensions": {"width": img.width, "height": img.height},
                "agent_id": agent_id, "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "pending_ocr"}

    async def _process_pdf(self, content, filename, agent_id):
        doc_id = f"PDF-{uuid.uuid4().hex[:8]}"
        storage_path = Path(f"./storage/objects/{doc_id}_{filename}")
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        storage_path.write_bytes(content)
        doc = fitz.open(stream=content, filetype="pdf")
        pages = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            pages.append({"page_number": page_num + 1, "text": text, "word_count": len(text.split())})
        doc.close()
        return {"document_id": doc_id, "type": "pdf", "filename": filename,
                "file_path": str(storage_path), "page_count": len(pages), "pages": pages,
                "agent_id": agent_id, "timestamp": datetime.now(timezone.utc).isoformat()}

    async def _process_document(self, content, filename, agent_id):
        doc_id = f"DOC-{uuid.uuid4().hex[:8]}"
        text = content.decode("utf-8", errors="replace")
        return {"document_id": doc_id, "type": "document", "filename": filename,
                "text": text, "word_count": len(text.split()),
                "agent_id": agent_id, "timestamp": datetime.now(timezone.utc).isoformat()}

    async def _process_audio(self, content, filename, agent_id):
        doc_id = f"AUD-{uuid.uuid4().hex[:8]}"
        storage_path = Path(f"./storage/objects/{doc_id}_{filename}")
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        storage_path.write_bytes(content)
        return {"document_id": doc_id, "type": "audio", "filename": filename,
                "file_path": str(storage_path), "agent_id": agent_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "pending_transcription",
                "note": "Audio transcription requires external STT service"}
