#!/usr/bin/env python3
"""
Comprehensive test suite for Phase 4 Production Integration System.

Tests all components of the production deployment orchestrator including:
- Safe prompt deployment with rollback capabilities
- Real-world performance monitoring across 7 models and 7 data spectrums
- A/B testing infrastructure for production environment
- Automated quality assurance with 90%+ achievement validation
- Railway production environment integration
- Ongoing optimization pipeline with continuous monitoring

Author: Roo (Elite Software Engineer)
Created: 2025-08-16
Phase: 4 - Production Integration Testing
"""

import asyncio
import os
import sys
import tempfile
from datetime import timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Import Phase 4 components
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from phase4_production_integration import (
    ABTestConfiguration,
    DeploymentStatus,
    ProductionABTester,
    ProductionEnvironment,
    ProductionIntegrationOrchestrator,
    ProductionMetrics,
    ProductionPerformanceMonitor,
    ProductionPromptManager,
    PromptDeployment,
)


class TestProductionPromptManager:
    """Test suite for ProductionPromptManager."""

    @pytest.fixture
    def temp_core_app(self):
        """Create temporary core_app.py for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            # Write mock core_app.py content
            f.write(
                """#!/usr/bin/env python3
# Mock core_app.py for testing

def some_function():
    pass

        # FIXED: Simplified system prompt that forces tool usage
        system_prompt = f\"\"\"You are a customer service assistant.
{comprehensive_fields_text}

# CRITICAL: YOU MUST USE TOOLS FOR ALL CUSTOMER QUERIES

For ANY customer query containing:
- Email addresses (user@domain.com)
- Customer IDs (numbers like 1881899)

YOU MUST IMMEDIATELY call the tilores_search tool FIRST.

Available tools:
1. tilores_search - Find customers by email, name, or ID.

MANDATORY: Call tools first, then provide real data.\"\"\"

        # Rest of function
        return system_prompt
"""
            )
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def prompt_manager(self, temp_core_app):
        """Create ProductionPromptManager with temporary file."""
        return ProductionPromptManager(core_app_path=temp_core_app)

    def test_prompt_manager_initialization(self, prompt_manager):
        """Test prompt manager initialization."""
        assert prompt_manager.core_app_path.exists()
        assert prompt_manager.backup_dir.exists()
        assert "system_prompt" in prompt_manager.prompt_locations
        assert len(prompt_manager.deployment_history) == 0

    def test_create_backup(self, prompt_manager):
        """Test backup creation functionality."""
        deployment_id = "test_deployment_001"
        backup_path = prompt_manager.create_backup(deployment_id)

        assert Path(backup_path).exists()
        assert deployment_id in backup_path
        assert backup_path.endswith(".py")

        # Cleanup
        Path(backup_path).unlink(missing_ok=True)

    def test_extract_current_prompt(self, prompt_manager):
        """Test current prompt extraction."""
        current_prompt = prompt_manager.extract_current_prompt("system_prompt")

        assert 'system_prompt = f"""' in current_prompt
        assert "customer service assistant" in current_prompt
        assert "CRITICAL" in current_prompt

    def test_extract_invalid_location(self, prompt_manager):
        """Test extraction with invalid location."""
        with pytest.raises(ValueError, match="Unknown prompt location"):
            prompt_manager.extract_current_prompt("invalid_location")

    @pytest.mark.asyncio
    async def test_deploy_prompt_success(self, prompt_manager):
        """Test successful prompt deployment."""
        deployment = PromptDeployment(
            deployment_id="test_deploy_001",
            prompt_content="You are an optimized assistant.",
            target_location="system_prompt",
            deployment_status=DeploymentStatus.PENDING,
            validation_results={},
            performance_metrics={},
        )

        success = await prompt_manager.deploy_prompt(deployment)

        assert success
        assert deployment.deployment_status == DeploymentStatus.DEPLOYED
        assert deployment.deployment_time is not None
        assert len(prompt_manager.deployment_history) == 1

    @pytest.mark.asyncio
    async def test_rollback_deployment(self, prompt_manager):
        """Test deployment rollback functionality."""
        # First deploy something
        deployment = PromptDeployment(
            deployment_id="test_rollback_001",
            prompt_content="You are a test assistant.",
            target_location="system_prompt",
            deployment_status=DeploymentStatus.DEPLOYED,
            validation_results={},
            performance_metrics={},
            rollback_data={"backup_path": "fake_backup.py"},
        )

        # Mock the backup file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as backup_file:
            backup_file.write("# Original content")
            if deployment.rollback_data is None:
                deployment.rollback_data = {}
            deployment.rollback_data["backup_path"] = backup_file.name

        try:
            success = await prompt_manager.rollback_deployment(deployment)

            assert success
            assert deployment.deployment_status == DeploymentStatus.ROLLED_BACK
            assert deployment.rollback_time is not None
        finally:
            # Cleanup
            if deployment.rollback_data and "backup_path" in deployment.rollback_data:
                Path(deployment.rollback_data["backup_path"]).unlink(missing_ok=True)


