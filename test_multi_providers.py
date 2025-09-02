#!/usr/bin/env python3
"""
Test script for multiple AI providers (Anthropic, Google Gemini, etc.)
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_anthropic():
    """Test Anthropic Claude models"""
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        print("🧪 TESTING ANTHROPIC CLAUDE MODELS")
        print("=" * 50)

        # Test Claude 3.5 Sonnet
        print("\n📊 Testing Claude 3.5 Sonnet...")
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": "What is Esteban Price's current credit score from each bureau? Provide a brief analysis."}
            ]
        )

        print(f"✅ Claude 3.5 Sonnet Response:")
        print(f"Content: {response.content[0].text[:200]}...")
        print(f"Usage: {response.usage}")

        return True

    except ImportError:
        print("❌ Anthropic library not installed")
        return False
    except Exception as e:
        print(f"❌ Anthropic test failed: {e}")
        return False

def test_google_gemini():
    """Test Google Gemini models"""
    try:
        import google.generativeai as genai

        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        print("\n🧪 TESTING GOOGLE GEMINI MODELS")
        print("=" * 50)

        # Test Gemini 1.5 Flash
        print("\n📊 Testing Gemini 1.5 Flash...")
        model = genai.GenerativeModel('gemini-1.5-flash')

        response = model.generate_content(
            "What is Esteban Price's current credit score from each bureau? Provide a brief analysis."
        )

        print(f"✅ Gemini 1.5 Flash Response:")
        print(f"Content: {response.text[:200]}...")
        print(f"Usage: {response.usage_metadata}")

        return True

    except ImportError:
        print("❌ Google Generative AI library not installed")
        return False
    except Exception as e:
        print(f"❌ Google Gemini test failed: {e}")
        return False

def main():
    """Run all provider tests"""
    print("🚀 MULTI-PROVIDER AI TESTING")
    print("=" * 60)

    results = {}

    # Test Anthropic
    results['anthropic'] = test_anthropic()

    # Test Google Gemini
    results['gemini'] = test_google_gemini()

    # Summary
    print("\n📋 TEST RESULTS SUMMARY")
    print("=" * 30)
    for provider, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{provider.upper()}: {status}")

    total_tests = len(results)
    passed_tests = sum(results.values())

    print(f"\n🎯 OVERALL: {passed_tests}/{total_tests} providers working")

    if passed_tests == total_tests:
        print("🎉 All providers are working correctly!")
    else:
        print("⚠️  Some providers need attention")

if __name__ == "__main__":
    main()
