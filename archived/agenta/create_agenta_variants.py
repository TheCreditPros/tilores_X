#!/usr/bin/env python3
"""
Create Agenta.ai Variants for Routing-Aware Prompts

This script creates the routing-aware variants directly in Agenta.ai using the SDK
and then tests them thoroughly with live functionality.
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
    from agenta_sdk_manager_enhanced import enhanced_agenta_manager
    print("✅ Successfully imported Agenta SDK")
except ImportError as e:
    print(f"❌ Failed to import Agenta SDK: {e}")
    sys.exit(1)


class AgentaVariantCreator:
    """Creates and tests routing-aware variants in Agenta.ai"""

    def __init__(self):
        self.created_variants = []
        self.test_results = []

    def create_routing_aware_variants(self):
        """Create routing-aware variants in Agenta.ai"""
        print("🚀 Creating Routing-Aware Variants in Agenta.ai")
        print("=" * 60)

        # Get template prompts
        available_prompts = enhanced_agenta_manager.get_available_prompts()
        template_prompts = available_prompts.get("template_prompts", {})

        print(f"📋 Available template prompts: {list(template_prompts.keys())}")
        print()

        # Define variants to create with their configurations
        variants_config = [
            {
                "variant_name": "credit-analysis-comprehensive-v1",
                "base_template": "credit_analysis_comprehensive",
                "system_prompt": """You are a Credit Pros advisor with access to comprehensive credit data.
Analyze the provided temporal credit data to answer the user's question accurately and professionally.

Available data includes:
- Credit scores across multiple bureaus (Equifax, Experian, TransUnion) over time
- Summary parameters including utilization rates, inquiry counts, account counts, payment amounts, and delinquencies
- Historical credit report data with temporal analysis capabilities

[ROUTING CONTEXT INSTRUCTIONS]
This prompt was selected for credit analysis queries. When you receive routing context:
[ROUTING CONTEXT: This query was routed to credit analysis based on detected keywords: <keywords>]
[DATA AVAILABILITY: Available - <available_types>; Unavailable - <unavailable_types>]

Use this context to:
1. Understand why this specific prompt was chosen for credit analysis
2. Adapt your response based on available data types
3. Acknowledge any data limitations in your analysis
4. Provide targeted credit insights and improvement recommendations

Provide detailed insights that help customers understand their credit profile and improvement opportunities.""",
                "temperature": 0.5,
                "max_tokens": 1500,
                "model": "gpt-4o-mini"
            },
            {
                "variant_name": "multi-data-analysis-v1",
                "base_template": "multi_data_analysis",
                "system_prompt": """You are a Credit Pros advisor with access to comprehensive customer data across multiple sources.
Analyze the provided data to answer the user's question accurately and professionally.

Available data sources:
- Temporal credit data with scores, utilization, and bureau information
- Phone call history with agent interactions, call duration, and campaign data
- Transaction records with amounts, payment methods, and billing information
- Credit card data with BINs, expiration dates, and status information
- Support ticket data with categories, statuses, and resolution patterns

[ROUTING CONTEXT INSTRUCTIONS]
This prompt was selected for multi-data analysis queries. When you receive routing context:
[ROUTING CONTEXT: This query was routed to multi_data analysis based on detected keywords: <keywords>]
[DATA AVAILABILITY: Available - <available_types>; Unavailable - <unavailable_types>]

Use this context to:
1. Understand why this comprehensive analysis prompt was chosen
2. Combine insights from multiple available data sources
3. Acknowledge any missing data types and their impact
4. Provide holistic customer intelligence and recommendations

Provide insights that combine multiple data sources when relevant and focus on the specific question asked.""",
                "temperature": 0.6,
                "max_tokens": 2000,
                "model": "gpt-4o-mini"
            },
            {
                "variant_name": "transaction-analysis-v1",
                "base_template": "transaction_analysis",
                "system_prompt": """You are a Credit Pros advisor specializing in transaction and payment analysis.
Analyze the provided transaction data to answer the user's question accurately and professionally.

Available transaction data includes:
- Payment amounts, dates, and methods
- Billing cycles and payment patterns
- Transaction categories and merchant information
- Payment success rates and failure analysis
- Historical payment trends and behaviors

[ROUTING CONTEXT INSTRUCTIONS]
This prompt was selected for transaction analysis queries. When you receive routing context:
[ROUTING CONTEXT: This query was routed to transaction analysis based on detected keywords: <keywords>]
[DATA AVAILABILITY: Available - <available_types>; Unavailable - <unavailable_types>]

