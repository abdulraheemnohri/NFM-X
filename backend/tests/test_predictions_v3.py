"""Tests for NFM-X V3 Predictions with confidence intervals"""

import pytest
from backend.app.predictions.confidence import ConfidenceCalculator, PatternData


class TestPredictionsV3:
    def test_confidence_calculator_init(self):
        """Test confidence calculator initialization"""
        calculator = ConfidenceCalculator(default_confidence_level=0.95)
        assert calculator.default_confidence_level == 0.95
    
    def test_calculate_confidence_intervals_basic(self):
        """Test basic confidence interval calculation"""
        calculator = ConfidenceCalculator()
        
        pattern_data = [
            PatternData(pattern_id="p1", weight=0.5, historical_accuracy=0.9, variance=0.1),
            PatternData(pattern_id="p2", weight=0.5, historical_accuracy=0.8, variance=0.15)
        ]
        
        lower, upper = calculator.calculate_confidence_intervals(
            base_confidence=0.85,
            pattern_data=pattern_data
        )
        
        assert lower < upper
        assert 0.0 <= lower <= 1.0
        assert 0.0 <= upper <= 1.0
    
    def test_calculate_confidence_intervals_no_patterns(self):
        """Test confidence interval with no pattern data"""
        calculator = ConfidenceCalculator()
        
        lower, upper = calculator.calculate_confidence_intervals(
            base_confidence=0.8,
            pattern_data=[]
        )
        
        assert lower == pytest.approx(0.75, abs=0.01)
        assert upper == pytest.approx(0.85, abs=0.01)
    
    def test_calculate_pattern_variance(self):
        """Test pattern variance calculation"""
        calculator = ConfidenceCalculator()
        
        accuracies = [0.8, 0.85, 0.9, 0.95, 0.9]
        variance = calculator.calculate_pattern_variance(accuracies)
        
        assert variance >= 0
    
    def test_get_z_score(self):
        """Test z-score retrieval"""
        calculator = ConfidenceCalculator()
        
        assert calculator._get_z_score(0.90) == 1.645
        assert calculator._get_z_score(0.95) == 1.960
        assert calculator._get_z_score(0.99) == 2.576
        assert calculator._get_z_score(0.999) == 3.291
        assert calculator._get_z_score(0.5) == 1.960  # Default
    
    def test_create_prediction(self):
        """Test prediction creation with confidence intervals"""
        calculator = ConfidenceCalculator()
        
        pattern_data = [
            PatternData(pattern_id="p1", weight=1.0, historical_accuracy=0.9, variance=0.05)
        ]
        
        prediction = calculator.create_prediction(
            prediction_id="pred_1",
            prediction_value=42.0,
            base_confidence=0.9,
            pattern_data=pattern_data
        )
        
        assert prediction.prediction_id == "pred_1"
        assert prediction.prediction_value == 42.0
        assert prediction.confidence == 0.9
        assert prediction.confidence_lower < prediction.confidence_upper
        assert prediction.pattern_variance == 0.05