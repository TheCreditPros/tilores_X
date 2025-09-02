#!/usr/bin/env python3
"""
Query DATA_SET Fields
Query the DATA_SET field which likely contains the rollup summary parameters
"""

from dotenv import load_dotenv
load_dotenv()

def query_dataset_fields():
    """Query the DATA_SET field for rollup summary data"""

    print("🔍 QUERYING DATA_SET FIELDS FOR ROLLUP DATA")
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

    print(f"\n🔍 QUERYING DATA_SET FOR ENTITY: {entity_id}")
    print("-" * 50)

    # Query 1: Get the DATA_SET schema to see what fields are available
    print("\n🔍 QUERY 1: DATA_SET SCHEMA")
    print("-" * 40)

    dataset_schema_query = """
    query GetDataSetSchema {
      __type(name: "CreditResponseCreditSummaryDataSet") {
        name
        fields {
          name
          description
          type {
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
    """

    try:
        result = tilores_api.gql(dataset_schema_query)
        if result and 'data' in result:
            dataset_type = result['data']['__type']
            if dataset_type:
                fields = dataset_type.get('fields', [])
                print(f"   CreditResponseCreditSummaryDataSet fields: {len(fields)}")

                for field in fields:
                    field_name = field.get('name')
                    field_desc = field.get('description', 'No description')
                    field_type = field.get('type', {})
                    type_name = field_type.get('name', 'Unknown')
                    of_type = field_type.get('ofType', {})
                    of_type_name = of_type.get('name', '')

                    print(f"     - {field_name}: {type_name} {of_type_name} - {field_desc}")
            else:
                print("   ❌ CreditResponseCreditSummaryDataSet type not found")
        else:
            print("   ❌ Schema query failed")

    except Exception as e:
        print(f"   ❌ Schema query failed: {e}")

    # Query 2: Try to query the actual DATA_SET field
    print("\n🔍 QUERY 2: ACTUAL DATA_SET QUERY")
    print("-" * 40)

    dataset_query = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              Report_ID
              CREDIT_SUMMARY {
                BorrowerID
                Name
                DATA_SET {
                  # This should contain the rollup data
                }
              }
            }
          }
        }
      }
    }
    """

    try:
        result = tilores_api.gql(dataset_query, {"id": entity_id})
        if result and 'data' in result:
            print("✅ DATA_SET query executed")

            if result.get("errors"):
                print("   ❌ GraphQL errors found:")
                for error in result["errors"]:
                    print(f"     {error.get('message', 'Unknown error')}")
            else:
                print("   ✅ No GraphQL errors - DATA_SET fields exist")

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
                            borrower_id = summary.get('BorrowerID')
                            name = summary.get('Name')
                            data_set = summary.get('DATA_SET')

                            print(f"     BorrowerID: {borrower_id}")
                            print(f"     Name: {name}")
                            print(f"     DATA_SET: {data_set}")
                        else:
                            print("     CREDIT_SUMMARY: None")
        else:
            print("   ❌ DATA_SET query failed")

    except Exception as e:
        print(f"   ❌ DATA_SET query failed: {e}")

    # Query 3: Look for other potential summary fields
    print("\n🔍 QUERY 3: OTHER SUMMARY FIELDS")
    print("-" * 40)

    # Check if there are other summary fields we missed
    other_summary_query = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              Report_ID
              # Look for any fields that might contain summary data
              TotalAccounts
              TotalInquiries
              AverageScore
              TotalUtilization
              # These might be direct fields, not nested
            }
          }
        }
      }
    }
    """

    try:
        result = tilores_api.gql(other_summary_query, {"id": entity_id})
        if result and 'data' in result:
            print("✅ Other summary fields query executed")

            if result.get("errors"):
                print("   ❌ GraphQL errors found:")
                for error in result["errors"]:
                    print(f"     {error.get('message', 'Unknown error')}")
            else:
                print("   ✅ No GraphQL errors - Other summary fields may exist")
        else:
            print("   ❌ Other summary fields query failed")

    except Exception as e:
        print(f"   ❌ Other summary fields query failed: {e}")

    print("\n🎯 DATA_SET FIELD QUERY COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    query_dataset_fields()
