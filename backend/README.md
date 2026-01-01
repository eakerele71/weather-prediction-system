# Weather App Backend

## Quick Start

1. **Setup Configuration**
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your keys:
   ```env
   # Required for Weather Data
   OPENWEATHER_API_KEY=your_openweather_key
   
   # Required for "Use My Location" (Reverse Geocoding)
   GOOGLE_MAPS_API_KEY=your_google_maps_key
   ```
   
   ### How to get Keys
   - **OpenWeather**: [Get Free Key](https://openweathermap.org/api)
   - **Google Maps**:
     1. Go to [Google Cloud Console](https://console.cloud.google.com/)
     2. Create a new project
     3. Enable **"Geocoding API"**
     4. Create Credentials -> API Key
     5. (Recommended) Restrict the key to use only Geocoding API

2. **Run the Server**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Verify**
   Open http://localhost:8000/docs to see the API documentation.

## Running Tests

To test the API validation:
```bash
cd ..
python test_api.py
```
