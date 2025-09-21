#!/usr/bin/env python3
"""
Railway Deployment Troubleshooting Tool
Diagnoses and monitors Railway deployment issues
"""

import time
import requests
import json
from datetime import datetime

def test_railway_endpoint(url="https://tilores-x.up.railway.app"):
    """Test Railway deployment endpoints and diagnose issues"""

    print("🚂 RAILWAY DEPLOYMENT TROUBLESHOOTING")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing URL: {url}")
    print()

    # Test endpoints in order of complexity
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check endpoint"),
        ("/v1/models", "Models endpoint"),
        ("/v1/chat/completions", "Chat completions endpoint (POST)")
    ]

    results = {}

    for endpoint, description in endpoints:
        print(f"🔍 Testing {description}: {url}{endpoint}")

        try:
            if endpoint == "/v1/chat/completions":
                # POST request for chat completions
                response = requests.post(
                    f"{url}{endpoint}",
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": "test"}],
                        "temperature": 0.7
                    },
                    timeout=30
                )
            else:
                # GET request for other endpoints
                response = requests.get(f"{url}{endpoint}", timeout=10)

            results[endpoint] = {
                "status_code": response.status_code,
                "success": response.status_code < 400,
                "response_time": response.elapsed.total_seconds(),
                "headers": dict(response.headers),
                "content": response.text[:200] if len(response.text) < 200 else response.text[:200] + "..."
            }

            if response.status_code < 400:
                print(f"  ✅ SUCCESS: {response.status_code} ({response.elapsed.total_seconds():.2f}s)")
            else:
                print(f"  ❌ FAILED: {response.status_code} - {response.reason}")

        except requests.exceptions.ConnectTimeout:
            print(f"  ❌ CONNECTION TIMEOUT: Server not responding")
            results[endpoint] = {"error": "connection_timeout"}
        except requests.exceptions.ReadTimeout:
            print(f"  ❌ READ TIMEOUT: Server too slow to respond")
            results[endpoint] = {"error": "read_timeout"}
        except requests.exceptions.ConnectionError as e:
            print(f"  ❌ CONNECTION ERROR: {str(e)}")
            results[endpoint] = {"error": "connection_error", "details": str(e)}
        except Exception as e:
            print(f"  ❌ UNEXPECTED ERROR: {str(e)}")
            results[endpoint] = {"error": "unexpected", "details": str(e)}

        print()

    return results

def analyze_deployment_issues(results):
    """Analyze test results and provide deployment recommendations"""

    print("📊 DEPLOYMENT ANALYSIS")
    print("=" * 40)

    # Check if any endpoints are working
    working_endpoints = [ep for ep, result in results.items()
                        if isinstance(result, dict) and result.get("success")]

    if not working_endpoints:
        print("🚨 CRITICAL: No endpoints responding")
        print()
        print("LIKELY CAUSES:")
        print("1. ❌ Application not starting (check Railway logs)")
        print("2. ❌ PORT binding issue (fixed in latest commit)")
        print("3. ❌ Missing environment variables")
        print("4. ❌ Application crash during startup")
        print()
        print("IMMEDIATE ACTIONS:")
        print("1. Check Railway deployment logs")
        print("2. Verify environment variables are set")
        print("3. Confirm latest commit deployed")
        print("4. Check for startup errors in logs")

    elif len(working_endpoints) < len(results):
        print("⚠️  PARTIAL: Some endpoints working")
        print(f"Working: {working_endpoints}")
        failed = [ep for ep in results.keys() if ep not in working_endpoints]
        print(f"Failed: {failed}")

    else:
        print("✅ SUCCESS: All endpoints responding")
        print("Deployment appears to be working correctly")

    print()

    # Check for specific error patterns
    for endpoint, result in results.items():
        if isinstance(result, dict) and result.get("status_code") == 502:
            print(f"🚨 502 Bad Gateway on {endpoint}:")
            print("  - Application not responding to Railway proxy")
            print("  - Check if app is binding to correct PORT")
            print("  - Verify application startup logs")
            print()
        elif isinstance(result, dict) and result.get("status_code") == 500:
            print(f"⚠️  500 Internal Server Error on {endpoint}:")
            print("  - Application started but encountering runtime errors")
            print("  - Check application logs for exceptions")
            print("  - Verify environment variables and dependencies")
            print()

