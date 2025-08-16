#!/usr/bin/env python3
"""
Clean test for the final LangSmith framework
Tests the production-ready, synchronous framework
"""

import pytest


def test_langsmith_framework_functionality():
    """Test that the clean LangSmith framework works"""
    from .langsmith_framework import LangSmithFramework

    framework = LangSmithFramework()

    # Test framework initialization
    assert len(framework.working_models) == 5  # 5 context-compatible models
    assert "gpt-3.5-turbo" not in framework.working_models  # Removed due to context limit
    assert "gpt-4o-mini" in framework.working_models  # 128K context model included
    assert len(framework.test_scenarios) == 2  # Real customer scenarios


def test_model_testing_sync():
    """Test synchronous model testing"""
    from .langsmith_framework import LangSmithFramework

    framework = LangSmithFramework()

    # Test single model
    result = framework._test_model_sync("gpt-4o-mini", "Find customer blessedwina@aol.com")

    assert "response" in result
    assert "model" in result
    assert "response_time_ms" in result
    assert "success" in result


def test_evaluators():
    """Test speed and accuracy evaluators"""
    from .langsmith_framework import LangSmithFramework

    framework = LangSmithFramework()

    # Mock run and example for testing
    class MockRun:
        def __init__(self, outputs):
            self.outputs = outputs

    class MockExample:
        def __init__(self, outputs):
            self.outputs = outputs

    # Test speed evaluator
    run = MockRun({"success": True, "response_time_ms": 3000})
    example = MockExample({})

    speed_result = framework._speed_evaluator(run, example)
    assert speed_result["key"] == "speed_score"
    assert 0 <= speed_result["score"] <= 1

    # Test accuracy evaluator
    run = MockRun({"success": True, "response": "Customer Edwina Hawthorne with ID 2270"})
    example = MockExample({"expected_customer": "Edwina Hawthorne", "expected_client_id": "2270"})

    accuracy_result = framework._accuracy_evaluator(run, example)
    assert accuracy_result["key"] == "accuracy_score"
    assert accuracy_result["score"] > 0.5  # Should find both customer and ID


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
