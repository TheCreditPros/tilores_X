#!/usr/bin/env python3
"""
Test script to mock Agenta.ai requests against LOCAL server
"""

import requests
import json
import time
import subprocess
import os
import signal

def start_local_server():
    """Start the local FastAPI server"""
    print("🚀 Starting local server...")

    # Start server in background
    process = subprocess.Popen(
        ["python3", "direct_credit_api_with_phone.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    time.sleep(3)

    # Test if server is running
    try:
        response = requests.get("http://localhost:8080/v1", timeout=5)
        if response.status_code == 200:
            print("✅ Local server started successfully!")
            return process
        else:
            print(f"❌ Server responded with {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return None

def test_agenta_mock_request():
    """Mock the exact request that AsyncOpenAI would send"""

    # This matches what we saw in Railway logs (292 bytes)
    agenta_request = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "Hello, this is a test from Agenta.ai"
            }
        ],
        "temperature": 0.7,
        "max_tokens": None,
        "stream": False,
        "stop": None,
        "presence_penalty": None,
        "frequency_penalty": None,
        "top_p": None,
        "n": 1,
        "user": None
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "AsyncOpenAI/Python 1.102.0",
        "Accept": "application/json",
        "Authorization": "Bearer fake-key-for-testing"
    }

    print("🔍 Testing Agenta.ai-style request against LOCAL server:")
    print(f"📦 Request size: {len(json.dumps(agenta_request))} bytes")
    print(f"📋 Payload preview: {json.dumps(agenta_request, indent=2)[:200]}...")

    try:
        response = requests.post(
            "http://localhost:8080/v1/chat/completions",
            headers=headers,
            json=agenta_request,
            timeout=30
        )

        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📏 Response Size: {len(response.content)} bytes")

        if response.status_code == 200:
            print("🎉 SUCCESS! Local request worked!")
            result = response.json()
            print(f"🤖 Model: {result.get('model')}")
            print(f"💬 Response preview: {result.get('choices', [{}])[0].get('message', {}).get('content', '')[:100]}...")
            return True
        else:
            print(f"❌ FAILED with {response.status_code}")
            print(f"🚨 Error: {response.text}")
            return False

    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

def test_minimal_request():
    """Test with minimal request"""

    minimal_request = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "test"}]
    }

    print("\n🔍 Testing minimal request against LOCAL server:")

    try:
        response = requests.post(
            "http://localhost:8080/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=minimal_request,
            timeout=30
        )

        print(f"✅ Response Status: {response.status_code}")
        if response.status_code != 200:
            print(f"🚨 Error: {response.text}")
            return False
        else:
            print("🎉 Minimal request worked!")
            return True

    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    print("🧪 LOCAL AGENTA.AI REQUEST MOCK TEST")
    print("=" * 60)

    # Start local server
    server_process = start_local_server()

    if not server_process:
        print("❌ Could not start local server. Exiting.")
        exit(1)

    try:
        # Test 1: Full AsyncOpenAI-style request
        success1 = test_agenta_mock_request()

        # Test 2: Minimal request
        success2 = test_minimal_request()

        print("\n" + "=" * 60)
        if success1 and success2:
            print("🎉 ALL TESTS PASSED! The fix works locally!")
            print("🚀 Ready to deploy to Railway!")
        else:
            print("❌ Some tests failed. Check the output above.")

    finally:
        # Clean up: kill the server
        print("\n🛑 Stopping local server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Local server stopped.")
