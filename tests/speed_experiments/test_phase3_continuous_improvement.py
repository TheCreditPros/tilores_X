#!/usr/bin/env python3
"""
Comprehensive tests for Phase 3: Continuous Improvement Engine.

Tests all components of the continuous improvement system including:
- Quality threshold monitoring with 90% threshold detection
- Automated alerting system for quality degradation
- Learning accumulation across optimization cycles
- Self-improving prompt optimization with iteration learning
- Automated improvement deployment system
- Self-healing optimization cycles

Author: Roo (Elite Software Engineer)
Created: 2025-08-16
Phase: 3 - Continuous Improvement Testing
"""

import asyncio
import json
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Import Phase 3 components
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from phase3_continuous_improvement import (
    AlertSeverity,
    AlertType,
    AutomatedAlertingSystem,
    AutomatedImprovementDeployment,
    ContinuousImprovementOrchestrator,
    LearningAccumulator,
    LearningPattern,
    QualityAlert,
    QualityThresholdMonitor,
    SelfImprovingOptimizer,
)


class TestQualityThresholdMonitor:
    """Test quality threshold monitoring system."""

    @pytest.fixture
    def mock_quality_collector(self):
        """Create mock quality collector."""
        collector = MagicMock()
        collector.storage = MagicMock()
        return collector

    @pytest.fixture
    def threshold_monitor(self, mock_quality_collector):
        """Create threshold monitor instance."""
        return QualityThresholdMonitor(mock_quality_collector)

    def test_threshold_monitor_initialization(self, threshold_monitor):
        """Test threshold monitor initialization."""
        assert threshold_monitor.thresholds["critical"] == 0.85
        assert threshold_monitor.thresholds["warning"] == 0.90
        assert threshold_monitor.thresholds["target"] == 0.95
        assert threshold_monitor.thresholds["excellent"] == 0.98
        assert threshold_monitor.variance_threshold == 0.05

    def test_critical_threshold_breach_detection(self, threshold_monitor):
        """Test detection of critical quality threshold breaches."""
        # Mock metrics with quality below critical threshold
        mock_metrics = [MagicMock(score=0.82), MagicMock(score=0.83), MagicMock(score=0.84)]
        threshold_monitor.quality_collector.storage.get_spectrum_metrics.return_value = mock_metrics

        alerts = threshold_monitor.check_quality_thresholds("test_spectrum")

        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL
        assert alerts[0].alert_type == AlertType.QUALITY_THRESHOLD_BREACH
        assert alerts[0].current_quality == 0.83  # Average of mock scores
        assert alerts[0].threshold == 0.85

    def test_warning_threshold_breach_detection(self, threshold_monitor):
        """Test detection of warning quality threshold breaches."""
        # Mock metrics with quality below warning threshold
        mock_metrics = [MagicMock(score=0.87), MagicMock(score=0.88), MagicMock(score=0.89)]
        threshold_monitor.quality_collector.storage.get_spectrum_metrics.return_value = mock_metrics

        alerts = threshold_monitor.check_quality_thresholds("test_spectrum")

        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.HIGH
        assert alerts[0].alert_type == AlertType.QUALITY_THRESHOLD_BREACH
        assert alerts[0].current_quality == 0.88  # Average of mock scores

    def test_declining_trend_detection(self, threshold_monitor):
        """Test detection of declining quality trends."""
        # Mock metrics with declining trend
        mock_metrics = [
            MagicMock(score=0.95),
            MagicMock(score=0.93),
            MagicMock(score=0.91),
            MagicMock(score=0.89),
            MagicMock(score=0.87),
        ]
        threshold_monitor.quality_collector.storage.get_spectrum_metrics.return_value = mock_metrics

        alerts = threshold_monitor.check_quality_thresholds("test_spectrum")

        # Should detect both warning threshold and declining trend
        assert len(alerts) >= 1
        trend_alerts = [a for a in alerts if a.alert_type == AlertType.QUALITY_DEGRADATION]
        assert len(trend_alerts) == 1
        assert trend_alerts[0].severity == AlertSeverity.MEDIUM

    def test_high_variance_detection(self, threshold_monitor):
        """Test detection of high quality variance."""
        # Mock metrics with high variance
        mock_metrics = [
            MagicMock(score=0.95),
            MagicMock(score=0.85),
            MagicMock(score=0.98),
            MagicMock(score=0.82),
            MagicMock(score=0.96),
        ]
        threshold_monitor.quality_collector.storage.get_spectrum_metrics.return_value = mock_metrics

        alerts = threshold_monitor.check_quality_thresholds("test_spectrum")

        variance_alerts = [a for a in alerts if a.alert_type == AlertType.HIGH_VARIANCE]
        assert len(variance_alerts) == 1
        assert variance_alerts[0].severity == AlertSeverity.LOW

    def test_no_alerts_for_good_quality(self, threshold_monitor):
        """Test no alerts generated for good quality metrics."""
        # Mock metrics with consistently good quality
        mock_metrics = [
            MagicMock(score=0.95),
            MagicMock(score=0.96),
            MagicMock(score=0.94),
            MagicMock(score=0.97),
            MagicMock(score=0.95),
        ]
        threshold_monitor.quality_collector.storage.get_spectrum_metrics.return_value = mock_metrics

        alerts = threshold_monitor.check_quality_thresholds("test_spectrum")

        assert len(alerts) == 0


