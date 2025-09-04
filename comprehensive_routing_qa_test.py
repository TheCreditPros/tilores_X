#!/usr/bin/env python3
"""
Comprehensive Multi-Threaded QA Testing for Routing System
Goal: Try to break the routing system and ensure accuracy, succinctness, and precision
"""

import sys
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Any

sys.path.append('.')
from direct_credit_api_fixed import MultiProviderCreditAPI

class RoutingQATester:
    def __init__(self):
        self.api = MultiProviderCreditAPI()
        self.results = []
        self.lock = threading.Lock()
        self.test_customers = [
            "e.j.price1986@gmail.com",
            "1747598",  # Client ID
            "Esteban Price",  # Name
            "invalid@email.com",  # Invalid customer
            "999999",  # Invalid client ID
        ]

    def evaluate_response_quality(self, query: str, response: str, expected_type: str) -> Dict:
        """Evaluate response quality based on QA criteria"""
        evaluation = {
            'accurate': True,
            'succinct': True,
            'precise': True,
            'data_specific': True,
            'issues': []
        }

        # Check accuracy
        if "I don't have access" in response or "please note that I" in response:
            evaluation['accurate'] = False
            evaluation['issues'].append("Generic disclaimer instead of real data")

        # Check succinctness (length-based heuristics)
        if expected_type == "status" and len(response) > 300:
            evaluation['succinct'] = False
            evaluation['issues'].append(f"Status response too long: {len(response)} chars")
        elif expected_type == "general" and len(response) > 500:
            evaluation['succinct'] = False
            evaluation['issues'].append(f"General response too long: {len(response)} chars")
        elif "comprehensive analysis" in response.lower() and expected_type != "multi_data":
            evaluation['succinct'] = False
            evaluation['issues'].append("Verbose analysis for simple query")

        # Check precision (specific to query type)
        if expected_type == "status":
            if not ("Active" in response or "Past Due" in response or "Canceled" in response):
                evaluation['precise'] = False
                evaluation['issues'].append("Status query missing status information")
        elif expected_type == "general" and "who is" in query.lower():
            if not ("Esteban Price" in response or "1747598" in response):
                evaluation['precise'] = False
                evaluation['issues'].append("Customer profile missing key identifiers")

        # Check data specificity
        if "entity" in response and "dc93a2cd" not in response:
            evaluation['data_specific'] = False
            evaluation['issues'].append("Generic entity reference instead of specific ID")

        return evaluation

    def test_single_query(self, query: str, expected_type: str, conversation_context: str = "") -> Dict:
        """Test a single query with quality evaluation"""
        try:
            start_time = time.time()

            # Test routing
            detected_type = self.api.detect_query_type(query)

            # Test full response
            response = self.api.process_chat_request(query, 'gpt-4o-mini')

            duration = time.time() - start_time

            # Evaluate response quality
            quality = self.evaluate_response_quality(query, response, expected_type)

            result = {
                'query': query,
                'expected_type': expected_type,
                'detected_type': detected_type,
                'response': response,
                'response_length': len(response),
                'duration': duration,
                'conversation_context': conversation_context,
                'routing_correct': detected_type == expected_type,
                'quality': quality,
                'overall_score': sum([
                    quality['accurate'],
                    quality['succinct'],
                    quality['precise'],
                    quality['data_specific'],
                    detected_type == expected_type
                ]) / 5.0
            }

            with self.lock:
                self.results.append(result)
                status = "✅" if result['overall_score'] >= 0.8 else "⚠️" if result['overall_score'] >= 0.6 else "❌"
                print(f"{status} {query[:40]:<40} → {detected_type:<12} ({result['overall_score']:.1f}) {len(response)}ch")

            return result

        except Exception as e:
            error_result = {
                'query': query,
                'expected_type': expected_type,
                'detected_type': 'ERROR',
                'error': str(e),
                'duration': 0,
                'routing_correct': False,
                'overall_score': 0.0
            }

            with self.lock:
                self.results.append(error_result)
                print(f"❌ {query[:40]:<40} → ERROR: {str(e)}")

            return error_result

