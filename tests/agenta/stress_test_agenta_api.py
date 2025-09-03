#!/usr / bin / env python3
"""
Agenta API Stress Testing Suite

Comprehensive stress tests for the uploaded test set and evaluation API.
Tests dataset integrity, API performance, and evaluation capabilities.
"""

import os
import json
import time
import requests
import asyncio
import aiohttp
import statistics
from datetime import datetime
from typing import Dict, List, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed


class AgentaAPIStressTester:
    """Comprehensive stress testing for Agenta API and test sets"""

    def __init__(self):
        """Initialize stress tester"""
        self.api_key = "NF5cGzQx.7325e5e4abd347302148eadc966f4e4991be7aad9f80636159368206f251afa2"
        self.base_url = "https://cloud.agenta.ai / api"
        self.testset_id = "01990cbe - 4cad - 7f42 - a9e3 - b39f68731284"  # Our uploaded test set
        self.testset_name = "tilores_x_complete_testset_20250902_192341"

        self.headers = {
            'Authorization': self.api_key,
            'Content - Type': 'application / json'
        }

        print("🧪 Agenta API Stress Tester Initialized")
        print(f"  - API Key: {'✅ Set' if self.api_key else '❌ Missing'}")
        print(f"  - Base URL: {self.base_url}")
        print(f"  - Test Set ID: {self.testset_id}")
        print(f"  - Test Set Name: {self.testset_name}")

    def test_api_connectivity(self) -> Dict:
        """Test basic API connectivity and authentication"""
        print("\n🔍 TESTING API CONNECTIVITY")
        print("=" * 40)

        results = {
            "connectivity": False,
            "authentication": False,
            "testset_access": False,
            "response_time": None,
            "error": None
        }

        try:
            start_time = time.time()

            # Test basic connectivity
            response = requests.get(f"{self.base_url}/testsets", headers=self.headers, timeout=10)
            response_time = time.time() - start_time
            results["response_time"] = round(response_time, 3)

            if response.status_code == 200:
                results["connectivity"] = True
                results["authentication"] = True

                # Check if our test set exists
                testsets = response.json()
                for testset in testsets:
                    if testset.get("_id") == self.testset_id:
                        results["testset_access"] = True
                        break

                print(f"✅ Connectivity: PASS ({response_time:.3f}s)")
                print("✅ Authentication: PASS")
                print(f"{'✅' if results['testset_access'] else '❌'} Test Set Access: {'PASS' if results['testset_access'] else 'FAIL'}")
                print(f"📊 Found {len(testsets)} total test sets")

            else:
                results["error"] = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ API Error: {results['error']}")

        except Exception as e:
            results["error"] = str(e)
            print(f"❌ Connection Error: {e}")

        return results

    def get_testset_details(self) -> Dict:
        """Get detailed information about our test set"""
        print("\n📊 ANALYZING TEST SET DETAILS")
        print("=" * 40)

        try:
            # Get specific test set details
            response = requests.get(f"{self.base_url}/testsets/{self.testset_id}", headers=self.headers, timeout=10)

            if response.status_code == 200:
                testset_data = response.json()

                print("✅ Test Set Retrieved Successfully")
                print(f"  - Name: {testset_data.get('name', 'Unknown')}")
                print(f"  - ID: {testset_data.get('_id', 'Unknown')}")
                print(f"  - Created: {testset_data.get('created_at', 'Unknown')}")

                # Analyze CSV data if available
                csvdata = testset_data.get('csvdata', [])
                if csvdata:
                    print(f"  - Test Cases: {len(csvdata)}")

                    # Analyze test case structure
                    if csvdata:
                        sample_case = csvdata[0]
                        print(f"  - Fields per case: {len(sample_case.keys())}")
                        print(f"  - Sample fields: {list(sample_case.keys())[:5]}...")

                return {
                    "success": True,
                    "data": testset_data,
                    "test_case_count": len(csvdata),
                    "fields": list(csvdata[0].keys()) if csvdata else []
                }
            else:
                print(f"❌ Failed to retrieve test set: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            print(f"❌ Error retrieving test set: {e}")
            return {"success": False, "error": str(e)}

    def stress_test_api_endpoints(self, num_requests: int = 50) -> Dict:
        """Stress test API endpoints with concurrent requests"""
        print(f"\n⚡ STRESS TESTING API ENDPOINTS ({num_requests} requests)")
        print("=" * 50)

        results = {
            "total_requests": num_requests,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "errors": [],
            "average_response_time": 0,
            "max_response_time": 0,
            "min_response_time": 0
        }

        def make_request(request_id: int) -> Tuple[int, float, str]:
            """Make a single API request"""
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/testsets", headers=self.headers, timeout=30)
                response_time = time.time() - start_time

                return request_id, response_time, None if response.status_code == 200 else f"HTTP {response.status_code}"
            except Exception as e:
                return request_id, 0, str(e)

        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]

            for future in as_completed(futures):
                request_id, response_time, error = future.result()

                if error:
                    results["failed_requests"] += 1
                    results["errors"].append(f"Request {request_id}: {error}")
                else:
                    results["successful_requests"] += 1
                    results["response_times"].append(response_time)

                # Progress indicator
                completed = results["successful_requests"] + results["failed_requests"]
                if completed % 10 == 0:
                    print(f"  Progress: {completed}/{num_requests} requests completed")

        # Calculate statistics
        if results["response_times"]:
            results["average_response_time"] = round(statistics.mean(results["response_times"]), 3)
            results["max_response_time"] = round(max(results["response_times"]), 3)
            results["min_response_time"] = round(min(results["response_times"]), 3)
            results["p95_response_time"] = round(statistics.quantiles(results["response_times"], n=20)[18], 3)

        # Print results
        print("\n📊 STRESS TEST RESULTS:")
        print(f"  ✅ Successful: {results['successful_requests']}/{num_requests}")
        print(f"  ❌ Failed: {results['failed_requests']}/{num_requests}")
        print(f"  📈 Success Rate: {(results['successful_requests']/num_requests)*100:.1f}%")

        if results["response_times"]:
            print(f"  ⏱️ Avg Response Time: {results['average_response_time']}s")
            print(f"  ⏱️ Min Response Time: {results['min_response_time']}s")
            print(f"  ⏱️ Max Response Time: {results['max_response_time']}s")
            print(f"  ⏱️ P95 Response Time: {results['p95_response_time']}s")

        if results["errors"]:
            print("  ⚠️ Sample Errors:")
            for error in results["errors"][:3]:
                print(f"    • {error}")

        return results

    def test_testset_data_integrity(self, testset_data: Dict) -> Dict:
        """Test the integrity and structure of test set data"""
        print("\n🔍 TESTING TEST SET DATA INTEGRITY")
        print("=" * 45)

        results = {
            "total_test_cases": 0,
            "valid_test_cases": 0,
            "invalid_test_cases": 0,
            "missing_fields": [],
            "field_coverage": {},
            "data_quality_issues": [],
            "integrity_score": 0
        }

        csvdata = testset_data.get("csvdata", [])
        results["total_test_cases"] = len(csvdata)

        if not csvdata:
            print("❌ No test case data found")
            return results

        # Define required fields
        required_fields = ["test_name", "customer_id", "query"]
        expected_fields = [
            "expected_customer_found", "expected_customer_name",
            "expected_has_credit_data", "expected_explanation"
        ]

        # Analyze each test case
        for i, test_case in enumerate(csvdata):
            is_valid = True

            # Check required fields
            for field in required_fields:
                if not test_case.get(field, "").strip():
                    results["data_quality_issues"].append(f"Test case {i + 1}: Missing {field}")
                    is_valid = False

            # Check field coverage
            for field, value in test_case.items():
                if field not in results["field_coverage"]:
                    results["field_coverage"][field] = {"total": 0, "populated": 0}

                results["field_coverage"][field]["total"] += 1
                if value and str(value).strip():
                    results["field_coverage"][field]["populated"] += 1

            if is_valid:
                results["valid_test_cases"] += 1
            else:
                results["invalid_test_cases"] += 1

        # Calculate integrity score
        if results["total_test_cases"] > 0:
            results["integrity_score"] = round((results["valid_test_cases"] / results["total_test_cases"]) * 100, 1)

        # Print results
        print("📊 DATA INTEGRITY RESULTS:")
        print(f"  📋 Total Test Cases: {results['total_test_cases']}")
        print(f"  ✅ Valid Cases: {results['valid_test_cases']}")
        print(f"  ❌ Invalid Cases: {results['invalid_test_cases']}")
        print(f"  🎯 Integrity Score: {results['integrity_score']}%")

        print("\n📈 FIELD COVERAGE:")
        for field, coverage in results["field_coverage"].items():
            percentage = (coverage["populated"] / coverage["total"]) * 100
            print(f"  • {field}: {coverage['populated']}/{coverage['total']} ({percentage:.1f}%)")

        if results["data_quality_issues"]:
            print("\n⚠️ DATA QUALITY ISSUES:")
            for issue in results["data_quality_issues"][:5]:
                print(f"  • {issue}")
            if len(results["data_quality_issues"]) > 5:
                print(f"  • ... and {len(results['data_quality_issues']) - 5} more issues")

        return results

    def simulate_evaluation_load(self, num_evaluations: int = 20) -> Dict:
        """Simulate evaluation load by creating mock evaluation requests"""
        print(f"\n🚀 SIMULATING EVALUATION LOAD ({num_evaluations} evaluations)")
        print("=" * 55)

        results = {
            "total_evaluations": num_evaluations,
            "successful_evaluations": 0,
            "failed_evaluations": 0,
            "evaluation_times": [],
            "errors": []
        }

        # Mock evaluation payload (simulating what would be sent to evaluate variants)
        mock_evaluation_data = {
            "testset_id": self.testset_id,
            "variant_id": "mock_variant",
            "evaluator_configs": ["accuracy", "relevance"]
        }

        def simulate_evaluation(eval_id: int) -> Tuple[int, float, str]:
            """Simulate a single evaluation request"""
            try:
                start_time = time.time()

                # Since we don't have actual evaluation endpoints, we'll simulate
                # by making requests to test the API under load
                time.sleep(0.1)  # Simulate evaluation processing time

                # Make a real API call to test load
                response = requests.get(f"{self.base_url}/testsets/{self.testset_id}",
                                      headers=self.headers, timeout=30)

                eval_time = time.time() - start_time

                return eval_id, eval_time, None if response.status_code == 200 else f"HTTP {response.status_code}"
            except Exception as e:
                return eval_id, 0, str(e)

        # Execute simulated evaluations
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(simulate_evaluation, i) for i in range(num_evaluations)]

            for future in as_completed(futures):
                eval_id, eval_time, error = future.result()

                if error:
                    results["failed_evaluations"] += 1
                    results["errors"].append(f"Evaluation {eval_id}: {error}")
                else:
                    results["successful_evaluations"] += 1
                    results["evaluation_times"].append(eval_time)

                # Progress indicator
                completed = results["successful_evaluations"] + results["failed_evaluations"]
                if completed % 5 == 0:
                    print(f"  Progress: {completed}/{num_evaluations} evaluations completed")

        # Calculate statistics
        if results["evaluation_times"]:
            avg_time = round(statistics.mean(results["evaluation_times"]), 3)
            max_time = round(max(results["evaluation_times"]), 3)
            min_time = round(min(results["evaluation_times"]), 3)
        else:
            avg_time = max_time = min_time = 0

        # Print results
        print("\n📊 EVALUATION LOAD TEST RESULTS:")
        print(f"  ✅ Successful: {results['successful_evaluations']}/{num_evaluations}")
        print(f"  ❌ Failed: {results['failed_evaluations']}/{num_evaluations}")
        print(f"  📈 Success Rate: {(results['successful_evaluations']/num_evaluations)*100:.1f}%")
        print(f"  ⏱️ Avg Evaluation Time: {avg_time}s")
        print(f"  ⏱️ Min Evaluation Time: {min_time}s")
        print(f"  ⏱️ Max Evaluation Time: {max_time}s")

        return results

    def run_comprehensive_stress_test(self) -> Dict:
        """Run comprehensive stress testing suite"""
        print("🧪 COMPREHENSIVE AGENTA API STRESS TEST")
        print("=" * 60)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        overall_results = {
            "start_time": datetime.now().isoformat(),
            "connectivity_test": {},
            "testset_details": {},
            "api_stress_test": {},
            "data_integrity_test": {},
            "evaluation_load_test": {},
            "overall_status": "UNKNOWN"
        }

        try:
            # 1. Test API Connectivity
            overall_results["connectivity_test"] = self.test_api_connectivity()

            if not overall_results["connectivity_test"]["connectivity"]:
                overall_results["overall_status"] = "FAILED - No API Connectivity"
                return overall_results

            # 2. Get Test Set Details
            overall_results["testset_details"] = self.get_testset_details()

            if not overall_results["testset_details"]["success"]:
                overall_results["overall_status"] = "FAILED - Cannot Access Test Set"
                return overall_results

            # 3. Stress Test API Endpoints
            overall_results["api_stress_test"] = self.stress_test_api_endpoints(50)

            # 4. Test Data Integrity
            overall_results["data_integrity_test"] = self.test_testset_data_integrity(
                overall_results["testset_details"]["data"]
            )

            # 5. Simulate Evaluation Load
            overall_results["evaluation_load_test"] = self.simulate_evaluation_load(20)

            # Determine overall status
            api_success_rate = (overall_results["api_stress_test"]["successful_requests"] /
                              overall_results["api_stress_test"]["total_requests"]) * 100

            integrity_score = overall_results["data_integrity_test"]["integrity_score"]

            eval_success_rate = (overall_results["evaluation_load_test"]["successful_evaluations"] /
                               overall_results["evaluation_load_test"]["total_evaluations"]) * 100

            if api_success_rate >= 95 and integrity_score >= 90 and eval_success_rate >= 95:
                overall_results["overall_status"] = "EXCELLENT"
            elif api_success_rate >= 90 and integrity_score >= 80 and eval_success_rate >= 90:
                overall_results["overall_status"] = "GOOD"
            elif api_success_rate >= 80 and integrity_score >= 70 and eval_success_rate >= 80:
                overall_results["overall_status"] = "ACCEPTABLE"
            else:
                overall_results["overall_status"] = "NEEDS_IMPROVEMENT"

        except Exception as e:
            overall_results["overall_status"] = f"FAILED - {str(e)}"

        overall_results["end_time"] = datetime.now().isoformat()

        # Print final summary
        self.print_final_summary(overall_results)

        return overall_results

    def print_final_summary(self, results: Dict):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE STRESS TEST SUMMARY")
        print("=" * 60)

        print(f"🕐 Test Duration: {results['start_time']} to {results['end_time']}")
        print(f"🎯 Overall Status: {results['overall_status']}")

        print("\n📊 KEY METRICS:")

        # API Performance
        api_results = results.get("api_stress_test", {})
        if api_results:
            success_rate = (api_results["successful_requests"] / api_results["total_requests"]) * 100
            print(f"  🌐 API Success Rate: {success_rate:.1f}%")
            print(f"  ⏱️ API Avg Response: {api_results.get('average_response_time', 0)}s")

        # Data Integrity
        integrity_results = results.get("data_integrity_test", {})
        if integrity_results:
            print(f"  📋 Data Integrity: {integrity_results.get('integrity_score', 0)}%")
            print(f"  📊 Test Cases: {integrity_results.get('valid_test_cases', 0)}/{integrity_results.get('total_test_cases', 0)}")

        # Evaluation Performance
        eval_results = results.get("evaluation_load_test", {})
        if eval_results:
            eval_success_rate = (eval_results["successful_evaluations"] / eval_results["total_evaluations"]) * 100
            print(f"  🚀 Evaluation Success: {eval_success_rate:.1f}%")

        print("\n🎉 STRESS TEST COMPLETE!")

        # Recommendations
        if results["overall_status"] in ["EXCELLENT", "GOOD"]:
            print("✅ Your Agenta setup is ready for production use!")
        elif results["overall_status"] == "ACCEPTABLE":
            print("⚠️ Your setup works but could be optimized")
        else:
            print("❌ Issues found that should be addressed before production")


def main():
    """Main stress test execution"""
    try:
        tester = AgentaAPIStressTester()
        results = tester.run_comprehensive_stress_test()

        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"tests / agenta / stress_test_results_{timestamp}.json"

        with open(results_file, 'w', encoding='utf - 8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n📁 Results saved to: {results_file}")

        return results["overall_status"] in ["EXCELLENT", "GOOD", "ACCEPTABLE"]

    except Exception as e:
        print(f"❌ Stress test failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


