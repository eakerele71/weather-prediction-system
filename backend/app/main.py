"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import weather, analytics, gemini, auth
from app.logging_config import setup_logging, log_startup_configuration
from app.config import settings

# Setup logging
setup_logging(
    log_level=settings.log_level,
    log_file="logs/weather_system.log",
    enable_console=True
)

# Log startup configuration
config_dict = {
    "api_host": settings.api_host,
    "api_port": settings.api_port,
    "database_url": settings.database_url,
    "data_collection_interval_minutes": settings.data_collection_interval_minutes,
    "prediction_update_interval_hours": settings.prediction_update_interval_hours,
    "data_retention_days": settings.data_retention_days,
    "accuracy_threshold": settings.accuracy_threshold,
    "log_level": settings.log_level,
    "openweather_api_key": settings.openweather_api_key,
    "gemini_api_key": settings.gemini_api_key,
}
log_startup_configuration(config_dict)

app = FastAPI(
    title="Weather Prediction System API",
    description="ML-powered weather forecasting with real-time analytics",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(weather.router)
app.include_router(analytics.router)
app.include_router(gemini.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Weather Prediction System API",
        "version": "0.1.0",
        "endpoints": {
            "auth": "/api/v1/auth/token, /api/v1/auth/login, /api/v1/auth/me",
            "weather": "/api/v1/forecast/{city}, /api/v1/current/{city}, /api/v1/warnings/{city}",
            "analytics": "/api/v1/analytics/*",
            "gemini": "/api/v1/gemini/*",
            "health": "/api/v1/health",
            "docs": "/docs"
        }
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "weather-prediction-system"}

@app.get("/api/v1/status")
async def status():
    """System status endpoint"""
    return {
        "status": "operational",
        "services": {
            "weather_api": "operational",
            "analytics": "operational",
            "gemini": "operational",
            "prediction_engine": "operational"
        },
        "version": "0.1.0"
    }
