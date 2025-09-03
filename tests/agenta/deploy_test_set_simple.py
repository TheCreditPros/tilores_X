#!/usr / bin / env python3
"""
Deploy Test Set to Agenta.ai (Simple Version)

Creates CSV file for manual upload to Agenta.ai dashboard.
No external dependencies required.
"""

import os
import json
import csv
from datetime import datetime
from typing import Dict, List, Any

try:
    import agenta as ag
    AGENTA_AVAILABLE = True
except ImportError:
    AGENTA_AVAILABLE = False


class SimpleAgentaDeployer:
    """Simple deployer that creates CSV files for manual upload"""

    def __init__(self):
        """Initialize deployer"""
        self.api_key = os.getenv("AGENTA_API_KEY")
        self.host = os.getenv("AGENTA_HOST", "https://cloud.agenta.ai")
        self.app_slug = os.getenv("AGENTA_APP_SLUG", "tilores - x")

        print("🚀 Simple Agenta Deployer Initialized")
        print(f"  - API Key: {'✅ Set' if self.api_key else '❌ Missing'}")
        print(f"  - Host: {self.host}")
        print(f"  - App Slug: {self.app_slug}")
        print(f"  - Agenta SDK: {'✅ Available' if AGENTA_AVAILABLE else '❌ Not Available'}")

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

    def create_csv_for_agenta(self, test_cases: List[Dict], filename: str) -> str:
        """Create CSV file formatted for Agenta.ai upload"""

        # Define CSV columns for Agenta
        columns = [
            'test_name',
            'category',
            'customer_id',
            'query',
            'expected_customer_found',
            'expected_customer_name',
            'expected_client_id',
            'expected_has_credit_data',
            'expected_has_transaction_data',
            'expected_risk_level',
            'expected_total_credit_reports',
            'expected_latest_credit_score',
            'expected_explanation'
        ]

        try:
            with open(filename, 'w', newline='', encoding='utf - 8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=columns)
                writer.writeheader()

                for test_case in test_cases:
                    inputs = test_case.get("inputs", {})
                    expected = test_case.get("expected", {})

                    # Create CSV row
                    row = {
                        'test_name': test_case.get('id', 'unknown'),
                        'category': test_case.get('category', 'unknown'),
                        'customer_id': inputs.get('customer_id', ''),
                        'query': inputs.get('query', ''),
                        'expected_customer_found': expected.get('customer_found', ''),
                        'expected_customer_name': expected.get('customer_name', ''),
                        'expected_client_id': expected.get('client_id', ''),
                        'expected_has_credit_data': expected.get('has_credit_data', ''),
                        'expected_has_transaction_data': expected.get('has_transaction_data', ''),
                        'expected_risk_level': expected.get('risk_level', ''),
                        'expected_total_credit_reports': expected.get('total_credit_reports', ''),
                        'expected_latest_credit_score': expected.get('latest_credit_score', ''),
                        'expected_explanation': expected.get('explanation', '')[:200]  # Truncate long explanations
                    }

                    writer.writerow(row)

            print(f"✅ CSV file created: {filename}")
            print(f"📊 Columns: {len(columns)}")
            print(f"📋 Rows: {len(test_cases)}")

            return filename

        except Exception as e:
            print(f"❌ Failed to create CSV: {e}")
            return None

    def try_sdk_upload(self, test_set_name: str, csv_filename: str) -> bool:
        """Try to upload using Agenta SDK if available"""
        if not AGENTA_AVAILABLE:
            print("⚠️ Agenta SDK not available for automatic upload")
            return False

        if not self.api_key:
            print("⚠️ No API key available for SDK upload")
            return False

        try:
            print("🔄 Attempting SDK upload...")

            # Set environment variables
            os.environ["AGENTA_API_KEY"] = self.api_key
            os.environ["AGENTA_HOST"] = self.host

            # Initialize Agenta
            ag.init()

            # Read CSV data
            csv_data = []
            with open(csv_filename, 'r', encoding='utf - 8') as f:
                reader = csv.DictReader(f)
                csv_data = list(reader)

            # Try different SDK methods
            try:
                # Method 1: Direct testset creation
                result = ag.create_testset(name=test_set_name, csvdata=csv_data)
                print("✅ Test set uploaded via SDK (create_testset)")
                return True
            except Exception as e1:
                print(f"⚠️ Method 1 failed: {e1}")

            try:
                # Method 2: Using client
                client = ag.get_client()
                result = client.create_testset(name=test_set_name, csvdata=csv_data)
                print("✅ Test set uploaded via SDK (client)")
                return True
            except Exception as e2:
                print(f"⚠️ Method 2 failed: {e2}")

            print("❌ All SDK upload methods failed")
            return False

        except Exception as e:
            print(f"❌ SDK upload error: {e}")
            return False

    def deploy_test_set(self, test_file: str, test_set_name: str = None) -> Dict:
        """Deploy test set (create CSV and optionally upload via SDK)"""
        if not test_set_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_set_name = f"tilores_x_test_set_{timestamp}"

        print(f"\n🚀 DEPLOYING TEST SET: {test_set_name}")
        print("=" * 60)

        try:
            # Load test cases
            test_cases = self.load_test_cases(test_file)

            # Create CSV file
            csv_filename = f"tests / agenta / agenta_testset_{test_set_name}.csv"
            csv_file = self.create_csv_for_agenta(test_cases, csv_filename)

            if not csv_file:
                return {"success": False, "error": "Failed to create CSV file"}

            # Try SDK upload
            sdk_success = self.try_sdk_upload(test_set_name, csv_file)

            return {
                "success": True,
                "test_set_name": test_set_name,
                "test_cases_count": len(test_cases),
                "csv_file": csv_file,
                "sdk_upload": sdk_success,
                "manual_upload_required": not sdk_success
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def print_manual_upload_instructions(self, result: Dict):
        """Print instructions for manual upload"""
        print("\n📋 MANUAL UPLOAD INSTRUCTIONS")
        print("=" * 40)
        print(f"1. 🌐 Go to: {self.host}")
        print(f"2. 📁 Navigate to your app: {self.app_slug}")
        print("3. 🔧 Go to 'Test Sets' section")
        print("4. ➕ Click 'Create New Test Set'")
        print(f"5. 📄 Upload CSV file: {result['csv_file']}")
        print(f"6. 🏷️ Name it: {result['test_set_name']}")
        print("7. ✅ Save and run evaluations")

        print("\n📊 Test Set Details:")
        print(f"  - Name: {result['test_set_name']}")
        print(f"  - Test Cases: {result['test_cases_count']}")
        print(f"  - CSV File: {result['csv_file']}")

    def validate_deployment(self, csv_file: str) -> bool:
        """Validate the CSV file was created correctly"""
        try:
            with open(csv_file, 'r', encoding='utf - 8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                print("✅ CSV Validation:")
                print("  - File exists: ✅")
                print(f"  - Headers: {len(reader.fieldnames)} columns")
                print(f"  - Data rows: {len(rows)}")
                print(f"  - Sample test: {rows[0]['test_name'] if rows else 'No data'}")

                return len(rows) > 0

        except Exception as e:
            print(f"❌ CSV validation failed: {e}")
            return False


def main():
    """Main deployment execution"""
    print("🚀 AGENTA TEST SET DEPLOYMENT (SIMPLE)")
    print("=" * 60)

    try:
        # Initialize deployer
        deployer = SimpleAgentaDeployer()

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

        # Deploy test set
        result = deployer.deploy_test_set(test_file)

        # Print results
        print("\n🎯 DEPLOYMENT RESULTS")
        print("=" * 30)

        if result["success"]:
            print("✅ Deployment completed!")

            # Validate CSV
            csv_valid = deployer.validate_deployment(result['csv_file'])

            if result['sdk_upload']:
                print("🎉 SUCCESS: Test set uploaded automatically via SDK!")
                print(f"🔗 Check Agenta.ai dashboard for: {result['test_set_name']}")
            else:
                print("📁 CSV file created - manual upload required")
                deployer.print_manual_upload_instructions(result)

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


