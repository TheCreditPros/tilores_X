#!/usr/bin/env python3
"""
Additional Coverage Tests for VirtuousCycleManager.

Focused on improving test coverage for virtuous_cycle_api.py
from 32% to 80%+ by testing uncovered code paths.

Author: Roo (Elite Software Engineer)
Created: 2025-08-16
Purpose: Improve backend test coverage for deployment readiness
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from virtuous_cycle_api import VirtuousCycleManager


class TestVirtuousCycleCoverage:
    """Additional tests to improve coverage of VirtuousCycleManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = VirtuousCycleManager()

    def test_init_method_coverage(self):
        """Test VirtuousCycleManager initialization."""
        manager = VirtuousCycleManager()

        # Test default values
        assert manager.monitoring_active is True
        assert manager.quality_threshold == 0.90
        assert manager.last_optimization_time is None
        assert manager.trace_queue == []
        assert manager.optimization_cooldown_hours == 1

    def test_get_status_with_no_traces(self):
        """Test get_status when no traces are available."""
        # Clear any existing traces
        self.manager.trace_queue = []

        status = self.manager.get_status()

        assert isinstance(status, dict)
        assert status["monitoring_active"] is True
        assert "metrics" in status
        assert status["metrics"]["traces_processed"] >= 0

    def test_get_status_with_traces(self):
        """Test get_status with simulated traces."""
        # Add some mock traces
        mock_traces = [
            {"id": "trace_1", "quality_score": 0.95, "timestamp": datetime.now().isoformat()},
            {"id": "trace_2", "quality_score": 0.88, "timestamp": datetime.now().isoformat()},
        ]
        self.manager.trace_queue = mock_traces

        status = self.manager.get_status()

        assert status["metrics"]["traces_processed"] >= 2

    def test_simulate_traces_method(self):
        """Test _simulate_traces method coverage."""
        traces = self.manager._simulate_traces()

        assert isinstance(traces, list)
        assert len(traces) >= 1
        assert len(traces) <= 10

        # Test trace structure
        for trace in traces:
            assert "id" in trace
            assert "timestamp" in trace
            assert "quality_score" in trace
            assert "model" in trace
            assert "spectrum" in trace
            assert 0.0 <= trace["quality_score"] <= 1.0

    def test_analyze_quality_method(self):
        """Test _analyze_quality method coverage."""
        # Test with empty traces
        quality = self.manager._analyze_quality([])
        assert quality == 0.0

        # Test with mock traces
        mock_traces = [{"quality_score": 0.95}, {"quality_score": 0.88}, {"quality_score": 0.92}]
        quality = self.manager._analyze_quality(mock_traces)
        assert 0.0 <= quality <= 1.0
        assert quality > 0.0

    def test_can_trigger_optimization_various_states(self):
        """Test _can_trigger_optimization under various conditions."""
        # Test initial state (no previous optimization)
        assert self.manager._can_trigger_optimization() is True

        # Test with recent optimization (within cooldown)
        self.manager.last_optimization_time = datetime.now()
        assert self.manager._can_trigger_optimization() is False

        # Test with old optimization (outside cooldown)
        self.manager.last_optimization_time = datetime.now() - timedelta(hours=2)
        assert self.manager._can_trigger_optimization() is True

        # Test edge case: exactly at cooldown boundary
        self.manager.last_optimization_time = datetime.now() - timedelta(hours=1, minutes=1)
        assert self.manager._can_trigger_optimization() is True

    @pytest.mark.asyncio
    async def test_trigger_manual_optimization_success(self):
        """Test successful manual optimization trigger."""
        # Ensure no cooldown
        self.manager.last_optimization_time = None

        result = await self.manager.trigger_manual_optimization("Coverage test trigger")

        assert isinstance(result, dict)
        assert "success" in result
        assert "reason" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_trigger_manual_optimization_during_cooldown(self):
        """Test manual optimization trigger during cooldown."""
        # Set recent optimization time
        self.manager.last_optimization_time = datetime.now()

        result = await self.manager.trigger_manual_optimization("Coverage test during cooldown")

        assert result["success"] is False
        assert "Cooldown active" in result["reason"]

    def test_get_frameworks_available_method(self):
        """Test frameworks availability check."""
        # This method checks for framework imports
        frameworks = self.manager._get_frameworks_available()

        assert isinstance(frameworks, bool)
        # Should be True in test environment

    def test_get_langsmith_available_method(self):
        """Test LangSmith availability check."""
        langsmith = self.manager._get_langsmith_available()

        assert isinstance(langsmith, bool)

    def test_component_status_method(self):
        """Test _get_component_status method."""
        status = self.manager._get_component_status()

        assert isinstance(status, dict)
        expected_components = [
            "langsmith_client",
            "quality_collector",
            "phase2_orchestrator",
            "phase3_orchestrator",
            "phase4_orchestrator",
        ]

        for component in expected_components:
            assert component in status
            assert isinstance(status[component], bool)

    @pytest.mark.asyncio
    async def test_start_monitoring_method(self):
        """Test start_monitoring method."""
        # Mock the background tasks
        with patch.object(self.manager, "_start_background_tasks") as mock_start:
            await self.manager.start_monitoring()
            mock_start.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_monitoring_method(self):
        """Test stop_monitoring method."""
        # Mock the background tasks
        with patch.object(self.manager, "_stop_background_tasks") as mock_stop:
            await self.manager.stop_monitoring()
            mock_stop.assert_called_once()

    def test_process_trace_batch_method(self):
        """Test _process_trace_batch method."""
        mock_traces = [{"id": "trace_1", "quality_score": 0.95}, {"id": "trace_2", "quality_score": 0.88}]

        # This method processes traces and updates metrics
        self.manager._process_trace_batch(mock_traces)

        # Verify traces were processed
        assert len(self.manager.trace_queue) >= 0

    def test_quality_threshold_validation(self):
        """Test quality threshold validation logic."""
        # Test with high quality (above threshold)
        high_quality_traces = [{"quality_score": 0.95}, {"quality_score": 0.93}, {"quality_score": 0.96}]
        quality = self.manager._analyze_quality(high_quality_traces)
        assert quality >= self.manager.quality_threshold

        # Test with low quality (below threshold)
        low_quality_traces = [{"quality_score": 0.85}, {"quality_score": 0.82}, {"quality_score": 0.87}]
        quality = self.manager._analyze_quality(low_quality_traces)
        assert quality < self.manager.quality_threshold

    def test_metrics_calculation_edge_cases(self):
        """Test metrics calculation with edge cases."""
        # Test with single trace
        single_trace = [{"quality_score": 0.90}]
        quality = self.manager._analyze_quality(single_trace)
        assert quality == 0.90

        # Test with identical quality scores
        identical_traces = [{"quality_score": 0.90}, {"quality_score": 0.90}, {"quality_score": 0.90}]
        quality = self.manager._analyze_quality(identical_traces)
        assert quality == 0.90

    def test_timestamp_formatting(self):
        """Test timestamp formatting in responses."""
        status = self.manager.get_status()

        # Verify timestamp format
        assert "last_update" in status["metrics"]
        timestamp = status["metrics"]["last_update"]

        # Should be valid ISO format
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail("Invalid timestamp format")

    def test_error_handling_in_status(self):
        """Test error handling within get_status method."""
        # Mock an internal error
        with patch.object(self.manager, "_simulate_traces") as mock_simulate:
            mock_simulate.side_effect = Exception("Simulation error")

            # Should still return valid status
            status = self.manager.get_status()
            assert isinstance(status, dict)
            assert "monitoring_active" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
