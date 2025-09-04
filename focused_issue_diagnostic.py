#!/usr/bin/env python3
"""
Focused Issue Diagnostic Test
============================

Based on the comprehensive QA test results, this script focuses on the specific issues found:
1. API_ERROR (17 occurrences) - 14.7% failure rate
2. SLOW_RESPONSE (23 occurrences) - Performance issues
3. MISSING_CUSTOMER_DATA (8 occurrences) - Data retrieval problems
4. POOR_ERROR_HANDLING (2 occurrences) - Edge case handling

This diagnostic will help identify root causes and validate fixes.
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, Any, List

class IssuesDiagnostic:
    def __init__(self, base_url: str = "http://127.0.0.1:8081"):
        self.base_url = base_url
        self.test_results = []

    def make_request(self, query: str, timeout: int = 30) -> Dict[str, Any]:
        """Make API request with detailed error tracking"""
        start_time = time.time()

        try:
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": query}],
                "temperature": 0.7,
                "max_tokens": 1500
            }

            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=timeout
            )

            end_time = time.time()
            response_time = end_time - start_time

            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                return {
                    "success": True,
                    "query": query,
                    "response": content,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat(),
                    "raw_response": result
                }
            else:
                return {
                    "success": False,
                    "query": query,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "query": query,
                "error": "Request timeout",
                "response_time": timeout,
                "status_code": 0,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "response_time": end_time - start_time,
                "status_code": 0,
                "timestamp": datetime.now().isoformat()
            }

    def test_api_errors(self):
        """Test queries that caused API errors"""
        print("🔍 Testing API Error Scenarios...")

        api_error_queries = [
            "",  # Empty query
            "invalid@customer.com",  # Non-existent customer
            "e.j.price1986@gmail.com" * 100,  # Very long query
            "SELECT * FROM customers WHERE email = 'e.j.price1986@gmail.com'",  # SQL injection
            "<script>alert('xss')</script> e.j.price1986@gmail.com",  # XSS attempt
            "e.j.price1986@gmail.com\n\n\n\nwho is this customer",  # Malformed query
            "transaction history for nonexistent@email.com",  # Invalid customer transaction query
            "credit analysis for fake@customer.com",  # Invalid customer credit query
        ]

        for query in api_error_queries:
            print(f"  Testing: {query[:50]}...")
            result = self.make_request(query)
            self.test_results.append({**result, "test_category": "api_errors"})

            if result["success"]:
                print(f"    ✅ Success ({result['response_time']:.2f}s)")
            else:
                print(f"    ❌ Failed: {result['error']}")

            time.sleep(0.1)  # Brief pause between requests

    def test_slow_responses(self):
        """Test queries that caused slow responses"""
        print("\n⏱️  Testing Slow Response Scenarios...")

        heavy_queries = [
            "comprehensive analysis for e.j.price1986@gmail.com",
            "all data for e.j.price1986@gmail.com",
            "combined credit and transaction analysis for e.j.price1986@gmail.com",
            "full customer intelligence for e.j.price1986@gmail.com",
            "detailed credit bureau comparison for e.j.price1986@gmail.com",
            "complete transaction history and payment patterns for e.j.price1986@gmail.com",
        ]

        for query in heavy_queries:
            print(f"  Testing: {query[:50]}...")
            result = self.make_request(query, timeout=45)  # Longer timeout for heavy queries
            self.test_results.append({**result, "test_category": "slow_responses"})

            if result["success"]:
                if result["response_time"] > 10:
                    print(f"    ⚠️  Slow ({result['response_time']:.2f}s)")
                else:
                    print(f"    ✅ Good speed ({result['response_time']:.2f}s)")
            else:
                print(f"    ❌ Failed: {result['error']}")

            time.sleep(0.2)

    def test_missing_customer_data(self):
        """Test queries that should return customer data but didn't"""
        print("\n👤 Testing Customer Data Retrieval...")

        customer_data_queries = [
            "who is e.j.price1986@gmail.com",
            "tell me about customer e.j.price1986@gmail.com",
            "customer profile for e.j.price1986@gmail.com",
            "what do you know about e.j.price1986@gmail.com",
            "show me details for e.j.price1986@gmail.com",
            "analyze customer e.j.price1986@gmail.com",
        ]

        for query in customer_data_queries:
            print(f"  Testing: {query}")
            result = self.make_request(query)
            self.test_results.append({**result, "test_category": "customer_data"})

            if result["success"]:
                response = result["response"].lower()
                has_customer_data = any(term in response for term in ["esteban", "price", "1747598", "dc93a2cd"])

                if has_customer_data:
                    print(f"    ✅ Contains customer data ({result['response_time']:.2f}s)")
                else:
                    print(f"    ⚠️  Missing customer data ({result['response_time']:.2f}s)")
                    print(f"        Response: {result['response'][:100]}...")
            else:
                print(f"    ❌ Failed: {result['error']}")

            time.sleep(0.1)

    def test_error_handling(self):
        """Test error handling for edge cases"""
        print("\n🛡️  Testing Error Handling...")

        error_test_queries = [
            "invalid@customer.com",
            "nonexistent@email.com",
            "fake.customer@test.com",
            "",
            "   ",
            None,
        ]

        for query in error_test_queries:
            if query is None:
                query = ""
            print(f"  Testing: '{query}'")
            result = self.make_request(query)
            self.test_results.append({**result, "test_category": "error_handling"})

            if result["success"]:
                response = result["response"].lower()
                good_error_handling = any(term in response for term in [
                    "not found", "no records", "no data", "invalid", "customer not found",
                    "unable to find", "does not exist"
                ])

                if good_error_handling:
                    print(f"    ✅ Good error handling ({result['response_time']:.2f}s)")
                else:
                    print(f"    ⚠️  Poor error handling ({result['response_time']:.2f}s)")
                    print(f"        Response: {result['response'][:100]}...")
            else:
                print(f"    ❌ API Error: {result['error']}")

            time.sleep(0.1)

    def test_data_source_transitions(self):
        """Test transitions between different data sources"""
        print("\n🔄 Testing Data Source Transitions...")

        # Simulate a conversation jumping between data types
        conversation_queries = [
            "who is e.j.price1986@gmail.com",
            "what is their credit score",
            "show me their transactions",
            "any support tickets",
            "account status",
            "credit utilization",
            "payment history"
        ]

        conversation_id = f"transition_test_{int(time.time())}"

        for i, query in enumerate(conversation_queries):
            print(f"  Step {i+1}: {query}")
            result = self.make_request(query)
            result["conversation_step"] = i + 1
            result["conversation_id"] = conversation_id
            self.test_results.append({**result, "test_category": "data_transitions"})

            if result["success"]:
                print(f"    ✅ Success ({result['response_time']:.2f}s) - {len(result['response'])} chars")
            else:
                print(f"    ❌ Failed: {result['error']}")

            time.sleep(0.5)  # Pause between conversation steps

    def generate_diagnostic_report(self) -> Dict[str, Any]:
        """Generate detailed diagnostic report"""
        if not self.test_results:
            return {"error": "No test results available"}

        # Categorize results
        categories = {}
        for result in self.test_results:
            category = result.get("test_category", "unknown")
            if category not in categories:
                categories[category] = {"total": 0, "successful": 0, "failed": 0, "avg_time": 0, "issues": []}

            categories[category]["total"] += 1
            if result.get("success", False):
                categories[category]["successful"] += 1
            else:
                categories[category]["failed"] += 1
                categories[category]["issues"].append(result.get("error", "Unknown error"))

        # Calculate averages
        for category in categories:
            successful_results = [r for r in self.test_results
                                if r.get("test_category") == category and r.get("success", False)]
            if successful_results:
                categories[category]["avg_time"] = sum(r["response_time"] for r in successful_results) / len(successful_results)

        # Overall statistics
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.get("success", False)])

        report = {
            "diagnostic_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "category_analysis": categories,
            "recommendations": self._generate_recommendations(categories),
            "detailed_failures": [r for r in self.test_results if not r.get("success", False)]
        }

        return report

    def _generate_recommendations(self, categories: Dict) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # API Error recommendations
        if "api_errors" in categories:
            failure_rate = categories["api_errors"]["failed"] / categories["api_errors"]["total"]
            if failure_rate > 0.3:
                recommendations.append("HIGH: Improve input validation and error handling for malformed queries")

        # Performance recommendations
        if "slow_responses" in categories:
            avg_time = categories["slow_responses"]["avg_time"]
            if avg_time > 10:
                recommendations.append(f"MEDIUM: Optimize performance - average response time is {avg_time:.1f}s")

        # Customer data recommendations
        if "customer_data" in categories:
            success_rate = categories["customer_data"]["successful"] / categories["customer_data"]["total"]
            if success_rate < 0.9:
                recommendations.append("HIGH: Fix customer data retrieval - some queries not returning expected data")

        # Error handling recommendations
        if "error_handling" in categories:
            if categories["error_handling"]["failed"] > 0:
                recommendations.append("MEDIUM: Improve error handling for invalid customer queries")

        return recommendations

    def run_all_diagnostics(self):
        """Run all diagnostic tests"""
        print("🚀 Starting Focused Issue Diagnostic Tests")
        print("=" * 50)

        self.test_api_errors()
        self.test_slow_responses()
        self.test_missing_customer_data()
        self.test_error_handling()
        self.test_data_source_transitions()

        # Generate and display report
        report = self.generate_diagnostic_report()

        print("\n" + "=" * 50)
        print("📊 DIAGNOSTIC RESULTS")
        print("=" * 50)

        summary = report["diagnostic_summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Success Rate: {summary['success_rate']:.2%}")

        print("\n📈 Category Analysis:")
        for category, stats in report["category_analysis"].items():
            print(f"  {category}:")
            print(f"    Success: {stats['successful']}/{stats['total']} ({stats['successful']/stats['total']:.2%})")
            if stats['avg_time'] > 0:
                print(f"    Avg Time: {stats['avg_time']:.2f}s")
            if stats['issues']:
                print(f"    Issues: {len(set(stats['issues']))} unique errors")

        if report["recommendations"]:
            print("\n🎯 Recommendations:")
            for rec in report["recommendations"]:
                print(f"  • {rec}")

        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diagnostic_report_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed diagnostic report saved to: {filename}")

        return report

def main():
    diagnostic = IssuesDiagnostic()
    diagnostic.run_all_diagnostics()

if __name__ == "__main__":
    main()
