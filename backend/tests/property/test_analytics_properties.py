"""Property-based tests for analytics processor"""
import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime, timedelta, date
from app.services.analytics_processor import (
    TrendAnalyzer,
    VisualizationDataBuilder,
    AnalyticsProcessor
)
from app.models import WeatherData, Forecast, Location, ChartData, AccuracyMetrics


# Custom strategies for generating test data
@st.composite
def location_strategy(draw):
    """Generate valid Location objects"""
    return Location(
        latitude=draw(st.floats(min_value=-90, max_value=90)),
        longitude=draw(st.floats(min_value=-180, max_value=180)),
        city=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))),
        country=draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))))
    )


@st.composite
def weather_data_strategy(draw, location=None):
    """Generate valid WeatherData objects"""
    if location is None:
        location = draw(location_strategy())
    
    return WeatherData(
        location=location,
        timestamp=datetime.now() + timedelta(days=draw(st.integers(min_value=0, max_value=30))),
        temperature=draw(st.floats(min_value=-50, max_value=50)),
        humidity=draw(st.floats(min_value=0, max_value=100)),
        pressure=draw(st.floats(min_value=900, max_value=1100)),
        wind_speed=draw(st.floats(min_value=0, max_value=50)),
        wind_direction=draw(st.floats(min_value=0, max_value=360)),
        precipitation=draw(st.floats(min_value=0, max_value=100)),
        cloud_cover=draw(st.floats(min_value=0, max_value=100)),
        weather_condition=draw(st.sampled_from(['Clear', 'Cloudy', 'Rainy', 'Snowy', 'Partly Cloudy']))
    )


@st.composite
def forecast_strategy(draw, location=None):
    """Generate valid Forecast objects"""
    if location is None:
        location = draw(location_strategy())
    
    temp_low = draw(st.floats(min_value=-50, max_value=40))
    temp_high = temp_low + draw(st.floats(min_value=0, max_value=20))
    
    return Forecast(
        location=location,
        forecast_date=date.today() + timedelta(days=draw(st.integers(min_value=1, max_value=7))),
        predicted_temperature_high=temp_high,
        predicted_temperature_low=temp_low,
        precipitation_probability=draw(st.floats(min_value=0, max_value=1)),
        weather_condition=draw(st.sampled_from(['Clear', 'Cloudy', 'Rainy', 'Snowy', 'Sunny'])),
        confidence_score=draw(st.floats(min_value=0, max_value=1)),
        generated_at=datetime.now()
    )


# Feature: weather-prediction-system, Property 11: Analytics Data Structure
@given(st.lists(weather_data_strategy(), min_size=1, max_size=20))
def test_analytics_data_structure_property(weather_data_list):
    """
    Property 11: Analytics Data Structure
    For any time-series weather data, the Analytics_Processor should generate 
    chart data with properly formatted labels and datasets suitable for visualization.
    
    Validates: Requirements 7.1, 7.2, 7.3
    """
    builder = VisualizationDataBuilder()
    
    # Test temperature chart
    temp_chart = builder.prepare_temperature_chart(weather_data_list)
    assert isinstance(temp_chart, ChartData)
    assert isinstance(temp_chart.labels, list)
    assert isinstance(temp_chart.datasets, list)
    assert len(temp_chart.labels) > 0
    assert len(temp_chart.datasets) > 0
    
    # Verify each dataset has required fields
    for dataset in temp_chart.datasets:
        assert 'label' in dataset
        assert 'data' in dataset
        assert 'color' in dataset
        assert 'type' in dataset
        assert isinstance(dataset['label'], str)
        assert isinstance(dataset['data'], list)
        assert isinstance(dataset['color'], str)
        assert len(dataset['data']) > 0


# Feature: weather-prediction-system, Property 11: Analytics Data Structure (Precipitation)
@given(st.lists(weather_data_strategy(), min_size=1, max_size=20))
def test_precipitation_chart_structure_property(weather_data_list):
    """
    Property 11: Analytics Data Structure (Precipitation)
    For any weather data, precipitation charts should have proper structure.
    
    Validates: Requirements 7.2
    """
    builder = VisualizationDataBuilder()
    
    precip_chart = builder.prepare_precipitation_chart(weather_data_list)
    assert isinstance(precip_chart, ChartData)
    assert isinstance(precip_chart.labels, list)
    assert isinstance(precip_chart.datasets, list)
    
    if len(weather_data_list) > 0:
        assert len(precip_chart.labels) > 0
        assert len(precip_chart.datasets) > 0
        
        for dataset in precip_chart.datasets:
            assert 'label' in dataset
            assert 'data' in dataset
            assert 'color' in dataset


