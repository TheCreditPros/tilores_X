# Open WebUI Manual Setup Guide

## Current Status ✅

- **FastAPI Server**: Running on http://localhost:8080
- **Open WebUI**: Running on http://localhost:3000
- **Rating Webhook**: Working at http://localhost:8080/webhooks/openwebui-rating
- **All Tests**: Passing ✅

## Manual Configuration Steps

### 1. Access Open WebUI

Open your browser and go to: **http://localhost:3000**

### 2. Initial Setup

- Create an admin account when prompted
- Complete the initial setup wizard

### 3. Add Models

Navigate to **Settings > Models** and add:

**Model 1: Tilores Local GPT-4o-mini**

- Name: `Tilores/local/gpt-4o-mini`
- Base URL: `http://host.docker.internal:8080`
- API Key: `dummy`

**Model 2: Tilores Local GPT-4o**

- Name: `Tilores/local/gpt-4o`
- Base URL: `http://host.docker.internal:8080`
- API Key: `dummy`

### 4. Configure Rating Webhook (Optional)

If available in Settings > Webhooks:

- Event: `rating.created`
- URL: `http://host.docker.internal:8080/webhooks/openwebui-rating`

### 5. Set Default Model

In Settings > General:

- Set default model to: `Tilores/local/gpt-4o-mini`

## Test Queries

Try these test queries to validate functionality:

1. **Account Status**: "What is the account status for e.j.price1986@gmail.com?"
2. **Credit Analysis**: "What is the credit analysis for e.j.price1986@gmail.com?"
3. **Transaction Analysis**: "Show me transaction analysis for e.j.price1986@gmail.com"

## Expected Results

✅ **Account Status Query**: Should return Salesforce status (Active, customer name, product info)
✅ **Credit Analysis Query**: Should return comprehensive credit report with scores, utilization, recommendations
✅ **Transaction Analysis Query**: Should return payment patterns and billing data

## Rating System Test

After each response:

1. Use the thumbs up/down buttons
2. Check webhook logs: `tail -f openwebui_ratings.jsonl`
3. Verify ratings are being captured with proper metadata

## Validation Checklist

- [ ] Open WebUI accessible at http://localhost:3000
- [ ] Models configured and selectable
- [ ] Test queries return expected results
- [ ] Rating buttons work and log to webhook
- [ ] No errors in browser console or server logs

## Troubleshooting

**If models don't work:**

- Verify FastAPI server is running: `curl http://localhost:8080/health`
- Check Docker network connectivity
- Ensure API key is set to `dummy`

**If ratings don't work:**

- Check webhook endpoint: `curl -X POST http://localhost:8080/webhooks/openwebui-rating -H 'Content-Type: application/json' -d '{"model":"test","rating":"up"}'`
- Verify webhook URL uses `host.docker.internal:8080`

## Next Steps

Once manual setup is complete:

1. Test all functionality end-to-end
2. Document any issues or improvements needed
3. Consider automating the setup process if API endpoints are discovered
