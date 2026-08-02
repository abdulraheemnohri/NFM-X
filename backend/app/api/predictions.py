"""NFM-X V3 Predictions API
Enhanced with confidence intervals"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.app.predictions.engine import PredictionEngineV3, PredictionResult

router = APIRouter(prefix="/api/v1/predictions", tags=["Predictions"])


# Initialize prediction engine
prediction_engine = PredictionEngineV3()


class PredictionRequest(BaseModel):
    query: str
    pattern_ids: Optional[List[str]] = None
    base_confidence: Optional[float] = None


class PredictionResponse(BaseModel):
    prediction_id: str
    query: str
    prediction_value: Any
    confidence: float
    confidence_lower: float
    confidence_upper: float
    pattern_variance: float
    patterns_used: List[str]
    created_at: datetime
    metadata: Dict[str, Any]


@router.post("/", response_model=PredictionResponse, status_code=201)
async def create_prediction(request: PredictionRequest):
    """
    Create a new prediction with confidence intervals
    
    Request body:
    - query: The prediction query
    - pattern_ids: Optional list of pattern IDs to use
    - base_confidence: Optional base confidence score (0.0-1.0)
    
    Returns:
    - prediction_id: Unique identifier for the prediction
    - prediction_value: The predicted value
    - confidence: Base confidence score
    - confidence_lower: Lower bound of confidence interval
    - confidence_upper: Upper bound of confidence interval
    - pattern_variance: Variance of underlying patterns
    - patterns_used: List of pattern IDs used
    """
    try:
        result = prediction_engine.predict(
            query=request.query,
            base_confidence=request.base_confidence,
            pattern_ids=request.pattern_ids
        )
        
        return PredictionResponse(
            prediction_id=result.prediction_id,
            query=result.query,
            prediction_value=result.prediction_value,
            confidence=result.confidence,
            confidence_lower=result.confidence_lower,
            confidence_upper=result.confidence_upper,
            pattern_variance=result.pattern_variance,
            patterns_used=result.patterns_used,
            created_at=result.created_at,
            metadata=result.metadata
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[PredictionResponse])
async def list_predictions(limit: int = 100):
    """
    List recent predictions
    """
    history = prediction_engine.get_prediction_history(limit)
    return [
        PredictionResponse(
            prediction_id=p.prediction_id,
            query=p.query,
            prediction_value=p.prediction_value,
            confidence=p.confidence,
            confidence_lower=p.confidence_lower,
            confidence_upper=p.confidence_upper,
            pattern_variance=p.pattern_variance,
            patterns_used=p.patterns_used,
            created_at=p.created_at,
            metadata=p.metadata
        )
        for p in history
    ]


@router.get("/patterns", response_model=List[Dict])
async def list_patterns():
    """
    List all available patterns for predictions
    """
    return prediction_engine.get_patterns()


@router.post("/patterns/{pattern_id}/accuracy", status_code=200)
async def record_pattern_accuracy(pattern_id: str, accuracy: float):
    """
    Record accuracy for a pattern to improve confidence calculations
    """
    prediction_engine.record_pattern_accuracy(pattern_id, accuracy)
    return {"message": f"Accuracy recorded for pattern {pattern_id}"}