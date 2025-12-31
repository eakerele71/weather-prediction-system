"""Unit tests for analytics processor"""
import pytest
from datetime import datetime, timedelta, date
from app.services.analytics_processor import (
    TrendAnalyzer, 
    VisualizationDataBuilder, 
    AnalyticsProcessor
)
from app.models import WeatherData, Forecast, Location, ChartData, AccuracyMetrics


@pytest.fixture
def sample_location():
    """Sample location for testing"""
    return Location(
        latitude=47.6062,
        longitude=-122.3321,
        city="Seattle",
        country="United States"
    )


@pytest.fixture
def sample_weather_data_list(sample_location):
    """Sample weather data list for testing"""
    base_time = datetime.now()
    data_list = []
    
    for i in range(7):
        data = WeatherData(
            location=sample_location,
            timestamp=base_time + timedelta(days=i),
            temperature=15.0 + i * 0.5,  # Increasing trend
            humidity=60.0 + i * 2,
            pressure=1013.0 + i,
            wind_speed=5.0 + i * 0.3,
            wind_direction=180.0 + i * 10,
            precipitation=0.5 * i,
            cloud_cover=40.0,
            weather_condition="Partly Cloudy"
        )
        data_list.append(data)
    
    return data_list


@pytest.fixture
def sample_forecasts(sample_location):
    """Sample forecast list for testing"""
    base_date = date.today()
    forecasts = []
    
    for i in range(7):
        forecast = Forecast(
            location=sample_location,
            forecast_date=base_date + timedelta(days=i),
            predicted_temperature_high=20.0 + i,
            predicted_temperature_low=10.0 + i * 0.5,
            precipitation_probability=0.3 + i * 0.05,
            weather_condition="Sunny",
            confidence_score=0.85,
            generated_at=datetime.now()
        )
        forecasts.append(forecast)
    
    return forecasts


@pytest.fixture
def sample_accuracy_metrics(sample_location):
    """Sample accuracy metrics for testing"""
    metrics_list = []
    base_time = datetime.now()
    
    for i in range(5):
        metrics = AccuracyMetrics(
            location=sample_location,
            overall_accuracy=0.80 + i * 0.02,
            temperature_mae=2.5 - i * 0.1,
            temperature_rmse=3.2 - i * 0.1,
            precipitation_accuracy=0.75 + i * 0.03,
            condition_accuracy=0.85,
            total_predictions=50,
            evaluation_period_days=7,
            calculated_at=base_time + timedelta(days=i)
        )
        metrics_list.append(metrics)
    
    return metrics_list


class TestTrendAnalyzer:
    """Test cases for TrendAnalyzer"""
    
    def test_initialization(self):
        """Test TrendAnalyzer initialization"""
        analyzer = TrendAnalyzer()
        assert analyzer is not None

    def test_calculate_temperature_trend_increasing(self, sample_weather_data_list):
        """Test temperature trend calculation with increasing temperatures"""
        analyzer = TrendAnalyzer()
        result = analyzer.calculate_temperature_trend(sample_weather_data_list)
        
        assert result['trend_direction'] == 'increasing'
        assert result['average_temperature'] > 0
        assert result['temperature_change'] > 0
        assert result['min_temperature'] <= result['max_temperature']
        assert result['data_points'] == 7

    def test_calculate_temperature_trend_empty_data(self):
        """Test temperature trend with empty data"""
        analyzer = TrendAnalyzer()
        result = analyzer.calculate_temperature_trend([])
        
        assert result['trend_direction'] == 'stable'
        assert result['average_temperature'] == 0.0
        assert result['temperature_change'] == 0.0

    def test_calculate_precipitation_pattern(self, sample_weather_data_list):
        """Test precipitation pattern calculation"""
        analyzer = TrendAnalyzer()
        result = analyzer.calculate_precipitation_pattern(sample_weather_data_list)
        
        assert 'total_precipitation' in result
        assert 'average_precipitation' in result
        assert 'rainy_days' in result
        assert 'precipitation_probability' in result
        assert result['rainy_days'] >= 0
        assert 0 <= result['precipitation_probability'] <= 1

    def test_calculate_precipitation_pattern_empty_data(self):
        """Test precipitation pattern with empty data"""
        analyzer = TrendAnalyzer()
        result = analyzer.calculate_precipitation_pattern([])
        
        assert result['total_precipitation'] == 0.0
        assert result['rainy_days'] == 0

    def test_calculate_wind_statistics(self, sample_weather_data_list):
        """Test wind statistics calculation"""
        analyzer = TrendAnalyzer()
        result = analyzer.calculate_wind_statistics(sample_weather_data_list)
        
        assert 'average_wind_speed' in result
        assert 'max_wind_speed' in result
        assert 'predominant_direction' in result
        assert 'wind_variability' in result
        assert result['average_wind_speed'] >= 0
        assert result['max_wind_speed'] >= result['average_wind_speed']
        assert result['predominant_direction'] in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

    def test_calculate_wind_statistics_empty_data(self):
        """Test wind statistics with empty data"""
        analyzer = TrendAnalyzer()
        result = analyzer.calculate_wind_statistics([])
        
        assert result['average_wind_speed'] == 0.0
        assert result['predominant_direction'] == 'N'

    def test_calculate_humidity_pressure_stats(self, sample_weather_data_list):
        """Test humidity and pressure statistics"""
        analyzer = TrendAnalyzer()
        result = analyzer.calculate_humidity_pressure_stats(sample_weather_data_list)
        
        assert 'average_humidity' in result
        assert 'average_pressure' in result
        assert 'humidity_range' in result
        assert 'pressure_range' in result
        assert 0 <= result['average_humidity'] <= 100
        assert result['average_pressure'] > 0

    def test_calculate_humidity_pressure_stats_empty_data(self):
        """Test humidity/pressure stats with empty data"""
        analyzer = TrendAnalyzer()
        result = analyzer.calculate_humidity_pressure_stats([])
        
        assert result['average_humidity'] == 0.0
        assert result['average_pressure'] == 0.0


