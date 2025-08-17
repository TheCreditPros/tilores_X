# Production Configuration & Troubleshooting Guide
## Tilores_X Autonomous AI Platform - DAY 1 Configuration Setup

**Status**: 🔧 **CONFIGURATION IN PROGRESS** - DAY 1: Configuration & Secrets Setup
**Phase**: Production Activation - Environment Configuration
**Updated**: 2025-08-17

---

## 📋 CONFIGURATION OVERVIEW

### **Current Deployment Status**
- ✅ **Codebase Deployed**: 3,125+ lines of autonomous AI platform code
- ✅ **Railway Infrastructure**: Production environment operational
- ✅ **LangSmith Integration**: 241 API endpoints ready for activation
- ⏳ **Secrets Configuration**: GitHub Secrets and Railway environment variables pending
- ⏳ **Autonomous AI Activation**: Awaiting configuration completion

### **Configuration Requirements**
1. **GitHub Secrets Configuration** - API keys and production credentials
2. **Railway Environment Variables** - Autonomous AI platform settings
3. **Environment Validation** - Connectivity and configuration testing
4. **LangSmith Enterprise Setup** - Workspace and project configuration

---

## 🔐 STEP 1: GITHUB SECRETS CONFIGURATION

### **Required Secrets Checklist**
```bash
# Core LangSmith Enterprise Integration
□ LANGSMITH_API_KEY=ls_[your_enterprise_key]
□ LANGSMITH_ORGANIZATION_ID=b36f2280-93a9-4523-bf03-707ac1032a33
□ LANGSMITH_PROJECT_PRODUCTION=tilores_production_llama_3.3_70b_versatile-8c273476
□ LANGSMITH_PROJECT_EXPERIMENTS=tilores_llama_3.3_70b_versatile-25078bc4
□ LANGSMITH_PROJECT_DEVELOPMENT=tilores_production_gpt_4o_mini-68758e59
□ LANGSMITH_WORKSPACE_ID=b36f2280-93a9-4523-bf03-707ac1032a33

# AI Provider APIs
□ OPENAI_API_KEY=sk-[your_openai_key]
□ ANTHROPIC_API_KEY=sk-ant-[your_anthropic_key]
□ GROQ_API_KEY=gsk_[your_groq_key]
□ GOOGLE_API_KEY=[your_google_ai_key]

# Production Environment Flags
□ RAILWAY_ENVIRONMENT=production
□ AUTONOMOUS_AI_ENABLED=true
□ AUTONOMOUS_AI_PLATFORM_ENABLED=true
□ PREDICTIVE_QUALITY_ENABLED=true
□ LANGSMITH_ENTERPRISE_MODE=true

# Autonomous AI Capabilities
□ META_LEARNING_ENGINE_ENABLED=true
□ PATTERN_INDEXING_ENABLED=true
□ A_B_TESTING_FRAMEWORK_ENABLED=true
□ FEEDBACK_COLLECTION_ENABLED=true
□ BULK_ANALYTICS_ENABLED=true
□ ANNOTATION_QUEUE_ENABLED=true
□ DELTA_REGRESSION_ANALYSIS_ENABLED=true
□ PREDICTIVE_QUALITY_MANAGEMENT=true

# Quality Management Thresholds
□ QUALITY_THRESHOLD_CRITICAL=85
□ QUALITY_THRESHOLD_WARNING=90
□ QUALITY_THRESHOLD_TARGET=95
□ QUALITY_THRESHOLD_EXCELLENT=98
□ PREDICTIVE_FORECAST_DAYS=7
```

### **Configuration Steps**
1. **Navigate to GitHub Repository**
   ```
   https://github.com/[username]/tilores_X
   Settings → Secrets and variables → Actions
   ```

2. **Add Each Secret**
   - Click "New repository secret"
   - Enter exact variable name (case-sensitive)
   - Paste the actual value (will be masked automatically)
   - Click "Add secret"

3. **Verify Configuration**
   - All secrets appear in the secrets list
   - No typos in secret names
   - Values are properly masked in display

---

## 🚂 STEP 2: RAILWAY ENVIRONMENT VARIABLES

### **Automated Configuration Script**
Use the provided Railway configuration script:

