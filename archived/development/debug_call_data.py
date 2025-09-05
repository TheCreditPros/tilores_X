#!/usr/bin/env python3
"""
Systematic debugging script to find where call data actually lives
Following the troubleshooting plan to isolate the data linkage issue
"""

import asyncio
import json
import re
from direct_credit_api_with_phone import DirectCreditAPIWithPhone

async def debug_call_data():
    """Systematic debugging of call data location and format"""

    api = DirectCreditAPIWithPhone()
    entity_id = "dc93a2cd-de0a-444f-ad47-3003ba998cd3"

    print("🔍 SYSTEMATIC CALL DATA DEBUGGING")
    print("=" * 50)

    # Step 1: Get contact info to extract phone numbers
    print("\n1️⃣ GETTING CONTACT INFO...")
    try:
        contact_query = """
        query GetContactInfo($id: ID!) {
          entity(input: { id: $id }) {
            entity {
              id
              records {
                id
                EMAIL
                PHONE_EXTERNAL
                PHONE_NUMBER
                FIRST_NAME
                LAST_NAME
                CLIENT_ID
              }
            }
          }
        }
        """

        result = await api.query_tilores(contact_query, {"id": entity_id})
        entity = result.get("data", {}).get("entity", {}).get("entity")

        if entity:
            records = entity.get("records", [])
            print(f"✅ Found {len(records)} records for entity")

            # Extract phone numbers
            phone_external = None
            phone_number = None
            for record in records:
                if record.get("PHONE_EXTERNAL") and not phone_external:
                    phone_external = record.get("PHONE_EXTERNAL")
                if record.get("PHONE_NUMBER") and not phone_number:
                    phone_number = record.get("PHONE_NUMBER")

            print(f"📞 PHONE_EXTERNAL: {phone_external}")
            print(f"📞 PHONE_NUMBER: {phone_number}")
        else:
            print("❌ No entity found")
            return

    except Exception as e:
        print(f"❌ Contact info error: {e}")
        return

    # Step 2: Test record-scope call data (current approach)
    print("\n2️⃣ TESTING RECORD-SCOPE CALL DATA...")
    try:
        record_query = """
        query RecordScopeCalls($id: ID!) {
          entity(input: { id: $id }) {
            entity {
              id
              records {
                id
                PHONE_NUMBER
                CALL_ID
                CALL_START_TIME
                CALL_DURATION
                CALL_TYPE
                AGENT_USERNAME
                CAMPAIGN_NAME
              }
            }
          }
        }
        """

        result = await api.query_tilores(record_query, {"id": entity_id})
        entity = result.get("data", {}).get("entity", {}).get("entity")

        if entity:
            records = entity.get("records", [])
            call_records = [r for r in records if r.get("CALL_ID") or r.get("CALL_START_TIME")]

            print(f"📊 Total records: {len(records)}")
            print(f"📞 Call records: {len(call_records)}")

            if call_records:
                print("✅ Found call records in current entity:")
                for i, record in enumerate(call_records[:3]):  # Show first 3
                    print(f"  Record {i+1}:")
                    print(f"    CALL_ID: {record.get('CALL_ID')}")
                    print(f"    CALL_START_TIME: {record.get('CALL_START_TIME')}")
                    print(f"    CALL_DURATION: {record.get('CALL_DURATION')}")
                    print(f"    CALL_TYPE: {record.get('CALL_TYPE')}")
                    print(f"    AGENT_USERNAME: {record.get('AGENT_USERNAME')}")
            else:
                print("❌ No call records found in current entity")
        else:
            print("❌ No entity found")

    except Exception as e:
        print(f"❌ Record scope error: {e}")

    # Step 3: Test phone-first searches with variants
    print("\n3️⃣ TESTING PHONE-FIRST SEARCHES...")

    def generate_phone_variants(phone):
        """Generate phone number variants for testing"""
        if not phone:
            return []

        # Clean the phone number
        cleaned = re.sub(r'[^\d]', '', phone)

        variants = [
            phone,  # Original
            cleaned,  # Digits only
            f"+1{cleaned}",  # E.164
            f"1{cleaned}",  # 1 prefix
        ]

        # Add formatted versions if it's a 10-digit number
        if len(cleaned) == 10:
            area = cleaned[:3]
            exchange = cleaned[3:6]
            number = cleaned[6:]
            variants.extend([
                f"{area}-{exchange}-{number}",
                f"({area}) {exchange}-{number}",
                f"{area}.{exchange}.{number}",
            ])

        return list(set(variants))  # Remove duplicates

    # Test with both phone numbers
    test_phones = [phone_external, phone_number]
    test_phones = [p for p in test_phones if p]  # Remove None values

    for phone in test_phones:
        print(f"\n📞 Testing phone: {phone}")
        variants = generate_phone_variants(phone)

        for variant in variants[:5]:  # Test first 5 variants
            try:
                search_query = f"""
                query PhoneSearch {{
                  search(input: {{ parameters: {{ PHONE_NUMBER: "{variant}" }} }}) {{
                    entities {{
                      id
                      hits
                      records {{
                        id
                        PHONE_NUMBER
                        CALL_ID
                        CALL_START_TIME
                        CALL_DURATION
                        CALL_TYPE
                        AGENT_USERNAME
                        CAMPAIGN_NAME
                        EMAIL
                        FIRST_NAME
                        LAST_NAME
                      }}
                    }}
                  }}
                }}
                """

                result = await api.query_tilores(search_query)
                entities = result.get("data", {}).get("search", {}).get("entities", [])

                if entities:
                    print(f"  ✅ Variant '{variant}': Found {len(entities)} entities")

                    for entity in entities:
                        records = entity.get("records", [])
                        call_records = [r for r in records if r.get("CALL_ID") or r.get("CALL_START_TIME")]

                        if call_records:
                            print(f"    📞 Entity {entity['id']}: {len(call_records)} call records")
                            for record in call_records[:2]:  # Show first 2
                                print(f"      CALL_ID: {record.get('CALL_ID')}")
                                print(f"      CALL_START_TIME: {record.get('CALL_START_TIME')}")
                                print(f"      CALL_DURATION: {record.get('CALL_DURATION')}")
                        else:
                            print(f"    📞 Entity {entity['id']}: No call records")
                else:
                    print(f"  ❌ Variant '{variant}': No entities found")

            except Exception as e:
                print(f"  ❌ Variant '{variant}': Error - {e}")

    # Step 4: Test edges for separate PhoneCall type
    print("\n4️⃣ TESTING EDGES FOR SEPARATE PHONECALL TYPE...")
    try:
        edges_query = """
        query TestEdges($id: ID!) {
          entity(input: { id: $id }) {
            entity {
              id
              edges {
                type
                nodes {
                  __typename
                  ... on Record {
                    id
                    PHONE_NUMBER
                    CALL_ID
                    CALL_START_TIME
                    CALL_DURATION
                    CALL_TYPE
                    AGENT_USERNAME
                    CAMPAIGN_NAME
                  }
                }
              }
            }
          }
        }
        """

        result = await api.query_tilores(edges_query, {"id": entity_id})
        entity = result.get("data", {}).get("entity", {}).get("entity")

        if entity:
            edges = entity.get("edges", [])
            print(f"📊 Found {len(edges)} edge types")

            for edge in edges:
                edge_type = edge.get("type")
                nodes = edge.get("nodes", [])
                print(f"  Edge type: {edge_type} ({len(nodes)} nodes)")

                call_nodes = [n for n in nodes if n.get("CALL_ID") or n.get("CALL_START_TIME")]
                if call_nodes:
                    print(f"    ✅ Found {len(call_nodes)} call nodes")
                    for node in call_nodes[:2]:
                        print(f"      CALL_ID: {node.get('CALL_ID')}")
                        print(f"      CALL_START_TIME: {node.get('CALL_START_TIME')}")
                else:
                    print(f"    ❌ No call nodes in this edge type")
        else:
            print("❌ No entity found")

    except Exception as e:
        print(f"❌ Edges test error: {e}")

    # Step 5: Check for PhoneCall type in schema
    print("\n5️⃣ CHECKING FOR PHONECALL TYPE IN SCHEMA...")
    try:
        schema_query = """
        query CheckPhoneCallType {
          __type(name: "PhoneCall") {
            name
            fields {
              name
              type {
                name
                kind
              }
            }
          }
        }
        """

        result = await api.query_tilores(schema_query)
        phone_call_type = result.get("data", {}).get("__type")

        if phone_call_type:
            print("✅ PhoneCall type exists in schema!")
            fields = phone_call_type.get("fields", [])
            print(f"📊 PhoneCall has {len(fields)} fields:")
            for field in fields[:10]:  # Show first 10 fields
                print(f"  - {field['name']}")
        else:
            print("❌ PhoneCall type not found in schema")

    except Exception as e:
        print(f"❌ Schema check error: {e}")

    print("\n" + "=" * 50)
    print("🎯 DEBUGGING COMPLETE")
    print("Check the results above to identify where call data actually lives!")

if __name__ == "__main__":
    asyncio.run(debug_call_data())
