"""
Unit tests for main_enhanced.py API endpoints.

Tests the FastAPI application endpoints including chat completions,
model listing, health checks, and token counting utilities.
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main_enhanced import (
    app,
    count_tokens,
    count_messages_tokens,
    generate_unique_id,
    get_system_fingerprint,
    determine_finish_reason,
)


class TestTokenCountingUtilities:
    """Test token counting and utility functions."""

    @pytest.mark.unit
    def test_count_tokens_with_supported_model(self):
        """Test token counting with supported model encoding."""
        text = "Hello, this is a test message."

        token_count = count_tokens(text, "gpt-4o")

        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count < len(text)  # Should be fewer tokens than characters

    @pytest.mark.unit
    def test_count_tokens_with_unsupported_model(self):
        """Test token counting fallback for unsupported model."""
        text = "Hello, this is a test message."

        token_count = count_tokens(text, "unknown-model")

        assert isinstance(token_count, int)
        assert token_count > 0
        # Should use fallback estimation (characters / 4 + 1)
        expected_fallback = len(text) // 4 + 1
        assert token_count == expected_fallback

    @pytest.mark.unit
    def test_count_tokens_empty_text(self):
        """Test token counting with empty text."""
        token_count = count_tokens("", "gpt-4")

        assert token_count == 0  # Empty text should return 0 tokens

    @pytest.mark.unit
    def test_count_tokens_with_exception(self):
        """Test token counting fallback when tiktoken throws exception."""
        with patch("main_enhanced.tiktoken.get_encoding") as mock_get_encoding:
            mock_get_encoding.side_effect = Exception("Encoding error")

            token_count = count_tokens("test text", "gpt-4")

            assert token_count >= 1
            # Should use character-based fallback

    @pytest.mark.unit
    def test_count_messages_tokens_multiple_messages(self, sample_chat_request):
        """Test token counting for multiple chat messages."""
        messages = [
            MagicMock(role="system", content="You are a helpful assistant."),
            MagicMock(role="user", content="Hello!"),
            MagicMock(role="assistant", content="Hi there!"),
        ]

        token_count = count_messages_tokens(messages, "gpt-4")

        assert isinstance(token_count, int)
        assert token_count > 0
        # Should include overhead tokens (4 per message + 2 for conversation)
        expected_min = len(messages) * 4 + 2
        assert token_count >= expected_min

    @pytest.mark.unit
    def test_count_messages_tokens_empty_list(self):
        """Test token counting for empty message list."""
        token_count = count_messages_tokens([], "gpt-4")

        assert token_count == 2  # Just conversation overhead

    @pytest.mark.unit
    def test_generate_unique_id_format(self):
        """Test unique ID generation format and uniqueness."""
        id1 = generate_unique_id()
        id2 = generate_unique_id("custom-prefix")

        assert id1.startswith("chatcmpl-")
        assert id2.startswith("custom-prefix-")
        assert len(id1.split("-")[1]) == 20  # UUID hex length
        assert id1 != id2

    @pytest.mark.unit
    def test_get_system_fingerprint_format(self):
        """Test system fingerprint generation format."""
        fingerprint1 = get_system_fingerprint()
        fingerprint2 = get_system_fingerprint()

        assert fingerprint1.startswith("fp_")
        assert len(fingerprint1.split("_")[1]) == 10
        assert fingerprint1 != fingerprint2  # Should be unique

    @pytest.mark.unit
    def test_determine_finish_reason_stop(self):
        """Test finish reason determination for normal completion."""
        content = "This is a normal response."

        reason = determine_finish_reason(content, max_tokens=1000)

        assert reason == "stop"

    @pytest.mark.unit
    def test_determine_finish_reason_length(self):
        """Test finish reason determination for length limit."""
        content = "This is a very long response that exceeds the token limit."

        with patch("main_enhanced.count_tokens") as mock_count:
            mock_count.return_value = 1500  # Exceeds limit

            reason = determine_finish_reason(content, max_tokens=1000)

            assert reason == "length"

    @pytest.mark.unit
    def test_determine_finish_reason_no_max_tokens(self):
        """Test finish reason determination without max_tokens."""
        content = "Normal response without token limit."

        reason = determine_finish_reason(content)

        assert reason == "stop"


class TestChatCompletionsEndpoint:
    """Test the /v1/chat/completions API endpoint."""

    @pytest.mark.unit
    def test_chat_completions_successful_response(self, test_client, sample_chat_request_dict):
        """Test successful chat completion request."""
        with patch("main_enhanced.run_chain") as mock_run_chain:
            mock_run_chain.return_value = "Test response from LLM"

            response = test_client.post("/v1/chat/completions", json=sample_chat_request_dict)

            assert response.status_code == 200
            data = response.json()
            assert data["object"] == "chat.completion"
            assert data["model"] == sample_chat_request_dict["model"]
            assert len(data["choices"]) == 1
            assert data["choices"][0]["message"]["content"] == "Test response from LLM"
            assert data["choices"][0]["finish_reason"] == "stop"
            assert "usage" in data
            assert data["usage"]["total_tokens"] > 0

    @pytest.mark.unit
    def test_chat_completions_streaming_response(self, test_client):
        """Test streaming chat completion request."""
        request_data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello"}], "stream": True}

        with patch("main_enhanced.run_chain") as mock_run_chain:
            mock_run_chain.return_value = "Streaming test response"

            response = test_client.post("/v1/chat/completions", json=request_data)

            assert response.status_code == 200
            assert response.headers["content-type"] == "text/plain; charset=utf-8"
            # Should contain Server-Sent Events format
            assert "data:" in response.text

    @pytest.mark.unit
    def test_chat_completions_complex_response_extraction(self, test_client):
        """Test extraction of content from complex LangChain response objects."""
        request_data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Test"}]}

        # Test different response types
        test_cases = [
            # String response
            "Direct string response",
            # Object with content attribute
            MagicMock(content="Response with content attribute"),
            # Object with message.content
            MagicMock(message=MagicMock(content="Nested content")),
            # Dict with content key
            {"content": "Dict with content"},
            # Dict with nested message content
            {"message": {"content": "Nested dict content"}},
            # Complex object that should use fallback
            MagicMock(spec=[]),
        ]

        for i, mock_response in enumerate(test_cases):
            with patch("main_enhanced.run_chain") as mock_run_chain:
                mock_run_chain.return_value = mock_response

                response = test_client.post("/v1/chat/completions", json=request_data)

                assert response.status_code == 200
                data = response.json()
                assert "choices" in data
                assert len(data["choices"]) == 1
                # All should extract some content
                assert data["choices"][0]["message"]["content"] is not None

    @pytest.mark.unit
    def test_chat_completions_error_handling(self, test_client, sample_chat_request_dict):
        """Test error handling in chat completions endpoint."""
        with patch("main_enhanced.run_chain") as mock_run_chain:
            mock_run_chain.side_effect = Exception("LLM processing error")

            response = test_client.post("/v1/chat/completions", json=sample_chat_request_dict)

            assert response.status_code == 200  # Still returns 200 with error in response
            data = response.json()
            assert data["object"] == "chat.completion"
            assert "error" in data
            assert data["error"]["type"] == "internal_error"
            assert "LLM processing error" in data["error"]["message"]

    @pytest.mark.unit
    def test_chat_completions_invalid_request_format(self, test_client):
        """Test handling of invalid request format."""
        invalid_request = {
            "model": "gpt-4o-mini",
            # Missing required 'messages' field
            "temperature": 0.7,
        }

        response = test_client.post("/v1/chat/completions", json=invalid_request)

        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    def test_chat_completions_langsmith_integration(self, test_client, sample_chat_request_dict):
        """Test LangSmith observability integration."""
        with patch("main_enhanced.run_chain") as mock_run_chain, patch("main_enhanced.engine") as mock_engine:

            # Mock LangSmith availability
            mock_engine.langsmith_client = MagicMock()
            mock_run_chain.return_value = "Test response"

            response = test_client.post("/v1/chat/completions", json=sample_chat_request_dict)

            assert response.status_code == 200
            # Should not fail with LangSmith enabled

    @pytest.mark.unit
    def test_chat_completions_conversation_history(self, test_client):
        """Test chat completions with conversation history."""
        request_data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"},
            ],
        }

        with patch("main_enhanced.run_chain") as mock_run_chain:
            mock_run_chain.return_value = "I'm doing well, thank you!"

            response = test_client.post("/v1/chat/completions", json=request_data)

            assert response.status_code == 200
            # Should call run_chain with full conversation history
            mock_run_chain.assert_called_once()
            call_args = mock_run_chain.call_args[0]
            assert len(call_args[0]) == 4  # All 4 messages


class TestModelsEndpoint:
    """Test the /v1/models API endpoint."""

    @pytest.mark.unit
    def test_models_list_successful(self, test_client):
        """Test successful model listing."""
        mock_models = [
            {"id": "gpt-4o-mini", "provider": "openai"},
            {"id": "claude-3-haiku", "provider": "anthropic"},
            {"id": "llama-3.3-70b-versatile", "provider": "groq"},
        ]

        with patch("main_enhanced.get_available_models") as mock_get_models:
            mock_get_models.return_value = mock_models

            response = test_client.get("/v1/models")

            assert response.status_code == 200
            data = response.json()
            assert data["object"] == "list"
            assert len(data["data"]) == 3

            # Check model format
            for model in data["data"]:
                assert "id" in model
                assert "object" in model
                assert model["object"] == "model"
                assert "created" in model
                assert "owned_by" in model

    @pytest.mark.unit
    def test_models_list_error_handling(self, test_client):
        """Test error handling in models endpoint."""
        with patch("main_enhanced.get_available_models") as mock_get_models:
            mock_get_models.side_effect = Exception("Model discovery failed")

            response = test_client.get("/v1/models")

            assert response.status_code == 200  # Still returns 200 with error structure
            data = response.json()
            assert data["object"] == "error"
            assert "error" in data
            assert "Model discovery failed" in data["error"]["message"]

    @pytest.mark.unit
    def test_models_list_empty_response(self, test_client):
        """Test models endpoint with empty model list."""
        with patch("main_enhanced.get_available_models") as mock_get_models:
            mock_get_models.return_value = []

            response = test_client.get("/v1/models")

            assert response.status_code == 200
            data = response.json()
            assert data["object"] == "list"
            assert len(data["data"]) == 0

    @pytest.mark.unit
    def test_models_list_sorting(self, test_client):
        """Test that models are sorted by created timestamp."""
        mock_models = [
            {"id": "model-z", "provider": "provider1"},
            {"id": "model-a", "provider": "provider2"},
            {"id": "model-m", "provider": "provider3"},
        ]

        with patch("main_enhanced.get_available_models") as mock_get_models:
            mock_get_models.return_value = mock_models

            response = test_client.get("/v1/models")

            assert response.status_code == 200
            data = response.json()

            # Should be sorted by created timestamp
            created_times = [model["created"] for model in data["data"]]
            assert created_times == sorted(created_times)


class TestHealthAndInfoEndpoints:
    """Test health check and root information endpoints."""

    @pytest.mark.unit
    def test_health_endpoint(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "tilores-anythingllm"
        assert data["version"] == "6.4.0"

    @pytest.mark.unit
    def test_root_endpoint(self, test_client):
        """Test root information endpoint."""
        mock_models = [{"id": "gpt-4o-mini", "provider": "openai"}, {"id": "claude-3-haiku", "provider": "anthropic"}]

        with patch("main_enhanced.get_available_models") as mock_get_models:
            mock_get_models.return_value = mock_models

            response = test_client.get("/")

            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "Tilores API for AnythingLLM"
            assert data["version"] == "6.4.0"
            assert "compliance" in data
            assert data["compliance"]["openai_compatible"] is True
            assert "endpoints" in data
            assert "models" in data
            assert data["models"]["total"] == 2
            assert len(data["models"]["providers"]) >= 1


class TestStreamingFunctionality:
    """Test streaming response functionality."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_streaming_response_format(self, sample_chat_request):
        """Test streaming response format and structure."""
        from main_enhanced import generate_streaming_response

        content = "This is a test streaming response."

        # Collect all chunks
        chunks = []
        async for chunk in generate_streaming_response(sample_chat_request, content):
            chunks.append(chunk)

        assert len(chunks) > 2  # Should have opening, content, and closing chunks

        # First chunk should have role delta
        first_chunk_data = json.loads(chunks[0].replace("data: ", ""))
        assert first_chunk_data["choices"][0]["delta"]["role"] == "assistant"

        # Last chunk should be [DONE]
        assert chunks[-1] == "data: [DONE]\n\n"

        # Second to last should have finish_reason
        final_chunk_data = json.loads(chunks[-2].replace("data: ", ""))
        assert final_chunk_data["choices"][0]["finish_reason"] is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_streaming_response_metadata(self, sample_chat_request):
        """Test streaming response metadata consistency."""
        from main_enhanced import generate_streaming_response

        content = "Test content"
        chunks = []
        async for chunk in generate_streaming_response(sample_chat_request, content):
            if chunk != "data: [DONE]\n\n":
                chunks.append(chunk)

        # Parse chunks and verify consistent metadata
        chunk_data = []
        for chunk in chunks:
            data = json.loads(chunk.replace("data: ", ""))
            chunk_data.append(data)

        # All chunks should have same ID, model, and created timestamp
        first_id = chunk_data[0]["id"]
        first_model = chunk_data[0]["model"]
        first_created = chunk_data[0]["created"]

        for data in chunk_data:
            assert data["id"] == first_id
            assert data["model"] == first_model
            assert data["created"] == first_created
            assert data["object"] == "chat.completion.chunk"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_streaming_response_content_chunking(self, sample_chat_request):
        """Test content is properly chunked in streaming response."""
        from main_enhanced import generate_streaming_response

        content = "This is a longer test message that should be chunked properly."

        content_chunks = []
        async for chunk in generate_streaming_response(sample_chat_request, content):
            if chunk != "data: [DONE]\n\n":
                data = json.loads(chunk.replace("data: ", ""))
                if "content" in data["choices"][0]["delta"]:
                    content_chunks.append(data["choices"][0]["delta"]["content"])

        # Reassemble content from chunks
        reassembled = "".join(content_chunks)
        assert reassembled.strip() == content

        # Should have multiple content chunks for longer text
        assert len(content_chunks) > 1


class TestApplicationInitialization:
    """Test FastAPI application initialization and configuration."""

    @pytest.mark.unit
    def test_app_configuration(self):
        """Test FastAPI app configuration."""
        assert app.title == "Tilores API for AnythingLLM"
        assert app.description == "Fully OpenAI-compatible API with Tilores integration"
        assert app.version == "6.4.0"

    @pytest.mark.unit
    def test_engine_initialization(self):
        """Test engine initialization is called during import."""
        # Engine initialization happens at module import time,
        # so we test that the initialize_engine function exists and is callable
        from main_enhanced import initialize_engine

        assert callable(initialize_engine)

        # Test that we can call it without errors
        try:
            initialize_engine()
        except Exception as e:
            # Should not raise unexpected exceptions in test environment
            assert "test" in str(e).lower() or "mock" in str(e).lower()
