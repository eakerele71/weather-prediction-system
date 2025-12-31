import React, { useState, useRef, useEffect } from 'react';
import { useWeather } from '../context/WeatherContext';
import './LocationInput.css';

// Popular cities for autocomplete suggestions
const POPULAR_CITIES = [
  { city: 'New York', country: 'United States', latitude: 40.7128, longitude: -74.0060 },
  { city: 'Los Angeles', country: 'United States', latitude: 34.0522, longitude: -118.2437 },
  { city: 'Chicago', country: 'United States', latitude: 41.8781, longitude: -87.6298 },
  { city: 'Houston', country: 'United States', latitude: 29.7604, longitude: -95.3698 },
  { city: 'Phoenix', country: 'United States', latitude: 33.4484, longitude: -112.0740 },
  { city: 'London', country: 'United Kingdom', latitude: 51.5074, longitude: -0.1278 },
  { city: 'Paris', country: 'France', latitude: 48.8566, longitude: 2.3522 },
  { city: 'Tokyo', country: 'Japan', latitude: 35.6762, longitude: 139.6503 },
  { city: 'Sydney', country: 'Australia', latitude: -33.8688, longitude: 151.2093 },
  { city: 'Toronto', country: 'Canada', latitude: 43.6532, longitude: -79.3832 },
  { city: 'Berlin', country: 'Germany', latitude: 52.5200, longitude: 13.4050 },
  { city: 'Madrid', country: 'Spain', latitude: 40.4168, longitude: -3.7038 },
  { city: 'Rome', country: 'Italy', latitude: 41.9028, longitude: 12.4964 },
  { city: 'Mumbai', country: 'India', latitude: 19.0760, longitude: 72.8777 },
  { city: 'Singapore', country: 'Singapore', latitude: 1.3521, longitude: 103.8198 },
];

/**
 * Smart pre-validation to catch obviously invalid inputs
 * before calling the API. This provides instant UX feedback
 * while keeping the comprehensive API validation as source of truth.
 */
