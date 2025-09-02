#!/usr/bin/env python3
"""
Simple GraphQL Introspection - Find credit data structure
Use proper GraphQL introspection to discover where credit data is stored
"""

from dotenv import load_dotenv
load_dotenv()

def introspect_schema():
    """Introspect the schema to find credit-related types and fields"""

    print("🔍 GRAPHQL INTROSPECTION FOR CREDIT DATA")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        # Simple introspection query to get all types
        introspection_query = """
        query IntrospectSchema {
          __schema {
            types {
              name
              kind
              description
              fields {
                name
                description
                type {
                  kind
                  name
                  ofType {
                    kind
                    name
                  }
                }
              }
            }
          }
        }
        """

        print("🔍 Executing GraphQL introspection...")
        result = tilores_api.gql(introspection_query)

        if result and 'data' in result:
            types = result['data']['__schema']['types']
            print(f"✅ Introspection successful! Found {len(types)} types")

            # Look for credit-related types
            credit_types = []
            for type_info in types:
                type_name = type_info.get('name', '')
                if any(credit_term in type_name.upper() for credit_term in ['CREDIT', 'SCORE', 'BUREAU', 'INQUIRY', 'PAYMENT', 'ACCOUNT']):
                    credit_types.append(type_info)

            if credit_types:
                print("\n🎉 CREDIT-RELATED TYPES FOUND!")
                for type_info in credit_types:
                    print(f"\n   📋 Type: {type_info['name']}")
                    print(f"      Kind: {type_info['kind']}")
                    if type_info.get('description'):
                        print(f"      Description: {type_info['description']}")

                    # Show fields if available
                    if type_info.get('fields'):
                        field_names = [field['name'] for field in type_info['fields']]
                        print(f"      Fields: {field_names}")

                        # Look for credit-related fields within this type
                        credit_fields = [name for name in field_names if any(credit_term in name.upper() for credit_term in ['CREDIT', 'SCORE', 'BUREAU', 'INQUIRY', 'PAYMENT'])]
                        if credit_fields:
                            print(f"      🎯 Credit Fields: {credit_fields}")

                return True
            else:
                print("\n❌ No credit-related types found in schema")

                # Show all type names for debugging
                print("\n📋 All available types:")
                for type_info in types[:20]:  # Show first 20
                    print(f"   • {type_info['name']}")
                if len(types) > 20:
                    print(f"   ... and {len(types) - 20} more types")

                return False

        else:
            print(f"❌ Introspection failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Introspection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def introspect_record_type():
    """Introspect the Record type specifically"""

    print("\n🔍 INTROSPECTING RECORD TYPE")
    print("=" * 70)

    try:
        from tilores import TiloresAPI

        tilores_api = TiloresAPI.from_environ()

        # Introspect the Record type
        record_query = """
        query IntrospectRecord {
          __type(name: "Record") {
            name
            kind
            description
            fields {
              name
              description
              type {
                kind
                name
                ofType {
                  kind
                  name
                }
              }
            }
          }
        }
        """

        print("🔍 Introspecting Record type...")
        result = tilores_api.gql(record_query)

        if result and 'data' in result:
            record_type = result['data']['__type']
            if record_type:
                print(f"✅ Record type found: {record_type['name']}")
                print(f"   Kind: {record_type['kind']}")
                if record_type.get('description'):
                    print(f"   Description: {record_type['description']}")

                # Show all fields
                fields = record_type.get('fields', [])
                if fields:
                    print(f"\n📋 Record fields ({len(fields)} total):")
                    for field in fields:
                        field_name = field['name']
                        field_type = field['type']['name'] or field['type']['ofType']['name']
                        print(f"   • {field_name}: {field_type}")

                        # Highlight credit-related fields
                        if any(credit_term in field_name.upper() for credit_term in ['CREDIT', 'SCORE', 'BUREAU', 'INQUIRY', 'PAYMENT']):
                            print(f"      🎯 CREDIT FIELD: {field_name}")

                    # Count credit fields
                    credit_fields = [f['name'] for f in fields if any(credit_term in f['name'].upper() for credit_term in ['CREDIT', 'SCORE', 'BUREAU', 'INQUIRY', 'PAYMENT'])]
                    if credit_fields:
                        print(f"\n🎉 Found {len(credit_fields)} credit-related fields in Record type!")
                        return True
                    else:
                        print("\n❌ No credit-related fields found in Record type")
                        return False
                else:
                    print("   No fields found")
                    return False
            else:
                print("❌ Record type not found")
                return False

        else:
            print(f"❌ Record introspection failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Record introspection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 SIMPLE GRAPHQL INTROSPECTION FOR CREDIT DATA")
    print("=" * 70)

    # Run introspection
    test1_success = introspect_schema()
    test2_success = introspect_record_type()

    print("\n" + "=" * 70)
    print("📊 INTROSPECTION RESULTS:")
    print(f"   • Schema Overview: {'✅ SUCCESS' if test1_success else '❌ FAILED'}")
    print(f"   • Record Type: {'✅ SUCCESS' if test2_success else '❌ FAILED'}")

    overall_success = test1_success or test2_success
    print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")

    if overall_success:
        print("🎉 Credit schema discovery successful!")
        print("   • Real credit data structure identified")
        print("   • Ready to implement enhanced credit tool")
    else:
        print("⚠️  Credit schema discovery needs investigation")
        print("   • Check if introspection is enabled")
        print("   • Verify authentication and permissions")
