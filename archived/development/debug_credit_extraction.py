#!/usr/bin/env python3
"""
Debug credit data extraction to find actual credit scores in Tilores data
"""

import json
import re
from dotenv import load_dotenv
load_dotenv()

from core_app import initialize_engine
import core_app

def debug_credit_data_extraction():
    """Debug what credit data is actually available in Tilores"""

    print("🔍 DEBUGGING CREDIT DATA EXTRACTION")
    print("=" * 60)

    initialize_engine()
    engine = core_app.engine

    if not engine or not engine.tools:
        print("❌ Engine not available")
        return

    # Get the tilores_search tool to see raw customer data
    tilores_search_tool = None
    for tool in engine.tools:
        if tool.name == "tilores_search":
            tilores_search_tool = tool
            break

    if not tilores_search_tool:
        print("❌ tilores_search tool not found")
        return

    # Get raw customer data for Esteban Price
    test_email = "e.j.price1986@gmail.com"
    print(f"🎯 Searching for credit data in: {test_email}")

    try:
        result = tilores_search_tool.invoke({"query": test_email})

        if isinstance(result, dict):
            data = result
        else:
            data = json.loads(str(result))

        # Look for ALL fields that might contain credit information
        print("\n🔍 SCANNING ALL FIELDS FOR CREDIT DATA:")

        entities = data["data"]["search"]["entities"]
        credit_fields_found = {}

        for entity in entities:
            records = entity.get("records", [])

            for i, record in enumerate(records):
                print(f"\n📋 RECORD {i + 1} - Scanning for credit fields:")

                for field_name, field_value in record.items():
                    if field_value is not None and str(field_value).strip():
                        # Check if field might contain credit information
                        field_lower = field_name.lower()
                        value_lower = str(field_value).lower()

                        # Look for credit-related field names
                        credit_keywords = [
                            'credit', 'score', 'experian', 'equifax', 'transunion',
                            'bureau', 'fico', 'vantage', 'utilization', 'balance',
                            'debt', 'tradeline', 'inquiry', 'report', 'rating'
                        ]

                        # Check if field name contains credit keywords
                        if any(keyword in field_lower for keyword in credit_keywords):
                            print(f"   🎯 CREDIT FIELD: {field_name} = {field_value}")
                            credit_fields_found[field_name] = field_value

                        # Check if field value contains credit score numbers (300 - 850)
                        score_match = re.search(r'\b([3 - 8][0 - 9]{2})\b', str(field_value))
                        if score_match:
                            score = int(score_match.group(1))
                            if 300 <= score <= 850:
                                print(f"   🎯 POTENTIAL SCORE: {field_name} = {field_value} (extracted: {score})")
                                credit_fields_found[f"{field_name}_SCORE"] = score

                        # Check for specific credit-related values
                        if any(term in value_lower for term in ['experian', 'equifax', 'transunion', 'fico']):
                            print(f"   🎯 BUREAU DATA: {field_name} = {field_value}")
                            credit_fields_found[field_name] = field_value

        print("\n📊 SUMMARY OF CREDIT FIELDS FOUND:")
        if credit_fields_found:
            for field, value in credit_fields_found.items():
                print(f"   ✅ {field}: {value}")
        else:
            print("   ❌ NO CREDIT FIELDS FOUND IN CUSTOMER DATA")

        # Test the credit extraction logic
        print("\n🔧 TESTING CREDIT EXTRACTION LOGIC:")

        # Simulate what the credit tool does
        all_credit_fields = []
        for field_name, field_value in credit_fields_found.items():
            if "credit" in field_name.lower() or "score" in field_name.lower():
                all_credit_fields.append(f"{field_name}: {field_value}")

        print(f"   Credit fields identified: {len(all_credit_fields)}")
        for field in all_credit_fields:
            print(f"   - {field}")

        # Test score extraction
        credit_scores = []
        for field_entry in all_credit_fields:
            if any(term in field_entry.lower() for term in ["score", "credit_score", "starting_credit"]):
                score_match = re.search(r"(\d{3,4})", field_entry)
                if score_match:
                    credit_scores.append(score_match.group(1))

        print(f"   Extracted scores: {credit_scores}")

        if not credit_scores:
            print("\n🚨 ROOT CAUSE IDENTIFIED:")
            print("   The customer data contains NO actual credit scores")
            print("   This explains why the credit tool returns template responses")
            print("   Need to check if credit scores are stored in different fields or different records")

            # Check if there are other record types that might have credit data
            print("\n🔍 CHECKING ALL RECORD SOURCES:")
            for entity in entities:
                records = entity.get("records", [])
                for record in records:
                    source = record.get("SOURCE", "Unknown")
                    record_id = record.get("id", "Unknown")
                    print(f"   📋 Record {record_id} from {source}")

                    # Look for any numeric values that could be scores
                    for field, value in record.items():
                        if isinstance(value, (int, float)) and 300 <= float(value) <= 850:
                            print(f"      🎯 POTENTIAL SCORE: {field} = {value}")
        else:
            print(f"\n✅ CREDIT SCORES FOUND: {credit_scores}")

        return len(credit_scores) > 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_alternative_credit_sources():
    """Test if credit data might be in different Tilores endpoints"""

    print("\n🔍 TESTING ALTERNATIVE CREDIT DATA SOURCES")
    print("=" * 60)

    engine = core_app.engine
    if not engine:
        return False

    # Test if there are other tools that might have credit data
    print("Available tools:")
    for tool in engine.tools:
        print(f"   - {tool.name}: {tool.description[:100]}...")

    # Test entity edges - might have credit relationships
    entity_edges_tool = None
    for tool in engine.tools:
        if tool.name == "tilores_entity_edges":
            entity_edges_tool = tool
            break

    if entity_edges_tool:
        print("\n🔧 Testing tilores_entity_edges for credit data...")
        try:
            # We need an entity ID from the customer search
            tilores_search_tool = None
            for tool in engine.tools:
                if tool.name == "tilores_search":
                    tilores_search_tool = tool
                    break

            if tilores_search_tool:
                search_result = tilores_search_tool.invoke({"query": "e.j.price1986@gmail.com"})
                if isinstance(search_result, dict):
                    entities = search_result["data"]["search"]["entities"]
                    if entities:
                        entity_id = entities[0]["id"]
                        print(f"   Testing entity edges for: {entity_id}")

                        edges_result = entity_edges_tool.invoke({"entity_id": entity_id})
                        print(f"   Entity edges result: {str(edges_result)[:200]}...")

                        # Look for credit-related edges
                        edges_str = str(edges_result).lower()
                        if any(term in edges_str for term in ['credit', 'score', 'bureau', 'experian']):
                            print("   🎯 CREDIT DATA FOUND in entity edges!")
                        else:
                            print("   ❌ No credit data in entity edges")
        except Exception as e:
            print(f"   ❌ Error testing entity edges: {e}")

    return False

if __name__ == "__main__":
    print("🚨 DEBUGGING CREDIT DATA EXTRACTION ISSUE")
    print("=" * 70)

    # Test 1: Look for credit data in customer records
    has_credit_data = debug_credit_data_extraction()

    # Test 2: Check alternative sources
    has_alternative_sources = test_alternative_credit_sources()

    print("\n" + "=" * 70)
    print("📊 CREDIT DATA AVAILABILITY:")
    print(f"   Credit scores in customer records: {'✅ FOUND' if has_credit_data else '❌ NOT FOUND'}")
    print(f"   Alternative credit sources: {'✅ FOUND' if has_alternative_sources else '❌ NOT FOUND'}")

    if not has_credit_data and not has_alternative_sources:
        print("\n🚨 CRITICAL FINDING:")
        print("   Tilores customer data does NOT contain actual credit scores")
        print("   This explains why queries return template responses")
        print("   Options:")
        print("   1. Credit scores may be in a separate Tilores endpoint")
        print("   2. Credit scores may need to be pulled from external bureau APIs")
        print("   3. Credit scores may be stored in different field names")
        print("   4. This customer may not have credit data in the system")
    else:
        print("\n✅ CREDIT DATA AVAILABLE - Can implement accurate responses")
