#!/usr/bin/env python3
"""
Comprehensive Agenta.ai UI Integration Test

Tests the complete Agenta.ai integration including:
1. Environment setup
2. SDK installation and initialization
3. Template prompt system
4. Fallback mechanisms
5. UI integration validation
6. End-to-end functionality
"""

import subprocess
import sys
import requests
import time
import json
from datetime import datetime

def run_setup():
    """Run the Agenta environment setup"""
    print("🔧 Running Agenta environment setup...")
    try:
        result = subprocess.run([
            sys.executable, "setup_agenta_environment.py"
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ Environment setup completed successfully")
            print("📋 Setup output:")
            print(result.stdout)
            return True
        else:
            print(f"❌ Environment setup failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ Environment setup timed out")
        return False
    except Exception as e:
        print(f"❌ Environment setup error: {e}")
        return False

def kill_existing_servers():
    """Kill any existing server processes"""
    try:
        subprocess.run(["pkill", "-f", "direct_credit_api"],
                      capture_output=True, text=True)
        print("🧹 Killed existing server processes")
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Error killing processes: {e}")

def start_enhanced_server():
    """Start the enhanced server with Agenta integration"""
    try:
        print("🚀 Starting enhanced server with Agenta integration...")

        # Start the fixed server with enhanced Agenta manager
        process = subprocess.Popen(
            [sys.executable, "direct_credit_api_fixed.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Wait for startup
        startup_timeout = 20
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
                    print("✅ Enhanced server is running!")
                    return process
            except Exception:
                pass

            time.sleep(0.5)

        print("⚠️ Server startup timeout")
        return process

    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def test_fallback_system():
    """Test the fallback prompt system"""
    print("\n🧪 Testing Fallback Prompt System...")

    test_cases = [
        {
            "name": "Account Status Query",
            "query": "What is the account status for e.j.price1986@gmail.com?",
            "expected_type": "status"
        },
        {
            "name": "Credit Analysis Query",
            "query": "Analyze credit report for customer",
            "expected_type": "credit"
        },
        {
            "name": "Transaction Analysis Query",
            "query": "Show payment history and billing information",
            "expected_type": "transaction"
        },
        {
            "name": "Multi-Data Query",
            "query": "Comprehensive customer analysis with all data",
            "expected_type": "multi_data"
        }
    ]

    results = []

    for test_case in test_cases:
        print(f"\n  📋 Testing: {test_case['name']}")

        request_data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": test_case["query"]}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(
                "http://localhost:8080/v1/chat/completions",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                # Check if response is reasonable
                if len(content) > 50:  # Basic sanity check
                    print(f"    ✅ {test_case['name']}: SUCCESS")
                    print(f"    📝 Response length: {len(content)} chars")
                    results.append({"test": test_case["name"], "success": True, "response_length": len(content)})
                else:
                    print(f"    ⚠️ {test_case['name']}: Response too short")
                    results.append({"test": test_case["name"], "success": False, "error": "Response too short"})
            else:
                print(f"    ❌ {test_case['name']}: HTTP {response.status_code}")
                results.append({"test": test_case["name"], "success": False, "error": f"HTTP {response.status_code}"})

        except Exception as e:
            print(f"    ❌ {test_case['name']}: {e}")
            results.append({"test": test_case["name"], "success": False, "error": str(e)})

    return results

def test_agenta_prompt_parameters():
    """Test Agenta.ai specific prompt parameters"""
    print("\n🧪 Testing Agenta.ai Prompt Parameters...")

    test_cases = [
        {
            "name": "Explicit Prompt ID",
            "prompt_id": "account-status-v1",
            "query": "Check status for customer@example.com"
        },
        {
            "name": "Template Prompt ID",
            "prompt_id": "credit_analysis_comprehensive",
            "query": "Analyze credit for customer"
        },
        {
            "name": "Fallback Prompt ID",
            "prompt_id": "fallback_default",
            "query": "General customer inquiry"
        }
    ]

    results = []

    for test_case in test_cases:
        print(f"\n  📋 Testing: {test_case['name']}")

        request_data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": test_case["query"]}
            ],
            "temperature": 0.7,
            "prompt_id": test_case["prompt_id"],
            "prompt_version": "1.0"
        }

        try:
            response = requests.post(
                "http://localhost:8080/v1/chat/completions",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                print(f"    ✅ {test_case['name']}: SUCCESS")
                print(f"    📝 Prompt ID: {test_case['prompt_id']}")
                print(f"    📝 Response length: {len(content)} chars")
                results.append({
                    "test": test_case["name"],
                    "success": True,
                    "prompt_id": test_case["prompt_id"],
                    "response_length": len(content)
                })
            else:
                print(f"    ❌ {test_case['name']}: HTTP {response.status_code}")
                results.append({
                    "test": test_case["name"],
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })

        except Exception as e:
            print(f"    ❌ {test_case['name']}: {e}")
            results.append({
                "test": test_case["name"],
                "success": False,
                "error": str(e)
            })

    return results

def test_template_prompt_availability():
    """Test that template prompts are available and properly loaded"""
    print("\n🧪 Testing Template Prompt Availability...")

    # Check if template prompts file exists
    import os
    template_file = "agenta_template_prompts.json"

    if os.path.exists(template_file):
        try:
            with open(template_file, 'r') as f:
                templates = json.load(f)

            print(f"✅ Template prompts file found: {len(templates)} prompts")

            # Validate template structure
            required_fields = ["name", "description", "system_prompt", "temperature", "max_tokens"]
            valid_templates = 0

            for key, template in templates.items():
                if all(field in template for field in required_fields):
                    valid_templates += 1
                    print(f"  ✅ {template['name']}: Valid structure")
                else:
                    print(f"  ❌ {key}: Missing required fields")

            return {
                "templates_found": len(templates),
                "valid_templates": valid_templates,
                "success": valid_templates > 0
            }

        except Exception as e:
            print(f"❌ Error reading template prompts: {e}")
            return {"success": False, "error": str(e)}
    else:
        print(f"⚠️ Template prompts file not found: {template_file}")
        return {"success": False, "error": "Template file not found"}

def test_agenta_ui_compatibility():
    """Test compatibility with Agenta.ai UI expectations"""
    print("\n🧪 Testing Agenta.ai UI Compatibility...")

    # Test various request formats that Agenta.ai might send
    test_formats = [
        {
            "name": "Standard OpenAI Format",
            "request": {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Test query"}],
                "temperature": 0.7
            }
        },
        {
            "name": "Agenta.ai Extended Format",
            "request": {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Test query"}],
                "temperature": 0.5,
                "max_tokens": 500,
                "prompt_id": "test-prompt",
                "prompt_version": "1.0"
            }
        },
        {
            "name": "Structured Content Format",
            "request": {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": "Structured content test"}]
                    }
                ],
                "temperature": 0.7
            }
        }
    ]

    results = []

    for test_format in test_formats:
        print(f"\n  📋 Testing: {test_format['name']}")

        try:
            response = requests.post(
                "http://localhost:8080/v1/chat/completions",
                json=test_format["request"],
                headers={"Content-Type": "application/json"},
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()

                # Validate OpenAI-compatible response structure
                required_fields = ["id", "object", "created", "model", "choices"]
                if all(field in result for field in required_fields):
                    print(f"    ✅ {test_format['name']}: Valid OpenAI format")
                    results.append({"test": test_format["name"], "success": True})
                else:
                    print(f"    ⚠️ {test_format['name']}: Invalid response structure")
                    results.append({"test": test_format["name"], "success": False, "error": "Invalid structure"})
            else:
                print(f"    ❌ {test_format['name']}: HTTP {response.status_code}")
                results.append({"test": test_format["name"], "success": False, "error": f"HTTP {response.status_code}"})

        except Exception as e:
            print(f"    ❌ {test_format['name']}: {e}")
            results.append({"test": test_format["name"], "success": False, "error": str(e)})

    return results

def generate_test_report(fallback_results, prompt_results, template_results, ui_results):
    """Generate comprehensive test report"""

    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("=" * 60)

    # Calculate success rates
    fallback_success = sum(1 for r in fallback_results if r.get("success", False))
    prompt_success = sum(1 for r in prompt_results if r.get("success", False))
    ui_success = sum(1 for r in ui_results if r.get("success", False))

    print(f"\n🎯 SUCCESS RATES:")
    print(f"  - Fallback System: {fallback_success}/{len(fallback_results)} ({fallback_success/len(fallback_results)*100:.1f}%)")
    print(f"  - Prompt Parameters: {prompt_success}/{len(prompt_results)} ({prompt_success/len(prompt_results)*100:.1f}%)")
    print(f"  - UI Compatibility: {ui_success}/{len(ui_results)} ({ui_success/len(ui_results)*100:.1f}%)")
    print(f"  - Template System: {'✅ PASS' if template_results.get('success') else '❌ FAIL'}")

    # Overall assessment
    overall_success = (
        fallback_success == len(fallback_results) and
        prompt_success == len(prompt_results) and
        ui_success == len(ui_results) and
        template_results.get("success", False)
    )

    print(f"\n🏆 OVERALL RESULT: {'🎉 ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}")

    # Detailed results
    print(f"\n📋 DETAILED RESULTS:")

    print(f"\n  🔄 Fallback System Tests:")
    for result in fallback_results:
        status = "✅" if result.get("success") else "❌"
        print(f"    {status} {result['test']}")

    print(f"\n  🎯 Prompt Parameter Tests:")
    for result in prompt_results:
        status = "✅" if result.get("success") else "❌"
        print(f"    {status} {result['test']}")

    print(f"\n  🖥️ UI Compatibility Tests:")
    for result in ui_results:
        status = "✅" if result.get("success") else "❌"
        print(f"    {status} {result['test']}")

    print(f"\n  📋 Template System:")
    if template_results.get("success"):
        print(f"    ✅ {template_results.get('valid_templates', 0)} valid templates loaded")
    else:
        print(f"    ❌ Template system failed: {template_results.get('error', 'Unknown error')}")

    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if overall_success:
        print(f"  ✅ System is ready for Agenta.ai UI integration")
        print(f"  ✅ All fallback mechanisms are working correctly")
        print(f"  ✅ Template prompts are properly configured")
        print(f"  🚀 Proceed with Agenta.ai dashboard configuration")
    else:
        print(f"  ⚠️ Address failing tests before production deployment")
        print(f"  🔧 Check server logs for detailed error information")
        print(f"  📋 Verify template prompt configurations")

    return overall_success

def main():
    """Main test function"""
    print("🚀 Agenta.ai UI Integration Test Suite")
    print("=" * 60)

    start_time = datetime.now()

    # Step 1: Run setup
    if not run_setup():
        print("❌ Setup failed, cannot proceed")
        return False

    # Step 2: Kill existing servers and start enhanced server
    kill_existing_servers()
    server_process = start_enhanced_server()

    if not server_process:
        print("❌ Cannot proceed without running server")
        return False

    try:
        # Step 3: Test template prompt availability
        template_results = test_template_prompt_availability()

        # Step 4: Test fallback system
        fallback_results = test_fallback_system()

        # Step 5: Test Agenta.ai prompt parameters
        prompt_results = test_agenta_prompt_parameters()

        # Step 6: Test UI compatibility
        ui_results = test_agenta_ui_compatibility()

        # Step 7: Generate comprehensive report
        overall_success = generate_test_report(
            fallback_results, prompt_results, template_results, ui_results
        )

        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n⏱️ Total test duration: {duration:.1f} seconds")
        print(f"🎯 Test completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        return overall_success

    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up...")
        if server_process:
            server_process.terminate()
            server_process.wait()
        print("✅ Cleanup complete")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
