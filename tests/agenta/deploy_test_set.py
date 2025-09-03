#!/usr / bin / env python3
"""
Deploy Test Set to Agenta.ai

Deploys the generated test cases to Agenta.ai as a test set for evaluation.
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Any


class AgentaTestSetDeployer:
    """Deploy test cases to Agenta.ai"""

    def __init__(self):
        """Initialize deployer"""
        self.api_key = os.getenv("AGENTA_API_KEY")
        self.base_url = os.getenv("AGENTA_HOST", "https://cloud.agenta.ai")
        self.app_slug = os.getenv("AGENTA_APP_SLUG", "tilores - x")

        if not self.api_key:
            raise ValueError("AGENTA_API_KEY environment variable not set")

        print("🚀 Agenta Test Set Deployer Initialized")
        print(f"  - API Key: {'✅ Set' if self.api_key else '❌ Missing'}")
        print(f"  - Host: {self.base_url}")
        print(f"  - App Slug: {self.app_slug}")

    def load_test_cases(self, test_file: str) -> List[Dict]:
        """Load test cases from JSONL file"""
        test_cases = []

        try:
            with open(test_file, 'r', encoding='utf - 8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            test_case = json.loads(line)
                            test_cases.append(test_case)
                        except json.JSONDecodeError as e:
                            print(f"⚠️ Error parsing line {line_num}: {e}")

            print(f"✅ Loaded {len(test_cases)} test cases from {test_file}")
            return test_cases

        except FileNotFoundError:
            raise FileNotFoundError(f"Test file not found: {test_file}")
        except Exception as e:
            raise Exception(f"Error loading test cases: {e}")

    def convert_to_agenta_format(self, test_cases: List[Dict]) -> List[Dict]:
        """Convert test cases to Agenta.ai format"""
        agenta_test_cases = []

        for test_case in test_cases:
            # Convert to Agenta format
            agenta_case = {
                "name": test_case.get("id", "unknown"),
                "inputs": test_case.get("inputs", {}),
                "expected_output": test_case.get("expected", {}),
                "metadata": {
                    "category": test_case.get("category", "unknown"),
                    "description": f"Test case for {test_case.get('category', 'unknown')} functionality"
                }
            }

            agenta_test_cases.append(agenta_case)

        print(f"✅ Converted {len(agenta_test_cases)} test cases to Agenta format")
        return agenta_test_cases

    def create_test_set(self, name: str, test_cases: List[Dict]) -> Dict:
        """Create a test set in Agenta.ai"""
        url = f"{self.base_url}/api / testsets/"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content - Type": "application / json"
        }

        payload = {
            "name": name,
            "app_name": self.app_slug,
            "csvdata": self._convert_to_csv_format(test_cases)
        }

        try:
            print(f"🔄 Creating test set '{name}' in Agenta...")
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 201:
                result = response.json()
                print("✅ Test set created successfully")
                print(f"  - Test Set ID: {result.get('id')}")
                print(f"  - Name: {result.get('name')}")
                return result
            else:
                print(f"❌ Failed to create test set: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None

    def _convert_to_csv_format(self, test_cases: List[Dict]) -> List[Dict]:
        """Convert test cases to CSV - like format for Agenta"""
        csv_data = []

        for test_case in test_cases:
            inputs = test_case.get("inputs", {})
            expected = test_case.get("expected", {})

            # Flatten the data for CSV format
            row = {
                "test_name": test_case.get("name", "unknown"),
                **inputs,
                "expected_output": json.dumps(expected),
                "category": test_case.get("metadata", {}).get("category", "unknown")
            }

            csv_data.append(row)

        return csv_data

    def list_test_sets(self) -> List[Dict]:
        """List existing test sets"""
        url = f"{self.base_url}/api / testsets/"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content - Type": "application / json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                test_sets = response.json()
                print(f"✅ Found {len(test_sets)} existing test sets")
                return test_sets
            else:
                print(f"❌ Failed to list test sets: {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return []

    def validate_deployment(self, test_set_id: str) -> bool:
        """Validate that the test set was deployed correctly"""
        url = f"{self.base_url}/api / testsets/{test_set_id}/"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content - Type": "application / json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                test_set = response.json()
                print("✅ Test set validation successful")
                print(f"  - ID: {test_set.get('id')}")
                print(f"  - Name: {test_set.get('name')}")
                print(f"  - Test Cases: {len(test_set.get('csvdata', []))}")
                return True
            else:
                print(f"❌ Validation failed: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Validation request failed: {e}")
            return False

    def deploy_test_set(self, test_file: str, test_set_name: str = None) -> Dict:
        """Complete deployment process"""
        if not test_set_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_set_name = f"tilores_x_test_set_{timestamp}"

        print("\n🚀 DEPLOYING TEST SET TO AGENTA")
        print("=" * 50)

        try:
            # Load test cases
            test_cases = self.load_test_cases(test_file)

            # Convert to Agenta format
            agenta_cases = self.convert_to_agenta_format(test_cases)

            # Create test set
            result = self.create_test_set(test_set_name, agenta_cases)

            if result:
                # Validate deployment
                test_set_id = result.get('id')
                if test_set_id:
                    validation_success = self.validate_deployment(test_set_id)

                    return {
                        "success": True,
                        "test_set_id": test_set_id,
                        "test_set_name": test_set_name,
                        "test_cases_count": len(test_cases),
                        "validation_success": validation_success
                    }

            return {"success": False, "error": "Failed to create test set"}

        except Exception as e:
            return {"success": False, "error": str(e)}


def main():
    """Main deployment execution"""
    print("🚀 AGENTA TEST SET DEPLOYMENT")
    print("=" * 50)

    try:
        # Initialize deployer
        deployer = AgentaTestSetDeployer()

        # Find the most recent test cases file
        import glob
        test_files = glob.glob("tests / agenta / test_cases_*.jsonl")

        if not test_files:
            print("❌ No test case files found")
            print("Run: python tests / agenta / test_case_generator.py")
            return False

        # Use the most recent file
        test_file = max(test_files, key=os.path.getmtime)
        print(f"📁 Using test file: {test_file}")

        # List existing test sets
        print("\n📋 Existing test sets:")
        existing_sets = deployer.list_test_sets()
        for i, test_set in enumerate(existing_sets[:5], 1):
            print(f"  {i}. {test_set.get('name', 'Unknown')} (ID: {test_set.get('id')})")

        # Deploy new test set
        result = deployer.deploy_test_set(test_file)

        # Print results
        print("\n🎯 DEPLOYMENT RESULTS")
        print("=" * 30)

        if result["success"]:
            print("✅ Deployment successful!")
            print(f"  - Test Set ID: {result['test_set_id']}")
            print(f"  - Test Set Name: {result['test_set_name']}")
            print(f"  - Test Cases: {result['test_cases_count']}")
            print(f"  - Validation: {'✅' if result['validation_success'] else '❌'}")

            print("\n🔗 Next steps:")
            print("  1. Go to Agenta.ai dashboard")
            print(f"  2. Find test set: {result['test_set_name']}")
            print("  3. Run evaluations against your variants")

            return True
        else:
            print(f"❌ Deployment failed: {result['error']}")
            return False

    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


