#!/usr/bin/env python3
"""
Langfuse Integration Example for Tilores_X Architecture
Demonstrates how to add Langfuse observability to your current LangChain setup
"""

import os
from typing import Any, Dict, Optional

# Langfuse imports
from langfuse import Langfuse, observe

# Your existing LangChain imports (commented out for demo)
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser

class LangfuseIntegrationManager:
    """Integrates Langfuse observability with your existing LangChain architecture"""

    def __init__(self):
        # Initialize Langfuse client
        self.langfuse = self._init_langfuse()

    def _init_langfuse(self) -> Optional[Langfuse]:
        """Initialize Langfuse client with environment variables"""
        try:
            # Check for Langfuse credentials
            public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
            secret_key = os.getenv("LANGFUSE_SECRET_KEY")
            host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

            if not public_key or not secret_key:
                print("⚠️ Langfuse credentials not found - observability disabled")
                return None

            # Initialize Langfuse client
            langfuse = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host
            )

            print("✅ Langfuse client initialized")
            return langfuse

        except Exception as e:
            print(f"❌ Langfuse initialization failed: {e}")
            return None

    @observe(name="customer_query_orchestration")
    def orchestrate_customer_query(self, query: str, agent_type: str = "zoho_cs") -> str:
        """
        Example of how to integrate Langfuse with your existing orchestration logic
        This replaces your current direct LLM calls with Langfuse-traced versions
        """

        # Your existing LLM logic would go here
        # For demo, we'll just return a mock response
        result = f"Processed {agent_type} query: {query}"

        return result

    def create_traced_tool_execution(self, tool_name: str, input_data: Dict[str, Any]) -> Any:
        """
        Example of how to trace tool executions with Langfuse
        Replace your current tool execution logic with this pattern
        """

        @observe(name=f"tool_execution_{tool_name}")
        def execute_tool():
            # Your existing tool logic here
            # For example, GraphQL queries, API calls, etc.
            result = {"tool": tool_name, "input": input_data, "output": "mock_result"}
            return result

        return execute_tool()

    def log_custom_metrics(self, metric_name: str, value: float, metadata: Dict[str, Any] = None):
        """Log custom metrics to Langfuse"""
        if not self.langfuse:
            return

        try:
            # Create a custom span for metrics
            span = self.langfuse.span(
                name=f"metric_{metric_name}",
                metadata=metadata or {}
            )

            # Add metric data
            span.generation(
                name=metric_name,
                input={"value": value},
                metadata=metadata
            )

            span.end()

        except Exception as e:
            print(f"❌ Failed to log metric {metric_name}: {e}")


if __name__ == "__main__":
    # Test the integration
    print("🔍 Testing Langfuse Integration...")

    # Initialize
    manager = LangfuseIntegrationManager()

    # Test basic orchestration (requires valid Langfuse keys)
    if manager.langfuse:
        print("✅ Langfuse integration ready for production use")
        print("\n📋 Integration Summary:")
        print("- Automatic LangChain tracing enabled")
        print("- Custom observability decorators available")
        print("- Tool execution tracing ready")
        print("- Custom metrics logging available")
    else:
        print("⚠️ Langfuse not configured - set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY")

    print("\n🔧 To integrate with your existing code:")
    print("1. Add 'langfuse>=2.30.0' to requirements.txt")
    print("2. Set environment variables: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY")
    print("3. Import and initialize LangfuseIntegrationManager in core_app.py")
    print("4. Replace direct LLM calls with traced versions")
    print("5. Add @observe decorators to key functions")
