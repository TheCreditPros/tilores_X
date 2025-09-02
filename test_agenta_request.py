#!/usr/bin/env python3
"""
Test script to mock the exact request that Agenta.ai sends
Based on Railway logs showing AsyncOpenAI/Python 1.102.0 client
"""

import requests
import json

def test_agenta_mock_request():
    """Mock the exact request structure that AsyncOpenAI would send"""

    # This is what AsyncOpenAI typically sends
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

    print("🔍 Testing with Agenta.ai-style request:")
    print(f"📦 Request size: {len(json.dumps(agenta_request))} bytes")
    print(f"🔧 Headers: {headers}")
    print(f"📋 Payload: {json.dumps(agenta_request, indent=2)}")

    try:
        response = requests.post(
            "https://tilores-x.up.railway.app/v1/chat/completions",
            headers=headers,
            json=agenta_request,
            timeout=30
        )

        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📏 Response Size: {len(response.content)} bytes")

        if response.status_code == 200:
            print("🎉 SUCCESS! Request worked!")
            result = response.json()
            print(f"🤖 Model: {result.get('model')}")
            print(f"💬 Response: {result.get('choices', [{}])[0].get('message', {}).get('content', '')[:100]}...")
        else:
            print(f"❌ FAILED with {response.status_code}")
            print(f"🚨 Error: {response.text}")

    except Exception as e:
        print(f"💥 Exception: {e}")

def test_minimal_request():
    """Test with minimal request to isolate issues"""

    minimal_request = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "test"}]
    }

    print("\n🔍 Testing with minimal request:")
    print(f"📋 Payload: {json.dumps(minimal_request, indent=2)}")

    try:
        response = requests.post(
            "https://tilores-x.up.railway.app/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=minimal_request,
            timeout=30
        )

        print(f"✅ Response Status: {response.status_code}")
        if response.status_code != 200:
            print(f"🚨 Error: {response.text}")
        else:
            print("🎉 Minimal request worked!")

    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    print("🧪 AGENTA.AI REQUEST MOCK TEST")
    print("=" * 50)

    # Test 1: Full AsyncOpenAI-style request
    test_agenta_mock_request()

    # Test 2: Minimal request
    test_minimal_request()

    print("\n" + "=" * 50)
    print("🔍 Check Railway logs for detailed debug output!")
