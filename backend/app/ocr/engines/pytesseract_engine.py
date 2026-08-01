"""
NFM-X Pytesseract OCR Engine
============================

OCR engine implementation using Pytesseract.
"""

import warnings
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
from PIL import Image
from ..models import OCRLayout, OCRTextBlock, OCRLine, OCRParagraph, BoundingBox
from .base import BaseOCREngine


class PytesseractEngine(BaseOCREngine):
    def __init__(self, lang: str = 'eng+ur', config: str = '', **kwargs):
        super().__init__(**kwargs)
        self.lang = lang
        self.config = config
        self._pytesseract = None
        self._initialized = False
    
    def initialize(self):
        if self._initialized:
            return
        try:
            import pytesseract
            self._pytesseract = pytesseract
            self._initialized = True
        except ImportError as e:
            raise RuntimeError("Pytesseract is not installed. Please install with: pip install pytesseract")
    
    def get_languages(self) -> List[str]:
        return ['eng', 'ur', 'ara', 'hin', 'fra', 'spa', 'deu', 'rus']
    
    def set_language(self, language: str):
        self.lang = language
    
    def extract_text(self, image: Any, **kwargs) -> Tuple[str, OCRLayout]:
        self.initialize()
        
        if isinstance(image, np.ndarray):
            img = Image.fromarray(image)
        elif isinstance(image, Image.Image):
            img = image
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")
        
        lang = kwargs.get('lang', self.lang)
        config = kwargs.get('config', self.config)
        
        try:
            text = self._pytesseract.image_to_string(img, lang=lang, config=config)
            layout = OCRLayout()
            return text.strip(), layout
        except Exception as e:
            warnings.warn(f"Pytesseract extraction failed: {e}")
            return "", OCRLayout()
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': 'pytesseract',
            'type': self.__class__.__name__,
            'available': self._initialized or self.is_available(),
            'languages': self.get_languages(),
            'current_language': self.lang
        }


# Urdu: NFM-X Pytesseract OCR انجن