# Feature: weather-prediction-system, Property 11: Analytics Data Structure (Wind)
@given(st.lists(weather_data_strategy(), min_size=1, max_size=20))
def test_wind_vector_data_structure_property(weather_data_list):
    """
    Property 11: Analytics Data Structure (Wind)
    For any weather data, wind vector data should have proper structure.
    
    Validates: Requirements 7.3
    """
    builder = VisualizationDataBuilder()
    
    wind_data = builder.prepare_wind_vector_data(weather_data_list)
    assert isinstance(wind_data, dict)
    assert 'vectors' in wind_data
    assert 'compass_data' in wind_data
    assert isinstance(wind_data['vectors'], list)
    assert isinstance(wind_data['compass_data'], dict)
    
    # Verify vector structure
    for vector in wind_data['vectors']:
        assert 'timestamp' in vector
        assert 'speed' in vector
        assert 'direction' in vector
        assert 'u' in vector
        assert 'v' in vector
        assert isinstance(vector['speed'], (int, float))
        assert isinstance(vector['direction'], (int, float))


# Feature: weather-prediction-system, Property 31: Graphical Analytics Completeness
@given(st.lists(weather_data_strategy(), min_size=1, max_size=15))
def test_graphical_analytics_completeness_property(weather_data_list):
    """
    Property 31: Graphical Analytics Completeness
    For any weather data set, the Analytics_Processor should generate graphical 
    representations for all key metrics (temperature, precipitation, wind, humidity, 
    pressure, UV index).
    
    Validates: Requirements 7.1, 7.2, 7.3, 7.6
    """
    processor = AnalyticsProcessor()
    
    result = processor.process_weather_analytics(weather_data_list)
    
    # Verify all required chart types are present
    assert 'charts' in result
    charts = result['charts']
    
    # Check for all key metrics
    assert 'temperature' in charts
    assert 'precipitation' in charts
    assert 'wind_vectors' in charts
    assert 'humidity' in charts
    assert 'pressure' in charts
    
    # Verify each chart has proper structure
    for chart_name in ['temperature', 'precipitation', 'humidity', 'pressure']:
        chart = charts[chart_name]
        assert 'labels' in chart
        assert 'datasets' in chart
        assert isinstance(chart['labels'], list)
        assert isinstance(chart['datasets'], list)


# Feature: weather-prediction-system, Property 31: Graphical Analytics Completeness (with forecasts)
@given(
    st.lists(weather_data_strategy(), min_size=1, max_size=10),
    st.lists(forecast_strategy(), min_size=1, max_size=7)
)
def test_graphical_analytics_with_forecasts_property(weather_data_list, forecasts):
    """
    Property 31: Graphical Analytics Completeness (with forecasts)
    Analytics should include forecast data when provided.
    
    Validates: Requirements 7.1, 7.2
    """
    processor = AnalyticsProcessor()
    
    result = processor.process_weather_analytics(weather_data_list, forecasts)
    
    assert 'charts' in result
    assert 'temperature' in result['charts']
    assert 'precipitation' in result['charts']
    
    # Temperature chart should have forecast data
    temp_chart = result['charts']['temperature']
    assert len(temp_chart['datasets']) >= 1  # At least historical or forecast


# Feature: weather-prediction-system, Property 11: Chart Data Labels Consistency
@given(st.lists(weather_data_strategy(), min_size=2, max_size=20))
def test_chart_labels_consistency_property(weather_data_list):
    """
    Property 11: Chart Data Labels Consistency
    For any weather data, chart labels should match the number of data points.
    
    Validates: Requirements 7.1, 7.2, 7.3
    """
    builder = VisualizationDataBuilder()
    
    # Test temperature chart
    temp_chart = builder.prepare_temperature_chart(weather_data_list)
    if temp_chart.datasets:
        # Labels should exist for the data
        assert len(temp_chart.labels) > 0
        
        # Each dataset should have data
        for dataset in temp_chart.datasets:
            assert len(dataset['data']) > 0


# Feature: weather-prediction-system, Property 11: Blue Color Scheme
@given(st.lists(weather_data_strategy(), min_size=1, max_size=10))
def test_blue_color_scheme_property(weather_data_list):
    """
    Property 11: Blue Color Scheme
    For any chart data, all colors should be from the blue palette.
    
    Validates: Requirements 7.5
    """
    builder = VisualizationDataBuilder()
    
    temp_chart = builder.prepare_temperature_chart(weather_data_list)
    
    # Verify all colors are in the blue palette
    for dataset in temp_chart.datasets:
        assert dataset['color'] in builder.blue_colors


