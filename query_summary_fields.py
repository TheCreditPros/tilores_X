#!/usr/bin/env python3
"""
Query Credit Summary Fields
Query the actual credit summary fields to see what rollup data is available
"""

from dotenv import load_dotenv
load_dotenv()

def query_summary_fields():
    """Query the actual credit summary fields for rollup data"""

    print("🔍 QUERYING CREDIT SUMMARY FIELDS")
    print("=" * 60)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized successfully")
    except Exception as e:
        print(f"❌ Tilores API initialization failed: {e}")
        return

    # Use the working entity ID
    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    print(f"\n🔍 QUERYING SUMMARY FIELDS FOR ENTITY: {entity_id}")
    print("-" * 50)

    # Query 1: Basic CREDIT_SUMMARY fields
    print("\n🔍 QUERY 1: CREDIT_SUMMARY FIELDS")
    print("-" * 40)

    summary_query1 = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              Report_ID
              CREDIT_SUMMARY {
                # These should contain rollup data
              }
            }
          }
        }
      }
    }
    """

    try:
        result = tilores_api.gql(summary_query1, {"id": entity_id})
        if result and 'data' in result:
            print("✅ CREDIT_SUMMARY query executed")

            # Check for errors to see what fields exist
            if result.get("errors"):
                print("   ❌ GraphQL errors found:")
                for error in result["errors"]:
                    print(f"     {error.get('message', 'Unknown error')}")
            else:
                print("   ✅ No GraphQL errors - CREDIT_SUMMARY fields exist")

                # Display the data
                entity = result['data']['entity']['entity']
                records = entity.get('records', [])

                for i, record in enumerate(records):
                    credit_response = record.get('CREDIT_RESPONSE')
                    if credit_response:
                        bureau = credit_response.get('CREDIT_BUREAU')
                        date = credit_response.get('CreditReportFirstIssuedDate')
                        summary = credit_response.get('CREDIT_SUMMARY')

                        print(f"   Record {i + 1}: {bureau} | {date}")
                        if summary:
                            print(f"     CREDIT_SUMMARY: {summary}")
                        else:
                            print("     CREDIT_SUMMARY: None")
        else:
            print("   ❌ CREDIT_SUMMARY query failed")

    except Exception as e:
        print(f"   ❌ CREDIT_SUMMARY query failed: {e}")

    # Query 2: CREDIT_SUMMARY_TUI fields
    print("\n🔍 QUERY 2: CREDIT_SUMMARY_TUI FIELDS")
    print("-" * 40)

    summary_query2 = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              Report_ID
              CREDIT_SUMMARY_TUI {
                # TransUnion summary fields
              }
            }
          }
        }
      }
    }
    """

    try:
        result = tilores_api.gql(summary_query2, {"id": entity_id})
        if result and 'data' in result:
            print("✅ CREDIT_SUMMARY_TUI query executed")

            if result.get("errors"):
                print("   ❌ GraphQL errors found:")
                for error in result["errors"]:
                    print(f"     {error.get('message', 'Unknown error')}")
            else:
                print("   ✅ No GraphQL errors - CREDIT_SUMMARY_TUI fields exist")

                # Display the data
                entity = result['data']['entity']['entity']
                records = entity.get('records', [])

                for i, record in enumerate(records):
                    credit_response = record.get('CREDIT_RESPONSE')
                    if credit_response:
                        bureau = credit_response.get('CREDIT_BUREAU')
                        date = credit_response.get('CreditReportFirstIssuedDate')
                        summary_tui = credit_response.get('CREDIT_SUMMARY_TUI')

                        print(f"   Record {i + 1}: {bureau} | {date}")
                        if summary_tui:
                            print(f"     CREDIT_SUMMARY_TUI: {summary_tui}")
                        else:
                            print("     CREDIT_SUMMARY_TUI: None")
        else:
            print("   ❌ CREDIT_SUMMARY_TUI query failed")

    except Exception as e:
        print(f"   ❌ CREDIT_SUMMARY_TUI query failed: {e}")

    # Query 3: Try to get the actual field names from schema
    print("\n🔍 QUERY 3: SCHEMA FIELD NAMES")
    print("-" * 40)

    schema_query = """
    query GetCreditSummaryFields {
      __type(name: "CreditResponseCreditSummary") {
        name
        fields {
          name
          description
          type {
            name
            kind
          }
        }
      }
    }
    """

    try:
        result = tilores_api.gql(schema_query)
        if result and 'data' in result:
            credit_summary_type = result['data']['__type']
            if credit_summary_type:
                fields = credit_summary_type.get('fields', [])
                print(f"   CreditResponseCreditSummary fields: {len(fields)}")

                for field in fields:
                    field_name = field.get('name')
                    field_desc = field.get('description', 'No description')
                    field_type = field.get('type', {})
                    type_name = field_type.get('name', 'Unknown')

                    print(f"     - {field_name}: {type_name} - {field_desc}")
            else:
                print("   ❌ CreditResponseCreditSummary type not found")
        else:
            print("   ❌ Schema query failed")

    except Exception as e:
        print(f"   ❌ Schema query failed: {e}")

    # Query 4: Test with actual field names
    print("\n🔍 QUERY 4: TEST WITH ACTUAL FIELD NAMES")
    print("-" * 40)

    # This will be populated after we discover the actual field names
    print("   Will test with actual field names after discovery")

    print("\n🎯 SUMMARY FIELD QUERY COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    query_summary_fields()