class TestAutomatedAlertingSystem:
    """Test automated alerting system."""

    @pytest.fixture
    def alerting_system(self):
        """Create alerting system instance."""
        config = {"email_alerts": False, "alert_recipients": ["test@example.com"]}
        return AutomatedAlertingSystem(config)

    @pytest.fixture
    def sample_alert(self):
        """Create sample quality alert."""
        return QualityAlert(
            alert_id="test_alert_001",
            alert_type=AlertType.QUALITY_THRESHOLD_BREACH,
            severity=AlertSeverity.HIGH,
            spectrum="test_spectrum",
            model="gpt-4o-mini",
            current_quality=0.87,
            threshold=0.90,
            message="Quality below warning threshold",
            timestamp=datetime.now().isoformat(),
        )

    @pytest.mark.asyncio
    async def test_alert_processing(self, alerting_system, sample_alert):
        """Test alert processing functionality."""
        with patch.object(alerting_system, "_deliver_alert", new_callable=AsyncMock) as mock_deliver:
            success = await alerting_system.process_alert(sample_alert)

            assert success is True
            assert len(alerting_system.alert_history) == 1
            assert alerting_system.alert_history[0] == sample_alert
            mock_deliver.assert_called()

    @pytest.mark.asyncio
    async def test_rate_limiting(self, alerting_system, sample_alert):
        """Test alert rate limiting functionality."""
        # Process first alert
        await alerting_system.process_alert(sample_alert)

        # Create second alert for same spectrum/type
        second_alert = QualityAlert(
            alert_id="test_alert_002",
            alert_type=AlertType.QUALITY_THRESHOLD_BREACH,
            severity=AlertSeverity.HIGH,
            spectrum="test_spectrum",
            model="gpt-4o-mini",
            current_quality=0.86,
            threshold=0.90,
            message="Another quality alert",
            timestamp=datetime.now().isoformat(),
        )

        with patch.object(alerting_system, "_deliver_alert", new_callable=AsyncMock):
            # Second alert should be rate limited
            success = await alerting_system.process_alert(second_alert)
            assert success is False

    @pytest.mark.asyncio
    async def test_console_alert_delivery(self, alerting_system, sample_alert, capsys):
        """Test console alert delivery."""
        await alerting_system._deliver_console_alert(sample_alert)

        captured = capsys.readouterr()
        assert "QUALITY ALERT" in captured.out
        assert "test_spectrum" in captured.out
        assert "87.0%" in captured.out

    @pytest.mark.asyncio
    async def test_file_alert_delivery(self, alerting_system, sample_alert):
        """Test file alert delivery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Update alert channels to use temp directory
            alerting_system.alert_channels["file"]["path"] = f"{temp_dir}/test_alerts.log"

            await alerting_system._deliver_file_alert(sample_alert)

            # Check file was created and contains alert
            log_file = Path(temp_dir) / "test_alerts.log"
            assert log_file.exists()

            with open(log_file, "r") as f:
                log_content = f.read()
                log_data = json.loads(log_content.strip())

            assert log_data["alert_id"] == sample_alert.alert_id
            assert log_data["spectrum"] == sample_alert.spectrum
            assert log_data["severity"] == sample_alert.severity.value


class TestLearningAccumulator:
    """Test learning accumulation system."""

    @pytest.fixture
    def learning_accumulator(self):
        """Create learning accumulator with temporary storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield LearningAccumulator(storage_path=temp_dir)

    @pytest.fixture
    def sample_cycle_results(self):
        """Create sample optimization cycle results."""
        return {
            "cycle_id": "test_cycle_001",
            "timestamp": datetime.now().isoformat(),
            "phase": "continuous_improvement",
            "model_strategies": [
                {"optimization_approach": "quality_enhancement"},
                {"optimization_approach": "pattern_reinforcement"},
            ],
            "improvements": {
                "customer_profile": {"quality_improvement": 0.05, "optimization_strategy": "ai_driven"},
                "credit_analysis": {"quality_improvement": 0.03, "optimization_strategy": "pattern_based"},
            },
            "identified_patterns": [{"pattern_id": "pattern_001"}, {"pattern_id": "pattern_002"}],
            "phases": {
                "validation": {
                    "customer_profile": {"is_statistically_significant": True},
                    "credit_analysis": {"is_statistically_significant": False},
                }
            },
            "recommendations": {"optimization_strategy": "expand"},
        }

    def test_learning_accumulator_initialization(self, learning_accumulator):
        """Test learning accumulator initialization."""
        assert learning_accumulator.storage_path.exists()
        assert learning_accumulator.patterns_file.name == "learning_patterns.json"
        assert learning_accumulator.cycles_file.name == "optimization_cycles.json"
        assert isinstance(learning_accumulator.learning_patterns, dict)
        assert isinstance(learning_accumulator.cycle_memory, list)

    def test_cycle_recording(self, learning_accumulator, sample_cycle_results):
        """Test recording optimization cycle results."""
        initial_patterns_count = len(learning_accumulator.learning_patterns)
        initial_cycles_count = len(learning_accumulator.cycle_memory)

        learning_accumulator.record_optimization_cycle(sample_cycle_results)

        # Check cycle was recorded
        assert len(learning_accumulator.cycle_memory) == initial_cycles_count + 1
        recorded_cycle = learning_accumulator.cycle_memory[-1]
        assert recorded_cycle.cycle_id == "test_cycle_001"

        # Check learning patterns were updated
        assert len(learning_accumulator.learning_patterns) > initial_patterns_count

    def test_pattern_extraction(self, learning_accumulator, sample_cycle_results):
        """Test extraction of optimization strategies and patterns."""
        strategies = learning_accumulator._extract_strategies_used(sample_cycle_results)
        improvements = learning_accumulator._extract_improvements(sample_cycle_results)
        patterns = learning_accumulator._extract_patterns(sample_cycle_results)

        assert "quality_enhancement" in strategies
        assert "pattern_reinforcement" in strategies
        assert improvements["customer_profile"] == 0.05
        assert improvements["credit_analysis"] == 0.03
        assert "pattern_001" in patterns
        assert "pattern_002" in patterns

    def test_learning_pattern_updates(self, learning_accumulator, sample_cycle_results):
        """Test learning pattern updates from cycle results."""
        learning_accumulator.record_optimization_cycle(sample_cycle_results)

        # Check that patterns were created/updated
        strategy_pattern = learning_accumulator.learning_patterns.get("strategy_quality_enhancement")
        assert strategy_pattern is not None
        assert strategy_pattern.success_count > 0
        assert strategy_pattern.confidence_score > 0

    def test_learned_patterns_retrieval(self, learning_accumulator):
        """Test retrieval of learned patterns for specific contexts."""
        # Create test pattern
        test_pattern = LearningPattern(
            pattern_id="test_pattern",
            pattern_type="test_strategy",
            success_count=5,
            failure_count=1,
            average_improvement=0.04,
            applicable_contexts=["customer_profile", "credit_analysis"],
            learned_optimizations=[],
            confidence_score=0.83,
            last_updated=datetime.now().isoformat(),
        )
        learning_accumulator.learning_patterns["test_pattern"] = test_pattern

        # Test retrieval
        patterns = learning_accumulator.get_learned_patterns_for_context("customer_profile")
        assert len(patterns) == 1
        assert patterns[0].pattern_id == "test_pattern"

        # Test no patterns for unknown context
        patterns = learning_accumulator.get_learned_patterns_for_context("unknown_context")
        assert len(patterns) == 0


