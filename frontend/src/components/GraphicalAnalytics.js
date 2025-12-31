import { useState } from 'react';
import { useWeather } from '../context/WeatherContext';
import WeatherCard from './WeatherCard';
import './GraphicalAnalytics.css';

const GraphicalAnalytics = () => {
  const { currentWeather, forecast } = useWeather();
  const [activeView, setActiveView] = useState('wind');

  if (!currentWeather && !forecast) {
    return null;
  }

  // Wind compass component
  const WindCompass = () => {
    if (!currentWeather) return <div className="no-data">No wind data available</div>;

    const { wind_speed, wind_direction } = currentWeather;
    
    const getWindDirectionLabel = (degrees) => {
      if (degrees === null || degrees === undefined) return 'N';
      const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
      const index = Math.round(degrees / 22.5) % 16;
      return directions[index];
    };

    const getWindSpeedCategory = (speed) => {
      if (speed < 5) return { label: 'Calm', color: '#10b981' };
      if (speed < 20) return { label: 'Light', color: '#3b82f6' };
      if (speed < 40) return { label: 'Moderate', color: '#f59e0b' };
      if (speed < 60) return { label: 'Strong', color: '#ef4444' };
      return { label: 'Severe', color: '#dc2626' };
    };

    const category = getWindSpeedCategory(wind_speed);

    return (
      <div className="wind-compass-container">
        <div className="compass-circle">
          <div className="compass-directions">
            <span className="compass-n">N</span>
            <span className="compass-e">E</span>
            <span className="compass-s">S</span>
            <span className="compass-w">W</span>
          </div>
          <div 
            className="wind-arrow"
            style={{ 
              transform: `rotate(${wind_direction || 0}deg)`,
              borderBottomColor: category.color
            }}
          />
          <div className="compass-center" />
        </div>
        <div className="wind-info">
          <div className="wind-speed" style={{ color: category.color }}>
            {wind_speed} km/h
          </div>
          <div className="wind-direction-label">
            {getWindDirectionLabel(wind_direction)}
          </div>
          <div className="wind-category" style={{ color: category.color }}>
            {category.label}
          </div>
        </div>
      </div>
    );
  };

  // UV Index gauge component
  const UVIndexGauge = () => {
    if (!currentWeather || currentWeather.uv_index === null || currentWeather.uv_index === undefined) {
      return <div className="no-data">No UV index data available</div>;
    }

    const { uv_index } = currentWeather;

    const getUVCategory = (uv) => {
      if (uv <= 2) return { label: 'Low', color: '#10b981', range: '0-2' };
      if (uv <= 5) return { label: 'Moderate', color: '#f59e0b', range: '3-5' };
      if (uv <= 7) return { label: 'High', color: '#fb923c', range: '6-7' };
      if (uv <= 10) return { label: 'Very High', color: '#ef4444', range: '8-10' };
      return { label: 'Extreme', color: '#dc2626', range: '11+' };
    };

    const category = getUVCategory(uv_index);
    const percentage = Math.min((uv_index / 11) * 100, 100);

    return (
      <div className="uv-gauge-container">
        <div className="uv-gauge">
          <svg viewBox="0 0 200 120" className="gauge-svg">
            {/* Background arc */}
            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="20"
              strokeLinecap="round"
            />
            {/* Colored segments */}
            <path
              d="M 20 100 A 80 80 0 0 1 52 36"
              fill="none"
              stroke="#10b981"
              strokeWidth="20"
              strokeLinecap="round"
            />
            <path
              d="M 52 36 A 80 80 0 0 1 100 20"
              fill="none"
              stroke="#f59e0b"
              strokeWidth="20"
              strokeLinecap="round"
            />
            <path
              d="M 100 20 A 80 80 0 0 1 148 36"
              fill="none"
              stroke="#fb923c"
              strokeWidth="20"
              strokeLinecap="round"
            />
            <path
              d="M 148 36 A 80 80 0 0 1 180 100"
              fill="none"
              stroke="#ef4444"
              strokeWidth="20"
              strokeLinecap="round"
            />
            {/* Needle */}
            <line
              x1="100"
              y1="100"
              x2="100"
              y2="30"
              stroke={category.color}
              strokeWidth="3"
              strokeLinecap="round"
              transform={`rotate(${-90 + (percentage * 1.8)} 100 100)`}
            />
            <circle cx="100" cy="100" r="8" fill={category.color} />
          </svg>
        </div>
        <div className="uv-info">
          <div className="uv-value" style={{ color: category.color }}>
            {uv_index}
          </div>
          <div className="uv-category" style={{ color: category.color }}>
            {category.label}
          </div>
          <div className="uv-range">Range: {category.range}</div>
        </div>
      </div>
    );
  };

  // Comparative temperature graph
  const ComparativeGraph = () => {
    if (!forecast || forecast.length === 0) {
      return <div className="no-data">No forecast data available</div>;
    }

    const maxTemp = Math.max(...forecast.map(d => d.temperature_high));
    const minTemp = Math.min(...forecast.map(d => d.temperature_low));
    const range = maxTemp - minTemp;

    return (
      <div className="comparative-graph-container">
        <h4 className="graph-title">Temperature Comparison (7 Days)</h4>
        <div className="temp-bars">
          {forecast.map((day, index) => {
            const date = new Date(day.date);
            const highPercent = ((day.temperature_high - minTemp) / range) * 100;
            const lowPercent = ((day.temperature_low - minTemp) / range) * 100;

            return (
              <div key={index} className="temp-bar-item">
                <div className="temp-bar-label">
                  {date.toLocaleDateString('en-US', { weekday: 'short' })}
                </div>
                <div className="temp-bar-container">
                  <div 
                    className="temp-bar-high"
                    style={{ height: `${highPercent}%` }}
                  >
                    <span className="temp-bar-value">{Math.round(day.temperature_high)}°</span>
                  </div>
                  <div 
                    className="temp-bar-low"
                    style={{ height: `${lowPercent}%` }}
                  >
                    <span className="temp-bar-value">{Math.round(day.temperature_low)}°</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        <div className="graph-legend">
          <div className="legend-item">
            <span className="legend-color high"></span>
            <span>High</span>
          </div>
          <div className="legend-item">
            <span className="legend-color low"></span>
            <span>Low</span>
          </div>
        </div>
      </div>
    );
  };

  const views = [
    { id: 'wind', label: 'Wind Compass', icon: '🧭' },
    { id: 'uv', label: 'UV Index', icon: '☀️' },
    { id: 'comparison', label: 'Temperature Comparison', icon: '📊' },
  ];

  const renderView = () => {
    switch (activeView) {
      case 'wind':
        return <WindCompass />;
      case 'uv':
        return <UVIndexGauge />;
      case 'comparison':
        return <ComparativeGraph />;
      default:
        return null;
    }
  };

  return (
    <WeatherCard title="Graphical Analytics" className="graphical-analytics-card">
      <div className="analytics-tabs">
        {views.map(view => (
          <button
            key={view.id}
            className={`analytics-tab ${activeView === view.id ? 'active' : ''}`}
            onClick={() => setActiveView(view.id)}
          >
            <span className="analytics-tab-icon">{view.icon}</span>
            <span className="analytics-tab-label">{view.label}</span>
          </button>
        ))}
      </div>

      <div className="analytics-view">
        {renderView()}
      </div>
    </WeatherCard>
  );
};

export default GraphicalAnalytics;
