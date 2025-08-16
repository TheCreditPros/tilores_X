"""
Comprehensive test fixtures and mocks for tilores_X testing infrastructure.

This file provides shared fixtures for unit, integration, and performance tests,
following pytest best practices and TDD principles.
"""

import asyncio
import os
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Import application modules for testing
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_enhanced import app
from core_app import MultiProviderLLMEngine, QueryRouter
from redis_cache import RedisCacheManager
from field_discovery_system import TiloresFieldDiscovery


# ============================================================================
# ENVIRONMENT AND CONFIGURATION FIXTURES
# ============================================================================


@pytest.fixture(scope="session")
def test_env_vars():
    """Set up test environment variables."""
    test_env = {
        "TILORES_API_URL": "https://test-api.example.com",
        "TILORES_CLIENT_ID": "test_client_id",
        "TILORES_CLIENT_SECRET": "test_client_secret",
        "TILORES_TOKEN_URL": "https://test-token.example.com/oauth2/token",
        "TILORES_TIMEOUT": "30000",
        "OPENAI_API_KEY": "test_openai_key",
        "ANTHROPIC_API_KEY": "test_anthropic_key",
        "GOOGLE_API_KEY": "test_google_key",
        "GROQ_API_KEY": "test_groq_key",
        "OPENROUTER_API_KEY": "test_openrouter_key",
        "REDIS_URL": "redis://localhost:6379/1",
        "LANGSMITH_TRACING": "false",
        "PORT": "8001",
    }

    # Store original values
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    yield test_env

    # Restore original values
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def mock_env_missing_vars():
    """Test environment with missing critical variables."""
    return {
        "TILORES_API_URL": "",
        "TILORES_CLIENT_ID": "",
        "TILORES_CLIENT_SECRET": "",
        "TILORES_TOKEN_URL": "",
    }


# ============================================================================
# API CLIENT FIXTURES
# ============================================================================


@pytest.fixture
def test_client(test_env_vars):
    """FastAPI test client for API endpoint testing."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def async_test_client(test_env_vars):
    """Async test client for async endpoint testing."""
    from httpx import AsyncClient

    async def _get_client():
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    return _get_client


# ============================================================================
# MOCK FIXTURES FOR EXTERNAL DEPENDENCIES
# ============================================================================


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing cache functionality."""
    mock_client = MagicMock()
    mock_client.ping.return_value = True
    mock_client.get.return_value = None
    mock_client.setex.return_value = True
    mock_client.delete.return_value = 1
    mock_client.keys.return_value = []
    return mock_client


@pytest.fixture
def mock_redis_unavailable():
    """Mock Redis client that simulates unavailable Redis."""
    mock_client = MagicMock()
    mock_client.ping.side_effect = Exception("Redis connection failed")
    return mock_client


@pytest.fixture
def mock_tilores_api():
    """Mock Tilores API for testing integrations."""
    mock_api = MagicMock()
    mock_api.api_url = "https://test-api.example.com"
    mock_api.gql.return_value = {
        "data": {
            "search": {
                "entities": [
                    {
                        "id": "test_entity_id",
                        "records": [
                            {
                                "id": "test_record_id",
                                "EMAIL": "test@example.com",
                                "FIRST_NAME": "Test",
                                "LAST_NAME": "User",
                                "CLIENT_ID": "123456",
                                "PHONE_EXTERNAL": "555-0123",
                            }
                        ],
                    }
                ]
            }
        }
    }
    return mock_api


@pytest.fixture
def mock_tilores_tools():
    """Mock TiloresTools for testing tool functionality."""
    mock_tools = MagicMock()

    # Mock search tool
    mock_search_tool = MagicMock()
    mock_search_tool.name = "tilores_search"
    mock_search_tool.invoke.return_value = "Test customer data retrieved"

    # Mock edge tool
    mock_edge_tool = MagicMock()
    mock_edge_tool.name = "tilores_entity_edges"
    mock_edge_tool.invoke.return_value = "Test edge data retrieved"

    mock_tools.search_tool.return_value = mock_search_tool
    mock_tools.edge_tool.return_value = mock_edge_tool

    return mock_tools


@pytest.fixture
def mock_llm_providers():
    """Mock LLM providers for testing multi-provider functionality."""
    providers = {}

    # Mock OpenAI
    mock_openai = MagicMock()
    mock_openai.invoke.return_value = MagicMock(content="Test OpenAI response")
    mock_openai.stream.return_value = iter(["Test", " OpenAI", " streaming"])
    # Add length support for mock
    mock_openai.__len__ = MagicMock(return_value=1)
    providers["openai"] = mock_openai

    # Mock Anthropic
    mock_anthropic = MagicMock()
    mock_anthropic.invoke.return_value = MagicMock(content="Test Anthropic response")
    mock_anthropic.stream.return_value = iter(["Test", " Anthropic", " streaming"])
    mock_anthropic.__len__ = MagicMock(return_value=1)
    providers["anthropic"] = mock_anthropic

    # Mock Groq
    mock_groq = MagicMock()
    mock_groq.invoke.return_value = MagicMock(content="Test Groq response")
    mock_groq.stream.return_value = iter(["Test", " Groq", " streaming"])
    mock_groq.__len__ = MagicMock(return_value=1)
    providers["groq"] = mock_groq

    return providers


