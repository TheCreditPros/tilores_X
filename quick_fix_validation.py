#!/usr/bin/env python3
"""
Quick Fix Validation
===================

Validate that the critical empty query fix is working properly.
"""

import requests

def test_empty_query_fix():
    """Test the empty query fix"""
    base_url = "http://127.0.0.1:8080"

    test_cases = [
        {"name": "Empty String", "content": ""},
        {"name": "Whitespace Only", "content": "   "},
        {"name": "Tab and Newlines", "content": "\t\n\r"},
        {"name": "Normal Query", "content": "who is e.j.price1986@gmail.com"},
    ]

    results = []

    for test_case in test_cases:
        try:
            response = requests.post(
                f"{base_url}/v1/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": test_case["content"]}],
                    "temperature": 0.7,
                    "max_tokens": 100
                },
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                results.append({
                    "test": test_case["name"],
                    "status": "SUCCESS",
                    "response": content[:100] + "..." if len(content) > 100 else content,
                    "is_helpful_message": "Please provide a question" in content
                })
            else:
                results.append({
                    "test": test_case["name"],
                    "status": "FAILED",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "is_helpful_message": False
                })

        except Exception as e:
            results.append({
                "test": test_case["name"],
                "status": "ERROR",
                "error": str(e),
                "is_helpful_message": False
            })

    return results

def main():
    print("🔍 QUICK FIX VALIDATION - Empty Query Handling")
    print("=" * 50)

    results = test_empty_query_fix()

    all_passed = True

    for result in results:
        status_emoji = "✅" if result["status"] == "SUCCESS" else "❌"
        print(f"{status_emoji} {result['test']}: {result['status']}")

        if result["status"] == "SUCCESS":
            if "Normal Query" in result["test"]:
                # Normal query should return customer data
                if "e.j.price1986@gmail.com" in result["response"]:
                    print("    ✅ Contains expected customer data")
                else:
                    print("    ⚠️  Missing customer data")
                    all_passed = False
            else:
                # Empty queries should return helpful message
                if result["is_helpful_message"]:
                    print("    ✅ Returns helpful message")
                else:
                    print("    ❌ Does not return helpful message")
                    all_passed = False
        else:
            print(f"    Error: {result.get('error', 'Unknown error')}")
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎯 ALL TESTS PASSED - Empty query fix is working correctly!")
        print("✅ Ready for production deployment")
    else:
        print("❌ Some tests failed - fix needs additional work")

    return all_passed

if __name__ == "__main__":
    main()
