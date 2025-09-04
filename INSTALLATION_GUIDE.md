# TLRS System Installation Guide

## Complete Setup Instructions for Target Repository

---

## 🎯 **Overview**

This guide will help you install the complete TLRS (Tilores Credit Analysis) system on a target repository, including:

- Multi-Provider Credit Analysis API
- Open WebUI Integration
- Webhook Logging System
- Comprehensive QA Testing Framework

---

## 📋 **Prerequisites**

### **System Requirements**

- **Python 3.8+** (recommended: Python 3.11+)
- **Node.js 18+** (for Open WebUI)
- **Git** for version control
- **Docker** (optional, for containerized deployment)

### **Required API Keys**

- **OpenAI API Key** (for GPT models)
- **Google AI API Key** (for Gemini models)
- **Groq API Key** (for Llama/DeepSeek models)
- **Tilores API Credentials** (Client ID, Secret, Token URL)

---

## 🚀 **Installation Steps**

### **Step 1: Clone or Copy Core Files**

```bash
# Option A: Clone this repository
git clone <your-tilores-repo-url>
cd tilores_X

# Option B: Copy essential files to your target repository
# Copy these core files:
# - direct_credit_api_fixed.py
# - enhanced_chat_webhook.py
# - requirements.txt (create from dependencies below)
# - .env.example (create from environment variables below)
```

### **Step 2: Create Python Environment**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### **Step 3: Install Python Dependencies**

Create `requirements.txt`:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
requests==2.31.0
redis==5.0.1
python-multipart==0.0.6
pydantic==2.5.0
python-dotenv==1.0.0
openai==1.3.0
google-generativeai==0.3.0
groq==0.4.0
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### **Step 4: Environment Configuration**

Create `.env` file:

```env
# Tilores API Configuration
TILORES_API_URL=https://your-tilores-api-url.com
TILORES_CLIENT_ID=your_client_id
TILORES_CLIENT_SECRET=your_client_secret
TILORES_TOKEN_URL=https://your-tilores-token-url.com/oauth/token

# LLM Provider API Keys
OPENAI_API_KEY=sk-your-openai-api-key
GOOGLE_API_KEY=your-google-ai-api-key
GROQ_API_KEY=gsk_your-groq-api-key

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# Enhanced Chat Logging
ENHANCED_CHAT_LOGGING=true

# Server Configuration
HOST=0.0.0.0
PORT=8080
```

### **Step 5: Redis Setup (Optional but Recommended)**

```bash
# Install Redis (macOS with Homebrew)
brew install redis
brew services start redis

# Install Redis (Ubuntu/Debian)
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server

# Install Redis (Docker)
docker run -d --name redis -p 6379:6379 redis:alpine
```

---

## 🔧 **Core System Setup**

### **Main API Server**

The core file `direct_credit_api_fixed.py` includes:

- ✅ Multi-provider LLM support (OpenAI, Gemini, Groq)
- ✅ Comprehensive credit analysis
- ✅ Customer data retrieval
- ✅ Redis caching
- ✅ Error handling and validation
- ✅ OpenAI-compatible API endpoints

### **Webhook Integration**

The `enhanced_chat_webhook.py` provides:

- ✅ Chat completion logging
- ✅ Full conversation tracking
- ✅ JSONL file storage
- ✅ REST API for data retrieval

### **Start the System**

```bash
# Start the API server
python3 direct_credit_api_fixed.py

# Server will start on http://localhost:8080
# Health check: http://localhost:8080/health
# API docs: http://localhost:8080/docs
```

---

## 🌐 **Open WebUI Integration**

### **Option 1: Docker Deployment (Recommended)**

```bash
# Pull and run Open WebUI
docker run -d \
  --name open-webui \
  -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8080/v1 \
  -e OPENAI_API_KEY=dummy-key \
  -e WEBUI_AUTH=false \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main

# Access at: http://localhost:3000
```

### **Option 2: Manual Installation**

```bash
# Install Node.js dependencies
npm install -g open-webui

# Configure environment
export OPENAI_API_BASE_URL=http://localhost:8080/v1
export OPENAI_API_KEY=dummy-key

# Start Open WebUI
open-webui serve --port 3000
```

---

## 🧪 **Testing Framework Setup**

### **Install Testing Dependencies**

```bash
# Additional testing dependencies
pip install pytest pytest-asyncio httpx
```

### **Run Comprehensive Tests**

