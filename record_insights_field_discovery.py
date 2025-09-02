#!/usr/bin/env python3
"""
Record Insights Field Discovery
Use recordInsights to discover the actual working field structure
"""

from dotenv import load_dotenv
load_dotenv()

def record_insights_field_discovery():
    """Use recordInsights to discover working field structure"""

    print("🔍 RECORD INSIGHTS FIELD DISCOVERY")
    print("=" * 50)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return

    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    # Test 1: Use recordInsights to discover all available fields
    print("\n🔍 TEST 1: DISCOVER ALL AVAILABLE FIELDS")
    print("-" * 50)

    query1 = """
    query DiscoverAllFields {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          recordInsights {{
            # Get all available fields
            allFields: valuesDistinct(field: "*")
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(query1)
        if result and 'data' in result:
            entity = result['data']['entity']['entity']
            record_insights = entity.get('recordInsights', {})
            all_fields = record_insights.get('allFields', [])

            print("📊 ALL AVAILABLE FIELDS:")
            print(f"   Total fields found: {len(all_fields)}")

            if all_fields:
                print("\n📋 FIELD LIST:")
                for i, field in enumerate(all_fields[:20]):  # Show first 20
                    print(f"   {i + 1}. {field}")

                if len(all_fields) > 20:
                    print(f"   ... and {len(all_fields) - 20} more fields")

                # Look for credit-related fields
                credit_fields = [field for field in all_fields if 'credit' in field.lower()]
                if credit_fields:
                    print("\n📋 CREDIT-RELATED FIELDS:")
                    for field in credit_fields:
                        print(f"   {field}")

                # Look for bureau-related fields
                bureau_fields = [field for field in all_fields if 'bureau' in field.lower() or 'source' in field.lower() or 'repository' in field.lower()]
                if bureau_fields:
                    print("\n📋 BUREAU-RELATED FIELDS:")
                    for field in bureau_fields:
                        print(f"   {field}")

                # Look for report-related fields
                report_fields = [field for field in all_fields if 'report' in field.lower()]
                if report_fields:
                    print("\n📋 REPORT-RELATED FIELDS:")
                    for field in report_fields:
                        print(f"   {field}")

            else:
                print("❌ No fields found")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 1 failed: {e}")

    # Test 2: Use recordInsights to check specific credit fields
    print("\n🔍 TEST 2: CHECK SPECIFIC CREDIT FIELDS")
    print("-" * 50)

    query2 = """
    query CheckSpecificCreditFields {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          recordInsights {{
            # Check for credit response fields
            creditResponseFields: valuesDistinct(field: "CREDIT_RESPONSE")
            creditBureauFields: valuesDistinct(field: "CREDIT_BUREAU")
            creditRepositoryFields: valuesDistinct(field: "CreditRepositorySourceType")
            creditSourceFields: valuesDistinct(field: "CreditRepositorySource")
            # Check for any other potential bureau fields
            bureauFields: valuesDistinct(field: "BUREAU")
            sourceFields: valuesDistinct(field: "Source")
            repositoryFields: valuesDistinct(field: "Repository")
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(query2)
        if result and 'data' in result:
            entity = result['data']['entity']['entity']
            record_insights = entity.get('recordInsights', {})

            print("📊 SPECIFIC CREDIT FIELD CHECK:")

            # Check each field type
            field_types = [
                'creditResponseFields', 'creditBureauFields', 'creditRepositoryFields',
                'creditSourceFields', 'bureauFields', 'sourceFields', 'repositoryFields'
            ]

            for field_type in field_types:
                values = record_insights.get(field_type, [])
                if values:
                    print(f"   {field_type}: {values}")
                else:
                    print(f"   {field_type}: No values found")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 2 failed: {e}")

    # Test 3: Use recordInsights to check for nested credit fields
    print("\n🔍 TEST 3: CHECK NESTED CREDIT FIELDS")
    print("-" * 50)

    query3 = """
    query CheckNestedCreditFields {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          recordInsights {{
            # Check for nested credit response fields
            creditResponseBureau: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_BUREAU")
            creditResponseRepository: valuesDistinct(field: "CREDIT_RESPONSE.CreditRepositorySourceType")
            creditResponseSource: valuesDistinct(field: "CREDIT_RESPONSE.CreditRepositorySource")
            # Check for any other nested patterns
            creditFileRepository: valuesDistinct(field: "CREDIT_FILE.CreditRepositorySourceType")
            creditScoreRepository: valuesDistinct(field: "CREDIT_SCORE.CreditRepositorySourceType")
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(query3)
        if result and 'data' in result:
            entity = result['data']['entity']['entity']
            record_insights = entity.get('recordInsights', {})

            print("📊 NESTED CREDIT FIELD CHECK:")

            # Check each nested field type
            nested_field_types = [
                'creditResponseBureau', 'creditResponseRepository', 'creditResponseSource',
                'creditFileRepository', 'creditScoreRepository'
            ]

            for field_type in nested_field_types:
                values = record_insights.get(field_type, [])
                if values:
                    print(f"   {field_type}: {values}")
                else:
                    print(f"   {field_type}: No values found")

        else:
            print("❌ Query failed")

    except Exception as e:
        print(f"❌ Test 3 failed: {e}")

    print("\n🎯 RECORD INSIGHTS FIELD DISCOVERY COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    record_insights_field_discovery()
