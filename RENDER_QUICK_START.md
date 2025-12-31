# Render Deployment - Quick Checklist

## Before You Start

Get these ready:
- [ ] GitHub account (create at https://github.com)
- [ ] OpenWeather API key (get at https://openweathermap.org/api)
- [ ] Gemini API key (get at https://makersuite.google.com/app/apikey)

---

## Step-by-Step Checklist

### ☐ Step 1: Push to GitHub (10 min)

```bash
# Open Command Prompt (CMD)
cd "C:\Users\EMMANUEL\Documents\wether forcasting bot"

git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/weather-prediction-system.git
git push -u origin main
```

**Stuck?** See detailed instructions in `RENDER_DEPLOYMENT_GUIDE.md` Step 1

---

### ☐ Step 2: Create Render Account (2 min)

1. Go to: https://render.com
2. Click "Get Started"
3. Sign up with GitHub
4. Authorize Render

---

### ☐ Step 3: Deploy Database (3 min)

1. Click "New +" → "PostgreSQL"
2. Name: `weather-db`
3. Plan: **Free**
4. Click "Create Database"
5. **Copy "Internal Database URL"** (save it!)

---

### ☐ Step 4: Deploy Backend (5 min)

1. Click "New +" → "Web Service"
2. Connect your GitHub repo
3. Settings:
   - Name: `weather-backend`
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free**

4. Add Environment Variables:
   - `DATABASE_URL` = (paste Internal Database URL)
   - `OPENWEATHER_API_KEY` = your_key
   - `GEMINI_API_KEY` = your_key
   - `JWT_SECRET_KEY` = any_random_string
   - `USE_MOCK_DB` = false

5. Click "Create Web Service"
6. **Copy your backend URL** (e.g., `https://weather-backend.onrender.com`)

---

### ☐ Step 5: Deploy Frontend (5 min)

1. Click "New +" → "Static Site"
2. Connect your GitHub repo
3. Settings:
   - Name: `weather-frontend`
   - Root Directory: `frontend`
   - Build: `npm install && npm run build`
   - Publish: `build`

4. Add Environment Variable:
   - `REACT_APP_API_URL` = (paste your backend URL)

5. Click "Create Static Site"

---

### ☐ Step 6: Initialize Database (2 min)

1. Go to backend service → "Shell" tab
2. Run:
```bash
apt-get update && apt-get install -y postgresql-client
psql $DATABASE_URL -f /app/../init-db.sql
```

---

### ☐ Step 7: Test! 🎉

1. Open your frontend URL
2. Search for a city
3. Check weather data
4. Try AI chat
5. Test login (username: `testuser`, password: `secret`)

---

## Your URLs

After deployment, save these:

- **Frontend:** `https://weather-frontend.onrender.com`
- **Backend:** `https://weather-backend.onrender.com`
- **API Docs:** `https://weather-backend.onrender.com/docs`

---

## Need Help?

**Detailed guide:** `RENDER_DEPLOYMENT_GUIDE.md`

**Common issues:**
- Can't push to GitHub? Check authentication (use Personal Access Token)
- Backend won't start? Check environment variables
- Frontend can't connect? Verify REACT_APP_API_URL
- Database errors? Make sure init script ran

---

## Total Time: ~25 minutes

- GitHub setup: 10 min
- Render account: 2 min
- Database: 3 min
- Backend: 5 min
- Frontend: 5 min
- Testing: 2 min

---

**Ready?** Start with Step 1! 🚀

Tell me when you complete each step and I'll help if you get stuck!
