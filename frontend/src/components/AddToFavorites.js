import React from 'react';
import { useWeather } from '../context/WeatherContext';
import './AddToFavorites.css';

const AddToFavorites = ({ location }) => {
  const { favoriteLocations, addFavoriteLocation, removeFavoriteLocation } = useWeather();

  if (!location) {
    return null;
  }

  const isFavorite = favoriteLocations.some((fav) => fav.city === location.city);

  const handleToggleFavorite = () => {
    if (isFavorite) {
      removeFavoriteLocation(location.city);
    } else {
      addFavoriteLocation(location);
    }
  };

  return (
    <button
      className={`add-to-favorites-btn ${isFavorite ? 'is-favorite' : ''}`}
      onClick={handleToggleFavorite}
      aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
      title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
    >
      <svg
        width="20"
        height="20"
        viewBox="0 0 20 20"
        fill={isFavorite ? 'currentColor' : 'none'}
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M10 3.5l2.5 5 5.5.8-4 3.9.9 5.3-4.9-2.6-4.9 2.6.9-5.3-4-3.9 5.5-.8 2.5-5z"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      {isFavorite ? 'Remove from Favorites' : 'Add to Favorites'}
    </button>
  );
};

export default AddToFavorites;