def check_railway_environment_requirements():
    """Check what environment variables Railway needs"""

    print("🔧 RAILWAY ENVIRONMENT REQUIREMENTS")
    print("=" * 50)

    required_vars = [
        ("TILORES_GRAPHQL_API_URL", "Tilores GraphQL endpoint", True),
        ("TILORES_CLIENT_ID", "Tilores OAuth client ID", True),
        ("TILORES_CLIENT_SECRET", "Tilores OAuth client secret", True),
        ("TILORES_OAUTH_TOKEN_URL", "Tilores OAuth token endpoint", True),
        ("OPENAI_API_KEY", "OpenAI API key for LLM calls", True),
        ("GOOGLE_API_KEY", "Google Gemini API key", False),
        ("GROQ_API_KEY", "Groq API key", False),
        ("PORT", "Railway-provided port (automatic)", False)
    ]

    print("Required Environment Variables:")
    for var, description, required in required_vars:
        status = "🔴 REQUIRED" if required else "🟡 OPTIONAL"
        print(f"  {status} {var}")
        print(f"    └─ {description}")

    print()
    print("🎯 RAILWAY DEPLOYMENT CHECKLIST:")
    print("✅ Set TILORES_GRAPHQL_API_URL in Railway dashboard")
    print("✅ Set TILORES_CLIENT_ID in Railway dashboard")
    print("✅ Set TILORES_CLIENT_SECRET in Railway dashboard")
    print("✅ Set TILORES_OAUTH_TOKEN_URL in Railway dashboard")
    print("✅ Set OPENAI_API_KEY in Railway dashboard")
    print("✅ Verify latest commit deployed (PORT fix)")
    print("✅ Check Railway build logs for errors")
    print("✅ Check Railway application logs for startup messages")

def monitor_deployment_recovery(url="https://tilores-x.up.railway.app", max_attempts=10):
    """Monitor Railway deployment for recovery"""

    print("⏱️  MONITORING DEPLOYMENT RECOVERY")
    print("=" * 45)
    print(f"URL: {url}")
    print(f"Max attempts: {max_attempts}")
    print(f"Check interval: 30 seconds")
    print()

    for attempt in range(1, max_attempts + 1):
        print(f"🔍 Attempt {attempt}/{max_attempts} - {datetime.now().strftime('%H:%M:%S')}")

        try:
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ DEPLOYMENT RECOVERED!")
                print(f"Health check: {response.status_code}")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"❌ Still failing: {response.status_code}")
        except Exception as e:
            print(f"❌ Still failing: {str(e)}")

        if attempt < max_attempts:
            print("⏳ Waiting 30 seconds before next check...")
            time.sleep(30)
        print()

    print("⚠️  Deployment did not recover within monitoring period")
    return False

if __name__ == "__main__":
    print("🚀 RAILWAY DEPLOYMENT TROUBLESHOOTING STARTED")
    print("=" * 70)

    # Test current deployment status
    results = test_railway_endpoint()

    # Analyze issues
    analyze_deployment_issues(results)

    # Show environment requirements
    check_railway_environment_requirements()

    print("\n" + "=" * 70)
    print("📋 TROUBLESHOOTING SUMMARY")
    print("=" * 70)

    # Determine if monitoring is needed
    working_endpoints = [ep for ep, result in results.items()
                        if isinstance(result, dict) and result.get("success")]

    if not working_endpoints:
        print("🚨 DEPLOYMENT CURRENTLY FAILING")
        print("✅ PORT fix has been deployed to GitHub")
        print("✅ Railway should automatically redeploy")
        print()

        monitor_choice = input("🔍 Monitor for deployment recovery? (y/n): ").lower().strip()
        if monitor_choice == 'y':
            print()
            monitor_deployment_recovery()
    else:
        print("✅ DEPLOYMENT APPEARS TO BE WORKING")
        print("🎯 Ready for production use")

    print("\n🔗 Railway Dashboard: https://railway.app/dashboard")
    print("📊 Check deployment logs for detailed information")
