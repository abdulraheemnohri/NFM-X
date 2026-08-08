"""
NFM-X Context API
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import re
import html

from ..memory.models import Memory
from ..retrieval.engine import RetrievalEngine
from ..storage.database import get_db

router = APIRouter(prefix="", tags=["Context"])


class ContextRequest(BaseModel):
    query: Optional[str] = None
    memory_ids: Optional[List[str]] = None
    max_tokens: int = 4000
    max_memories: int = 10
    min_relevance: float = 0.3


class MemoryContext(BaseModel):
    memory_id: str
    content: str
    title: Optional[str]
    relevance_score: float
    memory_type: str
    tags: List[str]
    categories: List[str]


class ContextResponse(BaseModel):
    context: str
    memories: List[MemoryContext]
    total_tokens: int
    memory_count: int
    query: Optional[str]


def count_tokens(text: str) -> int:
    """Count tokens using a simple but more accurate approach than word splitting."""
    # Basic tokenization that handles common patterns
    # This is more accurate than simple word splitting
    tokens = re.findall(r"\w+|[^\s\w]", text)
    return len(tokens)


def sanitize_content(content: str) -> str:
    """Sanitize content to prevent prompt injection attacks."""
    if not content:
        return content
    
    # Escape XML/HTML special characters to prevent injection in structured prompts
    sanitized = html.escape(content)
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r'<\?xml',
        r'<\?script',
        r'<\?/script',
        r'javascript:',
        r'onerror=',
        r'onload=',
        r'data:',
        r'vbscript:',
    ]
    
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
    
    return sanitized


@router.post("/context", response_model=ContextResponse)
async def build_context(request: ContextRequest, db: AsyncSession = Depends(get_db)) -> ContextResponse:
    retrieval = RetrievalEngine()
    memories, scores = await retrieval.get_context_memories(
        query=request.query,
        memory_ids=request.memory_ids,
        limit=request.max_memories,
        min_relevance=request.min_relevance,
        db_session=db
    )
    
    context_parts = []
    memory_contexts = []
    total_tokens = 0
    processed_memories = []
    
    for memory, score in zip(memories, scores):
        if score < request.min_relevance:
            continue
        
        # Use proper token counting
        content_tokens = count_tokens(memory.content)
        if total_tokens + content_tokens > request.max_tokens:
            break
        
        memory_contexts.append(MemoryContext(
            memory_id=memory.id,
            content=memory.content,
            title=memory.title,
            relevance_score=score,
            memory_type=memory.memory_type.value if memory.memory_type else "TEXT",
            tags=memory.tags or [],
            categories=memory.categories or []
        ))
        total_tokens += content_tokens
        processed_memories.append(memory)
        
        context_parts.append(f"--- Memory {memory.id} ---")
        if memory.title:
            context_parts.append(f"Title: {memory.title}")
        context_parts.append(f"Type: {memory.memory_type.value if memory.memory_type else 'TEXT'}")
        context_parts.append(f"Relevance: {score:.2f}")
        context_parts.append(f"Content: {memory.content}")
        context_parts.append("")
    
    # Batch update access counts to avoid N+1 commits
    for memory in processed_memories:
        memory.access_count += 1
    
    if processed_memories:
        await db.commit()
        # Refresh all memories to get updated access counts
        for memory in processed_memories:
            await db.refresh(memory)
    
    return ContextResponse(
        context="\n".join(context_parts),
        memories=memory_contexts,
        total_tokens=total_tokens,
        memory_count=len(memory_contexts),
        query=request.query
    )


@router.post("/context/for-prompt")
async def build_prompt_context(request: ContextRequest, db: AsyncSession = Depends(get_db)):
    retrieval = RetrievalEngine()
    memories, scores = await retrieval.get_context_memories(
        query=request.query,
        memory_ids=request.memory_ids,
        limit=request.max_memories,
        min_relevance=request.min_relevance,
        db_session=db
    )
    
    context_string = """You are an AI assistant with access to the following relevant memories.
Use this information to provide accurate and context-aware responses.
If the information in memories conflicts, note the conflict in your response.

<context>"""
    
    processed_memories = []
    for memory, score in zip(memories, scores):
        if score < request.min_relevance:
            continue
        
        # Sanitize content to prevent prompt injection
        sanitized_title = sanitize_content(memory.title or 'Untitled')
        sanitized_content = sanitize_content(memory.content)
        
        context_string += f'\n<memory id="{memory.id}" relevance="{score:.2f}">\n'
        context_string += f"  <title>{sanitized_title}</title>\n"
        context_string += f"  <type>{memory.memory_type.value if memory.memory_type else 'TEXT'}</type>\n"
        context_string += f"  <content>{sanitized_content}</content>\n"
        context_string += f"</memory>\n"
        processed_memories.append(memory)
    
    context_string += "\n</context>\n"
    
    # Batch update access counts to avoid N+1 commits
    for memory in processed_memories:
        memory.access_count += 1
    
    if processed_memories:
        await db.commit()
    
    return {
        "prompt": context_string,
        "memory_count": len(processed_memories)
    }