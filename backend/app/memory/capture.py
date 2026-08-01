#!/usr/bin/env python3
"""
NFM-X Memory Capture Engine
===========================

Handles the capture and ingestion of new memories into the system.
Supports multiple memory types and automatic classification.

Urdu: Yadashthon ko capture karne aur system mein shamil karne ka engine
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
import uuid
import json
import hashlib

from .models import Memory, MemoryVersion, MemoryType
from .classification import MemoryClassifier
from .confidence import ConfidenceCalculator


class MemoryCaptureInput(BaseModel):
    content: str
    memory_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    timestamp: Optional[datetime] = None
    confidence: Optional[float] = None
    tags: Optional[List[str]] = None
    related_entities: Optional[List[str]] = None


class MemoryCaptureResult(BaseModel):
    memory_id: str
    version_id: str
    classified_type: str
    confidence_score: float
    timestamp: datetime
    checksum: str
    status: str


class MemoryCapturer:
    def __init__(self, classifier: Optional[MemoryClassifier] = None, 
                 confidence_calculator: Optional[ConfidenceCalculator] = None):
        self.classifier = classifier or MemoryClassifier()
        self.confidence_calculator = confidence_calculator or ConfidenceCalculator()
    
    def capture_memory(self, input_data: MemoryCaptureInput) -> MemoryCaptureResult:
        memory_id = str(uuid.uuid4())
        version_id = str(uuid.uuid4())
        timestamp = input_data.timestamp or datetime.utcnow()
        
        memory_type = input_data.memory_type
        if not memory_type:
            memory_type = self.classifier.classify_memory(input_data.content, input_data.metadata or {})
        
        confidence = input_data.confidence
        if confidence is None:
            confidence = self.confidence_calculator.calculate_confidence(
                input_data.content, memory_type, input_data.metadata or {}
            )
        
        checksum = self._generate_checksum(input_data.content)
        
        memory = Memory(
            id=memory_id, content=input_data.content, memory_type=memory_type,
            source=input_data.source, metadata=input_data.metadata or {},
            tags=input_data.tags or [], created_at=timestamp, updated_at=timestamp,
            current_version_id=version_id
        )
        
        version = MemoryVersion(
            id=version_id, memory_id=memory_id, content=input_data.content,
            memory_type=memory_type, confidence=confidence, checksum=checksum,
            timestamp=timestamp, source=input_data.source, metadata=input_data.metadata or {},
            version_number=1, is_current=True
        )
        
        return MemoryCaptureResult(
            memory_id=memory_id, version_id=version_id, classified_type=memory_type,
            confidence_score=confidence, timestamp=timestamp, checksum=checksum, status="captured"
        )
    
    def _generate_checksum(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def batch_capture(self, inputs: List[MemoryCaptureInput]) -> List[MemoryCaptureResult]:
        return [self.capture_memory(input_data) for input_data in inputs]
    
    def capture_from_dict(self, data: Dict[str, Any]) -> MemoryCaptureResult:
        input_data = MemoryCaptureInput(**data)
        return self.capture_memory(input_data)


# Urdu: NFM-X memory capture engine - Yadashthon ko system mein shamil karne ke liye