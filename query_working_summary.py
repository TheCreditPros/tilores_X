#!/usr/bin/env python3
"""
Query Working Credit Summary
Query the working CREDIT_SUMMARY fields to see rollup data
"""

from dotenv import load_dotenv
load_dotenv()

def query_working_summary():
    """Query the working CREDIT_SUMMARY fields"""

    print("🔍 QUERYING WORKING CREDIT_SUMMARY FIELDS")
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

    print(f"\n🔍 QUERYING CREDIT_SUMMARY FOR ENTITY: {entity_id}")
    print("-" * 50)

    # Query the working CREDIT_SUMMARY fields
    working_summary_query = """
    query($id:ID!){
      entity(input:{id:$id}){
        entity{
          records {
            CREDIT_RESPONSE {
              CREDIT_BUREAU
              CreditReportFirstIssuedDate
              Report_ID
              CREDIT_SCORE {
                Value
                ModelNameType
                CreditRepositorySourceType
              }
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
        result = tilores_api.gql(working_summary_query, {"id": entity_id})
        if result and 'data' in result:
            print("✅ CREDIT_SUMMARY query executed successfully!")

            if result.get("errors"):
                print("   ❌ GraphQL errors found:")
                for error in result["errors"]:
                    print(f"     {error.get('message', 'Unknown error')}")
            else:
                print("   ✅ No GraphQL errors - CREDIT_SUMMARY data retrieved!")

                # Display the data
                entity = result['data']['entity']['entity']
                records = entity.get('records', [])

                print("\n📊 CREDIT_SUMMARY DATA:")
                print(f"   Total records: {len(records)}")

                for i, record in enumerate(records):
                    credit_response = record.get('CREDIT_RESPONSE')
                    if credit_response:
                        bureau = credit_response.get('CREDIT_BUREAU')
                        date = credit_response.get('CreditReportFirstIssuedDate')
                        report_id = credit_response.get('Report_ID')
                        summary = credit_response.get('CREDIT_SUMMARY')

                        print(f"\n   Record {i + 1}: {bureau} | {date} | {report_id}")

                        if summary:
                            borrower_id = summary.get('BorrowerID')
                            name = summary.get('Name')
                            data_set = summary.get('DATA_SET')

                            print("     CREDIT_SUMMARY:")
                            print(f"       BorrowerID: {borrower_id}")
                            print(f"       Name: {name}")
                            print(f"       DATA_SET: {data_set}")

                            # If DATA_SET has data, explore it further
                            if data_set:
                                print("       🎯 DATA_SET contains rollup data!")
                            else:
                                print("       ⚠️  DATA_SET is empty")
                        else:
                            print("     CREDIT_SUMMARY: None")

                        # Also show the scores for context
                        scores = credit_response.get('CREDIT_SCORE', [])
                        if scores:
                            print(f"     CREDIT_SCORE: {len(scores)} scores")
                            for score in scores:
                                value = score.get('Value')
                                model = score.get('ModelNameType')
                                source = score.get('CreditRepositorySourceType')
                                print(f"       - {value} | {model} | {source}")
        else:
            print("   ❌ CREDIT_SUMMARY query failed")

    except Exception as e:
        print(f"   ❌ CREDIT_SUMMARY query failed: {e}")

    # Now try to query the DATA_SET fields specifically
    print("\n🔍 QUERYING DATA_SET FIELDS")
    print("-" * 40)

    # Get the DATA_SET schema to see what fields are available
    dataset_schema_query = """
    query GetDataSetFields {
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

                    print(f"     - {field_name}: {type_name} - {field_desc}")

                    # If this field has sub-fields, explore them
                    if type_name and type_name != 'Unknown':
                        try:
                            sub_schema_query = """
                            query GetSubFields {{
                              __type(name: "{type_name}") {{
                                name
                                fields {{
                                  name
                                  description
                                  type {{
                                    name
                                    kind
                                  }}
                                }}
                              }}
                            }}
                            """

                            sub_result = tilores_api.gql(sub_schema_query)
                            if sub_result and 'data' in sub_result:
                                sub_type = sub_result['data']['__type']
                                if sub_type:
                                    sub_fields = sub_type.get('fields', [])
                                    if sub_fields:
                                        print(f"       Sub-fields ({len(sub_fields)}):")
                                        for sub_field in sub_fields[:5]:  # Show first 5
                                            sub_name = sub_field.get('name')
                                            sub_desc = sub_field.get('description', 'No description')
                                            print(f"         - {sub_name}: {sub_desc}")
                                        if len(sub_fields) > 5:
                                            print(f"         ... and {len(sub_fields) - 5} more")
                        except Exception as e:
                            # Skip if sub-field exploration fails
                            pass
            else:
                print("   ❌ CreditResponseCreditSummaryDataSet type not found")
        else:
            print("   ❌ DATA_SET schema query failed")

    except Exception as e:
        print(f"   ❌ DATA_SET schema query failed: {e}")

    print("\n🎯 WORKING SUMMARY QUERY COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    query_working_summary()
