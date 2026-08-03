"""
NFM-X Stats API
"""
from fastapi import APIRouter, Depends
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, cast, Date, String

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


def extract_date(date_value) -> str:
    """Extract date string from datetime in a database-agnostic way."""
    if date_value is None:
        return ""
    return date_value.strftime('%Y-%m-%d")


def extract_week(date_value) -> str:
    """Extract week string from datetime in a database-agnostic way."""
    if date_value is None:
        return ""
    return date_value.strftime('%Y-%W")


def extract_month(date_value) -> str:
    """Extract month string from datetime in a database-agnostic way."""
    if date_value is None:
        return ""
    return date_value.strftime('%Y-%m")


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
    # Database-agnostic daily counts using in-memory processing
    result = await db.execute(
        select(Memory.created_at).order_by(Memory.created_at)
    )
    all_memories = result.scalars().all()
    
    daily_counts = []
    daily_map = {}
    for mem in all_memories:
        if mem and mem.created_at:
            date_str = extract_date(mem.created_at)
            daily_map[date_str] = daily_map.get(date_str, 0) + 1
    
    for date_str, count in sorted(daily_map.items()):
        daily_counts.append({"date": date_str, "count": count})
    
    # Weekly counts
    weekly_counts = []
    weekly_map = {}
    for mem in all_memories:
        if mem and mem.created_at:
            week_str = extract_week(mem.created_at)
            weekly_map[week_str] = weekly_map.get(week_str, 0) + 1
    
    for week_str, count in sorted(weekly_map.items()):
        weekly_counts.append({"week": week_str, "count": count})
    
    # Monthly counts
    monthly_counts = []
    monthly_map = {}
    for mem in all_memories:
        if mem and mem.created_at:
            month_str = extract_month(mem.created_at)
            monthly_map[month_str] = monthly_map.get(month_str, 0) + 1
    
    for month_str, count in sorted(monthly_map.items()):
        monthly_counts.append({"month": month_str, "count": count})
    
    # Access stats
    result = await db.execute(
        select(Memory.updated_at, Memory.access_count).order_by(Memory.updated_at)
    )
    access_rows = result.all()
    
    access_stats = []
    access_map = {}
    for row in access_rows:
        if row.updated_at:
            date_str = extract_date(row.updated_at)
            access_map[date_str] = access_map.get(date_str, 0) + (row.access_count or 0)
    
    for date_str, accesses in sorted(access_map.items()):
        access_stats.append({"date": date_str, "accesses": accesses})
    
    return {
        "daily_counts": daily_counts,
        "weekly_counts": weekly_counts,
        "monthly_counts": monthly_counts,
        "access_stats": access_stats
    }