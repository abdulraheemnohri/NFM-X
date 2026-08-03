"""
NFM-X Structured Data Extraction Module
Extracts tables, key-value pairs, and structured data from documents during OCR processing.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import json
import re
from datetime import datetime


@dataclass
class ExtractedTable:
    rows: List[List[str]]
    headers: Optional[List[str]] = None
    page_number: int = 1
    confidence: float = 0.0


@dataclass
class ExtractedKeyValue:
    key: str
    value: str
    page_number: int = 1
    confidence: float = 0.0


@dataclass
class ExtractedEntity:
    text: str
    entity_type: str
    page_number: int = 1
    confidence: float = 0.0


@dataclass
class StructuredExtractionResult:
    document_id: str
    document_name: str
    tables: List[ExtractedTable]
    key_value_pairs: List[ExtractedKeyValue]
    entities: List[ExtractedEntity]
    extracted_at: str
    processing_time_ms: float
    
    def __post_init__(self):
        if self.tables is None:
            self.tables = []
        if self.key_value_pairs is None:
            self.key_value_pairs = []
        if self.entities is None:
            self.entities = []
        if self.extracted_at is None:
            self.extracted_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StructuredDataExtractor:
    def __init__(self):
        self.key_value_separators = [':', '-', '=']
        self.entity_patterns = {
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'amount': r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\+?\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b',
        }
    
    def extract_tables_from_ocr(self, ocr_result: Dict[str, Any]) -> List[ExtractedTable]:
        tables = []
        if 'tables' in ocr_result:
            for table_data in ocr_result['tables']:
                tables.append(ExtractedTable(
                    rows=table_data.get('rows', []),
                    headers=table_data.get('headers'),
                    page_number=table_data.get('page', 1),
                    confidence=table_data.get('confidence', 0.85)
                ))
        return tables
    
    def extract_key_value_pairs(self, text: str, page_number: int = 1) -> List[ExtractedKeyValue]:
        pairs = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            for sep in self.key_value_separators:
                if sep in line:
                    parts = line.split(sep, 1)
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if key and value and len(key) < 100:
                        pairs.append(ExtractedKeyValue(
                            key=key,
                            value=value,
                            page_number=page_number,
                            confidence=0.9
                        ))
                        break
        return pairs
    
    def extract_entities(self, text: str, page_number: int = 1) -> List[ExtractedEntity]:
        entities = []
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append(ExtractedEntity(
                    text=match.group(0),
                    entity_type=entity_type,
                    page_number=page_number,
                    confidence=0.8
                ))
        return entities
    
    def extract_all(self, text: str, document_id: str, document_name: str, page_number: int = 1) -> StructuredExtractionResult:
        import time
        start_time = time.time()
        tables = self.extract_tables_from_ocr({'tables': []})
        pairs = self.extract_key_value_pairs(text, page_number)
        entities = self.extract_entities(text, page_number)
        processing_time = (time.time() - start_time) * 1000
        return StructuredExtractionResult(
            document_id=document_id,
            document_name=document_name,
            tables=tables,
            key_value_pairs=pairs,
            entities=entities,
            extracted_at=datetime.utcnow().isoformat(),
            processing_time_ms=processing_time
        )
    
    def to_memory_entries(self, extraction_result: StructuredExtractionResult) -> List[Dict[str, Any]]:
        memories = []
        for i, table in enumerate(extraction_result.tables):
            table_data = {'headers': table.headers or [], 'rows': table.rows}
            memories.append({
                'content': json.dumps(table_data),
                'subtype': 'table',
                'metadata': {
                    'source': extraction_result.document_name,
                    'document_id': extraction_result.document_id,
                    'page': table.page_number,
                    'confidence': table.confidence
                }
            })
        for pair in extraction_result.key_value_pairs:
            memories.append({
                'content': f"{pair.key}: {pair.value}",
                'subtype': 'key_value',
                'metadata': {
                    'source': extraction_result.document_name,
                    'document_id': extraction_result.document_id,
                    'key': pair.key,
                    'page': pair.page_number
                }
            })
        for entity in extraction_result.entities:
            memories.append({
                'content': entity.text,
                'subtype': entity.entity_type,
                'metadata': {
                    'source': extraction_result.document_name,
                    'document_id': extraction_result.document_id,
                    'page': entity.page_number
                }
            })
        return memories


structured_extractor = StructuredDataExtractor()