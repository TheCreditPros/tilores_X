#!/usr/bin/env python3
"""
Schema discovery script to find actual phone call field names
and avoid 422 errors by only querying fields that exist.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Tilores API configuration
TILORES_GRAPHQL_API_URL = os.getenv("TILORES_GRAPHQL_API_URL")
TILORES_OAUTH_TOKEN_URL = os.getenv("TILORES_OAUTH_TOKEN_URL")
TILORES_CLIENT_ID = os.getenv("TILORES_CLIENT_ID")
TILORES_CLIENT_SECRET = os.getenv("TILORES_CLIENT_SECRET")

def get_tilores_token():
    """Get OAuth2 token from Tilores"""
    try:
        response = requests.post(
            TILORES_OAUTH_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": TILORES_CLIENT_ID,
                "client_secret": TILORES_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"❌ Token error: {e}")
        return None

def introspect_schema(token):
    """Introspect the GraphQL schema to get all field names"""
    query = """
    query IntrospectSchema {
      __schema {
        types {
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
    }
    """

    try:
        response = requests.post(
            TILORES_GRAPHQL_API_URL,
            json={"query": query},
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Schema introspection error: {e}")
        return None

def get_record_fields(schema_data):
    """Extract field names from the Record type"""
    if not schema_data or "data" not in schema_data:
        return []

    for type_info in schema_data["data"]["__schema"]["types"]:
        if type_info["name"] == "Record":
            return [field["name"] for field in type_info["fields"]]

    return []

def _normalize(s: str) -> str:
    """Strip non-alnum and collapse case to improve fuzzy matching"""
    import re
    return re.sub(r"[^a-z0-9]", "", s.lower())

def discover_call_field_map(all_fields: list) -> dict:
    """
    all_fields is a list of field names from the Record type
    Returns a map of canonical keys -> actual field names present in the schema.
    """
    # Build lookup of normalized->actual
    norm_lookup = {_normalize(name): name for name in all_fields}

    candidates = {
        "phone_number": ["PHONE_NUMBER", "PHONE", "PHONE_EXTERNAL", "HODU_PHONE_NUMBER"],
        "agent_username": ["AGENT_USERNAME", "AGENT"],
        "call_duration": ["CALL_DURATION", "DURATION", "HODU_CALL_DURATION"],
        "call_hangup_time": ["CALL_HANGUP_TIME", "END_TIME", "HANGUP_TIME"],
        "call_id": ["CALL_ID", "HODU_CALL_ID"],
        "call_start_time": ["CALL_START_TIME", "START_TIME", "HODU_CALL_START_TIME"],
        "call_type": ["CALL_TYPE", "TYPE"],
        "campaign_name": ["CAMPAIGN_NAME", "CAMPAIGN"],
    }

    resolved = {}
    for canon, options in candidates.items():
        for opt in options:
            n = _normalize(opt)
            if n in norm_lookup:
                resolved[canon] = norm_lookup[n]
                break
    return resolved

def find_phone_related_fields(all_fields: list) -> list:
    """Find all fields that might be phone/call related"""
    phone_keywords = ["phone", "call", "agent", "campaign", "duration", "hangup", "start", "end"]
    phone_fields = []

    for field in all_fields:
        field_lower = field.lower()
        if any(keyword in field_lower for keyword in phone_keywords):
            phone_fields.append(field)

    return sorted(phone_fields)

def main():
    print("🔍 Discovering phone call field names in Tilores schema...")

    # Get token
    token = get_tilores_token()
    if not token:
        print("❌ Failed to get token")
        return

    print("✅ Got Tilores token")

    # Introspect schema
    schema_data = introspect_schema(token)
    if not schema_data:
        print("❌ Failed to introspect schema")
        return

    print("✅ Schema introspection successful")

    # Get Record fields
    record_fields = get_record_fields(schema_data)
    print(f"📊 Found {len(record_fields)} fields on Record type")

    # Find phone-related fields
    phone_fields = find_phone_related_fields(record_fields)
    print(f"📞 Found {len(phone_fields)} phone/call related fields:")
    for field in phone_fields:
        print(f"  - {field}")

    # Discover call field mapping
    field_map = discover_call_field_map(record_fields)
    print(f"\n🎯 Discovered call field mapping:")
    for canon, actual in field_map.items():
        print(f"  {canon} -> {actual}")

    if not field_map:
        print("⚠️  No call fields found on Record type - may need to check edges")

    # Save results
    results = {
        "record_fields": record_fields,
        "phone_fields": phone_fields,
        "call_field_map": field_map,
        "total_fields": len(record_fields)
    }

    with open("phone_field_discovery_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to phone_field_discovery_results.json")

    return results

if __name__ == "__main__":
    main()
