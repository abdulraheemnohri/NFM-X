"""
Rule-based memory classification for NFM-X
"""
from typing import Optional
from dataclasses import dataclass
from enum import Enum
import re
from .models import MemoryType

@dataclass
class ClassificationResult:
    memory_type: MemoryType
    confidence: float
    reason: str

class MemoryClassifier:
    TYPE_PATTERNS = {
        MemoryType.FACT: {"keywords": ["is", "are", "fact", "true"], "patterns": [r'\b(is|are|was)\b'], "weight": 1.0},
        MemoryType.CONCEPT: {"keywords": ["concept", "idea", "theory"], "patterns": [r'\b(concept|idea)\b'], "weight": 1.2},
        MemoryType.PROCEDURE: {"keywords": ["step", "how to", "first", "then"], "patterns": [r'\b(step|how to)\b'], "weight": 1.3},
        MemoryType.EXPERIENCE: {"keywords": ["I", "experience", "happened"], "patterns": [r'\b(I|me)\b'], "weight": 1.1},
        MemoryType.CAUSAL: {"keywords": ["because", "causes", "leads to"], "patterns": [r'\b(because|causes)\b'], "weight": 1.4},
        MemoryType.DECISION: {"keywords": ["decide", "decision", "choose"], "patterns": [r'\b(decide|decision)\b'], "weight": 1.2},
        MemoryType.OBSERVATION: {"keywords": ["observe", "notice"], "patterns": [r'\b(observe|notice)\b'], "weight": 1.1},
        MemoryType.HYPOTHESIS: {"keywords": ["hypothesis", "maybe"], "patterns": [r'\b(hypothesis|maybe)\b'], "weight": 1.0},
        MemoryType.GOAL: {"keywords": ["goal", "want", "achieve"], "patterns": [r'\b(goal|objective)\b'], "weight": 1.2},
        MemoryType.PLAN: {"keywords": ["plan", "strategy", "will"], "patterns": [r'\b(plan|strategy)\b'], "weight": 1.3},
    }

    def __init__(self):
        self._compiled = {t: [re.compile(p, re.IGNORECASE) for p in c["patterns"]] for t, c in self.TYPE_PATTERNS.items()}

    def classify(self, content: str, default_type: MemoryType = MemoryType.FACT) -> ClassificationResult:
        if not content or not content.strip():
            return ClassificationResult(memory_type=default_type, confidence=0.5, reason="Empty")
        clean = content.strip().lower()
        scores = {}
        for mem_type, config in self.TYPE_PATTERNS.items():
            score = sum(len(p.findall(clean)) * config["weight"] * 0.5 for p in self._compiled[mem_type])
            score += sum(0.1 * config["weight"] for k in config["keywords"] if k.lower() in clean)
            if len(clean) > 0:
                score = score / (len(clean.split()) ** 0.5)
            scores[mem_type] = score
        if scores:
            best = max(scores.items(), key=lambda x: x[1])
            total = sum(scores.values())
            confidence = best[1] / total if total > 0 else 0.5
            confidence = max(0.3, min(0.95, confidence))
            return ClassificationResult(memory_type=best[0], confidence=round(confidence, 2), reason="Pattern match")
        return ClassificationResult(memory_type=default_type, confidence=0.5, reason="No match")

classifier = MemoryClassifier()