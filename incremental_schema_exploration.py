#!/usr/bin/env python3
"""
Incremental Schema Exploration
Build incrementally on working query structure to find multi-bureau data
"""

from dotenv import load_dotenv
load_dotenv()

def incremental_schema_exploration():
    """Build incrementally on working query structure"""

    print("🔍 INCREMENTAL SCHEMA EXPLORATION")
    print("=" * 50)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return

    # entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    # Start with the working query structure and add fields incrementally
    print("\n🔍 STEP 1: WORKING QUERY STRUCTURE")
    print("-" * 50)

    working_query = """
    query WorkingQueryStructure {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
            }}
            PHONE_EXTERNAL
            CREATED_DATE
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(working_query)
        if result and 'data' in result:
            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            print("📊 WORKING QUERY RESULTS:")
            print(f"   Total records: {len(records)}")

            # Analyze what we have
            bureaus = set()
            for record in records:
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    bureau = credit_response.get('CREDIT_BUREAU')
                    if bureau:
                        bureaus.add(bureau)

            print(f"   Bureaus found: {list(bureaus)}")

        else:
            print("❌ Working query failed")
            return

    except Exception as e:
        print(f"❌ Working query failed: {e}")
        return

    # Step 2: Add one field at a time to find where multi-bureau data is
    print("\n🔍 STEP 2: ADD FIELDS INCREMENTALLY")
    print("-" * 50)

    # Test 1: Add CREDIT_REPORT field
    print("   Testing CREDIT_REPORT field...")

    test1_query = """
    query TestCreditReport {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
            }}
            CREDIT_REPORT {{
              BUREAU
            }}
            PHONE_EXTERNAL
            CREATED_DATE
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(test1_query)
        if result and 'data' in result:
            print("     ✅ CREDIT_REPORT field works")

            # Check if we found additional bureau data
            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            all_bureaus = set()
            for record in records:
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    bureau = credit_response.get('CREDIT_BUREAU')
                    if bureau:
                        all_bureaus.add(bureau)

                credit_report = record.get('CREDIT_REPORT')
                if credit_report:
                    bureau = credit_report.get('BUREAU')
                    if bureau:
                        all_bureaus.add(bureau)

            print(f"     Bureaus found: {list(all_bureaus)}")

        else:
            print("     ❌ CREDIT_REPORT field failed")

    except Exception as e:
        print(f"     ❌ CREDIT_REPORT field error: {e}")

    # Test 2: Add CREDIT_FILE field
    print("   Testing CREDIT_FILE field...")

    test2_query = """
    query TestCreditFile {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
            }}
            CREDIT_FILE {{
              CreditRepositorySourceType
            }}
            PHONE_EXTERNAL
            CREATED_DATE
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(test2_query)
        if result and 'data' in result:
            print("     ✅ CREDIT_FILE field works")

            # Check if we found additional bureau data
            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            all_bureaus = set()
            for record in records:
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    bureau = credit_response.get('CREDIT_BUREAU')
                    if bureau:
                        all_bureaus.add(bureau)

                credit_file = record.get('CREDIT_FILE')
                if credit_file:
                    source_type = credit_file.get('CreditRepositorySourceType')
                    if source_type:
                        all_bureaus.add(source_type)

            print(f"     Bureaus found: {list(all_bureaus)}")

        else:
            print("     ❌ CREDIT_FILE field failed")

    except Exception as e:
        print(f"     ❌ CREDIT_FILE field error: {e}")

    # Test 3: Add any other potential bureau fields
    print("   Testing other potential bureau fields...")

    test3_query = """
    query TestOtherBureauFields {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
            }}
            BUREAU
            Source
            Repository
            PHONE_EXTERNAL
            CREATED_DATE
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(test3_query)
        if result and 'data' in result:
            print("     ✅ Other bureau fields work")

            # Check if we found additional bureau data
            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            all_bureaus = set()
            for record in records:
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    bureau = credit_response.get('CREDIT_BUREAU')
                    if bureau:
                        all_bureaus.add(bureau)

                bureau = record.get('BUREAU')
                if bureau:
                    all_bureaus.add(bureau)

                source = record.get('Source')
                if source:
                    all_bureaus.add(source)

                repository = record.get('Repository')
                if repository:
                    all_bureaus.add(repository)

            print(f"     Bureaus found: {list(all_bureaus)}")

        else:
            print("     ❌ Other bureau fields failed")

    except Exception as e:
        print(f"     ❌ Other bureau fields error: {e}")

    # Step 3: Check if there are different record types
    print("\n🔍 STEP 3: CHECK FOR DIFFERENT RECORD TYPES")
    print("-" * 50)

    # Look at all available fields in the working records
    print("   Analyzing all available fields...")

    try:
        entity = result['data']['entity']['entity']
        records = entity.get('records', [])

        all_fields = set()
        for record in records:
            for field_name in record.keys():
                all_fields.add(field_name)

        print(f"   All available fields: {sorted(list(all_fields))}")

        # Look for any field that might contain bureau info
        bureau_related_fields = [field for field in all_fields if 'bureau' in field.lower() or 'source' in field.lower() or 'repository' in field.lower()]
        if bureau_related_fields:
            print(f"   Bureau-related fields: {bureau_related_fields}")
        else:
            print("   No additional bureau-related fields found")

    except Exception as e:
        print(f"   Error analyzing fields: {e}")

    print("\n🎯 INCREMENTAL SCHEMA EXPLORATION COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    incremental_schema_exploration()
