# 🔧 Manual Model Setup Guide - Open WebUI

## ✅ **You're Logged In - Ready to Configure!**

**Credentials Used**: damon@thecreditpros.com / Credit@123

---

## 🚀 **Step-by-Step Model Configuration**

### **Step 1: Navigate to Settings**

1. Look for the **Settings** icon (⚙️ gear icon) in the left sidebar
2. Click on **Settings**
3. Navigate to **Models** or **Connections** section

### **Step 2: Add New Model Connection**

Look for **"Add Model"**, **"New Connection"**, or **"+"** button

### **Step 3: Configure Each Model (Use Same Settings for All)**

**🔑 Universal Settings (for ALL 9 models):**

```
Base URL: http://host.docker.internal:8080
API Key: dummy
Provider: OpenAI Compatible
```

---

## 📋 **All 9 Models to Add**

### **🤖 OpenAI Models (3)**

**Model 1:**

```
Model ID: gpt-4o-mini
Display Name: Tilores GPT-4o Mini
Base URL: http://host.docker.internal:8080
API Key: dummy
```

**Model 2:**

```
Model ID: gpt-4o
Display Name: Tilores GPT-4o
Base URL: http://host.docker.internal:8080
API Key: dummy
```

**Model 3:**

```
Model ID: gpt-3.5-turbo
Display Name: Tilores GPT-3.5 Turbo
Base URL: http://host.docker.internal:8080
API Key: dummy
```

### **🧠 Google Gemini Models (4)**

**Model 4:**

```
Model ID: gemini-1.5-flash
Display Name: Tilores Gemini 1.5 Flash
Base URL: http://host.docker.internal:8080
API Key: dummy
```

**Model 5:**

```
Model ID: gemini-1.5-pro
Display Name: Tilores Gemini 1.5 Pro
Base URL: http://host.docker.internal:8080
API Key: dummy
```

**Model 6:**

```
Model ID: gemini-2.0-flash-exp
Display Name: Tilores Gemini 2.0 Flash Experimental
Base URL: http://host.docker.internal:8080
API Key: dummy
```

**Model 7:**

```
Model ID: gemini-2.5-flash
Display Name: Tilores Gemini 2.5 Flash
Base URL: http://host.docker.internal:8080
API Key: dummy
```

### **⚡ Groq Models (2)**

**Model 8:**

```
Model ID: llama-3.3-70b-versatile
Display Name: Tilores Llama 3.3 70B Versatile
Base URL: http://host.docker.internal:8080
API Key: dummy
```

**Model 9:**

```
Model ID: deepseek-r1-distill-llama-70b
Display Name: Tilores DeepSeek R1 Distill Llama 70B
Base URL: http://host.docker.internal:8080
API Key: dummy
```

---

## 🎯 **After Adding All Models**

### **Set Default Model**

- Go to **Settings > General** or **Preferences**
- Set **Default Model**: `gpt-4o-mini` (recommended)

### **Test Configuration**

Try this query with different models:

```
What is the account status for e.j.price1986@gmail.com?
```

**Expected Response:**

- ✅ "Active" status
- ✅ Customer name "Esteban Price"
- ✅ Product information

---

## 🔍 **Troubleshooting**

### **If Models Don't Appear:**

- Check that Base URL is exactly: `http://host.docker.internal:8080`
- Ensure API Key is: `dummy`
- Verify Tilores API is running: `curl http://localhost:8080/health`

### **If Models Don't Respond:**

- Test Tilores API directly:
  ```bash
  curl -X POST http://localhost:8080/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"test"}]}'
  ```

### **Connection Issues:**

- Restart Open WebUI container: `docker restart openwebui`
- Check Docker network: `docker network ls`

---

## 🎊 **Success Criteria**

When complete, you should have:

- ✅ **9 models** configured and selectable
- ✅ **3 providers** represented (OpenAI, Google, Groq)
- ✅ **Real Tilores data** returned from test queries
- ✅ **Model comparison** capability across providers

**You're now ready for comprehensive team evaluation of all Tilores models! 🚀**
