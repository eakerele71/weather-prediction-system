# ⚡ Railway Quick Start Checklist

Follow these steps in order. Check off each one as you complete it.

---

## ✅ Checklist

### 1. Sign Up (2 minutes)
- [ ] Go to https://railway.app
- [ ] Click "Login with GitHub"
- [ ] Authorize Railway

### 2. Create Project (1 minute)
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose "weather-prediction-system"

### 3. Add Database (1 minute)
- [ ] Click "New" → "Database" → "PostgreSQL"
- [ ] Wait for database to provision

### 4. Configure Backend (3 minutes)
- [ ] Click on backend service
- [ ] Go to "Settings" tab
- [ ] Set Root Directory: `backend`
- [ ] Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Go to "Variables" tab
- [ ] Add these variables:
  - `OPENWEATHER_API_KEY` = your key
  - `GEMINI_API_KEY` = your key
  - `JWT_SECRET_KEY` = random-secret-string-32-chars-min
  - `USE_MOCK_DB` = false

### 5. Deploy Backend (5 minutes)
- [ ] Wait for automatic deployment
- [ ] Check "Deployments" tab for success
- [ ] Go to "Settings" → "Networking"
- [ ] Click "Generate Domain"
- [ ] Copy your backend URL

### 6. Test Backend (1 minute)
- [ ] Open: `https://your-backend-url/api/v1/health`
- [ ] Should see: `{"status": "healthy"}`

### 7. Deploy Frontend (5 minutes)
- [ ] Click "New" → "GitHub Repo" → "weather-prediction-system"
- [ ] Click on new service
- [ ] Go to "Settings"
- [ ] Set Root Directory: `frontend`
- [ ] Set Build Command: `npm install && npm run build`
- [ ] Set Start Command: `npx serve -s build -l $PORT`
- [ ] Go to "Variables" tab
- [ ] Add: `REACT_APP_API_URL` = your backend URL
- [ ] Generate domain for frontend

### 8. Test Everything (2 minutes)
- [ ] Open frontend URL
- [ ] Search for a city
- [ ] Check weather loads
- [ ] Try Gemini chat
- [ ] Verify forecasts work

---

## 🎉 Done!

**Total Time:** ~20 minutes

**Your URLs:**
- Frontend: `https://your-frontend-url.up.railway.app`
- Backend: `https://your-backend-url.up.railway.app`
- API Docs: `https://your-backend-url.up.railway.app/docs`

---

## 💡 Tips

- First deployment takes 5-10 minutes (installing ML packages)
- Railway auto-deploys on every GitHub push
- Check "Usage" tab to monitor your $5 credit
- Logs are in "Deployments" tab

---

## 🆘 Having Issues?

Check the full guide: `RAILWAY_DEPLOYMENT_GUIDE.md`
