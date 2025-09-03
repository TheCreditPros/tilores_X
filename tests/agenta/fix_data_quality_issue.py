#!/usr / bin / env python3
"""
Fix Data Quality Issue in Test Set

Identifies and fixes the missing query in test case 17.
"""

import csv
import json
from datetime import datetime


def analyze_and_fix_csv():
    """Analyze CSV file and fix the missing query issue"""
    csv_file = "tests / agenta / agenta_testset_tilores_x_test_set_20250902_174026.csv"

    print("🔍 ANALYZING CSV DATA QUALITY")
    print("=" * 40)

    # Read and analyze
    rows = []
    with open(csv_file, 'r', encoding='utf - 8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            if not row.get('query', '').strip():
                print(f"❌ Found missing query in row {i}: {row.get('test_name', 'Unknown')}")

                # Fix based on test name and category
                test_name = row.get('test_name', '')
                category = row.get('category', '')
                customer_id = row.get('customer_id', '')

                if 'edge_case' in test_name and 'empty' in test_name:
                    row['query'] = "What can you tell me about this customer?"
                    print("✅ Fixed: Added generic query for edge case")
                elif customer_id:
                    row['query'] = f"Analyze the data for {customer_id}"
                    print("✅ Fixed: Added customer - specific query")
                else:
                    row['query'] = "Provide customer analysis"
                    print("✅ Fixed: Added default query")

            rows.append(row)

    print(f"\n📊 Analysis complete: {len(rows)} rows processed")

    # Create fixed version
    fixed_file = csv_file.replace('.csv', '_fixed.csv')

    with open(fixed_file, 'w', newline='', encoding='utf - 8') as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    print(f"✅ Fixed CSV saved to: {fixed_file}")
    return fixed_file


def upload_fixed_testset(csv_file):
    """Upload the fixed test set"""
    import subprocess
    import os

    # Convert CSV to JSON
    json_data = []
    with open(csv_file, 'r', encoding='utf - 8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            json_data.append(dict(row))

    # Create payload
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    testset_name = f"tilores_x_fixed_testset_{timestamp}"

    payload = {
        "name": testset_name,
        "csvdata": json_data
    }

    # Write to temp file
    temp_file = "temp_fixed_payload.json"
    with open(temp_file, 'w', encoding='utf - 8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    try:
        # Upload via curl
        api_key = "NF5cGzQx.7325e5e4abd347302148eadc966f4e4991be7aad9f80636159368206f251afa2"

        curl_command = [
            'curl', '-X', 'POST', 'https://cloud.agenta.ai / api / testsets',
            '-H', f'Authorization: {api_key}',
            '-H', 'Content - Type: application / json',
            '-d', f'@{temp_file}'
        ]

        print(f"\n🔄 Uploading fixed test set: {testset_name}")
        result = subprocess.run(curl_command, capture_output=True, text=True)

        if result.returncode == 0 and result.stdout:
            try:
                response_data = json.loads(result.stdout)
                if 'id' in response_data:
                    print("✅ SUCCESS: Fixed test set uploaded!")
                    print(f"  - ID: {response_data['id']}")
                    print(f"  - Name: {response_data['name']}")
                    return response_data['id']
            except json.JSONDecodeError:
                pass

        print(f"❌ Upload failed: {result.stdout}")
        return None

    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)


def main():
    """Main execution"""
    print("🔧 FIXING DATA QUALITY ISSUES")
    print("=" * 50)

    # Fix CSV
    fixed_csv = analyze_and_fix_csv()

    # Upload fixed version
    testset_id = upload_fixed_testset(fixed_csv)

    if testset_id:
        print("\n🎉 FIXED TEST SET DEPLOYED!")
        print(f"🆔 New Test Set ID: {testset_id}")
        print("🔗 Go to Agenta dashboard to use the fixed version")
        return True
    else:
        print("\n❌ Failed to upload fixed version")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


