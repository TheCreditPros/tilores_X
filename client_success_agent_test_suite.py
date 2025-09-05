#!/usr/bin/env python3
"""
Comprehensive Client Success Agent Test Suite
Tests 50 most common multi-threaded conversations across all data sources
"""

import json
import requests
import time
import threading
from datetime import datetime
from typing import Dict, List, Any
import concurrent.futures

class ClientSuccessAgentTestSuite:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results = []
        self.test_customer = "e.j.price1986@gmail.com"
        self.client_id = "1747598"
        self.customer_name = "Esteban Price"

        # 50 Most Common Client Success Agent Conversations
        self.conversation_scenarios = [
            # Basic Account Information (10 scenarios)
            {
                "name": "Basic Account Lookup",
                "conversation": [
                    f"Who is {self.test_customer}?",
                    "What's their account status?",
                    "When did they enroll?"
                ],
                "expected_data": ["Esteban Price", "Active", "2025-04-10", "$54.75"]
            },
            {
                "name": "Client ID Lookup",
                "conversation": [
                    f"Look up client {self.client_id}",
                    "What product are they on?",
                    "How much do they pay monthly?"
                ],
                "expected_data": ["Esteban Price", "Downsell Credit Repair", "$54.75"]
            },
            {
                "name": "Customer Name Search",
                "conversation": [
                    f"Find customer {self.customer_name}",
                    "Show me their contact information",
                    "What's their enrollment date?"
                ],
                "expected_data": ["e.j.price1986@gmail.com", "Active", "2025-04-10"]
            },
            {
                "name": "Account Status Check",
                "conversation": [
                    f"Is {self.test_customer} active?",
                    "What's their current status?",
                    "Any issues with their account?"
                ],
                "expected_data": ["Active", "Esteban Price", "no issues"]
            },
            {
                "name": "Product Information",
                "conversation": [
                    f"What service does {self.test_customer} have?",
                    "How much do they pay?",
                    "When do they get billed?"
                ],
                "expected_data": ["Credit Repair", "$54.75", "Monthly"]
            },
            {
                "name": "Enrollment Details",
                "conversation": [
                    f"When did {self.test_customer} sign up?",
                    "How long have they been a customer?",
                    "What was their original product?"
                ],
                "expected_data": ["2025-04-10", "Downsell Credit Repair"]
            },
            {
                "name": "Contact Verification",
                "conversation": [
                    f"Verify contact info for {self.customer_name}",
                    "What's their email address?",
                    "Do we have their phone number?"
                ],
                "expected_data": ["e.j.price1986@gmail.com", "Esteban Price"]
            },
            {
                "name": "Account Summary",
                "conversation": [
                    f"Give me a summary of {self.test_customer}",
                    "What's their current situation?",
                    "Any recent changes?"
                ],
                "expected_data": ["Esteban Price", "Active", "$54.75", "Credit Repair"]
            },
            {
                "name": "Customer Profile",
                "conversation": [
                    f"Pull up the profile for client {self.client_id}",
                    "What do I need to know about them?",
                    "Any special notes?"
                ],
                "expected_data": ["Esteban Price", "Active", "Credit Repair"]
            },
            {
                "name": "Quick Status Check",
                "conversation": [
                    f"Status of {self.test_customer}?",
                    "All good with their account?",
                    "Anything I should know?"
                ],
                "expected_data": ["Active", "Esteban Price", "$54.75"]
            },

            # Credit Analysis (15 scenarios)
            {
                "name": "Credit Score Inquiry",
                "conversation": [
                    f"What's the credit score for {self.test_customer}?",
                    "Which bureau is that from?",
                    "When was it last updated?"
                ],
                "expected_data": ["Credit Score", "Esteban Price", "bureau", "monitoring"]
            },
            {
                "name": "Experian Report Request",
                "conversation": [
                    f"Show me {self.customer_name}'s Experian report",
                    "What's their current score?",
                    "Any recent changes?"
                ],
                "expected_data": ["Experian", "Credit", "Esteban Price", "monitoring"]
            },
            {
                "name": "TransUnion Analysis",
                "conversation": [
                    f"Pull TransUnion data for {self.test_customer}",
                    "How does it compare to Experian?",
                    "Any discrepancies?"
                ],
                "expected_data": ["TransUnion", "Credit", "Esteban Price", "monitoring"]
            },
            {
                "name": "Equifax Review",
                "conversation": [
                    f"Check Equifax report for client {self.client_id}",
                    "What's showing up there?",
                    "Any negative items?"
                ],
                "expected_data": ["Equifax", "Credit", "Esteban Price", "monitoring"]
            },
            {
                "name": "Credit Utilization Check",
                "conversation": [
                    f"What's {self.test_customer}'s credit utilization?",
                    "Is it improving?",
                    "What's the target?"
                ],
                "expected_data": ["Credit", "utilization", "Esteban Price", "improving"]
            },
            {
                "name": "Payment History Review",
                "conversation": [
                    f"How's {self.customer_name}'s payment history?",
                    "Any late payments?",
                    "Trend improving?"
                ],
                "expected_data": ["payment history", "Credit", "Esteban Price"]
            },
            {
                "name": "Credit Accounts Analysis",
                "conversation": [
                    f"Show me credit accounts for {self.test_customer}",
                    "How many accounts do they have?",
                    "Any closed accounts?"
                ],
                "expected_data": ["Credit", "accounts", "Esteban Price"]
            },
            {
                "name": "Credit Inquiries Check",
                "conversation": [
                    f"Any recent credit inquiries for {self.client_id}?",
                    "Hard or soft inquiries?",
                    "Impact on score?"
                ],
                "expected_data": ["Credit", "inquiries", "Esteban Price"]
            },
            {
                "name": "Dispute Status",
                "conversation": [
                    f"Are there any disputes for {self.test_customer}?",
                    "What's being disputed?",
                    "Status of disputes?"
                ],
                "expected_data": ["dispute", "Credit", "Esteban Price", "resolution"]
            },
            {
                "name": "Credit Improvement Progress",
                "conversation": [
                    f"How is {self.customer_name}'s credit improving?",
                    "What's the trend?",
                    "Expected timeline?"
                ],
                "expected_data": ["Credit", "improving", "Esteban Price", "repair program"]
            },
            {
                "name": "Bureau Comparison",
                "conversation": [
                    f"Compare all three bureaus for {self.test_customer}",
                    "Which is highest?",
                    "Biggest differences?"
                ],
                "expected_data": ["Experian", "TransUnion", "Equifax", "Esteban Price"]
            },
            {
                "name": "Credit Monitoring Status",
                "conversation": [
                    f"Is {self.test_customer} being monitored?",
                    "How often are reports pulled?",
                    "Any alerts?"
                ],
                "expected_data": ["monitoring", "Credit", "Esteban Price", "Active"]
            },
            {
                "name": "Score Change Analysis",
                "conversation": [
                    f"Has {self.customer_name}'s score changed recently?",
                    "Up or down?",
                    "What caused the change?"
                ],
                "expected_data": ["Credit Score", "change", "Esteban Price"]
            },
            {
                "name": "Credit Goals Review",
                "conversation": [
                    f"What are the credit goals for {self.test_customer}?",
                    "Target score?",
                    "Timeline to achieve?"
                ],
                "expected_data": ["Credit", "goals", "Esteban Price", "repair"]
            },
            {
                "name": "Negative Items Check",
                "conversation": [
                    f"Any negative items for client {self.client_id}?",
                    "What type of negatives?",
                    "Removal strategy?"
                ],
                "expected_data": ["negative", "Credit", "Esteban Price", "dispute"]
            },

            # Payment & Transaction Analysis (15 scenarios)
            {
                "name": "Payment History Review",
                "conversation": [
                    f"Show me payment history for {self.test_customer}",
                    "Are they current?",
                    "Any missed payments?"
                ],
                "expected_data": ["Payment History", "Esteban Price", "$54.75", "Active"]
            },
            {
                "name": "Last Payment Check",
                "conversation": [
                    f"When was {self.customer_name}'s last payment?",
                    "How much was it?",
                    "Payment method?"
                ],
                "expected_data": ["Last Payment", "Esteban Price", "payment"]
            },
            {
                "name": "Next Payment Due",
                "conversation": [
                    f"When is {self.test_customer}'s next payment due?",
                    "How much will it be?",
                    "Auto-pay setup?"
                ],
                "expected_data": ["Next Payment", "Esteban Price", "$54.75"]
            },
            {
                "name": "Billing Cycle Info",
                "conversation": [
                    f"What's the billing cycle for client {self.client_id}?",
                    "Monthly or annual?",
                    "Bill date?"
                ],
                "expected_data": ["billing", "Monthly", "Esteban Price"]
            },
            {
                "name": "Payment Method Verification",
                "conversation": [
                    f"How does {self.test_customer} pay?",
                    "Credit card or bank?",
                    "Need to update payment method?"
                ],
                "expected_data": ["payment method", "Esteban Price"]
            },
            {
                "name": "Transaction History",
                "conversation": [
                    f"Show all transactions for {self.customer_name}",
                    "Any refunds or adjustments?",
                    "Payment patterns?"
                ],
                "expected_data": ["Transaction", "Esteban Price", "history"]
            },
            {
                "name": "Outstanding Balance",
                "conversation": [
                    f"Does {self.test_customer} owe anything?",
                    "Current balance?",
                    "Past due amount?"
                ],
                "expected_data": ["balance", "Esteban Price", "Active"]
            },
            {
                "name": "Payment Plan Status",
                "conversation": [
                    f"Is {self.customer_name} on a payment plan?",
                    "What are the terms?",
                    "Compliance status?"
                ],
                "expected_data": ["payment plan", "Esteban Price", "Active"]
            },
            {
                "name": "Refund History",
                "conversation": [
                    f"Any refunds issued to {self.test_customer}?",
                    "Reason for refunds?",
                    "Amounts?"
                ],
                "expected_data": ["refund", "Esteban Price"]
            },
            {
                "name": "Billing Issues Check",
                "conversation": [
                    f"Any billing problems with client {self.client_id}?",
                    "Failed payments?",
                    "Disputes?"
                ],
                "expected_data": ["billing", "Esteban Price", "Active"]
            },
            {
                "name": "Auto-Pay Status",
                "conversation": [
                    f"Is {self.test_customer} on auto-pay?",
                    "Which card/account?",
                    "Working properly?"
                ],
                "expected_data": ["auto-pay", "Esteban Price"]
            },
            {
                "name": "Payment Frequency",
                "conversation": [
                    f"How often does {self.customer_name} pay?",
                    "Monthly payments?",
                    "On time percentage?"
                ],
                "expected_data": ["payment frequency", "Monthly", "Esteban Price"]
            },
            {
                "name": "Charge History",
                "conversation": [
                    f"What charges are on {self.test_customer}'s account?",
                    "Monthly service fees?",
                    "Any additional charges?"
                ],
                "expected_data": ["charges", "$54.75", "Esteban Price"]
            },
            {
                "name": "Payment Trends",
                "conversation": [
                    f"Payment trends for client {self.client_id}?",
                    "Consistent payer?",
                    "Any patterns?"
                ],
                "expected_data": ["payment trends", "Esteban Price"]
            },
            {
                "name": "Invoice Details",
                "conversation": [
                    f"Show me latest invoice for {self.test_customer}",
                    "What's included?",
                    "Due date?"
                ],
                "expected_data": ["invoice", "Esteban Price", "$54.75"]
            },

            # Multi-Data Comprehensive Analysis (10 scenarios)
            {
                "name": "Complete Customer Overview",
                "conversation": [
                    f"Give me everything on {self.test_customer}",
                    "Credit, payments, account status - all of it",
                    "What's the full picture?"
                ],
                "expected_data": ["Esteban Price", "Credit", "Payment", "Active", "$54.75"]
            },
            {
                "name": "Customer Health Check",
                "conversation": [
                    f"How is {self.customer_name} doing overall?",
                    "Credit improving? Payments current?",
                    "Any concerns?"
                ],
                "expected_data": ["Esteban Price", "Credit", "improving", "Active"]
            },
            {
                "name": "Account Performance Review",
                "conversation": [
                    f"Performance review for client {self.client_id}",
                    "Credit progress and payment history",
                    "Meeting goals?"
                ],
                "expected_data": ["Esteban Price", "Credit", "Payment", "progress"]
            },
            {
                "name": "Comprehensive Analysis",
                "conversation": [
                    f"Full analysis of {self.test_customer}",
                    "All data sources and trends",
                    "Recommendations?"
                ],
                "expected_data": ["Esteban Price", "Credit", "Payment", "analysis"]
            },
            {
                "name": "Customer Success Metrics",
                "conversation": [
                    f"Success metrics for {self.customer_name}",
                    "Credit improvement and payment compliance",
                    "Overall satisfaction?"
                ],
                "expected_data": ["Esteban Price", "Credit", "Payment", "success"]
            },
            {
                "name": "Risk Assessment",
                "conversation": [
                    f"Risk assessment for {self.test_customer}",
                    "Payment risk? Credit risk?",
                    "Retention probability?"
                ],
                "expected_data": ["risk", "Esteban Price", "Active"]
            },
            {
                "name": "Customer Journey Review",
                "conversation": [
                    f"Customer journey for client {self.client_id}",
                    "From enrollment to now",
                    "Key milestones?"
                ],
                "expected_data": ["journey", "Esteban Price", "2025-04-10"]
            },
            {
                "name": "Service Effectiveness",
                "conversation": [
                    f"How effective is our service for {self.test_customer}?",
                    "Credit improvements? Worth the cost?",
                    "ROI for customer?"
                ],
                "expected_data": ["effectiveness", "Credit", "Esteban Price"]
            },
            {
                "name": "Retention Analysis",
                "conversation": [
                    f"Retention analysis for {self.customer_name}",
                    "Likely to stay or leave?",
                    "Satisfaction indicators?"
                ],
                "expected_data": ["retention", "Esteban Price", "Active"]
            },
            {
                "name": "Complete Data Dump",
                "conversation": [
                    f"Everything we have on {self.test_customer}",
                    "All systems, all data",
                    "Complete picture"
                ],
                "expected_data": ["Esteban Price", "Credit", "Payment", "Active", "$54.75"]
            }
        ]

    def send_message(self, message: str) -> Dict[str, Any]:
        """Send a single message to the API"""
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": message}]
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def run_conversation(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a complete conversation scenario"""
        conversation_results = []
        scenario_name = scenario["name"]

        print(f"🧪 Testing: {scenario_name}")

        for i, message in enumerate(scenario["conversation"]):
            print(f"   [{i+1}/{len(scenario['conversation'])}] {message[:50]}...")

            start_time = time.time()
            response = self.send_message(message)
            end_time = time.time()

            if "error" in response:
                conversation_results.append({
                    "message": message,
                    "error": response["error"],
                    "success": False
                })
                print(f"      ❌ Error: {response['error']}")
                break
            else:
                content = response.get("choices", [{}])[0].get("message", {}).get("content", "")

                # Check if expected data is present
                expected_data = scenario.get("expected_data", [])
                found_data = []
                missing_data = []

                for expected in expected_data:
                    if expected.lower() in content.lower():
                        found_data.append(expected)
                    else:
                        missing_data.append(expected)

                success = len(missing_data) == 0

                conversation_results.append({
                    "message": message,
                    "response": content,
                    "response_time": end_time - start_time,
                    "found_data": found_data,
                    "missing_data": missing_data,
                    "success": success
                })

                if success:
                    print(f"      ✅ Success ({len(found_data)}/{len(expected_data)} data points)")
                else:
                    print(f"      ❌ Missing: {', '.join(missing_data)}")

        # Calculate overall scenario success
        scenario_success = all(result.get("success", False) for result in conversation_results)

        return {
            "scenario_name": scenario_name,
            "conversation_results": conversation_results,
            "scenario_success": scenario_success,
            "timestamp": datetime.utcnow().isoformat()
        }

    def run_single_thread_test(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single scenario (for threading)"""
        return self.run_conversation(scenario)

    def run_multithreaded_test(self, max_workers: int = 10):
        """Run all scenarios in parallel"""
        print(f"🚀 Starting Multi-threaded Client Success Agent Test Suite")
        print(f"📋 Testing {len(self.conversation_scenarios)} scenarios with {max_workers} threads")
        print("=" * 80)

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scenarios
            future_to_scenario = {
                executor.submit(self.run_single_thread_test, scenario): scenario
                for scenario in self.conversation_scenarios
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_scenario):
                scenario = future_to_scenario[future]
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    print(f"❌ Scenario {scenario['name']} failed with exception: {e}")
                    self.results.append({
                        "scenario_name": scenario["name"],
                        "error": str(e),
                        "scenario_success": False
                    })

        end_time = time.time()

        # Analyze results
        self.analyze_results(end_time - start_time)

    def analyze_results(self, total_time: float):
        """Analyze and report test results"""
        total_scenarios = len(self.results)
        successful_scenarios = sum(1 for r in self.results if r.get("scenario_success", False))
        success_rate = (successful_scenarios / total_scenarios) * 100 if total_scenarios > 0 else 0

        print("\n" + "=" * 80)
        print("🎯 CLIENT SUCCESS AGENT TEST RESULTS")
        print("=" * 80)
        print(f"Total Scenarios: {total_scenarios}")
        print(f"Successful: {successful_scenarios}")
        print(f"Failed: {total_scenarios - successful_scenarios}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Time: {total_time:.1f}s")
        print(f"Avg Time per Scenario: {total_time/total_scenarios:.1f}s")

        if success_rate >= 100.0:
            print("✅ 🎉 100% SUCCESS ACHIEVED!")
        else:
            print(f"❌ Need {100 - success_rate:.1f}% improvement to reach 100%")

        # Category breakdown
        categories = {
            "Basic Account": [r for r in self.results if "Account" in r.get("scenario_name", "") or "Status" in r.get("scenario_name", "") or "Profile" in r.get("scenario_name", "")],
            "Credit Analysis": [r for r in self.results if "Credit" in r.get("scenario_name", "") or "Score" in r.get("scenario_name", "") or "Bureau" in r.get("scenario_name", "")],
            "Payment & Transaction": [r for r in self.results if "Payment" in r.get("scenario_name", "") or "Transaction" in r.get("scenario_name", "") or "Billing" in r.get("scenario_name", "")],
            "Multi-Data Analysis": [r for r in self.results if "Complete" in r.get("scenario_name", "") or "Comprehensive" in r.get("scenario_name", "") or "Overview" in r.get("scenario_name", "")]
        }

        print("\n📊 Category Breakdown:")
        for category, results in categories.items():
            if results:
                category_success = sum(1 for r in results if r.get("scenario_success", False))
                category_rate = (category_success / len(results)) * 100
                status = "✅" if category_rate >= 100 else "❌"
                print(f"{status} {category:<25}: {category_rate:.1f}% ({category_success}/{len(results)})")

        # Failed scenarios
        failed_scenarios = [r for r in self.results if not r.get("scenario_success", False)]
        if failed_scenarios:
            print(f"\n🚨 FAILED SCENARIOS ({len(failed_scenarios)}):")
            for scenario in failed_scenarios:
                print(f"   • {scenario.get('scenario_name', 'Unknown')}")
                if 'conversation_results' in scenario:
                    for conv_result in scenario['conversation_results']:
                        if not conv_result.get('success', True):
                            missing = conv_result.get('missing_data', [])
                            if missing:
                                print(f"     Missing: {', '.join(missing)}")

        # Save detailed results
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"client_success_test_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump({
                "summary": {
                    "total_scenarios": total_scenarios,
                    "successful_scenarios": successful_scenarios,
                    "success_rate": success_rate,
                    "total_time": total_time
                },
                "results": self.results
            }, f, indent=2)

        print(f"\n📄 Detailed results saved to: {filename}")

        return success_rate

if __name__ == "__main__":
    suite = ClientSuccessAgentTestSuite()
    suite.run_multithreaded_test(max_workers=5)  # Start with 5 threads to avoid overwhelming