```bash
# Run the comprehensive QA test suite
python3 comprehensive_qa_stress_test.py

# Run production endpoint tests
python3 production_endpoint_test.py

# Run focused diagnostic tests
python3 focused_issue_diagnostic.py
```

---

## 🚀 **Production Deployment**

### **Railway Deployment**

1. **Install Railway CLI**:

```bash
npm install -g @railway/cli
railway login
```

2. **Deploy API Service**:

```bash
railway init
railway add
# Set environment variables in Railway dashboard
railway deploy
```

3. **Deploy Open WebUI**:

```bash
# Use provided Dockerfile.openwebui
railway deploy --dockerfile Dockerfile.openwebui
```

### **Docker Deployment**

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "direct_credit_api_fixed.py"]
```

Build and run:

```bash
docker build -t tlrs-api .
docker run -p 8080:8080 --env-file .env tlrs-api
```

---

## 📊 **Verification & Testing**

### **Health Checks**

```bash
# Test API health
curl http://localhost:8080/health

# Test models endpoint
curl http://localhost:8080/v1/models

# Test chat completion
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "who is e.j.price1986@gmail.com"}],
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

### **Webhook Testing**

```bash
# Test webhook health
curl http://localhost:8080/webhooks/chat/health

# Test webhook logging
curl -X POST http://localhost:8080/webhooks/chat/completion \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "test-123",
    "message_id": "msg-456",
    "user_message": "test query",
    "assistant_response": "test response",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'"
  }'
```

---

## 🔧 **Configuration Options**

### **Model Configuration**

The system supports multiple LLM providers:

```python
# Available models:
OPENAI_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
GEMINI_MODELS = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
GROQ_MODELS = ["llama-3.3-70b-versatile", "deepseek-r1-distill-llama-70b"]
```

### **Performance Tuning**

```env
# Cache settings
CACHE_TTL=3600
REDIS_MAX_CONNECTIONS=10

# Request timeouts
REQUEST_TIMEOUT=30
GRAPHQL_TIMEOUT=45

# Rate limiting
MAX_REQUESTS_PER_MINUTE=60
```

---

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Missing Dependencies**:

```bash
# Install missing packages
pip install --upgrade -r requirements.txt
```

2. **Redis Connection Issues**:

```bash
# Check Redis status
redis-cli ping
# Should return: PONG
```

3. **API Key Issues**:

```bash
# Verify environment variables
python3 -c "import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY')))"
```

4. **Port Conflicts**:

```bash
# Check what's using port 8080
lsof -i :8080
# Kill process if needed
kill -9 <PID>
```

### **Vitest Coverage Issue (from your screenshot)**

For the specific issue in your screenshot:

```bash
# Install the missing dependency
npm install --save-dev @vitest/coverage-v8

# Or if using yarn
yarn add -D @vitest/coverage-v8

# Then run tests
npm run test:ci
```

---

## 📚 **Additional Resources**

### **Documentation Files**

- `COMPREHENSIVE_QA_ANALYSIS_REPORT.md` - Testing results
- `PRODUCTION_TESTING_SUMMARY.md` - Production validation
- `AGENTA_DEPRECATION_PLAN.md` - Architecture decisions

### **Testing Scripts**

- `comprehensive_qa_stress_test.py` - Multi-threaded testing
- `production_endpoint_test.py` - Production validation
- `focused_issue_diagnostic.py` - Issue analysis

### **Configuration Files**

- `prompt_store.json` - Prompt configurations
- `railway.json` - Railway deployment config
- `Dockerfile.openwebui` - Open WebUI container

---

## ✅ **Installation Verification**

After installation, verify everything is working:

1. **API Server**: ✅ http://localhost:8080/health returns `{"status": "healthy"}`
2. **Models**: ✅ http://localhost:8080/v1/models returns model list
3. **Chat**: ✅ Chat completions return proper responses
4. **Webhooks**: ✅ Webhook endpoints log data correctly
5. **Open WebUI**: ✅ UI accessible and can connect to API

---

## 🎯 **Next Steps**

1. **Configure your specific Tilores API credentials**
2. **Test with your customer data**
3. **Deploy to your preferred hosting platform**
4. **Set up monitoring and alerts**
5. **Train your team on the system**

---

**Installation Support**: If you encounter issues, check the troubleshooting section or review the comprehensive testing results in the provided documentation files.

**Status**: ✅ **READY FOR PRODUCTION DEPLOYMENT**


