#!/usr/bin/env python3
"""
Test Working Credit Function
Test the get_customer_credit_report function to access multi-bureau data
"""

from dotenv import load_dotenv
load_dotenv()

def test_working_credit_function():
    """Test the working get_customer_credit_report function"""

    print("🔍 TEST WORKING CREDIT FUNCTION")
    print("=" * 50)

    try:
        from core_app import initialize_engine
        initialize_engine()
        from core_app import engine
        print("✅ Core app engine initialized")
    except Exception as e:
        print(f"❌ Core app initialization failed: {e}")
        return

    # Test the get_customer_credit_report function with email
    print("\n🔍 TEST 1: GET CUSTOMER CREDIT REPORT BY EMAIL")
    print("-" * 50)

    try:
        # Use the working function with email parameter
        credit_report = engine.get_customer_credit_report(email="e.j.price1986@gmail.com")

        print("📊 CREDIT REPORT RESULT:")
        print(f"   Report length: {len(credit_report)} characters")
        print(f"   Report preview: {credit_report[:200]}...")

        # Check for multi-bureau indicators
        multi_bureau_indicators = [
            "TransUnion", "Experian", "Equifax",
            "TU", "EXP", "EFX",
            "bureau", "bureaus", "multi-bureau"
        ]

        found_indicators = []
        for indicator in multi_bureau_indicators:
            if indicator.lower() in credit_report.lower():
                found_indicators.append(indicator)

        if found_indicators:
            print("\n✅ MULTI-BUREAU INDICATORS FOUND:")
            for indicator in found_indicators:
                print(f"   - {indicator}")
        else:
            print("\n⚠️  No multi-bureau indicators found")

        # Show the full report
        print("\n📋 FULL CREDIT REPORT:")
        print("=" * 50)
        print(credit_report)
        print("=" * 50)

    except Exception as e:
        print(f"❌ Test 1 failed: {e}")

    # Test 2: Try with client_id
    print("\n🔍 TEST 2: GET CUSTOMER CREDIT REPORT BY CLIENT ID")
    print("-" * 50)

    try:
        # Use the working function with client_id parameter
        credit_report_client = engine.get_customer_credit_report(client_id="1747598")

        print("📊 CREDIT REPORT RESULT (CLIENT ID):")
        print(f"   Report length: {len(credit_report_client)} characters")
        print(f"   Report preview: {credit_report_client[:200]}...")

        # Check for multi-bureau indicators
        found_indicators_client = []
        for indicator in multi_bureau_indicators:
            if indicator.lower() in credit_report_client.lower():
                found_indicators_client.append(indicator)

        if found_indicators_client:
            print("\n✅ MULTI-BUREAU INDICATORS FOUND (CLIENT ID):")
            for indicator in found_indicators_client:
                print(f"   - {indicator}")
        else:
            print("\n⚠️  No multi-bureau indicators found (CLIENT ID)")

    except Exception as e:
        print(f"❌ Test 2 failed: {e}")

    # Test 3: Try with customer name
    print("\n🔍 TEST 3: GET CUSTOMER CREDIT REPORT BY NAME")
    print("-" * 50)

    try:
        # Use the working function with customer_name parameter
        credit_report_name = engine.get_customer_credit_report(customer_name="Esteban Price")

        print("📊 CREDIT REPORT RESULT (NAME):")
        print(f"   Report length: {len(credit_report_name)} characters")
        print(f"   Report preview: {credit_report_name[:200]}...")

        # Check for multi-bureau indicators
        found_indicators_name = []
        for indicator in multi_bureau_indicators:
            if indicator.lower() in credit_report_name.lower():
                found_indicators_name.append(indicator)

        if found_indicators_name:
            print("\n✅ MULTI-BUREAU INDICATORS FOUND (NAME):")
            for indicator in found_indicators_name:
                print(f"   - {indicator}")
        else:
            print("\n⚠️  No multi-bureau indicators found (NAME)")

    except Exception as e:
        print(f"❌ Test 3 failed: {e}")

    print("\n🎯 TEST WORKING CREDIT FUNCTION COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_working_credit_function()
