#!/usr / bin / env python3
"""
Master Schema Mapper for Tilores GraphQL API
Comprehensive schema introspection and field relationship mapping system
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

@dataclass
class GraphQLField:
    """Represents a GraphQL field with its metadata"""
    name: str
    type_name: str
    type_kind: str
    is_list: bool = False
    is_non_null: bool = False
    description: Optional[str] = None
    nested_type: Optional[str] = None
    enum_values: Optional[List[str]] = None

@dataclass
class GraphQLType:
    """Represents a GraphQL type with its fields and metadata"""
    name: str
    kind: str
    description: Optional[str] = None
    fields: Dict[str, GraphQLField] = None
    input_fields: Dict[str, GraphQLField] = None
    enum_values: List[str] = None
    interfaces: List[str] = None
    possible_types: List[str] = None

    def __post_init__(self):
        if self.fields is None:
            self.fields = {}
        if self.input_fields is None:
            self.input_fields = {}
        if self.enum_values is None:
            self.enum_values = []
        if self.interfaces is None:
            self.interfaces = []
        if self.possible_types is None:
            self.possible_types = []

@dataclass
class SchemaMap:
    """Complete schema mapping with relationships and metadata"""
    types: Dict[str, GraphQLType]
    query_root_fields: Dict[str, GraphQLField]
    mutation_root_fields: Dict[str, GraphQLField]
    subscription_root_fields: Dict[str, GraphQLField]
    field_relationships: Dict[str, List[str]]  # field_name -> [types_that_contain_it]
    type_hierarchy: Dict[str, List[str]]  # parent_type -> [child_types]
    credit_related_types: List[str]
    entity_related_types: List[str]
    record_related_types: List[str]
    total_fields: int
    introspection_timestamp: str

    def __post_init__(self):
        if self.types is None:
            self.types = {}
        if self.query_root_fields is None:
            self.query_root_fields = {}
        if self.mutation_root_fields is None:
            self.mutation_root_fields = {}
        if self.subscription_root_fields is None:
            self.subscription_root_fields = {}
        if self.field_relationships is None:
            self.field_relationships = defaultdict(list)
        if self.type_hierarchy is None:
            self.type_hierarchy = defaultdict(list)

class MasterSchemaMapper:
    """Comprehensive GraphQL schema mapper and analyzer"""

    def __init__(self):
        self.tilores_api = None
        self.schema_map: Optional[SchemaMap] = None
        
    def initialize_api(self):
        """Initialize Tilores API connection"""
        try:
            from tilores import TiloresAPI
            self.tilores_api = TiloresAPI.from_environ()
            print("✅ Tilores API initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Tilores API: {e}")
            return False

    def get_complete_schema_introspection(self) -> Optional[Dict]:
        """Execute comprehensive GraphQL introspection query"""
        
        if not self.tilores_api:
            print("❌ API not initialized")
            return None

        # Comprehensive introspection query covering all GraphQL features
        introspection_query = """
        query CompleteIntrospection {
          __schema {
            queryType { name }
            mutationType { name }
            subscriptionType { name }
            types {
              kind
              name
              description
              fields(includeDeprecated: true) {
                name
                description
                args {
                  name
                  description
                  type {
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
                  defaultValue
                }
                type {
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
                isDeprecated
                deprecationReason
              }
              inputFields {
                name
                description
                type {
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
                defaultValue
              }
              interfaces {
                kind
                name
                ofType {
                  kind
                  name
                }
              }
              enumValues(includeDeprecated: true) {
                name
                description
                isDeprecated
                deprecationReason
              }
              possibleTypes {
                kind
                name
                ofType {
                  kind
                  name
                }
              }
            }
            directives {
              name
              description
              locations
              args {
                name
                description
                type {
                  kind
                  name
                  ofType {
                    kind
                    name
                  }
                }
                defaultValue
              }
            }
          }
        }
        """

        try:
            print("🔍 Executing comprehensive schema introspection...")
            result = self.tilores_api.gql(introspection_query)
            
            if result and 'data' in result and '__schema' in result['data']:
                print("✅ Schema introspection successful!")
                return result['data']['__schema']
            else:
                print(f"❌ Schema introspection failed: {result}")
                return None
                
        except Exception as e:
            print(f"❌ Schema introspection error: {e}")
            return None

    def parse_type_reference(self, type_ref: Dict) -> Tuple[str, str, bool, bool, Optional[str]]:
        """Parse GraphQL type reference to extract type info"""
        if not type_ref:
            return "Unknown", "SCALAR", False, False, None
            
        kind = type_ref.get('kind', 'SCALAR')
        name = type_ref.get('name')
        is_list = False
        is_non_null = False
        nested_type = None
        
        # Handle wrapped types (NON_NULL, LIST)
        current = type_ref
        while current and not name:
            if current.get('kind') == 'NON_NULL':
                is_non_null = True
                current = current.get('ofType')
            elif current.get('kind') == 'LIST':
                is_list = True
                current = current.get('ofType')
            else:
                break
                
        if current:
            name = current.get('name', 'Unknown')
            kind = current.get('kind', 'SCALAR')
            if current.get('ofType'):
                nested_type = current['ofType'].get('name')
        
        return name or "Unknown", kind, is_list, is_non_null, nested_type

    def build_schema_map(self, schema_data: Dict) -> SchemaMap:
        """Build comprehensive schema map from introspection data"""
        
        print("🏗️  Building comprehensive schema map...")
        
        # Initialize schema map
        schema_map = SchemaMap(
            types={},
            query_root_fields={},
            mutation_root_fields={},
            subscription_root_fields={},
            field_relationships=defaultdict(list),
            type_hierarchy=defaultdict(list),
            credit_related_types=[],
            entity_related_types=[],
            record_related_types=[],
            total_fields=0,
            introspection_timestamp=datetime.now().isoformat()
        )
        
        # Process all types
        types_data = schema_data.get('types', [])
        total_field_count = 0
        
        for type_data in types_data:
            type_name = type_data.get('name', '')
            type_kind = type_data.get('kind', '')
            
            # Skip GraphQL built - in types
            if type_name.startswith('__'):
                continue
                
            # Create GraphQL type
            gql_type = GraphQLType(
                name=type_name,
                kind=type_kind,
                description=type_data.get('description')
            )
            
            # Process fields
            if type_data.get('fields'):
                for field_data in type_data['fields']:
                    field_name = field_data.get('name', '')
                    type_name_parsed, type_kind_parsed, is_list, is_non_null, nested_type = self.parse_type_reference(field_data.get('type', {}))
                    
                    field = GraphQLField(
                        name=field_name,
                        type_name=type_name_parsed,
                        type_kind=type_kind_parsed,
                        is_list=is_list,
                        is_non_null=is_non_null,
                        description=field_data.get('description'),
                        nested_type=nested_type
                    )
                    
                    gql_type.fields[field_name] = field
                    schema_map.field_relationships[field_name].append(type_name)
                    total_field_count += 1
            
            # Process input fields
            if type_data.get('inputFields'):
                for field_data in type_data['inputFields']:
                    field_name = field_data.get('name', '')
                    type_name_parsed, type_kind_parsed, is_list, is_non_null, nested_type = self.parse_type_reference(field_data.get('type', {}))
                    
                    field = GraphQLField(
                        name=field_name,
                        type_name=type_name_parsed,
                        type_kind=type_kind_parsed,
                        is_list=is_list,
                        is_non_null=is_non_null,
                        description=field_data.get('description'),
                        nested_type=nested_type
                    )
                    
                    gql_type.input_fields[field_name] = field
                    total_field_count += 1
            
            # Process enum values
            if type_data.get('enumValues'):
                gql_type.enum_values = [ev.get('name', '') for ev in type_data['enumValues']]
            
            # Process interfaces
            if type_data.get('interfaces'):
                gql_type.interfaces = [iface.get('name', '') for iface in type_data['interfaces'] if iface.get('name')]
            
            # Process possible types (for unions / interfaces)
            if type_data.get('possibleTypes'):
                gql_type.possible_types = [pt.get('name', '') for pt in type_data['possibleTypes'] if pt.get('name')]
                for pt_name in gql_type.possible_types:
                    schema_map.type_hierarchy[type_name].append(pt_name)
            
            # Categorize types
            type_name_lower = type_name.lower()
            if any(term in type_name_lower for term in ['credit', 'score', 'bureau', 'inquiry', 'payment', 'liability']):
                schema_map.credit_related_types.append(type_name)
            if any(term in type_name_lower for term in ['entity', 'search']):
                schema_map.entity_related_types.append(type_name)
            if any(term in type_name_lower for term in ['record', 'insight']):
                schema_map.record_related_types.append(type_name)
            
            schema_map.types[type_name] = gql_type
        
        # Process root types
        query_type = schema_data.get('queryType')
        if query_type and query_type.get('name') and query_type['name'] in schema_map.types:
            schema_map.query_root_fields = schema_map.types[query_type['name']].fields
            
        mutation_type = schema_data.get('mutationType')
        if mutation_type and mutation_type.get('name') and mutation_type['name'] in schema_map.types:
            schema_map.mutation_root_fields = schema_map.types[mutation_type['name']].fields
            
        subscription_type = schema_data.get('subscriptionType')
        if subscription_type and subscription_type.get('name') and subscription_type['name'] in schema_map.types:
            schema_map.subscription_root_fields = schema_map.types[subscription_type['name']].fields
        
        schema_map.total_fields = total_field_count
        
        print("✅ Schema map built successfully!")
        print(f"   📊 Total types: {len(schema_map.types)}")
        print(f"   📊 Total fields: {total_field_count}")
        print(f"   🎯 Credit - related types: {len(schema_map.credit_related_types)}")
        print(f"   🎯 Entity - related types: {len(schema_map.entity_related_types)}")
        print(f"   🎯 Record - related types: {len(schema_map.record_related_types)}")
        
        return schema_map

    def generate_master_schema_map(self) -> bool:
        """Generate complete master schema map"""
        
        print("🚀 GENERATING MASTER SCHEMA MAP")
        print("=" * 60)
        
        # Initialize API
        if not self.initialize_api():
            return False
        
        # Get schema introspection
        schema_data = self.get_complete_schema_introspection()
        if not schema_data:
            return False
        
        # Build schema map
        self.schema_map = self.build_schema_map(schema_data)
        
        return True

    def save_schema_map(self, filename: str = "master_schema_map.json") -> bool:
        """Save schema map to JSON file"""
        
        if not self.schema_map:
            print("❌ No schema map to save")
            return False
        
        try:
            # Convert to serializable format
            schema_dict = {
                'metadata': {
                    'total_types': len(self.schema_map.types),
                    'total_fields': self.schema_map.total_fields,
                    'introspection_timestamp': self.schema_map.introspection_timestamp,
                    'credit_related_types': self.schema_map.credit_related_types,
                    'entity_related_types': self.schema_map.entity_related_types,
                    'record_related_types': self.schema_map.record_related_types
                },
                'types': {},
                'query_root_fields': {name: asdict(field) for name, field in self.schema_map.query_root_fields.items()},
                'mutation_root_fields': {name: asdict(field) for name, field in self.schema_map.mutation_root_fields.items()},
                'subscription_root_fields': {name: asdict(field) for name, field in self.schema_map.subscription_root_fields.items()},
                'field_relationships': dict(self.schema_map.field_relationships),
                'type_hierarchy': dict(self.schema_map.type_hierarchy)
            }
            
            # Convert types
            for type_name, gql_type in self.schema_map.types.items():
                type_dict = asdict(gql_type)
                # Convert field dictionaries
                type_dict['fields'] = {name: asdict(field) for name, field in gql_type.fields.items()}
                type_dict['input_fields'] = {name: asdict(field) for name, field in gql_type.input_fields.items()}
                schema_dict['types'][type_name] = type_dict
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(schema_dict, f, indent=2, default=str)
            
            print(f"✅ Schema map saved to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save schema map: {e}")
            return False

    def generate_schema_report(self) -> str:
        """Generate comprehensive schema analysis report"""
        
        if not self.schema_map:
            return "❌ No schema map available"
        
        report = []
        report.append("📊 TILORES GRAPHQL SCHEMA ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {self.schema_map.introspection_timestamp}")
        report.append("")
        
        # Overview
        report.append("🎯 SCHEMA OVERVIEW")
        report.append("-" * 30)
        report.append(f"Total Types: {len(self.schema_map.types)}")
        report.append(f"Total Fields: {self.schema_map.total_fields}")
        report.append(f"Query Root Fields: {len(self.schema_map.query_root_fields)}")
        report.append(f"Mutation Root Fields: {len(self.schema_map.mutation_root_fields)}")
        report.append(f"Subscription Root Fields: {len(self.schema_map.subscription_root_fields)}")
        report.append("")
        
        # Categorized types
        report.append("🎯 CATEGORIZED TYPES")
        report.append("-" * 30)
        report.append(f"Credit - Related Types ({len(self.schema_map.credit_related_types)}):")
        for type_name in sorted(self.schema_map.credit_related_types):
            field_count = len(self.schema_map.types[type_name].fields)
            report.append(f"  • {type_name} ({field_count} fields)")
        
        report.append(f"\nEntity - Related Types ({len(self.schema_map.entity_related_types)}):")
        for type_name in sorted(self.schema_map.entity_related_types):
            field_count = len(self.schema_map.types[type_name].fields)
            report.append(f"  • {type_name} ({field_count} fields)")
        
        report.append(f"\nRecord - Related Types ({len(self.schema_map.record_related_types)}):")
        for type_name in sorted(self.schema_map.record_related_types):
            field_count = len(self.schema_map.types[type_name].fields)
            report.append(f"  • {type_name} ({field_count} fields)")
        
        # Top types by field count
        report.append("\n🎯 TOP TYPES BY FIELD COUNT")
        report.append("-" * 30)
        type_field_counts = [(name, len(gql_type.fields)) for name, gql_type in self.schema_map.types.items()]
        type_field_counts.sort(key=lambda x: x[1], reverse=True)
        
        for type_name, field_count in type_field_counts[:15]:
            report.append(f"  • {type_name}: {field_count} fields")
        
        # Most common field names
        report.append("\n🎯 MOST COMMON FIELD NAMES")
        report.append("-" * 30)
        field_counts = defaultdict(int)
        for field_name, type_list in self.schema_map.field_relationships.items():
            field_counts[field_name] = len(type_list)
        
        common_fields = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)
        for field_name, count in common_fields[:20]:
            report.append(f"  • {field_name}: appears in {count} types")
        
        # Query root analysis
        report.append("\n🎯 QUERY ROOT OPERATIONS")
        report.append("-" * 30)
        for field_name, field in sorted(self.schema_map.query_root_fields.items()):
            report.append(f"  • {field_name} -> {field.type_name}")
        
        return "\n".join(report)

    def search_schema(self, search_term: str, case_sensitive: bool = False) -> Dict[str, List[str]]:
        """Search schema for types and fields matching a term"""
        
        if not self.schema_map:
            return {}
        
        results = {
            'types': [],
            'fields': [],
            'descriptions': []
        }
        
        search_func = (lambda x, term: term in x) if case_sensitive else (lambda x, term: term.lower() in x.lower())
        
        # Search type names
        for type_name in self.schema_map.types.keys():
            if search_func(type_name, search_term):
                results['types'].append(type_name)
        
        # Search field names
        for field_name, type_list in self.schema_map.field_relationships.items():
            if search_func(field_name, search_term):
                results['fields'].append(f"{field_name} (in {len(type_list)} types)")
        
        # Search descriptions
        for type_name, gql_type in self.schema_map.types.items():
            if gql_type.description and search_func(gql_type.description, search_term):
                results['descriptions'].append(f"{type_name}: {gql_type.description}")
            
            for field_name, field in gql_type.fields.items():
                if field.description and search_func(field.description, search_term):
                    results['descriptions'].append(f"{type_name}.{field_name}: {field.description}")
        
        return results

def main():
    """Main execution function"""
    
    mapper = MasterSchemaMapper()
    
    # Generate master schema map
    if mapper.generate_master_schema_map():
        
        # Save schema map
        mapper.save_schema_map("tilores_master_schema_map.json")
        
        # Generate and save report
        report = mapper.generate_schema_report()
        with open("tilores_schema_analysis_report.txt", "w") as f:
            f.write(report)
        
        print("\n" + report)
        
        # Interactive search demo
        print("\n🔍 INTERACTIVE SCHEMA SEARCH")
        print("=" * 60)
        
        while True:
            search_term = input("\nEnter search term (or 'quit' to exit): ").strip()
            if search_term.lower() in ['quit', 'exit', 'q']:
                break
            
            if search_term:
                results = mapper.search_schema(search_term)
                
                print(f"\n📊 Search results for '{search_term}':")
                
                if results['types']:
                    print(f"  Types ({len(results['types'])}):")
                    for type_name in results['types'][:10]:
                        print(f"    • {type_name}")
                
                if results['fields']:
                    print(f"  Fields ({len(results['fields'])}):")
                    for field_info in results['fields'][:10]:
                        print(f"    • {field_info}")
                
                if results['descriptions']:
                    print(f"  Descriptions ({len(results['descriptions'])}):")
                    for desc in results['descriptions'][:5]:
                        print(f"    • {desc}")
                
                if not any(results.values()):
                    print("  No results found")
    
    else:
        print("❌ Failed to generate master schema map")

if __name__ == "__main__":
    main()
