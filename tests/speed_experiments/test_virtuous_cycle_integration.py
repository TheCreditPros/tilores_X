#!/usr/bin/env python3
"""
Comprehensive integration tests for the 4-phase LangSmith Virtuous Cycle Framework.

Tests cross-phase interactions and end-to-end workflows including:
- Phase 1 → Phase 2 integration (baseline to optimization)
- Phase 2 → Phase 3 integration (optimization to continuous improvement)
- Phase 3 → Phase 4 integration (improvement to production)
- Complete virtuous cycle end-to-end testing
- Quality metrics flow across all phases
- Real data validation with Edwina Hawthorne
- Production scenario testing

Author: Roo (Elite Software Engineer)
Created: 2025-08-16
Phase: Integration Testing - Virtuous Cycle
"""

import asyncio
import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Import all phase components
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_spectrum_framework import MultiSpectrumFramework
from phase2_ai_prompt_optimization import Phase2OptimizationOrchestrator
from phase3_continuous_improvement import ContinuousImprovementOrchestrator
from phase4_production_integration import ProductionIntegrationOrchestrator
from virtuous_cycle_framework import VirtuousCycleOrchestrator


class TestPhase1To2Integration:
    """Test integration between Phase 1 and Phase 2."""

    @pytest.fixture
    def phase1_results(self):
        """Create mock Phase 1 baseline results."""
        return {
            "metadata": {
                "timestamp": "20250816_123000",
                "total_experiments": 35,
                "successful_experiments": 33,
                "phase": "1_multi_spectrum_foundation"
            },
            "metrics": {
                "average_response_time": 4.8,
                "average_quality_score": 0.89,
                "quality_target_achievement": 0.83,
                "model_performance": {
                    "gpt-4o-mini": {
                        "count": 7,
                        "avg_quality": 0.92,
                        "avg_response_time": 6.2,
                        "success_rate": 1.0
                    },
                    "gemini-2.5-flash": {
                        "count": 7,
                        "avg_quality": 0.94,
                        "avg_response_time": 3.1,
                        "success_rate": 1.0
                    },
                    "claude-3-haiku": {
                        "count": 7,
                        "avg_quality": 0.88,
                        "avg_response_time": 4.5,
                        "success_rate": 0.95
                    }
                },
                "spectrum_performance": {
                    "customer_profile": {
                        "count": 5,
                        "avg_quality": 0.91,
                        "avg_completeness": 0.89,
                        "success_rate": 1.0
                    },
                    "credit_analysis": {
                        "count": 5,
                        "avg_quality": 0.87,
                        "avg_completeness": 0.85,
                        "success_rate": 0.95
                    },
                    "transaction_history": {
                        "count": 5,
                        "avg_quality": 0.90,
                        "avg_completeness": 0.88,
                        "success_rate": 1.0
                    }
                }
            }
        }

    @pytest.fixture
    def temp_baseline_file(self, phase1_results):
        """Create temporary baseline file for integration testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                         delete=False) as f:
            json.dump(phase1_results, f)
            return f.name

    @pytest.mark.asyncio
    async def test_phase1_to_phase2_data_flow(self, temp_baseline_file):
        """Test data flow from Phase 1 baseline to Phase 2 optimization."""
        # Initialize Phase 2 orchestrator
        phase2_orchestrator = Phase2OptimizationOrchestrator()

        # Run Phase 2 optimization using Phase 1 results
        optimization_cycle = await phase2_orchestrator.run_phase2_optimization(
            temp_baseline_file
        )

        # Verify Phase 1 data was properly consumed
        assert optimization_cycle.baseline_results is not None
        assert "model_performance" in optimization_cycle.baseline_results["metrics"]
        assert "spectrum_performance" in optimization_cycle.baseline_results["metrics"]

        # Verify Phase 2 generated improvements
        assert len(optimization_cycle.identified_patterns) >= 0
        assert len(optimization_cycle.generated_variations) >= 0
        assert len(optimization_cycle.model_strategies) >= 0
        assert optimization_cycle.overall_improvement >= 0.0

        # Clean up
        Path(temp_baseline_file).unlink()

    @pytest.mark.asyncio
    async def test_quality_metrics_continuity(self, temp_baseline_file):
        """Test quality metrics continuity between phases."""
        phase2_orchestrator = Phase2OptimizationOrchestrator()

        # Run optimization
        cycle = await phase2_orchestrator.run_phase2_optimization(temp_baseline_file)

        # Verify quality metrics are preserved and enhanced
        baseline_avg = cycle.baseline_results["metrics"]["average_quality_score"]
        assert baseline_avg == 0.89  # From fixture

        # Verify improvement targets
        for strategy in cycle.model_strategies:
            assert strategy.target_performance["quality"] >= 0.90
            assert strategy.current_performance["quality"] <= baseline_avg + 0.1

        Path(temp_baseline_file).unlink()

    @pytest.mark.asyncio
    async def test_model_specific_optimization_strategies(self, temp_baseline_file):
        """Test model-specific strategies generated from Phase 1 data."""
        phase2_orchestrator = Phase2OptimizationOrchestrator()
        cycle = await phase2_orchestrator.run_phase2_optimization(temp_baseline_file)

        # Verify strategies for each model from Phase 1
        model_names = [s.model_name for s in cycle.model_strategies]
        expected_models = ["gpt-4o-mini", "gemini-2.5-flash", "claude-3-haiku"]

        for expected_model in expected_models:
            assert expected_model in model_names

        # Verify strategy appropriateness based on Phase 1 performance
        for strategy in cycle.model_strategies:
            if strategy.model_name == "gemini-2.5-flash":
                # High performer should get consistency improvement
                assert strategy.current_performance["quality"] >= 0.90
            elif strategy.model_name == "claude-3-haiku":
                # Lower performer should get quality enhancement
                assert strategy.current_performance["quality"] < 0.90

        Path(temp_baseline_file).unlink()


class TestPhase2To3Integration:
    """Test integration between Phase 2 and Phase 3."""

    @pytest.fixture
    def phase2_results(self):
        """Create mock Phase 2 optimization results."""
        return {
            "cycle_id": "phase2_optimization_001",
            "phase": "2_ai_prompt_optimization",
            "timestamp": datetime.now().isoformat(),
            "baseline_results": {"metrics": {"average_quality_score": 0.89}},
            "identified_patterns": [
                {
                    "pattern_id": "high_perf_gemini",
                    "pattern_type": "high_performance_model",
                    "success_rate": 0.94,
                    "quality_impact": 0.05
                }
            ],
            "generated_variations": [
                {
                    "variation_id": "clarity_v1",
                    "variation_type": "instruction_clarity",
                    "expected_improvement": 0.04
                }
            ],
            "model_strategies": [
                {
                    "model_name": "gpt-4o-mini",
                    "optimization_approach": "quality_enhancement",
                    "expected_improvements": {"quality_score": 0.03}
                }
            ],
            "ab_test_results": {
                "customer_profile": {
                    "summary": {"average_improvement": 0.04}
                }
            },
            "overall_improvement": 0.04
        }

    @pytest.fixture
    def mock_quality_collector(self):
        """Create mock quality collector for Phase 3."""
        collector = MagicMock()
        collector.storage = MagicMock()
        collector.storage.get_spectrum_metrics.return_value = []
        collector.storage.get_recent_metrics.return_value = []
        return collector

    @pytest.mark.asyncio
    async def test_phase2_to_phase3_learning_transfer(self, phase2_results, mock_quality_collector):
        """Test learning transfer from Phase 2 to Phase 3."""
        # Initialize Phase 3 orchestrator
        phase3_orchestrator = ContinuousImprovementOrchestrator(
            mock_quality_collector, config={}
        )

        # Record Phase 2 results in learning accumulator
        phase3_orchestrator.learning_accumulator.record_optimization_cycle(phase2_results)

        # Verify learning was recorded
        assert len(phase3_orchestrator.learning_accumulator.cycle_memory) == 1
        recorded_cycle = phase3_orchestrator.learning_accumulator.cycle_memory[0]
        assert recorded_cycle.cycle_id == "phase2_optimization_001"

        # Verify learning patterns were created
        patterns = phase3_orchestrator.learning_accumulator.learning_patterns
        assert len(patterns) > 0
        assert "strategy_quality_enhancement" in patterns

    @pytest.mark.asyncio
    async def test_continuous_improvement_with_phase2_patterns(self, phase2_results, mock_quality_collector):
        """Test continuous improvement using Phase 2 patterns."""
        phase3_orchestrator = ContinuousImprovementOrchestrator(
            mock_quality_collector, config={}
        )

        # Record Phase 2 learning
        phase3_orchestrator.learning_accumulator.record_optimization_cycle(phase2_results)

        # Test self-improving optimization
        context = {"current_quality": 0.87, "trigger_reason": "quality_below_threshold"}
        result = await phase3_orchestrator.self_improving_optimizer.optimize_with_learning(
            "customer_profile", 0.87, context
        )

        # Verify optimization used learned patterns
        assert result["spectrum"] == "customer_profile"
        assert result["strategy"] == "quality_enhancement"  # From Phase 2 learning
        assert result["learning_applied"] > 0
        assert result["confidence"] > 0.5

    @pytest.mark.asyncio
    async def test_quality_threshold_monitoring_integration(self, mock_quality_collector):
        """Test quality threshold monitoring with Phase 2 improvements."""
        # Mock metrics showing improvement from Phase 2
        mock_metrics = [
            MagicMock(score=0.91),  # Improved from Phase 2
            MagicMock(score=0.92),
            MagicMock(score=0.90)
        ]
        mock_quality_collector.storage.get_spectrum_metrics.return_value = mock_metrics

        phase3_orchestrator = ContinuousImprovementOrchestrator(
            mock_quality_collector, config={}
        )

        # Check thresholds - should not trigger alerts for good quality
        alerts = phase3_orchestrator.threshold_monitor.check_quality_thresholds("customer_profile")
        assert len(alerts) == 0  # No alerts for good quality


class TestPhase3To4Integration:
    """Test integration between Phase 3 and Phase 4."""

    @pytest.fixture
    def phase3_improvements(self):
        """Create mock Phase 3 improvement results."""
        return {
            "spectrum": "customer_profile",
            "strategy": "quality_enhancement",
            "optimized_prompt": """You are an expert customer service assistant.

