
# 🚀 Agenta.ai UI Configuration Guide

## Step 1: Access Your Agenta.ai Dashboard
1. Go to https://cloud.agenta.ai
2. Log in with your account
3. Navigate to your 'tilores-x' application

## Step 2: Configure Webhooks
In Settings > Webhooks, add these URLs:

```
Evaluation Complete: https://tilores-x.up.railway.app/webhooks/evaluation-complete
Deployment Status: https://tilores-x.up.railway.app/webhooks/deployment-status
Performance Alert: https://tilores-x.up.railway.app/webhooks/performance-alert
```

## Step 3: Create Prompt Variants
Create these 6 variants in the Playground:


### Variant 1: Credit Analysis - Comprehensive
- **Name**: `Credit Analysis - Comprehensive`
- **Description**: Current production prompt for comprehensive credit analysis
- **Model**: gpt-4o-mini
- **Temperature**: 0.5
- **Max Tokens**: 1500
- **System Prompt**: 
```
You are a Credit Pros advisor with access to comprehensive credit data.
Analyze the provided temporal credit data to answer the user's question accurately and professionally.

Available data includes:...
```
- **Use Case**: Comprehensive credit report analysis


### Variant 2: Multi-Data Analysis
- **Name**: `Multi-Data Analysis`
- **Description**: Current production prompt for multi-source data analysis
- **Model**: gpt-4o-mini
- **Temperature**: 0.6
- **Max Tokens**: 2000
- **System Prompt**: 
```
You are a Credit Pros advisor with access to comprehensive customer data across multiple sources.
Analyze the provided data to answer the user's question accurately and professionally.

Available data...
```
- **Use Case**: Multi-source customer intelligence


### Variant 3: Account Status Query
- **Name**: `Account Status Query`
- **Description**: Optimized prompt for Salesforce account status queries
- **Model**: gpt-4o-mini
- **Temperature**: 0.3
- **Max Tokens**: 200
- **System Prompt**: 
```
You are a customer service AI assistant specializing in account status queries.

**PRIMARY FOCUS**: Provide concise, accurate Salesforce account status information.

**RESPONSE FORMAT**:
• **Status**:...
```
- **Use Case**: Quick account status lookups


### Variant 4: Transaction Analysis
- **Name**: `Transaction Analysis`
- **Description**: Current production prompt for transaction analysis
- **Model**: gpt-4o-mini
- **Temperature**: 0.4
- **Max Tokens**: 1200
- **System Prompt**: 
```
You are a Credit Pros advisor with access to transaction history data.
Analyze the provided transaction data to answer the user's question accurately and professionally.

Available data:
- Transaction...
```
- **Use Case**: Payment and transaction pattern analysis


### Variant 5: Phone Call Analysis
- **Name**: `Phone Call Analysis`
- **Description**: Current production prompt for call history analysis
- **Model**: gpt-4o-mini
- **Temperature**: 0.4
- **Max Tokens**: 1200
- **System Prompt**: 
```
You are a Credit Pros advisor with access to phone call history data.
Analyze the provided call data to answer the user's question accurately and professionally.

Available data:
- Phone call records ...
```
- **Use Case**: Call history and agent performance analysis


### Variant 6: Fallback Default
- **Name**: `Fallback Default`
- **Description**: Robust fallback prompt when Agenta.ai is unavailable
- **Model**: gpt-4o-mini
- **Temperature**: 0.7
- **Max Tokens**: 1000
- **System Prompt**: 
```
You are an advanced AI assistant with access to comprehensive Tilores customer data and credit analysis capabilities.

Available Tools:
- get_customer_credit_report(client_identifier): Get detailed cr...
```
- **Use Case**: General customer data analysis when specific prompts unavailable


## Step 4: Run Test Evaluations
1. Go to Evaluations section
2. Select a test set (you have 6 available)
3. Choose variants to test
4. Run evaluation
5. Review results and webhook notifications

## Step 5: Set Up A/B Testing
1. Go to Experiments section
2. Create new experiment
3. Select variants to compare
4. Set traffic split (e.g., 50/50)
5. Define success metrics
6. Launch experiment

## Step 6: Monitor Performance
1. Check webhook logs in your production API
2. Monitor response times and token usage
3. Set up alerts for performance thresholds
4. Review evaluation results regularly

## 🎯 Success Criteria
- [ ] All 6 variants created
- [ ] Webhooks configured and tested
- [ ] At least one evaluation completed
- [ ] A/B test experiment running
- [ ] Performance monitoring active

