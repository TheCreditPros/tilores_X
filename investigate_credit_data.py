#!/usr/bin/env python3
"""
Direct investigation of credit data availability for test record
"""

from dotenv import load_dotenv
load_dotenv()

def investigate_credit_data():
    """Investigate what credit data is actually available for the test record"""

    print("🔍 INVESTIGATING CREDIT DATA FOR TEST RECORD")
    print("=" * 60)

    try:
        from tilores import TiloresAPI

        # Initialize Tilores API
        tilores_api = TiloresAPI.from_environ()

        # Search for the test record
        search_query = """
        query SearchCustomer {
          search(
            query: "e.j.price1986@gmail.com"
            limit: 10
          ) {
            entities {
              id
              entity {
                id
                records {
                  id
                  source
                  # Check for credit-related fields
                  CREDIT_RESPONSE {
                    CREDIT_SCORE {
                      Value
                      Date
                    }
                    BUREAU
                    REPORT_DATE
                  }
                  TRANSUNION_REPORT {
                    CREDIT_SCORE
                    REPORT_DATE
                    BUREAU
                  }
                  EXPERIAN_REPORT {
                    CREDIT_SCORE
                    REPORT_DATE
                    BUREAU
                  }
                  EQUIFAX_REPORT {
                    CREDIT_SCORE
                    REPORT_DATE
                    BUREAU
                  }
                  # Also check for any credit-related fields
                  CREDIT_SCORE
                  BUREAU
                  REPORT_DATE
                  CREDIT_LIMIT
                  CREDIT_BALANCE
                  PAYMENT_HISTORY
                  LATE_PAYMENTS
                  UTILIZATION
                }
              }
            }
          }
        }
        """

        print("🔍 Searching for test record...")
        search_result = tilores_api.gql(search_query)

        if "data" in search_result and search_result["data"]["search"]["entities"]:
            entities = search_result["data"]["search"]["entities"]
            print(f"✅ Found {len(entities)} entities")

            for i, entity in enumerate(entities):
                print(f"\n📊 ENTITY {i + 1}:")
                print(f"   ID: {entity['id']}")

                records = entity["entity"]["records"]
                print(f"   Records: {len(records)}")

                # Check each record for credit data
                for j, record in enumerate(records):
                    print(f"\n   📄 RECORD {j + 1}:")
                    print(f"      Source: {record.get('source', 'Unknown')}")

                    # Check for credit response data
                    if "CREDIT_RESPONSE" in record:
                        credit_data = record["CREDIT_RESPONSE"]
                        print("      ✅ CREDIT_RESPONSE found!")
                        if isinstance(credit_data, list):
                            for k, credit in enumerate(credit_data):
                                print(f"         Credit {k + 1}: {credit}")
                        else:
                            print(f"         Credit: {credit_data}")

                    # Check for bureau-specific reports
                    for bureau in ["TRANSUNION_REPORT", "EXPERIAN_REPORT", "EQUIFAX_REPORT"]:
                        if bureau in record:
                            bureau_data = record[bureau]
                            print(f"      ✅ {bureau} found!")
                            if isinstance(bureau_data, list):
                                for k, report in enumerate(bureau_data):
                                    print(f"         Report {k + 1}: {report}")
                            else:
                                print(f"         Report: {bureau_data}")

                    # Check for individual credit fields
                    credit_fields = ["CREDIT_SCORE", "BUREAU", "REPORT_DATE", "CREDIT_LIMIT", "CREDIT_BALANCE"]
                    for field in credit_fields:
                        if field in record and record[field] is not None:
                            print(f"      ✅ {field}: {record[field]}")

                # Store entity ID for further investigation
                entity_id = entity["entity"]["id"]
                print(f"\n🔍 Entity ID for further investigation: {entity_id}")

                # Now let's check Record Insights for this entity
                print(f"\n🔍 Checking Record Insights for entity {entity_id}...")

                record_insights_query = """
                query RecordInsights {{
                  entity(input: {{ id: "{entity_id}" }}) {{
                    entity {{
                      id
                      recordInsights {{
                        # Credit-specific insights
                        creditScores: valuesDistinct(field: "CREDIT_SCORE")
                        bureaus: valuesDistinct(field: "BUREAU")
                        reportDates: valuesDistinct(field: "REPORT_DATE")
                        creditLimits: valuesDistinct(field: "CREDIT_LIMIT")
                        creditBalances: valuesDistinct(field: "CREDIT_BALANCE")
                        paymentHistories: valuesDistinct(field: "PAYMENT_HISTORY")
                        latePayments: valuesDistinct(field: "LATE_PAYMENTS")
                        utilizations: valuesDistinct(field: "UTILIZATION")

                        # Also check for nested credit response data
                        creditResponseScores: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Value")
                        creditResponseBureaus: valuesDistinct(field: "CREDIT_RESPONSE.BUREAU")
                        creditResponseDates: valuesDistinct(field: "CREDIT_RESPONSE.REPORT_DATE")

                        # Check for any fields containing "credit" or "score"
                        allFields: valuesDistinct(field: "*")
                      }}
                    }}
                  }}
                }}
                """

                insights_result = tilores_api.gql(record_insights_query)

                if "data" in insights_result:
                    insights = insights_result["data"]["entity"]["entity"]["recordInsights"]
                    print("✅ Record Insights successful!")
                    print(f"📊 Available insights keys: {list(insights.keys())}")

                    # Show credit-related insights
                    for key, value in insights.items():
                        if any(term in key.lower() for term in ["credit", "score", "bureau", "payment", "utilization"]):
                            print(f"   {key}: {value}")
                else:
                    print(f"❌ Record Insights failed: {insights_result}")

                break  # Just check the first entity for now

            return search_result

        else:
            print(f"❌ No entities found: {search_result}")
            return None

    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    investigate_credit_data()
