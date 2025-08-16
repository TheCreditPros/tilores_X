#!/usr/bin/env python3
"""
Test script for Gemini 2.5 Flash, Flash Lite, and 1.5 Flash models
Tests basic API connectivity and compares performance
"""

import os
import time
import json
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Model configurations
GEMINI_MODELS = {
    "gemini-1.5-flash-002": {
        "name": "Gemini 1.5 Flash",
        "version": "1.5",
        "context_window": 1048576,  # 1M tokens
        "description": "Current production model",
    },
    "gemini-2.5-flash": {
        "name": "Gemini 2.5 Flash",
        "version": "2.5",
        "context_window": 1048576,  # 1M tokens expected
        "description": "New enhanced model with improved reasoning",
    },
    "gemini-2.5-flash-lite": {
        "name": "Gemini 2.5 Flash Lite",
        "version": "2.5-lite",
        "context_window": 1048576,  # 1M tokens expected
        "description": "Lightweight version optimized for speed",
    },
}

# Test queries
TEST_QUERIES = [
    {"type": "simple", "query": "What is 2+2?", "expected_elements": ["4", "four"]},
    {
        "type": "reasoning",
        "query": "Explain why water expands when it freezes, and what implications this has for life on Earth.",
        "expected_elements": ["hydrogen bonds", "density", "ice", "life", "ocean"],
    },
    {
        "type": "customer_data",
        "query": "Find customer with email blessedwina@aol.com and provide their details.",
        "expected_elements": ["customer", "email", "blessedwina"],
    },
    {
        "type": "complex_analysis",
        "query": "Compare the advantages and disadvantages of microservices vs monolithic architecture for a startup with 5 developers.",
        "expected_elements": ["microservices", "monolithic", "startup", "developers", "complexity"],
    },
]


