#!/usr/bin/env python3
"""
Query DATA_SET Values
Query the actual DATA_SET values to see what summary parameters are available
"""

from dotenv import load_dotenv
load_dotenv()

def query_dataset_values():
    """Query the actual DATA_SET values for summary parameters"""

    print("🔍 QUERYING DATA_SET VALUES FOR SUMMARY PARAMETERS")
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

    print(f"\n🔍 QUERYING DATA_SET VALUES FOR ENTITY: {entity_id}")
    print("-" * 50)

    # Query the DATA_SET with the correct field structure
    dataset_values_query = """
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
                  ID
                  Name
                  Value
                }
              }
            }
          }
        }
      }
    }
    """

    try:
        result = tilores_api.gql(dataset_values_query, {"id": entity_id})
        if result and 'data' in result:
            print("✅ DATA_SET values query executed successfully!")

            if result.get("errors"):
                print("   ❌ GraphQL errors found:")
                for error in result["errors"]:
                    print(f"     {error.get('message', 'Unknown error')}")
            else:
                print("   ✅ No GraphQL errors - DATA_SET values retrieved!")

                # Display the data
                entity = result['data']['entity']['entity']
                records = entity.get('records', [])

                print("\n📊 DATA_SET VALUES:")
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
                            data_set = summary.get('DATA_SET', [])

                            print("     CREDIT_SUMMARY:")
                            print(f"       BorrowerID: {borrower_id}")
                            print(f"       Name: {name}")

                            if data_set:
                                print(f"       🎯 DATA_SET contains {len(data_set)} summary parameters:")

                                # Group summary parameters by category
                                categories = {
                                    'accounts': [],
                                    'utilization': [],
                                    'inquiries': [],
                                    'scores': [],
                                    'payments': [],
                                    'other': []
                                }

                                for param in data_set:
                                    param_id = param.get('ID')
                                    param_name = param.get('Name')
                                    param_value = param.get('Value')

                                    # Categorize the parameter
                                    if any(keyword in param_name.lower() for keyword in ['account', 'total']):
                                        categories['accounts'].append((param_name, param_value))
                                    elif any(keyword in param_name.lower() for keyword in ['utilization', 'balance', 'limit']):
                                        categories['utilization'].append((param_name, param_value))
                                    elif any(keyword in param_name.lower() for keyword in ['inquiry', 'inquiries']):
                                        categories['inquiries'].append((param_name, param_value))
                                    elif any(keyword in param_name.lower() for keyword in ['score', 'average']):
                                        categories['scores'].append((param_name, param_value))
                                    elif any(keyword in param_name.lower() for keyword in ['payment', 'late', 'delinquent']):
                                        categories['payments'].append((param_name, param_value))
                                    else:
                                        categories['other'].append((param_name, param_value))

                                # Display categorized parameters
                                for category, params in categories.items():
                                    if params:
                                        print(f"         📋 {category.upper()}:")
                                        for param_name, param_value in params:
                                            print(f"           - {param_name}: {param_value}")
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
            print("   ❌ DATA_SET values query failed")

    except Exception as e:
        print(f"   ❌ DATA_SET values query failed: {e}")

    print("\n🎯 DATA_SET VALUES QUERY COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    query_dataset_values()
