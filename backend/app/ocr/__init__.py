"""
NFM-X OCR Module
================

OCR (Optical Character Recognition) subsystem for NFM-X.
This module provides complete document and image text extraction capabilities
with support for multiple OCR engines, preprocessing, and memory extraction.

Features:
- Multiple OCR engine support (Tesseract, EasyOCR, PaddleOCR)
- Document preprocessing (denoising, deskewing, binarization)
- Text extraction with layout preservation
- Language detection (including Urdu, English, and mixed content)
- Entity extraction from OCR results
- Memory extraction and storage
- Provenance tracking for OCR-derived memories

Usage:
    from app.ocr import OCRProcessor
    
    processor = OCRProcessor(engine='pytesseract')
    result = processor.process_document('/path/to/document.pdf')
    
    # Access extracted text
    print(result.text)
    
    # Access extracted memories
    for memory in result.memories:
        print(f"Memory: {memory.content}")

Author: Abdulraheem Nohari
Project: NFM-X - Non-Forgettable Evolutionary AI Memory
"""

# Urdu: NFM-X OCR ماڈول
# یہ ماڈول NFM-X کے لیے مکمل OCR سب سسٹم فراہم کرتا ہے