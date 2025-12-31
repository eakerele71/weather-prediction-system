"""Unit tests for weather prediction engine"""
import pytest
import numpy as np
from datetime import datetime, date, timedelta
from app.services.predictor import WeatherPredictor, FeatureExtractor
from app.models import Location, WeatherData, Forecast


class TestFeatureExtractor:
    """Tests for FeatureExtractor"""

    def test_feature_extractor_initialization(self):
        """Test FeatureExtractor initialization"""
        extractor = FeatureExtractor()
        assert extractor.is_fitted is False
        assert extractor.scaler is not None

    def test_extract_features_from_single_data_point(self):
        """Test extracting features from a single weather data point"""
        extractor = FeatureExtractor()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        weather_data = WeatherData(
            location=location,
            timestamp=datetime.now(),
            temperature=15.5,
            humidity=65,
            pressure=1013,
            wind_speed=5.2,
            wind_direction=180,
            precipitation=0,
            cloud_cover=40,
            weather_condition="Cloudy"
        )

        features = extractor.extract_features(weather_data)
        assert features.shape == (1, 10)
        assert features[0, 0] == 15.5  # temperature
        assert features[0, 1] == 65    # humidity

    def test_extract_batch_features(self):
        """Test extracting features from multiple data points"""
        extractor = FeatureExtractor()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        weather_data_list = [
            WeatherData(
                location=location,
                timestamp=datetime.now(),
                temperature=15.5 + i,
                humidity=65,
                pressure=1013,
                wind_speed=5.2,
                wind_direction=180,
                precipitation=0,
                cloud_cover=40,
                weather_condition="Cloudy"
            )
            for i in range(5)
        ]

        features = extractor.extract_batch_features(weather_data_list)
        assert features.shape == (5, 10)

    def test_normalize_features_with_fit(self):
        """Test normalizing features with fitting"""
        extractor = FeatureExtractor()
        features = np.array([
            [15.5, 65, 1013, 5.2, 180, 0, 40, 12, 15, 1],
            [16.0, 70, 1012, 5.5, 185, 0.5, 45, 13, 15, 1],
            [14.5, 60, 1014, 4.8, 175, 0, 35, 11, 15, 1],
        ])

        normalized = extractor.normalize_features(features, fit=True)
        assert normalized.shape == features.shape
        assert extractor.is_fitted is True
        # Check that values are normalized (mean ~0, std ~1)
        assert np.abs(np.mean(normalized)) < 1.0

    def test_normalize_features_without_fit(self):
        """Test normalizing features without fitting"""
        extractor = FeatureExtractor()
        features = np.array([
            [15.5, 65, 1013, 5.2, 180, 0, 40, 12, 15, 1],
            [16.0, 70, 1012, 5.5, 185, 0.5, 45, 13, 15, 1],
        ])

        # First fit
        extractor.normalize_features(features, fit=True)

        # Then normalize without fit
        new_features = np.array([[15.0, 62, 1013.5, 5.0, 180, 0, 40, 12, 15, 1]])
        normalized = extractor.normalize_features(new_features, fit=False)
        assert normalized.shape == (1, 10)


