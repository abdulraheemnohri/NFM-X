"""
NFM-X OCR Language Detection Module
=====================================

Language detection for OCR extracted text.
"""

import re
from typing import Dict, List, Tuple


LANGUAGE_PATTERNS = {
    'ur': {'name': 'Urdu', 'ranges': [(0x0600, 0x06FF), (0x0750, 0x077F), (0x0850, 0x089F)], 'weight': 1.5},
    'en': {'name': 'English', 'ranges': [(0x0041, 0x005A), (0x0061, 0x007A)], 'weight': 1.0},
    'ar': {'name': 'Arabic', 'ranges': [(0x0600, 0x06FF)], 'weight': 1.2},
}


def detect_language(text: str, default_language: str = 'en') -> str:
    if not text or len(text.strip()) < 10:
        return default_language
    
    scores = {}
    for lang_code, lang_data in LANGUAGE_PATTERNS.items():
        score = calculate_language_score(text, lang_data)
        if score > 0:
            scores[lang_code] = score * lang_data.get('weight', 1.0)
    
    if not scores:
        return default_language
    
    return max(scores.items(), key=lambda x: x[1])[0]


def calculate_language_score(text: str, lang_data: Dict) -> float:
    char_score = calculate_char_range_score(text, lang_data.get('ranges', []))
    return char_score


def calculate_char_range_score(text: str, ranges: List[Tuple[int, int]]) -> float:
    if not ranges:
        return 0.0
    
    total_chars = len(text)
    if total_chars == 0:
        return 0.0
    
    matching_chars = 0
    for char in text:
        code = ord(char)
        for start, end in ranges:
            if start <= code <= end:
                matching_chars += 1
                break
    
    return matching_chars / total_chars


def is_urdu_text(text: str, threshold: float = 0.5) -> bool:
    if not text:
        return False
    scores = {lang: calculate_language_score(text, data) * data.get('weight', 1.0) 
              for lang, data in LANGUAGE_PATTERNS.items()}
    return scores.get('ur', 0.0) >= threshold


# Urdu: NFM-X OCR لینگویج ڈٹیکشن ماڈول