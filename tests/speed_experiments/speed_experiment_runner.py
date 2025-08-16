#!/usr/bin/env python3
"""
LangSmith Speed Experiment Runner
Implementation for testing the 6 fastest models with conversational credit scenarios
"""

import time
import os
import requests
from typing import Dict, List, Any, Union


class LangSmithSpeedExperimentRunner:
    """Runner for LangSmith speed experiments with the 6 fastest models"""

    def __init__(self):
        """Initialize the experiment runner"""
        self.api_url = os.getenv("TILORES_API_URL", "https://tiloresx-production.up.railway.app")
        self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "tilores-speed-experiments")
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")

    def create_experiment_config(self, experiment_name: str, models: List[Dict]) -> Dict[str, Any]:
        """Create LangSmith experiment configuration"""
        config = {
            "name": experiment_name,
            "description": f"Speed and accuracy testing for {len(models)} fastest models",
            "models": models,
            "scenarios": self._get_credit_scenarios(),
            "metrics": [
                "response_time_ms",
                "tokens_per_second",
                "accuracy_score",
                "credit_data_completeness"
            ],
            "langsmith_project": self.langsmith_project,
            "created_at": time.time()
        }
        return config

    def create_conversational_credit_scenario(self, customer_data: Dict) -> Dict[str, Any]:
        """Create conversational credit report scenario"""
        scenario = {
            "scenario_id": f"credit_conversation_{customer_data.get('customer_id', 'unknown')}",
            "customer_data": customer_data,
            "conversation": [
                {
                    "turn": 1,
                    "role": "user",
                    "content": f"Hello, I need information about customer {customer_data.get('name', 'Unknown')}"
                },
                {
                    "turn": 2,
                    "role": "user",
                    "content": f"Can you get me the credit report for customer ID {customer_data.get('customer_id')}?"
                }
            ],
            "expected_data": {
                "customer_name": customer_data.get("name"),
                "credit_score": customer_data.get("credit_score"),
                "has_credit_report": customer_data.get("has_credit_report", False)
            }
        }
        return scenario

    def measure_response_speed(self, model_name: str, message: str) -> Dict[str, Union[float, bool, str, int]]:
        """Measure response speed for a model"""
        start_time = time.time()

        # Make request to our production API
        try:
            response = requests.post(
                f"{self.api_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": message}],
                    "max_tokens": 500
                },
                timeout=30
            )

            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            if response.status_code == 200:
                response_data = response.json()
                content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

                # Estimate tokens per second (rough calculation)
                estimated_tokens = len(content.split())
                tokens_per_second = estimated_tokens / (response_time_ms / 1000) if response_time_ms > 0 else 0

                return {
                    "response_time_ms": response_time_ms,
                    "tokens_per_second": tokens_per_second,
                    "success": True,
                    "content_length": len(content)
                }
            else:
                return {
                    "response_time_ms": response_time_ms,
                    "tokens_per_second": 0,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }

        except Exception as e:
            end_time = time.time()
            return {
                "response_time_ms": (end_time - start_time) * 1000,
                "tokens_per_second": 0,
                "success": False,
                "error": str(e)
            }

    def evaluate_response_accuracy(self, response: str, expected_data: Dict) -> Dict[str, Any]:
        """Evaluate response accuracy against expected credit data"""
        accuracy_score = 0
        details = {}

        # Check if customer name is mentioned
        if expected_data.get("customer_name"):
            name_mentioned = expected_data["customer_name"].lower() in response.lower()
            details["name_mentioned"] = name_mentioned
            if name_mentioned:
                accuracy_score += 25

        # Check if credit score is mentioned
        if expected_data.get("credit_score"):
            score_mentioned = str(expected_data["credit_score"]) in response
            details["credit_score_mentioned"] = score_mentioned
            if score_mentioned:
                accuracy_score += 25

        # Check for credit-related keywords
        credit_keywords = ["credit", "score", "report", "utilization", "payment", "history"]
        keywords_found = sum(1 for keyword in credit_keywords if keyword in response.lower())
        details["credit_keywords_found"] = keywords_found
        accuracy_score += min(keywords_found * 5, 25)

        # Check response length (comprehensive responses score higher)
        if len(response) > 200:
            details["comprehensive_response"] = True
            accuracy_score += 25
        else:
            details["comprehensive_response"] = False

        return {
            "accuracy_score": accuracy_score,
            "max_score": 100,
            "details": details,
            "response_length": len(response)
        }

    def validate_with_graphql_curl(self, customer_data: Dict) -> Dict[str, Any]:
        """Validate response quality using GraphQL curl"""
        # This will be implemented to test direct GraphQL queries
        # For now, return a placeholder that indicates the validation structure
        return {
            "validation_method": "graphql_curl",
            "customer_id": customer_data.get("customer_id"),
            "query_executed": False,
            "note": "GraphQL validation implementation pending"
        }

    def _get_credit_scenarios(self) -> List[Dict]:
        """Get predefined credit report scenarios"""
        return [
            {
                "customer_id": "1881899",
                "name": "John Smith",
                "email": "john.smith@techcorp.com",
                "has_credit_report": True,
                "credit_score": 750
            },
            {
                "customer_id": "1992837",
                "name": "Sarah Johnson",
                "email": "sarah.johnson@healthcare.org",
                "has_credit_report": True,
                "credit_score": 820
            },
            {
                "customer_id": "2003948",
                "name": "Michael Brown",
                "email": "mike.brown@retail.com",
                "has_credit_report": True,
                "credit_score": 680
            }
        ]
