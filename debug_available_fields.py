#!/usr/bin/env python3
"""
Debug what fields are actually available for this customer
Create working Record Insights queries with real data
"""

from dotenv import load_dotenv
load_dotenv()

def check_available_fields():
    """Check what fields are actually available for our test customer"""

    print("🔍 CHECKING AVAILABLE FIELDS FOR CUSTOMER")
    print("=" * 60)

    try:
        from core_app import initialize_engine
        import core_app

        initialize_engine()
        engine = core_app.engine

        # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Get full record structure
        full_record_query = """
        query FullRecordStructure {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              id
              records {{
                id
                EMAIL
                FIRST_NAME
                LAST_NAME
                CLIENT_ID
                PHONE_EXTERNAL
                CUSTOMER_AGE
                DATE_OF_BIRTH
                ENROLL_DATE
                STATUS
                PRODUCT_NAME
                AMOUNT
                TRANSACTION_AMOUNT
                CARD_TYPE
                PAYMENT_METHOD
              }}
            }}
          }}
        }}
        """

        result = engine.tilores.gql(full_record_query)
        records = result.get('data', {}).get('entity', {}).get('entity', {}).get('records', [])

        print(f"📊 Found {len(records)} records for customer")

        if records:
            # Analyze first record
            first_record = records[0]
            print("\n📋 FIRST RECORD ANALYSIS:")

            for key, value in first_record.items():
                if value is not None:
                    print(f"   • {key}: {value}")

            # Check all records for any credit-related data
            print(f"\n🔍 SCANNING ALL {len(records)} RECORDS FOR CREDIT DATA:")

            all_fields = set()
            for record in records:
                all_fields.update(record.keys())

            credit_related = [f for f in all_fields if any(term in f.upper() for term in ['CREDIT', 'SCORE', 'BUREAU', 'EXPERIAN', 'TRANSUNION', 'EQUIFAX'])]

            if credit_related:
                print(f"   ✅ Credit fields found: {credit_related}")
            else:
                print("   ❌ NO credit fields found in any record")
                print(f"   📋 Available fields: {sorted(list(all_fields))}")

        return records

    except Exception as e:
        print(f"❌ Field check failed: {e}")
        return []

