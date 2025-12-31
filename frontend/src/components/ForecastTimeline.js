import { useWeather } from '../context/WeatherContext';
import WeatherCard from './WeatherCard';
import './ForecastTimeline.css';

const ForecastTimeline = () => {
  const { forecast } = useWeather();

  if (!forecast || forecast.length === 0) {
    return null;
  }

  // Format date
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return 'Tomorrow';
    } else {
      return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    }
  };

  // Get weather icon
  const getWeatherIcon = (condition) => {
    const icons = {
      clear: '☀️',
      sunny: '☀️',
      cloudy: '☁️',
      'partly cloudy': '⛅',
      overcast: '☁️',
      rainy: '🌧️',
      rain: '🌧️',
      stormy: '⛈️',
      storm: '⛈️',
      snowy: '❄️',
      snow: '❄️',
      foggy: '🌫️',
      fog: '🌫️',
      windy: '💨',
    };
    return icons[condition?.toLowerCase()] || '🌤️';
  };

  // Get confidence color
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#10b981'; // green
    if (confidence >= 0.6) return '#f59e0b'; // orange
    return '#ef4444'; // red
  };

  // Get confidence label
  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <WeatherCard title="7-Day Forecast" className="forecast-timeline-card">
      <div className="forecast-timeline">
        {forecast.map((day, index) => (
          <div key={index} className="forecast-day">
            <div className="forecast-date">{formatDate(day.date)}</div>
            
            <div className="forecast-icon">
              {getWeatherIcon(day.condition)}
            </div>

            <div className="forecast-condition">{day.condition}</div>

            <div className="forecast-temps">
              <span className="temp-high">{Math.round(day.temperature_high)}°</span>
              <span className="temp-separator">/</span>
              <span className="temp-low">{Math.round(day.temperature_low)}°</span>
            </div>

            {day.precipitation_probability !== null && day.precipitation_probability !== undefined && (
              <div className="forecast-precipitation">
                <span className="precip-icon">💧</span>
                <span className="precip-value">{Math.round(day.precipitation_probability * 100)}%</span>
              </div>
            )}

            {day.confidence_score !== null && day.confidence_score !== undefined && (
              <div className="forecast-confidence">
                <div 
                  className="confidence-bar"
                  style={{ 
                    width: `${day.confidence_score * 100}%`,
                    backgroundColor: getConfidenceColor(day.confidence_score)
                  }}
                />
                <div className="confidence-label">
                  {getConfidenceLabel(day.confidence_score)} confidence
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </WeatherCard>
  );
};

export default ForecastTimeline;
