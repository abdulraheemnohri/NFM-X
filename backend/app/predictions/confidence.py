"""NFM-X V3 Predictive Confidence Intervals
Calculates confidence intervals for predictions based on pattern variance"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math
import statistics
import logging

logger = logging.getLogger(__name__)


@dataclass
class Prediction:
    """Represents a prediction with confidence intervals"""
    prediction_id: str
    prediction_value: float
    confidence: float  # 0.0 to 1.0
    confidence_lower: float  # Lower bound of confidence interval
    confidence_upper: float  # Upper bound of confidence interval
    pattern_variance: float  # Variance of underlying patterns
    created_at: datetime = datetime.utcnow()
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict:
        return {
            "prediction_id": self.prediction_id,
            "prediction_value": self.prediction_value,
            "confidence": self.confidence,
            "confidence_lower": self.confidence_lower,
            "confidence_upper": self.confidence_upper,
            "pattern_variance": self.pattern_variance,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class PatternData:
    """Data about patterns used for prediction"""
    pattern_id: str
    weight: float
    historical_accuracy: float
    variance: float


class ConfidenceCalculator:
    """Calculates confidence intervals for predictions"""
    
    def __init__(self, default_confidence_level: float = 0.95):
        """
        Initialize with default confidence level (e.g., 0.95 for 95% CI)
        """
        self.default_confidence_level = default_confidence_level
    
    def calculate_confidence_intervals(
        self,
        base_confidence: float,
        pattern_data: List[PatternData],
        confidence_level: Optional[float] = None
    ) -> Tuple[float, float]:
        """
        Calculate confidence intervals based on pattern variance
        
        Args:
            base_confidence: Base confidence score (0.0 to 1.0)
            pattern_data: List of pattern data with variances
            confidence_level: Confidence level for interval (default: 0.95)
            
        Returns:
            Tuple of (confidence_lower, confidence_upper)
        """
        if confidence_level is None:
            confidence_level = self.default_confidence_level
        
        if not pattern_data:
            # No pattern data, return base confidence with small interval
            margin = 0.05
            lower = max(0.0, base_confidence - margin)
            upper = min(1.0, base_confidence + margin)
            return lower, upper
        
        # Calculate weighted average variance
        total_weight = sum(p.weight for p in pattern_data)
        if total_weight == 0:
            total_weight = 1.0
        
        weighted_variances = [
            p.variance * (p.weight / total_weight) for p in pattern_data
        ]
        avg_variance = sum(weighted_variances)
        std_dev = math.sqrt(avg_variance)
        
        # Calculate z-score for the confidence level
        # For 95% CI, z ≈ 1.96; for 99% CI, z ≈ 2.576
        z_score = self._get_z_score(confidence_level)
        
        # Margin of error
        margin = z_score * std_dev
        
        # Calculate interval bounds
        lower = max(0.0, base_confidence - margin)
        upper = min(1.0, base_confidence + margin)
        
        logger.debug(f"Confidence interval: base={base_confidence}, lower={lower}, upper={upper}")
        
        return lower, upper
    
    def _get_z_score(self, confidence_level: float) -> float:
        """Get z-score for a given confidence level"""
        # Common z-scores for different confidence levels
        z_scores = {
            0.90: 1.645,
            0.95: 1.960,
            0.99: 2.576,
            0.999: 3.291
        }
        return z_scores.get(confidence_level, 1.960)  # Default to 95%
    
    def calculate_pattern_variance(
        self,
        pattern_accuracies: List[float]
    ) -> float:
        """
        Calculate variance from historical pattern accuracies
        """
        if len(pattern_accuracies) < 2:
            return 0.0
        
        mean = statistics.mean(pattern_accuracies)
        variance = statistics.variance(pattern_accuracies)
        return variance
    
    def create_prediction(
        self,
        prediction_id: str,
        prediction_value: float,
        base_confidence: float,
        pattern_data: List[PatternData],
        metadata: Optional[Dict] = None
    ) -> Prediction:
        """
        Create a prediction with confidence intervals
        """
        confidence_lower, confidence_upper = self.calculate_confidence_intervals(
            base_confidence, pattern_data
        )
        
        # Calculate average pattern variance
        if pattern_data:
            pattern_variance = sum(p.variance for p in pattern_data) / len(pattern_data)
        else:
            pattern_variance = 0.0
        
        return Prediction(
            prediction_id=prediction_id,
            prediction_value=prediction_value,
            confidence=base_confidence,
            confidence_lower=confidence_lower,
            confidence_upper=confidence_upper,
            pattern_variance=pattern_variance,
            metadata=metadata or {}
        )