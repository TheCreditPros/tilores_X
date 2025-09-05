#!/usr/bin/env python3
"""
Debug the GraphQL schema discovery to see what credit fields are actually available
"""

import json
from dotenv import load_dotenv
load_dotenv()

from core_app import initialize_engine, get_all_tilores_fields
import core_app

def debug_schema_discovery():
    """Debug what fields are actually discovered from the GraphQL schema"""

    print("🔍 DEBUGGING GRAPHQL SCHEMA DISCOVERY")
    print("=" * 60)

    initialize_engine()
    engine = core_app.engine

    if not engine or not engine.tilores:
        print("❌ Engine or Tilores not available")
        return

    print("🔧 Getting all fields from Tilores GraphQL schema...")

    # Get the actual discovered fields
    discovered_fields = get_all_tilores_fields(engine.tilores)

    print(f"📊 Total fields discovered: {len(discovered_fields)}")

    # Look for credit-related fields
    credit_fields = {}
    score_fields = {}

    for field_name, available in discovered_fields.items():
        if available:  # Only look at available fields
            field_lower = field_name.lower()

            # Look for credit-related fields
            if any(term in field_lower for term in ['credit', 'score', 'fico', 'vantage', 'experian', 'transunion', 'equifax']):
                credit_fields[field_name] = available

            # Look specifically for score fields
            if 'score' in field_lower:
                score_fields[field_name] = available

    print(f"\n🎯 CREDIT-RELATED FIELDS FOUND: {len(credit_fields)}")
    for field, available in credit_fields.items():
        status = "✅" if available else "❌"
        print(f"   {status} {field}")

    print(f"\n🎯 SCORE-SPECIFIC FIELDS FOUND: {len(score_fields)}")
    for field, available in score_fields.items():
        status = "✅" if available else "❌"
        print(f"   {status} {field}")

    # Check if the expected credit fields from field_discovery_system.py are in the schema
    expected_credit_fields = [
        "STARTING_CREDIT_SCORE",
        "CURRENT_CREDIT_SCORE",
        "FICO_SCORE",
        "VANTAGE_SCORE",
        "CREDIT_KARMA_SCORE",
        "TRANSUNION_REPORT",
        "EXPERIAN_REPORT",
        "EQUIFAX_REPORT",
        "CREDIT_UTILIZATION",
        "PAYMENT_HISTORY"
    ]

    print("\n🔍 CHECKING EXPECTED CREDIT FIELDS:")
    found_expected = 0
    for field in expected_credit_fields:
        if field in discovered_fields and discovered_fields[field]:
            print(f"   ✅ {field}: Available")
            found_expected += 1
        else:
            print(f"   ❌ {field}: Not found in schema")

    print(f"\n📊 EXPECTED FIELDS FOUND: {found_expected}/{len(expected_credit_fields)}")

    if found_expected == 0:
        print("\n🚨 CRITICAL ISSUE: NO EXPECTED CREDIT FIELDS FOUND IN SCHEMA")
        print("   This means the field discovery system has hardcoded fields")
        print("   that don't actually exist in the Tilores GraphQL schema")
        print("   Need to use the actual schema fields instead")

        # Show what fields ARE available that might be credit-related
        print("\n🔧 ALTERNATIVE CREDIT FIELDS IN SCHEMA:")
        alternative_fields = []
        for field_name in discovered_fields:
            if discovered_fields[field_name]:
                field_lower = field_name.lower()
                if any(term in field_lower for term in ['credit', 'score', 'bureau', 'report', 'debt', 'balance', 'payment']):
                    alternative_fields.append(field_name)

        for field in sorted(alternative_fields):
            print(f"   🔍 {field}")

        return False
    else:
        print("\n✅ SCHEMA HAS CREDIT FIELDS - Can implement accurate credit tool")
        return True

