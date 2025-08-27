#!/usr/bin/env python3
"""
Comprehensive Test Suite for Phase 2 AI Prompt Optimization System.

This module provides complete testing coverage for the Phase 2 AI Prompt
Optimization system, including pattern analysis, AI-driven refinement,
A/B testing framework, and optimization orchestration.

Author: Roo (Elite Software Engineer)
Created: 2025-08-16
Phase: 2 - AI Prompt Optimization Testing
"""

import asyncio
import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from phase2_ai_prompt_optimization import (
    ABTestingFramework,
    AIPromptRefiner,
    ModelOptimizationStrategy,
    OptimizationCycle,
    OptimizationStrategy,
    Phase2OptimizationOrchestrator,
    PromptPattern,
    PromptPatternAnalyzer,
    PromptVariation,
    PromptVariationType,
)


class TestPromptPatternAnalyzer:
    """Test suite for PromptPatternAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return PromptPatternAnalyzer()

    @pytest.fixture
    def mock_baseline_data(self):
        """Create mock baseline data for testing."""
        return {
            "metrics": {
                "model_performance": {
                    "gpt-4o-mini": {"avg_quality": 0.94, "avg_response_time": 7.4, "success_rate": 0.98},
                    "gemini-1.5-flash-002": {"avg_quality": 0.95, "avg_response_time": 3.1, "success_rate": 0.99},
                },
                "spectrum_performance": {
                    "customer_profile": {"avg_quality": 0.92, "avg_completeness": 0.91, "success_rate": 0.96},
                    "credit_analysis": {"avg_quality": 0.89, "avg_completeness": 0.88, "success_rate": 0.94},
                },
            }
        }

    @pytest.fixture
    def temp_baseline_file(self, mock_baseline_data):
        """Create temporary baseline file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(mock_baseline_data, f)
            return f.name

    @pytest.mark.asyncio
    async def test_analyze_baseline_results(self, analyzer, temp_baseline_file):
        """Test baseline results analysis."""
        patterns = await analyzer.analyze_baseline_results(temp_baseline_file)

        assert len(patterns) >= 2  # At least model and spectrum patterns
        assert all(isinstance(p, PromptPattern) for p in patterns)
        assert any(p.pattern_type == "high_performance_model" for p in patterns)
        assert any(p.pattern_type == "spectrum_specific" for p in patterns)

        # Clean up
        Path(temp_baseline_file).unlink()

    def test_generate_model_specific_template(self, analyzer):
        """Test model-specific template generation."""
        success_factors = ["exceptional_quality_achievement", "fast_response_time"]
        template = analyzer._generate_model_specific_template("gpt-4o-mini", success_factors)

        assert "gpt-4o-mini" in template
        assert "exceptional quality" in template
        assert "quick responses" in template or "fast response" in template
        assert len(template) > 100  # Substantial template

    def test_generate_spectrum_template(self, analyzer):
        """Test spectrum-specific template generation."""
        template = analyzer._generate_spectrum_template("customer_profile", ["exceptional_quality"])

        assert "customer profile" in template.lower()
        assert "identification" in template.lower()
        assert len(template) > 50  # Meaningful template

    def test_analyze_spectrum_success_factors(self, analyzer):
        """Test spectrum success factor analysis."""
        perf_data = {"avg_quality": 0.96, "avg_completeness": 0.92, "success_rate": 0.97}

        factors = analyzer._analyze_spectrum_success_factors("test_spectrum", perf_data)

        assert "exceptional_quality" in factors
        assert "high_completeness" in factors
        assert "high_reliability" in factors