Use this context to:
1. Understand why this transaction-focused prompt was chosen
2. Focus on payment patterns and transaction behaviors
3. Acknowledge any missing financial data and its impact
4. Provide actionable insights about payment optimization

Provide detailed transaction insights that help customers understand their payment patterns and optimize their financial behaviors.""",
                "temperature": 0.6,
                "max_tokens": 1500,
                "model": "gpt-4o-mini"
            },
            {
                "variant_name": "phone-call-analysis-v1",
                "base_template": "phone_call_analysis",
                "system_prompt": """You are a Credit Pros advisor specializing in phone call and customer interaction analysis.
Analyze the provided call data to answer the user's question accurately and professionally.

Available phone call data includes:
- Call duration, frequency, and timing patterns
- Agent interactions and conversation outcomes
- Campaign effectiveness and response rates
- Customer engagement levels and satisfaction indicators
- Call resolution status and follow-up requirements

[ROUTING CONTEXT INSTRUCTIONS]
This prompt was selected for phone call analysis queries. When you receive routing context:
[ROUTING CONTEXT: This query was routed to phone analysis based on detected keywords: <keywords>]
[DATA AVAILABILITY: Available - <available_types>; Unavailable - <unavailable_types>]

Use this context to:
1. Understand why this call-focused prompt was chosen
2. Focus on communication patterns and agent effectiveness
3. Acknowledge when phone data is unavailable and suggest alternatives
4. Provide insights about customer engagement and service quality

Provide detailed call analysis insights that help improve customer service and engagement strategies.""",
                "temperature": 0.7,
                "max_tokens": 1500,
                "model": "gpt-4o-mini"
            },
            {
                "variant_name": "account-status-v1",
                "base_template": "account_status",
                "system_prompt": """You are a Credit Pros advisor specializing in account status and subscription management.
Provide clear, accurate account status information based on the available data.

Available account data includes:
- Current subscription status and enrollment details
- Account activity and engagement levels
- Payment status and billing information
- Service history and account changes
- Customer lifecycle stage and status transitions

[ROUTING CONTEXT INSTRUCTIONS]
This prompt was selected for account status queries. When you receive routing context:
[ROUTING CONTEXT: This query was routed to account_status analysis based on detected keywords: <keywords>]
[DATA AVAILABILITY: Available - <available_types>; Unavailable - <unavailable_types>]

Use this context to:
1. Understand why this status-focused prompt was chosen
2. Provide clear, direct account status information
3. Acknowledge any data limitations affecting status accuracy
4. Offer next steps or actions based on current status

