#!/usr/bin/env python3
"""
Test Agenta.ai SDK integration and fixed API functionality
"""

import subprocess
import sys
import os
import requests
import json
import time

def install_agenta_sdk():
    """Install the Agenta SDK"""
    try:
        print("📦 Installing Agenta.ai SDK...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-U", "agenta"
        ], capture_output=True, text=True, check=True)

        print("✅ Agenta SDK installed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Agenta SDK: {e}")
        print(f"Error output: {e.stderr}")
        return False

def test_agenta_import():
    """Test if Agenta can be imported"""
    try:
        import agenta as ag
        print("✅ Agenta SDK imported successfully!")
        print(f"Agenta version: {getattr(ag, '__version__', 'Unknown')}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Agenta: {e}")
        return False

def kill_existing_server():
    """Kill any existing server processes"""
    try:
        subprocess.run(["pkill", "-f", "direct_credit_api"],
                      capture_output=True, text=True)
        print("🧹 Killed existing server processes")
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Error killing processes: {e}")

def start_fixed_server():
    """Start the fixed server"""
    try:
        print("🚀 Starting fixed server...")
        # Start server in background
        process = subprocess.Popen(
            [sys.executable, "direct_credit_api_fixed.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Wait for startup
        startup_timeout = 15
        start_time = time.time()

        while time.time() - start_time < startup_timeout:
            if process.poll() is not None:
                # Process ended
                output, _ = process.communicate()
                print(f"❌ Server failed to start:\n{output}")
                return None

            # Check if server is responding
            try:
                response = requests.get("http://localhost:8080/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Fixed server is running!")
                    return process
            except Exception:
                pass

            time.sleep(0.5)

        print("⚠️ Server startup timeout")
        return process

    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def test_status_query():
    """Test the fixed status query functionality"""

    test_query = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "What is the account status for e.j.price1986@gmail.com?"
            }
        ],
        "temperature": 0.7
    }

    try:
        print("\n🧪 Testing fixed status query...")
        response = requests.post(
            "http://localhost:8080/v1/chat/completions",
            json=test_query,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"\n✅ Status query SUCCESS! Response:\n{content}")
            return True
        else:
            print(f"❌ Status query failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Status query request failed: {e}")
        return False

def test_agenta_prompt_query():
    """Test query with Agenta.ai prompt parameters"""

    test_query = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "Analyze credit for e.j.price1986@gmail.com"
            }
        ],
        "temperature": 0.7,
        "prompt_id": "credit-analysis-v1",
        "prompt_version": "1.0"
    }

    try:
        print("\n🧪 Testing Agenta.ai prompt integration...")
        response = requests.post(
            "http://localhost:8080/v1/chat/completions",
            json=test_query,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"\n✅ Agenta prompt query SUCCESS! Response:\n{content}")
            return True
        else:
            print(f"❌ Agenta prompt query failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Agenta prompt query request failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Agenta.ai SDK Integration...")

    # Step 1: Install Agenta SDK
    if not install_agenta_sdk():
        print("❌ Cannot proceed without Agenta SDK")
        return False

    # Step 2: Test import
    if not test_agenta_import():
        print("❌ Cannot proceed without working Agenta import")
        return False

    # Step 3: Kill existing servers
    kill_existing_server()

    # Step 4: Start fixed server
    server_process = start_fixed_server()
    if not server_process:
        print("❌ Cannot proceed without running server")
        return False

    try:
        # Step 5: Test status query (the previously failing functionality)
        status_success = test_status_query()

        # Step 6: Test Agenta.ai prompt integration
        agenta_success = test_agenta_prompt_query()

        # Results
        print("\n📊 TEST RESULTS:")
        print(f"  - Status Query Fix: {'✅ PASS' if status_success else '❌ FAIL'}")
        print(f"  - Agenta Integration: {'✅ PASS' if agenta_success else '❌ FAIL'}")

        overall_success = status_success and agenta_success
        print(f"\n{'🎉 ALL TESTS PASSED!' if overall_success else '⚠️ SOME TESTS FAILED'}")

        return overall_success

    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        if server_process:
            server_process.terminate()
            server_process.wait()
        print("✅ Cleanup complete")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