class TestProductionPerformanceMonitor:
    """Test suite for ProductionPerformanceMonitor."""

    @pytest.fixture
    def performance_monitor(self):
        """Create ProductionPerformanceMonitor instance."""
        return ProductionPerformanceMonitor()

    def test_monitor_initialization(self, performance_monitor):
        """Test performance monitor initialization."""
        assert len(performance_monitor.models) == 7
        assert len(performance_monitor.spectrums) == 7
        assert not performance_monitor.monitoring_active
        assert len(performance_monitor.metrics_history) == 0

    @pytest.mark.asyncio
    async def test_collect_performance_metrics(self, performance_monitor):
        """Test performance metrics collection."""
        metrics = await performance_monitor.collect_performance_metrics()

        assert isinstance(metrics, ProductionMetrics)
        assert len(metrics.model_performance) == 7
        assert len(metrics.spectrum_performance) == 7
        assert 0.0 <= metrics.quality_achievement_rate <= 1.0
        assert isinstance(metrics.customer_satisfaction_score, float)

    @pytest.mark.asyncio
    async def test_model_metrics_collection(self, performance_monitor):
        """Test individual model metrics collection."""
        model_metrics = await performance_monitor._collect_model_metrics("llama-3.3-70b-versatile")

        assert "quality_score" in model_metrics
        assert "response_time" in model_metrics
        assert "success_rate" in model_metrics
        assert "error_rate" in model_metrics
        assert "throughput" in model_metrics

        # Validate ranges
        assert 0.0 <= model_metrics["quality_score"] <= 1.0
        assert model_metrics["response_time"] > 0
        assert 0.0 <= model_metrics["success_rate"] <= 1.0

    @pytest.mark.asyncio
    async def test_spectrum_metrics_collection(self, performance_monitor):
        """Test individual spectrum metrics collection."""
        spectrum_metrics = await performance_monitor._collect_spectrum_metrics("customer_profile")

        assert "completeness_score" in spectrum_metrics
        assert "accuracy_score" in spectrum_metrics
        assert "data_coverage" in spectrum_metrics
        assert "processing_time" in spectrum_metrics

        # Validate ranges
        assert 0.0 <= spectrum_metrics["completeness_score"] <= 1.0
        assert 0.0 <= spectrum_metrics["accuracy_score"] <= 1.0
        assert spectrum_metrics["processing_time"] > 0

    def test_quality_achievement_calculation(self, performance_monitor):
        """Test quality achievement rate calculation."""
        mock_metrics = ProductionMetrics()
        mock_metrics.model_performance = {
            "model1": {"quality_score": 0.95},
            "model2": {"quality_score": 0.88},
            "model3": {"quality_score": 0.92},
            "model4": {"quality_score": 0.85},
        }

        rate = performance_monitor._calculate_quality_achievement_rate(mock_metrics)
        assert rate == 0.75  # 3 out of 4 models above 90%

    def test_response_time_improvement_calculation(self, performance_monitor):
        """Test response time improvement calculation."""
        # Add previous metrics
        previous_metrics = ProductionMetrics()
        previous_metrics.model_performance = {"model1": {"response_time": 5.0}, "model2": {"response_time": 6.0}}
        performance_monitor.metrics_history.append(previous_metrics)

        # Current metrics with improvement
        current_metrics = ProductionMetrics()
        current_metrics.model_performance = {"model1": {"response_time": 4.0}, "model2": {"response_time": 5.0}}

        improvement = performance_monitor._calculate_response_time_improvement(current_metrics)
        assert improvement > 0  # Should show improvement


