#!/usr/bin/env python3
"""
Test implementation for tool calling fix
Tests the OpenAI API compatibility with proper tools parameter
"""

import json
import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Import existing functionality
from core_app import get_available_models, initialize_engine, run_chain
from core_app import engine

# Initialize the engine
print("🔧 TEST: Initializing engine...")
initialize_engine()
print(f"🔧 TEST: Engine initialized: {engine is not None}")
if engine and hasattr(engine, 'tools'):
    print(f"🔧 TEST: Tools available: {len(engine.tools) if engine.tools else 0}")

app = FastAPI(
    title="Tilores API Tool Fix Test",
    description="Test implementation for tool calling fix",
    version="TEST - 1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ToolDefinition(BaseModel):
    type: str = "function"
    function: Dict[str, Any]

class ChatCompletionRequest(BaseModel):
    model: str = "gpt - 4o-mini"
    messages: List[ChatMessage]
    tools: Optional[List[ToolDefinition]] = None  # CRITICAL FIX: Add tools parameter
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0

def get_tilores_tools_schema() -> List[ToolDefinition]:
    """Generate OpenAI-compatible tool schema for Tilores tools"""
    if not engine or not engine.tools:
        return []

    tools_schema = []
    for tool in engine.tools:
        tool_def = ToolDefinition(
            type="function",
            function={
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.args_schema.model_json_schema() if hasattr(tool, 'args_schema') else {}
            }
        )
        tools_schema.append(tool_def)

    return tools_schema

def run_chain_with_tools(
    messages,
    model: str = "llama - 3.3 - 70b-versatile",
    tools: Optional[List[ToolDefinition]] = None,
    **kwargs
):
    """
    Enhanced run_chain that handles OpenAI tools parameter properly
    """
    try:
        # Ensure engine is initialized
        if engine is None:
            raise RuntimeError("Engine initialization failed")

        # Convert messages format
        if isinstance(messages, str):
            user_input = messages
            conversation_history = []
        else:
            user_input = messages[-1]["content"] if messages else ""
            conversation_history = messages[:-1]

        # Determine if this query needs Tilores tools
        from core_app import query_router
        use_tilores_tools = query_router.should_use_tilores_tools(user_input)

        print(f"🎯 TEST QUERY ROUTING: '{user_input[:50]}...' → {'CUSTOMER (tools)' if use_tilores_tools else 'GENERAL (no tools)'}")

        if not use_tilores_tools:
            # General query - no tools needed
            llm = engine.get_model(model, **kwargs)
            messages_for_llm = [{"role": "assistant", "content": "I'm a helpful assistant."}]
            messages_for_llm.extend(conversation_history)
            messages_for_llm.append({"role": "user", "content": user_input})

            response = llm.invoke(messages_for_llm)
            return getattr(response, 'content', str(response))

        # Customer query - tools needed
        if not engine.tools:
            return "❌ TEST: No Tilores tools available"

        # CRITICAL FIX: Handle tools parameter properly
        if tools is None:
            # Auto-provide Tilores tools if not specified
            print("🔧 TEST: Auto-providing Tilores tools (no tools in request)")
            tools_to_use = engine.tools
        else:
            # Use provided tools and validate they match available tools
            print(f"🔧 TEST: Using provided tools ({len(tools)} tools specified)")
            available_tool_names = {tool.name for tool in engine.tools}
            requested_tool_names = {tool.function["name"] for tool in tools}

            # Validate that requested tools are available
            invalid_tools = requested_tool_names - available_tool_names
            if invalid_tools:
                return f"❌ TEST: Invalid tools requested: {invalid_tools}"

            # Filter engine tools to match request
            tools_to_use = [tool for tool in engine.tools if tool.name in requested_tool_names]

        print(f"🔧 TEST TOOLS: {len(tools_to_use)} tools will be used")
        for i, tool in enumerate(tools_to_use):
            print(f"   Tool {i + 1}: {tool.name}")

        # Get LLM and bind the specific tools
        llm = engine.get_model(model, **kwargs)
        llm_with_tools = llm.bind_tools(tools_to_use)

        # Build messages
        from core_app import _get_provider_specific_prompt
        provider = engine.get_provider(model)
        system_prompt = _get_provider_specific_prompt(provider, "")

        llm_messages = [{"role": "system", "content": system_prompt}]
        llm_messages.extend(conversation_history)
        llm_messages.append({"role": "user", "content": user_input})

        print(f"🔧 TEST MODEL: {type(llm).__name__} for {model}")
        print(f"🔍 TEST INVOKING: LLM with {len(tools_to_use)} tools bound")

        # Invoke with tools
        response = llm_with_tools.invoke(llm_messages)

        # Check if tools were called
        has_tool_calls = hasattr(response, 'tool_calls') and response.tool_calls
        print(f"🎯 TEST LLM RESPONSE: Tool calls = {has_tool_calls}")

        if has_tool_calls:
            tool_names = [tc["name"] for tc in response.tool_calls]
            print(f"   Tools called: {tool_names}")
            return f"✅ TEST SUCCESS: Tools called successfully: {tool_names}. Response: {getattr(response, 'content', 'No content')}"
        else:
            content = getattr(response, 'content', str(response))
            print(f"   Direct response: {content[:100]}...")
            return f"⚠️ TEST: No tools called. Response: {content}"

    except Exception as e:
        error_msg = str(e)
        print(f"❌ TEST ERROR: {error_msg}")
        return f"❌ TEST FAILED: {error_msg}"

@app.get("/test/health")
async def test_health():
    """Test health endpoint"""
    return {
        "status": "ok",
        "service": "tilores-tool-fix-test",
        "tools_available": len(engine.tools) if engine and engine.tools else 0,
        "engine_initialized": engine is not None
    }

@app.get("/test/tools")
async def test_tools():
    """Get available tools in OpenAI format"""
    tools_schema = get_tilores_tools_schema()
    return {
        "tools_count": len(tools_schema),
        "tools": [{"name": tool.function["name"], "description": tool.function["description"]} for tool in tools_schema]
    }

@app.post("/test/chat/completions")
async def test_chat_completions(chat_request: ChatCompletionRequest):
    """Test chat completions with proper tools handling"""

    # Convert messages
    messages = [{"role": msg.role, "content": msg.content} for msg in chat_request.messages]

    # CRITICAL TEST: Pass tools to run_chain
    response = run_chain_with_tools(
        messages,
        model=chat_request.model,
        tools=chat_request.tools
    )

    # Return OpenAI-compatible response
    return {
        "id": "test-" + str(hash(str(messages)))[-8:],
        "object": "chat.completion",
        "created": 1234567890,
        "model": chat_request.model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": response
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }

if __name__ == "__main__":
    print("🧪 Starting Tilores Tool Fix Test Server")
    print(f"🔧 Engine initialized: {engine is not None}")
    print(f"🔧 Tools available: {len(engine.tools) if engine and engine.tools else 0}")

    if engine and engine.tools:
        print("🔧 Available tools:")
        for i, tool in enumerate(engine.tools):
            print(f"   {i + 1}. {tool.name}")

    uvicorn.run(app, host="0.0.0.0", port=9001)
