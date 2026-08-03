"""
NFM-X Stats API
"""
from fastapi import APIRouter, Depends
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from ..memory.models import Memory, MemoryStatus, MemoryType
from ..storage.database import get_db
from ..config import settings

router = APIRouter(prefix="", tags=["Stats"])


class SystemStats(BaseModel):
    total_memories: int
    active_memories: int
    archived_memories: int
    deleted_memories: int
    merged_memories: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    by_category: Dict[str, int]
    by_tag: Dict[str, int]
    by_author: Dict[str, int]
    by_source: Dict[str, int]
    avg_relevance_score: float
    total_access_count: int
    avg_access_count: float
    created_this_week: int
    created_this_month: int
    vector_store_stats: Dict


@router.get("/", response_model=SystemStats)
async def get_stats(db: AsyncSession = Depends(get_db)) -> SystemStats:
    result = await db.execute(
        select(Memory.status, func.count(Memory.id)).group_by(Memory.status)
    )
    by_status = {k.value if hasattr(k, 'value') else str(k): v for k, v in result.all()}
    
    result = await db.execute(
        select(Memory.memory_type, func.count(Memory.id)).group_by(Memory.memory_type)
    )
    by_type = {k.value if hasattr(k, 'value') else str(k): v for k, v in result.all()}
    
    result = await db.execute(
        select(Memory.categories, func.count(Memory.id)).group_by(Memory.categories)
    )
    by_category: Dict[str, int] = {}
    for categories, count in result.all():
        if categories:
            for category in categories:
                by_category[category] = by_category.get(category, 0) + count
    
    result = await db.execute(
        select(Memory.tags, func.count(Memory.id)).group_by(Memory.tags)
    )
    by_tag: Dict[str, int] = {}
    for tags, count in result.all():
        if tags:
            for tag in tags:
                by_tag[tag] = by_tag.get(tag, 0) + count
    
    result = await db.execute(
        select(Memory.author, func.count(Memory.id)).group_by(Memory.author)
    )
    by_author = {k or "Unknown": v for k, v in result.all()}
    
    result = await db.execute(
        select(Memory.source, func.count(Memory.id)).group_by(Memory.source)
    )
    by_source = {k or "Unknown": v for k, v in result.all()}
    
    result = await db.execute(select(func.avg(Memory.relevance_score)))
    avg_relevance = result.scalar() or 0.0
    
    result = await db.execute(select(func.sum(Memory.access_count)))
    total_access = result.scalar() or 0
    
    result = await db.execute(select(func.count(Memory.id)))
    total_memories = result.scalar() or 0
    avg_access = total_access / total_memories if total_memories > 0 else 0.0
    
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    result = await db.execute(
        select(func.count(Memory.id)).where(Memory.created_at >= one_week_ago)
    )
    created_this_week = result.scalar() or 0
    
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    result = await db.execute(
        select(func.count(Memory.id)).where(Memory.created_at >= one_month_ago)
    )
    created_this_month = result.scalar() or 0
    
    vector_store_stats = {"available": False, "vector_count": 0}
    try:
        from ..embeddings.vector_store import vector_store
        vector_store_stats = {
            "available": vector_store.is_available,
            "vector_count": vector_store.count
        }
    except Exception:
        pass
    
    return SystemStats(
        total_memories=total_memories,
        active_memories=by_status.get("ACTIVE", 0),
        archived_memories=by_status.get("ARCHIVED", 0),
        deleted_memories=by_status.get("DELETED", 0),
        merged_memories=by_status.get("MERGED", 0),
        by_type=by_type,
        by_status=by_status,
        by_category=by_category,
        by_tag=by_tag,
        by_author=by_author,
        by_source=by_source,
        avg_relevance_score=round(float(avg_relevance), 2),
        total_access_count=total_access,
        avg_access_count=round(avg_access, 2),
        created_this_week=created_this_week,
        created_this_month=created_this_month,
        vector_store_stats=vector_store_stats
    )


@router.get("/memory")
async def get_memory_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            func.strftime('%Y-%m-%d', Memory.created_at).label('date'),
            func.count(Memory.id).label('count')
        )
        .group_by('date')
        .order_by('date')
    )
    daily_counts = [{"date": row.date, "count": row.count} for row in result.all()]
    
    result = await db.execute(
        select(
            func.strftime('%Y-%W', Memory.created_at).label('week'),
            func.count(Memory.id).label('count')
        )
        .group_by('week')
        .order_by('week')
    )
    weekly_counts = [{"week": row.week, "count": row.count} for row in result.all()]
    
    result = await db.execute(
        select(
            func.strftime('%Y-%m', Memory.created_at).label('month'),
            func.count(Memory.id).label('count')
        )
        .group_by('month')
        .order_by('month')
    )
    monthly_counts = [{"month": row.month, "count": row.count} for row in result.all()]
    
    result = await db.execute(
        select(
            func.date(Memory.updated_at).label('date'),
            func.sum(Memory.access_count).label('accesses')
        )
        .group_by('date')
        .order_by('date')
    )
    access_stats = [{"date": str(row.date), "accesses": row.accesses or 0} for row in result.all()]
    
    return {
        "daily_counts": daily_counts,
        "weekly_counts": weekly_counts,
        "monthly_counts": monthly_counts,
        "access_stats": access_stats
    }