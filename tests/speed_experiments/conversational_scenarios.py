#!/usr/bin/env python3
"""
Conversational Credit Report Scenarios
Implementation for creating multi-turn conversations with credit data requests
"""

from typing import Dict, List, Any


class ConversationalCreditScenarios:
    """Create conversational scenarios for credit report testing"""

    def __init__(self):
        """Initialize conversational scenarios"""
        self.scenarios_created = 0

    def create_two_turn_scenario(self, customer_data: Dict) -> Dict[str, Any]:
        """Create a two-turn conversation scenario"""
        self.scenarios_created += 1

        scenario = {
            "scenario_id": f"two_turn_{self.scenarios_created}",
            "customer_data": customer_data,
            "turns": [
                {
                    "turn_number": 1,
                    "role": "user",
                    "content": f"Hello, I need to look up information for customer {customer_data.get('name', 'Unknown')}",
                    "expected_response_elements": ["greeting", "customer_acknowledgment", "data_request"],
                },
                {
                    "turn_number": 2,
                    "role": "user",
                    "content": f"Can you pull the credit report for customer ID {customer_data.get('customer_id')}? I need to see their credit score and utilization.",
                    "expected_response_elements": [
                        "credit_score",
                        "utilization_data",
                        "payment_history",
                        "account_details",
                    ],
                },
            ],
            "success_criteria": {
                "min_response_time_ms": 2000,
                "max_response_time_ms": 10000,
                "required_data_points": ["customer_name", "credit_score", "account_information"],
            },
        }

        return scenario

    def create_credit_report_request(self, customer_data: Dict) -> Dict[str, Any]:
        """Create credit report request scenario"""
        request = {
            "request_type": "credit_report",
            "customer_identifier": {
                "customer_id": customer_data.get("customer_id"),
                "email": customer_data.get("email"),
                "name": customer_data.get("name"),
            },
            "request_content": f"Get me the complete credit report for {customer_data.get('name')} (ID: {customer_data.get('customer_id')}). I need to see their current credit score, utilization rates, payment history, and any recent inquiries.",
            "expected_response_structure": {
                "customer_info": {
                    "name": customer_data.get("name"),
                    "id": customer_data.get("customer_id"),
                    "email": customer_data.get("email"),
                },
                "credit_data": {
                    "score": customer_data.get("credit_score"),
                    "utilization": "percentage",
                    "payment_history": "status",
                    "inquiries": "list",
                },
            },
            "quality_metrics": {"completeness_score": 0, "accuracy_score": 0, "response_time_ms": 0},
        }

        return request

    def score_credit_response_accuracy(self, response: str, expected_data: Dict) -> Dict[str, Any]:
        """Score the accuracy of credit response"""
        score = 0
        max_score = 100
        details = {}

        # Check for customer identification (25 points)
        customer_name = expected_data.get("name", "")
        if customer_name and customer_name.lower() in response.lower():
            score += 25
            details["customer_identified"] = True
        else:
            details["customer_identified"] = False

        # Check for credit score mention (25 points)
        expected_score = expected_data.get("credit_score")
        if expected_score and str(expected_score) in response:
            score += 25
            details["credit_score_mentioned"] = True
        else:
            details["credit_score_mentioned"] = False

        # Check for credit-related terminology (25 points)
        credit_terms = [
            "credit",
            "score",
            "utilization",
            "payment",
            "history",
            "inquiry",
            "account",
            "balance",
            "limit",
            "report",
        ]
        terms_found = sum(1 for term in credit_terms if term.lower() in response.lower())
        term_score = min(terms_found * 3, 25)  # Max 25 points
        score += term_score
        details["credit_terms_found"] = terms_found
        details["credit_terms_score"] = term_score

        # Check response comprehensiveness (25 points)
        response_length = len(response)
        if response_length > 500:
            comprehensiveness_score = 25
        elif response_length > 200:
            comprehensiveness_score = 15
        elif response_length > 100:
            comprehensiveness_score = 10
        else:
            comprehensiveness_score = 5

        score += comprehensiveness_score
        details["response_length"] = response_length
        details["comprehensiveness_score"] = comprehensiveness_score

        # Calculate final accuracy percentage
        accuracy_percentage = (score / max_score) * 100

        return {
            "accuracy_score": score,
            "max_score": max_score,
            "accuracy_percentage": accuracy_percentage,
            "details": details,
            "grade": self._get_grade(accuracy_percentage),
        }

    def create_batch_scenarios(self, customers: List[Dict]) -> List[Dict[str, Any]]:
        """Create multiple scenarios for batch testing"""
        scenarios = []

        for customer in customers:
            # Create both two-turn and credit report scenarios
            two_turn = self.create_two_turn_scenario(customer)
            credit_request = self.create_credit_report_request(customer)

            scenarios.append(
                {
                    "customer_id": customer.get("customer_id"),
                    "customer_name": customer.get("name"),
                    "two_turn_scenario": two_turn,
                    "credit_request_scenario": credit_request,
                }
            )

        return scenarios

    def _get_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade"""
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"
