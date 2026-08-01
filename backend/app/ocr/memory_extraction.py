"""
NFM-X OCR Memory Extraction Module
====================================

Memory extraction from OCR results.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from .models import OCRResult, OCRDocument, OCRRegion
from .entity_extraction import extract_entities


MEMORY_TYPE_RULES = [
    {'name': 'episodic', 'patterns': [r'(requested|asked|wanted|needed|happened|occurred)'], 'weight': 1.0},
    {'name': 'semantic', 'patterns': [r'(is|are|was|were|be|been|has|have|had)'], 'weight': 0.9},
    {'name': 'preference', 'patterns': [r'(prefer|prefers|preferred|like|likes|liked)'], 'weight': 0.8},
    {'name': 'decision', 'patterns': [r'(decided|decision|chose|choose|selected)'], 'weight': 0.9},
]


def detect_memory_type(text: str, entities: List[Dict], language: str = 'en') -> str:
    if not text or not text.strip():
        return 'semantic'
    
    scores = {}
    for rule in MEMORY_TYPE_RULES:
        score = 0.0
        for pattern in rule['patterns']:
            if re.search(pattern, text, re.IGNORECASE):
                score += rule['weight'] * 0.5
        scores[rule['name']] = score
    
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    return 'semantic'


def extract_memories_from_ocr(text: str, language: str = 'en') -> List[Dict]:
    memories = []
    if not text or not text.strip():
        return memories
    
    entities = extract_entities(text)
    chunks = text.split('\n\n')
    
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        
        memory_type = detect_memory_type(chunk, entities, language)
        memory_id = f"NFM-{uuid.uuid4().hex[:8].upper()}"
        
        memories.append({
            'memory_id': memory_id,
            'content': chunk,
            'memory_type': memory_type,
            'confidence': 0.85,
            'language': language,
            'entities': entities,
            'source_type': 'ocr',
            'extracted_at': datetime.utcnow().isoformat()
        })
    
    return memories


# Urdu: NFM-X OCR میموری ایکسٹرکشن ماڈول