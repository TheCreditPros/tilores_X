#!/usr/bin/env python3
"""
LangSmith experiment to compare Gemini 1.5 Flash vs 2.5 Flash vs 2.5 Flash Lite
Tests performance on Tilores customer data queries
"""

import os
import time
import requests
from typing import Dict, Any
from langsmith import Client
from langsmith.evaluation import evaluate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize LangSmith client
client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

# Model configurations for testing
GEMINI_MODELS = ["gemini-1.5-flash-002", "gemini-2.5-flash", "gemini-2.5-flash-lite"]

# API endpoint
API_URL = "http://localhost:8080/v1/chat/completions"


def create_gemini_dataset():
    """Create a LangSmith dataset for Gemini model comparison"""
    dataset_name = f"gemini_comparison_{int(time.time())}"

    try:
        # Create dataset
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Comparing Gemini 1.5 Flash vs 2.5 Flash vs 2.5 Flash Lite on Tilores queries",
        )

        # Test scenarios
        examples = [
            {
                "inputs": {"query": "Find customer with client ID 1648647", "test_type": "customer_lookup"},
                "outputs": {
                    "expected_customer": "Dawn Bruton",
                    "expected_id": "1648647",
                    "expected_elements": ["Dawn", "Bruton", "1648647", "De Soto", "Missouri"],
                },
            },
            {
                "inputs": {
                    "query": "Search for customer with email blessedwina@aol.com and show their credit data",
                    "test_type": "credit_lookup",
                },
                "outputs": {
                    "expected_customer": "Edwina",
                    "expected_email": "blessedwina@aol.com",
                    "expected_elements": ["customer", "email", "credit", "San Francisco"],
                },
            },
            {
                "inputs": {
                    "query": "Get transaction history for lelisguardado@sbcglobal.net",
                    "test_type": "transaction_history",
                },
                "outputs": {
                    "expected_customer": "Lelis Guardado",
                    "expected_email": "lelisguardado@sbcglobal.net",
                    "expected_elements": ["transaction", "history", "payment"],
                },
            },
            {
                "inputs": {
                    "query": "Show me all available data for customer migdaliareyes53@gmail.com including credit reports",
                    "test_type": "comprehensive_data",
                },
                "outputs": {
                    "expected_customer": "Migdalia Reyes",
                    "expected_email": "migdaliareyes53@gmail.com",
                    "expected_elements": ["credit", "report", "customer", "data"],
                },
            },
            {
                "inputs": {"query": "What is the credit score for customer 1648647?", "test_type": "credit_score"},
                "outputs": {
                    "expected_customer": "Dawn Bruton",
                    "expected_id": "1648647",
                    "expected_elements": ["credit", "score"],
                },
            },
        ]

        # Add examples to dataset
        for example in examples:
            client.create_example(dataset_id=dataset.id, inputs=example["inputs"], outputs=example["outputs"])

        print(f"✅ Created dataset: {dataset_name}")
        return dataset

    except Exception as e:
        print(f"❌ Error creating dataset: {e}")
        return None


