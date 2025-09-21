#!/usr/bin/env python3
"""
Working Query Bureau Investigation
Use the working query structure from Phase 3 to find missing bureau data
"""

from dotenv import load_dotenv
load_dotenv()

def working_query_bureau_investigation():
    """Use working query structure to investigate bureau data"""

    print("🔍 WORKING QUERY BUREAU INVESTIGATION")
    print("=" * 50)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return

    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    # Use the working query structure from Phase 3
    print("\n🔍 USING WORKING QUERY STRUCTURE FROM PHASE 3")
    print("-" * 50)

    working_query = """
    query WorkingBureauInvestigation {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              CREDIT_SCORE {{
                Value
                ModelNameType
              }}
              CREDIT_LIABILITY {{
                AccountType
                CreditLimitAmount
                CreditBalance
              }}
            }}
            PHONE_EXTERNAL
            CREATED_DATE
            PRODUCT_NAME
            TRANSACTION_AMOUNT
            CARD_TYPE
            STATUS
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(working_query)
        if result and 'data' in result:
            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            print("📊 WORKING QUERY RESULTS:")
            print(f"   Total records: {len(records)}")

            # Analyze all records for bureau information
            all_bureaus = set()
            bureau_details = []

            for i, record in enumerate(records):
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    bureau = credit_response.get('CREDIT_BUREAU')
                    if bureau:
                        all_bureaus.add(bureau)
                        bureau_details.append({
                            "record_index": i,
                            "bureau": bureau,
                            "date": credit_response.get('CreditReportFirstIssuedDate'),
                            "has_scores": bool(credit_response.get('CREDIT_SCORE')),
                            "has_liabilities": bool(credit_response.get('CREDIT_LIABILITY'))
                        })

            print("\n📋 BUREAU ANALYSIS:")
            print(f"   Unique bureaus found: {list(all_bureaus)}")
            print(f"   Total credit responses: {len(bureau_details)}")

            if all_bureaus:
                print("\n📋 DETAILED BUREAU BREAKDOWN:")
                for detail in bureau_details:
                    print(f"   Record {detail['record_index']}:")
                    print(f"     Bureau: {detail['bureau']}")
                    print(f"     Date: {detail['date']}")
                    print(f"     Has Scores: {detail['has_scores']}")
                    print(f"     Has Liabilities: {detail['has_liabilities']}")
                    print("     ---")

                # Check for multi-bureau coverage
                if len(all_bureaus) > 1:
                    print("\n✅ MULTI-BUREAU ENTITY CONFIRMED!")
                    print(f"   Bureaus: {list(all_bureaus)}")
                else:
                    print("\n⚠️  SINGLE BUREAU ENTITY")
                    print(f"   Only {list(all_bureaus)[0]} data available")
            else:
                print("\n❌ NO BUREAU DATA FOUND")

        else:
            print("❌ Working query failed")

    except Exception as e:
        print(f"❌ Working query investigation failed: {e}")

    # Test 2: Check if there are other entities with different data
    print("\n🔍 TEST 2: CHECK FOR OTHER ENTITIES")
    print("-" * 50)

    # Use a simple search query that should work
    simple_search = """
    query SimpleEntitySearch {
      search(input: {
        page: 1,
        pageSize: 5
      }) {
        entities {
          id
        }
        total
      }
    }
    """

    try:
        result = tilores_api.gql(simple_search)
        if result and 'data' in result:
            search_data = result['data']['search']
            entities = search_data.get('entities', [])
            total = search_data.get('total', 0)

            print("📊 ENTITY SEARCH RESULTS:")
            print(f"   Total entities available: {total}")
            print(f"   Entities in current page: {len(entities)}")

            if entities:
                print("\n📋 AVAILABLE ENTITIES:")
                for i, entity in enumerate(entities):
                    entity_id = entity.get('id')
                    print(f"   Entity {i + 1}: {entity_id[:8]}...")

                    # Test the first few entities for bureau data
                    if i < 3:  # Only test first 3 to avoid overwhelming
                        print("     Testing for bureau data...")

                        test_query = """
                        query TestEntityBureaus {{
                          entity(input: {{ id: "{entity_id}" }}) {{
                            entity {{
                              records {{
                                CREDIT_RESPONSE {{
                                  CREDIT_BUREAU
                                }}
                              }}
                            }}
                          }}
                        }}
                        """

                        try:
                            test_result = tilores_api.gql(test_query)
                            if test_result and 'data' in test_result:
                                test_entity = test_result['data']['entity']['entity']
                                test_records = test_entity.get('records', [])

                                test_bureaus = set()
                                for record in test_records:
                                    credit_response = record.get('CREDIT_RESPONSE')
                                    if credit_response:
                                        bureau = credit_response.get('CREDIT_BUREAU')
                                        if bureau:
                                            test_bureaus.add(bureau)

                                if test_bureaus:
                                    print(f"       Bureaus found: {list(test_bureaus)}")
                                    if len(test_bureaus) > 1:
                                        print("       ✅ MULTI-BUREAU ENTITY FOUND!")
                                else:
                                    print("       No bureaus found")
                            else:
                                print("       Query failed")

                        except Exception as e:
                            print(f"       Error: {e}")

                        print("     ---")

        else:
            print("❌ Simple search failed")

    except Exception as e:
        print(f"❌ Entity search failed: {e}")

    print("\n🎯 WORKING QUERY BUREAU INVESTIGATION COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    working_query_bureau_investigation()
