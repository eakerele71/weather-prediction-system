import React from 'react';
import { useWeather } from '../context/WeatherContext';
import './FavoriteLocations.css';

const FavoriteLocations = () => {
  const {
    favoriteLocations,
    removeFavoriteLocation,
    fetchLocationData,
    currentLocation,
  } = useWeather();

  const handleLocationClick = async (location) => {
    try {
      await fetchLocationData(location.city);
    } catch (error) {
      console.error('Error fetching location data:', error);
    }
  };

  const handleRemoveFavorite = (e, city) => {
    e.stopPropagation();
    removeFavoriteLocation(city);
  };

  if (favoriteLocations.length === 0) {
    return null;
  }

  return (
    <div className="favorite-locations">
      <h3 className="favorite-locations-title">Favorite Locations</h3>
      <div className="favorite-locations-list">
        {favoriteLocations.map((location) => (
          <div
            key={location.city}
            className={`favorite-location-item ${
              currentLocation === location.city ? 'active' : ''
            }`}
            onClick={() => handleLocationClick(location)}
          >
            <div className="favorite-location-icon">
              <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M8 8.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"
                  fill="currentColor"
                />
                <path
                  d="M8 1a5.5 5.5 0 0 0-5.5 5.5c0 3.5 5.5 8.5 5.5 8.5s5.5-5 5.5-8.5A5.5 5.5 0 0 0 8 1z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  fill="none"
                />
              </svg>
            </div>
            <div className="favorite-location-text">
              <div className="favorite-location-city">{location.city}</div>
              {location.country && (
                <div className="favorite-location-country">{location.country}</div>
              )}
            </div>
            <button
              className="favorite-location-remove"
              onClick={(e) => handleRemoveFavorite(e, location.city)}
              aria-label="Remove from favorites"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M12 4L4 12M4 4l8 8"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FavoriteLocations;
