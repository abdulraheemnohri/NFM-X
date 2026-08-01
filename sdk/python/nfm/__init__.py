#!/usr/bin/env python3
"""
NFM-X SDK Package
==================

Main package for NFM-X Python SDK.

Urdu: NFM-X پائتھن SDK کے لیے بنیادی پیکیج
"""

from .client import NFMClient
from .models import (
    Memory, MemoryVersion, MemoryType, MemoryCreate, MemoryUpdate,
    SearchQuery, SearchResult, ContextQuery, ContextResult,
    EvolutionQuery, EvolutionResult, GraphQuery, GraphResult,
    AgentQuery, AgentResult
)

__all__ = [
    'NFMClient',
    'Memory', 'MemoryVersion', 'MemoryType', 'MemoryCreate', 'MemoryUpdate',
    'SearchQuery', 'SearchResult', 'ContextQuery', 'ContextResult',
    'EvolutionQuery', 'EvolutionResult', 'GraphQuery', 'GraphResult',
    'AgentQuery', 'AgentResult'
]


# Urdu Documentation
"""
 NFM-X SDK پیکیج
 ==============

 یہ NFM-X پائتھن SDK کا بنیادی پیکیج ہے۔

 کلاسز:
 - NFMClient: سسٹم سے بات چیت کے لیے بنیادی کلاس
 - Memory: میموری آبجیکٹ
 - MemoryVersion: میموری ورژن آبجیکٹ
 - MemoryType: میموری کی اقسام
 - MemoryCreate: نئی میموری بنانے کے لیے
 - MemoryUpdate: میموری اپ ڈیٹ کرنے کے لیے

 استعمال:
 ```python
 from nfm import NFMClient, MemoryCreate
 
 client = NFMClient(base_url="http://localhost:8000")
 memory = MemoryCreate(content="ٹیسٹ میموری", memory_type="episodic")
 result = client.create_memory(memory)
 ```
"""