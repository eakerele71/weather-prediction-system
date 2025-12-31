"""Unit tests for logging configuration"""
import pytest
import logging
from pathlib import Path
from app.logging_config import (
    setup_logging,
    log_startup_configuration,
    log_critical_error,
    ErrorLogger
)


class TestLoggingSetup:
    """Test logging setup and configuration"""

    def test_setup_logging_creates_logger(self):
        """Test that setup_logging creates a logger"""
        setup_logging(log_level="INFO", enable_console=True)
        logger = logging.getLogger()
        assert logger.level == logging.INFO

    def test_setup_logging_with_debug_level(self):
        """Test setup with DEBUG level"""
        setup_logging(log_level="DEBUG", enable_console=True)
        logger = logging.getLogger()
        assert logger.level == logging.DEBUG

    def test_setup_logging_with_file(self, tmp_path):
        """Test setup with log file"""
        log_file = tmp_path / "test.log"
        setup_logging(log_level="INFO", log_file=str(log_file), enable_console=False)
        
        # Log a message
        logger = logging.getLogger()
        logger.info("Test message")
        
        # Verify file was created
        assert log_file.exists()

    def test_log_startup_configuration(self, caplog):
        """Test logging startup configuration"""
        config = {
            "api_host": "0.0.0.0",
            "api_port": 8000,
            "log_level": "INFO"
        }
        
        with caplog.at_level(logging.INFO):
            log_startup_configuration(config)
        
        assert "STARTUP CONFIGURATION" in caplog.text
        assert "api_host" in caplog.text
        assert "0.0.0.0" in caplog.text

    def test_log_startup_masks_sensitive_data(self, caplog):
        """Test that sensitive data is masked in startup logs"""
        config = {
            "api_key": "secret123",
            "password": "mypassword",
            "database_url": "postgresql://localhost"
        }
        
        with caplog.at_level(logging.INFO):
            log_startup_configuration(config)
        
        assert "***MASKED***" in caplog.text
        assert "secret123" not in caplog.text
        assert "mypassword" not in caplog.text

    def test_log_critical_error(self, caplog):
        """Test logging critical errors"""
        error = ValueError("Test error")
        context = {"location": "Seattle", "attempt": 3}
        
        with caplog.at_level(logging.CRITICAL):
            log_critical_error(error, context)
        
        assert "CRITICAL ERROR OCCURRED" in caplog.text
        assert "ValueError" in caplog.text
        assert "Test error" in caplog.text
        assert "Seattle" in caplog.text


class TestErrorLogger:
    """Test ErrorLogger class"""

    def test_error_logger_initialization(self):
        """Test ErrorLogger initializes correctly"""
        logger = ErrorLogger("test_logger")
        assert logger.logger.name == "test_logger"

    def test_log_api_error(self, caplog):
        """Test logging API errors"""
        logger = ErrorLogger()
        error = Exception("API failed")
        
        with caplog.at_level(logging.ERROR):
            logger.log_api_error(
                endpoint="/api/v1/forecast",
                error=error,
                status_code=500
            )
        
        assert "API Error" in caplog.text
        assert "/api/v1/forecast" in caplog.text
        assert "500" in caplog.text

    def test_log_api_error_with_request_data(self, caplog):
        """Test logging API errors with request data"""
        logger = ErrorLogger()
        error = Exception("API failed")
        request_data = {"city": "Seattle", "api_key": "secret123"}
        
        with caplog.at_level(logging.ERROR):
            logger.log_api_error(
                endpoint="/api/v1/forecast",
                error=error,
                request_data=request_data
            )
        
        assert "Seattle" in caplog.text
        assert "***MASKED***" in caplog.text
        assert "secret123" not in caplog.text

    def test_log_data_collection_error(self, caplog):
        """Test logging data collection errors"""
        logger = ErrorLogger()
        error = Exception("Collection failed")
        
        with caplog.at_level(logging.ERROR):
            logger.log_data_collection_error(
                location="Seattle",
                error=error,
                attempt=2,
                max_attempts=3
            )
        
        assert "Data collection failed" in caplog.text
        assert "Seattle" in caplog.text
        assert "Attempt 2/3" in caplog.text

    def test_log_data_collection_exhausted_retries(self, caplog):
        """Test logging when retries are exhausted"""
        logger = ErrorLogger()
        error = Exception("Collection failed")
        
        with caplog.at_level(logging.ERROR):
            logger.log_data_collection_error(
                location="Seattle",
                error=error,
                attempt=3,
                max_attempts=3
            )
        
        assert "All retry attempts exhausted" in caplog.text

    def test_log_prediction_error(self, caplog):
        """Test logging prediction errors"""
        logger = ErrorLogger()
        error = Exception("Prediction failed")
        
        with caplog.at_level(logging.ERROR):
            logger.log_prediction_error(
                location="Seattle",
                error=error,
                model_type="RandomForest"
            )
        
        assert "Prediction failed" in caplog.text
        assert "Seattle" in caplog.text
        assert "RandomForest" in caplog.text

    def test_log_database_error(self, caplog):
        """Test logging database errors"""
        logger = ErrorLogger()
        error = Exception("Database connection failed")
        
        with caplog.at_level(logging.ERROR):
            logger.log_database_error(
                operation="INSERT",
                error=error,
                table="weather_data"
            )
        
        assert "Database error" in caplog.text
        assert "INSERT" in caplog.text
        assert "weather_data" in caplog.text

    def test_log_validation_error(self, caplog):
        """Test logging validation errors"""
        logger = ErrorLogger()
        error = ValueError("Invalid data")
        
        with caplog.at_level(logging.WARNING):
            logger.log_validation_error(
                data_type="WeatherData",
                error=error,
                invalid_fields=["temperature", "humidity"]
            )
        
        assert "Validation failed" in caplog.text
        assert "WeatherData" in caplog.text
        assert "temperature" in caplog.text
        assert "humidity" in caplog.text

    def test_log_external_service_error(self, caplog):
        """Test logging external service errors"""
        logger = ErrorLogger()
        error = Exception("Service unavailable")
        
        with caplog.at_level(logging.ERROR):
            logger.log_external_service_error(
                service_name="OpenWeatherMap",
                error=error,
                retry_available=True
            )
        
        assert "External service error" in caplog.text
        assert "OpenWeatherMap" in caplog.text
        assert "Retry will be attempted" in caplog.text

    def test_log_external_service_error_no_retry(self, caplog):
        """Test logging external service errors without retry"""
        logger = ErrorLogger()
        error = Exception("Service unavailable")
        
        with caplog.at_level(logging.ERROR):
            logger.log_external_service_error(
                service_name="OpenWeatherMap",
                error=error,
                retry_available=False
            )
        
        assert "No retry available - using fallback" in caplog.text

    def test_sanitize_data(self):
        """Test data sanitization"""
        logger = ErrorLogger()
        data = {
            "city": "Seattle",
            "api_key": "secret123",
            "password": "mypassword",
            "temperature": 15.5
        }
        
        sanitized = logger._sanitize_data(data)
        
        assert sanitized["city"] == "Seattle"
        assert sanitized["temperature"] == 15.5
        assert sanitized["api_key"] == "***MASKED***"
        assert sanitized["password"] == "***MASKED***"
