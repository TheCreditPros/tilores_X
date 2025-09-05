#!/bin/bash

echo "🧪 Testing OpenWebUI Conversation Context Fix"
echo "============================================="
echo ""

# Test the TLRS endpoint directly to confirm it works with conversation history
echo "1. Testing TLRS endpoint directly with conversation history:"
echo "-----------------------------------------------------------"

RESPONSE=$(curl -s -X POST https://tilores-x.up.railway.app/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "who is e.j.price1986@gmail.com"},
      {"role": "assistant", "content": "**Salesforce Account Status:**\n\n• **Status:** Active\n• **Customer:** Esteban Price\n• **Product:** Downsell Credit Repair Monthly $54.75\n• **Enrolled:** 2025-04-10"},
      {"role": "user", "content": "What is their credit score?"}
    ]
  }' | jq -r '.choices[0].message.content')

if [[ $RESPONSE == *"Credit Analysis for Esteban Price"* ]]; then
    echo "✅ TLRS endpoint properly handles conversation history"
    echo "   Response includes: Credit Analysis for Esteban Price"
else
    echo "❌ TLRS endpoint conversation history issue"
    echo "   Response: $RESPONSE"
fi

echo ""
echo "2. Checking recent webhook logs for conversation patterns:"
echo "--------------------------------------------------------"

# Check if recent logs show proper conversation handling
RECENT_LOGS=$(curl -s "https://tilores-x.up.railway.app/v1/monitoring/webhook-logs?limit=3")
SYSTEM_PROMPTS=$(echo "$RECENT_LOGS" | jq -r '.monitoring_logs[] | select(.message_length > 500) | .user_message' | head -1)

if [[ $SYSTEM_PROMPTS == *"### Task:"* ]]; then
    echo "❌ Still receiving OpenWebUI system prompts instead of user queries"
    echo "   This indicates OpenWebUI configuration hasn't taken effect yet"
else
    echo "✅ No system prompt contamination detected"
fi

echo ""
echo "3. Configuration Status:"
echo "------------------------"
echo "Applied fixes based on community research:"
echo "• NUM_CTX=4096 (enable conversation context)"
echo "• ENABLE_WEBSOCKET_SUPPORT=true"
echo "• DISABLE_EMPTY_MESSAGES=true"
echo "• CONVERSATION_MEMORY=true"
echo "• CHAT_TEMPLATE=openai"
echo "• Debug logging enabled"

echo ""
echo "4. Next Steps:"
echo "-------------"
if [[ $SYSTEM_PROMPTS == *"### Task:"* ]]; then
    echo "⏳ Wait 5-10 minutes for OpenWebUI service to fully restart"
    echo "🔄 Try a fresh conversation in OpenWebUI interface"
    echo "📋 Test with: 'who is e.j.price1986@gmail.com' followed by 'what is their credit score?'"
else
    echo "🎉 Configuration appears to be working!"
    echo "📋 Test conversation flow in OpenWebUI interface"
fi

echo ""
echo "🔍 Monitor webhook logs at: https://tilores-x.up.railway.app/v1/monitoring/webhook-logs?limit=5"
