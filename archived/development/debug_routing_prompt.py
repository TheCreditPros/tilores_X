#!/usr/bin/env python3
"""
Debug script to check routing-aware prompt generation
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agenta_sdk_manager_enhanced import RoutingAwareAgentaManager

def debug_prompt_generation():
    """Debug the prompt generation process"""

    manager = RoutingAwareAgentaManager()

    # Test a simple credit query
    query = "What's the credit score for e.j.price1986@gmail.com?"

    print("🔍 Debugging Routing-Aware Prompt Generation")
    print("=" * 60)
    print(f"Query: {query}")
    print()

    # Get routing-aware prompt
    prompt_config = manager.get_routing_aware_prompt(
        query=query,
        customer_id="test-customer-id"
    )

    print("📋 Prompt Configuration:")
    print(f"  Source: {prompt_config.get('source')}")
    print(f"  Routing Aware: {prompt_config.get('routing_aware')}")
    print(f"  Routing Decision: {prompt_config.get('routing_metadata', {}).get('routing_decision')}")
    print(f"  Keywords: {prompt_config.get('routing_metadata', {}).get('keywords_detected')}")
    print()

    print("📝 System Prompt:")
    print("-" * 40)
    system_prompt = prompt_config.get('system_prompt', '')
    print(system_prompt)
    print("-" * 40)
    print()

    # Check for routing context
    has_routing_context = "[ROUTING CONTEXT:" in system_prompt
    print(f"🎯 Has Routing Context: {has_routing_context}")

    if not has_routing_context:
        print("❌ ISSUE: Routing context not found in system prompt!")
        print("🔍 Let's debug the injection process...")

        # Debug the routing context building
        routing_metadata = prompt_config.get('routing_metadata', {})
        context_text = manager._build_routing_context_text(routing_metadata)
        print(f"📊 Built Context Text: '{context_text}'")
        print(f"📊 Context Text Length: {len(context_text)}")

        if not context_text:
            print("❌ ISSUE: Context text is empty!")

    print()
    print("🔍 Routing Metadata:")
    routing_metadata = prompt_config.get('routing_metadata', {})
    for key, value in routing_metadata.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    debug_prompt_generation()
