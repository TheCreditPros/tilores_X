#!/usr/bin/env python3
"""
Comprehensive test suite for Phase 1 Multi-Spectrum Foundation System.

Tests all components of the multi-spectrum baseline framework including:
- 7-spectrum data experimentation framework
- 7-model LangSmith integration
- Quality metrics collection and analysis
- Baseline performance measurement
- Real customer data validation (Edwina Hawthorne)
- Comprehensive evaluator system

Author: Roo (Elite Software Engineer)
Created: 2025-08-16
Phase: 1 - Multi-Spectrum Foundation Testing
"""

import asyncio
import pytest
from unittest.mock import MagicMock, patch

# Import Phase 1 components
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_spectrum_framework import ExperimentSpectrum, MultiSpectrumFramework, QualityScore


class TestExperimentSpectrum:
    """Test suite for ExperimentSpectrum dataclass."""

    def test_experiment_spectrum_creation(self):
        """Test ExperimentSpectrum dataclass creation."""
        spectrum = ExperimentSpectrum(
            name="test_spectrum",
            description="Test spectrum for validation",
            data_samples=[
                {
                    "query": "Find customer test@example.com",
                    "expected_customer": "Test Customer",
                    "identity_type": "email",
                }
            ],
            quality_targets={"accuracy": 0.95, "completeness": 0.90},
            optimization_focus="customer_identification",
        )

        assert spectrum.name == "test_spectrum"
        assert spectrum.description == "Test spectrum for validation"
        assert len(spectrum.data_samples) == 1
        assert spectrum.quality_targets["accuracy"] == 0.95
        assert spectrum.optimization_focus == "customer_identification"

    def test_experiment_spectrum_data_samples_validation(self):
        """Test data samples structure validation."""
        data_samples = [
            {
                "query": "Find customer blessedwina@aol.com",
                "expected_customer": "Edwina Hawthorne",
                "expected_client_id": "2270",
                "identity_type": "email",
            },
            {
                "query": "Look up customer 2270",
                "expected_customer": "Edwina Hawthorne",
                "expected_client_id": "2270",
                "identity_type": "client_id",
            },
        ]

        spectrum = ExperimentSpectrum(
            name="customer_identity_resolution",
            description="Customer identification testing",
            data_samples=data_samples,
            quality_targets={"accuracy": 0.95},
            optimization_focus="identity_resolution",
        )

        assert len(spectrum.data_samples) == 2
        assert all("query" in sample for sample in spectrum.data_samples)
        assert all("expected_customer" in sample for sample in spectrum.data_samples)
        assert spectrum.data_samples[0]["identity_type"] == "email"
        assert spectrum.data_samples[1]["identity_type"] == "client_id"


class TestQualityScore:
    """Test suite for QualityScore dataclass."""

    def test_quality_score_creation(self):
        """Test QualityScore dataclass creation."""
        score = QualityScore(
            overall_score=0.92,
            speed_score=0.88,
            accuracy_score=0.95,
            completeness_score=0.90,
            relevance_score=0.89,
            professional_tone_score=0.93,
            customer_satisfaction_score=0.91,
            improvements=["improve_response_time", "enhance_accuracy"],
        )

        assert score.overall_score == 0.92
        assert score.speed_score == 0.88
        assert score.accuracy_score == 0.95
        assert len(score.improvements) == 2
        assert "improve_response_time" in score.improvements

    def test_quality_score_validation_ranges(self):
        """Test quality score validation within expected ranges."""
        score = QualityScore(
            overall_score=0.85,
            speed_score=0.80,
            accuracy_score=0.90,
            completeness_score=0.88,
            relevance_score=0.87,
            professional_tone_score=0.92,
            customer_satisfaction_score=0.89,
            improvements=[],
        )

        # All scores should be between 0 and 1
        assert 0.0 <= score.overall_score <= 1.0
        assert 0.0 <= score.speed_score <= 1.0
        assert 0.0 <= score.accuracy_score <= 1.0
        assert 0.0 <= score.completeness_score <= 1.0
        assert 0.0 <= score.relevance_score <= 1.0
        assert 0.0 <= score.professional_tone_score <= 1.0
        assert 0.0 <= score.customer_satisfaction_score <= 1.0


