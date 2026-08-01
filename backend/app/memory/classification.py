from typing import Dict, Any, Optional
import re

class MemoryClassifier:
    def __init__(self):
        self.type_patterns = {
            "episodic": [r"user\s+(requested|asked|said|told|says)", r"ai\s+(responded|replied|said|generated)", r"conversation", r"interaction", r"yesterday", r"today", r"meeting"],
            "semantic": [r"is\s+a\s+\w+", r"\w+\s+is\s+\w+", r"definition", r"fact", r"knowledge", r"capital\s+of", r"founded\s+in"],
            "procedural": [r"step\s+\d+", r"how\s+to\s+", r"procedure", r"algorithm", r"process", r"first,", r"second,", r"then\s+run"],
            "preference": [r"prefer\s+\w+", r"like\s+\w+", r"favorite", r"preference", r"hates", r"likes"],
            "decision": [r"decided\s+to\s+", r"chose\s+\w+", r"decision", r"choice", r"selected"],
            "failure": [r"failed\s+to\s+", r"error", r"exception", r"problem", r"issue", r"crash", r"bug"],
            "success": [r"success", r"completed", r"finished", r"achieved", r"worked", r"resolved", r"passed"]
        }
        self.importance_keywords = {
            "critical": 1.0,
            "essential": 1.0,
            "important": 0.9,
            "key": 0.9,
            "major": 0.8,
            "urgent": 0.9,
            "trivial": 0.1,
            "minor": 0.3
        }

    def classify(self, content: str) -> Dict[str, Any]:
        content_lower = content.lower().strip()
        detected_type = self._detect_type(content_lower) or "episodic"
        importance = self._calculate_importance(content_lower)
        confidence = self._calculate_confidence(detected_type)

        return {
            "type": detected_type,
            "confidence": confidence,
            "importance": importance
        }

    def _detect_type(self, content: str) -> Optional[str]:
        for mem_type, patterns in self.type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    return mem_type
        return None

    def _calculate_importance(self, content: str) -> float:
        score = 0.5
        for keyword, val in self.importance_keywords.items():
            if keyword in content:
                score = max(score, val)
        return score

    def _calculate_confidence(self, mem_type: str) -> float:
        return {
            "working": 0.7,
            "episodic": 0.7,
            "semantic": 0.8,
            "procedural": 0.8,
            "preference": 0.7,
            "decision": 0.7,
            "failure": 0.9,
            "success": 0.8
        }.get(mem_type, 0.7)
