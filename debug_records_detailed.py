#!/usr/bin/env python3
"""
Debug script to examine individual records in detail
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

def test_record_query(record_id):
    """Test GraphQL query for specific record"""
    token = get_tilores_token()
    if not token:
        return None

    query = """
    query($id:ID!){
      entityByRecord(input:{id:$id}){
        entity{
          records {
            id
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              Report_ID
              CREDIT_SCORE {
                Value
                ModelNameType
                CreditRepositorySourceType
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
            json={"query": query, "variables": {"id": record_id}},
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

        return result.get("data", {}).get("entityByRecord", {}).get("entity", {}).get("records", [])

    except Exception as e:
        print(f"Query failed: {e}")
        return None

def main():
    """Main debug function"""
    print("🔍 DEBUGGING INDIVIDUAL RECORDS")
    print("=" * 40)

    # First, let's get all record IDs for Esteban Price
    entity_id = "dc93a2cd-de0a-444f-ad47-3003ba998cd3"

    search_query = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          records {
            id
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
            }
          }
        }
      }
    }
    """

    token = get_tilores_token()
    if not token:
        print("❌ Failed to get token")
        return

    try:
        response = requests.post(
            os.getenv("TILORES_GRAPHQL_API_URL"),
            json={"query": search_query, "variables": {"id": entity_id}},
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
            return

        records = result.get("data", {}).get("entity", {}).get("entity", {}).get("records", [])
        print(f"Found {len(records)} records")

        # Test each record individually
        for i, record in enumerate(records):
            record_id = record.get("id")
            print(f"\n📋 Record {i+1}: {record_id}")

            # Get detailed info for this record
            detailed_records = test_record_query(record_id)
            if detailed_records:
                for detailed_record in detailed_records:
                    credit_response = detailed_record.get("CREDIT_RESPONSE", {})
                    if credit_response:
                        bureau = credit_response.get("CREDIT_BUREAU", "Unknown")
                        date = credit_response.get("CreditReportFirstIssuedDate", "Unknown")
                        print(f"  Bureau: {bureau}, Date: {date}")

                        scores = credit_response.get("CREDIT_SCORE", [])
                        for score in scores:
                            print(f"    Score: {score.get('Value')}, Model: {score.get('ModelNameType')}")
                    else:
                        print("  No credit response data")
            else:
                print("  Failed to get detailed record data")

    except Exception as e:
        print(f"Query failed: {e}")

if __name__ == "__main__":
    main()
