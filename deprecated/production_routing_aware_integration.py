#!/usr/bin/env python3
"""
Production Integration for Routing-Aware Agenta SDK Manager

This module provides the integration layer to update your production API
(direct_credit_api_with_phone.py) to use routing-aware Agenta.ai prompts.
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agenta_sdk_manager_enhanced import (
        routing_aware_agenta_manager,
        get_routing_aware_prompt
    )
    print("✅ Successfully imported routing-aware Agenta components")
except ImportError as e:
    print(f"❌ Failed to import routing-aware components: {e}")
    sys.exit(1)


class RoutingAwareProductionIntegration:
    """
    Production integration class that provides routing-aware prompt functionality
    for the existing TLRS API
    """

    def __init__(self):
        self.routing_manager = routing_aware_agenta_manager
        self.performance_metrics = []

    async def get_enhanced_system_prompt(self, query: str, entity_id: str = None,
                                       data_availability: Dict[str, bool] = None) -> Dict[str, Any]:
        """
        Get routing-aware system prompt for production use

        Args:
            query: User's query
            entity_id: Customer entity ID
            data_availability: Dict of available data types

        Returns:
            Enhanced prompt configuration with routing context
        """

        start_time = datetime.now()

        try:
            # Get routing-aware prompt configuration
            prompt_config = self.routing_manager.get_routing_aware_prompt(
                query=query,
                customer_id=entity_id,
                data_availability=data_availability
            )

            # Log performance metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._log_performance_metric(
                query=query,
                routing_decision=prompt_config.get("routing_metadata", {}).get("routing_decision"),
                processing_time=processing_time,
                success=True
            )

            return prompt_config

        except Exception as e:
            # Log error and return fallback
            processing_time = (datetime.now() - start_time).total_seconds()
            self._log_performance_metric(
                query=query,
                routing_decision="error",
                processing_time=processing_time,
                success=False,
                error=str(e)
            )

            # Return fallback configuration
            return self._get_fallback_prompt_config(query)

    def _get_fallback_prompt_config(self, query: str) -> Dict[str, Any]:
        """Get fallback prompt configuration when routing-aware fails"""
        return {
            "system_prompt": """You are a Credit Pros advisor with access to comprehensive customer data.
Analyze the provided data to answer the user's question accurately and professionally.

[ROUTING CONTEXT: Using fallback prompt due to routing-aware system unavailable]

Provide detailed insights based on the available data.""",
            "temperature": 0.7,
            "max_tokens": 1500,
            "source": "fallback_routing_aware",
            "routing_aware": False,
            "routing_metadata": {
                "routing_decision": "fallback",
                "fallback_reason": "routing_aware_system_error"
            }
        }

    def _log_performance_metric(self, query: str, routing_decision: str,
                              processing_time: float, success: bool, error: str = None):
        """Log performance metrics for monitoring"""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "query_length": len(query),
            "routing_decision": routing_decision,
            "processing_time_ms": processing_time * 1000,
            "success": success,
            "error": error
        }

        self.performance_metrics.append(metric)

        # Keep only last 1000 metrics to prevent memory issues
        if len(self.performance_metrics) > 1000:
            self.performance_metrics = self.performance_metrics[-1000:]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for monitoring"""
        if not self.performance_metrics:
            return {"status": "no_data"}

        total_requests = len(self.performance_metrics)
        successful_requests = sum(1 for m in self.performance_metrics if m["success"])
        avg_processing_time = sum(m["processing_time_ms"] for m in self.performance_metrics) / total_requests

        # Group by routing decision
        routing_stats = {}
        for metric in self.performance_metrics:
            decision = metric["routing_decision"]
            if decision not in routing_stats:
                routing_stats[decision] = {"count": 0, "avg_time": 0, "success_rate": 0}
            routing_stats[decision]["count"] += 1

        # Calculate averages
        for decision, stats in routing_stats.items():
            decision_metrics = [m for m in self.performance_metrics if m["routing_decision"] == decision]
            stats["avg_time"] = sum(m["processing_time_ms"] for m in decision_metrics) / len(decision_metrics)
            stats["success_rate"] = sum(1 for m in decision_metrics if m["success"]) / len(decision_metrics) * 100

        return {
            "total_requests": total_requests,
            "success_rate": (successful_requests / total_requests * 100),
            "avg_processing_time_ms": avg_processing_time,
            "routing_stats": routing_stats,
            "last_updated": datetime.now().isoformat()
        }


