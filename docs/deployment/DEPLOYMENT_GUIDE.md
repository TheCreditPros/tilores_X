# Autonomous AI Platform Deployment Guide

## 🚨 CRITICAL: Mandatory GitHub Actions Monitoring Required

**ALL DEPLOYMENTS MUST INCLUDE REAL-TIME MONITORING** - See [Mandatory GitHub Actions Monitoring Protocol](MANDATORY_GITHUB_ACTIONS_MONITORING.md)

## Overview
This guide covers the secure deployment of the tilores_X Autonomous AI Platform using GitHub Actions CI/CD pipeline with Railway hosting. Following critical deployment lessons learned, **all deployments now require mandatory real-time GitHub Actions monitoring**.

## Architecture
- **Entry Point**: `main_autonomous_production.py`
- **Core Components**:
  - `autonomous_ai_platform.py` - 8 advanced AI capabilities
  - `langsmith_enterprise_client.py` - 241 LangSmith API endpoints
  - `autonomous_integration.py` - Enhanced virtuous cycle management
- **Infrastructure**: Railway with NIXPACKS builder
- **CI/CD**: GitHub Actions with multi-stage validation

## Deployment Process

### 🚨 MANDATORY: GitHub Actions Monitoring

**CRITICAL REQUIREMENT**: Every deployment MUST include real-time GitHub Actions monitoring using:

```bash
gh run watch --exit-status
```

**This command must be executed immediately after triggering any deployment.**

For complete monitoring procedures, see: [Mandatory GitHub Actions Monitoring Protocol](MANDATORY_GITHUB_ACTIONS_MONITORING.md)

### 1. Security & Compliance
- Bandit security scanning
- Safety vulnerability checks
- Semgrep code analysis
- All security reports uploaded as artifacts

### 2. Test Validation
- **Unit Tests**: Core component validation
- **Integration Tests**: LangSmith API connectivity
- **Performance Tests**: Load and response time validation
- **Autonomous AI Validation**: Platform initialization and status checks

### 3. Build Process
- Python 3.11 environment setup
- Dashboard build with Node.js 18
- Dependency caching for performance
- Artifact generation and storage

### 4. Deployment Stages

#### Staging Deployment
- **Trigger**: Push to `main` branch
- **Environment**: `staging`
- **Validation**: Health checks, autonomous status, metrics
- **URL**: Configured via `STAGING_URL` secret

#### Production Deployment
- **Trigger**: Push to `production` branch or manual dispatch
- **Environment**: `production`
- **Validation**: Full smoke tests including autonomous AI endpoints
- **URL**: Configured via `PRODUCTION_URL` secret

### 5. Post-Deployment Validation

#### Mandatory Verification Steps
- [ ] GitHub Actions monitoring completed with exit status 0
- [ ] GitHub Actions run ID documented
- [ ] All workflow jobs marked as successful
- [ ] Deployment artifacts confirmed
- [ ] Health endpoints validated

#### Automated Monitoring Setup
- Automated monitoring setup
- Deployment report generation
- Performance metrics collection

#### Deployment Report Requirements
All deployment reports MUST include:
- GitHub Actions run ID
- Exit status confirmation (0 = success)
- Monitoring command execution evidence
- Workflow completion timestamp
- Any error messages or warnings

## Required GitHub Secrets

### Test Environment
- `LANGSMITH_API_KEY_TEST`: Test LangSmith API key
- `LANGSMITH_ORGANIZATION_ID_TEST`: Test organization ID

### Staging Environment
- `RAILWAY_TOKEN_STAGING`: Railway staging deployment token
- `STAGING_URL`: Staging environment URL

### Production Environment
- `RAILWAY_TOKEN_PRODUCTION`: Railway production deployment token
- `PRODUCTION_URL`: Production environment URL
- `LANGSMITH_API_KEY_PROD`: Production LangSmith API key

## Environment Variables (Railway)

### Core Configuration
```bash
AUTONOMOUS_AI_ENABLED=true
META_LEARNING_ENABLED=true
LANGSMITH_API_KEY=<production-key>
LANGSMITH_ORGANIZATION_ID=<org-id>
```

### Optional Configuration
```bash
REDIS_URL=<redis-connection-string>
LOG_LEVEL=INFO
ENVIRONMENT=production
```

## Deployment Commands

### Manual Deployment (Emergency Only)
```bash
# Never use direct Railway deployment
# All deployments must go through GitHub Actions
```

### Trigger Deployment with Mandatory Monitoring

**CRITICAL**: Every deployment must follow this exact sequence:

```bash
# 1. Trigger deployment
git push origin main  # or production branch

# 2. IMMEDIATELY start monitoring (MANDATORY)
gh run watch --exit-status

# 3. Wait for completion and verify exit status is 0
# 4. Document GitHub Actions run ID in deployment report
```

**Alternative Methods:**
```bash
# Manual dispatch via GitHub UI
# Actions -> Deploy Autonomous AI Platform -> Run workflow
# Then IMMEDIATELY execute: gh run watch --exit-status
```

**⚠️ WARNING**: Never report deployment success without GitHub Actions verification!

## Rollback Procedures

### Automatic Rollback
- Failed health checks trigger automatic rollback
- Previous deployment maintained for instant recovery

### Manual Rollback
1. Navigate to Railway dashboard
2. Select previous successful deployment
3. Click "Redeploy"
4. Verify health checks pass

### Emergency Rollback
```bash
# Use Railway CLI (emergency only)
railway rollback --environment production
```

## Monitoring & Observability

### Health Endpoints
- `/health` - Basic health check
- `/autonomous/status` - Autonomous AI platform status
- `/metrics` - Performance metrics
- `/langsmith/projects` - LangSmith connectivity

### Key Metrics
- Response time < 2s for health checks
- Autonomous AI initialization success rate > 99%
- LangSmith API connectivity > 99.9%
- Memory usage < 512MB baseline

## Security Considerations

### Secrets Management
- All credentials stored in GitHub Secrets
- Environment-specific secret isolation
- No hardcoded tokens or keys in code

### Network Security
- HTTPS-only communication
- Railway managed TLS certificates
- API key rotation procedures

### Compliance
- Security scanning on every deployment
- Vulnerability assessment reports
- Audit trail via GitHub Actions logs

## Troubleshooting

### Common Issues

#### Deployment Failures
1. Check GitHub Actions logs
2. Verify all required secrets are set
3. Validate Railway service configuration
4. Review security scan results

#### Health Check Failures
1. Check application logs in Railway
2. Verify environment variables
3. Test LangSmith API connectivity
4. Validate autonomous AI platform initialization

#### Performance Issues
1. Monitor memory usage
2. Check Redis cache connectivity
3. Review LangSmith API response times
4. Analyze autonomous AI processing metrics

### Support Contacts
- **DevOps**: GitHub Issues
- **Security**: Security scan reports
- **Platform**: Railway dashboard logs

## Best Practices

### Development Workflow
1. Feature development on feature branches
2. Pull request to `main` triggers staging deployment
3. Manual promotion to `production` branch
4. Automated testing at every stage

### Security Practices
1. Regular dependency updates
2. Security scan review before deployment
3. Environment variable rotation
4. Access control via GitHub permissions

### Monitoring Practices
1. Real-time health monitoring
2. Performance baseline tracking
3. Error rate alerting
4. Capacity planning based on metrics

## Version History
- **v1.0**: Initial autonomous AI platform deployment
- **v1.1**: Enhanced security scanning and validation
- **v1.2**: Multi-environment deployment pipeline
