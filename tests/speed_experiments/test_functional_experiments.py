#!/usr/bin/env python3
"""
Functional tests for speed experiments
Tests actual functionality rather than NotImplementedError
"""

import pytest
from .speed_experiment_runner import LangSmithSpeedExperimentRunner
from .conversational_scenarios import ConversationalCreditScenarios
from .graphql_validator import GraphQLValidator


def test_speed_experiment_runner_functionality():
    """Test that speed experiment runner works functionally"""
    runner = LangSmithSpeedExperimentRunner()

    # Test experiment config creation
    models = [{"id": "test-model", "provider": "test"}]
    config = runner.create_experiment_config("test-experiment", models)

    assert config["name"] == "test-experiment"
    assert config["models"] == models
    assert "scenarios" in config
    assert "metrics" in config


def test_conversational_scenarios_functionality():
    """Test that conversational scenarios work functionally"""
    scenarios = ConversationalCreditScenarios()

    customer_data = {"customer_id": "123", "name": "Test Customer", "credit_score": 750}

    # Test two-turn scenario creation
    scenario = scenarios.create_two_turn_scenario(customer_data)

    assert "scenario_id" in scenario
    assert scenario["customer_data"] == customer_data
    assert len(scenario["turns"]) == 2
    assert scenario["turns"][0]["turn_number"] == 1
    assert scenario["turns"][1]["turn_number"] == 2


def test_graphql_validator_functionality():
    """Test that GraphQL validator works functionally"""
    validator = GraphQLValidator()

    customer_data = {"customer_id": "123", "name": "Test Customer", "email": "test@example.com"}

    # Test query building
    query = validator.build_credit_report_query(customer_data)

    assert "search" in query
    assert "EMAIL" in query
    assert "test@example.com" in query


def test_accuracy_scoring():
    """Test accuracy scoring functionality"""
    scenarios = ConversationalCreditScenarios()

    expected_data = {"name": "John Smith", "credit_score": 750}

    # Test with good response
    good_response = "Customer John Smith found. Credit score: 750. Payment history shows good standing."
    result = scenarios.score_credit_response_accuracy(good_response, expected_data)

    assert result["accuracy_score"] > 50
    assert result["details"]["customer_identified"] == True
    assert result["details"]["credit_score_mentioned"] == True

    # Test with poor response
    poor_response = "Hello"
    result = scenarios.score_credit_response_accuracy(poor_response, expected_data)

    assert result["accuracy_score"] < 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