def run_gemini_model(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Run a query against a specific Gemini model"""
    model_id = inputs.get("model_id")
    query = inputs.get("query")

    if not model_id or not query:
        return {"response": "Error: Missing model_id or query", "success": False, "response_time_ms": 0}

    try:
        start_time = time.time()

        # Make API request
        response = requests.post(
            API_URL,
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": query}],
                "temperature": 0.7,
                "max_tokens": 2048,
            },
            timeout=30,
        )

        response_time_ms = (time.time() - start_time) * 1000

        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            return {
                "response": content,
                "success": True,
                "response_time_ms": round(response_time_ms, 2),
                "content_length": len(content),
                "model": model_id,
            }
        else:
            return {
                "response": f"Error: HTTP {response.status_code}",
                "success": False,
                "response_time_ms": round(response_time_ms, 2),
                "model": model_id,
            }

    except Exception as e:
        return {"response": f"Error: {str(e)}", "success": False, "response_time_ms": 0, "model": model_id}


def create_evaluators():
    """Create evaluators for the experiment"""

    def speed_evaluator(run, example):
        """Evaluate response speed"""
        response_time = run.outputs.get("response_time_ms", 0)

        # Speed scoring (faster is better)
        if response_time == 0:
            score = 0
        elif response_time < 1000:
            score = 1.0
        elif response_time < 3000:
            score = 0.8
        elif response_time < 5000:
            score = 0.6
        elif response_time < 10000:
            score = 0.4
        else:
            score = 0.2

        return {"key": "speed_score", "score": score, "comment": f"Response time: {response_time:.0f}ms"}

    def accuracy_evaluator(run, example):
        """Evaluate response accuracy"""
        if not run.outputs.get("success", False):
            return {"key": "accuracy_score", "score": 0.0, "comment": "Request failed"}

        response = run.outputs.get("response", "").lower()
        expected_elements = example.outputs.get("expected_elements", [])

        # Check how many expected elements are in the response
        found_elements = sum(1 for elem in expected_elements if elem.lower() in response)
        score = found_elements / len(expected_elements) if expected_elements else 0

        return {
            "key": "accuracy_score",
            "score": score,
            "comment": f"Found {found_elements}/{len(expected_elements)} expected elements",
        }

    def quality_evaluator(run, example):
        """Evaluate overall response quality"""
        if not run.outputs.get("success", False):
            return {"key": "quality_score", "score": 0.0, "comment": "Request failed"}

        response = run.outputs.get("response", "")
        content_length = run.outputs.get("content_length", 0)

        # Quality based on response completeness
        if content_length < 50:
            score = 0.3
        elif content_length < 200:
            score = 0.6
        elif content_length < 1000:
            score = 0.8
        else:
            score = 0.9

        # Bonus for structured response
        if any(indicator in response for indicator in ["•", "-", ":", "\n"]):
            score = min(1.0, score + 0.1)

        return {"key": "quality_score", "score": score, "comment": f"Content length: {content_length} chars"}

    return [speed_evaluator, accuracy_evaluator, quality_evaluator]


def run_gemini_experiments():
    """Run experiments for all Gemini models"""
    print("\n🧪 Gemini Model LangSmith Experiments")
    print("=" * 60)

    # Create dataset
    dataset = create_gemini_dataset()
    if not dataset:
        print("❌ Failed to create dataset")
        return

    # Create evaluators
    evaluators = create_evaluators()

    # Run experiment for each model
    experiment_results = {}

    for model_id in GEMINI_MODELS:
        print(f"\n📊 Testing {model_id}...")

        experiment_name = f"gemini_comparison_{model_id.replace('.', '_').replace('-', '_')}_{int(time.time())}"

        try:
            # Create target function for this model
            def target_fn(inputs: Dict[str, Any]) -> Dict[str, Any]:
                return run_gemini_model({"model_id": model_id, "query": inputs.get("query", "")})

            # Run evaluation
            results = evaluate(
                target_fn,
                data=dataset.name,
                evaluators=evaluators,
                experiment_prefix=experiment_name,
                metadata={"model": model_id, "framework": "tilores_X", "test_type": "gemini_comparison"},
                max_concurrency=1,  # Run sequentially for accurate timing
            )

            # Collect metrics
            metrics = {"speed_scores": [], "accuracy_scores": [], "quality_scores": [], "response_times": []}

            for result in results:
                if "evaluator_results" in result:
                    for eval_result in result["evaluator_results"]:
                        if eval_result.key == "speed_score":
                            metrics["speed_scores"].append(eval_result.score)
                        elif eval_result.key == "accuracy_score":
                            metrics["accuracy_scores"].append(eval_result.score)
                        elif eval_result.key == "quality_score":
                            metrics["quality_scores"].append(eval_result.score)

                if "run" in result and result["run"].outputs:
                    rt = result["run"].outputs.get("response_time_ms", 0)
                    if rt > 0:
                        metrics["response_times"].append(rt)

            # Calculate averages
            avg_speed = sum(metrics["speed_scores"]) / len(metrics["speed_scores"]) if metrics["speed_scores"] else 0
            avg_accuracy = (
                sum(metrics["accuracy_scores"]) / len(metrics["accuracy_scores"]) if metrics["accuracy_scores"] else 0
            )
            avg_quality = (
                sum(metrics["quality_scores"]) / len(metrics["quality_scores"]) if metrics["quality_scores"] else 0
            )
            avg_response_time = (
                sum(metrics["response_times"]) / len(metrics["response_times"]) if metrics["response_times"] else 0
            )

            experiment_results[model_id] = {
                "experiment_name": experiment_name,
                "avg_speed_score": round(avg_speed, 3),
                "avg_accuracy_score": round(avg_accuracy, 3),
                "avg_quality_score": round(avg_quality, 3),
                "avg_response_time_ms": round(avg_response_time, 2),
                "success": True,
            }

            print(f"  ✅ Experiment created: {experiment_name}")
            print(f"     Speed Score: {avg_speed:.2f}")
            print(f"     Accuracy Score: {avg_accuracy:.2f}")
            print(f"     Quality Score: {avg_quality:.2f}")
            print(f"     Avg Response Time: {avg_response_time:.0f}ms")

        except Exception as e:
            print(f"  ❌ Error running experiment: {e}")
            experiment_results[model_id] = {"experiment_name": experiment_name, "error": str(e), "success": False}

    # Print comparison summary
    print("\n" + "=" * 80)
    print("📊 GEMINI MODEL COMPARISON SUMMARY")
    print("=" * 80)

    successful_models = {k: v for k, v in experiment_results.items() if v.get("success", False)}

    if successful_models:
        # Sort by response time
        sorted_by_speed = sorted(successful_models.items(), key=lambda x: x[1]["avg_response_time_ms"])

        print("\n⚡ SPEED RANKING:")
        for i, (model, results) in enumerate(sorted_by_speed, 1):
            print(f"  {i}. {model:<30} {results['avg_response_time_ms']:.0f}ms")

        # Sort by accuracy
        sorted_by_accuracy = sorted(successful_models.items(), key=lambda x: x[1]["avg_accuracy_score"], reverse=True)

        print("\n🎯 ACCURACY RANKING:")
        for i, (model, results) in enumerate(sorted_by_accuracy, 1):
            print(f"  {i}. {model:<30} {results['avg_accuracy_score'] * 100:.1f}%")

        # Sort by quality
        sorted_by_quality = sorted(successful_models.items(), key=lambda x: x[1]["avg_quality_score"], reverse=True)

        print("\n✨ QUALITY RANKING:")
        for i, (model, results) in enumerate(sorted_by_quality, 1):
            print(f"  {i}. {model:<30} {results['avg_quality_score'] * 100:.1f}%")

        # Overall recommendation
        print("\n📋 RECOMMENDATIONS:")

        fastest = sorted_by_speed[0][0]
        most_accurate = sorted_by_accuracy[0][0]
        best_quality = sorted_by_quality[0][0]

        print(f"  🚀 Fastest: {fastest}")
        print(f"  🎯 Most Accurate: {most_accurate}")
        print(f"  ✨ Best Quality: {best_quality}")

        # Determine best overall
        scores = {}
        for model in successful_models:
            # Weighted score: speed (40%), accuracy (40%), quality (20%)
            speed_rank = next(i for i, (m, _) in enumerate(sorted_by_speed, 1) if m == model)
            accuracy_rank = next(i for i, (m, _) in enumerate(sorted_by_accuracy, 1) if m == model)
            quality_rank = next(i for i, (m, _) in enumerate(sorted_by_quality, 1) if m == model)

            # Lower rank is better, so invert for scoring
            n_models = len(successful_models)
            speed_score = (n_models - speed_rank + 1) / n_models
            accuracy_score = (n_models - accuracy_rank + 1) / n_models
            quality_score = (n_models - quality_rank + 1) / n_models

            scores[model] = speed_score * 0.4 + accuracy_score * 0.4 + quality_score * 0.2

        best_overall = max(scores.items(), key=lambda x: x[1])
        print(f"\n  🏆 BEST OVERALL: {best_overall[0]}")

        # Specific use case recommendations
        print("\n  USE CASE RECOMMENDATIONS:")
        print(f"    • Speed-critical queries: {fastest}")
        print(f"    • Data accuracy critical: {most_accurate}")
        print(f"    • Customer-facing responses: {best_quality}")

    print("\n🔗 View experiments at: https://smith.langchain.com")

    return experiment_results


if __name__ == "__main__":
    # Check prerequisites
    if not os.getenv("LANGSMITH_API_KEY"):
        print("❌ Error: LANGSMITH_API_KEY not found")
        exit(1)

    # Run experiments
    results = run_gemini_experiments()

    # Save results
    import json

    with open(f"gemini_langsmith_results_{int(time.time())}.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n✅ Gemini comparison experiments complete!")
