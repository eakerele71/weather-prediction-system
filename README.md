# 🌤️ Weather Prediction System

ML-powered weather forecasting with real-time analytics, AI chat assistant, and beautiful visualizations.

## ✨ Features

- 🌍 **Real-time Weather Data** - Current conditions for any city worldwide via OpenWeather API
- ⏰ **Hourly Forecasts** - 48-hour detailed hourly predictions
- 📅 **7-Day Forecasts** - Daily predictions with clickable AI explanations
- ⚠️ **Weather Warnings** - Alerts for severe weather conditions
- 📊 **Analytics Dashboard** - Temperature trends, precipitation, humidity, pressure
- � **AnI Chat Assistant** - Ask questions about weather (powered by Google Gemini)
- 🧭 **Interactive Visualizations** - Wind compass, UV index gauge, charts
- ⭐ **Favorites** - Save your favorite locations
- 🔍 **Location Validation** - Shows error for invalid city/country names

## 🚀 Quick Deploy to Render.com (FREE)

### Prerequisites

1. **GitHub Account** - https://github.com
2. **OpenWeather API Key** (FREE) - https://openweathermap.org/api
3. **Gemini API Key** (FREE) - https://makersuite.google.com/app/apikey

### Step 1: Fork Repository
Fork this repo to your GitHub account.

### Step 2: Deploy Backend on Render
1. Go to https://render.com and sign up
2. Click "New" → "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name:** `weather-backend`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `OPENWEATHER_API_KEY` = your OpenWeather key
   - `GEMINI_API_KEY` = your Gemini key
   - `SECRET_KEY` = any random string
6. Click "Create Web Service"

### Step 3: Deploy Frontend on Render
1. Click "New" → "Static Site"
2. Connect same GitHub repo
3. Configure:
   - **Name:** `weather-frontend`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `build`
4. Add Environment Variable:
   - `REACT_APP_API_URL` = your backend URL (e.g., `https://weather-backend.onrender.com`)
5. Click "Create Static Site"

Your app will be live at your frontend URL!

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **OpenWeather API** - Real-time weather data
- **Google Gemini** - AI chat assistant
- **Scikit-learn** - ML predictions

### Frontend
- **React 18** - UI framework
- **Chart.js** - Data visualizations
- **Axios** - API communication

## 💰 Cost

**$0/month** - Everything runs on Render's free tier!

## 🧪 Local Development

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Environment Variables
Create `.env` files:

**backend/.env:**
```
OPENWEATHER_API_KEY=your_key
GEMINI_API_KEY=your_key
SECRET_KEY=your_secret
```

**frontend/.env:**
```
REACT_APP_API_URL=http://localhost:8000
```

## 📖 API Documentation

Once running, visit: `http://localhost:8000/docs`

## 📄 License

MIT License

---

**Built with ❤️ using FastAPI, React, and Machine Learning**