def debug_graphql_types():
    """Debug the GraphQL types to understand the credit data structure"""

    print("\n🔍 DEBUGGING GRAPHQL TYPES FOR CREDIT DATA")
    print("=" * 60)

    engine = core_app.engine
    if not engine or not engine.tilores:
        print("❌ Engine not available")
        return

    # Get the schema introspection
    schema_query = """
    {
      __schema {
        types {
          name
          fields {
            name
            type {
              name
              kind
            }
          }
        }
      }
    }
    """

    try:
        schema_result = engine.tilores.gql(schema_query)

        # Look for credit-related types
        credit_types = []

        for type_info in schema_result.get("data", {}).get("__schema", {}).get("types", []):
            type_name = type_info.get("name", "")

            if any(term in type_name.lower() for term in ['credit', 'score', 'bureau', 'report']):
                credit_types.append(type_info)

        print(f"🎯 CREDIT-RELATED GRAPHQL TYPES: {len(credit_types)}")

        for type_info in credit_types:
            type_name = type_info.get("name", "")
            fields = type_info.get("fields", [])

            print(f"\n📋 TYPE: {type_name}")
            print(f"   Fields: {len(fields) if fields else 0}")

            if fields:
                for field in fields[:10]:  # Show first 10 fields
                    field_name = field.get("name", "")
                    field_type = field.get("type", {}).get("name", "Unknown")
                    print(f"     - {field_name}: {field_type}")

                if len(fields) > 10:
                    print(f"     ... and {len(fields) - 10} more fields")

        return len(credit_types) > 0

    except Exception as e:
        print(f"❌ Error getting schema: {e}")
        return False

def test_actual_credit_query():
    """Test a GraphQL query that should return credit data"""

    print("\n🧪 TESTING ACTUAL CREDIT DATA QUERY")
    print("=" * 60)

    engine = core_app.engine
    if not engine or not engine.tilores:
        print("❌ Engine not available")
        return

    # Test query for customer with potential credit data
    test_query = """
    query TestCreditData($email: String!) {
      search(input: {
        filters: [
          { field: "EMAIL", value: $email }
        ]
      }) {
        entities {
          id
          hits
          records {
            id
            EMAIL
            FIRST_NAME
            LAST_NAME
            CLIENT_ID
            # Try to get any credit-related fields that exist
            SOURCE
          }
        }
      }
    }
    """

    try:
        result = engine.tilores.gql(test_query, {"email": "e.j.price1986@gmail.com"})

        print("📋 GRAPHQL QUERY RESULT:")
        print(json.dumps(result, indent=2)[:1000] + "...")

        # Check if we got data
        entities = result.get("data", {}).get("search", {}).get("entities", [])
        if entities:
            print(f"\n✅ Found {len(entities)} entities")

            # Look at the records to see what fields are actually available
            for entity in entities:
                records = entity.get("records", [])
                print(f"   Entity has {len(records)} records")

                for i, record in enumerate(records[:3]):  # Check first 3 records
                    print(f"   Record {i + 1} fields: {list(record.keys())}")
        else:
            print("❌ No entities found")

    except Exception as e:
        print(f"❌ Error executing query: {e}")

if __name__ == "__main__":
    print("🚨 DEBUGGING GRAPHQL SCHEMA DISCOVERY FOR CREDIT FIELDS")
    print("=" * 70)

    # Test 1: Check discovered fields
    has_expected_fields = debug_schema_discovery()

    # Test 2: Check GraphQL types
    has_credit_types = debug_graphql_types()

    # Test 3: Test actual query
    test_actual_credit_query()

    print("\n" + "=" * 70)
    print("📊 SCHEMA DISCOVERY ANALYSIS:")
    print(f"   Expected credit fields in schema: {'✅ YES' if has_expected_fields else '❌ NO'}")
    print(f"   Credit-related GraphQL types: {'✅ YES' if has_credit_types else '❌ NO'}")

    if not has_expected_fields:
        print("\n🚨 ROOT CAUSE IDENTIFIED:")
        print("   The field_discovery_system.py has hardcoded credit fields")
        print("   that don't exist in the actual Tilores GraphQL schema")
        print("   Need to use the real schema fields for credit data")
    else:
        print("\n✅ SCHEMA IS CORRECT - Issue is in credit tool implementation")

