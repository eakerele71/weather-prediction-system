# Weather App - API Testing Guide

## Prerequisites

1. **OpenWeather API Key** (Free - get from https://openweathermap.org/api)
2. **Python packages**: `uvicorn`, `fastapi`, `httpx`, `requests`

## Setup Steps

### 1. Create Environment File

Create `backend/.env` with your API key:

```bash
OPENWEATHER_API_KEY=your_api_key_here
GEMINI_API_KEY=optional_gemini_key
USE_MOCK_DB=true
```

### 2. Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 3. Run API Tests

In a new terminal:

```bash
cd "c:\Users\EMMANUEL\Documents\wether forcasting bot"
python test_api.py
```

## Expected Results

### ✅ Valid Locations (Should Pass)
- **London** → Shows weather data
- **New York** → Shows weather data
- **Tokyo** → Shows weather data
- **Paris** → Shows weather data

### ❌ Invalid Locations (Should Fail)
- **rice and beans** → 404 Error
- **pizza** → 404 Error
- **12345** → 404 Error
- **asdf** → 404 Error
- **xyz123** → 404 Error

## Manual API Testing (Using Browser)

### Test Valid Location
```
http://localhost:8000/api/v1/current/London
```

Expected Response:
```json
{
  "location": {
    "city": "London",
    "country": "GB",
    "latitude": 51.5074,
    "longitude": -0.1278
  },
  "temperature": 15.5,
  "humidity": 70,
  "weather_condition": "Clouds",
  ...
}
```

### Test Invalid Location
```
http://localhost:8000/api/v1/current/xyz123
```

Expected Response:
```json
{
  "detail": "Location not found: 'xyz123'. Please enter a valid city, state, or country name."
}
```

## API Documentation

Once backend is running, visit:
```
http://localhost:8000/docs
```

This shows interactive API documentation where you can test all endpoints!

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify `.env` file exists in `backend/` directory
- Check Python dependencies are installed

### Location validation not working
- Verify `OPENWEATHER_API_KEY` is set correctly
- Check internet connection (API requires external calls)
- Look at backend logs for error messages

### Frontend testing
```bash
cd frontend
npm run dev
```

Then open http://localhost:3000 and test in the UI!