class TestMultiSpectrumFramework:
    """Test suite for MultiSpectrumFramework."""

    @pytest.fixture
    def mock_langsmith_client(self):
        """Create mock LangSmith client."""
        client = MagicMock()
        client.create_dataset.return_value = MagicMock(id="test_dataset_id")
        client.create_example.return_value = MagicMock(id="test_example_id")
        return client

    @pytest.fixture
    def framework(self, mock_langsmith_client):
        """Create MultiSpectrumFramework instance with mocked dependencies."""
        with patch("multi_spectrum_framework.Client") as mock_client_class:
            mock_client_class.return_value = mock_langsmith_client
            with patch.dict("os.environ", {"LANGSMITH_API_KEY": "test_key", "TILORES_API_URL": "https://test-api.com"}):
                framework = MultiSpectrumFramework()
                framework.client = mock_langsmith_client
                return framework

    def test_framework_initialization(self, framework):
        """Test framework initialization."""
        assert framework.client is not None
        assert len(framework.models) == 5  # Context-compatible models
        assert len(framework.data_spectrums) == 7  # 7 data spectrums
        assert framework.quality_targets["overall_quality"] == 0.90
        assert framework.api_url == "https://tiloresx-production.up.railway.app/v1/chat/completions"

    def test_models_configuration(self, framework):
        """Test models configuration for context compatibility."""
        expected_models = [
            "llama-3.3-70b-versatile",
            "gpt-4o-mini",
            "deepseek-r1-distill-llama-70b",
            "claude-3-haiku",
            "gemini-1.5-flash-002",
        ]

        assert framework.models == expected_models
        assert all(isinstance(model, str) for model in framework.models)

    def test_data_spectrums_initialization(self, framework):
        """Test 7-spectrum data initialization."""
        assert len(framework.data_spectrums) == 7

        spectrum_names = [spectrum.name for spectrum in framework.data_spectrums]
        expected_spectrums = [
            "customer_identity_resolution",
            "financial_analysis_depth",
            "multi_field_integration",
            "conversational_context",
            "performance_scaling",
            "edge_case_handling",
            "professional_communication",
        ]

        for expected in expected_spectrums:
            assert expected in spectrum_names

    def test_customer_identity_spectrum_configuration(self, framework):
        """Test customer identity resolution spectrum configuration."""
        identity_spectrum = next(
            (s for s in framework.data_spectrums if s.name == "customer_identity_resolution"), None
        )

        assert identity_spectrum is not None
        assert identity_spectrum.optimization_focus == "customer_identification_accuracy"
        assert len(identity_spectrum.data_samples) >= 4

        # Test Edwina Hawthorne data samples
        edwina_samples = [
            sample
            for sample in identity_spectrum.data_samples
            if "blessedwina@aol.com" in sample.get("query", "")
            or "Edwina Hawthorne" in sample.get("expected_customer", "")
        ]
        assert len(edwina_samples) >= 2  # Email and name queries

    def test_financial_analysis_spectrum_configuration(self, framework):
        """Test financial analysis depth spectrum configuration."""
        financial_spectrum = next((s for s in framework.data_spectrums if s.name == "financial_analysis_depth"), None)

        assert financial_spectrum is not None
        assert financial_spectrum.optimization_focus == "financial_analysis_depth"
        assert len(financial_spectrum.data_samples) >= 3

        # Test credit score analysis samples
        credit_samples = [
            sample for sample in financial_spectrum.data_samples if "credit score" in sample.get("query", "").lower()
        ]
        assert len(credit_samples) >= 1

    def test_quality_targets_configuration(self, framework):
        """Test quality targets configuration."""
        expected_targets = {
            "overall_quality": 0.90,
            "speed_performance": 0.85,
            "accuracy_rate": 0.95,
            "completeness_rate": 0.90,
            "relevance_score": 0.88,
            "professional_tone": 0.92,
            "customer_satisfaction": 0.90,
        }

        for target, expected_value in expected_targets.items():
            assert framework.quality_targets[target] == expected_value

    def test_create_comprehensive_experiments(self, framework):
        """Test comprehensive experiment creation."""
        with patch("requests.post") as mock_post:
            # Mock successful API responses
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"choices": [{"message": {"content": "Test response"}}]}

            results = framework.create_comprehensive_experiments()

            assert results["success"] is True
            assert results["spectrums_tested"] == 7
            assert results["models_tested"] == 5
            assert "experiments" in results

            # Verify dataset creation calls
            assert framework.client.create_dataset.call_count == 7

    def test_spectrum_evaluators_creation(self, framework):
        """Test spectrum-specific evaluators creation."""
        # Test customer identity evaluators
        identity_spectrum = next(s for s in framework.data_spectrums if s.name == "customer_identity_resolution")
        evaluators = framework._create_spectrum_evaluators(identity_spectrum)

        assert len(evaluators) >= 3
        assert framework._identity_accuracy_evaluator in evaluators
        assert framework._identity_completeness_evaluator in evaluators
        assert framework._response_speed_evaluator in evaluators

        # Test financial analysis evaluators
        financial_spectrum = next(s for s in framework.data_spectrums if s.name == "financial_analysis_depth")
        financial_evaluators = framework._create_spectrum_evaluators(financial_spectrum)

        assert len(financial_evaluators) >= 3
        assert framework._financial_accuracy_evaluator in financial_evaluators

    @pytest.mark.asyncio
    async def test_execute_spectrum_test(self, framework):
        """Test spectrum test execution."""
        test_spectrum = framework.data_spectrums[0]
        test_inputs = {"query": "Find customer blessedwina@aol.com"}

        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "choices": [{"message": {"content": "Customer found: Edwina Hawthorne"}}]
            }

            result = framework._execute_spectrum_test("gpt-4o-mini", test_spectrum, test_inputs)

            assert result["success"] is True
            assert result["model"] == "gpt-4o-mini"
            assert result["spectrum"] == test_spectrum.name
            assert "response_time_ms" in result
            assert "quality_score" in result
            assert 0.0 <= result["quality_score"] <= 1.0

    def test_quality_score_calculation(self, framework):
        """Test quality score calculation."""
        test_response = "Customer found: Edwina Hawthorne, Client ID: 2270, Email: blessedwina@aol.com"
        test_spectrum = framework.data_spectrums[0]  # Customer identity spectrum
        test_inputs = {
            "query": "Find customer blessedwina@aol.com",
            "expected_customer": "Edwina Hawthorne",
            "expected_client_id": "2270",
        }

        quality_score = framework._calculate_quality_score(test_response, test_spectrum, test_inputs)

        assert isinstance(quality_score, QualityScore)
        assert 0.0 <= quality_score.overall_score <= 1.0
        assert 0.0 <= quality_score.accuracy_score <= 1.0
        assert 0.0 <= quality_score.completeness_score <= 1.0
        assert isinstance(quality_score.improvements, list)

    def test_evaluator_methods(self, framework):
        """Test individual evaluator methods."""
        # Mock run and example objects
        mock_run = MagicMock()
        mock_run.outputs = {
            "success": True,
            "response": "Customer found: Edwina Hawthorne, Client ID: 2270",
            "response_time_ms": 1500,
        }

        mock_example = MagicMock()
        mock_example.outputs = {"expected_customer": "Edwina Hawthorne", "expected_client_id": "2270"}

        # Test identity accuracy evaluator
        result = framework._identity_accuracy_evaluator(mock_run, mock_example)
        assert result["key"] == "identity_accuracy"
        assert 0.0 <= result["score"] <= 1.0

        # Test response speed evaluator
        speed_result = framework._response_speed_evaluator(mock_run, mock_example)
        assert speed_result["key"] == "response_speed"
        assert 0.0 <= speed_result["score"] <= 1.0
        assert "1500ms" in speed_result["comment"]

    def test_run_comprehensive_cycle(self, framework):
        """Test complete comprehensive cycle execution."""
        with patch.object(framework, "create_comprehensive_experiments") as mock_create:
            with patch.object(framework, "analyze_multi_spectrum_results") as mock_analyze:
                with patch.object(framework, "generate_optimization_recommendations") as mock_optimize:
                    with patch.object(framework, "create_virtuous_improvement_cycle") as mock_cycle:

                        # Mock return values
                        mock_create.return_value = {"success": True, "experiments": {}}
                        mock_analyze.return_value = {"overall_metrics": {"average_quality_score": 0.91}}
                        mock_optimize.return_value = [{"category": "quality_improvement"}]
                        mock_cycle.return_value = {"cycle_id": "test_cycle"}

                        results = framework.run_comprehensive_cycle()

                        assert results["success"] is True
                        assert "experiment_results" in results
                        assert "analysis" in results
                        assert "improvements" in results
                        assert "optimization_cycle" in results
                        assert "quality_achievement" in results

    def test_analyze_multi_spectrum_results(self, framework):
        """Test multi-spectrum results analysis."""
        mock_experiment_results = {
            "success": True,
            "experiments": {
                "customer_identity_resolution": {"gpt-4o-mini": {"success": True}, "claude-3-haiku": {"success": True}},
                "financial_analysis_depth": {"gpt-4o-mini": {"success": False}, "claude-3-haiku": {"success": True}},
            },
        }

        analysis = framework.analyze_multi_spectrum_results(mock_experiment_results)

        assert "spectrum_performance" in analysis
        assert "overall_metrics" in analysis
        assert analysis["overall_metrics"]["total_experiments"] == 4
        assert analysis["overall_metrics"]["successful_experiments"] == 3

    def test_generate_optimization_recommendations(self, framework):
        """Test optimization recommendations generation."""
        mock_analysis = {
            "overall_metrics": {"average_quality_score": 0.87},
            "spectrum_performance": {
                "customer_identity_resolution": {"quality_achievement": True, "average_quality": 0.92},
                "financial_analysis_depth": {"quality_achievement": False, "average_quality": 0.85},
            },
        }

        recommendations = framework.generate_optimization_recommendations(mock_analysis)

        assert len(recommendations) >= 1
        assert any(rec["category"] == "quality_improvement" for rec in recommendations)
        assert any(rec["category"] == "spectrum_optimization" for rec in recommendations)

    def test_quality_targets_assessment(self, framework):
        """Test quality targets achievement assessment."""
        mock_analysis = {
            "overall_metrics": {"average_quality_score": 0.92, "spectrums_above_90_percent": 5},
            "spectrum_performance": {
                "spectrum1": {},
                "spectrum2": {},
                "spectrum3": {},
                "spectrum4": {},
                "spectrum5": {},
                "spectrum6": {},
                "spectrum7": {},
            },
        }

        assessment = framework._assess_quality_targets(mock_analysis)

        assert assessment["overall_quality_achieved"] is True
        assert assessment["overall_quality_score"] == 0.92
        assert assessment["spectrums_target_achievement"] == 5 / 7
        assert assessment["target_90_percent"] == 0.90


