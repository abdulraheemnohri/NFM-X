"""NFM-X V2 Memory Capture - Multi-modal memory acquisition"""

from typing import Optional, Dict, List
from datetime import datetime
from .models_v2 import MemoryV2, MemoryModality


def capture_memory_v2(
    content: str,
    metadata: Optional[Dict] = None,
    tags: Optional[List[str]] = None,
    source: Optional[str] = None,
    modality: MemoryModality = MemoryModality.TEXT,
    previous_version_id: Optional[str] = None
) -> MemoryV2:
    """
    Capture a new memory with V2 features
    - Multi-modal support (text, image, audio)
    - Automatic versioning
    - Relationship tracking
    """
    memory = MemoryV2(
        content=content,
        metadata=metadata or {},
        tags=tags or [],
        source=source,
        modality=modality,
        version=1
    )
    
    if previous_version_id:
        memory.version = 2  # Will be incremented based on actual previous versions
        memory.previous_version_id = previous_version_id
    
    return memory