def generate_comprehensive_test_cases() -> List[Tuple[str, str, str]]:
    """Generate comprehensive test cases to break the routing system"""

    test_cases = []

    # 1. BASIC CUSTOMER PROFILE QUERIES (should be concise)
    profile_queries = [
        ("who is e.j.price1986@gmail.com", "general", "basic_profile"),
        ("tell me about e.j.price1986@gmail.com", "general", "basic_profile"),
        ("customer profile for e.j.price1986@gmail.com", "general", "basic_profile"),
        ("profile of client 1747598", "general", "basic_profile"),
        ("information about Esteban Price", "general", "basic_profile"),
        ("e.j.price1986@gmail.com", "general", "basic_profile"),
    ]
    test_cases.extend(profile_queries)

    # 2. ACCOUNT STATUS QUERIES (should be very concise)
    status_queries = [
        ("account status for e.j.price1986@gmail.com", "status", "status_check"),
        ("is e.j.price1986@gmail.com active", "status", "status_check"),
        ("customer status e.j.price1986@gmail.com", "status", "status_check"),
        ("subscription status for client 1747598", "status", "status_check"),
        ("enrollment status Esteban Price", "status", "status_check"),
    ]
    test_cases.extend(status_queries)

    # 3. CREDIT QUERIES (can be longer but focused)
    credit_queries = [
        ("credit score for e.j.price1986@gmail.com", "credit", "credit_analysis"),
        ("experian score e.j.price1986@gmail.com", "credit", "credit_analysis"),
        ("credit report for client 1747598", "credit", "credit_analysis"),
        ("utilization rate e.j.price1986@gmail.com", "credit", "credit_analysis"),
        ("bureau information for Esteban Price", "credit", "credit_analysis"),
    ]
    test_cases.extend(credit_queries)

    # 4. TRANSACTION QUERIES (focused on payments)
    transaction_queries = [
        ("transaction history e.j.price1986@gmail.com", "transaction", "payment_analysis"),
        ("payment history for client 1747598", "transaction", "payment_analysis"),
        ("billing information e.j.price1986@gmail.com", "transaction", "payment_analysis"),
        ("recent payments Esteban Price", "transaction", "payment_analysis"),
    ]
    test_cases.extend(transaction_queries)

    # 5. MULTI-DATA QUERIES (comprehensive but structured)
    multi_data_queries = [
        ("comprehensive analysis e.j.price1986@gmail.com", "multi_data", "comprehensive"),
        ("full analysis client 1747598", "multi_data", "comprehensive"),
        ("credit and transaction data e.j.price1986@gmail.com", "multi_data", "comprehensive"),
        ("complete profile Esteban Price", "multi_data", "comprehensive"),
    ]
    test_cases.extend(multi_data_queries)

    # 6. EDGE CASES TO BREAK THE SYSTEM
    edge_cases = [
        # Ambiguous queries
        ("e.j.price1986@gmail.com status credit", "general", "ambiguous"),
        ("status and credit for e.j.price1986@gmail.com", "multi_data", "ambiguous"),
        ("quick status e.j.price1986@gmail.com", "status", "ambiguous"),

        # Invalid customers
        ("who is invalid@email.com", "general", "invalid_customer"),
        ("account status for nonexistent@test.com", "status", "invalid_customer"),
        ("credit score for client 999999", "credit", "invalid_customer"),

        # Empty/minimal queries
        ("e.j.price1986@gmail.com?", "general", "minimal"),
        ("1747598", "general", "minimal"),
        ("Esteban", "general", "minimal"),

        # Mixed case and formatting
        ("WHO IS E.J.PRICE1986@GMAIL.COM", "general", "formatting"),
        ("Account Status For e.j.price1986@gmail.com", "status", "formatting"),
        ("CREDIT SCORE e.j.price1986@gmail.com", "credit", "formatting"),

        # Typos and variations
        ("who is e.j.price1986@gmai.com", "general", "typo"),  # Typo in email
        ("accont status e.j.price1986@gmail.com", "status", "typo"),  # Typo in query
        ("credt score e.j.price1986@gmail.com", "credit", "typo"),  # Typo in query

        # Context-dependent queries (should fail gracefully)
        ("what about their credit score", "general", "context_dependent"),
        ("and their transaction history", "general", "context_dependent"),
        ("how about the status", "general", "context_dependent"),
    ]
    test_cases.extend(edge_cases)

    # 7. MULTI-TURN CONVERSATION SIMULATION
    conversation_queries = [
        ("who is e.j.price1986@gmail.com", "general", "turn_1"),
        ("what is their account status", "general", "turn_2"),  # Should require customer info
        ("show me their credit score", "general", "turn_3"),   # Should require customer info
        ("account status for e.j.price1986@gmail.com", "status", "turn_4"),  # Explicit customer
    ]
    test_cases.extend(conversation_queries)

    return test_cases

