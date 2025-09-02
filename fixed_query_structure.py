#!/usr/bin/env python3
"""
Fixed Query Structure
Use the correct query structure to access multi-bureau data
"""

from dotenv import load_dotenv
load_dotenv()

def fixed_query_structure():
    """Use the correct query structure to access multi-bureau data"""

    print("🔍 FIXED QUERY STRUCTURE")
    print("=" * 50)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized successfully")
    except Exception as e:
        print(f"❌ Tilores API initialization failed: {e}")
        return

    # Use the working search approach
    print("\n🔍 STEP 1: SEARCH BY EMAIL")
    print("-" * 50)

    search_query = """
    query SearchMultiBureauEntity {
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

                # Test the first few records with a simpler query
                for i, record in enumerate(records[:5]):  # Test first 5
                    record_id = record.get('id')
                    print(f"\n   Testing record {i + 1}: {record_id}")

                    # Use a very simple query first
                    simple_query = """
                    query SimpleEntityTest {{
                      entity(input: {{ id: "{record_id}" }}) {{
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
                        simple_result = tilores_api.gql(simple_query)
                        if simple_result and 'data' in simple_result:
                            entity_data = simple_result.get('data', {}).get('entity', {})
                            if entity_data:
                                entity = entity_data.get('entity', {})
                                if entity:
                                    entity_records = entity.get('records', [])
                                    print("     ✅ Entity data retrieved successfully")
                                    print(f"     Records found: {len(entity_records)}")

                                    # Check for credit data
                                    bureaus = set()
                                    for record_data in entity_records:
                                        credit_response = record_data.get('CREDIT_RESPONSE')
                                        if credit_response:
                                            bureau = credit_response.get('CREDIT_BUREAU')
                                            if bureau:
                                                bureaus.add(bureau)

                                    if bureaus:
                                        print(f"     Bureaus found: {list(bureaus)}")
                                        if len(bureaus) > 1:
                                            print("     🎯 MULTI-BUREAU ENTITY FOUND!")
                                            print(f"     This record has: {list(bureaus)}")

                                            # Now test the full credit analysis
                                            print("\n🔍 TESTING FULL CREDIT ANALYSIS:")
                                            print("-" * 40)

                                            full_query = """
                                            query FullCreditAnalysis {{
                                              entity(input: {{ id: "{record_id}" }}) {{
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
                                                  }}
                                                }}
                                              }}
                                            }}
                                            """

                                            try:
                                                full_result = tilores_api.gql(full_query)
                                                if full_result and 'data' in full_result:
                                                    full_entity_data = full_result.get('data', {}).get('entity', {})
                                                    if full_entity_data:
                                                        full_entity = full_entity_data.get('entity', {})
                                                        if full_entity:
                                                            full_records = full_entity.get('records', [])

                                                            print("📊 FULL CREDIT ANALYSIS RESULTS:")
                                                            print(f"   Total records: {len(full_records)}")

                                                            # Analyze the data
                                                            bureau_data = {}
                                                            for record_data in full_records:
                                                                credit_response = record_data.get('CREDIT_RESPONSE')
                                                                if credit_response:
                                                                    bureau = credit_response.get('CREDIT_BUREAU')
                                                                    date = credit_response.get('CreditReportFirstIssuedDate')

                                                                    if bureau and date:
                                                                        if bureau not in bureau_data:
                                                                            bureau_data[bureau] = {}

                                                                        if date not in bureau_data[bureau]:
                                                                            bureau_data[bureau][date] = {
                                                                                'scores': [],
                                                                                'liabilities': []
                                                                            }

                                                                        # Get scores
                                                                        scores = credit_response.get('CREDIT_SCORE', [])
                                                                        for score in scores:
                                                                            value = score.get('Value')
                                                                            model = score.get('ModelNameType')
                                                                            if value and value != "None":
                                                                                bureau_data[bureau][date]['scores'].append({
                                                                                    'value': value,
                                                                                    'model': model
                                                                                })

                                                                        # Get liabilities
                                                                        liabilities = credit_response.get('CREDIT_LIABILITY', [])
                                                                        for liability in liabilities:
                                                                            account_type = liability.get('AccountType')
                                                                            limit = liability.get('CreditLimitAmount')
                                                                            balance = liability.get('CreditBalance')

                                                                            if account_type:
                                                                                bureau_data[bureau][date]['liabilities'].append({
                                                                                    'type': account_type,
                                                                                    'limit': limit,
                                                                                    'balance': balance
                                                                                })

                                                            # Display results
                                                            for bureau, dates in bureau_data.items():
                                                                print(f"\n   📋 {bureau}:")
                                                                for date, data in dates.items():
                                                                    scores = data['scores']
                                                                    liabilities = data['liabilities']

                                                                    print(f"     {date}:")
                                                                    if scores:
                                                                        print(f"       Scores: {len(scores)}")
                                                                        for score in scores:
                                                                            print(f"         {score['value']} | {score['model']}")
                                                                    if liabilities:
                                                                        print(f"       Liabilities: {len(liabilities)}")
                                                                        for liability in liabilities:
                                                                            print(f"         {liability['type']}")

                                                            print("\n✅ FULL CREDIT ANALYSIS SUCCESSFUL!")
                                                            print("   Multi-bureau data accessed successfully")
                                                            print("   All credit information retrieved")
                                                            return  # Success, exit early

                                            except Exception as e:
                                                print(f"     ❌ Full analysis failed: {e}")

                                    else:
                                        print("     No bureaus found")
                                else:
                                    print("     ❌ No entity data")
                            else:
                                print("     ❌ No entity data")
                        else:
                            print("     ❌ Query failed")

                    except Exception as e:
                        print(f"     ❌ Error: {e}")

                print("\n⚠️  No multi-bureau entity found in first 5 records")

            else:
                print("❌ No entities found")

        else:
            print("❌ Search failed")

    except Exception as e:
        print(f"❌ Search failed: {e}")

    print("\n🎯 FIXED QUERY STRUCTURE COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    fixed_query_structure()