class TestProductionABTester:
    """Test suite for ProductionABTester."""

    @pytest.fixture
    def ab_tester(self):
        """Create ProductionABTester instance."""
        prompt_manager = MagicMock()
        performance_monitor = MagicMock()
        return ProductionABTester(prompt_manager, performance_monitor)

    def test_ab_tester_initialization(self, ab_tester):
        """Test A/B tester initialization."""
        assert ab_tester.prompt_manager is not None
        assert ab_tester.performance_monitor is not None
        assert len(ab_tester.active_tests) == 0
        assert len(ab_tester.test_results) == 0

    def test_validate_ab_config_valid(self, ab_tester):
        """Test A/B configuration validation with valid config."""
        config = ABTestConfiguration(
            test_id="test_001",
            control_prompt="Control prompt",
            variant_prompt="Variant prompt",
            traffic_split=0.1,
            target_models=["model1"],
            target_spectrums=["spectrum1"],
            success_criteria={"quality": 0.9},
            test_duration=timedelta(hours=2),
            minimum_sample_size=100,
        )

        assert ab_tester._validate_ab_config(config)

    def test_validate_ab_config_invalid_traffic_split(self, ab_tester):
        """Test A/B configuration validation with invalid traffic split."""
        config = ABTestConfiguration(
            test_id="test_002",
            control_prompt="Control prompt",
            variant_prompt="Variant prompt",
            traffic_split=1.5,  # Invalid
            target_models=["model1"],
            target_spectrums=["spectrum1"],
            success_criteria={"quality": 0.9},
            test_duration=timedelta(hours=2),
            minimum_sample_size=100,
        )

        assert not ab_tester._validate_ab_config(config)

    def test_validate_ab_config_short_duration(self, ab_tester):
        """Test A/B configuration validation with short duration."""
        config = ABTestConfiguration(
            test_id="test_003",
            control_prompt="Control prompt",
            variant_prompt="Variant prompt",
            traffic_split=0.1,
            target_models=["model1"],
            target_spectrums=["spectrum1"],
            success_criteria={"quality": 0.9},
            test_duration=timedelta(minutes=30),  # Too short
            minimum_sample_size=100,
        )

        assert not ab_tester._validate_ab_config(config)

    @pytest.mark.asyncio
    async def test_start_ab_test_success(self, ab_tester):
        """Test successful A/B test startup."""
        config = ABTestConfiguration(
            test_id="test_004",
            control_prompt="Control prompt",
            variant_prompt="Variant prompt",
            traffic_split=0.1,
            target_models=["model1"],
            target_spectrums=["spectrum1"],
            success_criteria={"quality": 0.9},
            test_duration=timedelta(hours=2),
            minimum_sample_size=100,
        )

        # Mock successful deployment
        ab_tester._deploy_with_traffic_split = AsyncMock(return_value=True)
        ab_tester._monitor_ab_test = AsyncMock()

        success = await ab_tester.start_ab_test(config)

        assert success
        assert config.test_id in ab_tester.active_tests

    @pytest.mark.asyncio
    async def test_collect_ab_test_metrics(self, ab_tester):
        """Test A/B test metrics collection."""
        config = ABTestConfiguration(
            test_id="test_005",
            control_prompt="Control prompt",
            variant_prompt="Variant prompt",
            traffic_split=0.2,
            target_models=["model1"],
            target_spectrums=["spectrum1"],
            success_criteria={"quality": 0.9},
            test_duration=timedelta(hours=2),
            minimum_sample_size=100,
        )

        await ab_tester._collect_ab_test_metrics(config)

        assert config.test_id in ab_tester.test_results
        results = ab_tester.test_results[config.test_id]
        assert "control_metrics" in results
        assert "variant_metrics" in results
        assert "sample_sizes" in results


