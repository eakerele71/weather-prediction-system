import { useWeather } from '../context/WeatherContext';
import WeatherCard from './WeatherCard';
import AddToFavorites from './AddToFavorites';
import './CurrentWeatherCard.css';

const CurrentWeatherCard = () => {
  const { currentWeather, currentLocation } = useWeather();

  if (!currentWeather || !currentLocation) {
    return null;
  }

  const {
    temperature,
    feels_like,
    condition,
    humidity,
    pressure,
    wind_speed,
    wind_direction,
    visibility,
    uv_index,
    timestamp,
  } = currentWeather;

  // Format timestamp
  const formatTime = (ts) => {
    if (!ts) return '';
    const date = new Date(ts);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Get weather icon based on condition
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

  // Get wind direction arrow
  const getWindDirection = (degrees) => {
    if (degrees === null || degrees === undefined) return 'N';
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    const index = Math.round(degrees / 45) % 8;
    return directions[index];
  };

  return (
    <WeatherCard title="Current Weather" className="current-weather-card">
      <div className="current-weather-header">
        <div className="location-info">
          <h2 className="location-name">{currentLocation}</h2>
          <p className="update-time">Updated: {formatTime(timestamp)}</p>
        </div>
        <AddToFavorites location={{ city: currentLocation }} />
      </div>

      <div className="current-weather-main">
        <div className="weather-icon-large">
          {getWeatherIcon(condition)}
        </div>
        <div className="temperature-main">
          <div className="temp-value">{Math.round(temperature)}°</div>
          <div className="temp-condition">{condition}</div>
          <div className="temp-feels-like">Feels like {Math.round(feels_like)}°</div>
        </div>
      </div>

      <div className="weather-details-grid">
        <div className="weather-detail-item">
          <div className="detail-icon">💧</div>
          <div className="detail-content">
            <div className="detail-label">Humidity</div>
            <div className="detail-value">{humidity}%</div>
          </div>
        </div>

        <div className="weather-detail-item">
          <div className="detail-icon">🌡️</div>
          <div className="detail-content">
            <div className="detail-label">Pressure</div>
            <div className="detail-value">{pressure} hPa</div>
          </div>
        </div>

        <div className="weather-detail-item">
          <div className="detail-icon">💨</div>
          <div className="detail-content">
            <div className="detail-label">Wind</div>
            <div className="detail-value">
              {wind_speed} km/h {getWindDirection(wind_direction)}
            </div>
          </div>
        </div>

        <div className="weather-detail-item">
          <div className="detail-icon">👁️</div>
          <div className="detail-content">
            <div className="detail-label">Visibility</div>
            <div className="detail-value">{visibility} km</div>
          </div>
        </div>

        {uv_index !== null && uv_index !== undefined && (
          <div className="weather-detail-item">
            <div className="detail-icon">☀️</div>
            <div className="detail-content">
              <div className="detail-label">UV Index</div>
              <div className="detail-value">{uv_index}</div>
            </div>
          </div>
        )}
      </div>
    </WeatherCard>
  );
};

export default CurrentWeatherCard;
