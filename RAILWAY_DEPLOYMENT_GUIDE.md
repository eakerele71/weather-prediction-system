# 🚂 Railway Deployment Guide

Complete step-by-step guide to deploy your Weather Prediction System on Railway.

---

## 📋 Prerequisites

- ✅ GitHub account (you have: eakerele71)
- ✅ Code pushed to GitHub (https://github.com/eakerele71/weather-prediction-system)
- ✅ OpenWeather API key
- ✅ Gemini API key

---

## 🚀 Step 1: Sign Up for Railway

1. Go to **https://railway.app**
2. Click **"Login"** in the top right
3. Select **"Login with GitHub"**
4. Authorize Railway to access your GitHub account
5. You'll get **$5 free credit per month** (no credit card required)

---

## 🎯 Step 2: Create New Project

1. Once logged in, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. You'll see a list of your repositories
4. Find and click **"weather-prediction-system"**
5. Railway will detect it's a Python project

---

## 🗄️ Step 3: Add PostgreSQL Database

1. In your project dashboard, click **"New"** button
2. Select **"Database"**
3. Choose **"Add PostgreSQL"**
4. Railway will automatically:
   - Create a PostgreSQL database
   - Generate a `DATABASE_URL` environment variable
   - Connect it to your backend service

---

## ⚙️ Step 4: Configure Backend Service

### 4.1 Find Your Backend Service
- Look for the service named after your repo (weather-prediction-system)
- Click on it to open settings

### 4.2 Add Environment Variables
1. Click on the **"Variables"** tab
2. Click **"New Variable"** and add these one by one:

```
OPENWEATHER_API_KEY=your_actual_openweather_key_here
GEMINI_API_KEY=your_actual_gemini_key_here
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
USE_MOCK_DB=false
```

**Important Notes:**
- Replace `your_actual_openweather_key_here` with your real OpenWeather API key
- Replace `your_actual_gemini_key_here` with your real Gemini API key
- For `JWT_SECRET_KEY`, use a random string (at least 32 characters)
- `DATABASE_URL` is automatically added by Railway (don't add it manually)

### 4.3 Configure Root Directory
1. Still in your backend service settings
2. Click on **"Settings"** tab
3. Find **"Root Directory"**
4. Set it to: `backend`
5. Click **"Save"**

### 4.4 Configure Start Command
1. In the same **"Settings"** tab
2. Find **"Start Command"**
3. Set it to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Click **"Save"**

---

## 🔨 Step 5: Deploy Backend

1. Railway will automatically start building your backend
2. Watch the **"Deployments"** tab for progress
3. Build takes about 3-5 minutes
4. Look for these messages:
   - ✅ "Building..."
   - ✅ "Installing dependencies..."
   - ✅ "Build successful"
   - ✅ "Deployment live"

### If Build Fails:
- Check the logs in the "Deployments" tab
- Make sure all environment variables are set correctly
- Verify the root directory is set to `backend`

---

## 🌐 Step 6: Get Your Backend URL

1. Click on your backend service
2. Go to **"Settings"** tab
3. Scroll to **"Networking"** section
4. Click **"Generate Domain"**
5. Railway will give you a URL like: `https://weather-prediction-system-production.up.railway.app`
6. **Copy this URL** - you'll need it for the frontend

### Test Your Backend:
Open in browser: `https://your-backend-url.up.railway.app/api/v1/health`

You should see:
```json
{
  "status": "healthy",
  "service": "weather-prediction-system"
}
```

---

## 🎨 Step 7: Deploy Frontend

### 7.1 Add Frontend Service
1. In your Railway project, click **"New"**
2. Select **"GitHub Repo"**
3. Choose **"weather-prediction-system"** again
4. Railway will create a second service

### 7.2 Configure Frontend Service
1. Click on the new service
2. Go to **"Settings"** tab
3. Set **"Root Directory"** to: `frontend`
4. Set **"Build Command"** to: `npm install && npm run build`
5. Set **"Start Command"** to: `npx serve -s build -l $PORT`

### 7.3 Add Frontend Environment Variables
1. Click **"Variables"** tab
2. Add this variable:
```
REACT_APP_API_URL=https://your-backend-url.up.railway.app
```
Replace with your actual backend URL from Step 6

### 7.4 Generate Frontend Domain
1. Go to **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. You'll get a URL like: `https://weather-prediction-system-frontend.up.railway.app`

---

## ✅ Step 8: Verify Deployment

### Test Backend:
```
https://your-backend-url.up.railway.app/api/v1/health
https://your-backend-url.up.railway.app/docs
```

### Test Frontend:
```
https://your-frontend-url.up.railway.app
```

### Test Full Integration:
1. Open your frontend URL
2. Search for a city (e.g., "London")
3. Check if weather data loads
4. Try the Gemini AI chat
5. Check forecasts and warnings

---

## 🔧 Step 9: Database Setup (Optional)

If you need to initialize the database with tables:

1. Go to your PostgreSQL service in Railway
2. Click **"Data"** tab
3. Click **"Query"** to open SQL console
4. Copy and paste the contents of `init-db.sql` from your repo
5. Click **"Run"**

**Note:** Your app should auto-create tables on first run, so this is usually not needed.

---

## 💰 Cost Breakdown

Railway gives you **$5 free credit per month**. Here's typical usage:

- **Backend API**: ~$1-2/month
- **PostgreSQL**: ~$1/month
- **Frontend**: ~$0.50/month
- **Total**: ~$2.50-3.50/month

Your $5 credit covers this with room to spare!

---

## 🐛 Troubleshooting

### Backend won't start:
- Check environment variables are set correctly
- Verify root directory is `backend`
- Check deployment logs for errors

### Frontend can't connect to backend:
- Verify `REACT_APP_API_URL` is set correctly
- Make sure backend URL includes `https://`
- Check CORS settings in backend

### Database connection errors:
- Railway auto-generates `DATABASE_URL`
- Don't manually add `DATABASE_URL` variable
- Check PostgreSQL service is running

### Build takes too long:
- First build takes 5-10 minutes (installing scikit-learn)
- Subsequent builds are faster (cached)

---

## 📊 Monitoring

### View Logs:
1. Click on any service
2. Go to **"Deployments"** tab
3. Click on latest deployment
4. View real-time logs

### Check Usage:
1. Click on your project name
2. Go to **"Usage"** tab
3. See how much of your $5 credit you've used

---

## 🔄 Auto-Deployments

Railway automatically deploys when you push to GitHub:

1. Make changes to your code locally
2. Commit and push to GitHub:
   ```cmd
   git add .
   git commit -m "Your changes"
   git push origin main
   ```
3. Railway detects the push and auto-deploys
4. Wait 2-3 minutes for deployment

---

## 🎉 You're Done!

Your weather prediction system is now live on Railway!

**Share your app:**
- Frontend: `https://your-frontend-url.up.railway.app`
- API Docs: `https://your-backend-url.up.railway.app/docs`

---

## 📝 Next Steps

1. Test all features thoroughly
2. Share the URL with friends/portfolio
3. Monitor usage in Railway dashboard
4. Add custom domain (optional, requires paid plan)

---

## ❓ Need Help?

If you run into issues:
1. Check the deployment logs in Railway
2. Verify all environment variables
3. Test backend health endpoint
4. Let me know what error you're seeing!
