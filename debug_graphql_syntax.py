#!/usr/bin/env python3
"""
Debug GraphQL syntax for Record Insights queries
Fix 422 error by testing simpler queries first
"""

import json
from dotenv import load_dotenv
load_dotenv()

def test_basic_record_insights():
    """Test basic Record Insights query to identify syntax issues"""

    print("🔍 DEBUGGING GRAPHQL SYNTAX FOR RECORD INSIGHTS")
    print("=" * 60)

    try:
        from core_app import initialize_engine
        import core_app

        initialize_engine()
        engine = core_app.engine

        if not engine or not engine.tilores:
            print("❌ Tilores not available")
            return False

        # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Test 1: Basic entity query (should work)
        print("🧪 Test 1: Basic entity query...")
        basic_query = """
        query BasicEntity {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              id
            }}
          }}
        }}
        """

        try:
            result1 = engine.tilores.gql(basic_query)
            print("✅ Basic entity query works")
            print(f"   Result: {json.dumps(result1, indent=2)}")
        except Exception as e:
            print(f"❌ Basic entity query failed: {e}")
            return False

        # Test 2: Simple recordInsights query
        print("\n🧪 Test 2: Simple recordInsights...")
        simple_insights_query = """
        query SimpleInsights {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              id
              recordInsights {{
                allEmails: valuesDistinct(field: "EMAIL")
              }}
            }}
          }}
        }}
        """

        try:
            result2 = engine.tilores.gql(simple_insights_query)
            print("✅ Simple recordInsights works")
            print(f"   Emails found: {result2.get('data', {}).get('entity', {}).get('entity', {}).get('recordInsights', {}).get('allEmails', [])}")
        except Exception as e:
            print(f"❌ Simple recordInsights failed: {e}")
            print("   This indicates Record Insights syntax issue")

        # Test 3: Credit score field test
        print("\n🧪 Test 3: Credit score field test...")
        credit_field_query = """
        query CreditFieldTest {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              id
              recordInsights {{
                creditScores: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Value")
              }}
            }}
          }}
        }}
        """

        try:
            result3 = engine.tilores.gql(credit_field_query)
            print("✅ Credit score field works")
            scores = result3.get('data', {}).get('entity', {}).get('entity', {}).get('recordInsights', {}).get('creditScores', [])
            print(f"   Credit scores found: {len(scores)} - {scores[:3] if scores else 'None'}")
        except Exception as e:
            print(f"❌ Credit score field failed: {e}")
            print("   This indicates the field path is wrong")

        # Test 4: Check what fields actually exist
        print("\n🧪 Test 4: Field existence check...")
        field_check_query = """
        query FieldCheck {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              id
              records {{
                id
              }}
            }}
          }}
        }}
        """

        try:
            result4 = engine.tilores.gql(field_check_query)
            print("✅ Records query works")
            records = result4.get('data', {}).get('entity', {}).get('entity', {}).get('records', [])
            print(f"   Records found: {len(records)}")

            if records:
                # Check first record structure
                first_record = records[0]
                print(f"   First record keys: {list(first_record.keys())}")

                # Look for credit-related fields
                credit_fields = [k for k in first_record.keys() if 'CREDIT' in k.upper()]
                print(f"   Credit-related fields: {credit_fields}")

        except Exception as e:
            print(f"❌ Records query failed: {e}")

        return True

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_working_record_insights_patterns():
    """Test Record Insights patterns that are known to work"""

    print("\n🔍 TESTING WORKING RECORD INSIGHTS PATTERNS")
    print("=" * 60)

    try:
        from core_app import initialize_engine
        import core_app

        initialize_engine()
        engine = core_app.engine

        # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Test patterns from Tilores documentation
        working_patterns = [
            {
                "name": "Basic valuesDistinct",
                "query": """
                query WorkingPattern1 {{
                  entity(input: {{ id: "{entity_id}" }}) {{
                    entity {{
                      recordInsights {{
                        emails: valuesDistinct(field: "EMAIL")
                        names: valuesDistinct(field: "FIRST_NAME")
                      }}
                    }}
                  }}
                }}
                """
            },
            {
                "name": "FrequencyDistribution",
                "query": """
                query WorkingPattern2 {{
                  entity(input: {{ id: "{entity_id}" }}) {{
                    entity {{
                      recordInsights {{
                        topNames: frequencyDistribution(field: "FIRST_NAME", direction: DESC) {{
                          value
                          frequency
                        }}
                      }}
                    }}
                  }}
                }}
                """
            }
        ]

        for pattern in working_patterns:
            print(f"\n🧪 Testing: {pattern['name']}")
            try:
                result = engine.tilores.gql(pattern['query'])
                print(f"✅ {pattern['name']} works")

                insights = result.get('data', {}).get('entity', {}).get('entity', {}).get('recordInsights', {})
                print(f"   Insights keys: {list(insights.keys())}")

                for key, value in insights.items():
                    if isinstance(value, list):
                        print(f"   {key}: {len(value)} items - {value[:2] if value else 'None'}")
                    else:
                        print(f"   {key}: {value}")

            except Exception as e:
                print(f"❌ {pattern['name']} failed: {e}")

        return True

    except Exception as e:
        print(f"❌ Pattern test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 STARTING GRAPHQL SYNTAX DEBUGGING")
    print("=" * 60)

    test1_result = test_basic_record_insights()
    test2_result = test_working_record_insights_patterns()

    print("\n" + "=" * 60)
    print("📊 DEBUG RESULTS:")
    print(f"   • Basic Record Insights: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"   • Working Patterns: {'✅ PASS' if test2_result else '❌ FAIL'}")

    if test1_result and test2_result:
        print("\n🎯 DIAGNOSIS: Record Insights syntax is working")
        print("   Issue is likely in our complex query structure")
    else:
        print("\n⚠️  DIAGNOSIS: Fundamental Record Insights issue")
        print("   Need to check Tilores API version or permissions")

