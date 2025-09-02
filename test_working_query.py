#!/usr/bin/env python3
"""
Test the exact working query we validated earlier
"""

import json
from dotenv import load_dotenv
load_dotenv()

def test_exact_working_query():
    """Test the exact query that worked in our debug"""

    print("🧪 TESTING EXACT WORKING QUERY")
    print("=" * 60)

    try:
        from core_app import initialize_engine
        import core_app

        initialize_engine()
        engine = core_app.engine

        entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # This is the EXACT query that worked in debug_available_fields.py
        working_query = """
        query WorkingRecordInsights {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              id
              recordInsights {{
                # ✅ Customer Profile (confirmed working)
                allEmails: valuesDistinct(field: "EMAIL")
                allNames: valuesDistinct(field: "FIRST_NAME")
                lastNames: valuesDistinct(field: "LAST_NAME")
                clientIds: valuesDistinct(field: "CLIENT_ID")

                # ✅ Contact Information
                phoneNumbers: valuesDistinct(field: "PHONE_EXTERNAL")

                # ✅ Account Information
                enrollmentDates: valuesDistinct(field: "ENROLL_DATE")
                customerStatus: frequencyDistribution(field: "STATUS") {{
                  value
                  frequency
                }}

                # ✅ Product Information
                products: valuesDistinct(field: "PRODUCT_NAME")

                # ✅ Transaction Information
                transactionAmounts: valuesDistinct(field: "TRANSACTION_AMOUNT")
                amounts: valuesDistinct(field: "AMOUNT")
                cardTypes: valuesDistinct(field: "CARD_TYPE")
                paymentMethods: frequencyDistribution(field: "PAYMENT_METHOD") {{
                  value
                  frequency
                }}

                # ✅ Demographics
                customerAges: valuesDistinct(field: "CUSTOMER_AGE")
                birthDates: valuesDistinct(field: "DATE_OF_BIRTH")
              }}
            }}
          }}
        }}
        """

        print("🔍 Executing exact working query...")

        result = engine.tilores.gql(working_query)

        if "data" in result:
            insights = result["data"]["entity"]["entity"]["recordInsights"]

            print("✅ EXACT WORKING QUERY SUCCESSFUL!")
            print(f"📊 Insights keys: {list(insights.keys())}")

            # Show key data
            emails = insights.get("allEmails", [])
            names = insights.get("allNames", [])
            client_ids = insights.get("clientIds", [])

            print(f"   👤 Customer: {names[0] if names else 'Unknown'}")
            print(f"   📧 Email: {emails[0] if emails else 'Unknown'}")
            print(f"   🆔 Client ID: {client_ids[0] if client_ids else 'Unknown'}")

            return result
        else:
            print(f"❌ Query failed: {result}")
            return None

    except Exception as e:
        print(f"❌ Working query failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_with_enhanced_query():
    """Compare working query with our enhanced query to find the difference"""

    print("\n🔍 COMPARING QUERIES TO FIND DIFFERENCE")
    print("=" * 60)

    try:
        from enhanced_record_insights_queries import RecordInsightsQueryBuilder

        entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Get our enhanced query
        query_builder = RecordInsightsQueryBuilder()
        enhanced_query = query_builder.build_comprehensive_credit_query(entity_id)

        print("🔍 Enhanced query structure:")
        print(enhanced_query[:500] + "...")

        # Look for differences
        print("\n🔍 Key differences to investigate:")
        print("   • Enhanced query uses 'primaryName: frequencyDistribution(field: \"FIRST_NAME\", direction: DESC, limit: 1)'")
        print("   • Working query uses 'allNames: valuesDistinct(field: \"FIRST_NAME\")'")
        print("   • Enhanced query may have syntax issues with limit parameter")

        return enhanced_query

    except Exception as e:
        print(f"❌ Query comparison failed: {e}")
        return None

def test_fixed_enhanced_query():
    """Test enhanced query with fixes based on working query"""

    print("\n🧪 TESTING FIXED ENHANCED QUERY")
    print("=" * 60)

    try:
        from core_app import initialize_engine
        import core_app

        initialize_engine()
        engine = core_app.engine

        entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Fixed enhanced query using working patterns
        fixed_query = """
        query FixedCustomerAnalysis {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              id
              recordInsights {{
                # ✅ Customer Profile (using working patterns)
                allEmails: valuesDistinct(field: "EMAIL")
                allNames: valuesDistinct(field: "FIRST_NAME")
                lastNames: valuesDistinct(field: "LAST_NAME")
                clientIds: valuesDistinct(field: "CLIENT_ID")

                # ✅ Contact Information
                phoneNumbers: valuesDistinct(field: "PHONE_EXTERNAL")

                # ✅ Account Information - With dates preserved
                enrollmentDates: valuesDistinct(field: "ENROLL_DATE")
                customerStatus: frequencyDistribution(field: "STATUS", direction: DESC) {{
                  value
                  frequency
                }}

                # ✅ Product Analysis
                products: valuesDistinct(field: "PRODUCT_NAME")

                # ✅ Financial Analysis - Using available transaction data
                transactionAmounts: valuesDistinct(field: "TRANSACTION_AMOUNT")
                amounts: valuesDistinct(field: "AMOUNT")

                # ✅ Payment Analysis - Credit-adjacent data
                paymentMethods: frequencyDistribution(field: "PAYMENT_METHOD", direction: DESC) {{
                  value
                  frequency
                }}
                cardTypes: valuesDistinct(field: "CARD_TYPE")

                # ✅ Demographics
                customerAges: valuesDistinct(field: "CUSTOMER_AGE")
                birthDates: valuesDistinct(field: "DATE_OF_BIRTH")
              }}
            }}
          }}
        }}
        """

        print("🔍 Executing fixed enhanced query...")

        result = engine.tilores.gql(fixed_query)

        if "data" in result:
            insights = result["data"]["entity"]["entity"]["recordInsights"]

            print("✅ FIXED ENHANCED QUERY SUCCESSFUL!")
            print(f"📊 Insights keys: {list(insights.keys())}")

            # Parse using our enhanced parser
            from enhanced_record_insights_queries import RecordInsightsResponseParser

            # Adapt the result to match our parser expectations
            adapted_result = {
                "data": {
                    "entity": {
                        "entity": {
                            "recordInsights": {
                                "primaryName": [{"value": insights.get("allNames", ["Unknown"])[0], "frequency": 1}] if insights.get("allNames") else [],
                                "allEmails": insights.get("allEmails", []),
                                "clientIds": insights.get("clientIds", []),
                                "lastNames": insights.get("lastNames", []),
                                "phoneNumbers": insights.get("phoneNumbers", []),
                                "enrollmentDates": insights.get("enrollmentDates", []),
                                "customerStatus": insights.get("customerStatus", []),
                                "products": insights.get("products", []),
                                "productFrequency": [{"value": p, "frequency": 1} for p in insights.get("products", [])],
                                "transactionAmounts": insights.get("transactionAmounts", []),
                                "amounts": insights.get("amounts", []),
                                "paymentMethods": insights.get("paymentMethods", []),
                                "cardTypes": insights.get("cardTypes", []),
                                "customerAges": insights.get("customerAges", []),
                                "birthDates": insights.get("birthDates", [])
                            }
                        }
                    }
                }
            }

            parser = RecordInsightsResponseParser()
            parsed_data = parser.parse_comprehensive_credit_response(adapted_result)
            formatted_report = parser.format_credit_report_with_dates(parsed_data)

            print("\n📊 FORMATTED CUSTOMER ANALYSIS:")
            print("-" * 50)
            print(formatted_report)
            print("-" * 50)

            return True
        else:
            print(f"❌ Fixed query failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Fixed query test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 TESTING WORKING QUERY PATTERNS")
    print("=" * 60)

    # Test exact working query
    working_result = test_exact_working_query()

    # Compare with enhanced query
    enhanced_query = compare_with_enhanced_query()

    # Test fixed enhanced query
    fixed_success = test_fixed_enhanced_query()

    print("\n" + "=" * 60)
    print("📊 QUERY TESTING RESULTS:")
    print(f"   • Exact working query: {'✅ SUCCESS' if working_result else '❌ FAIL'}")
    print(f"   • Enhanced query comparison: {'✅ SUCCESS' if enhanced_query else '❌ FAIL'}")
    print(f"   • Fixed enhanced query: {'✅ SUCCESS' if fixed_success else '❌ FAIL'}")

    if fixed_success:
        print("\n🎯 SOLUTION FOUND!")
        print("   • Working Record Insights query identified")
        print("   • Enhanced customer analysis format working")
        print("   • Ready to update enhanced credit tool")

