#!/bin/bash

# Railway Open WebUI Deployment Script
# Deploys Open WebUI as a separate Railway service

echo "🚀 Deploying Open WebUI to Railway Production"
echo "=============================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
railway login

# Create new Railway project for Open WebUI
echo "📦 Creating Railway project for Open WebUI..."
railway init --name "tilores-openwebui"

# Set environment variables
echo "⚙️ Configuring environment variables..."
railway variables set OPENAI_API_BASE_URL="https://tilores-x.up.railway.app"
railway variables set OPENAI_API_KEY="dummy"
railway variables set WEBUI_AUTH="true"
railway variables set WEBUI_SECRET_KEY="$(openssl rand -base64 32)"
railway variables set ENABLE_COMMUNITY_SHARING="true"
railway variables set ENABLE_MESSAGE_RATING="true"
railway variables set ENABLE_MODEL_FILTER="true"
railway variables set ENABLE_EVALUATION_ARENA="true"
railway variables set ENABLE_ADMIN_EXPORT="true"
railway variables set ENABLE_ADMIN_CHAT_ACCESS="true"
railway variables set TASK_MODEL="gpt-4o-mini"
railway variables set TITLE_GENERATION_PROMPT_TEMPLATE="Generate a concise title for this conversation"
railway variables set WEBHOOK_URL="https://tilores-x.up.railway.app/webhooks/openwebui-rating"
railway variables set ENABLE_SIGNUP="false"
railway variables set DEFAULT_USER_ROLE="user"

# Deploy using Docker
echo "🚢 Deploying Open WebUI..."
railway up --dockerfile Dockerfile.openwebui

echo "✅ Open WebUI deployment initiated!"
echo ""
echo "📋 Next Steps:"
echo "1. Wait for deployment to complete (check Railway dashboard)"
echo "2. Get the production URL from Railway dashboard"
echo "3. Create admin account on first visit"
echo "4. Configure team access"
echo ""
echo "🎯 The Open WebUI will automatically connect to:"
echo "   Tilores API: https://tilores-x.up.railway.app"
echo "   Available Models: 9 (OpenAI, Google, Groq)"
