# Repository Reversion Guide

## Emergency Reversion Procedures

### When to Use This Guide
Use this guide if you need to revert the extensive repository cleanup performed on September 25, 2025. This includes removal of deprecated/, dashboard/, dashboard-static/, archive/, and patches/ folders.

### Quick Reversion Commands

#### Complete Repository Reversion (Recommended)
```bash
# Revert to pre-cleanup state (includes all GraphQL fixes)
git reset --hard 61a7192

# Or revert just the folder cleanup
git reset --hard 935023b
```

#### Selective File/Folder Restoration
```bash
# Restore specific folders from before cleanup
git checkout 935023b -- deprecated/
git checkout 935023b -- dashboard/
git checkout 935023b -- dashboard-static/
git checkout 935023b -- archive/
git checkout 935023b -- patches/
```

### Detailed Reversion Steps

#### Step 1: Assess Current State
```bash
git status
git log --oneline -10
```

#### Step 2: Choose Reversion Strategy

**Option A: Complete Reversion (Safest)**
```bash
# Revert to state before any cleanup
git reset --hard 61a7192
```

**Option B: Partial Reversion (Selective)**
```bash
# Keep GraphQL fixes but restore removed folders
git reset --hard 39bfcd8  # File cleanup only
git checkout 935023b -- deprecated/
git checkout 935023b -- dashboard/
# ... restore other folders as needed
```

#### Step 3: Verify Functionality
```bash
# Test core functionality
python3 -c "
import direct_credit_api_fixed as api
instance = api.MultiProviderCreditAPI()
result = instance._process_slash_command('/cs marcogjones@yahoo.com')
print('Email detection works:', '**CUSTOMER PROFILE:**' in result)
print('GraphQL cleaned:', 'GRAPHQL' not in result.upper())
"
```

#### Step 4: Update Documentation
After reversion, update the activeContext.md to reflect the restored state.

### What Was Removed (Reference)

#### `deprecated/` Folder (72+ files)
- **Location**: `tilores_X/deprecated/`
- **Contents**: Old experimental code, deprecated APIs, unused scripts
- **Key files**: `agenta_*.py`, `openwebui_*.py`, `autonomous_*.py`, etc.
- **Safe to remove**: Explicitly marked as deprecated

#### `dashboard/` Folder (Full Application)
- **Location**: `tilores_X/dashboard/`
- **Contents**: Complete React/Vite dashboard with source, tests, build
- **Subfolders**: `src/`, `tests/`, `e2e-tests/`, `dist/`, `dashboard-static/`
- **Safe to remove**: Not referenced in main application code

#### `dashboard-static/` Folder (13 files)
- **Location**: `tilores_X/dashboard-static/`
- **Contents**: Compiled JavaScript, CSS, HTML assets
- **Safe to remove**: Redundant with source dashboard

#### `archive/` Folder (13 files)
- **Location**: `tilores_X/archive/`
- **Contents**: Old deployment reports (DAY1-5, langsmith analysis, etc.)
- **Safe to remove**: Better organized in `docs/` folder

#### `patches/` Folder (1 file)
- **Location**: `tilores_X/patches/`
- **Contents**: `roo-guard-env-dump.patch`
- **Safe to remove**: Patch for resolved environment issue

### Current Clean State (Post-Cleanup)

```
tilores_X/
├── docs/           # Documentation and guides
├── utils/          # Utility functions and tools
├── .git/           # Version control
├── .github/        # GitHub Actions and workflows
├── .githooks/      # Git hooks
├── .pytest_cache/  # Test cache
├── __pycache__/    # Python bytecode cache
└── .claude/        # IDE configuration
```

### Risk Assessment
- **Low Risk**: All removed content was unused/deprecated
- **Verified Safe**: Functionality tested after each removal phase
- **Git Recovery**: All content recoverable via git history
- **Impact**: Repository reduced from 50+ to 8 directories

### Contact Information
If reversion is needed, reference this guide and the memory bank documentation for complete context.
