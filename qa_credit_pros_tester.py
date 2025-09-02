#!/usr/bin/env python3
"""
QA Credit Pros Tester - Quality Assurance Agent
Tests system integrity for credit repair clients with mixed questions
Goal: Break the system and identify data integrity issues
"""

from dotenv import load_dotenv
load_dotenv()
from typing import Dict, Any

class QACreditProsTester:
    """Quality Assurance tester for Credit Pros system"""

    def __init__(self):
        """Initialize QA tester"""
        self.tilores_api = None
        self.test_results = []
        self.failures = []
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

    def test_credit_score_integrity(self, entity_id: str) -> Dict[str, Any]:
        """Test 1: Credit Score Data Integrity"""

        print("\n🔍 TEST 1: CREDIT SCORE DATA INTEGRITY")
        print("=" * 50)

        test_result = {
            "test_name": "Credit Score Data Integrity",
            "status": "FAILED",
            "issues": [],
            "data_quality": {},
            "response_integrity": {}
        }

        try:
            # Test basic credit score query
            query = """
            query TestCreditScoreIntegrity {{
              entity(input: {{ id: "{entity_id}" }}) {{
                entity {{
                  records {{
                    CREDIT_RESPONSE {{
                      CREDIT_SCORE {{
                        Value
                        ModelNameType
                        CreditRepositorySourceType
                        Date
                        FACTOR {{
                          Code
                          Text
                          Factor_Type
                        }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """

            result = self.tilores_api.gql(query)

            if not result or 'data' not in result:
                test_result["issues"].append("Query returned no data")
                return test_result

            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            if not records:
                test_result["issues"].append("No records found")
                return test_result

            # Analyze data quality
            total_scores = 0
            scores_with_values = 0
            scores_with_dates = 0
            scores_with_factors = 0
            empty_values = 0
            null_dates = 0

            for record in records:
                credit_response = record.get('CREDIT_RESPONSE', {})
                credit_scores = credit_response.get('CREDIT_SCORE', [])

                for score in credit_scores:
                    total_scores += 1

                    # Check value integrity
                    if score.get('Value') and score.get('Value') != "None":
                        scores_with_values += 1
                    else:
                        empty_values += 1

                    # Check date integrity
                    if score.get('Date') and score.get('Date') != "None":
                        scores_with_dates += 1
                    else:
                        null_dates += 1

                    # Check factor integrity
                    if score.get('FACTOR') and len(score.get('FACTOR', [])) > 0:
                        scores_with_factors += 1

            # Data quality metrics
            test_result["data_quality"] = {
                "total_scores": total_scores,
                "scores_with_values": scores_with_values,
                "scores_with_dates": scores_with_dates,
                "scores_with_factors": scores_with_factors,
                "empty_values": empty_values,
                "null_dates": null_dates
            }

            # Check for data integrity issues
            if empty_values > 0:
                test_result["issues"].append(f"Found {empty_values} scores with empty/null values")

            if null_dates > 0:
                test_result["issues"].append(f"Found {null_dates} scores with null dates")

            if total_scores == 0:
                test_result["issues"].append("No credit scores found in data")

            # Response integrity check
            test_result["response_integrity"] = {
                "has_data": bool(result.get('data')),
                "has_entity": bool(result.get('data', {}).get('entity')),
                "has_records": bool(records),
                "response_structure": "VALID" if result.get('data') else "INVALID"
            }

            # Determine test status
            if not test_result["issues"]:
                test_result["status"] = "PASSED"
                print("✅ Credit Score Integrity Test PASSED")
            else:
                test_result["status"] = "FAILED"
                print(f"❌ Credit Score Integrity Test FAILED: {len(test_result['issues'])} issues")
                for issue in test_result["issues"]:
                    print(f"   • {issue}")

            return test_result

        except Exception as e:
            test_result["issues"].append(f"Test execution failed: {e}")
            print(f"❌ Test execution failed: {e}")
            return test_result

    def test_temporal_analysis_integrity(self, entity_id: str) -> Dict[str, Any]:
        """Test 2: Temporal Analysis Data Integrity"""

        print("\n🔍 TEST 2: TEMPORAL ANALYSIS DATA INTEGRITY")
        print("=" * 50)

        test_result = {
            "test_name": "Temporal Analysis Data Integrity",
            "status": "FAILED",
            "issues": [],
            "temporal_data": {},
            "comparison_integrity": {}
        }

        try:
            # Test temporal analysis query
            query = """
            query TestTemporalIntegrity {{
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
                  }}
                }}
              }}
            }}
            """

            result = self.tilores_api.gql(query)

            if not result or 'data' not in result:
                test_result["issues"].append("Temporal query returned no data")
                return test_result

            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            if not records:
                test_result["issues"].append("No records found for temporal analysis")
                return test_result

            # Analyze temporal data integrity
            total_reports = 0
            reports_with_dates = 0
            unique_dates = set()
            date_consistency_issues = 0

            for record in records:
                credit_response = record.get('CREDIT_RESPONSE', {})
                total_reports += 1

                # Check report date
                report_date = credit_response.get('CreditReportFirstIssuedDate')
                if report_date and report_date != "None":
                    reports_with_dates += 1
                    unique_dates.add(report_date)

                # Check credit file date
                credit_file = credit_response.get('CREDIT_FILE', {})
                file_date = credit_file.get('InfileDate')
                if file_date and file_date != "None":
                    unique_dates.add(file_date)

                # Check for date consistency issues
                score_dates = credit_response.get('CREDIT_SCORE', [])
                for score in score_dates:
                    score_date = score.get('Date')
                    if score_date and score_date != "None":
                        unique_dates.add(score_date)
                    elif score_date == "None":
                        date_consistency_issues += 1

            # Temporal data metrics
            test_result["temporal_data"] = {
                "total_reports": total_reports,
                "reports_with_dates": reports_with_dates,
                "unique_dates": len(unique_dates),
                "date_consistency_issues": date_consistency_issues,
                "date_range": f"{min(unique_dates)} to {max(unique_dates)}" if unique_dates else "N/A"
            }

            # Check for temporal integrity issues
            if reports_with_dates == 0:
                test_result["issues"].append("No reports have valid dates for temporal analysis")

            if len(unique_dates) < 2:
                test_result["issues"].append("Insufficient date diversity for meaningful temporal comparison")

            if date_consistency_issues > 0:
                test_result["issues"].append(f"Found {date_consistency_issues} scores with null dates")

            # Comparison integrity check
            test_result["comparison_integrity"] = {
                "can_compare": len(unique_dates) >= 2,
                "date_coverage": reports_with_dates / total_reports if total_reports > 0 else 0,
                "temporal_granularity": len(unique_dates)
            }

            # Determine test status
            if not test_result["issues"]:
                test_result["status"] = "PASSED"
                print("✅ Temporal Analysis Integrity Test PASSED")
            else:
                test_result["status"] = "FAILED"
                print(f"❌ Temporal Analysis Integrity Test FAILED: {len(test_result['issues'])} issues")
                for issue in test_result["issues"]:
                    print(f"   • {issue}")

            return test_result

        except Exception as e:
            test_result["issues"].append(f"Temporal test execution failed: {e}")
            print(f"❌ Temporal test execution failed: {e}")
            return test_result

    def test_phone_call_integrity(self, entity_id: str) -> Dict[str, Any]:
        """Test 3: Phone Call Data Integrity"""

        print("\n🔍 TEST 3: PHONE CALL DATA INTEGRITY")
        print("=" * 50)

        test_result = {
            "test_name": "Phone Call Data Integrity",
            "status": "FAILED",
            "issues": [],
            "phone_data": {},
            "business_correlation": {}
        }

        try:
            # Test phone call data query
            query = """
            query TestPhoneCallIntegrity {{
              entity(input: {{ id: "{entity_id}" }}) {{
                entity {{
                  recordInsights {{
                    phoneNumbers: valuesDistinct(field: "PHONE_EXTERNAL")
                    createdDates: valuesDistinct(field: "CREATED_DATE")
                    productNames: valuesDistinct(field: "PRODUCT_NAME")
                    transactionAmounts: valuesDistinct(field: "TRANSACTION_AMOUNT")
                    cardTypes: valuesDistinct(field: "CARD_TYPE")
                    paymentMethods: valuesDistinct(field: "PAYMENT_METHOD")
                    statuses: valuesDistinct(field: "STATUS")
                  }}
                }}
              }}
            }}
            """

            result = self.tilores_api.gql(query)

            if not result or 'data' not in result:
                test_result["issues"].append("Phone call query returned no data")
                return test_result

            record_insights = result['data']['entity']['entity']['recordInsights']

            # Analyze phone data integrity
            phone_numbers = record_insights.get("phoneNumbers", [])
            created_dates = record_insights.get("createdDates", [])
            product_names = record_insights.get("productNames", [])
            transaction_amounts = record_insights.get("transactionAmounts", [])
            card_types = record_insights.get("cardTypes", [])
            payment_methods = record_insights.get("paymentMethods", [])
            statuses = record_insights.get("statuses", [])

            # Phone data metrics
            test_result["phone_data"] = {
                "phone_numbers_count": len(phone_numbers),
                "created_dates_count": len(created_dates),
                "product_names_count": len(product_names),
                "transaction_amounts_count": len(transaction_amounts),
                "card_types_count": len(card_types),
                "payment_methods_count": len(payment_methods),
                "statuses_count": len(statuses)
            }

            # Check for phone data integrity issues
            if len(phone_numbers) == 0:
                test_result["issues"].append("No phone numbers found for customer contact")

            if len(created_dates) == 0:
                test_result["issues"].append("No interaction dates found for temporal analysis")

            if len(product_names) == 0:
                test_result["issues"].append("No product data found for business correlation")

            if len(transaction_amounts) == 0:
                test_result["issues"].append("No transaction data found for financial analysis")

            # Business correlation check
            test_result["business_correlation"] = {
                "has_contact_info": len(phone_numbers) > 0,
                "has_temporal_data": len(created_dates) > 0,
                "has_product_data": len(product_names) > 0,
                "has_financial_data": len(transaction_amounts) > 0,
                "correlation_score": sum([
                    len(phone_numbers) > 0,
                    len(created_dates) > 0,
                    len(product_names) > 0,
                    len(transaction_amounts) > 0
                ]) / 4.0
            }

            # Determine test status
            if not test_result["issues"]:
                test_result["status"] = "PASSED"
                print("✅ Phone Call Integrity Test PASSED")
            else:
                test_result["status"] = "FAILED"
                print(f"❌ Phone Call Integrity Test FAILED: {len(test_result['issues'])} issues")
                for issue in test_result["issues"]:
                    print(f"   • {issue}")

            return test_result

        except Exception as e:
            test_result["issues"].append(f"Phone call test execution failed: {e}")
            print(f"❌ Phone call test execution failed: {e}")
            return test_result

    def test_mixed_question_integrity(self, entity_id: str) -> Dict[str, Any]:
        """Test 4: Mixed Question Response Integrity"""

        print("\n🔍 TEST 4: MIXED QUESTION RESPONSE INTEGRITY")
        print("=" * 50)

        test_result = {
            "test_name": "Mixed Question Response Integrity",
            "status": "FAILED",
            "issues": [],
            "question_responses": {},
            "synthesis_quality": {}
        }

        try:
            # Test complex mixed question: "Compare credit utilization and phone interactions over time"
            query = """
            query TestMixedQuestionIntegrity {{
              entity(input: {{ id: "{entity_id}" }}) {{
                entity {{
                  records {{
                    # Credit data
                    CREDIT_RESPONSE {{
                      CreditReportFirstIssuedDate
                      CREDIT_SCORE {{
                        Value
                        ModelNameType
                      }}
                      CREDIT_LIABILITY {{
                        CreditLimitAmount
                        CreditBalance
                        AccountOpenedDate
                      }}
                    }}
                    # Phone/Contact data
                    PHONE_EXTERNAL
                    CREATED_DATE
                    PRODUCT_NAME
                    TRANSACTION_AMOUNT
                  }}
                }}
              }}
            }}
            """

            result = self.tilores_api.gql(query)

            if not result or 'data' not in result:
                test_result["issues"].append("Mixed question query returned no data")
                return test_result

            entity = result['data']['entity']['entity']
            records = entity.get('records', [])

            if not records:
                test_result["issues"].append("No records found for mixed question analysis")
                return test_result

            # Analyze mixed question response integrity
            credit_data_count = 0
            phone_data_count = 0
            temporal_data_count = 0
            business_data_count = 0
            correlation_opportunities = 0

            for record in records:
                # Credit data presence
                if record.get('CREDIT_RESPONSE'):
                    credit_data_count += 1

                # Phone data presence
                if record.get('PHONE_EXTERNAL'):
                    phone_data_count += 1

                # Temporal data presence
                if record.get('CREATED_DATE'):
                    temporal_data_count += 1

                # Business data presence
                if record.get('PRODUCT_NAME') or record.get('TRANSACTION_AMOUNT'):
                    business_data_count += 1

                # Check for correlation opportunities
                if (record.get('CREDIT_RESPONSE') and
                    record.get('PHONE_EXTERNAL') and
                    record.get('CREATED_DATE')):
                    correlation_opportunities += 1

            # Question response metrics
            test_result["question_responses"] = {
                "total_records": len(records),
                "credit_data_count": credit_data_count,
                "phone_data_count": phone_data_count,
                "temporal_data_count": temporal_data_count,
                "business_data_count": business_data_count,
                "correlation_opportunities": correlation_opportunities
            }

            # Check for mixed question integrity issues
            if credit_data_count == 0:
                test_result["issues"].append("No credit data available for utilization analysis")

            if phone_data_count == 0:
                test_result["issues"].append("No phone data available for interaction analysis")

            if temporal_data_count == 0:
                test_result["issues"].append("No temporal data available for time-based comparison")

            if correlation_opportunities == 0:
                test_result["issues"].append("No opportunities for cross-data correlation")

            # Synthesis quality check
            test_result["synthesis_quality"] = {
                "data_completeness": sum([
                    credit_data_count > 0,
                    phone_data_count > 0,
                    temporal_data_count > 0,
                    business_data_count > 0
                ]) / 4.0,
                "correlation_potential": correlation_opportunities / len(records) if records else 0,
                "synthesis_ready": correlation_opportunities > 0
            }

            # Determine test status
            if not test_result["issues"]:
                test_result["status"] = "PASSED"
                print("✅ Mixed Question Integrity Test PASSED")
            else:
                test_result["status"] = "FAILED"
                print(f"❌ Mixed Question Integrity Test FAILED: {len(test_result['issues'])} issues")
                for issue in test_result["issues"]:
                    print(f"   • {issue}")

            return test_result

        except Exception as e:
            test_result["issues"].append(f"Mixed question test execution failed: {e}")
            print(f"❌ Mixed question test execution failed: {e}")
            return test_result

    def run_comprehensive_qa_test(self, entity_id: str) -> Dict[str, Any]:
        """Run comprehensive QA testing suite"""

        print("🚀 COMPREHENSIVE QA TESTING SUITE - CREDIT PROS")
        print("=" * 70)
        print("Goal: Break the system and identify data integrity issues")
        print("Role: Quality Assurance Agent for Credit Repair Clients")
        print("=" * 70)

        if not self.tilores_api:
            print("❌ Cannot run tests: Tilores API not available")
            return {"error": "Tilores API not available"}

        # Run all tests
        tests = [
            self.test_credit_score_integrity(entity_id),
            self.test_temporal_analysis_integrity(entity_id),
            self.test_phone_call_integrity(entity_id),
            self.test_mixed_question_integrity(entity_id)
        ]

        # Compile results
        passed_tests = sum(1 for test in tests if test.get("status") == "PASSED")
        failed_tests = sum(1 for test in tests if test.get("status") == "FAILED")
        total_issues = sum(len(test.get("issues", [])) for test in tests)

        # Overall assessment
        overall_score = passed_tests / len(tests) if tests else 0

        print("\n📊 QA TESTING RESULTS SUMMARY")
        print("=" * 50)
        print(f"   ✅ Passed Tests: {passed_tests}/{len(tests)}")
        print(f"   ❌ Failed Tests: {failed_tests}/{len(tests)}")
        print(f"   🚨 Total Issues: {total_issues}")
        print(f"   📈 Overall Score: {overall_score:.1%}")

        # Critical issues summary
        critical_issues = []
        for test in tests:
            if test.get("status") == "FAILED":
                critical_issues.extend(test.get("issues", []))

        if critical_issues:
            print("\n🚨 CRITICAL ISSUES IDENTIFIED:")
            print("-" * 40)
            for i, issue in enumerate(critical_issues[:10], 1):  # Show first 10
                print(f"   {i}. {issue}")
            if len(critical_issues) > 10:
                print(f"   ... and {len(critical_issues) - 10} more issues")

        # System integrity assessment
        print("\n🔍 SYSTEM INTEGRITY ASSESSMENT:")
        print("-" * 40)

        if overall_score >= 0.8:
            print("   🟢 SYSTEM STATUS: HEALTHY")
            print("   ✅ Data integrity maintained")
            print("   ✅ Response quality acceptable")
        elif overall_score >= 0.6:
            print("   🟡 SYSTEM STATUS: DEGRADED")
            print("   ⚠️  Some data integrity issues")
            print("   ⚠️  Response quality compromised")
        else:
            print("   🔴 SYSTEM STATUS: CRITICAL")
            print("   ❌ Significant data integrity issues")
            print("   ❌ Response quality severely compromised")

        # Recommendations for credit repair clients
        print("\n💡 RECOMMENDATIONS FOR CREDIT REPAIR CLIENTS:")
        print("-" * 50)

        if overall_score < 0.8:
            print("   ⚠️  SYSTEM NOT READY FOR PRODUCTION USE")
            print("   🔍 Data integrity issues may affect client outcomes")
            print("   📋 Recommend thorough testing before client deployment")
        else:
            print("   ✅ SYSTEM READY FOR PRODUCTION USE")
            print("   🎯 Data integrity sufficient for client needs")
            print("   🚀 Safe to deploy for credit repair services")

        return {
            "overall_score": overall_score,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "test_details": tests,
            "system_status": "HEALTHY" if overall_score >= 0.8 else "DEGRADED" if overall_score >= 0.6 else "CRITICAL"
        }

# Global instance
qa_tester = QACreditProsTester()

if __name__ == "__main__":
    print("🚀 QA CREDIT PROS TESTER")
    print("=" * 70)

    # Use known test entity
    entity_id = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

    print("🔍 Running comprehensive QA testing suite...")
    results = qa_tester.run_comprehensive_qa_test(entity_id)

    print("\n🎯 QA TESTING COMPLETE")
    print("=" * 70)
    print(f"System Status: {results.get('system_status', 'UNKNOWN')}")
    print(f"Overall Score: {results.get('overall_score', 0):.1%}")
    print(f"Critical Issues: {len(results.get('critical_issues', []))}")

    if results.get('system_status') == 'CRITICAL':
        print("\n🚨 SYSTEM BREAKING ISSUES IDENTIFIED!")
        print("Credit repair clients should NOT use this system until issues are resolved.")
    elif results.get('system_status') == 'DEGRADED':
        print("\n⚠️  SYSTEM HAS INTEGRITY ISSUES")
        print("Credit repair clients should use with caution and monitoring.")
    else:
        print("\n✅ SYSTEM INTEGRITY MAINTAINED")
        print("Safe for credit repair client use.")
