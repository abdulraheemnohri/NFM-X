"""
NFM-X Memory Classification
"""
from typing import List, Optional
from .models import Memory, MemoryType

class MemoryClassifier:
    def classify_memory(self, memory: Memory) -> Memory:
        return memory