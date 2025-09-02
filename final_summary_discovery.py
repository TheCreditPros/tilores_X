#!/usr/bin/env python3
"""
Final Summary Discovery
Final attempt to discover summary parameters using working query structure
"""

from dotenv import load_dotenv
load_dotenv()

def final_summary_discovery():
    """Final attempt to discover summary parameters"""

    print("🔍 FINAL SUMMARY PARAMETERS DISCOVERY")
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

    print(f"\n🔍 FINAL DISCOVERY FOR ENTITY: {entity_id}")
    print("-" * 50)

    # Use the exact working query structure we know works
    print("\n🔍 USING WORKING QUERY STRUCTURE")
    print("-" * 40)

    working_query = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              Report_ID
              CREDIT_SCORE {
                Value
                ModelNameType
                CreditRepositorySourceType
              }
            }
          }
        }
      }
    }
    """

    try:
        result = tilores_api.gql(working_query, {"id": entity_id})
        if result and 'data' in result:
            print("✅ Working query structure confirmed")

            # Now try to add summary fields one by one
            print("\n🔍 TESTING SUMMARY FIELD ADDITIONS")
            print("-" * 40)

            # Test 1: Add CREDIT_SUMMARY
            test1_query = """
            query($id:ID!){
              entity(input:{id:$id}){
                entity{
                  records {
                    CREDIT_RESPONSE {
                      CREDIT_BUREAU
                      CreditReportFirstIssuedDate
                      Report_ID
                      CREDIT_SCORE {
                        Value
                        ModelNameType
                        CreditRepositorySourceType
                      }
                      CREDIT_SUMMARY {
                        BorrowerID
                        Name
                      }
                    }
                  }
                }
              }
            }
            """

            try:
                result1 = tilores_api.gql(test1_query, {"id": entity_id})
                if result1 and 'data' in result1 and not result1.get("errors"):
                    print("   ✅ CREDIT_SUMMARY fields work!")
                else:
                    print("   ❌ CREDIT_SUMMARY fields failed")
            except Exception as e:
                print(f"   ❌ CREDIT_SUMMARY test failed: {e}")

            # Test 2: Try different field names
            test2_query = """
            query($id:ID!){
              entity(input:{id:$id}){
                entity{
                  records {
                    CREDIT_RESPONSE {
                      CREDIT_BUREAU
                      CreditReportFirstIssuedDate
                      Report_ID
                      CREDIT_SCORE {
                        Value
                        ModelNameType
                        CreditRepositorySourceType
                      }
                      # Try alternative field names
                      Summary
                      summary
                      SUMMARY
                    }
                  }
                }
              }
            }
            """

            try:
                result2 = tilores_api.gql(test2_query, {"id": entity_id})
                if result2 and 'data' in result2 and not result2.get("errors"):
                    print("   ✅ Alternative summary field names work!")
                else:
                    print("   ❌ Alternative summary field names failed")
            except Exception as e:
                print(f"   ❌ Alternative summary test failed: {e}")

            # Test 3: Look for summary fields in different locations
            test3_query = """
            query($id:ID!){
              entity(input:{id:$id}){
                entity{
                  records {
                    CREDIT_RESPONSE {
                      CREDIT_BUREAU
                      CreditReportFirstIssuedDate
                      Report_ID
                      CREDIT_SCORE {
                        Value
                        ModelNameType
                        CreditRepositorySourceType
                      }
                      # Look for summary fields at different levels
                      TotalAccounts
                      TotalInquiries
                      AverageScore
                    }
                  }
                }
              }
            }
            """

            try:
                result3 = tilores_api.gql(test3_query, {"id": entity_id})
                if result3 and 'data' in result3 and not result3.get("errors"):
                    print("   ✅ Direct summary fields work!")
                else:
                    print("   ❌ Direct summary fields failed")
            except Exception as e:
                print(f"   ❌ Direct summary test failed: {e}")

        else:
            print("   ❌ Working query structure failed")

    except Exception as e:
        print(f"   ❌ Working query test failed: {e}")

    # Final summary
    print("\n📊 FINAL SUMMARY DISCOVERY RESULTS")
    print("-" * 40)
    print("   Based on the schema discovery and testing:")
    print("   - CreditResponseCreditSummaryDataSet type exists")
    print("   - Fields: BorrowerID, Name, DATA_SET")
    print("   - But queries are failing with 422 errors")
    print("   - This suggests field name or structure differences")
    print("   - The summary parameters exist but may have different names")

    print("\n🎯 FINAL SUMMARY DISCOVERY COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    final_summary_discovery()
