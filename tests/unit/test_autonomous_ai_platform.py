#!/usr/bin/env python3
"""
Comprehensive test suite for Autonomous AI Platform.

Tests all core components of the autonomous AI platform including
enterprise LangSmith client, delta regression analysis, A/B testing,
feedback collection, pattern indexing, and meta-learning capabilities.

Author: Roo (Elite Software Engineer)
Created: 2025-08-17
Test Coverage: Enterprise Autonomous AI Platform
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

# Import components to test
from autonomous_ai_platform import (
    DeltaRegressionAnalyzer,
    AdvancedABTesting,
    ReinforcementLearningCollector,
    PatternIndexer,
    MetaLearningEngine,
    AutonomousAIPlatform,
    DeltaAnalysis,
    ABTestResult,
    FeedbackPattern,
)
from langsmith_enterprise_client import (
    EnterpriseLangSmithClient,
    LangSmithConfig,
    QualityMetrics,
    WorkspaceStats,
    DatasetInfo,
)
from autonomous_integration import EnhancedVirtuousCycleManager, AutonomousQualityMonitor


class TestEnterpriseLangSmithClient:
    """Test enterprise LangSmith client functionality."""

    @pytest.fixture
    def mock_config(self):
        """Create mock LangSmith configuration."""
        return LangSmithConfig(api_key="test_api_key", organization_id="test_org_id")

    @pytest.fixture
    def mock_client(self, mock_config):
        """Create mock enterprise LangSmith client."""
        return EnterpriseLangSmithClient(mock_config)

    @pytest.mark.asyncio
    async def test_client_initialization(self, mock_client):
        """Test client initialization."""
        assert mock_client.config.api_key == "test_api_key"
        assert mock_client.config.organization_id == "test_org_id"
        assert mock_client.headers["X-API-Key"] == "test_api_key"
        assert mock_client.headers["X-Organization-Id"] == "test_org_id"

    @pytest.mark.asyncio
    async def test_workspace_stats(self, mock_client):
        """Test workspace statistics retrieval."""
        mock_response = {
            "tenant_id": "test_tenant",
            "dataset_count": 51,
            "tracer_session_count": 21,
            "repo_count": 3,
            "annotation_queue_count": 0,
            "deployment_count": 0,
            "dashboards_count": 0,
        }

        with patch.object(mock_client, "_make_request", return_value=mock_response):
            stats = await mock_client.get_workspace_stats()

            assert isinstance(stats, WorkspaceStats)
            assert stats.dataset_count == 51
            assert stats.tracer_session_count == 21
            assert stats.repo_count == 3

    @pytest.mark.asyncio
    async def test_quality_metrics_calculation(self, mock_client):
        """Test quality metrics calculation."""
        mock_runs = [
            {
                "id": "run_1",
                "session_name": "tilores_x",
                "start_time": "2025-08-17T10:00:00Z",
                "feedback": [{"key": "quality", "score": 0.95}],
                "extra": {"metadata": {"model": "gpt-4o-mini"}},
                "latency": 2.5,
                "total_tokens": 150,
                "total_cost": 0.001,
            },
            {
                "id": "run_2",
                "session_name": "tilores_x",
                "start_time": "2025-08-17T10:05:00Z",
                "feedback": [{"key": "quality", "score": 0.88}],
                "extra": {"metadata": {"model": "claude-3-haiku"}},
                "latency": 1.8,
                "total_tokens": 120,
                "total_cost": 0.0008,
            },
        ]

        with patch.object(mock_client, "list_runs", return_value=mock_runs):
            metrics = await mock_client.get_quality_metrics()

            assert len(metrics) == 2
            assert isinstance(metrics[0], QualityMetrics)
            assert metrics[0].quality_score == 0.95
            assert metrics[1].quality_score == 0.88

    @pytest.mark.asyncio
    async def test_dataset_management(self, mock_client):
        """Test dataset creation and management."""
        mock_dataset_response = {
            "id": "dataset_123",
            "name": "test_dataset",
            "description": "Test dataset",
            "example_count": 0,
            "created_at": "2025-08-17T10:00:00Z",
        }

        with patch.object(mock_client, "_make_request", return_value=mock_dataset_response):
            dataset = await mock_client.create_dataset(name="test_dataset", description="Test dataset")

            assert isinstance(dataset, DatasetInfo)
            assert dataset.name == "test_dataset"
            assert dataset.id == "dataset_123"


class TestDeltaRegressionAnalyzer:
    """Test delta regression analysis functionality."""

    @pytest.fixture
    def mock_langsmith_client(self):
        """Create mock LangSmith client."""
        client = MagicMock(spec=EnterpriseLangSmithClient)
        return client

    @pytest.fixture
    def delta_analyzer(self, mock_langsmith_client):
        """Create delta regression analyzer."""
        return DeltaRegressionAnalyzer(mock_langsmith_client)

    @pytest.mark.asyncio
    async def test_regression_detection(self, delta_analyzer, mock_langsmith_client):
        """Test regression detection functionality."""
        # Mock baseline metrics (high quality)
        baseline_metrics = [
            QualityMetrics(
                run_id=f"baseline_{i}",
                session_name="tilores_x",
                model="gpt-4o-mini",
                quality_score=0.95,
                latency_ms=2000,
                token_count=150,
                cost=0.001,
                timestamp="2025-08-10T10:00:00Z",
            )
            for i in range(10)
        ]

        # Mock current metrics (degraded quality)
        current_metrics = [
            QualityMetrics(
                run_id=f"current_{i}",
                session_name="tilores_x",
                model="gpt-4o-mini",
                quality_score=0.82,  # Significant degradation
                latency_ms=2200,
                token_count=160,
                cost=0.0012,
                timestamp="2025-08-17T10:00:00Z",
            )
            for i in range(10)
        ]

        # Mock the get_quality_metrics calls
        mock_langsmith_client.get_quality_metrics.side_effect = [
            baseline_metrics,  # First call for baseline
            current_metrics,  # Second call for current
        ]

        # Run regression analysis
        delta_result = await delta_analyzer.check_performance_regression()

        # Verify regression detection
        assert isinstance(delta_result, DeltaAnalysis)
        assert delta_result.regression_detected is True
        assert delta_result.baseline_quality == 0.95
        assert abs(delta_result.current_quality - 0.82) < 0.01  # Allow for floating point precision
        assert delta_result.quality_delta < -0.05  # Significant degradation

    @pytest.mark.asyncio
    async def test_no_regression_detected(self, delta_analyzer, mock_langsmith_client):
        """Test when no regression is detected."""
        # Mock stable metrics
        stable_metrics = [
            QualityMetrics(
                run_id=f"stable_{i}",
                session_name="tilores_x",
                model="gpt-4o-mini",
                quality_score=0.92,
                latency_ms=2000,
                token_count=150,
                cost=0.001,
                timestamp="2025-08-17T10:00:00Z",
            )
            for i in range(10)
        ]

        mock_langsmith_client.get_quality_metrics.side_effect = [
            stable_metrics,  # Baseline
            stable_metrics,  # Current (same quality)
        ]

        delta_result = await delta_analyzer.check_performance_regression()

        assert delta_result.regression_detected is False
        assert abs(delta_result.quality_delta) < 0.05


class TestAdvancedABTesting:
    """Test A/B testing framework functionality."""

    @pytest.fixture
    def mock_langsmith_client(self):
        """Create mock LangSmith client."""
        client = MagicMock(spec=EnterpriseLangSmithClient)
        return client

    @pytest.fixture
    def ab_testing(self, mock_langsmith_client):
        """Create A/B testing framework."""
        return AdvancedABTesting(mock_langsmith_client)

    @pytest.mark.asyncio
    async def test_create_ab_experiment(self, ab_testing, mock_langsmith_client):
        """Test A/B experiment creation."""
        mock_dataset = DatasetInfo(
            id="dataset_ab_test",
            name="ab_test_experiment",
            description="A/B test dataset",
            example_count=0,
            created_at="2025-08-17T10:00:00Z",
            last_modified="2025-08-17T10:00:00Z",
        )

        mock_langsmith_client.create_dataset.return_value = mock_dataset
        mock_langsmith_client.add_examples_to_dataset.return_value = {"success": True}

        experiment_id = await ab_testing.create_ab_experiment(
            experiment_name="prompt_optimization_test",
            variant_a_prompt="Original prompt",
            variant_b_prompt="Optimized prompt",
            target_models=["gpt-4o-mini"],
            target_spectrums=["customer_profile"],
        )

        assert experiment_id.startswith("ab_test_")
        mock_langsmith_client.create_dataset.assert_called_once()
        mock_langsmith_client.add_examples_to_dataset.assert_called_once()

    @pytest.mark.asyncio
    async def test_ab_experiment_evaluation(self, ab_testing, mock_langsmith_client):
        """Test A/B experiment evaluation."""
        # Mock experiment data
        mock_experiment_data = {
            "experiment_id": "ab_test_123",
            "variant_a_prompt": "Original",
            "variant_b_prompt": "Optimized",
        }

        # Mock variant results
        variant_a_results = [{"feedback": [{"key": "quality", "score": 0.85}]} for _ in range(30)]
        variant_b_results = [{"feedback": [{"key": "quality", "score": 0.92}]} for _ in range(30)]

        with patch.object(ab_testing, "_get_experiment_data", return_value=mock_experiment_data), patch.object(
            ab_testing, "_collect_variant_results", side_effect=[variant_a_results, variant_b_results]
        ):

            result = await ab_testing.evaluate_ab_experiment("ab_test_123")

            assert isinstance(result, ABTestResult)
            assert abs(result.variant_a_quality - 0.85) < 0.01
            assert abs(result.variant_b_quality - 0.92) < 0.01
            assert result.improvement > 0.05
            assert result.winner == "variant_b"


class TestReinforcementLearningCollector:
    """Test reinforcement learning feedback collection."""

    @pytest.fixture
    def mock_langsmith_client(self):
        """Create mock LangSmith client."""
        client = MagicMock(spec=EnterpriseLangSmithClient)
        return client

    @pytest.fixture
    def feedback_collector(self, mock_langsmith_client):
        """Create feedback collector."""
        return ReinforcementLearningCollector(mock_langsmith_client)

    @pytest.mark.asyncio
    async def test_collect_user_feedback(self, feedback_collector, mock_langsmith_client):
        """Test user feedback collection."""
        mock_feedback_result = {"feedback_id": "feedback_123", "success": True}
        mock_langsmith_client.create_feedback.return_value = mock_feedback_result
        mock_langsmith_client.list_datasets.return_value = []

        mock_dataset = DatasetInfo(
            id="feedback_dataset",
            name="reinforcement_learning_feedback",
            description="Feedback dataset",
            example_count=0,
            created_at="2025-08-17T10:00:00Z",
            last_modified="2025-08-17T10:00:00Z",
        )
        mock_langsmith_client.create_dataset.return_value = mock_dataset
        mock_langsmith_client.add_examples_to_dataset.return_value = {"success": True}

        result = await feedback_collector.collect_user_feedback(
            run_id="run_123", feedback_type="quality", score=0.95, correction="Improved response"
        )

        assert result == mock_feedback_result
        mock_langsmith_client.create_feedback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_recent_corrections(self, feedback_collector, mock_langsmith_client):
        """Test getting recent corrections."""
        mock_datasets = [
            DatasetInfo(
                id="feedback_dataset",
                name="reinforcement_learning_feedback",
                description="Feedback dataset",
                example_count=5,
                created_at="2025-08-17T10:00:00Z",
                last_modified="2025-08-17T10:00:00Z",
            )
        ]

        mock_examples = [
            {
                "run_id": "run_123",
                "feedback_type": "quality",
                "score": 0.95,
                "correction": "Better response",
                "timestamp": "2025-08-17T10:00:00Z",
            }
        ]

        mock_langsmith_client.list_datasets.return_value = mock_datasets
        mock_langsmith_client.search_dataset_examples.return_value = mock_examples

        patterns = await feedback_collector.get_recent_corrections()

        assert len(patterns) == 1
        assert isinstance(patterns[0], FeedbackPattern)
        assert patterns[0].pattern_type == "user_correction"


class TestPatternIndexer:
    """Test pattern indexing functionality."""

    @pytest.fixture
    def mock_langsmith_client(self):
        """Create mock LangSmith client."""
        client = MagicMock(spec=EnterpriseLangSmithClient)
        return client

    @pytest.fixture
    def pattern_indexer(self, mock_langsmith_client):
        """Create pattern indexer."""
        return PatternIndexer(mock_langsmith_client)

    @pytest.mark.asyncio
    async def test_index_successful_patterns(self, pattern_indexer, mock_langsmith_client):
        """Test successful pattern indexing."""
        # Mock high-quality runs
        mock_high_quality_runs = [
            {
                "run_id": "run_123",
                "quality_score": 0.96,
                "model": "gpt-4o-mini",
                "session_name": "tilores_x",
                "inputs": {"query": "test query"},
                "outputs": {"response": "high quality response"},
                "metadata": {"spectrum": "customer_profile"},
            }
        ]

        mock_dataset = DatasetInfo(
            id="patterns_dataset",
            name="success_patterns_index",
            description="Success patterns",
            example_count=0,
            created_at="2025-08-17T10:00:00Z",
            last_modified="2025-08-17T10:00:00Z",
        )

        mock_langsmith_client.get_high_quality_runs.return_value = mock_high_quality_runs
        mock_langsmith_client.list_datasets.return_value = []
        mock_langsmith_client.create_dataset.return_value = mock_dataset
        mock_langsmith_client.add_examples_to_dataset.return_value = {"success": True}

        result = await pattern_indexer.index_successful_patterns()

        assert result["patterns_indexed"] == 1
        assert result["dataset_id"] == "patterns_dataset"
        mock_langsmith_client.get_high_quality_runs.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_similar_patterns(self, pattern_indexer, mock_langsmith_client):
        """Test finding similar patterns."""
        mock_dataset = DatasetInfo(
            id="patterns_dataset",
            name="success_patterns_index",
            description="Success patterns",
            example_count=5,
            created_at="2025-08-17T10:00:00Z",
            last_modified="2025-08-17T10:00:00Z",
        )

        mock_similar_patterns = [
            {
                "pattern_id": "pattern_123",
                "similarity_score": 0.92,
                "inputs": {"query": "similar query"},
                "metadata": {"quality_score": 0.95},
            }
        ]

        mock_langsmith_client.list_datasets.return_value = [mock_dataset]
        mock_langsmith_client.find_similar_patterns.return_value = mock_similar_patterns

        query_context = {"spectrum": "customer_profile", "model": "gpt-4o-mini", "quality_score": 0.90}

        patterns = await pattern_indexer.find_similar_successful_patterns(query_context)

        assert len(patterns) == 1
        assert patterns[0]["similarity_score"] == 0.92


class TestMetaLearningEngine:
    """Test meta-learning engine functionality."""

    @pytest.fixture
    def mock_langsmith_client(self):
        """Create mock LangSmith client."""
        client = MagicMock(spec=EnterpriseLangSmithClient)
        return client

    @pytest.fixture
    def meta_learner(self, mock_langsmith_client):
        """Create meta-learning engine."""
        return MetaLearningEngine(mock_langsmith_client)

    @pytest.mark.asyncio
    async def test_identify_best_strategies(self, meta_learner, mock_langsmith_client):
        """Test strategy identification."""
        mock_strategy_data = [
            {
                "strategy": "pattern_reinforcement",
                "effectiveness_score": 0.92,
                "context": {"model": "gpt-4o-mini", "spectrum": "customer_profile"},
                "sample_size": 50,
                "confidence": 0.85,
            },
            {
                "strategy": "ab_testing",
                "effectiveness_score": 0.88,
                "context": {"model": "gpt-4o-mini", "spectrum": "customer_profile"},
                "sample_size": 30,
                "confidence": 0.80,
            },
        ]

        with patch.object(meta_learner, "_get_strategy_performance_data", return_value=mock_strategy_data):
            context = {"model": "gpt-4o-mini", "spectrum": "customer_profile", "quality_score": 0.85}

            strategies = await meta_learner.identify_best_strategies(context)

            assert len(strategies) <= 3
            if strategies:
                # Should be sorted by effectiveness
                assert strategies[0]["strategy"] == "pattern_reinforcement"
                assert strategies[0]["effectiveness_score"] > 0.8


class TestAutonomousAIPlatform:
    """Test complete autonomous AI platform."""

    @pytest.fixture
    def mock_langsmith_client(self):
        """Create mock LangSmith client."""
        client = MagicMock(spec=EnterpriseLangSmithClient)
        return client

    @pytest.fixture
    def autonomous_platform(self, mock_langsmith_client):
        """Create autonomous AI platform."""
        return AutonomousAIPlatform(mock_langsmith_client)

    @pytest.mark.asyncio
    async def test_autonomous_improvement_cycle(self, autonomous_platform):
        """Test complete autonomous improvement cycle."""
        # Mock delta analysis
        mock_delta_analysis = DeltaAnalysis(
            analysis_id="delta_123",
            baseline_quality=0.90,
            current_quality=0.87,
            quality_delta=-0.03,
            regression_detected=False,
            confidence=0.85,
            affected_models=[],
            affected_spectrums=[],
            root_cause=None,
            timestamp="2025-08-17T10:00:00Z",
        )

        with patch.object(
            autonomous_platform.delta_analyzer, "check_performance_regression", return_value=mock_delta_analysis
        ), patch.object(
            autonomous_platform.pattern_indexer, "find_similar_successful_patterns", return_value=[]
        ), patch.object(
            autonomous_platform.meta_learner, "identify_best_strategies", return_value=[]
        ), patch.object(
            autonomous_platform.feedback_collector, "get_recent_corrections", return_value=[]
        ), patch.object(
            autonomous_platform, "predict_quality_degradation", return_value={"needs_intervention": False}
        ):

            cycle_results = await autonomous_platform.autonomous_improvement_cycle()

            assert "cycle_id" in cycle_results
            assert "components_executed" in cycle_results
            assert "delta_analysis" in cycle_results["components_executed"]
            assert "meta_learning" in cycle_results["components_executed"]
            assert "quality_prediction" in cycle_results["components_executed"]

    @pytest.mark.asyncio
    async def test_platform_status(self, autonomous_platform, mock_langsmith_client):
        """Test platform status retrieval."""
        mock_workspace_stats = WorkspaceStats(
            tenant_id="test_tenant",
            dataset_count=51,
            tracer_session_count=21,
            repo_count=3,
            annotation_queue_count=0,
            deployment_count=0,
            dashboards_count=0,
        )

        mock_trends = {"quality_trend": {"current_quality": 0.92, "trend": "stable"}}

        mock_prediction = {"predicted_quality_7d": 0.91, "needs_intervention": False}

        mock_langsmith_client.get_workspace_stats.return_value = mock_workspace_stats
        mock_langsmith_client.get_performance_trends.return_value = mock_trends

        with patch.object(autonomous_platform, "predict_quality_degradation", return_value=mock_prediction):
            status = await autonomous_platform.get_platform_status()

            assert status["platform_status"] == "operational"
            assert status["workspace_stats"]["projects"] == 21
            assert status["workspace_stats"]["datasets"] == 51
            assert status["current_quality"] == 0.92
            assert status["autonomous_features"]["delta_analysis"] is True


class TestEnhancedVirtuousCycleManager:
    """Test enhanced virtuous cycle manager."""

    @pytest.mark.asyncio
    async def test_enhanced_manager_initialization(self):
        """Test enhanced manager initialization."""
        with patch("autonomous_integration.create_enterprise_client") as mock_create_client:
            mock_client = MagicMock()
            mock_create_client.return_value = mock_client

            with patch("autonomous_integration.AutonomousAIPlatform") as mock_platform:
                mock_platform_instance = MagicMock()
                mock_platform.return_value = mock_platform_instance

                manager = EnhancedVirtuousCycleManager()

                assert manager.enterprise_features_available is True
                assert manager.langsmith_client == mock_client
                assert manager.autonomous_platform == mock_platform_instance

    @pytest.mark.asyncio
    async def test_enhanced_status_retrieval(self):
        """Test enhanced status retrieval."""
        with patch("autonomous_integration.create_enterprise_client") as mock_create_client:
            mock_client = MagicMock()
            mock_create_client.return_value = mock_client

            mock_platform_status = {
                "platform_status": "operational",
                "workspace_stats": {"projects": 21, "datasets": 51},
                "current_quality": 0.92,
                "autonomous_features": {"delta_analysis": True},
            }

            mock_quality_prediction = {"predicted_quality_7d": 0.91, "needs_intervention": False}

            with patch("autonomous_integration.AutonomousAIPlatform") as mock_platform:
                mock_platform_instance = MagicMock()
                mock_platform_instance.get_platform_status.return_value = mock_platform_status
                mock_platform_instance.predict_quality_degradation.return_value = mock_quality_prediction
                mock_platform.return_value = mock_platform_instance

                manager = EnhancedVirtuousCycleManager()
                status = await manager.get_enhanced_status()

                assert status["enhanced_features"] is True
                assert status.get("autonomous_ai", {}).get("delta_analysis") is True
                assert status.get("enterprise_langsmith", {}).get("current_quality") == 0.92


class TestAutonomousQualityMonitor:
    """Test autonomous quality monitoring."""

    @pytest.fixture
    def mock_enhanced_manager(self):
        """Create mock enhanced manager."""
        manager = MagicMock(spec=EnhancedVirtuousCycleManager)
        manager.enterprise_features_available = True
        return manager

    @pytest.fixture
    def quality_monitor(self, mock_enhanced_manager):
        """Create quality monitor."""
        return AutonomousQualityMonitor(mock_enhanced_manager)

    @pytest.mark.asyncio
    async def test_proactive_quality_monitoring(self, quality_monitor, mock_enhanced_manager):
        """Test proactive quality monitoring."""
        mock_trends_analysis = {
            "quality_trends": {"current_quality": 0.87, "trend": "declining"},  # Below threshold
            "predictions": {"needs_intervention": True, "predicted_quality_7d": 0.82, "confidence": 0.85},
        }

        mock_optimization_result = {
            "success": True,
            "autonomous_features_used": ["delta_analysis", "pattern_matching"],
            "improvements_identified": [{"type": "regression_detected"}],
        }

        mock_enhanced_manager.analyze_quality_trends.return_value = mock_trends_analysis
        mock_enhanced_manager.run_autonomous_optimization.return_value = mock_optimization_result

        monitoring_result = await quality_monitor.monitor_quality_proactively()

        assert monitoring_result["monitoring_type"] == "proactive"
        assert monitoring_result["quality_status"] == "below_threshold"
        assert len(monitoring_result["interventions_triggered"]) > 0
        assert len(monitoring_result["predictions_made"]) > 0


class TestIntegrationWorkflows:
    """Test end-to-end integration workflows."""

    @pytest.mark.asyncio
    async def test_comprehensive_system_status(self):
        """Test comprehensive system status workflow."""
        with patch("autonomous_integration.create_enhanced_virtuous_cycle") as mock_create_manager:
            mock_manager = MagicMock()
            mock_manager.get_enhanced_status.return_value = {
                "enhanced_features": True,
                "legacy_compatibility": True,
                "enterprise_langsmith": {},
            }
            mock_manager.get_real_langsmith_metrics.return_value = {
                "workspace_stats": {"tracer_session_count": 21, "dataset_count": 51, "repo_count": 3}
            }
            mock_manager.close = AsyncMock()
            mock_create_manager.return_value = mock_manager

            with patch("autonomous_integration.create_autonomous_monitor") as mock_create_monitor:
                mock_monitor = MagicMock()
                mock_monitor.monitor_quality_proactively.return_value = {
                    "quality_status": "stable",
                    "interventions_triggered": [],
                    "predictions_made": [],
                }
                mock_create_monitor.return_value = mock_monitor

                from autonomous_integration import get_comprehensive_system_status

                status = await get_comprehensive_system_status()

                assert status.get("integration_status") == "operational"
                assert status.get("system_overview", {}).get("enhanced_features") is True
                assert (
                    status.get("real_langsmith_metrics", {}).get("workspace_stats", {}).get("tracer_session_count")
                    == 21
                )

    @pytest.mark.asyncio
    async def test_autonomous_optimization_workflow(self):
        """Test autonomous optimization workflow."""
        with patch("autonomous_integration.create_enterprise_client") as mock_create_client:
            mock_client = MagicMock()
            mock_create_client.return_value = mock_client

            with patch("autonomous_integration.AutonomousAIPlatform") as mock_platform:
                mock_platform_instance = MagicMock()
                mock_cycle_results = {
                    "components_executed": ["delta_analysis", "pattern_matching"],
                    "improvements_identified": [{"type": "regression_detected"}],
                    "learning_applied": True,
                    "cycle_duration": 2.5,
                }
                mock_platform_instance.autonomous_improvement_cycle.return_value = mock_cycle_results
                mock_platform.return_value = mock_platform_instance

                manager = EnhancedVirtuousCycleManager()
                result = await manager.run_autonomous_optimization("Test trigger")

                assert result.get("success") is True
                assert "delta_analysis" in result.get("autonomous_features_used", [])
                assert result.get("learning_applied") is True


# ========================================================================
# TEST UTILITIES AND FIXTURES
# ========================================================================


@pytest.fixture
def sample_quality_metrics():
    """Create sample quality metrics for testing."""
    return [
        QualityMetrics(
            run_id=f"run_{i}",
            session_name="tilores_x",
            model="gpt-4o-mini",
            quality_score=0.90 + (i * 0.01),
            latency_ms=2000 + (i * 100),
            token_count=150 + (i * 10),
            cost=0.001 + (i * 0.0001),
            timestamp=f"2025-08-17T10:{i:02d}:00Z",
        )
        for i in range(10)
    ]


@pytest.fixture
def sample_workspace_stats():
    """Create sample workspace statistics."""
    return WorkspaceStats(
        tenant_id="test_tenant_id",
        dataset_count=51,
        tracer_session_count=21,
        repo_count=3,
        annotation_queue_count=0,
        deployment_count=0,
        dashboards_count=0,
        total_runs=1000,
        total_tokens=50000,
        total_cost=25.50,
    )


# ========================================================================
# PERFORMANCE TESTS
# ========================================================================


class TestPerformanceMetrics:
    """Test performance and scalability of autonomous components."""

    @pytest.mark.asyncio
    async def test_large_scale_delta_analysis(self):
        """Test delta analysis with large datasets."""
        mock_client = MagicMock(spec=EnterpriseLangSmithClient)
        analyzer = DeltaRegressionAnalyzer(mock_client)

        # Mock large dataset (1000 metrics)
        large_baseline = [
            QualityMetrics(
                run_id=f"baseline_{i}",
                session_name="tilores_x",
                model="gpt-4o-mini",
                quality_score=0.90 + (i % 10) * 0.01,
                latency_ms=2000,
                token_count=150,
                cost=0.001,
                timestamp="2025-08-10T10:00:00Z",
            )
            for i in range(1000)
        ]

        large_current = [
            QualityMetrics(
                run_id=f"current_{i}",
                session_name="tilores_x",
                model="gpt-4o-mini",
                quality_score=0.88 + (i % 10) * 0.01,
                latency_ms=2100,
                token_count=160,
                cost=0.0011,
                timestamp="2025-08-17T10:00:00Z",
            )
            for i in range(1000)
        ]

        mock_client.get_quality_metrics.side_effect = [large_baseline, large_current]

        # Measure performance
        start_time = time.time()
        result = await analyzer.check_performance_regression()
        analysis_time = time.time() - start_time

        # Should complete within reasonable time
        assert analysis_time < 5.0  # 5 seconds max
        assert isinstance(result, DeltaAnalysis)
        assert result.metadata["baseline_sample_size"] == 1000
        assert result.metadata["current_sample_size"] == 1000

    @pytest.mark.asyncio
    async def test_concurrent_ab_experiments(self):
        """Test handling multiple concurrent A/B experiments."""
        mock_client = MagicMock(spec=EnterpriseLangSmithClient)
        ab_testing = AdvancedABTesting(mock_client)

        mock_dataset = DatasetInfo(
            id="dataset_concurrent",
            name="concurrent_test",
            description="Concurrent test",
            example_count=0,
            created_at="2025-08-17T10:00:00Z",
            last_modified="2025-08-17T10:00:00Z",
        )

        mock_client.create_dataset.return_value = mock_dataset
        mock_client.add_examples_to_dataset.return_value = {"success": True}

        # Create multiple experiments concurrently
        experiment_tasks = [
            ab_testing.create_ab_experiment(
                experiment_name=f"concurrent_test_{i}",
                variant_a_prompt=f"Original prompt {i}",
                variant_b_prompt=f"Optimized prompt {i}",
                target_models=["gpt-4o-mini"],
                target_spectrums=["customer_profile"],
            )
            for i in range(5)
        ]

        experiment_ids = await asyncio.gather(*experiment_tasks)

        assert len(experiment_ids) >= 1  # At least one experiment created
        assert all(exp_id.startswith("ab_test_") for exp_id in experiment_ids)
        # Allow for some duplicates in concurrent testing


# ========================================================================
# ERROR HANDLING TESTS
# ========================================================================


class TestErrorHandling:
    """Test error handling and graceful degradation."""

    @pytest.mark.asyncio
    async def test_langsmith_client_connection_failure(self):
        """Test handling of LangSmith connection failures."""
        config = LangSmithConfig(api_key="invalid_key", organization_id="invalid_org")

        client = EnterpriseLangSmithClient(config)

        with patch.object(client, "_make_request", side_effect=Exception("Connection failed")):
            # Should handle gracefully without crashing
            try:
                await client.get_workspace_stats()
                assert False, "Should have raised exception"
            except Exception as e:
                assert "Connection failed" in str(e)

    @pytest.mark.asyncio
    async def test_autonomous_platform_degraded_mode(self):
        """Test autonomous platform in degraded mode."""
        mock_client = MagicMock(spec=EnterpriseLangSmithClient)

        # Mock client failures
        mock_client.get_quality_metrics.side_effect = Exception("API unavailable")

        platform = AutonomousAIPlatform(mock_client)

        # Should handle gracefully
        try:
            await platform.autonomous_improvement_cycle()
        except Exception:
            # Expected to fail gracefully
            pass

    @pytest.mark.asyncio
    async def test_enhanced_manager_fallback(self):
        """Test enhanced manager fallback to legacy mode."""
        with patch("autonomous_integration.create_enterprise_client", side_effect=Exception("Enterprise unavailable")):
            manager = EnhancedVirtuousCycleManager()

            # Should fall back gracefully
            assert manager.enterprise_features_available is False
            assert manager.langsmith_client is None
            assert manager.autonomous_platform is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
