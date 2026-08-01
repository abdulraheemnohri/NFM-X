"""
NFM-X Memory Classification Engine
Classifies memory candidates and determines memory types
"""

from typing import Dict, Any, List, Optional
import logging
import re

logger = logging.getLogger(__name__)


class MemoryClassifier:
    def __init__(self):
        self.type_patterns = {
            "episodic": [r"user\s+(requested|asked|said|told)", r"ai\s+(responded|replied|said|generated)", r"conversation", r"interaction"],
            "semantic": [r"is\s+a\s+\w+", r"\w+\s+is\s+\w+", r"definition", r"fact", r"knowledge"],
            "procedural": [r"step\s+\d+", r"how\s+to\s+", r"procedure", r"algorithm", r"process"],
            "preference": [r"prefer\s+\w+", r"like\s+\w+", r"favorite", r"preference"],
            "decision": [r"decided\s+to\s+", r"chose\s+\w+", r"decision", r"choice"],
            "failure": [r"failed\s+to\s+", r"error", r"exception", r"problem", r"issue"],
            "success": [r"success", r"completed", r"finished", r"achieved", r"worked"]
        }
        self.importance_keywords = {"critical": 1.0, "essential": 1.0, "important": 0.9, "key": 0.9, "major": 0.8}

    def classify(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        content = candidate.get("content", "").lower()
        classification = {"should_store": True, "type": candidate.get("type", "episodic"), "subtype": None, "priority": 0.5, "confidence": 0.7, "importance": 0.5, "reason": ""}
        if len(content.strip()) < 5:
            classification["should_store"] = False
            classification["reason"] = "Content too short"
            return classification
        detected_type = self._detect_type(content)
        if detected_type:
            classification["type"] = detected_type
        classification["importance"] = self._calculate_importance(content)
        classification["confidence"] = self._calculate_confidence(classification["type"])
        classification["priority"] = classification["importance"] * classification["confidence"]
        return classification

    def _detect_type(self, content: str) -> Optional[str]:
        for mem_type, patterns in self.type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    return mem_type
        return None

    def _calculate_importance(self, content: str) -> float:
        score = 0.5
        for keyword, importance in self.importance_keywords.items():
            if keyword in content:
                score = max(score, importance)
        return score

    def _calculate_confidence(self, mem_type: str) -> float:
        return {"episodic": 0.7, "semantic": 0.8, "procedural": 0.8, "preference": 0.7, "decision": 0.7, "failure": 0.9, "success": 0.8}.get(mem_type, 0.7)