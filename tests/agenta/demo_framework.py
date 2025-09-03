#!/usr / bin / env python3
"""
Agenta Testing Framework Demo

Demonstrates the complete framework capabilities without requiring
actual Agenta.ai endpoints configured.
"""

import os
import json
from datetime import datetime

def demo_ground_truth_extraction():
    """Demo ground truth extraction"""
    print("🔍 DEMO: Ground Truth Extraction")
    print("-" * 40)

    try:
        from ground_truth_extractor import GroundTruthExtractor

        # Extract ground truth
        extractor = GroundTruthExtractor()
        ground_truth = extractor.get_ground_truth()

        print(f"✅ Extracted {len(ground_truth)} ground truth fields")
        print(f"📧 Customer: {ground_truth.get('customer_email')}")
        print(f"💳 Credit Reports: {ground_truth.get('total_credit_reports')}")
        print(f"💰 Transactions: {ground_truth.get('total_transactions')}")
        print(f"🎯 Risk Level: {ground_truth.get('risk_level')}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_test_case_generation():
    """Demo test case generation"""
    print("\n📝 DEMO: Test Case Generation")
    print("-" * 40)

    try:
        from test_case_generator import TestCaseGenerator

        # Generate test cases
        generator = TestCaseGenerator()
        test_cases = generator.generate_all_test_cases()

        print(f"✅ Generated {len(test_cases)} test cases")

        # Show categories
        categories = {}
        for test in test_cases:
            category = test.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1

        print("📊 Categories:")
        for category, count in categories.items():
            print(f"  • {category}: {count} tests")

        # Show sample test case
        if test_cases:
            sample = test_cases[0]
            print(f"\n📋 Sample Test Case: {sample['id']}")
            print(f"  Query: {sample['inputs']['query']}")
            print(f"  Expected fields: {len(sample['expected'])}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_evaluation_framework():
    """Demo evaluation framework setup"""
    print("\n🎯 DEMO: Evaluation Framework")
    print("-" * 40)

    try:
        from agenta_evaluation_framework import AgentaEvaluationFramework

        # Initialize framework
        framework = AgentaEvaluationFramework()

        print("✅ Framework initialized")
        print(f"📊 Field weights configured: {len(framework.field_weights)}")
        print(f"🎯 Promotion rules: {len(framework.promotion_rules)} criteria")

        # Demo scoring
        expected = {
            "customer_name": "Esteban Price",
            "latest_credit_score": 689,
            "has_credit_data": True,
            "explanation": "Customer has excellent credit history"
        }

        actual = {
            "customer_name": "Esteban Price",
            "latest_credit_score": 685,  # Close but not exact
            "has_credit_data": True,
            "explanation": "Customer shows strong credit performance"
        }

        score, breakdown = framework.score_record(expected, actual)
        print("\n📈 Demo Scoring:")
        print(f"  Overall Score: {score:.3f}")
        print(f"  Field Breakdown: {len(breakdown)} fields scored")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_results_analysis():
    """Demo results analysis"""
    print("\n📊 DEMO: Results Analysis")
    print("-" * 40)

    try:
        from results_analyzer import ResultsAnalyzer

        # Create mock results data
        mock_results = {
            "metadata": {
                "evaluation_timestamp": datetime.now().isoformat(),
                "total_test_cases": 5,
                "total_variants": 2
            },
            "summary_statistics": {
                "baseline": {
                    "test_cases": 5,
                    "successes": 5,
                    "failures": 0,
                    "success_rate": 1.0,
                    "avg_score": 0.85,
                    "avg_latency_s": 3.2
                },
                "challenger": {
                    "test_cases": 5,
                    "successes": 5,
                    "failures": 0,
                    "success_rate": 1.0,
                    "avg_score": 0.89,  # 4.7% improvement
                    "avg_latency_s": 3.4   # 6.25% increase
                }
            },
            "detailed_results": []
        }

        # Initialize analyzer
        analyzer = ResultsAnalyzer()
        analysis = analyzer.analyze_results(mock_results)

        print("✅ Analysis completed")

        # Show promotion recommendation
        promotion = analysis['promotion_recommendation']
        print("\n🎯 Promotion Recommendation:")
        print(f"  Decision: {'✅ PROMOTE' if promotion['promote'] else '❌ DO NOT PROMOTE'}")
        print(f"  Confidence: {promotion['confidence']}")
        print(f"  Reason: {promotion['reason']}")

        # Show variant comparison
        comparison = analysis['variant_comparison']
        if 'challenger_vs_baseline' in comparison.get('score_differences', {}):
            score_diff = comparison['score_differences']['challenger_vs_baseline']
            print("\n📈 Performance Comparison:")
            print(f"  Score Improvement: +{score_diff['absolute_difference']:.4f} ({score_diff['percentage_improvement']:+.1f}%)")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_environment_validation():
    """Demo environment validation"""
    print("\n🔍 DEMO: Environment Validation")
    print("-" * 40)

    try:
        from agenta_test_runner import AgentaTestRunner

        # Initialize runner
        runner = AgentaTestRunner()

        # Validate environment
        validation = runner.validate_environment()

        print("✅ Validation completed")
        print(f"📊 Checks performed: {len(validation['checks'])}")
        print(f"⚠️ Warnings: {len(validation['warnings'])}")
        print(f"❌ Errors: {len(validation['errors'])}")
        print(f"🎯 Overall Valid: {validation['valid']}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run complete framework demo"""
    print("🚀 AGENTA TESTING FRAMEWORK DEMO")
    print("=" * 60)
    print("Demonstrating framework capabilities with your master data")
    print("=" * 60)

    demos = [
        ("Ground Truth Extraction", demo_ground_truth_extraction),
        ("Test Case Generation", demo_test_case_generation),
        ("Evaluation Framework", demo_evaluation_framework),
        ("Results Analysis", demo_results_analysis),
        ("Environment Validation", demo_environment_validation)
    ]

    results = {}

    for name, demo_func in demos:
        try:
            success = demo_func()
            results[name] = success
        except Exception as e:
            print(f"❌ Demo '{name}' failed: {e}")
            results[name] = False

    # Summary
    print("\n🎯 DEMO SUMMARY")
    print("=" * 30)

    successful = sum(results.values())
    total = len(results)

    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {name}")

    print(f"\n📊 Success Rate: {successful}/{total} ({successful / total * 100:.1f}%)")

    if successful == total:
        print("\n🎉 ALL DEMOS SUCCESSFUL!")
        print("Framework is ready for production use")
        print("\nNext steps:")
        print("1. Configure Agenta.ai endpoints (APP_URL_BASELINE, APP_URL_CHALLENGER)")
        print("2. Set AGENTA_API_KEY environment variable")
        print("3. Run: python agenta_test_runner.py --quick 5")
    else:
        print("\n⚠️ Some demos failed - check error messages above")

    return successful == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