class TestWeatherPredictor:
    """Tests for WeatherPredictor"""

    def test_predictor_initialization_random_forest(self):
        """Test WeatherPredictor initialization with Random Forest"""
        predictor = WeatherPredictor(model_type="random_forest")
        assert predictor.model_type == "random_forest"
        assert predictor.is_trained is False
        assert predictor.model is not None

    def test_predictor_initialization_gradient_boosting(self):
        """Test WeatherPredictor initialization with Gradient Boosting"""
        predictor = WeatherPredictor(model_type="gradient_boosting")
        assert predictor.model_type == "gradient_boosting"
        assert predictor.is_trained is False

    def test_predictor_invalid_model_type(self):
        """Test WeatherPredictor with invalid model type"""
        with pytest.raises(ValueError, match="Unknown model type"):
            WeatherPredictor(model_type="invalid_model")

    def test_train_model(self):
        """Test training the prediction model"""
        predictor = WeatherPredictor()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        # Create training data
        weather_data_list = [
            WeatherData(
                location=location,
                timestamp=datetime.now() - timedelta(days=i),
                temperature=15.5 + np.random.randn(),
                humidity=65 + np.random.randn() * 5,
                pressure=1013 + np.random.randn(),
                wind_speed=5.2 + np.random.randn(),
                wind_direction=180 + np.random.randn() * 30,
                precipitation=np.random.rand(),
                cloud_cover=40 + np.random.randn() * 10,
                weather_condition="Cloudy"
            )
            for i in range(20)
        ]

        target_values = np.array([16.0 + np.random.randn() for _ in range(20)])

        predictor.train(weather_data_list, target_values)
        assert predictor.is_trained is True

    def test_train_with_insufficient_data(self):
        """Test training with insufficient data"""
        predictor = WeatherPredictor()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        weather_data_list = [
            WeatherData(
                location=location,
                timestamp=datetime.now(),
                temperature=15.5,
                humidity=65,
                pressure=1013,
                wind_speed=5.2,
                wind_direction=180,
                precipitation=0,
                cloud_cover=40,
                weather_condition="Cloudy"
            )
        ]

        target_values = np.array([16.0])

        predictor.train(weather_data_list, target_values)
        assert predictor.is_trained is False

    def test_predict_without_training(self):
        """Test prediction without training (should return defaults)"""
        predictor = WeatherPredictor()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        forecasts = predictor.predict(location, days=7)
        assert len(forecasts) == 7
        assert all(isinstance(f, Forecast) for f in forecasts)
        # Default forecasts should have low confidence
        assert all(f.confidence_score == 0.5 for f in forecasts)

    def test_predict_with_training(self):
        """Test prediction after training"""
        predictor = WeatherPredictor()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        # Train model
        weather_data_list = [
            WeatherData(
                location=location,
                timestamp=datetime.now() - timedelta(days=i),
                temperature=15.5 + np.random.randn(),
                humidity=65 + np.random.randn() * 5,
                pressure=1013 + np.random.randn(),
                wind_speed=5.2 + np.random.randn(),
                wind_direction=180 + np.random.randn() * 30,
                precipitation=np.random.rand(),
                cloud_cover=40 + np.random.randn() * 10,
                weather_condition="Cloudy"
            )
            for i in range(20)
        ]

        target_values = np.array([16.0 + np.random.randn() for _ in range(20)])
        predictor.train(weather_data_list, target_values)

        # Make predictions
        forecasts = predictor.predict(location, days=7)
        assert len(forecasts) == 7
        assert all(isinstance(f, Forecast) for f in forecasts)
        # Trained model should have higher confidence
        assert all(f.confidence_score >= 0.5 for f in forecasts)

    def test_forecast_completeness(self):
        """Test that forecasts have all required fields"""
        predictor = WeatherPredictor()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        forecasts = predictor.predict(location, days=7)

        for forecast in forecasts:
            assert forecast.location == location
            assert forecast.forecast_date is not None
            assert forecast.predicted_temperature_high is not None
            assert forecast.predicted_temperature_low is not None
            assert 0 <= forecast.precipitation_probability <= 1
            assert forecast.weather_condition is not None
            assert 0 <= forecast.confidence_score <= 1
            assert forecast.generated_at is not None

    def test_forecast_temperature_relationship(self):
        """Test that high temperature >= low temperature"""
        predictor = WeatherPredictor()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        # Train model
        weather_data_list = [
            WeatherData(
                location=location,
                timestamp=datetime.now() - timedelta(days=i),
                temperature=15.5 + np.random.randn(),
                humidity=65 + np.random.randn() * 5,
                pressure=1013 + np.random.randn(),
                wind_speed=5.2 + np.random.randn(),
                wind_direction=180 + np.random.randn() * 30,
                precipitation=np.random.rand(),
                cloud_cover=40 + np.random.randn() * 10,
                weather_condition="Cloudy"
            )
            for i in range(20)
        ]

        target_values = np.array([16.0 + np.random.randn() for _ in range(20)])
        predictor.train(weather_data_list, target_values)

        forecasts = predictor.predict(location, days=7)

        for forecast in forecasts:
            assert forecast.predicted_temperature_high >= forecast.predicted_temperature_low

    def test_calculate_confidence(self):
        """Test confidence score calculation"""
        predictor = WeatherPredictor()

        # Confidence should decrease with forecast distance
        conf_day1 = predictor._calculate_confidence(0, 7)
        conf_day4 = predictor._calculate_confidence(3, 7)
        conf_day7 = predictor._calculate_confidence(6, 7)

        assert conf_day1 > conf_day4
        assert conf_day4 > conf_day7
        assert all(0.5 <= c <= 1.0 for c in [conf_day1, conf_day4, conf_day7])

    def test_determine_weather_condition(self):
        """Test weather condition determination"""
        predictor = WeatherPredictor()

        # Test different conditions
        assert predictor._determine_weather_condition(35, 30, 0) == "Sunny"
        assert predictor._determine_weather_condition(25, 20, 0) == "Partly Cloudy"
        assert predictor._determine_weather_condition(15, 10, 0) == "Cloudy"
        assert predictor._determine_weather_condition(-5, -10, 10) == "Snow"
        assert predictor._determine_weather_condition(15, 10, 10) == "Rainy"
        assert predictor._determine_weather_condition(15, 10, 2) == "Drizzle"

    def test_get_model_info(self):
        """Test getting model information"""
        predictor = WeatherPredictor(model_type="random_forest")
        info = predictor.get_model_info()

        assert info["model_type"] == "random_forest"
        assert info["is_trained"] is False
        assert info["feature_count"] == 10
        assert "model_params" in info

    def test_update_model(self):
        """Test updating model with new data"""
        predictor = WeatherPredictor()
        location = Location(
            latitude=47.6062,
            longitude=-122.3321,
            city="Seattle",
            country="United States"
        )

        # Initial training
        weather_data_list = [
            WeatherData(
                location=location,
                timestamp=datetime.now() - timedelta(days=i),
                temperature=15.5 + np.random.randn(),
                humidity=65 + np.random.randn() * 5,
                pressure=1013 + np.random.randn(),
                wind_speed=5.2 + np.random.randn(),
                wind_direction=180 + np.random.randn() * 30,
                precipitation=np.random.rand(),
                cloud_cover=40 + np.random.randn() * 10,
                weather_condition="Cloudy"
            )
            for i in range(20)
        ]

        target_values = np.array([16.0 + np.random.randn() for _ in range(20)])
        predictor.train(weather_data_list, target_values)

        # Update with new data
        new_data = weather_data_list[:5]
        new_targets = np.array([17.0 + np.random.randn() for _ in range(5)])
        predictor.update_model(new_data, new_targets)

        assert predictor.is_trained is True
