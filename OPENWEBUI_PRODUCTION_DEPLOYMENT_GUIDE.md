# Open WebUI Production Deployment Guide

## 🎯 **Objective**

Deploy Open WebUI to Railway as a separate production service that connects to the existing Tilores API.

## 🚀 **Method 1: Railway Web Interface (Recommended)**

### **Step 1: Create New Railway Service**

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from Docker Image"**
4. Use image: `ghcr.io/open-webui/open-webui:main`

### **Step 2: Configure Environment Variables**

Add these environment variables in Railway dashboard:

```bash
# Connection to Tilores API
OPENAI_API_BASE_URL=https://tilores-x.up.railway.app
OPENAI_API_KEY=dummy

# Authentication & Security
WEBUI_AUTH=true
WEBUI_SECRET_KEY=your-secret-key-here
ENABLE_SIGNUP=false
DEFAULT_USER_ROLE=user

# Team Evaluation Features
ENABLE_COMMUNITY_SHARING=true
ENABLE_MESSAGE_RATING=true
ENABLE_MODEL_FILTER=true
ENABLE_EVALUATION_ARENA=true
ENABLE_ADMIN_EXPORT=true
ENABLE_ADMIN_CHAT_ACCESS=true

# Model Configuration
TASK_MODEL=gpt-4o-mini
TITLE_GENERATION_PROMPT_TEMPLATE=Generate a concise title for this conversation

# Webhook Integration
WEBHOOK_URL=https://tilores-x.up.railway.app/webhooks/openwebui-rating

# Storage
DATA_DIR=/app/backend/data
```

### **Step 3: Deploy**

1. Click **"Deploy"**
2. Wait for deployment to complete
3. Get the production URL from Railway dashboard

---

## 🚀 **Method 2: Railway CLI (Alternative)**

### **Prerequisites**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

### **Deploy Command**

```bash
# Run the deployment script
./railway-deploy-openwebui.sh
```

---

## 🎯 **Post-Deployment Setup**

### **Step 1: Access Open WebUI**

1. Navigate to your Railway-provided URL (e.g., `https://tilores-openwebui.up.railway.app`)
2. Create admin account on first visit
3. Login with admin credentials

### **Step 2: Verify Connection**

1. Go to **Settings** → **Connections**
2. Verify OpenAI connection shows:
   - **Base URL**: `https://tilores-x.up.railway.app`
   - **Status**: ✅ Connected
   - **Models**: 9 models available

### **Step 3: Team Setup**

1. **Admin Panel**: Configure user roles and permissions
2. **Model Access**: Enable/disable specific models for team members
3. **Evaluation Features**: Configure rating and arena features

---

## 📊 **Expected Results**

### **✅ Production Open WebUI Features:**

- **Team Chat Interface**: Professional UI for all team members
- **9 AI Models**: OpenAI (3), Google Gemini (4), Groq (2)
- **Model Comparison**: Side-by-side evaluation capabilities
- **Rating System**: Feedback collection via webhooks
- **Admin Controls**: User management and model access control
- **Evaluation Arena**: A/B testing between models

### **🔗 Architecture:**

```
Team Members → Open WebUI (Railway) → Tilores API (Railway) → AI Providers
```

### **📈 Benefits:**

- **No Local Setup**: Team accesses via web browser
- **Centralized Management**: Admin controls all access
- **Professional Interface**: ChatGPT-like experience
- **Model Evaluation**: Built-in comparison tools
- **Feedback Collection**: Automatic rating webhooks

---

## 🛠️ **Troubleshooting**

### **Issue**: Models not showing

**Solution**: Check environment variables, ensure `OPENAI_API_BASE_URL` is correct

### **Issue**: Authentication problems

**Solution**: Verify `WEBUI_AUTH=true` and `WEBUI_SECRET_KEY` is set

### **Issue**: Webhook not working

**Solution**: Confirm `WEBHOOK_URL` points to correct Tilores API endpoint

---

## 🎉 **Final Result**

Your team will have a production Open WebUI at a Railway URL (e.g., `https://tilores-openwebui.up.railway.app`) with access to all 9 Tilores AI models for evaluation and daily use.
