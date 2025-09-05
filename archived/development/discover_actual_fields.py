#!/usr/bin/env python3
"""
Discover Actual Credit Summary Fields
Use Record Insights to find what credit summary fields actually exist
"""

from dotenv import load_dotenv
load_dotenv()

def discover_actual_fields():
    """Use Record Insights to discover actual credit summary fields"""

    print("🔍 DISCOVERING ACTUAL CREDIT SUMMARY FIELDS")
    print("=" * 60)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized successfully")
    except Exception as e:
        print(f"❌ Tilores API initialization failed: {e}")
        return

    # Use the working entity ID
    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    print(f"\n🔍 DISCOVERING FIELDS FOR ENTITY: {entity_id}")
    print("-" * 50)

    # Query 1: Use Record Insights to find all available fields
    print("\n🔍 QUERY 1: RECORD INSIGHTS - ALL FIELDS")
    print("-" * 40)

    all_fields_query = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          recordInsights {
            allFields: valuesDistinct(field: "*")
          }
        }
      }
    }
    """

    try:
        result = tilores_api.gql(all_fields_query, {"id": entity_id})
        if result and 'data' in result:
            entity = result['data']['entity']['entity']
            record_insights = entity.get('recordInsights', {})
            all_fields = record_insights.get('allFields', [])

            print(f"✅ All fields discovered: {len(all_fields)}")

            # Look for credit summary related fields
            credit_summary_fields = []
            for field in all_fields:
                if any(keyword in field.lower() for keyword in [
                    "summary", "total", "count", "utilization", "inquiry",
                    "average", "rollup", "aggregate", "credit"
                ]):
                    credit_summary_fields.append(field)

            if credit_summary_fields:
                print("\n📊 CREDIT SUMMARY RELATED FIELDS:")
                for field in credit_summary_fields:
                    print(f"   - {field}")
            else:
                print("   ❌ No credit summary fields found")

        else:
            print("   ❌ All fields query failed")

    except Exception as e:
        print(f"   ❌ All fields query failed: {e}")

    # Query 2: Look for specific summary field patterns
    print("\n🔍 QUERY 2: SPECIFIC SUMMARY FIELD PATTERNS")
    print("-" * 40)

    # Try different field name patterns
    field_patterns = [
        "CREDIT_SUMMARY",
        "CreditSummary",
        "credit_summary",
        "SUMMARY",
        "Summary",
        "summary"
    ]

    for pattern in field_patterns:
        try:
            pattern_query = """
            query($id:ID!){{
              entity(input:{{id:$id}}){{
                entity{{
                  records {{
                    CREDIT_RESPONSE {{
                      CREDIT_BUREAU
                      CreditReportFirstIssuedDate
                      {pattern} {{
                        # Try to get any fields
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """

            result = tilores_api.gql(pattern_query, {"id": entity_id})
            if result and 'data' in result and not result.get("errors"):
                print(f"   ✅ Pattern '{pattern}' works!")
                break
            else:
                print(f"   ❌ Pattern '{pattern}' failed")

        except Exception as e:
            print(f"   ❌ Pattern '{pattern}' error: {e}")

    # Query 3: Look for direct summary fields on CREDIT_RESPONSE
    print("\n🔍 QUERY 3: DIRECT SUMMARY FIELDS ON CREDIT_RESPONSE")
    print("-" * 40)

    direct_summary_query = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              Report_ID
              # Try common summary field names
              TotalAccounts
              TotalInquiries
              AverageScore
              TotalUtilization
              TotalLatePayments
              TotalDelinquentAccounts
              CreditLimitTotal
              CreditBalanceTotal
              # These might be direct fields
            }
          }
        }
      }
    }
    """

    try:
        result = tilores_api.gql(direct_summary_query, {"id": entity_id})
        if result and 'data' in result:
            if result.get("errors"):
                print("   ❌ Direct summary fields query failed with errors:")
                for error in result["errors"]:
                    print(f"     {error.get('message', 'Unknown error')}")
            else:
                print("   ✅ Direct summary fields query successful!")
                print("   🎯 Some summary fields may exist directly on CREDIT_RESPONSE")
        else:
            print("   ❌ Direct summary fields query failed")

    except Exception as e:
        print(f"   ❌ Direct summary fields query failed: {e}")

    print("\n🎯 ACTUAL FIELD DISCOVERY COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    discover_actual_fields()