class TestProductionIntegrationOrchestrator:
    """Test suite for ProductionIntegrationOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create ProductionIntegrationOrchestrator instance."""
        return ProductionIntegrationOrchestrator(ProductionEnvironment.LOCAL)

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert orchestrator.environment == ProductionEnvironment.LOCAL
        assert orchestrator.prompt_manager is not None
        assert orchestrator.performance_monitor is not None
        assert orchestrator.ab_tester is not None

    def test_extract_best_prompt_with_results(self, orchestrator):
        """Test extracting best prompt from optimization results."""
        optimization_results = {
            "ab_test_results": {
                "customer_profile": {
                    "summary": {"best_variation": "optimized_v1", "best_score": 0.92, "average_improvement": 0.05}
                }
            }
        }

        best_prompt = orchestrator._extract_best_prompt(optimization_results)

        assert best_prompt is not None
        assert "customer service assistant" in best_prompt
        assert "CRITICAL" in best_prompt
        assert "0.92" in best_prompt  # Should include the score

    def test_extract_best_prompt_fallback(self, orchestrator):
        """Test extracting best prompt with fallback."""
        optimization_results = {}  # Empty results

        best_prompt = orchestrator._extract_best_prompt(optimization_results)

        assert best_prompt is not None
        assert "customer service assistant" in best_prompt
        assert "90%+ QUALITY" in best_prompt

    def test_validate_prompt_syntax_valid(self, orchestrator):
        """Test prompt syntax validation with valid prompt."""
        valid_prompt = """You are a customer service assistant with access to tools.

# CRITICAL: YOU MUST USE TOOLS FOR ALL CUSTOMER QUERIES

For ANY customer query containing email addresses, you must call tools.

Available tools:
1. tilores_search - Find customers

MANDATORY: Call tools first, then provide real data."""

        assert orchestrator._validate_prompt_syntax(valid_prompt)

    def test_validate_prompt_syntax_invalid_short(self, orchestrator):
        """Test prompt syntax validation with too short prompt."""
        short_prompt = "You are an assistant."

        assert not orchestrator._validate_prompt_syntax(short_prompt)

    def test_validate_prompt_syntax_missing_components(self, orchestrator):
        """Test prompt syntax validation with missing components."""
        incomplete_prompt = """You are an assistant.
This prompt is missing critical components."""

        assert not orchestrator._validate_prompt_syntax(incomplete_prompt)

    def test_validate_prompt_content_valid(self, orchestrator):
        """Test prompt content validation with valid content."""
        valid_prompt = """You are a customer service assistant.

Tools available:
- tilores_search
- tilores_entity_edges
- tilores_record_lookup
- get_customer_credit_report

Handle email addresses, customer IDs, names, and record IDs."""

        assert orchestrator._validate_prompt_content(valid_prompt)

    def test_validate_prompt_content_missing_tools(self, orchestrator):
        """Test prompt content validation with missing tools."""
        incomplete_prompt = """You are a customer service assistant.

Tools available:
- tilores_search
- tilores_entity_edges

Handle customer queries."""

        assert not orchestrator._validate_prompt_content(incomplete_prompt)

    @pytest.mark.asyncio
    async def test_validate_integration_success(self, orchestrator):
        """Test integration validation success."""
        deployment = PromptDeployment(
            deployment_id="test_integration_001",
            prompt_content="You are an assistant. {comprehensive_fields_text}",
            target_location="system_prompt",
            deployment_status=DeploymentStatus.VALIDATING,
            validation_results={},
            performance_metrics={},
        )

        # Mock extract_current_prompt to return valid content
        orchestrator.prompt_manager.extract_current_prompt = MagicMock(
            return_value='system_prompt = f"""existing prompt"""'
        )

        result = await orchestrator._validate_integration(deployment)
        assert result

    @pytest.mark.asyncio
    async def test_validate_with_customer_data(self, orchestrator):
        """Test validation with Edwina Hawthorne customer data."""
        deployment = PromptDeployment(
            deployment_id="test_customer_001",
            prompt_content="""You are a comprehensive customer service assistant.
Provide accurate, professional responses with mandatory tool usage.""",
            target_location="system_prompt",
            deployment_status=DeploymentStatus.VALIDATING,
            validation_results={},
            performance_metrics={},
        )

        result = await orchestrator._validate_with_customer_data(deployment)
        assert result  # Should pass with comprehensive prompt

    @pytest.mark.asyncio
    async def test_test_prompt_effectiveness(self, orchestrator):
        """Test prompt effectiveness testing."""
        high_quality_prompt = """You are a comprehensive, professional,
accurate assistant with mandatory tool usage requirements."""

        score = await orchestrator._test_prompt_effectiveness(high_quality_prompt, "test query")

        assert 0.8 <= score <= 1.0  # Should score high

    @pytest.mark.asyncio
    async def test_deploy_optimized_prompts_success(self, orchestrator):
        """Test successful deployment of optimized prompts."""
        optimization_results = {
            "ab_test_results": {"customer_profile": {"summary": {"best_variation": "optimized_v1", "best_score": 0.93}}}
        }

        # Mock validation and deployment
        orchestrator._validate_deployment = AsyncMock(return_value=True)
        orchestrator.prompt_manager.deploy_prompt = AsyncMock(return_value=True)
        orchestrator._monitor_deployment = AsyncMock()

        success = await orchestrator.deploy_optimized_prompts(optimization_results)
        assert success

    @pytest.mark.asyncio
    async def test_deploy_optimized_prompts_validation_failure(self, orchestrator):
        """Test deployment failure due to validation."""
        optimization_results = {
            "ab_test_results": {"customer_profile": {"summary": {"best_variation": "optimized_v1", "best_score": 0.93}}}
        }

        # Mock validation failure
        orchestrator._validate_deployment = AsyncMock(return_value=False)

        success = await orchestrator.deploy_optimized_prompts(optimization_results)
        assert not success

    @pytest.mark.asyncio
    async def test_run_production_ab_test(self, orchestrator):
        """Test production A/B test execution."""
        control_prompt = "You are a helpful assistant."
        variant_prompt = "You are an expert customer service assistant."

        # Mock A/B test startup
        orchestrator.ab_tester.start_ab_test = AsyncMock(return_value=True)

        result = await orchestrator.run_production_ab_test(control_prompt, variant_prompt, traffic_split=0.1)

        assert result["status"] == "started"
        assert "test_id" in result

    def test_should_trigger_optimization_quality_low(self, orchestrator):
        """Test optimization trigger with low quality."""
        # Add mock metrics with low quality
        mock_metrics = ProductionMetrics()
        mock_metrics.quality_achievement_rate = 0.80  # Below 85% threshold
        orchestrator.performance_monitor.metrics_history = [mock_metrics]

        # Use asyncio.run for async method
        should_trigger = asyncio.run(orchestrator._should_trigger_optimization())
        assert should_trigger

    def test_should_trigger_optimization_models_failing(self, orchestrator):
        """Test optimization trigger with multiple failing models."""
        mock_metrics = ProductionMetrics()
        mock_metrics.quality_achievement_rate = 0.90  # Good overall
        mock_metrics.model_performance = {
            "model1": {"quality_score": 0.80},  # Below threshold
            "model2": {"quality_score": 0.82},  # Below threshold
            "model3": {"quality_score": 0.83},  # Below threshold
            "model4": {"quality_score": 0.95},  # Good
        }
        orchestrator.performance_monitor.metrics_history = [mock_metrics]

        should_trigger = asyncio.run(orchestrator._should_trigger_optimization())
        assert should_trigger

    @pytest.mark.asyncio
    async def test_validate_railway_integration(self, orchestrator):
        """Test Railway integration validation."""
        # Mock environment variables
        with patch.dict(
            os.environ,
            {
                "TILORES_API_URL": "https://api.tilores.com",
                "TILORES_CLIENT_ID": "test_client",
                "TILORES_CLIENT_SECRET": "test_secret",
                "LANGSMITH_API_KEY": "test_key",
                "LANGSMITH_PROJECT": "test_project",
            },
        ):
            validation_results = await orchestrator.validate_railway_integration()

            assert validation_results["environment_variables"]
            assert "overall_status" in validation_results

    @pytest.mark.asyncio
    async def test_check_deployment_health_healthy(self, orchestrator):
        """Test deployment health check with healthy metrics."""
        deployment = PromptDeployment(
            deployment_id="test_health_001",
            prompt_content="Test prompt",
            target_location="system_prompt",
            deployment_status=DeploymentStatus.MONITORING,
            validation_results={},
            performance_metrics={},
        )

        healthy_metrics = ProductionMetrics()
        healthy_metrics.quality_achievement_rate = 0.95
        healthy_metrics.model_performance = {
            "model1": {"quality_score": 0.92},
            "model2": {"quality_score": 0.88},
            "model3": {"quality_score": 0.94},
        }

        is_healthy = await orchestrator._check_deployment_health(deployment, healthy_metrics)
        assert is_healthy

    @pytest.mark.asyncio
    async def test_check_deployment_health_unhealthy(self, orchestrator):
        """Test deployment health check with unhealthy metrics."""
        deployment = PromptDeployment(
            deployment_id="test_health_002",
            prompt_content="Test prompt",
            target_location="system_prompt",
            deployment_status=DeploymentStatus.MONITORING,
            validation_results={},
            performance_metrics={},
        )

        unhealthy_metrics = ProductionMetrics()
        unhealthy_metrics.quality_achievement_rate = 0.70  # Below threshold
        unhealthy_metrics.model_performance = {
            "model1": {"quality_score": 0.70},  # Critical
            "model2": {"quality_score": 0.72},  # Critical
            "model3": {"quality_score": 0.74},  # Critical
            "model4": {"quality_score": 0.95},  # Good
        }

        is_healthy = await orchestrator._check_deployment_health(deployment, unhealthy_metrics)
        assert not is_healthy


