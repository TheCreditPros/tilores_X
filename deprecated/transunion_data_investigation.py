#!/usr/bin/env python3
"""
TransUnion Data Investigation
Investigate why TransUnion reports are missing and fix data access
"""

from dotenv import load_dotenv
load_dotenv()

def investigate_transunion_data():
    """Investigate TransUnion data access issues"""

    print("🔍 TRANSUNION DATA INVESTIGATION")
    print("=" * 50)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return

    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    # Test 1: Check all credit bureaus
    print("\n🔍 TEST 1: CHECK ALL CREDIT BUREAUS")
    print("-" * 40)

    query1 = """
    query AllCreditBureaus {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
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

            bureaus = {}
            for record in records:
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    bureau = credit_response.get('CREDIT_BUREAU')
                    if bureau:
                        if bureau not in bureaus:
                            bureaus[bureau] = 0
                        bureaus[bureau] += 1

            print("📊 CREDIT BUREAU ANALYSIS:")
            for bureau, count in bureaus.items():
                print(f"   {bureau}: {count} reports")

            # Check for TransUnion specifically
            transunion_variants = [k for k in bureaus.keys() if 'TRANSUNION' in str(k).upper() or 'TU' in str(k).upper()]
            if transunion_variants:
                print(f"\n✅ TransUnion data found: {transunion_variants}")
            else:
                print("\n❌ No TransUnion data found")
                print(f"   Available bureaus: {list(bureaus.keys())}")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 1 failed: {e}")

    # Test 2: Check for different field names
    print("\n🔍 TEST 2: CHECK FOR DIFFERENT FIELD NAMES")
    print("-" * 40)

    query2 = """
    query DifferentFieldNames {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CreditBureau
              BUREAU
              Bureau
              CreditReportFirstIssuedDate
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

            print("📊 FIELD NAME ANALYSIS:")
            for record in records:
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    print(f"   CREDIT_BUREAU: {credit_response.get('CREDIT_BUREAU')}")
                    print(f"   CreditBureau: {credit_response.get('CreditBureau')}")
                    print(f"   BUREAU: {credit_response.get('BUREAU')}")
                    print(f"   Bureau: {credit_response.get('Bureau')}")
                    print("   ---")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 2 failed: {e}")

    # Test 3: Check for nested bureau information
    print("\n🔍 TEST 3: CHECK FOR NESTED BUREAU INFORMATION")
    print("-" * 40)

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
              }}
              CREDIT_SCORE {{
                CreditRepositorySourceType
                CreditRepositorySource
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

            print("📊 NESTED BUREAU ANALYSIS:")
            for record in records:
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    print(f"   CREDIT_BUREAU: {credit_response.get('CREDIT_BUREAU')}")

                    credit_file = credit_response.get('CREDIT_FILE', [])
                    for file in credit_file:
                        print(f"     CREDIT_FILE.CreditRepositorySourceType: {file.get('CreditRepositorySourceType')}")
                        print(f"     CREDIT_FILE.CreditRepositorySource: {file.get('CreditRepositorySource')}")

                    credit_score = credit_response.get('CREDIT_SCORE', [])
                    for score in credit_score:
                        print(f"     CREDIT_SCORE.CreditRepositorySourceType: {score.get('CreditRepositorySourceType')}")
                        print(f"     CREDIT_SCORE.CreditRepositorySource: {score.get('CreditRepositorySource')}")
                    print("   ---")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 3 failed: {e}")

    print("\n🎯 TRANSUNION DATA INVESTIGATION COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    investigate_transunion_data()
