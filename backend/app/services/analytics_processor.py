"""Analytics processor for weather data visualization and trend analysis"""
import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
from statistics import mean, stdev
import math
from app.models import WeatherData, Forecast, ChartData, Location, AccuracyMetrics

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Analyzes weather trends and patterns"""
    
    def __init__(self):
        """Initialize trend analyzer"""
        pass

    def calculate_temperature_trend(
        self, 
        weather_data_list: List[WeatherData], 
        days: int = 7
    ) -> Dict[str, any]:
        """Calculate temperature trends over time
        
        Args:
            weather_data_list: List of historical weather data
            days: Number of days to analyze
            
        Returns:
            Dictionary with trend analysis results
        """
        if not weather_data_list:
            return {
                'trend_direction': 'stable',
                'average_temperature': 0.0,
                'temperature_change': 0.0,
                'min_temperature': 0.0,
                'max_temperature': 0.0
            }
        
        # Sort by timestamp
        sorted_data = sorted(weather_data_list, key=lambda x: x.timestamp)
        
        # Calculate statistics
        temperatures = [data.temperature for data in sorted_data]
        avg_temp = mean(temperatures)
        min_temp = min(temperatures)
        max_temp = max(temperatures)
        
        # Calculate trend direction
        if len(temperatures) >= 2:
            first_half = temperatures[:len(temperatures)//2]
            second_half = temperatures[len(temperatures)//2:]
            
            avg_first = mean(first_half)
            avg_second = mean(second_half)
            temp_change = avg_second - avg_first
            
            if temp_change > 1.0:
                trend_direction = 'increasing'
            elif temp_change < -1.0:
                trend_direction = 'decreasing'
            else:
                trend_direction = 'stable'
        else:
            trend_direction = 'stable'
            temp_change = 0.0
        
        return {
            'trend_direction': trend_direction,
            'average_temperature': round(avg_temp, 2),
            'temperature_change': round(temp_change, 2),
            'min_temperature': round(min_temp, 2),
            'max_temperature': round(max_temp, 2),
            'data_points': len(temperatures)
        }

    def calculate_precipitation_pattern(
        self, 
        weather_data_list: List[WeatherData]
    ) -> Dict[str, any]:
        """Calculate precipitation patterns
        
        Args:
            weather_data_list: List of historical weather data
            
        Returns:
            Dictionary with precipitation pattern analysis
        """
        if not weather_data_list:
            return {
                'total_precipitation': 0.0,
                'average_precipitation': 0.0,
                'rainy_days': 0,
                'precipitation_probability': 0.0
            }
        
        precipitations = [data.precipitation for data in weather_data_list]
        total_precip = sum(precipitations)
        avg_precip = mean(precipitations)
        rainy_days = sum(1 for p in precipitations if p > 0.1)  # > 0.1mm counts as rain
        precip_probability = rainy_days / len(precipitations) if precipitations else 0.0
        
        return {
            'total_precipitation': round(total_precip, 2),
            'average_precipitation': round(avg_precip, 2),
            'rainy_days': rainy_days,
            'precipitation_probability': round(precip_probability, 2)
        }

    def calculate_wind_statistics(
        self, 
        weather_data_list: List[WeatherData]
    ) -> Dict[str, any]:
        """Calculate wind speed and direction statistics
        
        Args:
            weather_data_list: List of historical weather data
            
        Returns:
            Dictionary with wind statistics
        """
        if not weather_data_list:
            return {
                'average_wind_speed': 0.0,
                'max_wind_speed': 0.0,
                'predominant_direction': 'N',
                'wind_variability': 0.0
            }
        
        wind_speeds = [data.wind_speed for data in weather_data_list]
        wind_directions = [data.wind_direction for data in weather_data_list]
        
        avg_speed = mean(wind_speeds)
        max_speed = max(wind_speeds)
        
        # Calculate predominant wind direction
        # Divide into 8 compass directions
        direction_bins = {
            'N': 0, 'NE': 0, 'E': 0, 'SE': 0,
            'S': 0, 'SW': 0, 'W': 0, 'NW': 0
        }
        
        for direction in wind_directions:
            if 337.5 <= direction or direction < 22.5:
                direction_bins['N'] += 1
            elif 22.5 <= direction < 67.5:
                direction_bins['NE'] += 1
            elif 67.5 <= direction < 112.5:
                direction_bins['E'] += 1
            elif 112.5 <= direction < 157.5:
                direction_bins['SE'] += 1
            elif 157.5 <= direction < 202.5:
                direction_bins['S'] += 1
            elif 202.5 <= direction < 247.5:
                direction_bins['SW'] += 1
            elif 247.5 <= direction < 292.5:
                direction_bins['W'] += 1
            elif 292.5 <= direction < 337.5:
                direction_bins['NW'] += 1
        
        predominant_direction = max(direction_bins, key=direction_bins.get)
        
        # Calculate wind variability (standard deviation)
        wind_variability = stdev(wind_speeds) if len(wind_speeds) > 1 else 0.0
        
        return {
            'average_wind_speed': round(avg_speed, 2),
            'max_wind_speed': round(max_speed, 2),
            'predominant_direction': predominant_direction,
            'wind_variability': round(wind_variability, 2)
        }

    def calculate_humidity_pressure_stats(
        self, 
        weather_data_list: List[WeatherData]
    ) -> Dict[str, any]:
        """Calculate humidity and pressure statistics
        
        Args:
            weather_data_list: List of historical weather data
            
        Returns:
            Dictionary with humidity and pressure statistics
        """
        if not weather_data_list:
            return {
                'average_humidity': 0.0,
                'average_pressure': 0.0,
                'humidity_range': (0.0, 0.0),
                'pressure_range': (0.0, 0.0)
            }
        
        humidities = [data.humidity for data in weather_data_list]
        pressures = [data.pressure for data in weather_data_list]
        
        return {
            'average_humidity': round(mean(humidities), 2),
            'average_pressure': round(mean(pressures), 2),
            'humidity_range': (round(min(humidities), 2), round(max(humidities), 2)),
            'pressure_range': (round(min(pressures), 2), round(max(pressures), 2))
        }


class VisualizationDataBuilder:
    """Builds data structures for frontend chart visualization"""
    
    def __init__(self):
        """Initialize visualization data builder"""
        self.blue_colors = ['#0066CC', '#4A90E2', '#1E3A8A', '#3B82F6', '#60A5FA']

    def prepare_temperature_chart(
        self, 
        weather_data_list: List[WeatherData],
        forecasts: Optional[List[Forecast]] = None
    ) -> ChartData:
        """Prepare temperature trend chart data
        
        Args:
            weather_data_list: Historical weather data
            forecasts: Optional forecast data
            
        Returns:
            ChartData for temperature visualization
        """
        if not weather_data_list and not forecasts:
            return ChartData(labels=[], datasets=[])
        
        labels = []
        historical_temps = []
        forecast_temps_high = []
        forecast_temps_low = []
        
        # Process historical data
        if weather_data_list:
            sorted_data = sorted(weather_data_list, key=lambda x: x.timestamp)
            for data in sorted_data:
                labels.append(data.timestamp.strftime('%Y-%m-%d %H:%M'))
                historical_temps.append(data.temperature)
        
        # Process forecast data
        if forecasts:
            sorted_forecasts = sorted(forecasts, key=lambda x: x.forecast_date)
            for forecast in sorted_forecasts:
                label = forecast.forecast_date.strftime('%Y-%m-%d')
                if label not in labels:
                    labels.append(label)
                forecast_temps_high.append(forecast.predicted_temperature_high)
                forecast_temps_low.append(forecast.predicted_temperature_low)
        
        datasets = []
        
        if historical_temps:
            datasets.append({
                'label': 'Historical Temperature',
                'data': historical_temps,
                'color': self.blue_colors[0],
                'type': 'line'
            })
        
        if forecast_temps_high:
            datasets.append({
                'label': 'Forecast High',
                'data': forecast_temps_high,
                'color': self.blue_colors[1],
                'type': 'line'
            })
        
        if forecast_temps_low:
            datasets.append({
                'label': 'Forecast Low',
                'data': forecast_temps_low,
                'color': self.blue_colors[2],
                'type': 'line'
            })
        
        return ChartData(labels=labels, datasets=datasets)

    def prepare_precipitation_chart(
        self, 
        weather_data_list: List[WeatherData],
        forecasts: Optional[List[Forecast]] = None
    ) -> ChartData:
        """Prepare precipitation probability chart data
        
        Args:
            weather_data_list: Historical weather data
            forecasts: Optional forecast data
            
        Returns:
            ChartData for precipitation visualization
        """
        labels = []
        historical_precip = []
        forecast_precip_prob = []
        
        # Process historical data
        if weather_data_list:
            sorted_data = sorted(weather_data_list, key=lambda x: x.timestamp)
            for data in sorted_data:
                labels.append(data.timestamp.strftime('%Y-%m-%d %H:%M'))
                historical_precip.append(data.precipitation)
        
        # Process forecast data
        if forecasts:
            sorted_forecasts = sorted(forecasts, key=lambda x: x.forecast_date)
            for forecast in sorted_forecasts:
                label = forecast.forecast_date.strftime('%Y-%m-%d')
                if label not in labels:
                    labels.append(label)
                # Convert probability to percentage
                forecast_precip_prob.append(forecast.precipitation_probability * 100)
        
        datasets = []
        
        if historical_precip:
            datasets.append({
                'label': 'Historical Precipitation (mm)',
                'data': historical_precip,
                'color': self.blue_colors[0],
                'type': 'bar'
            })
        
        if forecast_precip_prob:
            datasets.append({
                'label': 'Forecast Precipitation Probability (%)',
                'data': forecast_precip_prob,
                'color': self.blue_colors[3],
                'type': 'bar'
            })
        
        return ChartData(labels=labels, datasets=datasets)

    def prepare_wind_vector_data(
        self, 
        weather_data_list: List[WeatherData]
    ) -> Dict[str, any]:
        """Prepare wind vector graphics data
        
        Args:
            weather_data_list: Historical weather data
            
        Returns:
            Dictionary with wind vector data for compass visualization
        """
        if not weather_data_list:
            return {
                'vectors': [],
                'compass_data': {}
            }
        
        vectors = []
        for data in weather_data_list:
            # Convert wind direction and speed to vector components
            direction_rad = math.radians(data.wind_direction)
            u_component = data.wind_speed * math.sin(direction_rad)
            v_component = data.wind_speed * math.cos(direction_rad)
            
            vectors.append({
                'timestamp': data.timestamp.strftime('%Y-%m-%d %H:%M'),
                'speed': round(data.wind_speed, 2),
                'direction': round(data.wind_direction, 2),
                'u': round(u_component, 2),
                'v': round(v_component, 2)
            })
        
        # Calculate compass data (direction frequency)
        direction_bins = {
            'N': 0, 'NE': 0, 'E': 0, 'SE': 0,
            'S': 0, 'SW': 0, 'W': 0, 'NW': 0
        }
        
        for data in weather_data_list:
            direction = data.wind_direction
            if 337.5 <= direction or direction < 22.5:
                direction_bins['N'] += 1
            elif 22.5 <= direction < 67.5:
                direction_bins['NE'] += 1
            elif 67.5 <= direction < 112.5:
                direction_bins['E'] += 1
            elif 112.5 <= direction < 157.5:
                direction_bins['SE'] += 1
            elif 157.5 <= direction < 202.5:
                direction_bins['S'] += 1
            elif 202.5 <= direction < 247.5:
                direction_bins['SW'] += 1
            elif 247.5 <= direction < 292.5:
                direction_bins['W'] += 1
            elif 292.5 <= direction < 337.5:
                direction_bins['NW'] += 1
        
        return {
            'vectors': vectors,
            'compass_data': direction_bins
        }

    def prepare_humidity_chart(
        self, 
        weather_data_list: List[WeatherData]
    ) -> ChartData:
        """Prepare humidity chart data
        
        Args:
            weather_data_list: Historical weather data
            
        Returns:
            ChartData for humidity visualization
        """
        if not weather_data_list:
            return ChartData(labels=[], datasets=[])
        
        sorted_data = sorted(weather_data_list, key=lambda x: x.timestamp)
        labels = [data.timestamp.strftime('%Y-%m-%d %H:%M') for data in sorted_data]
        humidity_values = [data.humidity for data in sorted_data]
        
        datasets = [{
            'label': 'Humidity (%)',
            'data': humidity_values,
            'color': self.blue_colors[1],
            'type': 'area'
        }]
        
        return ChartData(labels=labels, datasets=datasets)

    def prepare_pressure_chart(
        self, 
        weather_data_list: List[WeatherData]
    ) -> ChartData:
        """Prepare atmospheric pressure chart data
        
        Args:
            weather_data_list: Historical weather data
            
        Returns:
            ChartData for pressure visualization
        """
        if not weather_data_list:
            return ChartData(labels=[], datasets=[])
        
        sorted_data = sorted(weather_data_list, key=lambda x: x.timestamp)
        labels = [data.timestamp.strftime('%Y-%m-%d %H:%M') for data in sorted_data]
        pressure_values = [data.pressure for data in sorted_data]
        
        datasets = [{
            'label': 'Atmospheric Pressure (hPa)',
            'data': pressure_values,
            'color': self.blue_colors[2],
            'type': 'line'
        }]
        
        return ChartData(labels=labels, datasets=datasets)

    def prepare_accuracy_chart(
        self, 
        accuracy_metrics_list: List[AccuracyMetrics]
    ) -> ChartData:
        """Prepare accuracy metrics chart data
        
        Args:
            accuracy_metrics_list: List of accuracy metrics over time
            
        Returns:
            ChartData for accuracy visualization
        """
        if not accuracy_metrics_list:
            return ChartData(labels=[], datasets=[])
        
        sorted_metrics = sorted(accuracy_metrics_list, key=lambda x: x.calculated_at)
        labels = [m.calculated_at.strftime('%Y-%m-%d') for m in sorted_metrics]
        overall_accuracy = [m.overall_accuracy * 100 for m in sorted_metrics]
        temp_mae = [m.temperature_mae for m in sorted_metrics]
        precip_accuracy = [m.precipitation_accuracy * 100 for m in sorted_metrics]
        
        datasets = [
            {
                'label': 'Overall Accuracy (%)',
                'data': overall_accuracy,
                'color': self.blue_colors[0],
                'type': 'line'
            },
            {
                'label': 'Temperature MAE (°C)',
                'data': temp_mae,
                'color': self.blue_colors[1],
                'type': 'line'
            },
            {
                'label': 'Precipitation Accuracy (%)',
                'data': precip_accuracy,
                'color': self.blue_colors[3],
                'type': 'line'
            }
        ]
        
        return ChartData(labels=labels, datasets=datasets)

    def prepare_comparative_chart(
        self, 
        current_data: List[WeatherData],
        historical_average: List[float],
        metric: str = 'temperature'
    ) -> ChartData:
        """Prepare comparative chart (current vs historical average)
        
        Args:
            current_data: Current weather data
            historical_average: Historical average values
            metric: Metric to compare ('temperature', 'precipitation', etc.)
            
        Returns:
            ChartData for comparative visualization
        """
        if not current_data:
            return ChartData(labels=[], datasets=[])
        
        sorted_data = sorted(current_data, key=lambda x: x.timestamp)
        labels = [data.timestamp.strftime('%Y-%m-%d') for data in sorted_data]
        
        # Extract current values based on metric
        if metric == 'temperature':
            current_values = [data.temperature for data in sorted_data]
            label_current = 'Current Temperature (°C)'
            label_historical = 'Historical Average Temperature (°C)'
        elif metric == 'precipitation':
            current_values = [data.precipitation for data in sorted_data]
            label_current = 'Current Precipitation (mm)'
            label_historical = 'Historical Average Precipitation (mm)'
        elif metric == 'humidity':
            current_values = [data.humidity for data in sorted_data]
            label_current = 'Current Humidity (%)'
            label_historical = 'Historical Average Humidity (%)'
        else:
            current_values = [data.temperature for data in sorted_data]
            label_current = f'Current {metric}'
            label_historical = f'Historical Average {metric}'
        
        # Ensure historical_average matches length
        if len(historical_average) < len(current_values):
            historical_average = historical_average + [historical_average[-1]] * (len(current_values) - len(historical_average)) if historical_average else [0] * len(current_values)
        
        datasets = [
            {
                'label': label_current,
                'data': current_values,
                'color': self.blue_colors[0],
                'type': 'line'
            },
            {
                'label': label_historical,
                'data': historical_average[:len(current_values)],
                'color': self.blue_colors[4],
                'type': 'line'
            }
        ]
        
        return ChartData(labels=labels, datasets=datasets)


class AnalyticsProcessor:
    """Main analytics processor combining trend analysis and visualization"""
    
    def __init__(self):
        """Initialize analytics processor"""
        self.trend_analyzer = TrendAnalyzer()
        self.viz_builder = VisualizationDataBuilder()

    def process_weather_analytics(
        self, 
        weather_data_list: List[WeatherData],
        forecasts: Optional[List[Forecast]] = None,
        accuracy_metrics: Optional[List[AccuracyMetrics]] = None
    ) -> Dict[str, any]:
        """Process complete weather analytics
        
        Args:
            weather_data_list: Historical weather data
            forecasts: Optional forecast data
            accuracy_metrics: Optional accuracy metrics
            
        Returns:
            Dictionary with all analytics and chart data
        """
        # Calculate trends
        temp_trend = self.trend_analyzer.calculate_temperature_trend(weather_data_list)
        precip_pattern = self.trend_analyzer.calculate_precipitation_pattern(weather_data_list)
        wind_stats = self.trend_analyzer.calculate_wind_statistics(weather_data_list)
        humidity_pressure = self.trend_analyzer.calculate_humidity_pressure_stats(weather_data_list)
        
        # Prepare chart data
        temp_chart = self.viz_builder.prepare_temperature_chart(weather_data_list, forecasts)
        precip_chart = self.viz_builder.prepare_precipitation_chart(weather_data_list, forecasts)
        wind_vector_data = self.viz_builder.prepare_wind_vector_data(weather_data_list)
        humidity_chart = self.viz_builder.prepare_humidity_chart(weather_data_list)
        pressure_chart = self.viz_builder.prepare_pressure_chart(weather_data_list)
        
        result = {
            'trends': {
                'temperature': temp_trend,
                'precipitation': precip_pattern,
                'wind': wind_stats,
                'humidity_pressure': humidity_pressure
            },
            'charts': {
                'temperature': temp_chart.model_dump(),
                'precipitation': precip_chart.model_dump(),
                'wind_vectors': wind_vector_data,
                'humidity': humidity_chart.model_dump(),
                'pressure': pressure_chart.model_dump()
            }
        }
        
        # Add accuracy chart if metrics provided
        if accuracy_metrics:
            accuracy_chart = self.viz_builder.prepare_accuracy_chart(accuracy_metrics)
            result['charts']['accuracy'] = accuracy_chart.model_dump()
        
        return result