class TestIntegrationScenarios:
    """Integration test scenarios for Phase 4."""

    @pytest.fixture
    def full_orchestrator(self):
        """Create fully configured orchestrator for integration tests."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
        system_prompt = f\"\"\"You are a customer service assistant.
{comprehensive_fields_text}

# CRITICAL: YOU MUST USE TOOLS

MANDATORY: Call tools first.\"\"\"
"""
            )
            temp_path = f.name

        orchestrator = ProductionIntegrationOrchestrator(ProductionEnvironment.LOCAL)
        orchestrator.prompt_manager.core_app_path = Path(temp_path)

        yield orchestrator

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_end_to_end_deployment_workflow(self, full_orchestrator):
        """Test complete end-to-end deployment workflow."""
        # Mock optimization results
        optimization_results = {
            "ab_test_results": {
                "customer_profile": {
                    "summary": {"best_variation": "optimized_v1", "best_score": 0.94, "average_improvement": 0.06}
                }
            },
            "overall_improvement": 0.05,
        }

        # Mock monitoring
        full_orchestrator._monitor_deployment = AsyncMock()

        # Execute deployment
        success = await full_orchestrator.deploy_optimized_prompts(optimization_results)

        assert success
        assert len(full_orchestrator.prompt_manager.deployment_history) == 1

        deployment = full_orchestrator.prompt_manager.deployment_history[0]
        assert deployment.deployment_status == DeploymentStatus.DEPLOYED

    @pytest.mark.asyncio
    async def test_deployment_with_rollback(self, full_orchestrator):
        """Test deployment followed by rollback."""
        # Create a deployment
        deployment = PromptDeployment(
            deployment_id="test_rollback_workflow",
            prompt_content="You are an optimized assistant.",
            target_location="system_prompt",
            deployment_status=DeploymentStatus.DEPLOYED,
            validation_results={},
            performance_metrics={},
        )

        # Deploy first
        success = await full_orchestrator.prompt_manager.deploy_prompt(deployment)
        assert success

        # Then rollback
        rollback_success = await full_orchestrator.prompt_manager.rollback_deployment(deployment)
        assert rollback_success
        assert deployment.deployment_status == DeploymentStatus.ROLLED_BACK

    @pytest.mark.asyncio
    async def test_performance_monitoring_cycle(self, full_orchestrator):
        """Test performance monitoring cycle."""
        # Collect metrics
        metrics = await full_orchestrator.performance_monitor.collect_performance_metrics()

        assert isinstance(metrics, ProductionMetrics)
        assert len(metrics.model_performance) == 7
        assert len(metrics.spectrum_performance) == 7

        # Validate metric ranges
        for model_metrics in metrics.model_performance.values():
            assert 0.0 <= model_metrics["quality_score"] <= 1.0
            assert model_metrics["response_time"] > 0

        for spectrum_metrics in metrics.spectrum_performance.values():
            assert 0.0 <= spectrum_metrics["completeness_score"] <= 1.0
            assert spectrum_metrics["processing_time"] > 0

    @pytest.mark.asyncio
    async def test_quality_assurance_validation(self, full_orchestrator):
        """Test 90%+ quality achievement validation."""
        # Test with high-quality prompt
        high_quality_deployment = PromptDeployment(
            deployment_id="test_qa_001",
            prompt_content="""You are a comprehensive, professional, accurate
customer service assistant with mandatory tool usage for all customer queries.

# CRITICAL: YOU MUST USE TOOLS FOR ALL CUSTOMER QUERIES

For ANY customer query containing:
- Email addresses (user@domain.com)
- Customer IDs (numbers like 1881899)
- Names (John Smith)
- Record IDs (ID003Ux...)

YOU MUST IMMEDIATELY call the tilores_search tool FIRST.

Available tools:
1. tilores_search - Find customers by email, name, or ID
2. tilores_entity_edges - Get detailed relationship data
3. tilores_record_lookup - Direct lookup by Salesforce record ID
4. get_customer_credit_report - Get comprehensive credit analysis

MANDATORY: Call tools first, then provide real data. Never guess.""",
            target_location="system_prompt",
            deployment_status=DeploymentStatus.VALIDATING,
            validation_results={},
            performance_metrics={},
        )

        # Mock current prompt extraction
        full_orchestrator.prompt_manager.extract_current_prompt = MagicMock(
            return_value='system_prompt = f"""existing"""'
        )

        validation_passed = await full_orchestrator._validate_deployment(high_quality_deployment)
        assert validation_passed

        # Check validation results
        assert "syntax" in high_quality_deployment.validation_results
        assert "content" in high_quality_deployment.validation_results
        assert "integration" in high_quality_deployment.validation_results
        assert "quality" in high_quality_deployment.validation_results


