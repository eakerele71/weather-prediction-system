-- Initialize TimescaleDB extension and create tables

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Weather data table (time-series)
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL,
    location_id INTEGER NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    humidity DOUBLE PRECISION NOT NULL,
    pressure DOUBLE PRECISION NOT NULL,
    wind_speed DOUBLE PRECISION NOT NULL,
    wind_direction DOUBLE PRECISION NOT NULL,
    precipitation DOUBLE PRECISION NOT NULL,
    cloud_cover DOUBLE PRECISION NOT NULL,
    weather_condition VARCHAR(100) NOT NULL,
    PRIMARY KEY (id, timestamp)
);

-- Convert to hypertable
SELECT create_hypertable('weather_data', 'timestamp', if_not_exists => TRUE);

-- Locations table
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    city VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Forecasts table (time-series)
CREATE TABLE IF NOT EXISTS forecasts (
    id SERIAL,
    location_id INTEGER NOT NULL,
    forecast_date DATE NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL,
    predicted_temp_high DOUBLE PRECISION NOT NULL,
    predicted_temp_low DOUBLE PRECISION NOT NULL,
    precipitation_probability DOUBLE PRECISION NOT NULL,
    weather_condition VARCHAR(100) NOT NULL,
    confidence_score DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (id, generated_at)
);

-- Convert to hypertable
SELECT create_hypertable('forecasts', 'generated_at', if_not_exists => TRUE);

-- Weather warnings table
CREATE TABLE IF NOT EXISTS weather_warnings (
    id SERIAL PRIMARY KEY,
    warning_id VARCHAR(100) UNIQUE NOT NULL,
    location_id INTEGER NOT NULL,
    warning_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    issued_at TIMESTAMPTZ DEFAULT NOW()
);

-- Accuracy metrics table (time-series)
CREATE TABLE IF NOT EXISTS accuracy_metrics (
    id SERIAL,
    date DATE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    temperature_mae DOUBLE PRECISION NOT NULL,
    temperature_rmse DOUBLE PRECISION NOT NULL,
    precipitation_accuracy DOUBLE PRECISION NOT NULL,
    overall_accuracy DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (id, timestamp)
);

-- Convert to hypertable
SELECT create_hypertable('accuracy_metrics', 'timestamp', if_not_exists => TRUE);

-- User locations table
CREATE TABLE IF NOT EXISTS user_locations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    location_id INTEGER NOT NULL,
    is_favorite BOOLEAN DEFAULT FALSE,
    added_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_weather_data_location_time ON weather_data (location_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_forecasts_location_date ON forecasts (location_id, forecast_date);
CREATE INDEX IF NOT EXISTS idx_warnings_location ON weather_warnings (location_id);
CREATE INDEX IF NOT EXISTS idx_user_locations_user ON user_locations (user_id);

-- Create retention policy (remove data older than 1 year)
SELECT add_retention_policy('weather_data', INTERVAL '365 days', if_not_exists => TRUE);
SELECT add_retention_policy('forecasts', INTERVAL '365 days', if_not_exists => TRUE);
SELECT add_retention_policy('accuracy_metrics', INTERVAL '365 days', if_not_exists => TRUE);

-- Create compression policy (compress data older than 30 days)
ALTER TABLE weather_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'location_id'
);

SELECT add_compression_policy('weather_data', INTERVAL '30 days', if_not_exists => TRUE);
