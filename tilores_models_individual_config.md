# TILORES OPENWEBUI MODELS - INDIVIDUAL CONFIGURATIONS

## 🎯 MODEL CONFIGURATION OVERVIEW

**Base URL:** `https://tilores-x.up.railway.app/v1`
**API Key:** Use your Tilores API key or leave as `{{TILORES_API_KEY}}` for template

---

## 📋 OPENAI MODELS

### 1. GPT-4o

- **Model ID:** `gpt-4o`
- **Name:** GPT-4o
- **Provider:** OpenAI
- **Context Length:** 128,000 tokens
- **Max Tokens:** 4,096
- **Description:** OpenAI's most advanced model with superior reasoning capabilities
- **Base URL:** `https://tilores-x.up.railway.app/v1`

### 2. GPT-4o Mini

- **Model ID:** `gpt-4o-mini`
- **Name:** GPT-4o Mini
- **Provider:** OpenAI
- **Context Length:** 128,000 tokens
- **Max Tokens:** 4,096
- **Description:** Faster, cost-effective version of GPT-4o with excellent performance
- **Base URL:** `https://tilores-x.up.railway.app/v1`

### 3. GPT-3.5 Turbo

- **Model ID:** `gpt-3.5-turbo`
- **Name:** GPT-3.5 Turbo
- **Provider:** OpenAI
- **Context Length:** 16,385 tokens
- **Max Tokens:** 4,096
- **Description:** Fast and efficient model for general conversations
- **Base URL:** `https://tilores-x.up.railway.app/v1`

---

## 📋 GOOGLE GEMINI MODELS

### 4. Gemini 1.5 Flash

- **Model ID:** `gemini-1.5-flash-002`
- **Name:** Gemini 1.5 Flash
- **Provider:** Google
- **Context Length:** 1,000,000 tokens
- **Max Tokens:** 8,192
- **Description:** Google's fast and efficient multimodal model
- **Base URL:** `https://tilores-x.up.railway.app/v1`

### 5. Gemini 2.5 Flash

- **Model ID:** `gemini-2.5-flash`
- **Name:** Gemini 2.5 Flash
- **Provider:** Google
- **Context Length:** 1,000,000 tokens
- **Max Tokens:** 8,192
- **Description:** Google's latest enhanced reasoning model with improved capabilities
- **Base URL:** `https://tilores-x.up.railway.app/v1`

### 6. Gemini 2.5 Flash Lite

- **Model ID:** `gemini-2.5-flash-lite`
- **Name:** Gemini 2.5 Flash Lite
- **Provider:** Google
- **Context Length:** 1,000,000 tokens
- **Max Tokens:** 8,192
- **Description:** Lightweight version of Gemini 2.5 Flash optimized for speed
- **Base URL:** `https://tilores-x.up.railway.app/v1`

### 7. Gemini 1.5 Pro

- **Model ID:** `gemini-1.5-pro`
- **Name:** Gemini 1.5 Pro
- **Provider:** Google
- **Context Length:** 2,000,000 tokens
- **Max Tokens:** 8,192
- **Description:** Google's most capable model for complex reasoning tasks
- **Base URL:** `https://tilores-x.up.railway.app/v1`

---

## 📋 GROQ MODELS

### 8. Llama 3.3 70B Versatile

- **Model ID:** `llama-3.3-70b-versatile`
- **Name:** Llama 3.3 70B Versatile
- **Provider:** Groq
- **Context Length:** 131,072 tokens
- **Max Tokens:** 32,768
- **Description:** Meta's powerful open-source model via Groq for fast inference
- **Base URL:** `https://tilores-x.up.railway.app/v1`

### 9. DeepSeek R1 Distill Llama 70B

- **Model ID:** `deepseek-r1-distill-llama-70b`
- **Name:** DeepSeek R1 Distill Llama 70B
- **Provider:** Groq
- **Context Length:** 131,072 tokens
- **Max Tokens:** 32,768
- **Description:** Advanced reasoning model optimized for complex problem solving
- **Base URL:** `https://tilores-x.up.railway.app/v1`

---

## 🚀 IMPORT INSTRUCTIONS

### Method 1: Import JSON File

1. Click "Import Models" button in OpenWebUI
2. Upload `tilores_openwebui_models.json`
3. All 9 models will be imported at once
4. Replace `{{TILORES_API_KEY}}` with your actual API key if needed

### Method 2: Manual Model Addition

1. Click the "+" button to add new model
2. Fill in the details from the configurations above
3. Use the exact Model ID and Base URL as specified
4. Set the API key appropriately

### Method 3: Individual Configuration

For each model, use these settings:

**Common Settings:**

- **Base URL:** `https://tilores-x.up.railway.app/v1`
- **API Key:** Your Tilores API key
- **Temperature:** 0.7
- **Top P:** 1.0 (OpenAI/Groq) or 0.95 (Google)

---

## ✅ TESTING MODELS

After importing, test each model:

1. **Quick Test:** Use any model with "Hello, test message"
2. **Credit Test:** Use with Tilores prompts: "analyze credit for e.j.price1986@gmail.com"
3. **Performance Test:** Compare response times across providers:
   - **Fastest:** Gemini models (2-4 seconds)
   - **Balanced:** GPT-4o Mini (5-7 seconds)
   - **Powerful:** GPT-4o, Llama 3.3 (8-12 seconds)

## 🎯 RECOMMENDED USAGE

- **General Chat:** GPT-4o Mini, Gemini 2.5 Flash Lite
- **Credit Analysis:** GPT-4o, Gemini 1.5 Pro
- **Customer Service:** Gemini 1.5 Flash, GPT-4o Mini
- **Complex Reasoning:** DeepSeek R1, GPT-4o
- **Speed Priority:** Gemini 2.5 Flash Lite, Llama 3.3 70B

## 🔗 BACKEND INTEGRATION

All models route through our Tilores backend at `https://tilores-x.up.railway.app/v1`, which provides:

- ✅ Agent system integration
- ✅ Real customer data access
- ✅ Conversational context
- ✅ Caching and optimization
- ✅ Error handling and fallbacks
