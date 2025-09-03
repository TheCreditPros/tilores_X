#!/usr / bin / env python3
"""
Deploy Test Set to Agenta.ai using SDK

Uses the official Agenta SDK to deploy test cases as a test set for evaluation.
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any

try:
    import agenta as ag
    AGENTA_AVAILABLE = True
except ImportError:
    AGENTA_AVAILABLE = False
    print("❌ Agenta SDK not available")


class AgentaSDKTestSetDeployer:
    """Deploy test cases to Agenta.ai using official SDK"""

    def __init__(self):
        """Initialize deployer"""
        self.api_key = os.getenv("AGENTA_API_KEY")
        self.host = os.getenv("AGENTA_HOST", "https://cloud.agenta.ai")
        self.app_slug = os.getenv("AGENTA_APP_SLUG", "tilores - x")

        if not AGENTA_AVAILABLE:
            raise ImportError("Agenta SDK not available. Install with: pip install agenta")

        if not self.api_key:
            raise ValueError("AGENTA_API_KEY environment variable not set")

        # Set environment variables for Agenta SDK
        os.environ["AGENTA_API_KEY"] = self.api_key
        os.environ["AGENTA_HOST"] = self.host

        print("🚀 Agenta SDK Test Set Deployer Initialized")
        print(f"  - API Key: {'✅ Set' if self.api_key else '❌ Missing'}")
        print(f"  - Host: {self.host}")
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

    def convert_to_dataframe(self, test_cases: List[Dict]) -> pd.DataFrame:
        """Convert test cases to pandas DataFrame for Agenta"""
        rows = []

        for test_case in test_cases:
            inputs = test_case.get("inputs", {})
            expected = test_case.get("expected", {})

            # Create a flattened row
            row = {
                "test_name": test_case.get("id", "unknown"),
                "category": test_case.get("category", "unknown"),
                **inputs,  # Spread input fields
                "expected_output": json.dumps(expected, ensure_ascii=False),
                "expected_customer_found": expected.get("customer_found"),
                "expected_customer_name": expected.get("customer_name"),
                "expected_has_credit_data": expected.get("has_credit_data"),
                "expected_risk_level": expected.get("risk_level"),
                "expected_explanation": expected.get("explanation", "")[:200]  # Truncate for readability
            }

            rows.append(row)

        df = pd.DataFrame(rows)
        print(f"✅ Converted {len(df)} test cases to DataFrame")
        print(f"📊 Columns: {list(df.columns)}")
        return df

    def create_test_set_with_sdk(self, name: str, df: pd.DataFrame) -> bool:
        """Create test set using Agenta SDK"""
        try:
            print("🔄 Initializing Agenta SDK...")

            # Initialize Agenta
            ag.init()

            print(f"🔄 Creating test set '{name}'...")

            # Create test set using SDK
            # Note: The exact method may vary based on Agenta SDK version
            # This is a common pattern for test set creation

            # Method 1: Try using create_test_set if available
            try:
                result = ag.create_test_set(name=name, data=df)
                print("✅ Test set created using create_test_set method")
                return True
            except AttributeError:
                print("⚠️ create_test_set method not available, trying alternative...")

            # Method 2: Try using TestSet class if available
            try:
                test_set = ag.TestSet(name=name, data=df)
                test_set.save()
                print("✅ Test set created using TestSet class")
                return True
            except AttributeError:
                print("⚠️ TestSet class not available, trying alternative...")

            # Method 3: Manual approach using client
            try:
                client = ag.AgentaApi()
                result = client.create_testset(name=name, csvdata=df.to_dict('records'))
                print("✅ Test set created using AgentaApi client")
                return True
            except Exception as e:
                print(f"⚠️ AgentaApi method failed: {e}")

            print("❌ No suitable method found for creating test set")
            return False

        except Exception as e:
            print(f"❌ SDK test set creation failed: {e}")
            return False

    def save_as_csv(self, df: pd.DataFrame, filename: str = None) -> str:
        """Save DataFrame as CSV for manual upload"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tests / agenta / agenta_test_set_{timestamp}.csv"

        try:
            df.to_csv(filename, index=False)
            print(f"✅ Test set saved as CSV: {filename}")
            print("📁 You can manually upload this file to Agenta.ai dashboard")
            return filename
        except Exception as e:
            print(f"❌ Failed to save CSV: {e}")
            return None

    def validate_test_set_format(self, df: pd.DataFrame) -> bool:
        """Validate that the test set has the required format"""
        required_columns = ["test_name", "customer_id", "query"]

        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"⚠️ Missing required columns: {missing_columns}")
            return False

        print("✅ Test set format validation passed")
        return True

    def deploy_test_set(self, test_file: str, test_set_name: str = None) -> Dict:
        """Complete deployment process"""
        if not test_set_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_set_name = f"tilores_x_test_set_{timestamp}"

        print("\n🚀 DEPLOYING TEST SET TO AGENTA (SDK)")
        print("=" * 50)

        try:
            # Load test cases
            test_cases = self.load_test_cases(test_file)

            # Convert to DataFrame
            df = self.convert_to_dataframe(test_cases)

            # Validate format
            if not self.validate_test_set_format(df):
                return {"success": False, "error": "Invalid test set format"}

            # Save as CSV for manual upload (always do this as backup)
            csv_file = self.save_as_csv(df, f"tests / agenta / agenta_test_set_{test_set_name}.csv")

            # Try SDK deployment
            sdk_success = self.create_test_set_with_sdk(test_set_name, df)

            return {
                "success": True,
                "test_set_name": test_set_name,
                "test_cases_count": len(test_cases),
                "sdk_deployment": sdk_success,
                "csv_file": csv_file,
                "manual_upload_available": csv_file is not None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


def main():
    """Main deployment execution"""
    print("🚀 AGENTA TEST SET DEPLOYMENT (SDK)")
    print("=" * 50)

    try:
        # Initialize deployer
        deployer = AgentaSDKTestSetDeployer()

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
            print("✅ Deployment process completed!")
            print(f"  - Test Set Name: {result['test_set_name']}")
            print(f"  - Test Cases: {result['test_cases_count']}")
            print(f"  - SDK Deployment: {'✅' if result['sdk_deployment'] else '❌'}")
            print(f"  - CSV File: {result['csv_file']}")

            if result['sdk_deployment']:
                print("\n🎉 SUCCESS: Test set deployed via SDK!")
                print(f"🔗 Go to Agenta.ai dashboard to find: {result['test_set_name']}")
            else:
                print("\n📁 MANUAL UPLOAD REQUIRED:")
                print("  1. Go to Agenta.ai dashboard")
                print("  2. Navigate to Test Sets")
                print(f"  3. Upload CSV file: {result['csv_file']}")
                print(f"  4. Name it: {result['test_set_name']}")

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


