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
| Groq | llama-3.3-70b-versatile, llama-3.3-70b-specdec (1,665 tok/s), deepseek-r1-distill-llama-70b, mixtral-8x7b-32768, llama-3.2-90b-text-preview | ✅ Working |
| Anthropic | claude-3-haiku, claude-3-sonnet | ✅ Working |
| Google | gemini-pro, gemini-flash | ✅ Working |

*For detailed model specifications and use cases, see [Architecture Documentation](memory-bank/tilores_X_memory_bank_architecture_README.md#supported-models--providers)*

---

## 📚 Related Documentation

### Project Context & Background
- **[Project Overview](memory-bank/tilores_X_memory_bank_project-overview.md)** - What Tilores_X is and its relationship to legacy systems
- **[Project Status](memory-bank/tilores_X_memory_bank_project-status.md)** - Current development status and achievements
- **[Architecture Documentation](memory-bank/tilores_X_memory_bank_architecture_README.md)** - Detailed technical architecture and components

### Development & Operations
- **[Setup Guide](memory-bank/tilores_X_memory_bank_SETUP_GUIDE.md)** - Complete environment setup and configuration
- **[Migration Guide](memory-bank/tilores_X_memory_bank_migration-from-legacy.md)** - Transitioning from legacy Tilores-Jul10
- **[Decision Records](memory-bank/tilores_X_memory_bank_decisions_README.md)** - Architectural decisions and rationale

### Development Tracking
- **[Development Log](memory-bank/tilores_X_memory_bank_updates_development-log.md)** - Ongoing development progress
- **[Status Reports](memory-bank/tilores_X_memory_bank_status-reports_README.md)** - Regular project status updates

---

## 🚀 Production Status

✅ **Ready for Production**: Simplified, tested, and optimized for AnythingLLM
✅ **Clean Codebase**: Removed obsolete components and complexity
✅ **Performance Optimized**: Focus on core functionality
✅ **AnythingLLM Compatible**: Direct integration via `/chat/invoke`
✅ **Monitoring Ready**: LangSmith tracing active

*For detailed component information and system design, see [Architecture Documentation](memory-bank/tilores_X_memory_bank_architecture_README.md)*

---

**Ready for immediate deployment and AnythingLLM integration!**
