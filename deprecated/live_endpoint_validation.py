#!/usr/bin/env python3
"""
Live Endpoint Validation - Production Deployment Check
Validates live production endpoints for functionality and webhook monitoring
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

class LiveEndpointValidator:
    def __init__(self, base_url: str = "https://tilores-x.up.railway.app"):
        self.base_url = base_url
        self.results = []

        # Core functionality tests for live validation
        self.live_tests = [
            # Generic customer tests (not hardcoded)
            {
                "name": "Known Customer - Email Query",
                "query": "who is e.j.price1986@gmail.com",
                "expected_contains": ["Status:", "Customer:", "Active"],
                "expected_not_contains": ["No customer records found"],
                "category": "customer_identification"
            },
            {
                "name": "Known Customer - Client ID Query",
                "query": "account status for client 1747598",
                "expected_contains": ["Status:", "Active"],
                "expected_not_contains": ["No customer records found"],
                "category": "account_status"
            },
            {
                "name": "Non-existent Customer - Email",
                "query": "who is john.doe@example.com",
                "expected_contains": ["No customer records found"],
                "expected_not_contains": ["Status:", "Active"],
                "category": "edge_case"
            },
            {
                "name": "Non-existent Customer - Client ID",
                "query": "account status for client 999888",
                "expected_contains": ["No customer records found"],
                "expected_not_contains": ["Status:", "Active"],
                "category": "edge_case"
            },
            {
                "name": "Credit Analysis Query",
                "query": "credit score for e.j.price1986@gmail.com",
                "expected_contains": ["Status:", "Customer:"],
                "expected_not_contains": ["No customer records found"],
                "category": "credit_analysis"
            },
            {
                "name": "Transaction Analysis Query",
                "query": "billing information e.j.price1986@gmail.com",
                "expected_contains": ["Status:", "Customer:"],
                "expected_not_contains": ["No customer records found"],
                "category": "transaction_analysis"
            },
            {
                "name": "Empty Query Handling",
                "query": "",
                "expected_contains": ["Please provide"],
                "expected_not_contains": ["Status:", "Active"],
                "category": "edge_case"
            },
            {
                "name": "Typo Correction Test",
                "query": "accont status e.j.price1986@gmail.com",
                "expected_contains": ["Status:", "Active"],
                "expected_not_contains": ["No customer records found"],
                "category": "typo_handling"
            }
        ]

    def test_endpoint_health(self) -> Dict[str, Any]:
        """Test basic endpoint health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return {
                "endpoint": "/health",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            return {
                "endpoint": "/health",
                "status_code": 0,
                "response_time": 0,
                "success": False,
                "error": str(e)
            }

    def test_chat_completion(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test chat completion endpoint"""
        try:
            start_time = time.time()

            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": test_case["query"]}]
                },
                timeout=30
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                response_data = response.json()
                assistant_response = response_data["choices"][0]["message"]["content"]

                # Validate response content
                validation_result = self.validate_response_content(
                    assistant_response, test_case
                )

                return {
                    "test_name": test_case["name"],
                    "query": test_case["query"],
                    "category": test_case["category"],
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "response": assistant_response,
                    "validation": validation_result,
                    "success": validation_result["passed"],
                    "request_id": response_data.get("id")
                }
            else:
                return {
                    "test_name": test_case["name"],
                    "query": test_case["query"],
                    "category": test_case["category"],
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "response": response.text,
                    "validation": {"passed": False, "issues": ["HTTP_ERROR"]},
                    "success": False
                }

        except Exception as e:
            return {
                "test_name": test_case["name"],
                "query": test_case["query"],
                "category": test_case["category"],
                "status_code": 0,
                "response_time": 0,
                "response": f"ERROR: {str(e)}",
                "validation": {"passed": False, "issues": ["EXCEPTION"]},
                "success": False
            }

    def validate_response_content(self, response: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response content against expectations"""
        issues = []
        passed = True

        # Check required content
        for required in test_case.get("expected_contains", []):
            if required not in response:
                issues.append(f"MISSING_REQUIRED: {required}")
                passed = False

        # Check prohibited content
        for prohibited in test_case.get("expected_not_contains", []):
            if prohibited in response:
                issues.append(f"CONTAINS_PROHIBITED: {prohibited}")
                passed = False

        # Check response length
        if len(response) < 10:
            issues.append("RESPONSE_TOO_SHORT")
            passed = False

        return {
            "passed": passed,
            "issues": issues,
            "response_length": len(response)
        }

    def test_webhook_monitoring(self) -> Dict[str, Any]:
        """Test webhook monitoring endpoints"""
        try:
            # Test webhook logs endpoint
            response = requests.get(
                f"{self.base_url}/v1/monitoring/webhook-logs?limit=5",
                timeout=10
            )

            if response.status_code == 200:
                webhook_data = response.json()

                return {
                    "endpoint": "/v1/monitoring/webhook-logs",
                    "status_code": response.status_code,
                    "success": True,
                    "logs_count": len(webhook_data.get("monitoring_logs", [])),
                    "summary": webhook_data.get("summary", {}),
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "endpoint": "/v1/monitoring/webhook-logs",
                    "status_code": response.status_code,
                    "success": False,
                    "error": response.text,
                    "response_time": response.elapsed.total_seconds()
                }

        except Exception as e:
            return {
                "endpoint": "/v1/monitoring/webhook-logs",
                "status_code": 0,
                "success": False,
                "error": str(e),
                "response_time": 0
            }

    def test_conversation_logs(self) -> Dict[str, Any]:
        """Test conversation logs endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/v1/conversations/recent?limit=3",
                timeout=10
            )

            if response.status_code == 200:
                logs_data = response.json()

                return {
                    "endpoint": "/v1/conversations/recent",
                    "status_code": response.status_code,
                    "success": True,
                    "conversations_count": len(logs_data.get("conversations", [])),
                    "total_count": logs_data.get("count", 0),
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "endpoint": "/v1/conversations/recent",
                    "status_code": response.status_code,
                    "success": False,
                    "error": response.text,
                    "response_time": response.elapsed.total_seconds()
                }

        except Exception as e:
            return {
                "endpoint": "/v1/conversations/recent",
                "status_code": 0,
                "success": False,
                "error": str(e),
                "response_time": 0
            }

    def run_live_validation(self) -> Dict[str, Any]:
        """Run comprehensive live endpoint validation"""
        print("🌐 Starting Live Endpoint Validation")
        print(f"🎯 Target: {self.base_url}")
        print("=" * 60)

        # Test health endpoint first
        print("🏥 Testing Health Endpoint...")
        health_result = self.test_endpoint_health()
        print(f"   {'✅' if health_result['success'] else '❌'} Health: {health_result['status_code']} ({health_result['response_time']:.2f}s)")

        if not health_result['success']:
            print("❌ Health check failed - aborting validation")
            return {
                "overall_success": False,
                "health_check": health_result,
                "error": "Health check failed"
            }

        # Test chat completions
        print("\n💬 Testing Chat Completions...")
        chat_results = []
        successful_tests = 0

        for i, test_case in enumerate(self.live_tests):
            result = self.test_chat_completion(test_case)
            chat_results.append(result)

            if result["success"]:
                successful_tests += 1

            success_indicator = "✅" if result["success"] else "❌"
            print(f"   {success_indicator} [{i+1:2d}/{len(self.live_tests)}] {test_case['name']:35s} | {result['response_time']:.2f}s")

        success_rate = (successful_tests / len(self.live_tests)) * 100

        # Test webhook monitoring
        print("\n📊 Testing Webhook Monitoring...")
        webhook_result = self.test_webhook_monitoring()
        print(f"   {'✅' if webhook_result['success'] else '❌'} Webhook Logs: {webhook_result['status_code']} ({webhook_result.get('response_time', 0):.2f}s)")

        # Test conversation logs
        print("\n📝 Testing Conversation Logs...")
        logs_result = self.test_conversation_logs()
        print(f"   {'✅' if logs_result['success'] else '❌'} Conversation Logs: {logs_result['status_code']} ({logs_result.get('response_time', 0):.2f}s)")

        # Summary
        print("\n" + "=" * 60)
        print("🌐 LIVE ENDPOINT VALIDATION RESULTS")
        print("=" * 60)
        print(f"Chat Completions Success Rate: {success_rate:.1f}% ({successful_tests}/{len(self.live_tests)})")
        print(f"Webhook Monitoring: {'✅ Working' if webhook_result['success'] else '❌ Failed'}")
        print(f"Conversation Logs: {'✅ Working' if logs_result['success'] else '❌ Failed'}")

        overall_success = (
            health_result['success'] and
            success_rate >= 90 and
            webhook_result['success'] and
            logs_result['success']
        )

        print(f"\n🎯 Overall Status: {'✅ PRODUCTION READY' if overall_success else '❌ NEEDS ATTENTION'}")

        return {
            "overall_success": overall_success,
            "success_rate": success_rate,
            "health_check": health_result,
            "chat_results": chat_results,
            "webhook_monitoring": webhook_result,
            "conversation_logs": logs_result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

def main():
    validator = LiveEndpointValidator()
    results = validator.run_live_validation()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"live_validation_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Results saved to: live_validation_{timestamp}.json")

    if results["overall_success"]:
        print("\n🎉 SUCCESS! Live endpoints are fully functional!")
    else:
        print(f"\n⚠️  Issues detected - check results for details")

if __name__ == "__main__":
    main()
