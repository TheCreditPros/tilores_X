#!/bin/bash

# Configure Open WebUI Production Environment Variables
# Project ID: fa9936b3-30d3-4a07-a3c5-a0b2a975e343

echo "🚀 Configuring Open WebUI Production Environment Variables"
echo "========================================================="

# Link to the Open WebUI project
echo "🔗 Linking to Open WebUI project..."
railway link --project fa9936b3-30d3-4a07-a3c5-a0b2a975e343

# Set all environment variables
echo "⚙️ Setting environment variables..."

# Connection to Tilores API
railway variables --set "OPENAI_API_BASE_URL=https://tilores-x.up.railway.app"
railway variables --set "OPENAI_API_KEY=dummy"

# Authentication & Security
railway variables --set "WEBUI_AUTH=true"
railway variables --set "WEBUI_SECRET_KEY=$(openssl rand -base64 32)"
railway variables --set "ENABLE_SIGNUP=false"
railway variables --set "DEFAULT_USER_ROLE=user"

# Team Evaluation Features
railway variables --set "ENABLE_COMMUNITY_SHARING=true"
railway variables --set "ENABLE_MESSAGE_RATING=true"
railway variables --set "ENABLE_MODEL_FILTER=true"
railway variables --set "ENABLE_EVALUATION_ARENA=true"
railway variables --set "ENABLE_ADMIN_EXPORT=true"
railway variables --set "ENABLE_ADMIN_CHAT_ACCESS=true"

# Model Configuration
railway variables --set "TASK_MODEL=gpt-4o-mini"
railway variables --set "TITLE_GENERATION_PROMPT_TEMPLATE=Generate a concise title for this conversation"

# Webhook Integration
railway variables --set "WEBHOOK_URL=https://tilores-x.up.railway.app/webhooks/openwebui-rating"

# Storage Configuration
railway variables --set "DATA_DIR=/app/backend/data"

echo "✅ All environment variables configured!"
echo ""
echo "📋 Next Steps:"
echo "1. Check Railway dashboard for deployment status"
echo "2. Get the production URL from Railway"
echo "3. Access Open WebUI and create admin account"
echo "4. Verify connection to Tilores API (should show 9 models)"
echo ""
echo "🎯 Expected Result:"
echo "   Open WebUI will connect to: https://tilores-x.up.railway.app"
echo "   Available Models: 9 (OpenAI, Google Gemini, Groq)"
