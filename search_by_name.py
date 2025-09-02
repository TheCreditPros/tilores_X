#!/usr/bin/env python3
"""
Search for entities by name to find multi-bureau data
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_tilores_token():
    """Get Tilores OAuth token"""
    try:
        response = requests.post(
            os.getenv("TILORES_OAUTH_TOKEN_URL"),
            data={
                "grant_type": "client_credentials",
                "client_id": os.getenv("TILORES_CLIENT_ID"),
                "client_secret": os.getenv("TILORES_CLIENT_SECRET"),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        response.raise_for_status()

        token_data = response.json()
        return token_data["access_token"]
    except Exception as e:
        print(f"Failed to get token: {e}")
        return None

def search_by_name():
    """Search for entities by name"""
    token = get_tilores_token()
    if not token:
        return []

    # Search by first name
    search_query = """
    query {
      search(input: { parameters: { FIRST_NAME: "Esteban" } }) {
        entities {
          id
          hits
          records {
            id
          }
        }
      }
    }
    """

    try:
        response = requests.post(
            os.getenv("TILORES_GRAPHQL_API_URL"),
            json={"query": search_query},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        if "errors" in result:
            print(f"Search errors: {result['errors']}")
            return []

        return result.get("data", {}).get("search", {}).get("entities", [])

    except Exception as e:
        print(f"Search failed: {e}")
        return []

def search_by_last_name():
    """Search for entities by last name"""
    token = get_tilores_token()
    if not token:
        return []

    # Search by last name
    search_query = """
    query {
      search(input: { parameters: { LAST_NAME: "Price" } }) {
        entities {
          id
          hits
          records {
            id
          }
        }
      }
    }
    """

    try:
        response = requests.post(
            os.getenv("TILORES_GRAPHQL_API_URL"),
            json={"query": search_query},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        if "errors" in result:
            print(f"Search errors: {result['errors']}")
            return []

        return result.get("data", {}).get("search", {}).get("entities", [])

    except Exception as e:
        print(f"Search failed: {e}")
        return []

def test_entity_for_bureaus(entity_id):
    """Test an entity to see what bureaus it has"""
    token = get_tilores_token()
    if not token:
        return set()

    query = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              CREDIT_SCORE {
                Value
                ModelNameType
              }
            }
          }
        }
      }
    }
    """

    try:
        response = requests.post(
            os.getenv("TILORES_GRAPHQL_API_URL"),
            json={"query": query, "variables": {"id": entity_id}},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        if "errors" in result:
            return set()

        records = result.get("data", {}).get("entity", {}).get("entity", {}).get("records", [])
        bureaus = set()

        for record in records:
            credit_response = record.get("CREDIT_RESPONSE", {})
            if credit_response:
                bureau = credit_response.get("CREDIT_BUREAU", "Unknown")
                if bureau != "Unknown":
                    bureaus.add(bureau)

        return bureaus

    except Exception as e:
        return set()

def main():
    """Main function to search by name"""
    print("🔍 SEARCHING BY NAME FOR MULTI-BUREAU DATA")
    print("=" * 50)

    # Search by first name
    print("\n📋 Searching by FIRST_NAME: Esteban")
    entities_first = search_by_name()
    print(f"Found {len(entities_first)} entities")

    # Search by last name
    print("\n📋 Searching by LAST_NAME: Price")
    entities_last = search_by_last_name()
    print(f"Found {len(entities_last)} entities")

    # Combine and deduplicate
    all_entities = {}
    for entity in entities_first + entities_last:
        entity_id = entity.get("id")
        if entity_id not in all_entities:
            all_entities[entity_id] = entity

    print(f"\n📊 Total unique entities: {len(all_entities)}")

    # Test each entity for bureau data
    multi_bureau_entities = []
    for entity_id, entity in all_entities.items():
        record_count = len(entity.get("records", []))
        print(f"\n📋 Entity: {entity_id}")
        print(f"   Records: {record_count}")

        bureaus = test_entity_for_bureaus(entity_id)
        print(f"   Bureaus: {bureaus}")

        if len(bureaus) > 1:
            print(f"   ✅ MULTI-BUREAU ENTITY!")
            multi_bureau_entities.append((entity_id, bureaus))
        elif "Equifax" in bureaus and "TransUnion" in bureaus and "Experian" in bureaus:
            print(f"   ✅ ALL THREE BUREAUS!")
            multi_bureau_entities.append((entity_id, bureaus))

    if multi_bureau_entities:
        print(f"\n🎯 FOUND {len(multi_bureau_entities)} MULTI-BUREAU ENTITIES:")
        for entity_id, bureaus in multi_bureau_entities:
            print(f"   - {entity_id}: {', '.join(bureaus)}")
    else:
        print("\n❌ No multi-bureau entities found")
        print("This suggests the data structure might be different than expected")

if __name__ == "__main__":
    main()
