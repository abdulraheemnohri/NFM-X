"""
NFM-X Evolution Engine

Handles automatic memory evolution through:
- Reinforcement
- Refinement
- Expansion
- Correction
- Merging
- Splitting
- Superseding
- Contradiction handling
- Hypothesis validation
- Pattern discovery
"""

from .evolution_engine import EvolutionEngine
from .reinforcement import MemoryReinforcer
from .refinement import MemoryRefiner
from .expansion import MemoryExpander
from .correction import MemoryCorrector
from .merger import MemoryMerger
from .splitter import MemorySplitter

__all__ = [
    'EvolutionEngine',
    'MemoryReinforcer',
    'MemoryRefiner',
    'MemoryExpander',
    'MemoryCorrector',
    'MemoryMerger',
    'MemorySplitter',
]