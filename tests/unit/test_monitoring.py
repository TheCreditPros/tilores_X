"""
Comprehensive unit tests for monitoring.py
Tests enhanced monitoring and observability for Tilores API
"""

import json
import pytest
from unittest.mock import patch, MagicMock, call
from collections import defaultdict

# Import the module under test
from monitoring import TiloresMonitor, monitor


class TestTiloresMonitorInitialization:
    """Test TiloresMonitor initialization and setup."""

    def test_monitor_initialization_defaults(self):
        """Test monitor initialization with default values."""
        monitor_instance = TiloresMonitor()

        assert monitor_instance.max_history == 1000
        assert len(monitor_instance.api_calls) == 0
        assert len(monitor_instance.error_log) == 0
        assert isinstance(monitor_instance.performance_metrics, defaultdict)
        assert isinstance(monitor_instance.field_coverage_stats, defaultdict)
        assert isinstance(monitor_instance.active_timers, dict)
        assert isinstance(monitor_instance.request_counts, defaultdict)
        assert isinstance(monitor_instance.provider_usage, defaultdict)
        assert isinstance(monitor_instance.start_time, float)

    def test_monitor_initialization_custom_history(self):
        """Test monitor initialization with custom max_history."""
        custom_history = 500
        monitor_instance = TiloresMonitor(max_history=custom_history)

        assert monitor_instance.max_history == custom_history
        assert monitor_instance.api_calls.maxlen == custom_history
        assert monitor_instance.error_log.maxlen == custom_history


