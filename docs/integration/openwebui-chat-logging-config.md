# Open WebUI Chat Logging Configuration Guide

## 🎯 Objective

Configure Open WebUI to send full chat conversations to the enhanced logging endpoints for complete message tracking.

## 🔧 Method 1: Environment Variables (Recommended)

### **Configure via Railway Dashboard:**

1. **Go to Railway Dashboard** → Open WebUI Service
2. **Navigate to Variables** tab
3. **Add these environment variables:**

```bash
# Enhanced Chat Logging Configuration
ENABLE_CHAT_LOGGING=true
CHAT_LOGGING_WEBHOOK_URL=https://tilores-x.up.railway.app/webhooks/chat/completion
CHAT_LOGGING_CONVERSATION_URL=https://tilores-x.up.railway.app/webhooks/chat/conversation
CHAT_LOGGING_ENABLED=true

# Webhook Configuration for Full Conversations
WEBHOOK_CHAT_COMPLETION=https://tilores-x.up.railway.app/webhooks/chat/completion
WEBHOOK_FULL_CONVERSATION=https://tilores-x.up.railway.app/webhooks/chat/conversation

# Additional Logging Settings
LOG_CHAT_MESSAGES=true
LOG_USER_INTERACTIONS=true
SEND_CHAT_WEBHOOKS=true
```

### **Or via Railway CLI:**

```bash
# Set chat logging environment variables
railway variables --set "ENABLE_CHAT_LOGGING=true"
railway variables --set "CHAT_LOGGING_WEBHOOK_URL=https://tilores-x.up.railway.app/webhooks/chat/completion"
railway variables --set "WEBHOOK_CHAT_COMPLETION=https://tilores-x.up.railway.app/webhooks/chat/completion"
railway variables --set "LOG_CHAT_MESSAGES=true"
```

---

## 🔧 Method 2: Open WebUI Admin Configuration

### **Via Open WebUI Admin Panel:**

1. **Access Open WebUI**: `https://tilores-x-ui.up.railway.app`
2. **Login as Admin**
3. **Go to Settings** → **Admin Settings**
4. **Navigate to Webhooks/Integrations**
5. **Configure Chat Logging:**

```json
{
  "chat_completion_webhook": "https://tilores-x.up.railway.app/webhooks/chat/completion",
  "conversation_webhook": "https://tilores-x.up.railway.app/webhooks/chat/conversation",
  "enable_message_logging": true,
  "log_user_messages": true,
  "log_assistant_responses": true
}
```

---

## 🔧 Method 3: Custom Webhook Integration

### **Create Custom Integration Script:**

```javascript
// Custom Open WebUI Chat Logger
// Add this to Open WebUI's custom scripts

const CHAT_WEBHOOK_URL =
  "https://tilores-x.up.railway.app/webhooks/chat/completion";

// Hook into chat completion events
window.addEventListener("chatCompletion", function (event) {
  const chatData = {
    chat_id: event.detail.chatId,
    message_id: event.detail.messageId,
    user_id: event.detail.userId,
    model: event.detail.model,
    user_message: event.detail.userMessage,
    assistant_response: event.detail.assistantResponse,
    timestamp: new Date().toISOString(),
    response_time: event.detail.responseTime,
    tokens_used: event.detail.tokensUsed,
  };

  // Send to webhook
  fetch(CHAT_WEBHOOK_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(chatData),
  }).catch(console.error);
});
```

---

## 🔧 Method 4: Proxy Configuration

### **Configure API Proxy to Log Requests:**

Add to Open WebUI configuration:

```yaml
# Open WebUI Proxy Configuration
proxy:
  chat_completions:
    url: "https://tilores-x.up.railway.app/v1/chat/completions"
    webhook_url: "https://tilores-x.up.railway.app/webhooks/chat/completion"
    log_requests: true
    log_responses: true
```

---

## 🚀 Implementation Steps

### **Step 1: Configure Environment Variables**

```bash
# Run this to configure Open WebUI for chat logging
railway link --project 23cccd8d-f377-4552-a109-ab16ccfccf7a --service 104fad39-5d09-4389-92b6-95d8818456fd

# Set the logging configuration
railway variables --set "ENABLE_CHAT_LOGGING=true"
railway variables --set "CHAT_LOGGING_WEBHOOK_URL=https://tilores-x.up.railway.app/webhooks/chat/completion"
railway variables --set "WEBHOOK_CHAT_COMPLETION=https://tilores-x.up.railway.app/webhooks/chat/completion"
railway variables --set "LOG_CHAT_MESSAGES=true"
railway variables --set "SEND_CHAT_WEBHOOKS=true"
```

### **Step 2: Restart Open WebUI Service**

```bash
# Restart to apply new configuration
railway service restart
```

### **Step 3: Verify Configuration**

1. **Test Chat**: Send a message in Open WebUI
2. **Check Logs**: `curl https://tilores-x.up.railway.app/webhooks/chat/recent`
3. **Verify Data**: Should see full message content

---

## 📊 Expected Webhook Payload

### **What Open WebUI Should Send:**

```json
{
  "chat_id": "chat_abc123",
  "message_id": "msg_def456",
  "user_id": "user_789",
  "model": "gpt-4o-mini",
  "user_message": "What is credit analysis?",
  "assistant_response": "Credit analysis is the process...",
  "timestamp": "2025-09-04T12:00:00Z",
  "response_time": 1.2,
  "tokens_used": 156
}
```

### **What You'll Get Back:**

```json
{
  "status": "logged",
  "chat_id": "chat_abc123",
  "message_id": "msg_def456"
}
```

---

## 🔍 Troubleshooting

### **If Chat Logging Doesn't Work:**

1. **Check Environment Variables**: Ensure all webhook URLs are set
2. **Verify Network Access**: Test webhook endpoints manually
3. **Check Open WebUI Logs**: Look for webhook errors
4. **Test Webhook Manually**: Send test data to endpoints

### **Debug Commands:**

```bash
# Test webhook endpoint
curl -X POST https://tilores-x.up.railway.app/webhooks/chat/completion \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"test","message_id":"test","model":"gpt-4o-mini","user_message":"test","assistant_response":"test","timestamp":"2025-09-04T12:00:00Z"}'

# Check recent chats
curl https://tilores-x.up.railway.app/webhooks/chat/recent

# Check Open WebUI variables
railway variables
```

---

## 🎯 Result

After configuration, every chat in Open WebUI will automatically:

- ✅ Log full message content (user + assistant)
- ✅ Track conversation metadata
- ✅ Store performance metrics
- ✅ Enable conversation retrieval by chat ID
- ✅ Provide real-time chat monitoring

**Your team will have complete visibility into all Open WebUI conversations!**
