"""NFM-X V3 Predictions Engine
Enhanced with confidence intervals and pattern-based forecasting"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
import uuid
import logging

from backend.app.predictions.confidence import ConfidenceCalculator, Prediction, PatternData

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Complete prediction result with confidence intervals"""
    prediction_id: str
    query: str
    prediction_value: Any
    confidence: float
    confidence_lower: float
    confidence_upper: float
    pattern_variance: float
    patterns_used: List[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "query": self.query,
            "prediction_value": self.prediction_value,
            "confidence": self.confidence,
            "confidence_lower": self.confidence_lower,
            "confidence_upper": self.confidence_upper,
            "pattern_variance": self.pattern_variance,
            "patterns_used": self.patterns_used,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


class PredictionEngineV3:
    """V3 Prediction Engine with confidence intervals"""
    
    def __init__(self):
        self.confidence_calculator = ConfidenceCalculator()
        self.pattern_store: Dict[str, Dict] = {}  # pattern_id -> pattern data
        self.prediction_history: List[PredictionResult] = []
        self.pattern_accuracy: Dict[str, List[float]] = {}  # Track accuracy for variance calculation
    
    def add_pattern(self, pattern_id: str, pattern_data: Dict) -> None:
        """Add a pattern to the store"""
        self.pattern_store[pattern_id] = pattern_data
        logger.info(f"Added pattern: {pattern_id}")
    
    def record_pattern_accuracy(self, pattern_id: str, accuracy: float) -> None:
        """Record accuracy for a pattern to calculate variance"""
        if pattern_id not in self.pattern_accuracy:
            self.pattern_accuracy[pattern_id] = []
        self.pattern_accuracy[pattern_id].append(accuracy)
        
        # Keep only last 100 accuracy values
        if len(self.pattern_accuracy[pattern_id]) > 100:
            self.pattern_accuracy[pattern_id] = self.pattern_accuracy[pattern_id][-100:]
    
    def predict(
        self,
        query: str,
        base_confidence: Optional[float] = None,
        pattern_ids: Optional[List[str]] = None
    ) -> PredictionResult:
        """
        Make a prediction with confidence intervals
        
        Args:
            query: The prediction query
            base_confidence: Base confidence score (0.0-1.0), auto-calculated if None
            pattern_ids: Specific patterns to use, uses all if None
            
        Returns:
            PredictionResult with confidence intervals
        """
        # Select patterns to use
        if pattern_ids:
            patterns_to_use = [
                self.pattern_store[pid] for pid in pattern_ids
                if pid in self.pattern_store
            ]
        else:
            patterns_to_use = list(self.pattern_store.values())
        
        if not patterns_to_use:
            raise ValueError("No patterns available for prediction")
        
        # Calculate base confidence if not provided
        if base_confidence is None:
            base_confidence = self._calculate_base_confidence(patterns_to_use)
        
        # Create pattern data for confidence calculation
        pattern_data_list = []
        for pattern in patterns_to_use:
            pid = next(k for k, v in self.pattern_store.items() if v == pattern)
            accuracy_history = self.pattern_accuracy.get(pid, [0.8])
            variance = self.confidence_calculator.calculate_pattern_variance(accuracy_history)
            pattern_data_list.append(PatternData(
                pattern_id=pid,
                weight=1.0 / len(patterns_to_use),
                historical_accuracy=accuracy_history[-1] if accuracy_history else 0.8,
                variance=variance
            ))
        
        # Create prediction with confidence intervals
        prediction_id = str(uuid.uuid4())
        prediction = self.confidence_calculator.create_prediction(
            prediction_id=prediction_id,
            prediction_value=self._generate_prediction_value(patterns_to_use, query),
            base_confidence=base_confidence,
            pattern_data=pattern_data_list,
            metadata={"query": query, "pattern_count": len(patterns_to_use)}
        )
        
        # Create result
        result = PredictionResult(
            prediction_id=prediction_id,
            query=query,
            prediction_value=prediction.prediction_value,
            confidence=prediction.confidence,
            confidence_lower=prediction.confidence_lower,
            confidence_upper=prediction.confidence_upper,
            pattern_variance=prediction.pattern_variance,
            patterns_used=[p.pattern_id for p in pattern_data_list]
        )
        
        self.prediction_history.append(result)
        logger.info(f"Created prediction: {prediction_id} with confidence: {prediction.confidence}")
        
        return result
    
    def _calculate_base_confidence(self, patterns: List[Dict]) -> float:
        """Calculate base confidence from pattern weights"""
        if not patterns:
            return 0.5
        
        # Simple average of pattern confidence
        total = 0.0
        count = 0
        for pattern in patterns:
            conf = pattern.get("confidence", 0.8)
            total += conf
            count += 1
        
        return total / count if count > 0 else 0.5
    
    def _generate_prediction_value(self, patterns: List[Dict], query: str) -> Any:
        """Generate a prediction value based on patterns"""
        # Simple implementation: return the query as prediction for now
        # In a real implementation, this would use ML models
        return f"Prediction for: {query}"
    
    def get_prediction_history(self, limit: int = 100) -> List[PredictionResult]:
        """Get prediction history"""
        return self.prediction_history[-limit:]
    
    def get_patterns(self) -> List[Dict]:
        """Get all patterns"""
        return list(self.pattern_store.values())


# Alias for backward compatibility with backend/tests/
PredictiveMemoryEngine = PredictionEngineV3