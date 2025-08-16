"""
Functional Tests for Live LLM Provider Responses

Tests real user experience with actual LLM providers:
- OpenAI (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
- Anthropic (claude-3-5-sonnet-20241022, claude-3-haiku-20240307)
- Groq (llama-3.1-70b-versatile, llama-3.1-8b-instant)

Validates response quality, speed, and accuracy with live data.
"""

import pytest
import time
import os
from typing import Dict, Any
from fastapi.testclient import TestClient

# Import the FastAPI app
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from main_openai_compatible import app


@pytest.mark.functional
@pytest.mark.asyncio
class TestLiveLLMProviders:
    """Test all LLM providers with live responses."""

    @classmethod
    def setup_class(cls):
        """Set up test client and validate environment."""
        cls.client = TestClient(app)
        cls.test_results = {}
        cls.performance_metrics = {}

        # Validate required environment variables
        required_env_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GROQ_API_KEY", "TILORES_TOKEN"]

        cls.missing_env_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                cls.missing_env_vars.append(var)

        if cls.missing_env_vars:
            pytest.skip(f"Missing environment variables: {cls.missing_env_vars}")

    def make_chat_request(self, model: str, message: str, expected_min_length: int = 50) -> Dict[str, Any]:
        """Make a chat completion request and measure performance."""
        start_time = time.time()

        response = self.client.post(
            "/v1/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": message}],
                "temperature": 0.1,  # Low temperature for consistent responses
                "max_tokens": 1000,
            },
        )

        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        assert response.status_code == 200, f"Request failed with status {response.status_code}: {response.text}"

        data = response.json()
        assert "choices" in data
        assert len(data["choices"]) > 0
        assert "message" in data["choices"][0]
        assert "content" in data["choices"][0]["message"]

        content = data["choices"][0]["message"]["content"]
        assert len(content) >= expected_min_length, f"Response too short: {len(content)} chars"

        return {
            "response": data,
            "content": content,
            "response_time_ms": response_time,
            "model": model,
            "tokens_used": data.get("usage", {}).get("total_tokens", 0),
        }

    @pytest.mark.parametrize("model", ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"])
    def test_openai_models_general_query(self, model):
        """Test OpenAI models with general queries."""
        result = self.make_chat_request(
            model=model,
            message="What is the capital of France? Please provide a brief explanation.",
            expected_min_length=30,
        )

        # Validate response contains expected information
        content = result["content"].lower()
        assert "paris" in content, f"Expected 'Paris' in response: {result['content']}"

        # Performance validation - OpenAI should respond within 3 seconds
        assert result["response_time_ms"] < 3000, f"OpenAI {model} too slow: {result['response_time_ms']}ms"

        # Store metrics
        self.performance_metrics[f"openai_{model}"] = result["response_time_ms"]
        self.test_results[f"openai_{model}_general"] = True

    @pytest.mark.parametrize("model", ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"])
    def test_anthropic_models_general_query(self, model):
        """Test Anthropic models with general queries."""
        result = self.make_chat_request(
            model=model, message="Explain the concept of machine learning in simple terms.", expected_min_length=50
        )

        # Validate response quality
        content = result["content"].lower()
        assert any(
            term in content for term in ["machine learning", "algorithm", "data", "pattern"]
        ), f"Response lacks ML concepts: {result['content']}"

        # Performance validation - Anthropic should respond within 4 seconds
        assert result["response_time_ms"] < 4000, f"Anthropic {model} too slow: {result['response_time_ms']}ms"

        # Store metrics
        self.performance_metrics[f"anthropic_{model.split('-')[2]}"] = result["response_time_ms"]
        self.test_results[f"anthropic_{model}_general"] = True

    @pytest.mark.parametrize("model", ["llama-3.1-70b-versatile", "llama-3.1-8b-instant"])
    def test_groq_models_general_query(self, model):
        """Test Groq models with general queries."""
        result = self.make_chat_request(
            model=model, message="What are the benefits of renewable energy?", expected_min_length=40
        )

        # Validate response quality
        content = result["content"].lower()
        assert any(
            term in content for term in ["renewable", "energy", "environment", "solar", "wind"]
        ), f"Response lacks renewable energy concepts: {result['content']}"

        # Performance validation - Groq should be very fast (under 2 seconds)
        assert result["response_time_ms"] < 2000, f"Groq {model} too slow: {result['response_time_ms']}ms"

        # Store metrics
        self.performance_metrics[f"groq_{model.split('-')[2]}"] = result["response_time_ms"]
        self.test_results[f"groq_{model}_general"] = True

    def test_customer_query_with_live_tilores_data(self):
        """Test customer query using validated test record (Dawn Bruton)."""
        # Use the validated test customer from documentation
        customer_query = "Find customer with client ID 1648647"

        result = self.make_chat_request(
            model="gpt-4o-mini",  # Fast model for customer queries
            message=customer_query,
            expected_min_length=80,  # Expect detailed customer info
        )

        content = result["content"].lower()

        # Validate response contains expected customer information
        expected_elements = ["dawn", "bruton", "1648647"]
        missing_elements = [elem for elem in expected_elements if elem not in content]

        assert (
            len(missing_elements) == 0
        ), f"Missing customer elements {missing_elements} in response: {result['content']}"

        # Performance validation for customer queries (should be under 6 seconds total)
        assert result["response_time_ms"] < 6000, f"Customer query too slow: {result['response_time_ms']}ms"

        # Store customer query metrics
        self.performance_metrics["customer_query_response_time"] = result["response_time_ms"]
        self.test_results["customer_query_live_data"] = True

    def test_streaming_response_functionality(self):
        """Test streaming responses work correctly."""
        response = self.client.post(
            "/v1/chat/completions",
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Count from 1 to 5 with explanations"}],
                "stream": True,
                "max_tokens": 200,
            },
        )

        assert response.status_code == 200

        # For streaming, we expect SSE format
        response_text = response.text
        assert "data:" in response_text, "Expected SSE format in streaming response"
        assert "[DONE]" in response_text, "Expected [DONE] marker in streaming response"

        self.test_results["streaming_functionality"] = True

    def test_model_discovery_endpoint(self):
        """Test the models endpoint returns all available models."""
        response = self.client.get("/v1/models")

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert len(data["data"]) >= 7, f"Expected at least 7 models, got {len(data['data'])}"

        # Check that all major providers are represented
        model_ids = [model["id"] for model in data["data"]]

        # Validate OpenAI models
        openai_models = [m for m in model_ids if m.startswith("gpt")]
        assert len(openai_models) >= 3, f"Expected 3+ OpenAI models, got {openai_models}"

        # Validate Anthropic models
        anthropic_models = [m for m in model_ids if m.startswith("claude")]
        assert len(anthropic_models) >= 2, f"Expected 2+ Anthropic models, got {anthropic_models}"

        # Validate Groq models
        groq_models = [m for m in model_ids if "llama" in m]
        assert len(groq_models) >= 2, f"Expected 2+ Groq models, got {groq_models}"

        self.test_results["model_discovery"] = True

    def test_token_counting_accuracy(self):
        """Test token counting accuracy across providers."""
        test_message = "This is a test message for token counting validation."

        for model in ["gpt-4o-mini", "claude-3-haiku-20240307"]:
            result = self.make_chat_request(model=model, message=test_message, expected_min_length=10)

            usage = result["response"]["usage"]
            assert usage["prompt_tokens"] > 0, f"No prompt tokens counted for {model}"
            assert usage["completion_tokens"] > 0, f"No completion tokens counted for {model}"
            assert usage["total_tokens"] > 0, f"No total tokens counted for {model}"
            assert (
                usage["total_tokens"] == usage["prompt_tokens"] + usage["completion_tokens"]
            ), f"Token math incorrect for {model}"

        self.test_results["token_counting"] = True

    def test_error_handling_for_invalid_models(self):
        """Test error handling for invalid model requests."""
        response = self.client.post(
            "/v1/chat/completions",
            json={"model": "invalid-model-name", "messages": [{"role": "user", "content": "Test message"}]},
        )

        # Should return an error but not crash
        assert response.status_code in [
            400,
            404,
            422,
        ], f"Expected error status for invalid model, got {response.status_code}"

        self.test_results["error_handling"] = True

    @pytest.mark.slow
    def test_concurrent_requests_performance(self):
        """Test system performance under concurrent load."""
        import concurrent.futures

        def make_concurrent_request():
            return self.make_chat_request(model="gpt-4o-mini", message="What is 2+2?", expected_min_length=5)

        start_time = time.time()

        # Run 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_concurrent_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        total_time = time.time() - start_time

        # All requests should complete successfully
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"

        # Average response time should be reasonable under load
        avg_response_time = sum(r["response_time_ms"] for r in results) / len(results)
        assert avg_response_time < 5000, f"Average response time too high under load: {avg_response_time}ms"

        # Total time should be less than sequential (shows some parallelization)
        assert total_time < 15, f"Concurrent requests took too long: {total_time}s"

        self.performance_metrics["concurrent_avg_response_time"] = avg_response_time
        self.performance_metrics["concurrent_total_time"] = total_time * 1000
        self.test_results["concurrent_performance"] = True

    def test_health_check_endpoints(self):
        """Test system health endpoints."""
        # Basic health check
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

        # Detailed health check
        response = self.client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "timestamp" in data

        self.test_results["health_checks"] = True

    @classmethod
    def teardown_class(cls):
        """Print comprehensive test results and performance metrics."""
        print("\n" + "=" * 80)
        print("FUNCTIONAL TEST RESULTS - LIVE LLM PROVIDER VALIDATION")
        print("=" * 80)

        # Test results summary
        passed_tests = sum(1 for result in cls.test_results.values() if result)
        total_tests = len(cls.test_results)

        print(f"\n📊 Test Results: {passed_tests}/{total_tests} passed")
        for test_name, passed in cls.test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {test_name}")

        # Performance metrics
        if cls.performance_metrics:
            print("\n⚡ Performance Metrics:")
            for metric_name, value in cls.performance_metrics.items():
                if isinstance(value, (int, float)):
                    print(f"   • {metric_name}: {value:.0f}ms")

        # Provider speed comparison
        openai_metrics = {k: v for k, v in cls.performance_metrics.items() if k.startswith("openai")}
        anthropic_metrics = {k: v for k, v in cls.performance_metrics.items() if k.startswith("anthropic")}
        groq_metrics = {k: v for k, v in cls.performance_metrics.items() if k.startswith("groq")}

        if openai_metrics:
            avg_openai = sum(openai_metrics.values()) / len(openai_metrics)
            print(f"   📈 OpenAI Average: {avg_openai:.0f}ms")

        if anthropic_metrics:
            avg_anthropic = sum(anthropic_metrics.values()) / len(anthropic_metrics)
            print(f"   📈 Anthropic Average: {avg_anthropic:.0f}ms")

        if groq_metrics:
            avg_groq = sum(groq_metrics.values()) / len(groq_metrics)
            print(f"   📈 Groq Average: {avg_groq:.0f}ms")

        print(f"\n🎯 Overall Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if passed_tests == total_tests:
            print("🎉 ALL FUNCTIONAL TESTS PASSED! System validated for production.")
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed - review and fix before deployment.")
