#!/usr/bin/env python3
"""
Find the correct entity with multi-bureau credit data
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

def search_for_entities():
    """Search for entities with Esteban Price data"""
    token = get_tilores_token()
    if not token:
        return []

    # Search by email
    search_query = """
    query {
      search(input: { parameters: { EMAIL: "e.j.price1986@gmail.com" } }) {
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
            print(f"GraphQL errors for {entity_id}: {result['errors']}")
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
        print(f"Query failed for {entity_id}: {e}")
        return set()

def main():
    """Main function to find multi-bureau entity"""
    print("🔍 FINDING MULTI-BUREAU ENTITY")
    print("=" * 40)

    # Search for entities
    entities = search_for_entities()
    print(f"Found {len(entities)} entities for Esteban Price")

    if not entities:
        print("❌ No entities found")
        return

    # Test each entity for bureau data
    for i, entity in enumerate(entities):
        entity_id = entity.get("id")
        record_count = len(entity.get("records", []))
        print(f"\n📋 Entity {i+1}: {entity_id}")
        print(f"   Records: {record_count}")

        bureaus = test_entity_for_bureaus(entity_id)
        print(f"   Bureaus: {bureaus}")

        if len(bureaus) > 1:
            print(f"   ✅ MULTI-BUREAU ENTITY FOUND!")
            print(f"   🎯 This entity has data from: {', '.join(bureaus)}")

            # Test this entity with a detailed query
            print(f"\n🔍 DETAILED ANALYSIS FOR {entity_id}:")
            test_detailed_entity(entity_id)
            break
    else:
        print("\n❌ No multi-bureau entities found")
        print("All entities only have single bureau data")

def test_detailed_entity(entity_id):
    """Test entity with detailed credit data query"""
    token = get_tilores_token()
    if not token:
        return

    query = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              Report_ID
              CREDIT_SCORE {
                Value
                ModelNameType
                CreditRepositorySourceType
              }
              CREDIT_SUMMARY {
                BorrowerID
                Name
                DATA_SET {
                  ID
                  Name
                  Value
                }
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
            print(f"Detailed query errors: {result['errors']}")
            return

        records = result.get("data", {}).get("entity", {}).get("entity", {}).get("records", [])
        print(f"   📊 Found {len(records)} records with credit data")

        # Analyze by bureau
        bureau_data = {}
        for record in records:
            credit_response = record.get("CREDIT_RESPONSE", {})
            if credit_response:
                bureau = credit_response.get("CREDIT_BUREAU", "Unknown")
                date = credit_response.get("CreditReportFirstIssuedDate", "Unknown")

                if bureau not in bureau_data:
                    bureau_data[bureau] = []

                scores = credit_response.get("CREDIT_SCORE", [])
                for score in scores:
                    bureau_data[bureau].append({
                        "date": date,
                        "value": score.get("Value"),
                        "model": score.get("ModelNameType", "Unknown")
                    })

        # Display results
        for bureau, scores in bureau_data.items():
            print(f"   📈 {bureau}: {len(scores)} scores")
            for score in scores[:3]:  # Show first 3
                print(f"      - {score['date']}: {score['value']} ({score['model']})")

    except Exception as e:
        print(f"Detailed query failed: {e}")

if __name__ == "__main__":
    main()