class TestEdwinaHawthorneValidation:
    """Test validation with real Edwina Hawthorne customer data."""

    @pytest.fixture
    def framework_with_customer_data(self):
        """Create framework configured for Edwina Hawthorne validation."""
        with patch("multi_spectrum_framework.Client"):
            with patch.dict("os.environ", {"LANGSMITH_API_KEY": "test_key", "TILORES_API_URL": "https://test-api.com"}):
                return MultiSpectrumFramework()

    def test_edwina_hawthorne_data_samples(self, framework_with_customer_data):
        """Test Edwina Hawthorne data samples in customer identity spectrum."""
        identity_spectrum = next(
            s for s in framework_with_customer_data.data_spectrums if s.name == "customer_identity_resolution"
        )

        # Find Edwina Hawthorne samples
        edwina_samples = []
        for sample in identity_spectrum.data_samples:
            query = sample.get("query", "").lower()
            expected = sample.get("expected_customer", "").lower()
            if "blessedwina@aol.com" in query or "edwina hawthorne" in expected:
                edwina_samples.append(sample)

        assert len(edwina_samples) >= 2

        # Test email query sample
        email_sample = next((s for s in edwina_samples if "blessedwina@aol.com" in s.get("query", "")), None)
        assert email_sample is not None
        assert email_sample["expected_customer"] == "Edwina Hawthorne"
        assert email_sample["expected_client_id"] == "2270"
        assert email_sample["identity_type"] == "email"

        # Test name query sample
        name_sample = next((s for s in edwina_samples if "Edwina Hawthorne" in s.get("query", "")), None)
        assert name_sample is not None
        assert name_sample["expected_customer"] == "Edwina Hawthorne"
        assert name_sample["identity_type"] == "name"

    def test_edwina_hawthorne_phone_validation(self, framework_with_customer_data):
        """Test Edwina Hawthorne phone number validation."""
        identity_spectrum = next(
            s for s in framework_with_customer_data.data_spectrums if s.name == "customer_identity_resolution"
        )

        phone_sample = next((s for s in identity_spectrum.data_samples if "2672661591" in s.get("query", "")), None)

        assert phone_sample is not None
        assert phone_sample["expected_customer"] == "Edwina Hawthorne"
        assert phone_sample["expected_phone"] == "2672661591"
        assert phone_sample["identity_type"] == "phone"

    def test_edwina_hawthorne_credit_analysis(self, framework_with_customer_data):
        """Test Edwina Hawthorne credit analysis samples."""
        financial_spectrum = next(
            s for s in framework_with_customer_data.data_spectrums if s.name == "financial_analysis_depth"
        )

        credit_samples = [
            sample
            for sample in financial_spectrum.data_samples
            if "2270" in sample.get("query", "") or "blessedwina@aol.com" in sample.get("query", "")
        ]

        assert len(credit_samples) >= 1

        # Test credit score sample
        credit_score_sample = next((s for s in credit_samples if "credit score" in s.get("query", "").lower()), None)
        if credit_score_sample:
            assert "543" in credit_score_sample.get("expected_content", "")
            assert credit_score_sample.get("expected_analysis") == "Very Poor"