```bash
# Run the Railway environment setup script
python railway_environment_setup.py

# Expected output:
# ✅ Railway CLI version: x.x.x
# ✅ Linked to Railway project: 09db04c8-03ac-4661-b2fd-b631d7209c3d
# 🔧 Configuring Railway environment variables...
# ✅ Set AUTONOMOUS_AI_PLATFORM_ENABLED
# ✅ Set LANGSMITH_ENTERPRISE_MODE
# ... (all variables configured)
# 📄 Configuration report saved to: railway_configuration_report.md
```

### **Manual Configuration (Alternative)**
If automated script fails, configure manually via Railway dashboard:

1. **Access Railway Dashboard**
   ```
   https://railway.app/project/09db04c8-03ac-4661-b2fd-b631d7209c3d
   Navigate to Variables section
   ```

2. **Add Required Variables**
   ```bash
   # Core Platform Configuration
   AUTONOMOUS_AI_PLATFORM_ENABLED=true
   LANGSMITH_ENTERPRISE_MODE=true
   PREDICTIVE_QUALITY_MANAGEMENT=true
   META_LEARNING_ENGINE_ENABLED=true
   PATTERN_INDEXING_ENABLED=true
   A_B_TESTING_FRAMEWORK_ENABLED=true
   FEEDBACK_COLLECTION_ENABLED=true
   BULK_ANALYTICS_ENABLED=true
   ANNOTATION_QUEUE_ENABLED=true
   DELTA_REGRESSION_ANALYSIS_ENABLED=true

   # LangSmith Projects
   LANGSMITH_PROJECT_PRODUCTION=tilores_production_llama_3.3_70b_versatile-8c273476
   LANGSMITH_PROJECT_EXPERIMENTS=tilores_llama_3.3_70b_versatile-25078bc4
   LANGSMITH_PROJECT_DEVELOPMENT=tilores_production_gpt_4o_mini-68758e59
   LANGSMITH_WORKSPACE_ID=b36f2280-93a9-4523-bf03-707ac1032a33

   # Quality Thresholds
   QUALITY_THRESHOLD_CRITICAL=85
   QUALITY_THRESHOLD_WARNING=90
   QUALITY_THRESHOLD_TARGET=95
   QUALITY_THRESHOLD_EXCELLENT=98
   PREDICTIVE_FORECAST_DAYS=7

   # Environment Settings
   RAILWAY_ENVIRONMENT=production
   AUTONOMOUS_AI_ENABLED=true
   AUTONOMOUS_AI_MODE=production
   PREDICTIVE_QUALITY_ENABLED=true
   LANGSMITH_ENTERPRISE_FEATURES=true
   ```

3. **Trigger Deployment**
   ```bash
   # Via Railway CLI
   railway up --detach

   # Or via Git push
   git push origin main
   ```

---

## 🧪 STEP 3: ENVIRONMENT VALIDATION

### **Automated Validation Script**
Run comprehensive environment validation:

```bash
# Install required dependencies
pip install aiohttp

# Run validation script
python environment_validation_test.py

# Expected output:
# 🚀 Starting Comprehensive Environment Validation
# ============================================================
# 🔍 Environment Variables Validation
# ============================================================
# ✅ PASS LANGSMITH_API_KEY
# ✅ PASS LANGSMITH_ORGANIZATION_ID
# ... (all variables validated)
#
# ============================================================
# 🔍 LangSmith API Connectivity Test
# ============================================================
# ✅ PASS LangSmith Authentication
# ✅ PASS LangSmith /workspaces
# ... (all endpoints tested)
#
# 📊 Final Results: X/Y tests passed (Z.Z%)
# ✅ Environment validation completed successfully
```

### **Manual Validation Commands**
If automated validation fails, test manually:

```bash
# Test LangSmith API connectivity
curl -H "Authorization: Bearer $LANGSMITH_API_KEY" \
     -H "X-Organization-Id: $LANGSMITH_ORGANIZATION_ID" \
     https://api.smith.langchain.com/workspaces

# Test Railway deployment status
railway status
railway logs --tail

# Test production endpoints
curl https://tilores-x.up.railway.app/health
curl https://tilores-x.up.railway.app/health/autonomous
curl https://tilores-x.up.railway.app/metrics/autonomous
```

---

