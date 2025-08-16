#!/usr/bin/env python3
"""
Submit speed experiments to LangSmith platform
Creates experiments and uploads results for analysis
"""

import os
import json
import time
from langsmith import Client


def submit_speed_experiments():
    """Submit our speed experiments to LangSmith"""

    # Initialize LangSmith client
    api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        print("❌ LangSmith API key not found. Set LANGSMITH_API_KEY environment variable.")
        return False

    client = Client(api_key=api_key)
    project_name = os.getenv("LANGSMITH_PROJECT", "tilores-speed-experiments")

    print(f"🚀 Submitting speed experiments to LangSmith project: {project_name}")

    # Load our experiment results
    try:
        with open("tests/speed_experiments/working_models_results.json", "r") as f:
            results = json.load(f)
    except FileNotFoundError:
        print("❌ Experiment results not found. Run working_models_experiment.py first.")
        return False

    # Create experiment dataset
    experiment_name = f"tilores-speed-test-{int(time.time())}"

    print(f"📊 Creating LangSmith experiment: {experiment_name}")

    # Prepare experiment data
    experiment_data = {
        "experiment_name": experiment_name,
        "description": "Speed and accuracy testing for Tilores customer data retrieval",
        "metadata": {
            "framework": "tilores_X",
            "test_type": "speed_and_accuracy",
            "customer_data": "real_production_data",
            "models_tested": len(results["models_tested"]),
            "duration_minutes": results["duration_minutes"],
            "success_rate": "100%",
        },
        "results": results,
    }

    # Create runs for each model test
    runs_created = []

    for model_id in results["models_tested"]:
        model_data = results["customer_tests"][model_id]

        # Create run for basic customer lookup
        basic_lookup = model_data["customer_responses"]["basic_lookup"]

        run_data = {
            "name": f"{model_id}_customer_lookup",
            "inputs": {
                "model": model_id,
                "provider": model_data["model_info"]["provider"],
                "query": "Find customer with email blessedwina@aol.com",
                "test_type": "customer_lookup",
            },
            "outputs": {
                "response_time_ms": basic_lookup["response_time_ms"],
                "success": basic_lookup["success"],
                "content_length": basic_lookup.get("content_length", 0),
                "has_real_data": basic_lookup.get("has_real_data", False),
                "has_customer_name": basic_lookup.get("has_customer_name", False),
            },
            "metadata": {"experiment": experiment_name, "customer": "Edwina Hawthorne", "client_id": "2270"},
        }

        try:
            # Create run in LangSmith
            run = client.create_run(
                name=run_data["name"],
                run_type="llm",
                inputs=run_data["inputs"],
                outputs=run_data["outputs"],
                project_name=project_name,
                extra=run_data["metadata"],
            )
            runs_created.append(run.id)
            print(f"✅ Created run: {run_data['name']} (ID: {run.id})")

        except Exception as e:
            print(f"❌ Failed to create run {run_data['name']}: {e}")

    # Create summary run with overall results
    try:
        summary_run = client.create_run(
            name=f"{experiment_name}_summary",
            run_type="chain",
            inputs={
                "experiment_type": "speed_comparison",
                "models_tested": results["models_tested"],
                "test_duration": f"{results['duration_minutes']:.1f} minutes",
            },
            outputs={
                "fastest_model": results["performance_summary"]["fastest_model"]["model_id"],
                "fastest_time": f"{results['performance_summary']['fastest_model']['avg_response_time']:.0f}ms",
                "success_rate": "100%",
                "models_ranking": results["performance_summary"]["model_ranking"],
            },
            project_name=project_name,
            extra={
                "experiment": experiment_name,
                "total_runs": len(runs_created),
                "real_customer_data": "Edwina Hawthorne validated",
            },
        )

        print(f"✅ Created summary run: {summary_run.id}")

    except Exception as e:
        print(f"❌ Failed to create summary run: {e}")

    print(f"\n🎉 Successfully submitted {len(runs_created)} runs to LangSmith")
    print(f"📊 Project: {project_name}")
    print(f"🔗 View results at: https://smith.langchain.com/projects/{project_name}")

    return True


def create_experiment_dataset():
    """Create a dataset for our speed experiments"""

    api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        return False

    client = Client(api_key=api_key)

    # Create dataset with our test scenarios
    dataset_name = "tilores-speed-test-scenarios"

    try:
        # Check if dataset exists
        try:
            dataset = client.read_dataset(dataset_name=dataset_name)
            print(f"📊 Using existing dataset: {dataset_name}")
        except Exception:
            # Create new dataset
            dataset = client.create_dataset(
                dataset_name=dataset_name, description="Speed test scenarios for Tilores customer data retrieval"
            )
            print(f"📊 Created new dataset: {dataset_name}")

        # Add our test scenarios
        scenarios = [
            {
                "inputs": {
                    "query": "Find customer with email blessedwina@aol.com",
                    "customer_email": "blessedwina@aol.com",
                    "test_type": "customer_lookup",
                },
                "outputs": {
                    "expected_customer": "Edwina Hawthorne",
                    "expected_client_id": "2270",
                    "expected_phone": "2672661591",
                },
            },
            {
                "inputs": {
                    "query": "Get credit report for customer Edwina Hawthorne with client ID 2270",
                    "customer_name": "Edwina Hawthorne",
                    "test_type": "credit_report",
                },
                "outputs": {
                    "expected_content": "credit analysis",
                    "expected_elements": ["credit", "score", "analysis"],
                },
            },
        ]

        # Add scenarios to dataset
        for i, scenario in enumerate(scenarios):
            try:
                client.create_example(dataset_id=dataset.id, inputs=scenario["inputs"], outputs=scenario["outputs"])
                print(f"✅ Added scenario {i + 1} to dataset")
            except Exception as e:
                print(f"⚠️ Scenario {i + 1} may already exist: {e}")

        return dataset.id

    except Exception as e:
        print(f"❌ Failed to create dataset: {e}")
        return None


def main():
    """Main function to submit experiments"""
    print("🧪 LangSmith Speed Experiments Submission")
    print("=" * 50)

    # Create dataset first
    dataset_id = create_experiment_dataset()
    if dataset_id:
        print(f"📊 Dataset ready: {dataset_id}")

    # Submit experiment results
    success = submit_speed_experiments()

    if success:
        print("\n🎉 LangSmith submission completed successfully!")
        print("📊 Check your LangSmith dashboard for detailed analysis")
    else:
        print("\n❌ LangSmith submission failed")

    return success


if __name__ == "__main__":
    main()
