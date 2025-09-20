#!/usr/bin/env python3
"""
GraphQL Validator for Credit Report Testing
Implementation for validating responses using direct GraphQL curl requests
"""

import subprocess
import json
import os
from typing import Dict, Any


class GraphQLValidator:
    """Validate responses using GraphQL curl requests"""

    def __init__(self):
        """Initialize GraphQL validator"""
        self.tilores_api_url = os.getenv("TILORES_API_URL", "https://ly325mgfwk.execute-api.us-east-1.amazonaws.com")
        self.client_id = os.getenv("TILORES_CLIENT_ID")
        self.client_secret = os.getenv("TILORES_CLIENT_SECRET")
        self.token_url = os.getenv("TILORES_TOKEN_URL")
        self._access_token = None

    def build_credit_report_query(self, customer_data: Dict) -> str:
        """Build GraphQL query for credit report"""
        customer_id = customer_data.get("customer_id")
        email = customer_data.get("email")

        # Build search parameters based on available data
        if email:
            search_params = f'"EMAIL": "{email}"'
        elif customer_id:
            search_params = f'"CLIENT_ID": "{customer_id}"'
        else:
            name_parts = customer_data.get("name", "").split()
            if name_parts:
                search_params = f'"FIRST_NAME": "{name_parts[0]}"'
            else:
                search_params = '"FIRST_NAME": "Unknown"'

        query = f"""{{
            search(input: {{
                searchParams: {{{search_params}}}
                recordFieldsToQuery: {{
                    EMAIL: true
                    FIRST_NAME: true
                    LAST_NAME: true
                    CLIENT_ID: true
                    CUSTOMER_AGE: true
                    STARTING_CREDIT_SCORE: true
                    CREDIT_RESPONSE: true
                    TRANSUNION_REPORT: true
                }}
            }}) {{
                entities {{
                    id
                    hits
                    records {{
                        id
                        EMAIL
                        FIRST_NAME
                        LAST_NAME
                        CLIENT_ID
                        CUSTOMER_AGE
                        STARTING_CREDIT_SCORE
                        CREDIT_RESPONSE
                        TRANSUNION_REPORT
                    }}
                }}
            }}
        }}"""

        return query.strip()

    def execute_curl_request(self, query: str, customer_data: Dict) -> Dict[str, Any]:
        """Execute curl request with GraphQL query"""
        try:
            # Get access token if not already obtained
            if not self._access_token:
                self._get_access_token()

            # Prepare curl command
            curl_cmd = [
                "curl",
                "-X",
                "POST",
                self.tilores_api_url,
                "-H",
                "Content-Type: application/json",
                "-H",
                f"Authorization: Bearer {self._access_token}",
                "-d",
                json.dumps({"query": query}),
                "--max-time",
                "30",
            ]

            # Execute curl command
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                try:
                    response_data = json.loads(result.stdout)
                    return {
                        "success": True,
                        "data": response_data,
                        "response_time": "measured_by_curl",
                        "customer_id": customer_data.get("customer_id"),
                    }
                except json.JSONDecodeError as e:
                    return {"success": False, "error": f"JSON decode error: {e}", "raw_output": result.stdout[:500]}
            else:
                return {
                    "success": False,
                    "error": f"Curl failed with code {result.returncode}",
                    "stderr": result.stderr[:500],
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Request timeout (30s)", "customer_id": customer_data.get("customer_id")}
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "customer_id": customer_data.get("customer_id"),
            }

    def evaluate_response_quality(self, response: str, expected_data: Dict) -> Dict[str, Any]:
        """Evaluate response quality against expected data"""
        try:
            # Parse response if it's JSON string
            if isinstance(response, str):
                response_data = json.loads(response)
            else:
                response_data = response

            quality_score = 0
            details = {}

            # Check if we got data back
            if response_data.get("data", {}).get("search", {}).get("entities"):
                entities = response_data["data"]["search"]["entities"]
                details["entities_found"] = len(entities)
                quality_score += 20

                # Check if we found records
                total_records = sum(len(entity.get("records", [])) for entity in entities)
                details["total_records"] = total_records
                if total_records > 0:
                    quality_score += 30

                # Check for expected customer data
                for entity in entities:
                    for record in entity.get("records", []):
                        # Check email match
                        if expected_data.get("email") and record.get("EMAIL") == expected_data["email"]:
                            details["email_match"] = True
                            quality_score += 20

                        # Check name match
                        expected_name = expected_data.get("name", "").split()
                        if len(expected_name) >= 2:
                            first_match = record.get("FIRST_NAME") == expected_name[0]
                            last_match = record.get("LAST_NAME") == expected_name[1]
                            if first_match and last_match:
                                details["name_match"] = True
                                quality_score += 20

                        # Check for credit data
                        if record.get("STARTING_CREDIT_SCORE") or record.get("CREDIT_RESPONSE"):
                            details["has_credit_data"] = True
                            quality_score += 10
            else:
                details["no_entities"] = True

            # Check for errors
            if response_data.get("errors"):
                details["has_errors"] = True
                details["errors"] = response_data["errors"]
                quality_score = max(0, quality_score - 30)

            return {
                "quality_score": quality_score,
                "max_score": 100,
                "details": details,
                "response_valid": quality_score > 0,
            }

        except Exception as e:
            return {
                "quality_score": 0,
                "max_score": 100,
                "details": {"evaluation_error": str(e)},
                "response_valid": False,
            }

    def _get_access_token(self):
        """Get OAuth access token for Tilores API"""
        try:
            curl_cmd = [
                "curl",
                "-X",
                "POST",
                self.token_url,
                "-H",
                "Content-Type: application/x-www-form-urlencoded",
                "-d",
                f"grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}",
                "--max-time",
                "10",
            ]

            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                token_data = json.loads(result.stdout)
                self._access_token = token_data.get("access_token")
            else:
                raise Exception(f"Token request failed: {result.stderr}")

        except Exception as e:
            raise Exception(f"Failed to get access token: {e}")
