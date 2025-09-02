#!/usr/bin/env python3
"""
Temporal Analysis Quick Fix
Fix the 422 error in temporal analysis to complete Phase 2
"""

from dotenv import load_dotenv
load_dotenv()

def fix_temporal_analysis():
    """Quick fix for temporal analysis 422 error"""

    print("🔧 TEMPORAL ANALYSIS QUICK FIX")
    print("=" * 50)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return

    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    # Test different query structures to find what works
    print("\n🔍 TESTING TEMPORAL QUERY STRUCTURES")
    print("-" * 40)

    # Test 1: Minimal temporal query
    print("Test 1: Minimal temporal query...")
    query1 = """
    query MinimalTemporalTest {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CreditReportFirstIssuedDate
            }}
            PHONE_EXTERNAL
            CREATED_DATE
          }}
        }}
      }}
    }}
    """

    try:
        result1 = tilores_api.gql(query1)
        if result1 and 'data' in result1:
            print("✅ Minimal temporal query works")
            records = result1['data']['entity']['entity']['records']
            print(f"   Found {len(records)} records")
        else:
            print("❌ Minimal temporal query failed")
    except Exception as e:
        print(f"❌ Minimal temporal query error: {e}")

    # Test 2: Separate credit and phone queries
    print("\nTest 2: Separate credit and phone queries...")
    query2 = """
    query SeparateTemporalTest {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CreditReportFirstIssuedDate
              CREDIT_SCORE {{
                Value
              }}
            }}
          }}
        }}
      }}
    }}
    """

    try:
        result2 = tilores_api.gql(query2)
        if result2 and 'data' in result2:
            print("✅ Separate credit query works")
            records = result2['data']['entity']['entity']['records']
            credit_responses = sum(1 for r in records if r.get('CREDIT_RESPONSE'))
            print(f"   Found {credit_responses} credit responses")
        else:
            print("❌ Separate credit query failed")
    except Exception as e:
        print(f"❌ Separate credit query error: {e}")

    # Test 3: Phone data only
    print("\nTest 3: Phone data only...")
    query3 = """
    query PhoneTemporalTest {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            PHONE_EXTERNAL
            CREATED_DATE
            UPDATED_DATE
          }}
        }}
      }}
    }}
    """

    try:
        result3 = tilores_api.gql(query3)
        if result3 and 'data' in result3:
            print("✅ Phone temporal query works")
            records = result3['data']['entity']['entity']['records']
            phone_records = sum(1 for r in records if r.get('PHONE_EXTERNAL'))
            print(f"   Found {phone_records} phone records")
        else:
            print("❌ Phone temporal query failed")
    except Exception as e:
        print(f"❌ Phone temporal query error: {e}")

    print("\n🎯 TEMPORAL ANALYSIS QUICK FIX COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    fix_temporal_analysis()
