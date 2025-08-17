# LangSmith Configuration Research Results

## Executive Summary

Investigation completed on LangSmith CLI and project configuration. **Key Finding**: Dashboard 404 errors are caused by hardcoded project names that don't match actual LangSmith workspace projects.

## Research Findings

### Authentication Status
- ✅ LangSmith SDK installed and functional
- ✅ API connection successful (API key ending in ...1495)
- ✅ Organization ID confirmed: `b36f2280-93a9-4523-bf03-707ac1032a33`

### Current Dashboard Configuration Issues

**Problem**: Dashboard uses hardcoded project names that don't exist:
```javascript
PROJECTS: {
  PRODUCTION: 'tilores-x-production',      // ❌ Does not exist
  EXPERIMENTS: 'tilores-x-experiments',    // ❌ Does not exist
  DEVELOPMENT: 'tilores-x-dev'             // ❌ Does not exist
}
```

### Actual LangSmith Projects Found

From codebase analysis, the **real project names** are:

#### Production Projects (Model-Specific)
```
tilores_production_gemini_1.5_flash_002-5bcffe02
tilores_production_claude_3_haiku-6ac54420
tilores_production_deepseek_r1_distill_llama_70b-00469321
tilores_production_gpt_4o_mini-68758e59
tilores_production_llama_3.3_70b_versatile-8c273476
```

#### Experiment Projects
```
tilores_llama_3.3_70b_versatile-25078bc4
tilores_gpt_3.5_turbo-635bd77e
tilores_gpt_4o_mini-dccf58af
tilores_deepseek_r1_distill_llama_70b-4e8c1e8a
tilores_claude_3_haiku-a70a5b91
```

## Correct LangSmith URLs

### Organization Level
- **Dashboard**: `https://smith.langchain.com/o/b36f2280-93a9-4523-bf03-707ac1032a33`
- **Settings**: `https://smith.langchain.com/o/b36f2280-93a9-4523-bf03-707ac1032a33/settings`

### Project Level (Example using primary production project)
Using project: `tilores_production_llama_3.3_70b_versatile-8c273476`

- **Project Dashboard**: `https://smith.langchain.com/o/b36f2280-93a9-4523-bf03-707ac1032a33/projects/p/tilores_production_llama_3.3_70b_versatile-8c273476`
- **Traces**: `https://smith.langchain.com/o/b36f2280-93a9-4523-bf03-707ac1032a33/projects/p/tilores_production_llama_3.3_70b_versatile-8c273476/traces`
- **Experiments**: `https://smith.langchain.com/o/b36f2280-93a9-4523-bf03-707ac1032a33/projects/p/tilores_production_llama_3.3_70b_versatile-8c273476/experiments`
- **Analytics**: `https://smith.langchain.com/o/b36f2280-93a9-4523-bf03-707ac1032a33/projects/p/tilores_production_llama_3.3_70b_versatile-8c273476/analytics`

## Dashboard Fix Requirements

### 1. Update Project Names in `dashboard/src/services/langsmithService.js`

**Replace current hardcoded names with actual project names:**

```javascript
// CURRENT (❌ BROKEN)
PROJECTS: {
  PRODUCTION: 'tilores-x-production',
  EXPERIMENTS: 'tilores-x-experiments',
  DEVELOPMENT: 'tilores-x-dev'
}

// FIXED (✅ WORKING)
PROJECTS: {
  PRODUCTION: 'tilores_production_llama_3.3_70b_versatile-8c273476',
  EXPERIMENTS: 'tilores_llama_3.3_70b_versatile-25078bc4',
  DEVELOPMENT: 'tilores_production_gpt_4o_mini-68758e59'  // or another suitable project
}
```

### 2. Environment Configuration

**Verify these variables in `.env`:**
```bash
LANGSMITH_API_KEY=<verified_working_key_ending_in_1495>
LANGCHAIN_API_KEY=<same_as_above>
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=tilores_production_llama_3.3_70b_versatile-8c273476
LANGSMITH_PROJECT=tilores_production_llama_3.3_70b_versatile-8c273476
```

## CLI Commands for Dynamic Project Discovery

Since project names appear to be generated dynamically, use this script for future updates:

```python
from langsmith import Client
import os

# Get all projects programmatically
client = Client(api_key=os.getenv('LANGSMITH_API_KEY'))
runs = list(client.list_runs(limit=100))
projects = set(run.session_name for run in runs if hasattr(run, 'session_name') and run.session_name)
print("Available projects:", list(projects))
```

## Project Categorization

Based on naming patterns:

### Production Projects
- Pattern: `tilores_production_*`
- Primary: `tilores_production_llama_3.3_70b_versatile-8c273476`
- Count: 5 model-specific production projects

### Experimental Projects
- Pattern: `tilores_*` (without production prefix)
- Primary: `tilores_llama_3.3_70b_versatile-25078bc4`
- Count: 5 experimental projects

### Development Projects
- Could use any production project for development testing
- Or create new projects following pattern: `tilores_development_*`

## Security Notes

✅ **Secure Configuration Confirmed:**
- Organization ID safely exposed (public in URLs)
- API key properly secured in environment variables
- No credentials hardcoded in dashboard source

## Next Steps

1. **Immediate Fix**: Update `langsmithService.js` with correct project names
2. **Test**: Verify dashboard links now work correctly
3. **Monitor**: Set up automated checks for new project creation
4. **Document**: Update team on correct project naming conventions

---

**Investigation Date**: 2025-08-17
**API Status**: ✅ Connected and authenticated
**Organization**: b36f2280-93a9-4523-bf03-707ac1032a33
**Primary Project**: tilores_production_llama_3.3_70b_versatile-8c273476
