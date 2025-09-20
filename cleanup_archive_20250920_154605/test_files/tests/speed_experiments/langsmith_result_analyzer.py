#!/usr/bin/env python3
"""
LangSmith Result Analyzer
Fetches actual experiment results from LangSmith to identify specific failures
"""

import os
from langsmith import Client
from typing import Dict, List


def analyze_langsmith_experiment_results():
    """Fetch and analyze actual LangSmith experiment results"""

    from dotenv import load_dotenv

    load_dotenv()

    client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

    print("🔍 Analyzing Actual LangSmith Experiment Results")
    print("=" * 55)

    # Recent experiment IDs from our model comparison
    experiment_ids = [
        "tilores_llama_3.3_70b_versatile-25078bc4",
        "tilores_gpt_3.5_turbo-635bd77e",
        "tilores_gpt_4o_mini-dccf58af",
        "tilores_deepseek_r1_distill_llama_70b-4e8c1e8a",
        "tilores_claude_3_haiku-a70a5b91",
        "tilores_gemini_1.5_flash_002-4fd12b2c",
    ]

    all_failures = []

    for experiment_id in experiment_ids:
        print(f"\n📊 Analyzing experiment: {experiment_id}")

        try:
            # Get runs for this experiment
            runs = list(
                client.list_runs(project_name="tilores-speed-experiments", filter=f'eq(name, "{experiment_id}")')
            )

            print(f"   Found {len(runs)} runs")

            for run in runs:
                if hasattr(run, "outputs") and run.outputs:
                    # Check for failures
                    if not run.outputs.get("success", True):
                        failure_info = {
                            "experiment_id": experiment_id,
                            "run_id": str(run.id),
                            "error": run.outputs.get("error", "Unknown error"),
                            "status_code": run.outputs.get("status_code", "Unknown"),
                            "model": run.outputs.get("model", "Unknown"),
                            "response": run.outputs.get("response", "")[:200],  # First 200 chars
                        }
                        all_failures.append(failure_info)

                        print("   ❌ Failure found:")
                        print(f"      Model: {failure_info['model']}")
                        print(f"      Error: {failure_info['error']}")
                        print(f"      Status: {failure_info['status_code']}")
                    else:
                        print(f"   ✅ Run successful: {run.outputs.get('model', 'Unknown model')}")

        except Exception as e:
            print(f"   ❌ Failed to analyze {experiment_id}: {e}")

    # Analyze failure patterns
    print("\n🔍 FAILURE ANALYSIS")
    print("=" * 55)
    print(f"Total failures found: {len(all_failures)}")

    if all_failures:
        # Group by error type
        error_patterns = {}
        for failure in all_failures:
            error = failure["error"]
            if "400" in str(failure["status_code"]):
                if "context length" in error.lower():
                    error_patterns["CONTEXT_LENGTH"] = error_patterns.get("CONTEXT_LENGTH", 0) + 1
                elif "tool call validation" in error.lower():
                    error_patterns["TOOL_VALIDATION"] = error_patterns.get("TOOL_VALIDATION", 0) + 1
                elif "decommissioned" in error.lower():
                    error_patterns["MODEL_DEPRECATED"] = error_patterns.get("MODEL_DEPRECATED", 0) + 1
                else:
                    error_patterns["OTHER_HTTP_400"] = error_patterns.get("OTHER_HTTP_400", 0) + 1
            else:
                error_patterns["NON_HTTP_400"] = error_patterns.get("NON_HTTP_400", 0) + 1

        print("\n📈 ERROR PATTERNS:")
        for pattern, count in error_patterns.items():
            print(f"   {pattern}: {count} occurrences")

        # Show specific failures
        print("\n❌ SPECIFIC FAILURES:")
        for i, failure in enumerate(all_failures[:5], 1):  # Show first 5
            print(f"   {i}. {failure['model']}: {failure['error'][:100]}...")

        # Generate fix recommendations
        recommendations = generate_fix_recommendations(error_patterns, all_failures)

        print("\n💡 FIX RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")

        return {
            "total_failures": len(all_failures),
            "error_patterns": error_patterns,
            "failures": all_failures,
            "recommendations": recommendations,
        }
    else:
        print("✅ No failures detected in LangSmith experiments")
        return {"total_failures": 0, "message": "All experiments successful"}


def generate_fix_recommendations(error_patterns: Dict[str, int], failures: List[Dict]) -> List[str]:
    """Generate specific fix recommendations based on error patterns"""
    recommendations = []

    if error_patterns.get("CONTEXT_LENGTH", 0) > 0:
        recommendations.append("Reduce max_tokens to 100-150 for all models to prevent context length issues")

    if error_patterns.get("TOOL_VALIDATION", 0) > 0:
        recommendations.append("Fix tool parameter validation in core_app.py - ensure no null values passed to tools")

    if error_patterns.get("MODEL_DEPRECATED", 0) > 0:
        recommendations.append("Remove deprecated models from experiment list and update model mappings")

    if error_patterns.get("OTHER_HTTP_400", 0) > 0:
        recommendations.append("Investigate generic HTTP 400 errors - may be API rate limiting or malformed requests")

    # Analyze specific error messages for more targeted recommendations
    for failure in failures:
        error_msg = failure["error"].lower()
        if "null" in error_msg and "tool" in error_msg:
            recommendations.append(
                "Fix tool parameter schema - ensure all required parameters are provided as strings, not null"
            )
            break

    if not recommendations:
        recommendations.append("No specific patterns detected - manual investigation of individual failures required")

    return recommendations


def apply_fixes_and_rerun():
    """Apply fixes based on analysis and rerun experiments"""

    # First analyze current results
    analysis = analyze_langsmith_experiment_results()

    if analysis["total_failures"] == 0:
        print("\n✅ No failures to fix - experiments are working correctly")
        return True

    print(f"\n🔧 Applying fixes for {analysis['total_failures']} failures...")

    # Apply the most common fixes
    fixes_to_apply = []

    if analysis["error_patterns"].get("CONTEXT_LENGTH", 0) > 0:
        fixes_to_apply.append("reduce_max_tokens_to_100")

    if analysis["error_patterns"].get("TOOL_VALIDATION", 0) > 0:
        fixes_to_apply.append("simplify_queries_to_avoid_tools")

    print(f"🔧 Fixes to apply: {', '.join(fixes_to_apply)}")

    # Run the targeted fix framework
    from . import targeted_fix_and_rerun

    results = targeted_fix_and_rerun.fix_and_rerun_langsmith_experiments()

    return results


def main():
    """Main analysis and fix function"""
    print("🔍 LangSmith Result Analysis and Auto-Fix")
    print("=" * 50)

    # Step 1: Analyze current results
    analysis = analyze_langsmith_experiment_results()

    # Step 2: Apply fixes if needed
    if analysis["total_failures"] > 0:
        print(f"\n🔧 {analysis['total_failures']} failures detected - applying fixes...")
        fix_results = apply_fixes_and_rerun()

        if fix_results:
            print("✅ Fixes applied and experiments rerun")
        else:
            print("❌ Fix application failed")
    else:
        print("✅ No failures detected - experiments are working correctly")

    return analysis


if __name__ == "__main__":
    main()
