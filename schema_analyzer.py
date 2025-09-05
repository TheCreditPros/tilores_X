#!/usr/bin/env python3
"""
GraphQL Schema Analyzer for Tilores API
Analyzes the complete schema and creates useful documentation
"""

import json
from typing import Dict, List, Any
from collections import defaultdict

class TiloresSchemaAnalyzer:
    def __init__(self, schema_file: str = "tilores_graphql_schema.json"):
        with open(schema_file, 'r') as f:
            self.schema = json.load(f)

        print(f"📊 Loaded schema with {len(self.schema['types'])} types")

    def analyze_entity_structure(self):
        """Deep analysis of Entity structure"""
        print("\n🏗️ ENTITY STRUCTURE ANALYSIS")
        print("=" * 50)

        entity = self.schema["types"].get("Entity", {})
        if not entity:
            print("❌ Entity type not found")
            return

        print(f"Entity Type: {entity['kind']}")
        print(f"Description: {entity.get('description', 'No description')}")
        print(f"Fields ({len(entity['fields'])}):")

        for field in entity["fields"]:
            field_name = field["name"]
            field_type = self.get_type_string(field["type"])
            field_desc = field.get("description", "No description")

            print(f"  • {field_name}: {field_type}")
            if field_desc != "No description":
                print(f"    └─ {field_desc}")

            # Show args if any
            if field.get("args"):
                print(f"    └─ Args: {len(field['args'])}")
                for arg in field["args"]:
                    arg_name = arg["name"]
                    arg_type = self.get_type_string(arg["type"])
                    print(f"      • {arg_name}: {arg_type}")

    def analyze_record_structure(self):
        """Deep analysis of Record structure"""
        print("\n📝 RECORD STRUCTURE ANALYSIS")
        print("=" * 50)

        record = self.schema["types"].get("Record", {})
        if not record:
            print("❌ Record type not found")
            return

        print(f"Record Type: {record['kind']}")
        print(f"Description: {record.get('description', 'No description')}")
        print(f"Fields ({len(record['fields'])}):")

        for field in record["fields"]:
            field_name = field["name"]
            field_type = self.get_type_string(field["type"])
            field_desc = field.get("description", "No description")

            print(f"  • {field_name}: {field_type}")
            if field_desc != "No description":
                print(f"    └─ {field_desc}")

    def analyze_credit_response_structure(self):
        """Deep analysis of CreditResponse structure"""
        print("\n💳 CREDIT RESPONSE STRUCTURE ANALYSIS")
        print("=" * 50)

        credit_response = self.schema["types"].get("CreditResponse", {})
        if not credit_response:
            print("❌ CreditResponse type not found")
            return

        print(f"CreditResponse Type: {credit_response['kind']}")
        print(f"Description: {credit_response.get('description', 'No description')}")
        print(f"Fields ({len(credit_response['fields'])}):")

        for field in credit_response["fields"]:
            field_name = field["name"]
            field_type = self.get_type_string(field["type"])
            field_desc = field.get("description", "No description")

            print(f"  • {field_name}: {field_type}")
            if field_desc != "No description":
                print(f"    └─ {field_desc}")

    def analyze_queries(self):
        """Analyze available queries"""
        print("\n🔍 AVAILABLE QUERIES")
        print("=" * 50)

        queries = self.schema.get("queries", [])
        print(f"Total Queries: {len(queries)}")

        for query in queries:
            query_name = query["name"]
            query_type = self.get_type_string(query["type"])
            query_desc = query.get("description", "No description")

            print(f"\n📥 {query_name}: {query_type}")
            if query_desc != "No description":
                print(f"   └─ {query_desc}")

            # Show arguments
            args = query.get("args", [])
            if args:
                print(f"   └─ Arguments ({len(args)}):")
                for arg in args:
                    arg_name = arg["name"]
                    arg_type = self.get_type_string(arg["type"])
                    arg_desc = arg.get("description", "")
                    default_val = arg.get("defaultValue")

                    print(f"      • {arg_name}: {arg_type}")
                    if arg_desc:
                        print(f"        └─ {arg_desc}")
                    if default_val:
                        print(f"        └─ Default: {default_val}")

    def analyze_mutations(self):
        """Analyze available mutations"""
        print("\n🔄 AVAILABLE MUTATIONS")
        print("=" * 50)

        mutations = self.schema.get("mutations", [])
        print(f"Total Mutations: {len(mutations)}")

        for mutation in mutations:
            mutation_name = mutation["name"]
            mutation_type = self.get_type_string(mutation["type"])
            mutation_desc = mutation.get("description", "No description")

            print(f"\n📤 {mutation_name}: {mutation_type}")
            if mutation_desc != "No description":
                print(f"   └─ {mutation_desc}")

            # Show arguments
            args = mutation.get("args", [])
            if args:
                print(f"   └─ Arguments ({len(args)}):")
                for arg in args:
                    arg_name = arg["name"]
                    arg_type = self.get_type_string(arg["type"])
                    arg_desc = arg.get("description", "")

                    print(f"      • {arg_name}: {arg_type}")
                    if arg_desc:
                        print(f"        └─ {arg_desc}")

    def analyze_credit_types(self):
        """Analyze all credit-related types"""
        print("\n💳 CREDIT-RELATED TYPES")
        print("=" * 50)

        credit_types = {name: info for name, info in self.schema["types"].items()
                       if "credit" in name.lower()}

        print(f"Found {len(credit_types)} credit-related types:")

        for type_name, type_info in credit_types.items():
            print(f"\n📋 {type_name} ({type_info['kind']})")
            if type_info.get("description"):
                print(f"   └─ {type_info['description']}")

            # Show key fields for OBJECT types
            if type_info["kind"] == "OBJECT" and type_info.get("fields"):
                key_fields = [f["name"] for f in type_info["fields"][:5]]  # First 5 fields
                if len(type_info["fields"]) > 5:
                    key_fields.append(f"... and {len(type_info['fields']) - 5} more")
                print(f"   └─ Fields: {', '.join(key_fields)}")

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

    def create_field_reference(self):
        """Create a comprehensive field reference"""
        print("\n📚 COMPREHENSIVE FIELD REFERENCE")
        print("=" * 50)

        # Focus on key types
        key_types = ["Entity", "Record", "CreditResponse", "RecordInsights"]

        for type_name in key_types:
            type_info = self.schema["types"].get(type_name)
            if not type_info:
                continue

            print(f"\n🔸 {type_name}")
            print("-" * 30)

            fields = type_info.get("fields", [])
            for field in fields:
                field_name = field["name"]
                field_type = self.get_type_string(field["type"])
                print(f"  {field_name}: {field_type}")

    def generate_sample_queries(self):
        """Generate sample GraphQL queries based on schema"""
        print("\n📝 SAMPLE GRAPHQL QUERIES")
        print("=" * 50)

        # Entity query
        print("\n1. Basic Entity Query:")
        print("```graphql")
        print("query GetEntity($id: ID!) {")
        print("  entity(input: { id: $id }) {")
        print("    entity {")
        print("      id")

        entity = self.schema["types"].get("Entity", {})
        if entity and entity.get("fields"):
            # Show first 10 fields as example
            for field in entity["fields"][:10]:
                field_name = field["name"]
                if field_name != "id":  # Skip id as we already have it
                    print(f"      {field_name}")

        print("    }")
        print("  }")
        print("}")
        print("```")

        # Record query with credit data
        print("\n2. Entity with Records and Credit Data:")
        print("```graphql")
        print("query GetEntityWithCreditData($id: ID!) {")
        print("  entity(input: { id: $id }) {")
        print("    entity {")
        print("      id")
        print("      records {")
        print("        id")
        print("        # Basic customer fields")
        print("        STATUS")
        print("        FIRST_NAME")
        print("        LAST_NAME")
        print("        EMAIL")
        print("        CLIENT_ID")
        print("        PRODUCT_NAME")
        print("        CURRENT_PRODUCT")
        print("        ENROLL_DATE")
        print("        ")
        print("        # Credit response data")
        print("        CREDIT_RESPONSE {")

        credit_response = self.schema["types"].get("CreditResponse", {})
        if credit_response and credit_response.get("fields"):
            # Show key credit fields
            key_credit_fields = ["CREDIT_BUREAU", "CreditReportFirstIssuedDate"]
            for field in credit_response["fields"]:
                field_name = field["name"]
                if field_name in key_credit_fields:
                    print(f"          {field_name}")

        print("          CREDIT_SCORE {")
        print("            Value")
        print("            ModelNameType")
        print("            CreditRepositorySourceType")
        print("          }")
        print("          CREDIT_LIABILITY {")
        print("            AccountType")
        print("            CreditLimitAmount")
        print("            CreditBalance")
        print("          }")
        print("        }")
        print("      }")
        print("    }")
        print("  }")
        print("}")
        print("```")

    def run_complete_analysis(self):
        """Run complete schema analysis"""
        print("🚀 TILORES GRAPHQL SCHEMA ANALYSIS")
        print("=" * 60)

        # Basic stats
        print(f"📊 Schema Statistics:")
        print(f"  - Types: {len(self.schema['types'])}")
        print(f"  - Queries: {len(self.schema.get('queries', []))}")
        print(f"  - Mutations: {len(self.schema.get('mutations', []))}")
        print(f"  - Enums: {len(self.schema.get('enums', {}))}")
        print(f"  - Scalars: {len(self.schema.get('scalars', {}))}")

        # Detailed analysis
        self.analyze_queries()
        self.analyze_mutations()
        self.analyze_entity_structure()
        self.analyze_record_structure()
        self.analyze_credit_response_structure()
        self.analyze_credit_types()
        self.create_field_reference()
        self.generate_sample_queries()

        print("\n✅ Schema analysis completed!")

if __name__ == "__main__":
    analyzer = TiloresSchemaAnalyzer()
    analyzer.run_complete_analysis()
