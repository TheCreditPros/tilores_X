#!/usr/bin/env python3
"""
QA Credit Pros System Breaker
Act as a QA agent testing real credit repair client questions
Goal: Break the system and identify data integrity issues
"""

from dotenv import load_dotenv
load_dotenv()
from typing import Dict, Any

class QACreditProsBreaker:
    """QA Agent for Credit Pros System Breaking"""

    def __init__(self):
        """Initialize QA breaker"""
        self.tilores_api = None
        self.breaking_results = []
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

    def test_1_complex_utilization_comparison(self, entity_id: str) -> Dict[str, Any]:
        """Test 1: Complex Credit Utilization Comparison - Should break the system"""

        print("\n🔍 TEST 1: COMPLEX CREDIT UTILIZATION COMPARISON")
        print("-" * 60)
        print("Question: 'Compare the credit card utilization of the most recent")
        print("Experian report against their second to oldest Experian credit report'")
        print("-" * 60)

        result = {
            "test_name": "Complex Utilization Comparison",
            "question": "Compare Experian utilization across time periods",
            "expected_failure": True,
            "actual_result": "UNKNOWN",
            "data_integrity": "UNKNOWN",
            "breaking_points": [],
            "response_quality": "UNKNOWN"
        }

        try:
            # This query should be complex enough to break the system
            query = """
            query ComplexUtilizationComparison {{
              entity(input: {{ id: "{entity_id}" }}) {{
                entity {{
                  records {{
                    CREDIT_RESPONSE {{
                      CREDIT_BUREAU
                      CreditReportFirstIssuedDate
                      CREDIT_SCORE {{
                        Value
                        ModelNameType
                        Date
                      }}
                      CREDIT_LIABILITY {{
                        AccountType
                        CreditLimitAmount
                        CreditBalance
                        AccountOpenedDate
                        AccountClosedDate
                        PaymentPattern {{
                          Data
                          StartDate
                        }}
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

            response = self.tilores_api.gql(query)

            if response and 'data' in response:
                entity = response['data']['entity']['entity']
                records = entity.get('records', [])

                # Analyze response integrity
                data_analysis = {
                    "total_records": len(records),
                    "credit_responses": 0,
                    "credit_scores": 0,
                    "credit_liabilities": 0,
                    "utilization_data": 0,
                    "temporal_data": 0,
                    "missing_critical_fields": []
                }

                for record in records:
                    credit_response = record.get('CREDIT_RESPONSE')
                    if credit_response:
                        data_analysis["credit_responses"] += 1

                        # Check for critical missing fields
                        if not credit_response.get('CreditReportFirstIssuedDate'):
                            data_analysis["missing_critical_fields"].append("CreditReportFirstIssuedDate")

                        if not credit_response.get('CREDIT_SCORE'):
                            data_analysis["missing_critical_fields"].append("CREDIT_SCORE")

                        # Count data availability
                        credit_scores = credit_response.get('CREDIT_SCORE', [])
                        data_analysis["credit_scores"] += len(credit_scores)

                        credit_liabilities = credit_response.get('CREDIT_LIABILITY', [])
                        data_analysis["credit_liabilities"] += len(credit_liabilities)

                        # Check utilization data
                        for liability in credit_liabilities:
                            if (liability.get('CreditLimitAmount') and
                                liability.get('CreditBalance')):
                                data_analysis["utilization_data"] += 1

                        # Check temporal data
                        if credit_response.get('CreditReportFirstIssuedDate'):
                            data_analysis["temporal_data"] += 1

                # Assess breaking points
                breaking_points = []
                if data_analysis["utilization_data"] == 0:
                    breaking_points.append("No utilization data available for comparison")

                if data_analysis["temporal_data"] < 2:
                    breaking_points.append("Insufficient temporal data for comparison")

                if len(data_analysis["missing_critical_fields"]) > 0:
                    breaking_points.append(f"Missing critical fields: {data_analysis['missing_critical_fields']}")

                # Determine if system is broken
                system_broken = len(breaking_points) > 0

                result["actual_result"] = "BROKEN" if system_broken else "WORKING"
                result["breaking_points"] = breaking_points
                result["data_integrity"] = "LOW" if system_broken else "HIGH"
                result["response_quality"] = "POOR" if system_broken else "GOOD"

                print("📊 RESPONSE ANALYSIS:")
                print(f"   Total records: {data_analysis['total_records']}")
                print(f"   Credit responses: {data_analysis['credit_responses']}")
                print(f"   Credit scores: {data_analysis['credit_scores']}")
                print(f"   Credit liabilities: {data_analysis['credit_liabilities']}")
                print(f"   Utilization data: {data_analysis['utilization_data']}")
                print(f"   Temporal data: {data_analysis['temporal_data']}")

                if breaking_points:
                    print("\n🚨 SYSTEM BREAKING POINTS IDENTIFIED:")
                    for i, point in enumerate(breaking_points, 1):
                        print(f"   {i}. {point}")
                    print("\n❌ SYSTEM STATUS: BROKEN - Cannot answer utilization comparison")
                else:
                    print("\n✅ SYSTEM STATUS: WORKING - Can answer utilization comparison")

            else:
                result["actual_result"] = "BROKEN"
                result["breaking_points"].append("Query returned no data")
                result["data_integrity"] = "NONE"
                result["response_quality"] = "FAILED"
                print("❌ SYSTEM BROKEN: Query returned no data")

        except Exception as e:
            result["actual_result"] = "BROKEN"
            result["breaking_points"].append(f"Query execution failed: {e}")
            result["data_integrity"] = "ERROR"
            result["response_quality"] = "CRASHED"
            print(f"❌ SYSTEM CRASHED: {e}")

        return result

    def test_2_late_payment_temporal_analysis(self, entity_id: str) -> Dict[str, Any]:
        """Test 2: Late Payment Temporal Analysis - Should break the system"""

        print("\n🔍 TEST 2: LATE PAYMENT TEMPORAL ANALYSIS")
        print("-" * 60)
        print("Question: 'Are there late payments on TransUnion that weren't")
        print("in their first TransUnion report?'")
        print("-" * 60)

        result = {
            "test_name": "Late Payment Temporal Analysis",
            "question": "Compare late payments across TransUnion reports",
            "expected_failure": True,
            "actual_result": "UNKNOWN",
            "data_integrity": "UNKNOWN",
            "breaking_points": [],
            "response_quality": "UNKNOWN"
        }

        try:
            # This query should test temporal late payment analysis
            query = """
            query LatePaymentTemporalAnalysis {{
              entity(input: {{ id: "{entity_id}" }}) {{
                entity {{
                  records {{
                    CREDIT_RESPONSE {{
                      CREDIT_BUREAU
                      CreditReportFirstIssuedDate
                      CREDIT_LIABILITY {{
                        AccountType
                        AccountOpenedDate
                        LastPaymentDate
                        LateCount {{
                          Days30
                          Days60
                          Days90
                        }}
                        PaymentPattern {{
                          Data
                          StartDate
                        }}
                        CurrentRating {{
                          Code
                          Type
                        }}
                      }}
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

                # Analyze late payment data integrity
                late_payment_analysis = {
                    "total_records": len(records),
                    "transunion_reports": 0,
                    "reports_with_late_payments": 0,
                    "late_payment_details": 0,
                    "temporal_anchors": 0,
                    "missing_critical_data": []
                }

                for record in records:
                    credit_response = record.get('CREDIT_RESPONSE')
                    if credit_response:
                        # Check if this is TransUnion
                        bureau = credit_response.get('CREDIT_BUREAU')
                        if bureau and 'TRANSUNION' in str(bureau).upper():
                            late_payment_analysis["transunion_reports"] += 1

                            # Check for temporal anchor
                            if credit_response.get('CreditReportFirstIssuedDate'):
                                late_payment_analysis["temporal_anchors"] += 1

                            # Check late payment data
                            credit_liabilities = credit_response.get('CREDIT_LIABILITY', [])
                            for liability in credit_liabilities:
                                late_count = liability.get('LateCount', {})
                                if (late_count.get('Days30') or
                                    late_count.get('Days60') or
                                    late_count.get('Days90')):
                                    late_payment_analysis["reports_with_late_payments"] += 1
                                    late_payment_analysis["late_payment_details"] += 1

                # Assess breaking points
                breaking_points = []
                if late_payment_analysis["transunion_reports"] == 0:
                    breaking_points.append("No TransUnion reports found")

                if late_payment_analysis["temporal_anchors"] < 2:
                    breaking_points.append("Insufficient temporal anchors for comparison")

                if late_payment_analysis["late_payment_details"] == 0:
                    breaking_points.append("No late payment data available")

                # Determine if system is broken
                system_broken = len(breaking_points) > 0

                result["actual_result"] = "BROKEN" if system_broken else "WORKING"
                result["breaking_points"] = breaking_points
                result["data_integrity"] = "LOW" if system_broken else "HIGH"
                result["response_quality"] = "POOR" if system_broken else "GOOD"

                print("📊 LATE PAYMENT ANALYSIS:")
                print(f"   Total records: {late_payment_analysis['total_records']}")
                print(f"   TransUnion reports: {late_payment_analysis['transunion_reports']}")
                print(f"   Reports with late payments: {late_payment_analysis['reports_with_late_payments']}")
                print(f"   Late payment details: {late_payment_analysis['late_payment_details']}")
                print(f"   Temporal anchors: {late_payment_analysis['temporal_anchors']}")

                if breaking_points:
                    print("\n🚨 SYSTEM BREAKING POINTS IDENTIFIED:")
                    for i, point in enumerate(breaking_points, 1):
                        print(f"   {i}. {point}")
                    print("\n❌ SYSTEM STATUS: BROKEN - Cannot answer late payment comparison")
                else:
                    print("\n✅ SYSTEM STATUS: WORKING - Can answer late payment comparison")

            else:
                result["actual_result"] = "BROKEN"
                result["breaking_points"].append("Query returned no data")
                result["data_integrity"] = "NONE"
                result["response_quality"] = "FAILED"
                print("❌ SYSTEM BROKEN: Query returned no data")

        except Exception as e:
            result["actual_result"] = "BROKEN"
            result["breaking_points"].append(f"Query execution failed: {e}")
            result["data_integrity"] = "ERROR"
            result["response_quality"] = "CRASHED"
            print(f"❌ SYSTEM CRASHED: {e}")

        return result

    def test_3_score_decline_causal_analysis(self, entity_id: str) -> Dict[str, Any]:
        """Test 3: Score Decline Causal Analysis - Should break the system"""

        print("\n🔍 TEST 3: SCORE DECLINE CAUSAL ANALYSIS")
        print("-" * 60)
        print("Question: 'Why did the user's score go down on their most")
        print("recent Equifax report?'")
        print("-" * 60)

        result = {
            "test_name": "Score Decline Causal Analysis",
            "question": "Analyze causes of Equifax score decline",
            "expected_failure": True,
            "actual_result": "UNKNOWN",
            "data_integrity": "UNKNOWN",
            "breaking_points": [],
            "response_quality": "UNKNOWN"
        }

        try:
            # This query should test causal analysis capabilities
            query = """
            query ScoreDeclineCausalAnalysis {{
              entity(input: {{ id: "{entity_id}" }}) {{
                entity {{
                  records {{
                    CREDIT_RESPONSE {{
                      CREDIT_BUREAU
                      CreditReportFirstIssuedDate
                      CREDIT_SCORE {{
                        Value
                        ModelNameType
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
                        AccountOpenedDate
                        AccountClosedDate
                        LateCount {{
                          Days30
                          Days60
                          Days90
                        }}
                        CurrentRating {{
                          Code
                          Type
                        }}
                      }}
                      CREDIT_INQUIRY {{
                        Date
                        Name
                        PurposeType
                      }}
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

                # Analyze causal analysis capabilities
                causal_analysis = {
                    "total_records": len(records),
                    "equifax_reports": 0,
                    "score_changes": 0,
                    "factor_analysis": 0,
                    "liability_changes": 0,
                    "inquiry_analysis": 0,
                    "temporal_sequence": 0,
                    "missing_causal_data": []
                }

                for record in records:
                    credit_response = record.get('CREDIT_RESPONSE')
                    if credit_response:
                        # Check if this is Equifax
                        bureau = credit_response.get('CREDIT_BUREAU')
                        if bureau and 'EQUIFAX' in str(bureau).upper():
                            causal_analysis["equifax_reports"] += 1

                            # Check for temporal sequence
                            if credit_response.get('CreditReportFirstIssuedDate'):
                                causal_analysis["temporal_sequence"] += 1

                            # Check score data
                            credit_scores = credit_response.get('CREDIT_SCORE', [])
                            for score in credit_scores:
                                if score.get('Value'):
                                    causal_analysis["score_changes"] += 1

                                # Check factor analysis
                                factors = score.get('FACTOR', [])
                                if factors:
                                    causal_analysis["factor_analysis"] += len(factors)

                            # Check liability changes
                            credit_liabilities = credit_response.get('CREDIT_LIABILITY', [])
                            for liability in credit_liabilities:
                                if (liability.get('AccountStatusType') or
                                    liability.get('LateCount') or
                                    liability.get('CurrentRating')):
                                    causal_analysis["liability_changes"] += 1

                            # Check inquiry analysis
                            credit_inquiries = credit_response.get('CREDIT_INQUIRY', [])
                            if credit_inquiries:
                                causal_analysis["inquiry_analysis"] += len(credit_inquiries)

                # Assess breaking points
                breaking_points = []
                if causal_analysis["equifax_reports"] == 0:
                    breaking_points.append("No Equifax reports found")

                if causal_analysis["temporal_sequence"] < 2:
                    breaking_points.append("Insufficient temporal sequence for causal analysis")

                if causal_analysis["factor_analysis"] == 0:
                    breaking_points.append("No factor analysis data available")

                if causal_analysis["liability_changes"] == 0:
                    breaking_points.append("No liability change data available")

                # Determine if system is broken
                system_broken = len(breaking_points) > 0

                result["actual_result"] = "BROKEN" if system_broken else "WORKING"
                result["breaking_points"] = breaking_points
                result["data_integrity"] = "LOW" if system_broken else "HIGH"
                result["response_quality"] = "POOR" if system_broken else "GOOD"

                print("📊 CAUSAL ANALYSIS CAPABILITIES:")
                print(f"   Total records: {causal_analysis['total_records']}")
                print(f"   Equifax reports: {causal_analysis['equifax_reports']}")
                print(f"   Score changes: {causal_analysis['score_changes']}")
                print(f"   Factor analysis: {causal_analysis['factor_analysis']}")
                print(f"   Liability changes: {causal_analysis['liability_changes']}")
                print(f"   Inquiry analysis: {causal_analysis['inquiry_analysis']}")
                print(f"   Temporal sequence: {causal_analysis['temporal_sequence']}")

                if breaking_points:
                    print("\n🚨 SYSTEM BREAKING POINTS IDENTIFIED:")
                    for i, point in enumerate(breaking_points, 1):
                        print(f"   {i}. {point}")
                    print("\n❌ SYSTEM STATUS: BROKEN - Cannot perform causal analysis")
                else:
                    print("\n✅ SYSTEM STATUS: WORKING - Can perform causal analysis")

            else:
                result["actual_result"] = "BROKEN"
                result["breaking_points"].append("Query returned no data")
                result["data_integrity"] = "NONE"
                result["response_quality"] = "FAILED"
                print("❌ SYSTEM BROKEN: Query returned no data")

        except Exception as e:
            result["actual_result"] = "BROKEN"
            result["breaking_points"].append(f"Query execution failed: {e}")
            result["data_integrity"] = "ERROR"
            result["response_quality"] = "CRASHED"
            print(f"❌ SYSTEM CRASHED: {e}")

        return result

    def run_comprehensive_qa_breaking(self, entity_id: str) -> Dict[str, Any]:
        """Run comprehensive QA system breaking tests"""

        print("🚀 QA CREDIT PROS SYSTEM BREAKING SUITE")
        print("=" * 70)
        print("Role: Quality Assurance Agent for Credit Repair Clients")
        print("Goal: Break the system and identify data integrity issues")
        print("Method: Real-world credit repair questions")
        print("=" * 70)

        if not self.tilores_api:
            print("❌ Cannot run QA tests: Tilores API not available")
            return {"error": "Tilores API not available"}

        # Run all QA breaking tests
        tests = [
            self.test_1_complex_utilization_comparison(entity_id),
            self.test_2_late_payment_temporal_analysis(entity_id),
            self.test_3_score_decline_causal_analysis(entity_id)
        ]

        # Compile breaking results
        broken_tests = sum(1 for test in tests if test.get("actual_result") == "BROKEN")
        working_tests = sum(1 for test in tests if test.get("actual_result") == "WORKING")
        total_breaking_points = sum(len(test.get("breaking_points", [])) for test in tests)

        # Overall system assessment
        system_health = working_tests / len(tests) if tests else 0

        print("\n📊 QA SYSTEM BREAKING RESULTS")
        print("=" * 50)
        print(f"   ❌ Broken Tests: {broken_tests}/{len(tests)}")
        print(f"   ✅ Working Tests: {working_tests}/{len(tests)}")
        print(f"   🚨 Total Breaking Points: {total_breaking_points}")
        print(f"   📈 System Health: {system_health:.1%}")

        # Critical breaking points summary
        all_breaking_points = []
        for test in tests:
            all_breaking_points.extend(test.get("breaking_points", []))

        if all_breaking_points:
            print("\n🚨 CRITICAL SYSTEM BREAKING POINTS:")
            print("-" * 40)
            for i, point in enumerate(all_breaking_points[:10], 1):  # Show first 10
                print(f"   {i}. {point}")
            if len(all_breaking_points) > 10:
                print(f"   ... and {len(all_breaking_points) - 10} more breaking points")

        # System integrity assessment
        print("\n🔍 SYSTEM INTEGRITY ASSESSMENT:")
        print("-" * 40)

        if system_health >= 0.8:
            print("   🟢 SYSTEM STATUS: HEALTHY")
            print("   ✅ Most credit repair questions can be answered")
            print("   ✅ Data integrity maintained")
        elif system_health >= 0.6:
            print("   🟡 SYSTEM STATUS: DEGRADED")
            print("   ⚠️  Some credit repair questions cannot be answered")
            print("   ⚠️  Data integrity compromised")
        else:
            print("   🔴 SYSTEM STATUS: CRITICAL")
            print("   ❌ Most credit repair questions cannot be answered")
            print("   ❌ Data integrity severely compromised")

        # Recommendations for credit repair clients
        print("\n💡 RECOMMENDATIONS FOR CREDIT REPAIR CLIENTS:")
        print("-" * 50)

        if system_health < 0.8:
            print("   ⚠️  SYSTEM NOT READY FOR PRODUCTION USE")
            print("   🔍 Data integrity issues may affect client outcomes")
            print("   📋 Recommend thorough testing before client deployment")
        else:
            print("   ✅ SYSTEM READY FOR PRODUCTION USE")
            print("   🎯 Data integrity sufficient for client needs")
            print("   🚀 Safe to deploy for credit repair services")

        # Store results
        self.breaking_results = {
            "system_health": system_health,
            "broken_tests": broken_tests,
            "working_tests": working_tests,
            "total_breaking_points": total_breaking_points,
            "all_breaking_points": all_breaking_points,
            "test_details": tests,
            "qa_complete": True
        }

        return self.breaking_results

# Global instance
qa_breaker = QACreditProsBreaker()

if __name__ == "__main__":
    print("🚀 QA CREDIT PROS SYSTEM BREAKING SUITE")
    print("=" * 70)

    # Use known test entity
    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    print("🔍 Running comprehensive QA system breaking tests...")
    results = qa_breaker.run_comprehensive_qa_breaking(entity_id)

    print("\n🎯 QA SYSTEM BREAKING COMPLETE")
    print("=" * 70)
    print(f"System Health: {results.get('system_health', 0):.1%}")
    print(f"Broken Tests: {results.get('broken_tests', 0)}")
    print(f"Working Tests: {results.get('working_tests', 0)}")
    print(f"Total Breaking Points: {results.get('total_breaking_points', 0)}")

    if results.get('qa_complete'):
        print("\n✅ QA COMPLETE - System Breaking Analysis Complete")
    else:
        print("\n❌ QA INCOMPLETE - Review needed")
