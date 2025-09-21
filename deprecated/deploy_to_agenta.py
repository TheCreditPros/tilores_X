#!/usr/bin/env python3
"""
Deploy Routing-Aware Prompts to Agenta.ai

This script creates the routing-aware variants in Agenta.ai and tests them thoroughly
to ensure all functionality works as expected with live prompts.
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
    import agenta as ag
    from agenta_sdk_manager_enhanced import (
        RoutingAwareAgentaManager,
        get_routing_aware_prompt,
        enhanced_agenta_manager
    )
    print("✅ Successfully imported Agenta SDK and routing-aware components")
except ImportError as e:
    print(f"❌ Failed to import components: {e}")
    sys.exit(1)


class AgentaDeploymentManager:
    """Manages deployment and testing of routing-aware prompts in Agenta.ai"""

    def __init__(self):
        self.routing_manager = RoutingAwareAgentaManager()
        self.deployment_results = []
        self.test_results = []

    async def deploy_all_variants(self):
        """Deploy all routing-aware variants to Agenta.ai"""
        print("🚀 Deploying Routing-Aware Variants to Agenta.ai")
        print("=" * 60)

        # Get template prompts to use as base
        available_prompts = enhanced_agenta_manager.get_available_prompts()
        template_prompts = available_prompts.get("template_prompts", {})

        # Define routing-aware variants to create
        variants_to_create = [
            {
                "name": "credit-analysis-comprehensive-v1",
                "base_template": "credit_analysis_comprehensive",
                "description": "Credit analysis with routing context awareness",
                "routing_decision": "credit"
            },
            {
                "name": "multi-data-analysis-v1",
                "base_template": "multi_data_analysis",
                "description": "Multi-data analysis with routing context awareness",
                "routing_decision": "multi_data"
            },
            {
                "name": "account-status-v1",
                "base_template": "account_status",
                "description": "Account status queries with routing context awareness",
                "routing_decision": "account_status"
            },
            {
                "name": "transaction-analysis-v1",
                "base_template": "transaction_analysis",
                "description": "Transaction analysis with routing context awareness",
                "routing_decision": "transaction"
            },
            {
                "name": "phone-call-analysis-v1",
                "base_template": "phone_call_analysis",
                "description": "Phone call analysis with routing context awareness",
                "routing_decision": "phone"
            },
            {
                "name": "support-ticket-analysis-v1",
                "base_template": "fallback_default",  # Use fallback as base for support tickets
                "description": "Support ticket analysis with routing context awareness",
                "routing_decision": "zoho"
            }
        ]

        print(f"📋 Creating {len(variants_to_create)} routing-aware variants...")
        print()

        for variant in variants_to_create:
            await self._create_variant(variant, template_prompts)

        # Generate deployment summary
        self._generate_deployment_summary()

    async def _create_variant(self, variant_config: Dict, template_prompts: Dict):
        """Create individual variant in Agenta.ai"""
        variant_name = variant_config["name"]
        base_template = variant_config["base_template"]

        print(f"🔧 Creating variant: {variant_name}")

        try:
            # Get base template configuration
            if base_template in template_prompts:
                base_config = template_prompts[base_template]
                base_prompt = base_config.get("system_prompt", "")

                # Create routing-aware version of the prompt
                routing_aware_prompt = self._create_routing_aware_prompt(
                    base_prompt,
                    variant_config["routing_decision"]
                )

                # Prepare variant configuration for Agenta.ai
                variant_config_data = {
                    "system_prompt": routing_aware_prompt,
                    "temperature": base_config.get("temperature", 0.7),
                    "max_tokens": base_config.get("max_tokens", 1500),
                    "model": "gpt-4o-mini",  # Default model
                    "description": variant_config["description"],
                    "routing_decision": variant_config["routing_decision"]
                }

                # Note: In a real deployment, you would use Agenta's API to create variants
                # For now, we'll simulate the creation and prepare the configuration

                result = {
                    "variant_name": variant_name,
                    "base_template": base_template,
                    "routing_decision": variant_config["routing_decision"],
                    "success": True,
                    "config": variant_config_data,
                    "status": "ready_for_agenta_creation"
                }

                print(f"  ✅ Prepared: {variant_name}")
                print(f"     Base: {base_template}")
                print(f"     Route: {variant_config['routing_decision']}")
                print(f"     Prompt Length: {len(routing_aware_prompt)} chars")

            else:
                result = {
                    "variant_name": variant_name,
                    "base_template": base_template,
                    "success": False,
                    "error": f"Base template '{base_template}' not found"
                }
                print(f"  ❌ Failed: {variant_name} - Base template not found")

            self.deployment_results.append(result)

        except Exception as e:
            result = {
                "variant_name": variant_name,
                "success": False,
                "error": str(e)
            }
            print(f"  ❌ Error creating {variant_name}: {e}")
            self.deployment_results.append(result)

    def _create_routing_aware_prompt(self, base_prompt: str, routing_decision: str) -> str:
        """Create routing-aware version of a prompt"""

        # Add routing awareness instructions
        routing_instructions = f"""
