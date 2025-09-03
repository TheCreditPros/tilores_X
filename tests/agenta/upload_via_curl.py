#!/usr / bin / env python3
"""
Upload Test Set via Curl (Working Method)

Uses the curl method that we confirmed works for uploading our test set.
"""

import csv
import json
import subprocess
import os
from datetime import datetime


def csv_to_json_data(csv_file: str):
    """Convert CSV to JSON data for API"""
    json_data = []

    with open(csv_file, 'r', encoding='utf - 8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            json_data.append(dict(row))

    return json_data


def upload_via_curl(testset_name: str, csv_data: list):
    """Upload test set using curl (the method that works)"""

    api_key = "NF5cGzQx.7325e5e4abd347302148eadc966f4e4991be7aad9f80636159368206f251afa2"

    # Create the JSON payload
    payload = {
        "name": testset_name,
        "csvdata": csv_data
    }

    # Write payload to temporary file
    temp_file = "temp_payload.json"
    with open(temp_file, 'w', encoding='utf - 8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    try:
        # Use curl to upload
        curl_command = [
            'curl', '-X', 'POST', 'https://cloud.agenta.ai / api / testsets',
            '-H', f'Authorization: {api_key}',
            '-H', 'Content - Type: application / json',
            '-d', f'@{temp_file}'
        ]

        print(f"🔄 Uploading test set '{testset_name}'...")
        print(f"📊 Test cases: {len(csv_data)}")

        result = subprocess.run(curl_command, capture_output=True, text=True)

        print(f"📡 Response Status: {result.returncode}")
        print(f"📤 Response: {result.stdout}")

        if result.stderr:
            print(f"⚠️ Stderr: {result.stderr}")

        # Clean up temp file
        os.remove(temp_file)

        if result.returncode == 0 and result.stdout:
            try:
                response_data = json.loads(result.stdout)
                if 'id' in response_data:
                    print("✅ SUCCESS: Test set uploaded!")
                    print(f"  - ID: {response_data['id']}")
                    print(f"  - Name: {response_data['name']}")
                    print(f"  - Created: {response_data.get('created_at', 'Unknown')}")
                    return True
            except json.JSONDecodeError:
                pass

        return False

    except Exception as e:
        print(f"❌ Upload error: {e}")
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False


def main():
    """Main upload execution"""
    print("🚀 AGENTA TEST SET UPLOAD (CURL METHOD)")
    print("=" * 50)

    # Find CSV file
    csv_file = "tests / agenta / agenta_testset_tilores_x_test_set_20250902_174026.csv"

    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return False

    # Convert CSV to JSON
    print(f"📁 Reading CSV: {csv_file}")
    csv_data = csv_to_json_data(csv_file)
    print(f"✅ Converted {len(csv_data)} test cases")

    # Generate testset name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    testset_name = f"tilores_x_complete_testset_{timestamp}"

    # Upload
    success = upload_via_curl(testset_name, csv_data)

    if success:
        print("\n🎉 DEPLOYMENT COMPLETE!")
        print("🔗 Go to: https://cloud.agenta.ai")
        print(f"📋 Find testset: {testset_name}")
        print("🚀 Run evaluations against your variants")
        return True
    else:
        print("\n❌ Upload failed")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


