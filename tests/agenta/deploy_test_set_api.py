#!/usr / bin / env python3
"""
Deploy Test Set to Agenta.ai using Upload API

Uses the official Agenta API endpoint to upload CSV files directly.
Based on: https://docs.agenta.ai / evaluation / create - test - sets#creating - a-test - set - using - the - api
"""

import os
import requests
from datetime import datetime
from typing import Dict


class AgentaAPIUploader:
    """Upload test sets to Agenta.ai using the upload API"""

    def __init__(self):
        """Initialize uploader"""
        self.api_key = os.getenv("AGENTA_API_KEY")
        self.host = os.getenv("AGENTA_HOST", "https://cloud.agenta.ai")
        self.upload_url = f"{self.host}/api / testsets / upload"

        if not self.api_key:
            raise ValueError("AGENTA_API_KEY environment variable not set")

        print("🚀 Agenta API Uploader Initialized")
        print(f"  - API Key: {'✅ Set' if self.api_key else '❌ Missing'}")
        print(f"  - Host: {self.host}")
        print(f"  - Upload URL: {self.upload_url}")

    def upload_csv_testset(self, csv_file_path: str, testset_name: str) -> Dict:
        """Upload CSV file as test set using Agenta API"""

        if not os.path.exists(csv_file_path):
            return {"success": False, "error": f"File not found: {csv_file_path}"}

        try:
            print(f"🔄 Uploading test set '{testset_name}'...")
            print(f"📁 File: {csv_file_path}")

            # Prepare the upload
            with open(csv_file_path, 'rb') as file:
                files = {'file': file}
                data = {'testset_name': testset_name}
                headers = {'Authorization': f'Bearer {self.api_key}'}

                # Make the API call
                response = requests.post(
                    self.upload_url,
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=60
                )

                print(f"📡 Response Status: {response.status_code}")

                if response.status_code == 200 or response.status_code == 201:
                    result = response.json()
                    print("✅ Upload successful!")
                    print(f"📊 Response: {result}")

                    return {
                        "success": True,
                        "testset_name": testset_name,
                        "response": result,
                        "status_code": response.status_code
                    }
                else:
                    error_msg = f"Upload failed with status {response.status_code}"
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
            error_msg = f"Upload error: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

    def validate_upload(self, testset_name: str) -> bool:
        """Validate that the test set was uploaded successfully"""
        try:
            # Try to list test sets to verify upload
            list_url = f"{self.host}/api / testsets/"
            headers = {'Authorization': f'Bearer {self.api_key}'}

            response = requests.get(list_url, headers=headers, timeout=30)

            if response.status_code == 200:
                testsets = response.json()

                # Look for our uploaded test set
                for testset in testsets:
                    if testset.get('name') == testset_name:
                        print(f"✅ Validation successful: Test set '{testset_name}' found")
                        print(f"  - ID: {testset.get('id')}")
                        print(f"  - Created: {testset.get('created_at', 'Unknown')}")
                        return True

                print(f"⚠️ Test set '{testset_name}' not found in list")
                return False
            else:
                print(f"⚠️ Could not validate upload (status: {response.status_code})")
                return False

        except Exception as e:
            print(f"⚠️ Validation error: {e}")
            return False

    def deploy_test_set(self, csv_file_path: str, testset_name: str = None) -> Dict:
        """Complete deployment process using API upload"""

        if not testset_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            testset_name = f"tilores_x_test_set_{timestamp}"

        print("\n🚀 DEPLOYING TEST SET VIA API")
        print("=" * 50)

        # Upload the test set
        result = self.upload_csv_testset(csv_file_path, testset_name)

        if result["success"]:
            # Validate the upload
            validation_success = self.validate_upload(testset_name)
            result["validation_success"] = validation_success

        return result


def main():
    """Main deployment execution"""
    print("🚀 AGENTA TEST SET DEPLOYMENT (API UPLOAD)")
    print("=" * 60)

    try:
        # Initialize uploader
        uploader = AgentaAPIUploader()

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
            print("🎉 SUCCESS: Test set uploaded via API!")
            print(f"  - Test Set Name: {result['testset_name']}")
            print(f"  - Status Code: {result['status_code']}")
            print(f"  - Validation: {'✅' if result.get('validation_success') else '⚠️'}")

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
                print("  - Check your AGENTA_API_KEY")
                print("  - Ensure API key has upload permissions")
                print("  - Verify you have access to the app")
            elif result.get('status_code') == 400:
                print("\n💡 TROUBLESHOOTING:")
                print("  - Check CSV format")
                print("  - Ensure testset name is valid")
                print("  - Verify file is not corrupted")

            return False

    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