class TestEdwinaHawthorneValidation:
    """Test validation with Edwina Hawthorne customer data."""

    @pytest.fixture
    def orchestrator_with_customer_data(self):
        """Create orchestrator configured for customer data validation."""
        return ProductionIntegrationOrchestrator(ProductionEnvironment.LOCAL)

    @pytest.mark.asyncio
    async def test_customer_data_validation_queries(self, orchestrator_with_customer_data):
        """Test validation with Edwina Hawthorne customer data queries."""
        test_queries = [
            "edwina.hawthorne@example.com",
            "Find customer Edwina Hawthorne",
            "Get credit report for customer EDW_HAWTHORNE_001",
            "What is Edwina's credit utilization rate?",
            "Has Edwina Hawthorne missed any recent payments?",
        ]

        for query in test_queries:
            # Test prompt effectiveness with customer data
            score = await orchestrator_with_customer_data._test_prompt_effectiveness(
                """You are a comprehensive customer service assistant with
mandatory tool usage for accurate customer data analysis.""",
                query,
            )

            # Should achieve high scores for customer-focused prompts
            assert score >= 0.80, f"Query '{query}' scored too low: {score}"

        # Test overall validation
        deployment = PromptDeployment(
            deployment_id="test_edwina_validation",
            prompt_content="""You are a comprehensive, professional, accurate
customer service assistant with mandatory tool usage for all customer queries.

# CRITICAL: YOU MUST USE TOOLS FOR ALL CUSTOMER QUERIES

For customer queries about Edwina Hawthorne or any customer:
- Use tilores_search for profile information
- Use get_customer_credit_report for financial analysis
- Provide accurate, data-driven responses

Available tools:
1. tilores_search - Find customers by email, name, or ID
2. get_customer_credit_report - Get comprehensive credit analysis

MANDATORY: Call tools first, then provide real data.""",
            target_location="system_prompt",
            deployment_status=DeploymentStatus.VALIDATING,
            validation_results={},
            performance_metrics={},
        )

        # Mock integration validation
        orchestrator_with_customer_data.prompt_manager.extract_current_prompt = MagicMock(
            return_value='system_prompt = f"""existing"""'
        )

        validation_passed = await orchestrator_with_customer_data._validate_with_customer_data(deployment)
        assert validation_passed


