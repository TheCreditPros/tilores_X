#!/usr/bin/env python3
"""
Entity Search for Multi-Bureau Data
Search for entities that have TransUnion and Experian data
"""

from dotenv import load_dotenv
load_dotenv()

def entity_search_for_multi_bureau():
    """Search for entities with multi-bureau data"""

    print("🔍 ENTITY SEARCH FOR MULTI-BUREAU DATA")
    print("=" * 50)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return

    # Test 1: Simple search to see what entities exist
    print("\n🔍 TEST 1: SIMPLE ENTITY SEARCH")
    print("-" * 50)

    simple_search = """
    query SimpleEntitySearch {
      search(input: {
        page: 1,
        pageSize: 10
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

                    # Test each entity for bureau data
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
                                    print(f"       🎯 This entity has: {list(test_bureaus)}")
                                elif 'TransUnion' in test_bureaus:
                                    print("       🎯 TransUnion data found!")
                                elif 'Experian' in test_bureaus:
                                    print("       🎯 Experian data found!")
                            else:
                                print("       No bureaus found")
                        else:
                            print("       Query failed")

                    except Exception as e:
                        print(f"       Error: {e}")

                    print("     ---")

                    # Only test first 5 entities to avoid overwhelming
                    if i >= 4:
                        print("   ... testing limited to first 5 entities")
                        break

        else:
            print("❌ Simple search failed")

    except Exception as e:
        print(f"❌ Entity search failed: {e}")

    # Test 2: Check if there are different data structures
    print("\n🔍 TEST 2: CHECK FOR DIFFERENT DATA STRUCTURES")
    print("-" * 50)

    print("   The interface shows TransUnion, Equifax, and Experian tabs")
    print("   This suggests the data might be stored differently than we're querying")
    print("   Possible explanations:")
    print("     1. Multi-bureau data is in a different entity")
    print("     2. Data is stored in a different field structure")
    print("     3. Data is accessed through a different API endpoint")
    print("     4. The interface aggregates data from multiple sources")

    print("\n   Next steps:")
    print("     1. Find an entity with TransUnion/Experian data")
    print("     2. Understand the correct data structure")
    print("     3. Update our queries to match the actual schema")

    print("\n🎯 ENTITY SEARCH FOR MULTI-BUREAU DATA COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    entity_search_for_multi_bureau()
