#!/usr/bin/env python3
"""
Discover Credit Report Summary Parameters
Find the 100+ summary parameters that provide rollup information
Instead of manual calculations for utilization, inquiries, etc.
"""

from dotenv import load_dotenv
load_dotenv()

def discover_summary_parameters():
    """Discover credit report summary parameters from the schema"""

    print("🔍 DISCOVERING CREDIT REPORT SUMMARY PARAMETERS")
    print("=" * 60)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized successfully")
    except Exception as e:
        print(f"❌ Tilores API initialization failed: {e}")
        return

    # Step 1: Get the full schema to find summary parameters
    print("\n🔍 STEP 1: FULL SCHEMA INTROSPECTION")
    print("-" * 50)

    full_schema_query = """
    query FullSchemaIntrospection {
      __schema {
        types {
          name
          kind
          description
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
    }
    """

    try:
        resp = tilores_api.gql(full_schema_query)
        types = (resp.get("data") or {}).get("__schema", {}).get("types", []) or []

        print("📊 SCHEMA INTROSPECTION RESULTS:")
        print(f"   Total types found: {len(types)}")

        # Look for credit-related types
        credit_types = []
        for t in types:
            type_name = t.get("name", "")
            if any(keyword in type_name.lower() for keyword in ["credit", "report", "summary", "response"]):
                credit_types.append(t)

        print(f"   Credit-related types: {len(credit_types)}")

        # Display credit-related types
        for t in credit_types:
            print(f"\n   📋 Type: {t.get('name')}")
            print(f"      Kind: {t.get('kind')}")
            print(f"      Description: {t.get('description', 'No description')}")

            fields = t.get("fields", [])
            if fields:
                print(f"      Fields: {len(fields)}")

                # Look for summary/rollup fields
                summary_fields = []
                for field in fields:
                    field_name = field.get("name", "")
                    # field_desc = field.get("description", "")  # Not currently used

                    # Look for fields that might be summary parameters
                    if any(keyword in field_name.lower() for keyword in ["total", "count", "summary", "aggregate", "rollup", "utilization", "inquiry"]):
                        summary_fields.append(field)

                if summary_fields:
                    print(f"      Summary fields found: {len(summary_fields)}")
                    for field in summary_fields[:10]:  # Show first 10
                        print(f"        - {field['name']}: {field['description']}")
                    if len(summary_fields) > 10:
                        print(f"        ... and {len(summary_fields) - 10} more")

        # Step 2: Look specifically at CREDIT_RESPONSE fields
        print("\n🔍 STEP 2: CREDIT_RESPONSE FIELD ANALYSIS")
        print("-" * 50)

        credit_response_type = None
        for t in types:
            if t.get("name") == "CREDIT_RESPONSE":
                credit_response_type = t
                break

        if credit_response_type:
            fields = credit_response_type.get("fields", [])
            print(f"   CREDIT_RESPONSE fields: {len(fields)}")

            # Look for summary parameters
            summary_params = []
            for field in fields:
                field_name = field.get("name", "")
                # # field_desc = field.get("description", "")  # Not currently used  # Not currently used

                # Look for fields that provide rollup/summary information
                if any(keyword in field_name.lower() for keyword in [
                    "total", "count", "summary", "aggregate", "rollup",
                    "utilization", "inquiry", "balance", "limit", "payment",
                    "late", "delinquent", "account", "score", "bureau"
                ]):
                    summary_params.append(field)

            if summary_params:
                print(f"   Summary parameters found: {len(summary_params)}")
                print("\n   📊 SUMMARY PARAMETERS:")
                for field in summary_params:
                    print(f"     - {field['name']}: {field['description']}")
            else:
                print("   ❌ No summary parameters found in CREDIT_RESPONSE")
        else:
            print("   ❌ CREDIT_RESPONSE type not found")

        # Step 3: Test a query with potential summary fields
        print("\n🔍 STEP 3: TESTING SUMMARY PARAMETER QUERY")
        print("-" * 50)

        # Use the working entity ID
        entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

        # Query with potential summary fields
        summary_test_query = """
        query($id:ID!){
          entity(input:{id:$id}){
            entity{
              records {
                CREDIT_RESPONSE {
                  CREDIT_BUREAU
                  CreditReportFirstIssuedDate
                  Report_ID
                  # Try to find summary fields
                  TotalAccounts
                  TotalInquiries
                  TotalUtilization
                  AverageScore
                  TotalLatePayments
                  TotalDelinquentAccounts
                  CreditLimitTotal
                  CreditBalanceTotal
                  # Add more potential summary fields
                }
              }
            }
          }
        }
        """

        try:
            result = tilores_api.gql(summary_test_query, {"id": entity_id})
            if result and 'data' in result:
                print("✅ Summary parameter query executed")

                # Check for errors to see which fields don't exist
                if result.get("errors"):
                    print("   ❌ GraphQL errors found:")
                    for error in result["errors"]:
                        print(f"     {error.get('message', 'Unknown error')}")
                else:
                    print("   ✅ No GraphQL errors - summary fields may exist")

            else:
                print("   ❌ Summary parameter query failed")

        except Exception as e:
            print(f"   ❌ Summary parameter test failed: {e}")

    except Exception as e:
        print(f"❌ Schema introspection failed: {e}")

    print("\n🎯 SUMMARY PARAMETER DISCOVERY COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    discover_summary_parameters()
