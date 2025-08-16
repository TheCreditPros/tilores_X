"""
Functional Tests for Tilores Data Integration and Accuracy

Tests real Tilores data retrieval, customer search accuracy, and data quality:
- Live Tilores API integration
- Customer search validation with known test records
- Credit report functionality testing
- Data consistency and accuracy validation
- Response quality assessment
"""

import pytest
import time
import os
from typing import Dict, Any
from fastapi.testclient import TestClient

# Import the FastAPI app
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from main_openai_compatible import app


@pytest.mark.functional
@pytest.mark.tilores
class TestTiloresDataValidation:
    """Test Tilores data integration with live API."""

    # Known test records from memory bank
    VALIDATED_TEST_RECORDS = [
        {
            "client_id": "1648647",
            "name": "Dawn Bruton",
            "expected_age": 51,
            "expected_location": "De Soto, Missouri",
            "expected_email": "brutonda@gmail.com",
            "description": "Primary validated test customer",
        }
    ]

    @classmethod
    def setup_class(cls):
        """Set up test client and validate environment."""
        cls.client = TestClient(app)
        cls.test_results = {}
        cls.data_accuracy_scores = {}

        # Validate required environment variables
        required_env_vars = ["TILORES_TOKEN", "TILORES_URL"]
        cls.missing_env_vars = []

        for var in required_env_vars:
            if not os.getenv(var):
                cls.missing_env_vars.append(var)

        if cls.missing_env_vars:
            pytest.skip(f"Missing Tilores environment variables: {cls.missing_env_vars}")

    def make_customer_search_request(self, query: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """Make a customer search request and analyze response."""
        start_time = time.time()

        response = self.client.post(
            "/v1/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": query}],
                "temperature": 0.0,  # Deterministic for testing
                "max_tokens": 1500,
            },
        )

        response_time = (time.time() - start_time) * 1000

        assert response.status_code == 200, f"Request failed: {response.status_code} - {response.text}"

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        return {"response": data, "content": content, "response_time_ms": response_time, "query": query}

    def test_validated_customer_search_by_client_id(self):
        """Test customer search with validated test record using client ID."""
        test_record = self.VALIDATED_TEST_RECORDS[0]
        query = f"Find customer with client ID {test_record['client_id']}"

        result = self.make_customer_search_request(query)
        content = result["content"].lower()

        # Validate response contains expected customer information
        accuracy_checks = {
            "client_id": test_record["client_id"] in content,
            "name_dawn": "dawn" in content,
            "name_bruton": "bruton" in content,
            "email_present": "brutonda" in content or "gmail.com" in content,
            "location_missouri": "missouri" in content or "de soto" in content,
        }

        passed_checks = sum(accuracy_checks.values())
        total_checks = len(accuracy_checks)
        accuracy_score = (passed_checks / total_checks) * 100

        # Log detailed results
        print(f"\n🔍 Customer Search Validation for {test_record['name']}:")
        print(f"   Query: {query}")
        print(f"   Response time: {result['response_time_ms']:.0f}ms")
        print(f"   Accuracy checks: {passed_checks}/{total_checks} ({accuracy_score:.1f}%)")

        for check, passed in accuracy_checks.items():
            status = "✓" if passed else "✗"
            print(f"   {status} {check}")

        # Store results
        self.data_accuracy_scores["client_id_search"] = accuracy_score
        self.test_results["validated_customer_search"] = accuracy_score >= 80  # 80% accuracy threshold

        # Performance validation
        assert result["response_time_ms"] < 8000, f"Customer search too slow: {result['response_time_ms']}ms"

        # Accuracy validation
        assert accuracy_score >= 60, f"Accuracy too low: {accuracy_score}% (expected ≥60%)"

    def test_customer_search_by_email_pattern(self):
        """Test customer search using email pattern matching."""
        query = "Find customer with email containing brutonda"

        result = self.make_customer_search_request(query)
        content = result["content"].lower()

        # Check for expected customer information
        email_checks = {
            "email_found": "brutonda" in content,
            "gmail_domain": "gmail" in content,
            "customer_name": "dawn" in content or "bruton" in content,
            "data_present": len(content) > 100,  # Substantial response
        }

        passed_checks = sum(email_checks.values())
        accuracy_score = (passed_checks / len(email_checks)) * 100

        self.data_accuracy_scores["email_search"] = accuracy_score
        self.test_results["email_search_accuracy"] = accuracy_score >= 75

        assert result["response_time_ms"] < 6000, f"Email search too slow: {result['response_time_ms']}ms"

    def test_customer_360_comprehensive_data(self):
        """Test comprehensive customer 360 view with all data types."""
        test_record = self.VALIDATED_TEST_RECORDS[0]
        query = f"Get complete customer 360 profile for client {test_record['client_id']} including all available data"

        result = self.make_customer_search_request(query)
        content = result["content"]

        # Analyze comprehensiveness of response
        data_elements = {
            "personal_info": any(term in content.lower() for term in ["name", "age", "email", "phone"]),
            "location_info": any(term in content.lower() for term in ["address", "city", "state", "location"]),
            "account_info": any(term in content.lower() for term in ["account", "customer", "id", "client"]),
            "activity_data": any(term in content.lower() for term in ["activity", "transaction", "payment"]),
            "substantial_content": len(content) > 200,  # Comprehensive response
        }

        comprehensiveness_score = (sum(data_elements.values()) / len(data_elements)) * 100

        print("\n📊 Customer 360 Comprehensiveness Analysis:")
        print(f"   Response length: {len(content)} characters")
        print(f"   Data elements: {sum(data_elements.values())}/{len(data_elements)}")
        print(f"   Comprehensiveness: {comprehensiveness_score:.1f}%")

        self.data_accuracy_scores["customer_360"] = comprehensiveness_score
        self.test_results["customer_360_comprehensive"] = comprehensiveness_score >= 60

        # Performance check for complex queries
        assert result["response_time_ms"] < 10000, f"Customer 360 query too slow: {result['response_time_ms']}ms"

    def test_credit_analysis_functionality(self):
        """Test credit analysis capabilities if available."""
        query = "Get credit report and analysis for customer 1648647"

        result = self.make_customer_search_request(query)
        content = result["content"].lower()

        # Check for credit-related information
        credit_indicators = {
            "credit_mentioned": "credit" in content,
            "score_or_rating": any(term in content for term in ["score", "rating", "analysis"]),
            "financial_data": any(term in content for term in ["payment", "account", "financial"]),
            "meaningful_response": len(content) > 50,
        }

        credit_functionality_score = (sum(credit_indicators.values()) / len(credit_indicators)) * 100

        self.data_accuracy_scores["credit_functionality"] = credit_functionality_score
        self.test_results["credit_analysis"] = (
            credit_functionality_score >= 50
        )  # Lower threshold as credit may not always be available

        print("\n💳 Credit Analysis Test:")
        print(f"   Credit functionality: {credit_functionality_score:.1f}%")
        print(f"   Response time: {result['response_time_ms']:.0f}ms")

    def test_data_consistency_across_queries(self):
        """Test data consistency across multiple query formats for same customer."""
        test_record = self.VALIDATED_TEST_RECORDS[0]

        queries = [
            f"Find customer {test_record['client_id']}",
            f"Search for client ID {test_record['client_id']}",
            f"Look up customer with ID {test_record['client_id']}",
        ]

        responses = []
        for query in queries:
            result = self.make_customer_search_request(query)
            responses.append(result["content"].lower())

        # Check consistency across responses
        key_elements = ["dawn", "bruton", "1648647"]
        consistency_scores = []

        for element in key_elements:
            element_appearances = sum(1 for response in responses if element in response)
            consistency_scores.append(element_appearances / len(responses))

        overall_consistency = (sum(consistency_scores) / len(consistency_scores)) * 100

        print("\n🔄 Data Consistency Analysis:")
        print(f"   Queries tested: {len(queries)}")
        print(f"   Overall consistency: {overall_consistency:.1f}%")

        self.data_accuracy_scores["data_consistency"] = overall_consistency
        self.test_results["data_consistency"] = overall_consistency >= 70

        assert overall_consistency >= 50, f"Data consistency too low: {overall_consistency}%"

    def test_invalid_customer_handling(self):
        """Test handling of invalid or non-existent customer queries."""
        invalid_queries = [
            "Find customer with client ID 9999999",
            "Search for customer nonexistent@example.com",
            "Look up customer John Nonexistent",
        ]

        handled_correctly = 0

        for query in invalid_queries:
            result = self.make_customer_search_request(query)
            content = result["content"].lower()

            # Check for appropriate "not found" handling
            not_found_indicators = [
                "not found",
                "no results",
                "no customer",
                "not located",
                "unable to find",
                "no records",
                "does not exist",
            ]

            if any(indicator in content for indicator in not_found_indicators):
                handled_correctly += 1
                print(f"   ✓ Correctly handled: {query[:30]}...")
            else:
                print(f"   ✗ Poorly handled: {query[:30]}...")

        handling_score = (handled_correctly / len(invalid_queries)) * 100

        self.data_accuracy_scores["invalid_handling"] = handling_score
        self.test_results["invalid_customer_handling"] = handling_score >= 60

        print(f"\n🚫 Invalid Customer Handling: {handling_score:.1f}%")

    def test_response_quality_metrics(self):
        """Test overall response quality metrics."""
        test_record = self.VALIDATED_TEST_RECORDS[0]
        query = f"Tell me about customer {test_record['client_id']}"

        result = self.make_customer_search_request(query)
        content = result["content"]

        # Quality metrics
        quality_metrics = {
            "appropriate_length": 50 <= len(content) <= 2000,
            "contains_data": any(term in content.lower() for term in ["dawn", "bruton", "customer"]),
            "well_formatted": not content.startswith("Error") and len(content.strip()) > 0,
            "professional_tone": not any(term in content.lower() for term in ["sorry", "can't", "unable"]),
            "fast_response": result["response_time_ms"] < 5000,
        }

        quality_score = (sum(quality_metrics.values()) / len(quality_metrics)) * 100

        print("\n⭐ Response Quality Metrics:")
        for metric, passed in quality_metrics.items():
            status = "✓" if passed else "✗"
            print(f"   {status} {metric}")
        print(f"   Overall quality: {quality_score:.1f}%")

        self.data_accuracy_scores["response_quality"] = quality_score
        self.test_results["response_quality"] = quality_score >= 80

    @classmethod
    def teardown_class(cls):
        """Print comprehensive Tilores data validation results."""
        print("\n" + "=" * 80)
        print("TILORES DATA VALIDATION RESULTS")
        print("=" * 80)

        # Test results summary
        passed_tests = sum(1 for result in cls.test_results.values() if result)
        total_tests = len(cls.test_results)

        print(f"\n📊 Test Results: {passed_tests}/{total_tests} passed")
        for test_name, passed in cls.test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {test_name}")

        # Accuracy scores
        if cls.data_accuracy_scores:
            print("\n🎯 Data Accuracy Scores:")
            total_accuracy = 0
            for metric_name, score in cls.data_accuracy_scores.items():
                print(f"   • {metric_name}: {score:.1f}%")
                total_accuracy += score

            if cls.data_accuracy_scores:
                avg_accuracy = total_accuracy / len(cls.data_accuracy_scores)
                print(f"   📈 Average Accuracy: {avg_accuracy:.1f}%")

        print(f"\n🎯 Overall Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if passed_tests == total_tests:
            print("🎉 ALL TILORES DATA VALIDATION TESTS PASSED!")
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed - review Tilores integration.")
