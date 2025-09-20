# 🚨 DEPLOYMENT SAFETY CHECKLIST

## CRITICAL INCIDENT REPORT

**Date**: September 4, 2025
**Issue**: Accidentally deployed TLRS API code to OpenWebUI service
**Impact**: Complete OpenWebUI interface failure, wasted time and resources
**Root Cause**: Incorrect Railway service targeting during deployment

---

## MANDATORY PRE-DEPLOYMENT CHECKS

### 1. SERVICE VERIFICATION

```bash
# ALWAYS run these commands before ANY deployment:
railway status
railway service
```

**Expected Outputs**:

- TLRS API: `Project: tilores_x, Service: bubbly-simplicity`
- OpenWebUI: `Project: sincere-quietude, Service: open-webui`

### 2. DEPLOYMENT TARGET CONFIRMATION

- ✅ **TLRS API** → Deploy via **GitHub** (automatic Railway deployment)
- ✅ **OpenWebUI** → Deploy via **Docker template** (Railway template system)
- ❌ **NEVER** use `railway up` without confirming target service

### 3. URL MAPPING VERIFICATION

- `https://tilores-x.up.railway.app` → TLRS API (bubbly-simplicity)
- `https://tilores-x-ui.up.railway.app` → OpenWebUI (open-webui)

---

## DEPLOYMENT PROCEDURES

### TLRS API Deployment (Correct Method)

1. Commit and push code to GitHub
2. Railway automatically deploys from GitHub
3. Test endpoints: `/v1/models`, `/v1/chat/completions`

### OpenWebUI Deployment (Correct Method)

1. Use Railway Dashboard → Templates → Open WebUI
2. Configure environment variables from `openwebui-environment-config.sh`
3. Set custom domain: `tilores-x-ui.up.railway.app`

---

## PREVENTION MEASURES

### 1. MANDATORY COMMANDS BEFORE DEPLOYMENT

```bash
# Step 1: Verify current service
railway status

# Step 2: If wrong service, switch to correct one
railway service

# Step 3: Confirm target before proceeding
echo "Deploying to: $(railway status | grep Service)"
```

### 2. SERVICE ISOLATION

- **TLRS Repository** → Only deploys to `tilores_x` project
- **OpenWebUI** → Only uses Docker templates, never code deployment

### 3. TESTING REQUIREMENTS

- Test deployment target with sample API call BEFORE full deployment
- Verify service responds with expected content type (JSON vs HTML)

---

## RECOVERY PROCEDURES

### If TLRS API is Corrupted

1. Revert to last working GitHub commit
2. Railway will auto-deploy the revert
3. Test all endpoints for functionality

### If OpenWebUI is Corrupted

1. Delete corrupted Railway service
2. Create new OpenWebUI service from template
3. Apply environment variables from `openwebui-environment-config.sh`
4. Configure models via API

---

## COST IMPACT ANALYSIS

**Time Lost**: ~2 hours debugging and fixing regression
**Resources Wasted**: Multiple failed deployments, service recreation
**Business Impact**: OpenWebUI interface unavailable during fix period

**Prevention Value**: Following this checklist prevents 100% of similar incidents

---

## ACCOUNTABILITY

This checklist must be followed for ALL future deployments. Any deviation that causes service disruption will be considered a critical process violation.

**Signature Required**: All deployment procedures must be verified against this checklist before execution.
