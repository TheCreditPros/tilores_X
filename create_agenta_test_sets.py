#!/usr/bin/env python3
"""
Create Agenta.ai Test Sets via API

Creates comprehensive test sets for all prompt variants using the Agenta.ai API.
"""

import requests
import json
import os
from datetime import datetime

class AgentaTestSetCreator:
    def __init__(self):
        """Initialize Agenta API client"""
        self.base_url = "https://cloud.agenta.ai/api"
        self.api_key = os.getenv("AGENTA_API_KEY", "your_api_key_here")
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'ApiKey {self.api_key}'
        }

        print(f"🔧 Agenta API Configuration:")
        print(f"  - Base URL: {self.base_url}")
        print(f"  - API Key: {'✅ Set' if self.api_key != 'your_api_key_here' else '❌ Missing'}")

    def create_test_set(self, name: str, test_data: list) -> bool:
        """Create a test set via Agenta API"""
        url = f"{self.base_url}/testsets"

        data = {
            "name": name,
            "csvdata": test_data
        }

        try:
            print(f"\n📝 Creating test set: {name}")
            print(f"   - Test cases: {len(test_data)}")

            response = requests.post(
                url,
                data=json.dumps(data),
                headers=self.headers,
                timeout=30
            )

            print(f"   - Status Code: {response.status_code}")

            if response.status_code in [200, 201]:
                result = response.json()
                print(f"   ✅ Success: {name} created")
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                return False

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    def create_account_status_test_set(self):
        """Create test set for account status queries"""
        test_data = [
            {
                "query": "What is the account status for e.j.price1986@gmail.com?",
                "expected_format": "bullet_points",
                "expected_fields": "status,customer,product,enrolled",
                "query_type": "status",
                "priority": "high"
            },
            {
                "query": "Check customer status for john.doe@example.com",
                "expected_format": "bullet_points",
                "expected_fields": "status,customer",
                "query_type": "status",
                "priority": "medium"
            },
            {
                "query": "Is customer e.j.price1986@gmail.com active or canceled?",
                "expected_format": "bullet_points",
                "expected_fields": "status",
                "query_type": "status",
                "priority": "high"
            },
            {
                "query": "Show enrollment status for customer",
                "expected_format": "bullet_points",
                "expected_fields": "status,enrolled",
                "query_type": "status",
                "priority": "medium"
            },
            {
                "query": "What's the current account status?",
                "expected_format": "bullet_points",
                "expected_fields": "status",
                "query_type": "status",
                "priority": "low"
            }
        ]

        return self.create_test_set("Account Status Queries", test_data)

    def create_credit_analysis_test_set(self):
        """Create test set for credit analysis queries"""
        test_data = [
            {
                "query": "Analyze credit report for e.j.price1986@gmail.com",
                "expected_format": "detailed_analysis",
                "expected_fields": "credit_scores,bureaus,utilization,recommendations",
                "query_type": "credit",
                "priority": "high"
            },
            {
                "query": "What's the credit score trend for this customer?",
                "expected_format": "detailed_analysis",
                "expected_fields": "credit_scores,trends",
                "query_type": "credit",
                "priority": "high"
            },
            {
                "query": "Compare bureau reports for e.j.price1986@gmail.com",
                "expected_format": "detailed_analysis",
                "expected_fields": "bureaus,comparison,differences",
                "query_type": "credit",
                "priority": "medium"
            },
            {
                "query": "Credit utilization analysis",
                "expected_format": "detailed_analysis",
                "expected_fields": "utilization,recommendations",
                "query_type": "credit",
                "priority": "medium"
            },
            {
                "query": "Show credit improvement opportunities",
                "expected_format": "detailed_analysis",
                "expected_fields": "recommendations,improvement_plan",
                "query_type": "credit",
                "priority": "high"
            }
        ]

        return self.create_test_set("Credit Analysis Queries", test_data)

    def create_multi_data_test_set(self):
        """Create test set for multi-data analysis queries"""
        test_data = [
            {
                "query": "Comprehensive customer analysis for e.j.price1986@gmail.com",
                "expected_format": "comprehensive_report",
                "expected_fields": "credit,transactions,calls,tickets,overview",
                "query_type": "multi_data",
                "priority": "high"
            },
            {
                "query": "Full profile with all data sources",
                "expected_format": "comprehensive_report",
                "expected_fields": "all_data_types,correlations",
                "query_type": "multi_data",
                "priority": "high"
            },
            {
                "query": "Complete customer intelligence report",
                "expected_format": "comprehensive_report",
                "expected_fields": "intelligence,insights,patterns",
                "query_type": "multi_data",
                "priority": "medium"
            },
            {
                "query": "Cross-source data analysis",
                "expected_format": "comprehensive_report",
                "expected_fields": "cross_correlations,insights",
                "query_type": "multi_data",
                "priority": "medium"
            }
        ]

        return self.create_test_set("Multi-Data Analysis Queries", test_data)

    def create_transaction_analysis_test_set(self):
        """Create test set for transaction analysis queries"""
        test_data = [
            {
                "query": "Show payment history for e.j.price1986@gmail.com",
                "expected_format": "transaction_analysis",
                "expected_fields": "payment_patterns,history,trends",
                "query_type": "transaction",
                "priority": "high"
            },
            {
                "query": "Analyze billing patterns",
                "expected_format": "transaction_analysis",
                "expected_fields": "billing_analysis,patterns",
                "query_type": "transaction",
                "priority": "medium"
            },
            {
                "query": "Transaction trends and insights",
                "expected_format": "transaction_analysis",
                "expected_fields": "trends,insights,patterns",
                "query_type": "transaction",
                "priority": "medium"
            },
            {
                "query": "Payment method analysis",
                "expected_format": "transaction_analysis",
                "expected_fields": "payment_methods,preferences",
                "query_type": "transaction",
                "priority": "low"
            }
        ]

        return self.create_test_set("Transaction Analysis Queries", test_data)

    def create_phone_call_test_set(self):
        """Create test set for phone call analysis queries"""
        test_data = [
            {
                "query": "Analyze call history for e.j.price1986@gmail.com",
                "expected_format": "call_analysis",
                "expected_fields": "call_patterns,agents,duration,campaigns",
                "query_type": "phone",
                "priority": "medium"
            },
            {
                "query": "Show agent performance metrics",
                "expected_format": "call_analysis",
                "expected_fields": "agent_performance,metrics",
                "query_type": "phone",
                "priority": "medium"
            },
            {
                "query": "Call duration and frequency analysis",
                "expected_format": "call_analysis",
                "expected_fields": "duration,frequency,patterns",
                "query_type": "phone",
                "priority": "low"
            },
            {
                "query": "Campaign effectiveness analysis",
                "expected_format": "call_analysis",
                "expected_fields": "campaigns,effectiveness",
                "query_type": "phone",
                "priority": "low"
            }
        ]

        return self.create_test_set("Phone Call Analysis Queries", test_data)

    def create_performance_benchmark_test_set(self):
        """Create test set for performance benchmarking"""
        test_data = [
            {
                "query": "What is the account status for e.j.price1986@gmail.com?",
                "expected_response_time": "< 5 seconds",
                "expected_token_count": "< 250",
                "variant_to_test": "account-status-v1",
                "benchmark_type": "performance"
            },
            {
                "query": "Analyze credit report for e.j.price1986@gmail.com",
                "expected_response_time": "< 10 seconds",
                "expected_token_count": "< 1500",
                "variant_to_test": "credit-analysis-comprehensive-v1",
                "benchmark_type": "performance"
            },
            {
                "query": "Comprehensive customer analysis for e.j.price1986@gmail.com",
                "expected_response_time": "< 15 seconds",
                "expected_token_count": "< 2000",
                "variant_to_test": "multi-data-analysis-v1",
                "benchmark_type": "performance"
            }
        ]

        return self.create_test_set("Performance Benchmarks", test_data)

    def create_all_test_sets(self):
        """Create all test sets"""
        print("🚀 Creating Agenta.ai Test Sets via API...")

        results = []

        # Create each test set
        test_sets = [
            ("Account Status", self.create_account_status_test_set),
            ("Credit Analysis", self.create_credit_analysis_test_set),
            ("Multi-Data Analysis", self.create_multi_data_test_set),
            ("Transaction Analysis", self.create_transaction_analysis_test_set),
            ("Phone Call Analysis", self.create_phone_call_test_set),
            ("Performance Benchmarks", self.create_performance_benchmark_test_set)
        ]

        for name, create_func in test_sets:
            try:
                success = create_func()
                results.append((name, success))
            except Exception as e:
                print(f"❌ Failed to create {name}: {e}")
                results.append((name, False))

        # Summary
        print(f"\n📊 TEST SET CREATION SUMMARY:")
        successful = sum(1 for _, success in results if success)
        total = len(results)

        for name, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {name}")

        print(f"\n🎯 Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")

        if successful == total:
            print("🎉 All test sets created successfully!")
        else:
            print("⚠️ Some test sets failed. Check API key and permissions.")

        return results