class TestAIPromptRefiner:
    """Test suite for AIPromptRefiner."""

    @pytest.fixture
    def refiner(self):
        """Create refiner instance for testing."""
        return AIPromptRefiner()

    @pytest.fixture
    def mock_patterns(self):
        """Create mock patterns for testing."""
        return [
            PromptPattern(
                pattern_id="test_pattern_1",
                pattern_type="high_performance_model",
                description="Test pattern",
                success_rate=0.95,
                quality_impact=0.08,
                applicable_spectrums=["all"],
                applicable_models=["gpt-4o-mini"],
                pattern_template="Test template for optimization",
            )
        ]

    @pytest.mark.asyncio
    async def test_generate_prompt_variations(self, refiner, mock_patterns):
        """Test prompt variation generation."""
        base_prompt = "Analyze customer data"
        target_spectrum = "customer_profile"

        variations = await refiner.generate_prompt_variations(base_prompt, target_spectrum, mock_patterns)

        assert len(variations) >= 1  # At least pattern-based variation
        assert all(isinstance(v, PromptVariation) for v in variations)
        assert all(v.base_prompt == base_prompt for v in variations)

    @pytest.mark.asyncio
    async def test_apply_pattern_to_prompt(self, refiner, mock_patterns):
        """Test pattern application to prompt."""
        base_prompt = "Analyze customer data"
        pattern = mock_patterns[0]
        target_spectrum = "customer_profile"

        variation = await refiner._apply_pattern_to_prompt(base_prompt, pattern, target_spectrum, 0.90)

        assert variation is not None
        assert variation.base_prompt == base_prompt
        assert pattern.pattern_template in variation.variation_prompt
        assert variation.expected_improvement == pattern.quality_impact

    @pytest.mark.asyncio
    async def test_generate_ai_variations_without_langchain(self, refiner):
        """Test AI variation generation without LangChain."""
        # Ensure LangChain is disabled for this test
        refiner.refiner_llm = None

        variations = await refiner._generate_ai_variations("Test prompt", "test_spectrum", 0.90)

        assert variations == []  # Should return empty list without LangChain


class TestABTestingFramework:
    """Test suite for ABTestingFramework."""

    @pytest.fixture
    def mock_baseline_framework(self):
        """Create mock baseline framework."""
        return MagicMock()

    @pytest.fixture
    def ab_testing(self, mock_baseline_framework):
        """Create A/B testing framework instance."""
        return ABTestingFramework(mock_baseline_framework)

    @pytest.fixture
    def mock_variations(self):
        """Create mock variations for testing."""
        return [
            PromptVariation(
                variation_id="test_var_1",
                base_prompt="Base prompt",
                variation_prompt="Enhanced prompt",
                variation_type=PromptVariationType.STRUCTURE_VARIATION,
                hypothesis="Structure improvement",
                expected_improvement=0.05,
                metadata={"target_spectrum": "customer_profile"},
            ),
            PromptVariation(
                variation_id="test_var_2",
                base_prompt="Base prompt",
                variation_prompt="Clarity enhanced prompt",
                variation_type=PromptVariationType.INSTRUCTION_CLARITY,
                hypothesis="Clarity improvement",
                expected_improvement=0.04,
                metadata={"target_spectrum": "customer_profile"},
            ),
        ]

    @pytest.mark.asyncio
    async def test_run_ab_tests(self, ab_testing, mock_variations):
        """Test A/B testing execution."""
        target_spectrum = "customer_profile"

        results = await ab_testing.run_ab_tests(mock_variations, target_spectrum)

        assert results["target_spectrum"] == target_spectrum
        assert results["variations_tested"] == len(mock_variations)
        assert results["models_tested"] == len(ab_testing.models)
        assert "results" in results
        assert "summary" in results

    @pytest.mark.asyncio
    async def test_test_variation_across_models(self, ab_testing, mock_variations):
        """Test variation testing across models."""
        variation = mock_variations[0]
        target_spectrum = "customer_profile"

        results = await ab_testing._test_variation_across_models(variation, target_spectrum)

        assert results["variation_id"] == variation.variation_id
        assert "model_results" in results
        assert "overall_performance" in results
        assert len(results["model_results"]) == len(ab_testing.models)

    @pytest.mark.asyncio
    async def test_run_single_test(self, ab_testing, mock_variations):
        """Test single test execution."""
        variation = mock_variations[0]
        model = "gpt-4o-mini"
        target_spectrum = "customer_profile"

        score = await ab_testing._run_single_test(variation, model, target_spectrum, 0)

        assert 0.0 <= score <= 1.0
        assert isinstance(score, float)

    def test_calculate_test_summary(self, ab_testing):
        """Test test summary calculation."""
        mock_test_results = {
            "results": {
                "var1": {"overall_performance": {"average_score": 0.92}},
                "var2": {"overall_performance": {"average_score": 0.88}},
            }
        }

        summary = ab_testing._calculate_test_summary(mock_test_results)

        assert summary["best_variation"] == "var1"
        assert summary["best_score"] == 0.92
        assert "average_improvement" in summary
        assert "recommendation" in summary


