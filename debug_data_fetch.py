#!/usr/bin/env python3
"""
Debug script to test data fetching and identify the issue
"""

import os
import json
import requests
from datetime import datetime, timedelta
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

def test_entity_query(entity_id):
    """Test GraphQL query for specific entity"""
    token = get_tilores_token()
    if not token:
        return None

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
            print(f"GraphQL errors: {result['errors']}")
            return None

        return result.get("data", {}).get("entity", {}).get("entity", {}).get("records", [])

    except Exception as e:
        print(f"Query failed: {e}")
        return None

def analyze_records(records):
    """Analyze the records to see what data we have"""
    if not records:
        print("No records found")
        return

    print(f"Found {len(records)} records")

    bureaus = set()
    for record in records:
        credit_response = record.get("CREDIT_RESPONSE", {})
        if credit_response:
            bureau = credit_response.get("CREDIT_BUREAU", "Unknown")
            bureaus.add(bureau)
            date = credit_response.get("CreditReportFirstIssuedDate", "Unknown")
            print(f"  - Bureau: {bureau}, Date: {date}")

            # Check scores
            scores = credit_response.get("CREDIT_SCORE", [])
            print(f"    Scores: {len(scores)}")
            for score in scores:
                print(f"      - Value: {score.get('Value')}, Model: {score.get('ModelNameType')}")

    print(f"\nTotal bureaus found: {bureaus}")

def main():
    """Main debug function"""
    print("🔍 DEBUGGING DATA FETCH ISSUE")
    print("=" * 40)

    # Test the entity ID we're using
    entity_id = "dc93a2cd-de0a-444f-ad47-3003ba998cd3"
    print(f"Testing entity ID: {entity_id}")

    records = test_entity_query(entity_id)
    if records:
        analyze_records(records)
    else:
        print("❌ Failed to fetch data")

    # Let's also try to search for Esteban Price to see if we can find the right entity
    print("\n🔍 Searching for Esteban Price...")
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

    token = get_tilores_token()
    if token:
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
            else:
                entities = result.get("data", {}).get("search", {}).get("entities", [])
                print(f"Found {len(entities)} entities for Esteban Price")
                for entity in entities:
                    print(f"  Entity ID: {entity.get('id')}")
                    print(f"  Records: {len(entity.get('records', []))}")
        except Exception as e:
            print(f"Search failed: {e}")

if __name__ == "__main__":
    main()
