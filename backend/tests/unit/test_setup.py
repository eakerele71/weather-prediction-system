"""Test project setup and dependencies"""
import pytest
from app.main import app
from app.config import settings


def test_fastapi_app_created():
    """Test that FastAPI app is created successfully"""
    assert app is not None
    assert app.title == "Weather Prediction System API"


def test_settings_loaded():
    """Test that configuration settings are loaded"""
    assert settings is not None
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000


def test_app_has_health_endpoint():
    """Test that health check endpoint exists"""
    routes = [route.path for route in app.routes]
    assert "/api/v1/health" in routes


def test_app_has_root_endpoint():
    """Test that root endpoint exists"""
    routes = [route.path for route in app.routes]
    assert "/" in routes
