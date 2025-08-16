"""
Comprehensive unit tests for main_openai_compatible.py
Tests the OpenAI-compatible API implementation with Tilores integration
"""

import pytest
import time
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi.responses import StreamingResponse

# Import the module under test
from main_openai_compatible import (
    app,
    ChatMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ModelInfo,
    MultiProviderLLMEngine,
)


class TestPydanticModels:
    """Test Pydantic model validation and serialization."""

    def test_chat_message_creation(self):
        """Test ChatMessage model creation and validation."""
        message = ChatMessage(role="user", content="Hello, world!")
        assert message.role == "user"
        assert message.content == "Hello, world!"

    def test_chat_completion_request_creation(self):
        """Test ChatCompletionRequest model with all fields."""
        messages = [ChatMessage(role="user", content="Test message")]
        request = ChatCompletionRequest(
            model="gpt-4o", messages=messages, max_tokens=100, temperature=0.8, stream=True, user="test_user"
        )

        assert request.model == "gpt-4o"
        assert len(request.messages) == 1
        assert request.max_tokens == 100
        assert request.temperature == 0.8
        assert request.stream is True
        assert request.user == "test_user"

    def test_chat_completion_request_defaults(self):
        """Test ChatCompletionRequest model with default values."""
        messages = [ChatMessage(role="user", content="Test")]
        request = ChatCompletionRequest(model="gpt-4o", messages=messages)

        assert request.max_tokens is None
        assert request.temperature == 0.7
        assert request.stream is False
        assert request.user is None

    def test_chat_completion_response_creation(self):
        """Test ChatCompletionResponse model creation."""
        response = ChatCompletionResponse(
            id="test-id",
            object="chat.completion",
            created=1234567890,
            model="gpt-4o",
            choices=[{"index": 0, "message": {"role": "assistant", "content": "Test"}}],
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            system_fingerprint="fp_test",
        )

        assert response.id == "test-id"
        assert response.object == "chat.completion"
        assert response.created == 1234567890
        assert response.model == "gpt-4o"
        assert len(response.choices) == 1
        assert response.usage["total_tokens"] == 30
        assert response.system_fingerprint == "fp_test"

    def test_model_info_creation(self):
        """Test ModelInfo model creation."""
        model = ModelInfo(id="gpt-4o", object="model", created=1234567890, owned_by="openai")

        assert model.id == "gpt-4o"
        assert model.object == "model"
        assert model.created == 1234567890
        assert model.owned_by == "openai"


