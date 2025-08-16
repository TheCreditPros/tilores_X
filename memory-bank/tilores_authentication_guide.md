# Tilores Authentication Guide

## OAuth Token Requirement for Direct GraphQL Access

**CRITICAL**: Tilores requires OAuth token authentication for direct GraphQL API access.

### Authentication Flow

```bash
# 1. Get OAuth Token
curl -X POST https://saas-umgegwho-tilores.auth.eu-central-1.amazoncognito.com/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=${TILORES_CLIENT_ID}&client_secret=${TILORES_CLIENT_SECRET}"

# 2. Use Token for GraphQL Requests
curl -X POST https://8edvhd7rqb.execute-api.eu-central-1.amazonaws.com \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{"query": "{ search(input: {...}) { ... } }"}'
```

### Environment Configuration

**Required Environment Variables:**
```bash
TILORES_GRAPHQL_API_URL=https://8edvhd7rqb.execute-api.eu-central-1.amazonaws.com
TILORES_OAUTH_TOKEN_URL=https://saas-umgegwho-tilores.auth.eu-central-1.amazoncognito.com/oauth2/token
TILORES_CLIENT_ID=3l3i0ifjurnr58u4lgf0eaeqa3
TILORES_CLIENT_SECRET=1c0g3v0u7pf1bvb7v65pauqt6s0h3vkkcf9u232u92ov3lm4aun2
```

### Current Project Configuration

**Our tilores_X Environment:**
```bash
TILORES_API_URL=https://ly325mgfwk.execute-api.us-east-1.amazonaws.com
TILORES_TOKEN_URL=https://saas-swidepnf-tilores.auth.us-east-1.amazoncognito.com/oauth2/token
TILORES_CLIENT_ID=2057mnnrv3...
TILORES_CLIENT_SECRET=[configured]
```

### Authentication Implementation

**Working Implementation in [`core_app.py`](core_app.py:502):**
- TiloresAPI.from_environ() handles OAuth automatically
- Token refresh managed internally
- No manual token management required for our API

**Direct GraphQL Access:**
- Requires manual OAuth token retrieval
- Token must be included in Authorization header
- Used for speed experiments and direct validation

### Test Records

**Validated Test Email Addresses:**
- `blessedwina@aol.com`
- `lelisguardado@sbcglobal.net`
- `migdaliareyes53@gmail.com`

**Note**: These are real customer records in the Tilores system and require proper OAuth authentication for direct GraphQL access.

### Speed Experiment Implications

**For LangSmith Experiments:**
1. Use our production API (https://tiloresx-production.up.railway.app) - no auth required
2. For direct GraphQL validation - OAuth token required
3. Current LangSmith callback conflict prevents tool execution
4. Remediation needed in [`core_app.py`](core_app.py:2049) callback handling

**Authentication Status:**
- ✅ Production API: No authentication required (working)
- ❌ Direct GraphQL: OAuth required (not implemented in experiments)
- 🔧 LangSmith Integration: Callback conflict needs resolution

Updated: 2025-08-16
