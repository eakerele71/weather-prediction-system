"""Comprehensive logging configuration for the Weather Prediction System"""
import logging
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path


class DetailedFormatter(logging.Formatter):
    """Custom formatter with detailed error information"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with additional details
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log string
        """
        # Add timestamp
        record.timestamp = datetime.now().isoformat()
        
        # Add module and function info
        record.location = f"{record.module}.{record.funcName}"
        
        # Format the base message
        formatted = super().format(record)
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\nException Type: {record.exc_info[0].__name__}"
            formatted += f"\nException Message: {record.exc_info[1]}"
        
        return formatted


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> None:
    """Setup comprehensive logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        enable_console: Whether to enable console logging
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    detailed_format = (
        "%(timestamp)s - %(levelname)s - %(location)s - "
        "%(message)s"
    )
    formatter = DetailedFormatter(detailed_format)
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logger.info(f"Logging configured: level={log_level}, file={log_file}")


def log_startup_configuration(config: dict) -> None:
    """Log startup configuration for verification
    
    Args:
        config: Configuration dictionary to log
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("STARTUP CONFIGURATION")
    logger.info("=" * 60)
    
    for key, value in sorted(config.items()):
        # Mask sensitive values
        if any(sensitive in key.lower() for sensitive in ['key', 'password', 'secret', 'token']):
            masked_value = "***MASKED***" if value else "Not Set"
            logger.info(f"{key}: {masked_value}")
        else:
            logger.info(f"{key}: {value}")
    
    logger.info("=" * 60)


def log_critical_error(
    error: Exception,
    context: Optional[dict] = None,
    logger_name: Optional[str] = None
) -> None:
    """Log critical error with detailed information
    
    Args:
        error: Exception that occurred
        context: Additional context information
        logger_name: Name of logger to use (uses root if None)
    """
    logger = logging.getLogger(logger_name or __name__)
    
    logger.critical("=" * 60)
    logger.critical("CRITICAL ERROR OCCURRED")
    logger.critical("=" * 60)
    logger.critical(f"Error Type: {type(error).__name__}")
    logger.critical(f"Error Message: {str(error)}")
    logger.critical(f"Timestamp: {datetime.now().isoformat()}")
    
    if context:
        logger.critical("Context Information:")
        for key, value in context.items():
            logger.critical(f"  {key}: {value}")
    
    logger.critical("Stack Trace:", exc_info=True)
    logger.critical("=" * 60)


class ErrorLogger:
    """Centralized error logging utility"""

    def __init__(self, logger_name: str = __name__):
        """Initialize error logger
        
        Args:
            logger_name: Name for the logger
        """
        self.logger = logging.getLogger(logger_name)

    def log_api_error(
        self,
        endpoint: str,
        error: Exception,
        status_code: Optional[int] = None,
        request_data: Optional[dict] = None
    ) -> None:
        """Log API-related errors
        
        Args:
            endpoint: API endpoint that failed
            error: Exception that occurred
            status_code: HTTP status code (if applicable)
            request_data: Request data (will be sanitized)
        """
        self.logger.error(f"API Error at {endpoint}")
        self.logger.error(f"Error Type: {type(error).__name__}")
        self.logger.error(f"Error Message: {str(error)}")
        
        if status_code:
            self.logger.error(f"Status Code: {status_code}")
        
        if request_data:
            # Sanitize sensitive data
            sanitized = self._sanitize_data(request_data)
            self.logger.error(f"Request Data: {sanitized}")
        
        self.logger.error("Stack Trace:", exc_info=True)

    def log_data_collection_error(
        self,
        location: str,
        error: Exception,
        attempt: int,
        max_attempts: int
    ) -> None:
        """Log data collection errors
        
        Args:
            location: Location being collected
            error: Exception that occurred
            attempt: Current attempt number
            max_attempts: Maximum number of attempts
        """
        self.logger.error(f"Data collection failed for {location}")
        self.logger.error(f"Attempt {attempt}/{max_attempts}")
        self.logger.error(f"Error: {type(error).__name__}: {str(error)}")
        
        if attempt >= max_attempts:
            self.logger.error(f"All retry attempts exhausted for {location}")

    def log_prediction_error(
        self,
        location: str,
        error: Exception,
        model_type: Optional[str] = None
    ) -> None:
        """Log prediction engine errors
        
        Args:
            location: Location for prediction
            error: Exception that occurred
            model_type: Type of model that failed
        """
        self.logger.error(f"Prediction failed for {location}")
        
        if model_type:
            self.logger.error(f"Model Type: {model_type}")
        
        self.logger.error(f"Error: {type(error).__name__}: {str(error)}")
        self.logger.error("Stack Trace:", exc_info=True)

    def log_database_error(
        self,
        operation: str,
        error: Exception,
        table: Optional[str] = None
    ) -> None:
        """Log database-related errors
        
        Args:
            operation: Database operation that failed
            error: Exception that occurred
            table: Table name (if applicable)
        """
        self.logger.error(f"Database error during {operation}")
        
        if table:
            self.logger.error(f"Table: {table}")
        
        self.logger.error(f"Error: {type(error).__name__}: {str(error)}")
        self.logger.error("Stack Trace:", exc_info=True)

    def log_validation_error(
        self,
        data_type: str,
        error: Exception,
        invalid_fields: Optional[list] = None
    ) -> None:
        """Log data validation errors
        
        Args:
            data_type: Type of data being validated
            error: Exception that occurred
            invalid_fields: List of invalid fields
        """
        self.logger.warning(f"Validation failed for {data_type}")
        self.logger.warning(f"Error: {str(error)}")
        
        if invalid_fields:
            self.logger.warning(f"Invalid Fields: {', '.join(invalid_fields)}")

    def log_external_service_error(
        self,
        service_name: str,
        error: Exception,
        retry_available: bool = False
    ) -> None:
        """Log external service errors
        
        Args:
            service_name: Name of external service
            error: Exception that occurred
            retry_available: Whether retry is available
        """
        self.logger.error(f"External service error: {service_name}")
        self.logger.error(f"Error: {type(error).__name__}: {str(error)}")
        
        if retry_available:
            self.logger.error("Retry will be attempted")
        else:
            self.logger.error("No retry available - using fallback")

    def _sanitize_data(self, data: dict) -> dict:
        """Sanitize sensitive data from logs
        
        Args:
            data: Data dictionary to sanitize
            
        Returns:
            Sanitized data dictionary
        """
        sensitive_keys = ['password', 'token', 'key', 'secret', 'api_key']
        sanitized = {}
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***MASKED***"
            else:
                sanitized[key] = value
        
        return sanitized


# Global error logger instance
error_logger = ErrorLogger()
