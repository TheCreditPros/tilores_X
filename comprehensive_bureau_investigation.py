#!/usr/bin/env python3
"""
Comprehensive Bureau Data Investigation
Thoroughly investigate all credit bureaus to find missing TransUnion and Experian data
"""

from dotenv import load_dotenv
load_dotenv()

def comprehensive_bureau_investigation():
    """Comprehensive investigation of all credit bureau data"""

    print("🔍 COMPREHENSIVE BUREAU DATA INVESTIGATION")
    print("=" * 60)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return

    # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"  # Example entity ID for reference

    # Test 1: Comprehensive credit response analysis
    print("\n🔍 TEST 1: COMPREHENSIVE CREDIT RESPONSE ANALYSIS")
    print("-" * 50)

    query1 = """
    query ComprehensiveCreditResponse {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              Report_ID
              Report_Type
              Vendor
            }}
          }}
        }}
      }}
    }}
    """

    try:
        result1 = tilores_api.gql(query1)
        if result1 and 'data' in result1:
            entity = result1['data']['entity']['entity']
            records = entity.get('records', [])

            print("📊 COMPREHENSIVE CREDIT RESPONSE ANALYSIS:")
            print(f"   Total records: {len(records)}")

            bureaus = {}
            report_details = []

            for i, record in enumerate(records):
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    bureau = credit_response.get('CREDIT_BUREAU')
                    report_date = credit_response.get('CreditReportFirstIssuedDate')
                    report_id = credit_response.get('Report_ID')
                    report_type = credit_response.get('Report_Type')
                    vendor = credit_response.get('Vendor')

                    if bureau:
                        if bureau not in bureaus:
                            bureaus[bureau] = 0
                        bureaus[bureau] += 1

                    report_details.append({
                        "record_index": i,
                        "bureau": bureau,
                        "report_date": report_date,
                        "report_id": report_id,
                        "report_type": report_type,
                        "vendor": vendor
                    })

            print("\n📋 CREDIT BUREAU SUMMARY:")
            for bureau, count in bureaus.items():
                print(f"   {bureau}: {count} reports")

            print("\n📋 DETAILED REPORT ANALYSIS:")
            for detail in report_details:
                print(f"   Record {detail['record_index']}:")
                print(f"     Bureau: {detail['bureau']}")
                print(f"     Date: {detail['report_date']}")
                print(f"     Report ID: {detail['report_id']}")
                print(f"     Type: {detail['report_type']}")
                print(f"     Vendor: {detail['vendor']}")
                print("     ---")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 1 failed: {e}")

    # Test 2: Check for different bureau field names
    print("\n🔍 TEST 2: ALTERNATIVE BUREAU FIELD NAMES")
    print("-" * 50)

    query2 = """
    query AlternativeBureauFields {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CreditBureau
              BUREAU
              Bureau
              Source
              CreditSource
              Repository
              CreditRepository
            }}
          }}
        }}
      }}
    }}
    """

    try:
        result2 = tilores_api.gql(query2)
        if result2 and 'data' in result2:
            entity = result2['data']['entity']['entity']
            records = entity.get('records', [])

            print("📊 ALTERNATIVE BUREAU FIELD ANALYSIS:")
            for i, record in enumerate(records):
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    print(f"   Record {i}:")
                    print(f"     CREDIT_BUREAU: {credit_response.get('CREDIT_BUREAU')}")
                    print(f"     CreditBureau: {credit_response.get('CreditBureau')}")
                    print(f"     BUREAU: {credit_response.get('BUREAU')}")
                    print(f"     Bureau: {credit_response.get('Bureau')}")
                    print(f"     Source: {credit_response.get('Source')}")
                    print(f"     CreditSource: {credit_response.get('CreditSource')}")
                    print(f"     Repository: {credit_response.get('Repository')}")
                    print(f"     CreditRepository: {credit_response.get('CreditRepository')}")
                    print("     ---")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 2 failed: {e}")

    # Test 3: Check nested bureau information in credit files and scores
    print("\n🔍 TEST 3: NESTED BUREAU INFORMATION")
    print("-" * 50)

    query3 = """
    query NestedBureauInfo {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CREDIT_FILE {{
                CreditRepositorySourceType
                CreditRepositorySource
                Repository
                Source
              }}
              CREDIT_SCORE {{
                CreditRepositorySourceType
                CreditRepositorySource
                Repository
                Source
              }}
            }}
          }}
        }}
      }}
    }}
    """

    try:
        result3 = tilores_api.gql(query3)
        if result3 and 'data' in result3:
            entity = result3['data']['entity']['entity']
            records = entity.get('records', [])

            print("📊 NESTED BUREAU INFORMATION ANALYSIS:")
            for i, record in enumerate(records):
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    print(f"   Record {i}:")
                    print(f"     CREDIT_BUREAU: {credit_response.get('CREDIT_BUREAU')}")

                    credit_files = credit_response.get('CREDIT_FILE', [])
                    for j, credit_file in enumerate(credit_files):
                        print(f"       CREDIT_FILE {j}:")
                        print(f"         CreditRepositorySourceType: {credit_file.get('CreditRepositorySourceType')}")
                        print(f"         CreditRepositorySource: {credit_file.get('CreditRepositorySource')}")
                        print(f"         Repository: {credit_file.get('Repository')}")
                        print(f"         Source: {credit_file.get('Source')}")

                    credit_scores = credit_response.get('CREDIT_SCORE', [])
                    for j, credit_score in enumerate(credit_scores):
                        print(f"       CREDIT_SCORE {j}:")
                        print(f"         CreditRepositorySourceType: {credit_score.get('CreditRepositorySourceType')}")
                        print(f"         CreditRepositorySource: {credit_score.get('CreditRepositorySource')}")
                        print(f"         Repository: {credit_score.get('Repository')}")
                        print(f"         Source: {credit_score.get('Source')}")

                    print("     ---")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 3 failed: {e}")

    # Test 4: Check for bureau information in different record types
    print("\n🔍 TEST 4: DIFFERENT RECORD TYPES")
    print("-" * 50)

    query4 = """
    query DifferentRecordTypes {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
            }}
            CREDIT_REPORT {{
              BUREAU
              CreditBureau
              Source
            }}
            CREDIT_FILE {{
              Repository
              Source
              CreditRepository
            }}
          }}
        }}
      }}
    }}
    """

    try:
        result4 = tilores_api.gql(query4)
        if result4 and 'data' in result4:
            entity = result4['data']['entity']['entity']
            records = entity.get('records', [])

            print("📊 DIFFERENT RECORD TYPES ANALYSIS:")
            for i, record in enumerate(records):
                print(f"   Record {i}:")

                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    print(f"     CREDIT_RESPONSE.CREDIT_BUREAU: {credit_response.get('CREDIT_BUREAU')}")

                credit_report = record.get('CREDIT_REPORT')
                if credit_report:
                    print(f"     CREDIT_REPORT.BUREAU: {credit_report.get('BUREAU')}")
                    print(f"     CREDIT_REPORT.CreditBureau: {credit_report.get('CreditBureau')}")
                    print(f"     CREDIT_REPORT.Source: {credit_report.get('Source')}")

                credit_file = record.get('CREDIT_FILE')
                if credit_file:
                    print(f"     CREDIT_FILE.Repository: {credit_file.get('Repository')}")
                    print(f"     CREDIT_FILE.Source: {credit_file.get('Source')}")
                    print(f"     CREDIT_FILE.CreditRepository: {credit_file.get('CreditRepository')}")

                print("     ---")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 4 failed: {e}")

    print("\n🎯 COMPREHENSIVE BUREAU INVESTIGATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    comprehensive_bureau_investigation()