# ============================================================================
# APPLICATION COMPONENT FIXTURES
# ============================================================================


@pytest.fixture
def mock_cache_manager(mock_redis_client):
    """Mock cache manager with Redis functionality."""
    with patch("redis_cache.redis") as mock_redis_module:
        mock_redis_module.from_url.return_value = mock_redis_client
        mock_redis_module.Redis.return_value = mock_redis_client

        cache_manager = RedisCacheManager()
        cache_manager.redis_client = mock_redis_client
        cache_manager.cache_available = True

        yield cache_manager


@pytest.fixture
def mock_cache_manager_unavailable(mock_redis_unavailable):
    """Mock cache manager with unavailable Redis."""
    with patch("redis_cache.redis") as mock_redis_module:
        mock_redis_module.from_url.side_effect = Exception("Redis unavailable")
        mock_redis_module.Redis.side_effect = Exception("Redis unavailable")

        cache_manager = RedisCacheManager()
        cache_manager.redis_client = None
        cache_manager.cache_available = False

        yield cache_manager


@pytest.fixture
def mock_query_router():
    """Mock query router for testing routing logic."""
    router = QueryRouter()
    return router


@pytest.fixture
def mock_field_discovery():
    """Mock field discovery system."""
    discovery = TiloresFieldDiscovery()
    discovery._field_cache = {
        "customer_fields": ["EMAIL", "FIRST_NAME", "LAST_NAME", "CLIENT_ID"],
        "credit_fields": ["CREDIT_SCORE", "CREDIT_REPORT", "PAYMENT_HISTORY"],
        "system_fields": ["RECORD_ID", "CREATED_DATE", "UPDATED_DATE"],
    }
    return discovery


@pytest.fixture
def mock_llm_engine(mock_tilores_api, mock_tilores_tools, mock_llm_providers):
    """Mock LLM engine with all components."""
    with patch("core_app.TiloresAPI") as mock_tilores_class, patch("core_app.TiloresTools") as mock_tools_class:

        mock_tilores_class.from_environ.return_value = mock_tilores_api
        mock_tools_class.return_value = mock_tilores_tools

        engine = MultiProviderLLMEngine()
        engine.tilores = mock_tilores_api

        # Create mock tools with proper attributes and length support
        mock_search_tool = MagicMock()
        mock_search_tool.name = "tilores_search"
        mock_search_tool.invoke.return_value = "Test customer data retrieved"
        mock_search_tool.__len__ = MagicMock(return_value=1)

        mock_edge_tool = MagicMock()
        mock_edge_tool.name = "tilores_entity_edges"
        mock_edge_tool.invoke.return_value = "Test edge data retrieved"
        mock_edge_tool.__len__ = MagicMock(return_value=1)

        mock_record_tool = MagicMock()
        mock_record_tool.name = "tilores_record_lookup"
        mock_record_tool.invoke.return_value = "Test record data retrieved"
        mock_record_tool.__len__ = MagicMock(return_value=1)

        mock_credit_tool = MagicMock()
        mock_credit_tool.name = "tilores_credit_report"
        mock_credit_tool.invoke.return_value = "Test credit data retrieved"
        mock_credit_tool.__len__ = MagicMock(return_value=1)

        # Tools list with length support
        engine.tools = [mock_search_tool, mock_edge_tool, mock_record_tool, mock_credit_tool]
        engine.tools.__len__ = MagicMock(return_value=4)

        engine.all_fields = {"EMAIL": True, "FIRST_NAME": True, "LAST_NAME": True}

        # Enhanced model configuration
        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content="Test response from LLM")
        mock_model.stream.return_value = [MagicMock(content="chunk1"), MagicMock(content="chunk2")]
        mock_model.__len__ = MagicMock(return_value=1)

        # Mock get_model to return properly configured model
        engine.get_model = MagicMock(return_value=mock_model)

        # Mock get_llm_with_tools for tool-enabled scenarios
        mock_llm_with_tools = MagicMock()
        mock_response_with_tools = MagicMock()
        mock_response_with_tools.content = "Customer found: John Doe"
        mock_response_with_tools.tool_calls = []
        mock_llm_with_tools.invoke.return_value = mock_response_with_tools
        mock_llm_with_tools.stream.return_value = [MagicMock(content="tool_chunk1")]
        mock_llm_with_tools.__len__ = MagicMock(return_value=1)
        engine.get_llm_with_tools = MagicMock(return_value=mock_llm_with_tools)

        # Mock provider information
        engine.get_provider = MagicMock(return_value="openai")

        # Mock model mappings for testing
        engine.model_mappings = {
            "gpt-4o": {"provider": "openai"},
            "gpt-4o-mini": {"provider": "openai"},
            "claude-3-haiku": {"provider": "anthropic"},
            "llama-3.3-70b-versatile": {"provider": "groq"},
        }

        # Mock list_models method
        engine.list_models = MagicMock(
            return_value=[
                {"id": "gpt-4o", "provider": "openai"},
                {"id": "gpt-4o-mini", "provider": "openai"},
                {"id": "llama-3.3-70b-versatile", "provider": "groq"},
            ]
        )

        yield engine


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return {
        "id": "test_record_id",
        "EMAIL": "test.customer@example.com",
        "FIRST_NAME": "John",
        "LAST_NAME": "Doe",
        "CLIENT_ID": "123456",
        "PHONE_EXTERNAL": "555-0123",
        "CUSTOMER_AGE": "35",
        "DATE_OF_BIRTH": "1988-01-15",
        "STATUS": "ACTIVE",
        "PRODUCT_NAME": "Credit Monitoring",
    }