class TestVisualizationDataBuilder:
    """Test cases for VisualizationDataBuilder"""
    
    def test_initialization(self):
        """Test VisualizationDataBuilder initialization"""
        builder = VisualizationDataBuilder()
        assert builder is not None
        assert len(builder.blue_colors) > 0

    def test_prepare_temperature_chart_with_data(self, sample_weather_data_list, sample_forecasts):
        """Test temperature chart preparation with data"""
        builder = VisualizationDataBuilder()
        chart_data = builder.prepare_temperature_chart(sample_weather_data_list, sample_forecasts)
        
        assert isinstance(chart_data, ChartData)
        assert len(chart_data.labels) > 0
        assert len(chart_data.datasets) > 0
        assert any('Temperature' in d['label'] for d in chart_data.datasets)

    def test_prepare_temperature_chart_empty_data(self):
        """Test temperature chart with empty data"""
        builder = VisualizationDataBuilder()
        chart_data = builder.prepare_temperature_chart([], None)
        
        assert isinstance(chart_data, ChartData)
        assert len(chart_data.labels) == 0
        assert len(chart_data.datasets) == 0

    def test_prepare_precipitation_chart(self, sample_weather_data_list, sample_forecasts):
        """Test precipitation chart preparation"""
        builder = VisualizationDataBuilder()
        chart_data = builder.prepare_precipitation_chart(sample_weather_data_list, sample_forecasts)
        
        assert isinstance(chart_data, ChartData)
        assert len(chart_data.labels) > 0
        assert len(chart_data.datasets) > 0

    def test_prepare_wind_vector_data(self, sample_weather_data_list):
        """Test wind vector data preparation"""
        builder = VisualizationDataBuilder()
        wind_data = builder.prepare_wind_vector_data(sample_weather_data_list)
        
        assert 'vectors' in wind_data
        assert 'compass_data' in wind_data
        assert len(wind_data['vectors']) > 0
        assert len(wind_data['compass_data']) == 8  # 8 compass directions

    def test_prepare_wind_vector_data_empty(self):
        """Test wind vector data with empty input"""
        builder = VisualizationDataBuilder()
        wind_data = builder.prepare_wind_vector_data([])
        
        assert wind_data['vectors'] == []
        assert wind_data['compass_data'] == {}

    def test_prepare_humidity_chart(self, sample_weather_data_list):
        """Test humidity chart preparation"""
        builder = VisualizationDataBuilder()
        chart_data = builder.prepare_humidity_chart(sample_weather_data_list)
        
        assert isinstance(chart_data, ChartData)
        assert len(chart_data.labels) > 0
        assert len(chart_data.datasets) == 1
        assert 'Humidity' in chart_data.datasets[0]['label']

    def test_prepare_pressure_chart(self, sample_weather_data_list):
        """Test pressure chart preparation"""
        builder = VisualizationDataBuilder()
        chart_data = builder.prepare_pressure_chart(sample_weather_data_list)
        
        assert isinstance(chart_data, ChartData)
        assert len(chart_data.labels) > 0
        assert len(chart_data.datasets) == 1
        assert 'Pressure' in chart_data.datasets[0]['label']

    def test_prepare_accuracy_chart(self, sample_accuracy_metrics):
        """Test accuracy chart preparation"""
        builder = VisualizationDataBuilder()
        chart_data = builder.prepare_accuracy_chart(sample_accuracy_metrics)
        
        assert isinstance(chart_data, ChartData)
        assert len(chart_data.labels) > 0
        assert len(chart_data.datasets) >= 3  # Overall, temp MAE, precip accuracy

    def test_prepare_accuracy_chart_empty(self):
        """Test accuracy chart with empty data"""
        builder = VisualizationDataBuilder()
        chart_data = builder.prepare_accuracy_chart([])
        
        assert isinstance(chart_data, ChartData)
        assert len(chart_data.labels) == 0

    def test_prepare_comparative_chart_temperature(self, sample_weather_data_list):
        """Test comparative chart for temperature"""
        builder = VisualizationDataBuilder()
        historical_avg = [14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0]
        chart_data = builder.prepare_comparative_chart(
            sample_weather_data_list, 
            historical_avg, 
            'temperature'
        )
        
        assert isinstance(chart_data, ChartData)
        assert len(chart_data.datasets) == 2  # Current and historical
        assert any('Current' in d['label'] for d in chart_data.datasets)
        assert any('Historical' in d['label'] for d in chart_data.datasets)

    def test_prepare_comparative_chart_precipitation(self, sample_weather_data_list):
        """Test comparative chart for precipitation"""
        builder = VisualizationDataBuilder()
        historical_avg = [1.0, 1.2, 1.5, 1.8, 2.0, 2.2, 2.5]
        chart_data = builder.prepare_comparative_chart(
            sample_weather_data_list, 
            historical_avg, 
            'precipitation'
        )
        
        assert isinstance(chart_data, ChartData)
        assert len(chart_data.datasets) == 2

    def test_chart_data_has_blue_colors(self, sample_weather_data_list):
        """Test that chart data uses blue color scheme"""
        builder = VisualizationDataBuilder()
        chart_data = builder.prepare_temperature_chart(sample_weather_data_list)
        
        for dataset in chart_data.datasets:
            assert 'color' in dataset
            # Check if color is in blue palette
            assert dataset['color'] in builder.blue_colors


