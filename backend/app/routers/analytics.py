"""Analytics and historical data API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models import AccuracyMetrics, ChartData, Location, WeatherData
from app.services import (
    AnalyticsProcessor,
    AccuracyTracker
)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

# Initialize services
analytics_processor = AnalyticsProcessor()
accuracy_tracker = AccuracyTracker()


@router.get("/temperature-trend/{city}")
async def get_temperature_trend(
    city: str,
    country: Optional[str] = Query(None, description="Country name"),
    days: int = Query(30, ge=1, le=90, description="Number of days of historical data")
):
    """
    Get temperature trend analysis for a location
    
    Args:
        city: City name
        country: Optional country name
        days: Number of days to analyze
        
    Returns:
        Temperature trend data and chart
    """
    try:
        # Create location
        location = Location(
            latitude=0.0,
            longitude=0.0,
            city=city,
            country=country or "Unknown"
        )
        
        # Generate sample historical data (in production, fetch from database)
        historical_data = _generate_sample_historical_data(location, days)
        
        # Calculate trend
        trend = analytics_processor.trend_analyzer.calculate_temperature_trend(
            historical_data, days=days
        )
        
        # Prepare chart data
        chart = analytics_processor.viz_builder.prepare_temperature_chart(historical_data)
        
        return {
            "location": location,
            "trend": trend,
            "chart": chart
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating temperature trend: {str(e)}")


@router.get("/accuracy-metrics", response_model=AccuracyMetrics)
async def get_accuracy_metrics(
    city: Optional[str] = Query(None, description="City name for location-specific metrics"),
    country: Optional[str] = Query(None, description="Country name"),
    days: int = Query(7, ge=1, le=90, description="Evaluation period in days")
):
    """
    Get prediction accuracy metrics
    
    Args:
        city: Optional city name for location-specific metrics
        country: Optional country name
        days: Evaluation period in days
        
    Returns:
        Accuracy metrics
    """
    try:
        location = None
        if city:
            location = Location(
                latitude=0.0,
                longitude=0.0,
                city=city,
                country=country or "Unknown"
            )
        
        # Calculate accuracy metrics
        metrics = accuracy_tracker.calculate_accuracy_metrics(location, days=days)
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating accuracy metrics: {str(e)}")


@router.get("/weather-analytics/{city}")
async def get_weather_analytics(
    city: str,
    country: Optional[str] = Query(None, description="Country name"),
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze")
):
    """
    Get comprehensive weather analytics for a location
    
    Args:
        city: City name
        country: Optional country name
        days: Number of days to analyze
        
    Returns:
        Complete weather analytics including trends and charts
    """
    try:
        # Create location
        location = Location(
            latitude=0.0,
            longitude=0.0,
            city=city,
            country=country or "Unknown"
        )
        
        # Generate sample data
        historical_data = _generate_sample_historical_data(location, days)
        
        # Process analytics
        analytics = analytics_processor.process_weather_analytics(historical_data)
        
        return {
            "location": location,
            "period_days": days,
            "analytics": analytics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing analytics: {str(e)}")


@router.get("/precipitation-analysis/{city}")
async def get_precipitation_analysis(
    city: str,
    country: Optional[str] = Query(None, description="Country name"),
    days: int = Query(30, ge=1, le=90, description="Number of days to analyze")
):
    """
    Get precipitation pattern analysis
    
    Args:
        city: City name
        country: Optional country name
        days: Number of days to analyze
        
    Returns:
        Precipitation analysis and chart
    """
    try:
        location = Location(
            latitude=0.0,
            longitude=0.0,
            city=city,
            country=country or "Unknown"
        )
        
        historical_data = _generate_sample_historical_data(location, days)
        
        # Calculate precipitation pattern
        pattern = analytics_processor.trend_analyzer.calculate_precipitation_pattern(
            historical_data
        )
        
        # Prepare chart
        chart = analytics_processor.viz_builder.prepare_precipitation_chart(historical_data)
        
        return {
            "location": location,
            "pattern": pattern,
            "chart": chart
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing precipitation: {str(e)}")


@router.get("/wind-analysis/{city}")
async def get_wind_analysis(
    city: str,
    country: Optional[str] = Query(None, description="Country name"),
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze")
):
    """
    Get wind pattern analysis with vector graphics data
    
    Args:
        city: City name
        country: Optional country name
        days: Number of days to analyze
        
    Returns:
        Wind analysis with vector data and compass visualization
    """
    try:
        location = Location(
            latitude=0.0,
            longitude=0.0,
            city=city,
            country=country or "Unknown"
        )
        
        historical_data = _generate_sample_historical_data(location, days)
        
        # Calculate wind statistics
        wind_stats = analytics_processor.trend_analyzer.calculate_wind_statistics(
            historical_data
        )
        
        # Prepare wind vector data
        wind_vectors = analytics_processor.viz_builder.prepare_wind_vector_data(
            historical_data
        )
        
        return {
            "location": location,
            "statistics": wind_stats,
            "vectors": wind_vectors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing wind: {str(e)}")


def _generate_sample_historical_data(location: Location, days: int) -> List[WeatherData]:
    """Generate sample historical weather data for testing
    
    Args:
        location: Location
        days: Number of days
        
    Returns:
        List of sample weather data
    """
    import random
    
    data_list = []
    base_time = datetime.now()
    
    for i in range(days):
        data = WeatherData(
            location=location,
            timestamp=base_time - timedelta(days=days-i),
            temperature=15.0 + random.uniform(-5, 10),
            humidity=60.0 + random.uniform(-20, 20),
            pressure=1013.0 + random.uniform(-10, 10),
            wind_speed=5.0 + random.uniform(0, 10),
            wind_direction=random.uniform(0, 360),
            precipitation=random.uniform(0, 5),
            cloud_cover=random.uniform(0, 100),
            weather_condition=random.choice(['Clear', 'Cloudy', 'Partly Cloudy', 'Rainy'])
        )
        data_list.append(data)
    
    return data_list