# Performance test scenarios
class TestPerformanceScenarios:
    """Performance test scenarios for Phase 4."""

    @pytest.mark.asyncio
    async def test_high_volume_deployment_monitoring(self):
        """Test monitoring under high volume deployment scenarios."""
        orchestrator = ProductionIntegrationOrchestrator(ProductionEnvironment.LOCAL)

        # Simulate high volume metrics
        for _ in range(10):
            metrics = await orchestrator.performance_monitor.collect_performance_metrics()
            orchestrator.performance_monitor.metrics_history.append(metrics)

        # Verify metrics collection scales
        assert len(orchestrator.performance_monitor.metrics_history) == 10

        # Test optimization trigger logic
        should_optimize = await orchestrator._should_trigger_optimization()
        assert isinstance(should_optimize, bool)

    @pytest.mark.asyncio
    async def test_concurrent_ab_tests(self):
        """Test handling multiple concurrent A/B tests."""
        orchestrator = ProductionIntegrationOrchestrator(ProductionEnvironment.LOCAL)

        # Mock successful A/B test startup
        orchestrator.ab_tester.start_ab_test = AsyncMock(return_value=True)

        # Start multiple A/B tests
        test_results = []
        for i in range(3):
            result = await orchestrator.run_production_ab_test(
                f"Control prompt {i}", f"Variant prompt {i}", traffic_split=0.1
            )
            test_results.append(result)

        # Verify all tests started
        assert all(result["status"] == "started" for result in test_results)
        assert len(set(result["test_id"] for result in test_results)) == 3

    @pytest.mark.asyncio
    async def test_rollback_under_pressure(self):
        """Test rollback capabilities under system pressure."""
        orchestrator = ProductionIntegrationOrchestrator(ProductionEnvironment.LOCAL)

        # Create deployment with simulated system pressure
        deployment = PromptDeployment(
            deployment_id="pressure_test_001",
            prompt_content="Test prompt under pressure",
            target_location="system_prompt",
            deployment_status=DeploymentStatus.DEPLOYED,
            validation_results={},
            performance_metrics={},
            rollback_data={"backup_path": "/tmp/fake_backup.py"},
        )

        # Mock file operations for pressure test
        with patch("shutil.copy2") as mock_copy:
            mock_copy.return_value = True

            success = await orchestrator.prompt_manager.rollback_deployment(deployment)
            assert success
            assert deployment.deployment_status == DeploymentStatus.ROLLED_BACK


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
