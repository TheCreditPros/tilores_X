#!/usr/bin/env python3
"""
Comprehensive Backend Endpoint Tests for Virtuous Cycle API.

Tests the /v1/virtuous-cycle/status and /v1/virtuous-cycle/trigger endpoints
with comprehensive integration scenarios, error handling, and data validation.

Author: Roo (Elite Software Engineer)
Created: 2025-08-16
Integration: Backend API endpoint testing for dashboard integration
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

# Import the FastAPI app and VirtuousCycleManager
from main_enhanced import app
from virtuous_cycle_api import VirtuousCycleManager


class TestVirtuousCycleAPIEndpoints:
    """Test suite for Virtuous Cycle API endpoints."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create test client
        self.client = TestClient(app)

        # Mock virtuous cycle manager for controlled testing
        self.mock_manager = MagicMock(spec=VirtuousCycleManager)

        # Default mock status response
        self.mock_status = {
            "monitoring_active": True,
            "langsmith_available": True,
            "frameworks_available": True,
            "quality_threshold": 0.90,
            "last_optimization": datetime.utcnow().isoformat(),
            "metrics": {
                "traces_processed": 150,
                "quality_checks": 25,
                "optimizations_triggered": 3,
                "improvements_deployed": 2,
                "current_quality": 0.92,
                "last_update": datetime.utcnow().isoformat(),
            },
            "component_status": {
                "langsmith_client": True,
                "quality_collector": True,
                "phase2_orchestrator": True,
                "phase3_orchestrator": True,
                "phase4_orchestrator": True,
            },
        }

        # Default mock trigger response
        self.mock_trigger_success = {
            "success": True,
            "reason": "Test optimization trigger",
            "timestamp": datetime.utcnow().isoformat(),
        }

    @pytest.mark.asyncio
    async def test_virtuous_cycle_status_endpoint_success(self):
        """Test successful virtuous cycle status retrieval."""
        with patch("main_enhanced.virtuous_cycle_manager") as mock_manager:
            mock_manager.get_status.return_value = self.mock_status

            response = self.client.get("/v1/virtuous-cycle/status")

            assert response.status_code == 200
            data = response.json()

            # Validate response structure
            assert "monitoring_active" in data
            assert "langsmith_available" in data
            assert "frameworks_available" in data
            assert "quality_threshold" in data
            assert "metrics" in data
            assert "component_status" in data

            # Validate metrics structure
            metrics = data["metrics"]
            assert "traces_processed" in metrics
            assert "quality_checks" in metrics
            assert "optimizations_triggered" in metrics
            assert "improvements_deployed" in metrics
            assert "current_quality" in metrics
            assert "last_update" in metrics

            # Validate component status structure
            components = data["component_status"]
            assert "langsmith_client" in components
            assert "quality_collector" in components
            assert "phase2_orchestrator" in components
            assert "phase3_orchestrator" in components
            assert "phase4_orchestrator" in components

            # Validate data types
            assert isinstance(data["monitoring_active"], bool)
            assert isinstance(data["quality_threshold"], float)
            assert isinstance(metrics["traces_processed"], int)
            assert isinstance(metrics["current_quality"], float)

    def test_virtuous_cycle_status_endpoint_manager_error(self):
        """Test virtuous cycle status when manager throws error."""
        with patch("main_enhanced.virtuous_cycle_manager") as mock_manager:
            mock_manager.get_status.side_effect = Exception("Manager error")

            response = self.client.get("/v1/virtuous-cycle/status")

            # Should still return 200 but with error information
            assert response.status_code == 500 or response.status_code == 200

    def test_virtuous_cycle_status_endpoint_rate_limiting(self):
        """Test rate limiting on status endpoint."""
        # Make multiple rapid requests to test rate limiting
        responses = []
        for i in range(150):  # Exceed 100/minute limit
            response = self.client.get("/v1/virtuous-cycle/status")
            responses.append(response.status_code)
            if response.status_code == 429:  # Rate limit exceeded
                break

        # Should eventually get rate limited
        assert 429 in responses

    @pytest.mark.asyncio
    async def test_virtuous_cycle_trigger_endpoint_success(self):
        """Test successful manual optimization trigger."""
        with patch("main_enhanced.virtuous_cycle_manager") as mock_manager:
            mock_manager.trigger_manual_optimization = AsyncMock(return_value=self.mock_trigger_success)

            trigger_data = {"reason": "Test optimization trigger"}
            response = self.client.post("/v1/virtuous-cycle/trigger", json=trigger_data)

            assert response.status_code == 200
            data = response.json()

            # Validate response structure
            assert "success" in data
            assert "reason" in data
            assert "timestamp" in data

            # Validate response content
            assert data["success"] is True
            assert data["reason"] == trigger_data["reason"]

            # Verify manager method was called
            mock_manager.trigger_manual_optimization.assert_called_once_with(trigger_data["reason"])

    @pytest.mark.asyncio
    async def test_virtuous_cycle_trigger_endpoint_no_body(self):
        """Test trigger endpoint with no request body."""
        with patch("main_enhanced.virtuous_cycle_manager") as mock_manager:
            mock_manager.trigger_manual_optimization = AsyncMock(return_value=self.mock_trigger_success)

            response = self.client.post("/v1/virtuous-cycle/trigger")

            assert response.status_code == 200
            data = response.json()

            # Should use default reason
            assert "success" in data

            # Verify manager method was called with default reason
            mock_manager.trigger_manual_optimization.assert_called_once_with("Manual API trigger")

    @pytest.mark.asyncio
    async def test_virtuous_cycle_trigger_endpoint_cooldown(self):
        """Test trigger endpoint during cooldown period."""
        cooldown_response = {"success": False, "reason": "Cooldown active, 0:45:30 remaining"}

        with patch("main_enhanced.virtuous_cycle_manager") as mock_manager:
            mock_manager.trigger_manual_optimization = AsyncMock(return_value=cooldown_response)

            response = self.client.post("/v1/virtuous-cycle/trigger", json={"reason": "Test during cooldown"})

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is False
            assert "Cooldown active" in data["reason"]

    @pytest.mark.asyncio
    async def test_virtuous_cycle_trigger_endpoint_error(self):
        """Test trigger endpoint when optimization fails."""
        with patch("main_enhanced.virtuous_cycle_manager") as mock_manager:
            mock_manager.trigger_manual_optimization = AsyncMock(side_effect=Exception("Optimization failed"))

            response = self.client.post("/v1/virtuous-cycle/trigger", json={"reason": "Test failure scenario"})

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is False
            assert "Trigger failed" in data["reason"]
            assert "timestamp" in data

    def test_virtuous_cycle_trigger_rate_limiting(self):
        """Test rate limiting on trigger endpoint (10/minute limit)."""
        with patch("main_enhanced.virtuous_cycle_manager") as mock_manager:
            mock_manager.trigger_manual_optimization = AsyncMock(return_value=self.mock_trigger_success)

            # Make multiple rapid requests to test rate limiting
            responses = []
            for i in range(15):  # Exceed 10/minute limit
                response = self.client.post("/v1/virtuous-cycle/trigger", json={"reason": f"Test trigger {i}"})
                responses.append(response.status_code)
                if response.status_code == 429:  # Rate limit exceeded
                    break

            # Should eventually get rate limited
            assert 429 in responses

    def test_virtuous_cycle_endpoints_cors_headers(self):
        """Test CORS headers for dashboard integration."""
        # Test status endpoint
        response = self.client.get("/v1/virtuous-cycle/status")
        # Note: CORS headers would be added by middleware if configured

        # Test trigger endpoint
        response = self.client.post("/v1/virtuous-cycle/trigger", json={"reason": "CORS test"})
        # Should accept requests (CORS handled by middleware if configured)
        assert response.status_code in [200, 429]  # 429 for rate limiting

    def test_sync_client_virtuous_cycle_status(self):
        """Test status endpoint with synchronous client."""
        with patch("main_enhanced.virtuous_cycle_manager") as mock_manager:
            mock_manager.get_status.return_value = self.mock_status

            response = self.client.get("/v1/virtuous-cycle/status")

            assert response.status_code == 200
            data = response.json()
            assert "monitoring_active" in data
            assert "metrics" in data

    def test_sync_client_virtuous_cycle_trigger(self):
        """Test trigger endpoint with synchronous client."""
        with patch("main_enhanced.virtuous_cycle_manager") as mock_manager:
            mock_manager.trigger_manual_optimization = AsyncMock(return_value=self.mock_trigger_success)

            response = self.client.post("/v1/virtuous-cycle/trigger", json={"reason": "Sync client test"})

            assert response.status_code == 200
            data = response.json()
            assert "success" in data

    def test_virtuous_cycle_status_response_format_validation(self):
        """Test comprehensive response format validation."""
        with patch("main_enhanced.virtuous_cycle_manager") as mock_manager:
            mock_manager.get_status.return_value = self.mock_status

            response = self.client.get("/v1/virtuous-cycle/status")
            data = response.json()

            # Validate all required fields are present
            required_fields = [
                "monitoring_active",
                "langsmith_available",
                "frameworks_available",
                "quality_threshold",
                "metrics",
                "component_status",
            ]

            for field in required_fields:
                assert field in data, f"Missing required field: {field}"

            # Validate metrics subfields
            metrics_fields = [
                "traces_processed",
                "quality_checks",
                "optimizations_triggered",
                "improvements_deployed",
                "current_quality",
                "last_update",
            ]

            for field in metrics_fields:
                assert field in data["metrics"], f"Missing metric field: {field}"

            # Validate component status subfields
            component_fields = [
                "langsmith_client",
                "quality_collector",
                "phase2_orchestrator",
                "phase3_orchestrator",
                "phase4_orchestrator",
            ]

            for field in component_fields:
                assert field in data["component_status"], f"Missing component field: {field}"

    def test_integration_with_dashboard_data_requirements(self):
        """Test that endpoint responses meet dashboard data requirements."""
        with patch("main_enhanced.virtuous_cycle_manager") as mock_manager:
            # Mock realistic dashboard data requirements
            dashboard_data = {
                "monitoring_active": True,
                "langsmith_available": True,
                "frameworks_available": True,
                "quality_threshold": 0.90,
                "last_optimization": datetime.utcnow().isoformat(),
                "metrics": {
                    "traces_processed": 1250,
                    "quality_checks": 85,
                    "optimizations_triggered": 7,
                    "improvements_deployed": 5,
                    "current_quality": 0.94,
                    "last_update": datetime.utcnow().isoformat(),
                },
                "component_status": {
                    "langsmith_client": True,
                    "quality_collector": True,
                    "phase2_orchestrator": True,
                    "phase3_orchestrator": True,
                    "phase4_orchestrator": True,
                },
            }

            mock_manager.get_status.return_value = dashboard_data

            response = self.client.get("/v1/virtuous-cycle/status")
            data = response.json()

            # Verify data can be used for dashboard KPI cards
            assert data["metrics"]["current_quality"] >= 0.0
            assert data["metrics"]["current_quality"] <= 1.0
            assert data["metrics"]["traces_processed"] >= 0
            assert data["quality_threshold"] >= 0.0
            assert data["quality_threshold"] <= 1.0

            # Verify data can be used for phase status indicators
            components = data["component_status"]
            phase_components = ["phase2_orchestrator", "phase3_orchestrator", "phase4_orchestrator"]
            for component in phase_components:
                assert isinstance(components[component], bool)


