# 🚀 Deploy Your GlomoPay Shopping API to Render (FREE!)

## ✅ What You're Deploying:
- Flask API with GlomoPay payment integration
- ChatGPT Custom GPT compatible
- Completely FREE forever (750 hours/month)

---

## 📋 STEP-BY-STEP DEPLOYMENT GUIDE

### **STEP 1: Create a GitHub Account (if you don't have one)**

1. Go to https://github.com
2. Click "Sign up"
3. Create a free account (takes 2 minutes)

---

### **STEP 2: Create a New Repository**

1. Go to https://github.com/new
2. **Repository name:** `glomopay-shopping-api`
3. **Description:** "AI Shopping Assistant with GlomoPay Integration"
4. **Visibility:** Public ✅
5. **Initialize with README:** ❌ Leave unchecked
6. Click **"Create repository"**

---

### **STEP 3: Upload Your Files to GitHub**

After creating the repository, you'll see a page with instructions. Follow these:

#### **Option A: Upload via Web Interface (Easiest)**

1. Click **"uploading an existing file"** link on that page
2. **Drag and drop** these 3 files:
   - `app.py`
   - `requirements.txt`
   - `render.yaml`
3. Scroll down and click **"Commit changes"**

#### **Option B: Use Git Command Line** (if you know Git)

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/glomopay-shopping-api.git
git push -u origin main
```

---

### **STEP 4: Deploy to Render**

1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with your **GitHub account** (click "GitHub" button)
4. Authorize Render to access your repositories

---

### **STEP 5: Create a New Web Service**

1. On Render dashboard, click **"New +"** → **"Web Service"**
2. Find your repository: **"glomopay-shopping-api"**
3. Click **"Connect"**

Render will auto-detect your settings from `render.yaml`, but verify:

- **Name:** `glomopay-shopping-api`
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`
- **Plan:** **Free** ✅

4. Click **"Create Web Service"**

---

### **STEP 6: Add Your GlomoPay API Key**

While it's deploying:

1. In Render, click on **"Environment"** tab (left sidebar)
2. Click **"Add Environment Variable"**
3. **Key:** `GLOMOPAY_API_KEY`
4. **Value:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjcyNzVhYmIxMTczMmJhMTM0ZTliZTJkIiwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTczMTMyMTE4MiwiZXhwIjoxNzMzOTEzMTgyfQ.YWLdoM5Xs3zRVOdjJBd--3mKAiEWBSFvPZW31RLCw`
5. Click **"Save Changes"**

The app will automatically redeploy with the API key.

---

### **STEP 7: Get Your API URL**

1. Wait for deployment to finish (2-3 minutes)
2. You'll see: **"Live ✅"** with a green dot
3. Your URL will be at the top, something like:
   ```
   https://glomopay-shopping-api.onrender.com
   ```
4. **Copy this URL!**

---

### **STEP 8: Test Your API**

Open your URL in a browser:
```
https://glomopay-shopping-api.onrender.com
```

You should see:
```json
{
  "status": "✅ API is running",
  "message": "GlomoPay Shopping Assistant API",
  ...
}
```

🎉 **IT'S LIVE!**

---

### **STEP 9: Update Your ChatGPT Custom GPT**

1. Go to https://chat.openai.com/gpts/editor
2. Click on **"Instant Shop Assistant"**
3. Click **"Configure"** tab
4. Scroll to **"Actions"**
5. Click the **gear icon** ⚙️
6. Find the `servers:` line
7. **Update the URL** to your new Render URL:

```yaml
servers:
  - url: https://glomopay-shopping-api.onrender.com
```

8. Click **"Save"**
9. Click **"Update"** (top right)

---

### **STEP 10: TEST THE FULL FLOW!** 🎉

1. Go to ChatGPT
2. Start a **new chat** with your Custom GPT
3. Type: **"Show me wireless earbuds under $300"**
4. Select a product and provide your email
5. **Get a REAL GlomoPay payment link!**

---

## ✅ YOU'RE DONE!

Your AI Shopping Assistant is now:
- ✅ Live and running 24/7
- ✅ Completely FREE (forever on Render)
- ✅ Integrated with real GlomoPay payments
- ✅ Accessible from ChatGPT Custom GPT

---

## 🔧 Troubleshooting

**Deployment Failed?**
- Check the logs in Render dashboard
- Make sure all 3 files were uploaded correctly
- Verify Python version is 3.11

**API Not Responding?**
- Check if the service shows "Live ✅"
- Try restarting the service in Render
- Check environment variables are set

**ChatGPT Can't Connect?**
- Verify the URL in Actions matches your Render URL exactly
- Start a new chat (fresh session)
- Check that CORS is enabled (it is by default in our code)

---

## 🎯 Next Steps

- Add more products to the PRODUCTS list
- Customize the API responses
- Add webhooks for payment confirmations
- Monitor usage in Render dashboard

---

**Enjoy your FREE, production-ready AI Shopping Assistant!** 🛍️🔥
