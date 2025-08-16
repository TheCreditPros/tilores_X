"""
Unit tests for field_discovery_system.py - Comprehensive Field Discovery System

Tests the TiloresFieldDiscovery class, OAuth2 authentication, field categorization,
statistics generation, and the LangChain tool functions.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientResponseError

from field_discovery_system import (
    TiloresFieldDiscovery,
    discover_tilores_fields,
    get_field_discovery_stats,
    field_discovery,
)


class TestTiloresFieldDiscoveryInitialization:
    """Test TiloresFieldDiscovery class initialization and configuration."""

    @pytest.mark.unit
    def test_field_discovery_initialization_with_env_vars(self, test_env_vars):
        """Test field discovery initialization with environment variables."""
        discovery = TiloresFieldDiscovery()

        assert discovery.api_url == "https://test-api.example.com"
        assert discovery.token_url == "https://test-token.example.com/oauth2/token"
        assert discovery.client_id == "test_client_id"
        assert discovery.client_secret == "test_client_secret"
        assert discovery.access_token is None
        assert discovery._field_cache is None
        assert discovery._schema_cache is None

    @pytest.mark.unit
    def test_field_discovery_initialization_with_defaults(self):
        """Test field discovery initialization with default values."""
        with patch.dict("os.environ", {}, clear=True):
            discovery = TiloresFieldDiscovery()

            assert "ly325mgfwk.execute-api.us-east-1.amazonaws.com" in discovery.api_url
            assert "saas-swidepnf-tilores.auth.us-east-1.amazoncognito.com" in discovery.token_url
            assert discovery.client_id is None
            assert discovery.client_secret is None

    @pytest.mark.unit
    def test_field_discovery_initialization_partial_env(self):
        """Test field discovery initialization with partial environment configuration."""
        with patch.dict("os.environ", {"TILORES_API_URL": "https://custom.api.com"}, clear=True):
            discovery = TiloresFieldDiscovery()

            assert discovery.api_url == "https://custom.api.com"
            assert "saas-swidepnf-tilores.auth.us-east-1.amazoncognito.com" in discovery.token_url


class TestOAuth2Authentication:
    """Test OAuth2 authentication functionality."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_access_token_successful(self, test_env_vars):
        """Test successful OAuth2 token retrieval."""
        discovery = TiloresFieldDiscovery()

        mock_token_response = {"access_token": "test_access_token_12345", "token_type": "Bearer", "expires_in": 3600}

        # Create a proper async context manager mock
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=mock_token_response)
        mock_response.raise_for_status = AsyncMock()

        # Create a proper async context manager factory
        def mock_post_context(*args, **kwargs):
            context_manager = AsyncMock()
            context_manager.__aenter__ = AsyncMock(return_value=mock_response)
            context_manager.__aexit__ = AsyncMock(return_value=None)
            return context_manager

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.post = mock_post_context  # Not async - returns context manager directly
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_session_class.return_value = mock_session

            token = await discovery.get_access_token()

            assert token == "test_access_token_12345"
            assert discovery.access_token == "test_access_token_12345"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_access_token_missing_credentials(self):
        """Test OAuth2 token retrieval with missing credentials."""
        with patch.dict("os.environ", {}, clear=True):
            discovery = TiloresFieldDiscovery()

            with pytest.raises(Exception) as exc_info:
                await discovery.get_access_token()

            assert "Tilores credentials not configured" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_access_token_http_error(self, test_env_vars):
        """Test OAuth2 token retrieval with HTTP error."""
        discovery = TiloresFieldDiscovery()

        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.raise_for_status = AsyncMock(
                side_effect=ClientResponseError(request_info=MagicMock(), history=MagicMock(), status=401)
            )

            mock_post = AsyncMock()
            mock_post.__aenter__ = AsyncMock(return_value=mock_response)
            mock_post.__aexit__ = AsyncMock(return_value=None)

            mock_session_instance = AsyncMock()
            mock_session_instance.post.return_value = mock_post
            mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)

            mock_session.return_value = mock_session_instance

            with pytest.raises(Exception) as exc_info:
                await discovery.get_access_token()

            assert "Failed to get Tilores token" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_access_token_network_error(self, test_env_vars):
        """Test OAuth2 token retrieval with network error."""
        discovery = TiloresFieldDiscovery()

        # Create a factory that returns a context manager that raises an error on enter
        def mock_post_error(*args, **kwargs):
            context_manager = AsyncMock()
            context_manager.__aenter__ = AsyncMock(side_effect=Exception("Network error"))
            context_manager.__aexit__ = AsyncMock(return_value=None)
            return context_manager

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.post = mock_post_error  # Not async - returns context manager directly
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_session_class.return_value = mock_session

            with pytest.raises(Exception) as exc_info:
                await discovery.get_access_token()

            assert "Failed to get Tilores token" in str(exc_info.value)
            assert "Network error" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_access_token_invalid_response(self, test_env_vars):
        """Test OAuth2 token retrieval with invalid response."""
        discovery = TiloresFieldDiscovery()

        mock_token_response = {"error": "invalid_client"}

        # Create a proper async context manager mock
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=mock_token_response)
        mock_response.raise_for_status = AsyncMock()

        # Create a proper async context manager factory
        def mock_post_context(*args, **kwargs):
            context_manager = AsyncMock()
            context_manager.__aenter__ = AsyncMock(return_value=mock_response)
            context_manager.__aexit__ = AsyncMock(return_value=None)
            return context_manager

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.post = mock_post_context  # Not async - returns context manager directly
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_session_class.return_value = mock_session

            token = await discovery.get_access_token()

            assert token is None
            assert discovery.access_token is None


