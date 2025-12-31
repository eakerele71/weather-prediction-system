import { useState } from 'react';
import { useWeather } from '../context/WeatherContext';
import WeatherCard from './WeatherCard';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import './AnalyticsCharts.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const AnalyticsCharts = () => {
  const { analytics, forecast } = useWeather();
  const [activeChart, setActiveChart] = useState('temperature');

  if (!analytics && !forecast) {
    return null;
  }

  // Prepare temperature trend data
  const getTemperatureData = () => {
    if (!forecast || forecast.length === 0) return null;

    const labels = forecast.map(day => {
      const dateStr = day.forecast_date || day.date;
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });

    return {
      labels,
      datasets: [
        {
          label: 'High Temperature',
          data: forecast.map(day => day.predicted_temperature_high || day.temperature_high || 0),
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          fill: true,
          tension: 0.4,
        },
        {
          label: 'Low Temperature',
          data: forecast.map(day => day.predicted_temperature_low || day.temperature_low || 0),
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true,
          tension: 0.4,
        },
      ],
    };
  };

  // Prepare precipitation data
  const getPrecipitationData = () => {
    if (!forecast || forecast.length === 0) return null;

    const labels = forecast.map(day => {
      const dateStr = day.forecast_date || day.date;
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });

    return {
      labels,
      datasets: [
        {
          label: 'Precipitation Probability',
          data: forecast.map(day => (day.precipitation_probability || 0) * 100),
          backgroundColor: '#0066CC',
          borderColor: '#0066CC',
          borderWidth: 1,
        },
      ],
    };
  };

  // Prepare humidity data
  const getHumidityData = () => {
    if (!forecast || forecast.length === 0) return null;

    const labels = forecast.map(day => {
      const dateStr = day.forecast_date || day.date;
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });

    return {
      labels,
      datasets: [
        {
          label: 'Humidity',
          data: forecast.map(day => day.humidity || 0),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.2)',
          fill: true,
          tension: 0.4,
        },
      ],
    };
  };

  // Prepare pressure data
  const getPressureData = () => {
    if (!forecast || forecast.length === 0) return null;

    const labels = forecast.map(day => {
      const dateStr = day.forecast_date || day.date;
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });

    return {
      labels,
      datasets: [
        {
          label: 'Pressure',
          data: forecast.map(day => day.pressure || 0),
          borderColor: '#8b5cf6',
          backgroundColor: 'rgba(139, 92, 246, 0.2)',
          fill: true,
          tension: 0.4,
        },
      ],
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: {
            size: 12,
          },
        },
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        cornerRadius: 8,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  const precipitationOptions = {
    ...chartOptions,
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: (value) => value + '%',
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  const charts = [
    { id: 'temperature', label: 'Temperature', icon: '🌡️' },
    { id: 'precipitation', label: 'Precipitation', icon: '💧' },
    { id: 'humidity', label: 'Humidity', icon: '💨' },
    { id: 'pressure', label: 'Pressure', icon: '🌡️' },
  ];

  const renderChart = () => {
    switch (activeChart) {
      case 'temperature':
        const tempData = getTemperatureData();
        return tempData ? (
          <Line data={tempData} options={chartOptions} />
        ) : (
          <div className="no-data">No temperature data available</div>
        );
      case 'precipitation':
        const precipData = getPrecipitationData();
        return precipData ? (
          <Bar data={precipData} options={precipitationOptions} />
        ) : (
          <div className="no-data">No precipitation data available</div>
        );
      case 'humidity':
        const humidityData = getHumidityData();
        return humidityData ? (
          <Line data={humidityData} options={chartOptions} />
        ) : (
          <div className="no-data">No humidity data available</div>
        );
      case 'pressure':
        const pressureData = getPressureData();
        return pressureData ? (
          <Line data={pressureData} options={chartOptions} />
        ) : (
          <div className="no-data">No pressure data available</div>
        );
      default:
        return null;
    }
  };

  return (
    <WeatherCard title="Weather Analytics" className="analytics-charts-card">
      <div className="chart-tabs">
        {charts.map(chart => (
          <button
            key={chart.id}
            className={`chart-tab ${activeChart === chart.id ? 'active' : ''}`}
            onClick={() => setActiveChart(chart.id)}
          >
            <span className="chart-tab-icon">{chart.icon}</span>
            <span className="chart-tab-label">{chart.label}</span>
          </button>
        ))}
      </div>

      <div className="chart-container">
        {renderChart()}
      </div>
    </WeatherCard>
  );
};

export default AnalyticsCharts;
