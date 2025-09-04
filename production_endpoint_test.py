#!/usr/bin/env python3
"""
Production Endpoint & Webhook Testing Suite
==========================================

Comprehensive testing of all production endpoints and webhook integrations.
Tests both local (port 8080) and Railway production environments.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import concurrent.futures
import threading

class ProductionEndpointTester:
    def __init__(self):
        self.local_base_url = "http://127.0.0.1:8080"
        self.prod_base_url = "https://tilores-x.up.railway.app"
        self.openwebui_url = "https://tilores-x-ui.up.railway.app"

        self.test_results = []
        self.webhook_results = []

        # Test scenarios
        self.test_scenarios = [
            # Basic functionality tests
            {"name": "Health Check", "endpoint": "/health", "method": "GET"},
            {"name": "Root Endpoint", "endpoint": "/", "method": "GET"},
            {"name": "V1 Info", "endpoint": "/v1", "method": "GET"},
            {"name": "Models List", "endpoint": "/v1/models", "method": "GET"},

            # Chat completion tests
            {"name": "Simple Customer Query", "endpoint": "/v1/chat/completions", "method": "POST",
             "payload": {
                 "model": "gpt-4o-mini",
                 "messages": [{"role": "user", "content": "who is e.j.price1986@gmail.com"}],
                 "temperature": 0.7,
                 "max_tokens": 500
             }},

            {"name": "Credit Analysis Query", "endpoint": "/v1/chat/completions", "method": "POST",
             "payload": {
                 "model": "gpt-4o-mini",
                 "messages": [{"role": "user", "content": "credit analysis for e.j.price1986@gmail.com"}],
                 "temperature": 0.7,
                 "max_tokens": 1000
             }},

            {"name": "Account Status Query", "endpoint": "/v1/chat/completions", "method": "POST",
             "payload": {
                 "model": "gpt-4o-mini",
                 "messages": [{"role": "user", "content": "account status for e.j.price1986@gmail.com"}],
                 "temperature": 0.7,
                 "max_tokens": 300
             }},

            {"name": "Multi-Data Analysis", "endpoint": "/v1/chat/completions", "method": "POST",
             "payload": {
                 "model": "gpt-4o-mini",
                 "messages": [{"role": "user", "content": "comprehensive analysis for e.j.price1986@gmail.com"}],
                 "temperature": 0.7,
                 "max_tokens": 1500
             }},

            # Error handling tests
            {"name": "Empty Query Fix", "endpoint": "/v1/chat/completions", "method": "POST",
             "payload": {
                 "model": "gpt-4o-mini",
                 "messages": [{"role": "user", "content": ""}],
                 "temperature": 0.7,
                 "max_tokens": 100
             }},

            {"name": "Invalid Customer", "endpoint": "/v1/chat/completions", "method": "POST",
             "payload": {
                 "model": "gpt-4o-mini",
                 "messages": [{"role": "user", "content": "who is invalid@customer.com"}],
                 "temperature": 0.7,
                 "max_tokens": 300
             }},

            # Different model tests
            {"name": "GPT-4o Model", "endpoint": "/v1/chat/completions", "method": "POST",
             "payload": {
                 "model": "gpt-4o",
                 "messages": [{"role": "user", "content": "who is e.j.price1986@gmail.com"}],
                 "temperature": 0.7,
                 "max_tokens": 300
             }},

            {"name": "Gemini Model", "endpoint": "/v1/chat/completions", "method": "POST",
             "payload": {
                 "model": "gemini-1.5-flash",
                 "messages": [{"role": "user", "content": "who is e.j.price1986@gmail.com"}],
                 "temperature": 0.7,
                 "max_tokens": 300
             }},
        ]

        # Webhook test scenarios
        self.webhook_scenarios = [
            {"name": "Chat Log Webhook", "endpoint": "/webhook/chat-log", "method": "POST"},
            {"name": "Evaluation Webhook", "endpoint": "/webhook/evaluation", "method": "POST"},
            {"name": "Model Performance Webhook", "endpoint": "/webhook/model-performance", "method": "POST"},
            {"name": "Error Report Webhook", "endpoint": "/webhook/error-report", "method": "POST"},
            {"name": "System Health Webhook", "endpoint": "/webhook/system-health", "method": "POST"},
        ]

    def test_endpoint(self, base_url: str, scenario: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Test a single endpoint"""
        start_time = time.time()

        try:
            url = f"{base_url}{scenario['endpoint']}"
            method = scenario['method']
            payload = scenario.get('payload')

            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=45
                )
            else:
                raise ValueError(f"Unsupported method: {method}")

            end_time = time.time()
            response_time = end_time - start_time

            # Parse response
            try:
                response_data = response.json()
            except:
                response_data = {"raw_text": response.text}

            result = {
                "scenario": scenario['name'],
                "environment": environment,
                "endpoint": scenario['endpoint'],
                "method": method,
                "status_code": response.status_code,
                "success": 200 <= response.status_code < 300,
                "response_time": response_time,
                "response_size": len(response.text),
                "timestamp": datetime.now().isoformat(),
                "response_data": response_data
            }

            # Additional validation for specific endpoints
            if scenario['endpoint'] == "/v1/models":
                models = response_data.get("data", [])
                result["models_count"] = len(models)
                result["has_openai_models"] = any("gpt" in model.get("id", "") for model in models)
                result["has_gemini_models"] = any("gemini" in model.get("id", "") for model in models)
                result["has_groq_models"] = any("llama" in model.get("id", "") or "deepseek" in model.get("id", "") for model in models)

            elif scenario['endpoint'] == "/v1/chat/completions":
                choices = response_data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    result["response_length"] = len(content)
                    result["has_customer_data"] = "e.j.price1986@gmail.com" in content or "esteban" in content.lower()
                    result["is_helpful_message"] = "Please provide a question" in content
                    result["response_preview"] = content[:200] + "..." if len(content) > 200 else content

            return result

        except requests.exceptions.Timeout:
            return {
                "scenario": scenario['name'],
                "environment": environment,
                "endpoint": scenario['endpoint'],
                "success": False,
                "error": "Request timeout",
                "response_time": 30.0,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "scenario": scenario['name'],
                "environment": environment,
                "endpoint": scenario['endpoint'],
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }

    def test_webhook(self, base_url: str, scenario: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Test webhook endpoints"""
        start_time = time.time()

        # Sample webhook payloads
        webhook_payloads = {
            "/webhook/chat-log": {
                "conversation_id": "test-conv-123",
                "user_message": "who is e.j.price1986@gmail.com",
                "assistant_response": "Customer profile data...",
                "model": "gpt-4o-mini",
                "response_time": 2.5,
                "timestamp": datetime.now().isoformat()
            },
            "/webhook/evaluation": {
                "conversation_id": "test-conv-123",
                "rating": 5,
                "feedback": "Excellent response quality",
                "model": "gpt-4o-mini",
                "timestamp": datetime.now().isoformat()
            },
            "/webhook/model-performance": {
                "model": "gpt-4o-mini",
                "avg_response_time": 3.2,
                "success_rate": 0.95,
                "total_requests": 100,
                "timestamp": datetime.now().isoformat()
            },
            "/webhook/error-report": {
                "error_type": "timeout",
                "error_message": "Request timeout after 30s",
                "endpoint": "/v1/chat/completions",
                "model": "gpt-4o",
                "timestamp": datetime.now().isoformat()
            },
            "/webhook/system-health": {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "active_connections": 12,
                "cache_hit_rate": 0.85,
                "timestamp": datetime.now().isoformat()
            }
        }

        try:
            url = f"{base_url}{scenario['endpoint']}"
            payload = webhook_payloads.get(scenario['endpoint'], {"test": True})

            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15
            )

            end_time = time.time()
            response_time = end_time - start_time

            try:
                response_data = response.json()
            except:
                response_data = {"raw_text": response.text}

            return {
                "scenario": scenario['name'],
                "environment": environment,
                "endpoint": scenario['endpoint'],
                "status_code": response.status_code,
                "success": 200 <= response.status_code < 300,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
                "response_data": response_data
            }

        except Exception as e:
            return {
                "scenario": scenario['name'],
                "environment": environment,
                "endpoint": scenario['endpoint'],
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }

    def test_openwebui_integration(self) -> Dict[str, Any]:
        """Test Open WebUI integration"""
        try:
            # Test Open WebUI health
            response = requests.get(f"{self.openwebui_url}/health", timeout=10)

            return {
                "scenario": "Open WebUI Health",
                "environment": "production",
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": 1.0,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "scenario": "Open WebUI Health",
                "environment": "production",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def run_comprehensive_tests(self):
        """Run all tests comprehensively"""
        print("🚀 PRODUCTION ENDPOINT & WEBHOOK TESTING SUITE")
        print("=" * 60)

        environments = [
            ("Local", self.local_base_url),
            ("Production", self.prod_base_url)
        ]

        # Test API endpoints
        print("\n📡 Testing API Endpoints...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []

            for env_name, base_url in environments:
                for scenario in self.test_scenarios:
                    future = executor.submit(self.test_endpoint, base_url, scenario, env_name)
                    futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                self.test_results.append(result)

                status_emoji = "✅" if result.get("success", False) else "❌"
                env = result.get("environment", "Unknown")
                scenario = result.get("scenario", "Unknown")
                response_time = result.get("response_time", 0)

                print(f"{status_emoji} {env}: {scenario} ({response_time:.2f}s)")

        # Test webhook endpoints
        print("\n🔗 Testing Webhook Endpoints...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = []

            for env_name, base_url in environments:
                for scenario in self.webhook_scenarios:
                    future = executor.submit(self.test_webhook, base_url, scenario, env_name)
                    futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                self.webhook_results.append(result)

                status_emoji = "✅" if result.get("success", False) else "❌"
                env = result.get("environment", "Unknown")
                scenario = result.get("scenario", "Unknown")
                response_time = result.get("response_time", 0)

                print(f"{status_emoji} {env}: {scenario} ({response_time:.2f}s)")

        # Test Open WebUI integration
        print("\n🌐 Testing Open WebUI Integration...")
        openwebui_result = self.test_openwebui_integration()
        self.test_results.append(openwebui_result)

        status_emoji = "✅" if openwebui_result.get("success", False) else "❌"
        print(f"{status_emoji} Open WebUI: {openwebui_result.get('scenario', 'Unknown')}")

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        all_results = self.test_results + self.webhook_results

        # Overall statistics
        total_tests = len(all_results)
        successful_tests = len([r for r in all_results if r.get("success", False)])
        success_rate = successful_tests / total_tests if total_tests > 0 else 0

        # Environment breakdown
        env_stats = {}
        for result in all_results:
            env = result.get("environment", "Unknown")
            if env not in env_stats:
                env_stats[env] = {"total": 0, "successful": 0, "avg_response_time": 0}

            env_stats[env]["total"] += 1
            if result.get("success", False):
                env_stats[env]["successful"] += 1

        # Calculate average response times
        for env in env_stats:
            env_results = [r for r in all_results if r.get("environment") == env and "response_time" in r]
            if env_results:
                env_stats[env]["avg_response_time"] = sum(r["response_time"] for r in env_results) / len(env_results)

        # Endpoint type breakdown
        api_results = [r for r in self.test_results if "/v1/" in r.get("endpoint", "")]
        webhook_results = [r for r in self.webhook_results]

        # Model testing results
        model_results = [r for r in self.test_results if r.get("endpoint") == "/v1/chat/completions"]

        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": success_rate,
                "timestamp": datetime.now().isoformat()
            },
            "environment_performance": {
                env: {
                    "success_rate": stats["successful"] / stats["total"] if stats["total"] > 0 else 0,
                    "avg_response_time": stats["avg_response_time"],
                    "total_tests": stats["total"]
                }
                for env, stats in env_stats.items()
            },
            "endpoint_analysis": {
                "api_endpoints": {
                    "total": len(api_results),
                    "successful": len([r for r in api_results if r.get("success", False)]),
                    "success_rate": len([r for r in api_results if r.get("success", False)]) / len(api_results) if api_results else 0
                },
                "webhook_endpoints": {
                    "total": len(webhook_results),
                    "successful": len([r for r in webhook_results if r.get("success", False)]),
                    "success_rate": len([r for r in webhook_results if r.get("success", False)]) / len(webhook_results) if webhook_results else 0
                }
            },
            "model_testing": {
                "total_model_tests": len(model_results),
                "successful_model_tests": len([r for r in model_results if r.get("success", False)]),
                "models_tested": list(set([r.get("response_data", {}).get("model", "unknown") for r in model_results])),
                "avg_response_time": sum(r.get("response_time", 0) for r in model_results) / len(model_results) if model_results else 0
            },
            "critical_validations": {
                "empty_query_fix": any(r.get("is_helpful_message", False) for r in model_results),
                "customer_data_retrieval": any(r.get("has_customer_data", False) for r in model_results),
                "models_endpoint_working": any(r.get("models_count", 0) > 0 for r in self.test_results),
                "multi_provider_support": any(r.get("has_openai_models", False) and r.get("has_gemini_models", False) for r in self.test_results)
            },
            "detailed_results": all_results
        }

        return report

    def save_results(self, filename: str = None):
        """Save test results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"production_test_results_{timestamp}.json"

        report = self.generate_comprehensive_report()

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        return filename

def main():
    """Main execution function"""
    tester = ProductionEndpointTester()

    # Run comprehensive tests
    tester.run_comprehensive_tests()

    # Generate and display report
    report = tester.generate_comprehensive_report()

    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)

    summary = report["test_summary"]
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Success Rate: {summary['success_rate']:.2%}")

    print("\n🌍 Environment Performance:")
    for env, stats in report["environment_performance"].items():
        print(f"  {env}: {stats['success_rate']:.2%} success, {stats['avg_response_time']:.2f}s avg")

    print("\n📡 Endpoint Analysis:")
    api_stats = report["endpoint_analysis"]["api_endpoints"]
    webhook_stats = report["endpoint_analysis"]["webhook_endpoints"]
    print(f"  API Endpoints: {api_stats['success_rate']:.2%} ({api_stats['successful']}/{api_stats['total']})")
    print(f"  Webhook Endpoints: {webhook_stats['success_rate']:.2%} ({webhook_stats['successful']}/{webhook_stats['total']})")

    print("\n🤖 Model Testing:")
    model_stats = report["model_testing"]
    print(f"  Model Tests: {model_stats['successful_model_tests']}/{model_stats['total_model_tests']}")
    print(f"  Average Response Time: {model_stats['avg_response_time']:.2f}s")

    print("\n✅ Critical Validations:")
    validations = report["critical_validations"]
    for validation, status in validations.items():
        status_emoji = "✅" if status else "❌"
        print(f"  {status_emoji} {validation.replace('_', ' ').title()}")

    # Save detailed results
    filename = tester.save_results()
    print(f"\n📄 Detailed results saved to: {filename}")

    # Overall status
    overall_success = summary['success_rate'] >= 0.8
    status_emoji = "✅" if overall_success else "❌"
    print(f"\n{status_emoji} OVERALL STATUS: {'PRODUCTION READY' if overall_success else 'NEEDS ATTENTION'}")

if __name__ == "__main__":
    main()


