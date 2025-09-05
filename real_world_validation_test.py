#!/usr/bin/env python3
"""
Real-World Validation Test - User Journey Focus
Tests actual user scenarios and expectations, not technical edge cases
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

class RealWorldValidator:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results = []

        # REAL USER SCENARIOS - What customers actually ask for
        self.user_scenarios = {
            "basic_customer_lookup": [
                {
                    "query": "who is e.j.price1986@gmail.com",
                    "expectation": "Should return customer name, status, and basic account info",
                    "must_contain": ["Esteban Price", "Active", "Status"],
                    "must_not_contain": ["I need customer information", "No records found"]
                }
            ],
            "credit_information_requests": [
                {
                    "query": "what is the credit score for e.j.price1986@gmail.com",
                    "expectation": "Should return actual credit scores from bureaus, not generic status",
                    "must_contain": ["credit", "score", "Esteban Price"],
                    "must_not_contain": ["I need customer information", "unable to access", "privacy"]
                },
                {
                    "query": "show me experian credit report for client 1747598",
                    "expectation": "Should return Experian-specific credit data",
                    "must_contain": ["experian", "credit", "Esteban Price"],
                    "must_not_contain": ["I need customer information", "unable to access"]
                }
            ],
            "conversational_follow_ups": [
                {
                    "setup_query": "who is e.j.price1986@gmail.com",
                    "follow_up_query": "what is their credit score",
                    "expectation": "Should maintain context and return credit data without asking for customer info again",
                    "must_contain": ["credit", "score", "Esteban Price"],
                    "must_not_contain": ["I need customer information", "unable to access"]
                },
                {
                    "setup_query": "customer profile for client 1747598",
                    "follow_up_query": "what is their most recent experian score",
                    "expectation": "Should use context from previous query to provide credit data",
                    "must_contain": ["experian", "credit", "Esteban Price"],
                    "must_not_contain": ["I need customer information", "unable to access"]
                }
            ],
            "transaction_requests": [
                {
                    "query": "payment history for e.j.price1986@gmail.com",
                    "expectation": "Should return actual payment/transaction data",
                    "must_contain": ["payment", "transaction", "Esteban Price"],
                    "must_not_contain": ["I need customer information", "unable to access"]
                }
            ]
        }

    def test_single_scenario(self, scenario: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Test a single real-world scenario"""
        try:
            if "setup_query" in scenario:
                # Conversational scenario - test context maintenance
                return self.test_conversational_scenario(scenario, category)
            else:
                # Single query scenario
                return self.test_single_query_scenario(scenario, category)
        except Exception as e:
            return {
                "scenario": scenario.get("query", "conversational"),
                "category": category,
                "success": False,
                "issues": [f"EXCEPTION: {str(e)}"],
                "expectation": scenario["expectation"],
                "response": f"ERROR: {str(e)}"
            }

    def test_single_query_scenario(self, scenario: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Test a single query scenario"""
        query = scenario["query"]
        start_time = time.time()

        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": query}]
            },
            timeout=30
        )

        response_time = time.time() - start_time

        if response.status_code == 200:
            response_data = response.json()
            assistant_response = response_data["choices"][0]["message"]["content"]

            validation = self.validate_real_world_response(assistant_response, scenario)

            return {
                "scenario": query,
                "category": category,
                "success": validation["success"],
                "issues": validation["issues"],
                "expectation": scenario["expectation"],
                "response": assistant_response,
                "response_time": response_time
            }
        else:
            return {
                "scenario": query,
                "category": category,
                "success": False,
                "issues": [f"HTTP_{response.status_code}"],
                "expectation": scenario["expectation"],
                "response": f"HTTP {response.status_code}",
                "response_time": response_time
            }

    def test_conversational_scenario(self, scenario: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Test conversational context maintenance"""
        setup_query = scenario["setup_query"]
        follow_up_query = scenario["follow_up_query"]

        # Step 1: Setup context
        setup_response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": setup_query}]
            },
            timeout=30
        )

        if setup_response.status_code != 200:
            return {
                "scenario": f"{setup_query} -> {follow_up_query}",
                "category": category,
                "success": False,
                "issues": ["SETUP_FAILED"],
                "expectation": scenario["expectation"],
                "response": f"Setup failed: HTTP {setup_response.status_code}"
            }

        # Step 2: Test follow-up (simulating OpenWebUI behavior)
        start_time = time.time()
        follow_up_response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": follow_up_query}]
            },
            timeout=30
        )
        response_time = time.time() - start_time

        if follow_up_response.status_code == 200:
            response_data = follow_up_response.json()
            assistant_response = response_data["choices"][0]["message"]["content"]

            validation = self.validate_real_world_response(assistant_response, scenario)

            return {
                "scenario": f"{setup_query} -> {follow_up_query}",
                "category": category,
                "success": validation["success"],
                "issues": validation["issues"],
                "expectation": scenario["expectation"],
                "response": assistant_response,
                "response_time": response_time
            }
        else:
            return {
                "scenario": f"{setup_query} -> {follow_up_query}",
                "category": category,
                "success": False,
                "issues": [f"HTTP_{follow_up_response.status_code}"],
                "expectation": scenario["expectation"],
                "response": f"HTTP {follow_up_response.status_code}",
                "response_time": response_time
            }

    def validate_real_world_response(self, response: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response against real-world expectations"""
        issues = []
        response_lower = response.lower()

        # Check required content (what users expect to see)
        for required in scenario["must_contain"]:
            if required.lower() not in response_lower:
                issues.append(f"MISSING_REQUIRED: {required}")

        # Check forbidden content (failure indicators)
        for forbidden in scenario["must_not_contain"]:
            if forbidden.lower() in response_lower:
                issues.append(f"CONTAINS_FORBIDDEN: {forbidden}")

        success = len(issues) == 0

        return {
            "success": success,
            "issues": issues
        }

    def run_all_tests(self):
        """Run all real-world scenario tests"""
        print("🌍 Starting Real-World User Scenario Validation")
        print("=" * 60)

        all_results = []
        category_stats = {}

        for category, scenarios in self.user_scenarios.items():
            print(f"\n📋 Testing: {category.replace('_', ' ').title()}")
            category_results = []

            for i, scenario in enumerate(scenarios, 1):
                result = self.test_single_scenario(scenario, category)
                category_results.append(result)
                all_results.append(result)

                status = "✅" if result["success"] else "❌"
                scenario_name = result["scenario"][:60] + "..." if len(result["scenario"]) > 60 else result["scenario"]
                print(f"  {status} [{i}/{len(scenarios)}] {scenario_name}")

                if not result["success"]:
                    print(f"      Issues: {', '.join(result['issues'])}")
                    print(f"      Expected: {result['expectation']}")

            # Category statistics
            success_count = sum(1 for r in category_results if r["success"])
            success_rate = (success_count / len(category_results)) * 100
            category_stats[category] = {
                "success_rate": success_rate,
                "success_count": success_count,
                "total_count": len(category_results)
            }

        # Overall statistics
        total_success = sum(1 for r in all_results if r["success"])
        total_tests = len(all_results)
        overall_success_rate = (total_success / total_tests) * 100

        print("\n" + "=" * 60)
        print("🌍 REAL-WORLD VALIDATION RESULTS")
        print("=" * 60)
        print(f"Overall Success Rate: {overall_success_rate:.1f}% ({total_success}/{total_tests})")

        if overall_success_rate >= 90:
            print("✅ PRODUCTION READY - Real user scenarios working")
        else:
            print("❌ NOT READY - Critical user scenarios failing")

        print(f"\nCategory Breakdown:")
        for category, stats in category_stats.items():
            status = "✅" if stats["success_rate"] >= 90 else "❌"
            print(f"{status} {category.replace('_', ' ').title():<30}: {stats['success_rate']:5.1f}% ({stats['success_count']}/{stats['total_count']})")

        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"real_world_validation_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "overall_success_rate": overall_success_rate,
                "total_tests": total_tests,
                "successful_tests": total_success,
                "category_stats": category_stats,
                "detailed_results": all_results
            }, f, indent=2)

        print(f"\n📄 Detailed results saved to: {filename}")

        if overall_success_rate < 90:
            print(f"\n⚠️  Need {90 - overall_success_rate:.1f}% more improvement to reach production readiness")

            # Show critical failures
            critical_failures = [r for r in all_results if not r["success"]]
            if critical_failures:
                print(f"\n🚨 Critical Failures to Fix:")
                for failure in critical_failures[:5]:  # Show top 5
                    print(f"   • {failure['scenario'][:50]}...")
                    print(f"     Expected: {failure['expectation']}")
                    print(f"     Issues: {', '.join(failure['issues'])}")

        return overall_success_rate >= 90

if __name__ == "__main__":
    validator = RealWorldValidator()
    success = validator.run_all_tests()

    if success:
        print("\n🎉 All real-world scenarios passing - Ready for production!")
    else:
        print("\n🔧 Fix critical user scenarios before deployment")