@pytest.fixture
def sample_chat_request():
    """Sample chat completion request for API testing."""
    from main_enhanced import ChatCompletionRequest, ChatMessage

    return ChatCompletionRequest(
        model="gpt-4o-mini",
        messages=[ChatMessage(role="user", content="Find customer test.customer@example.com")],
        temperature=0.7,
        max_tokens=1000,
        stream=False,
    )


@pytest.fixture
def sample_chat_request_dict():
    """Sample chat completion request as dict for JSON API testing."""
    return {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Find customer test.customer@example.com"}],
        "temperature": 0.7,
        "max_tokens": 1000,
        "stream": False,
    }


@pytest.fixture
def sample_credit_data():
    """Sample credit report data for testing."""
    return {
        "STARTING_CREDIT_SCORE": "650",
        "CURRENT_CREDIT_SCORE": "720",
        "CREDIT_UTILIZATION": "25%",
        "PAYMENT_HISTORY": "Good",
        "CREDIT_AGE": "8 years",
        "HARD_INQUIRIES": "2",
        "DEROGATORY_MARKS": "0",
    }


# ============================================================================
# PERFORMANCE AND LOAD TESTING FIXTURES
# ============================================================================


@pytest.fixture
def performance_test_config():
    """Configuration for performance testing."""
    return {
        "concurrent_users": 10,
        "test_duration": 30,  # seconds
        "ramp_up_time": 5,  # seconds
        "target_response_time": 2.0,  # seconds
        "error_threshold": 0.05,  # 5% error rate threshold
    }


@pytest.fixture
def load_test_scenarios():
    """Load testing scenarios for different endpoints."""
    return {
        "chat_completions": {
            "endpoint": "/v1/chat/completions",
            "method": "POST",
            "payload": {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello"}], "stream": False},
        },
        "models_list": {"endpoint": "/v1/models", "method": "GET", "payload": None},
        "health_check": {"endpoint": "/health", "method": "GET", "payload": None},
    }


# ============================================================================
# UTILITY FIXTURES
# ============================================================================


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests to ensure isolation."""
    # Clear any cached instances or global state
    yield
    # Cleanup after test
    import importlib

    modules_to_reload = ["core_app", "redis_cache", "field_discovery_system"]
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])


@pytest.fixture
def mock_time():
    """Mock time module for testing time-dependent functionality."""
    with patch("time.time") as mock_time_func:
        mock_time_func.return_value = 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00
        yield mock_time_func


@pytest.fixture(autouse=True)
def mock_rate_limiter():
    """Mock rate limiter to prevent 429 errors during testing."""
    # Create a mock limiter that always allows requests
    mock_limiter = MagicMock()

    # Mock the limit decorator to return the function unchanged
    def mock_limit_decorator(*args, **kwargs):
        def decorator(func):
            return func  # Return the original function without rate limiting

        return decorator

    mock_limiter.limit = mock_limit_decorator

    # Also mock the limiter properties and methods
    mock_limiter.enabled = False
    mock_limiter.check = MagicMock(return_value=None)
    mock_limiter._check_request_limit = MagicMock(return_value=None)

    # Patch multiple places where the limiter might be used
    with patch("slowapi.Limiter", return_value=mock_limiter), patch("main_enhanced.limiter", mock_limiter), patch(
        "slowapi.util.get_remote_address", return_value="127.0.0.1"
    ):

        yield mock_limiter