class TestMultiProviderLLMEngine:
    """Test the MultiProviderLLMEngine class."""

    @patch("tiktoken.get_encoding")
    def test_engine_initialization(self, mock_get_encoding):
        """Test engine initialization with model mappings and tokenizer."""
        mock_tokenizer = MagicMock()
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()

        # Verify model mappings are loaded
        assert "gpt-4o" in engine.model_mappings
        assert "claude-3-sonnet" in engine.model_mappings
        assert "llama-3.3-70b-versatile" in engine.model_mappings
        assert "gemini-pro" in engine.model_mappings

        # Verify tokenizer is initialized
        mock_get_encoding.assert_called_once_with("cl100k_base")
        assert engine.tokenizer == mock_tokenizer

    @patch("tiktoken.get_encoding")
    def test_get_available_models(self, mock_get_encoding):
        """Test getting list of available models."""
        mock_tokenizer = MagicMock()
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()
        models = engine.get_available_models()

        # Should return list of ModelInfo objects
        assert isinstance(models, list)
        assert len(models) > 0
        assert all(isinstance(model, ModelInfo) for model in models)

        # Check specific models are included
        model_ids = [model.id for model in models]
        assert "gpt-4o" in model_ids
        assert "claude-3-sonnet" in model_ids
        assert "llama-3.3-70b-versatile" in model_ids

        # Verify model properties
        gpt_model = next(m for m in models if m.id == "gpt-4o")
        assert gpt_model.object == "model"
        assert gpt_model.owned_by == "openai"
        assert isinstance(gpt_model.created, int)

    @patch("tiktoken.get_encoding")
    def test_count_tokens(self, mock_get_encoding):
        """Test token counting functionality."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = ["token1", "token2", "token3"]
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()
        token_count = engine.count_tokens("Hello, world!")

        assert token_count == 3
        mock_tokenizer.encode.assert_called_once_with("Hello, world!")

    @patch("tiktoken.get_encoding")
    def test_count_message_tokens(self, mock_get_encoding):
        """Test counting tokens in message list."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.side_effect = lambda text: ["token"] * len(text.split())
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()
        messages = [ChatMessage(role="user", content="Hello world"), ChatMessage(role="assistant", content="Hi there")]

        token_count = engine.count_message_tokens(messages)

        # Should include tokens for content + role + overhead
        # user: 1 token, Hello world: 2 tokens, assistant: 1 token, Hi there: 2 tokens
        # Plus 4 tokens overhead per message + 2 for conversation = 6 + 8 + 2 = 16
        assert token_count == 16

    @patch("tiktoken.get_encoding")
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_generate_response_unsupported_model(self, mock_get_encoding):
        """Test generate_response with unsupported model raises HTTPException."""
        mock_tokenizer = MagicMock()
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()
        request = ChatCompletionRequest(model="unsupported-model", messages=[ChatMessage(role="user", content="Test")])

        with pytest.raises(Exception) as exc_info:
            await engine.generate_response(request)

        assert "Model unsupported-model not supported" in str(exc_info.value)

    @patch("tiktoken.get_encoding")
    @pytest.mark.asyncio
    async def test_enhance_messages_with_tilores(self, mock_get_encoding):
        """Test message enhancement with Tilores context."""
        mock_tokenizer = MagicMock()
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()
        original_messages = [ChatMessage(role="user", content="Hello")]

        enhanced = await engine._enhance_messages_with_tilores(original_messages)

        # Should add system message + original messages
        assert len(enhanced) == 2
        assert enhanced[0].role == "system"
        assert "Tilores" in enhanced[0].content
        assert "get_customer_credit_report" in enhanced[0].content
        assert enhanced[1] == original_messages[0]

    @patch("tiktoken.get_encoding")
    @pytest.mark.asyncio
    async def test_generate_mock_response_credit_query(self, mock_get_encoding):
        """Test mock response generation for credit queries."""
        mock_tokenizer = MagicMock()
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()
        messages = [ChatMessage(role="user", content="Get credit report for customer 123")]

        with patch("main_openai_compatible.get_customer_credit_report") as mock_credit:
            mock_credit.return_value = "Credit report data"
            response = await engine._generate_mock_response(messages, "gpt-4o")

            assert response == "Credit report data"
            mock_credit.assert_called_once_with("123")

    @patch("tiktoken.get_encoding")
    @pytest.mark.asyncio
    async def test_generate_mock_response_credit_comparison(self, mock_get_encoding):
        """Test mock response generation for credit comparison."""
        mock_tokenizer = MagicMock()
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()
        messages = [ChatMessage(role="user", content="Compare credit for 123 and 456")]

        with patch("main_openai_compatible.compare_customer_credit_profiles") as mock_compare:
            mock_compare.return_value = "Comparison data"
            response = await engine._generate_mock_response(messages, "gpt-4o")

            assert response == "Comparison data"
            mock_compare.assert_called_once_with("123, 456")

    @patch("tiktoken.get_encoding")
    @pytest.mark.asyncio
    async def test_generate_mock_response_field_discovery(self, mock_get_encoding):
        """Test mock response generation for field discovery."""
        mock_tokenizer = MagicMock()
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()
        messages = [ChatMessage(role="user", content="Discover available fields")]

        with patch("main_openai_compatible.discover_tilores_fields") as mock_discover:
            mock_discover.return_value = "Field discovery data"
            response = await engine._generate_mock_response(messages, "gpt-4o")

            assert response == "Field discovery data"
            mock_discover.assert_called_once_with("all")

    @patch("tiktoken.get_encoding")
    @pytest.mark.asyncio
    async def test_generate_mock_response_default(self, mock_get_encoding):
        """Test mock response generation for generic queries."""
        mock_tokenizer = MagicMock()
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()
        messages = [ChatMessage(role="user", content="Hello, how are you?")]

        response = await engine._generate_mock_response(messages, "gpt-4o")

        assert "gpt-4o" in response
        assert "Tilores" in response
        assert "customer data analysis" in response

    @patch("tiktoken.get_encoding")
    @pytest.mark.asyncio
    async def test_handle_credit_report_no_identifier(self, mock_get_encoding):
        """Test credit report handler when no identifier is found."""
        mock_tokenizer = MagicMock()
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()
        response = await engine._handle_credit_report("show me credit information")

        assert "Please provide a client ID" in response

    @patch("tiktoken.get_encoding")
    @pytest.mark.asyncio
    async def test_handle_credit_report_with_error(self, mock_get_encoding):
        """Test credit report handler when function raises error."""
        mock_tokenizer = MagicMock()
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()

        with patch("main_openai_compatible.get_customer_credit_report") as mock_credit:
            mock_credit.side_effect = Exception("Test error")
            response = await engine._handle_credit_report("credit report for 123")

            assert "Error retrieving credit report: Test error" in response

    @patch("tiktoken.get_encoding")
    @pytest.mark.asyncio
    async def test_handle_credit_comparison_insufficient_identifiers(self, mock_get_encoding):
        """Test credit comparison with insufficient identifiers."""
        mock_tokenizer = MagicMock()
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()
        response = await engine._handle_credit_comparison("compare credit for 123")

        assert "Please provide at least 2 client identifiers" in response

    @patch("tiktoken.get_encoding")
    @pytest.mark.asyncio
    async def test_handle_credit_comparison_with_error(self, mock_get_encoding):
        """Test credit comparison handler when function raises error."""
        mock_tokenizer = MagicMock()
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()

        with patch("main_openai_compatible.compare_customer_credit_profiles") as mock_compare:
            mock_compare.side_effect = Exception("Test error")
            response = await engine._handle_credit_comparison("compare 123 and 456")

            assert "Error comparing credit profiles: Test error" in response

    @patch("tiktoken.get_encoding")
    @pytest.mark.asyncio
    async def test_handle_field_discovery_stats(self, mock_get_encoding):
        """Test field discovery handler for stats query."""
        mock_tokenizer = MagicMock()
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()
        response = await engine._handle_field_discovery("show me field stats")

        assert "310+ fields available" in response

    @patch("tiktoken.get_encoding")
    @pytest.mark.asyncio
    async def test_handle_field_discovery_with_error(self, mock_get_encoding):
        """Test field discovery handler when function raises error."""
        mock_tokenizer = MagicMock()
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()

        with patch("main_openai_compatible.discover_tilores_fields") as mock_discover:
            mock_discover.side_effect = Exception("Test error")
            response = await engine._handle_field_discovery("discover fields")

            assert "Error with field discovery: Test error" in response


