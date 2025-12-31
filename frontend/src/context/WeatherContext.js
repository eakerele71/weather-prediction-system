import React, { createContext, useContext, useState, useCallback } from 'react';
import axios from 'axios';

const WeatherContext = createContext();

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const useWeather = () => {
  const context = useContext(WeatherContext);
  if (!context) {
    throw new Error('useWeather must be used within a WeatherProvider');
  }
  return context;
};

export const WeatherProvider = ({ children }) => {
  // State
  const [currentLocation, setCurrentLocation] = useState(null);
  const [currentWeather, setCurrentWeather] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [accuracyMetrics, setAccuracyMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [favoriteLocations, setFavoriteLocations] = useState([]);

  // API client with auth token
  const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Add auth token to requests if available
  apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // Fetch current weather
  const fetchCurrentWeather = useCallback(async (city) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get(`/api/v1/current/${city}`);
      setCurrentWeather(response.data);
      return response.data;
    } catch (err) {
      let errorMsg = 'Failed to fetch current weather';
      if (err.response?.data?.detail) {
        errorMsg = Array.isArray(err.response.data.detail)
          ? err.response.data.detail.map(e => e.msg).join(', ')
          : err.response.data.detail;
      } else if (err.message) {
        errorMsg = err.message;
      }
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch forecast
  const fetchForecast = useCallback(async (city, days = 7) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get(`/api/v1/forecast/${city}`, {
        params: { days },
      });
      // Backend returns array directly, not wrapped in { forecasts: [...] }
      const forecastData = Array.isArray(response.data) ? response.data : (response.data.forecasts || []);
      setForecast(forecastData);
      return response.data;
    } catch (err) {
      let errorMsg = 'Failed to fetch forecast';
      if (err.response?.data?.detail) {
        errorMsg = Array.isArray(err.response.data.detail)
          ? err.response.data.detail.map(e => e.msg).join(', ')
          : err.response.data.detail;
      } else if (err.message) {
        errorMsg = err.message;
      }
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch warnings
  const fetchWarnings = useCallback(async (city) => {
    try {
      const response = await apiClient.get(`/api/v1/warnings/${city}`);
      // Backend returns array directly, not wrapped in { warnings: [...] }
      const warningsData = Array.isArray(response.data) ? response.data : (response.data.warnings || []);
      setWarnings(warningsData);
      return response.data;
    } catch (err) {
      console.error('Failed to fetch warnings:', err);
      setWarnings([]);
    }
  }, []);

  // Fetch analytics
  const fetchAnalytics = useCallback(async (city, days = 30) => {
    try {
      const response = await apiClient.get(`/api/v1/analytics/weather-analytics/${city}`, {
        params: { days },
      });
      setAnalytics(response.data);
      return response.data;
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
      setAnalytics(null);
    }
  }, []);

  // Fetch accuracy metrics
  const fetchAccuracyMetrics = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/v1/analytics/accuracy-metrics');
      setAccuracyMetrics(response.data);
      return response.data;
    } catch (err) {
      console.error('Failed to fetch accuracy metrics:', err);
      setAccuracyMetrics(null);
    }
  }, []);

  // Fetch all data for a location
  const fetchLocationData = useCallback(async (city) => {
    setLoading(true);
    setError(null);

    // Reset ALL data when searching for a new location (including currentLocation)
    // This ensures only successfully validated locations display weather data
    setCurrentLocation(null);
    setCurrentWeather(null);
    setForecast([]);
    setWarnings([]);
    setAnalytics(null);

    try {
      // First try to fetch current weather - this validates the location
      await fetchCurrentWeather(city);

      // If current weather succeeded, location is valid - set it and fetch rest
      setCurrentLocation(city);

      await Promise.all([
        fetchForecast(city),
        fetchWarnings(city),
        fetchAnalytics(city),
      ]);
    } catch (err) {
      console.error('Error fetching location data:', err);
      // Don't set location if it's invalid - it's already null from the reset
      // Error is already set by fetchCurrentWeather
    } finally {
      setLoading(false);
    }
  }, [fetchCurrentWeather, fetchForecast, fetchWarnings, fetchAnalytics]);

  // Add favorite location
  const addFavoriteLocation = useCallback((location) => {
    setFavoriteLocations((prev) => {
      if (prev.find((loc) => loc.city === location.city)) {
        return prev;
      }
      const updated = [...prev, location];
      localStorage.setItem('favoriteLocations', JSON.stringify(updated));
      return updated;
    });
  }, []);

  // Remove favorite location
  const removeFavoriteLocation = useCallback((city) => {
    setFavoriteLocations((prev) => {
      const updated = prev.filter((loc) => loc.city !== city);
      localStorage.setItem('favoriteLocations', JSON.stringify(updated));
      return updated;
    });
  }, []);

  // Load favorite locations from localStorage
  React.useEffect(() => {
    const stored = localStorage.getItem('favoriteLocations');
    if (stored) {
      try {
        setFavoriteLocations(JSON.parse(stored));
      } catch (err) {
        console.error('Failed to parse favorite locations:', err);
      }
    }
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Gemini chat - ask a question
  const askGemini = useCallback(async (question, context = {}) => {
    try {
      const response = await apiClient.post('/api/v1/gemini/chat', {
        question,
        city: context.location || currentLocation || null,
      });
      return response.data;
    } catch (err) {
      console.error('Failed to get Gemini response:', err);
      throw err;
    }
  }, [currentLocation]);

  // Gemini explain - get weather explanation
  const explainWeather = useCallback(async (city) => {
    try {
      const response = await apiClient.post('/api/v1/gemini/explain', {
        city: city,
      });
      return response.data;
    } catch (err) {
      console.error('Failed to get weather explanation:', err);
      throw err;
    }
  }, []);

  const value = {
    // State
    currentLocation,
    currentWeather,
    forecast,
    warnings,
    analytics,
    accuracyMetrics,
    loading,
    error,
    favoriteLocations,

    // Actions
    fetchCurrentWeather,
    fetchForecast,
    fetchWarnings,
    fetchAnalytics,
    fetchAccuracyMetrics,
    fetchLocationData,
    addFavoriteLocation,
    removeFavoriteLocation,
    clearError,
    setCurrentLocation,
    askGemini,
    explainWeather,
  };

  return (
    <WeatherContext.Provider value={value}>
      {children}
    </WeatherContext.Provider>
  );
};
