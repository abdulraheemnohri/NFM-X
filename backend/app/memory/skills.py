from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from ..memory.models import Memory, MemoryProcedure, MemorySkill, MemoryType, MemoryStatus

class SkillLearningEngine:
    async def learn_skill_from_procedure(self, db_session: AsyncSession, procedure_name: str,
                                          agent_id: Optional[str] = None) -> Optional[MemorySkill]:
        stmt = select(MemoryProcedure).where(MemoryProcedure.name == procedure_name)
        result = await db_session.execute(stmt)
        procedures = result.scalars().all()
        if not procedures:
            return None
        total = len(procedures)
        successes = sum(1 for p in procedures if p.success_count > 0)
        success_rate = successes / total if total > 0 else 0
        if success_rate < 0.7 or total < 3:
            return None
        skill = MemorySkill(
            id=str(uuid.uuid4()), name=procedure_name,
            description=f"Skill from {total} executions ({success_rate:.0%} success)",
            source_procedure_ids=[p.id for p in procedures],
            success_rate=success_rate, execution_count=total,
            confidence=min(0.95, 0.5 + success_rate * 0.4),
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(skill)
        await db_session.commit()
        return skill

    async def evaluate_procedure_execution(self, db_session, procedure_id: str, success: bool,
                                            error_message: Optional[str] = None):
        result = await db_session.execute(select(MemoryProcedure).where(MemoryProcedure.id == procedure_id))
        proc = result.scalar_one_or_none()
        if not proc:
            raise ValueError(f"Procedure {procedure_id} not found")
        proc.execution_count += 1
        if success:
            proc.success_count += 1
        else:
            proc.failure_count += 1
            current = proc.metadata.get("failure_log", [])
            current.append({"timestamp": datetime.now(timezone.utc).isoformat(), "error": error_message})
            proc.metadata["failure_log"] = current
        proc.success_rate = proc.success_count / proc.execution_count
        proc.last_executed = datetime.now(timezone.utc)
        await db_session.commit()
        return proc
