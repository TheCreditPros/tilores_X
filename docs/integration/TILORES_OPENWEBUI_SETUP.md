# Tilores Open WebUI Setup Guide

## 🚀 Quick Start - Pre-Configured Models

**Both services are running and ready:**

- **Tilores API**: http://localhost:8080 ✅
- **Open WebUI**: http://localhost:3000 ✅

## 📋 Step-by-Step Setup

### 1. Access Open WebUI

Open your browser: **http://localhost:3000**

### 2. Create Admin Account

- **Name**: Tilores Admin
- **Email**: admin@tilores.com
- **Password**: TiloresAdmin123!

### 3. Configure Tilores Models

Navigate to **Settings → Models** and add these **exact** models:

#### Model 1: Tilores GPT-4o Mini (Default)

```
Name: gpt-4o-mini
Display Name: Tilores GPT-4o Mini
Base URL: http://host.docker.internal:8080
API Key: dummy
```

#### Model 2: Tilores GPT-4o

```
Name: gpt-4o
Display Name: Tilores GPT-4o
Base URL: http://host.docker.internal:8080
API Key: dummy
```

#### Model 3: Tilores GPT-3.5 Turbo

```
Name: gpt-3.5-turbo
Display Name: Tilores GPT-3.5 Turbo
Base URL: http://host.docker.internal:8080
API Key: dummy
```

### 4. Set Default Model

In **Settings → General**:

- Set **Default Model**: `gpt-4o-mini`

### 5. Configure Rating Webhook (Optional)

If webhook settings are available:

- **URL**: `http://host.docker.internal:8080/webhooks/openwebui-rating`
- **Events**: `rating.created`

## 🧪 Test Queries

Use these **exact** test queries to validate your Tilores integration:

### Account Status Query

```
What is the account status for e.j.price1986@gmail.com?
```

**Expected**: Returns "Active" status with customer name "Esteban Price"

### Credit Analysis Query

```
What is the credit analysis for e.j.price1986@gmail.com?
```

**Expected**: Comprehensive credit report with scores, utilization, recommendations

### Transaction Analysis Query

```
Show me transaction analysis for e.j.price1986@gmail.com
```

**Expected**: Payment patterns, amounts, billing data

### Multi-Data Analysis Query

```
Give me a comprehensive analysis for e.j.price1986@gmail.com including credit and transactions
```

**Expected**: Combined analysis from multiple data sources

## ✅ Validation Checklist

- [ ] Open WebUI accessible at http://localhost:3000
- [ ] Admin account created with Tilores credentials
- [ ] All 3 Tilores models configured (gpt-4o-mini, gpt-4o, gpt-3.5-turbo)
- [ ] Default model set to gpt-4o-mini
- [ ] Account status query returns "Active" and "Esteban Price"
- [ ] Credit analysis query returns detailed credit report
- [ ] Transaction analysis query returns payment data
- [ ] Rating buttons work (thumbs up/down)
- [ ] Ratings logged to webhook (check `openwebui_ratings.jsonl`)

## 🔧 Troubleshooting

### Models Not Working

1. Verify Tilores API is running: `curl http://localhost:8080/health`
2. Check model names match exactly: `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`
3. Ensure Base URL is: `http://host.docker.internal:8080`
4. API Key must be: `dummy`

### No Response from Models

1. Check Docker network connectivity
2. Verify container can reach host: `docker exec openwebui ping host.docker.internal`
3. Check Tilores API logs for errors

### Rating Webhook Not Working

1. Test webhook directly:
   ```bash
   curl -X POST http://localhost:8080/webhooks/openwebui-rating \
     -H 'Content-Type: application/json' \
     -d '{"model":"gpt-4o-mini","rating":"up"}'
   ```
2. Check webhook logs: `tail -f openwebui_ratings.jsonl`

## 🎯 Success Criteria

When setup is complete, you should be able to:

1. **Chat with Tilores Models**: Select any of the 3 configured models
2. **Get Real Credit Data**: Queries return actual Tilores customer data
3. **Rate Responses**: Thumbs up/down buttons capture feedback
4. **Team Evaluation**: Non-technical team members can easily test the system

## 📊 Model Performance

| Model         | Speed  | Quality   | Use Case                           |
| ------------- | ------ | --------- | ---------------------------------- |
| gpt-4o-mini   | Fast   | Good      | Quick queries, status checks       |
| gpt-4o        | Medium | Excellent | Complex analysis, detailed reports |
| gpt-3.5-turbo | Fast   | Good      | General queries, conversations     |

## 🚀 Ready for Team Use

Once configured, your team can:

- Test different query types with real customer data
- Compare model responses and quality
- Provide feedback via rating system
- Evaluate system performance for different use cases

**The system is now ready for comprehensive team evaluation! 🎉**
