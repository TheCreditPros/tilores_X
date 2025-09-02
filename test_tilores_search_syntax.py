#!/usr/bin/env python3
"""
Test proper Tilores search syntax based on documentation
"""

from dotenv import load_dotenv
load_dotenv()

def test_tilores_search_syntax():
    """Test the correct Tilores search syntax from documentation"""
    
    print("🔍 TESTING TILORES SEARCH SYNTAX FROM DOCUMENTATION")
    print("=" * 70)
    
    try:
        from tilores import TiloresAPI
        
        tilores_api = TiloresAPI.from_environ()
        
        # Test 1: Basic search with proper syntax
        print("\n🎯 TEST 1: Basic search with proper syntax")
        basic_search = """
        query BasicSearch {
          search(input: { parameters: { EMAIL: "e.j.price1986@gmail.com" } }) {
            entities {
              id
              entity {
                id
              }
            }
          }
        }
        """
        
        print("🔍 Executing basic search...")
        result1 = tilores_api.gql(basic_search)
        
        if result1 and 'data' in result1:
            entities = result1['data']['search']['entities']
            print(f"✅ Basic search successful: {len(entities)} entities found")
            if entities:
                print(f"   First entity ID: {entities[0]['id']}")
                return entities[0]['id']
        else:
            print("❌ Basic search failed")
            print(f"   Result: {result1}")
        
        return None
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_alternative_search_fields():
    """Test alternative search field combinations"""
    
    print("\n🔍 TESTING ALTERNATIVE SEARCH FIELDS")
    print("=" * 70)
    
    try:
        from tilores import TiloresAPI
        
        tilores_api = TiloresAPI.from_environ()
        
        # Test different field combinations
        search_tests = [
            {
                "name": "EMAIL search",
                "query": """
                query EmailSearch {
                  search(input: { parameters: { EMAIL: "e.j.price1986@gmail.com" } }) {
                    entities {
                      id
                      entity {
                        id
                      }
                    }
                  }
                }
                """
            },
            {
                "name": "FIRST_NAME search",
                "query": """
                query NameSearch {
                  search(input: { parameters: { FIRST_NAME: "Esteban" } }) {
                    entities {
                      id
                      entity {
                        id
                      }
                    }
                  }
                }
                """
            },
            {
                "name": "CLIENT_ID search",
                "query": """
                query ClientSearch {
                  search(input: { parameters: { CLIENT_ID: "1747598" } }) {
                    entities {
                      id
                      entity {
                        id
                      }
                    }
                  }
                }
                """
            }
        ]
        
        for test in search_tests:
            print(f"\n🎯 Testing: {test['name']}")
            try:
                result = tilores_api.gql(test['query'])
                if result and 'data' in result and result['data']['search']['entities']:
                    entities = result['data']['search']['entities']
                    print(f"   ✅ SUCCESS: {len(entities)} entities found")
                    if entities:
                        print(f"      Entity ID: {entities[0]['id']}")
                else:
                    print("   ❌ FAILED: No entities found")
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
        
    except Exception as e:
        print(f"❌ Alternative search test failed: {e}")

if __name__ == "__main__":
    print("🚀 TESTING TILORES SEARCH SYNTAX")
    print("=" * 70)
    
    # Test 1: Basic search syntax
    entity_id = test_tilores_search_syntax()
    
    # Test 2: Alternative search fields
    test_alternative_search_fields()
    
    if entity_id:
        print("\n🎉 SUCCESS: Found working search syntax!")
        print(f"   Entity ID: {entity_id}")
    else:
        print("\n⚠️  Search syntax needs refinement")
