#!/usr / bin / env python3
"""
Complete Schema Deep Dive - Master Map of Every Field, Table, and Data Type
Comprehensive analysis of the entire Tilores GraphQL schema with full nested field mapping
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict, deque
from dotenv import load_dotenv

load_dotenv()

class CompleteSchemaAnalyzer:
    """Complete schema analyzer that maps every field, nested field, table, and data type"""

    def __init__(self):
        self.schema_data = None
        self.complete_field_map = {}
        self.type_hierarchy = defaultdict(list)
        self.field_paths = defaultdict(list)  # field_name -> [full.path.to.field]
        self.data_source_mapping = defaultdict(dict)

    def load_schema(self, filename: str = "tilores_master_schema_map.json") -> bool:
        """Load the schema map from JSON file"""
        try:
            with open(filename, 'r') as f:
                self.schema_data = json.load(f)
            print(f"✅ Schema loaded: {len(self.schema_data['types'])} types, {self.schema_data['metadata']['total_fields']} fields")
            return True
        except Exception as e:
            print(f"❌ Failed to load schema: {e}")
            return False

    def build_complete_field_paths(self, type_name: str, current_path: str = "", visited: Set[str] = None, max_depth: int = 10) -> Dict[str, Any]:
        """Recursively build complete field paths for a type"""
        if visited is None:
            visited = set()

        if type_name in visited or max_depth <= 0 or type_name not in self.schema_data['types']:
            return {}

        visited.add(type_name)
        type_info = self.schema_data['types'][type_name]
        field_map = {}

        for field_name, field_info in type_info['fields'].items():
            field_path = f"{current_path}.{field_name}" if current_path else field_name

            field_details = {
                'field_name': field_name,
                'type_name': field_info['type_name'],
                'type_kind': field_info['type_kind'],
                'is_list': field_info['is_list'],
                'is_non_null': field_info['is_non_null'],
                'description': field_info.get('description'),
                'full_path': field_path,
                'nested_fields': {}
            }

            # Add to global field path tracking
            self.field_paths[field_name].append(field_path)

            # Recursively get nested fields
            nested_type = field_info['type_name']
            if (nested_type in self.schema_data['types'] and
                nested_type not in ['String', 'Int', 'Float', 'Boolean', 'ID', 'Any', 'Time'] and
                not nested_type.endswith('Input')):

                nested_fields = self.build_complete_field_paths(
                    nested_type,
                    field_path,
                    visited.copy(),
                    max_depth - 1
                )
                field_details['nested_fields'] = nested_fields

            field_map[field_name] = field_details

        return field_map

    def analyze_data_sources(self) -> Dict[str, Dict]:
        """Analyze and categorize all data sources based on Record type fields"""
        if 'Record' not in self.schema_data['types']:
            print("❌ Record type not found")
            return {}

        record_type = self.schema_data['types']['Record']
        data_sources = {
            'CREDIT': {'root_fields': [], 'total_nested_fields': 0, 'types': set()},
            'TRANSACTION': {'root_fields': [], 'total_nested_fields': 0, 'types': set()},
            'CARD': {'root_fields': [], 'total_nested_fields': 0, 'types': set()},
            'PHONE': {'root_fields': [], 'total_nested_fields': 0, 'types': set()},
            'TICKET': {'root_fields': [], 'total_nested_fields': 0, 'types': set()},
            'IDENTITY': {'root_fields': [], 'total_nested_fields': 0, 'types': set()},
            'BUSINESS': {'root_fields': [], 'total_nested_fields': 0, 'types': set()},
            'SYSTEM': {'root_fields': [], 'total_nested_fields': 0, 'types': set()}
        }

        # Categorize each Record field
        for field_name, field_info in record_type['fields'].items():
            field_upper = field_name.upper()

            # Determine data source category
            if any(term in field_upper for term in ['CREDIT', 'SCORE', 'BUREAU', 'INQUIRY', 'LIABILITY', 'BORROWER']):
                category = 'CREDIT'
            elif any(term in field_upper for term in ['TRANSACTION', 'PAYMENT', 'BILLING', 'CHARGE', 'REFUND', 'DEBT']):
                category = 'TRANSACTION'
            elif any(term in field_upper for term in ['CARD', 'BIN', 'EXPIR']):
                category = 'CARD'
            elif any(term in field_upper for term in ['PHONE', 'CALL', 'CONTACT']):
                category = 'PHONE'
            elif any(term in field_upper for term in ['TICKET', 'SUPPORT', 'ZOHO', 'CASE']):
                category = 'TICKET'
            elif any(term in field_upper for term in ['EMAIL', 'NAME', 'SSN', 'DOB', 'ADDRESS']):
                category = 'IDENTITY'
            elif any(term in field_upper for term in ['PRODUCT', 'CAMPAIGN', 'AGENT', 'STAGE']):
                category = 'BUSINESS'
            else:
                category = 'SYSTEM'

            # Add to category
            data_sources[category]['root_fields'].append(field_name)

            # Build complete field map for this field
            field_map = self.build_complete_field_paths(field_info['type_name'])

            # Count total nested fields
            def count_nested_fields(field_dict):
                count = len(field_dict)
                for field_data in field_dict.values():
                    if field_data['nested_fields']:
                        count += count_nested_fields(field_data['nested_fields'])
                return count

            nested_count = count_nested_fields(field_map)
            data_sources[category]['total_nested_fields'] += nested_count

            # Track types used
            def collect_types(field_dict):
                types = set()
                for field_data in field_dict.values():
                    types.add(field_data['type_name'])
                    if field_data['nested_fields']:
                        types.update(collect_types(field_data['nested_fields']))
                return types

            field_types = collect_types(field_map)
            data_sources[category]['types'].update(field_types)

            # Store the complete field map
            self.data_source_mapping[category][field_name] = field_map

        return data_sources

    def generate_complete_field_inventory(self) -> Dict[str, Any]:
        """Generate complete inventory of every field in the schema"""
        print("🔍 Building complete field inventory...")

        inventory = {
            'total_types': len(self.schema_data['types']),
            'total_direct_fields': 0,
            'total_nested_fields': 0,
            'field_frequency': defaultdict(int),
            'type_field_counts': {},
            'deepest_nesting_level': 0,
            'field_type_distribution': defaultdict(int),
            'complete_field_paths': []
        }

        # Analyze every type
        for type_name, type_info in self.schema_data['types'].items():
            if type_name.startswith('__'):  # Skip GraphQL introspection types
                continue

            field_count = len(type_info['fields'])
            inventory['total_direct_fields'] += field_count
            inventory['type_field_counts'][type_name] = field_count

            # Build complete field paths for this type
            complete_paths = self.build_complete_field_paths(type_name)

            # Count all nested fields
            def count_and_analyze_fields(field_dict, current_depth=0):
                count = 0
                max_depth = current_depth

                for field_name, field_data in field_dict.items():
                    count += 1
                    inventory['field_frequency'][field_name] += 1
                    inventory['field_type_distribution'][field_data['type_name']] += 1
                    inventory['complete_field_paths'].append(field_data['full_path'])

                    if field_data['nested_fields']:
                        nested_count, nested_depth = count_and_analyze_fields(
                            field_data['nested_fields'],
                            current_depth + 1
                        )
                        count += nested_count
                        max_depth = max(max_depth, nested_depth)

                return count, max_depth

            nested_count, max_depth = count_and_analyze_fields(complete_paths)
            inventory['total_nested_fields'] += nested_count
            inventory['deepest_nesting_level'] = max(inventory['deepest_nesting_level'], max_depth)

        return inventory

    def generate_master_report(self) -> str:
        """Generate the complete master report"""
        print("📊 Generating complete master schema report...")

        # Analyze data sources
        data_sources = self.analyze_data_sources()

        # Generate complete field inventory
        inventory = self.generate_complete_field_inventory()

        report = []
        report.append("🎯 COMPLETE TILORES SCHEMA MASTER MAP")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Schema Timestamp: {self.schema_data['metadata']['introspection_timestamp']}")
        report.append("")

        # Overall Statistics
        report.append("📊 COMPLETE SCHEMA STATISTICS")
        report.append("-" * 50)
        report.append(f"Total GraphQL Types: {inventory['total_types']}")
        report.append(f"Total Direct Fields: {inventory['total_direct_fields']}")
        report.append(f"Total Nested Fields (All Levels): {inventory['total_nested_fields']}")
        report.append(f"Deepest Nesting Level: {inventory['deepest_nesting_level']}")
        report.append(f"Unique Field Names: {len(inventory['field_frequency'])}")
        report.append(f"Complete Field Paths: {len(inventory['complete_field_paths'])}")
        report.append("")

        # Data Source Analysis
        report.append("🎯 DATA SOURCE BREAKDOWN (FROM RECORD TYPE)")
        report.append("-" * 50)
        total_root_fields = 0
        total_nested_fields = 0

        for source_name, source_data in sorted(data_sources.items()):
            root_count = len(source_data['root_fields'])
            nested_count = source_data['total_nested_fields']
            type_count = len(source_data['types'])

            total_root_fields += root_count
            total_nested_fields += nested_count

            report.append(f"{source_name}:")
            report.append(f"  Root Fields: {root_count}")
            report.append(f"  Total Nested Fields: {nested_count}")
            report.append(f"  Related Types: {type_count}")
            report.append(f"  Root Field Names: {', '.join(sorted(source_data['root_fields']))}")
            report.append("")

        report.append(f"TOTALS: {total_root_fields} root fields, {total_nested_fields} nested fields")
        report.append("")

        # Most Complex Types
        report.append("🏗️ MOST COMPLEX TYPES (BY DIRECT FIELD COUNT)")
        report.append("-" * 50)
        complex_types = sorted(inventory['type_field_counts'].items(), key=lambda x: x[1], reverse=True)
        for i, (type_name, field_count) in enumerate(complex_types[:20]):
            report.append(f"{i + 1:2d}. {type_name}: {field_count} direct fields")
        report.append("")

        # Most Common Field Names
        report.append("🔄 MOST COMMON FIELD NAMES")
        report.append("-" * 50)
        common_fields = sorted(inventory['field_frequency'].items(), key=lambda x: x[1], reverse=True)
        for i, (field_name, count) in enumerate(common_fields[:25]):
            report.append(f"{i + 1:2d}. {field_name}: appears {count} times")
        report.append("")

        # Field Type Distribution
        report.append("📈 FIELD TYPE DISTRIBUTION")
        report.append("-" * 50)
        type_dist = sorted(inventory['field_type_distribution'].items(), key=lambda x: x[1], reverse=True)
        for i, (type_name, count) in enumerate(type_dist[:20]):
            report.append(f"{i + 1:2d}. {type_name}: {count} fields")
        report.append("")

        # Detailed Data Source Field Maps
        report.append("🗺️ DETAILED DATA SOURCE FIELD MAPS")
        report.append("-" * 50)

        for source_name, source_fields in sorted(self.data_source_mapping.items()):
            if not source_fields:
                continue

            report.append(f"\n{source_name} DATA SOURCE:")
            report.append("=" * 30)

            for root_field, field_map in sorted(source_fields.items()):
                report.append(f"\n📋 {root_field}:")

                def print_field_tree(fields, indent="  "):
                    for field_name, field_data in sorted(fields.items()):
                        type_info = f"{field_data['type_name']}"
                        if field_data['is_list']:
                            type_info += " (LIST)"
                        if field_data['is_non_null']:
                            type_info += " (NON_NULL)"

                        report.append(f"{indent}• {field_name} -> {type_info}")

                        if field_data['nested_fields']:
                            print_field_tree(field_data['nested_fields'], indent + "  ")

                print_field_tree(field_map)

        return "\n".join(report)

    def save_complete_analysis(self, report: str, filename_prefix: str = "complete_schema_analysis"):
        """Save the complete analysis to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save the report
        report_filename = f"{filename_prefix}_report_{timestamp}.txt"
        with open(report_filename, 'w') as f:
            f.write(report)
        print(f"✅ Complete report saved to {report_filename}")

        # Save the complete field mapping as JSON
        json_filename = f"{filename_prefix}_data_{timestamp}.json"
        analysis_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_types': len(self.schema_data['types']),
                'total_fields': sum(len(t['fields']) for t in self.schema_data['types'].values())
            },
            'data_source_mapping': {k: v for k, v in self.data_source_mapping.items()},
            'field_paths': dict(self.field_paths),
            'complete_schema': self.schema_data
        }

        with open(json_filename, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        print(f"✅ Complete data saved to {json_filename}")

        return report_filename, json_filename

def main():
    """Main execution function"""
    print("🚀 COMPLETE SCHEMA DEEP DIVE ANALYSIS")
    print("=" * 80)

    analyzer = CompleteSchemaAnalyzer()

    # Load schema
    if not analyzer.load_schema():
        return

    # Generate complete analysis
    report = analyzer.generate_master_report()

    # Save analysis
    report_file, data_file = analyzer.save_complete_analysis(report)

    # Display report
    print("\n" + report)

    print("\n🎯 ANALYSIS COMPLETE!")
    print(f"📄 Report: {report_file}")
    print(f"📊 Data: {data_file}")

if __name__ == "__main__":
    main()


