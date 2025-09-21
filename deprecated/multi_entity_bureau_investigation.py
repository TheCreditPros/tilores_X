#!/usr/bin/env python3
"""
Multi-Entity Bureau Investigation
Find entities with TransUnion and Experian data
"""

from dotenv import load_dotenv
load_dotenv()

def multi_entity_bureau_investigation():
    """Investigate multiple entities for multi-bureau data"""

    print("🔍 MULTI-ENTITY BUREAU INVESTIGATION")
    print("=" * 50)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return

    # Test 1: Search for entities with different bureaus
    print("\n🔍 TEST 1: SEARCH FOR MULTI-BUREAU ENTITIES")
    print("-" * 50)

    search_query = """
    query SearchMultiBureauEntities {
      search(input: {
        parameters: {
          CREDIT_RESPONSE: {
            CREDIT_BUREAU: ["TransUnion", "Experian", "TU", "EXP", "EFX"]
          }
        },
        page: 1,
        pageSize: 10
      }) {
        entities {
          id
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
            }
          }
        }
        total
      }
    }
    """

    try:
        result = tilores_api.gql(search_query)
        if result and 'data' in result:
            search_data = result['data']['search']
            entities = search_data.get('entities', [])
            total = search_data.get('total', 0)

            print("📊 SEARCH RESULTS:")
            print(f"   Total entities found: {total}")
            print(f"   Entities in current page: {len(entities)}")

            if entities:
                print("\n📋 ENTITY ANALYSIS:")
                for i, entity in enumerate(entities):
                    entity_id = entity.get('id')
                    records = entity.get('records', [])

                    print(f"   Entity {i + 1} (ID: {entity_id[:8]}...):")

                    bureaus = set()
                    for record in records:
                        credit_response = record.get('CREDIT_RESPONSE')
                        if credit_response:
                            bureau = credit_response.get('CREDIT_BUREAU')
                            if bureau:
                                bureaus.add(bureau)

                    if bureaus:
                        print(f"     Bureaus found: {list(bureaus)}")
                        if len(bureaus) > 1:
                            print("     ✅ MULTI-BUREAU ENTITY FOUND!")
                    else:
                        print("     No bureaus found")
                    print("     ---")
            else:
                print("   No entities found with TransUnion/Experian data")

        else:
            print("❌ Search query failed")

    except Exception as e:
        print(f"❌ Test 1 failed: {e}")

    # Test 2: Check if our current entity has hidden bureau data
    print("\n🔍 TEST 2: DEEP DIVE INTO CURRENT ENTITY")
    print("-" * 50)

    # current_entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    deep_query = """
    query DeepBureauInvestigation {{
      entity(input: {{ id: "{current_entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              Report_ID
            }}
            # Check if there are other credit-related fields
            CREDIT_REPORT {{
              BUREAU
              CreditBureau
            }}
            CREDIT_FILE {{
              CreditRepositorySourceType
            }}
            # Check for any other fields that might contain bureau info
            SOURCE
            BUREAU
            CreditBureau
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(deep_query)
        if result and 'data' in result:
            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            print("📊 DEEP DIVE ANALYSIS:")
            print(f"   Total records: {len(records)}")

            all_fields = set()
            for record in records:
                # Get all top-level fields
                for field_name, field_value in record.items():
                    if field_value:
                        all_fields.add(field_name)

            print(f"   All available fields: {sorted(list(all_fields))}")

            # Check for any bureau-related fields
            bureau_fields = [field for field in all_fields if 'bureau' in field.lower() or 'source' in field.lower()]
            if bureau_fields:
                print(f"   Bureau-related fields: {bureau_fields}")
            else:
                print("   No additional bureau-related fields found")

        else:
            print("❌ Deep dive query failed")

    except Exception as e:
        print(f"❌ Test 2 failed: {e}")

    # Test 3: Check if we need to look at different data structures
    print("\n🔍 TEST 3: ALTERNATIVE DATA STRUCTURES")
    print("-" * 50)

    alt_query = """
    query AlternativeDataStructures {{
      entity(input: {{ id: "{current_entity_id}" }}) {{
        entity {{
          # Check if there are other entity-level fields
          CREDIT_RESPONSE {{
            CREDIT_BUREAU
          }}
          CREDIT_REPORT {{
            BUREAU
          }}
          # Check for any other entity-level credit fields
          records {{
            # Look for any field that might contain bureau info
            CREDIT_BUREAU
            BUREAU
            Source
            Repository
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(alt_query)
        if result and 'data' in result:
            entity = result['data']['entity']['entity']

            print("📊 ALTERNATIVE STRUCTURE ANALYSIS:")

            # Check entity-level fields
            entity_fields = [field for field in entity.keys() if field != 'records']
            print(f"   Entity-level fields: {entity_fields}")

            # Check if there are any credit fields at entity level
            credit_entity_fields = [field for field in entity_fields if 'credit' in field.lower()]
            if credit_entity_fields:
                print(f"   Entity-level credit fields: {credit_entity_fields}")

        else:
            print("❌ Alternative structure query failed")

    except Exception as e:
        print(f"❌ Test 3 failed: {e}")

    print("\n🎯 MULTI-ENTITY BUREAU INVESTIGATION COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    multi_entity_bureau_investigation()
