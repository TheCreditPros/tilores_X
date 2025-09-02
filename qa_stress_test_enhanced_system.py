#!/usr/bin/env python3
"""
QA Stress Testing - Enhanced Temporal Credit System
Intentional system breaking and stress testing
"""

from dotenv import load_dotenv
load_dotenv()

def qa_stress_test_enhanced_system():
    """QA stress testing of enhanced temporal credit system"""

    print("🔍 QA STRESS TESTING - ENHANCED TEMPORAL CREDIT SYSTEM")
    print("=" * 70)
    print("Goal: Intentionally break and stress test the system")
    print("=" * 70)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized successfully")
    except Exception as e:
        print(f"❌ Tilores API initialization failed: {e}")
        return

    # Use the working entity ID
    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    print(f"\n🎯 STRESS TESTING ENTITY: {entity_id}")
    print("-" * 50)

    # Test 1: Malformed GraphQL queries
    print("\n🔍 TEST 1: MALFORMED GRAPHQL QUERIES")
    print("-" * 40)

    malformed_queries = [
        # Missing required fields
        """
        query($id:ID!){
          entity(input:{id:$id}){
            entity{
              records {
                CREDIT_RESPONSE {
                  # Missing CREDIT_BUREAU
                  CreditReportFirstIssuedDate
                }
              }
            }
          }
        }
        """,

        # Invalid field names
        """
        query($id:ID!){
          entity(input:{id:$id}){
            entity{
              records {
                CREDIT_RESPONSE {
                  CREDIT_BUREAU
                  INVALID_FIELD_NAME
                  CREDIT_SUMMARY {
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
        """,

        # Deep nesting attack
        """
        query($id:ID!){
          entity(input:{id:$id}){
            entity{
              records {
                CREDIT_RESPONSE {
                  CREDIT_BUREAU
                  CreditReportFirstIssuedDate
                  CREDIT_SUMMARY {
                    DATA_SET {
                      ID
                      Name
                      Value
                      NESTED_FIELD {
                        DEEPER_NESTED {
                          EVEN_DEEPER {
                            TOO_DEEP {
                              SHOULD_FAIL {
                                field: "value"
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """,

        # Large result set attack
        """
        query($id:ID!){
          entity(input:{id:$id}){
            entity{
              records {
                CREDIT_RESPONSE {
                  CREDIT_BUREAU
                  CreditReportFirstIssuedDate
                  CREDIT_SCORE {
                    Value
                    ModelNameType
                    CreditRepositorySourceType
                  }
                  CREDIT_SUMMARY {
                    DATA_SET {
                      ID
                      Name
                      Value
                    }
                  }
                  CREDIT_LIABILITY {
                    AccountType
                    CreditLimitAmount
                    CreditBalance
                    LateCount {
                      Days30
                      Days60
                      Days90
                    }
                  }
                }
              }
            }
          }
        }
        """
    ]

    for i, query in enumerate(malformed_queries, 1):
        try:
            print(f"   Testing malformed query {i}...")
            result = tilores_api.gql(query, {"id": entity_id})

            if result and 'data' in result:
                print(f"     ❌ Query {i} should have failed but succeeded")
            elif result.get("errors"):
                print(f"     ✅ Query {i} correctly failed with errors")
                for error in result["errors"]:
                    print(f"       Error: {error.get('message', 'Unknown error')}")
            else:
                print(f"     ⚠️  Query {i} failed silently")

        except Exception as e:
            print(f"     ✅ Query {i} correctly failed with exception: {e}")

    # Test 2: Edge case data handling
    print("\n🔍 TEST 2: EDGE CASE DATA HANDLING")
    print("-" * 40)

    edge_case_query = """
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
        result = tilores_api.gql(edge_case_query, {"id": entity_id})
        if result and 'data' in result:
            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            print("   Testing edge case data handling...")
            print(f"   Total records: {len(records)}")

            # Test with None values
            for i, record in enumerate(records):
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    bureau = credit_response.get('CREDIT_BUREAU')
                    date = credit_response.get('CreditReportFirstIssuedDate')
                    summary = credit_response.get('CREDIT_SUMMARY', {})
                    data_set = summary.get('DATA_SET', [])

                    print(f"     Record {i + 1}: Bureau={bureau}, Date={date}")

                    # Test None handling in summary parameters
                    if data_set:
                        for param in data_set:
                            param_id = param.get('ID')
                            param_name = param.get('Name')
                            param_value = param.get('Value')

                            # Test edge cases
                            if param_value == "None" or param_value == "N/A" or param_value == "-3" or param_value == "-4" or param_value == "-5":
                                print(f"       Edge case value: {param_name} = {param_value}")

                    # Test missing fields
                    missing_fields = []
                    if not bureau:
                        missing_fields.append("CREDIT_BUREAU")
                    if not date:
                        missing_fields.append("CreditReportFirstIssuedDate")
                    if not summary:
                        missing_fields.append("CREDIT_SUMMARY")

                    if missing_fields:
                        print(f"       Missing fields: {missing_fields}")

        else:
            print("   ❌ Edge case query failed")

    except Exception as e:
        print(f"   ❌ Edge case testing failed: {e}")

    # Test 3: Performance stress testing
    print("\n🔍 TEST 3: PERFORMANCE STRESS TESTING")
    print("-" * 40)

    performance_query = """
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
              CREDIT_LIABILITY {
                AccountType
                CreditLimitAmount
                CreditBalance
                LateCount {
                  Days30
                  Days60
                  Days90
                }
              }
            }
          }
        }
      }
    }
    """

    try:
        print("   Testing performance with large data retrieval...")
        import time

        start_time = time.time()
        result = tilores_api.gql(performance_query, {"id": entity_id})
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"   Query execution time: {execution_time:.2f} seconds")

        if execution_time > 5.0:
            print(f"     ⚠️  Performance warning: Query took {execution_time:.2f}s (>5s threshold)")
        else:
            print(f"     ✅ Performance acceptable: {execution_time:.2f}s")

        if result and 'data' in result:
            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            # Count total data points
            total_data_points = 0
            for record in records:
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    scores = credit_response.get('CREDIT_SCORE', [])
                    summary = credit_response.get('CREDIT_SUMMARY', {})
                    data_set = summary.get('DATA_SET', [])
                    liabilities = credit_response.get('CREDIT_LIABILITY', [])

                    total_data_points += len(scores) + len(data_set) + len(liabilities)

            print(f"   Total data points retrieved: {total_data_points}")

            if total_data_points > 1000:
                print(f"     ⚠️  Large dataset warning: {total_data_points} data points")
            else:
                print(f"     ✅ Dataset size acceptable: {total_data_points} data points")

        else:
            print("   ❌ Performance query failed")

    except Exception as e:
        print(f"   ❌ Performance testing failed: {e}")

    # Test 4: Error handling robustness
    print("\n🔍 TEST 4: ERROR HANDLING ROBUSTNESS")
    print("-" * 40)

    # error_test_queries = [
    # # Invalid entity ID
    # """
    # query($id:ID!){
    # entity(input:{id:$id}){
    # entity{
    # records {
    # CREDIT_RESPONSE {
    # CREDIT_BUREAU
    # }
    # }
    # }
    # }
    # }
    # """,
    #     # # Empty entity ID
    # """
    # query($id:ID!){
    # entity(input:{id:""}){
    # entity{
    # records {
    # CREDIT_RESPONSE {
    # CREDIT_BUREAU
    # }
    # }
    # }
    # }
    # }
    # """,
    #     # # Null entity ID
    # """
    # query($id:ID!){
    # entity(input:{id:null}){
    # entity{
    # records {
    # CREDIT_RESPONSE {
    # CREDIT_BUREAU
    # }
    # }
    # }
    # }
    # }
    # """
    # ]

    invalid_ids = ["invalid-uuid", "", "null", "00000000 - 0000 - 0000 - 0000 - 000000000000"]

    for i, invalid_id in enumerate(invalid_ids):
        try:
            print(f"   Testing invalid entity ID: '{invalid_id}'")
            result = tilores_api.gql(edge_case_query, {"id": invalid_id})

            if result and 'data' in result:
                entity = result['data']['entity']['entity']
                if entity:
                    print(f"     ❌ Invalid ID '{invalid_id}' returned data when it should have failed")
                else:
                    print(f"     ✅ Invalid ID '{invalid_id}' correctly returned no entity data")
            elif result.get("errors"):
                print(f"     ✅ Invalid ID '{invalid_id}' correctly failed with errors")
                for error in result["errors"]:
                    print(f"       Error: {error.get('message', 'Unknown error')}")
            else:
                print(f"     ⚠️  Invalid ID '{invalid_id}' failed silently")

        except Exception as e:
            print(f"     ✅ Invalid ID '{invalid_id}' correctly failed with exception: {e}")

    # Test 5: Data integrity validation
    print("\n🔍 TEST 5: DATA INTEGRITY VALIDATION")
    print("-" * 40)

    integrity_query = """
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
        result = tilores_api.gql(integrity_query, {"id": entity_id})
        if result and 'data' in result:
            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            print("   Testing data integrity...")
            print(f"   Total records: {len(records)}")

            # Validate data consistency
            integrity_issues = []

            for i, record in enumerate(records):
                credit_response = record.get('CREDIT_RESPONSE')
                if credit_response:
                    bureau = credit_response.get('CREDIT_BUREAU')
                    date = credit_response.get('CreditReportFirstIssuedDate')
                    scores = credit_response.get('CREDIT_SCORE', [])
                    summary = credit_response.get('CREDIT_SUMMARY', {})
                    data_set = summary.get('DATA_SET', [])

                    # Check for data consistency issues
                    if bureau and date:
                        # Validate date format
                        if not isinstance(date, str) or len(date) != 10:
                            integrity_issues.append(f"Record {i + 1}: Invalid date format '{date}'")

                        # Validate bureau values
                        valid_bureaus = ['Equifax', 'Experian', 'TransUnion', 'TU', 'EXP', 'EFX']
                        if bureau not in valid_bureaus:
                            integrity_issues.append(f"Record {i + 1}: Invalid bureau '{bureau}'")

                    # Validate score data
                    for score in scores:
                        value = score.get('Value')
                        if value and value != "None":
                            try:
                                int(value)
                            except ValueError:
                                integrity_issues.append(f"Record {i + 1}: Invalid score value '{value}'")

                    # Validate summary parameters
                    for param in data_set:
                        param_id = param.get('ID')
                        param_name = param.get('Name')
                        param_value = param.get('Value')

                        if not param_id or not param_name:
                            integrity_issues.append(f"Record {i + 1}: Missing parameter ID or Name")

                        if param_value == "None" and param_name:
                            # Check if this is expected behavior
                            print(f"       Note: Parameter '{param_name}' has value 'None'")

            if integrity_issues:
                print("     ❌ Data integrity issues found:")
                for issue in integrity_issues:
                    print(f"       - {issue}")
            else:
                print("     ✅ Data integrity validation passed")

        else:
            print("   ❌ Integrity query failed")

    except Exception as e:
        print(f"   ❌ Data integrity testing failed: {e}")

    # Final Summary
    print("\n📊 QA STRESS TESTING RESULTS")
    print("=" * 50)
    print("🔍 STRESS TESTING COMPLETE!")
    print("   🎯 System tested for:")
    print("      • Malformed GraphQL queries")
    print("      • Edge case data handling")
    print("      • Performance under load")
    print("      • Error handling robustness")
    print("      • Data integrity validation")

    print("\n🎯 ENHANCED SYSTEM STRESS TESTING COMPLETE!")
    print("=" * 50)

if __name__ == "__main__":
    qa_stress_test_enhanced_system()