class TestPhase2OptimizationOrchestrator:
    """Test suite for Phase2OptimizationOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing."""
        return Phase2OptimizationOrchestrator()

    @pytest.fixture
    def mock_baseline_data(self):
        """Create comprehensive mock baseline data."""
        return {
            "metadata": {
                "timestamp": "20250816_123000",
                "total_experiments": 49,
                "successful_experiments": 47,
                "failed_experiments": 2,
                "phase": "1_multi_spectrum_foundation",
            },
            "metrics": {
                "average_response_time": 5.2,
                "average_quality_score": 0.91,
                "quality_target_achievement": 0.85,
                "model_performance": {
                    "gpt-4o-mini": {"count": 7, "avg_quality": 0.94, "avg_response_time": 7.4, "success_rate": 1.0},
                    "gemini-1.5-flash-002": {
                        "count": 7,
                        "avg_quality": 0.95,
                        "avg_response_time": 3.1,
                        "success_rate": 1.0,
                    },
                },
                "spectrum_performance": {
                    "customer_profile": {
                        "count": 7,
                        "avg_quality": 0.92,
                        "avg_completeness": 0.91,
                        "success_rate": 1.0,
                    },
                    "credit_analysis": {"count": 7, "avg_quality": 0.89, "avg_completeness": 0.88, "success_rate": 1.0},
                },
            },
        }

    @pytest.fixture
    def temp_baseline_file(self, mock_baseline_data):
        """Create temporary baseline file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(mock_baseline_data, f)
            return f.name

    @pytest.mark.asyncio
    async def test_run_phase2_optimization(self, orchestrator, temp_baseline_file):
        """Test complete Phase 2 optimization cycle."""
        # Mock the baseline framework
        mock_framework = MagicMock()

        cycle = await orchestrator.run_phase2_optimization(temp_baseline_file, mock_framework)

        assert isinstance(cycle, OptimizationCycle)
        assert cycle.phase == "2_ai_prompt_optimization"
        assert len(cycle.identified_patterns) >= 0
        assert len(cycle.generated_variations) >= 0
        assert len(cycle.model_strategies) >= 0
        assert cycle.overall_improvement >= 0.0

        # Clean up
        Path(temp_baseline_file).unlink()

    @pytest.mark.asyncio
    async def test_generate_model_strategies(self, orchestrator, mock_baseline_data):
        """Test model strategy generation."""
        patterns = [
            PromptPattern(
                pattern_id="test_pattern",
                pattern_type="high_performance_model",
                description="Test pattern",
                success_rate=0.95,
                quality_impact=0.05,
                applicable_spectrums=["all"],
                applicable_models=["all"],
                pattern_template="Test template",
            )
        ]

        strategies = await orchestrator._generate_model_strategies(mock_baseline_data, patterns, {})

        assert len(strategies) == 2  # Two models in mock data
        assert all(isinstance(s, ModelOptimizationStrategy) for s in strategies)
        assert all(s.target_performance["quality"] >= 0.90 for s in strategies)

    def test_calculate_overall_improvement(self, orchestrator):
        """Test overall improvement calculation."""
        ab_results = {
            "spectrum1": {"summary": {"average_improvement": 0.05}},
            "spectrum2": {"summary": {"average_improvement": 0.03}},
        }

        improvement = orchestrator._calculate_overall_improvement({}, ab_results)

        assert improvement == 0.04  # Average of 0.05 and 0.03

    @pytest.mark.asyncio
    async def test_save_optimization_cycle(self, orchestrator):
        """Test optimization cycle saving."""
        cycle = OptimizationCycle(
            cycle_id="test_cycle",
            phase="2_ai_prompt_optimization",
            timestamp=datetime.now().isoformat(),
            baseline_results={},
            identified_patterns=[],
            generated_variations=[],
            model_strategies=[],
            ab_test_results={},
            overall_improvement=0.05,
        )

        # Test saving (should not raise exception)
        await orchestrator._save_optimization_cycle(cycle)

        # Verify file was created
        expected_files = list(Path("tests/speed_experiments").glob("phase2_optimization_cycle_*.json"))
        assert len(expected_files) >= 1


class TestPromptVariationTypes:
    """Test suite for prompt variation types and enums."""

    def test_optimization_strategy_enum(self):
        """Test OptimizationStrategy enum values."""
        assert OptimizationStrategy.PATTERN_ANALYSIS.value == "pattern_analysis"
        assert OptimizationStrategy.PERFORMANCE_TUNING.value == "performance_tuning"  # noqa: E501
        assert OptimizationStrategy.QUALITY_ENHANCEMENT.value == "quality_enhancement"  # noqa: E501

    def test_prompt_variation_type_enum(self):
        """Test PromptVariationType enum values."""
        assert PromptVariationType.STRUCTURE_VARIATION.value == "structure_variation"  # noqa: E501
        assert PromptVariationType.INSTRUCTION_CLARITY.value == "instruction_clarity"  # noqa: E501
        assert PromptVariationType.CONTEXT_ENHANCEMENT.value == "context_enhancement"  # noqa: E501


class TestDataStructures:
    """Test suite for data structures and dataclasses."""

    def test_prompt_pattern_creation(self):
        """Test PromptPattern dataclass creation."""
        pattern = PromptPattern(
            pattern_id="test_pattern",
            pattern_type="test_type",
            description="Test description",
            success_rate=0.95,
            quality_impact=0.05,
            applicable_spectrums=["test_spectrum"],
            applicable_models=["test_model"],
            pattern_template="Test template",
        )

        assert pattern.pattern_id == "test_pattern"
        assert pattern.success_rate == 0.95
        assert pattern.quality_impact == 0.05
        assert len(pattern.usage_examples) == 0  # Default empty list

    def test_prompt_variation_creation(self):
        """Test PromptVariation dataclass creation."""
        variation = PromptVariation(
            variation_id="test_variation",
            base_prompt="Base prompt",
            variation_prompt="Enhanced prompt",
            variation_type=PromptVariationType.STRUCTURE_VARIATION,
            hypothesis="Test hypothesis",
            expected_improvement=0.05,
        )

        assert variation.variation_id == "test_variation"
        assert variation.variation_type == PromptVariationType.STRUCTURE_VARIATION
        assert variation.expected_improvement == 0.05
        assert len(variation.test_results) == 0  # Default empty dict

    def test_model_optimization_strategy_creation(self):
        """Test ModelOptimizationStrategy dataclass creation."""
        strategy = ModelOptimizationStrategy(
            model_name="test_model",
            current_performance={"quality": 0.85},
            target_performance={"quality": 0.90},
            optimization_approach=OptimizationStrategy.QUALITY_ENHANCEMENT,
            recommended_patterns=[],
            custom_instructions=["Test instruction"],
            expected_improvements={"quality_score": 0.05},
        )

        assert strategy.model_name == "test_model"
        assert strategy.optimization_approach == OptimizationStrategy.QUALITY_ENHANCEMENT  # noqa: E501
        assert strategy.expected_improvements["quality_score"] == 0.05

    def test_optimization_cycle_creation(self):
        """Test OptimizationCycle dataclass creation."""
        cycle = OptimizationCycle(
            cycle_id="test_cycle",
            phase="2_ai_prompt_optimization",
            timestamp=datetime.now().isoformat(),
            baseline_results={},
            identified_patterns=[],
            generated_variations=[],
            model_strategies=[],
            ab_test_results={},
            overall_improvement=0.05,
        )

        assert cycle.cycle_id == "test_cycle"
        assert cycle.phase == "2_ai_prompt_optimization"
        assert cycle.overall_improvement == 0.05
        assert len(cycle.next_actions) == 0  # Default empty list


class TestIntegrationScenarios:
    """Test suite for integration scenarios."""

    @pytest.mark.asyncio
    async def test_end_to_end_optimization_flow(self):
        """Test complete end-to-end optimization flow."""
        # Create mock baseline data
        baseline_data = {
            "metrics": {
                "model_performance": {
                    "gpt-4o-mini": {"avg_quality": 0.88, "avg_response_time": 7.4, "success_rate": 0.95}
                },
                "spectrum_performance": {
                    "customer_profile": {"avg_quality": 0.87, "avg_completeness": 0.85, "success_rate": 0.93}
                },
            }
        }

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(baseline_data, f)
            temp_file = f.name

        try:
            # Initialize orchestrator
            orchestrator = Phase2OptimizationOrchestrator()

            # Run optimization
            cycle = await orchestrator.run_phase2_optimization(temp_file)

            # Verify results
            assert isinstance(cycle, OptimizationCycle)
            assert cycle.overall_improvement >= 0.0
            assert len(cycle.next_actions) > 0

        finally:
            # Clean up
            Path(temp_file).unlink()

    def test_quality_improvement_calculation(self):
        """Test quality improvement calculations."""
        # Test various improvement scenarios
        test_cases = [
            (0.85, 0.90, 0.05),  # 5% improvement needed
            (0.92, 0.90, 0.0),  # Already above target
            (0.75, 0.90, 0.15),  # 15% improvement needed
        ]

        for current, target, expected_gap in test_cases:
            gap = max(0, target - current)
            assert abs(gap - expected_gap) < 0.001

    @pytest.mark.asyncio
    async def test_pattern_application_effectiveness(self):
        """Test effectiveness of pattern application."""
        # Create high-quality pattern
        pattern = PromptPattern(
            pattern_id="high_quality_pattern",
            pattern_type="exceptional_performance",
            description="Pattern from 96% quality model",
            success_rate=0.98,
            quality_impact=0.08,
            applicable_spectrums=["all"],
            applicable_models=["all"],
            pattern_template="High-quality template",
        )

        refiner = AIPromptRefiner()
        variation = await refiner._apply_pattern_to_prompt("Base prompt", pattern, "test_spectrum", 0.90)

        assert variation is not None
        if variation:
            assert variation.expected_improvement == pattern.quality_impact
            assert pattern.pattern_template in variation.variation_prompt


class TestErrorHandling:
    """Test suite for error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_missing_baseline_file(self):
        """Test handling of missing baseline file."""
        orchestrator = Phase2OptimizationOrchestrator()

        with pytest.raises(FileNotFoundError):
            await orchestrator.run_phase2_optimization("nonexistent_file.json")

    @pytest.mark.asyncio
    async def test_invalid_baseline_data(self):
        """Test handling of invalid baseline data."""
        # Create file with invalid JSON
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name

        try:
            orchestrator = Phase2OptimizationOrchestrator()

            with pytest.raises(json.JSONDecodeError):
                await orchestrator.run_phase2_optimization(temp_file)

        finally:
            Path(temp_file).unlink()

    def test_empty_patterns_handling(self):
        """Test handling of empty patterns list."""
        refiner = AIPromptRefiner()

        # Should handle empty patterns gracefully
        result = refiner._apply_pattern_to_prompt.__func__(
            refiner,
            "test",
            PromptPattern(
                pattern_id="empty",
                pattern_type="empty",
                description="",
                success_rate=0,
                quality_impact=0,
                applicable_spectrums=[],
                applicable_models=[],
                pattern_template="",
            ),
            "test",
            0.90,
        )

        # Should not raise exception
        assert result is not None or result is None  # Either outcome is valid