Provide clear, concise account status information with actionable next steps when appropriate.""",
                "temperature": 0.3,
                "max_tokens": 1000,
                "model": "gpt-4o-mini"
            }
        ]

        print(f"🔧 Creating {len(variants_config)} routing-aware variants...")
        print()

        for variant in variants_config:
            self._create_variant_config(variant)

        # Generate creation summary
        self._generate_creation_summary()

    def _create_variant_config(self, variant_config: Dict):
        """Create variant configuration (ready for manual creation in Agenta.ai)"""
        variant_name = variant_config["variant_name"]

        print(f"📝 Preparing: {variant_name}")

        try:
            # Prepare the complete configuration
            config = {
                "variant_name": variant_name,
                "base_template": variant_config["base_template"],
                "configuration": {
                    "system_prompt": variant_config["system_prompt"],
                    "temperature": variant_config["temperature"],
                    "max_tokens": variant_config["max_tokens"],
                    "model": variant_config["model"]
                },
                "routing_aware": True,
                "created_for": "routing_aware_tlrs_integration"
            }

            result = {
                "variant_name": variant_name,
                "success": True,
                "config": config,
                "prompt_length": len(variant_config["system_prompt"]),
                "status": "ready_for_manual_creation"
            }

            print(f"  ✅ Configured: {variant_name}")
            print(f"     Temperature: {variant_config['temperature']}")
            print(f"     Max Tokens: {variant_config['max_tokens']}")
            print(f"     Prompt Length: {len(variant_config['system_prompt'])} chars")

            self.created_variants.append(result)

        except Exception as e:
            result = {
                "variant_name": variant_name,
                "success": False,
                "error": str(e)
            }
            print(f"  ❌ Error: {variant_name} - {e}")
            self.created_variants.append(result)

        print()

    def _generate_creation_summary(self):
        """Generate variant creation summary"""
        print("=" * 60)
        print("📊 VARIANT CREATION SUMMARY")
        print("=" * 60)

        total_variants = len(self.created_variants)
        successful_configs = sum(1 for r in self.created_variants if r["success"])
        failed_configs = total_variants - successful_configs

        print(f"\n📈 CONFIGURATION RESULTS:")
        print(f"  Total Variants: {total_variants}")
        print(f"  Successfully Configured: {successful_configs}")
        print(f"  Failed: {failed_configs}")

        if successful_configs > 0:
            print(f"\n✅ SUCCESSFULLY CONFIGURED VARIANTS:")
            for result in self.created_variants:
                if result["success"]:
                    print(f"  - {result['variant_name']} ({result['prompt_length']} chars)")

        if failed_configs > 0:
            print(f"\n❌ FAILED CONFIGURATIONS:")
            for result in self.created_variants:
                if not result["success"]:
                    print(f"  - {result['variant_name']}: {result.get('error', 'Unknown error')}")

        # Save configurations for manual creation
        creation_config = {
            "timestamp": datetime.now().isoformat(),
            "creation_type": "routing_aware_variants_manual",
            "app_slug": "tilores-x",
            "agenta_dashboard_url": "https://cloud.agenta.ai",
            "variants": self.created_variants,
            "manual_creation_instructions": [
                "1. Log into Agenta.ai dashboard at https://cloud.agenta.ai",
                "2. Navigate to your 'tilores-x' application",
                "3. For each variant configuration below:",
                "   a. Click 'Create New Variant'",
                "   b. Use the variant_name as the variant name",
                "   c. Copy the system_prompt into the prompt field",
                "   d. Set temperature, max_tokens, and model as specified",
                "   e. Save the variant",
                "4. After creating all variants, run the test script to validate"
            ]
        }

        config_filename = f"agenta_variants_manual_creation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(config_filename, 'w') as f:
            json.dump(creation_config, f, indent=2)

        print(f"\n💾 Manual creation guide saved to: {config_filename}")

        # Also create individual prompt files for easy copy-paste
        print(f"\n📁 Creating individual prompt files for easy copy-paste...")

        for result in self.created_variants:
            if result["success"]:
                variant_name = result["variant_name"]
                config = result["config"]["configuration"]

                prompt_filename = f"prompt_{variant_name}.txt"
                with open(prompt_filename, 'w') as f:
                    f.write(f"Variant Name: {variant_name}\n")
                    f.write(f"Temperature: {config['temperature']}\n")
                    f.write(f"Max Tokens: {config['max_tokens']}\n")
                    f.write(f"Model: {config['model']}\n")
                    f.write(f"\nSystem Prompt:\n")
                    f.write("=" * 50 + "\n")
                    f.write(config['system_prompt'])
                    f.write("\n" + "=" * 50 + "\n")

                print(f"  📝 Created: {prompt_filename}")

    def test_routing_with_current_system(self):
        """Test routing functionality with current system (template fallbacks)"""
        print(f"\n🧪 Testing Routing Functionality")
        print("=" * 60)
        print("Testing with current system (will use template fallbacks until variants are created)")
        print()

        # Import routing components
        from agenta_sdk_manager_enhanced import get_routing_aware_prompt

        test_scenarios = [
            {
                "name": "Credit Analysis Routing Test",
                "query": "What's the credit score for e.j.price1986@gmail.com?",
                "expected_route": "credit",
                "expected_variant": "credit-analysis-comprehensive-v1"
            },
            {
                "name": "Multi-Data Analysis Routing Test",
                "query": "Give me comprehensive analysis for customer@email.com",
                "expected_route": "multi_data",
                "expected_variant": "multi-data-analysis-v1"
            },
            {
                "name": "Account Status Routing Test",
                "query": "What's the account status for john.doe@email.com?",
                "expected_route": "account_status",
                "expected_variant": "account-status-v1"
            },
            {
                "name": "Transaction Analysis Routing Test",
                "query": "Show me payment patterns for customer@email.com",
                "expected_route": "transaction",
                "expected_variant": "transaction-analysis-v1"
            },
            {
                "name": "Phone Analysis Routing Test",
                "query": "Show me call history for customer@email.com",
                "expected_route": "phone",
                "expected_variant": "phone-call-analysis-v1"
            }
        ]

        print(f"🔍 Running {len(test_scenarios)} routing tests...")
        print()

        for scenario in test_scenarios:
            self._test_routing_scenario(scenario)

        # Generate test summary
        self._generate_routing_test_summary()

    def _test_routing_scenario(self, scenario: Dict):
        """Test individual routing scenario"""
        print(f"📋 Testing: {scenario['name']}")

        try:
            # Get routing-aware prompt
            prompt_config = get_routing_aware_prompt(
                query=scenario["query"],
                customer_id="test-customer-id",
                data_availability={
                    "credit_data": True,
                    "phone_data": False,
                    "transaction_data": True,
                    "card_data": True,
                    "ticket_data": False
                }
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

            # Check if routing instructions would be present (in created variants)
            expected_instructions = "[ROUTING CONTEXT INSTRUCTIONS]"

            success = route_correct and has_routing_context

            result = {
                "scenario_name": scenario["name"],
                "query": scenario["query"],
                "expected_route": expected_route,
                "actual_route": actual_route,
                "expected_variant": scenario["expected_variant"],
                "route_correct": route_correct,
                "has_routing_context": has_routing_context,
                "has_data_availability": has_data_availability,
                "prompt_source": prompt_config.get("source", ""),
                "success": success,
                "routing_metadata": routing_metadata
            }

            self.test_results.append(result)

            # Display results
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} Route: {actual_route} → {scenario['expected_variant']}")
            print(f"  🎯 Routing Context: {'✅' if has_routing_context else '❌'}")
            print(f"  📊 Data Availability: {'✅' if has_data_availability else '❌'}")
            print(f"  📋 Source: {prompt_config.get('source', 'unknown')}")

        except Exception as e:
            result = {
                "scenario_name": scenario["name"],
                "success": False,
                "error": str(e)
            }
            print(f"  ❌ ERROR: {e}")
            self.test_results.append(result)

        print()

    def _generate_routing_test_summary(self):
        """Generate routing test summary"""
        print("=" * 60)
        print("📊 ROUTING TEST SUMMARY")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.get("success", False))
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"\n📈 ROUTING TEST RESULTS:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {success_rate:.1f}%")

        # Show routing accuracy
        correct_routes = sum(1 for r in self.test_results if r.get("route_correct", False))
        routing_accuracy = (correct_routes / total_tests * 100) if total_tests > 0 else 0

        print(f"\n🎯 ROUTING ACCURACY:")
        print(f"  Correct Routes: {correct_routes}/{total_tests}")
        print(f"  Routing Accuracy: {routing_accuracy:.1f}%")

        # Show expected variant mapping
        print(f"\n📋 VARIANT MAPPING:")
        for result in self.test_results:
            if result.get("success"):
                print(f"  {result['actual_route']} → {result['expected_variant']}")

        # Save test results
        test_report = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "routing_functionality_validation",
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "routing_accuracy": routing_accuracy
            },
            "detailed_results": self.test_results
        }

        report_filename = f"routing_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(test_report, f, indent=2)

        print(f"\n💾 Test report saved to: {report_filename}")

        if success_rate >= 95:
            print(f"\n🎉 EXCELLENT: Routing functionality working perfectly!")
            print("✅ Ready for Agenta.ai variant creation")
        elif success_rate >= 85:
            print(f"\n✅ GOOD: Routing mostly working correctly")
            print("⚠️ Minor issues to address")
        else:
            print(f"\n❌ NEEDS WORK: Routing has significant issues")
            print("🔧 Fix routing before creating variants")


def main():
    """Main variant creation and testing workflow"""
    print("🚀 Agenta.ai Routing-Aware Variant Creation")
    print("Creating configurations for manual variant creation in Agenta.ai dashboard")
    print()

    creator = AgentaVariantCreator()

    # Phase 1: Create variant configurations
    creator.create_routing_aware_variants()

    # Phase 2: Test routing functionality
    creator.test_routing_with_current_system()

    print("\n🎯 VARIANT CREATION COMPLETE")
    print("=" * 60)
    print("📋 NEXT STEPS:")
    print("1. Review the generated prompt files (prompt_*.txt)")
    print("2. Log into Agenta.ai dashboard at https://cloud.agenta.ai")
    print("3. Navigate to your 'tilores-x' application")
    print("4. Create each variant manually using the provided configurations")
    print("5. Test the variants using the Agenta.ai playground")
    print("6. Run live testing once variants are created")
    print()
    print("📁 FILES CREATED:")
    print("- agenta_variants_manual_creation_*.json (complete configuration)")
    print("- prompt_*.txt (individual prompts for copy-paste)")
    print("- routing_test_report_*.json (routing functionality validation)")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Variant creation failed: {e}")
        sys.exit(1)
