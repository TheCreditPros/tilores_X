#!/usr / bin / env python3
"""
Test Webhook Integration

Tests the webhook endpoints to ensure they're ready for Agenta.ai integration.
"""

import requests
import json
import time

class WebhookIntegrationTest:
    def __init__(self):
        """Initialize webhook test"""
        self.base_url = "https://tilores - x.up.railway.app"
        self.webhook_endpoints = {
            "evaluation - complete": f"{self.base_url}/webhooks / evaluation - complete",
            "deployment - status": f"{self.base_url}/webhooks / deployment - status",
            "performance - alert": f"{self.base_url}/webhooks / performance - alert",
            "health": f"{self.base_url}/webhooks / health"
        }

        print("🧪 Webhook Integration Test")
        print("=" * 40)

    def test_webhook_health(self) -> bool:
        """Test webhook health endpoint"""
        print("\n🔍 Testing Webhook Health...")

        try:
            response = requests.get(self.webhook_endpoints["health"], timeout=10)

            if response.status_code == 200:
                data = response.json()
                print("   ✅ Health check passed")
                print(f"   📊 Status: {data.get('status')}")
                print(f"   📋 Endpoints: {len(data.get('endpoints', []))}")
                return True
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            return False

    def test_evaluation_webhook(self) -> bool:
        """Test evaluation complete webhook"""
        print("\n🧪 Testing Evaluation Webhook...")

        test_payload = {
            "evaluation_id": "test - eval - 123",
            "test_set_name": "Account Status Queries",
            "variant_name": "account - status - v1",
            "results": {
                "accuracy": 95.0,
                "response_time": 2.5,
                "token_usage": 150
            },
            "status": "completed",
            "completion_time": "2025 - 09 - 02T18:45:00Z"
        }

        try:
            response = requests.post(
                self.webhook_endpoints["evaluation - complete"],
                json=test_payload,
                headers={"Content - Type": "application / json"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                print("   ✅ Evaluation webhook working")
                print(f"   📊 Response: {data.get('message', 'Success')}")
                return True
            else:
                print(f"   ❌ Evaluation webhook failed: {response.status_code}")
                print(f"   📋 Response: {response.text[:100]}")
                return False

        except Exception as e:
            print(f"   ❌ Evaluation webhook error: {e}")
            return False

    def test_deployment_webhook(self) -> bool:
        """Test deployment status webhook"""
        print("\n🚀 Testing Deployment Webhook...")

        test_payload = {
            "deployment_id": "deploy - 456",
            "environment": "production",
            "variant_name": "credit - analysis - v1",
            "status": "completed",
            "timestamp": "2025 - 09 - 02T18:45:00Z",
            "logs": "Deployment successful"
        }

        try:
            response = requests.post(
                self.webhook_endpoints["deployment - status"],
                json=test_payload,
                headers={"Content - Type": "application / json"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                print("   ✅ Deployment webhook working")
                print(f"   📊 Response: {data.get('message', 'Success')}")
                return True
            else:
                print(f"   ❌ Deployment webhook failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"   ❌ Deployment webhook error: {e}")
            return False

    def test_performance_webhook(self) -> bool:
        """Test performance alert webhook"""
        print("\n📊 Testing Performance Webhook...")

        test_payload = {
            "alert_type": "response_time",
            "metric_name": "avg_response_time",
            "current_value": 18.5,
            "threshold_value": 15.0,
            "variant_name": "multi - data - analysis - v1",
            "timestamp": "2025 - 09 - 02T18:45:00Z"
        }

        try:
            response = requests.post(
                self.webhook_endpoints["performance - alert"],
                json=test_payload,
                headers={"Content - Type": "application / json"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                print("   ✅ Performance webhook working")
                print(f"   📊 Response: {data.get('message', 'Success')}")
                return True
            else:
                print(f"   ❌ Performance webhook failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"   ❌ Performance webhook error: {e}")
            return False

    def run_all_tests(self) -> bool:
        """Run all webhook tests"""
        print("🚀 Running Webhook Integration Tests")
        print("=" * 50)

        tests = [
            ("Webhook Health", self.test_webhook_health),
            ("Evaluation Complete", self.test_evaluation_webhook),
            ("Deployment Status", self.test_deployment_webhook),
            ("Performance Alert", self.test_performance_webhook)
        ]

        results = []
        for test_name, test_func in tests:
            result = test_func()
            results.append((test_name, result))

        # Summary
        print("\n📊 WEBHOOK INTEGRATION TEST SUMMARY:")
        print("=" * 40)

        successful = sum(1 for _, success in results if success)
        total = len(results)

        for test_name, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}")

        print(f"\n🎯 Success Rate: {successful}/{total} ({successful / total * 100:.1f}%)")

        if successful == total:
            print("\n🎉 All webhook endpoints ready for Agenta.ai!")
            print("\n🚀 Next Steps:")
            print("  1. Configure webhook URLs in Agenta.ai UI")
            print("  2. Create prompt variants")
            print("  3. Run test evaluations")
            print("  4. Set up A / B testing experiments")
        else:
            print("\n⚠️ Some webhook tests failed. Check deployment.")

        return successful == total

def main():
    """Main function"""
    tester = WebhookIntegrationTest()
    success = tester.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
