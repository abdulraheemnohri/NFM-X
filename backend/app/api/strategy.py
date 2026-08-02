from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from ..storage.database import get_db_session
from ..strategy.engine import StrategyLearningEngine

router = APIRouter()

@router.get("/strategies")
async def get_strategies(agent_id: Optional[str] = None, db_session=Depends(get_db_session)):
    engine = StrategyLearningEngine()
    strategies = await engine.analyze_decision_outcomes(db_session, agent_id)
    return {"strategies": strategies, "count": len(strategies)}

@router.post("/strategies/learn")
async def learn_strategies(agent_id: Optional[str] = None, db_session=Depends(get_db_session)):
    engine = StrategyLearningEngine()
    strategies = await engine.analyze_decision_outcomes(db_session, agent_id)
    created = []
    for s in strategies:
        if s["confidence"] >= 0.7 and s["total_attempts"] >= 5:
            strategy = await engine.create_strategy(
                db_session, s["decision"], s["recommendation"], s["confidence"]
            )
            created.append({"id": strategy.id, "name": strategy.name, "confidence": strategy.confidence})
    return {"analyzed": len(strategies), "created": len(created), "strategies": created}
