import React, { useState } from 'react';
import './CurrentLocationButton.css';

const CurrentLocationButton = ({ onLocationDetected }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleGetLocation = async () => {
        setLoading(true);
        setError(null);

        if (!navigator.geolocation) {
            setError('Geolocation is not supported by your browser');
            setLoading(false);
            return;
        }

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                try {
                    const { latitude, longitude } = position.coords;
                    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

                    const response = await fetch(
                        `${apiUrl}/api/v1/geolocation/coords-to-city/${latitude}/${longitude}`
                    );

                    if (!response.ok) {
                        throw new Error('Failed to determine location');
                    }

                    const locationData = await response.json();

                    if (onLocationDetected) {
                        onLocationDetected(locationData.city, locationData);
                    }

                    setLoading(false);
                } catch (err) {
                    setError('Could not determine your location');
                    setLoading(false);
                    console.error('Location error:', err);
                }
            },
            (err) => {
                let errorMessage = 'Unable to get your location';

                if (err.code === 1) {
                    errorMessage = 'Location permission denied. Please enable location access.';
                } else if (err.code === 2) {
                    errorMessage = 'Location information unavailable';
                } else if (err.code === 3) {
                    errorMessage = 'Location request timed out';
                }

                setError(errorMessage);
                setLoading(false);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    };

    return (
        <div className="current-location-wrapper">
            <button
                className={`current-location-btn ${loading ? 'loading' : ''}`}
                onClick={handleGetLocation}
                disabled={loading}
                title="Use my current location"
            >
                {loading ? (
                    <React.Fragment>
                        <span className="spinner"></span>
                        <span>Getting location...</span>
                    </React.Fragment>
                ) : (
                    <React.Fragment>
                        <span className="location-icon">📍</span>
                        <span>Use My Location</span>
                    </React.Fragment>
                )}
            </button>

            {error && (
                <div className="location-error">
                    <span className="error-icon">⚠️</span>
                    <span>{error}</span>
                </div>
            )}
        </div>
    );
};

export default CurrentLocationButton;