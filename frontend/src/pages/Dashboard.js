import React from 'react';
import { useWeather } from '../context/WeatherContext';
import Header from '../components/Header';
import Footer from '../components/Footer';
import DashboardContainer from '../components/DashboardContainer';
import WeatherCard from '../components/WeatherCard';
import LocationInput from '../components/LocationInput';
import CurrentLocationButton from '../components/CurrentLocationButton';

import FavoriteLocations from '../components/FavoriteLocations';
import CurrentWeatherCard from '../components/CurrentWeatherCard';
import HourlyForecast from '../components/HourlyForecast';
import ForecastTimeline from '../components/ForecastTimeline';
import AnalyticsCharts from '../components/AnalyticsCharts';
import GraphicalAnalytics from '../components/GraphicalAnalytics';
import WeatherWarnings from '../components/WeatherWarnings';
import GeminiChatPanel from '../components/GeminiChatPanel';
import './Dashboard.css';

const Dashboard = () => {
  const { currentLocation, loading, error, clearError, fetchLocationData } = useWeather();

  const handleLocationSelect = (cityOrLocation) => {
    const cityName = typeof cityOrLocation === 'string'
      ? cityOrLocation
      : cityOrLocation?.city;

    if (cityName) {
      fetchLocationData(cityName);
    }
  };

  return (
    <div className="dashboard">
      <Header
        title="Weather Prediction System"
        subtitle="ML-powered weather forecasting with real-time analytics"
      />

      <main className="dashboard-main">
        <div className="container">
          <div className="location-input-row">
            <LocationInput
              onLocationSelect={handleLocationSelect}
              initialValue={currentLocation}
            />
            <CurrentLocationButton
              onLocationDetected={(cityName, locationData) => {
                handleLocationSelect(cityName);
                console.log('Detected location:', locationData);
              }}
            />
          </div>
          <FavoriteLocations />

          {error && (
            <div className="error-message" role="alert">
              <span className="error-icon">⚠️</span>
              <p>{error}</p>
              <button className="error-close-btn" onClick={clearError} aria-label="Close error message">
                ×
              </button>
            </div>
          )}

          {loading && (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Loading weather data...</p>
            </div>
          )}

          {!currentLocation && !loading && (
            <WeatherCard className="welcome-card">
              <div className="welcome-message">
                <h2>Welcome to Weather Prediction System</h2>
                <p>Enter a location above to get started with accurate weather predictions powered by machine learning.</p>
              </div>
            </WeatherCard>
          )}

          {currentLocation && !loading && (
            <DashboardContainer>
              <div className="grid-col-12">
                <WeatherWarnings />
              </div>
              <div className="grid-col-12">
                <CurrentWeatherCard />
              </div>
              <div className="grid-col-12">
                <HourlyForecast />
              </div>
              <div className="grid-col-12">
                <ForecastTimeline />
              </div>
              <div className="grid-col-12">
                <AnalyticsCharts />
              </div>
              <div className="grid-col-12">
                <GraphicalAnalytics />
              </div>
              <div className="grid-col-12">
                <GeminiChatPanel />
              </div>
            </DashboardContainer>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Dashboard;
