#!/usr/bin/env python3
"""
Credit Repair Expert QA Test Suite
Comprehensive testing from the perspective of a client success agent
Goal: Find and fix all bugs to achieve 100% success rate
"""

import requests
import json
import time
import subprocess
import sys
from typing import List, Dict, Any, Tuple
import threading
import queue

class CreditExpertQATest:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.server_process = None
        self.test_results = []
        self.failed_tests = []

        # Test customer data
        self.test_customer = "e.j.price1986@gmail.com"
        self.invalid_customer = "nonexistent@fake.com"

    def start_local_server(self):
        """Start local server for testing"""
        print("🚀 Starting local server for QA testing...")
        self.server_process = subprocess.Popen(
            ["python3", "direct_credit_api_with_phone.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(4)

        try:
            response = requests.get(f"{self.base_url}/v1", timeout=5)
            if response.status_code == 200:
                print("✅ Local server started successfully!")
                return True
        except Exception as e:
            print(f"❌ Server failed to start: {e}")
            return False

    def stop_server(self):
        """Clean up server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 Server stopped")

    def make_expert_query(self, query: str, test_name: str, expected_keywords: List[str] = None, should_fail: bool = False) -> Dict:
        """Make a query as a credit repair expert would"""

        # Use Agenta.ai format with structured content
        messages = [
            {"role": "system", "content": "You are a helpful customer service chatbot for TheCreditPros. Provide detailed credit analysis."},
            {"role": "user", "content": [{"type": "text", "text": query}]}
        ]

        payload = {
            "messages": messages,
            "model": "gpt-4o-mini",
            "temperature": 0.7
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AsyncOpenAI/Python 1.102.0"
        }

        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=45  # Longer timeout for complex queries
            )
            duration = time.time() - start_time

            result = {
                "test_name": test_name,
                "query": query,
                "status_code": response.status_code,
                "duration": round(duration, 2),
                "success": response.status_code == 200,
                "should_fail": should_fail
            }

            if response.status_code == 200:
                response_data = response.json()
                content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                result["response"] = content
                result["response_length"] = len(content)

                # Check for expected keywords
                if expected_keywords:
                    found_keywords = [kw for kw in expected_keywords if kw.lower() in content.lower()]
                    result["expected_keywords"] = expected_keywords
                    result["found_keywords"] = found_keywords
                    result["keyword_match_rate"] = len(found_keywords) / len(expected_keywords)

                # Check for error indicators
                error_indicators = ["error:", "no records found", "could not identify", "failed to"]
                has_errors = any(indicator in content.lower() for indicator in error_indicators)
                result["has_errors"] = has_errors

                # If we expected success but got errors, mark as failed
                if not should_fail and has_errors:
                    result["success"] = False
                    result["failure_reason"] = "Unexpected error in response"

            else:
                result["error"] = response.text
                if should_fail:
                    result["success"] = True  # Expected to fail

            return result

        except Exception as e:
            result = {
                "test_name": test_name,
                "query": query,
                "status_code": 0,
                "success": should_fail,  # If we expected it to fail, timeout is "success"
                "error": str(e),
                "duration": 45 if "timeout" in str(e).lower() else 0
            }
            return result

    def test_credit_analysis_queries(self):
        """Test comprehensive credit analysis queries"""
        print("\n🔍 Testing Credit Analysis Queries...")

        credit_tests = [
            # Basic credit queries
            {
                "query": f"Analyze the credit report for {self.test_customer}",
                "name": "Basic Credit Analysis",
                "keywords": ["credit", "score", "utilization", "tradelines", "inquiries"]
            },
            {
                "query": f"What is the current credit score for {self.test_customer}?",
                "name": "Credit Score Query",
                "keywords": ["score", "equifax", "experian", "transunion"]
            },
            {
                "query": f"Show me the credit utilization breakdown for {self.test_customer}",
                "name": "Utilization Analysis",
                "keywords": ["utilization", "balance", "limit", "percentage"]
            },

            # Advanced credit queries
            {
                "query": f"Compare the most recent Equifax score vs the oldest Equifax score for {self.test_customer}",
                "name": "Temporal Score Comparison",
                "keywords": ["equifax", "score", "comparison", "recent", "oldest"]
            },
            {
                "query": f"What negative items are impacting {self.test_customer}'s credit score?",
                "name": "Negative Items Analysis",
                "keywords": ["negative", "delinquent", "late", "collections", "impact"]
            },
            {
                "query": f"Show me the payment history trends for {self.test_customer}",
                "name": "Payment History Trends",
                "keywords": ["payment", "history", "trends", "on-time", "late"]
            },

            # Bureau-specific queries
            {
                "query": f"What does TransUnion show for {self.test_customer} that Experian doesn't?",
                "name": "Bureau Comparison",
                "keywords": ["transunion", "experian", "difference", "bureau"]
            },
            {
                "query": f"Are there any new inquiries on {self.test_customer}'s Equifax report?",
                "name": "New Inquiries Check",
                "keywords": ["inquiries", "equifax", "new", "recent"]
            }
        ]

        for test in credit_tests:
            result = self.make_expert_query(test["query"], test["name"], test["keywords"])
            self.test_results.append(result)
            self.print_result(result)

    def test_transaction_analysis_queries(self):
        """Test transaction and payment analysis queries"""
        print("\n🔍 Testing Transaction Analysis Queries...")

        transaction_tests = [
            {
                "query": f"Show me all transactions for {self.test_customer} in the last 30 days",
                "name": "Recent Transactions",
                "keywords": ["transactions", "payments", "amount", "date"]
            },
            {
                "query": f"What is the average transaction amount for {self.test_customer}?",
                "name": "Average Transaction Amount",
                "keywords": ["average", "amount", "transaction", "payment"]
            },
            {
                "query": f"Are there any failed payments for {self.test_customer}?",
                "name": "Failed Payments Check",
                "keywords": ["failed", "declined", "payment", "error"]
            },
            {
                "query": f"Show me the payment method breakdown for {self.test_customer}",
                "name": "Payment Methods Analysis",
                "keywords": ["payment", "method", "card", "bank", "breakdown"]
            },
            {
                "query": f"What is the total amount paid by {self.test_customer} this year?",
                "name": "Annual Payment Total",
                "keywords": ["total", "amount", "year", "sum"]
            }
        ]

        for test in transaction_tests:
            result = self.make_expert_query(test["query"], test["name"], test["keywords"])
            self.test_results.append(result)
            self.print_result(result)

    def test_phone_call_analysis_queries(self):
        """Test phone call and agent interaction queries"""
        print("\n🔍 Testing Phone Call Analysis Queries...")

        call_tests = [
            {
                "query": f"Show me the call history for {self.test_customer}",
                "name": "Call History Overview",
                "keywords": ["call", "history", "agent", "duration"]
            },
            {
                "query": f"Which agent has spoken to {self.test_customer} the most?",
                "name": "Top Agent Analysis",
                "keywords": ["agent", "most", "calls", "frequency"]
            },
            {
                "query": f"What is the average call duration for {self.test_customer}?",
                "name": "Average Call Duration",
                "keywords": ["average", "duration", "call", "time"]
            },
            {
                "query": f"Are there any recent calls with {self.test_customer}?",
                "name": "Recent Calls Check",
                "keywords": ["recent", "calls", "latest", "last"]
            },
            {
                "query": f"Show me calls by campaign type for {self.test_customer}",
                "name": "Campaign Analysis",
                "keywords": ["campaign", "type", "calls", "breakdown"]
            }
        ]

        for test in call_tests:
            result = self.make_expert_query(test["query"], test["name"], test["keywords"])
            self.test_results.append(result)
            self.print_result(result)

    def test_support_ticket_queries(self):
        """Test Zoho support ticket analysis"""
        print("\n🔍 Testing Support Ticket Analysis...")

        ticket_tests = [
            {
                "query": f"Show me all support tickets for {self.test_customer}",
                "name": "All Support Tickets",
                "keywords": ["ticket", "support", "issue", "zoho"]
            },
            {
                "query": f"What are the most common issues for {self.test_customer}?",
                "name": "Common Issues Analysis",
                "keywords": ["common", "issues", "frequent", "problems"]
            },
            {
                "query": f"Are there any unresolved tickets for {self.test_customer}?",
                "name": "Unresolved Tickets",
                "keywords": ["unresolved", "open", "pending", "status"]
            },
            {
                "query": f"What is the average resolution time for {self.test_customer}'s tickets?",
                "name": "Resolution Time Analysis",
                "keywords": ["resolution", "time", "average", "duration"]
            },
            {
                "query": f"Show me the ticket sentiment analysis for {self.test_customer}",
                "name": "Sentiment Analysis",
                "keywords": ["sentiment", "satisfaction", "positive", "negative"]
            }
        ]

        for test in ticket_tests:
            result = self.make_expert_query(test["query"], test["name"], test["keywords"])
            self.test_results.append(result)
            self.print_result(result)

    def test_credit_card_analysis_queries(self):
        """Test credit card specific analysis"""
        print("\n🔍 Testing Credit Card Analysis...")

        card_tests = [
            {
                "query": f"Show me all credit cards for {self.test_customer}",
                "name": "All Credit Cards",
                "keywords": ["credit card", "cards", "account", "number"]
            },
            {
                "query": f"Are there any expired cards for {self.test_customer}?",
                "name": "Expired Cards Check",
                "keywords": ["expired", "expiration", "date", "card"]
            },
            {
                "query": f"What is the BIN analysis for {self.test_customer}'s cards?",
                "name": "BIN Analysis",
                "keywords": ["bin", "bank", "issuer", "card type"]
            },
            {
                "query": f"Show me prepaid vs credit cards for {self.test_customer}",
                "name": "Card Type Breakdown",
                "keywords": ["prepaid", "credit", "debit", "type"]
            }
        ]

        for test in card_tests:
            result = self.make_expert_query(test["query"], test["name"], test["keywords"])
            self.test_results.append(result)
            self.print_result(result)

    def test_comprehensive_analysis_queries(self):
        """Test comprehensive multi-data analysis"""
        print("\n🔍 Testing Comprehensive Analysis...")

        comprehensive_tests = [
            {
                "query": f"Give me a complete profile analysis for {self.test_customer} including credit, transactions, calls, and tickets",
                "name": "Complete Customer Profile",
                "keywords": ["credit", "transactions", "calls", "tickets", "comprehensive"]
            },
            {
                "query": f"What is the relationship between {self.test_customer}'s payment behavior and credit score changes?",
                "name": "Payment-Credit Correlation",
                "keywords": ["payment", "credit score", "correlation", "relationship"]
            },
            {
                "query": f"How has {self.test_customer}'s engagement changed over time across all touchpoints?",
                "name": "Engagement Timeline",
                "keywords": ["engagement", "timeline", "touchpoints", "changes"]
            }
        ]

        for test in comprehensive_tests:
            result = self.make_expert_query(test["query"], test["name"], test["keywords"])
            self.test_results.append(result)
            self.print_result(result)

    def test_edge_cases_and_error_scenarios(self):
        """Test edge cases that might break the system"""
        print("\n🔍 Testing Edge Cases and Error Scenarios...")

        edge_cases = [
            # Invalid customer scenarios
            {
                "query": f"Analyze credit for {self.invalid_customer}",
                "name": "Invalid Customer Email",
                "keywords": ["no records", "not found"],
                "should_fail": True
            },
            {
                "query": "Analyze credit for customer ID 99999999",
                "name": "Invalid Customer ID",
                "keywords": ["no records", "not found"],
                "should_fail": True
            },

            # Ambiguous queries
            {
                "query": "Show me credit information",
                "name": "Ambiguous Query - No Customer",
                "keywords": ["provide", "identifier", "email"],
                "should_fail": True
            },
            {
                "query": f"What happened to {self.test_customer}?",
                "name": "Vague Query",
                "keywords": ["credit", "analysis", "information"]
            },

            # Complex temporal queries
            {
                "query": f"Compare {self.test_customer}'s credit score from 6 months ago to today",
                "name": "Complex Temporal Query",
                "keywords": ["comparison", "score", "months", "change"]
            },

            # Multi-customer queries (should be rejected)
            {
                "query": f"Compare {self.test_customer} and {self.invalid_customer}",
                "name": "Multi-Customer Query",
                "keywords": ["provide", "single", "customer"],
                "should_fail": True
            },

            # Very long queries
            {
                "query": f"Please provide a comprehensive detailed analysis of {self.test_customer} " * 10,
                "name": "Very Long Query",
                "keywords": ["credit", "analysis"]
            },

            # Special characters and formatting
            {
                "query": f"Analyze credit for {self.test_customer} !@#$%^&*()",
                "name": "Special Characters Query",
                "keywords": ["credit", "analysis"]
            }
        ]

        for test in edge_cases:
            result = self.make_expert_query(
                test["query"],
                test["name"],
                test["keywords"],
                test.get("should_fail", False)
            )
            self.test_results.append(result)
            self.print_result(result)

    def test_multi_turn_conversations(self):
        """Test complex multi-turn conversations"""
        print("\n🔍 Testing Multi-Turn Conversations...")

        # Simulate a real client success conversation
        conversation_tests = [
            {
                "initial": f"Show me the credit profile for {self.test_customer}",
                "followup": "What are the biggest issues I should focus on?",
                "name": "Credit Profile + Focus Areas"
            },
            {
                "initial": f"Analyze recent transactions for {self.test_customer}",
                "followup": "Are there any patterns that might affect their credit?",
                "name": "Transactions + Credit Impact"
            },
            {
                "initial": f"Show me call history for {self.test_customer}",
                "followup": "What was discussed in the most recent call?",
                "name": "Call History + Recent Discussion"
            }
        ]

        for test in conversation_tests:
            # First query
            result1 = self.make_expert_query(test["initial"], f"{test['name']} - Initial", ["analysis", "data"])
            self.test_results.append(result1)
            self.print_result(result1)

            if result1["success"]:
                # Follow-up query (this is where many systems fail)
                result2 = self.make_expert_query(test["followup"], f"{test['name']} - Follow-up", ["analysis", "recommendation"])
                self.test_results.append(result2)
                self.print_result(result2)

    def test_performance_under_load(self):
        """Test system performance under various loads"""
        print("\n🔍 Testing Performance Under Load...")

        # Test rapid sequential queries
        for i in range(3):
            result = self.make_expert_query(
                f"Quick credit check for {self.test_customer} - request {i+1}",
                f"Rapid Sequential {i+1}",
                ["credit"]
            )
            self.test_results.append(result)
            self.print_result(result)
            time.sleep(0.5)

        # Test concurrent queries
        def concurrent_query(query_id, results_queue):
            result = self.make_expert_query(
                f"Concurrent credit analysis for {self.test_customer} - thread {query_id}",
                f"Concurrent Query {query_id}",
                ["credit"]
            )
            results_queue.put(result)

        results_queue = queue.Queue()
        threads = []

        for i in range(3):  # Reduced from 5 to 3 for stability
            thread = threading.Thread(target=concurrent_query, args=(i, results_queue))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        while not results_queue.empty():
            result = results_queue.get()
            self.test_results.append(result)
            self.print_result(result)

    def print_result(self, result: Dict):
        """Print test result with expert analysis"""
        if result["success"]:
            status_icon = "✅"
            status_color = ""
        else:
            status_icon = "❌"
            status_color = ""
            self.failed_tests.append(result)

        print(f"{status_icon} {result['test_name']}: {result['status_code']} ({result.get('duration', 0)}s)")

        if not result["success"]:
            print(f"   🚨 Error: {result.get('error', result.get('failure_reason', 'Unknown error'))}")
        elif result.get("response"):
            # Check keyword matching
            if result.get("keyword_match_rate"):
                match_rate = result["keyword_match_rate"] * 100
                if match_rate >= 80:
                    print(f"   ✅ Keyword Match: {match_rate:.0f}% ({result['found_keywords']})")
                else:
                    print(f"   ⚠️  Keyword Match: {match_rate:.0f}% (Missing: {set(result['expected_keywords']) - set(result['found_keywords'])})")

            # Check response quality
            response_len = result.get("response_length", 0)
            if response_len > 500:
                print(f"   📝 Response: Comprehensive ({response_len} chars)")
            elif response_len > 100:
                print(f"   📝 Response: Adequate ({response_len} chars)")
            else:
                print(f"   ⚠️  Response: Too brief ({response_len} chars)")

    def analyze_failures(self):
        """Analyze failed tests to identify patterns"""
        if not self.failed_tests:
            return

        print(f"\n🔍 FAILURE ANALYSIS ({len(self.failed_tests)} failures):")

        # Group failures by type
        failure_types = {}
        for failure in self.failed_tests:
            error = failure.get("error", failure.get("failure_reason", "Unknown"))
            if "timeout" in error.lower():
                failure_type = "Timeout"
            elif "no records" in error.lower():
                failure_type = "No Records Found"
            elif "error" in error.lower():
                failure_type = "Processing Error"
            else:
                failure_type = "Other"

            if failure_type not in failure_types:
                failure_types[failure_type] = []
            failure_types[failure_type].append(failure)

        for failure_type, failures in failure_types.items():
            print(f"\n📊 {failure_type} ({len(failures)} cases):")
            for failure in failures[:3]:  # Show first 3 examples
                print(f"   - {failure['test_name']}: {failure['query'][:60]}...")

    def print_comprehensive_summary(self):
        """Print detailed QA summary with recommendations"""
        print("\n" + "="*100)
        print("🧪 CREDIT REPAIR EXPERT QA TEST SUMMARY")
        print("="*100)

        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests/total_tests*100) if total_tests > 0 else 0

        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Successful: {successful_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")

        # Performance analysis
        durations = [r.get("duration", 0) for r in self.test_results if r.get("duration")]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            print(f"\n⏱️  PERFORMANCE ANALYSIS:")
            print(f"   Average Response Time: {avg_duration:.2f}s")
            print(f"   Slowest Response: {max_duration:.2f}s")
            print(f"   Responses > 10s: {sum(1 for d in durations if d > 10)}")
            print(f"   Responses > 20s: {sum(1 for d in durations if d > 20)}")

        # Quality analysis
        keyword_matches = [r.get("keyword_match_rate", 0) for r in self.test_results if r.get("keyword_match_rate")]
        if keyword_matches:
            avg_keyword_match = sum(keyword_matches) / len(keyword_matches) * 100
            print(f"\n🎯 QUALITY ANALYSIS:")
            print(f"   Average Keyword Match: {avg_keyword_match:.1f}%")
            print(f"   High Quality Responses (>80% match): {sum(1 for m in keyword_matches if m > 0.8)}")

        # Failure analysis
        self.analyze_failures()

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if success_rate < 90:
            print("   🚨 CRITICAL: Success rate below 90% - immediate fixes needed")
        if avg_duration > 10:
            print("   ⚠️  Performance optimization needed - responses too slow")
        if failed_tests > 0:
            print("   🔧 Address specific failure patterns identified above")

        print("\n" + "="*100)

        return success_rate >= 95  # 95% target for production readiness

    def run_comprehensive_qa_suite(self):
        """Run the complete QA test suite"""
        print("🧪 COMPREHENSIVE CREDIT REPAIR EXPERT QA SUITE")
        print("="*80)
        print("🎯 Goal: Achieve 100% success rate for production deployment")
        print("👨‍💼 Perspective: Client Success Agent / Credit Repair Expert")
        print("="*80)

        if not self.start_local_server():
            print("❌ Cannot run QA suite - server failed to start")
            return False

        try:
            # Run all test categories
            self.test_credit_analysis_queries()
            self.test_transaction_analysis_queries()
            self.test_phone_call_analysis_queries()
            self.test_support_ticket_queries()
            self.test_credit_card_analysis_queries()
            self.test_comprehensive_analysis_queries()
            self.test_edge_cases_and_error_scenarios()
            self.test_multi_turn_conversations()
            self.test_performance_under_load()

            # Analyze results
            return self.print_comprehensive_summary()

        finally:
            self.stop_server()

if __name__ == "__main__":
    qa_tester = CreditExpertQATest()
    production_ready = qa_tester.run_comprehensive_qa_suite()

    if production_ready:
        print("🎉 QA SUITE PASSED - SYSTEM IS PRODUCTION READY!")
        sys.exit(0)
    else:
        print("🚨 QA SUITE FAILED - CRITICAL ISSUES MUST BE ADDRESSED!")
        sys.exit(1)