def run_comprehensive_qa_testing():
    """Run comprehensive QA testing with multi-threading"""

    print("🧪 COMPREHENSIVE ROUTING QA TESTING")
    print("=" * 80)
    print("Goal: Break the routing system and ensure accuracy, succinctness, precision")
    print()

    test_cases = generate_comprehensive_test_cases()
    tester = RoutingQATester()

    print(f"🚀 Running {len(test_cases)} QA tests with {min(12, len(test_cases))} threads...")
    print(f"{'Query':<40} {'Route':<12} {'Score':<6} {'Length'}")
    print("-" * 80)

    # Run tests in parallel
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [
            executor.submit(tester.test_single_query, query, expected, context)
            for query, expected, context in test_cases
        ]

        # Wait for all tests to complete
        for future in as_completed(futures):
            future.result()

    print()
    print("📊 QA TEST ANALYSIS")
    print("=" * 80)

    # Overall statistics
    total_tests = len(tester.results)
    high_quality = sum(1 for r in tester.results if r.get('overall_score', 0) >= 0.8)
    medium_quality = sum(1 for r in tester.results if 0.6 <= r.get('overall_score', 0) < 0.8)
    low_quality = sum(1 for r in tester.results if r.get('overall_score', 0) < 0.6)
    errors = sum(1 for r in tester.results if r.get('detected_type') == 'ERROR')

    print(f"Total Tests: {total_tests}")
    print(f"High Quality (≥80%): {high_quality}/{total_tests} ({high_quality/total_tests*100:.1f}%)")
    print(f"Medium Quality (60-79%): {medium_quality}/{total_tests} ({medium_quality/total_tests*100:.1f}%)")
    print(f"Low Quality (<60%): {low_quality}/{total_tests} ({low_quality/total_tests*100:.1f}%)")
    print(f"Errors: {errors}")
    print()

    # Routing accuracy
    correct_routing = sum(1 for r in tester.results if r.get('routing_correct') == True)
    print(f"Routing Accuracy: {correct_routing}/{total_tests} ({correct_routing/total_tests*100:.1f}%)")
    print()

    # Quality issues breakdown
    print("🚨 QUALITY ISSUES BREAKDOWN:")
    all_issues = []
    for result in tester.results:
        if 'quality' in result and result['quality'].get('issues'):
            all_issues.extend(result['quality']['issues'])

    issue_counts = {}
    for issue in all_issues:
        issue_counts[issue] = issue_counts.get(issue, 0) + 1

    for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {issue}: {count} occurrences")
    print()

    # Worst performing queries
    print("❌ WORST PERFORMING QUERIES:")
    worst_results = sorted(tester.results, key=lambda x: x.get('overall_score', 0))[:10]
    for result in worst_results:
        print(f"  Score: {result.get('overall_score', 0):.1f} - {result['query'][:60]}")
        if 'quality' in result and result['quality'].get('issues'):
            for issue in result['quality']['issues'][:2]:  # Show top 2 issues
                print(f"    Issue: {issue}")
    print()

    # Performance analysis
    avg_duration = sum(r.get('duration', 0) for r in tester.results) / len(tester.results)
    slow_queries = [r for r in tester.results if r.get('duration', 0) > avg_duration * 2]

    print(f"⏱️ PERFORMANCE ANALYSIS:")
    print(f"Average Response Time: {avg_duration:.1f}s")
    print(f"Slow Queries (>2x avg): {len(slow_queries)}")
    print()

    # Final verdict
    overall_pass_rate = high_quality / total_tests
    print("🎯 FINAL QA VERDICT:")
    if overall_pass_rate >= 0.9:
        print(f"✅ EXCELLENT - {overall_pass_rate*100:.1f}% high quality responses")
        print("   System is ready for deployment")
    elif overall_pass_rate >= 0.8:
        print(f"⚠️ GOOD - {overall_pass_rate*100:.1f}% high quality responses")
        print("   Minor issues to address before deployment")
    else:
        print(f"❌ NEEDS WORK - {overall_pass_rate*100:.1f}% high quality responses")
        print("   Significant issues must be fixed before deployment")

    return tester.results

if __name__ == "__main__":
    results = run_comprehensive_qa_testing()
