#!/usr/bin/env python3
"""
Phase 1: System Diagnosis & Validation
Systematically validate what's working and identify exact failure points
"""

from dotenv import load_dotenv
load_dotenv()
from typing import Dict, Any

class Phase1Diagnosis:
    """Phase 1: System Diagnosis & Validation"""

    def __init__(self):
        """Initialize Phase 1 diagnosis"""
        self.tilores_api = None
        self.diagnosis_results = {}
        self._initialize_tilores()

    def _initialize_tilores(self):
        """Initialize Tilores API connection"""
        try:
            from tilores import TiloresAPI
            self.tilores_api = TiloresAPI.from_environ()
            print("✅ Tilores API initialized successfully")
        except Exception as e:
            print(f"❌ Tilores API initialization failed: {e}")
            self.tilores_api = None

    def test_1_basic_entity_query(self, entity_id: str) -> Dict[str, Any]:
        """Test 1: Basic entity query - should work"""

        print("\n🔍 TEST 1: BASIC ENTITY QUERY")
        print("-" * 40)

        result = {
            "test_name": "Basic Entity Query",
            "status": "UNKNOWN",
            "working": False,
            "data_structure": {},
            "issues": []
        }

        try:
            # Simplest possible query
            query = """
            query BasicEntityTest {{
              entity(input: {{ id: "{entity_id}" }}) {{
                entity {{
                  id
                  records {{
                    id
                  }}
                }}
              }}
            }}
            """

            response = self.tilores_api.gql(query)

            if response and 'data' in response:
                entity = response['data']['entity']['entity']
                records = entity.get('records', [])

                result["working"] = True
                result["status"] = "PASSED"
                result["data_structure"] = {
                    "has_entity": bool(entity),
                    "has_records": bool(records),
                    "record_count": len(records),
                    "response_keys": list(response.keys())
                }

                print("✅ Basic entity query working")
                print(f"   Found {len(records)} records")

            else:
                result["status"] = "FAILED"
                result["issues"].append("Query returned no data")
                print("❌ Basic entity query failed")

        except Exception as e:
            result["status"] = "FAILED"
            result["issues"].append(f"Query execution failed: {e}")
            print(f"❌ Basic entity query failed: {e}")

        return result

    def test_2_record_insights_phone_data(self, entity_id: str) -> Dict[str, Any]:
        """Test 2: Record Insights phone data - should work"""

        print("\n🔍 TEST 2: RECORD INSIGHTS PHONE DATA")
        print("-" * 40)

        result = {
            "test_name": "Record Insights Phone Data",
            "status": "UNKNOWN",
            "working": False,
            "data_structure": {},
            "issues": []
        }

        try:
            # Test Record Insights for phone data
            query = """
            query PhoneRecordInsightsTest {{
              entity(input: {{ id: "{entity_id}" }}) {{
                entity {{
                  recordInsights {{
                    phoneNumbers: valuesDistinct(field: "PHONE_EXTERNAL")
                    createdDates: valuesDistinct(field: "CREATED_DATE")
                  }}
                }}
              }}
            }}
            """

            response = self.tilores_api.gql(query)

            if response and 'data' in response:
                record_insights = response['data']['entity']['entity']['recordInsights']
                phone_numbers = record_insights.get("phoneNumbers", [])
                created_dates = record_insights.get("createdDates", [])

                result["working"] = True
                result["status"] = "PASSED"
                result["data_structure"] = {
                    "has_record_insights": bool(record_insights),
                    "phone_numbers_count": len(phone_numbers),
                    "created_dates_count": len(created_dates),
                    "phone_numbers": phone_numbers[:3],
                    "created_dates": created_dates[:3]
                }

                print("✅ Record Insights phone data working")
                print(f"   Phone numbers: {len(phone_numbers)}")
                print(f"   Created dates: {len(created_dates)}")

            else:
                result["status"] = "FAILED"
                result["issues"].append("Record Insights query returned no data")
                print("❌ Record Insights phone data failed")

        except Exception as e:
            result["status"] = "FAILED"
            result["issues"].append(f"Record Insights query failed: {e}")
            print(f"❌ Record Insights phone data failed: {e}")

        return result

    def test_3_simple_credit_response_query(self, entity_id: str) -> Dict[str, Any]:
        """Test 3: Simple credit response query - should work"""

        print("\n🔍 TEST 3: SIMPLE CREDIT RESPONSE QUERY")
        print("-" * 40)

        result = {
            "test_name": "Simple Credit Response Query",
            "status": "UNKNOWN",
            "working": False,
            "data_structure": {},
            "issues": []
        }

        try:
            # Test simple credit response query
            query = """
            query SimpleCreditResponseTest {{
              entity(input: {{ id: "{entity_id}" }}) {{
                entity {{
                  records {{
                    CREDIT_RESPONSE {{
                      CREDIT_BUREAU
                      CreditReportFirstIssuedDate
                    }}
                  }}
                }}
              }}
            }}
            """

            response = self.tilores_api.gql(query)

            if response and 'data' in response:
                entity = response['data']['entity']['entity']
                records = entity.get('records', [])

                credit_responses = 0
                for record in records:
                    if record.get('CREDIT_RESPONSE'):
                        credit_responses += 1

                result["working"] = True
                result["status"] = "PASSED"
                result["data_structure"] = {
                    "has_entity": bool(entity),
                    "has_records": bool(records),
                    "record_count": len(records),
                    "credit_responses": credit_responses
                }

                print("✅ Simple credit response query working")
                print(f"   Found {credit_responses} credit responses")

            else:
                result["status"] = "FAILED"
                result["issues"].append("Credit response query returned no data")
                print("❌ Simple credit response query failed")

        except Exception as e:
            result["status"] = "FAILED"
            result["issues"].append(f"Credit response query failed: {e}")
            print(f"❌ Simple credit response query failed: {e}")

        return result

    def test_4_field_existence_validation(self, entity_id: str) -> Dict[str, Any]:
        """Test 4: Field existence validation"""

        print("\n🔍 TEST 4: FIELD EXISTENCE VALIDATION")
        print("-" * 40)

        result = {
            "test_name": "Field Existence Validation",
            "status": "UNKNOWN",
            "working": False,
            "data_structure": {},
            "issues": []
        }

        try:
            # Test field existence systematically
            query = """
            query FieldExistenceTest {{
              entity(input: {{ id: "{entity_id}" }}) {{
                entity {{
                  records {{
                    # Basic fields
                    EMAIL
                    FIRST_NAME
                    LAST_NAME
                    CLIENT_ID
                    PHONE_EXTERNAL
                    CREATED_DATE

                    # Credit fields
                    CREDIT_RESPONSE {{
                      CREDIT_BUREAU
                      CreditReportFirstIssuedDate
                      CREDIT_SCORE {{
                        Value
                        ModelNameType
                        Date
                      }}
                    }}

                    # Business fields
                    PRODUCT_NAME
                    TRANSACTION_AMOUNT
                    CARD_TYPE
                    STATUS
                  }}
                }}
              }}
            }}
            """

            response = self.tilores_api.gql(query)

            if response and 'data' in response:
                entity = response['data']['entity']['entity']
                records = entity.get('records', [])

                if records:
                    # Analyze field existence
                    field_analysis = {}
                    for field in ["EMAIL", "FIRST_NAME", "LAST_NAME", "CLIENT_ID", "PHONE_EXTERNAL", "CREATED_DATE", "PRODUCT_NAME", "TRANSACTION_AMOUNT", "CARD_TYPE", "STATUS"]:
                        field_analysis[field] = any(record.get(field) for record in records)

                    # Analyze credit response structure
                    credit_analysis = {
                        "has_credit_response": any(record.get('CREDIT_RESPONSE') for record in records),
                        "credit_score_count": 0,
                        "credit_score_with_values": 0,
                        "credit_score_with_dates": 0
                    }

                    for record in records:
                        credit_response = record.get('CREDIT_RESPONSE', {})
                        if credit_response:
                            credit_scores = credit_response.get('CREDIT_SCORE', [])
                            credit_analysis["credit_score_count"] += len(credit_scores)

                            for score in credit_scores:
                                if score.get('Value') and score.get('Value') != "None":
                                    credit_analysis["credit_score_with_values"] += 1
                                if score.get('Date') and score.get('Date') != "None":
                                    credit_analysis["credit_score_with_dates"] += 1

                    result["working"] = True
                    result["status"] = "PASSED"
                    result["data_structure"] = {
                        "field_existence": field_analysis,
                        "credit_analysis": credit_analysis,
                        "record_count": len(records)
                    }

                    print("✅ Field existence validation working")
                    print(f"   Basic fields: {sum(field_analysis.values())}/{len(field_analysis)} present")
                    print(f"   Credit scores: {credit_analysis['credit_score_count']} total, {credit_analysis['credit_score_with_values']} with values, {credit_analysis['credit_score_with_dates']} with dates")

                else:
                    result["status"] = "FAILED"
                    result["issues"].append("No records found for field validation")
                    print("❌ Field existence validation failed - no records")

            else:
                result["status"] = "FAILED"
                result["issues"].append("Field validation query returned no data")
                print("❌ Field existence validation failed")

        except Exception as e:
            result["status"] = "FAILED"
            result["issues"].append(f"Field validation failed: {e}")
            print(f"❌ Field existence validation failed: {e}")

        return result

    def run_phase1_diagnosis(self, entity_id: str) -> Dict[str, Any]:
        """Run complete Phase 1 diagnosis"""

        print("🚀 PHASE 1: SYSTEM DIAGNOSIS & VALIDATION")
        print("=" * 70)
        print("Goal: Validate what's working and identify exact failure points")
        print("=" * 70)

        if not self.tilores_api:
            print("❌ Cannot run diagnosis: Tilores API not available")
            return {"error": "Tilores API not available"}

        # Run all Phase 1 tests
        tests = [
            self.test_1_basic_entity_query(entity_id),
            self.test_2_record_insights_phone_data(entity_id),
            self.test_3_simple_credit_response_query(entity_id),
            self.test_4_field_existence_validation(entity_id)
        ]

        # Compile results
        working_tests = sum(1 for test in tests if test.get("working", False))
        failed_tests = sum(1 for test in tests if test.get("status") == "FAILED")
        total_issues = sum(len(test.get("issues", [])) for test in tests)

        # Overall assessment
        success_rate = working_tests / len(tests) if tests else 0

        print("\n📊 PHASE 1 DIAGNOSIS RESULTS")
        print("=" * 50)
        print(f"   ✅ Working Tests: {working_tests}/{len(tests)}")
        print(f"   ❌ Failed Tests: {failed_tests}/{len(tests)}")
        print(f"   🚨 Total Issues: {total_issues}")
        print(f"   📈 Success Rate: {success_rate:.1%}")

        # Store results
        self.diagnosis_results = {
            "success_rate": success_rate,
            "working_tests": working_tests,
            "failed_tests": failed_tests,
            "total_issues": total_issues,
            "test_details": tests,
            "phase1_complete": True
        }

        # Phase 1 validation checkpoint
        print("\n🔍 PHASE 1 VALIDATION CHECKPOINT:")
        print("-" * 40)

        if success_rate >= 0.75:
            print("   ✅ PHASE 1 COMPLETE: Ready for Phase 2")
            print("   🎯 System understanding validated")
            print("   🚀 Proceeding to incremental repair")
        elif success_rate >= 0.5:
            print("   ⚠️  PHASE 1 PARTIAL: Some validation needed")
            print("   🔍 Review failed tests before Phase 2")
            print("   📋 Adjust approach based on findings")
        else:
            print("   ❌ PHASE 1 FAILED: Major issues identified")
            print("   🚨 System understanding incomplete")
            print("   🔧 Need fundamental approach adjustment")

        return self.diagnosis_results

# Global instance
phase1_diagnosis = Phase1Diagnosis()

if __name__ == "__main__":
    print("🚀 PHASE 1: SYSTEM DIAGNOSIS & VALIDATION")
    print("=" * 70)

    # Use known test entity
    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    print("🔍 Running Phase 1 diagnosis...")
    results = phase1_diagnosis.run_phase1_diagnosis(entity_id)

    print("\n🎯 PHASE 1 DIAGNOSIS COMPLETE")
    print("=" * 70)
    print(f"Success Rate: {results.get('success_rate', 0):.1%}")
    print(f"Working Tests: {results.get('working_tests', 0)}")
    print(f"Failed Tests: {results.get('failed_tests', 0)}")
    print(f"Total Issues: {results.get('total_issues', 0)}")

    if results.get('phase1_complete'):
        print("\n✅ PHASE 1 COMPLETE - Ready for Phase 2")
    else:
        print("\n❌ PHASE 1 INCOMPLETE - Review needed")
