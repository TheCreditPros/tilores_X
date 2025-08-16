#!/usr/bin/env python3
"""
Simple data gatherer that bypasses LangSmith conflicts
Uses direct API calls to get real customer data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import requests
import json


def get_customer_data_via_api():
    """Get customer data using direct API calls to our production endpoint"""

    # The correct test email addresses
    test_emails = [
        "blessedwina@aol.com",
        "lelisguardado@sbcglobal.net",
        "migdaliareyes53@gmail.com"
    ]

    api_url = "https://tiloresx-production.up.railway.app/v1/chat/completions"

    real_customers = []

    print("🔍 Gathering real customer data via production API...")

    for email in test_emails:
        print(f"\n📧 Processing: {email}")

        try:
            # Make direct API call
            response = requests.post(
                api_url,
                headers={"Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Find customer with email {email} and get their complete profile including name, phone, client ID, and credit score"
                        }
                    ],
                    "max_tokens": 500
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"✅ Response received: {len(content)} characters")

                # Extract customer info
                customer_data = extract_customer_info(content, email)
                real_customers.append(customer_data)

            else:
                print(f"❌ API error: {response.status_code}")
                real_customers.append({
                    "email": email,
                    "name": "API Error",
                    "error": f"HTTP {response.status_code}",
                    "status": "failed"
                })

        except Exception as e:
            print(f"❌ Error processing {email}: {e}")
            real_customers.append({
                "email": email,
                "name": "Request Failed",
                "error": str(e),
                "status": "failed"
            })

    return real_customers


def extract_customer_info(response_text, email):
    """Extract structured customer information from LLM response"""

    response = str(response_text)

    customer_data = {
        "email": email,
        "raw_response": response,
        "status": "success"
    }

    # Extract name using common patterns
    import re

    # Look for name patterns
    name_patterns = [
        r"(?:Name|Customer):\s*([A-Z][a-z]+\s+[A-Z][a-z]+)",
        r"([A-Z][a-z]+\s+[A-Z][a-z]+)\s+found",
        r"Customer\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
        r"FIRST_NAME.*?([A-Z][a-z]+).*?LAST_NAME.*?([A-Z][a-z]+)",
        r"Name:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)",
    ]

    for pattern in name_patterns:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2:
                customer_data["name"] = f"{match.group(1)} {match.group(2)}"
            else:
                customer_data["name"] = match.group(1)
            break

    if "name" not in customer_data:
        customer_data["name"] = "Unknown Customer"

    # Extract client ID
    client_id_patterns = [
        r"(?:Client ID|CLIENT_ID):\s*(\d+)",
        r"ID:\s*(\d{6,8})",
        r"\b(\d{7,8})\b"  # 7-8 digit numbers
    ]

    for pattern in client_id_patterns:
        match = re.search(pattern, response)
        if match:
            customer_data["client_id"] = match.group(1)
            break

    # Extract phone
    phone_patterns = [
        r"(?:Phone|PHONE_EXTERNAL):\s*([\d\-\(\)\s]+)",
        r"\b(\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4})\b"
    ]

    for pattern in phone_patterns:
        match = re.search(pattern, response)
        if match:
            customer_data["phone"] = match.group(1).strip()
            break

    # Extract credit score
    credit_patterns = [
        r"(?:Credit Score|STARTING_CREDIT_SCORE):\s*(\d{3})",
        r"Score:\s*(\d{3})",
        r"\b(\d{3})\b.*(?:credit|score)"
    ]

    for pattern in credit_patterns:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            if 300 <= score <= 850:  # Valid credit score range
                customer_data["credit_score"] = score
                customer_data["has_credit_report"] = True
                break

    # Check for credit data indicators
    credit_indicators = ["credit", "score", "transunion", "report", "utilization"]
    has_credit_data = any(indicator.lower() in response.lower() for indicator in credit_indicators)

    if "has_credit_report" not in customer_data:
        customer_data["has_credit_report"] = has_credit_data

    return customer_data


def main():
    """Main function"""
    print("🚀 Starting Simple Customer Data Gathering")
    print("=" * 50)

    # Gather the data
    customers = get_customer_data_via_api()

    # Save the results
    output_file = "tests/speed_experiments/real_customer_data.json"

    with open(output_file, 'w') as f:
        json.dump(customers, f, indent=2)

    print(f"\n💾 Customer data saved to: {output_file}")

    # Print summary
    print("\n📊 CUSTOMER DATA SUMMARY")
    print("=" * 50)

    for i, customer in enumerate(customers, 1):
        print(f"\n{i}. {customer['email']}")
        print(f"   Name: {customer.get('name', 'Unknown')}")
        print(f"   Client ID: {customer.get('client_id', 'Not found')}")
        print(f"   Phone: {customer.get('phone', 'Not found')}")
        print(f"   Credit Score: {customer.get('credit_score', 'Not found')}")
        print(f"   Has Credit Data: {customer.get('has_credit_report', False)}")
        print(f"   Status: {customer.get('status', 'unknown')}")

    print(f"\n✅ Successfully gathered data for {len(customers)} customers")
    return customers


if __name__ == "__main__":
    main()
