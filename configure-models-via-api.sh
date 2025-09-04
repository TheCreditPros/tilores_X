#!/bin/bash

# Configure Tilores Models in Open WebUI via API (Alternative to File Upload)
# This bypasses WebSocket upload issues

echo "🚀 Configuring Tilores Models via API"
echo "====================================="

OPENWEBUI_URL="https://tilores-x-ui.up.railway.app"
TILORES_API_URL="https://tilores-x.up.railway.app"

echo "📋 Open WebUI URL: $OPENWEBUI_URL"
echo "🔗 Tilores API URL: $TILORES_API_URL"
echo ""

echo "🔧 Alternative Configuration Methods:"
echo ""

echo "Method 1: Direct API Configuration"
echo "=================================="
echo "1. Go to: $OPENWEBUI_URL/admin/settings"
echo "2. Navigate to 'Connections' tab"
echo "3. Add OpenAI Connection:"
echo "   • Name: Tilores API"
echo "   • Base URL: $TILORES_API_URL"
echo "   • API Key: dummy"
echo "   • Click 'Test Connection'"
echo "   • Should auto-discover 9 models"
echo ""

echo "Method 2: Environment Variable Configuration"
echo "==========================================="
echo "Models are pre-configured via environment variables:"
echo "• OPENAI_API_BASE_URL=$TILORES_API_URL"
echo "• OPENAI_API_KEY=dummy"
echo ""

echo "Method 3: Manual Model Addition"
echo "==============================="
echo "If auto-discovery fails, manually add each model:"
echo ""

# Generate curl commands for each model
models=(
    "gpt-4o:GPT-4o"
    "gpt-4o-mini:GPT-4o Mini"
    "gpt-3.5-turbo:GPT-3.5 Turbo"
    "gemini-1.5-flash:Gemini 1.5 Flash"
    "gemini-1.5-pro:Gemini 1.5 Pro"
    "gemini-2.0-flash-exp:Gemini 2.0 Flash (Experimental)"
    "gemini-2.5-flash:Gemini 2.5 Flash"
    "llama-3.3-70b-versatile:Llama 3.3 70B Versatile"
    "deepseek-r1-distill-llama-70b:DeepSeek R1 Distill Llama 70B"
)

echo "Available Models to Add Manually:"
for model in "${models[@]}"; do
    IFS=':' read -r id name <<< "$model"
    echo "• Model ID: $id"
    echo "  Name: $name"
    echo "  Provider: OpenAI Compatible"
    echo "  Base URL: $TILORES_API_URL"
    echo ""
done

echo "🎯 Troubleshooting WebSocket Issues:"
echo "===================================="
echo "If you continue to see WebSocket errors:"
echo "1. Try using a different browser"
echo "2. Disable browser extensions"
echo "3. Check if corporate firewall blocks WebSockets"
echo "4. Use the manual configuration methods above"
echo ""

echo "✅ All methods will result in the same 9 models being available!"
echo "🎉 Your team can start using the models immediately after configuration."
