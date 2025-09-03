#!/usr / bin / env python3
"""
Deploy Test Set to Agenta.ai using JSON API

Uses the JSON API method from Agenta documentation.
Based on: https://docs.agenta.ai / evaluation / create - test - sets#creating - a-test - set - using - the - api
"""

import os
import json
import csv
import requests
from datetime import datetime
from typing import Dict, List


class AgentaJSONAPIUploader:
    """Upload test sets to Agenta.ai using JSON API method"""

    def __init__(self):
        """Initialize uploader"""
        self.api_key = os.getenv("AGENTA_API_KEY")
        self.host = os.getenv("AGENTA_HOST", "https://cloud.agenta.ai")
        self.testsets_url = f"{self.host}/api / testsets"

        if not self.api_key:
            raise ValueError("AGENTA_API_KEY environment variable not set")

        print("🚀 Agenta JSON API Uploader Initialized")
        print(f"  - API Key: {'✅ Set' if self.api_key else '❌ Missing'}")
        print(f"  - Host: {self.host}")
        print(f"  - API URL: {self.testsets_url}")

    def csv_to_json_data(self, csv_file_path: str) -> List[Dict]:
        """Convert CSV file to JSON data format for API"""
        json_data = []

        try:
            with open(csv_file_path, 'r', encoding='utf - 8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    json_data.append(dict(row))

            print(f"✅ Converted CSV to JSON: {len(json_data)} rows")
            return json_data

        except Exception as e:
            print(f"❌ CSV conversion error: {e}")
            return []

    def create_testset_json_api(self, testset_name: str, csv_data: List[Dict]) -> Dict:
        """Create test set using JSON API method"""

        try:
            print(f"🔄 Creating test set '{testset_name}' via JSON API...")

            # Prepare the request payload (as shown in documentation)
            payload = {
                "name": testset_name,
                "csvdata": csv_data
            }

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content - Type': 'application / json'
            }

            print(f"📊 Payload size: {len(csv_data)} test cases")
            print(f"📡 Making POST request to: {self.testsets_url}")

            # Make the API call
            response = requests.post(
                self.testsets_url,
                json=payload,
                headers=headers,
                timeout=60
            )

            print(f"📡 Response Status: {response.status_code}")

            if response.status_code in [200, 201]:
                try:
                    result = response.json()
                    print("✅ Test set created successfully!")
                    print(f"📊 Response: {result}")

                    return {
                        "success": True,
                        "testset_name": testset_name,
                        "response": result,
                        "status_code": response.status_code,
                        "testset_id": result.get('id') if isinstance(result, dict) else None
                    }
                except json.JSONDecodeError:
                    # Sometimes successful responses might not be JSON
                    print("✅ Test set created (non - JSON response)")
                    return {
                        "success": True,
                        "testset_name": testset_name,
                        "response": response.text,
                        "status_code": response.status_code
                    }
            else:
                error_msg = f"API call failed with status {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f": {error_detail}"
                except Exception:
                    error_msg += f": {response.text}"

                print(f"❌ {error_msg}")

                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code,
                    "response_text": response.text
                }

        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        except Exception as e:
            error_msg = f"API call error: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

    def test_api_connection(self) -> bool:
        """Test API connection and authentication"""
        try:
            print("🔍 Testing API connection...")

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content - Type': 'application / json'
            }

            # Try to list existing test sets
            response = requests.get(self.testsets_url, headers=headers, timeout=30)

            print(f"📡 Connection test status: {response.status_code}")

            if response.status_code == 200:
                print("✅ API connection successful")
                try:
                    testsets = response.json()
                    print(f"📋 Found {len(testsets)} existing test sets")
                    return True
                except Exception:
                    print("✅ API connection successful (non - JSON response)")
                    return True
            elif response.status_code == 401:
                print("❌ Authentication failed - check API key")
                return False
            elif response.status_code == 403:
                print("❌ Access forbidden - check permissions")
                return False
            else:
                print(f"⚠️ Unexpected response: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

    def deploy_test_set(self, csv_file_path: str, testset_name: str = None) -> Dict:
        """Complete deployment process using JSON API"""

        if not testset_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            testset_name = f"tilores_x_test_set_{timestamp}"

        print("\n🚀 DEPLOYING TEST SET VIA JSON API")
        print("=" * 50)

        # Test API connection first
        if not self.test_api_connection():
            return {"success": False, "error": "API connection test failed"}

        # Convert CSV to JSON data
        csv_data = self.csv_to_json_data(csv_file_path)
        if not csv_data:
            return {"success": False, "error": "Failed to convert CSV to JSON"}

        # Create the test set
        result = self.create_testset_json_api(testset_name, csv_data)

        return result


def main():
    """Main deployment execution"""
    print("🚀 AGENTA TEST SET DEPLOYMENT (JSON API)")
    print("=" * 60)

    try:
        # Initialize uploader
        uploader = AgentaJSONAPIUploader()

        # Find the most recent CSV file
        import glob
        csv_files = glob.glob("tests / agenta / agenta_testset_*.csv")

        if not csv_files:
            print("❌ No Agenta test set CSV files found")
            print("Run: python tests / agenta / deploy_test_set_simple.py")
            return False

        # Use the most recent file
        csv_file = max(csv_files, key=os.path.getmtime)
        print(f"📁 Using CSV file: {csv_file}")

        # Generate test set name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        testset_name = f"tilores_x_test_set_{timestamp}"

        # Deploy test set
        result = uploader.deploy_test_set(csv_file, testset_name)

        # Print results
        print("\n🎯 DEPLOYMENT RESULTS")
        print("=" * 30)

        if result["success"]:
            print("🎉 SUCCESS: Test set created via JSON API!")
            print(f"  - Test Set Name: {result['testset_name']}")
            print(f"  - Status Code: {result['status_code']}")

            if result.get('testset_id'):
                print(f"  - Test Set ID: {result['testset_id']}")

            print("\n🔗 NEXT STEPS:")
            print("1. Go to: https://cloud.agenta.ai")
            print("2. Navigate to your app's Test Sets")
            print(f"3. Find: {result['testset_name']}")
            print("4. Run evaluations against your variants")

            return True
        else:
            print(f"❌ Deployment failed: {result['error']}")

            if result.get('status_code') == 401:
                print("\n💡 TROUBLESHOOTING:")
                print("  - API Key format might be incorrect")
                print("  - Try different authentication header format")
                print("  - Check if API key is active and has permissions")
            elif result.get('status_code') == 400:
                print("\n💡 TROUBLESHOOTING:")
                print("  - Check JSON payload format")
                print("  - Verify testset name is valid")
                print("  - Ensure CSV data is properly formatted")

            return False

    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


