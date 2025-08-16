# Deployment Versioning Requirements

## 🚨 CRITICAL: Version Update Policy

**EVERY DEPLOYMENT REQUIRES AN UPDATED VERSION NUMBER**

### Mandatory Version Updates

Before ANY deployment to production or staging:

1. **Update Version in main_enhanced.py**
   ```python
   # Line 50
   version="X.Y.Z"  # MUST increment before deployment
   ```

2. **Update Version in Health Endpoints**
   ```python
   # Line 405
   return {"status": "ok", "service": "tilores-anythingllm", "version": "X.Y.Z"}
   ```

3. **Update Version in Root Endpoint**
   ```python
   # Line 430
   "version": "X.Y.Z"
   ```

### Version Numbering Convention

Follow Semantic Versioning (SemVer):
- **MAJOR.MINOR.PATCH** (e.g., 6.2.0)

#### When to Increment:

**PATCH (X.Y.Z → X.Y.Z+1)**
- Bug fixes
- Performance improvements
- Documentation updates
- Minor refactoring
- Test additions

**MINOR (X.Y.Z → X.Y+1.0)**
- New features (backward compatible)
- New endpoints
- New utilities
- Significant improvements
- New integrations

**MAJOR (X.Y.Z → X+1.0.0)**
- Breaking API changes
- Major architectural changes
- Incompatible updates
- Complete rewrites

### Current Version History

- **6.0.0** - Initial production deployment with Phase VII completion
- **6.1.0** - Added streaming enhancements and data expansion (Phase IX)
- **6.2.0** - Added Function Executor pattern (Phase X)

### Deployment Checklist

Before deployment, ensure:

- [ ] Version number incremented in ALL locations
- [ ] Tests pass (run `python -m pytest`)
- [ ] Linting passes (run `flake8`)
- [ ] Memory bank updated with changes
- [ ] Git commit includes version in message
- [ ] Deployment notes reference new version

### Version Update Locations

Files that MUST be checked for version updates:

1. **main_enhanced.py**
   - Line ~50: FastAPI app version
   - Line ~405: Health endpoint version
   - Line ~430: Root endpoint version

2. **monitoring.py** (if version tracked)
   - Check for any version constants

3. **Docker/Deployment Files**
   - Dockerfile labels
   - docker-compose.yml services
   - Kubernetes manifests
   - CI/CD pipeline files

### Git Commit Message Format

When updating version:
```bash
git commit -m "chore: bump version to X.Y.Z for [reason]"
```

Example:
```bash
git commit -m "chore: bump version to 6.2.0 for Function Executor pattern"
```

### Verification Commands

After updating version, verify:
```bash
# Check version in code
grep -n "version.*6\." main_enhanced.py

# Verify in running app
curl http://localhost:8000/health | jq .version
curl http://localhost:8000/ | jq .version
```

## 🔴 NEVER DEPLOY WITHOUT VERSION UPDATE

Deploying without incrementing version number causes:
- Inability to track deployments
- Confusion in debugging issues
- Difficulty in rollback scenarios
- Loss of deployment history
- Compliance and audit problems

**Make version updates a non-negotiable part of the deployment process.**