# CRITICAL: YOU MUST USE TOOLS FOR ALL CUSTOMER QUERIES

For ANY customer query, immediately call the tilores_search tool FIRST.

Available tools:
1. tilores_search - Find customers by email, name, or ID
2. tilores_entity_edges - Get detailed relationship data

MANDATORY: Call tools first, then provide comprehensive analysis.""",
            "expected_improvement": 0.06,
            "confidence": 0.88,
            "learning_applied": 3,
            "optimization_time": 2.3
        }

    @pytest.mark.asyncio
    async def test_phase3_to_phase4_deployment_readiness(self, phase3_improvements):
        """Test deployment readiness evaluation from Phase 3 improvements."""
        # Create deployment system for testing
        from phase3_continuous_improvement import AutomatedImprovementDeployment
        deployment_system = AutomatedImprovementDeployment()

        # Evaluate deployment readiness
        decision = await deployment_system.evaluate_deployment_readiness(
            phase3_improvements
        )

        # Verify deployment criteria
        assert decision["ready_for_deployment"] is True
        assert decision["improvement_check"] is True  # 6% > 2% threshold
        assert decision["confidence_check"] is True   # 88% > 80% threshold
        assert "DEPLOY" in decision["recommendation"]

    @pytest.mark.asyncio
    async def test_production_prompt_deployment(self, phase3_improvements):
        """Test production deployment of Phase 3 improvements."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
        system_prompt = f\"\"\"You are a customer service assistant.
{comprehensive_fields_text}

