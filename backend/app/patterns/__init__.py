"""
NFM-X Pattern Discovery Module

Automatically identifies repeated patterns from experiences.

Pattern discovery pipeline:
Experiences -> Clusters -> Relationships -> Pattern -> Hypothesis -> Validation -> Derived Knowledge

Derived knowledge must reference its supporting memories.
"""

from .pattern_discoverer import PatternDiscoverer
from .cluster_analyzer import ClusterAnalyzer
from .pattern_validator import PatternValidator

__all__ = ['PatternDiscoverer', 'ClusterAnalyzer', 'PatternValidator']