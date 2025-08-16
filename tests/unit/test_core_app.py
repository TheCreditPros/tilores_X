#!/usr/bin/env python3
"""
Unit tests for core_app.py - Unified LangChain core logic
Tests for QueryRouter, MultiProviderLLMEngine, and utility functions
"""

import pytest
import os
from unittest.mock import Mock, patch


@pytest.mark.unit
class TestQueryRouter:
    """Test cases for QueryRouter class"""

    def test_router_initialization(self):
        """Test QueryRouter initializes with correct patterns"""
        from core_app import QueryRouter

        router = QueryRouter()

        assert hasattr(router, "general_patterns")
        assert hasattr(router, "general_regex")
        assert len(router.general_patterns) > 0
        assert len(router.general_regex) == len(router.general_patterns)

    def test_should_use_tilores_tools_math_queries(self):
        """Test router correctly identifies math queries as general"""
        from core_app import QueryRouter

        router = QueryRouter()

        # Math queries should NOT use Tilores tools
        math_queries = [
            "2 + 2",
            "what is 5 * 3?",
            "calculate 15 / 3",
            "what is 10 minus 4?",
        ]

        for query in math_queries:
            assert router.should_use_tilores_tools(query) is False

    def test_should_use_tilores_tools_greetings(self):
        """Test router correctly identifies greetings as general"""
        from core_app import QueryRouter

        router = QueryRouter()

        # Greeting queries should NOT use Tilores tools
        greeting_queries = [
            "hi",
            "hello there",
            "thank you",
            "how are you?",
        ]

        for query in greeting_queries:
            assert router.should_use_tilores_tools(query) is False

    def test_should_use_tilores_tools_customer_queries(self):
        """Test router correctly identifies customer queries as needing tools"""
        from core_app import QueryRouter

        router = QueryRouter()

        # Customer queries should use Tilores tools
        customer_queries = [
            "find customer john.doe@example.com",
            "search for customer 1234567",
            "get customer information for John Smith",
            "show me customer details",
        ]

        for query in customer_queries:
            assert router.should_use_tilores_tools(query) is True

    def test_should_use_tilores_tools_edge_cases(self):
        """Test router handles edge cases appropriately"""
        from core_app import QueryRouter

        router = QueryRouter()

        # Edge cases - should default to using tools
        edge_cases = [
            "",  # Empty query
            "   ",  # Whitespace only
            "something completely random",
            "technical question about APIs",
        ]

        for query in edge_cases:
            # Default behavior is to give LLM access to tools
            assert router.should_use_tilores_tools(query) is True


@pytest.mark.unit
class TestGetAllTiloresFields:
    """Test cases for get_all_tilores_fields function"""

    def test_get_all_tilores_fields_with_cache_hit(self):
        """Test field discovery with cache hit"""
        from core_app import get_all_tilores_fields

        # Mock Tilores API
        mock_tilores_api = Mock()
        mock_tilores_api.api_url = "https://test.tilores.com"

        # Mock cache manager
        mock_cache_manager = Mock()
        cached_fields = '{"EMAIL": true, "FIRST_NAME": true, "LAST_NAME": true}'
        mock_cache_manager.get_tilores_fields.return_value = cached_fields

        with patch("core_app.CACHE_AVAILABLE", True), patch("core_app.cache_manager", mock_cache_manager):

            result = get_all_tilores_fields(mock_tilores_api)

            assert result == {"EMAIL": True, "FIRST_NAME": True, "LAST_NAME": True}
            mock_cache_manager.get_tilores_fields.assert_called_once()
            mock_tilores_api.gql.assert_not_called()

    def test_get_all_tilores_fields_cache_miss(self):
        """Test field discovery with cache miss"""
        from core_app import get_all_tilores_fields

        # Mock Tilores API
        mock_tilores_api = Mock()
        mock_tilores_api.api_url = "https://test.tilores.com"

        # Mock GraphQL response
        mock_schema_response = {
            "data": {
                "__schema": {
                    "types": [
                        {
                            "name": "Record",
                            "fields": [
                                {"name": "EMAIL"},
                                {"name": "FIRST_NAME"},
                                {"name": "LAST_NAME"},
                                {"name": "CREDIT_RESPONSE"},  # Should be excluded
                                {"name": "TRANSUNION_SUMMARY_LINK"},  # Should be excluded
                            ],
                        },
                        {
                            "name": "CreditResponseCreditLiability",
                            "fields": [
                                {"name": "ACCOUNT_TYPE"},
                                {"name": "BALANCE"},
                            ],
                        },
                    ]
                }
            }
        }

        mock_tilores_api.gql.return_value = mock_schema_response

        # Mock cache manager with cache miss
        mock_cache_manager = Mock()
        mock_cache_manager.get_tilores_fields.return_value = None

        with patch("core_app.CACHE_AVAILABLE", True), patch("core_app.cache_manager", mock_cache_manager):

            result = get_all_tilores_fields(mock_tilores_api)

            # Should include Record fields except excluded ones
            assert "EMAIL" in result
            assert "FIRST_NAME" in result
            assert "LAST_NAME" in result
            assert "ACCOUNT_TYPE" in result
            assert "BALANCE" in result

            # Should exclude complex fields
            assert "CREDIT_RESPONSE" not in result
            assert "TRANSUNION_SUMMARY_LINK" not in result

            mock_tilores_api.gql.assert_called_once()

    def test_get_all_tilores_fields_api_error(self):
        """Test field discovery handles API errors gracefully"""
        from core_app import get_all_tilores_fields

        # Mock Tilores API that raises exception
        mock_tilores_api = Mock()
        mock_tilores_api.gql.side_effect = Exception("API Error")

        with patch("core_app.CACHE_AVAILABLE", False):
            result = get_all_tilores_fields(mock_tilores_api)

            # Should return empty dict on error
            assert result == {}

    def test_get_all_tilores_fields_no_cache(self):
        """Test field discovery when cache is not available"""
        from core_app import get_all_tilores_fields

        # Mock Tilores API
        mock_tilores_api = Mock()
        mock_schema_response = {
            "data": {
                "__schema": {
                    "types": [
                        {
                            "name": "Record",
                            "fields": [
                                {"name": "EMAIL"},
                                {"name": "CLIENT_ID"},
                            ],
                        }
                    ]
                }
            }
        }
        mock_tilores_api.gql.return_value = mock_schema_response

        with patch("core_app.CACHE_AVAILABLE", False):
            result = get_all_tilores_fields(mock_tilores_api)

            assert "EMAIL" in result
            assert "CLIENT_ID" in result
            mock_tilores_api.gql.assert_called_once()