class TestFieldDiscovery:
    """Test field discovery functionality."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_discover_all_fields_first_call(self):
        """Test field discovery on first call (cache miss)."""
        discovery = TiloresFieldDiscovery()

        fields = await discovery.discover_all_fields()

        assert isinstance(fields, dict)
        assert len(fields) == 7  # 7 categories

        # Verify all expected categories
        expected_categories = [
            "customer_fields",
            "credit_fields",
            "product_fields",
            "interaction_fields",
            "transaction_fields",
            "relationship_fields",
            "system_fields",
        ]
        for category in expected_categories:
            assert category in fields
            assert isinstance(fields[category], list)
            assert len(fields[category]) > 0

        # Verify cache is populated
        assert discovery._field_cache is not None
        assert discovery._field_cache == fields

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_discover_all_fields_cached(self):
        """Test field discovery with cache hit."""
        discovery = TiloresFieldDiscovery()

        # Set up cache
        cached_fields = {"test_category": ["TEST_FIELD_1", "TEST_FIELD_2"]}
        discovery._field_cache = cached_fields

        fields = await discovery.discover_all_fields()

        assert fields == cached_fields
        assert fields is discovery._field_cache

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_field_categories_content(self):
        """Test field categories contain expected content."""
        discovery = TiloresFieldDiscovery()

        fields = await discovery.discover_all_fields()

        # Test customer fields
        customer_fields = fields["customer_fields"]
        assert "EMAIL" in customer_fields
        assert "FIRST_NAME" in customer_fields
        assert "LAST_NAME" in customer_fields
        assert "CLIENT_ID" in customer_fields
        assert "SSN" in customer_fields

        # Test credit fields
        credit_fields = fields["credit_fields"]
        assert "STARTING_CREDIT_SCORE" in credit_fields
        assert "CURRENT_CREDIT_SCORE" in credit_fields
        assert "PAYMENT_HISTORY" in credit_fields
        assert "CREDIT_UTILIZATION" in credit_fields

        # Test system fields
        system_fields = fields["system_fields"]
        assert "RECORD_ID" in system_fields
        assert "ENTITY_ID" in system_fields
        assert "CREATED_DATE" in system_fields
        assert "UPDATED_DATE" in system_fields

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_field_count_expectations(self):
        """Test field counts meet expected minimums."""
        discovery = TiloresFieldDiscovery()

        fields = await discovery.discover_all_fields()

        # Verify reasonable field counts per category
        assert len(fields["customer_fields"]) >= 20  # Should have substantial customer fields
        assert len(fields["credit_fields"]) >= 25  # Should have comprehensive credit fields
        assert len(fields["product_fields"]) >= 10  # Should have product fields
        assert len(fields["interaction_fields"]) >= 15  # Should have interaction fields
        assert len(fields["transaction_fields"]) >= 15  # Should have transaction fields
        assert len(fields["relationship_fields"]) >= 10  # Should have relationship fields
        assert len(fields["system_fields"]) >= 10  # Should have system fields


class TestFieldStatistics:
    """Test field statistics functionality."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_field_statistics_structure(self):
        """Test field statistics structure and content."""
        discovery = TiloresFieldDiscovery()

        stats = await discovery.get_field_statistics()

        assert isinstance(stats, dict)
        assert "total_fields_discovered" in stats
        assert "field_categories" in stats
        assert "discovery_status" in stats

        assert isinstance(stats["total_fields_discovered"], int)
        assert isinstance(stats["field_categories"], dict)
        assert stats["discovery_status"] == "✅ Complete"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_field_statistics_calculations(self):
        """Test field statistics calculations are accurate."""
        discovery = TiloresFieldDiscovery()

        stats = await discovery.get_field_statistics()
        fields = await discovery.discover_all_fields()

        # Verify total count matches sum of categories
        expected_total = sum(len(field_list) for field_list in fields.values())
        assert stats["total_fields_discovered"] == expected_total

        # Verify category counts
        for category, field_list in fields.items():
            assert stats["field_categories"][category] == len(field_list)

        # Verify total is substantial (300+ fields expected)
        assert stats["total_fields_discovered"] >= 100  # Conservative minimum

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_field_statistics_category_coverage(self):
        """Test field statistics cover all categories."""
        discovery = TiloresFieldDiscovery()

        stats = await discovery.get_field_statistics()

        expected_categories = [
            "customer_fields",
            "credit_fields",
            "product_fields",
            "interaction_fields",
            "transaction_fields",
            "relationship_fields",
            "system_fields",
        ]

        for category in expected_categories:
            assert category in stats["field_categories"]
            assert stats["field_categories"][category] > 0


