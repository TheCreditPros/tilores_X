#!/usr / bin / env python3
"""
Verify Fixed Test Set

Quick verification that the fixed test set has 100% data integrity.
"""

import requests
import json


def verify_fixed_testset():
    """Verify the fixed test set has perfect data integrity"""
    api_key = "NF5cGzQx.7325e5e4abd347302148eadc966f4e4991be7aad9f80636159368206f251afa2"
    testset_id = "01990cd8 - 871c - 7af3 - 91f1 - e3d084d4c330"  # Fixed test set ID

    headers = {
        'Authorization': api_key,
        'Content - Type': 'application / json'
    }

    print("🔍 VERIFYING FIXED TEST SET")
    print("=" * 40)

    try:
        # Get test set data
        response = requests.get(f"https://cloud.agenta.ai / api / testsets/{testset_id}",
                              headers=headers, timeout=10)

        if response.status_code == 200:
            testset_data = response.json()
            csvdata = testset_data.get('csvdata', [])

            print(f"✅ Test Set Retrieved: {testset_data.get('name')}")
            print(f"📊 Test Cases: {len(csvdata)}")

            # Check data integrity
            required_fields = ["test_name", "customer_id", "query"]
            valid_cases = 0
            issues = []

            for i, test_case in enumerate(csvdata, 1):
                is_valid = True
                for field in required_fields:
                    if not test_case.get(field, "").strip():
                        issues.append(f"Test case {i}: Missing {field}")
                        is_valid = False

                if is_valid:
                    valid_cases += 1

            integrity_score = (valid_cases / len(csvdata)) * 100 if csvdata else 0

            print(f"📈 Data Integrity: {integrity_score:.1f}%")
            print(f"✅ Valid Cases: {valid_cases}/{len(csvdata)}")

            if issues:
                print("❌ Remaining Issues:")
                for issue in issues:
                    print(f"  • {issue}")
            else:
                print("🎉 Perfect Data Integrity - No Issues Found!")

            return integrity_score == 100.0

        else:
            print(f"❌ Failed to retrieve test set: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False


def main():
    """Main verification"""
    success = verify_fixed_testset()

    if success:
        print("\n✅ VERIFICATION COMPLETE - TEST SET IS PERFECT!")
    else:
        print("\n❌ VERIFICATION FAILED - ISSUES REMAIN")

    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


