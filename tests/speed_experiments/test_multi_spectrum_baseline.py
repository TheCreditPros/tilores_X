#!/usr/bin/env python3
"""
Test suite for Multi-Spectrum Baseline Framework.

This module provides comprehensive testing for the Phase 1 Multi-Spectrum
Foundation implementation, validating all 7 data spectrums, 7 models,
and real customer data integration.

Author: Roo (Elite Software Engineer)
Created: 2025-08-16
Phase: 1 - Multi-Spectrum Foundation Testing
"""

import logging
import pytest
from datetime import datetime

from multi_spectrum_baseline_framework import (
    DataSpectrum,
    ModelProvider,
    MultiSpectrumBaselineFramework,
    EdwinaHawthorneDataProvider,
    ExperimentResult
)


class TestEdwinaHawthorneDataProvider:
    """Test suite for real customer data provider."""

    def setup_method(self):
        """Set up test fixtures."""
        self.data_provider = EdwinaHawthorneDataProvider()

    def test_data_provider_initialization(self):
        """Test data provider initializes correctly."""
        assert self.data_provider.customer_data is not None
        assert self.data_provider.field_mappings is not None
        assert len(self.data_provider.field_mappings) == 7

    def test_customer_profile_spectrum_data(self):
        """Test Customer Profile spectrum data extraction."""
        data = self.data_provider.get_spectrum_data(
            DataSpectrum.CUSTOMER_PROFILE
        )

        # Validate required fields
        assert "customer_id" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "email" in data
        assert data["customer_id"] == "EDW_HAWTHORNE_001"
        assert data["first_name"] == "Edwina"
        assert data["last_name"] == "Hawthorne"

        # Validate field count (should have 12+ fields)
        assert len(data) >= 12

    def test_credit_analysis_spectrum_data(self):
        """Test Credit Analysis spectrum data extraction."""
        data = self.data_provider.get_spectrum_data(
            DataSpectrum.CREDIT_ANALYSIS
        )

        # Validate required fields
        assert "credit_score" in data
        assert "credit_rating" in data
        assert data["credit_score"] == 742
        assert data["credit_rating"] == "GOOD"

        # Validate field count (should have 10+ fields)
        assert len(data) >= 10

    def test_transaction_history_spectrum_data(self):
        """Test Transaction History spectrum data extraction."""
        data = self.data_provider.get_spectrum_data(
            DataSpectrum.TRANSACTION_HISTORY
        )

        # Validate required fields
        assert "total_transactions" in data
        assert "last_transaction_date" in data
        assert data["total_transactions"] == 1247
        assert data["last_transaction_date"] == "2025-08-15"

        # Validate field count (should have 7+ fields)
        assert len(data) >= 7

    def test_call_center_operations_spectrum_data(self):
        """Test Call Center Operations spectrum data extraction."""
        data = self.data_provider.get_spectrum_data(
            DataSpectrum.CALL_CENTER_OPERATIONS
        )

        # Validate required fields
        assert "total_support_calls" in data
        assert "satisfaction_score" in data
        assert data["total_support_calls"] == 12
        assert data["satisfaction_score"] == 4.2

        # Validate field count (should have 7+ fields)
        assert len(data) >= 7

    def test_entity_relationship_spectrum_data(self):
        """Test Entity Relationship spectrum data extraction."""
        data = self.data_provider.get_spectrum_data(
            DataSpectrum.ENTITY_RELATIONSHIP
        )

        # Validate required fields
        assert "household_members" in data
        assert "relationship_strength" in data
        assert data["household_members"] == 3
        assert data["relationship_strength"] == "HIGH"

        # Validate field count (should have 6+ fields)
        assert len(data) >= 6

    def test_geographic_analysis_spectrum_data(self):
        """Test Geographic Analysis spectrum data extraction."""
        data = self.data_provider.get_spectrum_data(
            DataSpectrum.GEOGRAPHIC_ANALYSIS
        )

        # Validate required fields
        assert "primary_address" in data
        assert "regional_risk_score" in data
        assert data["regional_risk_score"] == "LOW"

        # Validate address structure
        address = data["primary_address"]
        assert "street" in address
        assert "city" in address
        assert "state" in address
        assert address["city"] == "Springfield"

        # Validate field count (should have 4+ fields)
        assert len(data) >= 4

    def test_temporal_analysis_spectrum_data(self):
        """Test Temporal Analysis spectrum data extraction."""
        data = self.data_provider.get_spectrum_data(
            DataSpectrum.TEMPORAL_ANALYSIS
        )

        # Validate required fields
        assert "account_tenure" in data
        assert "activity_trend" in data
        assert data["account_tenure"] == 78
        assert data["activity_trend"] == "STABLE"

        # Validate seasonal patterns
        assert "seasonal_spending_patterns" in data
        patterns = data["seasonal_spending_patterns"]
        assert "Q1" in patterns
        assert "Q4" in patterns

        # Validate field count (should have 5+ fields)
        assert len(data) >= 5

    def test_all_spectrums_data_coverage(self):
        """Test that all 7 spectrums have comprehensive data coverage."""
        total_fields = 0

        for spectrum in DataSpectrum:
            data = self.data_provider.get_spectrum_data(spectrum)
            total_fields += len(data)

            # Each spectrum should have meaningful data
            assert len(data) > 0

            # Validate no None values in primary fields
            for key, value in data.items():
                if key in ["customer_id", "credit_score", "total_transactions"]:
                    assert value is not None

        # Total field coverage should be substantial (targeting 310+ fields)
        # Note: Some fields may be shared across spectrums
        assert total_fields >= 50  # Conservative minimum

    def test_get_all_data_completeness(self):
        """Test complete customer data retrieval."""
        all_data = self.data_provider.get_all_data()

        # Validate comprehensive data coverage
        assert len(all_data) >= 30  # Minimum field count

        # Validate key customer identifiers
        assert all_data["customer_id"] == "EDW_HAWTHORNE_001"
        assert all_data["full_name"] == "Edwina Hawthorne"
        assert all_data["email"] == "edwina.hawthorne@example.com"

        # Validate data types
        assert isinstance(all_data["credit_score"], int)
        assert isinstance(all_data["total_transactions"], int)
        assert isinstance(all_data["satisfaction_score"], float)


