"""Unit tests for accuracy tracking system"""
import pytest
from datetime import datetime, timedelta, date
from app.models import Location, WeatherData, Forecast, AccuracyMetrics
from app.services.accuracy_tracker import (
    AccuracyCalculator, AccuracyTracker, PredictionOutcome
)


class TestAccuracyCalculator:
    """Test cases for AccuracyCalculator"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.calculator = AccuracyCalculator()
    
    def test_temperature_accuracy_perfect_match(self):
        """Test temperature accuracy calculation for perfect match"""
        accuracy, error = self.calculator.calculate_temperature_accuracy(25.0, 25.0)
        assert accuracy == 1.0
        assert error == 0.0
    
    def test_temperature_accuracy_small_error(self):
        """Test temperature accuracy calculation for small error"""
        accuracy, error = self.calculator.calculate_temperature_accuracy(25.0, 26.0)
        assert accuracy == 0.9  # 1°C error = 90% accuracy
        assert error == 1.0
    
    def test_temperature_accuracy_large_error(self):
        """Test temperature accuracy calculation for large error"""
        accuracy, error = self.calculator.calculate_temperature_accuracy(25.0, 35.0)
        assert accuracy == 0.0  # 10°C+ error = 0% accuracy
        assert error == 10.0
    
    def test_temperature_accuracy_medium_error(self):
        """Test temperature accuracy calculation for medium error"""
        accuracy, error = self.calculator.calculate_temperature_accuracy(20.0, 25.0)
        assert accuracy == 0.5  # 5°C error = 50% accuracy
        assert error == 5.0
    
    def test_precipitation_accuracy_perfect_match(self):
        """Test precipitation accuracy for perfect probability match"""
        accuracy, error = self.calculator.calculate_precipitation_accuracy(0.8, 8.0)
        assert accuracy == 1.0  # 8mm = 80% probability, matches 0.8
        assert error == 0.0
    
    def test_precipitation_accuracy_no_rain_predicted_none_actual(self):
        """Test precipitation accuracy when no rain predicted and none occurred"""
        accuracy, error = self.calculator.calculate_precipitation_accuracy(0.0, 0.0)
        assert accuracy == 1.0
        assert error == 0.0
    
    def test_precipitation_accuracy_high_error(self):
        """Test precipitation accuracy with high error"""
        accuracy, error = self.calculator.calculate_precipitation_accuracy(0.0, 10.0)
        assert accuracy == 0.0  # Predicted 0%, actual 100%
        assert error == 1.0
    
    def test_condition_accuracy_exact_match(self):
        """Test weather condition accuracy for exact match"""
        accuracy, match = self.calculator.calculate_condition_accuracy('Sunny', 'Sunny')
        assert accuracy == 1.0
        assert match is True
    
    def test_condition_accuracy_case_insensitive(self):
        """Test weather condition accuracy is case insensitive"""
        accuracy, match = self.calculator.calculate_condition_accuracy('SUNNY', 'sunny')
        assert accuracy == 1.0
        assert match is True
    
    def test_condition_accuracy_partial_match(self):
        """Test weather condition accuracy for partial match within same group"""
        accuracy, match = self.calculator.calculate_condition_accuracy('Clear', 'Sunny')
        assert accuracy == 0.7  # Partial match within clear group
        assert match is False
    
    def test_condition_accuracy_no_match(self):
        """Test weather condition accuracy for no match"""
        accuracy, match = self.calculator.calculate_condition_accuracy('Sunny', 'Rainy')
        assert accuracy == 0.0
        assert match is False
    
    def test_overall_accuracy_calculation(self):
        """Test weighted overall accuracy calculation"""
        accuracy = self.calculator.calculate_overall_accuracy(1.0, 0.8, 0.6)
        expected = 1.0 * 0.4 + 0.8 * 0.3 + 0.6 * 0.3  # Weighted average
        assert accuracy == expected
    
    def test_mae_calculation(self):
        """Test Mean Absolute Error calculation"""
        errors = [1.0, 2.0, 3.0, 4.0, 5.0]
        mae = self.calculator.calculate_mae(errors)
        assert mae == 3.0
    
    def test_mae_empty_list(self):
        """Test MAE calculation with empty list"""
        mae = self.calculator.calculate_mae([])
        assert mae == 0.0
    
    def test_rmse_calculation(self):
        """Test Root Mean Square Error calculation"""
        errors = [1.0, 2.0, 3.0, 4.0, 5.0]
        rmse = self.calculator.calculate_rmse(errors)
        expected = (1 + 4 + 9 + 16 + 25) / 5  # MSE = 11
        expected = expected ** 0.5  # RMSE = sqrt(11) ≈ 3.317
        assert abs(rmse - expected) < 0.001
    
    def test_rmse_empty_list(self):
        """Test RMSE calculation with empty list"""
        rmse = self.calculator.calculate_rmse([])
        assert rmse == 0.0


class TestAccuracyTracker:
    """Test cases for AccuracyTracker"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.tracker = AccuracyTracker(retention_days=30)
        self.location = Location(
            latitude=40.7128,
            longitude=-74.0060,
            city='New York',
            country='USA'
        )
    
    def create_forecast(self, temp_high=25.0, precip_prob=0.3, condition='Sunny'):
        """Helper to create test forecast"""
        return Forecast(
            location=self.location,
            forecast_date=date.today(),
            predicted_temperature_high=temp_high,
            predicted_temperature_low=temp_high - 10,
            precipitation_probability=precip_prob,
            weather_condition=condition,
            confidence_score=0.8,
            generated_at=datetime.now()
        )
    
    def create_weather_data(self, temp=25.0, precip=3.0, condition='Sunny'):
        """Helper to create test weather data"""
        return WeatherData(
            location=self.location,
            timestamp=datetime.now(),
            temperature=temp,
            humidity=60.0,
            pressure=1013.0,
            wind_speed=5.0,
            wind_direction=180.0,
            precipitation=precip,
            cloud_cover=30.0,
            weather_condition=condition
        )
    
    def test_compare_prediction_to_actual_perfect_match(self):
        """Test comparing prediction to actual with perfect match"""
        forecast = self.create_forecast(25.0, 0.3, 'Sunny')
        actual = self.create_weather_data(25.0, 3.0, 'Sunny')
        
        outcome = self.tracker.compare_prediction_to_actual(forecast, actual)
        
        assert outcome.forecast == forecast
        assert outcome.actual_weather == actual
        assert outcome.accuracy_score == 1.0  # Perfect match
        assert outcome.temperature_error == 0.0
        assert outcome.condition_match is True
    
    def test_compare_prediction_to_actual_with_errors(self):
        """Test comparing prediction to actual with some errors"""
        forecast = self.create_forecast(25.0, 0.3, 'Sunny')
        actual = self.create_weather_data(28.0, 8.0, 'Cloudy')
        
        outcome = self.tracker.compare_prediction_to_actual(forecast, actual)
        
        assert outcome.temperature_error == 3.0
        assert outcome.condition_match is False
        assert 0.0 < outcome.accuracy_score < 1.0
    
    def test_add_prediction_outcome(self):
        """Test adding prediction outcome to tracker"""
        forecast = self.create_forecast()
        actual = self.create_weather_data()
        outcome = self.tracker.compare_prediction_to_actual(forecast, actual)
        
        initial_count = len(self.tracker.prediction_outcomes)
        self.tracker.add_prediction_outcome(outcome)
        
        assert len(self.tracker.prediction_outcomes) == initial_count + 1
        assert self.tracker.prediction_outcomes[-1] == outcome
    
    def test_calculate_accuracy_metrics_no_data(self):
        """Test calculating accuracy metrics with no data"""
        metrics = self.tracker.calculate_accuracy_metrics(self.location, days=7)
        
        assert metrics.location == self.location
        assert metrics.overall_accuracy == 0.0
        assert metrics.total_predictions == 0
        assert metrics.evaluation_period_days == 7
    
    def test_calculate_accuracy_metrics_with_data(self):
        """Test calculating accuracy metrics with prediction data"""
        # Add some prediction outcomes
        for i in range(5):
            forecast = self.create_forecast(25.0 + i, 0.3, 'Sunny')
            actual = self.create_weather_data(25.0 + i + 1, 3.0, 'Sunny')  # 1°C error each
            outcome = self.tracker.compare_prediction_to_actual(forecast, actual)
            self.tracker.add_prediction_outcome(outcome)
        
        metrics = self.tracker.calculate_accuracy_metrics(self.location, days=7)
        
        assert metrics.location == self.location
        assert metrics.total_predictions == 5
        assert metrics.temperature_mae == 1.0  # All predictions had 1°C error
        assert metrics.condition_accuracy == 1.0  # All conditions matched
        assert 0.0 < metrics.overall_accuracy < 1.0
    
    def test_calculate_accuracy_metrics_location_filter(self):
        """Test calculating accuracy metrics with location filtering"""
        # Add outcomes for different locations
        other_location = Location(latitude=51.5074, longitude=-0.1278, city='London', country='UK')
        
        # Add outcome for target location
        forecast1 = self.create_forecast()
        actual1 = self.create_weather_data()
        outcome1 = self.tracker.compare_prediction_to_actual(forecast1, actual1)
        self.tracker.add_prediction_outcome(outcome1)
        
        # Add outcome for other location
        forecast2 = Forecast(
            location=other_location,
            forecast_date=date.today(),
            predicted_temperature_high=20.0,
            predicted_temperature_low=10.0,
            precipitation_probability=0.5,
            weather_condition='Rainy',
            confidence_score=0.7,
            generated_at=datetime.now()
        )
        actual2 = WeatherData(
            location=other_location,
            timestamp=datetime.now(),
            temperature=20.0,
            humidity=80.0,
            pressure=1000.0,
            wind_speed=10.0,
            wind_direction=270.0,
            precipitation=5.0,
            cloud_cover=90.0,
            weather_condition='Rainy'
        )
        outcome2 = self.tracker.compare_prediction_to_actual(forecast2, actual2)
        self.tracker.add_prediction_outcome(outcome2)
        
        # Test filtering by target location
        metrics = self.tracker.calculate_accuracy_metrics(self.location, days=7)
        assert metrics.total_predictions == 1
        
        # Test filtering by other location
        metrics_other = self.tracker.calculate_accuracy_metrics(other_location, days=7)
        assert metrics_other.total_predictions == 1
    
    def test_get_accuracy_trend(self):
        """Test getting accuracy trend over time"""
        # Add some historical metrics
        for i in range(3):
            metrics = AccuracyMetrics(
                location=self.location,
                overall_accuracy=0.8 + i * 0.05,
                temperature_mae=2.0 - i * 0.2,
                temperature_rmse=2.5 - i * 0.2,
                precipitation_accuracy=0.7 + i * 0.1,
                condition_accuracy=0.9,
                total_predictions=10,
                evaluation_period_days=7,
                calculated_at=datetime.now() - timedelta(days=i)
            )
            self.tracker.accuracy_history.append(metrics)
        
        trend = self.tracker.get_accuracy_trend(self.location, days=30)
        
        assert len(trend) == 3
        # Should be ordered by calculation time (oldest first)
        assert trend[0].calculated_at < trend[1].calculated_at < trend[2].calculated_at
    
    def test_check_accuracy_alerts_no_alerts(self):
        """Test accuracy alerts when accuracy is good"""
        # Add good prediction outcomes
        for i in range(15):  # Above minimum threshold
            forecast = self.create_forecast(25.0, 0.3, 'Sunny')
            actual = self.create_weather_data(25.0, 3.0, 'Sunny')  # Perfect matches
            outcome = self.tracker.compare_prediction_to_actual(forecast, actual)
            self.tracker.add_prediction_outcome(outcome)
        
        alerts = self.tracker.check_accuracy_alerts(self.location)
        assert len(alerts) == 0
    
    def test_check_accuracy_alerts_low_accuracy(self):
        """Test accuracy alerts when accuracy is low"""
        # Add poor prediction outcomes
        for i in range(15):  # Above minimum threshold
            forecast = self.create_forecast(25.0, 0.0, 'Sunny')
            actual = self.create_weather_data(35.0, 10.0, 'Rainy')  # Large errors
            outcome = self.tracker.compare_prediction_to_actual(forecast, actual)
            self.tracker.add_prediction_outcome(outcome)
        
        alerts = self.tracker.check_accuracy_alerts(self.location)
        assert len(alerts) > 0
        assert any('accuracy' in alert.lower() for alert in alerts)
    
    def test_check_accuracy_alerts_insufficient_data(self):
        """Test accuracy alerts with insufficient data"""
        # Add only a few outcomes (below minimum threshold)
        for i in range(5):
            forecast = self.create_forecast(25.0, 0.0, 'Sunny')
            actual = self.create_weather_data(35.0, 10.0, 'Rainy')
            outcome = self.tracker.compare_prediction_to_actual(forecast, actual)
            self.tracker.add_prediction_outcome(outcome)
        
        alerts = self.tracker.check_accuracy_alerts(self.location)
        assert len(alerts) == 0  # Not enough data for alerts
    
    def test_get_prediction_count(self):
        """Test getting prediction count"""
        # Add some outcomes
        for i in range(3):
            forecast = self.create_forecast()
            actual = self.create_weather_data()
            outcome = self.tracker.compare_prediction_to_actual(forecast, actual)
            self.tracker.add_prediction_outcome(outcome)
        
        count = self.tracker.get_prediction_count(self.location, days=7)
        assert count == 3
    
    def test_get_prediction_count_location_filter(self):
        """Test getting prediction count with location filter"""
        other_location = Location(latitude=51.5074, longitude=-0.1278, city='London', country='UK')
        
        # Add outcome for target location
        forecast1 = self.create_forecast()
        actual1 = self.create_weather_data()
        outcome1 = self.tracker.compare_prediction_to_actual(forecast1, actual1)
        self.tracker.add_prediction_outcome(outcome1)
        
        # Add outcome for other location
        forecast2 = Forecast(
            location=other_location,
            forecast_date=date.today(),
            predicted_temperature_high=20.0,
            predicted_temperature_low=10.0,
            precipitation_probability=0.5,
            weather_condition='Rainy',
            confidence_score=0.7,
            generated_at=datetime.now()
        )
        actual2 = WeatherData(
            location=other_location,
            timestamp=datetime.now(),
            temperature=20.0,
            humidity=80.0,
            pressure=1000.0,
            wind_speed=10.0,
            wind_direction=270.0,
            precipitation=5.0,
            cloud_cover=90.0,
            weather_condition='Rainy'
        )
        outcome2 = self.tracker.compare_prediction_to_actual(forecast2, actual2)
        self.tracker.add_prediction_outcome(outcome2)
        
        # Test count for target location
        count = self.tracker.get_prediction_count(self.location, days=7)
        assert count == 1
        
        # Test count for other location
        count_other = self.tracker.get_prediction_count(other_location, days=7)
        assert count_other == 1
    
    def test_cleanup_old_data(self):
        """Test cleaning up old data beyond retention period"""
        # Set short retention period for testing
        self.tracker.retention_days = 1
        
        # Add old outcome (beyond retention) directly to list to bypass automatic cleanup
        old_actual = WeatherData(
            location=self.location,
            timestamp=datetime.now() - timedelta(days=2),  # 2 days old
            temperature=25.0,
            humidity=60.0,
            pressure=1013.0,
            wind_speed=5.0,
            wind_direction=180.0,
            precipitation=3.0,
            cloud_cover=30.0,
            weather_condition='Sunny'
        )
        old_forecast = self.create_forecast()
        old_outcome = PredictionOutcome(
            forecast=old_forecast,
            actual_weather=old_actual,
            accuracy_score=0.8,
            temperature_error=1.0,
            precipitation_error=0.1,
            condition_match=True
        )
        self.tracker.prediction_outcomes.append(old_outcome)
        
        # Add recent outcome directly to list
        recent_actual = WeatherData(
            location=self.location,
            timestamp=datetime.now(),  # Current time
            temperature=25.0,
            humidity=60.0,
            pressure=1013.0,
            wind_speed=5.0,
            wind_direction=180.0,
            precipitation=3.0,
            cloud_cover=30.0,
            weather_condition='Sunny'
        )
        recent_forecast = self.create_forecast()
        recent_outcome = PredictionOutcome(
            forecast=recent_forecast,
            actual_weather=recent_actual,
            accuracy_score=0.8,
            temperature_error=1.0,
            precipitation_error=0.1,
            condition_match=True
        )
        self.tracker.prediction_outcomes.append(recent_outcome)
        
        # Add old accuracy history
        old_metrics = AccuracyMetrics(
            location=self.location,
            overall_accuracy=0.8,
            temperature_mae=2.0,
            temperature_rmse=2.5,
            precipitation_accuracy=0.7,
            condition_accuracy=0.9,
            total_predictions=10,
            evaluation_period_days=7,
            calculated_at=datetime.now() - timedelta(days=2)  # 2 days old
        )
        self.tracker.accuracy_history.append(old_metrics)
        
        initial_outcomes = len(self.tracker.prediction_outcomes)
        initial_history = len(self.tracker.accuracy_history)
        
        # Should have 2 outcomes and 1 history item
        assert initial_outcomes == 2
        assert initial_history == 1
        
        removed_count = self.tracker.cleanup_old_data()
        
        # Should have removed old data
        assert removed_count > 0
        assert len(self.tracker.prediction_outcomes) == 1  # Only recent outcome remains
        assert len(self.tracker.accuracy_history) == 0     # Old history removed
    
    def test_retention_period_enforcement(self):
        """Test that retention period is enforced when adding outcomes"""
        # Set short retention period
        self.tracker.retention_days = 1
        
        # Add old outcome
        old_actual = WeatherData(
            location=self.location,
            timestamp=datetime.now() - timedelta(days=2),
            temperature=25.0,
            humidity=60.0,
            pressure=1013.0,
            wind_speed=5.0,
            wind_direction=180.0,
            precipitation=3.0,
            cloud_cover=30.0,
            weather_condition='Sunny'
        )
        old_forecast = self.create_forecast()
        old_outcome = PredictionOutcome(
            forecast=old_forecast,
            actual_weather=old_actual,
            accuracy_score=0.8,
            temperature_error=1.0,
            precipitation_error=0.1,
            condition_match=True
        )
        self.tracker.prediction_outcomes.append(old_outcome)
        
        # Add new outcome - should trigger cleanup
        new_forecast = self.create_forecast()
        new_actual = self.create_weather_data()
        new_outcome = self.tracker.compare_prediction_to_actual(new_forecast, new_actual)
        self.tracker.add_prediction_outcome(new_outcome)
        
        # Old outcome should be removed
        assert len(self.tracker.prediction_outcomes) == 1
        assert self.tracker.prediction_outcomes[0] == new_outcome