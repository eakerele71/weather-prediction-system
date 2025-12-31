"""Accuracy tracking system for validating weather predictions"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from statistics import mean
import math
from app.models import WeatherData, Forecast, AccuracyMetrics, Location

logger = logging.getLogger(__name__)


@dataclass
class PredictionOutcome:
    """Represents a prediction and its actual outcome for accuracy calculation"""
    forecast: Forecast
    actual_weather: WeatherData
    accuracy_score: float
    temperature_error: float
    precipitation_error: float
    condition_match: bool


class AccuracyCalculator:
    """Calculates various accuracy metrics for weather predictions"""
    
    def __init__(self):
        """Initialize accuracy calculator"""
        self.temperature_weight = 0.4
        self.precipitation_weight = 0.3
        self.condition_weight = 0.3

    def calculate_temperature_accuracy(self, predicted: float, actual: float) -> Tuple[float, float]:
        """Calculate temperature prediction accuracy
        
        Args:
            predicted: Predicted temperature
            actual: Actual temperature
            
        Returns:
            Tuple of (accuracy_score, absolute_error)
        """
        absolute_error = abs(predicted - actual)
        
        # Temperature accuracy: 100% if within 1°C, decreasing linearly to 0% at 10°C error
        max_error = 10.0
        accuracy = max(0.0, 1.0 - (absolute_error / max_error))
        
        return accuracy, absolute_error

    def calculate_precipitation_accuracy(self, predicted_prob: float, actual_precip: float) -> Tuple[float, float]:
        """Calculate precipitation prediction accuracy
        
        Args:
            predicted_prob: Predicted precipitation probability (0-1)
            actual_precip: Actual precipitation amount in mm
            
        Returns:
            Tuple of (accuracy_score, probability_error)
        """
        # Convert actual precipitation to probability (simplified)
        # 0mm = 0% probability, 10mm+ = 100% probability
        actual_prob = min(1.0, actual_precip / 10.0)
        
        probability_error = abs(predicted_prob - actual_prob)
        
        # Precipitation accuracy: 100% if within 0.1 probability, decreasing to 0% at 1.0 error
        accuracy = max(0.0, 1.0 - probability_error)
        
        return accuracy, probability_error

    def calculate_condition_accuracy(self, predicted: str, actual: str) -> Tuple[float, bool]:
        """Calculate weather condition prediction accuracy
        
        Args:
            predicted: Predicted weather condition
            actual: Actual weather condition
            
        Returns:
            Tuple of (accuracy_score, exact_match)
        """
        exact_match = predicted.lower() == actual.lower()
        
        # Condition mapping for partial matches
        condition_groups = {
            'clear': ['clear', 'sunny'],
            'cloudy': ['cloudy', 'partly cloudy', 'overcast'],
            'rainy': ['rainy', 'drizzle', 'showers'],
            'stormy': ['stormy', 'thunderstorm', 'severe'],
            'snowy': ['snowy', 'snow', 'blizzard']
        }
        
        if exact_match:
            return 1.0, True
        
        # Check for partial matches within same group
        predicted_lower = predicted.lower()
        actual_lower = actual.lower()
        
        for group_conditions in condition_groups.values():
            if predicted_lower in group_conditions and actual_lower in group_conditions:
                return 0.7, False  # Partial match within same group
        
        return 0.0, False

    def calculate_overall_accuracy(self, temperature_acc: float, precipitation_acc: float, 
                                 condition_acc: float) -> float:
        """Calculate weighted overall accuracy score
        
        Args:
            temperature_acc: Temperature accuracy (0-1)
            precipitation_acc: Precipitation accuracy (0-1)
            condition_acc: Condition accuracy (0-1)
            
        Returns:
            Overall accuracy score (0-1)
        """
        return (temperature_acc * self.temperature_weight + 
                precipitation_acc * self.precipitation_weight + 
                condition_acc * self.condition_weight)

    def calculate_mae(self, errors: List[float]) -> float:
        """Calculate Mean Absolute Error
        
        Args:
            errors: List of absolute errors
            
        Returns:
            Mean absolute error
        """
        if not errors:
            return 0.0
        return mean(errors)

    def calculate_rmse(self, errors: List[float]) -> float:
        """Calculate Root Mean Square Error
        
        Args:
            errors: List of absolute errors
            
        Returns:
            Root mean square error
        """
        if not errors:
            return 0.0
        
        mse = mean([error ** 2 for error in errors])
        return math.sqrt(mse)


class AccuracyTracker:
    """Tracks and analyzes prediction accuracy over time"""
    
    def __init__(self, retention_days: int = 90):
        """Initialize accuracy tracker
        
        Args:
            retention_days: Number of days to retain accuracy history
        """
        self.retention_days = retention_days
        self.calculator = AccuracyCalculator()
        self.prediction_outcomes: List[PredictionOutcome] = []
        self.accuracy_history: List[AccuracyMetrics] = []
        
        # Accuracy alert thresholds
        self.accuracy_alert_threshold = 0.6  # Alert if accuracy drops below 60%
        self.min_predictions_for_alert = 10   # Minimum predictions before triggering alerts

    def compare_prediction_to_actual(self, forecast: Forecast, actual_weather: WeatherData) -> PredictionOutcome:
        """Compare a forecast to actual weather and calculate accuracy
        
        Args:
            forecast: Weather forecast
            actual_weather: Actual weather data
            
        Returns:
            PredictionOutcome with accuracy metrics
        """
        # Calculate individual accuracy components
        temp_accuracy, temp_error = self.calculator.calculate_temperature_accuracy(
            forecast.predicted_temperature_high, actual_weather.temperature
        )
        
        precip_accuracy, precip_error = self.calculator.calculate_precipitation_accuracy(
            forecast.precipitation_probability, actual_weather.precipitation
        )
        
        condition_accuracy, condition_match = self.calculator.calculate_condition_accuracy(
            forecast.weather_condition, actual_weather.weather_condition
        )
        
        # Calculate overall accuracy
        overall_accuracy = self.calculator.calculate_overall_accuracy(
            temp_accuracy, precip_accuracy, condition_accuracy
        )
        
        return PredictionOutcome(
            forecast=forecast,
            actual_weather=actual_weather,
            accuracy_score=overall_accuracy,
            temperature_error=temp_error,
            precipitation_error=precip_error,
            condition_match=condition_match
        )

    def add_prediction_outcome(self, outcome: PredictionOutcome) -> None:
        """Add a prediction outcome to the tracking history
        
        Args:
            outcome: Prediction outcome to add
        """
        self.prediction_outcomes.append(outcome)
        
        # Clean up old outcomes beyond retention period
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        self.prediction_outcomes = [
            outcome for outcome in self.prediction_outcomes
            if outcome.actual_weather.timestamp >= cutoff_date
        ]
        
        logger.info(f"Added prediction outcome. Total outcomes: {len(self.prediction_outcomes)}")

    def calculate_accuracy_metrics(self, location: Optional[Location] = None, 
                                 days: int = 7) -> AccuracyMetrics:
        """Calculate accuracy metrics for recent predictions
        
        Args:
            location: Optional location filter
            days: Number of recent days to analyze
            
        Returns:
            AccuracyMetrics object with calculated metrics
        """
        # Filter outcomes by location and time period
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_outcomes = [
            outcome for outcome in self.prediction_outcomes
            if outcome.actual_weather.timestamp >= cutoff_date
        ]
        
        if location:
            filtered_outcomes = [
                outcome for outcome in filtered_outcomes
                if (outcome.forecast.location.latitude == location.latitude and
                    outcome.forecast.location.longitude == location.longitude)
            ]
        
        if not filtered_outcomes:
            # Return default metrics if no data
            return AccuracyMetrics(
                location=location,
                overall_accuracy=0.0,
                temperature_mae=0.0,
                temperature_rmse=0.0,
                precipitation_accuracy=0.0,
                condition_accuracy=0.0,
                total_predictions=0,
                evaluation_period_days=days,
                calculated_at=datetime.now()
            )
        
        # Calculate metrics
        accuracy_scores = [outcome.accuracy_score for outcome in filtered_outcomes]
        temperature_errors = [outcome.temperature_error for outcome in filtered_outcomes]
        precipitation_errors = [outcome.precipitation_error for outcome in filtered_outcomes]
        condition_matches = [outcome.condition_match for outcome in filtered_outcomes]
        
        overall_accuracy = mean(accuracy_scores)
        temperature_mae = self.calculator.calculate_mae(temperature_errors)
        temperature_rmse = self.calculator.calculate_rmse(temperature_errors)
        precipitation_accuracy = 1.0 - mean(precipitation_errors)  # Convert error to accuracy
        condition_accuracy = sum(condition_matches) / len(condition_matches)
        
        metrics = AccuracyMetrics(
            location=location,
            overall_accuracy=overall_accuracy,
            temperature_mae=temperature_mae,
            temperature_rmse=temperature_rmse,
            precipitation_accuracy=max(0.0, precipitation_accuracy),
            condition_accuracy=condition_accuracy,
            total_predictions=len(filtered_outcomes),
            evaluation_period_days=days,
            calculated_at=datetime.now()
        )
        
        # Store in history
        self.accuracy_history.append(metrics)
        
        # Clean up old history beyond retention period
        history_cutoff = datetime.now() - timedelta(days=self.retention_days)
        self.accuracy_history = [
            metric for metric in self.accuracy_history
            if metric.calculated_at >= history_cutoff
        ]
        
        return metrics

    def get_accuracy_trend(self, location: Optional[Location] = None, 
                          days: int = 30) -> List[AccuracyMetrics]:
        """Get accuracy trend over time
        
        Args:
            location: Optional location filter
            days: Number of days to analyze
            
        Returns:
            List of AccuracyMetrics ordered by calculation time
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_history = [
            metric for metric in self.accuracy_history
            if metric.calculated_at >= cutoff_date
        ]
        
        if location:
            filtered_history = [
                metric for metric in filtered_history
                if (metric.location and 
                    metric.location.latitude == location.latitude and
                    metric.location.longitude == location.longitude)
            ]
        
        return sorted(filtered_history, key=lambda x: x.calculated_at)

    def check_accuracy_alerts(self, location: Optional[Location] = None) -> List[str]:
        """Check if accuracy has dropped below alert thresholds
        
        Args:
            location: Optional location filter
            
        Returns:
            List of alert messages
        """
        alerts = []
        
        # Get recent accuracy metrics
        recent_metrics = self.calculate_accuracy_metrics(location, days=7)
        
        if recent_metrics.total_predictions < self.min_predictions_for_alert:
            return alerts  # Not enough data for reliable alerts
        
        # Check overall accuracy
        if recent_metrics.overall_accuracy < self.accuracy_alert_threshold:
            location_str = f" for {recent_metrics.location.city}" if recent_metrics.location else ""
            alerts.append(
                f"Overall prediction accuracy{location_str} has dropped to "
                f"{recent_metrics.overall_accuracy:.1%} (below {self.accuracy_alert_threshold:.1%} threshold)"
            )
        
        # Check temperature accuracy specifically
        if recent_metrics.temperature_mae > 5.0:  # Alert if MAE > 5°C
            location_str = f" for {recent_metrics.location.city}" if recent_metrics.location else ""
            alerts.append(
                f"Temperature prediction accuracy{location_str} has degraded "
                f"(MAE: {recent_metrics.temperature_mae:.1f}°C)"
            )
        
        # Check condition accuracy
        if recent_metrics.condition_accuracy < 0.5:  # Alert if condition accuracy < 50%
            location_str = f" for {recent_metrics.location.city}" if recent_metrics.location else ""
            alerts.append(
                f"Weather condition prediction accuracy{location_str} has dropped to "
                f"{recent_metrics.condition_accuracy:.1%}"
            )
        
        return alerts

    def get_prediction_count(self, location: Optional[Location] = None, days: int = 30) -> int:
        """Get count of predictions for a location and time period
        
        Args:
            location: Optional location filter
            days: Number of days to count
            
        Returns:
            Number of predictions
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_outcomes = [
            outcome for outcome in self.prediction_outcomes
            if outcome.actual_weather.timestamp >= cutoff_date
        ]
        
        if location:
            filtered_outcomes = [
                outcome for outcome in filtered_outcomes
                if (outcome.forecast.location.latitude == location.latitude and
                    outcome.forecast.location.longitude == location.longitude)
            ]
        
        return len(filtered_outcomes)

    def cleanup_old_data(self) -> int:
        """Remove data older than retention period
        
        Returns:
            Number of records removed
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        # Clean prediction outcomes
        initial_outcomes = len(self.prediction_outcomes)
        self.prediction_outcomes = [
            outcome for outcome in self.prediction_outcomes
            if outcome.actual_weather.timestamp >= cutoff_date
        ]
        outcomes_removed = initial_outcomes - len(self.prediction_outcomes)
        
        # Clean accuracy history
        initial_history = len(self.accuracy_history)
        self.accuracy_history = [
            metric for metric in self.accuracy_history
            if metric.calculated_at >= cutoff_date
        ]
        history_removed = initial_history - len(self.accuracy_history)
        
        total_removed = outcomes_removed + history_removed
        if total_removed > 0:
            logger.info(f"Cleaned up {total_removed} old accuracy records")
        
        return total_removed