"""
NFM-X Conflict Engine

Handles detection and resolution of contradictory information.

Key features:
- Detect contradictions between memories
- Preserve contradictory information until resolved
- Use multiple signals for resolution:
  * Recency
  * Source reliability
  * Explicit confirmation
  * Context
  * Evidence
  * Temporal validity
"""

from .conflict_detector import ConflictDetector
from .conflict_resolver import ConflictResolver
from .conflict_store import ConflictStore

__all__ = ['ConflictDetector', 'ConflictResolver', 'ConflictStore']