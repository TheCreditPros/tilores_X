#!/usr/bin/env python3
"""
Schema Introspection Reinvestigation
Re-explore the schema to find where TransUnion and Experian data is stored
"""

from dotenv import load_dotenv
load_dotenv()

def schema_introspection_reinvestigation():
    """Re-explore schema to find multi-bureau data"""

    print("🔍 SCHEMA INTROSPECTION REINVESTIGATION")
    print("=" * 60)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return

    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    # Test 1: Check if there are different record types for different bureaus
    print("\n🔍 TEST 1: DIFFERENT RECORD TYPES FOR DIFFERENT BUREAUS")
    print("-" * 60)

    query1 = """
    query DifferentRecordTypes {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            # Check for different credit record types
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
            }}
            CREDIT_REPORT {{
              BUREAU
              CreditBureau
              Source
            }}
            CREDIT_FILE {{
              CreditRepositorySourceType
              Repository
            }}
            # Check for bureau-specific record types
            TRANSUNION_REPORT {{
              ReportDate
              Score
            }}
            EXPERIAN_REPORT {{
              ReportDate
              Score
            }}
            EQUIFAX_REPORT {{
              ReportDate
              Score
            }}
            # Check for any other credit-related fields
            CREDIT_SCORE
            CREDIT_LIABILITY
            CREDIT_INQUIRY
          }}
        }}
      }}
    }}
    """

    try:
        result1 = tilores_api.gql(query1)
        if result1 and 'data' in result1:
            entity = result1['data']['entity']['entity']
            records = entity.get('records', [])

            print("📊 DIFFERENT RECORD TYPES ANALYSIS:")
            print(f"   Total records: {len(records)}")

            # Analyze all available fields across all records
            all_fields = set()
            record_type_counts = {}

            for i, record in enumerate(records):
                print(f"   Record {i}:")

                # Get all top-level fields for this record
                for field_name, field_value in record.items():
                    if field_value:
                        all_fields.add(field_name)
                        if field_name not in record_type_counts:
                            record_type_counts[field_name] = 0
                        record_type_counts[field_name] += 1

                # Check specific credit-related fields
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    print(f"     CREDIT_RESPONSE: {credit_response.get('CREDIT_BUREAU')}")

                credit_report = record.get('CREDIT_REPORT')
                if credit_report:
                    print(f"     CREDIT_REPORT: {credit_report.get('BUREAU')}")

                transunion_report = record.get('TRANSUNION_REPORT')
                if transunion_report:
                    print("     TRANSUNION_REPORT: Found!")

                experian_report = record.get('EXPERIAN_REPORT')
                if experian_report:
                    print("     EXPERIAN_REPORT: Found!")

                equifax_report = record.get('EQUIFAX_REPORT')
                if equifax_report:
                    print("     EQUIFAX_REPORT: Found!")

                print("     ---")

            print("\n📋 FIELD ANALYSIS:")
            print(f"   All available fields: {sorted(list(all_fields))}")
            print("   Record type distribution:")
            for field, count in sorted(record_type_counts.items()):
                print(f"     {field}: {count} records")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 1 failed: {e}")

    # Test 2: Check if bureaus are stored in different field names
    print("\n🔍 TEST 2: ALTERNATIVE BUREAU FIELD NAMES")
    print("-" * 60)

    query2 = """
    query AlternativeBureauFields {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            # Check for any field that might contain bureau info
            CREDIT_BUREAU
            CreditBureau
            BUREAU
            Bureau
            Source
            CreditSource
            Repository
            CreditRepository
            ReportSource
            CreditReportSource
            # Check for any field with 'bureau' in the name
            _bureau
            bureau_
            # Check for any field with 'source' in the name
            _source
            source_
          }}
        }}
      }}
    }}
    """

    try:
        result2 = tilores_api.gql(query2)
        if result2 and 'data' in result2:
            entity = result2['data']['entity']['entity']
            records = entity.get('records', [])

            print("📊 ALTERNATIVE BUREAU FIELD ANALYSIS:")
            for i, record in enumerate(records):
                print(f"   Record {i}:")

                # Check all possible bureau field names
                bureau_fields = [
                    'CREDIT_BUREAU', 'CreditBureau', 'BUREAU', 'Bureau',
                    'Source', 'CreditSource', 'Repository', 'CreditRepository',
                    'ReportSource', 'CreditReportSource'
                ]

                for field in bureau_fields:
                    value = record.get(field)
                    if value:
                        print(f"     {field}: {value}")

                print("     ---")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 2 failed: {e}")

    # Test 3: Check if there are nested bureau structures
    print("\n🔍 TEST 3: NESTED BUREAU STRUCTURES")
    print("-" * 60)

    query3 = """
    query NestedBureauStructures {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            # Check for nested bureau information
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CREDIT_FILE {{
                CreditRepositorySourceType
                CreditRepositorySource
              }}
              CREDIT_SCORE {{
                CreditRepositorySourceType
                CreditRepositorySource
              }}
            }}
            # Check for any other nested structures
            CREDIT_DATA {{
              BUREAU
              Source
            }}
            REPORT_DATA {{
              BUREAU
              Source
            }}
          }}
        }}
      }}
    }}
    """

    try:
        result3 = tilores_api.gql(query3)
        if result3 and 'data' in result3:
            entity = result3['data']['entity']['entity']
            records = entity.get('records', [])

            print("📊 NESTED BUREAU STRUCTURE ANALYSIS:")
            for i, record in enumerate(records):
                print(f"   Record {i}:")

                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    print(f"     CREDIT_RESPONSE.CREDIT_BUREAU: {credit_response.get('CREDIT_BUREAU')}")

                    credit_files = credit_response.get('CREDIT_FILE', [])
                    for j, credit_file in enumerate(credit_files):
                        print(f"       CREDIT_FILE {j}:")
                        print(f"         CreditRepositorySourceType: {credit_file.get('CreditRepositorySourceType')}")
                        print(f"         CreditRepositorySource: {credit_file.get('CreditRepositorySource')}")

                    credit_scores = credit_response.get('CREDIT_SCORE', [])
                    for j, credit_score in enumerate(credit_scores):
                        print(f"       CREDIT_SCORE {j}:")
                        print(f"         CreditRepositorySourceType: {credit_score.get('CreditRepositorySourceType')}")
                        print(f"         CreditRepositorySource: {credit_score.get('CreditRepositorySource')}")

                credit_data = record.get('CREDIT_DATA')
                if credit_data:
                    print(f"     CREDIT_DATA.BUREAU: {credit_data.get('BUREAU')}")
                    print(f"     CREDIT_DATA.Source: {credit_data.get('Source')}")

                report_data = record.get('REPORT_DATA')
                if report_data:
                    print(f"     REPORT_DATA.BUREAU: {report_data.get('BUREAU')}")
                    print(f"     REPORT_DATA.Source: {report_data.get('Source')}")

                print("     ---")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 3 failed: {e}")

    # Test 4: Check if there are different entities or record structures
    print("\n🔍 TEST 4: ENTITY STRUCTURE ANALYSIS")
    print("-" * 60)

    query4 = """
    query EntityStructureAnalysis {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          # Check entity-level fields
          CREDIT_RESPONSE {{
            CREDIT_BUREAU
          }}
          CREDIT_REPORT {{
            BUREAU
          }}
          # Check for any other entity-level credit fields
          records {{
            # Look for any field that might contain bureau info
            CREDIT_BUREAU
            BUREAU
            Source
            Repository
            # Check for any field that might indicate record type
            RecordType
            DataType
            SourceType
          }}
        }}
      }}
    }}
    """

    try:
        result4 = tilores_api.gql(query4)
        if result4 and 'data' in result4:
            entity = result4['data']['entity']['entity']

            print("📊 ENTITY STRUCTURE ANALYSIS:")

            # Check entity-level fields
            entity_fields = [field for field in entity.keys() if field != 'records']
            print(f"   Entity-level fields: {entity_fields}")

            # Check if there are any credit fields at entity level
            credit_entity_fields = [field for field in entity_fields if 'credit' in field.lower()]
            if credit_entity_fields:
                print(f"   Entity-level credit fields: {credit_entity_fields}")

                # Check each credit field at entity level
                for field in credit_entity_fields:
                    field_data = entity.get(field)
                    if field_data:
                        print(f"     {field}: {field_data}")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 4 failed: {e}")

    print("\n🎯 SCHEMA INTROSPECTION REINVESTIGATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    schema_introspection_reinvestigation()
