"""Weather prediction engine using machine learning"""
import logging
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from app.models import WeatherData, Forecast, Location

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extracts and normalizes features from weather data for ML model"""

    def __init__(self):
        """Initialize feature extractor"""
        self.scaler = StandardScaler()
        self.is_fitted = False

    def extract_features(self, weather_data: WeatherData) -> np.ndarray:
        """Extract features from a single weather data point
        
        Args:
            weather_data: Weather observation
            
        Returns:
            Feature array
        """
        features = np.array([
            weather_data.temperature,
            weather_data.humidity,
            weather_data.pressure,
            weather_data.wind_speed,
            weather_data.wind_direction,
            weather_data.precipitation,
            weather_data.cloud_cover,
            # Add temporal features
            datetime.now().hour,
            datetime.now().day,
            datetime.now().month,
        ]).reshape(1, -1)

        return features

    def extract_batch_features(self, weather_data_list: List[WeatherData]) -> np.ndarray:
        """Extract features from multiple weather data points
        
        Args:
            weather_data_list: List of weather observations
            
        Returns:
            Feature matrix
        """
        features_list = []
        for data in weather_data_list:
            features = self.extract_features(data)
            features_list.append(features[0])

        return np.array(features_list)

    def normalize_features(self, features: np.ndarray, fit: bool = False) -> np.ndarray:
        """Normalize features using StandardScaler
        
        Args:
            features: Feature matrix
            fit: Whether to fit the scaler
            
        Returns:
            Normalized features
        """
        if fit:
            normalized = self.scaler.fit_transform(features)
            self.is_fitted = True
        else:
            if not self.is_fitted:
                logger.warning("Scaler not fitted, fitting on current data")
                normalized = self.scaler.fit_transform(features)
                self.is_fitted = True
            else:
                normalized = self.scaler.transform(features)

        return normalized


class WeatherPredictor:
    """ML-based weather prediction engine"""

    def __init__(self, model_type: str = "random_forest"):
        """Initialize weather predictor
        
        Args:
            model_type: Type of model ("random_forest" or "gradient_boosting")
        """
        self.model_type = model_type
        self.feature_extractor = FeatureExtractor()
        self.model = self._create_model()
        self.is_trained = False
        self.min_confidence_threshold = 0.70

    def _create_model(self):
        """Create ML model based on type
        
        Returns:
            Scikit-learn model instance
        """
        if self.model_type == "random_forest":
            return RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == "gradient_boosting":
            return GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def train(self, weather_data_list: List[WeatherData], target_values: np.ndarray) -> None:
        """Train the prediction model
        
        Args:
            weather_data_list: List of historical weather observations
            target_values: Target values (e.g., next day temperature)
        """
        if len(weather_data_list) < 10:
            logger.warning("Insufficient training data (< 10 samples)")
            return

        # Extract and normalize features
        features = self.feature_extractor.extract_batch_features(weather_data_list)
        normalized_features = self.feature_extractor.normalize_features(features, fit=True)

        # Train model
        try:
            self.model.fit(normalized_features, target_values)
            self.is_trained = True
            logger.info(f"Model trained successfully with {len(weather_data_list)} samples")
        except Exception as e:
            logger.error(f"Error training model: {e}")
            self.is_trained = False

    def predict(self, location: Location, days: int = 7) -> List[Forecast]:
        """Generate weather forecast for a location
        
        Args:
            location: Location to forecast for
            days: Number of days to forecast (default 7)
            
        Returns:
            List of Forecast objects
        """
        if not self.is_trained:
            logger.warning("Model not trained, returning default forecasts")
            return self._generate_default_forecasts(location, days)

        forecasts = []
        current_date = date.today()

        for day_offset in range(days):
            forecast_date = current_date + timedelta(days=day_offset + 1)

            # Generate synthetic features for future date
            # In production, this would use actual weather data
            features = np.array([[
                15.0 + np.random.randn() * 5,  # temperature
                65.0 + np.random.randn() * 10,  # humidity
                1013.0 + np.random.randn() * 10,  # pressure
                5.0 + np.random.randn() * 2,  # wind_speed
                180.0 + np.random.randn() * 90,  # wind_direction
                0.5 + np.random.randn() * 0.5,  # precipitation
                40.0 + np.random.randn() * 20,  # cloud_cover
                12,  # hour
                forecast_date.day,  # day
                forecast_date.month,  # month
            ]])

            # Normalize features
            normalized_features = self.feature_extractor.scaler.transform(features)

            # Make prediction
            try:
                temp_high = float(self.model.predict(normalized_features)[0])
                temp_low = temp_high - 5 + np.random.randn() * 2

                # Ensure valid temperature range
                temp_high = np.clip(temp_high, -100, 60)
                temp_low = np.clip(temp_low, -100, 60)

                # Calculate confidence score based on model uncertainty
                confidence = self._calculate_confidence(day_offset, days)

                # Determine weather condition
                weather_condition = self._determine_weather_condition(
                    temp_high, temp_low, features[0][5]
                )

                forecast = Forecast(
                    location=location,
                    forecast_date=forecast_date,
                    predicted_temperature_high=temp_high,
                    predicted_temperature_low=temp_low,
                    precipitation_probability=float(np.clip(features[0][5], 0, 1)),
                    weather_condition=weather_condition,
                    confidence_score=confidence,
                    generated_at=datetime.now()
                )

                forecasts.append(forecast)

            except Exception as e:
                logger.error(f"Error generating forecast for {forecast_date}: {e}")
                continue

        return forecasts

    def _calculate_confidence(self, day_offset: int, total_days: int) -> float:
        """Calculate confidence score for forecast
        
        Args:
            day_offset: Days into the future
            total_days: Total forecast days
            
        Returns:
            Confidence score 0-1
        """
        # Confidence decreases with forecast distance
        base_confidence = 0.85
        decay_factor = 0.05 * day_offset
        confidence = max(0.5, base_confidence - decay_factor)
        return min(1.0, confidence)

    def _determine_weather_condition(self, temp_high: float, temp_low: float,
                                     precipitation: float) -> str:
        """Determine weather condition based on predicted values
        
        Args:
            temp_high: Predicted high temperature
            temp_low: Predicted low temperature
            precipitation: Predicted precipitation
            
        Returns:
            Weather condition string
        """
        if precipitation > 5:
            if temp_high < 0:
                return "Snow"
            else:
                return "Rainy"
        elif precipitation > 1:
            return "Drizzle"
        elif temp_high > 30:
            return "Sunny"
        elif temp_high > 20:
            return "Partly Cloudy"
        else:
            return "Cloudy"

    def _generate_default_forecasts(self, location: Location, days: int) -> List[Forecast]:
        """Generate default forecasts when model is not trained
        
        Args:
            location: Location to forecast for
            days: Number of days to forecast
            
        Returns:
            List of default Forecast objects
        """
        forecasts = []
        current_date = date.today()

        for day_offset in range(days):
            forecast_date = current_date + timedelta(days=day_offset + 1)

            forecast = Forecast(
                location=location,
                forecast_date=forecast_date,
                predicted_temperature_high=15.0 + day_offset,
                predicted_temperature_low=10.0 + day_offset,
                precipitation_probability=0.3,
                weather_condition="Partly Cloudy",
                confidence_score=0.5,  # Low confidence for default
                generated_at=datetime.now()
            )

            forecasts.append(forecast)

        return forecasts

    def update_model(self, new_weather_data: List[WeatherData],
                     new_targets: np.ndarray) -> None:
        """Update model with new training data
        
        Args:
            new_weather_data: New weather observations
            new_targets: New target values
        """
        if not self.is_trained:
            logger.warning("Model not trained yet, training from scratch")
            self.train(new_weather_data, new_targets)
        else:
            # In production, implement incremental learning
            logger.info("Retraining model with new data")
            self.train(new_weather_data, new_targets)

    def get_model_info(self) -> dict:
        """Get information about the current model
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_type": self.model_type,
            "is_trained": self.is_trained,
            "feature_count": 10,
            "min_confidence_threshold": self.min_confidence_threshold,
            "model_params": self.model.get_params() if hasattr(self.model, 'get_params') else {}
        }