# Global instance for production use
production_integration = RoutingAwareProductionIntegration()


# ============================================================================
# PRODUCTION API INTEGRATION METHODS
# ============================================================================

async def enhance_chat_request_with_routing_aware_prompts(
    messages: List[Dict[str, str]],
    entity_id: str = None,
    data_availability: Dict[str, bool] = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> Dict[str, Any]:
    """
    Enhanced chat request processing with routing-aware prompts

    This function can be integrated into your existing process_chat_request method
    in direct_credit_api_with_phone.py

    Args:
        messages: Chat messages from the request
        entity_id: Customer entity ID
        data_availability: Dict of available data types
        model: AI model to use
        temperature: Temperature setting
        max_tokens: Max tokens setting

    Returns:
        Enhanced request configuration with routing-aware prompt
    """

    # Extract query from messages
    query = messages[-1]["content"] if messages else ""

    # Get routing-aware prompt configuration
    prompt_config = await production_integration.get_enhanced_system_prompt(
        query=query,
        entity_id=entity_id,
        data_availability=data_availability
    )

    # Use routing-aware settings or fallback to provided values
    enhanced_config = {
        "system_prompt": prompt_config["system_prompt"],
        "temperature": prompt_config.get("temperature", temperature),
        "max_tokens": prompt_config.get("max_tokens", max_tokens),
        "model": model,
        "routing_metadata": prompt_config.get("routing_metadata", {}),
        "routing_aware": prompt_config.get("routing_aware", False),
        "source": prompt_config.get("source", "unknown")
    }

    return enhanced_config


def create_routing_aware_ai_messages(
    messages: List[Dict[str, str]],
    system_prompt: str,
    context_data: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    Create AI messages with routing-aware system prompt and context

    Args:
        messages: Original chat messages
        system_prompt: Routing-aware system prompt
        context_data: Customer data context

    Returns:
        Enhanced AI messages ready for API call
    """

    # Build context string
    context_str = json.dumps(context_data, indent=2) if context_data else "{}"

    # Create enhanced messages
    ai_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Query: {messages[-1]['content'] if messages else ''}\n\nCustomer Data: {context_str}"}
    ]

    return ai_messages


async def log_routing_aware_interaction(
    query: str,
    response: str,
    routing_metadata: Dict[str, Any],
    success: bool,
    response_time: float
):
    """
    Log routing-aware interaction for observability

    Args:
        query: User's query
        response: AI response
        routing_metadata: Routing context metadata
        success: Whether the request was successful
        response_time: Response time in seconds
    """

    try:
        # Log to Agenta.ai if available
        routing_aware_agenta_manager.log_interaction(
            query_type=routing_metadata.get("routing_decision", "unknown"),
            query=query,
            response=response,
            success=success,
            response_time=response_time,
            config={
                "routing_metadata": routing_metadata,
                "source": "production_routing_aware"
            }
        )

        print(f"📊 Logged routing-aware interaction: {routing_metadata.get('routing_decision')} ({success})")

    except Exception as e:
        print(f"⚠️ Failed to log routing-aware interaction: {e}")


# ============================================================================
# INTEGRATION EXAMPLE FOR DIRECT_CREDIT_API_WITH_PHONE.PY
# ============================================================================

def get_integration_example():
    """
    Get example code for integrating into direct_credit_api_with_phone.py
    """

    integration_code = '''
# Add this import at the top of direct_credit_api_with_phone.py
from production_routing_aware_integration import (
    enhance_chat_request_with_routing_aware_prompts,
    create_routing_aware_ai_messages,
    log_routing_aware_interaction,
    production_integration
)

# Modify your process_chat_request method like this:
async def process_chat_request(self, messages: List[ChatMessage], model: str, temperature: float = 0.7, max_tokens: Optional[int] = None):
    """Enhanced request processing with routing-aware Agenta.ai prompts"""

    self.active_requests += 1
    start_time = datetime.now()

    try:
        # ... existing customer identification logic ...

        # Check data availability (your existing method)
        data_availability = await self.check_data_availability(entity_id)

        # Get routing-aware prompt configuration
        enhanced_config = await enhance_chat_request_with_routing_aware_prompts(
            messages=[{"content": msg.content, "role": msg.role} for msg in messages],
            entity_id=entity_id,
            data_availability=data_availability,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Use routing-aware system prompt
        system_prompt = enhanced_config["system_prompt"]
        temperature = enhanced_config["temperature"]
        max_tokens = enhanced_config["max_tokens"]

        # ... your existing data fetching logic ...

        # Create routing-aware AI messages
        ai_messages = create_routing_aware_ai_messages(
            messages=[{"content": msg.content, "role": msg.role} for msg in messages],
            system_prompt=system_prompt,
            context_data=context  # Your existing context dict
        )

        # ... your existing AI API call logic ...

        # Log routing-aware interaction
        response_time = (datetime.now() - start_time).total_seconds()
        await log_routing_aware_interaction(
            query=messages[-1].content if messages else "",
            response=response,
            routing_metadata=enhanced_config["routing_metadata"],
            success=True,
            response_time=response_time
        )

        return response

    except Exception as e:
        # ... existing error handling ...

        # Log failed interaction
        if 'enhanced_config' in locals():
            await log_routing_aware_interaction(
                query=messages[-1].content if messages else "",
                response="",
                routing_metadata=enhanced_config.get("routing_metadata", {}),
                success=False,
                response_time=(datetime.now() - start_time).total_seconds()
            )

        raise e

    finally:
        self.active_requests -= 1

# Add monitoring endpoint
@app.get("/v1/routing-aware/metrics")
async def get_routing_aware_metrics():
    """Get routing-aware performance metrics"""
    return production_integration.get_performance_summary()
'''

    return integration_code


def main():
    """Test the production integration"""
    print("🚀 Testing Production Routing-Aware Integration")
    print("=" * 60)

    # Test the integration
    import asyncio

    async def test_integration():
        # Test basic functionality
        messages = [{"content": "What's the credit score for e.j.price1986@gmail.com?", "role": "user"}]

        enhanced_config = await enhance_chat_request_with_routing_aware_prompts(
            messages=messages,
            entity_id="test-entity-id",
            data_availability={"credit_data": True, "phone_data": False}
        )

        print("📋 Enhanced Configuration:")
        print(f"  Routing Decision: {enhanced_config['routing_metadata'].get('routing_decision')}")
        print(f"  Routing Aware: {enhanced_config['routing_aware']}")
        print(f"  Source: {enhanced_config['source']}")
        print(f"  Temperature: {enhanced_config['temperature']}")
        print(f"  Max Tokens: {enhanced_config['max_tokens']}")

        print("\n📝 System Prompt Preview:")
        print("-" * 40)
        prompt = enhanced_config['system_prompt']
        print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
        print("-" * 40)

        # Test AI messages creation
        ai_messages = create_routing_aware_ai_messages(
            messages=messages,
            system_prompt=enhanced_config['system_prompt'],
            context_data={"test": "data"}
        )

        print(f"\n🤖 AI Messages Created: {len(ai_messages)} messages")

        # Test logging
        await log_routing_aware_interaction(
            query="test query",
            response="test response",
            routing_metadata=enhanced_config['routing_metadata'],
            success=True,
            response_time=0.5
        )

        print("\n✅ Production integration test completed successfully!")

        # Show performance summary
        summary = production_integration.get_performance_summary()
        print(f"\n📊 Performance Summary: {summary}")

        return True

    try:
        success = asyncio.run(test_integration())

        if success:
            print("\n🎉 PRODUCTION INTEGRATION READY!")
            print("\nNext steps:")
            print("1. Review the integration example code")
            print("2. Update your direct_credit_api_with_phone.py")
            print("3. Test with real customer queries")
            print("4. Monitor performance metrics")

            # Save integration example
            with open("routing_aware_integration_example.py", "w") as f:
                f.write(get_integration_example())
            print("\n💾 Integration example saved to: routing_aware_integration_example.py")

        return success

    except Exception as e:
        print(f"❌ Production integration test failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
