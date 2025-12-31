import { useState } from 'react';
import { useWeather } from '../context/WeatherContext';
import WeatherCard from './WeatherCard';
import './ForecastTimeline.css';

const ForecastTimeline = () => {
  const { forecast, currentLocation } = useWeather();
  const [selectedDay, setSelectedDay] = useState(null);
  const [explanation, setExplanation] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  if (!forecast || forecast.length === 0) {
    return null;
  }

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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

  // Format full date for modal
  const formatFullDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  // Get weather icon
  const getWeatherIcon = (condition) => {
    const icons = {
      clear: '☀️',
      sunny: '☀️',
      cloudy: '☁️',
      'partly cloudy': '⛅',
      clouds: '☁️',
      overcast: '☁️',
      rainy: '🌧️',
      rain: '🌧️',
      stormy: '⛈️',
      storm: '⛈️',
      thunderstorm: '⛈️',
      snowy: '❄️',
      snow: '❄️',
      foggy: '🌫️',
      fog: '🌫️',
      mist: '🌫️',
      windy: '💨',
      drizzle: '🌦️',
    };
    return icons[condition?.toLowerCase()] || '🌤️';
  };

  // Get confidence color
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#10b981';
    if (confidence >= 0.6) return '#f59e0b';
    return '#ef4444';
  };

  // Get confidence label
  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  // Handle day click - fetch AI explanation
  const handleDayClick = async (day, index) => {
    setSelectedDay({ ...day, index });
    setIsLoading(true);
    setExplanation('');

    const dateStr = day.forecast_date || day.date;
    const condition = day.weather_condition || day.condition;
    const tempHigh = day.predicted_temperature_high || day.temperature_high || 0;
    const tempLow = day.predicted_temperature_low || day.temperature_low || 0;
    const precipProb = day.precipitation_probability || 0;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/gemini/explain-day`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          city: currentLocation,
          date: dateStr,
          condition: condition,
          temp_high: tempHigh,
          temp_low: tempLow,
          precipitation_probability: precipProb,
          confidence_score: day.confidence_score || 0.85
        })
      });

      if (response.ok) {
        const data = await response.json();
        setExplanation(data.explanation);
      } else {
        setExplanation(generateFallbackExplanation(day));
      }
    } catch (error) {
      console.error('Error fetching explanation:', error);
      setExplanation(generateFallbackExplanation(day));
    } finally {
      setIsLoading(false);
    }
  };

  // Generate fallback explanation if API fails
  const generateFallbackExplanation = (day) => {
    const condition = day.weather_condition || day.condition || 'variable';
    const tempHigh = day.predicted_temperature_high || day.temperature_high || 0;
    const tempLow = day.predicted_temperature_low || day.temperature_low || 0;
    const precipProb = (day.precipitation_probability || 0) * 100;

    let explanation = `Weather Prediction Analysis:\n\n`;
    explanation += `Expected conditions: ${condition}\n`;
    explanation += `Temperature range: ${Math.round(tempLow)}°C to ${Math.round(tempHigh)}°C\n\n`;

    if (precipProb > 70) {
      explanation += `High precipitation probability (${Math.round(precipProb)}%) suggests an active weather system moving through the area. Consider carrying rain gear and planning indoor alternatives.\n\n`;
    } else if (precipProb > 30) {
      explanation += `Moderate precipitation chance (${Math.round(precipProb)}%) indicates some atmospheric instability. Keep an eye on updates throughout the day.\n\n`;
    } else {
      explanation += `Low precipitation probability (${Math.round(precipProb)}%) suggests stable atmospheric conditions with minimal chance of rain.\n\n`;
    }

    const tempDiff = tempHigh - tempLow;
    if (tempDiff > 15) {
      explanation += `Large temperature variation (${Math.round(tempDiff)}°C) expected. Dress in layers to stay comfortable throughout the day.`;
    } else if (tempDiff > 8) {
      explanation += `Moderate temperature variation expected. Morning and evening may feel noticeably cooler than midday.`;
    } else {
      explanation += `Relatively stable temperatures throughout the day with minimal variation.`;
    }

    return explanation;
  };

  // Close modal
  const closeModal = () => {
    setSelectedDay(null);
    setExplanation('');
  };

  return (
    <>
      <WeatherCard title="7-Day Forecast" className="forecast-timeline-card">
        <p className="forecast-hint">Click on any day for detailed prediction analysis</p>
        <div className="forecast-timeline">
          {forecast.map((day, index) => {
            const dateStr = day.forecast_date || day.date;
            const condition = day.weather_condition || day.condition;
            const tempHigh = day.predicted_temperature_high || day.temperature_high || 0;
            const tempLow = day.predicted_temperature_low || day.temperature_low || 0;
            
            return (
              <div 
                key={index} 
                className="forecast-day"
                onClick={() => handleDayClick(day, index)}
                role="button"
                tabIndex={0}
                onKeyPress={(e) => e.key === 'Enter' && handleDayClick(day, index)}
              >
                <div className="forecast-date">{formatDate(dateStr)}</div>
                
                <div className="forecast-icon">
                  {getWeatherIcon(condition)}
                </div>

                <div className="forecast-condition">{condition}</div>

                <div className="forecast-temps">
                  <span className="temp-high">{Math.round(tempHigh)}°</span>
                  <span className="temp-separator">/</span>
                  <span className="temp-low">{Math.round(tempLow)}°</span>
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

                <div className="click-hint">
                  <span>ℹ️ Click for details</span>
                </div>
              </div>
            );
          })}
        </div>
      </WeatherCard>

      {/* Prediction Explanation Modal */}
      {selectedDay && (
        <div className="forecast-modal-overlay" onClick={closeModal}>
          <div className="forecast-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>×</button>
            
            <div className="modal-header">
              <div className="modal-icon">
                {getWeatherIcon(selectedDay.weather_condition || selectedDay.condition)}
              </div>
              <div className="modal-title">
                <h3>{formatFullDate(selectedDay.forecast_date || selectedDay.date)}</h3>
                <p className="modal-location">{currentLocation}</p>
              </div>
            </div>

            <div className="modal-weather-summary">
              <div className="summary-item">
                <span className="summary-label">Condition</span>
                <span className="summary-value">{selectedDay.weather_condition || selectedDay.condition}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">High</span>
                <span className="summary-value temp-high">
                  {Math.round(selectedDay.predicted_temperature_high || selectedDay.temperature_high || 0)}°C
                </span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Low</span>
                <span className="summary-value temp-low">
                  {Math.round(selectedDay.predicted_temperature_low || selectedDay.temperature_low || 0)}°C
                </span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Rain Chance</span>
                <span className="summary-value">
                  {Math.round((selectedDay.precipitation_probability || 0) * 100)}%
                </span>
              </div>
            </div>

            <div className="modal-explanation">
              <h4>🤖 AI Prediction Analysis</h4>
              {isLoading ? (
                <div className="explanation-loading">
                  <div className="loading-spinner"></div>
                  <p>Analyzing weather patterns...</p>
                </div>
              ) : (
                <div className="explanation-content">
                  {explanation.split('\n').map((line, i) => (
                    <p key={i}>{line}</p>
                  ))}
                </div>
              )}
            </div>

            <div className="modal-footer">
              <p className="confidence-note">
                Prediction confidence: {' '}
                <span style={{ color: getConfidenceColor(selectedDay.confidence_score || 0.85) }}>
                  {getConfidenceLabel(selectedDay.confidence_score || 0.85)} 
                  ({Math.round((selectedDay.confidence_score || 0.85) * 100)}%)
                </span>
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ForecastTimeline;
