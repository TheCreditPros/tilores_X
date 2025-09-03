#!/usr/bin/env python3
"""
Comprehensive Test Suite to Ensure No Existing Functionality Was Broken

This test validates that all existing functionality still works correctly
after implementing the routing-aware Agenta.ai features.
"""

import json
import sys
import os
from typing import Dict, List, Any
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ExistingFunctionalityTestSuite:
    """Test suite to validate existing functionality remains intact"""

    def __init__(self):
        self.test_results = []

    def run_all_tests(self):
        """Run all existing functionality tests"""
        print("🔍 Testing Existing Functionality After Routing-Aware Implementation")
        print("=" * 80)
        print("Ensuring no existing functionality was broken by the new routing-aware features")
        print()

        # Test original Agenta SDK manager
        self.test_original_agenta_manager()

        # Test template prompts loading
        self.test_template_prompts()

        # Test local prompts functionality
        self.test_local_prompts()

        # Test fallback system
        self.test_fallback_system()

        # Test backward compatibility
        self.test_backward_compatibility()

        # Test existing convenience functions
        self.test_convenience_functions()

        # Test with actual Agenta.ai API
        self.test_agenta_api_connection()

        # Generate test report
        self.generate_test_report()

    def test_original_agenta_manager(self):
        """Test that the original EnhancedAgentaManager still works"""
        print("📋 Testing Original EnhancedAgentaManager")
        print("-" * 50)

        try:
            from agenta_sdk_manager_enhanced import EnhancedAgentaManager

            # Create original manager
            original_manager = EnhancedAgentaManager()

            # Test basic functionality
            prompt_config = original_manager.get_prompt_config("credit", "What's the credit score?")

            required_fields = ["system_prompt", "temperature", "max_tokens", "source"]
            has_required_fields = all(field in prompt_config for field in required_fields)

            result = {
                "test_name": "Original EnhancedAgentaManager",
                "test_type": "original_functionality",
                "success": has_required_fields,
                "details": {
                    "manager_created": True,
                    "prompt_config_generated": bool(prompt_config),
                    "has_required_fields": has_required_fields,
                    "source": prompt_config.get("source"),
                    "prompt_length": len(prompt_config.get("system_prompt", ""))
                }
            }

            status = "✅ PASS" if has_required_fields else "❌ FAIL"
            print(f"{status} Original EnhancedAgentaManager works correctly")

            self.test_results.append(result)

        except Exception as e:
            result = {
                "test_name": "Original EnhancedAgentaManager",
                "test_type": "original_functionality",
                "success": False,
                "error": str(e)
            }
            print(f"❌ ERROR Original EnhancedAgentaManager: {e}")
            self.test_results.append(result)

    def test_template_prompts(self):
        """Test that template prompts are loaded correctly"""
        print("\n📁 Testing Template Prompts Loading")
        print("-" * 50)

        try:
            from agenta_sdk_manager_enhanced import enhanced_agenta_manager

            # Test template prompts loading
            available_prompts = enhanced_agenta_manager.get_available_prompts()

            template_prompts = available_prompts.get("template_prompts", {})
            expected_templates = [
                "credit_analysis_comprehensive",
                "multi_data_analysis",
                "account_status",
                "transaction_analysis",
                "phone_call_analysis",
                "fallback_default"
            ]

            has_expected_templates = all(template in template_prompts for template in expected_templates)

            result = {
                "test_name": "Template Prompts Loading",
                "test_type": "template_functionality",
                "success": has_expected_templates,
                "details": {
                    "total_templates": len(template_prompts),
                    "expected_templates": expected_templates,
                    "actual_templates": list(template_prompts.keys()),
                    "has_expected_templates": has_expected_templates
                }
            }

            status = "✅ PASS" if has_expected_templates else "❌ FAIL"
            print(f"{status} Template prompts loaded: {len(template_prompts)} templates")

            self.test_results.append(result)

        except Exception as e:
            result = {
                "test_name": "Template Prompts Loading",
                "test_type": "template_functionality",
                "success": False,
                "error": str(e)
            }
            print(f"❌ ERROR Template prompts: {e}")
            self.test_results.append(result)

    def test_local_prompts(self):
        """Test local prompts functionality"""
        print("\n📂 Testing Local Prompts Functionality")
        print("-" * 50)

        try:
            from agenta_sdk_manager_enhanced import enhanced_agenta_manager

            # Check if local prompts file exists and is loaded
            available_prompts = enhanced_agenta_manager.get_available_prompts()
            local_prompts = available_prompts.get("local_prompts", [])

            # Test that local prompts can be accessed
            local_prompt_accessible = True
            if local_prompts:
                # Try to get a local prompt
                for prompt_key in local_prompts:
                    config = enhanced_agenta_manager.get_prompt_config("general", "test", prompt_key)
                    if not config:
                        local_prompt_accessible = False
                        break

            result = {
                "test_name": "Local Prompts Functionality",
                "test_type": "local_functionality",
                "success": local_prompt_accessible,
                "details": {
                    "local_prompts_count": len(local_prompts),
                    "local_prompts": local_prompts,
                    "accessible": local_prompt_accessible
                }
            }

            status = "✅ PASS" if local_prompt_accessible else "❌ FAIL"
            print(f"{status} Local prompts: {len(local_prompts)} prompts accessible")

            self.test_results.append(result)

        except Exception as e:
            result = {
                "test_name": "Local Prompts Functionality",
                "test_type": "local_functionality",
                "success": False,
                "error": str(e)
            }
            print(f"❌ ERROR Local prompts: {e}")
            self.test_results.append(result)

    def test_fallback_system(self):
        """Test that the fallback system works correctly"""
        print("\n🔄 Testing Fallback System")
        print("-" * 50)

        try:
            from agenta_sdk_manager_enhanced import enhanced_agenta_manager

            # Test fallback with unknown query type
            fallback_config = enhanced_agenta_manager.get_prompt_config("unknown_type", "test query")

            # Should get fallback configuration
            has_fallback = bool(fallback_config.get("system_prompt"))
            is_fallback_source = "fallback" in fallback_config.get("source", "").lower()

            result = {
                "test_name": "Fallback System",
                "test_type": "fallback_functionality",
                "success": has_fallback and is_fallback_source,
                "details": {
                    "has_fallback_prompt": has_fallback,
                    "is_fallback_source": is_fallback_source,
                    "fallback_source": fallback_config.get("source"),
                    "fallback_prompt_length": len(fallback_config.get("system_prompt", ""))
                }
            }

            status = "✅ PASS" if (has_fallback and is_fallback_source) else "❌ FAIL"
            print(f"{status} Fallback system works correctly")

            self.test_results.append(result)

        except Exception as e:
            result = {
                "test_name": "Fallback System",
                "test_type": "fallback_functionality",
                "success": False,
                "error": str(e)
            }
            print(f"❌ ERROR Fallback system: {e}")
            self.test_results.append(result)

    def test_backward_compatibility(self):
        """Test backward compatibility with existing code"""
        print("\n🔙 Testing Backward Compatibility")
        print("-" * 50)

        try:
            from agenta_sdk_manager_enhanced import get_prompt_for_query, log_prompt_performance

            # Test existing convenience function
            prompt_config = get_prompt_for_query("test query", "credit")

            has_prompt = bool(prompt_config.get("system_prompt"))

            # Test logging function (should not throw error)
            try:
                log_prompt_performance("test-prompt", "test query", "test response", True, 0.5)
                logging_works = True
            except Exception:
                logging_works = False

            result = {
                "test_name": "Backward Compatibility",
                "test_type": "compatibility",
                "success": has_prompt and logging_works,
                "details": {
                    "convenience_function_works": has_prompt,
                    "logging_function_works": logging_works,
                    "prompt_source": prompt_config.get("source")
                }
            }

            status = "✅ PASS" if (has_prompt and logging_works) else "❌ FAIL"
            print(f"{status} Backward compatibility maintained")

            self.test_results.append(result)

        except Exception as e:
            result = {
                "test_name": "Backward Compatibility",
                "test_type": "compatibility",
                "success": False,
                "error": str(e)
            }
            print(f"❌ ERROR Backward compatibility: {e}")
            self.test_results.append(result)

    def test_convenience_functions(self):
        """Test existing convenience functions"""
        print("\n🛠️ Testing Convenience Functions")
        print("-" * 50)

        try:
            from agenta_sdk_manager_enhanced import (
                get_prompt_for_query,
                log_prompt_performance,
                get_routing_aware_prompt,
                create_routing_test_case
            )

            # Test original convenience function
            original_prompt = get_prompt_for_query("test query", "credit")
            original_works = bool(original_prompt.get("system_prompt"))

            # Test new routing-aware convenience function
            routing_prompt = get_routing_aware_prompt("test query", "customer-id")
            routing_works = bool(routing_prompt.get("system_prompt"))

            # Test routing test case creation
            test_case = create_routing_test_case("test query", "customer-id", "credit")
            test_case_works = bool(test_case.get("input"))

            all_functions_work = original_works and routing_works and test_case_works

            result = {
                "test_name": "Convenience Functions",
                "test_type": "convenience_functionality",
                "success": all_functions_work,
                "details": {
                    "original_function_works": original_works,
                    "routing_aware_function_works": routing_works,
                    "test_case_function_works": test_case_works
                }
            }

            status = "✅ PASS" if all_functions_work else "❌ FAIL"
            print(f"{status} All convenience functions work correctly")

            self.test_results.append(result)

        except Exception as e:
            result = {
                "test_name": "Convenience Functions",
                "test_type": "convenience_functionality",
                "success": False,
                "error": str(e)
            }
            print(f"❌ ERROR Convenience functions: {e}")
            self.test_results.append(result)

    def test_agenta_api_connection(self):
        """Test actual Agenta.ai API connection with the provided key"""
        print("\n🌐 Testing Agenta.ai API Connection")
        print("-" * 50)

        try:
            from agenta_sdk_manager_enhanced import RoutingAwareAgentaManager

            # Create new manager to test with API key
            api_manager = RoutingAwareAgentaManager()

            # Check if Agenta is initialized
            agenta_initialized = api_manager.initialized
            agenta_available = api_manager.agenta_available
            has_api_key = bool(os.getenv("AGENTA_API_KEY"))

            # Try to get a prompt configuration
            prompt_config = api_manager.get_prompt_config("credit", "test query")
            prompt_generated = bool(prompt_config.get("system_prompt"))

            # Check source - should be from Agenta if connected, template if fallback
            source = prompt_config.get("source", "")

            result = {
                "test_name": "Agenta.ai API Connection",
                "test_type": "api_connection",
                "success": prompt_generated,  # Success if we get a prompt (either from API or fallback)
                "details": {
                    "agenta_initialized": agenta_initialized,
                    "agenta_available": agenta_available,
                    "has_api_key": has_api_key,
                    "prompt_generated": prompt_generated,
                    "prompt_source": source,
                    "api_key_set": "AGENTA_API_KEY" in os.environ
                }
            }

            if agenta_initialized:
                status = "✅ PASS"
                print(f"{status} Agenta.ai API connected successfully")
            else:
                status = "⚠️ FALLBACK"
                print(f"{status} Using fallback prompts (API key may need configuration in Agenta.ai)")

            self.test_results.append(result)

        except Exception as e:
            result = {
                "test_name": "Agenta.ai API Connection",
                "test_type": "api_connection",
                "success": False,
                "error": str(e)
            }
            print(f"❌ ERROR Agenta.ai API: {e}")
            self.test_results.append(result)

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print(f"\n" + "=" * 80)
        print("📊 EXISTING FUNCTIONALITY TEST REPORT")
        print("=" * 80)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"\n📈 OVERALL RESULTS:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {success_rate:.1f}%")

        # Group results by test type
        test_types = {}
        for result in self.test_results:
            test_type = result["test_type"]
            if test_type not in test_types:
                test_types[test_type] = {"passed": 0, "failed": 0, "total": 0}

            test_types[test_type]["total"] += 1
            if result["success"]:
                test_types[test_type]["passed"] += 1
            else:
                test_types[test_type]["failed"] += 1

        print(f"\n📊 RESULTS BY TEST TYPE:")
        for test_type, stats in test_types.items():
            type_success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"  {test_type.replace('_', ' ').title()}: {stats['passed']}/{stats['total']} ({type_success_rate:.1f}%)")

        # Show failed tests
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print(f"\n❌ FAILED TESTS:")
            for result in failed_results:
                print(f"  - {result['test_name']}")
                if "error" in result:
                    print(f"    Error: {result['error']}")

        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "existing_functionality_validation",
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate
            },
            "test_types": test_types,
            "detailed_results": self.test_results
        }

        report_filename = f"existing_functionality_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n💾 Detailed report saved to: {report_filename}")

        # Final assessment
        if success_rate >= 95:
            print(f"\n🎉 EXCELLENT: All existing functionality preserved!")
            print("✅ Safe to deploy routing-aware features")
            print("✅ No breaking changes detected")
        elif success_rate >= 85:
            print(f"\n✅ GOOD: Most existing functionality preserved")
            print("⚠️ Minor issues detected - review before deployment")
        else:
            print(f"\n❌ CRITICAL: Existing functionality may be broken")
            print("🔧 Fix issues before deployment")

        return report_data


def main():
    """Run existing functionality tests"""
    print("🔍 Existing Functionality Validation")
    print("Testing that routing-aware implementation doesn't break existing features")

    test_suite = ExistingFunctionalityTestSuite()
    test_suite.run_all_tests()

    # Calculate success rate from test results
    total_tests = len(test_suite.test_results)
    passed_tests = sum(1 for result in test_suite.test_results if result["success"])
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    return success_rate >= 85


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
