#!/usr/bin/env python3
"""
Test script to find the correct phone call field names
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Tilores API configuration
TILORES_API_URL = os.getenv("TILORES_GRAPHQL_API_URL")
TILORES_CLIENT_ID = os.getenv("TILORES_CLIENT_ID")
TILORES_CLIENT_SECRET = os.getenv("TILORES_CLIENT_SECRET")
TILORES_TOKEN_URL = os.getenv("TILORES_OAUTH_TOKEN_URL")

def get_tilores_token():
    """Get fresh Tilores API token"""
    try:
        response = requests.post(TILORES_TOKEN_URL, data={
            'grant_type': 'client_credentials',
            'client_id': TILORES_CLIENT_ID,
            'client_secret': TILORES_CLIENT_SECRET
        })
        response.raise_for_status()
        token_data = response.json()
        return token_data['access_token']
    except Exception as e:
        print(f"Failed to get token: {e}")
        return None

def query_tilores(query, variables=None):
    """Execute GraphQL query against Tilores API"""
    token = get_tilores_token()
    if not token:
        return None

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    payload = {
        'query': query,
        'variables': variables or {}
    }

    try:
        response = requests.post(TILORES_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Query failed: {e}")
        return None

def test_phone_fields():
    """Test different phone call field names"""

    # Known entity ID for Esteban Price
    entity_id = "dc93a2cd-de0a-444f-ad47-3003ba998cd3"

    # Test 1: Try the user's suggested query structure
    print("🔍 Testing user's suggested query structure...")

    query1 = """
    query CallsForEntityByRecord($id: ID!) {
      entityByRecord(input: { id: $id }) {
        entity {
          id
          records {
            id
            PHONE_NUMBER
            AGENT_USERNAME
            CALL_DURATION
            CALL_HANGUP_TIME
            CALL_ID
            CALL_START_TIME
            CALL_TYPE
            CAMPAIGN_NAME
          }
        }
      }
    }
    """

    # First, get a record ID
    search_query = """
    query SearchByEmail {
      search(input: { parameters: { EMAIL: "e.j.price1986@gmail.com" } }) {
        entities {
          id
          records {
            id
          }
        }
      }
    }
    """

    search_result = query_tilores(search_query)
    if search_result and search_result.get("data", {}).get("search", {}).get("entities"):
        entities = search_result["data"]["search"]["entities"]
        if entities and entities[0].get("records"):
            record_id = entities[0]["records"][0]["id"]
            print(f"✅ Found record ID: {record_id}")

            # Now test the phone call query
            result1 = query_tilores(query1, {"id": record_id})
            if result1:
                print("✅ Query 1 successful!")
                print(f"Result: {result1}")
            else:
                print("❌ Query 1 failed")
        else:
            print("❌ No records found in search")
    else:
        print("❌ Search query failed")

    # Test 2: Try entity-based query
    print("\n🔍 Testing entity-based query...")

    query2 = """
    query CallsByEntity($id: ID!) {
      entity(input: { id: $id }) {
        entity {
          id
          records {
            id
            PHONE_NUMBER
            AGENT_USERNAME
            CALL_DURATION
            CALL_HANGUP_TIME
            CALL_ID
            CALL_START_TIME
            CALL_TYPE
            CAMPAIGN_NAME
          }
        }
      }
    }
    """

    result2 = query_tilores(query2, {"id": entity_id})
    if result2:
        print("✅ Query 2 successful!")
        print(f"Result: {result2}")
    else:
        print("❌ Query 2 failed")

    # Test 3: Try with different field names
    print("\n🔍 Testing with different field names...")

    query3 = """
    query TestFields($id: ID!) {
      entity(input: { id: $id }) {
        entity {
          id
          records {
            id
            EMAIL
            FIRST_NAME
            LAST_NAME
            CLIENT_ID
            PHONE_EXTERNAL
            # Try some variations
            PHONE
            CALL_DATE
            CALL_TIME
            AGENT
            CAMPAIGN
          }
        }
      }
    }
    """

    result3 = query_tilores(query3, {"id": entity_id})
    if result3:
        print("✅ Query 3 successful!")
        print(f"Result: {result3}")
    else:
        print("❌ Query 3 failed")

if __name__ == "__main__":
    print("🚀 TESTING PHONE CALL FIELD NAMES")
    print("=" * 50)
    test_phone_fields()
