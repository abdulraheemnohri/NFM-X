from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..storage.database import get_db_session
from ..causal.advanced import AdvancedCausalEngine

router = APIRouter()

class CausalChainRequest(BaseModel):
    cause: str
    effect: str
    max_hops: int = 5

class CounterfactualRequest(BaseModel):
    remove_event: str
    agent_id: Optional[str] = None

@router.post("/causal/chain")
async def find_causal_chain(request: CausalChainRequest, db_session=Depends(get_db_session)):
    engine = AdvancedCausalEngine()
    chain = await engine.find_causal_chain(db_session, request.cause, request.effect, request.max_hops)
    if not chain:
        return {"cause": request.cause, "effect": request.effect, "chain": None, "found": False}
    return {"cause": request.cause, "effect": request.effect, "chain": chain, "hops": len(chain), "found": True}

@router.post("/causal/counterfactual")
async def counterfactual(request: CounterfactualRequest, db_session=Depends(get_db_session)):
    engine = AdvancedCausalEngine()
    return await engine.counterfactual_query(db_session, request.remove_event, request.agent_id)