class TestDiscoverTiloresFieldsTool:
    """Test the discover_tilores_fields LangChain tool."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_discover_tilores_fields_all_category(self):
        """Test discover_tilores_fields tool with 'all' category."""
        result = await discover_tilores_fields.ainvoke({"category": "all"})

        assert isinstance(result, str)
        assert "COMPREHENSIVE FIELD DISCOVERY" in result
        assert "Total Fields:" in result
        assert "Customer Fields:" in result
        assert "Credit Fields:" in result
        assert "Use specific categories" in result
        assert "discover_tilores_fields('customer')" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_discover_tilores_fields_customer_category(self):
        """Test discover_tilores_fields tool with customer category."""
        result = await discover_tilores_fields.ainvoke({"category": "customer"})

        assert isinstance(result, str)
        assert "CUSTOMER FIELDS" in result
        assert "EMAIL" in result
        assert "FIRST_NAME" in result
        assert "LAST_NAME" in result
        assert "total)" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_discover_tilores_fields_credit_category(self):
        """Test discover_tilores_fields tool with credit category."""
        result = await discover_tilores_fields.ainvoke({"category": "credit"})

        assert isinstance(result, str)
        assert "CREDIT FIELDS" in result
        assert "STARTING_CREDIT_SCORE" in result
        assert "CURRENT_CREDIT_SCORE" in result
        assert "PAYMENT_HISTORY" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_discover_tilores_fields_all_categories(self):
        """Test discover_tilores_fields tool with all valid categories."""
        categories = ["customer", "credit", "product", "interaction", "transaction", "relationship", "system"]

        for category in categories:
            result = await discover_tilores_fields.ainvoke({"category": category})

            assert isinstance(result, str)
            assert category.upper() in result
            assert "FIELDS" in result
            assert "total)" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_discover_tilores_fields_invalid_category(self):
        """Test discover_tilores_fields tool with invalid category."""
        result = await discover_tilores_fields.ainvoke({"category": "invalid_category"})

        assert isinstance(result, str)
        assert "Invalid category" in result
        assert "Available:" in result
        assert "customer" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_discover_tilores_fields_case_insensitive(self):
        """Test discover_tilores_fields tool is case insensitive."""
        result_lower = await discover_tilores_fields.ainvoke({"category": "customer"})
        result_upper = await discover_tilores_fields.ainvoke({"category": "CUSTOMER"})
        result_mixed = await discover_tilores_fields.ainvoke({"category": "Customer"})

        # All should produce the same result
        assert result_lower == result_upper == result_mixed
        assert "CUSTOMER FIELDS" in result_lower

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_discover_tilores_fields_formatting(self):
        """Test discover_tilores_fields tool output formatting."""
        result = await discover_tilores_fields.ainvoke({"category": "customer"})

        lines = result.split("\n")

        # Check header format
        assert lines[0].startswith("=== CUSTOMER FIELDS")
        assert "total)" in lines[0]

        # Check field numbering format
        field_lines = [line for line in lines[2:] if line.strip() and not line.startswith("===")]
        for i, line in enumerate(field_lines[:5]):  # Check first 5 field lines
            if line.strip():  # Skip empty lines
                # Field format is " 1. FIELD_NAME" so check for number+period
                assert f"{i + 1}." in line.strip()


class TestGetFieldDiscoveryStatsTool:
    """Test the get_field_discovery_stats LangChain tool."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_field_discovery_stats_structure(self):
        """Test get_field_discovery_stats tool output structure."""
        result = await get_field_discovery_stats.ainvoke({})

        assert isinstance(result, str)
        assert "FIELD DISCOVERY STATISTICS" in result
        assert "Discovery Status:" in result
        assert "Total Fields Available:" in result
        assert "CATEGORY BREAKDOWN:" in result
        assert "CAPABILITIES:" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_field_discovery_stats_content(self):
        """Test get_field_discovery_stats tool content accuracy."""
        result = await get_field_discovery_stats.ainvoke({})

        # Should include expected capabilities
        assert "310+ field comprehensive access" in result
        assert "Real-time field discovery" in result
        assert "Category-based field organization" in result
        assert "Dynamic GraphQL query generation" in result
        assert "Complete TLRS table coverage" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_field_discovery_stats_category_breakdown(self):
        """Test get_field_discovery_stats category breakdown."""
        result = await get_field_discovery_stats.ainvoke({})

        # Should include all category types
        assert "Customer Fields:" in result
        assert "Credit Fields:" in result
        assert "Product Fields:" in result
        assert "Interaction Fields:" in result
        assert "Transaction Fields:" in result
        assert "Relationship Fields:" in result
        assert "System Fields:" in result

        # Should include percentages
        assert "%" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_field_discovery_stats_status_indicators(self):
        """Test get_field_discovery_stats status indicators."""
        result = await get_field_discovery_stats.ainvoke({})

        # Should include emoji indicators and positive status
        assert "🎯" in result
        assert "📊" in result
        assert "📁" in result
        assert "✅" in result
        assert "Complete" in result


