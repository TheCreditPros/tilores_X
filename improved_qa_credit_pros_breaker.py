#!/usr/bin/env python3
"""
Improved QA Credit Pros System Breaker
Adapted to work with available Equifax data and provide meaningful analysis
"""

from dotenv import load_dotenv
load_dotenv()
from typing import Dict, Any

class ImprovedQACreditProsBreaker:
    """Improved QA Agent for Credit Pros System Breaking"""

    def __init__(self):
        """Initialize improved QA breaker"""
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

    def test_1_equifax_utilization_comparison(self, entity_id: str) -> Dict[str, Any]:
        """Test 1: Equifax Credit Utilization Comparison - Adapted for available data"""

        print("\n🔍 TEST 1: EQUIFAX CREDIT UTILIZATION COMPARISON")
        print("-" * 60)
        print("Question: 'Compare the credit card utilization across different")
        print("Equifax reports to identify trends and changes'")
        print("-" * 60)

        result = {
            "test_name": "Equifax Utilization Comparison",
            "question": "Compare Equifax utilization across time periods",
            "expected_failure": False,
            "actual_result": "UNKNOWN",
            "data_integrity": "UNKNOWN",
            "breaking_points": [],
            "response_quality": "UNKNOWN"
        }

        try:
            # Query adapted for available Equifax data
            query = """
            query EquifaxUtilizationComparison {{
              entity(input: {{ id: "{entity_id}" }}) {{
                entity {{
                  records {{
                    CREDIT_RESPONSE {{
                      CREDIT_BUREAU
                      CreditReportFirstIssuedDate
                      CREDIT_SCORE {{
                        Value
                        ModelNameType
                      }}
                      CREDIT_LIABILITY {{
                        AccountType
                        CreditLimitAmount
                        CreditBalance
                        AccountOpenedDate
                        AccountStatusType
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

                # Analyze Equifax utilization data
                utilization_analysis = {
                    "total_records": len(records),
                    "equifax_reports": 0,
                    "reports_with_dates": 0,
                    "unique_dates": set(),
                    "credit_liabilities": 0,
                    "utilization_data": 0,
                    "account_types": set(),
                    "temporal_coverage": "N/A"
                }

                for record in records:
                    credit_response = record.get('CREDIT_RESPONSE')
                    if credit_response:
                        bureau = credit_response.get('CREDIT_BUREAU')
                        if bureau and 'EQUIFAX' in str(bureau).upper():
                            utilization_analysis["equifax_reports"] += 1

                            # Check dates
                            report_date = credit_response.get('CreditReportFirstIssuedDate')
                            if report_date and report_date != "None":
                                utilization_analysis["reports_with_dates"] += 1
                                utilization_analysis["unique_dates"].add(report_date)

                            # Check liabilities and utilization
                            credit_liabilities = credit_response.get('CREDIT_LIABILITY', [])
                            for liability in credit_liabilities:
                                utilization_analysis["credit_liabilities"] += 1

                                account_type = liability.get('AccountType')
                                if account_type:
                                    utilization_analysis["account_types"].add(account_type)

                                # Check utilization data
                                if (liability.get('CreditLimitAmount') and
                                    liability.get('CreditBalance')):
                                    utilization_analysis["utilization_data"] += 1

                # Calculate temporal coverage
                if len(utilization_analysis["unique_dates"]) > 1:
                    dates_list = sorted(list(utilization_analysis["unique_dates"]))
                    utilization_analysis["temporal_coverage"] = f"{dates_list[0]} to {dates_list[-1]}"

                # Assess capabilities
                breaking_points = []
                if utilization_analysis["equifax_reports"] == 0:
                    breaking_points.append("No Equifax reports found")

                if utilization_analysis["utilization_data"] == 0:
                    breaking_points.append("No utilization data available")

                if len(utilization_analysis["unique_dates"]) < 2:
                    breaking_points.append("Insufficient temporal data for comparison")

                # Determine if system can answer the question
                system_capable = len(breaking_points) == 0

                result["actual_result"] = "WORKING" if system_capable else "BROKEN"
                result["breaking_points"] = breaking_points
                result["data_integrity"] = "HIGH" if system_capable else "LOW"
                result["response_quality"] = "GOOD" if system_capable else "POOR"

                print("📊 EQUIFAX UTILIZATION ANALYSIS:")
                print(f"   Total records: {utilization_analysis['total_records']}")
                print(f"   Equifax reports: {utilization_analysis['equifax_reports']}")
                print(f"   Reports with dates: {utilization_analysis['reports_with_dates']}")
                print(f"   Unique dates: {len(utilization_analysis['unique_dates'])}")
                print(f"   Credit liabilities: {utilization_analysis['credit_liabilities']}")
                print(f"   Utilization data: {utilization_analysis['utilization_data']}")
                print(f"   Account types: {len(utilization_analysis['account_types'])}")
                print(f"   Temporal coverage: {utilization_analysis['temporal_coverage']}")

                if breaking_points:
                    print("\n🚨 SYSTEM BREAKING POINTS IDENTIFIED:")
                    for i, point in enumerate(breaking_points, 1):
                        print(f"   {i}. {point}")
                    print("\n❌ SYSTEM STATUS: BROKEN - Cannot answer utilization comparison")
                else:
                    print("\n✅ SYSTEM STATUS: WORKING - Can answer utilization comparison")
                    print(f"   🎯 Can analyze utilization trends across {len(utilization_analysis['unique_dates'])} time periods")

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

    def test_2_equifax_late_payment_analysis(self, entity_id: str) -> Dict[str, Any]:
        """Test 2: Equifax Late Payment Analysis - Adapted for available data"""

        print("\n🔍 TEST 2: EQUIFAX LATE PAYMENT ANALYSIS")
        print("-" * 60)
        print("Question: 'What late payment patterns are visible in the")
        print("Equifax reports and how have they changed over time?'")
        print("-" * 60)

        result = {
            "test_name": "Equifax Late Payment Analysis",
            "question": "Analyze late payment patterns in Equifax reports",
            "expected_failure": False,
            "actual_result": "UNKNOWN",
            "data_integrity": "UNKNOWN",
            "breaking_points": [],
            "response_quality": "UNKNOWN"
        }

        try:
            # Query adapted for Equifax late payment analysis
            query = """
            query EquifaxLatePaymentAnalysis {{
              entity(input: {{ id: "{entity_id}" }}) {{
                entity {{
                  records {{
                    CREDIT_RESPONSE {{
                      CREDIT_BUREAU
                      CreditReportFirstIssuedDate
                      CREDIT_LIABILITY {{
                        AccountType
                        AccountStatusType
                        AccountOpenedDate
                        LastPaymentDate
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

                # Analyze Equifax late payment data
                late_payment_analysis = {
                    "total_records": len(records),
                    "equifax_reports": 0,
                    "reports_with_dates": 0,
                    "unique_dates": set(),
                    "accounts_with_late_payments": 0,
                    "total_late_payments": 0,
                    "late_payment_types": {"30_days": 0, "60_days": 0, "90_days": 0},
                    "account_statuses": set(),
                    "temporal_coverage": "N/A"
                }

                for record in records:
                    credit_response = record.get('CREDIT_RESPONSE')
                    if credit_response:
                        bureau = credit_response.get('CREDIT_BUREAU')
                        if bureau and 'EQUIFAX' in str(bureau).upper():
                            late_payment_analysis["equifax_reports"] += 1

                            # Check dates
                            report_date = credit_response.get('CreditReportFirstIssuedDate')
                            if report_date and report_date != "None":
                                late_payment_analysis["reports_with_dates"] += 1
                                late_payment_analysis["unique_dates"].add(report_date)

                            # Check late payment data
                            credit_liabilities = credit_response.get('CREDIT_LIABILITY', [])
                            for liability in credit_liabilities:
                                account_status = liability.get('AccountStatusType')
                                if account_status:
                                    late_payment_analysis["account_statuses"].add(account_status)

                                # Check late payment counts
                                late_count = liability.get('LateCount', {})
                                if late_count:
                                    days_30 = late_count.get('Days30', 0)
                                    days_60 = late_count.get('Days60', 0)
                                    days_90 = late_count.get('Days90', 0)

                                    if days_30 or days_60 or days_90:
                                        late_payment_analysis["accounts_with_late_payments"] += 1
                                        late_payment_analysis["total_late_payments"] += (days_30 + days_60 + days_90)

                                        if days_30:
                                            late_payment_analysis["late_payment_types"]["30_days"] += days_30
                                        if days_60:
                                            late_payment_analysis["late_payment_types"]["60_days"] += days_60
                                        if days_90:
                                            late_payment_analysis["late_payment_types"]["90_days"] += days_90

                # Calculate temporal coverage
                if len(late_payment_analysis["unique_dates"]) > 1:
                    dates_list = sorted(list(late_payment_analysis["unique_dates"]))
                    late_payment_analysis["temporal_coverage"] = f"{dates_list[0]} to {dates_list[-1]}"

                # Assess capabilities
                breaking_points = []
                if late_payment_analysis["equifax_reports"] == 0:
                    breaking_points.append("No Equifax reports found")

                if late_payment_analysis["accounts_with_late_payments"] == 0:
                    breaking_points.append("No late payment data available")

                if len(late_payment_analysis["unique_dates"]) < 2:
                    breaking_points.append("Insufficient temporal data for trend analysis")

                # Determine if system can answer the question
                system_capable = len(breaking_points) == 0

                result["actual_result"] = "WORKING" if system_capable else "BROKEN"
                result["breaking_points"] = breaking_points
                result["data_integrity"] = "HIGH" if system_capable else "LOW"
                result["response_quality"] = "GOOD" if system_capable else "POOR"

                print("📊 EQUIFAX LATE PAYMENT ANALYSIS:")
                print(f"   Total records: {late_payment_analysis['total_records']}")
                print(f"   Equifax reports: {late_payment_analysis['equifax_reports']}")
                print(f"   Reports with dates: {late_payment_analysis['reports_with_dates']}")
                print(f"   Unique dates: {len(late_payment_analysis['unique_dates'])}")
                print(f"   Accounts with late payments: {late_payment_analysis['accounts_with_late_payments']}")
                print(f"   Total late payments: {late_payment_analysis['total_late_payments']}")
                print("   Late payment breakdown:")
                print(f"     30 days: {late_payment_analysis['late_payment_types']['30_days']}")
                print(f"     60 days: {late_payment_analysis['late_payment_types']['60_days']}")
                print(f"     90 days: {late_payment_analysis['late_payment_types']['90_days']}")
                print(f"   Account statuses: {len(late_payment_analysis['account_statuses'])}")
                print(f"   Temporal coverage: {late_payment_analysis['temporal_coverage']}")

                if breaking_points:
                    print("\n🚨 SYSTEM BREAKING POINTS IDENTIFIED:")
                    for i, point in enumerate(breaking_points, 1):
                        print(f"   {i}. {point}")
                    print("\n❌ SYSTEM STATUS: BROKEN - Cannot analyze late payment patterns")
                else:
                    print("\n✅ SYSTEM STATUS: WORKING - Can analyze late payment patterns")
                    print(f"   🎯 Can track late payment trends across {len(late_payment_analysis['unique_dates'])} time periods")

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

    def test_3_equifax_score_decline_causal_analysis(self, entity_id: str) -> Dict[str, Any]:
        """Test 3: Equifax Score Decline Causal Analysis - Enhanced for available data"""

        print("\n🔍 TEST 3: EQUIFAX SCORE DECLINE CAUSAL ANALYSIS")
        print("-" * 60)
        print("Question: 'Why did the user's Equifax score change and what")
        print("factors contributed to the score movement?'")
        print("-" * 60)

        result = {
            "test_name": "Equifax Score Decline Causal Analysis",
            "question": "Analyze causes of Equifax score changes",
            "expected_failure": False,
            "actual_result": "UNKNOWN",
            "data_integrity": "UNKNOWN",
            "breaking_points": [],
            "response_quality": "UNKNOWN"
        }

        try:
            # Enhanced query for Equifax causal analysis
            query = """
            query EnhancedEquifaxCausalAnalysis {{
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

                # Enhanced causal analysis for Equifax
                causal_analysis = {
                    "total_records": len(records),
                    "equifax_reports": 0,
                    "reports_with_dates": 0,
                    "unique_dates": set(),
                    "score_changes": 0,
                    "factor_analysis": 0,
                    "liability_changes": 0,
                    "inquiry_analysis": 0,
                    "temporal_sequence": 0,
                    "causal_factors": set(),
                    "temporal_coverage": "N/A"
                }

                for record in records:
                    credit_response = record.get('CREDIT_RESPONSE')
                    if credit_response:
                        bureau = credit_response.get('CREDIT_BUREAU')
                        if bureau and 'EQUIFAX' in str(bureau).upper():
                            causal_analysis["equifax_reports"] += 1

                            # Check temporal sequence
                            report_date = credit_response.get('CreditReportFirstIssuedDate')
                            if report_date and report_date != "None":
                                causal_analysis["reports_with_dates"] += 1
                                causal_analysis["unique_dates"].add(report_date)
                                causal_analysis["temporal_sequence"] += 1

                            # Check score data
                            credit_scores = credit_response.get('CREDIT_SCORE', [])
                            for score in credit_scores:
                                if score.get('Value'):
                                    causal_analysis["score_changes"] += 1

                                # Check factor analysis
                                factors = score.get('FACTOR', [])
                                for factor in factors:
                                    if factors:
                                        causal_analysis["factor_analysis"] += 1
                                        factor_text = factor.get('Text', '')
                                        if factor_text:
                                            causal_analysis["causal_factors"].add(factor_text[:50])  # First 50 chars

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

                # Calculate temporal coverage
                if len(causal_analysis["unique_dates"]) > 1:
                    dates_list = sorted(list(causal_analysis["unique_dates"]))
                    causal_analysis["temporal_coverage"] = f"{dates_list[0]} to {dates_list[-1]}"

                # Assess capabilities
                breaking_points = []
                if causal_analysis["equifax_reports"] == 0:
                    breaking_points.append("No Equifax reports found")

                if causal_analysis["temporal_sequence"] < 2:
                    breaking_points.append("Insufficient temporal sequence for causal analysis")

                if causal_analysis["factor_analysis"] == 0:
                    breaking_points.append("No factor analysis data available")

                # Determine if system can answer the question
                system_capable = len(breaking_points) == 0

                result["actual_result"] = "WORKING" if system_capable else "BROKEN"
                result["breaking_points"] = breaking_points
                result["data_integrity"] = "HIGH" if system_capable else "LOW"
                result["response_quality"] = "GOOD" if system_capable else "POOR"

                print("📊 ENHANCED EQUIFAX CAUSAL ANALYSIS:")
                print(f"   Total records: {causal_analysis['total_records']}")
                print(f"   Equifax reports: {causal_analysis['equifax_reports']}")
                print(f"   Reports with dates: {causal_analysis['reports_with_dates']}")
                print(f"   Unique dates: {len(causal_analysis['unique_dates'])}")
                print(f"   Score changes: {causal_analysis['score_changes']}")
                print(f"   Factor analysis: {causal_analysis['factor_analysis']}")
                print(f"   Liability changes: {causal_analysis['liability_changes']}")
                print(f"   Inquiry analysis: {causal_analysis['inquiry_analysis']}")
                print(f"   Temporal sequence: {causal_analysis['temporal_sequence']}")
                print(f"   Causal factors: {len(causal_analysis['causal_factors'])}")
                print(f"   Temporal coverage: {causal_analysis['temporal_coverage']}")

                if breaking_points:
                    print("\n🚨 SYSTEM BREAKING POINTS IDENTIFIED:")
                    for i, point in enumerate(breaking_points, 1):
                        print(f"   {i}. {point}")
                    print("\n❌ SYSTEM STATUS: BROKEN - Cannot perform causal analysis")
                else:
                    print("\n✅ SYSTEM STATUS: WORKING - Can perform causal analysis")
                    print(f"   🎯 Can analyze score changes across {len(causal_analysis['unique_dates'])} time periods")
                    print(f"   🎯 Can identify {causal_analysis['factor_analysis']} causal factors")

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

    def run_improved_qa_breaking(self, entity_id: str) -> Dict[str, Any]:
        """Run improved QA system breaking tests"""

        print("🚀 IMPROVED QA CREDIT PROS SYSTEM BREAKING SUITE")
        print("=" * 70)
        print("Role: Quality Assurance Agent for Credit Repair Clients")
        print("Goal: Test system with available Equifax data")
        print("Method: Adapted questions for single-bureau scenario")
        print("=" * 70)

        if not self.tilores_api:
            print("❌ Cannot run QA tests: Tilores API not available")
            return {"error": "Tilores API not available"}

        # Run all improved QA tests
        tests = [
            self.test_1_equifax_utilization_comparison(entity_id),
            self.test_2_equifax_late_payment_analysis(entity_id),
            self.test_3_equifax_score_decline_causal_analysis(entity_id)
        ]

        # Compile results
        working_tests = sum(1 for test in tests if test.get("actual_result") == "WORKING")
        broken_tests = sum(1 for test in tests if test.get("actual_result") == "BROKEN")
        total_breaking_points = sum(len(test.get("breaking_points", [])) for test in tests)

        # Overall system assessment
        system_health = working_tests / len(tests) if tests else 0

        print("\n📊 IMPROVED QA SYSTEM BREAKING RESULTS")
        print("=" * 50)
        print(f"   ✅ Working Tests: {working_tests}/{len(tests)}")
        print(f"   ❌ Broken Tests: {broken_tests}/{len(tests)}")
        print(f"   🚨 Total Breaking Points: {total_breaking_points}")
        print(f"   📈 System Health: {system_health:.1%}")

        # Critical breaking points summary
        all_breaking_points = []
        for test in tests:
            all_breaking_points.extend(test.get("breaking_points", []))

        if all_breaking_points:
            print("\n🚨 REMAINING SYSTEM BREAKING POINTS:")
            print("-" * 40)
            for i, point in enumerate(all_breaking_points[:10], 1):
                print(f"   {i}. {point}")
            if len(all_breaking_points) > 10:
                print(f"   ... and {len(all_breaking_points) - 10} more breaking points")

        # System integrity assessment
        print("\n🔍 IMPROVED SYSTEM INTEGRITY ASSESSMENT:")
        print("-" * 40)

        if system_health >= 0.9:
            print("   🟢 SYSTEM STATUS: HEALTHY")
            print("   ✅ Most Equifax-based questions can be answered")
            print("   ✅ Data integrity maintained for available data")
        elif system_health >= 0.8:
            print("   🟢 SYSTEM STATUS: MOSTLY HEALTHY")
            print("   ✅ Most Equifax-based questions can be answered")
            print("   ⚠️  Minor limitations with available data")
        elif system_health >= 0.6:
            print("   🟡 SYSTEM STATUS: DEGRADED")
            print("   ⚠️  Some Equifax-based questions cannot be answered")
            print("   ⚠️  Data integrity compromised in some areas")
        else:
            print("   🔴 SYSTEM STATUS: CRITICAL")
            print("   ❌ Most Equifax-based questions cannot be answered")
            print("   ❌ Data integrity severely compromised")

        # Recommendations for credit repair clients
        print("\n💡 RECOMMENDATIONS FOR CREDIT REPAIR CLIENTS:")
        print("-" * 50)

        if system_health >= 0.8:
            print("   ✅ SYSTEM READY FOR EQUIFAX-BASED ANALYSIS")
            print("   🎯 Can provide meaningful Equifax credit insights")
            print("   ⚠️  Limited to single bureau (Equifax only)")
            print("   📋 Recommend disclosing bureau limitations to clients")
        else:
            print("   ⚠️  SYSTEM NOT READY FOR PRODUCTION USE")
            print("   🔍 Data integrity issues may affect client outcomes")
            print("   📋 Recommend thorough testing before client deployment")

        # Store results
        self.breaking_results = {
            "system_health": system_health,
            "working_tests": working_tests,
            "broken_tests": broken_tests,
            "total_breaking_points": total_breaking_points,
            "all_breaking_points": all_breaking_points,
            "test_details": tests,
            "qa_complete": True
        }

        return self.breaking_results

# Global instance
improved_qa_breaker = ImprovedQACreditProsBreaker()

if __name__ == "__main__":
    print("🚀 IMPROVED QA CREDIT PROS SYSTEM BREAKING SUITE")
    print("=" * 70)

    # Use known test entity
    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    print("🔍 Running improved QA system breaking tests...")
    results = improved_qa_breaker.run_improved_qa_breaking(entity_id)

    print("\n🎯 IMPROVED QA SYSTEM BREAKING COMPLETE")
    print("=" * 70)
    print(f"System Health: {results.get('system_health', 0):.1%}")
    print(f"Working Tests: {results.get('working_tests', 0)}")
    print(f"Broken Tests: {results.get('broken_tests', 0)}")
    print(f"Total Breaking Points: {results.get('total_breaking_points', 0)}")

    if results.get('qa_complete'):
        print("\n✅ IMPROVED QA COMPLETE - System Analysis Complete")
    else:
        print("\n❌ IMPROVED QA INCOMPLETE - Review needed")