@pytest.mark.unit
class TestMultiProviderLLMEngine:
    """Test cases for MultiProviderLLMEngine class"""

    def test_engine_initialization_basic(self):
        """Test basic engine initialization without external dependencies"""
        from core_app import MultiProviderLLMEngine

        with patch("core_app.ANTHROPIC_AVAILABLE", False), patch("core_app.GEMINI_AVAILABLE", False), patch(
            "core_app.GROQ_AVAILABLE", False
        ), patch("core_app.OPENROUTER_AVAILABLE", False), patch.object(
            MultiProviderLLMEngine, "_init_langsmith"
        ), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            # Should have OpenAI models by default
            assert "gpt-4o" in engine.model_mappings
            assert "gpt-4o-mini" in engine.model_mappings
            # gpt-3.5-turbo has been deprecated, check for available models instead
            assert len(engine.model_mappings) > 0
            assert any("gpt" in model for model in engine.model_mappings.keys())

            # Should not have optional provider models
            assert "claude-3-sonnet" not in engine.model_mappings
            assert "gemini-1.5-flash-002" not in engine.model_mappings

    def test_engine_initialization_with_providers(self):
        """Test engine initialization with all providers available"""
        from core_app import MultiProviderLLMEngine

        with patch("core_app.ANTHROPIC_AVAILABLE", True), patch("core_app.GEMINI_AVAILABLE", True), patch(
            "core_app.GROQ_AVAILABLE", True
        ), patch("core_app.OPENROUTER_AVAILABLE", True), patch("core_app.ChatAnthropic", Mock()), patch(
            "core_app.ChatGoogleGenerativeAI", Mock()
        ), patch(
            "core_app.ChatGroq", Mock()
        ), patch(
            "core_app.OpenRouterChatOpenAI", Mock()
        ), patch.object(
            MultiProviderLLMEngine, "_init_langsmith"
        ), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            # Should have models from all providers
            assert "gpt-4o" in engine.model_mappings
            assert "claude-3-sonnet" in engine.model_mappings
            assert "gemini-1.5-flash-002" in engine.model_mappings
            assert "llama-3.3-70b-versatile" in engine.model_mappings

    @patch.dict(
        os.environ, {"LANGSMITH_TRACING": "true", "LANGSMITH_API_KEY": "test-key", "LANGSMITH_PROJECT": "test-project"}
    )
    def test_init_langsmith_enabled(self):
        """Test LangSmith initialization when enabled"""
        from core_app import MultiProviderLLMEngine

        mock_client = Mock()
        mock_tracer = Mock()

        with patch("core_app.LANGSMITH_AVAILABLE", True), patch(
            "core_app.LangSmithClient", return_value=mock_client
        ), patch("core_app.LangChainTracer", return_value=mock_tracer), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            assert engine.langsmith_client == mock_client
            assert engine.langchain_tracer == mock_tracer

    def test_init_langsmith_disabled(self):
        """Test LangSmith initialization when disabled"""
        from core_app import MultiProviderLLMEngine

        with patch("core_app.LANGSMITH_AVAILABLE", False), patch.object(MultiProviderLLMEngine, "_init_tilores"):

            engine = MultiProviderLLMEngine()

            assert engine.langsmith_client is None
            assert engine.langchain_tracer is None

    def test_init_tilores_success(self, mock_tilores_api, mock_tilores_tools):
        """Test successful Tilores initialization"""
        from core_app import MultiProviderLLMEngine

        # Create proper mock tools with required attributes
        mock_search_tool = Mock()
        mock_search_tool.name = "tilores_unified_search"
        mock_search_tool.__len__ = Mock(return_value=1)

        mock_edge_tool = Mock()
        mock_edge_tool.name = "tilores_edge_search"
        mock_edge_tool.__len__ = Mock(return_value=1)

        mock_record_tool = Mock()
        mock_record_tool.name = "tilores_record_lookup"
        mock_record_tool.__len__ = Mock(return_value=1)

        mock_credit_tool = Mock()
        mock_credit_tool.name = "tilores_credit_report"
        mock_credit_tool.__len__ = Mock(return_value=1)

        with patch.dict(
            os.environ,
            {
                "TILORES_API_URL": "https://test.tilores.com",
                "TILORES_CLIENT_ID": "test-client",
                "TILORES_CLIENT_SECRET": "test-secret",
                "TILORES_TOKEN_URL": "https://test.token.url",
            },
        ), patch("core_app.TiloresAPI") as mock_tilores_class, patch(
            "core_app.TiloresTools", return_value=mock_tilores_tools
        ), patch(
            "core_app.get_all_tilores_fields", return_value={"EMAIL": True}
        ), patch.object(
            MultiProviderLLMEngine, "_init_langsmith"
        ), patch.object(
            MultiProviderLLMEngine, "_create_unified_search_tool", return_value=mock_search_tool
        ), patch.object(
            MultiProviderLLMEngine, "_create_record_lookup_tool", return_value=mock_record_tool
        ), patch.object(
            MultiProviderLLMEngine, "_create_credit_report_tool", return_value=mock_credit_tool
        ):

            mock_tilores_class.from_environ.return_value = mock_tilores_api

            engine = MultiProviderLLMEngine()

            # Verify TiloresAPI.from_environ was called
            mock_tilores_class.from_environ.assert_called_once()
            assert len(engine.tools) == 4  # Should have 4 tools
            assert engine.all_fields == {"EMAIL": True}

    def test_init_tilores_missing_env_vars(self):
        """Test Tilores initialization with missing environment variables"""
        from core_app import MultiProviderLLMEngine

        # Mock environment to be completely empty for Tilores variables
        clean_env = {k: v for k, v in os.environ.items() if not k.startswith("TILORES_")}

        with patch.dict(os.environ, clean_env, clear=True), patch.object(
            MultiProviderLLMEngine, "_init_langsmith"
        ), patch("dotenv.load_dotenv"), patch("core_app.TiloresAPI") as mock_tilores_class:

            # Make TiloresAPI.from_environ return None to simulate missing vars
            mock_tilores_class.from_environ.return_value = None

            engine = MultiProviderLLMEngine()

            assert engine.tilores is None
            assert engine.tools == []

    def test_get_model_openai(self):
        """Test getting OpenAI model"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ), patch("core_app.ChatOpenAI") as mock_openai:

            engine = MultiProviderLLMEngine()
            mock_model = Mock()
            mock_openai.return_value = mock_model

            result = engine.get_model("gpt-4o")

            assert result == mock_model
            mock_openai.assert_called_once_with(model="gpt-4o")

    def test_get_model_nonexistent_fallback(self):
        """Test getting nonexistent model falls back to default"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ), patch("core_app.ChatGroq") as mock_groq:

            engine = MultiProviderLLMEngine()
            mock_model = Mock()
            mock_groq.return_value = mock_model

            result = engine.get_model("nonexistent-model")

            assert result == mock_model
            mock_groq.assert_called_once()

    def test_get_provider(self):
        """Test getting provider for a model"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            assert engine.get_provider("gpt-4o") == "openai"
            assert engine.get_provider("nonexistent-model") == "openai"  # Default

    def test_list_models(self):
        """Test listing available models"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()
            models = engine.list_models()

            assert isinstance(models, list)
            assert len(models) > 0

            # Check model structure
            for model in models:
                assert "id" in model
                assert "provider" in model

    def test_parse_query_string_email(self):
        """Test parsing query string for email"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            result = engine._parse_query_string("find user@example.com")
            assert result == {"EMAIL": "user@example.com"}

    def test_parse_query_string_client_id(self):
        """Test parsing query string for client ID"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            result = engine._parse_query_string("search client 1234567")
            assert result == {"CLIENT_ID": "1234567"}

    def test_parse_query_string_name(self):
        """Test parsing query string for name"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            result = engine._parse_query_string("find John Smith")
            assert result == {"FIRST_NAME": "John", "LAST_NAME": "Smith"}

    def test_parse_query_string_salesforce_id(self):
        """Test parsing query string for Salesforce ID"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            result = engine._parse_query_string("lookup 003Ux00000WCmXtIAL")
            assert result == {"SALESFORCE_ID": "003Ux00000WCmXtIAL"}

    def test_parse_query_string_fallback(self):
        """Test parsing query string fallback"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            result = engine._parse_query_string("random search query")
            # The flexible name pattern will match "Random Search" as FIRST_NAME/LAST_NAME
            assert result == {"FIRST_NAME": "Random", "LAST_NAME": "Search"}


@pytest.mark.unit
class TestEngineToolCreation:
    """Test cases for engine tool creation methods"""

    def test_create_unified_search_tool(self):
        """Test creation of unified search tool"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()
            engine.all_fields = {"EMAIL": True, "FIRST_NAME": True}

            mock_tilores_tools = Mock()
            mock_search_tool = Mock()
            mock_tilores_tools.search_tool.return_value = mock_search_tool

            tool = engine._create_unified_search_tool(mock_tilores_tools)

            assert hasattr(tool, "name")
            assert hasattr(tool, "invoke")

    def test_create_record_lookup_tool(self):
        """Test creation of record lookup tool"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()
            engine.tilores = Mock()

            tool = engine._create_record_lookup_tool()

            assert hasattr(tool, "name")
            assert hasattr(tool, "invoke")

    def test_create_credit_report_tool(self):
        """Test creation of credit report tool"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()
            engine.tilores = Mock()

            tool = engine._create_credit_report_tool()

            assert hasattr(tool, "name")
            assert hasattr(tool, "invoke")


