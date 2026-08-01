"""
NFM-X OCR Entity Extraction Module
====================================

Entity extraction from OCR text.
"""

import re
from typing import List, Dict, Any
from enum import Enum


class EntityType(Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    TIME = "time"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    NUMERIC = "numeric"
    MONETARY = "monetary"


PATTERNS = {
    EntityType.EMAIL: [r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'],
    EntityType.PHONE: [r'\+?[0-9\s\-\(\)]{10,15}'],
    EntityType.URL: [r'https?://[^\s]+'],
    EntityType.DATE: [r'\d{4}-\d{2}-\d{2}', r'\d{1,2}/\d{1,2}/\d{4}'],
    EntityType.TIME: [r'\d{1,2}:\d{2}(:\d{2})?'],
}


def extract_entities(text: str, entity_types: List[EntityType] = None) -> List[Dict]:
    entities = []
    if not text or not text.strip():
        return entities
    
    if entity_types is None:
        entity_types = list(EntityType)
    
    for entity_type in entity_types:
        if entity_type in PATTERNS:
            for pattern in PATTERNS[entity_type]:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entities.append({
                        'type': entity_type.value,
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.9
                    })
    
    return entities


# Urdu: NFM-X OCR اینٹیٹی ایکسٹرکشن ماڈول