class TestAPIEndpoints:
    """Test FastAPI endpoints."""

    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test root endpoint returns API information."""
        response = self.client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Tilores OpenAI-Compatible API v6.0.0"
        assert "features" in data
        assert "endpoints" in data
        assert len(data["features"]) > 0

    def test_health_check_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "tilores-openai-compatible"
        assert data["version"] == "6.0.0"
        assert "timestamp" in data
        assert isinstance(data["timestamp"], int)

    def test_list_models_endpoint(self):
        """Test models listing endpoint."""
        response = self.client.get("/v1/models")

        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "list"
        assert "data" in data
        assert len(data["data"]) > 0

        # Check model structure
        model = data["data"][0]
        assert "id" in model
        assert "object" in model
        assert "created" in model
        assert "owned_by" in model

    @patch("main_openai_compatible.llm_engine.generate_response")
    def test_chat_completions_endpoint_success(self, mock_generate):
        """Test chat completions endpoint success case."""
        mock_response = ChatCompletionResponse(
            id="test-id",
            object="chat.completion",
            created=int(time.time()),
            model="gpt-4o",
            choices=[{"index": 0, "message": {"role": "assistant", "content": "Test response"}}],
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            system_fingerprint="fp_test",
        )
        mock_generate.return_value = mock_response

        request_data = {"model": "gpt-4o", "messages": [{"role": "user", "content": "Hello"}]}

        response = self.client.post("/v1/chat/completions", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-id"
        assert data["model"] == "gpt-4o"

    @patch("main_openai_compatible.llm_engine.generate_response")
    def test_chat_completions_endpoint_error(self, mock_generate):
        """Test chat completions endpoint error handling."""
        mock_generate.side_effect = Exception("Test error")

        request_data = {"model": "gpt-4o", "messages": [{"role": "user", "content": "Hello"}]}

        response = self.client.post("/v1/chat/completions", json=request_data)

        assert response.status_code == 500
        assert "Test error" in response.json()["detail"]

    @patch("main_openai_compatible.discover_tilores_fields")
    def test_field_discovery_endpoint_success(self, mock_discover):
        """Test field discovery endpoint success case."""
        mock_discover.return_value = "Field discovery result"

        response = self.client.get("/v1/field-discovery/customer")

        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "Field discovery result"
        mock_discover.assert_called_once_with("customer")

    @patch("main_openai_compatible.discover_tilores_fields")
    def test_field_discovery_endpoint_default_category(self, mock_discover):
        """Test field discovery endpoint with default category."""
        mock_discover.return_value = "All fields"

        response = self.client.get("/v1/field-discovery/all")

        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "All fields"
        mock_discover.assert_called_once_with("all")

    @patch("main_openai_compatible.discover_tilores_fields")
    def test_field_discovery_endpoint_error(self, mock_discover):
        """Test field discovery endpoint error handling."""
        mock_discover.side_effect = Exception("Discovery error")

        response = self.client.get("/v1/field-discovery/customer")

        assert response.status_code == 500
        assert "Discovery error" in response.json()["detail"]

    @patch("main_openai_compatible.get_customer_credit_report")
    def test_credit_report_endpoint_success(self, mock_credit):
        """Test credit report endpoint success case."""
        mock_credit.return_value = "Credit report data"

        response = self.client.get("/v1/credit-report/12345")

        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "Credit report data"
        mock_credit.assert_called_once_with("12345")

    @patch("main_openai_compatible.get_customer_credit_report")
    def test_credit_report_endpoint_error(self, mock_credit):
        """Test credit report endpoint error handling."""
        mock_credit.side_effect = Exception("Credit error")

        response = self.client.get("/v1/credit-report/12345")

        assert response.status_code == 500
        assert "Credit error" in response.json()["detail"]

    @patch("main_openai_compatible.compare_customer_credit_profiles")
    def test_credit_comparison_endpoint_success(self, mock_compare):
        """Test credit comparison endpoint success case."""
        mock_compare.return_value = "Comparison result"

        request_data = ["123", "456", "789"]
        response = self.client.post("/v1/credit-comparison", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "Comparison result"
        mock_compare.assert_called_once_with("123, 456, 789")

    @patch("main_openai_compatible.compare_customer_credit_profiles")
    def test_credit_comparison_endpoint_error(self, mock_compare):
        """Test credit comparison endpoint error handling."""
        mock_compare.side_effect = Exception("Comparison error")

        request_data = ["123", "456"]
        response = self.client.post("/v1/credit-comparison", json=request_data)

        assert response.status_code == 500
        assert "Comparison error" in response.json()["detail"]


class TestStreamingResponse:
    """Test streaming response functionality."""

    @patch("tiktoken.get_encoding")
    @pytest.mark.asyncio
    async def test_generate_streaming_response(self, mock_get_encoding):
        """Test streaming response generation."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = ["token"] * 5
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()
        request = ChatCompletionRequest(
            model="gpt-4o", messages=[ChatMessage(role="user", content="Hello")], stream=True
        )

        model_config = engine.model_mappings["gpt-4o"]
        input_tokens = 10
        messages = [ChatMessage(role="user", content="Hello")]

        with patch.object(engine, "_generate_mock_response") as mock_gen:
            mock_gen.return_value = "Hello world test"

            response = await engine._generate_streaming_response(request, model_config, input_tokens, messages)

            assert isinstance(response, StreamingResponse)
            assert response.media_type == "text/plain"

    @patch("tiktoken.get_encoding")
    @pytest.mark.asyncio
    async def test_generate_complete_response(self, mock_get_encoding):
        """Test complete response generation."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = ["token"] * 5
        mock_get_encoding.return_value = mock_tokenizer

        engine = MultiProviderLLMEngine()
        request = ChatCompletionRequest(model="gpt-4o", messages=[ChatMessage(role="user", content="Hello")])

        model_config = engine.model_mappings["gpt-4o"]
        input_tokens = 10
        messages = [ChatMessage(role="user", content="Hello")]

        with patch.object(engine, "_generate_mock_response") as mock_gen:
            mock_gen.return_value = "Test response"

            response = await engine._generate_complete_response(request, model_config, input_tokens, messages)

            assert isinstance(response, ChatCompletionResponse)
            assert response.model == "gpt-4o"
            assert response.object == "chat.completion"
            assert response.choices[0]["message"]["content"] == "Test response"
            assert response.usage["prompt_tokens"] == input_tokens
            assert response.usage["completion_tokens"] == 5
            assert response.usage["total_tokens"] == 15


class TestIntegrationWithDependencies:
    """Test integration with external dependencies."""

    @patch("tiktoken.get_encoding")
    @patch("main_openai_compatible.get_customer_credit_report")
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_full_generate_response_credit_query(self, mock_credit, mock_get_encoding):
        """Test full response generation for credit query."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = ["token"] * 3
        mock_get_encoding.return_value = mock_tokenizer
        mock_credit.return_value = "Full credit report"

        engine = MultiProviderLLMEngine()
        request = ChatCompletionRequest(
            model="gpt-4o", messages=[ChatMessage(role="user", content="Get credit report for 123")]
        )

        response = await engine.generate_response(request)

        assert isinstance(response, ChatCompletionResponse)
        assert response.choices[0]["message"]["content"] == "Full credit report"

    @patch("tiktoken.get_encoding")
    @patch("main_openai_compatible.discover_tilores_fields")
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_full_generate_response_field_discovery(self, mock_discover, mock_get_encoding):
        """Test full response generation for field discovery."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = ["token"] * 3
        mock_get_encoding.return_value = mock_tokenizer
        mock_discover.return_value = "Field discovery results"

        engine = MultiProviderLLMEngine()
        request = ChatCompletionRequest(
            model="gpt-4o", messages=[ChatMessage(role="user", content="Discover customer fields")]
        )

        response = await engine.generate_response(request)

        assert isinstance(response, ChatCompletionResponse)
        assert response.choices[0]["message"]["content"] == "Field discovery results"
