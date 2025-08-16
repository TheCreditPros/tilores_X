#!/usr/bin/env python3
"""
Simple test for LangSmith speed experiments
TDD approach - tests fail initially, then we implement
"""

import pytest


def test_speed_experiment_runner_not_implemented():
    """Test that speed experiment runner raises NotImplementedError"""
    from .speed_experiment_runner import LangSmithSpeedExperimentRunner

    runner = LangSmithSpeedExperimentRunner()

    with pytest.raises(NotImplementedError):
        runner.create_experiment_config("test", [])


def test_conversational_scenarios_not_implemented():
    """Test that conversational scenarios raise NotImplementedError"""
    from .conversational_scenarios import ConversationalCreditScenarios

    scenarios = ConversationalCreditScenarios()

    with pytest.raises(NotImplementedError):
        scenarios.create_two_turn_scenario({})


def test_graphql_validator_not_implemented():
    """Test that GraphQL validator raises NotImplementedError"""
    from .graphql_validator import GraphQLValidator

    validator = GraphQLValidator()

    with pytest.raises(NotImplementedError):
        validator.build_credit_report_query({})


def test_cli_integration_not_implemented():
    """Test that CLI integration raises NotImplementedError"""
    from .cli_integration import LangSmithCLI

    cli = LangSmithCLI()

    with pytest.raises(NotImplementedError):
        cli.create_experiment("test", [])


def test_experiment_pipeline_not_implemented():
    """Test that experiment pipeline raises NotImplementedError"""
    from .experiment_pipeline import SpeedExperimentPipeline

    pipeline = SpeedExperimentPipeline()

    with pytest.raises(NotImplementedError):
        pipeline.run_full_experiment([], [])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