class TestSelfImprovingOptimizer:
    """Test self-improving prompt optimizer."""

    @pytest.fixture
    def learning_accumulator(self):
        """Create learning accumulator for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield LearningAccumulator(storage_path=temp_dir)

    @pytest.fixture
    def self_improving_optimizer(self, learning_accumulator):
        """Create self-improving optimizer instance."""
        return SelfImprovingOptimizer(learning_accumulator)

    @pytest.mark.asyncio
    async def test_optimization_with_learning(self, self_improving_optimizer, learning_accumulator):
        """Test optimization using accumulated learning."""
        # Add test learning pattern
        test_pattern = LearningPattern(
            pattern_id="test_pattern",
            pattern_type="quality_enhancement",
            success_count=10,
            failure_count=2,
            average_improvement=0.06,
            applicable_contexts=["test_spectrum"],
            learned_optimizations=[],
            confidence_score=0.83,
            last_updated=datetime.now().isoformat(),
        )
        learning_accumulator.learning_patterns["test_pattern"] = test_pattern

        # Run optimization
        context = {"current_quality": 0.85, "trigger_reason": "quality_below_threshold"}
        result = await self_improving_optimizer.optimize_with_learning("test_spectrum", 0.85, context)

        assert result["spectrum"] == "test_spectrum"
        assert result["strategy"] == "quality_enhancement"
        assert result["expected_improvement"] == 0.06
        assert result["confidence"] == 0.83
        assert result["learning_applied"] == 1
        assert "optimized_prompt" in result

    @pytest.mark.asyncio
    async def test_optimization_without_learning(self, self_improving_optimizer):
        """Test optimization when no learning patterns available."""
        context = {"current_quality": 0.85}
        result = await self_improving_optimizer.optimize_with_learning("unknown_spectrum", 0.85, context)

        assert result["spectrum"] == "unknown_spectrum"
        assert result["strategy"] == "gradual_enhancement"
        assert result["expected_improvement"] == 0.02
        assert result["confidence"] == 0.5
        assert result["learning_applied"] == 0

    def test_historical_analysis(self, self_improving_optimizer):
        """Test historical optimization analysis."""
        # Add mock optimization history
        self_improving_optimizer.optimization_history.extend(
            [
                {"spectrum": "test_spectrum", "success": True, "strategy": "pattern_a"},
                {"spectrum": "test_spectrum", "success": False, "strategy": "pattern_b"},
                {"spectrum": "test_spectrum", "success": True, "strategy": "pattern_a"},
                {"spectrum": "other_spectrum", "success": True, "strategy": "pattern_c"},
            ]
        )

        analysis = self_improving_optimizer._analyze_historical_optimizations("test_spectrum")

        assert analysis["total_attempts"] == 3
        assert analysis["successful_attempts"] == 2
        assert analysis["success_rate"] == 2 / 3
        assert "pattern_a" in analysis["success_patterns"]
        assert "pattern_b" in analysis["failure_patterns"]


class TestAutomatedImprovementDeployment:
    """Test automated improvement deployment system."""

    @pytest.fixture
    def deployment_system(self):
        """Create deployment system instance."""
        return AutomatedImprovementDeployment()

    @pytest.fixture
    def good_optimization_result(self):
        """Create optimization result that meets deployment criteria."""
        return {
            "spectrum": "test_spectrum",
            "strategy": "quality_enhancement",
            "optimized_prompt": "Optimized prompt content",
            "expected_improvement": 0.05,  # 5% improvement
            "confidence": 0.85,  # 85% confidence
            "learning_applied": 3,
        }

    @pytest.fixture
    def poor_optimization_result(self):
        """Create optimization result that doesn't meet deployment criteria."""
        return {
            "spectrum": "test_spectrum",
            "strategy": "gradual_enhancement",
            "optimized_prompt": "Basic prompt content",
            "expected_improvement": 0.01,  # 1% improvement (below threshold)
            "confidence": 0.6,  # 60% confidence (below threshold)
            "learning_applied": 0,
        }

    @pytest.mark.asyncio
    async def test_deployment_readiness_evaluation_success(self, deployment_system, good_optimization_result):
        """Test deployment readiness evaluation for good results."""
        decision = await deployment_system.evaluate_deployment_readiness(good_optimization_result)

        assert decision["ready_for_deployment"] is True
        assert decision["improvement_check"] is True
        assert decision["confidence_check"] is True
        assert "DEPLOY" in decision["recommendation"]

    @pytest.mark.asyncio
    async def test_deployment_readiness_evaluation_failure(self, deployment_system, poor_optimization_result):
        """Test deployment readiness evaluation for poor results."""
        decision = await deployment_system.evaluate_deployment_readiness(poor_optimization_result)

        assert decision["ready_for_deployment"] is False
        assert decision["improvement_check"] is False
        assert decision["confidence_check"] is False
        assert "REJECT" in decision["recommendation"]

    @pytest.mark.asyncio
    async def test_successful_deployment(self, deployment_system, good_optimization_result):
        """Test successful optimization deployment."""
        result = await deployment_system.deploy_optimization(good_optimization_result)

        assert result["deployed"] is True
        assert "deployment_id" in result
        assert result["spectrum"] == "test_spectrum"
        assert result["rollback_available"] is True
        assert len(deployment_system.deployment_history) == 1

    @pytest.mark.asyncio
    async def test_failed_deployment(self, deployment_system, poor_optimization_result):
        """Test failed optimization deployment."""
        result = await deployment_system.deploy_optimization(poor_optimization_result)

        assert result["deployed"] is False
        assert "reason" in result
        assert "readiness_evaluation" in result
        assert len(deployment_system.deployment_history) == 0