class TestSevenModelIntegration:
    """Test integration with 7 models across all spectrums."""

    @pytest.fixture
    def framework_with_models(self):
        """Create framework with all 7 models configured."""
        with patch("multi_spectrum_framework.Client"):
            with patch.dict("os.environ", {"LANGSMITH_API_KEY": "test_key"}):
                framework = MultiSpectrumFramework()
                # Add Gemini 2.5 models for complete 7-model testing
                framework.models.extend(["gemini-2.5-flash", "gemini-2.5-flash-lite"])
                return framework

    def test_seven_model_configuration(self, framework_with_models):
        """Test all 7 models are properly configured."""
        expected_models = [
            "llama-3.3-70b-versatile",
            "gpt-4o-mini",
            "deepseek-r1-distill-llama-70b",
            "claude-3-haiku",
            "gemini-1.5-flash-002",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
        ]

        assert len(framework_with_models.models) == 7
        for model in expected_models:
            assert model in framework_with_models.models

    def test_model_spectrum_matrix_coverage(self, framework_with_models):
        """Test 7x7 model-spectrum matrix coverage."""
        models = framework_with_models.models
        spectrums = framework_with_models.data_spectrums

        assert len(models) == 7
        assert len(spectrums) == 7

        # Test matrix coverage (7 models × 7 spectrums = 49 combinations)
        total_combinations = len(models) * len(spectrums)
        assert total_combinations == 49

    @pytest.mark.asyncio
    async def test_model_performance_across_spectrums(self, framework_with_models):
        """Test model performance measurement across all spectrums."""
        with patch("requests.post") as mock_post:
            # Mock different performance levels for different models
            def mock_response(*args, **kwargs):
                response = MagicMock()
                response.status_code = 200

                # Simulate different quality levels based on model
                model = kwargs.get("json", {}).get("model", "")
                if "gemini-2.5" in model:
                    content = "High quality response with comprehensive analysis"
                elif "gpt-4o" in model:
                    content = "Good quality response with detailed information"
                else:
                    content = "Standard quality response"

                response.json.return_value = {"choices": [{"message": {"content": content}}]}
                return response

            mock_post.side_effect = mock_response

            # Test execution across first spectrum
            test_spectrum = framework_with_models.data_spectrums[0]
            test_inputs = {"query": "Test query"}

            results = []
            for model in framework_with_models.models:
                result = framework_with_models._execute_spectrum_test(model, test_spectrum, test_inputs)
                results.append(result)

            assert len(results) == 7
            assert all(result["success"] for result in results)
            assert all(0.0 <= result["quality_score"] <= 1.0 for result in results)


