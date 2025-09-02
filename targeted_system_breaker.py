#!/usr/bin/env python3
"""
Targeted System Breaker - QA Agent
Further exposes system vulnerabilities and tests specific failure points
"""

from dotenv import load_dotenv
load_dotenv()

def test_specific_failure_points():
    """Test specific points of failure to break the system"""

    print("🚨 TARGETED SYSTEM BREAKER - QA AGENT")
    print("=" * 70)
    print("Goal: Expose specific vulnerabilities and break system components")
    print("=" * 70)

    try:
        from tilores import TiloresAPI
        tilores_api = TiloresAPI.from_environ()
        print("✅ Tilores API initialized")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return

    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    # Test 1: Malformed GraphQL query
    print("\n🔍 TEST 1: MALFORMED GRAPHQL QUERY")
    print("-" * 40)

    malformed_query = """
    query MalformedQuery {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_SCORE {{
                Value
                Date
                # Missing closing brace to break syntax
              }}
            }}
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(malformed_query)
        print("❌ FAILED: Malformed query should have caused error")
    except Exception as e:
        print(f"✅ SUCCESS: Malformed query properly rejected: {e}")

    # Test 2: Non-existent fields
    print("\n🔍 TEST 2: NON-EXISTENT FIELDS")
    print("-" * 40)

    nonexistent_query = """
    query NonExistentFields {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            NONEXISTENT_FIELD {{
              FAKE_SUBFIELD
            }}
            ANOTHER_FAKE_FIELD
            CREDIT_RESPONSE {{
              CREDIT_SCORE {{
                Value
                ModelNameType
                FAKE_SCORE_FIELD
              }}
            }}
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(nonexistent_query)
        if result and 'data' in result:
            print("❌ FAILED: Query with non-existent fields should have failed")
        else:
            print("✅ SUCCESS: Non-existent fields properly handled")
    except Exception as e:
        print(f"✅ SUCCESS: Non-existent fields properly rejected: {e}")

    # Test 3: Deep nesting attack
    print("\n🔍 TEST 3: DEEP NESTING ATTACK")
    print("-" * 40)

    deep_nesting_query = """
    query DeepNestingAttack {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_SCORE {{
                FACTOR {{
                  Code
                  Text
                  Factor_Type
                  # Deep nesting to test limits
                  NESTED_LEVEL_1 {{
                    NESTED_LEVEL_2 {{
                      NESTED_LEVEL_3 {{
                        NESTED_LEVEL_4 {{
                          NESTED_LEVEL_5
                        }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(deep_nesting_query)
        if result and 'data' in result:
            print("❌ FAILED: Deep nesting should have been rejected")
        else:
            print("✅ SUCCESS: Deep nesting properly handled")
    except Exception as e:
        print(f"✅ SUCCESS: Deep nesting properly rejected: {e}")

    # Test 4: Large result set attack
    print("\n🔍 TEST 4: LARGE RESULT SET ATTACK")
    print("-" * 40)

    large_result_query = """
    query LargeResultSetAttack {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CREDIT_SCORE {{
                Value
                ModelNameType
                CreditRepositorySourceType
                Date
                CreditScoreID
                CreditFileID
                BorrowerID
                FACTOR {{
                  Code
                  Text
                  Factor_Type
                }}
              }}
              CREDIT_LIABILITY {{
                AccountType
                AccountStatusType
                CreditLimitAmount
                CreditBalance
                UnpaidBalanceAmount
                HighCreditAmount
                AccountOpenedDate
                AccountClosedDate
                LastPaymentDate
                PaymentPattern {{
                  Data
                  StartDate
                }}
                LateCount {{
                  Days30
                  Days60
                  Days90
                }}
                CurrentRating {{
                  Code
                  Type
                }}
                Creditor {{
                  Name
                  City
                  State
                }}
              }}
              CREDIT_INQUIRY {{
                Date
                Name
                City
                State
                PurposeType
                CreditBusinessType
              }}
              CREDIT_SUMMARY {{
                Name
                DATA_SET {{
                  ID
                  Name
                  Value
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(large_result_query)
        if result and 'data' in result:
            print("✅ SUCCESS: Large result set handled properly")
        else:
            print("❌ FAILED: Large result set should have returned data")
    except Exception as e:
        print(f"❌ FAILED: Large result set caused error: {e}")

    # Test 5: Mixed data type attack
    print("\n🔍 TEST 5: MIXED DATA TYPE ATTACK")
    print("-" * 40)

    mixed_type_query = """
    query MixedDataTypeAttack {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            # Mix different data types to test handling
            EMAIL
            FIRST_NAME
            LAST_NAME
            CLIENT_ID
            PHONE_EXTERNAL
            CREATED_DATE
            CREDIT_RESPONSE {{
              CREDIT_SCORE {{
                Value
                ModelNameType
              }}
            }}
            # Business data
            PRODUCT_NAME
            TRANSACTION_AMOUNT
            CARD_TYPE
            STATUS
            # Temporal data
            UPDATED_DATE
            ENROLL_DATE
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(mixed_type_query)
        if result and 'data' in result:
            records = result['data']['entity']['entity']['records']
            if records:
                print("✅ SUCCESS: Mixed data types handled properly")
                print(f"   Found {len(records)} records with mixed data")
            else:
                print("❌ FAILED: Mixed data query returned no records")
        else:
            print("❌ FAILED: Mixed data query failed")
    except Exception as e:
        print(f"❌ FAILED: Mixed data query caused error: {e}")

    # Test 6: Temporal comparison attack
    print("\n🔍 TEST 6: TEMPORAL COMPARISON ATTACK")
    print("-" * 40)

    temporal_attack_query = """
    query TemporalComparisonAttack {{
      entity(input: {{ id: "{entity_id}" }}) {{
        entity {{
          records {{
            CREDIT_RESPONSE {{
              CreditReportFirstIssuedDate
              CREDIT_SCORE {{
                Value
                Date
                CreditReportFirstIssuedDate
              }}
              CREDIT_FILE {{
                InfileDate
                ResultStatusType
              }}
            }}
            PHONE_EXTERNAL
            CREATED_DATE
            UPDATED_DATE
            PRODUCT_NAME
            TRANSACTION_AMOUNT
          }}
        }}
      }}
    }}
    """

    try:
        result = tilores_api.gql(temporal_attack_query)
        if result and 'data' in result:
            records = result['data']['entity']['entity']['records']
            if records:
                # Analyze temporal data integrity
                temporal_issues = []
                credit_data_count = 0
                phone_data_count = 0
                correlation_count = 0

                for record in records:
                    if record.get('CREDIT_RESPONSE'):
                        credit_data_count += 1
                    if record.get('PHONE_EXTERNAL'):
                        phone_data_count += 1
                    if (record.get('CREDIT_RESPONSE') and
                        record.get('PHONE_EXTERNAL') and
                        record.get('CREATED_DATE')):
                        correlation_count += 1

                if credit_data_count == 0:
                    temporal_issues.append("No credit data for temporal analysis")
                if phone_data_count == 0:
                    temporal_issues.append("No phone data for temporal analysis")
                if correlation_count == 0:
                    temporal_issues.append("No cross-data correlation possible")

                if temporal_issues:
                    print("❌ FAILED: Temporal comparison vulnerabilities found:")
                    for issue in temporal_issues:
                        print(f"   • {issue}")
                else:
                    print("✅ SUCCESS: Temporal comparison data integrity maintained")
            else:
                print("❌ FAILED: Temporal query returned no records")
        else:
            print("❌ FAILED: Temporal query failed")
    except Exception as e:
        print(f"❌ FAILED: Temporal query caused error: {e}")

    print("\n🎯 TARGETED SYSTEM BREAKER COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    test_specific_failure_points()