class TestAnalyticsProcessor:
    """Test cases for AnalyticsProcessor"""
    
    def test_initialization(self):
        """Test AnalyticsProcessor initialization"""
        processor = AnalyticsProcessor()
        assert processor is not None
        assert processor.trend_analyzer is not None
        assert processor.viz_builder is not None

    def test_process_weather_analytics_complete(
        self, 
        sample_weather_data_list, 
        sample_forecasts,
        sample_accuracy_metrics
    ):
        """Test complete weather analytics processing"""
        processor = AnalyticsProcessor()
        result = processor.process_weather_analytics(
            sample_weather_data_list,
            sample_forecasts,
            sample_accuracy_metrics
        )
        
        assert 'trends' in result
        assert 'charts' in result
        
        # Check trends
        assert 'temperature' in result['trends']
        assert 'precipitation' in result['trends']
        assert 'wind' in result['trends']
        assert 'humidity_pressure' in result['trends']
        
        # Check charts
        assert 'temperature' in result['charts']
        assert 'precipitation' in result['charts']
        assert 'wind_vectors' in result['charts']
        assert 'humidity' in result['charts']
        assert 'pressure' in result['charts']
        assert 'accuracy' in result['charts']

    def test_process_weather_analytics_without_forecasts(self, sample_weather_data_list):
        """Test analytics processing without forecasts"""
        processor = AnalyticsProcessor()
        result = processor.process_weather_analytics(sample_weather_data_list)
        
        assert 'trends' in result
        assert 'charts' in result
        assert 'accuracy' not in result['charts']

    def test_process_weather_analytics_without_accuracy(
        self, 
        sample_weather_data_list,
        sample_forecasts
    ):
        """Test analytics processing without accuracy metrics"""
        processor = AnalyticsProcessor()
        result = processor.process_weather_analytics(
            sample_weather_data_list,
            sample_forecasts,
            None
        )
        
        assert 'trends' in result
        assert 'charts' in result
        assert 'accuracy' not in result['charts']

    def test_analytics_output_structure(self, sample_weather_data_list):
        """Test that analytics output has correct structure"""
        processor = AnalyticsProcessor()
        result = processor.process_weather_analytics(sample_weather_data_list)
        
        # Verify trends structure
        assert isinstance(result['trends'], dict)
        assert isinstance(result['trends']['temperature'], dict)
        assert 'trend_direction' in result['trends']['temperature']
        
        # Verify charts structure
        assert isinstance(result['charts'], dict)
        assert isinstance(result['charts']['temperature'], dict)
        assert 'labels' in result['charts']['temperature']
        assert 'datasets' in result['charts']['temperature']

    def test_analytics_with_minimal_data(self, sample_location):
        """Test analytics with minimal data (single data point)"""
        processor = AnalyticsProcessor()
        
        single_data = [WeatherData(
            location=sample_location,
            timestamp=datetime.now(),
            temperature=15.0,
            humidity=60.0,
            pressure=1013.0,
            wind_speed=5.0,
            wind_direction=180.0,
            precipitation=0.0,
            cloud_cover=40.0,
            weather_condition="Clear"
        )]
        
        result = processor.process_weather_analytics(single_data)
        
        assert 'trends' in result
        assert 'charts' in result
        assert result['trends']['temperature']['data_points'] == 1