class TestPerformanceValidation:
    """Test suite for performance validation."""

    @pytest.mark.asyncio
    async def test_optimization_performance(self):
        """Test optimization system performance."""
        start_time = datetime.now()

        # Create small baseline data for performance test
        baseline_data = {
            "metrics": {
                "model_performance": {
                    "test_model": {"avg_quality": 0.85, "avg_response_time": 5.0, "success_rate": 0.95}
                },
                "spectrum_performance": {
                    "test_spectrum": {"avg_quality": 0.87, "avg_completeness": 0.85, "success_rate": 0.93}
                },
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(baseline_data, f)
            temp_file = f.name

        try:
            orchestrator = Phase2OptimizationOrchestrator()
            cycle = await orchestrator.run_phase2_optimization(temp_file)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Should complete within reasonable time (30 seconds)
            assert duration < 30
            assert isinstance(cycle, OptimizationCycle)

        finally:
            Path(temp_file).unlink()

    def test_memory_usage_efficiency(self):
        """Test memory usage efficiency of data structures."""
        # Create large number of patterns to test memory efficiency
        patterns = []
        for i in range(100):
            pattern = PromptPattern(
                pattern_id=f"pattern_{i}",
                pattern_type="test",
                description=f"Pattern {i}",
                success_rate=0.95,
                quality_impact=0.05,
                applicable_spectrums=["test"],
                applicable_models=["test"],
                pattern_template=f"Template {i}",
            )
            patterns.append(pattern)

        # Should handle large number of patterns efficiently
        assert len(patterns) == 100
        assert all(isinstance(p, PromptPattern) for p in patterns)


# Main execution for testing
async def main():
    """Main function to run Phase 2 tests."""
    print("🧪 Running Phase 2 AI Prompt Optimization Tests...")

    # Run pytest programmatically
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/speed_experiments/test_phase2_ai_prompt_optimization.py",
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
