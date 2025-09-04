#!/usr/bin/env python3
"""
Generic Validation Test - Works with Any Customer Data
Tests the system's ability to handle any customer identifiers, not just hardcoded test data
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class GenericValidator:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results = []

        # Generic test patterns that should work for ANY customer
        self.test_patterns = {
            "customer_identification": [
                "who is {email}",
                "customer profile for {email}",
                "tell me about {email}",
                "information about client {client_id}",
                "who is client ID {client_id}",
                "customer details for {email}",
                "show me {email} profile"
            ],
            "account_status": [
                "account status for {email}",
                "is {email} active",
                "customer status {email}",
                "subscription status for client {client_id}",
                "what is the status of {email}",
                "check account status {email}",
                "is client {client_id} canceled"
            ],
            "credit_analysis": [
                "credit score for {email}",
                "experian score {email}",
                "credit report for client {client_id}",
                "utilization rate {email}",
                "transunion report {email}",
                "equifax data for client {client_id}"
            ],
            "transaction_analysis": [
                "transaction history {email}",
                "payment history for client {client_id}",
                "billing information {email}",
                "invoice details for {email}",
                "charge history client {client_id}",
                "payment patterns {email}"
            ]
        }

        # Test with multiple different customer identifiers
        self.test_customers = [
            {
                "email": "e.j.price1986@gmail.com",
                "client_id": "1747598",
                "name": "Esteban Price",
                "expected_found": True,
                "description": "Known test customer"
            },
            {
                "email": "john.doe@example.com",
                "client_id": "999888",
                "name": "John Doe",
                "expected_found": False,
                "description": "Non-existent customer"
            },
            {
                "email": "jane.smith@company.org",
                "client_id": "555444",
                "name": "Jane Smith",
                "expected_found": False,
                "description": "Different non-existent customer"
            }
        ]

    def test_single_query(self, query: str, category: str, customer: Dict, expected_found: bool) -> Dict[str, Any]:
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

                validation_result = self.validate_generic_response(
                    assistant_response, category, customer, expected_found
                )

                result = {
                    "query": query,
                    "category": category,
                    "customer": customer["description"],
                    "expected_found": expected_found,
                    "response": assistant_response,
                    "response_time": response_time,
                    "validation_score": validation_result["score"],
                    "issues": validation_result["issues"],
                    "success": validation_result["score"] >= 0.8
                }
            else:
                result = {
                    "query": query,
                    "category": category,
                    "customer": customer["description"],
                    "expected_found": expected_found,
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
                "customer": customer["description"],
                "expected_found": expected_found,
                "response": f"ERROR: {str(e)}",
                "response_time": 0,
                "validation_score": 0,
                "issues": ["EXCEPTION"],
                "success": False
            }

        self.results.append(result)
        return result

    def validate_generic_response(self, response: str, category: str, customer: Dict, expected_found: bool) -> Dict[str, Any]:
        """Validate response without hardcoded customer expectations"""
        issues = []
        score = 1.0

        if expected_found:
            # For existing customers, expect structured data
            if "Status:" not in response:
                issues.append("MISSING_STATUS_STRUCTURE")
                score -= 0.3

            if "Customer:" not in response and "Active" not in response:
                issues.append("MISSING_CUSTOMER_DATA")
                score -= 0.4

            # Should contain the actual customer name (not hardcoded)
            if customer["name"] not in response:
                issues.append(f"MISSING_CUSTOMER_NAME_{customer['name'].replace(' ', '_')}")
                score -= 0.2

            # Check for generic template responses
            if "Analysis Type:" in response or "Data Cut-off" in response:
                issues.append("GENERIC_TEMPLATE_RESPONSE")
                score -= 0.5

        else:
            # For non-existent customers, expect "not found" message
            not_found_indicators = [
                "no customer records found",
                "not found",
                "no records found",
                "please check",
                "please verify"
            ]

            if not any(indicator in response.lower() for indicator in not_found_indicators):
                issues.append("INVALID_CUSTOMER_NOT_HANDLED")
                score -= 0.6

            # Should NOT contain customer data for non-existent customers
            if "Status:" in response or "Active" in response:
                issues.append("FALSE_POSITIVE_CUSTOMER_DATA")
                score -= 0.8

        # General response quality checks
        if len(response) < 20:
            issues.append("RESPONSE_TOO_SHORT")
            score -= 0.2

        return {
            "score": max(0, score),
            "issues": issues
        }

    def run_generic_test(self) -> Dict[str, Any]:
        """Run comprehensive generic validation test"""
        print("🌐 Starting Generic Customer Validation Test")
        print("=" * 60)
        print("Testing system with multiple different customers to ensure no hardcoding")
        print()

        category_results = {}
        total_queries = 0
        total_successful = 0

        for category, patterns in self.test_patterns.items():
            print(f"\n📊 Testing {category.replace('_', ' ').title()}")
            category_results[category] = {
                "queries": [],
                "success_count": 0,
                "total_count": 0,
                "avg_score": 0,
                "avg_time": 0
            }

            for customer in self.test_customers:
                print(f"\n  👤 Customer: {customer['description']}")

                for i, pattern in enumerate(patterns):
                    # Format the pattern with customer data
                    query = pattern.format(
                        email=customer["email"],
                        client_id=customer["client_id"],
                        name=customer["name"]
                    )

                    result = self.test_single_query(
                        query, category, customer, customer["expected_found"]
                    )

                    category_results[category]["queries"].append(result)
                    category_results[category]["total_count"] += 1
                    total_queries += 1

                    if result["success"]:
                        category_results[category]["success_count"] += 1
                        total_successful += 1

                    # Progress indicator
                    success_indicator = "✅" if result["success"] else "❌"
                    expected_indicator = "📍" if customer["expected_found"] else "🚫"
                    print(f"    {success_indicator}{expected_indicator} [{i+1}/{len(patterns)}] {query[:50]:50s} | Score: {result['validation_score']:.2f}")

            # Calculate category averages
            if category_results[category]["total_count"] > 0:
                category_results[category]["success_rate"] = (category_results[category]["success_count"] / category_results[category]["total_count"]) * 100
                category_results[category]["avg_score"] = sum(r["validation_score"] for r in category_results[category]["queries"]) / category_results[category]["total_count"]
                category_results[category]["avg_time"] = sum(r["response_time"] for r in category_results[category]["queries"]) / category_results[category]["total_count"]

        overall_success_rate = (total_successful / total_queries) * 100 if total_queries > 0 else 0

        # Analyze results by customer type
        existing_customer_results = [r for r in self.results if r["expected_found"]]
        nonexistent_customer_results = [r for r in self.results if not r["expected_found"]]

        existing_success_rate = (sum(1 for r in existing_customer_results if r["success"]) / len(existing_customer_results) * 100) if existing_customer_results else 0
        nonexistent_success_rate = (sum(1 for r in nonexistent_customer_results if r["success"]) / len(nonexistent_customer_results) * 100) if nonexistent_customer_results else 0

        # Print summary
        print("\n" + "=" * 60)
        print("🌐 GENERIC VALIDATION RESULTS")
        print("=" * 60)
        print(f"Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"Existing Customer Handling: {existing_success_rate:.1f}%")
        print(f"Non-existent Customer Handling: {nonexistent_success_rate:.1f}%")
        print()

        for category, stats in category_results.items():
            status = "✅" if stats["success_rate"] >= 80 else "❌"
            print(f"{status} {category.replace('_', ' ').title():25s}: {stats['success_rate']:5.1f}% ({stats['success_count']}/{stats['total_count']})")

        # Check for hardcoding issues
        hardcoding_issues = []
        if existing_success_rate < 80:
            hardcoding_issues.append("System may have hardcoded customer logic - existing customers not handled properly")
        if nonexistent_success_rate < 80:
            hardcoding_issues.append("System may have hardcoded validation - non-existent customers not handled properly")

        return {
            "overall_success_rate": overall_success_rate,
            "existing_customer_success_rate": existing_success_rate,
            "nonexistent_customer_success_rate": nonexistent_success_rate,
            "category_results": category_results,
            "total_queries": total_queries,
            "total_successful": total_successful,
            "hardcoding_issues": hardcoding_issues,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

def main():
    validator = GenericValidator()
    results = validator.run_generic_test()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"generic_validation_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Results saved to: generic_validation_{timestamp}.json")

    if results["hardcoding_issues"]:
        print(f"\n🚨 HARDCODING ISSUES DETECTED:")
        for issue in results["hardcoding_issues"]:
            print(f"  - {issue}")

    if results["overall_success_rate"] >= 80:
        print("\n🎉 SUCCESS! System works generically with different customers!")
    else:
        print(f"\n⚠️  System needs improvement - only {results['overall_success_rate']:.1f}% success rate")
        print("This suggests the system may be hardcoded to specific test data")

if __name__ == "__main__":
    main()
