#!/usr/bin/env python3
"""
Test script to verify Salesforce status query fix
"""

import requests
import json

def test_status_query():
    """Test the status query functionality"""

    # Test data
    test_query = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "What is the account status for e.j.price1986@gmail.com?"
            }
        ],
        "temperature": 0.7
    }

    try:
        # Make request to local server
        response = requests.post(
            "http://localhost:8080/v1/chat/completions",
            json=test_query,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"\n✅ Success! Response content:\n{content}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Salesforce status query...")
    success = test_status_query()
    print(f"\n{'✅ Test PASSED' if success else '❌ Test FAILED'}")