## 🔧 TROUBLESHOOTING GUIDE

### **Common Issues & Solutions**

#### **1. GitHub Secrets Not Propagating**
**Symptoms:**
- Environment variables not available in Railway
- Application logs show missing configuration
- Autonomous AI platform fails to initialize

**Solutions:**
```bash
# Check secret names (case-sensitive)
# Verify in GitHub: Settings → Secrets and variables → Actions

# Test secret accessibility
# Create test GitHub Action workflow:
name: Test Secrets
on: workflow_dispatch
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test LangSmith Key
        run: echo "Key configured: ${{ secrets.LANGSMITH_API_KEY != '' }}"
```

**Root Causes:**
- Typo in secret name (case-sensitive)
- Repository permissions don't allow Actions access
- Railway integration not properly configured

#### **2. LangSmith API Authentication Failures**
**Symptoms:**
- 401 Unauthorized responses from LangSmith API
- "Invalid API key" errors in logs
- Workspace access denied

**Solutions:**
```bash
# Verify API key format
echo $LANGSMITH_API_KEY | grep -E "^ls_[a-zA-Z0-9]+$"

# Test API key manually
curl -H "Authorization: Bearer $LANGSMITH_API_KEY" \
     https://api.smith.langchain.com/workspaces

# Check organization ID
curl -H "Authorization: Bearer $LANGSMITH_API_KEY" \
     -H "X-Organization-Id: $LANGSMITH_ORGANIZATION_ID" \
     https://api.smith.langchain.com/workspaces
```

**Root Causes:**
- Incorrect API key format (should start with `ls_`)
- Wrong organization ID
- API key doesn't have enterprise permissions
- Workspace access not granted

#### **3. Railway Environment Variables Not Loading**
**Symptoms:**
- Variables not visible in Railway dashboard
- Application startup fails with missing environment variables
- Railway deployment succeeds but app doesn't start

**Solutions:**
```bash
# Check Railway CLI authentication
railway login
railway link -p 09db04c8-03ac-4661-b2fd-b631d7209c3d

# List current variables
railway variables

# Set variables manually
railway variables set AUTONOMOUS_AI_ENABLED=true

# Trigger new deployment
railway up --detach
```

**Root Causes:**
- Railway CLI not authenticated
- Wrong project linked
- Variables not properly saved
- Deployment not triggered after variable changes

#### **4. Autonomous AI Platform Not Initializing**
**Symptoms:**
- `/health/autonomous` returns "disabled" or "error"
- Application logs show initialization failures
- Platform capabilities not available

**Solutions:**
```bash
# Check required environment variables
curl https://tilores-x.up.railway.app/health/autonomous

# Review application logs
railway logs --tail

# Verify all required variables are set
python environment_validation_test.py
```

**Root Causes:**
- Missing required environment variables
- LangSmith client initialization failure
- Network connectivity issues
- Insufficient API permissions

#### **5. Production Endpoints Not Responding**
**Symptoms:**
- 404 or 500 errors from production URLs
- Application not accessible
- Health checks failing

**Solutions:**
```bash
# Check deployment status
railway status

# View deployment logs
railway logs --tail

# Test basic connectivity
curl -I https://tilores-x.up.railway.app/health

# Check Railway service status
railway ps
```

**Root Causes:**
- Deployment failed
- Application startup errors
- Port configuration issues
- Railway service not running

### **Diagnostic Commands**

#### **Environment Validation**
```bash
# Quick environment check
python -c "
import os
required = ['LANGSMITH_API_KEY', 'LANGSMITH_ORGANIZATION_ID', 'AUTONOMOUS_AI_ENABLED']
for var in required:
    value = os.getenv(var)
    print(f'{var}: {\"✅ SET\" if value else \"❌ MISSING\"}')"

# Full validation suite
python environment_validation_test.py
```

#### **Railway Diagnostics**
```bash
# Railway project status
railway status --json

# Environment variables
railway variables

# Recent deployments
railway logs --tail

# Service health
railway ps
```

#### **LangSmith Connectivity**
```bash
# Test authentication
curl -s -H "Authorization: Bearer $LANGSMITH_API_KEY" \
     https://api.smith.langchain.com/workspaces | jq .

# Test organization access
curl -s -H "Authorization: Bearer $LANGSMITH_API_KEY" \
     -H "X-Organization-Id: $LANGSMITH_ORGANIZATION_ID" \
     https://api.smith.langchain.com/projects | jq length
```

