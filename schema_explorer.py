#!/usr/bin/env python3
"""
GraphQL Schema Explorer for Tilores API
Comprehensive introspection tool to build complete schema map
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class TiloresSchemaExplorer:
    def __init__(self):
        self.tilores_api_url = os.getenv("TILORES_GRAPHQL_API_URL")
        self.tilores_client_id = os.getenv("TILORES_CLIENT_ID")
        self.tilores_client_secret = os.getenv("TILORES_CLIENT_SECRET")
        self.tilores_token_url = os.getenv("TILORES_OAUTH_TOKEN_URL")

        self.token = None
        self.token_expires_at = None

        # Schema storage
        self.complete_schema = {
            "types": {},
            "queries": {},
            "mutations": {},
            "subscriptions": {},
            "enums": {},
            "interfaces": {},
            "unions": {},
            "scalars": {},
            "introspection_timestamp": None
        }

        print("🔍 Tilores GraphQL Schema Explorer initialized")
        print(f"  - API URL: {'✅ Set' if self.tilores_api_url else '❌ Missing'}")
        print(f"  - Client ID: {'✅ Set' if self.tilores_client_id else '❌ Missing'}")
        print(f"  - Client Secret: {'✅ Set' if self.tilores_client_secret else '❌ Missing'}")
        print(f"  - Token URL: {'✅ Set' if self.tilores_token_url else '❌ Missing'}")

    def get_token(self) -> str:
        """Get or refresh OAuth token"""
        if self.token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.token

        print("🔑 Getting OAuth token...")

        token_data = {
            "grant_type": "client_credentials",
            "client_id": self.tilores_client_id,
            "client_secret": self.tilores_client_secret
        }

        try:
            response = requests.post(self.tilores_token_url, data=token_data, timeout=30)
            response.raise_for_status()

            token_response = response.json()
            self.token = token_response["access_token"]
            expires_in = token_response.get("expires_in", 3600)
            self.token_expires_at = datetime.now().timestamp() + expires_in - 60  # 1 minute buffer

            print("✅ OAuth token obtained successfully")
            return self.token

        except Exception as e:
            print(f"❌ Failed to get OAuth token: {e}")
            raise

    def execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute GraphQL query"""
        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json"
        }

        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            response = requests.post(
                self.tilores_api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            raise

    def introspect_schema_root(self) -> Dict[str, Any]:
        """Get root schema information"""
        print("🔍 Introspecting root schema...")

        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType { name }
                mutationType { name }
                subscriptionType { name }
                types {
                    ...FullType
                }
                directives {
                    name
                    description
                    locations
                    args {
                        ...InputValue
                    }
                }
            }
        }

        fragment FullType on __Type {
            kind
            name
            description
            fields(includeDeprecated: true) {
                name
                description
                args {
                    ...InputValue
                }
                type {
                    ...TypeRef
                }
                isDeprecated
                deprecationReason
            }
            inputFields {
                ...InputValue
            }
            interfaces {
                ...TypeRef
            }
            enumValues(includeDeprecated: true) {
                name
                description
                isDeprecated
                deprecationReason
            }
            possibleTypes {
                ...TypeRef
            }
        }

        fragment InputValue on __InputValue {
            name
            description
            type { ...TypeRef }
            defaultValue
        }

        fragment TypeRef on __Type {
            kind
            name
            ofType {
                kind
                name
                ofType {
                    kind
                    name
                    ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                            ofType {
                                kind
                                name
                                ofType {
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
            }
        }
        """

        result = self.execute_query(introspection_query)

        if "errors" in result:
            print(f"❌ Introspection errors: {result['errors']}")
            return {}

        return result.get("data", {}).get("__schema", {})

    def process_schema_types(self, schema_data: Dict[str, Any]):
        """Process and categorize all schema types"""
        print("📊 Processing schema types...")

        types = schema_data.get("types", [])

        for type_info in types:
            type_name = type_info.get("name", "")
            type_kind = type_info.get("kind", "")

            # Skip introspection types
            if type_name.startswith("__"):
                continue

            print(f"  📝 Processing {type_kind}: {type_name}")

            if type_kind == "OBJECT":
                self.complete_schema["types"][type_name] = {
                    "kind": type_kind,
                    "description": type_info.get("description"),
                    "fields": self.process_fields(type_info.get("fields", [])),
                    "interfaces": self.process_type_refs(type_info.get("interfaces", []))
                }

            elif type_kind == "ENUM":
                self.complete_schema["enums"][type_name] = {
                    "kind": type_kind,
                    "description": type_info.get("description"),
                    "values": [
                        {
                            "name": enum_val.get("name"),
                            "description": enum_val.get("description"),
                            "isDeprecated": enum_val.get("isDeprecated", False)
                        }
                        for enum_val in type_info.get("enumValues", [])
                    ]
                }

            elif type_kind == "INTERFACE":
                self.complete_schema["interfaces"][type_name] = {
                    "kind": type_kind,
                    "description": type_info.get("description"),
                    "fields": self.process_fields(type_info.get("fields", [])),
                    "possibleTypes": self.process_type_refs(type_info.get("possibleTypes", []))
                }

            elif type_kind == "UNION":
                self.complete_schema["unions"][type_name] = {
                    "kind": type_kind,
                    "description": type_info.get("description"),
                    "possibleTypes": self.process_type_refs(type_info.get("possibleTypes", []))
                }

            elif type_kind == "SCALAR":
                self.complete_schema["scalars"][type_name] = {
                    "kind": type_kind,
                    "description": type_info.get("description")
                }

            elif type_kind == "INPUT_OBJECT":
                self.complete_schema["types"][type_name] = {
                    "kind": type_kind,
                    "description": type_info.get("description"),
                    "inputFields": self.process_input_fields(type_info.get("inputFields", []))
                }

    def process_fields(self, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process field definitions"""
        processed_fields = []

        for field in fields:
            processed_field = {
                "name": field.get("name"),
                "description": field.get("description"),
                "type": self.process_type_ref(field.get("type", {})),
                "args": self.process_input_fields(field.get("args", [])),
                "isDeprecated": field.get("isDeprecated", False)
            }

            if field.get("deprecationReason"):
                processed_field["deprecationReason"] = field.get("deprecationReason")

            processed_fields.append(processed_field)

        return processed_fields

    def process_input_fields(self, input_fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process input field definitions"""
        processed_fields = []

        for field in input_fields:
            processed_field = {
                "name": field.get("name"),
                "description": field.get("description"),
                "type": self.process_type_ref(field.get("type", {})),
                "defaultValue": field.get("defaultValue")
            }
            processed_fields.append(processed_field)

        return processed_fields

    def process_type_ref(self, type_ref: Dict[str, Any]) -> Dict[str, Any]:
        """Process type reference recursively"""
        if not type_ref:
            return {}

        processed_type = {
            "kind": type_ref.get("kind"),
            "name": type_ref.get("name")
        }

        if type_ref.get("ofType"):
            processed_type["ofType"] = self.process_type_ref(type_ref["ofType"])

        return processed_type

    def process_type_refs(self, type_refs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process list of type references"""
        return [self.process_type_ref(type_ref) for type_ref in type_refs]

    def identify_root_operations(self, schema_data: Dict[str, Any]):
        """Identify root query, mutation, and subscription types"""
        print("🎯 Identifying root operations...")

        query_type = schema_data.get("queryType", {})
        mutation_type = schema_data.get("mutationType", {})
        subscription_type = schema_data.get("subscriptionType")

        query_type_name = query_type.get("name") if query_type else None
        mutation_type_name = mutation_type.get("name") if mutation_type else None
        subscription_type_name = subscription_type.get("name") if subscription_type else None

        print(f"  📥 Query Type: {query_type_name}")
        print(f"  📤 Mutation Type: {mutation_type_name}")
        print(f"  📡 Subscription Type: {subscription_type_name}")

        # Extract operations from the types
        if query_type_name and query_type_name in self.complete_schema["types"]:
            self.complete_schema["queries"] = self.complete_schema["types"][query_type_name]["fields"]

        if mutation_type_name and mutation_type_name in self.complete_schema["types"]:
            self.complete_schema["mutations"] = self.complete_schema["types"][mutation_type_name]["fields"]

        if subscription_type_name and subscription_type_name in self.complete_schema["types"]:
            self.complete_schema["subscriptions"] = self.complete_schema["types"][subscription_type_name]["fields"]

    def explore_entity_structure(self):
        """Deep dive into Entity structure specifically"""
        print("🏗️ Exploring Entity structure in detail...")

        entity_query = """
        query ExploreEntityStructure {
            __type(name: "Entity") {
                name
                kind
                description
                fields {
                    name
                    description
                    type {
                        name
                        kind
                        ofType {
                            name
                            kind
                            ofType {
                                name
                                kind
                            }
                        }
                    }
                }
            }
        }
        """

        try:
            result = self.execute_query(entity_query)
            entity_type = result.get("data", {}).get("__type", {})

            if entity_type:
                print(f"  📋 Entity Type Details:")
                print(f"    - Name: {entity_type.get('name')}")
                print(f"    - Kind: {entity_type.get('kind')}")
                print(f"    - Description: {entity_type.get('description', 'No description')}")

                fields = entity_type.get("fields", [])
                print(f"    - Fields ({len(fields)}):")

                for field in fields:
                    field_name = field.get("name")
                    field_type = self.get_type_string(field.get("type", {}))
                    field_desc = field.get("description", "No description")
                    print(f"      • {field_name}: {field_type} - {field_desc}")

        except Exception as e:
            print(f"❌ Error exploring Entity structure: {e}")

    def get_type_string(self, type_info: Dict[str, Any]) -> str:
        """Convert type info to readable string"""
        if not type_info:
            return "Unknown"

        kind = type_info.get("kind")
        name = type_info.get("name")
        of_type = type_info.get("ofType")

        if kind == "NON_NULL":
            return f"{self.get_type_string(of_type)}!"
        elif kind == "LIST":
            return f"[{self.get_type_string(of_type)}]"
        elif name:
            return name
        else:
            return "Unknown"

    def save_schema_map(self, filename: str = "tilores_graphql_schema.json"):
        """Save complete schema map to file"""
        print(f"💾 Saving schema map to {filename}...")

        self.complete_schema["introspection_timestamp"] = datetime.now().isoformat()

        # Add summary statistics
        self.complete_schema["summary"] = {
            "total_types": len(self.complete_schema["types"]),
            "total_queries": len(self.complete_schema["queries"]),
            "total_mutations": len(self.complete_schema["mutations"]),
            "total_subscriptions": len(self.complete_schema["subscriptions"]),
            "total_enums": len(self.complete_schema["enums"]),
            "total_interfaces": len(self.complete_schema["interfaces"]),
            "total_unions": len(self.complete_schema["unions"]),
            "total_scalars": len(self.complete_schema["scalars"])
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.complete_schema, f, indent=2, ensure_ascii=False)

        print(f"✅ Schema map saved successfully!")
        print(f"📊 Summary:")
        for key, value in self.complete_schema["summary"].items():
            print(f"  - {key.replace('_', ' ').title()}: {value}")

    def run_complete_exploration(self):
        """Run complete schema exploration"""
        print("🚀 Starting complete GraphQL schema exploration...")

        try:
            # Step 1: Get root schema
            schema_data = self.introspect_schema_root()

            if not schema_data:
                print("❌ Failed to get schema data")
                return

            # Step 2: Process all types
            self.process_schema_types(schema_data)

            # Step 3: Identify root operations
            self.identify_root_operations(schema_data)

            # Step 4: Deep dive into Entity structure
            self.explore_entity_structure()

            # Step 5: Save complete schema
            self.save_schema_map()

            print("🎉 Schema exploration completed successfully!")

        except Exception as e:
            print(f"❌ Schema exploration failed: {e}")
            raise

if __name__ == "__main__":
    explorer = TiloresSchemaExplorer()
    explorer.run_complete_exploration()
