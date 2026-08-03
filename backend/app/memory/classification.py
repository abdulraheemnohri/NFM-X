"""
NFM-X Memory Classification
Automatic classification of memories using rule-based approaches
"""
from typing import List, Optional
import re
from .models import Memory, MemoryType, MemoryPriority


class MemoryClassifier:
    def __init__(self):
        self._init_keyword_classifiers()
    
    def _init_keyword_classifiers(self):
        self.type_keywords = {
            MemoryType.CONVERSATION: [
                "user:", "assistant:", "bot:", "ai:", "human:",
                "question:", "answer:", "response:", "message:"
            ],
            MemoryType.CODE: [
                "def ", "class ", "import ", "from ", "return ",
                "function", "var ", "const ", "let ", "if (",
                "for (", "while (", "#include", "public class", "private"
            ],
            MemoryType.DOCUMENT: [
                "chapter ", "section ", "paragraph", "table of contents",
                "abstract", "introduction", "conclusion", "references"
            ],
        }
        
        self.category_keywords = {
            "technical": ["code", "algorithm", "function", "api", "database"],
            "personal": ["I", "me", "my", "we", "our", "family"],
            "work": ["meeting", "project", "task", "deadline", "client"],
            "education": ["learn", "study", "course", "lecture", "exam"],
            "health": ["doctor", "hospital", "medicine", "fitness"],
            "finance": ["money", "bank", "investment", "budget"],
            "entertainment": ["movie", "music", "game", "book"],
            "travel": ["trip", "flight", "hotel", "vacation"],
        }
    
    def classify_memory(self, memory: Memory) -> Memory:
        content = memory.content or ""
        
        memory.memory_type = self._detect_memory_type(content, memory.memory_type)
        memory.tags = self._extract_tags(content, memory.tags or [])
        memory.categories = self._extract_categories(content, memory.categories or [])
        memory.priority = self._detect_priority(content)
        
        return memory
    
    def _detect_memory_type(self, content: str, current_type: Optional[MemoryType]) -> MemoryType:
        if current_type:
            pass
        
        for mem_type, keywords in self.type_keywords.items():
            for kw in keywords:
                if kw.lower() in content.lower():
                    return mem_type
        
        return MemoryType.TEXT
    
    def _extract_tags(self, content: str, existing_tags: List[str]) -> List[str]:
        tags = set(existing_tags)
        hashtags = re.findall(r'#(\w+)', content)
        tags.update(hashtags)
        return list(tags)[:50]
    
    def _extract_categories(self, content: str, existing_categories: List[str]) -> List[str]:
        categories = set(existing_categories)
        content_lower = content.lower()
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    categories.add(category)
                    break
        
        return list(categories)
    
    def _detect_priority(self, content: str) -> MemoryPriority:
        content_lower = content.lower()
        high_priority_keywords = ["urgent", "important", "critical", "emergency", "deadline"]
        
        for keyword in high_priority_keywords:
            if keyword in content_lower:
                return MemoryPriority.HIGH
        
        if len(content) < 50:
            return MemoryPriority.LOW
        
        return MemoryPriority.MEDIUM

    def classify(self, content: str) -> Memory:
        """Helper for testing classification directly on content string"""
        memory = Memory(
            content=content,
            memory_type=MemoryType.TEXT,
            tags=[],
            categories=[]
        )
        return self.classify_memory(memory)


classifier = MemoryClassifier()