"""
NFM-X PaddleOCR Engine
=======================

OCR engine implementation using PaddleOCR.
"""

import warnings
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
from PIL import Image
from ..models import OCRLayout
from .base import BaseOCREngine


class PaddleOCREngine(BaseOCREngine):
    def __init__(self, lang: str = 'en', use_gpu: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.lang = lang
        self.use_gpu = use_gpu
        self._ocr = None
        self._initialized = False
    
    def initialize(self):
        if self._initialized:
            return
        try:
            from paddleocr import PaddleOCR
            self._ocr = PaddleOCR(use_gpu=self.use_gpu, lang=self.lang)
            self._initialized = True
        except ImportError as e:
            raise RuntimeError("PaddleOCR is not installed. Please install with: pip install paddlepaddle paddleocr")
    
    def get_languages(self) -> List[str]:
        return ['ch', 'en', 'fr', 'german', 'ar', 'hi', 'ur', 'fa', 'ru', 'es']
    
    def set_language(self, language: str):
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
            result = self._ocr.ocr(img, cls=True, lang=self.lang)
            if result and len(result) > 0 and result[0]:
                text = ' '.join([r[1][0] for r in result[0]])
            else:
                text = ""
            layout = OCRLayout()
            return text.strip(), layout
        except Exception as e:
            warnings.warn(f"PaddleOCR extraction failed: {e}")
            return "", OCRLayout()
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': 'paddleocr',
            'type': self.__class__.__name__,
            'available': self._initialized or self.is_available(),
            'languages': self.get_languages(),
            'use_gpu': self.use_gpu,
            'current_language': self.lang
        }


# Urdu: NFM-X PaddleOCR انجن