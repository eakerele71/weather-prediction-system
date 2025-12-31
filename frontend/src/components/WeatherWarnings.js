import { useState } from 'react';
import { useWeather } from '../context/WeatherContext';
import './WeatherWarnings.css';

const WeatherWarnings = () => {
  const { warnings } = useWeather();
  const [expandedWarning, setExpandedWarning] = useState(null);

  if (!warnings || warnings.length === 0) {
    return null;
  }

  // Get severity color and icon
  const getSeverityStyle = (severity) => {
    const styles = {
      low: {
        color: '#f59e0b',
        bgColor: '#fef3c7',
        borderColor: '#fbbf24',
        icon: '⚠️',
        label: 'Low',
      },
      moderate: {
        color: '#f97316',
        bgColor: '#ffedd5',
        borderColor: '#fb923c',
        icon: '⚠️',
        label: 'Moderate',
      },
      high: {
        color: '#ef4444',
        bgColor: '#fee2e2',
        borderColor: '#f87171',
        icon: '🚨',
        label: 'High',
      },
      severe: {
        color: '#dc2626',
        bgColor: '#fecaca',
        borderColor: '#ef4444',
        icon: '🚨',
        label: 'Severe',
      },
    };
    return styles[severity?.toLowerCase()] || styles.moderate;
  };

  // Get warning type icon
  const getWarningTypeIcon = (type) => {
    const icons = {
      storm: '⛈️',
      heat: '🌡️',
      flood: '🌊',
      wind: '💨',
      air_quality: '😷',
    };
    return icons[type?.toLowerCase()] || '⚠️';
  };

  // Format warning type for display
  const formatWarningType = (type) => {
    return type
      ?.split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ') || 'Weather Warning';
  };

  const toggleWarning = (index) => {
    setExpandedWarning(expandedWarning === index ? null : index);
  };

  return (
    <div className="weather-warnings-container">
      <div className="warnings-header">
        <h3 className="warnings-title">
          <span className="warnings-icon">🚨</span>
          Active Weather Warnings
        </h3>
        <span className="warnings-count">{warnings.length}</span>
      </div>

      <div className="warnings-list">
        {warnings.map((warning, index) => {
          const severityStyle = getSeverityStyle(warning.severity);
          const isExpanded = expandedWarning === index;

          return (
            <div
              key={index}
              className="warning-card"
              style={{
                backgroundColor: severityStyle.bgColor,
                borderColor: severityStyle.borderColor,
              }}
            >
              <div
                className="warning-header"
                onClick={() => toggleWarning(index)}
              >
                <div className="warning-header-left">
                  <span className="warning-type-icon">
                    {getWarningTypeIcon(warning.warning_type)}
                  </span>
                  <div className="warning-header-text">
                    <h4 className="warning-type" style={{ color: severityStyle.color }}>
                      {formatWarningType(warning.warning_type)}
                    </h4>
                    <span className="warning-severity" style={{ color: severityStyle.color }}>
                      {severityStyle.icon} {severityStyle.label} Severity
                    </span>
                  </div>
                </div>
                <button
                  className="warning-expand-btn"
                  aria-label={isExpanded ? 'Collapse' : 'Expand'}
                >
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    style={{
                      transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                      transition: 'transform 0.3s ease',
                    }}
                  >
                    <path
                      d="M5 7.5L10 12.5L15 7.5"
                      stroke={severityStyle.color}
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </button>
              </div>

              {warning.description && (
                <div className="warning-description">
                  {warning.description}
                </div>
              )}

              {isExpanded && (
                <div className="warning-details">
                  {warning.start_time && (
                    <div className="warning-time">
                      <strong>Start:</strong>{' '}
                      {new Date(warning.start_time).toLocaleString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  )}

                  {warning.end_time && (
                    <div className="warning-time">
                      <strong>End:</strong>{' '}
                      {new Date(warning.end_time).toLocaleString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  )}

                  {warning.safety_recommendations && warning.safety_recommendations.length > 0 && (
                    <div className="safety-recommendations">
                      <h5 className="recommendations-title">Safety Recommendations:</h5>
                      <ul className="recommendations-list">
                        {warning.safety_recommendations.map((rec, recIndex) => (
                          <li key={recIndex} className="recommendation-item">
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default WeatherWarnings;
