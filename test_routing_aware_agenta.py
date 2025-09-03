#!/usr / bin / env python3
"""
Comprehensive Test Suite for Routing - Aware Agenta SDK Manager

Tests the routing - aware functionality that bridges TLRS routing logic
with Agenta.ai prompt optimization.
"""

import json
import sys
import os
from typing import Dict, List, Any
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agenta_sdk_manager_enhanced import (
        RoutingContext,
        RoutingAwareAgentaManager,
        get_routing_aware_prompt,
        create_routing_test_case
    )
    print("✅ Successfully imported routing - aware components")
except ImportError as e:
    print(f"❌ Failed to import routing - aware components: {e}")
    sys.exit(1)


class RoutingAwareTestSuite:
    """Comprehensive test suite for routing - aware Agenta functionality"""

    def __init__(self):
        self.test_results = []
        self.manager = RoutingAwareAgentaManager()

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Routing - Aware Agenta Test Suite")
        print("=" * 60)

        # Test routing context analysis
        self.test_routing_context_analysis()

        # Test routing - aware prompt generation
        self.test_routing_aware_prompts()

        # Test data availability handling
        self.test_data_availability_scenarios()

        # Test edge cases
        self.test_edge_cases()

        # Test integration scenarios
        self.test_integration_scenarios()

        # Generate test report
        self.generate_test_report()

    def test_routing_context_analysis(self):
        """Test routing context analysis functionality"""
        print("\n📊 Testing Routing Context Analysis")
        print("-" * 40)

        test_cases = [
            {
                "name": "Credit Analysis Query",
                "query": "What's the credit score for e.j.price1986@gmail.com?",
                "expected_route": "credit",
                "expected_keywords": ["credit"],
                "expected_data_types": ["credit"]
            },
            {
                "name": "Account Status Query",
                "query": "What's the account status for john.doe@email.com?",
                "expected_route": "account_status",
                "expected_keywords": ["account_status"],
                "expected_data_types": []
            },
            {
                "name": "Multi - Data Query",
                "query": "Give me comprehensive analysis for customer@email.com",
                "expected_route": "multi_data",
                "expected_keywords": ["combined"],
                "expected_data_types": [],
                "expected_multi_data": True
            },
            {
                "name": "Phone Analysis Query",
                "query": "Show me call history for customer@email.com",
                "expected_route": "phone",
                "expected_keywords": ["phone"],
                "expected_data_types": ["phone"]
            },
            {
                "name": "Transaction Analysis Query",
                "query": "What are the payment patterns for customer@email.com?",
                "expected_route": "transaction",
                "expected_keywords": ["transaction"],
                "expected_data_types": ["transaction"]
            },
            {
                "name": "Mixed Keywords Query",
                "query": "Show me credit score and transaction history for customer@email.com",
                "expected_route": "multi_data",
                "expected_keywords": ["credit", "transaction"],
                "expected_data_types": ["credit", "transaction"],
                "expected_multi_data": True
            },
            {
                "name": "Fallback Query",
                "query": "Tell me about customer@email.com",
                "expected_route": "credit",
                "expected_keywords": [],
                "expected_data_types": [],
                "expected_fallback": "no_specific_keywords_detected"
            }
        ]

        for test_case in test_cases:
            result = self._test_routing_context(test_case)
            self.test_results.append(result)

    def _test_routing_context(self, test_case: Dict) -> Dict:
        """Test individual routing context scenario"""
        try:
            # Analyze routing context
            context = RoutingContext(
                test_case["query"],
                "test - customer - id"
            ).analyze_query()

            # Check routing decision
            route_match = context.routing_decision == test_case["expected_route"]

            # Check keywords
            keywords_match = set(context.keywords_detected) == set(test_case["expected_keywords"])

            # Check data types
            data_types_match = set(context.data_types_requested) == set(test_case["expected_data_types"])

            # Check multi - data flag
            multi_data_match = context.is_multi_data == test_case.get("expected_multi_data", False)

            # Check fallback reason
            fallback_match = True
            if "expected_fallback" in test_case:
                fallback_match = context.fallback_reason == test_case["expected_fallback"]

            success = all([route_match, keywords_match, data_types_match, multi_data_match, fallback_match])

            result = {
                "test_name": test_case["name"],
                "test_type": "routing_context",
                "success": success,
                "details": {
                    "query": test_case["query"],
                    "expected_route": test_case["expected_route"],
                    "actual_route": context.routing_decision,
                    "route_match": route_match,
                    "expected_keywords": test_case["expected_keywords"],
                    "actual_keywords": context.keywords_detected,
                    "keywords_match": keywords_match,
                    "expected_data_types": test_case["expected_data_types"],
                    "actual_data_types": context.data_types_requested,
                    "data_types_match": data_types_match,
                    "multi_data_match": multi_data_match,
                    "fallback_match": fallback_match,
                    "complexity_score": context.complexity_score
                }
            }

            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_case['name']}: {context.routing_decision} "
                  f"(keywords: {context.keywords_detected})")

            return result

        except Exception as e:
            result = {
                "test_name": test_case["name"],
                "test_type": "routing_context",
                "success": False,
                "error": str(e)
            }
            print(f"❌ ERROR {test_case['name']}: {e}")
            return result

    def test_routing_aware_prompts(self):
        """Test routing - aware prompt generation"""
        print("\n🎯 Testing Routing - Aware Prompt Generation")
        print("-" * 40)

        test_queries = [
            "What's the credit score for e.j.price1986@gmail.com?",
            "Show me comprehensive analysis for customer@email.com",
            "What's the account status for john.doe@email.com?",
            "Show me call history and transactions for customer@email.com"
        ]

        for query in test_queries:
            result = self._test_prompt_generation(query)
            self.test_results.append(result)

    def _test_prompt_generation(self, query: str) -> Dict:
        """Test individual prompt generation"""
        try:
            # Get routing - aware prompt
            prompt_config = self.manager.get_routing_aware_prompt(
                query=query,
                customer_id="test - customer - id"
            )

            # Validate prompt structure
            required_fields = ["system_prompt", "routing_metadata", "routing_aware"]
            has_required_fields = all(field in prompt_config for field in required_fields)

            # Check if routing context is injected
            system_prompt = prompt_config.get("system_prompt", "")
            has_routing_context = "[ROUTING CONTEXT:" in system_prompt

            # Check routing metadata
            routing_metadata = prompt_config.get("routing_metadata", {})
            has_routing_decision = "routing_decision" in routing_metadata
            has_keywords = "keywords_detected" in routing_metadata

            success = all([has_required_fields, has_routing_context, has_routing_decision, has_keywords])

            result = {
                "test_name": f"Prompt Generation: {query[:50]}...",
                "test_type": "prompt_generation",
                "success": success,
                "details": {
                    "query": query,
                    "routing_decision": routing_metadata.get("routing_decision"),
                    "keywords_detected": routing_metadata.get("keywords_detected"),
                    "has_required_fields": has_required_fields,
                    "has_routing_context": has_routing_context,
                    "prompt_source": prompt_config.get("source"),
                    "routing_aware": prompt_config.get("routing_aware", False)
                }
            }

            status = "✅ PASS" if success else "❌ FAIL"
            route = routing_metadata.get("routing_decision", "unknown")
            print(f"{status} Prompt for {route} query")

            return result

        except Exception as e:
            result = {
                "test_name": f"Prompt Generation: {query[:50]}...",
                "test_type": "prompt_generation",
                "success": False,
                "error": str(e)
            }
            print(f"❌ ERROR generating prompt: {e}")
            return result

    def test_data_availability_scenarios(self):
        """Test data availability handling"""
        print("\n📊 Testing Data Availability Scenarios")
        print("-" * 40)

        scenarios = [
            {
                "name": "All Data Available",
                "query": "Give me comprehensive analysis for customer@email.com",
                "data_availability": {
                    "credit_data": True,
                    "phone_data": True,
                    "transaction_data": True,
                    "card_data": True,
                    "ticket_data": True
                }
            },
            {
                "name": "Phone Data Unavailable",
                "query": "Show me call history for customer@email.com",
                "data_availability": {
                    "credit_data": True,
                    "phone_data": False,
                    "transaction_data": True,
                    "card_data": True,
                    "ticket_data": True
                }
            },
            {
                "name": "Limited Data Available",
                "query": "Give me comprehensive analysis for customer@email.com",
                "data_availability": {
                    "credit_data": True,
                    "phone_data": False,
                    "transaction_data": False,
                    "card_data": False,
                    "ticket_data": False
                }
            }
        ]

        for scenario in scenarios:
            result = self._test_data_availability(scenario)
            self.test_results.append(result)

    def _test_data_availability(self, scenario: Dict) -> Dict:
        """Test individual data availability scenario"""
        try:
            # Get routing - aware prompt with data availability
            prompt_config = self.manager.get_routing_aware_prompt(
                query=scenario["query"],
                customer_id="test - customer - id",
                data_availability=scenario["data_availability"]
            )

            # Check if data availability is reflected in prompt
            system_prompt = prompt_config.get("system_prompt", "")
            has_data_availability = "[DATA AVAILABILITY:" in system_prompt

            # Check routing metadata includes data availability
            routing_metadata = prompt_config.get("routing_metadata", {})
            has_availability_metadata = "data_availability" in routing_metadata

            success = has_data_availability and has_availability_metadata

            result = {
                "test_name": scenario["name"],
                "test_type": "data_availability",
                "success": success,
                "details": {
                    "query": scenario["query"],
                    "data_availability": scenario["data_availability"],
                    "has_data_availability_context": has_data_availability,
                    "has_availability_metadata": has_availability_metadata,
                    "routing_decision": routing_metadata.get("routing_decision")
                }
            }

            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {scenario['name']}")

            return result

        except Exception as e:
            result = {
                "test_name": scenario["name"],
                "test_type": "data_availability",
                "success": False,
                "error": str(e)
            }
            print(f"❌ ERROR {scenario['name']}: {e}")
            return result

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n🔍 Testing Edge Cases")
        print("-" * 40)

        edge_cases = [
            {
                "name": "Empty Query",
                "query": "",
                "should_handle_gracefully": True
            },
            {
                "name": "Very Long Query",
                "query": "What is the credit score and transaction history and phone call data and support tickets and credit card information " * 10,
                "should_handle_gracefully": True
            },
            {
                "name": "Special Characters",
                "query": "What's the credit score for user@domain.com with special chars: !@#$%^&*()",
                "should_handle_gracefully": True
            },
            {
                "name": "No Customer ID",
                "query": "What's the credit score?",
                "customer_id": None,
                "should_handle_gracefully": True
            }
        ]

        for case in edge_cases:
            result = self._test_edge_case(case)
            self.test_results.append(result)

    def _test_edge_case(self, case: Dict) -> Dict:
        """Test individual edge case"""
        try:
            # Get routing - aware prompt
            prompt_config = self.manager.get_routing_aware_prompt(
                query=case["query"],
                customer_id=case.get("customer_id", "test - customer - id")
            )

            # Check if it handled gracefully
            has_system_prompt = bool(prompt_config.get("system_prompt"))
            has_routing_metadata = bool(prompt_config.get("routing_metadata"))

            success = has_system_prompt and has_routing_metadata

            result = {
                "test_name": case["name"],
                "test_type": "edge_case",
                "success": success,
                "details": {
                    "query": case["query"][:100] + "..." if len(case["query"]) > 100 else case["query"],
                    "handled_gracefully": success,
                    "has_system_prompt": has_system_prompt,
                    "has_routing_metadata": has_routing_metadata
                }
            }

            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {case['name']}")

            return result

        except Exception as e:
            # For edge cases, we expect some to potentially fail
            result = {
                "test_name": case["name"],
                "test_type": "edge_case",
                "success": case.get("should_handle_gracefully", False) == False,  # If we expect failure, success = True
                "details": {
                    "query": case["query"][:100] + "..." if len(case["query"]) > 100 else case["query"],
                    "error": str(e),
                    "expected_failure": not case.get("should_handle_gracefully", True)
                }
            }

            if case.get("should_handle_gracefully", True):
                print(f"❌ FAIL {case['name']}: {e}")
            else:
                print(f"✅ PASS {case['name']}: Expected failure occurred")

            return result

    def test_integration_scenarios(self):
        """Test integration scenarios that mirror real TLRS usage"""
        print("\n🔗 Testing Integration Scenarios")
        print("-" * 40)

        # Test routing - aware test case creation
        test_case = create_routing_test_case(
            query="What's the credit score for e.j.price1986@gmail.com?",
            customer_id="dc93a2cd - de0a - 444f - ad47 - 3003ba998cd3",
            expected_route="credit"
        )

        has_required_structure = all(key in test_case for key in ["input", "expected", "metadata"])

        result = {
            "test_name": "Test Case Creation",
            "test_type": "integration",
            "success": has_required_structure,
            "details": {
                "has_required_structure": has_required_structure,
                "test_case_keys": list(test_case.keys())
            }
        }

        status = "✅ PASS" if has_required_structure else "❌ FAIL"
        print(f"{status} Test Case Creation")

        self.test_results.append(result)

        # Test convenience function
        try:
            prompt_config = get_routing_aware_prompt(
                query="Show me comprehensive analysis for customer@email.com",
                customer_id="test - customer - id"
            )

            convenience_success = bool(prompt_config.get("routing_aware"))

            result = {
                "test_name": "Convenience Function",
                "test_type": "integration",
                "success": convenience_success,
                "details": {
                    "function_works": convenience_success,
                    "routing_aware": prompt_config.get("routing_aware", False)
                }
            }

            status = "✅ PASS" if convenience_success else "❌ FAIL"
            print(f"{status} Convenience Function")

            self.test_results.append(result)

        except Exception as e:
            result = {
                "test_name": "Convenience Function",
                "test_type": "integration",
                "success": False,
                "error": str(e)
            }
            print(f"❌ ERROR Convenience Function: {e}")
            self.test_results.append(result)

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 ROUTING - AWARE AGENTA TEST REPORT")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print("\n📈 OVERALL RESULTS:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {success_rate:.1f}%")

        # Group results by test type
        test_types = {}
        for result in self.test_results:
            test_type = result["test_type"]
            if test_type not in test_types:
                test_types[test_type] = {"passed": 0, "failed": 0, "total": 0}

            test_types[test_type]["total"] += 1
            if result["success"]:
                test_types[test_type]["passed"] += 1
            else:
                test_types[test_type]["failed"] += 1

        print("\n📊 RESULTS BY TEST TYPE:")
        for test_type, stats in test_types.items():
            type_success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"  {test_type.replace('_', ' ').title()}: {stats['passed']}/{stats['total']} ({type_success_rate:.1f}%)")

        # Show failed tests
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print("\n❌ FAILED TESTS:")
            for result in failed_results:
                print(f"  - {result['test_name']}")
                if "error" in result:
                    print(f"    Error: {result['error']}")

        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate
            },
            "test_types": test_types,
            "detailed_results": self.test_results
        }

        report_filename = f"routing_aware_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n💾 Detailed report saved to: {report_filename}")

        # Overall assessment
        if success_rate >= 90:
            print("\n🎉 EXCELLENT: Routing - aware functionality is working excellently!")
        elif success_rate >= 75:
            print("\n✅ GOOD: Routing - aware functionality is working well with minor issues.")
        elif success_rate >= 50:
            print("\n⚠️ NEEDS WORK: Routing - aware functionality has significant issues.")
        else:
            print("\n❌ CRITICAL: Routing - aware functionality has major problems.")

        return report_data


def main():
    """Run the routing-aware test suite"""
    print("🎯 Routing-Aware Agenta SDK Manager Test Suite")
    print("Testing the integration between TLRS routing logic and Agenta.ai")

    test_suite = RoutingAwareTestSuite()
    test_suite.run_all_tests()

    # Calculate success rate from test results
    total_tests = len(test_suite.test_results)
    passed_tests = sum(1 for result in test_suite.test_results if result["success"])
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    return success_rate >= 75


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
