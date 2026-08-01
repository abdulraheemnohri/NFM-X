"""
NFM-X OCR Base Engine
======================

Abstract base class for all OCR engines.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple
from ..models import OCRResult, OCRLayout, OCRDocument


class BaseOCREngine(ABC):
    def __init__(self, **kwargs):
        self.name = self.__class__.__name__.replace('Engine', '').lower()
        self.config = kwargs
        self._initialized = False
    
    @abstractmethod
    def initialize(self):
        pass
    
    @abstractmethod
    def extract_text(self, image: Any, **kwargs) -> Tuple[str, OCRLayout]:
        pass
    
    @abstractmethod
    def get_languages(self) -> List[str]:
        pass
    
    @abstractmethod
    def set_language(self, language: str):
        pass
    
    def is_available(self) -> bool:
        try:
            if not self._initialized:
                self.initialize()
                self._initialized = True
            return True
        except Exception:
            return False
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.__class__.__name__,
            'available': self.is_available(),
            'languages': self.get_languages(),
            'config': self.config
        }


def create_ocr_engine(engine_name: str, **kwargs) -> BaseOCREngine:
    if engine_name == 'pytesseract':
        from .pytesseract_engine import PytesseractEngine
        return PytesseractEngine(**kwargs)
    elif engine_name == 'easyocr':
        from .easyocr_engine import EasyOCREngine
        return EasyOCREngine(**kwargs)
    elif engine_name == 'paddleocr':
        from .paddleocr_engine import PaddleOCREngine
        return PaddleOCREngine(**kwargs)
    raise ValueError(f"Unknown OCR engine: {engine_name}")


# Urdu: NFM-X OCR بیس انجن