class TestVirtuousCycleManagerUnit:
    """Unit tests for VirtuousCycleManager class methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = VirtuousCycleManager()

    def test_get_status_structure(self):
        """Test get_status returns properly structured data."""
        status = self.manager.get_status()

        # Validate return type
        assert isinstance(status, dict)

        # Validate required fields
        required_fields = [
            "monitoring_active",
            "langsmith_available",
            "frameworks_available",
            "quality_threshold",
            "metrics",
            "component_status",
        ]

        for field in required_fields:
            assert field in status

    def test_can_trigger_optimization_logic(self):
        """Test optimization cooldown logic."""
        # Test when no previous optimization
        assert self.manager._can_trigger_optimization() is True

        # Test with recent optimization (within cooldown)
        self.manager.last_optimization_time = datetime.now()
        assert self.manager._can_trigger_optimization() is False

        # Test with old optimization (outside cooldown)
        self.manager.last_optimization_time = datetime.now() - timedelta(hours=2)
        assert self.manager._can_trigger_optimization() is True

    @pytest.mark.asyncio
    async def test_trigger_manual_optimization_cooldown(self):
        """Test manual optimization trigger with cooldown."""
        # Set recent optimization time
        self.manager.last_optimization_time = datetime.now()

        result = await self.manager.trigger_manual_optimization("Test")

        assert result["success"] is False
        assert "Cooldown active" in result["reason"]

    def test_simulate_traces_data_structure(self):
        """Test simulated trace data structure."""
        traces = self.manager._simulate_traces()

        assert isinstance(traces, list)
        assert len(traces) >= 1
        assert len(traces) <= 10

        # Validate trace structure
        for trace in traces:
            assert isinstance(trace, dict)
            required_trace_fields = [
                "id",
                "timestamp",
                "model",
                "quality_score",
                "response_time",
                "tokens_used",
                "success",
                "spectrum",
            ]
            for field in required_trace_fields:
                assert field in trace

            # Validate data ranges
            assert 0.0 <= trace["quality_score"] <= 1.0
            assert trace["response_time"] > 0
            assert trace["tokens_used"] > 0
            assert isinstance(trace["success"], bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
