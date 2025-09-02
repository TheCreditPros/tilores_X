#!/usr/bin/env python3
"""
Search for ANY call data in the entire system to see if it exists at all
"""

import asyncio
import json
from direct_credit_api_with_phone import DirectCreditAPIWithPhone

async def find_any_call_data():
    """Search for any call data anywhere in the system"""

    api = DirectCreditAPIWithPhone()

    print("🔍 SEARCHING FOR ANY CALL DATA IN THE SYSTEM")
    print("=" * 50)

    # Strategy 1: Search for any entity with non-null CALL_ID
    print("\n1️⃣ SEARCHING FOR ANY CALL_ID...")
    try:
        # Try a few common call ID patterns
        call_id_patterns = [
            "CALL_",  # Common prefix
            "HODU_",  # Hodu system prefix
            "2024",   # Year-based
            "2025",   # Year-based
        ]

        for pattern in call_id_patterns:
            search_query = f"""
            query SearchCallID {{
              search(input: {{ parameters: {{ CALL_ID: "{pattern}" }} }}) {{
                entities {{
                  id
                  hits
                  records {{
                    id
                    CALL_ID
                    CALL_START_TIME
                    CALL_DURATION
                    CALL_TYPE
                    AGENT_USERNAME
                    PHONE_NUMBER
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
                print(f"✅ Pattern '{pattern}': Found {len(entities)} entities")
                for entity in entities:
                    records = entity.get("records", [])
                    call_records = [r for r in records if r.get("CALL_ID")]
                    if call_records:
                        print(f"  📞 Entity {entity['id']}: {len(call_records)} call records")
                        for record in call_records[:2]:
                            print(f"    CALL_ID: {record.get('CALL_ID')}")
                            print(f"    CALL_START_TIME: {record.get('CALL_START_TIME')}")
                            print(f"    PHONE_NUMBER: {record.get('PHONE_NUMBER')}")
                            print(f"    EMAIL: {record.get('EMAIL')}")
            else:
                print(f"❌ Pattern '{pattern}': No entities found")

    except Exception as e:
        print(f"❌ Call ID search error: {e}")

    # Strategy 2: Search for any entity with non-null CALL_START_TIME
    print("\n2️⃣ SEARCHING FOR ANY CALL_START_TIME...")
    try:
        # Try date-based searches
        date_patterns = [
            "2024-",
            "2025-",
            "2024/",
            "2025/",
        ]

        for pattern in date_patterns:
            search_query = f"""
            query SearchCallTime {{
              search(input: {{ parameters: {{ CALL_START_TIME: "{pattern}" }} }}) {{
                entities {{
                  id
                  hits
                  records {{
                    id
                    CALL_ID
                    CALL_START_TIME
                    CALL_DURATION
                    CALL_TYPE
                    AGENT_USERNAME
                    PHONE_NUMBER
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
                print(f"✅ Date pattern '{pattern}': Found {len(entities)} entities")
                for entity in entities:
                    records = entity.get("records", [])
                    call_records = [r for r in records if r.get("CALL_START_TIME")]
                    if call_records:
                        print(f"  📞 Entity {entity['id']}: {len(call_records)} call records")
                        for record in call_records[:2]:
                            print(f"    CALL_START_TIME: {record.get('CALL_START_TIME')}")
                            print(f"    CALL_ID: {record.get('CALL_ID')}")
                            print(f"    PHONE_NUMBER: {record.get('PHONE_NUMBER')}")
            else:
                print(f"❌ Date pattern '{pattern}': No entities found")

    except Exception as e:
        print(f"❌ Call time search error: {e}")

    # Strategy 3: Search for any entity with non-null AGENT_USERNAME
    print("\n3️⃣ SEARCHING FOR ANY AGENT_USERNAME...")
    try:
        # Try common agent name patterns
        agent_patterns = [
            "agent",
            "support",
            "sales",
            "admin",
        ]

        for pattern in agent_patterns:
            search_query = f"""
            query SearchAgent {{
              search(input: {{ parameters: {{ AGENT_USERNAME: "{pattern}" }} }}) {{
                entities {{
                  id
                  hits
                  records {{
                    id
                    CALL_ID
                    CALL_START_TIME
                    CALL_DURATION
                    CALL_TYPE
                    AGENT_USERNAME
                    PHONE_NUMBER
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
                print(f"✅ Agent pattern '{pattern}': Found {len(entities)} entities")
                for entity in entities:
                    records = entity.get("records", [])
                    call_records = [r for r in records if r.get("AGENT_USERNAME")]
                    if call_records:
                        print(f"  📞 Entity {entity['id']}: {len(call_records)} call records")
                        for record in call_records[:2]:
                            print(f"    AGENT_USERNAME: {record.get('AGENT_USERNAME')}")
                            print(f"    CALL_ID: {record.get('CALL_ID')}")
                            print(f"    CALL_START_TIME: {record.get('CALL_START_TIME')}")
            else:
                print(f"❌ Agent pattern '{pattern}': No entities found")

    except Exception as e:
        print(f"❌ Agent search error: {e}")

    # Strategy 4: Search for any entity with non-null CAMPAIGN_NAME
    print("\n4️⃣ SEARCHING FOR ANY CAMPAIGN_NAME...")
    try:
        # Try common campaign patterns
        campaign_patterns = [
            "campaign",
            "outbound",
            "inbound",
            "follow",
        ]

        for pattern in campaign_patterns:
            search_query = f"""
            query SearchCampaign {{
              search(input: {{ parameters: {{ CAMPAIGN_NAME: "{pattern}" }} }}) {{
                entities {{
                  id
                  hits
                  records {{
                    id
                    CALL_ID
                    CALL_START_TIME
                    CALL_DURATION
                    CALL_TYPE
                    AGENT_USERNAME
                    CAMPAIGN_NAME
                    PHONE_NUMBER
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
                print(f"✅ Campaign pattern '{pattern}': Found {len(entities)} entities")
                for entity in entities:
                    records = entity.get("records", [])
                    call_records = [r for r in records if r.get("CAMPAIGN_NAME")]
                    if call_records:
                        print(f"  📞 Entity {entity['id']}: {len(call_records)} call records")
                        for record in call_records[:2]:
                            print(f"    CAMPAIGN_NAME: {record.get('CAMPAIGN_NAME')}")
                            print(f"    CALL_ID: {record.get('CALL_ID')}")
                            print(f"    CALL_START_TIME: {record.get('CALL_START_TIME')}")
            else:
                print(f"❌ Campaign pattern '{pattern}': No entities found")

    except Exception as e:
        print(f"❌ Campaign search error: {e}")

    # Strategy 5: Get a sample of all entities to see if any have call data
    print("\n5️⃣ SAMPLING ALL ENTITIES FOR CALL DATA...")
    try:
        # Get a broad search to sample entities
        sample_query = """
        query SampleEntities {
          search(input: { parameters: { EMAIL: "gmail.com" } }) {
            entities {
              id
              hits
              records {
                id
                EMAIL
                FIRST_NAME
                LAST_NAME
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

        result = await api.query_tilores(sample_query)
        entities = result.get("data", {}).get("search", {}).get("entities", [])

        print(f"📊 Sampled {len(entities)} entities")

        total_records = 0
        call_records = 0
        entities_with_calls = 0

        for entity in entities:
            records = entity.get("records", [])
            total_records += len(records)

            entity_call_records = [r for r in records if r.get("CALL_ID") or r.get("CALL_START_TIME")]
            if entity_call_records:
                entities_with_calls += 1
                call_records += len(entity_call_records)
                print(f"  ✅ Entity {entity['id']}: {len(entity_call_records)} call records")
                for record in entity_call_records[:1]:  # Show first call record
                    print(f"    CALL_ID: {record.get('CALL_ID')}")
                    print(f"    CALL_START_TIME: {record.get('CALL_START_TIME')}")
                    print(f"    PHONE_NUMBER: {record.get('PHONE_NUMBER')}")
                    print(f"    EMAIL: {record.get('EMAIL')}")

        print(f"\n📈 SUMMARY:")
        print(f"  Total entities sampled: {len(entities)}")
        print(f"  Total records: {total_records}")
        print(f"  Entities with call data: {entities_with_calls}")
        print(f"  Total call records: {call_records}")

        if call_records == 0:
            print("❌ NO CALL DATA FOUND ANYWHERE IN THE SYSTEM")
            print("   This suggests call data has not been ingested or is in a different format")
        else:
            print("✅ CALL DATA EXISTS - linkage issue confirmed")

    except Exception as e:
        print(f"❌ Sample search error: {e}")

    print("\n" + "=" * 50)
    print("🎯 SYSTEM-WIDE CALL DATA SEARCH COMPLETE")

if __name__ == "__main__":
    asyncio.run(find_any_call_data())
