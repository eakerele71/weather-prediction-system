# 🚀 START HERE - Railway Deployment

Your weather app is ready to deploy! Follow these simple steps.

---

## 🎯 What You Need

✅ GitHub account (you have it)  
✅ Code on GitHub (done: https://github.com/eakerele71/weather-prediction-system)  
✅ OpenWeather API key (you have it)  
✅ Gemini API key (you have it)  

---

## 📝 Quick Steps (20 minutes total)

### Step 1: Sign Up (2 min)
1. Go to **https://railway.app**
2. Click **"Login with GitHub"**
3. Authorize Railway

### Step 2: Deploy Backend (8 min)
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose **"weather-prediction-system"**
4. Click **"New"** → **"Database"** → **"PostgreSQL"**
5. Click on your backend service
6. Go to **"Settings"** tab:
   - Root Directory: `backend`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Go to **"Variables"** tab and add:
   ```
   OPENWEATHER_API_KEY=your_key_here
   GEMINI_API_KEY=your_key_here
   JWT_SECRET_KEY=make-this-a-long-random-string-32-chars
   USE_MOCK_DB=false
   ```
8. Wait 5 minutes for build to complete
9. Go to **"Settings"** → **"Networking"** → **"Generate Domain"**
10. **Copy your backend URL** (you'll need it next)

### Step 3: Test Backend (1 min)
Open in browser: `https://your-backend-url/api/v1/health`

Should see: `{"status": "healthy"}`

### Step 4: Deploy Frontend (8 min)
1. Click **"New"** → **"GitHub Repo"** → **"weather-prediction-system"**
2. Click on the new service
3. Go to **"Settings"** tab:
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npx serve -s build -l $PORT`
4. Go to **"Variables"** tab and add:
   ```
   REACT_APP_API_URL=https://your-backend-url-from-step-2
   ```
5. Wait 5 minutes for build
6. Go to **"Settings"** → **"Networking"** → **"Generate Domain"**

### Step 5: Test Everything (1 min)
1. Open your frontend URL
2. Search for "London"
3. Check if weather loads
4. Try the AI chat

---

## ✅ Done!

Your app is live! 🎉

**URLs:**
- **Frontend:** https://your-frontend-url.up.railway.app
- **Backend:** https://your-backend-url.up.railway.app
- **API Docs:** https://your-backend-url.up.railway.app/docs

---

## 💰 Cost

- **$5 free credit per month**
- Your app uses ~$2-3/month
- Credit card NOT required to start

---

## 📚 Need More Details?

- **Quick checklist:** `RAILWAY_QUICK_START.md`
- **Full guide:** `RAILWAY_DEPLOYMENT_GUIDE.md`

---

## 🆘 Having Issues?

**Backend won't build?**
- Check environment variables are correct
- Verify root directory is `backend`
- Look at deployment logs

**Frontend can't connect?**
- Make sure `REACT_APP_API_URL` has your backend URL
- Include `https://` in the URL
- No trailing slash

**Database errors?**
- Railway auto-creates `DATABASE_URL`
- Don't add it manually
- Make sure PostgreSQL service is running

---

## 🚀 Ready to Start?

Go to: **https://railway.app**

Let me know when you're signed up and I'll help with any issues!
