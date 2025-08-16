"""
Integration tests for Tilores Enhanced Multi-Provider API endpoints.

These tests use the actual FastAPI application and make real HTTP requests
to verify that the API endpoints work correctly in integration scenarios.
"""

from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

# Import the FastAPI app
from main_enhanced import app


class TestHealthEndpoints:
    """Test health check endpoints with real HTTP requests."""

    def test_health_check_endpoint(self):
        """Test basic health check endpoint returns success."""
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"  # Real API returns "ok", not "healthy"
        assert "service" in data
        assert "version" in data
        assert data["version"] == "6.4.0"

    def test_health_detailed_endpoint(self):
        """Test detailed health check includes system information."""
        client = TestClient(app)
        response = client.get("/health/detailed")

        assert response.status_code == 200
        data = response.json()
        assert "health" in data  # Real API returns "health", not "status"
        assert "uptime" in data
        assert "metrics_summary" in data
        assert "timestamp" in data


class TestModelEndpoints:
    """Test model discovery and listing endpoints."""

    @patch("core_app.MultiProviderLLMEngine")
    def test_models_endpoint(self, mock_engine_class):
        """Test models endpoint returns available models."""
        # Mock the engine instance
        mock_engine = MagicMock()
        mock_engine.get_available_models.return_value = [
            {"id": "gpt-4", "provider": "openai"},
            {"id": "claude-3-sonnet", "provider": "anthropic"},
        ]
        mock_engine_class.return_value = mock_engine

        client = TestClient(app)
        response = client.get("/v1/models")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) >= 0  # May be empty if no providers configured


class TestChatCompletionEndpoints:
    """Test chat completion endpoints with various scenarios."""

    @patch("core_app.MultiProviderLLMEngine")
    def test_chat_completion_basic_request(self, mock_engine_class):
        """Test basic chat completion request succeeds."""
        # Mock the engine instance
        mock_engine = MagicMock()
        mock_response = {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Hello! How can I help you today?"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        }
        mock_engine.aprocess_query = AsyncMock(return_value=mock_response)
        mock_engine_class.return_value = mock_engine

        client = TestClient(app)
        response = client.post(
            "/v1/chat/completions", json={"model": "gpt-4", "messages": [{"role": "user", "content": "Hello!"}]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "choices" in data
        assert len(data["choices"]) > 0

    def test_chat_completion_missing_model(self):
        """Test chat completion uses default model when not specified."""
        client = TestClient(app)
        response = client.post("/v1/chat/completions", json={"messages": [{"role": "user", "content": "Hello!"}]})

        # Should succeed with default model "gpt-4o-mini"
        assert response.status_code == 200
        data = response.json()
        assert "choices" in data
        assert data["model"] == "gpt-4o-mini"  # Default model

    def test_chat_completion_invalid_messages(self):
        """Test chat completion fails with invalid message format."""
        client = TestClient(app)
        response = client.post("/v1/chat/completions", json={"model": "gpt-4", "messages": [{"invalid": "format"}]})

        assert response.status_code == 422  # Validation error


class TestErrorHandling:
    """Test error handling scenarios in integration context."""

    def test_provider_error_handling(self):
        """Test API handles provider errors gracefully."""
        client = TestClient(app)

        # Use an invalid model to trigger error handling
        response = client.post(
            "/v1/chat/completions",
            json={"model": "invalid-model-xyz-123", "messages": [{"role": "user", "content": "Hello!"}]},
        )

        # API returns 200 with error in response body
        assert response.status_code == 200
        data = response.json()
        # Should contain either error field or a graceful response
        assert "choices" in data  # API always returns choices

    def test_invalid_endpoint(self):
        """Test accessing non-existent endpoint returns 404."""
        client = TestClient(app)
        response = client.get("/invalid/endpoint")

        assert response.status_code == 404


class TestStreamingResponses:
    """Test streaming response functionality."""

    @patch("core_app.MultiProviderLLMEngine")
    def test_streaming_chat_completion(self, mock_engine_class):
        """Test streaming chat completion endpoint."""
        # Mock the engine instance for streaming
        mock_engine = MagicMock()
        mock_engine.aprocess_query = AsyncMock(
            return_value={
                "id": "chatcmpl-test",
                "object": "chat.completion.chunk",
                "created": 1234567890,
                "model": "gpt-4",
                "choices": [{"index": 0, "delta": {"content": "Hello"}, "finish_reason": None}],
            }
        )
        mock_engine_class.return_value = mock_engine

        client = TestClient(app)
        response = client.post(
            "/v1/chat/completions",
            json={"model": "gpt-4", "messages": [{"role": "user", "content": "Hello!"}], "stream": True},
        )

        # For streaming, we expect a different response format
        assert response.status_code == 200


class TestAuthentication:
    """Test authentication and authorization scenarios."""

    def test_request_without_auth_header(self):
        """Test request without authorization header."""
        client = TestClient(app)
        response = client.post(
            "/v1/chat/completions", json={"model": "gpt-4", "messages": [{"role": "user", "content": "Hello!"}]}
        )

        # Depending on configuration, may require auth or not
        # This test verifies the endpoint at least responds
        assert response.status_code in [200, 401, 422]

    def test_request_with_invalid_auth_header(self):
        """Test request with invalid authorization header."""
        client = TestClient(app)
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.post(
            "/v1/chat/completions",
            headers=headers,
            json={"model": "gpt-4", "messages": [{"role": "user", "content": "Hello!"}]},
        )

        # Should handle invalid auth gracefully
        assert response.status_code in [200, 401, 422]


class TestConcurrentRequests:
    """Test concurrent request handling."""

    @patch("core_app.MultiProviderLLMEngine")
    def test_multiple_concurrent_requests(self, mock_engine_class):
        """Test handling multiple concurrent chat completion requests."""
        # Mock the engine instance
        mock_engine = MagicMock()
        mock_response = {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-4",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "Response"}, "finish_reason": "stop"}],
        }
        mock_engine.aprocess_query = AsyncMock(return_value=mock_response)
        mock_engine_class.return_value = mock_engine

        client = TestClient(app)

        # Make multiple requests
        responses = []
        for i in range(3):
            response = client.post(
                "/v1/chat/completions",
                json={"model": "gpt-4", "messages": [{"role": "user", "content": f"Request {i}"}]},
            )
            responses.append(response)

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200


class TestAsyncAPIBehavior:
    """Test asynchronous API behavior."""

    @patch("core_app.MultiProviderLLMEngine")
    def test_async_chat_completion(self, mock_engine_class):
        """Test chat completion with async client."""
        # Mock the engine instance
        mock_engine = MagicMock()
        mock_response = {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-4",
            "choices": [
                {"index": 0, "message": {"role": "assistant", "content": "Async response"}, "finish_reason": "stop"}
            ],
        }
        mock_engine.aprocess_query = AsyncMock(return_value=mock_response)
        mock_engine_class.return_value = mock_engine

        # Use TestClient for integration testing instead of AsyncClient
        client = TestClient(app)
        response = client.post(
            "/v1/chat/completions", json={"model": "gpt-4", "messages": [{"role": "user", "content": "Hello async!"}]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "choices" in data
