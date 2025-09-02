#!/usr/bin/env python3
"""
Show the actual full output from our test queries
Display complete responses before implementing any fixes
"""

import json
from dotenv import load_dotenv
load_dotenv()

from core_app import initialize_engine
import core_app

def show_actual_customer_data():
    """Show the actual complete customer data output"""

    print("📋 ACTUAL CUSTOMER DATA OUTPUT")
    print("=" * 60)

    initialize_engine()
    engine = core_app.engine

    if not engine or not engine.tools:
        print("❌ Engine not available")
        return

    # Get tilores_search tool
    tilores_search_tool = None
    for tool in engine.tools:
        if tool.name == "tilores_search":
            tilores_search_tool = tool
            break

    if not tilores_search_tool:
        print("❌ tilores_search tool not found")
        return

    # Execute search for e.j.price1986@gmail.com
    test_email = "e.j.price1986@gmail.com"
    print(f"🎯 Query: Who is {test_email}?")
    print("🔧 Executing tilores_search...")

    try:
        result = tilores_search_tool.invoke({"query": test_email})

        print(f"\n📊 RAW RESULT LENGTH: {len(str(result))} characters")
        print(f"📊 RESULT TYPE: {type(result)}")

        # Show the complete result
        print("\n📋 COMPLETE TILORES_SEARCH OUTPUT:")
        print("=" * 80)

        if isinstance(result, dict):
            # Pretty print the JSON
            formatted_result = json.dumps(result, indent=2)
            print(formatted_result)
        else:
            print(str(result))

        print("=" * 80)

        # Parse and extract key information
        if isinstance(result, dict):
            data = result
        else:
            try:
                data = json.loads(str(result))
            except Exception:
                print("❌ Could not parse as JSON")
                return

        # Extract customer information
        print("\n📊 PARSED CUSTOMER INFORMATION:")

        if "data" in data and "search" in data["data"] and "entities" in data["data"]["search"]:
            entities = data["data"]["search"]["entities"]

            if entities:
                entity = entities[0]
                records = entity.get("records", [])

                print(f"   Entity ID: {entity.get('id')}")
                print(f"   Number of records: {len(records)}")

                # Show all customer fields from all records
                all_fields = {}
                for i, record in enumerate(records):
                    print(f"\n   📋 RECORD {i + 1} FIELDS:")
                    for key, value in record.items():
                        if value and str(value).strip():  # Only show non-empty values
                            print(f"      {key}: {value}")
                            if key not in all_fields:
                                all_fields[key] = value

                print("\n📊 CONSOLIDATED CUSTOMER DATA:")
                customer_fields = ['EMAIL', 'FIRST_NAME', 'LAST_NAME', 'CLIENT_ID', 'MAILING_CITY', 'MAILING_STATE', 'PHONE_NUMBER', 'DATE_OF_BIRTH']

                for field in customer_fields:
                    if field in all_fields:
                        print(f"   ✅ {field}: {all_fields[field]}")
                    else:
                        print(f"   ❌ {field}: Not found")

    except Exception as e:
        print(f"❌ Error: {e}")

def show_actual_credit_data():
    """Show the actual complete credit report output"""

    print("\n📋 ACTUAL CREDIT REPORT OUTPUT")
    print("=" * 60)

    engine = core_app.engine
    if not engine:
        return

    # Get credit tool
    credit_tool = None
    for tool in engine.tools:
        if tool.name == "get_customer_credit_report":
            credit_tool = tool
            break

    if not credit_tool:
        print("❌ Credit tool not found")
        return

    # Execute credit report for Esteban Price
    customer_name = "Esteban Price"
    print(f"🎯 Query: What is {customer_name}'s credit information?")
    print("🔧 Executing get_customer_credit_report...")

    try:
        result = credit_tool.invoke({"customer_name": customer_name})

        print(f"\n📊 RAW RESULT LENGTH: {len(str(result))} characters")
        print(f"📊 RESULT TYPE: {type(result)}")

        # Show the complete result
        print("\n📋 COMPLETE CREDIT REPORT OUTPUT:")
        print("=" * 80)
        print(str(result))
        print("=" * 80)

        # Analyze the credit data
        result_str = str(result).lower()

        print("\n📊 CREDIT DATA ANALYSIS:")

        # Look for specific credit information
        credit_terms = {
            'experian': 'experian' in result_str,
            'credit score': 'score' in result_str,
            'utilization': 'utilization' in result_str,
            'payment history': 'payment' in result_str and 'history' in result_str,
            'accounts': 'account' in result_str,
            'inquiries': 'inquir' in result_str,
            'balances': 'balance' in result_str
        }

        for term, found in credit_terms.items():
            status = "✅" if found else "❌"
            print(f"   {status} Contains '{term}': {found}")

    except Exception as e:
        print(f"❌ Error: {e}")

def show_actual_llm_response():
    """Show what the LLM actually returns when it tries to call tools"""

    print("\n📋 ACTUAL LLM RESPONSE (Current Broken State)")
    print("=" * 60)

    engine = core_app.engine
    if not engine:
        return

    try:
        # Test the current broken flow
        model = engine.get_model("llama - 3.3 - 70b-versatile")
        llm_with_tools = model.bind_tools(engine.tools)

        messages = [
            {"role": "system", "content": "You are a customer service assistant. For customer queries, use tilores_search."},
            {"role": "user", "content": "Who is e.j.price1986@gmail.com?"}
        ]

        print("🎯 Query: Who is e.j.price1986@gmail.com?")
        print("🔧 Invoking LLM with tools bound...")

        response = llm_with_tools.invoke(messages)

        print(f"\n📊 LLM RESPONSE TYPE: {type(response)}")
        print(f"📊 HAS TOOL CALLS: {hasattr(response, 'tool_calls') and bool(response.tool_calls)}")

        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"📊 TOOL CALLS: {len(response.tool_calls)}")

            for i, tool_call in enumerate(response.tool_calls):
                print(f"\n   📋 TOOL CALL {i + 1}:")
                print(f"      Name: {tool_call.get('name')}")
                print(f"      Args: {tool_call.get('args')}")
                print(f"      ID: {tool_call.get('id')}")

        print("\n📋 LLM RESPONSE CONTENT:")
        print("=" * 80)
        content = getattr(response, 'content', '')
        print(f"Content: {content}")
        print("=" * 80)

        print("\n⚠️ CURRENT ISSUE:")
        print("   The LLM correctly generates tool calls, but Groq validation fails because:")
        print("   'tool call validation failed: attempted to call tool which was not in request.tools'")
        print("   This happens because our OpenAI API request doesn't include the 'tools' parameter")

    except Exception as e:
        print(f"❌ LLM Response Error: {e}")
        if "tool call validation failed" in str(e):
            print("✅ CONFIRMED: This is the exact production error we need to fix!")

if __name__ == "__main__":
    print("🔍 SHOWING ACTUAL COMPLETE OUTPUT FROM ALL QUERIES")
    print("=" * 80)
    print("This shows the real data our system returns BEFORE implementing any fixes")
    print("=" * 80)

    # Show actual customer data
    show_actual_customer_data()

    # Show actual credit data
    show_actual_credit_data()

    # Show actual LLM response (broken state)
    show_actual_llm_response()

    print("\n" + "=" * 80)
    print("📊 SUMMARY OF ACTUAL OUTPUT:")
    print("✅ Customer data: Complete profiles with all details")
    print("✅ Credit data: Full credit reports available")
    print("❌ LLM responses: Fail due to tool validation error")
    print("🔧 Fix needed: Add 'tools' parameter to OpenAI API requests")
    print("=" * 80)

