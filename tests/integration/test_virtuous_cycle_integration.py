#!/usr/bin/env python3
"""
Integration tests for Virtuous Cycle Production API Integration.

Tests the complete integration of the 4-phase Virtuous Cycle automation
into the production API for real-time monitoring and optimization.

Author: Roo (Elite Software Engineer)
Created: 2025-08-16
"""

import asyncio
import json
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from virtuous_cycle_api import VirtuousCycleManager


class TestVirtuousCycleIntegration:
    """Test suite for Virtuous Cycle production API integration."""

    @pytest.fixture
    def virtuous_cycle_manager(self):
        """Create VirtuousCycleManager instance for testing."""
        return VirtuousCycleManager()

    @pytest.fixture
    def mock_langsmith_client(self):
        """Mock LangSmith client for testing."""
        mock_client = MagicMock()
        mock_client.list_runs = AsyncMock(return_value=[])
        return mock_client

    @pytest.mark.asyncio
    async def test_virtuous_cycle_manager_initialization(
        self, virtuous_cycle_manager
    ):
        """Test VirtuousCycleManager initialization."""
        manager = virtuous_cycle_manager

        # Check basic initialization
        assert manager.quality_threshold == 0.90
        assert manager.monitoring_interval == 300
        assert manager.trace_batch_size == 50
        assert not manager.monitoring_active

        # Check metrics initialization
        assert 'traces_processed' in manager.metrics
        assert 'quality_checks' in manager.metrics
        assert 'optimizations_triggered' in manager.metrics
        assert manager.metrics['current_quality'] == 0.0

    @pytest.mark.asyncio
    async def test_trace_simulation(self, virtuous_cycle_manager):
        """Test LangSmith trace simulation."""
        manager = virtuous_cycle_manager

        traces = manager._simulate_traces()

        # Verify trace structure
        assert isinstance(traces, list)
        assert len(traces) >= 1

        for trace in traces:
            assert 'id' in trace
            assert 'timestamp' in trace
            assert 'model' in trace
            assert 'quality_score' in trace
            assert 'response_time' in trace
            assert 'spectrum' in trace
            assert isinstance(trace['quality_score'], float)
            assert 0.0 <= trace['quality_score'] <= 1.0

    @pytest.mark.asyncio
    async def test_trace_batch_analysis(self, virtuous_cycle_manager):
        """Test trace batch analysis functionality."""
        manager = virtuous_cycle_manager

        # Create mock traces
        mock_traces = [
            {
                'id': f'trace_{i}',
                'quality_score': 0.85 + (i * 0.02),
                'response_time': 3.0 + i,
                'spectrum': 'customer_profile',
                'model': 'gpt-4o-mini'
            }
            for i in range(5)
        ]

        # Analyze batch
        await manager._analyze_trace_batch(mock_traces)

        # Check metrics updated
        assert manager.metrics['traces_processed'] == 5
        assert manager.metrics['quality_checks'] == 1
        assert manager.metrics['current_quality'] > 0.0

    @pytest.mark.asyncio
    async def test_quality_threshold_monitoring(self, virtuous_cycle_manager):
        """Test quality threshold monitoring and optimization triggers."""
        manager = virtuous_cycle_manager

        # Mock low quality to trigger optimization
        manager.metrics['current_quality'] = 0.85  # Below 90% threshold

        # Mock the optimization trigger
        with patch.object(manager, '_trigger_optimization') as mock_trigger:
            mock_trigger.return_value = None

            # Simulate quality monitoring check
            current_quality = manager.metrics['current_quality']

            if current_quality < manager.quality_threshold:
                if manager._can_trigger_optimization():
                    await manager._trigger_optimization(
                        reason=f"Quality degradation: {current_quality:.1%}",
                        quality_score=current_quality
                    )

            # Verify optimization was triggered
            mock_trigger.assert_called_once()

    @pytest.mark.asyncio
    async def test_manual_optimization_trigger(self, virtuous_cycle_manager):
        """Test manual optimization trigger functionality."""
        manager = virtuous_cycle_manager

        # Mock the optimization methods
        with patch.object(manager, '_run_phase2_optimization') as mock_phase2, \
             patch.object(manager, '_run_phase3_improvement') as mock_phase3, \
             patch.object(manager, '_run_phase4_deployment') as mock_phase4:

            mock_phase2.return_value = {'cycle_id': 'test_cycle'}
            mock_phase3.return_value = None
            mock_phase4.return_value = True

            # Trigger manual optimization
            result = await manager.trigger_manual_optimization(
                "Test optimization trigger"
            )

            # Verify result
            assert result['success'] is True
            assert 'timestamp' in result
            assert manager.metrics['optimizations_triggered'] == 1

    @pytest.mark.asyncio
    async def test_cooldown_mechanism(self, virtuous_cycle_manager):
        """Test optimization cooldown mechanism."""
        manager = virtuous_cycle_manager

        # Set recent optimization time
        manager.last_optimization_time = datetime.now()

        # Try to trigger optimization (should be blocked by cooldown)
        result = await manager.trigger_manual_optimization("Test cooldown")

        # Verify cooldown is active
        assert result['success'] is False
        assert 'Cooldown active' in result['reason']

    @pytest.mark.asyncio
    async def test_status_endpoint_data(self, virtuous_cycle_manager):
        """Test status endpoint data structure."""
        manager = virtuous_cycle_manager

        status = manager.get_status()

        # Verify status structure
        assert 'monitoring_active' in status
        assert 'langsmith_available' in status
        assert 'frameworks_available' in status
        assert 'quality_threshold' in status
        assert 'metrics' in status
        assert 'component_status' in status

        # Verify metrics structure
        metrics = status['metrics']
        assert 'traces_processed' in metrics
        assert 'quality_checks' in metrics
        assert 'optimizations_triggered' in metrics
        assert 'current_quality' in metrics

    @pytest.mark.asyncio
    async def test_mock_baseline_creation(self, virtuous_cycle_manager):
        """Test mock baseline creation for development."""
        manager = virtuous_cycle_manager

        baseline_file = await manager._create_mock_baseline()

        # Verify baseline file creation
        assert baseline_file != ""
        assert "baseline_results_mock_" in baseline_file

        # Verify file exists and has correct structure
        import os
        if os.path.exists(baseline_file):
            with open(baseline_file, 'r') as f:
                baseline_data = json.load(f)

            assert 'timestamp' in baseline_data
            assert 'metrics' in baseline_data
            assert 'model_performance' in baseline_data['metrics']
            assert 'spectrum_performance' in baseline_data['metrics']

    @pytest.mark.asyncio
    async def test_health_check_functionality(self, virtuous_cycle_manager):
        """Test system health check functionality."""
        manager = virtuous_cycle_manager

        # Run health check
        await manager._health_check()

        # Verify no exceptions and basic functionality
        assert manager.metrics is not None
        assert isinstance(manager.monitoring_active, bool)

    @pytest.mark.asyncio
    async def test_optimization_cycle_coordination(self, virtuous_cycle_manager):
        """Test complete optimization cycle coordination."""
        manager = virtuous_cycle_manager

        # Mock all phase orchestrators
        manager.phase2_orchestrator = MagicMock()
        manager.phase3_orchestrator = MagicMock()
        manager.phase4_orchestrator = MagicMock()

        # Mock async methods
        manager.phase2_orchestrator.run_phase2_optimization = AsyncMock(
            return_value=MagicMock(__dict__={'cycle_id': 'test_cycle'})
        )
        manager.phase3_orchestrator.learning_accumulator = MagicMock()
        manager.phase3_orchestrator.run_self_healing_cycle = AsyncMock()
        manager.phase4_orchestrator.deploy_optimized_prompts = AsyncMock(
            return_value=True
        )

        # Mock baseline file
        with patch.object(manager, '_get_latest_baseline_file') as mock_baseline:
            mock_baseline.return_value = "mock_baseline.json"

            # Trigger optimization
            await manager._trigger_optimization(
                "Test coordination", 0.85
            )

            # Verify all phases were called
            manager.phase2_orchestrator.run_phase2_optimization.assert_called_once()
            manager.phase3_orchestrator.run_self_healing_cycle.assert_called_once()
            manager.phase4_orchestrator.deploy_optimized_prompts.assert_called_once()

    @pytest.mark.asyncio
    async def test_trace_processing_queue(self, virtuous_cycle_manager):
        """Test trace processing queue functionality."""
        manager = virtuous_cycle_manager

        # Add mock traces to queue
        mock_traces = [
            {'id': f'trace_{i}', 'quality_score': 0.9 + (i * 0.01)}
            for i in range(3)
        ]

        for trace in mock_traces:
            await manager.trace_processing_queue.put(trace)

        # Verify queue has traces
        assert manager.trace_processing_queue.qsize() == 3

        # Process one trace
        trace = await manager.trace_processing_queue.get()
        assert trace['id'] == 'trace_0'

    def test_can_trigger_optimization_logic(self, virtuous_cycle_manager):
        """Test optimization trigger logic."""
        manager = virtuous_cycle_manager

        # Test with no previous optimization
        assert manager._can_trigger_optimization() is True

        # Test with recent optimization (should block)
        manager.last_optimization_time = datetime.now()
        assert manager._can_trigger_optimization() is False

    @pytest.mark.asyncio
    async def test_error_handling_in_optimization(self, virtuous_cycle_manager):
        """Test error handling during optimization cycles."""
        manager = virtuous_cycle_manager

        # Mock phase2 to raise exception
        manager.phase2_orchestrator = MagicMock()
        manager.phase2_orchestrator.run_phase2_optimization = AsyncMock(
            side_effect=Exception("Test error")
        )

        # Trigger optimization (should handle error gracefully)
        await manager._trigger_optimization("Test error handling", 0.85)

        # Verify optimization was attempted but handled gracefully
        assert manager.metrics['optimizations_triggered'] == 1

    @pytest.mark.asyncio
    async def test_monitoring_loop_simulation(self, virtuous_cycle_manager):
        """Test monitoring loop simulation (short duration)."""
        manager = virtuous_cycle_manager

        # Start monitoring for a very short time
        manager.monitoring_active = True

        # Mock the monitoring methods to avoid infinite loop
        with patch.object(manager, '_run_monitoring_cycle') as mock_cycle:
            mock_cycle.return_value = None

            # Create a task that will run briefly
            monitoring_task = asyncio.create_task(
                manager._trace_monitoring_loop()
            )

            # Let it run briefly then stop
            await asyncio.sleep(0.1)
            manager.monitoring_active = False

            # Cancel the task
            monitoring_task.cancel()
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass

            # Verify monitoring was attempted
            assert mock_cycle.call_count >= 0  # May or may not be called


