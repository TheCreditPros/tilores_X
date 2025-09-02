#!/usr/bin/env python3
"""
Setup Agenta.ai Test Sets with API Key

Interactive script to set API key and create all test sets.
"""

import os
import subprocess
import sys

def set_api_key():
    """Set the Agenta API key"""
    print("🔐 Agenta.ai API Key Setup for Test Sets")
    print("=" * 50)

    # Check if already set
    current_key = os.getenv("AGENTA_API_KEY")
    if current_key and current_key != "your_api_key_here":
        print(f"✅ AGENTA_API_KEY already set: {'*' * 20}...{current_key[-4:] if len(current_key) > 4 else '****'}")

        use_existing = input("🔄 Use existing key? (Y/n): ").lower().strip()
        if use_existing != 'n':
            return current_key

    print("\n📝 Please enter your Agenta.ai API key:")
    print("(Find this in your Agenta.ai dashboard under Settings > API Keys)")

    # Get API key from user
    api_key = input("\n🔑 API Key: ").strip()

    if not api_key:
        print("❌ No API key provided")
        return None

    if len(api_key) < 10:  # Basic validation
        print("❌ API key seems too short")
        return None

    # Set environment variable for this session
    os.environ["AGENTA_API_KEY"] = api_key
    print(f"\n✅ API key set for this session")

    return api_key

def create_test_sets():
    """Create test sets using the API"""
    print("\n🧪 Creating Agenta.ai Test Sets...")

    try:
        # Run the test set creation script
        result = subprocess.run([
            sys.executable, "create_agenta_test_sets.py"
        ], capture_output=True, text=True, timeout=60)

        print("📋 Test Set Creation Output:")
        print("=" * 30)
        print(result.stdout)

        if result.stderr:
            print("⚠️ Warnings/Errors:")
            print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("⏰ Test set creation timed out")
        return False
    except Exception as e:
        print(f"❌ Error creating test sets: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Agenta.ai Test Set Setup")
    print("=" * 40)

    # Step 1: Set API key
    api_key = set_api_key()
    if not api_key:
        print("❌ Cannot proceed without API key")
        return False

    # Step 2: Create test sets
    success = create_test_sets()

    if success:
        print("\n🎉 Test sets created successfully!")
        print("\n📋 What was created:")
        print("  ✅ Account Status Queries (5 test cases)")
        print("  ✅ Credit Analysis Queries (5 test cases)")
        print("  ✅ Multi-Data Analysis Queries (4 test cases)")
        print("  ✅ Transaction Analysis Queries (4 test cases)")
        print("  ✅ Phone Call Analysis Queries (4 test cases)")
        print("  ✅ Performance Benchmarks (3 test cases)")

        print(f"\n🎯 Next steps:")
        print(f"  1. Go to Agenta.ai Test Sets section")
        print(f"  2. Run tests against your variants")
        print(f"  3. Compare performance across variants")
        print(f"  4. Use results to optimize prompts")
    else:
        print("\n❌ Test set creation failed")
        print("🔧 Check your API key and network connection")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
