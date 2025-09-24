#!/bin/bash
# Test script to validate LangFuse integration after Railway deployment

echo "🧪 Testing LangFuse Integration Post-Deployment"
echo "================================================"
echo ""

# Test 1: Health check
echo "1. Testing API health..."
HEALTH=$(curl -s https://tilores-x.up.railway.app/health | jq -r .status 2>/dev/null || echo "failed")
if [ "$HEALTH" = "healthy" ]; then
    echo "   ✅ Health check: PASSED"
else
    echo "   ❌ Health check: FAILED"
fi
echo ""

# Test 2: Slash commands
echo "2. Testing slash commands..."
HELP_LENGTH=$(curl -s -X POST https://tilores-x.up.railway.app/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"/help"}]}' | jq '.choices[0].message.content | length' 2>/dev/null || echo "0")

if [ "$HELP_LENGTH" -gt 1000 ]; then
    echo "   ✅ Slash commands: PASSED (${HELP_LENGTH} chars)"
else
    echo "   ❌ Slash commands: FAILED"
fi
echo ""

# Test 3: LangFuse connectivity (check logs for LangFuse messages)
echo "3. Checking LangFuse integration..."
echo "   📊 Checking Railway logs for LangFuse status..."
echo "   Look for these indicators in Railway logs:"
echo "   - '✅ Langfuse client initialized for metadata tracking'"
echo "   - '📊 Langfuse metadata tracking active'"
echo "   - No authentication errors"
echo ""

# Test 4: Prompt loading test
echo "4. Testing prompt loading..."
echo "   🚀 Run this locally to test LangFuse prompt loading:"
echo "   cd /path/to/project && python3 -c \""
echo "   from agent_prompts import get_agent_prompt"
echo "   prompt = get_agent_prompt('zoho_cs_agent')"
echo "   print(f'Prompt source: {prompt.get(\"source\")}')\""
echo "   Expected: 'langfuse' (not 'fallback')"
echo ""

echo "📋 NEXT STEPS AFTER CONFIRMATION:"
echo "=================================="
echo ""
echo "1. ✅ Confirm LangFuse variables are set in Railway dashboard"
echo "2. ✅ Wait for Railway auto-deployment to complete"
echo "3. ✅ Run migration: python migrate_prompts_to_langfuse.py"
echo "4. ✅ Visit LangFuse dashboard to see migrated prompts"
echo "5. ✅ Test A/B experiments and version control"
echo ""
echo "🎯 SUCCESS INDICATORS:"
echo "- Railway logs show LangFuse initialization without errors"
echo "- Local prompt loading shows 'source: langfuse'"
echo "- LangFuse dashboard shows migrated prompts"
echo "- API responses include LangFuse metadata tracking"