#### **Production Health Checks**
```bash
# Basic health
curl -s https://tilores-x.up.railway.app/health | jq .

# Autonomous AI health
curl -s https://tilores-x.up.railway.app/health/autonomous | jq .

# Metrics endpoint
curl -s https://tilores-x.up.railway.app/metrics/autonomous | jq .
```

---

## 📊 VALIDATION CHECKLIST

### **Pre-Activation Validation**
Before proceeding to autonomous AI platform activation, ensure:

#### **GitHub Secrets (Required: 100%)**
- [ ] All 28 required secrets configured
- [ ] Secret names match exactly (case-sensitive)
- [ ] Values are properly formatted
- [ ] Secrets accessible in GitHub Actions

#### **Railway Environment Variables (Required: 100%)**
- [ ] All 25+ autonomous AI variables configured
- [ ] LangSmith project IDs correct
- [ ] Quality thresholds properly set
- [ ] Environment flags enabled

#### **API Connectivity (Required: 90%+)**
- [ ] LangSmith API authentication successful
- [ ] All 4 LangSmith endpoints responding
- [ ] OpenAI API accessible
- [ ] Anthropic API accessible
- [ ] Groq API accessible

#### **Production Deployment (Required: 100%)**
- [ ] Railway deployment successful
- [ ] Application startup without errors
- [ ] Health endpoints responding
- [ ] Autonomous AI health check active

#### **Environment Validation (Required: 90%+)**
- [ ] Environment validation script passes
- [ ] All critical tests successful
- [ ] Validation report generated
- [ ] No blocking issues identified

---

## 🚀 SUCCESS CRITERIA

### **Configuration Complete Indicators**
1. **Environment Validation**: 90%+ test success rate
2. **GitHub Secrets**: All 28 secrets configured and accessible
3. **Railway Variables**: All autonomous AI variables set
4. **API Connectivity**: LangSmith and AI providers responding
5. **Production Health**: All health endpoints returning "healthy"

### **Ready for Next Phase**
When all criteria are met:
- ✅ **DAY 1 Complete**: Configuration & Secrets Setup finished
- 🚀 **DAY 2 Ready**: LangSmith Enterprise Setup can begin
- 🤖 **Platform Status**: Ready for autonomous AI activation

### **Activation Command**
Once validation passes, trigger autonomous AI platform activation:

```bash
# Trigger autonomous optimization cycle
curl -X POST https://tilores-x.up.railway.app/autonomous/optimize

# Expected response:
{
  "status": "success",
  "optimization_result": {
    "components_executed": 8,
    "improvements_identified": [...],
    "quality_improvement": 2.3
  },
  "timestamp": "2025-08-17T..."
}
```

---

## 📋 NEXT STEPS

### **Upon Successful Configuration**
1. **Generate Configuration Report**
   ```bash
   python railway_environment_setup.py
   python environment_validation_test.py
   ```

2. **Proceed to DAY 2: LangSmith Enterprise Setup**
   - Create dedicated autonomous AI projects
   - Configure workspace permissions
   - Set up dataset management
   - Enable bulk operations

3. **Monitor Initial Activation**
   - Watch deployment logs: `railway logs --tail`
   - Monitor health endpoints
   - Verify autonomous capabilities initialization

### **If Configuration Issues Persist**
1. **Review Error Logs**
   - GitHub Actions logs for secret issues
   - Railway deployment logs for variable problems
   - Application logs for initialization failures

2. **Contact Support Resources**
   - GitHub repository issues
   - Railway support documentation
   - LangSmith enterprise support

3. **Rollback Procedures**
   - Disable autonomous AI features: `AUTONOMOUS_AI_ENABLED=false`
   - Revert to previous stable deployment
   - Re-run configuration with corrected values

---

**Configuration Status**: ⏳ **IN PROGRESS** - DAY 1: Configuration & Secrets Setup
**Next Milestone**: 🚀 **DAY 2: LangSmith Enterprise Setup**
**Success Criteria**: 90%+ validation success rate with all autonomous AI capabilities operational
