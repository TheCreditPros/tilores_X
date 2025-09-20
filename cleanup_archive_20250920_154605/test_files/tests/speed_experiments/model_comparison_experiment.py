#!/usr/bin/env python3
"""
Proper LangSmith Model Comparison Experiment
Tests all 6 working models against each other for speed and answer quality
"""

import os
import time
import requests
from langsmith import Client
from langsmith.evaluation import evaluate


def create_model_comparison_experiment():
    """Create LangSmith experiment comparing all 6 models"""

    # Load environment
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        print("❌ LANGSMITH_API_KEY not found")
        return False

    client = Client(api_key=api_key)

    print("🚀 Creating Model Comparison Experiment")

    # Working models to compare
    models_to_compare = [
        "llama-3.3-70b-versatile",
        "gpt-3.5-turbo",
        "gpt-4o-mini",
        "deepseek-r1-distill-llama-70b",
        "claude-3-haiku",
        "gemini-1.5-flash-002",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]

    # Create dataset with real customer scenarios
    dataset_name = "tilores-model-comparison-scenarios"

    try:
        # Create dataset
        try:
            dataset = client.read_dataset(dataset_name=dataset_name)
            print(f"📊 Using existing dataset: {dataset_name}")
        except Exception:
            dataset = client.create_dataset(
                dataset_name=dataset_name, description="Model comparison scenarios with real Tilores customer data"
            )
            print(f"📊 Created dataset: {dataset_name}")

            # Add real test scenarios
            scenarios = [
                {
                    "inputs": {"query": "Find customer with email blessedwina@aol.com", "test_type": "customer_lookup"},
                    "outputs": {
                        "expected_customer": "Edwina Hawthorne",
                        "expected_client_id": "2270",
                        "expected_phone": "2672661591",
                    },
                },
                {
                    "inputs": {
                        "query": "Get credit report for customer Edwina Hawthorne with client ID 2270",
                        "test_type": "credit_analysis",
                    },
                    "outputs": {
                        "expected_keywords": ["credit", "score", "analysis", "Edwina", "Hawthorne"],
                        "min_response_length": 100,
                    },
                },
            ]

            for scenario in scenarios:
                client.create_example(dataset_id=dataset.id, inputs=scenario["inputs"], outputs=scenario["outputs"])

            print(f"✅ Added {len(scenarios)} comparison scenarios")

    except Exception as e:
        print(f"❌ Dataset creation failed: {e}")
        return False

    # Create target functions for each model
    def create_model_target_function(model_id: str):
        """Create a target function for a specific model"""

        def model_target_function(inputs):
            """Target function for specific model"""
            query = inputs.get("query", "")

            try:
                start_time = time.time()

                response = requests.post(
                    "https://tiloresx-production.up.railway.app/v1/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json={"model": model_id, "messages": [{"role": "user", "content": query}], "max_tokens": 500},
                    timeout=60,  # Increased timeout
                )

                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000

                if response.status_code == 200:
                    data = response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                    return {
                        "response": content,
                        "model": model_id,
                        "response_time_ms": response_time_ms,
                        "success": True,
                        "content_length": len(content),
                        "status_code": 200,
                    }
                else:
                    return {
                        "response": f"HTTP Error {response.status_code}",
                        "model": model_id,
                        "response_time_ms": response_time_ms,
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                    }

            except Exception as e:
                return {
                    "response": f"Request failed: {str(e)}",
                    "model": model_id,
                    "response_time_ms": 0,
                    "success": False,
                    "error": str(e),
                }

        return model_target_function

    # Define evaluators for comparison
    def speed_evaluator(run, example):
        """Evaluate response speed across models"""
        try:
            response_time = run.outputs.get("response_time_ms", 0)

            # Speed scoring (lower time = higher score)
            if response_time < 1000:  # Under 1s
                score = 1.0
            elif response_time < 2000:  # Under 2s
                score = 0.9
            elif response_time < 3000:  # Under 3s
                score = 0.8
            elif response_time < 5000:  # Under 5s
                score = 0.6
            else:
                score = 0.3

            return {"key": "speed_score", "score": score, "comment": f"{response_time:.0f}ms"}
        except Exception:
            return {"key": "speed_score", "score": 0.0, "comment": "Speed measurement failed"}

    def accuracy_evaluator(run, example):
        """Evaluate answer accuracy across models"""
        try:
            response = run.outputs.get("response", "")
            expected_items = example.outputs.get("expected_keywords", [])

            if not expected_items:
                # For customer lookup, check for expected customer data
                expected_customer = example.outputs.get("expected_customer", "")
                expected_client_id = example.outputs.get("expected_client_id", "")

                score = 0
                if expected_customer and expected_customer.lower() in response.lower():
                    score += 0.5
                if expected_client_id and expected_client_id in response:
                    score += 0.5

                return {
                    "key": "accuracy_score",
                    "score": score,
                    "comment": f"Customer data accuracy: {score * 100:.0f}%",
                }
            else:
                # For credit analysis, check for expected keywords
                found_keywords = sum(1 for keyword in expected_items if keyword.lower() in response.lower())
                accuracy_score = found_keywords / len(expected_items)

                return {
                    "key": "accuracy_score",
                    "score": accuracy_score,
                    "comment": f"Found {found_keywords}/{len(expected_items)} keywords",
                }

        except Exception:
            return {"key": "accuracy_score", "score": 0.0, "comment": "Accuracy evaluation failed"}

    def quality_evaluator(run, example):
        """Evaluate overall response quality"""
        try:
            response = run.outputs.get("response", "")
            success = run.outputs.get("success", False)
            content_length = run.outputs.get("content_length", 0)

            if not success:
                return {"key": "quality_score", "score": 0.0, "comment": "Request failed"}

            # Quality based on response characteristics
            quality_score = 0

            # Length check
            if content_length > 200:
                quality_score += 0.3
            elif content_length > 100:
                quality_score += 0.2
            elif content_length > 50:
                quality_score += 0.1

            # Error check
            if "error" not in response.lower():
                quality_score += 0.3

            # Professional tone check
            professional_indicators = ["customer", "found", "information", "data", "report"]
            found_indicators = sum(1 for indicator in professional_indicators if indicator in response.lower())
            quality_score += min(found_indicators * 0.08, 0.4)  # Max 0.4 points

            return {
                "key": "quality_score",
                "score": quality_score,
                "comment": f"Quality: {quality_score * 100:.0f}%, Length: {content_length}",
            }

        except Exception:
            return {"key": "quality_score", "score": 0.0, "comment": "Quality evaluation failed"}

    # Run experiments for each model
    experiment_results = {}

    for model_id in models_to_compare:
        print(f"\n🔧 Creating experiment for {model_id}...")

        try:
            # Create target function for this model
            model_target = create_model_target_function(model_id)

            # Run evaluation for this model
            result = evaluate(
                model_target,
                data=dataset_name,
                evaluators=[speed_evaluator, accuracy_evaluator, quality_evaluator],
                experiment_prefix=f"tilores_{model_id.replace('-', '_')}",
                description=f"Speed and quality testing for {model_id} with real Tilores customer data",
                metadata={
                    "model": model_id,
                    "api_endpoint": "https://tiloresx-production.up.railway.app/v1/chat/completions",
                    "real_customer": "Edwina Hawthorne",
                    "test_type": "model_comparison",
                },
            )

            experiment_results[model_id] = result.experiment_name
            print(f"✅ Created experiment for {model_id}: {result.experiment_name}")

        except Exception as e:
            print(f"❌ Failed to create experiment for {model_id}: {e}")
            experiment_results[model_id] = f"FAILED: {str(e)}"

    print("\n🎉 Model comparison experiments created!")
    print(f"📊 Total experiments: {len([r for r in experiment_results.values() if not r.startswith('FAILED')])}")
    print("🔗 View at: https://smith.langchain.com")

    # Print experiment URLs
    for model_id, experiment_name in experiment_results.items():
        if not experiment_name.startswith("FAILED"):
            print(f"   {model_id}: {experiment_name}")

    return experiment_results


def main():
    """Main function"""
    print("🧪 LangSmith Model Comparison Experiment")
    print("=" * 50)
    print("🎯 Testing all 6 models against each other for speed and quality")

    results = create_model_comparison_experiment()

    if results:
        successful_experiments = [r for r in results.values() if not r.startswith("FAILED")]
        print(f"\n✅ SUCCESS: {len(successful_experiments)} model experiments created")
        print("📊 Each model now has its own experiment for direct comparison")
        print("🏆 LangSmith will show speed and quality metrics side-by-side")
    else:
        print("\n❌ Model comparison experiment creation failed")

    return results


if __name__ == "__main__":
    main()
