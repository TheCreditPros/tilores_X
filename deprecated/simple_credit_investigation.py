#!/usr/bin/env python3
"""
Simple Credit Investigation - Find where credit data is stored
Since GoldenPeek didn't work, let's find the real credit data structure
"""

from dotenv import load_dotenv
load_dotenv()

def investigate_records_array():
    """Investigate the records array structure for credit data"""

    print("🔍 INVESTIGATING RECORDS ARRAY FOR CREDIT DATA")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Test records array with credit-related fields
        records_query = """
        query RecordsArrayCredit {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              records {{
                # Fields we know work from previous tests
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
                TRANSACTION_AMOUNT
                AMOUNT
                CARD_TYPE
                PAYMENT_METHOD

                # Test credit-related fields systematically
                CREDIT_SCORE
                CREDIT_BUREAU
                CREDIT_DATE
                CREDIT_REPORT
                CREDIT_INQUIRY
                CREDIT_LIABILITY

                # Alternative field names
                SCORE
                BUREAU
                REPORT_DATE
                INQUIRY_DATE
                ACCOUNT_TYPE
                ACCOUNT_BALANCE

                # Bureau-specific fields
                EXPERIAN
                TRANSUNION
                EQUIFAX

                # Payment and account fields
                PAYMENT_HISTORY
                LATE_PAYMENTS
                ACCOUNT_STATUS
                CREDIT_LIMIT
                UTILIZATION
              }}
            }}
          }}
        }}
        """

        print("🔍 Testing records array for credit data...")
        result = tilores_api.gql(records_query)

        if result and 'data' in result:
            records = result['data']['entity']['entity']['records']
            print("✅ Records array query successful!")
            print(f"   Number of records: {len(records) if records else 0}")

            if records:
                print("\n📊 RECORDS ARRAY ANALYSIS:")

                # Analyze first few records for structure
                for i, record in enumerate(records[:3]):
                    print(f"\n   Record {i + 1}:")
                    if record:
                        # Show all available fields
                        for field, value in record.items():
                            if value is not None:
                                print(f"      {field}: {value}")
                    else:
                        print("      (Empty record)")

                # Look for credit-related data
                credit_fields_found = []
                for record in records:
                    if record:
                        for field in record.keys():
                            if any(credit_term in field.upper() for credit_term in ['CREDIT', 'SCORE', 'BUREAU', 'INQUIRY', 'PAYMENT']):
                                if field not in credit_fields_found:
                                    credit_fields_found.append(field)

                if credit_fields_found:
                    print("\n🎉 CREDIT-RELATED FIELDS FOUND IN RECORDS ARRAY!")
                    print(f"   Fields: {credit_fields_found}")
                    return True
                else:
                    print("\n❌ No credit-related fields found in records array")
                    return False
            else:
                print("   No records found")
                return False

        else:
            print("❌ Records array query failed")
            return False

    except Exception as e:
        print(f"❌ Records array investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def investigate_working_approach():
    """Test the working records array approach we discovered earlier"""

    print("\n🔍 TESTING WORKING RECORDS ARRAY APPROACH")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Use the working approach from our previous tests
        working_query = """
        query WorkingRecordsArray {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              records {{
                # Fields we know work from previous tests
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
                TRANSACTION_AMOUNT
                AMOUNT
                CARD_TYPE
                PAYMENT_METHOD

                # Now let's add credit-related fields to see what's available
                # Test various patterns systematically
                CREDIT_SCORE
                CREDIT_BUREAU
                CREDIT_DATE
                CREDIT_REPORT
                CREDIT_INQUIRY
                CREDIT_LIABILITY

                # Alternative field names
                SCORE
                BUREAU
                REPORT_DATE
                INQUIRY_DATE
                ACCOUNT_TYPE
                ACCOUNT_BALANCE

                # Bureau-specific fields
                EXPERIAN
                TRANSUNION
                EQUIFAX

                # Payment and account fields
                PAYMENT_HISTORY
                LATE_PAYMENTS
                ACCOUNT_STATUS
                CREDIT_LIMIT
                UTILIZATION
              }}
            }}
          }}
        }}
        """

        print("🔍 Testing working records array approach...")
        result = tilores_api.gql(working_query)

        if result and 'data' in result:
            records = result['data']['entity']['entity']['records']
            print("✅ Working records array query successful!")
            print(f"   Number of records: {len(records) if records else 0}")

            if records:
                print("\n📊 WORKING RECORDS ARRAY RESULTS:")

                # Analyze first record for available fields
                first_record = records[0] if records else {}
                if first_record:
                    print(f"   First record fields: {list(first_record.keys())}")

                    # Check for credit-related fields
                    credit_fields = []
                    for field, value in first_record.items():
                        if value is not None and any(credit_term in field.upper() for credit_term in ['CREDIT', 'SCORE', 'BUREAU', 'INQUIRY', 'PAYMENT']):
                            credit_fields.append((field, value))

                    if credit_fields:
                        print("\n🎉 CREDIT DATA FOUND IN WORKING APPROACH!")
                        for field, value in credit_fields:
                            print(f"   {field}: {value}")
                        return True
                    else:
                        print("\n❌ No credit data found in working approach")
                        return False
                else:
                    print("   First record is empty")
                    return False
            else:
                print("   No records found")
                return False

        else:
            print("❌ Working records array query failed")
            return False

    except Exception as e:
        print(f"❌ Working approach investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 SIMPLE CREDIT SCHEMA INVESTIGATION")
    print("=" * 70)

    # Run investigations
    test1_success = investigate_records_array()
    test2_success = investigate_working_approach()

    print("\n" + "=" * 70)
    print("📊 INVESTIGATION RESULTS:")
    print(f"   • Records Array: {'✅ SUCCESS' if test1_success else '❌ FAILED'}")
    print(f"   • Working Approach: {'✅ SUCCESS' if test2_success else '❌ FAILED'}")

    overall_success = test1_success or test2_success
    print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")

    if overall_success:
        print("🎉 Credit data investigation successful!")
        print("   • Credit data location identified")
        print("   • Ready to implement enhanced credit tool")
    else:
        print("⚠️  Credit data investigation needs more work")