class TestTimerFunctionality:
    """Test timer start/end functionality."""

    def test_start_timer_basic(self):
        """Test starting a timer with basic parameters."""
        monitor_instance = TiloresMonitor()

        with patch("time.time", return_value=1000.0):
            timer_id = monitor_instance.start_timer("test_operation")

        assert timer_id == "test_operation_1000000"
        assert timer_id in monitor_instance.active_timers
        assert monitor_instance.active_timers[timer_id]["start"] == 1000.0
        assert monitor_instance.active_timers[timer_id]["operation"] == "test_operation"
        assert monitor_instance.active_timers[timer_id]["metadata"] == {}

    def test_start_timer_with_metadata(self):
        """Test starting a timer with metadata."""
        monitor_instance = TiloresMonitor()
        metadata = {"user_id": "123", "query": "test query"}

        with patch("time.time", return_value=1000.0):
            timer_id = monitor_instance.start_timer("test_operation", metadata)

        assert monitor_instance.active_timers[timer_id]["metadata"] == metadata

    def test_end_timer_successful(self):
        """Test ending a timer successfully."""
        monitor_instance = TiloresMonitor()

        # Start timer
        with patch("time.time", return_value=1000.0):
            timer_id = monitor_instance.start_timer("test_operation")

        # End timer
        with patch("time.time", return_value=1001.5):
            duration = monitor_instance.end_timer(timer_id, success=True)

        assert duration == 1.5
        assert timer_id not in monitor_instance.active_timers
        assert len(monitor_instance.api_calls) == 1
        assert len(monitor_instance.performance_metrics["test_operation"]) == 1

        api_call = monitor_instance.api_calls[0]
        assert api_call["operation"] == "test_operation"
        assert api_call["duration"] == 1.5
        assert api_call["success"] is True
        assert api_call["error"] is None

    def test_end_timer_with_error(self):
        """Test ending a timer with an error."""
        monitor_instance = TiloresMonitor()

        # Start timer
        with patch("time.time", return_value=1000.0):
            timer_id = monitor_instance.start_timer("test_operation")

        # End timer with error
        with patch("time.time", return_value=1001.0):
            duration = monitor_instance.end_timer(timer_id, success=False, error="Test error")

        assert duration == 1.0
        assert len(monitor_instance.error_log) == 1

        api_call = monitor_instance.api_calls[0]
        assert api_call["success"] is False
        assert api_call["error"] == "Test error"

    def test_end_timer_nonexistent(self):
        """Test ending a timer that doesn't exist."""
        monitor_instance = TiloresMonitor()

        with patch.object(monitor_instance.logger, "warning") as mock_warning:
            duration = monitor_instance.end_timer("nonexistent_timer")

        assert duration == 0.0
        mock_warning.assert_called_once_with("Timer nonexistent_timer not found")

    @patch("monitoring.cache_manager")
    @patch("monitoring.CACHE_AVAILABLE", True)
    def test_end_timer_with_redis_storage(self, mock_cache_manager):
        """Test ending a timer with Redis storage enabled."""
        monitor_instance = TiloresMonitor()
        mock_redis = MagicMock()
        mock_cache_manager.redis_client = mock_redis

        # Start and end timer
        with patch("time.time", return_value=1000.0):
            timer_id = monitor_instance.start_timer("test_operation")

        with patch("time.time", return_value=1001.0):
            with patch("monitoring.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "20240101"
                monitor_instance.end_timer(timer_id, success=True)

        # Check Redis calls
        expected_key = "metrics:test_operation:20240101"
        mock_redis.hincrby.assert_any_call(expected_key, "count", 1)
        mock_redis.hincrbyfloat.assert_called_once_with(expected_key, "total_time", 1.0)
        mock_redis.expire.assert_called_once_with(expected_key, 86400 * 7)

    @patch("monitoring.cache_manager")
    @patch("monitoring.CACHE_AVAILABLE", True)
    def test_end_timer_redis_error_handling(self, mock_cache_manager):
        """Test Redis error handling during timer end."""
        monitor_instance = TiloresMonitor()
        mock_redis = MagicMock()
        mock_redis.hincrby.side_effect = Exception("Redis error")
        mock_cache_manager.redis_client = mock_redis

        with patch("time.time", return_value=1000.0):
            timer_id = monitor_instance.start_timer("test_operation")

        with patch("time.time", return_value=1001.0):
            with patch.object(monitor_instance.logger, "debug") as mock_debug:
                monitor_instance.end_timer(timer_id)

        mock_debug.assert_called_once_with("Could not store metrics in Redis: Redis error")


class TestAPICallTracking:
    """Test API call tracking functionality."""

    def test_track_api_call_successful(self):
        """Test tracking a successful API call."""
        monitor_instance = TiloresMonitor()

        monitor_instance.track_api_call("search_customer", 1.23, True, provider="openai", user_id="123")

        assert monitor_instance.request_counts["search_customer"] == 1
        assert monitor_instance.provider_usage["openai"] == 1
        assert len(monitor_instance.api_calls) == 1

        call_data = monitor_instance.api_calls[0]
        assert call_data["function"] == "search_customer"
        assert call_data["execution_time"] == 1.23
        assert call_data["success"] is True
        assert call_data["error"] is None
        assert call_data["provider"] == "openai"
        assert call_data["user_id"] == "123"

    def test_track_api_call_with_error(self):
        """Test tracking a failed API call."""
        monitor_instance = TiloresMonitor()

        monitor_instance.track_api_call("search_customer", 2.45, False, error="Connection timeout")

        assert monitor_instance.request_counts["search_customer"] == 1
        assert len(monitor_instance.api_calls) == 1

        call_data = monitor_instance.api_calls[0]
        assert call_data["success"] is False
        assert call_data["error"] == "Connection timeout"

    def test_track_api_call_multiple_calls(self):
        """Test tracking multiple API calls."""
        monitor_instance = TiloresMonitor()

        # Track multiple calls
        for i in range(3):
            monitor_instance.track_api_call(f"operation_{i}", 1.0, True)

        monitor_instance.track_api_call("search_customer", 1.0, True)
        monitor_instance.track_api_call("search_customer", 1.0, True)

        assert monitor_instance.request_counts["search_customer"] == 2
        assert monitor_instance.request_counts["operation_0"] == 1
        assert len(monitor_instance.api_calls) == 5


class TestErrorRecording:
    """Test error recording functionality."""

    def test_record_error_basic(self):
        """Test basic error recording."""
        monitor_instance = TiloresMonitor()

        monitor_instance.record_error("search_customer", "Database connection failed")

        assert len(monitor_instance.error_log) == 1
        error_entry = monitor_instance.error_log[0]
        assert error_entry["function"] == "search_customer"
        assert error_entry["error"] == "Database connection failed"
        assert error_entry["context"] == {}
        assert "timestamp" in error_entry

    def test_record_error_with_context(self):
        """Test error recording with context."""
        monitor_instance = TiloresMonitor()
        context = {"user_id": "123", "query": "test query", "attempt": 2}

        with patch.object(monitor_instance.logger, "error") as mock_error:
            monitor_instance.record_error("search_customer", "API rate limit exceeded", context)

        assert len(monitor_instance.error_log) == 1
        error_entry = monitor_instance.error_log[0]
        assert error_entry["context"] == context

        # Check logging calls
        expected_calls = [
            call("❌ search_customer error: API rate limit exceeded"),
            call(f"Context: {json.dumps(context, indent=2)}"),
        ]
        mock_error.assert_has_calls(expected_calls)


class TestFieldCoverageTracking:
    """Test field coverage analytics."""

    def test_track_field_coverage_basic(self):
        """Test basic field coverage tracking."""
        monitor_instance = TiloresMonitor()

        result_data = {"name": "John Doe", "email": "john@example.com", "phone": "555-1234"}

        monitor_instance.track_field_coverage(result_data)

        assert monitor_instance.field_coverage_stats["total_calls"] == 1
        assert monitor_instance.field_coverage_stats["total_fields"] == 3
        assert monitor_instance.field_coverage_stats["field_name"] == 1
        assert monitor_instance.field_coverage_stats["field_email"] == 1
        assert monitor_instance.field_coverage_stats["field_phone"] == 1

    def test_track_field_coverage_empty_dict(self):
        """Test field coverage tracking with empty dict."""
        monitor_instance = TiloresMonitor()

        monitor_instance.track_field_coverage({})

        assert monitor_instance.field_coverage_stats["total_calls"] == 1
        assert monitor_instance.field_coverage_stats["total_fields"] == 0

    def test_track_field_coverage_non_dict(self):
        """Test field coverage tracking with non-dict data."""
        monitor_instance = TiloresMonitor()

        # Test with non-dict input (should not crash but not track anything)
        monitor_instance.track_field_coverage("not a dict")  # type: ignore

        # Should not track anything for non-dict input
        assert monitor_instance.field_coverage_stats["total_calls"] == 0

    def test_track_field_coverage_multiple_calls(self):
        """Test field coverage tracking across multiple calls."""
        monitor_instance = TiloresMonitor()

        # First call
        monitor_instance.track_field_coverage({"name": "John", "email": "john@test.com"})
        # Second call
        monitor_instance.track_field_coverage({"name": "Jane", "phone": "555-0000"})

        assert monitor_instance.field_coverage_stats["total_calls"] == 2
        assert monitor_instance.field_coverage_stats["total_fields"] == 4
        assert monitor_instance.field_coverage_stats["field_name"] == 2
        assert monitor_instance.field_coverage_stats["field_email"] == 1
        assert monitor_instance.field_coverage_stats["field_phone"] == 1


class TestTiloresConnectivity:
    """Test Tilores connectivity monitoring."""

    def test_track_tilores_connectivity_connected(self):
        """Test Tilores connectivity when connected."""
        monitor_instance = TiloresMonitor()

        # Mock the import and engine within the function
        with patch("builtins.__import__") as mock_import:
            mock_core_app = MagicMock()
            mock_engine = MagicMock()
            mock_tilores = MagicMock()
            mock_tilores.api.api_url = "https://api.tilores.com"
            mock_engine.tilores = mock_tilores
            mock_engine.tools = ["tool1", "tool2", "tool3"]
            mock_core_app.engine = mock_engine
            mock_import.return_value = mock_core_app

            result = monitor_instance.track_tilores_connectivity()

        assert result["status"] == "connected"
        assert result["api_url"] == "https://api.tilores.com"
        assert result["tools_available"] == 3
        assert "timestamp" in result

    def test_track_tilores_connectivity_no_engine(self):
        """Test Tilores connectivity when engine is None."""
        monitor_instance = TiloresMonitor()

        with patch("builtins.__import__") as mock_import:
            mock_core_app = MagicMock()
            mock_core_app.engine = None
            mock_import.return_value = mock_core_app

            result = monitor_instance.track_tilores_connectivity()

        assert result["status"] == "disconnected"
        assert "timestamp" in result

    def test_track_tilores_connectivity_no_tilores(self):
        """Test Tilores connectivity when tilores is None."""
        monitor_instance = TiloresMonitor()

        with patch("builtins.__import__") as mock_import:
            mock_core_app = MagicMock()
            mock_engine = MagicMock()
            mock_engine.tilores = None
            mock_core_app.engine = mock_engine
            mock_import.return_value = mock_core_app

            result = monitor_instance.track_tilores_connectivity()

        assert result["status"] == "disconnected"

    def test_track_tilores_connectivity_import_error(self):
        """Test Tilores connectivity when import fails."""
        monitor_instance = TiloresMonitor()

        with patch("builtins.__import__", side_effect=ImportError("Module not found")):
            result = monitor_instance.track_tilores_connectivity()

        assert result["status"] == "error"
        assert "Module not found" in result["error"]

    def test_track_tilores_connectivity_unknown_api_url(self):
        """Test Tilores connectivity with unknown API URL."""
        monitor_instance = TiloresMonitor()

        with patch("builtins.__import__") as mock_import:
            mock_core_app = MagicMock()
            mock_engine = MagicMock()
            mock_tilores = MagicMock()
            del mock_tilores.api.api_url  # Remove api_url attribute
            mock_engine.tilores = mock_tilores
            mock_engine.tools = []
            mock_core_app.engine = mock_engine
            mock_import.return_value = mock_core_app

            result = monitor_instance.track_tilores_connectivity()

        assert result["status"] == "connected"
        assert result["api_url"] == "unknown"
        assert result["tools_available"] == 0


class TestMetricsGeneration:
    """Test comprehensive metrics generation."""

    def test_get_metrics_basic(self):
        """Test getting metrics with basic data."""
        monitor_instance = TiloresMonitor()

        # Add some test data
        monitor_instance.api_calls.append({"operation": "test_op", "success": True, "duration": 1.0})
        monitor_instance.performance_metrics["test_op"] = [1.0, 1.5, 0.8]
        monitor_instance.request_counts["search"] = 5
        monitor_instance.provider_usage["openai"] = 3

        with patch.object(monitor_instance, "track_tilores_connectivity") as mock_connectivity:
            mock_connectivity.return_value = {"status": "connected"}
            metrics = monitor_instance.get_metrics()

        assert metrics["status"] == "operational"
        assert "uptime_seconds" in metrics
        assert "uptime_formatted" in metrics
        assert "timestamp" in metrics
        assert metrics["total_requests"] == 1
        assert "100.00%" in metrics["success_rate"]
        assert metrics["request_counts"] == {"search": 5}
        assert metrics["provider_usage"] == {"openai": 3}
        assert "test_op" in metrics["average_response_times"]
        assert metrics["average_response_times"]["test_op"]["avg"] == pytest.approx(1.1, rel=1e-9)
        assert metrics["average_response_times"]["test_op"]["min"] == 0.8
        assert metrics["average_response_times"]["test_op"]["max"] == 1.5
        assert metrics["average_response_times"]["test_op"]["count"] == 3

    def test_get_metrics_empty_state(self):
        """Test getting metrics with no data."""
        monitor_instance = TiloresMonitor()

        with patch.object(monitor_instance, "track_tilores_connectivity") as mock_connectivity:
            mock_connectivity.return_value = {"status": "disconnected"}
            metrics = monitor_instance.get_metrics()

        assert metrics["total_requests"] == 0
        assert metrics["success_rate"] == "100.00%"  # 100% when no calls
        assert metrics["request_counts"] == {}
        assert metrics["average_response_times"] == {}
        assert metrics["field_coverage"]["avg_fields_per_call"] == 0

    def test_get_metrics_field_coverage_calculation(self):
        """Test field coverage calculation in metrics."""
        monitor_instance = TiloresMonitor()

        # Add field coverage data
        monitor_instance.field_coverage_stats["total_calls"] = 5
        monitor_instance.field_coverage_stats["total_fields"] = 15

        with patch.object(monitor_instance, "track_tilores_connectivity"):
            metrics = monitor_instance.get_metrics()

        assert metrics["field_coverage"]["avg_fields_per_call"] == 3.0

    def test_get_metrics_success_rate_calculation(self):
        """Test success rate calculation with mixed results."""
        monitor_instance = TiloresMonitor()

        # Add mixed success/failure calls
        for success in [True, True, False, True, False]:
            monitor_instance.api_calls.append({"success": success})

        with patch.object(monitor_instance, "track_tilores_connectivity"):
            metrics = monitor_instance.get_metrics()

        assert metrics["success_rate"] == "60.00%"  # 3 out of 5 successful


class TestHealthStatus:
    """Test health status determination."""

    def test_get_health_status_healthy(self):
        """Test health status when system is healthy."""
        monitor_instance = TiloresMonitor()

        # Mock healthy metrics
        with patch.object(monitor_instance, "get_metrics") as mock_metrics:
            mock_metrics.return_value = {
                "success_rate": "98.50%",
                "tilores_connectivity": {"status": "connected"},
                "recent_errors": [{"error": "minor issue"}],
                "total_requests": 100,
                "uptime_formatted": "2:30:45",
                "timestamp": "2024-01-01T12:00:00",
            }

            health = monitor_instance.get_health_status()

        assert health["health"] == "healthy"
        assert health["uptime"] == "2:30:45"
        assert health["issues"] == []
        assert health["metrics_summary"]["total_requests"] == 100
        assert health["metrics_summary"]["success_rate"] == "98.50%"
        assert health["metrics_summary"]["tilores_status"] == "connected"

    def test_get_health_status_degraded_low_success_rate(self):
        """Test health status with degraded success rate."""
        monitor_instance = TiloresMonitor()

        with patch.object(monitor_instance, "get_metrics") as mock_metrics:
            mock_metrics.return_value = {
                "success_rate": "85.00%",
                "tilores_connectivity": {"status": "connected"},
                "recent_errors": [],
                "total_requests": 100,
                "uptime_formatted": "1:00:00",
                "timestamp": "2024-01-01T12:00:00",
            }

            health = monitor_instance.get_health_status()

        assert health["health"] == "degraded"
        assert "Low success rate: 85.00%" in health["issues"]

    def test_get_health_status_unhealthy_very_low_success_rate(self):
        """Test health status with very low success rate."""
        monitor_instance = TiloresMonitor()

        with patch.object(monitor_instance, "get_metrics") as mock_metrics:
            mock_metrics.return_value = {
                "success_rate": "75.00%",
                "tilores_connectivity": {"status": "connected"},
                "recent_errors": [],
                "total_requests": 100,
                "uptime_formatted": "1:00:00",
                "timestamp": "2024-01-01T12:00:00",
            }

            health = monitor_instance.get_health_status()

        assert health["health"] == "unhealthy"
        assert "Low success rate: 75.00%" in health["issues"]

    def test_get_health_status_tilores_disconnected(self):
        """Test health status when Tilores is disconnected."""
        monitor_instance = TiloresMonitor()

        with patch.object(monitor_instance, "get_metrics") as mock_metrics:
            mock_metrics.return_value = {
                "success_rate": "98.00%",
                "tilores_connectivity": {"status": "disconnected"},
                "recent_errors": [],
                "total_requests": 100,
                "uptime_formatted": "1:00:00",
                "timestamp": "2024-01-01T12:00:00",
            }

            health = monitor_instance.get_health_status()

        assert health["health"] == "unhealthy"
        assert "Tilores API disconnected" in health["issues"]

    def test_get_health_status_high_error_rate(self):
        """Test health status with high error rate."""
        monitor_instance = TiloresMonitor()

        recent_errors = [{"error": f"Error {i}"} for i in range(8)]

        with patch.object(monitor_instance, "get_metrics") as mock_metrics:
            mock_metrics.return_value = {
                "success_rate": "98.00%",
                "tilores_connectivity": {"status": "connected"},
                "recent_errors": recent_errors,
                "total_requests": 100,
                "uptime_formatted": "1:00:00",
                "timestamp": "2024-01-01T12:00:00",
            }

            health = monitor_instance.get_health_status()

        assert health["health"] == "degraded"
        assert "High error rate: 8 recent errors" in health["issues"]

    def test_get_health_status_multiple_issues(self):
        """Test health status with multiple issues."""
        monitor_instance = TiloresMonitor()

        with patch.object(monitor_instance, "get_metrics") as mock_metrics:
            mock_metrics.return_value = {
                "success_rate": "70.00%",
                "tilores_connectivity": {"status": "error"},
                "recent_errors": [{"error": f"Error {i}"} for i in range(6)],
                "total_requests": 100,
                "uptime_formatted": "1:00:00",
                "timestamp": "2024-01-01T12:00:00",
            }

            health = monitor_instance.get_health_status()

        assert health["health"] == "unhealthy"
        assert len(health["issues"]) == 3  # Low success rate, Tilores disconnected, high errors


class TestGlobalMonitorInstance:
    """Test the global monitor instance."""

    def test_global_monitor_exists(self):
        """Test that global monitor instance exists."""
        assert monitor is not None
        assert isinstance(monitor, TiloresMonitor)
        assert monitor.max_history == 1000


class TestCacheIntegration:
    """Test cache availability scenarios."""

    @patch("monitoring.CACHE_AVAILABLE", False)
    def test_end_timer_no_cache_available(self):
        """Test timer end when cache is not available."""
        monitor_instance = TiloresMonitor()

        with patch("time.time", return_value=1000.0):
            timer_id = monitor_instance.start_timer("test_operation")

        with patch("time.time", return_value=1001.0):
            # Should not raise any errors when cache not available
            duration = monitor_instance.end_timer(timer_id)

        assert duration == 1.0
        assert len(monitor_instance.api_calls) == 1
