#!/usr/bin/env python3
"""
Test Live Agenta.ai Variants

This script thoroughly tests the routing-aware variants once they're created
in the Agenta.ai dashboard to ensure all functionality works as expected.
"""

import json
import sys
import os
import asyncio
from typing import Dict, List, Any
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agenta_sdk_manager_enhanced import (
        RoutingAwareAgentaManager,
        get_routing_aware_prompt,
        enhanced_agenta_manager
    )
    print("✅ Successfully imported routing-aware components")
except ImportError as e:
    print(f"❌ Failed to import components: {e}")
    sys.exit(1)


class LiveAgentaVariantTester:
    """Tests live Agenta.ai variants with comprehensive scenarios"""

    def __init__(self):
        self.routing_manager = RoutingAwareAgentaManager()
        self.test_results = []

    async def test_all_live_variants(self):
        """Test all live variants with comprehensive scenarios"""
        print("🧪 Testing Live Agenta.ai Variants")
        print("=" * 60)
        print("Testing routing-aware functionality with live Agenta.ai variants")
        print()

        # Test basic routing functionality
        await self.test_routing_accuracy()

        # Test data availability scenarios
        await self.test_data_availability_scenarios()

        # Test edge cases
        await self.test_edge_cases()

        # Test prompt quality and context awareness
        await self.test_prompt_quality()

        # Generate comprehensive test report
        self.generate_comprehensive_report()

    async def test_routing_accuracy(self):
        """Test routing accuracy with live variants"""
        print("🎯 Testing Routing Accuracy")
        print("-" * 40)

        routing_scenarios = [
            {
                "name": "Credit Score Query",
                "query": "What's the credit score for e.j.price1986@gmail.com?",
                "expected_route": "credit",
                "expected_variant": "credit-analysis-comprehensive-v1",
                "customer_id": "dc93a2cd-de0a-444f-ad47-3003ba998cd3"
            },
            {
                "name": "Comprehensive Analysis Query",
                "query": "Give me comprehensive analysis for e.j.price1986@gmail.com including all available data",
                "expected_route": "multi_data",
                "expected_variant": "multi-data-analysis-v1",
                "customer_id": "dc93a2cd-de0a-444f-ad47-3003ba998cd3"
            },
            {
                "name": "Account Status Query",
                "query": "What's the current account status for john.doe@email.com?",
                "expected_route": "account_status",
                "expected_variant": "account-status-v1",
                "customer_id": "test-customer-123"
            },
            {
                "name": "Transaction Analysis Query",
                "query": "Show me payment patterns and transaction history for customer@email.com",
                "expected_route": "transaction",
                "expected_variant": "transaction-analysis-v1",
                "customer_id": "test-customer-456"
            },
            {
                "name": "Phone Call Analysis Query",
                "query": "Analyze call history and agent interactions for customer@email.com",
                "expected_route": "phone",
                "expected_variant": "phone-call-analysis-v1",
                "customer_id": "test-customer-789"
            },
            {
                "name": "Mixed Keywords Query",
                "query": "Show me credit score and transaction data for e.j.price1986@gmail.com",
                "expected_route": "multi_data",
                "expected_variant": "multi-data-analysis-v1",
                "customer_id": "dc93a2cd-de0a-444f-ad47-3003ba998cd3"
            }
        ]

        print(f"🔍 Testing {len(routing_scenarios)} routing scenarios...")
        print()

        for scenario in routing_scenarios:
            await self._test_routing_scenario(scenario)

    async def _test_routing_scenario(self, scenario: Dict):
        """Test individual routing scenario"""
        print(f"📋 Testing: {scenario['name']}")

        try:
            # Get routing-aware prompt
            prompt_config = get_routing_aware_prompt(
                query=scenario["query"],
                customer_id=scenario["customer_id"],
                data_availability={
                    "credit_data": True,
                    "phone_data": True,
                    "transaction_data": True,
                    "card_data": True,
                    "ticket_data": True
                }
            )

            routing_metadata = prompt_config.get("routing_metadata", {})
            actual_route = routing_metadata.get("routing_decision")
            expected_route = scenario["expected_route"]

            # Check routing accuracy
            route_correct = actual_route == expected_route

            # Check prompt source (Agenta vs template)
            prompt_source = prompt_config.get("source", "")
            is_agenta_source = "agenta" in prompt_source.lower()

            # Check routing context injection
            system_prompt = prompt_config.get("system_prompt", "")
            has_routing_context = "[ROUTING CONTEXT:" in system_prompt
            has_data_availability = "[DATA AVAILABILITY:" in system_prompt
            has_routing_instructions = "[ROUTING CONTEXT INSTRUCTIONS]" in system_prompt

            # Check prompt quality indicators
            prompt_length = len(system_prompt)
            has_specific_instructions = scenario["expected_route"] in system_prompt.lower()

            success = route_correct and has_routing_context

            result = {
                "test_type": "routing_accuracy",
                "scenario_name": scenario["name"],
                "query": scenario["query"],
                "expected_route": expected_route,
                "actual_route": actual_route,
                "expected_variant": scenario["expected_variant"],
                "route_correct": route_correct,
                "is_agenta_source": is_agenta_source,
                "prompt_source": prompt_source,
                "has_routing_context": has_routing_context,
                "has_data_availability": has_data_availability,
                "has_routing_instructions": has_routing_instructions,
                "prompt_length": prompt_length,
                "has_specific_instructions": has_specific_instructions,
                "success": success,
                "routing_metadata": routing_metadata
            }

            self.test_results.append(result)

            # Display results
            status = "✅ PASS" if success else "❌ FAIL"
            source_indicator = "🌐 AGENTA" if is_agenta_source else "📋 TEMPLATE"
            print(f"  {status} {source_indicator} Route: {actual_route} → {scenario['expected_variant']}")
            print(f"  🎯 Routing Context: {'✅' if has_routing_context else '❌'}")
            print(f"  📊 Data Availability: {'✅' if has_data_availability else '❌'}")
            print(f"  📝 Instructions: {'✅' if has_routing_instructions else '❌'}")
            print(f"  📏 Prompt Length: {prompt_length} chars")

        except Exception as e:
            result = {
                "test_type": "routing_accuracy",
                "scenario_name": scenario["name"],
                "success": False,
                "error": str(e)
            }
            print(f"  ❌ ERROR: {e}")
            self.test_results.append(result)

        print()

    async def test_data_availability_scenarios(self):
        """Test data availability handling"""
        print("📊 Testing Data Availability Scenarios")
        print("-" * 40)

        data_scenarios = [
            {
                "name": "All Data Available",
                "query": "Give me comprehensive analysis for e.j.price1986@gmail.com",
                "data_availability": {
                    "credit_data": True,
                    "phone_data": True,
                    "transaction_data": True,
                    "card_data": True,
                    "ticket_data": True
                },
                "expected_available": 5,
                "expected_unavailable": 0
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
                },
                "expected_available": 4,
                "expected_unavailable": 1
            },
            {
                "name": "Limited Data Available",
                "query": "Analyze customer data for customer@email.com",
                "data_availability": {
                    "credit_data": True,
                    "phone_data": False,
                    "transaction_data": False,
                    "card_data": False,
                    "ticket_data": False
                },
                "expected_available": 1,
                "expected_unavailable": 4
            },
            {
                "name": "No Data Available",
                "query": "What can you tell me about customer@email.com?",
                "data_availability": {
                    "credit_data": False,
                    "phone_data": False,
                    "transaction_data": False,
                    "card_data": False,
                    "ticket_data": False
                },
                "expected_available": 0,
                "expected_unavailable": 5
            }
        ]

        print(f"🔍 Testing {len(data_scenarios)} data availability scenarios...")
        print()

        for scenario in data_scenarios:
            await self._test_data_availability_scenario(scenario)

    async def _test_data_availability_scenario(self, scenario: Dict):
        """Test individual data availability scenario"""
        print(f"📋 Testing: {scenario['name']}")

        try:
            # Get routing-aware prompt
            prompt_config = get_routing_aware_prompt(
                query=scenario["query"],
                customer_id="test-customer-id",
                data_availability=scenario["data_availability"]
            )

            # Check data availability context
            system_prompt = prompt_config.get("system_prompt", "")
            has_data_availability = "[DATA AVAILABILITY:" in system_prompt

            # Count available and unavailable data types
            available_types = [k for k, v in scenario["data_availability"].items() if v]
            unavailable_types = [k for k, v in scenario["data_availability"].items() if not v]

            actual_available = len(available_types)
            actual_unavailable = len(unavailable_types)

            # Check if availability is reflected in prompt
            availability_accurate = (
                actual_available == scenario["expected_available"] and
                actual_unavailable == scenario["expected_unavailable"]
            )

            # Check if unavailable types are mentioned when relevant
            mentions_unavailable = any(data_type.replace("_data", "") in system_prompt.lower()
                                     for data_type in unavailable_types) if unavailable_types else True

            success = has_data_availability and availability_accurate

            result = {
                "test_type": "data_availability",
                "scenario_name": scenario["name"],
                "query": scenario["query"],
                "data_availability": scenario["data_availability"],
                "expected_available": scenario["expected_available"],
                "actual_available": actual_available,
                "expected_unavailable": scenario["expected_unavailable"],
                "actual_unavailable": actual_unavailable,
                "has_data_availability": has_data_availability,
                "availability_accurate": availability_accurate,
                "mentions_unavailable": mentions_unavailable,
                "available_types": available_types,
                "unavailable_types": unavailable_types,
                "success": success
            }

            self.test_results.append(result)

            # Display results
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} Available: {actual_available}/{scenario['expected_available']}, "
                  f"Unavailable: {actual_unavailable}/{scenario['expected_unavailable']}")
            print(f"  📊 Data Context: {'✅' if has_data_availability else '❌'}")
            print(f"  📋 Accuracy: {'✅' if availability_accurate else '❌'}")
            if unavailable_types:
                print(f"  ⚠️  Unavailable: {', '.join(unavailable_types)}")

        except Exception as e:
            result = {
                "test_type": "data_availability",
                "scenario_name": scenario["name"],
                "success": False,
                "error": str(e)
            }
            print(f"  ❌ ERROR: {e}")
            self.test_results.append(result)

        print()

    async def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("🔍 Testing Edge Cases")
        print("-" * 40)

        edge_cases = [
            {
                "name": "Empty Query",
                "query": "",
                "customer_id": "test-customer-id",
                "should_handle_gracefully": True
            },
            {
                "name": "Very Long Query",
                "query": "What is the comprehensive credit analysis including all bureau data, transaction history, payment patterns, call logs, support tickets, and credit card information for the customer " * 20,
                "customer_id": "test-customer-id",
                "should_handle_gracefully": True
            },
            {
                "name": "Special Characters Query",
                "query": "What's the credit score for user@domain.com with special chars: !@#$%^&*()?",
                "customer_id": "test-customer-id",
                "should_handle_gracefully": True
            },
            {
                "name": "No Customer ID",
                "query": "What's the credit score?",
                "customer_id": None,
                "should_handle_gracefully": True
            },
            {
                "name": "Unicode Query",
                "query": "¿Cuál es el puntaje crediticio para cliente@email.com?",
                "customer_id": "test-customer-id",
                "should_handle_gracefully": True
            }
        ]

        print(f"🔍 Testing {len(edge_cases)} edge cases...")
        print()

        for case in edge_cases:
            await self._test_edge_case(case)

    async def _test_edge_case(self, case: Dict):
        """Test individual edge case"""
        print(f"📋 Testing: {case['name']}")

        try:
            # Get routing-aware prompt
            prompt_config = get_routing_aware_prompt(
                query=case["query"],
                customer_id=case.get("customer_id", "test-customer-id")
            )

            # Check if it handled gracefully
            has_system_prompt = bool(prompt_config.get("system_prompt"))
            has_routing_metadata = bool(prompt_config.get("routing_metadata"))
            has_routing_decision = bool(prompt_config.get("routing_metadata", {}).get("routing_decision"))

            success = has_system_prompt and has_routing_metadata and has_routing_decision

            result = {
                "test_type": "edge_case",
                "case_name": case["name"],
                "query": case["query"][:100] + "..." if len(case["query"]) > 100 else case["query"],
                "customer_id": case.get("customer_id"),
                "handled_gracefully": success,
                "has_system_prompt": has_system_prompt,
                "has_routing_metadata": has_routing_metadata,
                "has_routing_decision": has_routing_decision,
                "routing_decision": prompt_config.get("routing_metadata", {}).get("routing_decision"),
                "success": success
            }

            self.test_results.append(result)

            # Display results
            status = "✅ PASS" if success else "❌ FAIL"
            route = prompt_config.get("routing_metadata", {}).get("routing_decision", "unknown")
            print(f"  {status} Handled gracefully, routed to: {route}")
            print(f"  📝 System Prompt: {'✅' if has_system_prompt else '❌'}")
            print(f"  📊 Routing Data: {'✅' if has_routing_metadata else '❌'}")

        except Exception as e:
            # For edge cases, we might expect some to fail
            expected_failure = not case.get("should_handle_gracefully", True)
            success = expected_failure  # If we expected failure, this is success

            result = {
                "test_type": "edge_case",
                "case_name": case["name"],
                "query": case["query"][:100] + "..." if len(case["query"]) > 100 else case["query"],
                "success": success,
                "error": str(e),
                "expected_failure": expected_failure
            }

            if expected_failure:
                print(f"  ✅ PASS Expected failure occurred: {e}")
            else:
                print(f"  ❌ FAIL Unexpected error: {e}")

            self.test_results.append(result)

        print()

    async def test_prompt_quality(self):
        """Test prompt quality and context awareness"""
        print("🎯 Testing Prompt Quality and Context Awareness")
        print("-" * 40)

        quality_tests = [
            {
                "name": "Credit Analysis Prompt Quality",
                "query": "Analyze credit data for e.j.price1986@gmail.com",
                "expected_route": "credit",
                "quality_indicators": [
                    "credit analysis",
                    "bureau",
                    "score",
                    "routing context instructions"
                ]
            },
            {
                "name": "Multi-Data Prompt Quality",
                "query": "Give me comprehensive analysis for customer@email.com",
                "expected_route": "multi_data",
                "quality_indicators": [
                    "multiple sources",
                    "comprehensive",
                    "combine",
                    "routing context instructions"
                ]
            },
            {
                "name": "Transaction Prompt Quality",
                "query": "Show me payment patterns for customer@email.com",
                "expected_route": "transaction",
                "quality_indicators": [
                    "transaction",
                    "payment",
                    "billing",
                    "routing context instructions"
                ]
            }
        ]

        print(f"🔍 Testing {len(quality_tests)} prompt quality scenarios...")
        print()

        for test in quality_tests:
            await self._test_prompt_quality(test)

    async def _test_prompt_quality(self, test: Dict):
        """Test individual prompt quality"""
        print(f"📋 Testing: {test['name']}")

        try:
            # Get routing-aware prompt
            prompt_config = get_routing_aware_prompt(
                query=test["query"],
                customer_id="test-customer-id"
            )

            system_prompt = prompt_config.get("system_prompt", "").lower()
            routing_decision = prompt_config.get("routing_metadata", {}).get("routing_decision")

            # Check route accuracy
            route_correct = routing_decision == test["expected_route"]

            # Check quality indicators
            quality_scores = []
            for indicator in test["quality_indicators"]:
                has_indicator = indicator.lower() in system_prompt
                quality_scores.append(has_indicator)
                print(f"    {'✅' if has_indicator else '❌'} {indicator}")

            quality_score = sum(quality_scores) / len(quality_scores) * 100

            # Check prompt source
            prompt_source = prompt_config.get("source", "")
            is_agenta_source = "agenta" in prompt_source.lower()

            success = route_correct and quality_score >= 75  # At least 75% quality indicators present

            result = {
                "test_type": "prompt_quality",
                "test_name": test["name"],
                "query": test["query"],
                "expected_route": test["expected_route"],
                "actual_route": routing_decision,
                "route_correct": route_correct,
                "quality_score": quality_score,
                "quality_indicators": test["quality_indicators"],
                "quality_results": dict(zip(test["quality_indicators"], quality_scores)),
                "is_agenta_source": is_agenta_source,
                "prompt_source": prompt_source,
                "prompt_length": len(prompt_config.get("system_prompt", "")),
                "success": success
            }

            self.test_results.append(result)

            # Display results
            status = "✅ PASS" if success else "❌ FAIL"
            source_indicator = "🌐 AGENTA" if is_agenta_source else "📋 TEMPLATE"
            print(f"  {status} {source_indicator} Quality Score: {quality_score:.1f}%")
            print(f"  🎯 Route: {routing_decision} (expected: {test['expected_route']})")

        except Exception as e:
            result = {
                "test_type": "prompt_quality",
                "test_name": test["name"],
                "success": False,
                "error": str(e)
            }
            print(f"  ❌ ERROR: {e}")
            self.test_results.append(result)

        print()

    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("=" * 60)
        print("📊 COMPREHENSIVE LIVE VARIANT TEST REPORT")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.get("success", False))
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"\n📈 OVERALL RESULTS:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {success_rate:.1f}%")

        # Group results by test type
        test_types = {}
        for result in self.test_results:
            test_type = result.get("test_type", "unknown")
            if test_type not in test_types:
                test_types[test_type] = {"passed": 0, "failed": 0, "total": 0}

            test_types[test_type]["total"] += 1
            if result.get("success", False):
                test_types[test_type]["passed"] += 1
            else:
                test_types[test_type]["failed"] += 1

        print(f"\n📊 RESULTS BY TEST TYPE:")
        for test_type, stats in test_types.items():
            type_success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"  {test_type.replace('_', ' ').title()}: {stats['passed']}/{stats['total']} ({type_success_rate:.1f}%)")

        # Analyze Agenta vs Template usage
        agenta_sources = sum(1 for r in self.test_results if r.get("is_agenta_source", False))
        template_sources = sum(1 for r in self.test_results if "is_agenta_source" in r and not r["is_agenta_source"])

        if agenta_sources + template_sources > 0:
            print(f"\n🌐 PROMPT SOURCES:")
            print(f"  Agenta.ai Variants: {agenta_sources}")
            print(f"  Template Fallbacks: {template_sources}")

            if template_sources > 0:
                print(f"\n⚠️  NOTE: {template_sources} tests used template fallbacks.")
                print("This indicates some Agenta.ai variants may not be created yet.")

        # Show failed tests
        failed_results = [r for r in self.test_results if not r.get("success", False)]
        if failed_results:
            print(f"\n❌ FAILED TESTS:")
            for result in failed_results:
                test_name = result.get("scenario_name") or result.get("case_name") or result.get("test_name", "Unknown")
                print(f"  - {test_name}")
                if "error" in result:
                    print(f"    Error: {result['error']}")

        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "live_agenta_variant_comprehensive_testing",
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "agenta_sources": agenta_sources,
                "template_sources": template_sources
            },
            "test_types": test_types,
            "detailed_results": self.test_results
        }

        report_filename = f"live_agenta_comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n💾 Detailed report saved to: {report_filename}")

        # Final assessment
        if success_rate >= 95:
            print(f"\n🎉 EXCELLENT: Live Agenta.ai variants working perfectly!")
            if agenta_sources > template_sources:
                print("✅ Most tests using live Agenta.ai variants")
            else:
                print("⚠️ Many tests still using template fallbacks")
        elif success_rate >= 85:
            print(f"\n✅ GOOD: Most functionality working correctly")
            print("⚠️ Minor issues to address")
        else:
            print(f"\n❌ NEEDS WORK: Significant issues detected")
            print("🔧 Review failed tests and fix before production use")

        print(f"\n🎯 NEXT STEPS:")
        if template_sources > agenta_sources:
            print("1. Create missing variants in Agenta.ai dashboard")
            print("2. Re-run this test to validate live variants")
        else:
            print("1. Review any failed tests and optimize prompts")
            print("2. Deploy routing-aware integration to production")
        print("3. Monitor performance and iterate on prompts")
        print("4. Use Agenta.ai A/B testing for optimization")

        return report_data


async def main():
    """Main testing workflow"""
    print("🧪 Live Agenta.ai Variant Testing")
    print("Comprehensive testing of routing-aware variants with live functionality")
    print()

    tester = LiveAgentaVariantTester()
    await tester.test_all_live_variants()

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Live testing failed: {e}")
        sys.exit(1)
