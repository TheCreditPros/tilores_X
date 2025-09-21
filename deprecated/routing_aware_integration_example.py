
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