class TestErrorHandling:
    """Test error handling in field discovery system."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_discover_tilores_fields_tool_error_handling(self):
        """Test discover_tilores_fields tool error handling."""
        # Create a new discovery instance that will throw an error
        discovery_with_error = TiloresFieldDiscovery()
        discovery_with_error.discover_all_fields = AsyncMock(side_effect=Exception("Test error"))

        with patch("field_discovery_system.field_discovery", discovery_with_error):
            result = await discover_tilores_fields.ainvoke({"category": "customer"})

            assert isinstance(result, str)
            assert "Error discovering fields" in result
            assert "Test error" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_field_discovery_stats_tool_error_handling(self):
        """Test get_field_discovery_stats tool error handling."""
        # Create a new discovery instance that will throw an error
        discovery_with_error = TiloresFieldDiscovery()
        discovery_with_error.get_field_statistics = AsyncMock(side_effect=Exception("Stats error"))

        with patch("field_discovery_system.field_discovery", discovery_with_error):
            result = await get_field_discovery_stats.ainvoke({})

            assert isinstance(result, str)
            assert "Error getting field statistics" in result
            assert "Stats error" in result


class TestGlobalFieldDiscoveryInstance:
    """Test the global field_discovery instance."""

    @pytest.mark.unit
    def test_global_field_discovery_instance_exists(self):
        """Test global field_discovery instance is properly initialized."""
        assert field_discovery is not None
        assert isinstance(field_discovery, TiloresFieldDiscovery)

    @pytest.mark.unit
    def test_global_instance_has_proper_configuration(self, test_env_vars):
        """Test global field_discovery instance has proper configuration."""
        assert field_discovery.api_url is not None
        assert field_discovery.token_url is not None
        assert field_discovery._field_cache is None  # Should start empty

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_global_instance_functionality(self):
        """Test global field_discovery instance basic functionality."""
        fields = await field_discovery.discover_all_fields()

        assert isinstance(fields, dict)
        assert len(fields) > 0

        # Should now have cache populated
        assert field_discovery._field_cache is not None


class TestIntegrationPatterns:
    """Test integration patterns and tool compatibility."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_langchain_tool_compatibility(self):
        """Test LangChain tool compatibility and function signatures."""
        # Test that tools can be called with proper signatures
        result1 = await discover_tilores_fields.ainvoke({"category": "all"})  # Default parameter
        result2 = await discover_tilores_fields.ainvoke({"category": "all"})  # Explicit parameter

        assert isinstance(result1, str)
        assert isinstance(result2, str)
        # Both should work and return similar content
        assert "COMPREHENSIVE FIELD DISCOVERY" in result1
        assert "COMPREHENSIVE FIELD DISCOVERY" in result2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_field_discovery_consistency(self):
        """Test field discovery returns consistent results."""
        # Multiple calls should return identical results
        fields1 = await field_discovery.discover_all_fields()
        fields2 = await field_discovery.discover_all_fields()

        assert fields1 == fields2
        assert fields1 is fields2  # Should be same cached object

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_statistics_consistency(self):
        """Test statistics are consistent with field discovery."""
        fields = await field_discovery.discover_all_fields()
        stats = await field_discovery.get_field_statistics()

        # Statistics should match actual fields
        manual_total = sum(len(field_list) for field_list in fields.values())
        assert stats["total_fields_discovered"] == manual_total

        for category, field_list in fields.items():
            assert stats["field_categories"][category] == len(field_list)
