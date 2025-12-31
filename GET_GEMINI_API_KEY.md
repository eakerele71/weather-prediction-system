# How to Get Gemini API Key - Step by Step

## Quick Answer

**You DON'T need to upload a project!** Just skip that step and get your API key directly.

---

## Method 1: Direct API Key (EASIEST - 2 minutes)

### Step 1: Go to Google AI Studio
Open this link: https://aistudio.google.com/app/apikey

### Step 2: Sign In
- Sign in with your Google account
- Any Gmail account works!

### Step 3: Get API Key
1. You'll see a page that says "Get API Key"
2. Click **"Create API Key"**
3. Choose **"Create API key in new project"** (recommended)
4. Click **"Create"**

### Step 4: Copy Your Key
1. Your API key will appear (starts with `AIza...`)
2. Click the **copy icon** to copy it
3. **Save it in a text file** - you'll need it for deployment!

**Done!** That's your Gemini API key.

---

## Method 2: If You See "Upload Project" Screen

If Google asks you to upload a project, here's what to do:

### Option A: Skip It (Recommended)
1. Look for a **"Skip"** or **"Continue without project"** button
2. Click it
3. You'll go straight to the API key page

### Option B: Create a Simple Project
If there's no skip button:

1. **Project Name:** Type anything (e.g., "Weather App")
2. **Description:** Type anything (e.g., "Weather prediction system")
3. **Upload files:** Click **"Skip"** or leave empty
4. Click **"Continue"** or **"Next"**
5. You'll get to the API key page

---

## What If I'm Stuck?

### Screen 1: "Welcome to Google AI Studio"
- Click **"Get API Key"** button
- Or click **"API Key"** in the left sidebar

### Screen 2: "Create API Key"
- Click **"Create API key in new project"**
- Wait 5 seconds
- Your key will appear!

### Screen 3: "Upload Project" (Optional)
- This is OPTIONAL - you can skip it
- Look for "Skip" or "Continue without project"
- Or just close this dialog and look for "API Key" in the menu

---

## Alternative: Use Google Cloud Console

If the above doesn't work, try this:

### Step 1: Go to Google Cloud
https://console.cloud.google.com

### Step 2: Create Project (if needed)
1. Click project dropdown at top
2. Click "New Project"
3. Name: "Weather App"
4. Click "Create"

### Step 3: Enable Gemini API
1. Go to: https://console.cloud.google.com/apis/library
2. Search for "Generative Language API"
3. Click on it
4. Click "Enable"

### Step 4: Create API Key
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "API Key"
3. Copy your API key
4. Click "Restrict Key" (optional but recommended)
5. Under "API restrictions", select "Generative Language API"
6. Click "Save"

---

## Important Notes

### About the API Key
- ✅ It's FREE to use
- ✅ Generous free tier (60 requests per minute)
- ✅ No credit card required
- ✅ Starts with `AIza...`

### Keep It Safe
- ❌ Don't share it publicly
- ❌ Don't commit it to GitHub
- ✅ Store it in `.env` file (which is in .gitignore)
- ✅ Only use it in environment variables

### Free Tier Limits
- 60 requests per minute
- 1,500 requests per day
- More than enough for your weather app!

---

## Testing Your API Key

Once you have your key, test it:

### Option 1: In Google AI Studio
1. Go to: https://aistudio.google.com
2. Click "Chat" or "Prompt"
3. Type a test message
4. If it works, your key is valid!

### Option 2: Quick Test (Command Line)
```bash
curl https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=YOUR_API_KEY \
  -H 'Content-Type: application/json' \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
```

Replace `YOUR_API_KEY` with your actual key.

If you get a response, it works!

---

## What to Do Next

Once you have your Gemini API key:

1. **Save it** in a text file with your OpenWeather API key
2. **Continue with deployment** - follow `RENDER_QUICK_START.md`
3. **Add it to Render** when deploying (Step 4 in the guide)

---

## Quick Recap

1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)
5. Save it somewhere safe
6. Continue with Render deployment!

**Time:** 2 minutes
**Cost:** FREE
**Credit card:** Not required

---

## Still Stuck?

Tell me:
1. What screen are you seeing?
2. What does it say?
3. Is there a "Skip" button?

I'll help you get past it! 🚀
