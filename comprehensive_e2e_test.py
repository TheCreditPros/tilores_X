#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for Tilores API
Tests all functionality before deployment
"""

import requests
import json
import time
import sys
from datetime import datetime
# Removed unused imports

class ComprehensiveE2ETest:
    def __init__(self):
        self.base_url = "http://localhost:8080"
        self.test_results = []
        self.start_time = datetime.now()

    def log_test(self, test_name: str, status: str, details: str = "", duration: float = 0):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "duration": f"{duration:.3f}s",
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)

        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status} ({duration:.3f}s)")
        if details:
            print(f"   {details}")

    def test_health_endpoints(self):
        """Test basic health endpoints"""
        test_start = time.time()

        try:
            # Test main health endpoint
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_test("Health Endpoint", "PASS", "API is healthy", time.time() - test_start)
                else:
                    self.log_test("Health Endpoint", "FAIL", f"Unexpected response: {data}", time.time() - test_start)
            else:
                self.log_test("Health Endpoint", "FAIL", f"Status: {response.status_code}", time.time() - test_start)
        except Exception as e:
            self.log_test("Health Endpoint", "FAIL", f"Exception: {str(e)}", time.time() - test_start)

    def test_models_endpoints(self):
        """Test models discovery endpoints"""
        test_start = time.time()

        # Test /api/models endpoint
        try:
            response = requests.get(f"{self.base_url}/api/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                if len(models) == 9:
                    self.log_test("API Models Endpoint", "PASS", f"Found {len(models)} models", time.time() - test_start)
                else:
                    self.log_test("API Models Endpoint", "FAIL", f"Expected 9 models, got {len(models)}", time.time() - test_start)
            else:
                self.log_test("API Models Endpoint", "FAIL", f"Status: {response.status_code}", time.time() - test_start)
        except Exception as e:
            self.log_test("API Models Endpoint", "FAIL", f"Exception: {str(e)}", time.time() - test_start)

        # Test /v1/models endpoint
        test_start = time.time()
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                if len(models) == 9:
                    # Verify model categories
                    openai_models = [m for m in models if m.get("owned_by") == "tilores-openai"]
                    google_models = [m for m in models if m.get("owned_by") == "tilores-google"]
                    groq_models = [m for m in models if m.get("owned_by") == "tilores-groq"]

                    if len(openai_models) == 3 and len(google_models) == 4 and len(groq_models) == 2:
                        self.log_test("V1 Models Endpoint", "PASS",
                                    f"OpenAI: {len(openai_models)}, Google: {len(google_models)}, Groq: {len(groq_models)}",
                                    time.time() - test_start)
                    else:
                        self.log_test("V1 Models Endpoint", "FAIL",
                                    f"Model distribution incorrect: OpenAI={len(openai_models)}, Google={len(google_models)}, Groq={len(groq_models)}",
                                    time.time() - test_start)
                else:
                    self.log_test("V1 Models Endpoint", "FAIL", f"Expected 9 models, got {len(models)}", time.time() - test_start)
            else:
                self.log_test("V1 Models Endpoint", "FAIL", f"Status: {response.status_code}", time.time() - test_start)
        except Exception as e:
            self.log_test("V1 Models Endpoint", "FAIL", f"Exception: {str(e)}", time.time() - test_start)

    def test_chat_completions_all_providers(self):
        """Test chat completions with all provider models"""
        models_to_test = [
            # OpenAI models
            ("gpt-4o-mini", "OpenAI"),
            ("gpt-4o", "OpenAI"),
            ("gpt-3.5-turbo", "OpenAI"),
            # Google models
            ("gemini-1.5-flash", "Google"),
            ("gemini-1.5-pro", "Google"),
            ("gemini-2.0-flash-exp", "Google"),
            ("gemini-2.5-flash", "Google"),
            # Groq models
            ("llama-3.3-70b-versatile", "Groq"),
            ("deepseek-r1-distill-llama-70b", "Groq")
        ]

        for model_id, provider in models_to_test:
            test_start = time.time()
            try:
                payload = {
                    "model": model_id,
                    "messages": [{"role": "user", "content": "Hello, test message for model validation"}],
                    "max_tokens": 50,
                    "temperature": 0.7
                }

                response = requests.post(f"{self.base_url}/v1/chat/completions",
                                       json=payload, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0].get("message", {}).get("content", "")
                        if content and len(content) > 0:
                            self.log_test(f"Chat - {model_id}", "PASS",
                                        f"{provider} model responded ({len(content)} chars)",
                                        time.time() - test_start)
                        else:
                            self.log_test(f"Chat - {model_id}", "FAIL",
                                        f"{provider} model returned empty response",
                                        time.time() - test_start)
                    else:
                        self.log_test(f"Chat - {model_id}", "FAIL",
                                    f"{provider} model response missing choices",
                                    time.time() - test_start)
                else:
                    self.log_test(f"Chat - {model_id}", "FAIL",
                                f"{provider} model returned status {response.status_code}",
                                time.time() - test_start)
            except Exception as e:
                self.log_test(f"Chat - {model_id}", "FAIL",
                            f"{provider} model exception: {str(e)}",
                            time.time() - test_start)

    def test_webhook_endpoints(self):
        """Test webhook endpoints"""
        test_start = time.time()

        # Test webhook health
        try:
            response = requests.get(f"{self.base_url}/webhooks/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "webhooks" in data and "openwebui_rating" in data["webhooks"]:
                    self.log_test("Webhook Health", "PASS", "All webhook endpoints available", time.time() - test_start)
                else:
                    self.log_test("Webhook Health", "FAIL", "Missing webhook endpoints", time.time() - test_start)
            else:
                self.log_test("Webhook Health", "FAIL", f"Status: {response.status_code}", time.time() - test_start)
        except Exception as e:
            self.log_test("Webhook Health", "FAIL", f"Exception: {str(e)}", time.time() - test_start)

        # Test rating webhook
        test_start = time.time()
        try:
            payload = {
                "model": "gpt-4o-mini",
                "rating": "up",
                "chat_id": "test-chat-123",
                "message_id": "test-msg-456",
                "user_id": "test-user-789"
            }

            response = requests.post(f"{self.base_url}/webhooks/openwebui-rating",
                                   json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "received":
                    self.log_test("Rating Webhook", "PASS", "Rating webhook processed successfully", time.time() - test_start)
                else:
                    self.log_test("Rating Webhook", "FAIL", f"Unexpected response: {data}", time.time() - test_start)
            else:
                self.log_test("Rating Webhook", "FAIL", f"Status: {response.status_code}", time.time() - test_start)
        except Exception as e:
            self.log_test("Rating Webhook", "FAIL", f"Exception: {str(e)}", time.time() - test_start)

    def test_customer_analysis_functionality(self):
        """Test core customer analysis functionality"""
        test_start = time.time()

        try:
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Analyze customer e.j.price1986@gmail.com"}],
                "max_tokens": 500,
                "temperature": 0.7
            }

            response = requests.post(f"{self.base_url}/v1/chat/completions",
                                   json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                # Check for key analysis components (more flexible)
                analysis_indicators = [
                    "customer",
                    "analysis",
                    "financial",
                    "data",
                    "dc93a2cd-de0a-444f-ad47-3003ba998cd3"  # Entity ID
                ]

                found_indicators = [indicator for indicator in analysis_indicators if indicator.lower() in content.lower()]

                if len(found_indicators) >= 3 and len(content) > 100:
                    self.log_test("Customer Analysis", "PASS",
                                f"Found {len(found_indicators)}/5 analysis components, {len(content)} chars",
                                time.time() - test_start)
                else:
                    self.log_test("Customer Analysis", "FAIL",
                                f"Only found {len(found_indicators)}/5 analysis components: {found_indicators}, content length: {len(content)}",
                                time.time() - test_start)
            else:
                self.log_test("Customer Analysis", "FAIL", f"Status: {response.status_code}", time.time() - test_start)
        except Exception as e:
            self.log_test("Customer Analysis", "FAIL", f"Exception: {str(e)}", time.time() - test_start)

    def test_error_handling(self):
        """Test error handling and edge cases"""
        test_start = time.time()

        # Test invalid model
        try:
            payload = {
                "model": "invalid-model-name",
                "messages": [{"role": "user", "content": "Test message"}],
                "max_tokens": 50
            }

            response = requests.post(f"{self.base_url}/v1/chat/completions",
                                   json=payload, timeout=30)

            # Should still work (fallback to default)
            if response.status_code == 200:
                self.log_test("Invalid Model Handling", "PASS", "Graceful fallback to default model", time.time() - test_start)
            else:
                self.log_test("Invalid Model Handling", "WARN", f"Status: {response.status_code}", time.time() - test_start)
        except Exception as e:
            self.log_test("Invalid Model Handling", "FAIL", f"Exception: {str(e)}", time.time() - test_start)

        # Test malformed request
        test_start = time.time()
        try:
            payload = {"invalid": "request"}

            response = requests.post(f"{self.base_url}/v1/chat/completions",
                                   json=payload, timeout=10)

            # Should return error but not crash
            if response.status_code in [400, 422]:
                self.log_test("Malformed Request Handling", "PASS", "Proper error response", time.time() - test_start)
            else:
                self.log_test("Malformed Request Handling", "WARN", f"Unexpected status: {response.status_code}", time.time() - test_start)
        except Exception as e:
            self.log_test("Malformed Request Handling", "FAIL", f"Exception: {str(e)}", time.time() - test_start)

    def run_all_tests(self):
        """Run all test suites"""
        print("🧪 Starting Comprehensive End-to-End Testing")
        print("=" * 60)

        # Run test suites
        self.test_health_endpoints()
        self.test_models_endpoints()
        self.test_webhook_endpoints()
        self.test_chat_completions_all_providers()
        self.test_customer_analysis_functionality()
        self.test_error_handling()

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        warned_tests = len([t for t in self.test_results if t["status"] == "WARN"])

        total_duration = (datetime.now() - self.start_time).total_seconds()

        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warned_tests}")
        print(f"🕒 Total Duration: {total_duration:.2f}s")
        print(f"📈 Success Rate: {(passed_tests / total_tests) * 100:.1f}%")

        # Save detailed results
        results_file = f"e2e_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "warnings": warned_tests,
                    "success_rate": (passed_tests / total_tests) * 100,
                    "total_duration": total_duration,
                    "timestamp": datetime.now().isoformat()
                },
                "detailed_results": self.test_results
            }, f, indent=2)

        print(f"📄 Detailed results saved to: {results_file}")

        # Determine overall status
        if failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED - READY FOR DEPLOYMENT!")
            return True
        else:
            print(f"\n⚠️  {failed_tests} TESTS FAILED - REVIEW REQUIRED BEFORE DEPLOYMENT")
            return False

if __name__ == "__main__":
    tester = ComprehensiveE2ETest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
