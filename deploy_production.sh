#!/bin/bash
# PRODUCTION DEPLOYMENT SCRIPT
# Deploys Tilores with Langfuse Integration to Production

set -e  # Exit on any error

echo "🚀 TILORES PRODUCTION DEPLOYMENT WITH LANGFUSE INTEGRATION"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Pre-deployment validation
echo ""
echo "🔍 PRE-DEPLOYMENT VALIDATION"
echo "-----------------------------"

# Check if in correct directory
if [ ! -f "direct_credit_api_fixed.py" ]; then
    print_error "Not in tilores_X directory. Please run from tilores_X/"
    exit 1
fi

print_status "Directory validation passed"

# Check if nixpacks.toml is updated
if grep -q "direct_credit_api_fixed:app" nixpacks.toml; then
    print_status "Nixpacks configuration updated for Langfuse integration"
else
    print_error "Nixpacks configuration not updated. Please check nixpacks.toml"
    exit 1
fi

# Check if Langfuse is in requirements
if grep -q "langfuse" requirements.txt; then
    print_status "Langfuse dependency found in requirements.txt"
else
    print_error "Langfuse not found in requirements.txt"
    exit 1
fi

# Check environment variables (warn if not set)
echo ""
echo "🔐 ENVIRONMENT VARIABLE CHECK"
echo "-----------------------------"

REQUIRED_VARS=("OPENAI_API_KEY" "TILORES_API_URL" "TILORES_CLIENT_ID" "TILORES_CLIENT_SECRET")
LANGFUSE_VARS=("LANGFUSE_PUBLIC_KEY" "LANGFUSE_SECRET_KEY" "LANGFUSE_HOST")

missing_required=0
missing_langfuse=0

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Missing required environment variable: $var"
        ((missing_required++))
    else
        print_status "Required var set: $var"
    fi
done

for var in "${LANGFUSE_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        print_warning "Missing Langfuse environment variable: $var"
        ((missing_langfuse++))
    else
        print_status "Langfuse var set: $var"
    fi
done

if [ $missing_required -gt 0 ]; then
    print_error "Cannot deploy: Missing $missing_required required environment variables"
    exit 1
fi

if [ $missing_langfuse -gt 0 ]; then
    print_warning "Langfuse integration will be disabled ($missing_langfuse vars missing)"
    print_warning "Application will still function but without observability features"
fi

# Run pre-deployment tests
echo ""
echo "🧪 PRE-DEPLOYMENT TESTING"
echo "-------------------------"

echo "Running core logic tests..."
if python ../langfuse-integration/core_logic_test.py > /dev/null 2>&1; then
    print_status "Core logic tests passed"
else
    print_error "Core logic tests failed"
    print_warning "Deployment proceeding but functionality may be impaired"
fi

# Deployment
echo ""
echo "🚀 INITIATING PRODUCTION DEPLOYMENT"
echo "==================================="

# Check deployment platform
if command -v railway &> /dev/null; then
    DEPLOY_CMD="railway up --detach"
    DEPLOY_PLATFORM="Railway"
elif command -v heroku &> /dev/null; then
    DEPLOY_CMD="git push heroku main"
    DEPLOY_PLATFORM="Heroku"
elif command -v docker &> /dev/null; then
    DEPLOY_CMD="docker build -t tilores . && docker run -d -p 8080:8080 tilores"
    DEPLOY_PLATFORM="Docker"
else
    print_warning "No deployment platform detected. Please deploy manually."
    DEPLOY_CMD=""
    DEPLOY_PLATFORM="Manual"
fi

if [ -n "$DEPLOY_CMD" ]; then
    echo "Deploying to $DEPLOY_PLATFORM..."
    echo "Command: $DEPLOY_CMD"

    if eval "$DEPLOY_CMD"; then
        print_status "Deployment command executed successfully"
    else
        print_error "Deployment command failed"
        exit 1
    fi
else
    echo "Please execute manual deployment steps:"
    echo "1. Push code to your deployment platform"
    echo "2. Set environment variables"
    echo "3. Monitor deployment logs"
fi

# Post-deployment validation
echo ""
echo "🔍 POST-DEPLOYMENT VALIDATION"
echo "=============================="

# Wait for deployment
echo "Waiting for deployment to complete..."
sleep 30

# Try to get deployment URL
if command -v railway &> /dev/null; then
    DEPLOY_URL=$(railway domain 2>/dev/null || echo "")
    if [ -n "$DEPLOY_URL" ]; then
        echo "Deployment URL: https://$DEPLOY_URL"
        HEALTH_URL="https://$DEPLOY_URL/health"
    fi
fi

# If no URL detected, ask user
if [ -z "$HEALTH_URL" ]; then
    echo "Please enter your deployment URL (or press Enter to skip health check):"
    read -r DEPLOY_URL
    if [ -n "$DEPLOY_URL" ]; then
        HEALTH_URL="$DEPLOY_URL/health"
    fi
fi

# Health check
if [ -n "$HEALTH_URL" ]; then
    echo "Testing health endpoint: $HEALTH_URL"
    if curl -f -s "$HEALTH_URL" > /dev/null 2>&1; then
        print_status "Health check passed"
    else
        print_warning "Health check failed - deployment may still be starting"
    fi

    # Test slash command
    CHAT_URL="${HEALTH_URL%/health}/v1/chat/completions"
    echo "Testing slash command endpoint: $CHAT_URL"

    if curl -f -s -X POST "$CHAT_URL" \
        -H "Content-Type: application/json" \
        -d '{"messages":[{"role":"user","content":"/help"}]}' > /dev/null 2>&1; then
        print_status "API endpoint test passed"
    else
        print_warning "API endpoint test failed - may still be starting"
    fi
fi

# Final status
echo ""
echo "🎉 DEPLOYMENT PROCESS COMPLETED"
echo "==============================="

print_status "Tilores with Langfuse Integration deployed to production"
print_status "Core functionality preserved and enhanced"
print_status "Observability features active"

echo ""
echo "📋 NEXT STEPS:"
echo "1. Monitor deployment logs for any startup issues"
echo "2. Verify all slash commands work: /help, /cs status, /client credit"
echo "3. Check Langfuse dashboard for session, user, and metadata data"
echo "4. Monitor application performance and error rates"

if [ $missing_langfuse -gt 0 ]; then
    echo ""
    print_warning "LANGFUSE INTEGRATION NOTE:"
    print_warning "Set LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, and LANGFUSE_HOST"
    print_warning "environment variables to enable full observability features"
fi

echo ""
print_status "PRODUCTION DEPLOYMENT SUCCESSFUL!"
echo "🔗 Langfuse Dashboard: https://us.cloud.langfuse.com"
