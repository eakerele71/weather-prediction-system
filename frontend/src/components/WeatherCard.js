import React from 'react';
import './WeatherCard.css';

const WeatherCard = ({ 
  title, 
  children, 
  className = '', 
  loading = false,
  error = null 
}) => {
  return (
    <div className={`weather-card card ${className}`}>
      {title && <h3 className="weather-card-title">{title}</h3>}
      
      {loading && (
        <div className="weather-card-loading">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      )}

      {error && (
        <div className="weather-card-error">
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && (
        <div className="weather-card-content">
          {children}
        </div>
      )}
    </div>
  );
};

export default WeatherCard;
