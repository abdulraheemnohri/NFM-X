from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional

from ..storage.database import get_db_session
from ..predictions.engine import PredictiveMemoryEngine

router = APIRouter()

class PredictRequest(BaseModel):
    context_query: Optional[str] = None
    agent_id: Optional[str] = None
    top_k: int = 3

class TrendRequest(BaseModel):
    entity: str
    agent_id: Optional[str] = None

@router.post("/predictions/next")
async def predict_next(request: PredictRequest, db_session=Depends(get_db_session)):
    engine = PredictiveMemoryEngine()
    predictions = await engine.predict_next(
        db_session=db_session, agent_id=request.agent_id,
        context_query=request.context_query, top_k=request.top_k
    )
    return {"predictions": predictions, "context": request.context_query}

@router.post("/predictions/trend")
async def predict_trend(request: TrendRequest, db_session=Depends(get_db_session)):
    engine = PredictiveMemoryEngine()
    trend = await engine.predict_trend(db_session=db_session, entity=request.entity, agent_id=request.agent_id)
    return trend