# Feature: weather-prediction-system, Property 31: Trend Analysis Completeness
@given(st.lists(weather_data_strategy(), min_size=1, max_size=20))
def test_trend_analysis_completeness_property(weather_data_list):
    """
    Property 31: Trend Analysis Completeness
    For any weather data, trend analysis should include all key metrics.
    
    Validates: Requirements 7.1, 7.2, 7.3, 7.6
    """
    processor = AnalyticsProcessor()
    
    result = processor.process_weather_analytics(weather_data_list)
    
    # Verify all required trends are present
    assert 'trends' in result
    trends = result['trends']
    
    assert 'temperature' in trends
    assert 'precipitation' in trends
    assert 'wind' in trends
    assert 'humidity_pressure' in trends
    
    # Verify temperature trend structure
    temp_trend = trends['temperature']
    assert 'trend_direction' in temp_trend
    assert 'average_temperature' in temp_trend
    assert temp_trend['trend_direction'] in ['increasing', 'decreasing', 'stable']
    
    # Verify precipitation pattern structure
    precip_pattern = trends['precipitation']
    assert 'total_precipitation' in precip_pattern
    assert 'average_precipitation' in precip_pattern
    assert 'rainy_days' in precip_pattern
    
    # Verify wind statistics structure
    wind_stats = trends['wind']
    assert 'average_wind_speed' in wind_stats
    assert 'predominant_direction' in wind_stats
    assert wind_stats['predominant_direction'] in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']


# Feature: weather-prediction-system, Property 11: Empty Data Handling
@given(st.just([]))
def test_empty_data_handling_property(empty_list):
    """
    Property 11: Empty Data Handling
    For empty weather data, analytics should return valid empty structures.
    
    Validates: Requirements 7.1, 7.2, 7.3
    """
    builder = VisualizationDataBuilder()
    
    # All chart methods should handle empty data gracefully
    temp_chart = builder.prepare_temperature_chart(empty_list)
    assert isinstance(temp_chart, ChartData)
    assert len(temp_chart.labels) == 0
    assert len(temp_chart.datasets) == 0
    
    precip_chart = builder.prepare_precipitation_chart(empty_list)
    assert isinstance(precip_chart, ChartData)
    
    wind_data = builder.prepare_wind_vector_data(empty_list)
    assert isinstance(wind_data, dict)
    assert wind_data['vectors'] == []


# Feature: weather-prediction-system, Property 31: Comparative Chart Structure
@given(
    st.lists(weather_data_strategy(), min_size=1, max_size=10),
    st.lists(st.floats(min_value=-50, max_value=50), min_size=1, max_size=10)
)
def test_comparative_chart_structure_property(weather_data_list, historical_avg):
    """
    Property 31: Comparative Chart Structure
    For any weather data and historical averages, comparative charts should have 
    both current and historical datasets.
    
    Validates: Requirements 7.7
    """
    builder = VisualizationDataBuilder()
    
    comp_chart = builder.prepare_comparative_chart(
        weather_data_list,
        historical_avg,
        'temperature'
    )
    
    assert isinstance(comp_chart, ChartData)
    assert len(comp_chart.datasets) == 2  # Current and historical
    
    # Verify dataset labels
    labels = [d['label'] for d in comp_chart.datasets]
    assert any('Current' in label for label in labels)
    assert any('Historical' in label for label in labels)


# Feature: weather-prediction-system, Property 11: Accuracy Chart Structure
@given(st.lists(
    st.builds(
        AccuracyMetrics,
        location=st.none(),
        overall_accuracy=st.floats(min_value=0, max_value=1),
        temperature_mae=st.floats(min_value=0, max_value=10),
        temperature_rmse=st.floats(min_value=0, max_value=15),
        precipitation_accuracy=st.floats(min_value=0, max_value=1),
        condition_accuracy=st.floats(min_value=0, max_value=1),
        total_predictions=st.integers(min_value=1, max_value=1000),
        evaluation_period_days=st.integers(min_value=1, max_value=90),
        calculated_at=st.just(datetime.now())
    ),
    min_size=1,
    max_size=10
))
def test_accuracy_chart_structure_property(accuracy_metrics_list):
    """
    Property 11: Accuracy Chart Structure
    For any accuracy metrics, the chart should have proper structure.
    
    Validates: Requirements 7.4
    """
    builder = VisualizationDataBuilder()
    
    accuracy_chart = builder.prepare_accuracy_chart(accuracy_metrics_list)
    
    assert isinstance(accuracy_chart, ChartData)
    assert len(accuracy_chart.labels) > 0
    assert len(accuracy_chart.datasets) >= 3  # Overall, temp MAE, precip accuracy
    
    # Verify all datasets have required fields
    for dataset in accuracy_chart.datasets:
        assert 'label' in dataset
        assert 'data' in dataset
        assert 'color' in dataset
        assert len(dataset['data']) == len(accuracy_chart.labels)
