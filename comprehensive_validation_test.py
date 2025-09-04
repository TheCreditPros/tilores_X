#!/usr/bin/env python3
"""
Comprehensive Validation Testing with Webhook Monitoring
Tests all potential user queries and validates responses for accuracy and completeness
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any
import concurrent.futures
import threading

class ComprehensiveValidator:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results = []
        self.lock = threading.Lock()

        # Load comprehensive query list
        with open('comprehensive_user_queries.json', 'r') as f:
            self.query_categories = json.load(f)

        # Expected response patterns for validation
        self.expected_patterns = {
            "customer_identification": {
                "should_contain": ["Status:", "Customer:", "Esteban Price", "Active"],
                "should_not_contain": ["Analysis Type:", "Data Cut-off", "October 2023"],
                "expected_query_type": "status",
                "expected_format": "structured"
            },
            "account_status": {
                "should_contain": ["Status:", "Active", "Esteban Price"],
                "should_not_contain": ["generic", "framework"],
                "expected_query_type": "status",
                "expected_format": "structured"
            },
            "credit_analysis": {
                "should_contain": ["Status:", "Customer:", "Esteban Price", "Active"],
                "should_not_contain": ["Analysis Type:", "Data Cut-off", "October 2023"],
                "expected_query_type": "status",
                "expected_format": "structured"
            },
            "transaction_analysis": {
                "should_contain": ["Status:", "Customer:", "Esteban Price", "Active"],
                "should_not_contain": ["Analysis Type:", "Data Cut-off", "October 2023"],
                "expected_query_type": "status",
                "expected_format": "structured"
            },
            "multi_data_analysis": {
                "should_contain": ["comprehensive", "analysis"],
                "should_not_contain": [],
                "expected_query_type": "multi_data",
                "expected_format": "narrative"
            },
            "edge_cases": {
                "should_contain": ["No customer records found", "not found", "Please check", "Please verify", "Please provide"],
                "should_not_contain": ["Esteban Price", "Active"],
                "expected_query_type": "general",
                "expected_format": "narrative"
            }
        }

    def test_single_query(self, query: str, category: str) -> Dict[str, Any]:
        """Test a single query and validate response"""
        try:
            start_time = time.time()

            # Send request to API
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": query}]
                },
                timeout=30
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                response_data = response.json()
                assistant_response = response_data["choices"][0]["message"]["content"]

                # Validate response against expected patterns
                validation_result = self.validate_response(assistant_response, category, query)

                result = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "query": query,
                    "category": category,
                    "response": assistant_response,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "validation": validation_result,
                    "request_id": response_data.get("id"),
                    "success": validation_result["overall_score"] >= 0.8
                }
            else:
                result = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "query": query,
                    "category": category,
                    "response": f"HTTP {response.status_code}: {response.text}",
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "validation": {"overall_score": 0, "issues": ["HTTP_ERROR"]},
                    "success": False
                }

        except Exception as e:
            result = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "query": query,
                "category": category,
                "response": f"ERROR: {str(e)}",
                "response_time": 0,
                "status_code": 0,
                "validation": {"overall_score": 0, "issues": ["EXCEPTION"]},
                "success": False
            }

        with self.lock:
            self.results.append(result)

        return result

    def validate_response(self, response: str, category: str, query: str) -> Dict[str, Any]:
        """Validate response against expected patterns"""
        if category not in self.expected_patterns:
            return {"overall_score": 0.5, "issues": ["UNKNOWN_CATEGORY"]}

        expected = self.expected_patterns[category]
        issues = []
        score = 1.0

        # Check required content
        for required in expected["should_contain"]:
            if required not in response:
                issues.append(f"MISSING_REQUIRED: {required}")
                score -= 0.2

        # Check prohibited content
        for prohibited in expected["should_not_contain"]:
            if prohibited in response:
                issues.append(f"CONTAINS_PROHIBITED: {prohibited}")
                score -= 0.3

        # Check response length (too short or too long)
        if len(response) < 50:
            issues.append("RESPONSE_TOO_SHORT")
            score -= 0.2
        elif len(response) > 2000:
            issues.append("RESPONSE_TOO_LONG")
            score -= 0.1

        # Special validation for customer identification queries
        if category == "customer_identification" or category == "account_status":
            if "Esteban Price" not in response:
                issues.append("MISSING_CUSTOMER_NAME")
                score -= 0.4
            if "Active" not in response:
                issues.append("MISSING_STATUS")
                score -= 0.4
            if "dc93a2cd-de0a-444f-ad47-3003ba998cd3" not in response:
                issues.append("MISSING_ENTITY_ID")
                score -= 0.2

        # Edge case validation
        if category == "edge_cases":
            if "invalid" in query.lower() or "nonexistent" in query.lower() or "999999" in query or "gmai.com" in query.lower():
                if "no customer records found" not in response.lower() and "not found" not in response.lower() and "please check" not in response.lower() and "please verify" not in response.lower():
                    issues.append("INVALID_CUSTOMER_NOT_HANDLED")
                    score -= 0.5
                else:
                    # Properly handled invalid customer
                    score += 0.3
            elif query.strip() == "":
                if "please provide" not in response.lower():
                    issues.append("EMPTY_QUERY_NOT_HANDLED")
                    score -= 0.5
                else:
                    # Properly handled empty query
                    score += 0.3
            elif "random text query" in query.lower():
                # Random text should get some kind of helpful response
                if len(response) < 20:
                    issues.append("RANDOM_QUERY_TOO_SHORT")
                    score -= 0.3
            elif query.upper() == query and len(query) > 10:
                # Case sensitivity test - should still work
                if "esteban" in response.lower() or "active" in response.lower():
                    score += 0.3
                else:
                    issues.append("CASE_SENSITIVITY_ISSUE")
                    score -= 0.3

        return {
            "overall_score": max(0, score),
            "issues": issues,
            "response_length": len(response)
        }

    def run_comprehensive_test(self, max_workers: int = 8) -> Dict[str, Any]:
        """Run comprehensive validation test on all queries"""
        print("🚀 Starting Comprehensive Validation Testing")
        print("=" * 60)

        all_queries = []
        for category, queries in self.query_categories.items():
            for query in queries:
                all_queries.append((query, category))

        print(f"📊 Total queries to test: {len(all_queries)}")
        print(f"🧵 Using {max_workers} concurrent workers")
        print()

        # Test all queries concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for query, category in all_queries:
                future = executor.submit(self.test_single_query, query, category)
                futures.append(future)

            # Process results as they complete
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                success_indicator = "✅" if result["success"] else "❌"
                print(f"{success_indicator} [{i+1:2d}/{len(all_queries)}] {result['category']:20s} | {result['query'][:50]:50s} | Score: {result['validation']['overall_score']:.2f}")

        return self.analyze_results()

    def analyze_results(self) -> Dict[str, Any]:
        """Analyze test results and generate comprehensive report"""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])

        # Category analysis
        category_stats = {}
        for result in self.results:
            category = result["category"]
            if category not in category_stats:
                category_stats[category] = {"total": 0, "successful": 0, "avg_score": 0, "avg_time": 0}

            category_stats[category]["total"] += 1
            if result["success"]:
                category_stats[category]["successful"] += 1
            category_stats[category]["avg_score"] += result["validation"]["overall_score"]
            category_stats[category]["avg_time"] += result["response_time"]

        # Calculate averages
        for category in category_stats:
            stats = category_stats[category]
            stats["success_rate"] = (stats["successful"] / stats["total"]) * 100
            stats["avg_score"] = stats["avg_score"] / stats["total"]
            stats["avg_time"] = stats["avg_time"] / stats["total"]

        # Collect all issues
        all_issues = {}
        for result in self.results:
            for issue in result["validation"].get("issues", []):
                all_issues[issue] = all_issues.get(issue, 0) + 1

        # Find worst performing queries
        worst_queries = sorted(self.results, key=lambda x: x["validation"]["overall_score"])[:10]

        analysis = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "overall_success_rate": (successful_tests / total_tests) * 100 if total_tests > 0 else 0,
                "avg_response_time": sum(r["response_time"] for r in self.results) / total_tests if total_tests > 0 else 0
            },
            "category_performance": category_stats,
            "common_issues": dict(sorted(all_issues.items(), key=lambda x: x[1], reverse=True)),
            "worst_performing_queries": worst_queries,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        return analysis

    def get_webhook_monitoring_data(self) -> Dict[str, Any]:
        """Retrieve webhook monitoring data for comparison"""
        try:
            response = requests.get(f"{self.base_url}/v1/monitoring/webhook-logs?limit=100")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def save_results(self, analysis: Dict[str, Any]):
        """Save comprehensive results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results
        with open(f"validation_results_{timestamp}.json", "w") as f:
            json.dump({
                "analysis": analysis,
                "detailed_results": self.results
            }, f, indent=2)

        # Save webhook monitoring data
        webhook_data = self.get_webhook_monitoring_data()
        with open(f"webhook_monitoring_{timestamp}.json", "w") as f:
            json.dump(webhook_data, f, indent=2)

        print(f"\n📄 Results saved to:")
        print(f"   - validation_results_{timestamp}.json")
        print(f"   - webhook_monitoring_{timestamp}.json")

def main():
    validator = ComprehensiveValidator()

    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(5)

    # Run comprehensive test
    analysis = validator.run_comprehensive_test()

    # Print summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE VALIDATION RESULTS")
    print("=" * 60)
    print(f"Total Tests: {analysis['summary']['total_tests']}")
    print(f"Success Rate: {analysis['summary']['overall_success_rate']:.1f}%")
    print(f"Avg Response Time: {analysis['summary']['avg_response_time']:.2f}s")
    print()

    print("📈 Category Performance:")
    for category, stats in analysis['category_performance'].items():
        print(f"  {category:25s}: {stats['success_rate']:5.1f}% success, {stats['avg_score']:.2f} avg score, {stats['avg_time']:.2f}s avg time")

    if analysis['common_issues']:
        print(f"\n⚠️  Most Common Issues:")
        for issue, count in list(analysis['common_issues'].items())[:5]:
            print(f"  {issue}: {count} occurrences")

    # Save results
    validator.save_results(analysis)

    print(f"\n✅ Comprehensive validation testing complete!")

if __name__ == "__main__":
    main()
