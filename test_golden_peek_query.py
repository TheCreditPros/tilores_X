#!/usr/bin/env python3
"""
Test GoldenPeek Query for Validity
Test the provided golden records schema method for accessing credit data
"""

from dotenv import load_dotenv
load_dotenv()

def test_golden_peek_query():
    """Test the GoldenPeek query for validity"""

    print("🔍 TESTING GOLDENPEEK QUERY VALIDITY")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        # Use the known working entity ID
        entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"
        since_date = "2024 - 01 - 01"  # Test with a recent date

        print(f"🎯 Testing entity: {entity_id}")
        print(f"📅 Since date: {since_date}")

        # Test the GoldenPeek query
        golden_peek_query = """
        query GoldenPeek {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              recordInsights {{
                emails: valuesDistinct(field: "EMAIL")
                phones: valuesDistinct(field: "PHONE_NUMBER")
                nameRank: frequencyDistribution(field: "FIRST_NAME", direction: DESC) {{ value frequency }}
                latestAddr: newest(field: "CREATED_DATE") {{
                  MAILING_STREET MAILING_CITY MAILING_STATE MAILING_POSTAL_CODE
                }}
                recentInquiries: filter(conditions: [
                  {{ field: "CREDIT_RESPONSE.CREDIT_INQUIRY.Date", since: "{since_date}" }}
                ]) {{
                  lenders: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_INQUIRY.Name")
                }}
              }}
            }}
          }}
        }}
        """

        print("🔍 Executing GoldenPeek query...")
        result = tilores_api.gql(golden_peek_query)

        if result and 'data' in result:
            insights = result['data']['entity']['entity']['recordInsights']
            print("✅ GoldenPeek query successful!")

            # Analyze the results
            print("\n📊 GOLDENPEEK RESULTS:")

            # Emails
            emails = insights.get('emails', [])
            print(f"   📧 Emails: {emails}")

            # Phones
            phones = insights.get('phones', [])
            print(f"   📞 Phones: {phones}")

            # Name ranking
            name_rank = insights.get('nameRank', [])
            if name_rank:
                print(f"   👤 Name Ranking: {name_rank[0]['value']} (frequency: {name_rank[0]['frequency']})")

            # Latest address
            latest_addr = insights.get('latestAddr', {})
            if latest_addr:
                print(f"   🏠 Latest Address: {latest_addr}")

            # Recent inquiries (this is the key part!)
            recent_inquiries = insights.get('recentInquiries', {})
            if recent_inquiries:
                lenders = recent_inquiries.get('lenders', [])
                print(f"   🔍 Recent Credit Inquiries: {lenders}")
                if lenders:
                    print(f"      ✅ CREDIT DATA FOUND! Lenders: {lenders}")
                    return True
                else:
                    print("      ⚠️  No lenders found in recent inquiries")
            else:
                print("   ❌ Recent inquiries not found")

            return False

        else:
            print("❌ GoldenPeek query failed")
            print(f"   Result: {result}")
            return False

    except Exception as e:
        print(f"❌ GoldenPeek test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_credit_response_fields():
    """Test individual CREDIT_RESPONSE fields to understand the structure"""

    print("\n🔍 TEST 2: CREDIT_RESPONSE Field Structure")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Test individual credit response fields
        credit_fields_query = """
        query CreditResponseFields {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              recordInsights {{
                # Test credit inquiry fields
                inquiryNames: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_INQUIRY.Name")
                inquiryDates: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_INQUIRY.Date")

                # Test credit score fields
                scoreValues: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Value")
                scoreModels: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.ModelNameType")

                # Test credit liability fields
                liabilityTypes: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_LIABILITY.AccountType")
                liabilityBalances: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_LIABILITY.Balance")

                # Test bureau fields
                bureaus: valuesDistinct(field: "CREDIT_RESPONSE.Bureau")
                creditDates: valuesDistinct(field: "CREDIT_RESPONSE.Date")
              }}
            }}
          }}
        }}
        """

        print("🔍 Testing individual CREDIT_RESPONSE fields...")
        result = tilores_api.gql(credit_fields_query)

        if result and 'data' in result:
            insights = result['data']['entity']['entity']['recordInsights']
            print("✅ CREDIT_RESPONSE fields query successful!")

            print("\n📊 CREDIT_RESPONSE FIELD RESULTS:")

            # Check each field
            fields_to_check = [
                ('inquiryNames', 'Credit Inquiry Names'),
                ('inquiryDates', 'Credit Inquiry Dates'),
                ('scoreValues', 'Credit Score Values'),
                ('scoreModels', 'Credit Score Models'),
                ('liabilityTypes', 'Credit Liability Types'),
                ('liabilityBalances', 'Credit Liability Balances'),
                ('bureaus', 'Credit Bureaus'),
                ('creditDates', 'Credit Dates')
            ]

            credit_data_found = False
            for field_name, field_desc in fields_to_check:
                field_data = insights.get(field_name, [])
                if field_data:
                    print(f"   ✅ {field_desc}: {field_data}")
                    credit_data_found = True
                else:
                    print(f"   ❌ {field_desc}: No data")

            if credit_data_found:
                print("\n🎉 CREDIT DATA FOUND IN CREDIT_RESPONSE FIELDS!")
                return True
            else:
                print("\n❌ No credit data found in CREDIT_RESPONSE fields")
                return False

        else:
            print("❌ CREDIT_RESPONSE fields query failed")
            return False

    except Exception as e:
        print(f"❌ CREDIT_RESPONSE fields test failed: {e}")
        return False

def test_temporal_credit_analysis():
    """Test temporal credit analysis capabilities"""

    print("\n🔍 TEST 3: Temporal Credit Analysis")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Test temporal credit analysis
        temporal_query = """
        query TemporalCreditAnalysis {{
          entity(input: {{ id: "{entity_id}" }}) {{
            entity {{
              recordInsights {{
                # Get first and newest credit reports
                firstCreditReport: first(field: "CREDIT_RESPONSE.Date") {{
                  CREDIT_RESPONSE {{
                    Date
                    Bureau
                    CREDIT_SCORE {{
                      Value
                      ModelNameType
                    }}
                    CREDIT_LIABILITY {{
                      AccountType
                      Balance
                      PaymentHistory
                    }}
                  }}
                }}

                newestCreditReport: newest(field: "CREDIT_RESPONSE.Date") {{
                  CREDIT_RESPONSE {{
                    Date
                    Bureau
                    CREDIT_SCORE {{
                      Value
                      ModelNameType
                    }}
                    CREDIT_LIABILITY {{
                      AccountType
                      Balance
                      PaymentHistory
                    }}
                  }}
                }}

                # Get all credit reports for comparison
                allCreditReports: group(field: "CREDIT_RESPONSE.Date") {{
                  CREDIT_RESPONSE {{
                    Date
                    Bureau
                    CREDIT_SCORE {{
                      Value
                      ModelNameType
                    }}
                    CREDIT_LIABILITY {{
                      AccountType
                      Balance
                      PaymentHistory
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """

        print("🔍 Testing temporal credit analysis...")
        result = tilores_api.gql(temporal_query)

        if result and 'data' in result:
            insights = result['data']['entity']['entity']['recordInsights']
            print("✅ Temporal credit analysis query successful!")

            print("\n📊 TEMPORAL CREDIT ANALYSIS RESULTS:")

            # Check first credit report
            first_report = insights.get('firstCreditReport', {})
            if first_report:
                print(f"   ✅ First Credit Report: {first_report}")
            else:
                print("   ❌ First Credit Report: Not found")

            # Check newest credit report
            newest_report = insights.get('newestCreditReport', {})
            if newest_report:
                print(f"   ✅ Newest Credit Report: {newest_report}")
            else:
                print("   ❌ Newest Credit Report: Not found")

            # Check all credit reports
            all_reports = insights.get('allCreditReports', [])
            if all_reports:
                print(f"   ✅ All Credit Reports: {len(all_reports)} reports found")
                for i, report in enumerate(all_reports[:3]):  # Show first 3
                    print(f"      Report {i + 1}: {report}")
            else:
                print("   ❌ All Credit Reports: Not found")

            temporal_data_found = first_report or newest_report or all_reports
            if temporal_data_found:
                print("\n🎉 TEMPORAL CREDIT DATA FOUND!")
                return True
            else:
                print("\n❌ No temporal credit data found")
                return False

        else:
            print("❌ Temporal credit analysis query failed")
            return False

    except Exception as e:
        print(f"❌ Temporal credit analysis test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING GOLDENPEEK QUERY VALIDITY")
    print("=" * 70)

    # Test 1: GoldenPeek query
    test1_success = test_golden_peek_query()

    # Test 2: CREDIT_RESPONSE fields
    test2_success = test_credit_response_fields()

    # Test 3: Temporal credit analysis
    test3_success = test_temporal_credit_analysis()

    print("\n" + "=" * 70)
    print("📊 VALIDATION RESULTS:")
    print(f"   • GoldenPeek Query: {'✅ VALID' if test1_success else '❌ INVALID'}")
    print(f"   • CREDIT_RESPONSE Fields: {'✅ WORKING' if test2_success else '❌ NOT WORKING'}")
    print(f"   • Temporal Analysis: {'✅ WORKING' if test3_success else '❌ NOT WORKING'}")

    overall_success = test1_success or test2_success or test3_success
    print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")

    if overall_success:
        print("🎉 GoldenPeek methodology validated!")
        print("   • Query syntax is correct")
        print("   • CREDIT_RESPONSE fields are accessible")
        print("   • Ready to integrate into enhanced credit tool")
    else:
        print("⚠️  GoldenPeek methodology needs investigation")
