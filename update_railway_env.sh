#!/bin/bash
# Script to update Railway environment variables with LangFuse configuration

echo "🚀 Updating Railway environment variables with LangFuse configuration..."
echo ""

# Build the railway command with all variables
CMD="railway variables"

# Add all existing variables plus LangFuse ones
while IFS= read -r line; do
    CMD="$CMD --set \"$line\""
done < railway_vars.txt

echo "Executing command with 65 environment variables..."
echo "⚠️  This may take a moment..."

# Execute the command
eval $CMD

echo ""
echo "✅ Railway environment variables updated!"
echo "🔄 Railway will automatically redeploy with new configuration"
echo ""
echo "📊 After deployment completes, test with:"
echo "   curl -s https://tilores-x.up.railway.app/health"
echo "   curl -s -X POST https://tilores-x.up.railway.app/v1/chat/completions -H 'Content-Type: application/json' -d '{\"messages\":[{\"role\":\"user\",\"content\":\"/help\"}]}' | jq '.choices[0].message.content | length'"
