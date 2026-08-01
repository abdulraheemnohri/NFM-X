"""
NFM-X OCR Engines Package
==========================

This package contains implementations of various OCR engines for NFM-X.
"""

from .base import BaseOCREngine, create_ocr_engine

__all__ = ['BaseOCREngine', 'create_ocr_engine']

AVAILABLE_ENGINES = ['pytesseract', 'easyocr', 'paddleocr']

# Urdu: NFM-X OCR انجنز پیکج