#!/usr/bin/env python3
"""
Simple test for multiple AI providers using existing LangChain infrastructure
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_providers():
    """Test different AI providers"""
    print("🚀 TESTING MULTIPLE AI PROVIDERS")
    print("=" * 50)

    # Test query
    test_query = "What is Esteban Price's current credit score from each bureau? Provide a brief analysis."

    results = {}

    # Test OpenAI (we know this works)
    print("\n📊 Testing OpenAI GPT-4o-mini...")
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": test_query}],
            max_tokens=500
        )

        print(f"✅ OpenAI Response: {response.choices[0].message.content[:100]}...")
        results['openai'] = True

    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        results['openai'] = False

    # Test Anthropic Claude
    print("\n📊 Testing Anthropic Claude...")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": test_query}]
        )

        print(f"✅ Anthropic Response: {response.content[0].text[:100]}...")
        results['anthropic'] = True

    except Exception as e:
        print(f"❌ Anthropic test failed: {e}")
        results['anthropic'] = False

    # Test Google Gemini (if available)
    print("\n📊 Testing Google Gemini...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(test_query)

        print(f"✅ Gemini Response: {response.text[:100]}...")
        results['gemini'] = True

    except ImportError:
        print("❌ Google Generative AI library not installed")
        results['gemini'] = False
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        results['gemini'] = False

    # Summary
    print("\n📋 PROVIDER TEST RESULTS")
    print("=" * 30)
    for provider, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{provider.upper()}: {status}")

    total_tests = len(results)
    passed_tests = sum(results.values())

    print(f"\n🎯 OVERALL: {passed_tests}/{total_tests} providers working")

    return results

if __name__ == "__main__":
    test_providers()
