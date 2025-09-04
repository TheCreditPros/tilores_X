#!/usr/bin/env python3
"""
Comprehensive QA Stress Testing Suite
=====================================

Multi-threaded testing framework designed to simulate real client success scenarios
and identify potential flaws in the TLRS system through extensive conversation testing.

Features:
- Multi-threaded concurrent conversation simulation
- Cross-data-source query testing
- Conversation restart and context handling
- Edge case and error condition testing
- Response quality and consistency analysis
- Performance monitoring under load
"""

import time
import json
import requests
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import statistics

class TLRSQATestSuite:
    def __init__(self, base_url: str = "http://localhost:8081"):
        self.base_url = base_url
        self.test_results = []
        self.performance_metrics = []
        self.conversation_logs = []

        # Test customer data
        self.test_customer = "e.j.price1986@gmail.com"

        # Comprehensive test scenarios
        self.client_success_scenarios = [
            # Basic customer profile queries
            {
                "category": "customer_profile",
                "conversations": [
                    ["who is e.j.price1986@gmail.com"],
                    ["tell me about customer e.j.price1986@gmail.com"],
                    ["customer profile for e.j.price1986@gmail.com"],
                    ["what do you know about e.j.price1986@gmail.com"],
                ]
            },

            # Account status inquiries
            {
                "category": "account_status",
                "conversations": [
                    ["what is the account status for e.j.price1986@gmail.com"],
                    ["is e.j.price1986@gmail.com account active"],
                    ["customer status e.j.price1986@gmail.com"],
                    ["subscription status for e.j.price1986@gmail.com"],
                ]
            },

            # Credit analysis deep dives
            {
                "category": "credit_analysis",
                "conversations": [
                    ["analyze credit for e.j.price1986@gmail.com"],
                    ["what is the credit score for e.j.price1986@gmail.com"],
                    ["credit utilization for e.j.price1986@gmail.com"],
                    ["bureau comparison for e.j.price1986@gmail.com"],
                ]
            },

            # Transaction analysis
            {
                "category": "transaction_analysis",
                "conversations": [
                    ["transaction history for e.j.price1986@gmail.com"],
                    ["payment patterns for e.j.price1986@gmail.com"],
                    ["billing analysis for e.j.price1986@gmail.com"],
                    ["refund history for e.j.price1986@gmail.com"],
                ]
            },

            # Multi-data comprehensive analysis
            {
                "category": "multi_data_analysis",
                "conversations": [
                    ["comprehensive analysis for e.j.price1986@gmail.com"],
                    ["all data for e.j.price1986@gmail.com"],
                    ["combined credit and transaction analysis for e.j.price1986@gmail.com"],
                    ["full customer intelligence for e.j.price1986@gmail.com"],
                ]
            },

            # Cross-data-source jumping scenarios
            {
                "category": "data_source_jumping",
                "conversations": [
                    [
                        "who is e.j.price1986@gmail.com",
                        "what is their credit score",
                        "show me their transactions",
                        "any support tickets",
                        "account status"
                    ],
                    [
                        "credit analysis for e.j.price1986@gmail.com",
                        "now show transactions",
                        "what about their account status",
                        "comprehensive view please"
                    ],
                    [
                        "transaction history for e.j.price1986@gmail.com",
                        "credit utilization",
                        "bureau comparison",
                        "support history"
                    ]
                ]
            },

            # Edge cases and error conditions
            {
                "category": "edge_cases",
                "conversations": [
                    [""],  # Empty query
                    ["invalid@customer.com"],  # Non-existent customer
                    ["e.j.price1986@gmail.com" * 50],  # Very long query
                    ["SELECT * FROM customers"],  # SQL injection attempt
                    ["<script>alert('xss')</script> e.j.price1986@gmail.com"],  # XSS attempt
                    ["e.j.price1986@gmail.com\n\n\nwho is this"],  # Malformed query
                ]
            },

            # Conversation restart scenarios
            {
                "category": "conversation_restart",
                "conversations": [
                    [
                        "who is e.j.price1986@gmail.com",
                        "RESTART_CONVERSATION",
                        "credit analysis for e.j.price1986@gmail.com"
                    ],
                    [
                        "comprehensive analysis for e.j.price1986@gmail.com",
                        "RESTART_CONVERSATION",
                        "account status for e.j.price1986@gmail.com"
                    ]
                ]
            },

            # Performance stress scenarios
            {
                "category": "performance_stress",
                "conversations": [
                    ["comprehensive analysis for e.j.price1986@gmail.com"] * 5,  # Repeated heavy queries
                    ["who is e.j.price1986@gmail.com"] * 10,  # Repeated light queries
                ]
            }
        ]

    def make_api_request(self, query: str, conversation_id: str = None) -> Dict[str, Any]:
        """Make API request to TLRS system"""
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
                timeout=30
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
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "query": query,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "conversation_id": conversation_id,
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
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            }

    def run_conversation(self, conversation: List[str], category: str, thread_id: int) -> Dict[str, Any]:
        """Run a complete conversation scenario"""
        conversation_id = f"{category}_{thread_id}_{int(time.time())}"
        conversation_results = []

        print(f"🧵 Thread {thread_id}: Starting {category} conversation with {len(conversation)} queries")

        for i, query in enumerate(conversation):
            if query == "RESTART_CONVERSATION":
                # Simulate conversation restart by creating new conversation_id
                conversation_id = f"{category}_{thread_id}_restart_{int(time.time())}"
                conversation_results.append({
                    "action": "conversation_restart",
                    "timestamp": datetime.now().isoformat()
                })
                continue

            result = self.make_api_request(query, conversation_id)
            result["query_index"] = i
            result["category"] = category
            result["thread_id"] = thread_id

            conversation_results.append(result)

            # Brief pause between queries in conversation
            time.sleep(0.1)

        return {
            "conversation_id": conversation_id,
            "category": category,
            "thread_id": thread_id,
            "results": conversation_results,
            "total_queries": len([q for q in conversation if q != "RESTART_CONVERSATION"]),
            "success_rate": len([r for r in conversation_results if r.get("success", False)]) / len(conversation_results) if conversation_results else 0
        }

    def analyze_response_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze response quality and extract key metrics"""
        if not result.get("success", False):
            return {"quality_score": 0, "issues": ["API_ERROR"]}

        response = result.get("response", "")
        query = result.get("query", "")
        category = result.get("category", "")

        issues = []
        quality_score = 100

        # Check response length appropriateness
        if len(response) < 50:
            issues.append("TOO_SHORT")
            quality_score -= 20
        elif len(response) > 3000:
            issues.append("TOO_VERBOSE")
            quality_score -= 15

        # Check for customer-specific data (for valid customer queries)
        if "e.j.price1986@gmail.com" in query.lower():
            if "esteban" not in response.lower() and "price" not in response.lower():
                issues.append("MISSING_CUSTOMER_DATA")
                quality_score -= 30

        # Check for appropriate data types based on category
        if category == "credit_analysis":
            if "credit" not in response.lower() and "score" not in response.lower():
                issues.append("MISSING_CREDIT_CONTEXT")
                quality_score -= 25

        elif category == "transaction_analysis":
            if "transaction" not in response.lower() and "payment" not in response.lower():
                issues.append("MISSING_TRANSACTION_CONTEXT")
                quality_score -= 25

        elif category == "account_status":
            if "status" not in response.lower() and "account" not in response.lower():
                issues.append("MISSING_STATUS_CONTEXT")
                quality_score -= 25

        # Check for error handling on invalid queries
        if "invalid@customer.com" in query:
            if "not found" not in response.lower() and "no records" not in response.lower():
                issues.append("POOR_ERROR_HANDLING")
                quality_score -= 30

        # Check response time
        response_time = result.get("response_time", 0)
        if response_time > 10:
            issues.append("SLOW_RESPONSE")
            quality_score -= 10
        elif response_time > 20:
            issues.append("VERY_SLOW_RESPONSE")
            quality_score -= 20

        return {
            "quality_score": max(0, quality_score),
            "issues": issues,
            "response_length": len(response),
            "response_time": response_time,
            "contains_customer_data": "esteban" in response.lower() or "price" in response.lower()
        }

    def run_stress_test(self, max_threads: int = 10, iterations_per_thread: int = 3):
        """Run comprehensive multi-threaded stress test"""
        print(f"🚀 Starting comprehensive QA stress test with {max_threads} threads")
        print(f"📊 Total scenarios: {len(self.client_success_scenarios)}")

        all_conversations = []

        # Prepare all conversation combinations
        for scenario in self.client_success_scenarios:
            category = scenario["category"]
            conversations = scenario["conversations"]

            for _ in range(iterations_per_thread):
                for conversation in conversations:
                    all_conversations.append((conversation, category))

        # Shuffle for realistic load distribution
        random.shuffle(all_conversations)

        print(f"🎯 Total conversations to test: {len(all_conversations)}")

        # Execute with thread pool
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []

            for i, (conversation, category) in enumerate(all_conversations):
                future = executor.submit(self.run_conversation, conversation, category, i % max_threads)
                futures.append(future)

            # Collect results as they complete
            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.conversation_logs.append(result)

                    # Analyze each query result
                    for query_result in result["results"]:
                        if isinstance(query_result, dict) and "query" in query_result:
                            quality_analysis = self.analyze_response_quality(query_result)
                            query_result["quality_analysis"] = quality_analysis
                            self.test_results.append(query_result)

                            # Track performance metrics
                            if query_result.get("success", False):
                                self.performance_metrics.append({
                                    "response_time": query_result.get("response_time", 0),
                                    "category": query_result.get("category", "unknown"),
                                    "quality_score": quality_analysis.get("quality_score", 0)
                                })

                    print(f"✅ Completed conversation {result['conversation_id']} - Success rate: {result['success_rate']:.2%}")

                except Exception as e:
                    print(f"❌ Conversation failed: {str(e)}")

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        if not self.test_results:
            return {"error": "No test results available"}

        # Overall statistics
        total_queries = len(self.test_results)
        successful_queries = len([r for r in self.test_results if r.get("success", False)])
        success_rate = successful_queries / total_queries if total_queries > 0 else 0

        # Performance statistics
        response_times = [m["response_time"] for m in self.performance_metrics]
        quality_scores = [m["quality_score"] for m in self.performance_metrics]

        # Category breakdown
        category_stats = {}
        for result in self.test_results:
            category = result.get("category", "unknown")
            if category not in category_stats:
                category_stats[category] = {"total": 0, "successful": 0, "quality_scores": []}

            category_stats[category]["total"] += 1
            if result.get("success", False):
                category_stats[category]["successful"] += 1
                if "quality_analysis" in result:
                    category_stats[category]["quality_scores"].append(
                        result["quality_analysis"].get("quality_score", 0)
                    )

        # Issue analysis
        all_issues = []
        for result in self.test_results:
            if "quality_analysis" in result:
                all_issues.extend(result["quality_analysis"].get("issues", []))

        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        report = {
            "test_summary": {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "success_rate": success_rate,
                "total_conversations": len(self.conversation_logs),
                "test_duration": "Multi-threaded execution",
                "timestamp": datetime.now().isoformat()
            },
            "performance_metrics": {
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "median_response_time": statistics.median(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "avg_quality_score": statistics.mean(quality_scores) if quality_scores else 0
            },
            "category_breakdown": {
                cat: {
                    "success_rate": stats["successful"] / stats["total"] if stats["total"] > 0 else 0,
                    "avg_quality": statistics.mean(stats["quality_scores"]) if stats["quality_scores"] else 0,
                    "total_queries": stats["total"]
                }
                for cat, stats in category_stats.items()
            },
            "quality_issues": issue_counts,
            "detailed_results": self.test_results[-10:],  # Last 10 for brevity
            "conversation_samples": self.conversation_logs[-5:]  # Last 5 conversations
        }

        return report

    def save_results(self, filename: str = None):
        """Save comprehensive test results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_qa_test_results_{timestamp}.json"

        report = self.generate_comprehensive_report()

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        print("📄 Comprehensive test results saved to:", filename)
        return filename

