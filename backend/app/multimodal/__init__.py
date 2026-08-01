"""
NFM-X Multimodal Memory Module

Handles memory storage and retrieval for various modalities:
- TEXT
- IMAGE
- PDF
- SCREENSHOT
- AUDIO
- VIDEO
- DOCUMENT
- CODE
- TABLE
- CSV
- JSON
- WEB CONTENT
- OCR

Each multimodal memory retains a reference to the original source.
"""

from .text_handler import TextHandler
from .image_handler import ImageHandler
from .pdf_handler import PDFHandler
from .audio_handler import AudioHandler
from .video_handler import VideoHandler

__all__ = ['TextHandler', 'ImageHandler', 'PDFHandler', 'AudioHandler', 'VideoHandler']