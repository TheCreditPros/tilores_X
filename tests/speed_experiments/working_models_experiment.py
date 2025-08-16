#!/usr/bin/env python3
"""
LangSmith Speed Experiments with Working Models Only
Updated after Groq model deprecations (Aug 2025)
"""

import time
import requests
import json
from typing import Dict, List, Any


class WorkingModelsSpeedExperiment:
    """Speed experiments with only working models"""

    def __init__(self):
        """Initialize with working models only"""
        self.api_url = "https://tiloresx-production.up.railway.app/v1/chat/completions"

        # Updated list of working models (deprecated models removed)
        self.working_models = [
            {"id": "llama-3.3-70b-versatile", "provider": "groq", "expected_speed": "~600ms", "status": "working"},
            {"id": "gpt-3.5-turbo", "provider": "openai", "expected_speed": "~1.5s", "status": "working"},
            {"id": "gpt-4o-mini", "provider": "openai", "expected_speed": "~1.9s", "status": "working"},
            {"id": "deepseek-r1-distill-llama-70b", "provider": "groq", "expected_speed": "~3.5s", "status": "working"},
            {"id": "claude-3-haiku", "provider": "anthropic", "expected_speed": "~2s", "status": "working"},
            {"id": "gemini-1.5-flash-002", "provider": "google", "expected_speed": "~2.2s", "status": "working"},
        ]

        # Real customer test data (validated)
        self.real_customers = [
            {
                "email": "blessedwina@aol.com",
                "name": "Edwina Hawthorne",
                "client_id": "2270",
                "phone": "2672661591",
                "dob": "1964-03-27",
                "status": "active",
            },
            {"email": "lelisguardado@sbcglobal.net", "name": "TBD", "status": "pending_validation"},
            {"email": "migdaliareyes53@gmail.com", "name": "TBD", "status": "pending_validation"},
        ]

    def run_speed_experiments(self) -> Dict[str, Any]:
        """Run speed experiments with working models"""
        print("🚀 Starting LangSmith Speed Experiments (Working Models Only)")
        print("=" * 60)

        results = {
            "experiment_id": f"working_models_{int(time.time())}",
            "start_time": time.time(),
            "models_tested": [],
            "customer_tests": {},
            "performance_summary": {},
        }

        # Test each working model
        for model in self.working_models:
            print(f"\n🔧 Testing {model['id']} ({model['provider']}) - Expected: {model['expected_speed']}")

            model_results = self._test_model_with_customers(model)
            results["models_tested"].append(model["id"])
            results["customer_tests"][model["id"]] = model_results

        results["end_time"] = time.time()
        results["duration_minutes"] = (results["end_time"] - results["start_time"]) / 60

        # Generate performance summary
        results["performance_summary"] = self._generate_performance_summary(results)

        return results

    def _test_model_with_customers(self, model: Dict) -> Dict[str, Any]:
        """Test a model with all customer scenarios"""
        model_results = {
            "model_info": model,
            "customer_responses": {},
            "avg_response_time": 0,
            "success_rate": 0,
            "total_tests": 0,
        }

        response_times = []
        successful_tests = 0

        # Test with validated customer (Edwina Hawthorne)
        validated_customer = self.real_customers[0]  # blessedwina@aol.com

        print(f"  👤 Testing with validated customer: {validated_customer['name']}")

        # Test basic customer lookup
        lookup_result = self._test_customer_lookup(model, validated_customer)
        model_results["customer_responses"]["basic_lookup"] = lookup_result

        if lookup_result["success"]:
            response_times.append(lookup_result["response_time_ms"])
            successful_tests += 1

        # Test credit report request (conversational turn 2)
        credit_result = self._test_credit_request(model, validated_customer)
        model_results["customer_responses"]["credit_request"] = credit_result

        if credit_result["success"]:
            response_times.append(credit_result["response_time_ms"])
            successful_tests += 1

        # Calculate metrics
        model_results["total_tests"] = 2
        model_results["success_rate"] = (successful_tests / 2) * 100
        model_results["avg_response_time"] = sum(response_times) / len(response_times) if response_times else 0

        return model_results

    def _test_customer_lookup(self, model: Dict, customer: Dict) -> Dict[str, Any]:
        """Test basic customer lookup"""
        start_time = time.time()

        try:
            response = requests.post(
                self.api_url,
                headers={"Content-Type": "application/json"},
                json={
                    "model": model["id"],
                    "messages": [{"role": "user", "content": f"Find customer with email {customer['email']}"}],
                    "max_tokens": 300,
                },
                timeout=30,
            )

            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                # Check if we got real customer data
                has_customer_name = customer.get("name", "").lower() in content.lower()
                has_client_id = customer.get("client_id", "") in content
                has_real_data = len(content) > 100 and "error" not in content.lower()

                return {
                    "success": True,
                    "response_time_ms": response_time_ms,
                    "content_length": len(content),
                    "has_customer_name": has_customer_name,
                    "has_client_id": has_client_id,
                    "has_real_data": has_real_data,
                    "content_preview": content[:150] + "..." if len(content) > 150 else content,
                }
            else:
                return {"success": False, "response_time_ms": response_time_ms, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            end_time = time.time()
            return {"success": False, "response_time_ms": (end_time - start_time) * 1000, "error": str(e)}

    def _test_credit_request(self, model: Dict, customer: Dict) -> Dict[str, Any]:
        """Test credit report request (conversational turn 2)"""
        start_time = time.time()

        try:
            response = requests.post(
                self.api_url,
                headers={"Content-Type": "application/json"},
                json={
                    "model": model["id"],
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Get the credit report for customer {customer['name']} with client ID {customer.get('client_id', 'unknown')}",
                        }
                    ],
                    "max_tokens": 500,
                },
                timeout=30,
            )

            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                # Check for credit-related content
                credit_keywords = ["credit", "score", "report", "analysis", "utilization"]
                has_credit_content = any(keyword in content.lower() for keyword in credit_keywords)
                has_customer_ref = customer.get("name", "").lower() in content.lower()

                return {
                    "success": True,
                    "response_time_ms": response_time_ms,
                    "content_length": len(content),
                    "has_credit_content": has_credit_content,
                    "has_customer_ref": has_customer_ref,
                    "content_preview": content[:150] + "..." if len(content) > 150 else content,
                }
            else:
                return {"success": False, "response_time_ms": response_time_ms, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            end_time = time.time()
            return {"success": False, "response_time_ms": (end_time - start_time) * 1000, "error": str(e)}

    def _generate_performance_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary"""
        model_performance = []

        for model_id in results["models_tested"]:
            model_data = results["customer_tests"][model_id]
            model_performance.append(
                {
                    "model_id": model_id,
                    "avg_response_time": model_data["avg_response_time"],
                    "success_rate": model_data["success_rate"],
                    "provider": model_data["model_info"]["provider"],
                }
            )

        # Sort by response time (fastest first)
        model_performance.sort(key=lambda x: x["avg_response_time"])

        return {
            "fastest_model": model_performance[0] if model_performance else None,
            "model_ranking": model_performance,
            "total_duration": results["duration_minutes"],
            "models_tested": len(results["models_tested"]),
        }


def main():
    """Run the working models speed experiment"""
    experiment = WorkingModelsSpeedExperiment()

    # Run experiments
    results = experiment.run_speed_experiments()

    # Save results
    with open("tests/speed_experiments/working_models_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n📊 WORKING MODELS EXPERIMENT SUMMARY")
    print("=" * 60)
    summary = results["performance_summary"]

    print(f"Duration: {summary['total_duration']:.1f} minutes")
    print(f"Models tested: {summary['models_tested']}")

    if summary["fastest_model"]:
        fastest = summary["fastest_model"]
        print(f"\n🏆 Fastest working model: {fastest['model_id']}")
        print(f"   Provider: {fastest['provider']}")
        print(f"   Response time: {fastest['avg_response_time']:.0f}ms")
        print(f"   Success rate: {fastest['success_rate']:.1f}%")

    print("\n🏆 PERFORMANCE RANKING:")
    for i, model in enumerate(summary["model_ranking"], 1):
        print(f"{i}. {model['model_id']} ({model['provider']})")
        print(f"   Response time: {model['avg_response_time']:.0f}ms")
        print(f"   Success rate: {model['success_rate']:.1f}%")

    return results


if __name__ == "__main__":
    main()
