import React, { useState, useRef, useEffect } from 'react';
import { useWeather } from '../context/WeatherContext';
import './LocationInput.css';

// Popular cities for autocomplete suggestions
const POPULAR_CITIES = [
  { city: 'Nigeria', country: 'Nigeria', latitude: 9.0820, longitude: 8.6753 },
  { city: 'United States', country: 'United States', latitude: 37.0902, longitude: -95.7129 },
  { city: 'United Kingdom', country: 'United Kingdom', latitude: 55.3781, longitude: -3.4360 },
  { city: 'Canada', country: 'Canada', latitude: 56.1304, longitude: -106.3468 },
  { city: 'Germany', country: 'Germany', latitude: 51.1657, longitude: 10.4515 },
  { city: 'France', country: 'France', latitude: 46.2276, longitude: 2.2137 },
  { city: 'Spain', country: 'Spain', latitude: 40.4637, longitude: -3.7492 },
  { city: 'Italy', country: 'Italy', latitude: 41.8719, longitude: 12.5674 },
  { city: 'Japan', country: 'Japan', latitude: 36.2048, longitude: 138.2529 },
  { city: 'Australia', country: 'Australia', latitude: -25.2744, longitude: 133.7751 },
  { city: 'India', country: 'India', latitude: 20.5937, longitude: 78.9629 },
  { city: 'South Africa', country: 'South Africa', latitude: -30.5595, longitude: 22.9375 },
  { city: 'Brazil', country: 'Brazil', latitude: -14.2350, longitude: -51.9253 },
  { city: 'China', country: 'China', latitude: 35.8617, longitude: 104.1954 },
  { city: 'Mexico', country: 'Mexico', latitude: 23.6345, longitude: -102.5528 },
];

/**
 * Smart pre-validation to catch obviously invalid inputs
 * before calling the API. This provides instant UX feedback
 * while keeping the comprehensive API validation as source of truth.
 */
function validateLocationInput(input) {
  const trimmed = input.trim();
  const lowerCased = trimmed.toLowerCase();
  const words = lowerCased.split(/\s+/);

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

  // Common human names (Global and Local Nigerian names) to block
  const commonHumanNames = [
    // Global Names
    'james', 'john', 'robert', 'michael', 'william', 'david', 'richard', 'joseph', 'thomas', 'charles',
    'mary', 'patricia', 'jennifer', 'linda', 'elizabeth', 'barbara', 'susan', 'jessica', 'sarah', 'karen',
    'emma', 'olivia', 'ava', 'isabella', 'sophia', 'mia', 'charlotte', 'amelia', 'evelyn', 'abigail',
    'liam', 'noah', 'oliver', 'elijah', 'james', 'william', 'benjamin', 'lucas', 'henry', 'alexander',

    // Local Nigerian Names
    'emeka', 'ngozi', 'chinelo', 'ifeanyi', 'chukwuma', 'nneka', 'obinna', 'chidi', 'ekene', 'chioma', // Igbo
    'babajide', 'olumide', 'adesola', 'folasade', 'temitope', 'adenike', 'olamide', 'tunde', 'seun', 'yinka', // Yoruba
    'musa', 'abubakar', 'fatima', 'aminu', 'zainab', 'umar', 'aisha', 'usman', 'hadiza', 'ibrahim', // Hausa/Fulani
    'emmanuel', 'samuel', 'david', 'blessing', 'favour', 'joy', 'patience', 'gift', 'mercy', 'hope' // Common English names in Nigeria
  ];

  // Common phrases for introducing oneself
  const namePhrases = [
    'my name is', 'i am', 'call me', 'iam', 'name is', 'this is'
  ];

  // Check for introduction phrases
  if (namePhrases.some(phrase => lowerCased.includes(phrase))) {
    return {
      valid: false,
      error: 'Please enter a location, not an introduction.'
    };
  }

  // Check if any word in the input is a common human name
  // We only block if the input is short (1-2 words) to avoid blocking cities with names in them
  if (words.length <= 2) {
    const containsName = words.some(word => commonHumanNames.includes(word));
    if (containsName) {
      return {
        valid: false,
        error: 'Please enter a valid city, state, or country name, not a personal name.'
      };
    }
  }

  // Common non-location words (food, objects, people, etc.)
  const nonLocationWords = [
    'rice', 'beans', 'food', 'pizza', 'burger', 'bread', 'meat', 'fish',
    'car', 'bike', 'phone', 'computer', 'table', 'chair', 'book', 'pen',
    'dog', 'cat', 'bird', 'animal', 'apple', 'orange', 'banana', 'fruit',
    'water', 'juice', 'coffee', 'tea', 'drink', 'shirt', 'pants', 'shoe',
    'person', 'people', 'man', 'men', 'woman', 'women', 'boy', 'girl', 'baby', 'name',
    'house', 'room', 'door', 'window', 'tree', 'flower', 'grass', 'plant'
  ];

  // Check if input contains multiple non-location words
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

const LocationInput = ({ onLocationSelect, initialValue }) => {
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

  // Sync input with initialValue (e.g., when detected by GPS)
  useEffect(() => {
    if (initialValue) {
      setInput(initialValue);
    }
  }, [initialValue]);

  const handleInputChange = (e) => {
    setInput(e.target.value);
    setSelectedIndex(-1);
    setValidationError(null); // Clear validation error when user types
  };

  const handleLocationSelect = async (location) => {
    setInput(location.city);
    setShowSuggestions(false);

    if (onLocationSelect) {
      onLocationSelect(location);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (input.trim()) {
      // If a suggestion is selected, use it (skip validation - suggestions are pre-validated)
      if (selectedIndex >= 0 && suggestions[selectedIndex]) {
        setValidationError(null);
        handleLocationSelect(suggestions[selectedIndex]);
      } else {
        // Validate input before making API call
        const validation = validateLocationInput(input);

        if (!validation.valid) {
          setValidationError(validation.error);
          return;
        }

        // Clear validation error and proceed
        setValidationError(null);

        // Otherwise, trigger the select callback
        setShowSuggestions(false);
        if (onLocationSelect) {
          onLocationSelect({ city: input.trim() });
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
            placeholder="Enter city, state, or country (e.g., New York, London, Nigeria)"
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
