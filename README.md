# Tilores Simplified API for AnythingLLM Integration

🚀 **Production-Ready Simplified Tilores API with AnythingLLM Compatibility**

## 🌐 Production Access

**🔗 Production API**: https://tilores-unified-api-production.up.railway.app
**💬 UI Interface**: AnythingLLM (anythingllm.thecreditpros.com)

**📊 Key Endpoints**:
- **Health Check**: `/health`
- **LangServe API**: `/chat/invoke` (AnythingLLM compatible)
- **Service Info**: `/`

---

## 🎯 Simplified Architecture

This API has been streamlined for optimal performance with AnythingLLM:

### **Core Features:**
- ✅ **LangServe Integration**: Direct `/chat/invoke` endpoint for AnythingLLM
- ✅ **Tilores Customer Data**: Complete access to 310+ customer fields
- ✅ **Multi-Provider Models**: OpenAI, Groq, Anthropic, Google AI support
- ✅ **LangSmith Tracing**: Complete conversation monitoring
- ✅ **Credit Reports**: Comprehensive credit data integration
- ✅ **Clean Architecture**: Minimal, focused codebase

### **Removed Complexity:**
- ❌ Multiple playground interfaces (use AnythingLLM instead)
- ❌ Complex agent implementations
- ❌ Redundant test infrastructure
- ❌ Excessive deployment machinery

---

## 🚀 Quick Start

### Local Development
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment (copy from .env.example)
cp .env .env.local
# Edit .env.local with your API keys

# 3. Start server
python main_enhanced.py
# Server runs on http://localhost:8000
```

### AnythingLLM Integration
```bash
# Configure AnythingLLM to use:
# API Base: http://localhost:8000 (local) or production URL
# Endpoint: /chat/invoke
# Model: gpt-4o-mini, llama-3.3-70b-versatile, etc.
```

---

## 📋 API Usage

### Health Check
```bash
curl https://tilores-unified-api-production.up.railway.app/health
```

### Customer Search via AnythingLLM
Simply ask in AnythingLLM:
- "Find customer with client ID 1648647"
- "Get credit report for Dawn Bruton" 
- "What is customer 1881899's email address?"

### Direct API Call
```bash
curl -X POST https://tilores-unified-api-production.up.railway.app/chat/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "input": "Find customer with client ID 1648647",
      "model": "gpt-4o-mini"
    }
  }'
```

---

## 🔧 Development & Testing

### Run Tests
```bash
# Simple test suite
python test_simplified_runner.py

# Pre-commit validation
./scripts/test/pre_commit_validation.sh
```

### Deployment
```bash
# Validate and deploy
./deploy-simple.sh
```

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AnythingLLM   │───▶│  Simplified API  │───▶│  Tilores Data   │
│      (UI)       │    │   (/chat/invoke) │    │  (310+ fields)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   LangSmith     │
                       │   (Tracing)     │
                       └─────────────────┘
```

## 📊 Supported Models

| Provider | Models | Status |
|----------|--------|--------|
| OpenAI | gpt-4o-mini, gpt-3.5-turbo | ✅ Working |
| Groq | llama-3.3-70b-versatile, deepseek-r1-distill-llama-70b | ✅ Working |
| Anthropic | claude-3-haiku, claude-3-sonnet | ✅ Working |
| Google | gemini-pro, gemini-flash | ✅ Working |

---

## 🚀 Production Status

✅ **Ready for Production**: Simplified, tested, and optimized for AnythingLLM
✅ **Clean Codebase**: Removed obsolete components and complexity  
✅ **Performance Optimized**: Focus on core functionality
✅ **AnythingLLM Compatible**: Direct integration via `/chat/invoke`
✅ **Monitoring Ready**: LangSmith tracing active

---

**Ready for immediate deployment and AnythingLLM integration!**