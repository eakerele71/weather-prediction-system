# 🌤️ Weather Prediction System

ML-powered weather forecasting with real-time analytics, AI chat assistant, and beautiful visualizations.

## ✨ Features

- 🌍 **Real-time Weather Data** - Current conditions for any city worldwide
- 📅 **7-Day Forecasts** - Detailed predictions with confidence scores
- ⚠️ **Weather Warnings** - Alerts for severe weather conditions
- 📊 **Analytics Dashboard** - Temperature trends, precipitation, humidity, pressure
- 🤖 **AI Chat Assistant** - Ask questions about weather (powered by Google Gemini)
- 🧭 **Interactive Visualizations** - Wind compass, UV index gauge, charts
- ⭐ **Favorites** - Save your favorite locations
- 🎨 **Beautiful UI** - Responsive blue-themed design

## 🚀 Quick Deploy to Render.com (FREE)

**Total Time:** 25 minutes

### Prerequisites

1. **GitHub Account** - https://github.com
2. **OpenWeather API Key** (FREE) - https://openweathermap.org/api
3. **Gemini API Key** (FREE) - https://makersuite.google.com/app/apikey

### Deployment Steps

1. **Read the guide:** `START_HERE_RENDER.md`
2. **Follow the checklist:** `RENDER_QUICK_START.md`
3. **Detailed instructions:** `RENDER_DEPLOYMENT_GUIDE.md`

Your app will be live at: `https://your-app.onrender.com`

## 📚 Documentation

- **`START_HERE_RENDER.md`** - Start here for deployment
- **`RENDER_QUICK_START.md`** - Quick checklist format
- **`RENDER_DEPLOYMENT_GUIDE.md`** - Detailed step-by-step guide

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database (TimescaleDB for time-series data)
- **Scikit-learn** - Machine learning for predictions
- **Google Gemini** - AI chat assistant
- **JWT** - Secure authentication

### Frontend
- **React 18** - UI framework
- **Chart.js** - Data visualizations
- **Axios** - API communication
- **Context API** - State management

### Hosting
- **Render.com** - FREE cloud hosting
- PostgreSQL database included
- Automatic HTTPS
- Auto-deploy from GitHub

## 🎯 What You Get

After deployment:
- ✅ Live website accessible from anywhere
- ✅ Real PostgreSQL database
- ✅ HTTPS security (automatic)
- ✅ Professional hosting
- ✅ Automatic deployments
- ✅ FREE forever (with limitations)

## 💰 Cost

**$0/month** - Everything runs on Render's free tier!

**Free tier includes:**
- PostgreSQL database (1GB storage)
- Backend API (750 hours/month)
- Frontend hosting (unlimited)

**Only limitation:** Backend sleeps after 15 min of inactivity (wakes in 30 seconds)

## 🧪 Testing

Backend includes comprehensive test suite:
- 226+ tests passing
- Unit tests for all components
- Property-based tests using Hypothesis
- 100% feature coverage

Run tests:
```bash
cd backend
python -m pytest tests/ -v
```

## 📖 API Documentation

Once deployed, visit: `https://your-backend.onrender.com/docs`

Interactive API documentation with:
- All endpoints documented
- Try-it-out functionality
- Request/response examples
- Authentication testing

## 🔐 Security

- JWT-based authentication
- Bcrypt password hashing
- HTTPS encryption (automatic on Render)
- Environment variable protection
- Input validation
- Rate limiting on AI endpoints

## 🌟 Key Features Explained

### Weather Data
- Real-time data from OpenWeather API
- 7-day forecasts with hourly breakdowns
- Confidence scores for predictions
- Historical data tracking

### Analytics
- Temperature trends over time
- Precipitation probability charts
- Humidity and pressure tracking
- Wind speed and direction compass
- UV index gauge

### AI Chat Assistant
- Natural language weather queries
- Personalized recommendations
- Weather pattern explanations
- Powered by Google Gemini

### Warnings System
- Severity-based alerts (low, moderate, high, severe)
- Multiple warning types (storm, heat, flood, wind, air quality)
- Safety recommendations
- Real-time updates

## 🎨 Design

- Blue color theme (#0066CC primary)
- Responsive design (desktop, tablet, mobile)
- Smooth animations and transitions
- Accessible with ARIA labels
- Modern, clean interface

## 📱 Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers

## 🤝 Contributing

This is a portfolio project. Feel free to fork and customize!

## 📄 License

MIT License - feel free to use for your own projects

## 🆘 Need Help?

1. Check `RENDER_DEPLOYMENT_GUIDE.md` for detailed instructions
2. Review `RENDER_QUICK_START.md` for quick steps
3. See troubleshooting section in deployment guide

## 🎉 Ready to Deploy?

1. Get your API keys (5 minutes)
2. Follow `START_HERE_RENDER.md`
3. Your app will be live in 25 minutes!

---

**Built with ❤️ using FastAPI, React, and Machine Learning**