class TestContinuousImprovementOrchestrator:
    """Test continuous improvement orchestrator."""

    @pytest.fixture
    def mock_quality_collector(self):
        """Create mock quality collector."""
        collector = MagicMock()
        collector.storage = MagicMock()
        collector.storage.get_spectrum_metrics.return_value = []
        collector.storage.get_recent_metrics.return_value = []
        return collector

    @pytest.fixture
    def orchestrator(self, mock_quality_collector):
        """Create orchestrator instance."""
        config = {"email_alerts": False}
        return ContinuousImprovementOrchestrator(mock_quality_collector, config)

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert orchestrator.threshold_monitor is not None
        assert orchestrator.alerting_system is not None
        assert orchestrator.learning_accumulator is not None
        assert orchestrator.self_improving_optimizer is not None
        assert orchestrator.deployment_system is not None
        assert orchestrator.monitoring_interval == timedelta(minutes=30)
        assert orchestrator.max_concurrent_optimizations == 3

    def test_monitored_spectrums_default(self, orchestrator):
        """Test default monitored spectrums when no recent data."""
        spectrums = orchestrator._get_monitored_spectrums()

        expected_spectrums = {
            "customer_profile",
            "credit_analysis",
            "transaction_history",
            "call_center_operations",
            "entity_relationship",
            "geographic_analysis",
            "temporal_analysis",
        }

        assert set(spectrums) == expected_spectrums

    def test_monitored_spectrums_from_metrics(self, orchestrator):
        """Test monitored spectrums extraction from recent metrics."""
        # Mock recent metrics
        mock_metrics = [
            MagicMock(spectrum="spectrum_a"),
            MagicMock(spectrum="spectrum_b"),
            MagicMock(spectrum="spectrum_a"),  # Duplicate
            MagicMock(spectrum="spectrum_c"),
        ]
        orchestrator.quality_collector.storage.get_recent_metrics.return_value = mock_metrics

        spectrums = orchestrator._get_monitored_spectrums()

        assert set(spectrums) == {"spectrum_a", "spectrum_b", "spectrum_c"}

    @pytest.mark.asyncio
    async def test_self_healing_cycle(self, orchestrator):
        """Test self-healing cycle execution."""
        # Mock spectrum health analysis
        with patch.object(orchestrator, "_analyze_spectrum_health") as mock_analyze:
            with patch.object(orchestrator, "_apply_self_healing") as mock_healing:
                mock_analyze.return_value = {"needs_healing": True, "current_quality": 0.85, "healing_priority": "high"}
                mock_healing.return_value = {"improvement_achieved": 0.04, "healing_strategy": "quality_enhancement"}

                results = await orchestrator.run_self_healing_cycle()

                assert "cycle_id" in results
                assert results["spectrums_analyzed"] > 0
                assert len(results["healing_actions"]) > 0
                assert "duration" in results

    @pytest.mark.asyncio
    async def test_spectrum_health_analysis(self, orchestrator):
        """Test spectrum health analysis."""
        # Mock quality metrics for health analysis
        mock_metrics = [MagicMock(score=0.87), MagicMock(score=0.86), MagicMock(score=0.88)]
        orchestrator.quality_collector.storage.get_spectrum_metrics.return_value = mock_metrics

        health = await orchestrator._analyze_spectrum_health("test_spectrum")

        assert health["spectrum"] == "test_spectrum"
        assert health["current_quality"] == 0.87  # Average
        assert health["needs_healing"] is True  # Below 0.90 threshold
        assert health["healing_priority"] == "medium"  # Above 0.85
        assert "below_quality_threshold" in health["issues"]


