# Tilores Simplified API for AnythingLLM Integration

🚀 **Production-Ready Simplified Tilores API with AnythingLLM Compatibility**

## 🌐 Production Access

**🔗 Production API**: https://tiloresx-production.up.railway.app
**💬 UI Interface**: AnythingLLM (anythingllm.thecreditpros.com)

**📊 Key Endpoints**:
- **Health Check**: `/health`
- **OpenAI API**: `/v1/chat/completions` (OpenAI compatible)
- **Models List**: `/v1/models`
- **Metrics**: `/metrics`
- **Detailed Health**: `/health/detailed`

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
curl https://tiloresx-production.up.railway.app/health
```

### Customer Search via AnythingLLM
Simply ask in AnythingLLM:
- "Find customer with client ID 1648647"
- "Get credit report for Dawn Bruton"
- "What is customer 1881899's email address?"

### Direct API Call
```bash
curl -X POST https://tiloresx-production.up.railway.app/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Find customer with client ID 1648647"}],
    "max_tokens": 500
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

## 📊 Supported Models & Performance

### 🏎️ **Ultra-Fast Models (Recommended for Production)**

| Model ID (OpenAI Endpoint) | Provider | Speed | Use Case | Status |
|----------------------------|----------|-------|----------|--------|
| `llama-3.3-70b-versatile` | Groq | **~600ms avg** | General purpose, fast responses | ✅ Working |
| `deepseek-r1-distill-llama-70b` | Groq | **~3.5s avg** | Cost-effective reasoning | ✅ Working |

### ⚠️ **Recently Deprecated Models**

| Model ID (OpenAI Endpoint) | Provider | Previous Speed | Status | Replacement |
|----------------------------|----------|----------------|--------|-------------|
| `llama-3.3-70b-specdec` | Groq | 1,665 tok/s | ❌ **DEPRECATED** | Use `llama-3.3-70b-versatile` |
| `mixtral-8x7b-32768` | Groq | 500+ tok/s | ❌ **DEPRECATED** | Use `llama-3.3-70b-versatile` |
| `llama-3.2-90b-text-preview` | Groq | 330 tok/s | ❌ **DEPRECATED** | Use `deepseek-r1-distill-llama-70b` |

### 🧠 **High-Quality Models**

| Model ID (OpenAI Endpoint) | Provider | Speed | Use Case | Status |
|----------------------------|----------|-------|----------|--------|
| `gpt-5-mini` | OpenAI | **Latest** | Advanced reasoning, latest features | ✅ Working |
| `gpt-4o` | OpenAI | **2.789s avg** | Complex analysis, high accuracy | ✅ Working |
| `gpt-4o-mini` | OpenAI | **1.915s avg** | Balanced speed/quality | ✅ Working |
| `gpt-4.1-mini` | OpenAI | **Fallback** | Reliable baseline | ✅ Working |
| `gpt-3.5-turbo` | OpenAI | **1.016s avg** | Fast, cost-effective | ✅ Working |

### 🎭 **Specialized Models**

| Model ID (OpenAI Endpoint) | Provider | Speed | Use Case | Status |
|----------------------------|----------|-------|----------|--------|
| `claude-3-sonnet` | Anthropic | **Advanced** | Complex reasoning, analysis | ✅ Working |
| `claude-3-haiku` | Anthropic | **Fast** | Quick responses, simple tasks | ✅ Working |
| `gemini-1.5-flash-002` | Google | **2.2s avg** | Multimodal, fast processing | ✅ Working |

### 🌐 **OpenRouter/Cerebras Models**

| Model ID (OpenAI Endpoint) | Provider | Speed | Use Case | Status |
|----------------------------|----------|-------|----------|--------|
| `llama-3.3-70b-versatile-openrouter` | OpenRouter/Cerebras | **2-4x faster** | Ultra-fast inference | ✅ Working |
| `qwen-3-32b-openrouter` | OpenRouter/Cerebras | **Ultra-fast** | Efficient reasoning | ✅ Working |

### 🎯 **Model Selection Guide**

**For Phone Applications (< 2s response):**
- Primary: `llama-3.3-70b-versatile` (~600ms avg)
- Backup: `gpt-4o-mini` (1.915s avg)

**For General Chat:**
- Primary: `llama-3.3-70b-versatile` (~600ms avg)
- Backup: `gpt-3.5-turbo` (1.016s avg)

**For Complex Analysis:**
- Primary: `claude-3-sonnet` (advanced reasoning)
- Backup: `gpt-4o` (2.789s avg)

**For Cost Optimization:**
- Primary: `deepseek-r1-distill-llama-70b` (~3.5s avg)
- Backup: `gpt-3.5-turbo` (1.016s avg)

### 📡 **OpenAI API Compatibility**

All models are accessible via standard OpenAI API format:

```bash
curl -X POST https://tiloresx-production.up.railway.app/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'
```

**Available Endpoints:**
- `/v1/models` - List all available models
- `/v1/chat/completions` - OpenAI-compatible chat completions
- `/health` - Service health check
- `/metrics` - Performance monitoring

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