def main():
    """Main function"""
    print("🧪 Agenta.ai Test Set Creator")
    print("=" * 50)

    # Check if we're in demo mode (no API key)
    api_key = os.getenv("AGENTA_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("⚠️ DEMO MODE: No AGENTA_API_KEY found")
        print("📝 This script will show you the test data structure")
        print("🔧 Set AGENTA_API_KEY to actually create test sets")
        print()

        # Show example test data structure
        creator = AgentaTestSetCreator()
        print("📋 Example Test Data Structure:")
        print("=" * 30)

        # Show one example from each category
        examples = {
            "Account Status": [
                {
                    "query": "What is the account status for e.j.price1986@gmail.com?",
                    "expected_format": "bullet_points",
                    "expected_fields": "status,customer,product,enrolled",
                    "query_type": "status",
                    "priority": "high"
                }
            ],
            "Credit Analysis": [
                {
                    "query": "Analyze credit report for e.j.price1986@gmail.com",
                    "expected_format": "detailed_analysis",
                    "expected_fields": "credit_scores,bureaus,utilization,recommendations",
                    "query_type": "credit",
                    "priority": "high"
                }
            ]
        }

        for category, data in examples.items():
            print(f"\n{category}:")
            print(json.dumps(data[0], indent=2))

        print(f"\n💡 To create test sets:")
        print(f"1. Set AGENTA_API_KEY environment variable")
        print(f"2. Run: python3 create_agenta_test_sets.py")

        return False

    # Create test sets with real API
    creator = AgentaTestSetCreator()
    results = creator.create_all_test_sets()

    return all(success for _, success in results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