class TestIntegrationScenarios:
    """Test integration scenarios for Phase 3 components."""

    @pytest.fixture
    def mock_quality_collector(self):
        """Create comprehensive mock quality collector."""
        collector = MagicMock()
        collector.storage = MagicMock()
        return collector

    @pytest.fixture
    def full_system(self, mock_quality_collector):
        """Create full Phase 3 system for integration testing."""
        config = {"email_alerts": False}
        return ContinuousImprovementOrchestrator(mock_quality_collector, config)

    @pytest.mark.asyncio
    async def test_end_to_end_quality_degradation_response(self, full_system):
        """Test complete response to quality degradation."""
        # Mock poor quality metrics
        mock_metrics = [MagicMock(score=0.82), MagicMock(score=0.83), MagicMock(score=0.81)]  # Below critical threshold
        full_system.quality_collector.storage.get_spectrum_metrics.return_value = mock_metrics

        # Mock successful optimization and deployment
        with patch.object(full_system.self_improving_optimizer, "optimize_with_learning") as mock_optimize:
            with patch.object(full_system.deployment_system, "deploy_optimization") as mock_deploy:
                mock_optimize.return_value = {
                    "spectrum": "test_spectrum",
                    "strategy": "quality_enhancement",
                    "expected_improvement": 0.08,
                    "confidence": 0.9,
                    "optimized_prompt": "Enhanced prompt",
                }
                mock_deploy.return_value = {"deployed": True, "deployment_id": "deploy_001"}

                # Run monitoring cycle
                results = await full_system._run_monitoring_cycle()

                # Verify complete workflow
                assert results["alerts_generated"] > 0
                assert results["optimizations_triggered"] > 0
                assert results["improvements_deployed"] > 0

    @pytest.mark.asyncio
    async def test_learning_accumulation_across_cycles(self, full_system):
        """Test learning accumulation across multiple optimization cycles."""
        # Simulate multiple optimization cycles
        cycle_results = [
            {
                "cycle_id": f"cycle_{i}",
                "improvements": {"test_spectrum": {"quality_improvement": 0.03 + i * 0.01}},
                "model_strategies": [{"optimization_approach": "quality_enhancement"}],
                "identified_patterns": [{"pattern_id": f"pattern_{i}"}],
            }
            for i in range(3)
        ]

        # Record all cycles
        for cycle in cycle_results:
            full_system.learning_accumulator.record_optimization_cycle(cycle)

        # Check learning accumulation
        patterns = full_system.learning_accumulator.learning_patterns
        assert len(patterns) > 0

        # Check that success counts increased
        strategy_pattern = patterns.get("strategy_quality_enhancement")
        assert strategy_pattern is not None
        assert strategy_pattern.success_count == 3
        assert strategy_pattern.confidence_score == 1.0  # All successful

    @pytest.mark.asyncio
    async def test_concurrent_optimization_limits(self, full_system):
        """Test concurrent optimization limits."""
        # Add spectrums to active optimizations
        full_system.active_optimizations.update(["spectrum_1", "spectrum_2", "spectrum_3"])

        # Create mock alert
        alert = QualityAlert(
            alert_id="test_alert",
            alert_type=AlertType.QUALITY_THRESHOLD_BREACH,
            severity=AlertSeverity.CRITICAL,
            spectrum="spectrum_4",
            model=None,
            current_quality=0.80,
            threshold=0.85,
            message="Test alert",
            timestamp=datetime.now().isoformat(),
        )

        # Try to trigger optimization (should fail due to limit)
        cycle_results = {"optimizations": [], "deployments": []}
        triggered = await full_system._trigger_optimization("spectrum_4", alert, cycle_results)

        assert triggered is False  # Should be rejected due to concurrent limit

    def test_optimization_cooldown(self, full_system):
        """Test optimization cooldown functionality."""
        spectrum = "test_spectrum"

        # Set recent optimization time
        full_system.last_optimization_times[spectrum] = datetime.now() - timedelta(minutes=30)

        # Create mock alert
        alert = QualityAlert(
            alert_id="test_alert",
            alert_type=AlertType.QUALITY_THRESHOLD_BREACH,
            severity=AlertSeverity.HIGH,
            spectrum=spectrum,
            model=None,
            current_quality=0.87,
            threshold=0.90,
            message="Test alert",
            timestamp=datetime.now().isoformat(),
        )

        # Should be in cooldown (2 hours default)
        cycle_results = {"optimizations": [], "deployments": []}

        # Use asyncio.run for the async method
        async def test_trigger():
            return await full_system._trigger_optimization(spectrum, alert, cycle_results)

        triggered = asyncio.run(test_trigger())
        assert triggered is False


