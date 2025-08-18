#!/usr/bin/env python3
"""
Additional comprehensive tests for LangSmith Enterprise Client.

Focuses on improving test coverage and reliability for critical
enterprise functionality and edge cases.

Author: Roo (Elite Software Engineer)
Created: 2025-08-17
Test Coverage: Additional LangSmith Enterprise Client Tests
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

# Import components to test
from langsmith_enterprise_client import (
    EnterpriseLangSmithClient,
    LangSmithConfig,
    QualityMetrics,
)


class TestLangSmithConfigValidation:
    """Additional tests for LangSmith configuration validation."""

    def test_config_validation_with_minimal_values(self):
        """Test configuration with minimal required values."""
        config = LangSmithConfig(api_key="minimal_key", organization_id="minimal_org")

        assert config.api_key == "minimal_key"
        assert config.organization_id == "minimal_org"
        assert config.timeout > 0
        assert config.max_retries > 0

    def test_config_validation_with_edge_case_values(self):
        """Test configuration with edge case values."""
        config = LangSmithConfig(
            api_key="edge_case_key_with_special_chars_!@#$%",
            organization_id="edge-case-org-123",
            timeout=1,
            max_retries=1,
            rate_limit_requests_per_minute=1,
        )

        assert config.timeout == 1
        assert config.max_retries == 1
        assert config.rate_limit_requests_per_minute == 1


class TestEnterpriseLangSmithClientRobustness:
    """Additional robustness tests for enterprise client."""

    @pytest.fixture
    def robust_client(self):
        """Create robust client for testing."""
        config = LangSmithConfig(
            api_key="robust_test_key", organization_id="robust_test_org", timeout=10, max_retries=2
        )
        return EnterpriseLangSmithClient(config)

    @pytest.mark.asyncio
    async def test_session_lifecycle_management(self, robust_client):
        """Test complete session lifecycle management."""
        # Initial state
        assert robust_client.session is None

        # Ensure session creation
        await robust_client._ensure_session()
        assert robust_client.session is not None

        # Multiple ensure calls should not create new sessions
        session_ref = robust_client.session
        await robust_client._ensure_session()
        assert robust_client.session is session_ref

        # Close session
        await robust_client.close()
        assert robust_client.session is None

    @pytest.mark.asyncio
    async def test_rate_limiting_edge_cases(self, robust_client):
        """Test rate limiting with edge cases."""
        import time

        # Test with empty request history
        robust_client._request_times = []
        await robust_client._rate_limit_check()
        assert len(robust_client._request_times) == 1

        # Test with old requests (should be cleaned up)
        old_time = time.time() - 120  # 2 minutes ago
        robust_client._request_times = [old_time, old_time + 1, old_time + 2]
        await robust_client._rate_limit_check()

        # Old requests should be removed, new one added
        assert all(t > old_time + 60 for t in robust_client._request_times)

    @pytest.mark.asyncio
    async def test_error_handling_comprehensive(self, robust_client):
        """Test comprehensive error handling scenarios."""
        mock_session = MagicMock()
        robust_client.session = mock_session

        # Test connection timeout
        mock_response = MagicMock()
        mock_response.status = 408  # Request timeout
        mock_response.text = AsyncMock(return_value="Request timeout")
        mock_session.request.return_value.__aenter__.return_value = mock_response

        with patch.object(robust_client, "_ensure_session"), patch.object(robust_client, "_rate_limit_check"):

            with pytest.raises(Exception, match="HTTP 408"):
                await robust_client._make_request("GET", "/test")

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, robust_client):
        """Test handling of concurrent requests."""
        mock_session = MagicMock()
        robust_client.session = mock_session

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"success": True})
        mock_session.request.return_value.__aenter__.return_value = mock_response

        with patch.object(robust_client, "_ensure_session"), patch.object(robust_client, "_rate_limit_check"):

            # Execute multiple concurrent requests
            tasks = [robust_client._make_request("GET", f"/test_{i}") for i in range(5)]

            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(r["success"] for r in results)


class TestQualityMetricsCalculationRobustness:
    """Additional tests for quality metrics calculation robustness."""

    @pytest.fixture
    def metrics_client(self):
        """Create client for metrics testing."""
        config = LangSmithConfig(api_key="metrics_test", organization_id="metrics_org")
        return EnterpriseLangSmithClient(config)

    def test_quality_score_calculation_edge_cases(self, metrics_client):
        """Test quality score calculation with edge cases."""
        # Test with empty feedback
        empty_feedback = {}
        run_success = {"error": None}
        score = metrics_client._calculate_quality_score(empty_feedback, run_success)
        assert score == 0.85  # Default for successful runs

        # Test with error run
        run_error = {"error": "API failure"}
        score = metrics_client._calculate_quality_score(empty_feedback, run_error)
        assert score == 0.0  # Error runs get 0 score

        # Test with unknown feedback keys
        unknown_feedback = {"unknown_metric": 0.95, "custom_score": 0.88}
        score = metrics_client._calculate_quality_score(unknown_feedback, run_success)
        assert 0.0 <= score <= 1.0  # Should be valid score

    def test_quality_score_calculation_weighted_comprehensive(self, metrics_client):
        """Test comprehensive weighted quality score calculation."""
        feedback_scores = {"quality": 1.0, "accuracy": 0.9, "helpfulness": 0.8, "relevance": 0.7, "custom_metric": 0.6}
        run = {"error": None}

        score = metrics_client._calculate_quality_score(feedback_scores, run)

        # Should be weighted average with custom metric getting default weight
        expected = (1.0 * 0.4) + (0.9 * 0.3) + (0.8 * 0.2) + (0.7 * 0.1) + (0.6 * 0.1)
        expected_normalized = expected / (0.4 + 0.3 + 0.2 + 0.1 + 0.1)

        assert abs(score - expected_normalized) < 0.01

    @pytest.mark.asyncio
    async def test_quality_metrics_with_large_dataset(self, metrics_client):
        """Test quality metrics processing with large datasets."""
        # Mock large run dataset
        large_runs = []
        for i in range(1000):
            large_runs.append(
                {
                    "id": f"large_run_{i}",
                    "session_name": f"session_{i % 10}",
                    "start_time": f"2025-08-17T{(i % 24):02d}:00:00Z",
                    "feedback": [{"key": "quality", "score": 0.85 + (i % 20) * 0.005}],
                    "extra": {"metadata": {"model": ["gpt-4o-mini", "claude-3-haiku"][i % 2]}},
                    "latency": 1.5 + (i % 10) * 0.1,
                    "total_tokens": 100 + (i % 100),
                    "total_cost": 0.001 + (i % 50) * 0.00001,
                }
            )

        with patch.object(metrics_client, "list_runs", return_value=large_runs):
            metrics = await metrics_client.get_quality_metrics(limit=1000)

            assert len(metrics) == 1000
            assert all(isinstance(m, QualityMetrics) for m in metrics)
            assert all(0.85 <= m.quality_score <= 0.95 for m in metrics)


class TestDatasetManagementRobustness:
    """Additional tests for dataset management robustness."""

    @pytest.fixture
    def dataset_client(self):
        """Create client for dataset testing."""
        config = LangSmithConfig(api_key="dataset_test", organization_id="dataset_org")
        return EnterpriseLangSmithClient(config)

    @pytest.mark.asyncio
    async def test_dataset_operations_with_large_examples(self, dataset_client):
        """Test dataset operations with large example sets."""
        # Create large example set
        large_examples = []
        for i in range(100):
            large_examples.append(
                {
                    "input": {"query": f"Test query {i}", "context": {"id": i, "type": "test"}},
                    "output": {"response": f"Test response {i}", "confidence": 0.9 + (i % 10) * 0.01},
                    "metadata": {"quality_score": 0.85 + (i % 15) * 0.01, "processing_time": 1.0 + (i % 5) * 0.2},
                }
            )

        mock_response = {
            "examples_added": 100,
            "dataset_id": "large_dataset_123",
            "success": True,
            "processing_time": 2.5,
        }

        with patch.object(dataset_client, "_make_request", return_value=mock_response):
            result = await dataset_client.add_examples_to_dataset("large_dataset_123", large_examples)

            assert result["examples_added"] == 100
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_dataset_search_with_complex_queries(self, dataset_client):
        """Test dataset search with complex query patterns."""
        complex_examples = [
            {
                "id": "complex_1",
                "input": {"query": "customer profile analysis with risk assessment"},
                "output": {"response": "Comprehensive analysis result"},
                "metadata": {
                    "quality_score": 0.96,
                    "complexity": "high",
                    "tags": ["customer", "profile", "risk", "analysis"],
                },
            },
            {
                "id": "complex_2",
                "input": {"query": "credit evaluation for loan approval"},
                "output": {"response": "Credit evaluation summary"},
                "metadata": {
                    "quality_score": 0.94,
                    "complexity": "medium",
                    "tags": ["credit", "evaluation", "loan", "approval"],
                },
            },
        ]

        mock_response = {"examples": complex_examples}

        with patch.object(dataset_client, "_make_request", return_value=mock_response):
            results = await dataset_client.search_dataset_examples(
                dataset_id="complex_dataset", query="customer credit analysis", limit=50
            )

            assert len(results) == 2
            assert all("quality_score" in ex["metadata"] for ex in results)


class TestPredictiveAnalyticsRobustness:
    """Additional tests for predictive analytics robustness."""

    @pytest.fixture
    def analytics_client(self):
        """Create client for analytics testing."""
        config = LangSmithConfig(api_key="analytics_test", organization_id="analytics_org")
        return EnterpriseLangSmithClient(config)

    def test_quality_trend_calculation_with_insufficient_data(self, analytics_client):
        """Test quality trend calculation with insufficient data."""
        # Test with no metrics
        empty_metrics = []
        trend = analytics_client._calculate_quality_trend(empty_metrics)
        assert trend["trend"] == "no_data"
        assert trend["slope"] == 0.0

        # Test with single metric
        single_metric = [
            QualityMetrics(
                run_id="single_run",
                session_name="test",
                model="gpt-4o-mini",
                quality_score=0.90,
                latency_ms=2000,
                token_count=150,
                cost=0.001,
                timestamp="2025-08-17T10:00:00Z",
            )
        ]
        trend = analytics_client._calculate_quality_trend(single_metric)
        assert trend["trend"] == "insufficient_data"

    def test_performance_trend_calculation_robustness(self, analytics_client):
        """Test performance trend calculation robustness."""
        # Test with no latency data
        no_latency_metrics = [
            QualityMetrics(
                run_id="no_latency",
                session_name="test",
                model="gpt-4o-mini",
                quality_score=0.90,
                latency_ms=0,  # No latency data
                token_count=150,
                cost=0.001,
                timestamp="2025-08-17T10:00:00Z",
            )
        ]

        trend = analytics_client._calculate_performance_trend(no_latency_metrics)
        assert trend["trend"] == "no_data"
        assert trend["avg_latency"] == 0.0

    def test_cost_trend_calculation_robustness(self, analytics_client):
        """Test cost trend calculation robustness."""
        # Test with no cost data
        no_cost_metrics = [
            QualityMetrics(
                run_id="no_cost",
                session_name="test",
                model="gpt-4o-mini",
                quality_score=0.90,
                latency_ms=2000,
                token_count=150,
                cost=0.0,  # No cost data
                timestamp="2025-08-17T10:00:00Z",
            )
        ]

        trend = analytics_client._calculate_cost_trend(no_cost_metrics)
        assert trend["total_cost"] == 0.0
        assert trend["avg_cost_per_run"] == 0.0

    @pytest.mark.asyncio
    async def test_predictions_generation_robustness(self, analytics_client):
        """Test predictions generation with various scenarios."""
        # Test with stable trend
        stable_trends = {"quality_trend": {"current_quality": 0.92, "slope": 0.001, "confidence": 0.95}}  # Very stable

        predictions = await analytics_client._generate_predictions(stable_trends)
        assert predictions["needs_intervention"] is False
        assert predictions["recommendation"] == "Quality trend stable"

        # Test with declining trend
        declining_trends = {"quality_trend": {"current_quality": 0.88, "slope": -0.02, "confidence": 0.85}}  # Declining

        predictions = await analytics_client._generate_predictions(declining_trends)
        assert predictions["needs_intervention"] is True
        assert "optimization recommended" in predictions["recommendation"].lower()


class TestBulkOperationsRobustness:
    """Additional tests for bulk operations robustness."""

    @pytest.fixture
    def bulk_client(self):
        """Create client for bulk operations testing."""
        config = LangSmithConfig(api_key="bulk_test", organization_id="bulk_org")
        return EnterpriseLangSmithClient(config)

    @pytest.mark.asyncio
    async def test_bulk_export_with_comprehensive_filters(self, bulk_client):
        """Test bulk export with comprehensive filtering options."""
        start_time = datetime.now() - timedelta(days=30)
        end_time = datetime.now()

        mock_response = {
            "export_id": "comprehensive_export_789",
            "status": "pending",
            "estimated_size": 1024 * 1024 * 50,  # 50MB
            "estimated_records": 25000,
            "filters_applied": {
                "session_names": ["session_1", "session_2"],
                "time_range": True,
                "feedback_included": True,
                "traces_included": True,
            },
        }

        with patch.object(bulk_client, "_make_request", return_value=mock_response):
            export_id = await bulk_client.create_bulk_export(
                session_names=["session_1", "session_2"],
                start_time=start_time,
                end_time=end_time,
                format_type="jsonl",
                include_feedback=True,
                include_traces=True,
            )

            assert export_id == "comprehensive_export_789"

    @pytest.mark.asyncio
    async def test_bulk_export_status_polling(self, bulk_client):
        """Test bulk export status polling scenarios."""
        export_id = "polling_test_export"

        # Test pending status
        pending_response = {
            "export_id": export_id,
            "status": "pending",
            "progress": 25,
            "estimated_completion": "2025-08-17T11:00:00Z",
        }

        # Test completed status
        completed_response = {
            "export_id": export_id,
            "status": "completed",
            "progress": 100,
            "file_size": 1024 * 1024 * 75,  # 75MB
            "record_count": 37500,
            "download_url": f"https://api.smith.langchain.com/exports/{export_id}/download",
        }

        with patch.object(bulk_client, "_make_request", side_effect=[pending_response, completed_response]):
            # Check pending status
            status = await bulk_client.get_bulk_export_status(export_id)
            assert status["status"] == "pending"
            assert status["progress"] == 25

            # Check completed status
            status = await bulk_client.get_bulk_export_status(export_id)
            assert status["status"] == "completed"
            assert status["progress"] == 100
            assert status["record_count"] == 37500


class TestPatternIndexingRobustness:
    """Additional tests for pattern indexing robustness."""

    @pytest.fixture
    def pattern_client(self):
        """Create client for pattern testing."""
        config = LangSmithConfig(api_key="pattern_test", organization_id="pattern_org")
        return EnterpriseLangSmithClient(config)

    def test_similarity_calculation_edge_cases(self, pattern_client):
        """Test similarity calculation with edge cases."""
        # Test with empty contexts
        empty_context1 = {}
        empty_context2 = {}
        similarity = pattern_client._calculate_similarity(empty_context1, empty_context2)
        # The algorithm still calculates some similarity even with empty contexts
        assert 0.0 <= similarity <= 0.5

        # Test with partial context overlap
        partial_context1 = {"model": "gpt-4o-mini"}
        partial_context2 = {"spectrum": "customer_profile"}
        similarity = pattern_client._calculate_similarity(partial_context1, partial_context2)
        assert 0.0 <= similarity <= 1.0

    def test_context_to_search_query_comprehensive(self, pattern_client):
        """Test context to search query conversion comprehensively."""
        # Test with full context
        full_context = {
            "spectrum": "credit_analysis",
            "model": "gpt-4o-mini",
            "query_type": "risk_assessment",
            "complexity": "high",
        }

        query = pattern_client._context_to_search_query(full_context)
        assert "spectrum:credit_analysis" in query
        assert "model:gpt-4o-mini" in query
        assert "type:risk_assessment" in query

        # Test with empty context
        empty_context = {}
        query = pattern_client._context_to_search_query(empty_context)
        assert query == "high_quality"

    @pytest.mark.asyncio
    async def test_pattern_indexing_with_diverse_data(self, pattern_client):
        """Test pattern indexing with diverse data types."""
        diverse_runs = [
            {
                "run_id": "diverse_1",
                "quality_score": 0.97,
                "model": "gpt-4o-mini",
                "session_name": "customer_analysis",
                "inputs": {"query": "Complex customer analysis"},
                "outputs": {"response": "Detailed analysis"},
                "metadata": {"spectrum": "customer_profile", "complexity": "high"},
            },
            {
                "run_id": "diverse_2",
                "quality_score": 0.95,
                "model": "claude-3-haiku",
                "session_name": "credit_evaluation",
                "inputs": {"query": "Credit risk assessment"},
                "outputs": {"response": "Risk evaluation"},
                "metadata": {"spectrum": "credit_analysis", "complexity": "medium"},
            },
        ]

        with patch.object(pattern_client, "get_high_quality_runs", return_value=diverse_runs), patch.object(
            pattern_client, "add_examples_to_dataset", return_value={"success": True}
        ):

            result = await pattern_client.index_successful_patterns(
                dataset_id="diverse_patterns", quality_threshold=0.94
            )

            assert result["patterns_indexed"] == 2
            assert result["quality_threshold"] == 0.94


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