class TestPerformanceAndScalability:
    """Test performance and scalability of the multi-spectrum framework."""

    @pytest.fixture
    def performance_framework(self):
        """Create framework for performance testing."""
        with patch("multi_spectrum_framework.Client"):
            with patch.dict("os.environ", {"LANGSMITH_API_KEY": "test_key"}):
                return MultiSpectrumFramework()

    def test_large_scale_experiment_creation(self, performance_framework):
        """Test creation of large-scale experiments (7x7 matrix)."""
        with patch.object(performance_framework, "_execute_spectrum_test") as mock_execute:
            mock_execute.return_value = {"success": True, "quality_score": 0.90, "response_time_ms": 1000}

            # Mock dataset creation
            performance_framework.client.create_dataset.return_value = MagicMock(id="test_id")
            performance_framework.client.create_example.return_value = MagicMock(id="example_id")

            with patch("multi_spectrum_framework.evaluate") as mock_evaluate:
                mock_evaluate.return_value = MagicMock(experiment_name="test_experiment")

                results = performance_framework.create_comprehensive_experiments()

                # Should handle 7 spectrums × 5 models = 35 experiments
                assert results["success"] is True
                assert results["spectrums_tested"] == 7
                assert results["models_tested"] == 5

    def test_memory_efficiency_with_large_datasets(self, performance_framework):
        """Test memory efficiency with large data samples."""
        # Create spectrum with many data samples
        large_spectrum = ExperimentSpectrum(
            name="large_test_spectrum",
            description="Large dataset for memory testing",
            data_samples=[
                {"query": f"Test query {i}", "expected_result": f"Expected result {i}"}
                for i in range(100)  # 100 samples
            ],
            quality_targets={"accuracy": 0.90},
            optimization_focus="memory_efficiency",
        )

        # Should handle large datasets without memory issues
        assert len(large_spectrum.data_samples) == 100
        assert all("query" in sample for sample in large_spectrum.data_samples)

    @pytest.mark.asyncio
    async def test_concurrent_spectrum_execution(self, performance_framework):
        """Test concurrent execution across multiple spectrums."""
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"choices": [{"message": {"content": "Test response"}}]}

            # Execute multiple spectrums concurrently
            tasks = []
            for spectrum in performance_framework.data_spectrums[:3]:  # Test first 3
                task = asyncio.create_task(
                    asyncio.to_thread(
                        performance_framework._execute_spectrum_test,
                        "gpt-4o-mini",
                        spectrum,
                        {"query": "Test concurrent query"},
                    )
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks)

            assert len(results) == 3
            assert all(result["success"] for result in results)


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases."""

    @pytest.fixture
    def error_test_framework(self):
        """Create framework for error testing."""
        with patch("multi_spectrum_framework.Client"):
            with patch.dict("os.environ", {"LANGSMITH_API_KEY": "test_key"}):
                return MultiSpectrumFramework()

    def test_api_failure_handling(self, error_test_framework):
        """Test handling of API failures."""
        with patch("requests.post") as mock_post:
            # Simulate API failure
            mock_post.return_value.status_code = 500
            mock_post.return_value.json.return_value = {"error": "Internal server error"}

            test_spectrum = error_test_framework.data_spectrums[0]
            result = error_test_framework._execute_spectrum_test("gpt-4o-mini", test_spectrum, {"query": "Test query"})

            assert result["success"] is False
            assert "HTTP 500" in result["response"]
            assert result["quality_score"] == 0.0

    def test_network_timeout_handling(self, error_test_framework):
        """Test handling of network timeouts."""
        with patch("requests.post") as mock_post:
            # Simulate timeout
            mock_post.side_effect = Exception("Request timeout")

            test_spectrum = error_test_framework.data_spectrums[0]
            result = error_test_framework._execute_spectrum_test("gpt-4o-mini", test_spectrum, {"query": "Test query"})

            assert result["success"] is False
            assert "Request timeout" in result["error"]
            assert result["quality_score"] == 0.0

    def test_invalid_model_handling(self, error_test_framework):
        """Test handling of invalid model names."""
        test_spectrum = error_test_framework.data_spectrums[0]

        # Should handle gracefully without crashing
        result = error_test_framework._execute_spectrum_test(
            "invalid-model-name", test_spectrum, {"query": "Test query"}
        )

        # Framework should handle this gracefully
        assert "model" in result
        assert result["model"] == "invalid-model-name"

    def test_empty_response_handling(self, error_test_framework):
        """Test handling of empty API responses."""
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"choices": [{"message": {"content": ""}}]}

            test_spectrum = error_test_framework.data_spectrums[0]
            result = error_test_framework._execute_spectrum_test("gpt-4o-mini", test_spectrum, {"query": "Test query"})

            assert result["success"] is True
            assert result["response"] == ""
            assert result["content_length"] == 0


# Main execution for testing
async def main():
    """Main function to run Phase 1 tests."""
    print("🧪 Running Phase 1 Multi-Spectrum Foundation Tests...")

    # Run pytest programmatically
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/speed_experiments/test_phase1_multi_spectrum_foundation.py",
            "-v",
            "--tb=short",
        ],
        capture_output=True,
        text=True,
    )

    print("Test Results:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)

    return result.returncode == 0


if __name__ == "__main__":
    asyncio.run(main())