def test_model(model_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test a single Gemini model"""
    print(f"\n📊 Testing {config['name']} ({model_id})")
    print("=" * 60)

    results = {
        "model_id": model_id,
        "name": config["name"],
        "version": config["version"],
        "available": False,
        "tests": [],
        "average_response_time": 0,
        "error": None,
    }

    try:
        # Initialize model
        print(f"  Initializing {model_id}...")
        model = ChatGoogleGenerativeAI(
            model=model_id, google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0.7, max_output_tokens=2048
        )

        # Test each query
        response_times = []
        for test in TEST_QUERIES:
            print(f"\n  Testing {test['type']} query...")

            start_time = time.time()
            test_result = {
                "type": test["type"],
                "query": test["query"][:50] + "...",
                "success": False,
                "response_time": 0,
                "response_length": 0,
                "has_expected_elements": False,
            }

            try:
                # Send query
                response = model.invoke(test["query"])
                response_time = (time.time() - start_time) * 1000  # Convert to ms

                # Extract content
                if hasattr(response, "content"):
                    content = response.content
                elif isinstance(response, dict) and "content" in response:
                    content = response["content"]
                else:
                    content = str(response)

                # Check for expected elements
                content_lower = content.lower()
                has_elements = any(elem.lower() in content_lower for elem in test["expected_elements"])

                test_result.update(
                    {
                        "success": True,
                        "response_time": round(response_time, 2),
                        "response_length": len(content),
                        "has_expected_elements": has_elements,
                        "sample_response": content[:200] + "..." if len(content) > 200 else content,
                    }
                )

                response_times.append(response_time)

                print(f"    ✅ Success - {response_time:.0f}ms, {len(content)} chars")
                if has_elements:
                    print("    ✓ Contains expected elements")
                else:
                    print("    ⚠️ Missing expected elements")

            except Exception as e:
                test_result["error"] = str(e)
                print(f"    ❌ Error: {e}")

            results["tests"].append(test_result)

        # Calculate average response time
        if response_times:
            results["available"] = True
            results["average_response_time"] = round(sum(response_times) / len(response_times), 2)
            print(f"\n  📈 Average response time: {results['average_response_time']:.0f}ms")

    except Exception as e:
        results["error"] = str(e)
        print(f"  ❌ Model initialization failed: {e}")

    return results


def compare_models(results: list) -> None:
    """Compare performance across models"""
    print("\n" + "=" * 80)
    print("📊 MODEL COMPARISON RESULTS")
    print("=" * 80)

    # Availability summary
    print("\n🔌 Model Availability:")
    for result in results:
        status = "✅ Available" if result["available"] else "❌ Not Available"
        print(f"  {result['name']:30} {status}")
        if result["error"] and not result["available"]:
            print(f"    Error: {result['error']}")

    # Performance comparison (only for available models)
    available_models = [r for r in results if r["available"]]

    if available_models:
        print("\n⚡ Performance Comparison (Available Models):")
        print(f"  {'Model':<30} {'Avg Response Time':<20} {'Success Rate'}")
        print("  " + "-" * 70)

        for result in sorted(available_models, key=lambda x: x["average_response_time"]):
            successful_tests = sum(1 for t in result["tests"] if t["success"])
            total_tests = len(result["tests"])
            success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

            print(f"  {result['name']:<30} {result['average_response_time']:.0f}ms{'':<15} {success_rate:.0f}%")

        # Query type analysis
        print("\n📝 Query Type Performance (ms):")
        query_types = ["simple", "reasoning", "customer_data", "complex_analysis"]

        print(f"  {'Model':<30}", end="")
        for qt in query_types:
            print(f"{qt[:10]:<12}", end="")
        print()
        print("  " + "-" * 78)

        for result in available_models:
            print(f"  {result['name']:<30}", end="")
            for qt in query_types:
                test = next((t for t in result["tests"] if t["type"] == qt and t["success"]), None)
                if test:
                    print(f"{test['response_time']:.0f}ms{'':<6}", end="")
                else:
                    print(f"{'N/A':<12}", end="")
            print()

        # Winner determination
        if len(available_models) > 1:
            fastest = min(available_models, key=lambda x: x["average_response_time"])
            print(f"\n🏆 Fastest Model: {fastest['name']} ({fastest['average_response_time']:.0f}ms average)")

            # Calculate improvement
            baseline = next((r for r in available_models if "1.5" in r["version"]), None)
            if baseline and baseline != fastest:
                improvement = (
                    (baseline["average_response_time"] - fastest["average_response_time"])
                    / baseline["average_response_time"]
                    * 100
                )
                print(f"   {improvement:.1f}% faster than {baseline['name']}")


def main():
    """Main test execution"""
    print("🚀 Gemini Model Testing Suite")
    print("Testing Gemini 1.5 Flash vs 2.5 Flash vs 2.5 Flash Lite")
    print("=" * 80)

    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        return

    # Test all models
    all_results = []
    for model_id, config in GEMINI_MODELS.items():
        result = test_model(model_id, config)
        all_results.append(result)
        time.sleep(1)  # Brief pause between models

    # Compare results
    compare_models(all_results)

    # Save results to file
    output_file = f"gemini_test_results_{int(time.time())}.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n💾 Results saved to {output_file}")

    # Recommendations
    print("\n📋 RECOMMENDATIONS:")
    available = [r for r in all_results if r["available"]]

    if any("2.5" in r["version"] for r in available):
        print("  ✅ Gemini 2.5 models are available and ready for integration")

        flash_25 = next((r for r in available if r["model_id"] == "gemini-2.5-flash"), None)
        flash_lite = next((r for r in available if r["model_id"] == "gemini-2.5-flash-lite"), None)
        flash_15 = next((r for r in available if r["model_id"] == "gemini-1.5-flash-002"), None)

        if flash_25 and flash_15:
            if flash_25["average_response_time"] < flash_15["average_response_time"]:
                print("  ⚡ Gemini 2.5 Flash is faster - recommend as primary model")
            else:
                print("  ⚠️ Gemini 2.5 Flash is slower but may have better quality")

        if flash_lite:
            print("  🚀 Gemini 2.5 Flash Lite available for speed-critical queries")
    else:
        print("  ⚠️ Gemini 2.5 models not yet available via API")
        print("  📅 Continue using Gemini 1.5 Flash until 2.5 is released")


if __name__ == "__main__":
    main()