@pytest.mark.unit
class TestEnvironmentLoading:
    """Test cases for environment loading functionality"""

    def test_load_environment_success(self):
        """Test successful environment loading"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()
            # Just test that method can be called without error
            engine._load_environment()

    def test_load_environment_no_dotenv(self):
        """Test environment loading when dotenv is not available"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ), patch("dotenv.load_dotenv", side_effect=ImportError("dotenv not available")):

            engine = MultiProviderLLMEngine()
            # Should not raise exception
            engine._load_environment()

    def test_load_environment_generic_error(self):
        """Test environment loading with generic error handling"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ), patch("pathlib.Path", side_effect=Exception("Path error")):

            engine = MultiProviderLLMEngine()
            # Should not raise exception even with Path errors
            engine._load_environment()


@pytest.mark.unit
class TestCreditAnalysisExtraction:
    """Test cases for credit analysis and extraction functionality"""

    def test_extract_credit_from_dict_success(self):
        """Test successful credit extraction from dict result"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            # Mock comprehensive result dict
            result_dict = {
                "data": {
                    "search": {
                        "entities": [
                            {
                                "records": [
                                    {
                                        "FIRST_NAME": "John",
                                        "LAST_NAME": "Doe",
                                        "EMAIL": "john.doe@example.com",
                                        "CLIENT_ID": "123456",
                                        "STARTING_CREDIT_SCORE": "720",
                                        "CREDIT_LIABILITY": "5000",
                                    }
                                ]
                            }
                        ]
                    }
                }
            }

            with patch.object(
                engine, "_format_comprehensive_credit_report", return_value="Credit Report"
            ) as mock_format:
                result = engine._extract_credit_from_dict(result_dict, {"EMAIL": "john.doe@example.com"})

                assert "Credit Report" in result
                mock_format.assert_called_once()

    def test_extract_credit_from_dict_no_entities(self):
        """Test credit extraction when no entities found"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            result_dict = {"data": {"search": {"entities": []}}}

            result = engine._extract_credit_from_dict(result_dict, {"EMAIL": "test@example.com"})

            assert "No customer data found" in result

    def test_extract_credit_information_success(self):
        """Test successful credit information extraction from string"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            result_str = """
            FIRST_NAME: John
            LAST_NAME: Doe
            EMAIL: john.doe@example.com
            STARTING_CREDIT_SCORE: 720
            CREDIT_RESPONSE: Available
            """

            with patch.object(
                engine, "_generate_credit_advisor_response", return_value="Credit Analysis"
            ) as mock_generate:
                result = engine._extract_credit_information(result_str, {"EMAIL": "john.doe@example.com"})

                assert "Credit Analysis" in result
                mock_generate.assert_called_once()

    def test_generate_credit_advisor_response_excellent_score(self):
        """Test credit advisor response for excellent credit score"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            result = engine._generate_credit_advisor_response(
                name="John",
                credit_score=780,
                has_credit_response=True,
                has_transunion_data=True,
                credit_indicators=["CREDIT_LIABILITY", "PAYMENT_HISTORY"],
                raw_data="Sample credit data",
            )

            assert "Excellent (750+)" in result
            assert "Very low risk borrower" in result
            assert "Current Credit Score:** 780" in result

    def test_generate_credit_advisor_response_poor_score(self):
        """Test credit advisor response for poor credit score"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            result = engine._generate_credit_advisor_response(
                name="Jane",
                credit_score=580,
                has_credit_response=False,
                has_transunion_data=False,
                credit_indicators=[],
                raw_data="Limited credit data",
            )

            assert "Very Poor (Below 600)" in result
            assert "Very high risk borrower" in result
            assert "Priority Actions:" in result

    def test_generate_credit_advisor_response_no_score(self):
        """Test credit advisor response when no credit score available"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            # Test with 0 score (very poor credit)
            result = engine._generate_credit_advisor_response(
                name="Unknown",
                credit_score=0,
                has_credit_response=False,
                has_transunion_data=False,
                credit_indicators=[],
                raw_data="",
            )

            # Check that the function handles zero score properly
            assert "Credit Score Status" in result
            assert "Not available in current data" in result or "Very Poor" in result

    def test_format_no_credit_data_report(self):
        """Test formatting report when no credit data available"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()

            customer_info = {"first_name": "John", "email": "john@example.com"}
            full_result = {"data": "sample"}

            with patch.object(
                engine, "_generate_credit_advisor_response", return_value="No Credit Report"
            ) as mock_generate:
                result = engine._format_no_credit_data_report(customer_info, full_result)

                assert "No Credit Report" in result
                mock_generate.assert_called_once()


@pytest.mark.unit
class TestToolExecution:
    """Test cases for tool execution functionality"""

    def test_unified_search_tool_execution(self):
        """Test execution of unified search tool"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()
            engine.all_fields = {"EMAIL": True}

            mock_tilores_tools = Mock()
            mock_search_tool = Mock()
            mock_search_tool.invoke.return_value = "Customer found"
            mock_tilores_tools.search_tool.return_value = mock_search_tool

            # Mock cache miss
            with patch("core_app.CACHE_AVAILABLE", False):
                tool = engine._create_unified_search_tool(mock_tilores_tools)
                result = tool.invoke("john.doe@example.com")

                assert "Customer found" in result

    def test_unified_search_tool_with_cache_hit(self):
        """Test unified search tool with cache hit"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()
            engine.all_fields = {"EMAIL": True}

            mock_tilores_tools = Mock()
            mock_cache_manager = Mock()
            mock_cache_manager.get_customer_search.return_value = "Cached customer data"

            with patch("core_app.CACHE_AVAILABLE", True), patch("core_app.cache_manager", mock_cache_manager):

                tool = engine._create_unified_search_tool(mock_tilores_tools)
                result = tool.invoke("john.doe@example.com")

                assert "Cached customer data" in result

    def test_record_lookup_tool_execution(self):
        """Test execution of record lookup tool"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()
            mock_tilores = Mock()

            # Mock successful GraphQL response
            mock_response = {
                "data": {
                    "entityByRecord": {
                        "entity": {
                            "records": [
                                {
                                    "id": "003Ux00000WCmXtIAL",
                                    "EMAIL": "john.doe@example.com",
                                    "FIRST_NAME": "John",
                                    "LAST_NAME": "Doe",
                                }
                            ]
                        }
                    }
                }
            }
            mock_tilores.gql.return_value = mock_response
            engine.tilores = mock_tilores

            tool = engine._create_record_lookup_tool()
            result = tool.invoke("003Ux00000WCmXtIAL")

            assert "john.doe@example.com" in result
            assert "John Doe" in result

    def test_credit_report_tool_execution(self):
        """Test execution of credit report tool"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()
            engine.tilores = Mock()

            mock_unified_search = Mock()
            mock_unified_search.invoke.return_value = "Customer credit data"

            with patch.object(engine, "_create_unified_search_tool", return_value=mock_unified_search), patch.object(
                engine, "_extract_credit_information", return_value="Credit Report"
            ):

                tool = engine._create_credit_report_tool()
                # Call tool with correct parameter structure
                result = tool.invoke({"email": "john.doe@example.com"})

                assert "Credit Report" in result


@pytest.mark.unit
class TestUtilityFunctions:
    """Test cases for utility functions"""

    def test_get_fastest_available_model_default(self):
        """Test getting fastest available model returns default"""
        from core_app import _get_fastest_available_model

        result = _get_fastest_available_model()
        assert result == "llama-3.3-70b-versatile"

    def test_get_fastest_available_model_with_engine(self):
        """Test getting fastest available model with engine"""
        from core_app import _get_fastest_available_model

        mock_engine = Mock()
        mock_engine.model_mappings = {
            "gpt-4o": {"provider": "openai"},
            "llama-3.3-70b-versatile": {"provider": "groq"},
        }

        with patch("core_app.engine", mock_engine):
            result = _get_fastest_available_model()
            assert result == "llama-3.3-70b-versatile"

    def test_initialize_engine(self):
        """Test engine initialization"""
        from core_app import initialize_engine

        with patch("core_app.engine", None), patch("core_app.MultiProviderLLMEngine") as mock_engine_class:

            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine

            initialize_engine()

            mock_engine_class.assert_called_once()

    def test_get_available_models(self):
        """Test getting available models"""
        from core_app import get_available_models

        mock_engine = Mock()
        mock_models = [{"id": "gpt-4o", "provider": "openai"}]
        mock_engine.list_models.return_value = mock_models

        with patch("core_app.engine", mock_engine):
            result = get_available_models()
            assert result == mock_models

    def test_get_model_provider(self):
        """Test getting model provider"""
        from core_app import get_model_provider

        mock_engine = Mock()
        mock_engine.get_provider.return_value = "openai"

        with patch("core_app.engine", mock_engine):
            result = get_model_provider("gpt-4o")
            assert result == "openai"


@pytest.mark.unit
class TestAdvancedModelHandling:
    """Test cases for advanced model handling functionality"""

    def test_get_model_anthropic(self):
        """Test getting Anthropic model"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ), patch("core_app.ANTHROPIC_AVAILABLE", True), patch("core_app.ChatAnthropic") as mock_anthropic:

            engine = MultiProviderLLMEngine()
            mock_model = Mock()
            mock_anthropic.return_value = mock_model

            result = engine.get_model("claude-3-sonnet")

            assert result == mock_model
            mock_anthropic.assert_called_once_with(model="claude-3-5-sonnet-20241022")

    def test_get_model_groq(self):
        """Test getting Groq model"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ), patch("core_app.GROQ_AVAILABLE", True), patch("core_app.ChatGroq") as mock_groq:

            engine = MultiProviderLLMEngine()
            mock_model = Mock()
            mock_groq.return_value = mock_model

            result = engine.get_model("llama-3.3-70b-versatile")

            assert result == mock_model
            mock_groq.assert_called_once_with(model="llama-3.3-70b-versatile")

    def test_get_model_openrouter(self):
        """Test getting OpenRouter model"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ), patch("core_app.OPENROUTER_AVAILABLE", True), patch(
            "core_app.OpenRouterChatOpenAI"
        ) as mock_openrouter, patch.dict(
            os.environ, {"OPENROUTER_API_KEY": "test-key"}
        ):

            engine = MultiProviderLLMEngine()
            mock_model = Mock()
            mock_openrouter.return_value = mock_model

            result = engine.get_model("llama-3.3-70b-versatile-openrouter")

            assert result == mock_model
            mock_openrouter.assert_called_once()

    def test_get_model_with_error_fallback(self):
        """Test model creation with error and fallback"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ), patch("core_app.ChatOpenAI", side_effect=Exception("Model error")), patch("core_app.ChatGroq") as mock_groq:

            engine = MultiProviderLLMEngine()
            mock_fallback = Mock()
            mock_groq.return_value = mock_fallback

            result = engine.get_model("gpt-4o")

            assert result == mock_fallback

    def test_get_llm_with_tools_debug_logging(self):
        """Test get_llm_with_tools with debug logging"""
        from core_app import MultiProviderLLMEngine

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()
            engine.tools = [Mock(), Mock()]

            mock_llm = Mock()
            mock_llm_with_tools = Mock()
            mock_llm.bind_tools.return_value = mock_llm_with_tools

            with patch.object(engine, "get_model", return_value=mock_llm), patch.object(
                engine, "get_provider", return_value="openai"
            ):

                result = engine.get_llm_with_tools("gpt-4o")

                assert result == mock_llm_with_tools
                mock_llm.bind_tools.assert_called_once_with(engine.tools)


@pytest.mark.unit
class TestTimeoutAndErrorHandling:
    """Test cases for timeout and error handling functionality"""

    def test_tilores_init_timeout_retry_logic(self):
        """Test Tilores initialization with timeout and retry logic"""
        from core_app import MultiProviderLLMEngine
        import concurrent.futures

        with patch.dict(
            os.environ,
            {
                "TILORES_API_URL": "https://test.tilores.com",
                "TILORES_CLIENT_ID": "test-client",
                "TILORES_CLIENT_SECRET": "test-secret",
                "TILORES_TOKEN_URL": "https://test.token.url",
            },
        ), patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch(
            "core_app.TiloresAPI"
        ) as mock_tilores_class, patch(
            "core_app.TiloresTools"
        ), patch(
            "core_app.get_all_tilores_fields", return_value={}
        ), patch(
            "time.sleep"
        ):  # Speed up test

            # First call times out, second succeeds
            mock_tilores_class.from_environ.side_effect = [
                concurrent.futures.TimeoutError("Timeout"),
                Mock(),  # Success on retry
            ]

            with patch("concurrent.futures.ThreadPoolExecutor") as mock_executor:
                mock_future = Mock()
                mock_future.result.side_effect = [
                    concurrent.futures.TimeoutError("Timeout"),
                    Mock(),  # Success on retry
                ]
                mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future

                engine = MultiProviderLLMEngine()

                # Should succeed after retry
                assert engine.tilores is not None

    def test_tilores_init_max_retries_exceeded(self):
        """Test Tilores initialization when max retries exceeded"""
        from core_app import MultiProviderLLMEngine
        import concurrent.futures

        with patch.dict(
            os.environ,
            {
                "TILORES_API_URL": "https://test.tilores.com",
                "TILORES_CLIENT_ID": "test-client",
                "TILORES_CLIENT_SECRET": "test-secret",
                "TILORES_TOKEN_URL": "https://test.token.url",
            },
        ), patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch(
            "time.sleep"
        ):  # Speed up test

            with patch("concurrent.futures.ThreadPoolExecutor") as mock_executor:
                mock_future = Mock()
                mock_future.result.side_effect = concurrent.futures.TimeoutError("Persistent timeout")
                mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future

                engine = MultiProviderLLMEngine()

                # Should fail and have no tools
                assert engine.tilores is None
                assert engine.tools == []

    def test_field_discovery_timeout_fallback(self):
        """Test field discovery timeout with fallback"""
        from core_app import MultiProviderLLMEngine
        import concurrent.futures

        with patch.dict(
            os.environ,
            {
                "TILORES_API_URL": "https://test.tilores.com",
                "TILORES_CLIENT_ID": "test-client",
                "TILORES_CLIENT_SECRET": "test-secret",
                "TILORES_TOKEN_URL": "https://test.token.url",
            },
        ), patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch(
            "core_app.TiloresAPI"
        ) as mock_tilores_class, patch(
            "core_app.TiloresTools"
        ):

            mock_tilores_class.from_environ.return_value = Mock()

            with patch("concurrent.futures.ThreadPoolExecutor") as mock_executor:
                # Main init succeeds, field discovery times out
                mock_future_init = Mock()
                mock_future_init.result.return_value = Mock()

                mock_future_fields = Mock()
                mock_future_fields.result.side_effect = concurrent.futures.TimeoutError("Field discovery timeout")

                mock_executor.return_value.__enter__.return_value.submit.side_effect = [
                    mock_future_init,  # TiloresAPI init
                    mock_future_fields,  # Field discovery
                ]

                engine = MultiProviderLLMEngine()

                # Should use fallback essential fields
                assert "EMAIL" in engine.all_fields
                assert "FIRST_NAME" in engine.all_fields
                assert len(engine.all_fields) >= 9  # Essential fields count

    def test_search_tool_timeout_handling(self):
        """Test search tool timeout handling with fallback"""
        from core_app import MultiProviderLLMEngine
        import concurrent.futures

        with patch.object(MultiProviderLLMEngine, "_init_langsmith"), patch.object(
            MultiProviderLLMEngine, "_init_tilores"
        ):

            engine = MultiProviderLLMEngine()
            engine.all_fields = {"EMAIL": True, "FIRST_NAME": True}

            mock_tilores_tools = Mock()
            mock_search_tool = Mock()

            # Mock timeout on comprehensive search, fallback to essential
            def search_side_effect(params):
                if len(params.get("recordFieldsToQuery", {})) > 50:
                    raise concurrent.futures.TimeoutError("Search timeout")
                return "Customer found with essential fields"

            mock_search_tool.invoke.side_effect = search_side_effect
            mock_tilores_tools.search_tool.return_value = mock_search_tool

            with patch("core_app.CACHE_AVAILABLE", False), patch(
                "concurrent.futures.ThreadPoolExecutor"
            ) as mock_executor:

                mock_future = Mock()
                mock_future.result.side_effect = concurrent.futures.TimeoutError("Timeout")
                mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future

                tool = engine._create_unified_search_tool(mock_tilores_tools)
                result = tool.invoke("john.doe@example.com")

                # Should fallback to essential fields and succeed
                assert "Customer found" in result or "Error searching" in result


@pytest.mark.unit
class TestRunChain:
    """Test cases for run_chain function"""

    def test_run_chain_general_query(self):
        """Test run_chain with general query (no tools needed)"""
        from core_app import run_chain

        mock_engine = Mock()
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Math answer: 4"

        # Add length support to mock objects
        mock_llm.__len__ = Mock(return_value=1)
        mock_engine.get_model.return_value = mock_llm
        mock_llm.invoke.return_value = mock_response

        # Configure tools with length support for general compatibility
        mock_tools_list = Mock()
        mock_tools_list.__len__ = Mock(return_value=0)
        mock_tools_list.__iter__ = Mock(return_value=iter([]))
        mock_engine.tools = mock_tools_list

        with patch("core_app.initialize_engine"), patch("core_app.engine", mock_engine), patch(
            "core_app.query_router"
        ) as mock_router, patch("core_app.CACHE_AVAILABLE", False):

            mock_router.should_use_tilores_tools.return_value = False

            result = run_chain("2 + 2", model="gpt-4o")

            assert result == "Math answer: 4"
            mock_engine.get_model.assert_called_once_with("gpt-4o")
            mock_llm.invoke.assert_called_once()

    def test_run_chain_customer_query_with_tools(self):
        """Test run_chain with customer query requiring tools"""
        from core_app import run_chain

        mock_engine = Mock()
        mock_llm = Mock()
        mock_llm_with_tools = Mock()
        mock_response = Mock()
        mock_response.content = "Customer found: John Doe"
        mock_response.tool_calls = []  # No tool calls in response

        # Add length support to all mock objects
        mock_llm.__len__ = Mock(return_value=1)
        mock_llm_with_tools.__len__ = Mock(return_value=1)
        mock_response.__len__ = Mock(return_value=1)

        # Create properly configured mock tools
        mock_tool = Mock()
        mock_tool.name = "tilores_search"
        mock_tool.__len__ = Mock(return_value=1)
        mock_tool.invoke.return_value = "Customer found: John Doe via tool"

        mock_engine.get_model.return_value = mock_llm
        mock_engine.get_llm_with_tools.return_value = mock_llm_with_tools
        # Use a simple list that can be iterated properly for tool lookup
        mock_engine.tools = [mock_tool]
        mock_engine.all_fields = {"EMAIL": True}
        mock_engine.get_provider.return_value = "openai"
        mock_llm_with_tools.invoke.return_value = mock_response

        with patch("core_app.initialize_engine"), patch("core_app.engine", mock_engine), patch(
            "core_app.query_router"
        ) as mock_router:

            mock_router.should_use_tilores_tools.return_value = True

            result = run_chain("find user@example.com", model="gpt-4o")

            result_str = str(result)
            assert "Customer found: John Doe" in result_str
            mock_engine.get_llm_with_tools.assert_called_once()

    def test_run_chain_no_tools_available(self):
        """Test run_chain when no tools are available"""
        from core_app import run_chain

        mock_engine = Mock()
        mock_engine.tools = []  # No tools available

        with patch("core_app.initialize_engine"), patch("core_app.engine", mock_engine), patch(
            "core_app.query_router"
        ) as mock_router:

            mock_router.should_use_tilores_tools.return_value = True

            result = run_chain("find customer", model="gpt-4o")

            result_str = str(result)
            assert "Tilores tools not available" in result_str

    def test_run_chain_streaming(self):
        """Test run_chain with streaming enabled"""
        from core_app import run_chain

        mock_engine = Mock()
        mock_llm = Mock()
        mock_stream = Mock()

        # Add length support to all mock objects
        mock_engine.__len__ = Mock(return_value=1)
        mock_llm.__len__ = Mock(return_value=1)
        mock_stream.__len__ = Mock(return_value=1)

        mock_engine.get_model.return_value = mock_llm
        mock_llm.stream.return_value = mock_stream

        # Configure tools with length support
        mock_tools_list = Mock()
        mock_tools_list.__len__ = Mock(return_value=0)
        mock_tools_list.__iter__ = Mock(return_value=iter([]))
        mock_engine.tools = mock_tools_list

        with patch("core_app.initialize_engine"), patch("core_app.engine", mock_engine), patch(
            "core_app.query_router"
        ) as mock_router, patch("core_app.CACHE_AVAILABLE", False):

            mock_router.should_use_tilores_tools.return_value = False

            result = run_chain("hello", model="gpt-4o", stream=True)

            assert result == mock_stream
            mock_llm.stream.assert_called_once()

    def test_run_chain_conversation_history(self):
        """Test run_chain with conversation history"""
        from core_app import run_chain

        mock_engine = Mock()
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Response with context"

        # Add length support to all mock objects
        mock_engine.__len__ = Mock(return_value=1)
        mock_llm.__len__ = Mock(return_value=1)
        mock_response.__len__ = Mock(return_value=1)

        mock_engine.get_model.return_value = mock_llm
        mock_llm.invoke.return_value = mock_response

        # Configure tools with length support
        mock_tools_list = Mock()
        mock_tools_list.__len__ = Mock(return_value=0)
        mock_tools_list.__iter__ = Mock(return_value=iter([]))
        mock_engine.tools = mock_tools_list

        conversation = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "What's 2+2?"},
        ]

        with patch("core_app.initialize_engine"), patch("core_app.engine", mock_engine), patch(
            "core_app.query_router"
        ) as mock_router, patch("core_app.CACHE_AVAILABLE", False):

            mock_router.should_use_tilores_tools.return_value = False

            result = run_chain(conversation, model="gpt-4o")

            assert result == "Response with context"
            # Verify LLM was called with conversation context
            mock_llm.invoke.assert_called_once()
            call_args = mock_llm.invoke.call_args[0][0]
            assert len(call_args) == 4  # system + 2 history + current

    def test_run_chain_error_handling(self):
        """Test run_chain error handling"""
        from core_app import run_chain

        mock_engine = Mock()
        mock_engine.get_model.side_effect = Exception("Model error")

        # Add length support to mock engine
        mock_engine.__len__ = Mock(return_value=1)

        # Configure tools with length support
        mock_tools_list = Mock()
        mock_tools_list.__len__ = Mock(return_value=0)
        mock_tools_list.__iter__ = Mock(return_value=iter([]))
        mock_engine.tools = mock_tools_list

        with patch("core_app.initialize_engine"), patch("core_app.engine", mock_engine), patch(
            "core_app.query_router"
        ) as mock_router:

            mock_router.should_use_tilores_tools.return_value = False

            result = run_chain("test query", model="gpt-4o")

            result_str = str(result)
            assert "I encountered an error" in result_str
            assert "Model error" in result_str
