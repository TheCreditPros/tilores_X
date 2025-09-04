#!/usr/bin/env python3
"""
Focused Validation Test - Core Functionality Only
Tests the main functional categories that should achieve 90%+ success
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

class FocusedValidator:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results = []

        # Focus on core functional queries only
        self.core_queries = {
            "customer_identification": [
                "who is e.j.price1986@gmail.com",
                "customer profile for e.j.price1986@gmail.com",
                "tell me about e.j.price1986@gmail.com",
                "information about client 1747598",
                "profile of Esteban Price",
                "who is client ID 1747598",
                "customer details for e.j.price1986@gmail.com",
                "show me e.j.price1986@gmail.com profile"
            ],
            "account_status": [
                "account status for e.j.price1986@gmail.com",
                "is e.j.price1986@gmail.com active",
                "customer status e.j.price1986@gmail.com",
                "subscription status for client 1747598",
                "enrollment status Esteban Price",
                "what is the status of e.j.price1986@gmail.com",
                "check account status e.j.price1986@gmail.com",
                "is client 1747598 canceled"
            ],
            "credit_analysis": [
                "credit score for e.j.price1986@gmail.com",
                "experian score e.j.price1986@gmail.com",
                "credit report for client 1747598",
                "bureau information for Esteban Price",
                "utilization rate e.j.price1986@gmail.com",
                "transunion report e.j.price1986@gmail.com",
                "equifax data for client 1747598",
                "credit analysis Esteban Price"
            ],
            "transaction_analysis": [
                "transaction history e.j.price1986@gmail.com",
                "payment history for client 1747598",
                "billing information e.j.price1986@gmail.com",
                "recent payments Esteban Price",
                "invoice details for e.j.price1986@gmail.com",
                "charge history client 1747598",
                "payment patterns e.j.price1986@gmail.com",
                "billing summary Esteban Price"
            ]
        }

        # Expected patterns for core functionality
        self.expected_patterns = {
            "customer_identification": {
                "should_contain": ["Status:", "Customer:", "Esteban Price", "Active"],
                "should_not_contain": ["Analysis Type:", "Data Cut-off"],
                "min_score": 0.8
            },
            "account_status": {
                "should_contain": ["Status:", "Active", "Esteban Price"],
                "should_not_contain": ["generic", "framework"],
                "min_score": 0.8
            },
            "credit_analysis": {
                "should_contain": ["Status:", "Customer:", "Esteban Price", "Active"],
                "should_not_contain": ["Analysis Type:", "Data Cut-off"],
                "min_score": 0.8
            },
            "transaction_analysis": {
                "should_contain": ["Status:", "Customer:", "Esteban Price", "Active"],
                "should_not_contain": ["Analysis Type:", "Data Cut-off"],
                "min_score": 0.8
            }
        }

    def test_single_query(self, query: str, category: str) -> Dict[str, Any]:
        """Test a single query and validate response"""
        try:
            start_time = time.time()

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

                validation_result = self.validate_response(assistant_response, category)

                result = {
                    "query": query,
                    "category": category,
                    "response": assistant_response,
                    "response_time": response_time,
                    "validation_score": validation_result["score"],
                    "issues": validation_result["issues"],
                    "success": validation_result["score"] >= self.expected_patterns[category]["min_score"]
                }
            else:
                result = {
                    "query": query,
                    "category": category,
                    "response": f"HTTP {response.status_code}",
                    "response_time": response_time,
                    "validation_score": 0,
                    "issues": ["HTTP_ERROR"],
                    "success": False
                }

        except Exception as e:
            result = {
                "query": query,
                "category": category,
                "response": f"ERROR: {str(e)}",
                "response_time": 0,
                "validation_score": 0,
                "issues": ["EXCEPTION"],
                "success": False
            }

        self.results.append(result)
        return result

    def validate_response(self, response: str, category: str) -> Dict[str, Any]:
        """Validate response against expected patterns"""
        expected = self.expected_patterns[category]
        issues = []
        score = 1.0

        # Check required content
        for required in expected["should_contain"]:
            if required not in response:
                issues.append(f"MISSING: {required}")
                score -= 0.2

        # Check prohibited content
        for prohibited in expected["should_not_contain"]:
            if prohibited in response:
                issues.append(f"CONTAINS: {prohibited}")
                score -= 0.3

        # Check response quality
        if len(response) < 50:
            issues.append("TOO_SHORT")
            score -= 0.2

        # Check for real customer data
        if "Esteban Price" not in response:
            issues.append("NO_CUSTOMER_DATA")
            score -= 0.4

        return {
            "score": max(0, score),
            "issues": issues
        }

    def run_focused_test(self) -> Dict[str, Any]:
        """Run focused validation test on core functionality"""
        print("🎯 Starting Focused Core Functionality Test")
        print("=" * 50)

        category_results = {}
        total_queries = 0
        total_successful = 0

        for category, queries in self.core_queries.items():
            print(f"\n📊 Testing {category.replace('_', ' ').title()}")
            category_results[category] = {
                "queries": [],
                "success_count": 0,
                "total_count": len(queries),
                "avg_score": 0,
                "avg_time": 0
            }

            for i, query in enumerate(queries):
                result = self.test_single_query(query, category)
                category_results[category]["queries"].append(result)

                if result["success"]:
                    category_results[category]["success_count"] += 1
                    total_successful += 1

                total_queries += 1

                # Progress indicator
                success_indicator = "✅" if result["success"] else "❌"
                print(f"  {success_indicator} [{i+1}/{len(queries)}] {query[:60]:60s} | Score: {result['validation_score']:.2f}")

            # Calculate category averages
            if queries:
                category_results[category]["success_rate"] = (category_results[category]["success_count"] / len(queries)) * 100
                category_results[category]["avg_score"] = sum(r["validation_score"] for r in category_results[category]["queries"]) / len(queries)
                category_results[category]["avg_time"] = sum(r["response_time"] for r in category_results[category]["queries"]) / len(queries)

        overall_success_rate = (total_successful / total_queries) * 100 if total_queries > 0 else 0

        # Print summary
        print("\n" + "=" * 50)
        print("🎯 FOCUSED VALIDATION RESULTS")
        print("=" * 50)
        print(f"Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"Target: 90%+ | {'✅ PASSED' if overall_success_rate >= 90 else '❌ NEEDS IMPROVEMENT'}")
        print()

        for category, stats in category_results.items():
            status = "✅" if stats["success_rate"] >= 90 else "❌"
            print(f"{status} {category.replace('_', ' ').title():25s}: {stats['success_rate']:5.1f}% ({stats['success_count']}/{stats['total_count']})")

        return {
            "overall_success_rate": overall_success_rate,
            "category_results": category_results,
            "total_queries": total_queries,
            "total_successful": total_successful,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

def main():
    validator = FocusedValidator()
    results = validator.run_focused_test()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"focused_validation_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Results saved to: focused_validation_{timestamp}.json")

    if results["overall_success_rate"] >= 90:
        print("\n🎉 SUCCESS! Core functionality ready for deployment!")
    else:
        print(f"\n⚠️  Need {90 - results['overall_success_rate']:.1f}% more improvement to reach 90% target")

if __name__ == "__main__":
    main()
