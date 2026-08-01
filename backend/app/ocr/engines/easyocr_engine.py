"""
NFM-X EasyOCR Engine
=====================

OCR engine implementation using EasyOCR.
"""

import warnings
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
from PIL import Image
from ..models import OCRLayout
from .base import BaseOCREngine


class EasyOCREngine(BaseOCREngine):
    def __init__(self, lang: List[str] = ['en', 'ur'], gpu: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.lang = lang
        self.gpu = gpu
        self._reader = None
        self._initialized = False
    
    def initialize(self):
        if self._initialized:
            return
        try:
            import easyocr
            self._reader = easyocr.Reader(lang_list=self.lang, gpu=self.gpu)
            self._initialized = True
        except ImportError as e:
            raise RuntimeError("EasyOCR is not installed. Please install with: pip install easyocr")
    
    def get_languages(self) -> List[str]:
        return ['en', 'ur', 'ar', 'hi', 'fr', 'es', 'de', 'ru', 'zh-sim']
    
    def set_language(self, language: str):
        if isinstance(language, str):
            self.lang = [language]
        else:
            self.lang = language
        self._initialized = False
    
    def extract_text(self, image: Any, **kwargs) -> Tuple[str, OCRLayout]:
        self.initialize()
        
        if isinstance(image, Image.Image):
            img = np.array(image)
        elif isinstance(image, np.ndarray):
            img = image
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")
        
        try:
            results = self._reader.readtext(img, detail=0)
            text = ' '.join([r[1] for r in results])
            layout = OCRLayout()
            return text.strip(), layout
        except Exception as e:
            warnings.warn(f"EasyOCR extraction failed: {e}")
            return "", OCRLayout()
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': 'easyocr',
            'type': self.__class__.__name__,
            'available': self._initialized or self.is_available(),
            'languages': self.get_languages(),
            'gpu': self.gpu,
            'current_languages': self.lang
        }


# Urdu: NFM-X EasyOCR انجن