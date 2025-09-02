#!/usr/bin/env python3
"""
Debug customer data extraction to understand the data structure
"""

import json
from dotenv import load_dotenv
load_dotenv()

from core_app import initialize_engine
import core_app

def debug_customer_data():
    """Debug the actual customer data structure"""

    print("🔍 DEBUGGING CUSTOMER DATA STRUCTURE")
    print("=" * 50)

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

    # Execute search
    test_email = "e.j.price1986@gmail.com"
    print(f"🎯 Searching for: {test_email}")

    try:
        result = tilores_search_tool.invoke({"query": test_email})
        print(f"✅ Search completed, result length: {len(str(result))}")

        # Parse result
        if isinstance(result, dict):
            data = result
        else:
            try:
                data = json.loads(str(result))
            except Exception:
                print("❌ Result is not valid JSON")
                print(f"Raw result: {str(result)[:500]}...")
                return

        # Debug data structure
        print("\n📊 DATA STRUCTURE ANALYSIS:")
        print(f"Root keys: {list(data.keys())}")

        if "data" in data:
            print(f"data keys: {list(data['data'].keys())}")

            if "search" in data["data"]:
                search_data = data["data"]["search"]
                print(f"search keys: {list(search_data.keys())}")

                if "entities" in search_data:
                    entities = search_data["entities"]
                    print(f"Found {len(entities)} entities")

                    if entities:
                        first_entity = entities[0]
                        print(f"First entity keys: {list(first_entity.keys())}")

                        if "records" in first_entity:
                            records = first_entity["records"]
                            print(f"Found {len(records)} records")

                            if records:
                                first_record = records[0]
                                print(f"First record keys: {list(first_record.keys())}")

                                if "record" in first_record:
                                    record_data = first_record["record"]
                                    print(f"Record data keys: {list(record_data.keys())}")

                                    # Look for customer fields
                                    customer_fields = {}
                                    for key, value in record_data.items():
                                        if any(field in key.lower() for field in ['email', 'name', 'client', 'first', 'last']):
                                            customer_fields[key] = value

                                    print("\n📋 CUSTOMER FIELDS FOUND:")
                                    for key, value in customer_fields.items():
                                        print(f"   {key}: {value}")

                                    # Check all records for customer data
                                    print(f"\n📋 CHECKING ALL {len(records)} RECORDS:")
                                    all_customer_data = {}

                                    for i, record in enumerate(records):
                                        if "record" in record:
                                            rec_data = record["record"]
                                            print(f"   Record {i + 1} keys: {list(rec_data.keys())}")

                                            # Extract key customer fields
                                            for key, value in rec_data.items():
                                                if key in ['email', 'firstName', 'lastName', 'clientId', 'Email', 'FirstName', 'LastName', 'ClientId']:
                                                    if key not in all_customer_data and value:
                                                        all_customer_data[key] = value

                                    print("\n🎯 CONSOLIDATED CUSTOMER DATA:")
                                    for key, value in all_customer_data.items():
                                        print(f"   {key}: {value}")

                                    if all_customer_data:
                                        print("\n✅ CUSTOMER DATA SUCCESSFULLY EXTRACTED!")

                                        # Test credit report if we have name
                                        first_name = all_customer_data.get('firstName') or all_customer_data.get('FirstName')
                                        last_name = all_customer_data.get('lastName') or all_customer_data.get('LastName')

                                        if first_name and last_name:
                                            customer_name = f"{first_name} {last_name}"
                                            print(f"\n🎯 Testing credit report for: {customer_name}")

                                            # Get credit tool
                                            credit_tool = None
                                            for tool in engine.tools:
                                                if tool.name == "get_customer_credit_report":
                                                    credit_tool = tool
                                                    break

                                            if credit_tool:
                                                try:
                                                    credit_result = credit_tool.invoke({"customer_name": customer_name})
                                                    print(f"✅ Credit report retrieved ({len(str(credit_result))} chars)")

                                                    # Check for credit scores
                                                    credit_str = str(credit_result).lower()
                                                    if "experian" in credit_str and "score" in credit_str:
                                                        print("✅ Credit scores found in report")
                                                    else:
                                                        print("⚠️ Credit scores not clearly identified")

                                                except Exception as e:
                                                    print(f"❌ Credit report error: {e}")
                                    else:
                                        print("\n❌ NO CUSTOMER DATA EXTRACTED")

                                        # Show sample of what we have
                                        print("\n📊 SAMPLE RECORD DATA:")
                                        sample_record = records[0]["record"] if records and "record" in records[0] else {}
                                        for key, value in list(sample_record.items())[:10]:
                                            print(f"   {key}: {str(value)[:100]}...")

                                else:
                                    print("❌ No 'record' key in first record")
                            else:
                                print("❌ No records found")
                        else:
                            print("❌ No 'records' key in first entity")
                    else:
                        print("❌ No entities found")
                else:
                    print("❌ No 'entities' key in search data")
            else:
                print("❌ No 'search' key in data")
        else:
            print("❌ No 'data' key in result")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_customer_data()