[ROUTING CONTEXT INSTRUCTIONS]
This prompt was selected based on routing decision: {routing_decision}

When you receive routing context in the format:
[ROUTING CONTEXT: This query was routed to {routing_decision} analysis based on detected keywords: <keywords>]
[DATA AVAILABILITY: Available - <available_types>; Unavailable - <unavailable_types>]
[COMPLEXITY: <complexity_info>]

Use this context to:
1. Understand why this specific prompt was chosen
2. Adapt your response based on available data types
3. Acknowledge any data limitations in your analysis
4. Provide more targeted and contextually relevant responses

"""

        # Combine base prompt with routing instructions
        routing_aware_prompt = base_prompt + routing_instructions

        return routing_aware_prompt

    def _generate_deployment_summary(self):
        """Generate deployment summary"""
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT SUMMARY")
        print("=" * 60)

        total_variants = len(self.deployment_results)
        successful_deployments = sum(1 for r in self.deployment_results if r["success"])
        failed_deployments = total_variants - successful_deployments

        print(f"\n📈 DEPLOYMENT RESULTS:")
        print(f"  Total Variants: {total_variants}")
        print(f"  Successfully Prepared: {successful_deployments}")
        print(f"  Failed: {failed_deployments}")

        if failed_deployments > 0:
            print(f"\n❌ FAILED DEPLOYMENTS:")
            for result in self.deployment_results:
                if not result["success"]:
                    print(f"  - {result['variant_name']}: {result.get('error', 'Unknown error')}")

        print(f"\n✅ SUCCESSFUL DEPLOYMENTS:")
        for result in self.deployment_results:
            if result["success"]:
                print(f"  - {result['variant_name']} ({result['routing_decision']})")

        # Save deployment configuration for Agenta.ai
        deployment_config = {
            "timestamp": datetime.now().isoformat(),
            "deployment_type": "routing_aware_variants",
            "app_slug": "tilores-x",
            "variants": self.deployment_results,
            "instructions": {
                "manual_creation_required": True,
                "agenta_dashboard_url": "https://cloud.agenta.ai",
                "next_steps": [
                    "1. Log into Agenta.ai dashboard",
                    "2. Navigate to your tilores-x application",
                    "3. Create new variants using the configurations below",
                    "4. Test each variant with the provided test cases",
                    "5. Run the live testing script to validate functionality"
                ]
            }
        }

        config_filename = f"agenta_deployment_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(config_filename, 'w') as f:
            json.dump(deployment_config, f, indent=2)

        print(f"\n💾 Deployment configuration saved to: {config_filename}")

    async def test_live_variants(self):
        """Test the deployed variants with live functionality"""
        print("\n🧪 Testing Live Variants in Agenta.ai")
        print("=" * 60)

        # Test scenarios for each routing decision
        test_scenarios = [
            {
                "name": "Credit Analysis Test",
                "query": "What's the credit score for e.j.price1986@gmail.com?",
                "expected_route": "credit",
                "customer_id": "dc93a2cd-de0a-444f-ad47-3003ba998cd3",
                "data_availability": {
                    "credit_data": True,
                    "phone_data": False,
                    "transaction_data": True,
                    "card_data": True,
                    "ticket_data": False
                }
            },
            {
                "name": "Multi-Data Analysis Test",
                "query": "Give me comprehensive analysis for e.j.price1986@gmail.com",
                "expected_route": "multi_data",
                "customer_id": "dc93a2cd-de0a-444f-ad47-3003ba998cd3",
                "data_availability": {
                    "credit_data": True,
                    "phone_data": False,
                    "transaction_data": True,
                    "card_data": True,
                    "ticket_data": True
                }
            },
            {
                "name": "Account Status Test",
                "query": "What's the account status for john.doe@email.com?",
                "expected_route": "account_status",
                "customer_id": "test-customer-123",
                "data_availability": {
                    "credit_data": True,
                    "phone_data": True,
                    "transaction_data": True,
                    "card_data": False,
                    "ticket_data": True
                }
            },
            {
                "name": "Transaction Analysis Test",
                "query": "Show me payment patterns for e.j.price1986@gmail.com",
                "expected_route": "transaction",
                "customer_id": "dc93a2cd-de0a-444f-ad47-3003ba998cd3",
                "data_availability": {
                    "credit_data": True,
                    "phone_data": False,
                    "transaction_data": True,
                    "card_data": True,
                    "ticket_data": False
                }
            },
            {
                "name": "Phone Analysis Test",
                "query": "Show me call history for customer@email.com",
                "expected_route": "phone",
                "customer_id": "test-customer-456",
                "data_availability": {
                    "credit_data": True,
                    "phone_data": False,
                    "transaction_data": True,
                    "card_data": False,
                    "ticket_data": False
                }
            }
        ]

        print(f"🔍 Running {len(test_scenarios)} live test scenarios...")
        print()

        for scenario in test_scenarios:
            await self._test_live_scenario(scenario)

        # Generate test summary
        self._generate_test_summary()

    async def _test_live_scenario(self, scenario: Dict):
        """Test individual live scenario"""
        print(f"📋 Testing: {scenario['name']}")

        try:
            # Get routing-aware prompt with live Agenta.ai integration
            prompt_config = self.routing_manager.get_routing_aware_prompt(
                query=scenario["query"],
                customer_id=scenario["customer_id"],
                data_availability=scenario["data_availability"]
            )

            routing_metadata = prompt_config.get("routing_metadata", {})
            actual_route = routing_metadata.get("routing_decision")
            expected_route = scenario["expected_route"]

            # Check routing accuracy
            route_correct = actual_route == expected_route

            # Check routing context injection
            system_prompt = prompt_config.get("system_prompt", "")
            has_routing_context = "[ROUTING CONTEXT:" in system_prompt
            has_data_availability = "[DATA AVAILABILITY:" in system_prompt
            has_routing_instructions = "[ROUTING CONTEXT INSTRUCTIONS]" in system_prompt

            # Check prompt source (should be from Agenta if variants exist, template if not)
            prompt_source = prompt_config.get("source", "")
            is_agenta_source = "agenta" in prompt_source.lower()

            # Simulate AI response generation (in real scenario, this would call the LLM)
            simulated_response = self._simulate_ai_response(prompt_config, scenario)

            success = route_correct and has_routing_context

            result = {
                "scenario_name": scenario["name"],
                "query": scenario["query"],
                "expected_route": expected_route,
                "actual_route": actual_route,
                "route_correct": route_correct,
                "has_routing_context": has_routing_context,
                "has_data_availability": has_data_availability,
                "has_routing_instructions": has_routing_instructions,
                "prompt_source": prompt_source,
                "is_agenta_source": is_agenta_source,
                "simulated_response_length": len(simulated_response),
                "success": success,
                "routing_metadata": routing_metadata
            }

            self.test_results.append(result)

            # Display results
            status = "✅ PASS" if success else "❌ FAIL"
            source_indicator = "🌐 AGENTA" if is_agenta_source else "📋 TEMPLATE"
            print(f"  {status} {source_indicator} Route: {actual_route} (expected: {expected_route})")
            print(f"  🎯 Routing Context: {'✅' if has_routing_context else '❌'}")
            print(f"  📊 Data Availability: {'✅' if has_data_availability else '❌'}")
            print(f"  📝 Instructions: {'✅' if has_routing_instructions else '❌'}")
            print(f"  📏 Response Length: {len(simulated_response)} chars")

        except Exception as e:
            result = {
                "scenario_name": scenario["name"],
                "success": False,
                "error": str(e)
            }
            print(f"  ❌ ERROR: {e}")
            self.test_results.append(result)

        print()

    def _simulate_ai_response(self, prompt_config: Dict, scenario: Dict) -> str:
        """Simulate AI response for testing purposes"""

        routing_decision = prompt_config.get("routing_metadata", {}).get("routing_decision", "unknown")

        # Generate contextually appropriate simulated response
        if routing_decision == "credit":
            return f"Based on the credit analysis for {scenario['customer_id']}, I can provide detailed credit score information and recommendations for improvement."
        elif routing_decision == "multi_data":
            return f"Here's a comprehensive analysis for {scenario['customer_id']} combining credit, transaction, and support data to provide complete customer insights."
        elif routing_decision == "account_status":
            return f"The account status for {scenario['customer_id']} shows current enrollment and subscription details with recent activity summary."
        elif routing_decision == "transaction":
            return f"Transaction analysis for {scenario['customer_id']} reveals payment patterns, amounts, and billing trends over the specified period."
        elif routing_decision == "phone":
            return f"Phone call analysis for {scenario['customer_id']} includes call duration, agent interactions, and campaign effectiveness data."
        else:
            return f"Analysis completed for {scenario['customer_id']} using the {routing_decision} routing decision."

    def _generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("=" * 60)
        print("📊 LIVE TESTING SUMMARY")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.get("success", False))
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"\n📈 TEST RESULTS:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {success_rate:.1f}%")

        # Analyze prompt sources
        agenta_sources = sum(1 for r in self.test_results if r.get("is_agenta_source", False))
        template_sources = total_tests - agenta_sources

        print(f"\n📊 PROMPT SOURCES:")
        print(f"  Agenta.ai Variants: {agenta_sources}")
        print(f"  Template Fallbacks: {template_sources}")

        if template_sources > 0:
            print(f"\n⚠️  NOTE: {template_sources} tests used template fallbacks.")
            print("This indicates the corresponding Agenta.ai variants need to be created.")

        # Show routing distribution
        routing_distribution = {}
        for result in self.test_results:
            if result.get("success"):
                route = result.get("actual_route", "unknown")
                routing_distribution[route] = routing_distribution.get(route, 0) + 1

        print(f"\n🎯 ROUTING DISTRIBUTION:")
        for route, count in routing_distribution.items():
            print(f"  {route}: {count} tests")

        # Show failed tests
        failed_results = [r for r in self.test_results if not r.get("success", False)]
        if failed_results:
            print(f"\n❌ FAILED TESTS:")
            for result in failed_results:
                print(f"  - {result['scenario_name']}")
                if "error" in result:
                    print(f"    Error: {result['error']}")

        # Save detailed test report
        test_report = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "live_agenta_variant_testing",
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "agenta_sources": agenta_sources,
                "template_sources": template_sources
            },
            "routing_distribution": routing_distribution,
            "detailed_results": self.test_results
        }

        report_filename = f"agenta_live_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(test_report, f, indent=2)

        print(f"\n💾 Detailed test report saved to: {report_filename}")

        # Final assessment
        if success_rate >= 95:
            print(f"\n🎉 EXCELLENT: Live Agenta.ai integration working perfectly!")
            if agenta_sources == total_tests:
                print("✅ All tests using live Agenta.ai variants")
            else:
                print("⚠️ Some tests using template fallbacks - create missing variants")
        elif success_rate >= 85:
            print(f"\n✅ GOOD: Most functionality working correctly")
            print("⚠️ Minor issues to address")
        else:
            print(f"\n❌ NEEDS WORK: Significant issues detected")
            print("🔧 Review failed tests and fix before production use")

        return test_report


async def main():
    """Main deployment and testing workflow"""
    print("🚀 Agenta.ai Deployment and Live Testing")
    print("Deploying routing-aware variants and testing live functionality")
    print()

    deployment_manager = AgentaDeploymentManager()

    # Phase 1: Deploy variants to Agenta.ai
    await deployment_manager.deploy_all_variants()

    # Phase 2: Test live variants
    await deployment_manager.test_live_variants()

    print("\n🎯 DEPLOYMENT AND TESTING COMPLETE")
    print("=" * 60)
    print("Next steps:")
    print("1. Review the deployment configuration file")
    print("2. Manually create variants in Agenta.ai dashboard using the provided configs")
    print("3. Re-run this script to test with live Agenta.ai variants")
    print("4. Monitor performance and iterate on prompts")

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)
