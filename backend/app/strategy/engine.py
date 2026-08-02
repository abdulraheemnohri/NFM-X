from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from ..memory.models import Memory, MemorySkill, MemoryType, MemoryStatus

class StrategyLearningEngine:
    """Learn WHEN to use skills (decision policies), not just HOW."""

    async def analyze_decision_outcomes(self, db_session: AsyncSession,
                                        agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Analyze which decisions led to success vs failure."""
        stmt = select(Memory).where(Memory.type == MemoryType.DECISION, Memory.status == MemoryStatus.ACTIVE)
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        result = await db_session.execute(stmt)
        decisions = result.scalars().all()

        # Find subsequent success/failure memories for each decision
        strategies = defaultdict(lambda: {"successes": 0, "failures": 0, "total": 0, "contexts": []})

        for decision in decisions:
            # Look for success/failure within next 10 memories
            stmt2 = select(Memory).where(
                Memory.agent_id == decision.agent_id,
                Memory.created_at > decision.created_at,
                Memory.type.in_([MemoryType.SUCCESS, MemoryType.FAILURE])
            ).order_by(Memory.created_at).limit(10)
            result2 = await db_session.execute(stmt2)
            outcomes = result2.scalars().all()

            decision_key = decision.content[:100]
            for outcome in outcomes:
                if (outcome.created_at - decision.created_at).total_seconds() < 3600:  # Within 1 hour
                    strategies[decision_key]["total"] += 1
                    strategies[decision_key]["contexts"].append({
                        "decision_id": decision.id,
                        "outcome_id": outcome.id,
                        "outcome_type": outcome.type.value,
                        "time_delta_sec": (outcome.created_at - decision.created_at).total_seconds()
                    })
                    if outcome.type == MemoryType.SUCCESS:
                        strategies[decision_key]["successes"] += 1
                    else:
                        strategies[decision_key]["failures"] += 1

        # Build strategy recommendations
        recommendations = []
        for decision_text, data in strategies.items():
            if data["total"] >= 3:
                success_rate = data["successes"] / data["total"]
                if success_rate >= 0.7:
                    recommendation = "recommended"
                elif success_rate <= 0.3:
                    recommendation = "avoid"
                else:
                    recommendation = "conditional"

                recommendations.append({
                    "decision": decision_text,
                    "success_rate": round(success_rate, 3),
                    "total_attempts": data["total"],
                    "successes": data["successes"],
                    "failures": data["failures"],
                    "recommendation": recommendation,
                    "confidence": round(min(0.95, 0.3 + success_rate * 0.6), 3)
                })

        recommendations.sort(key=lambda x: x["success_rate"], reverse=True)
        return recommendations

    async def create_strategy(self, db_session: AsyncSession, decision_pattern: str,
                              recommendation: str, confidence: float) -> MemorySkill:
        """Create a high-level strategy from analyzed patterns."""
        strategy = MemorySkill(
            id=str(uuid.uuid4()),
            name=f"Strategy: {decision_pattern[:50]}",
            description=f"Learned strategy: {recommendation} | Confidence: {confidence}",
            source_procedure_ids=[],
            success_rate=confidence,
            execution_count=0,
            confidence=confidence,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(strategy)
        await db_session.commit()
        return strategy
