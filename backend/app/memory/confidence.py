"""
NFM-X Confidence Engine
Calculates and manages memory confidence scores
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConfidenceEngine:
    def __init__(self):
        self.weights = {
            "source_reliability": 0.25,
            "evidence_strength": 0.20,
            "recency": 0.15,
            "repetition": 0.15,
            "user_confirmation": 0.10,
            "model_confidence": 0.05,
            "contradiction_level": -0.10,
            "temporal_stability": 0.10
        }

    def calculate_confidence(
        self,
        source_reliability: float = 0.8,
        evidence_strength: float = 0.7,
        recency: float = 0.8,
        repetition: int = 1,
        user_confirmed: bool = False,
        model_confidence: float = 0.7,
        contradiction_count: int = 0,
        temporal_stability: float = 0.8
    ) -> float:
        repetition_score = min(1.0, repetition * 0.2)
        contradiction_penalty = min(1.0, contradiction_count * 0.1)
        confidence = (
            self.weights["source_reliability"] * source_reliability +
            self.weights["evidence_strength"] * evidence_strength +
            self.weights["recency"] * recency +
            self.weights["repetition"] * repetition_score +
            self.weights["user_confirmation"] * (1.0 if user_confirmed else 0.0) +
            self.weights["model_confidence"] * model_confidence +
            self.weights["contradiction_level"] * (1.0 - contradiction_penalty) +
            self.weights["temporal_stability"] * temporal_stability
        )
        return max(0.0, min(1.0, confidence))

    def update_confidence(
        self,
        current_confidence: float,
        new_evidence_strength: float = 0.7,
        is_contradiction: bool = False,
        user_confirmed: bool = False
    ) -> float:
        if is_contradiction:
            return max(0.1, current_confidence - new_evidence_strength * 0.3)
        else:
            increase = new_evidence_strength * (1.0 - current_confidence) * 0.2
            if user_confirmed:
                increase *= 2.0
            return min(1.0, current_confidence + increase)