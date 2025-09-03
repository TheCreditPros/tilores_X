#!/usr/bin/env python3
"""
Test script to verify all Tilores models work correctly
Tests the exact models configured in the Tilores API
"""

import requests
import json
import time
from datetime import datetime

class TiloresModelTester:
    def __init__(self):
        self.api_url = "http://localhost:8080"
        self.test_query = "What is the account status for e.j.price1986@gmail.com?"
        self.models = [
            # OpenAI models
            "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo",
            # Google Gemini models
            "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp", "gemini-2.5-flash",
            # Groq models
            "llama-3.3-70b-versatile", "deepseek-r1-distill-llama-70b"
        ]

    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def test_model(self, model: str):
        """Test a specific model"""
        self.log(f"🧪 Testing model: {model}")

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": self.test_query}
            ],
            "temperature": 0.7
        }

        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            end_time = time.time()

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                # Check for expected content
                has_active = "Active" in content
                has_esteban = "Esteban" in content
                response_time = end_time - start_time

                if has_active and has_esteban:
                    self.log(f"✅ {model}: SUCCESS ({response_time:.1f}s) - Valid Tilores response")
                    return True, response_time, len(content)
                else:
                    self.log(f"⚠️ {model}: PARTIAL ({response_time:.1f}s) - Response missing expected content")
                    self.log(f"   Content preview: {content[:100]}...")
                    return False, response_time, len(content)
            else:
                self.log(f"❌ {model}: FAILED - HTTP {response.status_code}")
                self.log(f"   Error: {response.text}")
                return False, 0, 0

        except Exception as e:
            self.log(f"❌ {model}: ERROR - {e}")
            return False, 0, 0

    def test_api_health(self):
        """Test API health"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Tilores API is healthy")
                return True
            else:
                self.log(f"❌ Tilores API health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Tilores API not accessible: {e}")
            return False

    def test_webhook(self):
        """Test rating webhook"""
        try:
            payload = {
                "model": "gpt-4o-mini",
                "rating": "up",
                "tags": ["test"],
                "timestamp": datetime.now().isoformat()
            }

            response = requests.post(
                f"{self.api_url}/webhooks/openwebui-rating",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "received":
                    self.log("✅ Rating webhook is working")
                    return True

            self.log(f"⚠️ Rating webhook responded but format unexpected: {response.status_code}")
            return False

        except Exception as e:
            self.log(f"❌ Rating webhook test failed: {e}")
            return False

    def run_comprehensive_test(self):
        """Run all tests"""
        self.log("🚀 Starting Tilores Model Comprehensive Test")
        self.log("=" * 60)

        # Test API health
        if not self.test_api_health():
            self.log("❌ API not healthy, aborting tests")
            return False

        # Test webhook
        webhook_ok = self.test_webhook()

        # Test all models
        results = {}
        total_time = 0
        total_chars = 0

        for model in self.models:
            success, response_time, char_count = self.test_model(model)
            results[model] = {
                "success": success,
                "response_time": response_time,
                "char_count": char_count
            }
            if success:
                total_time += response_time
                total_chars += char_count

        # Summary
        successful_models = [m for m, r in results.items() if r["success"]]

        self.log("\n" + "=" * 60)
        self.log("📊 TILORES MODEL TEST SUMMARY")
        self.log("=" * 60)

        self.log(f"✅ API Health: {'OK' if True else 'FAILED'}")
        self.log(f"✅ Webhook: {'OK' if webhook_ok else 'FAILED'}")
        self.log(f"✅ Models Tested: {len(self.models)}")
        self.log(f"✅ Models Working: {len(successful_models)}")

        if successful_models:
            avg_time = total_time / len(successful_models)
            avg_chars = total_chars / len(successful_models)
            self.log(f"📊 Average Response Time: {avg_time:.1f}s")
            self.log(f"📊 Average Response Length: {avg_chars} characters")

            self.log(f"\n🎯 Working Models:")
            for model in successful_models:
                r = results[model]
                self.log(f"   ✅ {model}: {r['response_time']:.1f}s, {r['char_count']} chars")

        failed_models = [m for m, r in results.items() if not r["success"]]
        if failed_models:
            self.log(f"\n❌ Failed Models:")
            for model in failed_models:
                self.log(f"   ❌ {model}")

        # Open WebUI Configuration
        self.log(f"\n🔧 OPEN WEBUI CONFIGURATION")
        self.log("=" * 60)
        self.log("Use these exact model configurations in Open WebUI:")
        self.log("")

        for i, model in enumerate(self.models, 1):
            status = "✅ WORKING" if model in successful_models else "❌ FAILED"
            self.log(f"Model {i}: {model} ({status})")
            self.log(f"  Name: {model}")
            self.log(f"  Display Name: Tilores {model.upper()}")
            self.log(f"  Base URL: http://host.docker.internal:8080")
            self.log(f"  API Key: dummy")
            self.log("")

        if len(successful_models) == len(self.models):
            self.log("🎉 ALL TILORES MODELS ARE WORKING!")
            self.log("🌐 Open WebUI Setup: http://localhost:3000")
            self.log("📋 Follow: TILORES_OPENWEBUI_SETUP.md")
            return True
        else:
            self.log(f"⚠️ {len(failed_models)} models failed. Check the API configuration.")
            return False

if __name__ == "__main__":
    tester = TiloresModelTester()
    success = tester.run_comprehensive_test()

    if success:
        print(f"\n🎊 SUCCESS! All Tilores models are ready for Open WebUI!")
    else:
        print(f"\n⚠️ Some issues detected. Check the results above.")
