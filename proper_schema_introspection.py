#!/usr/bin/env python3
"""
Proper Schema Introspection
Use GraphQL introspection to understand the actual schema structure
"""

from dotenv import load_dotenv
load_dotenv()

def proper_schema_introspection():
    """Use proper GraphQL introspection to understand the schema"""

    print("🔍 PROPER SCHEMA INTROSPECTION")
    print("=" * 50)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return

    # Test 1: Minimal "give me all types" query (as suggested by user)
    print("\n🔍 TEST 1: MINIMAL SCHEMA INTROSPECTION")
    print("-" * 50)

    introspection_query = """
    query IntrospectAllTypes {
      __schema {
        types {
          name
          kind
          description
          fields {
            name
            description
          }
          inputFields {
            name
            description
          }
          enumValues {
            name
            description
          }
        }
      }
    }
    """

    try:
        result = tilores_api.gql(introspection_query)
        if result and 'data' in result:
            schema = result['data']['__schema']
            types = schema.get('types', [])

            print("📊 SCHEMA INTROSPECTION RESULTS:")
            print(f"   Total types found: {len(types)}")

            # Look for credit-related types
            credit_types = []
            for type_info in types:
                name = type_info.get('name', '')
                if 'credit' in name.lower() or 'bureau' in name.lower() or 'report' in name.lower():
                    credit_types.append(name)

            if credit_types:
                print("\n📋 CREDIT-RELATED TYPES:")
                for credit_type in credit_types:
                    print(f"   {credit_type}")

            # Look for entity/search types
            entity_types = []
            for type_info in types:
                name = type_info.get('name', '')
                if 'entity' in name.lower() or 'search' in name.lower():
                    entity_types.append(name)

            if entity_types:
                print("\n📋 ENTITY/SEARCH TYPES:")
                for entity_type in entity_types:
                    print(f"   {entity_type}")

            # Show first 10 types for reference
            print("\n📋 FIRST 10 TYPES:")
            for i, type_info in enumerate(types[:10]):
                name = type_info.get('name', '')
                kind = type_info.get('kind', '')
                print(f"   {i + 1}. {name} ({kind})")

        else:
            print("❌ Introspection query failed")

    except Exception as e:
        print(f"❌ Test 1 failed: {e}")

    # Test 2: Fetch SDL for specific types (as suggested by user)
    print("\n🔍 TEST 2: SPECIFIC TYPE INTROSPECTION")
    print("-" * 50)

    # Try to introspect the Entity type
    entity_introspection = """
    query IntrospectEntity {
      __type(name: "Entity") {
        name
        kind
        description
        fields {
          name
          type {
            kind
            name
            ofType {
              kind
              name
            }
          }
          description
        }
      }
    }
    """

    try:
        result = tilores_api.gql(entity_introspection)
        if result and 'data' in result:
            entity_type = result['data']['__type']
            if entity_type:
                name = entity_type.get('name', '')
                kind = entity_type.get('kind', '')
                fields = entity_type.get('fields', [])

                print("📊 ENTITY TYPE INTROSPECTION:")
                print(f"   Name: {name}")
                print(f"   Kind: {kind}")
                print(f"   Fields: {len(fields)}")

                if fields:
                    print("\n📋 ENTITY FIELDS:")
                    for field in fields:
                        field_name = field.get('name', '')
                        field_type = field.get('type', {})
                        field_kind = field_type.get('kind', '')
                        field_name_type = field_type.get('name', '')

                        print(f"     {field_name}: {field_kind} {field_name_type}")

            else:
                print("❌ Entity type not found")

        else:
            print("❌ Entity introspection failed")

    except Exception as e:
        print(f"❌ Test 2 failed: {e}")

    # Test 3: Try to introspect the Search type
    print("\n🔍 TEST 3: SEARCH TYPE INTROSPECTION")
    print("-" * 50)

    search_introspection = """
    query IntrospectSearch {
      __type(name: "Search") {
        name
        kind
        description
        fields {
          name
          type {
            kind
            name
            ofType {
              kind
              name
            }
          }
          description
        }
      }
    }
    """

    try:
        result = tilores_api.gql(search_introspection)
        if result and 'data' in result:
            search_type = result['data']['__type']
            if search_type:
                name = search_type.get('name', '')
                kind = search_type.get('kind', '')
                fields = search_type.get('fields', [])

                print("📊 SEARCH TYPE INTROSPECTION:")
                print(f"   Name: {name}")
                print(f"   Kind: {kind}")
                print(f"   Fields: {len(fields)}")

                if fields:
                    print("\n📋 SEARCH FIELDS:")
                    for field in fields:
                        field_name = field.get('name', '')
                        field_type = field.get('type', {})
                        field_kind = field_type.get('kind', '')
                        field_name_type = field_type.get('name', '')

                        print(f"     {field_name}: {field_kind} {field_name_type}")

            else:
                print("❌ Search type not found")

        else:
            print("❌ Search introspection failed")

    except Exception as e:
        print(f"❌ Test 3 failed: {e}")

    print("\n🎯 PROPER SCHEMA INTROSPECTION COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    proper_schema_introspection()