class TestMultiSpectrumBaselineFramework:
    """Test suite for the main baseline framework."""

    def setup_method(self):
        """Set up test fixtures."""
        self.framework = MultiSpectrumBaselineFramework(
            langsmith_project="test_tilores_x_phase1"
        )

    def test_framework_initialization(self):
        """Test framework initializes correctly."""
        assert self.framework.data_provider is not None
        assert len(self.framework.models) == 7
        assert len(self.framework.spectrums) == 7
        assert isinstance(self.framework.results, list)
        assert self.framework.metrics is not None

    def test_model_configurations(self):
        """Test all 7 model configurations are properly set."""
        expected_models = [
            ModelProvider.LLAMA_3_3_70B_VERSATILE.value,
            ModelProvider.GPT_4O_MINI.value,
            ModelProvider.DEEPSEEK_R1_DISTILL_LLAMA_70B.value,
            ModelProvider.CLAUDE_3_HAIKU.value,
            ModelProvider.GEMINI_1_5_FLASH_002.value,
            ModelProvider.GEMINI_2_5_FLASH.value,
            ModelProvider.GEMINI_2_5_FLASH_LITE.value
        ]

        for model_name in expected_models:
            assert model_name in self.framework.models
            config = self.framework.models[model_name]

            # Validate configuration completeness
            assert config.name == model_name
            assert config.provider is not None
            assert config.response_time_target > 0
            assert config.context_limit > 0
            assert 0.8 <= config.quality_target <= 1.0
            assert config.priority in ["HIGH", "MEDIUM", "LOW"]

    def test_spectrum_configurations(self):
        """Test all 7 spectrum configurations are properly set."""
        expected_spectrums = [
            DataSpectrum.CUSTOMER_PROFILE.value,
            DataSpectrum.CREDIT_ANALYSIS.value,
            DataSpectrum.TRANSACTION_HISTORY.value,
            DataSpectrum.CALL_CENTER_OPERATIONS.value,
            DataSpectrum.ENTITY_RELATIONSHIP.value,
            DataSpectrum.GEOGRAPHIC_ANALYSIS.value,
            DataSpectrum.TEMPORAL_ANALYSIS.value
        ]

        for spectrum_name in expected_spectrums:
            assert spectrum_name in self.framework.spectrums
            config = self.framework.spectrums[spectrum_name]

            # Validate configuration completeness
            assert config.name is not None
            assert config.description is not None
            assert config.field_count > 0
            assert len(config.primary_fields) >= 2
            assert config.validation_rules is not None
            assert 0.5 <= config.quality_threshold <= 1.0

    def test_experiment_prompt_generation(self):
        """Test experiment prompt generation for different combinations."""
        # Test Customer Profile + GPT-4o-mini combination
        data = self.framework.data_provider.get_spectrum_data(
            DataSpectrum.CUSTOMER_PROFILE
        )
        prompt = self.framework.generate_experiment_prompt(
            ModelProvider.GPT_4O_MINI.value,
            DataSpectrum.CUSTOMER_PROFILE.value,
            data
        )

        # Validate prompt structure
        assert "Customer Profile" in prompt
        assert "customer insights" in prompt
        assert "90%" in prompt
        assert "EDW_HAWTHORNE_001" in prompt
        assert len(prompt) > 200  # Substantial prompt

    @pytest.mark.asyncio
    async def test_single_experiment_execution(self):
        """Test single experiment execution."""
        result = await self.framework.run_single_experiment(
            ModelProvider.GEMINI_1_5_FLASH_002.value,
            DataSpectrum.CUSTOMER_PROFILE.value
        )

        # Validate experiment result
        assert isinstance(result, ExperimentResult)
        assert result.model == ModelProvider.GEMINI_1_5_FLASH_002.value
        assert result.spectrum == DataSpectrum.CUSTOMER_PROFILE.value
        assert result.customer_id == "EDW_HAWTHORNE_001"
        assert result.start_time is not None

        # If successful, validate metrics
        if result.error_message is None:
            assert result.end_time is not None
            assert result.response_time is not None
            assert result.quality_score is not None
            assert 0.0 <= result.quality_score <= 1.0
            assert result.accuracy_score is not None
            assert result.completeness_score is not None
            assert result.raw_response is not None

    def test_accuracy_score_calculation(self):
        """Test accuracy score calculation logic."""
        # Test with good response
        good_response = """
        Analysis shows strong customer profile with excellent credit history.
        Key insights include stable payment patterns and low risk indicators.
        Recommendations focus on relationship expansion opportunities.
        Data quality assessment shows 95% completeness across all fields.
        Next steps involve regular monitoring and potential product upsells.
        """

        data = {"field1": "value1", "field2": "value2", "field3": "value3"}
        score = self.framework._calculate_accuracy_score(good_response, data)

        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be reasonably high for good response

        # Test with empty response
        empty_score = self.framework._calculate_accuracy_score("", data)
        assert empty_score == 0.0

    def test_completeness_score_calculation(self):
        """Test completeness score calculation logic."""
        # Test with comprehensive response
        comprehensive_response = """
        Key insights from the analysis show strong performance.
        Risk assessment indicates low probability of default.
        Recommendations include expanding credit facilities.
        Quality evaluation shows excellent data completeness.
        Next steps involve quarterly review and monitoring.
        """

        data = {"field1": "value1"}
        score = self.framework._calculate_completeness_score(
            comprehensive_response, data
        )

        assert 0.0 <= score <= 1.0
        assert score == 1.0  # Should find all 5 components

        # Test with partial response
        partial_response = "Some insights and risk assessment."
        partial_score = self.framework._calculate_completeness_score(
            partial_response, data
        )
        assert 0.0 <= partial_score < 1.0

    def test_baseline_metrics_calculation(self):
        """Test baseline metrics calculation with mock results."""
        # Add mock successful results
        self.framework.results = [
            ExperimentResult(
                experiment_id="test_1",
                model="gpt-4o-mini",
                spectrum="customer_profile",
                customer_id="EDW_HAWTHORNE_001",
                start_time=datetime.now(),
                end_time=datetime.now(),
                response_time=5.2,
                quality_score=0.94,
                accuracy_score=0.91,
                completeness_score=0.88
            ),
            ExperimentResult(
                experiment_id="test_2",
                model="claude-3-haiku",
                spectrum="credit_analysis",
                customer_id="EDW_HAWTHORNE_001",
                start_time=datetime.now(),
                end_time=datetime.now(),
                response_time=3.8,
                quality_score=0.92,
                accuracy_score=0.89,
                completeness_score=0.95
            )
        ]

        metrics = self.framework._calculate_baseline_metrics()

        # Validate metrics calculation
        assert metrics.total_experiments == 2
        assert metrics.successful_experiments == 2
        assert metrics.failed_experiments == 0
        assert metrics.average_response_time == 4.5  # (5.2 + 3.8) / 2
        assert metrics.average_quality_score == 0.93  # (0.94 + 0.92) / 2
        assert metrics.quality_target_achievement == 1.0  # Both > 90%

        # Validate model performance tracking
        assert "gpt-4o-mini" in metrics.model_performance
        assert "claude-3-haiku" in metrics.model_performance

        # Validate spectrum performance tracking
        assert "customer_profile" in metrics.spectrum_performance
        assert "credit_analysis" in metrics.spectrum_performance

    def test_performance_report_generation(self):
        """Test performance report generation."""
        # Add mock results for report generation
        self.framework.results = [
            ExperimentResult(
                experiment_id="test_report",
                model="gemini-1.5-flash-002",
                spectrum="customer_profile",
                customer_id="EDW_HAWTHORNE_001",
                start_time=datetime.now(),
                end_time=datetime.now(),
                response_time=3.1,
                quality_score=0.95,
                accuracy_score=0.93,
                completeness_score=0.90
            )
        ]

        # Calculate metrics first
        self.framework.metrics = self.framework._calculate_baseline_metrics()

        # Generate report
        report = self.framework.generate_performance_report()

        # Validate report content
        assert "Phase 1 Multi-Spectrum Baseline Performance Report" in report
        assert "Executive Summary" in report
        assert "Performance Metrics" in report
        assert "Model Performance Rankings" in report
        assert "Spectrum Performance Rankings" in report
        assert "95.0%" in report  # Quality score
        assert "3.1s" in report   # Response time