class TestQualityMetricsIntegration:
    """Test integration with quality metrics collector."""

    @pytest.mark.asyncio
    async def test_quality_metrics_feeding_to_continuous_improvement(self):
        """Test feeding quality metrics to continuous improvement system."""
        # This test would verify integration with the existing quality_metrics_collector
        # For now, we'll test the interface compatibility

        with tempfile.TemporaryDirectory() as temp_dir:
            learning_accumulator = LearningAccumulator(storage_path=temp_dir)

            # Simulate quality metrics being fed to learning system
            cycle_data = {
                "cycle_id": "integration_test",
                "improvements": {"test_spectrum": {"quality_improvement": 0.04}},
                "model_strategies": [{"optimization_approach": "integration_test"}],
                "identified_patterns": [],
            }

            learning_accumulator.record_optimization_cycle(cycle_data)

            # Verify learning was recorded
            assert len(learning_accumulator.cycle_memory) == 1
            assert "strategy_integration_test" in learning_accumulator.learning_patterns


# Performance and stress tests
class TestPerformanceAndStress:
    """Test performance and stress scenarios."""

    @pytest.mark.asyncio
    async def test_high_volume_alert_processing(self):
        """Test processing high volume of alerts."""
        alerting_system = AutomatedAlertingSystem()

        # Create multiple alerts
        alerts = []
        for i in range(50):
            alert = QualityAlert(
                alert_id=f"stress_test_{i}",
                alert_type=AlertType.QUALITY_THRESHOLD_BREACH,
                severity=AlertSeverity.MEDIUM,
                spectrum=f"spectrum_{i % 5}",
                model=None,
                current_quality=0.85,
                threshold=0.90,
                message=f"Stress test alert {i}",
                timestamp=datetime.now().isoformat(),
            )
            alerts.append(alert)

        # Process all alerts
        with patch.object(alerting_system, "_deliver_alert", new_callable=AsyncMock):
            start_time = datetime.now()

            tasks = [alerting_system.process_alert(alert) for alert in alerts]
            results = await asyncio.gather(*tasks)

            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

        # Verify performance
        assert processing_time < 5.0  # Should process 50 alerts in under 5 seconds
        assert len(alerting_system.alert_history) <= 50  # Some may be rate limited

        # Verify rate limiting worked
        successful_alerts = sum(1 for result in results if result)
        assert successful_alerts < len(alerts)  # Some should be rate limited

    @pytest.mark.asyncio
    async def test_learning_pattern_persistence(self):
        """Test learning pattern persistence across restarts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create first accumulator and add patterns
            accumulator1 = LearningAccumulator(storage_path=temp_dir)

            test_pattern = LearningPattern(
                pattern_id="persistence_test",
                pattern_type="test_strategy",
                success_count=5,
                failure_count=1,
                average_improvement=0.04,
                applicable_contexts=["test_context"],
                learned_optimizations=[],
                confidence_score=0.83,
                last_updated=datetime.now().isoformat(),
            )

            accumulator1.learning_patterns["persistence_test"] = test_pattern
            accumulator1._save_learning_data()

            # Create second accumulator (simulating restart)
            accumulator2 = LearningAccumulator(storage_path=temp_dir)

            # Verify pattern was loaded
            assert "persistence_test" in accumulator2.learning_patterns
            loaded_pattern = accumulator2.learning_patterns["persistence_test"]
            assert loaded_pattern.success_count == 5
            assert loaded_pattern.confidence_score == 0.83


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
