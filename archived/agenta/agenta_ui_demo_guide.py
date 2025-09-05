#!/usr/bin/env python3
"""
Agenta.ai UI Demo Guide - Routing-Aware Integration

This script provides a comprehensive demo guide for showcasing the routing-aware
Agenta.ai integration in the UI, including test queries and expected behaviors.
"""

import json
import sys
import os
from typing import Dict, List, Any
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agenta_sdk_manager_enhanced import get_routing_aware_prompt
    print("✅ Successfully imported routing-aware components")
except ImportError as e:
    print(f"❌ Failed to import components: {e}")
    sys.exit(1)


class AgentaUIDemo:
    """Demo guide for showcasing routing-aware Agenta.ai integration"""

    def __init__(self):
        self.demo_scenarios = []

    def generate_demo_guide(self):
        """Generate comprehensive demo guide"""
        print("🎯 Agenta.ai UI Demo Guide - Routing-Aware Integration")
        print("=" * 70)
        print("Comprehensive guide for demonstrating routing-aware functionality")
        print()

        # Generate demo scenarios
        self.create_demo_scenarios()

        # Generate UI walkthrough
        self.generate_ui_walkthrough()

        # Generate test queries
        self.generate_test_queries()

        # Generate expected behaviors
        self.generate_expected_behaviors()

        # Save demo guide
        self.save_demo_guide()

    def create_demo_scenarios(self):
        """Create comprehensive demo scenarios"""

        self.demo_scenarios = [
            {
                "scenario_name": "Credit Analysis Demo",
                "description": "Demonstrate credit-specific routing and analysis",
                "test_query": "What's the credit score for e.j.price1986@gmail.com?",
                "expected_variant": "credit-analysis-comprehensive-v1",
                "expected_route": "credit",
                "demo_points": [
                    "Query contains 'credit score' keywords",
                    "System routes to credit analysis variant",
                    "Prompt includes credit-specific instructions",
                    "Response focuses on credit data and recommendations"
                ],
                "agenta_ui_steps": [
                    "1. Open credit-analysis-comprehensive-v1 variant",
                    "2. Enter the test query in playground",
                    "3. Show routing context in system prompt",
                    "4. Execute and demonstrate credit-focused response",
                    "5. Compare with other variants to show specialization"
                ]
            },
            {
                "scenario_name": "Multi-Data Analysis Demo",
                "description": "Demonstrate comprehensive multi-source analysis",
                "test_query": "Give me comprehensive analysis for e.j.price1986@gmail.com including all available data",
                "expected_variant": "multi-data-analysis-v1",
                "expected_route": "multi_data",
                "demo_points": [
                    "Query contains 'comprehensive' and 'all data' keywords",
                    "System routes to multi-data analysis variant",
                    "Prompt combines multiple data sources",
                    "Response provides holistic customer intelligence"
                ],
                "agenta_ui_steps": [
                    "1. Open multi-data-analysis-v1 variant",
                    "2. Enter comprehensive analysis query",
                    "3. Show multi-source data instructions",
                    "4. Execute and demonstrate cross-data insights",
                    "5. Highlight data availability handling"
                ]
            },
            {
                "scenario_name": "Account Status Demo",
                "description": "Demonstrate direct account status queries",
                "test_query": "What's the current account status for john.doe@email.com?",
                "expected_variant": "account-status-v1",
                "expected_route": "account_status",
                "demo_points": [
                    "Query contains 'account status' keywords",
                    "System routes to account status variant",
                    "Prompt optimized for direct, clear responses",
                    "Response provides concise status information"
                ],
                "agenta_ui_steps": [
                    "1. Open account-status-v1 variant",
                    "2. Enter account status query",
                    "3. Show direct response optimization",
                    "4. Execute and demonstrate clear status info",
                    "5. Compare response style with other variants"
                ]
            },
            {
                "scenario_name": "Transaction Analysis Demo",
                "description": "Demonstrate payment pattern analysis",
                "test_query": "Show me payment patterns and transaction history for customer@email.com",
                "expected_variant": "transaction-analysis-v1",
                "expected_route": "transaction",
                "demo_points": [
                    "Query contains 'payment patterns' and 'transaction' keywords",
                    "System routes to transaction analysis variant",
                    "Prompt focuses on financial behavior analysis",
                    "Response provides payment optimization insights"
                ],
                "agenta_ui_steps": [
                    "1. Open transaction-analysis-v1 variant",
                    "2. Enter transaction analysis query",
                    "3. Show payment-focused instructions",
                    "4. Execute and demonstrate financial insights",
                    "5. Highlight transaction-specific analysis"
                ]
            },
            {
                "scenario_name": "Data Availability Demo",
                "description": "Demonstrate adaptive responses to missing data",
                "test_query": "Show me call history for customer@email.com",
                "expected_variant": "phone-call-analysis-v1",
                "expected_route": "phone",
                "demo_points": [
                    "Query requests phone data that may be unavailable",
                    "System routes to phone analysis variant",
                    "Prompt adapts to data availability context",
                    "Response acknowledges limitations gracefully"
                ],
                "agenta_ui_steps": [
                    "1. Open phone-call-analysis-v1 variant",
                    "2. Enter call history query",
                    "3. Show data availability context handling",
                    "4. Execute and demonstrate adaptive response",
                    "5. Show how system handles missing data"
                ]
            },
            {
                "scenario_name": "A/B Testing Demo",
                "description": "Demonstrate prompt optimization with routing context",
                "test_query": "Analyze credit data for e.j.price1986@gmail.com",
                "expected_variant": "credit-analysis-comprehensive-v1",
                "expected_route": "credit",
                "demo_points": [
                    "Same query tested across different prompt versions",
                    "Routing context preserved in all variants",
                    "Performance metrics tracked automatically",
                    "Data-driven optimization with routing awareness"
                ],
                "agenta_ui_steps": [
                    "1. Create variant B of credit-analysis-comprehensive",
                    "2. Modify system prompt while keeping routing context",
                    "3. Run A/B test with same routing-aware query",
                    "4. Compare responses with routing context intact",
                    "5. Show performance metrics and optimization"
                ]
            }
        ]

    def generate_ui_walkthrough(self):
        """Generate step-by-step UI walkthrough"""
        print("🖥️ Agenta.ai UI Walkthrough")
        print("-" * 50)

        walkthrough_steps = [
            {
                "step": "1. Dashboard Overview",
                "description": "Show the tilores-x application dashboard",
                "actions": [
                    "Navigate to https://cloud.agenta.ai",
                    "Select 'tilores-x' application",
                    "Show 5 routing-aware variants created",
                    "Highlight variant naming convention"
                ],
                "talking_points": [
                    "Each variant corresponds to a TLRS routing decision",
                    "Variants are optimized for specific query types",
                    "Routing context is embedded in every variant",
                    "System automatically selects the right variant"
                ]
            },
            {
                "step": "2. Variant Configuration",
                "description": "Explore variant-specific configurations",
                "actions": [
                    "Open credit-analysis-comprehensive-v1",
                    "Show system prompt with routing instructions",
                    "Highlight temperature and token settings",
                    "Explain routing context integration"
                ],
                "talking_points": [
                    "Each variant has specialized instructions",
                    "Routing context instructions are embedded",
                    "Temperature optimized for response type",
                    "Token limits set based on expected response length"
                ]
            },
            {
                "step": "3. Playground Testing",
                "description": "Demonstrate live testing in playground",
                "actions": [
                    "Enter test query in playground",
                    "Show routing context injection",
                    "Execute query and show response",
                    "Highlight variant-specific behavior"
                ],
                "talking_points": [
                    "Routing context automatically injected",
                    "Response adapts to available data types",
                    "Variant specialization clearly visible",
                    "Quality and relevance improved"
                ]
            },
            {
                "step": "4. A/B Testing Setup",
                "description": "Show how to set up routing-aware A/B tests",
                "actions": [
                    "Create variant B with modified prompt",
                    "Preserve routing context instructions",
                    "Set up A/B test configuration",
                    "Define success metrics"
                ],
                "talking_points": [
                    "Routing context preserved across variants",
                    "Fair comparison with same routing logic",
                    "Performance metrics tracked automatically",
                    "Data-driven optimization enabled"
                ]
            },
            {
                "step": "5. Performance Analytics",
                "description": "Review performance metrics and insights",
                "actions": [
                    "Open analytics dashboard",
                    "Show variant performance comparison",
                    "Highlight routing-aware metrics",
                    "Demonstrate optimization insights"
                ],
                "talking_points": [
                    "Each routing decision tracked separately",
                    "Performance metrics by query type",
                    "Routing context impact on quality",
                    "Optimization recommendations"
                ]
            }
        ]

        for step_info in walkthrough_steps:
            print(f"\n📋 {step_info['step']}")
            print(f"   {step_info['description']}")
            print(f"   Actions:")
            for action in step_info['actions']:
                print(f"   • {action}")
            print(f"   Talking Points:")
            for point in step_info['talking_points']:
                print(f"   • {point}")

    def generate_test_queries(self):
        """Generate test queries for live demo"""
        print(f"\n🔍 Test Queries for Live Demo")
        print("-" * 50)

        test_queries = [
            {
                "category": "Credit Analysis",
                "queries": [
                    "What's the credit score for e.j.price1986@gmail.com?",
                    "How has the credit utilization changed for this customer?",
                    "Show me bureau-specific credit data for e.j.price1986@gmail.com",
                    "What credit improvement recommendations do you have?"
                ],
                "expected_behavior": "Routes to credit-analysis-comprehensive-v1, focuses on credit data, provides score analysis and improvement recommendations"
            },
            {
                "category": "Multi-Data Analysis",
                "queries": [
                    "Give me comprehensive analysis for e.j.price1986@gmail.com",
                    "Show me all available data for this customer",
                    "Provide complete customer intelligence report",
                    "Analyze both credit and transaction data together"
                ],
                "expected_behavior": "Routes to multi-data-analysis-v1, combines multiple data sources, provides holistic customer insights"
            },
            {
                "category": "Account Status",
                "queries": [
                    "What's the account status for john.doe@email.com?",
                    "Is this customer's account active?",
                    "Show me current subscription status",
                    "What's the enrollment status for this customer?"
                ],
                "expected_behavior": "Routes to account-status-v1, provides direct status information, offers clear next steps"
            },
            {
                "category": "Transaction Analysis",
                "queries": [
                    "Show me payment patterns for customer@email.com",
                    "What are the transaction trends for this customer?",
                    "Analyze billing and payment history",
                    "How consistent are the payment behaviors?"
                ],
                "expected_behavior": "Routes to transaction-analysis-v1, focuses on payment patterns, provides financial behavior insights"
            },
            {
                "category": "Phone Analysis",
                "queries": [
                    "Show me call history for customer@email.com",
                    "What's the agent interaction summary?",
                    "Analyze phone call patterns and outcomes",
                    "How effective are the customer calls?"
                ],
                "expected_behavior": "Routes to phone-call-analysis-v1, handles data availability gracefully, provides communication insights"
            },
            {
                "category": "Edge Cases",
                "queries": [
                    "",  # Empty query
                    "Tell me about customer@email.com",  # Vague query
                    "¿Cuál es el puntaje crediticio?",  # Unicode query
                    "What's the credit score and transaction data and call history for customer@email.com?"  # Mixed keywords
                ],
                "expected_behavior": "Handles gracefully, routes appropriately, provides relevant responses even for edge cases"
            }
        ]

        for category_info in test_queries:
            print(f"\n📊 {category_info['category']}")
            print(f"   Expected: {category_info['expected_behavior']}")
            print(f"   Test Queries:")
            for i, query in enumerate(category_info['queries'], 1):
                if query:  # Skip empty queries in display
                    print(f"   {i}. \"{query}\"")
                else:
                    print(f"   {i}. [Empty Query Test]")

    def generate_expected_behaviors(self):
        """Generate expected behaviors for demo"""
        print(f"\n🎯 Expected Behaviors During Demo")
        print("-" * 50)

        behaviors = [
            {
                "behavior": "Automatic Routing",
                "description": "System automatically selects the right variant based on query keywords",
                "demo_evidence": [
                    "Credit queries → credit-analysis-comprehensive-v1",
                    "Comprehensive queries → multi-data-analysis-v1",
                    "Status queries → account-status-v1",
                    "Payment queries → transaction-analysis-v1",
                    "Call queries → phone-call-analysis-v1"
                ]
            },
            {
                "behavior": "Context Injection",
                "description": "Routing context automatically injected into every prompt",
                "demo_evidence": [
                    "[ROUTING CONTEXT: ...] appears in system prompt",
                    "[DATA AVAILABILITY: ...] shows available data types",
                    "Prompts adapt based on routing decision",
                    "Responses acknowledge routing context"
                ]
            },
            {
                "behavior": "Data Availability Adaptation",
                "description": "Prompts adapt when certain data types are unavailable",
                "demo_evidence": [
                    "Phone queries handle missing call data gracefully",
                    "System explains data limitations",
                    "Alternative insights provided when possible",
                    "Clear communication about data gaps"
                ]
            },
            {
                "behavior": "Specialized Responses",
                "description": "Each variant provides specialized, targeted responses",
                "demo_evidence": [
                    "Credit variant focuses on scores and recommendations",
                    "Transaction variant emphasizes payment patterns",
                    "Status variant provides direct, clear information",
                    "Multi-data variant combines insights from multiple sources"
                ]
            },
            {
                "behavior": "Fallback Resilience",
                "description": "System gracefully handles edge cases and errors",
                "demo_evidence": [
                    "Empty queries route to default credit analysis",
                    "Vague queries still provide relevant responses",
                    "Unicode and special characters handled correctly",
                    "Mixed keyword queries route to multi-data analysis"
                ]
            }
        ]

        for behavior_info in behaviors:
            print(f"\n✅ {behavior_info['behavior']}")
            print(f"   {behavior_info['description']}")
            print(f"   Demo Evidence:")
            for evidence in behavior_info['demo_evidence']:
                print(f"   • {evidence}")

    def save_demo_guide(self):
        """Save comprehensive demo guide"""
        demo_guide = {
            "title": "Agenta.ai UI Demo Guide - Routing-Aware Integration",
            "created": datetime.now().isoformat(),
            "demo_scenarios": self.demo_scenarios,
            "preparation_checklist": [
                "✅ Ensure all 5 variants are created in Agenta.ai dashboard",
                "✅ Test each variant in playground before demo",
                "✅ Prepare customer data examples (e.g., e.j.price1986@gmail.com)",
                "✅ Have test queries ready for copy-paste",
                "✅ Understand routing logic and expected behaviors",
                "✅ Practice explaining routing context integration"
            ],
            "demo_flow": [
                "1. Introduction - Explain routing-aware concept (2 min)",
                "2. Dashboard Overview - Show variants and configuration (3 min)",
                "3. Live Testing - Demonstrate routing and responses (10 min)",
                "4. A/B Testing - Show optimization capabilities (5 min)",
                "5. Performance Analytics - Review metrics and insights (5 min)",
                "6. Q&A - Address questions and edge cases (5 min)"
            ],
            "key_talking_points": [
                "🎯 Routing Context Awareness - Prompts understand why they were selected",
                "📊 Data Availability Handling - Adaptive responses to missing data",
                "🚀 Specialized Variants - Each optimized for specific query types",
                "⚡ Automatic Selection - System chooses the right prompt automatically",
                "📈 A/B Testing Ready - Optimize prompts with routing context intact",
                "🔧 Production Ready - Seamless integration with existing TLRS system"
            ],
            "success_metrics": [
                "Audience understands routing-aware concept",
                "Clear demonstration of automatic variant selection",
                "Visible improvement in response quality and relevance",
                "Understanding of A/B testing capabilities",
                "Appreciation for data availability handling",
                "Recognition of production deployment readiness"
            ]
        }

        filename = f"agenta_ui_demo_guide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(demo_guide, f, indent=2)

        print(f"\n💾 Demo guide saved to: {filename}")

        # Also create a quick reference card
        self.create_quick_reference()

    def create_quick_reference(self):
        """Create quick reference card for demo"""
        quick_ref = """
🎯 AGENTA.AI ROUTING-AWARE DEMO - QUICK REFERENCE

📋 DEMO FLOW (30 minutes total):
1. Introduction (2 min) - Explain routing-aware concept
2. Dashboard (3 min) - Show 5 variants and configuration
3. Live Testing (10 min) - Demonstrate routing and responses
4. A/B Testing (5 min) - Show optimization capabilities
5. Analytics (5 min) - Review metrics and insights
6. Q&A (5 min) - Address questions

🔍 KEY TEST QUERIES:
• Credit: "What's the credit score for e.j.price1986@gmail.com?"
• Multi-Data: "Give me comprehensive analysis for e.j.price1986@gmail.com"
• Status: "What's the account status for john.doe@email.com?"
• Transaction: "Show me payment patterns for customer@email.com"
• Phone: "Show me call history for customer@email.com"

✅ EXPECTED BEHAVIORS:
• Automatic routing to correct variant
• Routing context injection in prompts
• Data availability adaptation
• Specialized, targeted responses
• Graceful error handling

🎯 KEY TALKING POINTS:
• Prompts understand routing decisions
• Adaptive responses to missing data
• Each variant optimized for query type
• A/B testing with routing context intact
• Production-ready integration

📊 SUCCESS INDICATORS:
• Audience sees automatic variant selection
• Clear improvement in response quality
• Understanding of optimization capabilities
• Recognition of production readiness
"""

        with open("agenta_demo_quick_reference.txt", 'w') as f:
            f.write(quick_ref)

        print("📋 Quick reference saved to: agenta_demo_quick_reference.txt")


def main():
    """Generate comprehensive demo guide"""
    print("🎯 Generating Agenta.ai UI Demo Guide")
    print("Creating comprehensive guide for demonstrating routing-aware integration")
    print()

    demo = AgentaUIDemo()
    demo.generate_demo_guide()

    print("\n🎉 Demo Guide Generation Complete!")
    print("=" * 50)
    print("📁 Files Created:")
    print("• agenta_ui_demo_guide_*.json - Complete demo guide")
    print("• agenta_demo_quick_reference.txt - Quick reference card")
    print()
    print("🚀 Ready for Demo!")
    print("Use these files to prepare and deliver an effective demonstration")
    print("of your routing-aware Agenta.ai integration.")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Demo guide generation failed: {e}")
        sys.exit(1)