def create_working_record_insights_query():
    """Create Record Insights query with fields that actually exist"""

    print("\n🔧 CREATING WORKING RECORD INSIGHTS QUERY")
    print("=" * 60)

    try:
        from core_app import initialize_engine
        import core_app

        initialize_engine()
        engine = core_app.engine

        # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Create query with fields we know exist
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
                paymentMethods: valuesDistinct(field: "PAYMENT_METHOD")

                # ✅ Demographics
                customerAges: valuesDistinct(field: "CUSTOMER_AGE")
                birthDates: valuesDistinct(field: "DATE_OF_BIRTH")
              }}
            }}
          }}
        }}
        """

        print("🔍 Executing working Record Insights query...")

        result = engine.tilores.gql(working_query)

        if "data" in result:
            insights = result["data"]["entity"]["entity"]["recordInsights"]

            print("✅ WORKING RECORD INSIGHTS SUCCESSFUL!")
            print("\n📊 CUSTOMER DATA SUMMARY:")

            # Customer Profile
            emails = insights.get("allEmails", [])
            names = insights.get("allNames", [])
            client_ids = insights.get("clientIds", [])

            print(f"   👤 Customer: {names[0] if names else 'Unknown'}")
            print(f"   📧 Email: {emails[0] if emails else 'Unknown'}")
            print(f"   🆔 Client ID: {client_ids[0] if client_ids else 'Unknown'}")

            # Account Information
            status = insights.get("customerStatus", [])
            products = insights.get("products", [])
            enroll_dates = insights.get("enrollmentDates", [])

            if status:
                print(f"   📊 Status: {status[0]['value']} (frequency: {status[0]['frequency']})")
            if products:
                print(f"   🎯 Products: {products}")
            if enroll_dates:
                print(f"   📅 Enrollment: {enroll_dates[0] if enroll_dates else 'Unknown'}")

            # Transaction Information
            amounts = insights.get("amounts", [])
            transaction_amounts = insights.get("transactionAmounts", [])
            payment_methods = insights.get("paymentMethods", [])

            if amounts:
                print(f"   💰 Amounts: {amounts[:3]}...")
            if transaction_amounts:
                print(f"   💳 Transactions: {transaction_amounts[:3]}...")
            if payment_methods:
                print(f"   💳 Payment Methods: {payment_methods}")

            return True
        else:
            print(f"❌ Query failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Working query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_customer_with_credit_data():
    """Try to find a customer that actually has credit data"""

    print("\n🔍 SEARCHING FOR CUSTOMER WITH CREDIT DATA")
    print("=" * 60)

    try:
        from core_app import initialize_engine
        import core_app

        initialize_engine()
        engine = core_app.engine

        # Search for customers with credit-related fields
        credit_search_query = """
        query FindCreditCustomers {
          search(input: {
            parameters: {}
            limit: 10
          }) {
            entities {
              id
              records {
                id
                EMAIL
                FIRST_NAME
                CLIENT_ID
              }
            }
          }
        }
        """

        print("🔍 Searching for customers with potential credit data...")

        result = engine.tilores.gql(credit_search_query)
        entities = result.get("data", {}).get("search", {}).get("entities", [])

        print(f"📊 Found {len(entities)} entities to check")

        for i, entity in enumerate(entities[:3]):  # Check first 3
            entity_id = entity["id"]
            records = entity.get("records", [])

            if records and records[0].get("EMAIL"):
                email = records[0]["EMAIL"]
                name = records[0].get("FIRST_NAME", "Unknown")
                client_id = records[0].get("CLIENT_ID", "Unknown")

                print(f"\n🧪 Testing entity {i + 1}: {name} ({email})")
                print(f"   Entity ID: {entity_id}")
                print(f"   Client ID: {client_id}")

                # Test for credit data
                credit_test_query = """
                query TestCreditData {{
                  entity(input: {{ id: "{entity_id}" }}) {{
                    entity {{
                      recordInsights {{
                        creditScores: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Value")
                      }}
                    }}
                  }}
                }}
                """

                try:
                    credit_result = engine.tilores.gql(credit_test_query)
                    scores = credit_result.get("data", {}).get("entity", {}).get("entity", {}).get("recordInsights", {}).get("creditScores", [])

                    if scores:
                        print(f"   ✅ HAS CREDIT DATA! Scores: {scores}")
                        return entity_id, email, name
                    else:
                        print("   ❌ No credit data")

                except Exception as e:
                    print(f"   ❌ Credit test failed: {e}")

        print("\n⚠️  NO CUSTOMERS WITH CREDIT DATA FOUND")
        print("   This suggests the Tilores instance may not have credit bureau data")

        return None, None, None

    except Exception as e:
        print(f"❌ Credit customer search failed: {e}")
        return None, None, None

if __name__ == "__main__":
    print("🚀 STARTING FIELD AVAILABILITY ANALYSIS")
    print("=" * 60)

    # Check what fields exist for our test customer
    records = check_available_fields()

    # Create working Record Insights query
    working_query_success = create_working_record_insights_query()

    # Try to find customer with actual credit data
    credit_entity_id, credit_email, credit_name = test_customer_with_credit_data()

    print("\n" + "=" * 60)
    print("📊 FIELD ANALYSIS RESULTS:")
    print(f"   • Records found: {len(records) if records else 0}")
    print(f"   • Working Record Insights: {'✅ SUCCESS' if working_query_success else '❌ FAIL'}")
    print(f"   • Customer with credit data: {'✅ FOUND' if credit_entity_id else '❌ NOT FOUND'}")

    if credit_entity_id:
        print("\n🎯 RECOMMENDED TEST CUSTOMER:")
        print(f"   • Name: {credit_name}")
        print(f"   • Email: {credit_email}")
        print(f"   • Entity ID: {credit_entity_id}")
    else:
        print("\n💡 RECOMMENDATION:")
        print("   • Use working Record Insights with available data")
        print("   • Focus on customer profile, transactions, products")
        print("   • Credit data may not be available in this Tilores instance")

