"""Application configuration management"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database Configuration (optional - can run without database)
    use_mock_db: bool = True  # Set to True to run without PostgreSQL
    database_url: str = "postgresql://weather_user:weather_pass@localhost:5432/weather_db"
    timescaledb_host: str = "localhost"
    timescaledb_port: int = 5432
    timescaledb_user: str = "weather_user"
    timescaledb_password: str = "weather_pass"
    timescaledb_database: str = "weather_db"
    
    # External API Keys
    openweather_api_key: Optional[str] = None
    google_maps_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # Application Configuration
    data_collection_interval_minutes: int = 15
    prediction_update_interval_hours: int = 1
    data_retention_days: int = 365
    accuracy_threshold: float = 0.70
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    jwt_secret_key: str = "change_this_secret_key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
