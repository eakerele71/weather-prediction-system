import { useState, useEffect, useRef } from 'react';
import { useWeather } from '../context/WeatherContext';
import WeatherCard from './WeatherCard';
import './HourlyForecast.css';

const HourlyForecast = () => {
  const { currentLocation } = useWeather();
  const [hourlyData, setHourlyData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const scrollRef = useRef(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    if (currentLocation) {
      fetchHourlyData();
    }
  }, [currentLocation]);

  const fetchHourlyData = async () => {
    if (!currentLocation) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/hourly/${currentLocation}?hours=48`);
      
      if (response.ok) {
        const data = await response.json();
        setHourlyData(data.hourly || []);
      } else {
        setError('Failed to fetch hourly forecast');
      }
    } catch (err) {
      console.error('Error fetching hourly data:', err);
      setError('Unable to load hourly forecast');
    } finally {
      setLoading(false);
    }
  };

  // Format time
  const formatTime = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    
    if (date.getHours() === now.getHours() && date.getDate() === now.getDate()) {
      return 'Now';
    }
    
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric',
      hour12: true 
    });
  };

  // Format day
  const formatDay = (dateStr) => {
    const date = new Date(dateStr);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return 'Tomorrow';
    }
    return date.toLocaleDateString('en-US', { weekday: 'short' });
  };

  // Get weather icon
  const getWeatherIcon = (condition, iconCode) => {
    const icons = {
      clear: '☀️',
      sunny: '☀️',
      clouds: '☁️',
      cloudy: '☁️',
      'few clouds': '🌤️',
      'scattered clouds': '⛅',
      'broken clouds': '🌥️',
      'overcast clouds': '☁️',
      rain: '🌧️',
      'light rain': '🌦️',
      'moderate rain': '🌧️',
      'heavy rain': '🌧️',
      drizzle: '🌦️',
      thunderstorm: '⛈️',
      snow: '❄️',
      mist: '🌫️',
      fog: '🌫️',
      haze: '🌫️',
    };
    
    // Check if it's night based on icon code
    const isNight = iconCode?.endsWith('n');
    
    if (condition?.toLowerCase().includes('clear') && isNight) {
      return '🌙';
    }
    
    return icons[condition?.toLowerCase()] || '🌤️';
  };

  // Get precipitation color
  const getPrecipColor = (prob) => {
    if (prob >= 0.7) return '#3b82f6';
    if (prob >= 0.4) return '#60a5fa';
    return '#93c5fd';
  };

  // Scroll handlers
  const scroll = (direction) => {
    if (scrollRef.current) {
      const scrollAmount = 300;
      scrollRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      });
    }
  };

  if (!currentLocation) {
    return null;
  }

  if (loading) {
    return (
      <WeatherCard title="Hourly Forecast" className="hourly-forecast-card">
        <div className="hourly-loading">
          <div className="loading-spinner"></div>
          <p>Loading hourly forecast...</p>
        </div>
      </WeatherCard>
    );
  }

  if (error) {
    return (
      <WeatherCard title="Hourly Forecast" className="hourly-forecast-card">
        <div className="hourly-error">
          <p>{error}</p>
          <button onClick={fetchHourlyData}>Retry</button>
        </div>
      </WeatherCard>
    );
  }

  if (!hourlyData || hourlyData.length === 0) {
    return null;
  }

  // Group by day for headers
  let currentDay = null;

  return (
    <WeatherCard title="Hourly Forecast" className="hourly-forecast-card">
      <div className="hourly-container">
        <button 
          className="scroll-btn scroll-left" 
          onClick={() => scroll('left')}
          aria-label="Scroll left"
        >
          ‹
        </button>
        
        <div className="hourly-scroll" ref={scrollRef}>
          {hourlyData.map((hour, index) => {
            const day = formatDay(hour.datetime);
            const showDayHeader = day !== currentDay;
            currentDay = day;
            
            return (
              <div key={index} className="hourly-item-wrapper">
                {showDayHeader && (
                  <div className="day-header">{day}</div>
                )}
                <div className="hourly-item">
                  <div className="hourly-time">{formatTime(hour.datetime)}</div>
                  
                  <div className="hourly-icon">
                    {getWeatherIcon(hour.weather_condition, hour.weather_icon)}
                  </div>
                  
                  <div className="hourly-temp">
                    {Math.round(hour.temperature)}°
                  </div>
                  
                  <div className="hourly-feels-like">
                    Feels {Math.round(hour.feels_like)}°
                  </div>
                  
                  {hour.precipitation_probability > 0 && (
                    <div 
                      className="hourly-precip"
                      style={{ color: getPrecipColor(hour.precipitation_probability) }}
                    >
                      💧 {Math.round(hour.precipitation_probability * 100)}%
                    </div>
                  )}
                  
                  <div className="hourly-wind">
                    💨 {Math.round(hour.wind_speed)} m/s
                  </div>
                  
                  <div className="hourly-humidity">
                    💦 {hour.humidity}%
                  </div>
                  
                  <div className="hourly-condition">
                    {hour.weather_description}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        
        <button 
          className="scroll-btn scroll-right" 
          onClick={() => scroll('right')}
          aria-label="Scroll right"
        >
          ›
        </button>
      </div>
      
      <div className="hourly-legend">
        <span>💧 Rain chance</span>
        <span>💨 Wind speed</span>
        <span>💦 Humidity</span>
      </div>
    </WeatherCard>
  );
};

export default HourlyForecast;
