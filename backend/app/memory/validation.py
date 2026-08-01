#!/usr/bin/env python3
"""
NFM-X Memory Validation Engine
=============================

Handles validation of memories before they are stored or retrieved.
Includes schema validation, content quality checks, and consistency verification.

Urdu: Yadashthon ki tasdeeq karne ka engine
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
import re
import json

from .models import Memory, MemoryVersion, MemoryType


class ValidationResult(BaseModel):
    is_valid: bool
    memory_id: Optional[str] = None
    errors: List[str] = []
    warnings: List[str] = []
    quality_score: float = 1.0
    suggestions: List[str] = []


class MemoryValidator:
    VALID_MEMORY_TYPES = {
        "episodic", "semantic", "procedural", "preference", 
        "decision", "failure", "success", "temporal", 
        "causal", "hypothesis", "conflict", "multimodal"
    }
    
    MIN_CONTENT_LENGTH = 10
    MAX_CONTENT_LENGTH = 10000
    MIN_QUALITY_SCORE = 0.3
    
    def __init__(self):
        self._empty_pattern = re.compile(r'^\s*$')
        self._url_pattern = re.compile(r'https?://\S+')
    
    def validate_memory(self, memory: Memory) -> ValidationResult:
        errors = []
        warnings = []
        suggestions = []
        quality_score = 1.0
        
        content_errors, content_warnings, content_suggestions, content_score = self._validate_content(memory.content)
        errors.extend(content_errors)
        warnings.extend(content_warnings)
        suggestions.extend(content_suggestions)
        quality_score *= content_score
        
        type_errors, type_warnings, type_suggestions, type_score = self._validate_memory_type(memory.memory_type)
        errors.extend(type_errors)
        warnings.extend(type_warnings)
        suggestions.extend(type_suggestions)
        quality_score *= type_score
        
        meta_errors, meta_warnings, meta_suggestions, meta_score = self._validate_metadata(memory.metadata)
        errors.extend(meta_errors)
        warnings.extend(meta_warnings)
        suggestions.extend(meta_suggestions)
        quality_score *= meta_score
        
        time_errors, time_warnings, time_suggestions, time_score = self._validate_timestamps(memory)
        errors.extend(time_errors)
        warnings.extend(time_warnings)
        suggestions.extend(time_suggestions)
        quality_score *= time_score
        
        if self._empty_pattern.match(memory.content):
            errors.append("Memory content cannot be empty")
            quality_score = 0.0
        
        if errors:
            is_valid = False
        elif quality_score < self.MIN_QUALITY_SCORE:
            is_valid = False
            errors.append(f"Quality score {quality_score:.2f} below minimum threshold {self.MIN_QUALITY_SCORE:.2f}")
        else:
            is_valid = True
        
        return ValidationResult(
            is_valid=is_valid, memory_id=memory.id, errors=errors,
            warnings=warnings, quality_score=quality_score, suggestions=suggestions
        )
    
    def validate_memory_version(self, version: MemoryVersion) -> ValidationResult:
        errors = []
        warnings = []
        suggestions = []
        quality_score = 1.0
        
        content_errors, content_warnings, content_suggestions, content_score = self._validate_content(version.content)
        errors.extend(content_errors)
        warnings.extend(content_warnings)
        suggestions.extend(content_suggestions)
        quality_score *= content_score
        
        if not (0 <= version.confidence <= 1):
            errors.append(f"Confidence score {version.confidence} must be between 0 and 1")
            quality_score *= 0.5
        
        if version.version_number < 1:
            errors.append(f"Version number {version.version_number} must be positive")
        
        if not version.checksum or len(version.checksum) < 10:
            warnings.append("Checksum appears to be invalid or too short")
        
        if version.timestamp > datetime.utcnow():
            errors.append("Version timestamp cannot be in the future")
        
        is_valid = len(errors) == 0 and quality_score >= self.MIN_QUALITY_SCORE
        
        return ValidationResult(
            is_valid=is_valid, memory_id=version.memory_id, errors=errors,
            warnings=warnings, quality_score=quality_score, suggestions=suggestions
        )
    
    def _validate_content(self, content: str) -> Tuple[List[str], List[str], List[str], float]:
        errors = []
        warnings = []
        suggestions = []
        quality_score = 1.0
        
        if not content:
            errors.append("Content cannot be empty")
            return errors, warnings, suggestions, 0.0
        
        if len(content) < self.MIN_CONTENT_LENGTH:
            errors.append(f"Content too short: {len(content)} characters (minimum: {self.MIN_CONTENT_LENGTH})")
            quality_score *= 0.3
        
        if len(content) > self.MAX_CONTENT_LENGTH:
            warnings.append(f"Content very long: {len(content)} characters (maximum: {self.MAX_CONTENT_LENGTH})")
            suggestions.append("Consider splitting long memories into smaller chunks")
            quality_score *= 0.8
        
        urls = self._url_pattern.findall(content)
        if len(urls) > 5:
            warnings.append(f"Excessive URLs found: {len(urls)}")
            suggestions.append("Consider reducing the number of URLs")
            quality_score *= 0.9
        
        lines = content.split('\n')
        if len(lines) > 50:
            warnings.append(f"Excessive line breaks: {len(lines)} lines")
            suggestions.append("Consider formatting long content as paragraphs")
            quality_score *= 0.85
        
        return errors, warnings, suggestions, quality_score
    
    def _validate_memory_type(self, memory_type: str) -> Tuple[List[str], List[str], List[str], float]:
        errors = []
        warnings = []
        suggestions = []
        quality_score = 1.0
        
        if not memory_type:
            errors.append("Memory type is required")
            return errors, warnings, suggestions, 0.5
        
        if memory_type not in self.VALID_MEMORY_TYPES:
            errors.append(f"Invalid memory type: {memory_type}")
            suggestions.append(f"Use one of: {', '.join(self.VALID_MEMORY_TYPES)}")
            quality_score = 0.0
        
        return errors, warnings, suggestions, quality_score
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> Tuple[List[str], List[str], List[str], float]:
        errors = []
        warnings = []
        suggestions = []
        quality_score = 1.0
        
        if not metadata:
            warnings.append("No metadata provided")
            suggestions.append("Consider adding metadata for better organization and retrieval")
            quality_score *= 0.9
            return errors, warnings, suggestions, quality_score
        
        try:
            json.dumps(metadata)
        except (TypeError, ValueError):
            errors.append("Metadata must be JSON serializable")
            quality_score = 0.5
        
        if len(str(metadata)) > 10000:
            warnings.append("Metadata is very large")
            suggestions.append("Consider reducing metadata size")
            quality_score *= 0.8
        
        return errors, warnings, suggestions, quality_score
    
    def _validate_timestamps(self, memory: Memory) -> Tuple[List[str], List[str], List[str], float]:
        errors = []
        warnings = []
        suggestions = []
        quality_score = 1.0
        
        if memory.created_at > datetime.utcnow():
            errors.append("Created timestamp cannot be in the future")
            quality_score = 0.0
        
        if memory.updated_at < memory.created_at:
            errors.append("Updated timestamp cannot be before created timestamp")
            quality_score *= 0.3
        
        now = datetime.utcnow()
        if memory.created_at < now.replace(year=now.year - 10):
            warnings.append("Created timestamp is very old (more than 10 years)")
            suggestions.append("Verify that the timestamp is correct")
            quality_score *= 0.8
        
        return errors, warnings, suggestions, quality_score
    
    def batch_validate(self, memories: List[Memory]) -> Dict[str, ValidationResult]:
        return {memory.id: self.validate_memory(memory) for memory in memories}


# Urdu: NFM-X memory validation engine - Yadashthon ki tasdeeq ke liye