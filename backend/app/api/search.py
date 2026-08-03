"""
NFM-X Search API
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, desc

import time
from ..memory.models import Memory, MemoryStatus, MemoryType
from ..retrieval.engine import RetrievalEngine
from ..storage.database import get_db

router = APIRouter(prefix="", tags=["Search"])
retrieval_engine = RetrievalEngine()


class SearchResult(BaseModel):
    id: str
    title: Optional[str]
    content_preview: str
    memory_type: MemoryType
    status: MemoryStatus
    relevance_score: float
    tags: List[str]
    categories: List[str]
    created_at: str
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int
    search_type: str
    execution_time: float


@router.get("/", response_model=SearchResponse)
async def keyword_search(
    query: str = Query(...),
    limit: int = Query(default=10, ge=1, le=100),
    memory_type: Optional[MemoryType] = Query(None),
    status: Optional[MemoryStatus] = Query(None),
    tags: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> SearchResponse:

    start_time = time.time()
    
    search_query = select(Memory)
    filters = []
    
    if status:
        filters.append(Memory.status == status)
    else:
        filters.append(Memory.status == MemoryStatus.ACTIVE)
    
    if memory_type:
        filters.append(Memory.memory_type == memory_type)
    
    if tags:
        for tag in tags:
            filters.append(Memory.tags.contains([tag]))
    
    if query:
        search_pattern = f"%{query}%"
        filters.append(or_(
            Memory.content.ilike(search_pattern),
            Memory.title.ilike(search_pattern),
            Memory.description.ilike(search_pattern)
        ))
    
    if filters:
        search_query = search_query.where(and_(*filters))
    
    search_query = search_query.order_by(desc(Memory.relevance_score), desc(Memory.access_count)).limit(limit)
    result = await db.execute(search_query)
    memories = result.scalars().all()
    
    for memory in memories:
        memory.access_count += 1
    await db.commit()
    
    results = []
    for memory in memories:
        content_preview = memory.content[:200] + "..." if len(memory.content) > 200 else memory.content
        results.append(SearchResult(
            id=memory.id,
            title=memory.title,
            content_preview=content_preview,
            memory_type=memory.memory_type,
            status=memory.status,
            relevance_score=memory.relevance_score,
            tags=memory.tags or [],
            categories=memory.categories or [],
            created_at=memory.created_at.isoformat() if memory.created_at else ""
        ))
    
    return SearchResponse(
        query=query,
        results=results,
        total=len(results),
        search_type="keyword",
        execution_time=time.time() - start_time
    )


@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    query: str,
    limit: int = 10,
    memory_type: Optional[MemoryType] = None,
    status: Optional[MemoryStatus] = None,
    db: AsyncSession = Depends(get_db)
) -> SearchResponse:
    import time
    start_time = time.time()
    
    retrieval = retrieval_engine
    results, total = await retrieval.semantic_search(
        query=query,
        limit=limit,
        memory_type=memory_type,
        status=status,
        db_session=db
    )
    
    search_results = []
    for memory, score in results:
        content_preview = memory.content[:200] + "..." if len(memory.content) > 200 else memory.content
        search_results.append(SearchResult(
            id=memory.id,
            title=memory.title,
            content_preview=content_preview,
            memory_type=memory.memory_type,
            status=memory.status,
            relevance_score=score,
            tags=memory.tags or [],
            categories=memory.categories or [],
            created_at=memory.created_at.isoformat() if memory.created_at else ""
        ))
    
    return SearchResponse(
        query=query,
        results=search_results,
        total=total,
        search_type="semantic",
        execution_time=time.time() - start_time
    )


@router.post("/hybrid", response_model=SearchResponse)
async def hybrid_search(
    query: str,
    limit: int = 10,
    memory_type: Optional[MemoryType] = None,
    status: Optional[MemoryStatus] = None,
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.3,
    db: AsyncSession = Depends(get_db)
) -> SearchResponse:
    import time
    start_time = time.time()
    
    retrieval = retrieval_engine
    results, total = await retrieval.hybrid_search(
        query=query,
        limit=limit,
        memory_type=memory_type,
        status=status,
        semantic_weight=semantic_weight,
        keyword_weight=keyword_weight,
        db_session=db
    )
    
    search_results = []
    for memory, score in results:
        content_preview = memory.content[:200] + "..." if len(memory.content) > 200 else memory.content
        search_results.append(SearchResult(
            id=memory.id,
            title=memory.title,
            content_preview=content_preview,
            memory_type=memory.memory_type,
            status=memory.status,
            relevance_score=score,
            tags=memory.tags or [],
            categories=memory.categories or [],
            created_at=memory.created_at.isoformat() if memory.created_at else ""
        ))
    
    return SearchResponse(
        query=query,
        results=search_results,
        total=total,
        search_type="hybrid",
        execution_time=time.time() - start_time
    )


@router.get("/{memory_id}/similar", response_model=SearchResponse)
async def find_similar(memory_id: str, limit: int = 10, db: AsyncSession = Depends(get_db)) -> SearchResponse:
    import time
    start_time = time.time()
    
    retrieval = retrieval_engine
    results, total = await retrieval.find_similar(memory_id=memory_id, limit=limit, db_session=db)
    
    search_results = []
    for memory, score in results:
        content_preview = memory.content[:200] + "..." if len(memory.content) > 200 else memory.content
        search_results.append(SearchResult(
            id=memory.id,
            title=memory.title,
            content_preview=content_preview,
            memory_type=memory.memory_type,
            status=memory.status,
            relevance_score=score,
            tags=memory.tags or [],
            categories=memory.categories or [],
            created_at=memory.created_at.isoformat() if memory.created_at else ""
        ))
    
    return SearchResponse(
        query=f"similar to {memory_id}",
        results=search_results,
        total=total,
        search_type="similar",
        execution_time=time.time() - start_time
    )


import time