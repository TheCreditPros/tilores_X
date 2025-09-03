#!/usr / bin / env python3
"""
Test Case Generator for Agenta Testing Framework

Generates comprehensive JSONL test cases from ground truth data,
covering all query types and scenarios for thorough prompt variant testing.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from ground_truth_extractor import GroundTruthExtractor


class TestCaseGenerator:
    """Generate comprehensive test cases for Agenta evaluation"""

    def __init__(self, ground_truth_file: str = None):
        """Initialize test case generator"""
        if ground_truth_file and os.path.exists(ground_truth_file):
            with open(ground_truth_file, 'r') as f:
                data = json.load(f)
                self.ground_truth = data.get('ground_truth', {})
                self.customer_context = data.get('customer_context', {})
        else:
            # Extract ground truth from master data
            extractor = GroundTruthExtractor()
            self.ground_truth = extractor.get_ground_truth()
            self.customer_context = extractor.get_customer_context()

        self.test_cases = []
        print(f"✅ Test case generator initialized with {len(self.ground_truth)} ground truth fields")

    def generate_account_status_tests(self) -> List[Dict]:
        """Generate account status query test cases"""
        customer_email = self.customer_context.get('customer_email')
        customer_name = self.customer_context.get('customer_name')
        client_id = self.customer_context.get('client_id')

        tests = [
            {
                "id": "account_status_email",
                "category": "account_status",
                "inputs": {
                    "customer_id": customer_email,
                    "query": f"What is the account status for {customer_email}?"
                },
                "expected": {
                    "customer_found": True,
                    "customer_name": customer_name,
                    "customer_email": customer_email,
                    "client_id": client_id,
                    "account_status": self.ground_truth.get('account_status', 'active'),
                    "has_credit_data": self.ground_truth.get('has_credit_data'),
                    "has_transaction_data": self.ground_truth.get('has_transaction_data'),
                    "data_available": True,
                    "explanation": f"Should confirm {customer_name} is found with active status"
                }
            },
            {
                "id": "account_status_client_id",
                "category": "account_status",
                "inputs": {
                    "customer_id": client_id,
                    "query": f"Show me the account status for client {client_id}"
                },
                "expected": {
                    "customer_found": True,
                    "customer_name": customer_name,
                    "client_id": client_id,
                    "account_status": self.ground_truth.get('account_status', 'active'),
                    "data_available": True,
                    "explanation": f"Should find customer by client ID {client_id}"
                }
            },
            {
                "id": "account_status_concise",
                "category": "account_status",
                "inputs": {
                    "customer_id": customer_email,
                    "query": "Account status?"
                },
                "expected": {
                    "customer_found": True,
                    "customer_name": customer_name,
                    "account_status": self.ground_truth.get('account_status', 'active'),
                    "explanation": "Should provide concise status information"
                }
            }
        ]

        return tests

    def generate_credit_analysis_tests(self) -> List[Dict]:
        """Generate credit analysis test cases"""
        customer_email = self.customer_context.get('customer_email')

        tests = [
            {
                "id": "credit_analysis_comprehensive",
                "category": "credit_analysis",
                "inputs": {
                    "customer_id": customer_email,
                    "query": f"Provide a comprehensive credit analysis for {customer_email}"
                },
                "expected": {
                    "customer_found": True,
                    "customer_name": self.customer_context.get('customer_name'),
                    "has_credit_data": True,
                    "total_credit_reports": self.ground_truth.get('total_credit_reports'),
                    "latest_credit_score": self.ground_truth.get('latest_credit_score'),
                    "credit_bureau": self.ground_truth.get('credit_bureau'),
                    "credit_score_range": self.ground_truth.get('credit_score_range'),
                    "risk_level": self.ground_truth.get('risk_level'),
                    "explanation": f"Should mention {self.ground_truth.get('total_credit_reports')} reports, {self.ground_truth.get('credit_bureau')} bureau, and score of {self.ground_truth.get('latest_credit_score')}"
                }
            },
            {
                "id": "credit_score_inquiry",
                "category": "credit_analysis",
                "inputs": {
                    "customer_id": customer_email,
                    "query": "What is the current credit score?"
                },
                "expected": {
                    "customer_found": True,
                    "has_credit_data": True,
                    "latest_credit_score": self.ground_truth.get('latest_credit_score'),
                    "credit_bureau": self.ground_truth.get('credit_bureau'),
                    "explanation": f"Should report score of {self.ground_truth.get('latest_credit_score')} from {self.ground_truth.get('credit_bureau')}"
                }
            },
            {
                "id": "risk_assessment",
                "category": "credit_analysis",
                "inputs": {
                    "customer_id": customer_email,
                    "query": "What is the risk level for this customer?"
                },
                "expected": {
                    "customer_found": True,
                    "has_credit_data": True,
                    "risk_level": self.ground_truth.get('risk_level'),
                    "latest_credit_score": self.ground_truth.get('latest_credit_score'),
                    "explanation": f"Should assess risk as {self.ground_truth.get('risk_level')} based on score {self.ground_truth.get('latest_credit_score')}"
                }
            },
            {
                "id": "credit_history_timeline",
                "category": "credit_analysis",
                "inputs": {
                    "customer_id": customer_email,
                    "query": "Show me the credit history timeline"
                },
                "expected": {
                    "customer_found": True,
                    "has_credit_data": True,
                    "total_credit_reports": self.ground_truth.get('total_credit_reports'),
                    "credit_report_date_range": self.ground_truth.get('credit_report_date_range'),
                    "credit_score_range": self.ground_truth.get('credit_score_range'),
                    "explanation": f"Should show {self.ground_truth.get('total_credit_reports')} reports over time period {self.ground_truth.get('credit_report_date_range')}"
                }
            }
        ]

        return tests

    def generate_transaction_analysis_tests(self) -> List[Dict]:
        """Generate transaction analysis test cases"""
        customer_email = self.customer_context.get('customer_email')

        tests = [
            {
                "id": "transaction_analysis_comprehensive",
                "category": "transaction_analysis",
                "inputs": {
                    "customer_id": customer_email,
                    "query": f"Analyze the transaction history for {customer_email}"
                },
                "expected": {
                    "customer_found": True,
                    "has_transaction_data": True,
                    "total_transactions": self.ground_truth.get('total_transactions'),
                    "total_transaction_amount": self.ground_truth.get('total_transaction_amount'),
                    "average_transaction_amount": self.ground_truth.get('average_transaction_amount'),
                    "explanation": f"Should reference {self.ground_truth.get('total_transactions')} transactions totaling ${self.ground_truth.get('total_transaction_amount') or 0:.2f}"
                }
            },
            {
                "id": "payment_patterns",
                "category": "transaction_analysis",
                "inputs": {
                    "customer_id": customer_email,
                    "query": "What are the payment patterns?"
                },
                "expected": {
                    "customer_found": True,
                    "has_transaction_data": True,
                    "total_transactions": self.ground_truth.get('total_transactions'),
                    "average_transaction_amount": self.ground_truth.get('average_transaction_amount'),
                    "explanation": f"Should analyze patterns from {self.ground_truth.get('total_transactions')} transactions with average ${self.ground_truth.get('average_transaction_amount') or 0:.2f}"
                }
            },
            {
                "id": "transaction_summary",
                "category": "transaction_analysis",
                "inputs": {
                    "customer_id": customer_email,
                    "query": "Give me a transaction summary"
                },
                "expected": {
                    "customer_found": True,
                    "has_transaction_data": True,
                    "total_transactions": self.ground_truth.get('total_transactions'),
                    "total_transaction_amount": self.ground_truth.get('total_transaction_amount'),
                    "explanation": "Should provide summary of transaction activity"
                }
            }
        ]

        return tests

    def generate_phone_call_analysis_tests(self) -> List[Dict]:
        """Generate phone call analysis test cases"""
        customer_email = self.customer_context.get('customer_email')

        tests = [
            {
                "id": "phone_call_analysis",
                "category": "phone_analysis",
                "inputs": {
                    "customer_id": customer_email,
                    "query": f"Show me phone call data for {customer_email}"
                },
                "expected": {
                    "customer_found": True,
                    "has_phone_data": self.ground_truth.get('has_phone_data'),
                    "contact_records_count": self.ground_truth.get('contact_records_count'),
                    "zoho_integration_records_count": self.ground_truth.get('zoho_integration_records_count'),
                    "explanation": f"Should reference {self.ground_truth.get('contact_records_count')} contact records and phone data availability"
                }
            },
            {
                "id": "contact_history",
                "category": "phone_analysis",
                "inputs": {
                    "customer_id": customer_email,
                    "query": "What is the contact history?"
                },
                "expected": {
                    "customer_found": True,
                    "has_phone_data": self.ground_truth.get('has_phone_data'),
                    "contact_records_count": self.ground_truth.get('contact_records_count'),
                    "explanation": "Should analyze available contact and phone interaction data"
                }
            }
        ]

        return tests

    def generate_multi_data_analysis_tests(self) -> List[Dict]:
        """Generate multi - source data analysis test cases"""
        customer_email = self.customer_context.get('customer_email')
        customer_name = self.customer_context.get('customer_name')

        tests = [
            {
                "id": "comprehensive_customer_analysis",
                "category": "multi_data_analysis",
                "inputs": {
                    "customer_id": customer_email,
                    "query": f"Provide a comprehensive analysis of {customer_email} across all data sources"
                },
                "expected": {
                    "customer_found": True,
                    "customer_name": customer_name,
                    "customer_email": customer_email,
                    "client_id": self.customer_context.get('client_id'),
                    "has_credit_data": self.ground_truth.get('has_credit_data'),
                    "has_transaction_data": self.ground_truth.get('has_transaction_data'),
                    "has_phone_data": self.ground_truth.get('has_phone_data'),
                    "has_card_data": self.ground_truth.get('has_card_data'),
                    "has_ticket_data": self.ground_truth.get('has_ticket_data'),
                    "total_credit_reports": self.ground_truth.get('total_credit_reports'),
                    "latest_credit_score": self.ground_truth.get('latest_credit_score'),
                    "total_transactions": self.ground_truth.get('total_transactions'),
                    "risk_level": self.ground_truth.get('risk_level'),
                    "data_completeness": self.ground_truth.get('data_completeness'),
                    "multiple_data_sources": True,
                    "explanation": f"Should provide comprehensive analysis covering credit ({self.ground_truth.get('total_credit_reports')} reports), transactions ({self.ground_truth.get('total_transactions')} records), and other data sources"
                }
            },
            {
                "id": "customer_360_view",
                "category": "multi_data_analysis",
                "inputs": {
                    "customer_id": customer_email,
                    "query": "Give me a 360 - degree view of this customer"
                },
                "expected": {
                    "customer_found": True,
                    "customer_name": customer_name,
                    "has_credit_data": True,
                    "has_transaction_data": True,
                    "has_phone_data": self.ground_truth.get('has_phone_data'),
                    "multiple_data_sources": True,
                    "data_completeness": self.ground_truth.get('data_completeness'),
                    "explanation": "Should integrate data from multiple sources for complete customer view"
                }
            },
            {
                "id": "data_availability_check",
                "category": "multi_data_analysis",
                "inputs": {
                    "customer_id": customer_email,
                    "query": "What data is available for this customer?"
                },
                "expected": {
                    "customer_found": True,
                    "data_available": True,
                    "has_credit_data": self.ground_truth.get('has_credit_data'),
                    "has_transaction_data": self.ground_truth.get('has_transaction_data'),
                    "has_phone_data": self.ground_truth.get('has_phone_data'),
                    "has_card_data": self.ground_truth.get('has_card_data'),
                    "has_ticket_data": self.ground_truth.get('has_ticket_data'),
                    "explanation": "Should enumerate all available data types and sources"
                }
            }
        ]

        return tests

    def generate_edge_case_tests(self) -> List[Dict]:
        """Generate edge case and error condition tests"""
        tests = [
            {
                "id": "nonexistent_customer",
                "category": "edge_cases",
                "inputs": {
                    "customer_id": "nonexistent@example.com",
                    "query": "What is the account status for nonexistent@example.com?"
                },
                "expected": {
                    "customer_found": False,
                    "data_available": False,
                    "explanation": "Should indicate customer not found"
                }
            },
            {
                "id": "empty_query",
                "category": "edge_cases",
                "inputs": {
                    "customer_id": self.customer_context.get('customer_email'),
                    "query": ""
                },
                "expected": {
                    "customer_found": True,
                    "explanation": "Should handle empty query gracefully"
                }
            },
            {
                "id": "malformed_email",
                "category": "edge_cases",
                "inputs": {
                    "customer_id": "not - an - email",
                    "query": "Account status for not - an - email"
                },
                "expected": {
                    "customer_found": False,
                    "explanation": "Should handle malformed email addresses"
                }
            },
            {
                "id": "very_long_query",
                "category": "edge_cases",
                "inputs": {
                    "customer_id": self.customer_context.get('customer_email'),
                    "query": "Please provide an extremely detailed and comprehensive analysis " * 20
                },
                "expected": {
                    "customer_found": True,
                    "explanation": "Should handle very long queries appropriately"
                }
            }
        ]

        return tests

    def generate_all_test_cases(self) -> List[Dict]:
        """Generate all test cases"""
        print("🔄 Generating comprehensive test cases...")

        all_tests = []

        # Generate test cases by category
        all_tests.extend(self.generate_account_status_tests())
        all_tests.extend(self.generate_credit_analysis_tests())
        all_tests.extend(self.generate_transaction_analysis_tests())
        all_tests.extend(self.generate_phone_call_analysis_tests())
        all_tests.extend(self.generate_multi_data_analysis_tests())
        all_tests.extend(self.generate_edge_case_tests())

        print(f"✅ Generated {len(all_tests)} test cases")

        # Print summary by category
        categories = {}
        for test in all_tests:
            category = test.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1

        print("\n📊 Test cases by category:")
        for category, count in categories.items():
            print(f"  • {category}: {count} tests")

        self.test_cases = all_tests
        return all_tests

    def save_test_cases_jsonl(self, output_file: str = None) -> str:
        """Save test cases in JSONL format"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"tests / agenta / test_cases_{timestamp}.jsonl"

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf - 8') as f:
            for test_case in self.test_cases:
                f.write(json.dumps(test_case, ensure_ascii=False) + '\n')

        print(f"✅ Test cases saved to: {output_file}")
        return output_file

    def save_test_cases_json(self, output_file: str = None) -> str:
        """Save test cases in JSON format with metadata"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"tests / agenta / test_suite_{timestamp}.json"

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Count categories
        categories = {}
        for test in self.test_cases:
            category = test.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1

        output_data = {
            "metadata": {
                "generation_timestamp": datetime.now().isoformat(),
                "total_test_cases": len(self.test_cases),
                "categories": categories,
                "customer_context": self.customer_context,
                "ground_truth_fields": len(self.ground_truth)
            },
            "test_cases": self.test_cases
        }

        with open(output_file, 'w', encoding='utf - 8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Test suite saved to: {output_file}")
        return output_file

    def print_summary(self):
        """Print test case generation summary"""
        print("\n📊 TEST CASE GENERATION SUMMARY")
        print("=" * 50)

        print(f"📁 Total Test Cases: {len(self.test_cases)}")
        print(f"👤 Customer: {self.customer_context.get('customer_name')} ({self.customer_context.get('customer_email')})")
        print(f"🎯 Ground Truth Fields: {len(self.ground_truth)}")

        # Category breakdown
        categories = {}
        for test in self.test_cases:
            category = test.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1

        print("\n📋 Test Categories:")
        for category, count in sorted(categories.items()):
            print(f"  • {category}: {count} tests")

        # Sample test case
        if self.test_cases:
            print(f"\n📝 Sample Test Case ({self.test_cases[0]['id']}):")
            sample = self.test_cases[0]
            print(f"  Query: {sample['inputs']['query']}")
            print(f"  Expected fields: {len(sample['expected'])}")
            print(f"  Category: {sample['category']}")


def main():
    """Main execution for testing"""
    print("🚀 TEST CASE GENERATOR")
    print("=" * 40)

    try:
        # Initialize generator
        generator = TestCaseGenerator()

        # Generate all test cases
        test_cases = generator.generate_all_test_cases()

        # Print summary
        generator.print_summary()

        # Save in both formats
        jsonl_file = generator.save_test_cases_jsonl()
        json_file = generator.save_test_cases_json()

        print("\n✅ Test case generation complete!")
        print(f"📁 JSONL file: {jsonl_file}")
        print(f"📁 JSON file: {json_file}")

        return generator

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    main()
