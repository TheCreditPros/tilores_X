#!/bin/bash

# OpenWebUI Environment Variables Configuration
# Use this script to configure the new OpenWebUI service after recreation

echo "🔧 OpenWebUI Environment Variables Configuration"
echo "================================================"
echo ""
echo "Copy and paste these environment variables into the new OpenWebUI service:"
echo ""

cat << 'EOF'
# Core OpenWebUI Configuration
WEBUI_AUTH=true
WEBUI_SECRET_KEY=MYuX4/TwZ5oNRrPHzbw0CQIgXWC2qhw2am2U4ycygI8=
ENABLE_SIGNUP=true
DEFAULT_USER_ROLE=user
ADMIN_EMAIL=damon@thecreditpros.com

# Tilores API Integration
OPENAI_API_BASE_URL=https://tilores-x.up.railway.app/v1
OPENAI_API_KEY=dummy
AUTO_DISCOVER_MODELS=true
OPENAI_API_MODELS=gpt-4o,gpt-4o-mini,gpt-3.5-turbo,gemini-1.5-flash,gemini-1.5-pro,gemini-2.0-flash-exp,gemini-2.5-flash,llama-3.3-70b-versatile,deepseek-r1-distill-llama-70b

# Team Evaluation Features
ENABLE_COMMUNITY_SHARING=true
ENABLE_MESSAGE_RATING=true
ENABLE_MODEL_FILTER=true
ENABLE_EVALUATION_ARENA=true
ENABLE_ADMIN_EXPORT=true
ENABLE_ADMIN_CHAT_ACCESS=true
ENABLE_ADMIN_CREATION=true

# Chat Logging and Webhooks
ENABLE_CHAT_LOGGING=true
ENABLE_MESSAGE_LOGGING=true
LOG_CHAT_MESSAGES=true
LOG_USER_INTERACTIONS=true
SEND_CHAT_WEBHOOKS=true

CHAT_COMPLETION_WEBHOOK=https://tilores-x.up.railway.app/webhooks/chat/completion
CHAT_LOGGING_WEBHOOK_URL=https://tilores-x.up.railway.app/webhooks/chat/completion
WEBHOOK_CHAT_COMPLETION=https://tilores-x.up.railway.app/webhooks/chat/completion
WEBHOOK_FULL_CONVERSATION=https://tilores-x.up.railway.app/webhooks/chat/conversation
WEBHOOK_URL=https://tilores-x.up.railway.app/webhooks/openwebui-rating

# Performance and Security
REQUEST_TIMEOUT=300
UPLOAD_TIMEOUT=300
MAX_UPLOAD_SIZE=100MB
CONNECTION_POOL_SIZE=20
CHUNK_SIZE=8192

# CORS Configuration
CORS_ALLOW_ORIGIN=*
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=*
CORS_ALLOW_CREDENTIALS=true

# WebSocket Configuration
ENABLE_WEBSOCKET=true
WEBSOCKET_PING_INTERVAL=25
WEBSOCKET_PING_TIMEOUT=60
WEBSOCKET_TIMEOUT=300

# Model Configuration
TASK_MODEL=gpt-4o-mini
TITLE_GENERATION_PROMPT_TEMPLATE=Generate a concise title for this conversation
ENABLE_OPENAI_API=true
ENABLE_MODEL_UPLOAD=false
ENABLE_MODEL_WHITELISTING=false

# User Agent
USER_AGENT=TiloresOpenWebUI/1.0
LANGCHAIN_USER_AGENT=TiloresOpenWebUI/1.0
EOF

echo ""
echo "🎯 CRITICAL DEPLOYMENT CHECKLIST:"
echo "=================================="
echo "1. ✅ Delete corrupted open-webui service"
echo "2. ✅ Create new OpenWebUI service from template"
echo "3. ✅ Set custom domain: tilores-x-ui.up.railway.app"
echo "4. ✅ Add all environment variables above"
echo "5. ✅ Delete duplicate open-webui/open-webui:main service"
echo "6. ✅ Test OpenWebUI interface loads properly"
echo "7. ✅ Configure models via API"
echo ""
echo "⚠️  PREVENTION MEASURES:"
echo "========================"
echo "- ALWAYS verify Railway service before deployment"
echo "- NEVER use 'railway up' without confirming target service"
echo "- ALWAYS test deployment target with 'railway status' first"
echo "- Use GitHub deployments for TLRS, Docker templates for OpenWebUI"
echo ""