function validateLocationInput(input) {
  const trimmed = input.trim();
  const lowerCased = trimmed.toLowerCase();

  // Too short
  if (trimmed.length < 2) {
    return {
      valid: false,
      error: 'Location name is too short. Please enter at least 2 characters.'
    };
  }

  // Only numbers (e.g., "12345")
  if (/^\d+$/.test(trimmed)) {
    return {
      valid: false,
      error: 'Please enter a location name, not a number.'
    };
  }

  // Excessive special characters (more than 20% of string)
  const specialChars = (trimmed.match(/[^a-zA-Z0-9\s\-,.']/g) || []).length;
  if (specialChars / trimmed.length > 0.2) {
    return {
      valid: false,
      error: 'Please enter a valid city, state, or country name.'
    };
  }

  // Common non-location words (food, objects, people, etc.)
  const nonLocationWords = [
    'rice', 'beans', 'food', 'pizza', 'burger', 'bread', 'meat', 'fish',
    'car', 'bike', 'phone', 'computer', 'table', 'chair', 'book', 'pen',
    'dog', 'cat', 'bird', 'animal', 'apple', 'orange', 'banana', 'fruit',
    'water', 'juice', 'coffee', 'tea', 'drink', 'shirt', 'pants', 'shoe',
    'person', 'people', 'man', 'woman', 'boy', 'girl', 'baby', 'name',
    'house', 'room', 'door', 'window', 'tree', 'flower', 'grass', 'plant'
  ];

  // Check if input contains multiple non-location words
  const words = lowerCased.split(/\s+/);
  const nonLocationCount = words.filter(word => nonLocationWords.includes(word)).length;

  if (nonLocationCount >= 2) {
    return {
      valid: false,
      error: 'Please enter a valid location name, not common objects or phrases.'
    };
  }

  if (nonLocationCount === 1 && words.length <= 2) {
    // Single non-location word like "rice" or "rice city" (unlikely to be valid)
    return {
      valid: false,
      error: 'Please enter a valid city, state, or country name.'
    };
  }

  // Common keyboard mashing patterns that are clearly not locations
  const invalidPatterns = [
    { pattern: /^[!@#$%^&*()_+={}[\]:;<>,.?~\\|/-]+$/, error: 'Please enter letters, not symbols.' },
    { pattern: /^(test|testing)$/i, error: 'Please enter a real location name.' },
    { pattern: /^(asdf|qwer|zxcv|hjkl)+/i, error: 'Please enter a real location name.' },
    { pattern: /^(zzz|xxx|aaa|bbb)+$/i, error: 'Please enter a real location name.' },
    { pattern: /^(.)\1{4,}/, error: 'Please enter a real location name.' }, // Repeated chars like "aaaaa"
  ];

  for (const { pattern, error } of invalidPatterns) {
    if (pattern.test(trimmed)) {
      return { valid: false, error };
    }
  }

  // Looks reasonable - let API validate
  return { valid: true };
}

const LocationInput = ({ onLocationSelect }) => {
  const [input, setInput] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [validationError, setValidationError] = useState(null);
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  const { fetchLocationData, favoriteLocations } = useWeather();

  // Filter suggestions based on input
  useEffect(() => {
    if (input.length > 0) {
      const filtered = POPULAR_CITIES.filter(
        (location) =>
          location.city.toLowerCase().includes(input.toLowerCase()) ||
          location.country.toLowerCase().includes(input.toLowerCase())
      );

      // Add favorite locations to suggestions
      const favoriteSuggestions = favoriteLocations.filter(
        (location) =>
          location.city.toLowerCase().includes(input.toLowerCase()) ||
          location.country.toLowerCase().includes(input.toLowerCase())
      );

      setSuggestions([...favoriteSuggestions, ...filtered].slice(0, 8));
      setShowSuggestions(true);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [input, favoriteLocations]);

  // Handle click outside to close suggestions
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target) &&
        !inputRef.current.contains(event.target)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e) => {
    setInput(e.target.value);
    setSelectedIndex(-1);
    setValidationError(null); // Clear validation error when user types
  };

  const handleLocationSelect = async (location) => {
    setInput(location.city);
    setShowSuggestions(false);

    try {
      await fetchLocationData(location.city);
      if (onLocationSelect) {
        onLocationSelect(location);
      }
    } catch (error) {
      console.error('Error fetching location data:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (input.trim()) {
      // If a suggestion is selected, use it (skip validation - suggestions are pre-validated)
      if (selectedIndex >= 0 && suggestions[selectedIndex]) {
        setValidationError(null);
        await handleLocationSelect(suggestions[selectedIndex]);
      } else {
        // Validate input before making API call
        const validation = validateLocationInput(input);

        if (!validation.valid) {
          setValidationError(validation.error);
          return;
        }

        // Clear validation error and proceed
        setValidationError(null);

        // Otherwise, try to fetch data for the entered city name
        try {
          await fetchLocationData(input.trim());
          setShowSuggestions(false);
          if (onLocationSelect) {
            onLocationSelect({ city: input.trim() });
          }
        } catch (error) {
          console.error('Error fetching location data:', error);
        }
      }
    }
  };

  const handleKeyDown = (e) => {
    if (!showSuggestions || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && suggestions[selectedIndex]) {
          handleLocationSelect(suggestions[selectedIndex]);
        } else {
          handleSubmit(e);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedIndex(-1);
        break;
      default:
        break;
    }
  };

  return (
    <div className="location-input-container">
      <form onSubmit={handleSubmit} className="location-input-form">
        <div className="location-input-wrapper">
          <input
            ref={inputRef}
            type="text"
            className="location-input"
            placeholder="Enter city name (e.g., New York, London, Tokyo)"
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={() => input.length > 0 && setShowSuggestions(true)}
          />
          <button type="submit" className="location-submit-btn btn btn-primary">
            <svg
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16zM19 19l-4.35-4.35"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            Search
          </button>
        </div>

        {validationError && (
          <div className="validation-error" role="alert">
            {validationError}
          </div>
        )}

        {showSuggestions && suggestions.length > 0 && (
          <div ref={suggestionsRef} className="location-suggestions">
            {suggestions.map((location, index) => (
              <div
                key={`${location.city}-${location.country}-${index}`}
                className={`location-suggestion-item ${index === selectedIndex ? 'selected' : ''
                  }`}
                onClick={() => handleLocationSelect(location)}
                onMouseEnter={() => setSelectedIndex(index)}
              >
                <div className="suggestion-icon">
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
                <div className="suggestion-text">
                  <div className="suggestion-city">{location.city}</div>
                  <div className="suggestion-country">{location.country}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </form>
    </div>
  );
};

export default LocationInput;