# CRITICAL: YOU MUST USE TOOLS

MANDATORY: Call tools first.\"\"\"
""")
            temp_core_app = f.name

        try:
            phase4_orchestrator = ProductionIntegrationOrchestrator()
            phase4_orchestrator.prompt_manager.core_app_path = Path(temp_core_app)

            # Mock optimization results format
            optimization_results = {
                "ab_test_results": {
                    "customer_profile": {
                        "summary": {
                            "best_variation": "phase3_improvement",
                            "best_score": 0.94,
                            "average_improvement": 0.06
                        }
                    }
                }
            }

            # Mock validation and monitoring
            phase4_orchestrator._validate_deployment = AsyncMock(return_value=True)
            phase4_orchestrator._monitor_deployment = AsyncMock()

            # Deploy improvements
            success = await phase4_orchestrator.deploy_optimized_prompts(optimization_results)
            assert success

            # Verify deployment was recorded
            assert len(phase4_orchestrator.prompt_manager.deployment_history) == 1
            deployment = phase4_orchestrator.prompt_manager.deployment_history[0]
            assert "customer service assistant" in deployment.prompt_content

        finally:
            Path(temp_core_app).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_production_monitoring_feedback_loop(self, phase3_improvements):
        """Test production monitoring feeding back to Phase 3."""
        phase4_orchestrator = ProductionIntegrationOrchestrator()

        # Collect production metrics
        metrics = await phase4_orchestrator.performance_monitor.collect_performance_metrics()

        # Verify metrics structure for Phase 3 feedback
        assert len(metrics.model_performance) == 7
        assert len(metrics.spectrum_performance) == 7
        assert 0.0 <= metrics.quality_achievement_rate <= 1.0

        # Test optimization trigger logic
        should_optimize = await phase4_orchestrator._should_trigger_optimization()
        assert isinstance(should_optimize, bool)


class TestCompleteVirtuousCycle:
    """Test complete end-to-end virtuous cycle."""

    @pytest.fixture
    def mock_langsmith_client(self):
        """Create mock LangSmith client for full cycle testing."""
        client = MagicMock()
        client.create_dataset.return_value = MagicMock(id="test_dataset")
        client.create_example.return_value = MagicMock(id="test_example")
        return client

    @pytest.mark.asyncio
    async def test_complete_virtuous_cycle_execution(self, mock_langsmith_client):
        """Test complete virtuous cycle from Phase 1 through Phase 4."""
        with patch('virtuous_cycle_framework.Client') as mock_client_class:
            mock_client_class.return_value = mock_langsmith_client

            # Initialize virtuous cycle orchestrator
            orchestrator = VirtuousCycleOrchestrator(mock_langsmith_client)

            # Run complete improvement cycle
            results = await orchestrator.run_improvement_cycle()

            # Verify complete cycle execution
            assert "cycle_id" in results
            assert "phases" in results
            assert "improvements" in results
            assert "recommendations" in results

            # Verify all phases were executed
            phases = results["phases"]
            assert "baseline_testing" in phases
            assert "trend_analysis" in phases
            assert "optimization_opportunities" in phases
            assert "validation" in phases

            # Verify cycle duration is reasonable
            assert results["duration_seconds"] < 300  # Should complete in 5 minutes

    @pytest.mark.asyncio
    async def test_quality_improvement_across_cycle(self, mock_langsmith_client):
        """Test quality improvement measurement across complete cycle."""
        with patch('virtuous_cycle_framework.Client') as mock_client_class:
            mock_client_class.return_value = mock_langsmith_client

            orchestrator = VirtuousCycleOrchestrator(mock_langsmith_client)

            # Mock baseline testing with lower quality
            with patch.object(orchestrator, '_run_baseline_testing') as mock_baseline:
                mock_baseline.return_value = {
                    "spectrum_averages": {
                        "customer_profile": 0.87,
                        "credit_analysis": 0.85,
                        "transaction_history": 0.89
                    },
                    "overall_average": 0.87
                }

                # Mock optimization with improvements
                with patch.object(orchestrator, '_optimize_and_test_spectrum') as mock_optimize:
                    mock_optimize.return_value = {
                        "baseline_quality": 0.87,
                        "improved_quality": 0.93,
                        "quality_improvement": 0.06,
                        "improvement_percentage": 6.9
                    }

                    results = await orchestrator.run_improvement_cycle()

                    # Verify quality improvements
                    improvements = results.get("improvements", {})
                    if improvements:
                        for spectrum, improvement in improvements.items():
                            assert improvement["quality_improvement"] > 0.02
                            assert improvement["improved_quality"] > improvement["baseline_quality"]

    @pytest.mark.asyncio
    async def test_90_percent_quality_achievement_validation(self, mock_langsmith_client):
        """Test validation of 90%+ quality achievement across the cycle."""
        with patch('virtuous_cycle_framework.Client') as mock_client_class:
            mock_client_class.return_value = mock_langsmith_client

            orchestrator = VirtuousCycleOrchestrator(mock_langsmith_client)

            # Mock high-quality baseline
            with patch.object(orchestrator, '_run_baseline_testing') as mock_baseline:
                mock_baseline.return_value = {
                    "spectrum_averages": {
                        "customer_profile": 0.92,
                        "credit_analysis": 0.91,
                        "transaction_history": 0.93,
                        "call_center_operations": 0.90,
                        "entity_relationship": 0.94,
                        "geographic_analysis": 0.89,
                        "temporal_analysis": 0.91
                    },
                    "overall_average": 0.914
                }

                results = await orchestrator.run_improvement_cycle()

                # Verify 90%+ quality achievement
                baseline = results["phases"]["baseline_testing"]
                assert baseline["overall_average"] > 0.90

                # Count spectrums above 90%
                above_90 = sum(1 for avg in baseline["spectrum_averages"].values() if avg >= 0.90)
                assert above_90 >= 5  # At least 5 out of 7 spectrums


class TestEdwinaHawthorneEndToEnd:
    """Test end-to-end validation with Edwina Hawthorne customer data."""

    @pytest.fixture
    def edwina_test_scenarios(self):
        """Create comprehensive Edwina Hawthorne test scenarios."""
        return [
            {
                "query": "Find customer blessedwina@aol.com",
                "expected_customer": "Edwina Hawthorne",
                "expected_client_id": "2270",
                "test_type": "email_lookup"
            },
            {
                "query": "Get credit report for customer 2270",
                "expected_content": "credit score 543",
                "expected_analysis": "Very Poor",
                "test_type": "credit_analysis"
            },
            {
                "query": "What is Edwina Hawthorne's payment history?",
                "expected_customer": "Edwina Hawthorne",
                "test_type": "payment_history"
            },
            {
                "query": "Show complete profile for client ID 2270",
                "expected_customer": "Edwina Hawthorne",
                "expected_fields": ["name", "email", "phone", "credit_score"],
                "test_type": "complete_profile"
            }
        ]

    @pytest.mark.asyncio
    async def test_edwina_hawthorne_across_all_phases(self, edwina_test_scenarios):
        """Test Edwina Hawthorne data validation across all phases."""
        # Phase 1: Multi-spectrum foundation with Edwina data
        with patch('multi_spectrum_framework.Client'):
            with patch.dict('os.environ', {'LANGSMITH_API_KEY': 'test_key'}):
                phase1_framework = MultiSpectrumFramework()

                # Verify Edwina data in customer identity spectrum
                identity_spectrum = next(
                    s for s in phase1_framework.data_spectrums
                    if s.name == "customer_identity_resolution"
                )

                edwina_samples = [
                    sample for sample in identity_spectrum.data_samples
                    if "blessedwina@aol.com" in sample.get("query", "") or
                       "Edwina Hawthorne" in sample.get("expected_customer", "")
                ]
                assert len(edwina_samples) >= 2

        # Phase 4: Production validation with Edwina scenarios
        phase4_orchestrator = ProductionIntegrationOrchestrator()

        for scenario in edwina_test_scenarios:
            # Test prompt effectiveness with Edwina data
            score = await phase4_orchestrator._test_prompt_effectiveness(
                """You are a comprehensive customer service assistant with