class TestIntegrationScenarios:
    """Integration test scenarios for comprehensive validation."""

    @pytest.mark.asyncio
    async def test_small_scale_baseline_run(self):
        """Test small-scale baseline experiment run (2 models, 2 spectrums)."""
        framework = MultiSpectrumBaselineFramework(
            langsmith_project="test_integration"
        )

        # Override models and spectrums for faster testing
        test_models = {
            ModelProvider.GEMINI_1_5_FLASH_002.value:
            framework.models[ModelProvider.GEMINI_1_5_FLASH_002.value],
            ModelProvider.CLAUDE_3_HAIKU.value:
            framework.models[ModelProvider.CLAUDE_3_HAIKU.value]
        }

        test_spectrums = {
            DataSpectrum.CUSTOMER_PROFILE.value:
            framework.spectrums[DataSpectrum.CUSTOMER_PROFILE.value],
            DataSpectrum.CREDIT_ANALYSIS.value:
            framework.spectrums[DataSpectrum.CREDIT_ANALYSIS.value]
        }

        framework.models = test_models
        framework.spectrums = test_spectrums

        # Run experiments (should be 4 total: 2 models × 2 spectrums)
        metrics = await framework.run_baseline_experiments()

        # Validate results
        assert metrics.total_experiments == 4
        assert len(framework.results) == 4

        # Validate all combinations were tested
        model_spectrum_combinations = set()
        for result in framework.results:
            model_spectrum_combinations.add((result.model, result.spectrum))

        expected_combinations = {
            (ModelProvider.GEMINI_1_5_FLASH_002.value,
             DataSpectrum.CUSTOMER_PROFILE.value),
            (ModelProvider.GEMINI_1_5_FLASH_002.value,
             DataSpectrum.CREDIT_ANALYSIS.value),
            (ModelProvider.CLAUDE_3_HAIKU.value,
             DataSpectrum.CUSTOMER_PROFILE.value),
            (ModelProvider.CLAUDE_3_HAIKU.value,
             DataSpectrum.CREDIT_ANALYSIS.value)
        }

        assert model_spectrum_combinations == expected_combinations

    def test_data_spectrum_field_coverage(self):
        """Test comprehensive field coverage across all spectrums."""
        provider = EdwinaHawthorneDataProvider()

        # Track unique fields across all spectrums
        all_fields = set()
        spectrum_field_counts = {}

        for spectrum in DataSpectrum:
            data = provider.get_spectrum_data(spectrum)
            spectrum_fields = set(data.keys())
            all_fields.update(spectrum_fields)
            spectrum_field_counts[spectrum.value] = len(spectrum_fields)

        # Validate field distribution
        assert len(all_fields) >= 30  # Minimum unique fields

        # Validate each spectrum has reasonable field count
        for spectrum_name, count in spectrum_field_counts.items():
            assert count >= 4, f"{spectrum_name} has insufficient fields: {count}"

        # Validate specific high-value spectrums have more fields
        assert spectrum_field_counts["customer_profile"] >= 10
        assert spectrum_field_counts["credit_analysis"] >= 8
        assert spectrum_field_counts["transaction_history"] >= 6


# Test execution configuration
if __name__ == "__main__":
    # Configure logging for test execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
