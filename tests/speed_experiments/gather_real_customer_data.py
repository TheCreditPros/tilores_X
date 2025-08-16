#!/usr/bin/env python3
"""
Gather real customer data for accurate speed experiments
Uses the correct test email addresses to build golden records
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core_app import initialize_engine, run_chain
import json


def gather_customer_data():
    """Gather real customer data using the correct test emails"""

    # Initialize the engine
    initialize_engine()

    # The correct test email addresses
    test_emails = ["blessedwina@aol.com", "lelisguardado@sbcglobal.net", "migdaliareyes53@gmail.com"]

    real_customers = []

    print("🔍 Gathering real customer data from Tilores...")

    for email in test_emails:
        print(f"\n📧 Processing: {email}")

        try:
            # Use our production-ready chain to get customer data
            query = f"Find customer with email {email} and get their complete profile including name, phone, client ID, and any available credit information"

            # Use the fastest model for data gathering
            response = run_chain(messages=query, model="llama-3.3-70b-versatile", stream=False)

            print(f"✅ Response received: {len(str(response))} characters")

            # Extract structured data from response
            customer_data = extract_customer_info(response, email)
            real_customers.append(customer_data)

        except Exception as e:
            print(f"❌ Error processing {email}: {e}")
            # Add placeholder data so we can continue
            real_customers.append({"email": email, "name": "Unknown Customer", "error": str(e), "status": "failed"})

    return real_customers


def extract_customer_info(response_text, email):
    """Extract structured customer information from LLM response"""

    # Convert response to string if needed
    response = str(response_text)

    customer_data = {"email": email, "raw_response": response, "status": "success"}

    # Extract name using common patterns
    import re

    # Look for name patterns
    name_patterns = [
        r"(?:Name|Customer):\s*([A-Z][a-z]+\s+[A-Z][a-z]+)",
        r"([A-Z][a-z]+\s+[A-Z][a-z]+)\s+found",
        r"Customer\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
        r"FIRST_NAME.*?([A-Z][a-z]+).*?LAST_NAME.*?([A-Z][a-z]+)",
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
        r"\b(\d{7,8})\b",  # 7-8 digit numbers
    ]

    for pattern in client_id_patterns:
        match = re.search(pattern, response)
        if match:
            customer_data["client_id"] = match.group(1)
            break

    # Extract phone
    phone_patterns = [r"(?:Phone|PHONE_EXTERNAL):\s*([\d\-\(\)\s]+)", r"\b(\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4})\b"]

    for pattern in phone_patterns:
        match = re.search(pattern, response)
        if match:
            customer_data["phone"] = match.group(1).strip()
            break

    # Extract credit score
    credit_patterns = [
        r"(?:Credit Score|STARTING_CREDIT_SCORE):\s*(\d{3})",
        r"Score:\s*(\d{3})",
        r"\b(\d{3})\b.*(?:credit|score)",
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


def save_customer_data(customers):
    """Save the gathered customer data to a file"""

    output_file = "tests/speed_experiments/real_customer_data.json"

    with open(output_file, "w") as f:
        json.dump(customers, f, indent=2)

    print(f"\n💾 Customer data saved to: {output_file}")

    # Also create a Python module for easy import
    python_file = "tests/speed_experiments/real_test_data.py"

    with open(python_file, "w") as f:
        f.write("#!/usr/bin/env python3\n")
        f.write('"""\n')
        f.write("Real customer test data gathered from Tilores\n")
        f.write("Generated automatically - do not edit manually\n")
        f.write('"""\n\n')
        f.write("REAL_TEST_CUSTOMERS = ")
        f.write(json.dumps(customers, indent=4))
        f.write("\n\n")
        f.write("def get_real_customers():\n")
        f.write('    """Get the real customer test data"""\n')
        f.write("    return REAL_TEST_CUSTOMERS\n")

    print(f"💾 Python module saved to: {python_file}")


def main():
    """Main function"""
    print("🚀 Starting Real Customer Data Gathering")
    print("=" * 50)

    # Gather the data
    customers = gather_customer_data()

    # Save the results
    save_customer_data(customers)

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