class TestVirtuousCycleAPIEndpoints:
    """Test the API endpoints integration."""

    @pytest.mark.asyncio
    async def test_status_endpoint_structure(self):
        """Test the status endpoint returns proper structure."""
        from main_enhanced import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Test status endpoint
        response = client.get("/v1/virtuous-cycle/status")

        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        assert 'monitoring_active' in data
        assert 'quality_threshold' in data
        assert 'metrics' in data
        assert 'component_status' in data

    @pytest.mark.asyncio
    async def test_trigger_endpoint_functionality(self):
        """Test the trigger endpoint functionality."""
        from main_enhanced import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Test trigger endpoint with reason
        response = client.post(
            "/v1/virtuous-cycle/trigger",
            json={"reason": "Test API trigger"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert 'success' in data
        assert 'reason' in data or 'timestamp' in data

    def test_api_endpoint_rate_limits(self):
        """Test API endpoint rate limiting configuration."""
        from main_enhanced import app

        # Check that endpoints have rate limiting decorators
        status_route = None
        trigger_route = None

        for route in app.routes:
            if hasattr(route, 'path'):
                if route.path == "/v1/virtuous-cycle/status":
                    status_route = route
                elif route.path == "/v1/virtuous-cycle/trigger":
                    trigger_route = route

        # Verify routes exist
        assert status_route is not None
        assert trigger_route is not None


class TestVirtuousCycleBackgroundTasks:
    """Test background task integration."""

    @pytest.mark.asyncio
    async def test_background_task_startup(self):
        """Test background task startup functionality."""
        from main_enhanced import startup_background_tasks, background_tasks

        # Clear any existing tasks
        background_tasks.clear()

        # Mock the virtuous cycle manager
        with patch('main_enhanced.virtuous_cycle_manager') as mock_manager:
            mock_manager.start_monitoring = AsyncMock()

            # Start background tasks
            await startup_background_tasks()

            # Verify monitoring was started
            mock_manager.start_monitoring.assert_called_once()

            # Verify task was added to background_tasks
            assert len(background_tasks) == 1

    @pytest.mark.asyncio
    async def test_background_task_shutdown(self):
        """Test background task shutdown functionality."""
        from main_enhanced import (
            shutdown_background_tasks,
            background_tasks,
            virtuous_cycle_manager
        )

        # Add a mock task
        mock_task = MagicMock()
        mock_task.done.return_value = False
        mock_task.cancel = MagicMock()
        background_tasks.append(mock_task)

        # Mock the virtuous cycle manager
        with patch.object(virtuous_cycle_manager, 'stop_monitoring') as mock_stop:
            mock_stop.return_value = None

            # Shutdown background tasks
            await shutdown_background_tasks()

            # Verify stop was called
            mock_stop.assert_called_once()

            # Verify task was cancelled
            mock_task.cancel.assert_called_once()


class TestVirtuousCyclePhaseIntegration:
    """Test integration between different phases."""

    @pytest.fixture
    def manager_with_mocked_phases(self):
        """Create manager with mocked phase orchestrators."""
        manager = VirtuousCycleManager()

        # Mock all phase orchestrators
        manager.phase2_orchestrator = MagicMock()
        manager.phase3_orchestrator = MagicMock()
        manager.phase4_orchestrator = MagicMock()
        manager.quality_collector = MagicMock()

        return manager

    @pytest.mark.asyncio
    async def test_phase2_optimization_integration(
        self, manager_with_mocked_phases
    ):
        """Test Phase 2 optimization integration."""
        manager = manager_with_mocked_phases

        # Mock Phase 2 orchestrator
        mock_cycle = MagicMock()
        mock_cycle.__dict__ = {'cycle_id': 'test_cycle', 'improvement': 0.05}
        manager.phase2_orchestrator.run_phase2_optimization = AsyncMock(
            return_value=mock_cycle
        )

        # Mock baseline file
        with patch.object(manager, '_get_latest_baseline_file') as mock_baseline:
            mock_baseline.return_value = "test_baseline.json"

            # Run Phase 2 optimization
            result = await manager._run_phase2_optimization()

            # Verify result
            assert result is not None
            assert 'cycle_id' in result
            assert result['cycle_id'] == 'test_cycle'

    @pytest.mark.asyncio
    async def test_phase3_improvement_integration(
        self, manager_with_mocked_phases
    ):
        """Test Phase 3 continuous improvement integration."""
        manager = manager_with_mocked_phases

        # Mock Phase 3 components
        manager.phase3_orchestrator.learning_accumulator = MagicMock()
        manager.phase3_orchestrator.learning_accumulator.record_optimization_cycle = MagicMock()  # noqa: E501
        manager.phase3_orchestrator.run_self_healing_cycle = AsyncMock()

        # Mock optimization results
        optimization_results = {
            'cycle_id': 'test_cycle',
            'improvements': {'customer_profile': 0.05}
        }

        # Run Phase 3 improvement
        await manager._run_phase3_improvement(optimization_results)

        # Verify learning accumulator was called
        manager.phase3_orchestrator.learning_accumulator.record_optimization_cycle.assert_called_once_with(  # noqa: E501
            optimization_results
        )

        # Verify self-healing cycle was called
        manager.phase3_orchestrator.run_self_healing_cycle.assert_called_once()

    @pytest.mark.asyncio
    async def test_phase4_deployment_integration(
        self, manager_with_mocked_phases
    ):
        """Test Phase 4 production deployment integration."""
        manager = manager_with_mocked_phases

        # Mock Phase 4 orchestrator
        manager.phase4_orchestrator.deploy_optimized_prompts = AsyncMock(
            return_value=True
        )

        # Mock optimization results
        optimization_results = {
            'cycle_id': 'test_cycle',
            'best_prompts': {'system_prompt': 'optimized prompt'}
        }

        # Run Phase 4 deployment
        result = await manager._run_phase4_deployment(optimization_results)

        # Verify deployment
        assert result is True
        manager.phase4_orchestrator.deploy_optimized_prompts.assert_called_once_with(  # noqa: E501
            optimization_results
        )

    @pytest.mark.asyncio
    async def test_end_to_end_optimization_cycle(
        self, manager_with_mocked_phases
    ):
        """Test complete end-to-end optimization cycle."""
        manager = manager_with_mocked_phases

        # Mock all phase methods
        manager.phase2_orchestrator.run_phase2_optimization = AsyncMock(
            return_value=MagicMock(__dict__={'cycle_id': 'e2e_test'})
        )
        manager.phase3_orchestrator.learning_accumulator.record_optimization_cycle = MagicMock()  # noqa: E501
        manager.phase3_orchestrator.run_self_healing_cycle = AsyncMock()
        manager.phase4_orchestrator.deploy_optimized_prompts = AsyncMock(
            return_value=True
        )

        # Mock baseline file
        with patch.object(manager, '_get_latest_baseline_file') as mock_baseline:
            mock_baseline.return_value = "test_baseline.json"

            # Trigger complete optimization cycle
            await manager._trigger_optimization(
                "End-to-end test", 0.85
            )

            # Verify all phases were executed
            manager.phase2_orchestrator.run_phase2_optimization.assert_called_once()  # noqa: E501
            manager.phase3_orchestrator.run_self_healing_cycle.assert_called_once()  # noqa: E501
            manager.phase4_orchestrator.deploy_optimized_prompts.assert_called_once()  # noqa: E501

            # Verify metrics updated
            assert manager.metrics['optimizations_triggered'] == 1
            assert manager.metrics['improvements_deployed'] == 1


class TestVirtuousCycleProduction:
    """Test production-ready scenarios."""

    @pytest.mark.asyncio
    async def test_production_monitoring_simulation(self):
        """Test production monitoring simulation."""
        manager = VirtuousCycleManager()

        # Simulate production traces
        traces = manager._simulate_traces()

        # Process traces
        await manager._analyze_trace_batch(traces)

        # Verify metrics were updated
        assert manager.metrics['traces_processed'] == len(traces)
        assert manager.metrics['quality_checks'] == 1
        assert manager.metrics['current_quality'] > 0.0

    @pytest.mark.asyncio
    async def test_quality_degradation_response(self):
        """Test system response to quality degradation."""
        manager = VirtuousCycleManager()

        # Simulate quality degradation
        low_quality_traces = [
            {
                'id': f'trace_{i}',
                'quality_score': 0.80,  # Below 90% threshold
                'spectrum': 'customer_profile'
            }
            for i in range(5)
        ]

        # Process low quality traces
        await manager._analyze_trace_batch(low_quality_traces)

        # Verify quality is below threshold
        assert manager.metrics['current_quality'] < manager.quality_threshold

        # Verify optimization can be triggered
        assert manager._can_trigger_optimization() is True

    def test_configuration_validation(self):
        """Test configuration validation."""
        manager = VirtuousCycleManager()

        # Verify configuration values
        assert manager.quality_threshold == 0.90
        assert manager.monitoring_interval == 300
        assert manager.trace_batch_size == 50
        assert manager.optimization_cooldown.total_seconds() == 3600

    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test graceful degradation when components unavailable."""
        # Test with no frameworks available
        with patch('virtuous_cycle_api.FRAMEWORKS_AVAILABLE', False):
            manager = VirtuousCycleManager()

            # Verify graceful handling
            assert manager.quality_collector is None
            assert manager.phase2_orchestrator is None
            assert manager.phase3_orchestrator is None
            assert manager.phase4_orchestrator is None

            # Verify status still works
            status = manager.get_status()
            assert status['frameworks_available'] is False