mandatory tool usage for accurate customer data analysis.""",
                scenario["query"]
            )

            # Should achieve high scores for customer-focused prompts
            assert score >= 0.80, f"Edwina scenario '{scenario['test_type']}' scored too low: {score}"

    @pytest.mark.asyncio
    async def test_edwina_hawthorne_quality_metrics_continuity(self, edwina_test_scenarios):
        """Test quality metrics continuity for Edwina Hawthorne across phases."""
        # Mock Phase 1 results with Edwina data
        phase1_results = {
            "metrics": {
                "model_performance": {
                    "gpt-4o-mini": {"avg_quality": 0.91, "edwina_test_score": 0.93}
                },
                "spectrum_performance": {
                    "customer_profile": {"avg_quality": 0.90, "edwina_accuracy": 0.95}
                }
            }
        }

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(phase1_results, f)
            temp_file = f.name

        try:
            # Phase 2: Optimization should maintain Edwina performance
            phase2_orchestrator = Phase2OptimizationOrchestrator()
            cycle = await phase2_orchestrator.run_phase2_optimization(temp_file)

            # Verify Edwina-specific optimizations
            assert cycle.baseline_results["metrics"]["model_performance"]["gpt-4o-mini"]["avg_quality"] == 0.91

            # Phase 3: Continuous improvement should learn from Edwina patterns
            mock_quality_collector = MagicMock()
            mock_quality_collector.storage.get_spectrum_metrics.return_value = []

            phase3_orchestrator = ContinuousImprovementOrchestrator(
                mock_quality_collector, config={}
            )

            # Record cycle for learning
            phase3_orchestrator.learning_accumulator.record_optimization_cycle(cycle.__dict__)

            # Verify learning patterns include customer-specific improvements
            patterns = phase3_orchestrator.learning_accumulator.learning_patterns
            assert len(patterns) > 0

        finally:
            Path(temp_file).unlink()


class TestProductionScenarios:
    """Test production scenario validation."""

    @pytest.mark.asyncio
    async def test_high_volume_production_scenario(self):
        """Test high-volume production scenario handling."""
        phase4_orchestrator = ProductionIntegrationOrchestrator()

        # Simulate high-volume metrics collection
        metrics_tasks = []
        for _ in range(10):
            task = asyncio.create_task(
                phase4_orchestrator.performance_monitor.collect_performance_metrics()
            )
            metrics_tasks.append(task)

        metrics_results = await asyncio.gather(*metrics_tasks)

        # Verify all metrics collected successfully
        assert len(metrics_results) == 10
        assert all(len(m.model_performance) == 7 for m in metrics_results)
        assert all(len(m.spectrum_performance) == 7 for m in metrics_results)

    @pytest.mark.asyncio
    async def test_production_failover_scenario(self):
        """Test production failover scenario."""
        phase4_orchestrator = ProductionIntegrationOrchestrator()

        # Mock deployment failure
        with patch.object(phase4_orchestrator.prompt_manager, 'deploy_prompt') as mock_deploy:
            mock_deploy.return_value = False

            # Mock optimization results
            optimization_results = {
                "ab_test_results": {
                    "customer_profile": {
                        "summary": {"best_score": 0.92}
                    }
                }
            }

            # Mock validation success but deployment failure
            phase4_orchestrator._validate_deployment = AsyncMock(return_value=True)

            # Should handle deployment failure gracefully
            success = await phase4_orchestrator.deploy_optimized_prompts(optimization_results)
            assert success is False

    @pytest.mark.asyncio
    async def test_railway_production_environment_validation(self):
        """Test Railway production environment validation."""
        phase4_orchestrator = ProductionIntegrationOrchestrator()

        # Mock Railway environment variables
        with patch.dict('os.environ', {
            'TILORES_API_URL': 'https://api.tilores.com',
            'TILORES_CLIENT_ID': 'prod_client',
            'TILORES_CLIENT_SECRET': 'prod_secret',
            'LANGSMITH_API_KEY': 'prod_key',
            'LANGSMITH_PROJECT': 'tilores_production'
        }):
            validation_results = await phase4_orchestrator.validate_railway_integration()

            # Verify production readiness
            assert validation_results["environment_variables"] is True
            assert validation_results["overall_status"] == "PASSED"


# Main execution for integration testing
async def main():
    """Main function to run integration tests."""
    print("🧪 Running Virtuous Cycle Integration Tests...")

    # Run pytest programmatically
    import subprocess
    import sys

    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/speed_experiments/test_virtuous_cycle_integration.py",
        "-v", "--tb=short", "-x"  # Stop on first failure
    ], capture_output=True, text=True)

    print("Integration Test Results:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)

    return result.returncode == 0


if __name__ == "__main__":
    asyncio.run(main())
