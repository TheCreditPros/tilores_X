#!/usr/bin/env python3
"""
Working Credit Analysis
Use the working approach from the user's example to analyze multi-bureau credit data
"""

from dotenv import load_dotenv
load_dotenv()

def working_credit_analysis():
    """Use the working approach to analyze credit data"""

    print("🔍 WORKING CREDIT ANALYSIS")
    print("=" * 50)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return

    # Use the working search approach from the user's example
    print("\n🔍 STEP 1: SEARCH BY EMAIL")
    print("-" * 50)

    search_query = """
    query SearchEntity {
      search(input: { parameters: { EMAIL: "e.j.price1986@gmail.com" } }) {
        entities {
          id
          hits
          records { id }
        }
      }
    }
    """

    try:
        search_result = tilores_api.gql(search_query)
        if search_result and 'data' in search_result:
            entities = search_result.get('data', {}).get('search', {}).get('entities', [])

            if entities:
                records = entities[0].get('records', [])
                print("📊 SEARCH RESULTS:")
                print(f"   Found {len(records)} records for e.j.price1986@gmail.com")

                # Test each record to find the one with credit data
                for i, record in enumerate(records):
                    record_id = record.get('id')
                    print(f"\n   Testing record {i + 1}: {record_id}")

                    # Query each record for credit data
                    entity_query = """
                    query EntityCreditData {{
                      entity(input: {{ id: "{record_id}" }}) {{
                        entity {{
                          records {{
                            CREDIT_RESPONSE {{
                              CREDIT_BUREAU
                              CreditReportFirstIssuedDate
                              CREDIT_SCORE {{
                                Value
                                ModelNameType
                                CreditRepositorySourceType
                              }}
                              CREDIT_LIABILITY {{
                                AccountType
                                CreditLimitAmount
                                CreditBalance
                              }}
                            }}
                          }}
                        }}
                      }}
                    }}
                    """

                    try:
                        entity_result = tilores_api.gql(entity_query)
                        if entity_result and 'data' in entity_result:
                            entity_data = entity_result.get('data', {}).get('entity', {}).get('entity', {})
                            entity_records = entity_data.get('records', [])

                            # Check for credit data
                            credit_data_found = False
                            bureaus = set()

                            for record_data in entity_records:
                                credit_response = record_data.get('CREDIT_RESPONSE')
                                if credit_response:
                                    credit_data_found = True
                                    bureau = credit_response.get('CREDIT_BUREAU')
                                    if bureau:
                                        bureaus.add(bureau)

                            if credit_data_found:
                                print("     ✅ FOUND CREDIT DATA!")
                                print(f"     Bureaus: {list(bureaus)}")

                                if len(bureaus) > 1:
                                    print("     🎯 MULTI-BUREAU ENTITY FOUND!")
                                    print(f"     This record has: {list(bureaus)}")

                                    # This is the record we want to analyze
                                    print("\n📊 DETAILED CREDIT ANALYSIS:")
                                    print(f"   Record ID: {record_id}")
                                    print(f"   Bureaus: {list(bureaus)}")

                                    # Show detailed credit data
                                    for record_data in entity_records:
                                        credit_response = record_data.get('CREDIT_RESPONSE')
                                        if credit_response:
                                            bureau = credit_response.get('CREDIT_BUREAU')
                                            date = credit_response.get('CreditReportFirstIssuedDate')

                                            print("   📋 Credit Report:")
                                            print(f"     Bureau: {bureau}")
                                            print(f"     Date: {date}")

                                            # Show credit scores
                                            credit_scores = credit_response.get('CREDIT_SCORE', [])
                                            if credit_scores:
                                                print(f"     Scores: {len(credit_scores)}")
                                                for score in credit_scores:
                                                    value = score.get('Value')
                                                    model = score.get('ModelNameType')
                                                    source = score.get('CreditRepositorySourceType')
                                                    print(f"       {value} | {model} | {source}")

                                            # Show credit liabilities
                                            credit_liabilities = credit_response.get('CREDIT_LIABILITY', [])
                                            if credit_liabilities:
                                                print(f"     Liabilities: {len(credit_liabilities)}")

                                    break
                                else:
                                    print(f"     Single bureau: {list(bureaus)[0] if bureaus else 'None'}")
                            else:
                                print("     No credit data found")
                        else:
                            print("     Could not fetch entity data")

                    except Exception as e:
                        print(f"     Error querying record: {e}")

            else:
                print("❌ No entities found for email")

        else:
            print("❌ Search query failed")

    except Exception as e:
        print(f"❌ Search failed: {e}")

    print("\n🎯 WORKING CREDIT ANALYSIS COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    working_credit_analysis()
