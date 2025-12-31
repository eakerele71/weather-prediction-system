# Weather App Backend

## Quick Start

1. **Setup Configuration**
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenWeather API key:
   ```
   OPENWEATHER_API_KEY=your_actual_api_key_here
   ```

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
