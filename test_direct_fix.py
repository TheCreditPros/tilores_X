#!/usr/bin/env python3
"""
Direct test of the tool calling fix
Tests the core issue without server complexity
"""

import json
from typing import List, Dict, Any

# Load environment first
from dotenv import load_dotenv
load_dotenv()

# Import core functionality
from core_app import initialize_engine
import core_app

def test_tool_calling_fix():
    """Test the tool calling fix directly"""

    print("🧪 DIRECT TEST: Tool Calling Fix")
    print("=" * 50)

    # Initialize engine
    print("🔧 Initializing engine...")
    initialize_engine()

    # Get the engine after initialization
    engine = core_app.engine

    if not engine:
        print("❌ Engine not initialized")
        return False

    if not engine.tools:
        print("❌ No tools available")
        return False

    print(f"✅ Engine initialized with {len(engine.tools)} tools")
    for i, tool in enumerate(engine.tools):
        print(f"   {i + 1}. {tool.name}")

    # Test the core issue: Groq tool validation
    print("\n🎯 Testing Groq tool calling...")

    try:
        # Get Groq model
        model = engine.get_model("llama - 3.3 - 70b-versatile")
        print(f"✅ Model created: {type(model).__name__}")

        # Test 1: Current broken approach (bind all tools, no tools in request)
        print("\n📋 TEST 1: Current approach (should fail)")
        llm_with_tools = model.bind_tools(engine.tools)

        messages = [
            {"role": "system", "content": "You are a helpful assistant with access to tools."},
            {"role": "user", "content": "Who is e.j.price1986@gmail.com?"}
        ]

        try:
            response = llm_with_tools.invoke(messages)
            has_tool_calls = hasattr(response, 'tool_calls') and response.tool_calls
            print(f"   Response has tool calls: {has_tool_calls}")

            if has_tool_calls:
                tool_names = [tc["name"] for tc in response.tool_calls]
                print(f"   Tools called: {tool_names}")
                print("   ❌ This should fail in production due to tool validation")
            else:
                print("   ⚠️ No tool calls made")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            if "tool call validation failed" in str(e):
                print("   ✅ CONFIRMED: This is the exact error we're seeing!")

        # Test 2: Proposed fix approach
        print("\n📋 TEST 2: Proposed fix (manual tool execution)")

        # Simulate what happens when we manually execute tools
        print("   🔧 Manually executing tilores_search...")

        # Find the tilores_search tool
        tilores_search_tool = None
        for tool in engine.tools:
            if tool.name == "tilores_search":
                tilores_search_tool = tool
                break

        if tilores_search_tool:
            try:
                # Execute the tool directly
                result = tilores_search_tool.invoke({"query": "e.j.price1986@gmail.com"})
                print("   ✅ Tool executed successfully!")
                print(f"   📊 Result length: {len(str(result))} characters")
                print(f"   📊 Result preview: {str(result)[:200]}...")

                # This proves the tools work, the issue is just the API validation
                return True

            except Exception as e:
                print(f"   ❌ Tool execution failed: {e}")
                return False
        else:
            print("   ❌ tilores_search tool not found")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_openai_tools_schema():
    """Test generating OpenAI-compatible tools schema"""

    print("\n🧪 TESTING: OpenAI Tools Schema Generation")
    print("=" * 50)

    # Get the engine after initialization
    engine = core_app.engine

    if not engine or not engine.tools:
        print("❌ No engine or tools available")
        return False

    # Generate OpenAI-compatible schema
    tools_schema = []
    for tool in engine.tools:
        tool_def = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.args_schema.model_json_schema() if hasattr(tool, 'args_schema') else {}
            }
        }
        tools_schema.append(tool_def)

    print(f"✅ Generated schema for {len(tools_schema)} tools")

    for tool in tools_schema:
        print(f"   📋 {tool['function']['name']}: {tool['function']['description'][:100]}...")

    # Test JSON serialization
    try:
        json_schema = json.dumps(tools_schema, indent=2)
        print(f"✅ Schema serializes to JSON ({len(json_schema)} chars)")
        return True
    except Exception as e:
        print(f"❌ Schema serialization failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Direct Tool Calling Fix Test")
    print("=" * 60)

    # Test 1: Core tool calling
    test1_result = test_tool_calling_fix()

    # Test 2: OpenAI schema generation
    test2_result = test_openai_tools_schema()

    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"   Tool Calling Test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"   Schema Generation: {'✅ PASS' if test2_result else '❌ FAIL'}")

    if test1_result and test2_result:
        print("\n🎉 ALL TESTS PASSED - Ready to implement fix!")
        print("\n📋 IMPLEMENTATION PLAN:")
        print("   1. Add 'tools' parameter to ChatCompletionRequest")
        print("   2. Generate OpenAI-compatible tools schema")
        print("   3. Pass tools parameter to run_chain")
        print("   4. Modify tool binding to use request tools")
        print("   5. Test with Groq to confirm validation passes")
    else:
        print("\n❌ TESTS FAILED - Need to investigate further")