def main():
    """Main execution function"""
    print("🔍 TLRS Comprehensive QA Stress Testing Suite")
    print("=" * 50)

    # Initialize test suite
    qa_suite = TLRSQATestSuite()

    # Run comprehensive stress test
    qa_suite.run_stress_test(max_threads=8, iterations_per_thread=2)

    # Generate and display report
    report = qa_suite.generate_comprehensive_report()

    print("\n" + "=" * 50)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 50)

    print(f"Total Queries: {report['test_summary']['total_queries']}")
    print(f"Success Rate: {report['test_summary']['success_rate']:.2%}")
    print(f"Avg Response Time: {report['performance_metrics']['avg_response_time']:.2f}s")
    print(f"Avg Quality Score: {report['performance_metrics']['avg_quality_score']:.1f}/100")

    print("\n📈 Category Performance:")
    for category, stats in report['category_breakdown'].items():
        print(f"  {category}: {stats['success_rate']:.2%} success, {stats['avg_quality']:.1f} quality")

    if report['quality_issues']:
        print("\n⚠️  Quality Issues Found:")
        for issue, count in sorted(report['quality_issues'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {issue}: {count} occurrences")

    # Save detailed results
    filename = qa_suite.save_results()

    print("\n✅ Comprehensive QA testing complete!")
    print(f"📄 Detailed results saved to: {filename}")

if __name__ == "__main__":
    main()
