"""
Unit tests for Redis Cache Manager functionality.

Tests the RedisCacheManager class with both available and unavailable Redis,
ensuring graceful fallback behavior and proper cache operations.
"""

import json
import pytest
from unittest.mock import MagicMock, patch, call
from redis_cache import RedisCacheManager


class TestRedisCacheManagerInitialization:
    """Test Redis cache manager initialization and connection."""

    @pytest.mark.unit
    def test_redis_available_successful_connection(self, mock_redis_client):
        """Test successful Redis connection when Redis is available."""
        with patch("redis_cache.redis") as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis_client
            mock_redis_module.Redis.return_value = mock_redis_client

            cache_manager = RedisCacheManager()

            assert cache_manager.cache_available is True
            assert cache_manager.redis_client is mock_redis_client
            mock_redis_client.ping.assert_called_once()

    @pytest.mark.unit
    def test_redis_unavailable_graceful_fallback(self):
        """Test graceful fallback when Redis is unavailable."""
        with patch("redis_cache.redis") as mock_redis_module:
            mock_redis_module.from_url.side_effect = Exception("Redis unavailable")
            mock_redis_module.Redis.side_effect = Exception("Redis unavailable")

            cache_manager = RedisCacheManager()

            assert cache_manager.cache_available is False
            assert cache_manager.redis_client is None

    @pytest.mark.unit
    def test_redis_connection_failure_during_ping(self, mock_redis_client):
        """Test connection failure during ping operation."""
        mock_redis_client.ping.side_effect = Exception("Connection timeout")

        with patch("redis_cache.redis") as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis_client

            cache_manager = RedisCacheManager()

            assert cache_manager.cache_available is False
            assert cache_manager.redis_client is None

    @pytest.mark.unit
    def test_redis_url_configuration(self, mock_redis_client):
        """Test Redis connection with REDIS_URL environment variable."""
        with patch("redis_cache.redis") as mock_redis_module, patch("redis_cache.os.getenv") as mock_getenv:

            mock_getenv.return_value = "redis://test:6379/0"
            mock_redis_module.from_url.return_value = mock_redis_client

            cache_manager = RedisCacheManager()

            mock_redis_module.from_url.assert_called_once_with(
                "redis://test:6379/0", decode_responses=True, socket_connect_timeout=5, socket_timeout=5
            )

    @pytest.mark.unit
    def test_local_redis_configuration(self, mock_redis_client):
        """Test local Redis connection configuration."""
        with patch("redis_cache.redis") as mock_redis_module, patch("redis_cache.os.getenv") as mock_getenv:

            def getenv_side_effect(key, default=None):
                env_vars = {
                    "REDIS_URL": None,
                    "REDIS_HOST": "test-host",
                    "REDIS_PORT": "6380",
                    "REDIS_PASSWORD": "test-password",
                }
                return env_vars.get(key, default)

            mock_getenv.side_effect = getenv_side_effect
            mock_redis_module.Redis.return_value = mock_redis_client

            cache_manager = RedisCacheManager()

            mock_redis_module.Redis.assert_called_once_with(
                host="test-host",
                port=6380,
                password="test-password",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )


class TestRedisCacheKeyGeneration:
    """Test cache key generation and management."""

    @pytest.mark.unit
    def test_generate_cache_key_normal_identifier(self):
        """Test cache key generation with normal identifier."""
        cache_manager = RedisCacheManager()

        key = cache_manager._generate_cache_key("test", "identifier123")

        assert key == "tilores:test:identifier123"

    @pytest.mark.unit
    def test_generate_cache_key_long_identifier(self):
        """Test cache key generation with long identifier that gets hashed."""
        cache_manager = RedisCacheManager()
        long_identifier = "x" * 150  # Longer than 100 characters

        key = cache_manager._generate_cache_key("test", long_identifier)

        assert key.startswith("tilores:test:")
        assert len(key.split(":")[2]) == 32  # MD5 hash length
        assert key != f"tilores:test:{long_identifier}"

    @pytest.mark.unit
    def test_generate_cache_key_with_special_characters(self):
        """Test cache key generation with special characters."""
        cache_manager = RedisCacheManager()

        key = cache_manager._generate_cache_key("fields", "api@url:123")

        assert key == "tilores:fields:api@url:123"


class TestTiloresFieldsCaching:
    """Test Tilores fields caching functionality."""

    @pytest.mark.unit
    def test_get_tilores_fields_cache_hit(self, mock_cache_manager):
        """Test successful cache hit for Tilores fields."""
        test_fields = '{"EMAIL": true, "FIRST_NAME": true}'
        mock_cache_manager.redis_client.get.return_value = test_fields

        result = mock_cache_manager.get_tilores_fields("test_api_id")

        assert result == test_fields
        mock_cache_manager.redis_client.get.assert_called_once_with("tilores:fields:test_api_id")

    @pytest.mark.unit
    def test_get_tilores_fields_cache_miss(self, mock_cache_manager):
        """Test cache miss for Tilores fields."""
        mock_cache_manager.redis_client.get.return_value = None

        result = mock_cache_manager.get_tilores_fields("test_api_id")

        assert result is None

    @pytest.mark.unit
    def test_get_tilores_fields_redis_unavailable(self, mock_cache_manager_unavailable):
        """Test Tilores fields retrieval when Redis is unavailable."""
        result = mock_cache_manager_unavailable.get_tilores_fields("test_api_id")

        assert result is None

    @pytest.mark.unit
    def test_set_tilores_fields_successful(self, mock_cache_manager):
        """Test successful caching of Tilores fields."""
        test_fields = '{"EMAIL": true, "FIRST_NAME": true}'

        mock_cache_manager.set_tilores_fields("test_api_id", test_fields)

        mock_cache_manager.redis_client.setex.assert_called_once_with("tilores:fields:test_api_id", 3600, test_fields)

    @pytest.mark.unit
    def test_set_tilores_fields_redis_unavailable(self, mock_cache_manager_unavailable):
        """Test Tilores fields caching when Redis is unavailable."""
        test_fields = '{"EMAIL": true, "FIRST_NAME": true}'

        # Should not raise exception
        mock_cache_manager_unavailable.set_tilores_fields("test_api_id", test_fields)

    @pytest.mark.unit
    def test_set_tilores_fields_redis_error(self, mock_cache_manager):
        """Test handling Redis errors during field caching."""
        mock_cache_manager.redis_client.setex.side_effect = Exception("Redis error")

        # Should not raise exception
        mock_cache_manager.set_tilores_fields("test_api_id", "test_data")


class TestLLMResponseCaching:
    """Test LLM response caching functionality."""

    @pytest.mark.unit
    def test_get_llm_response_cache_hit(self, mock_cache_manager):
        """Test successful cache hit for LLM response."""
        test_response = "This is a cached LLM response"
        mock_cache_manager.redis_client.get.return_value = test_response

        result = mock_cache_manager.get_llm_response("test_hash_123")

        assert result == test_response
        mock_cache_manager.redis_client.get.assert_called_once_with("tilores:llm:test_hash_123")

    @pytest.mark.unit
    def test_set_llm_response_successful(self, mock_cache_manager):
        """Test successful caching of LLM response."""
        test_response = "This is an LLM response to cache"

        mock_cache_manager.set_llm_response("test_hash_123", test_response)

        mock_cache_manager.redis_client.setex.assert_called_once_with("tilores:llm:test_hash_123", 86400, test_response)

    @pytest.mark.unit
    def test_llm_response_24_hour_ttl(self, mock_cache_manager):
        """Test LLM response TTL is set to 24 hours."""
        mock_cache_manager.set_llm_response("test_hash", "response")

        # Check that TTL is set to 86400 seconds (24 hours)
        call_args = mock_cache_manager.redis_client.setex.call_args
        assert call_args[0][1] == 86400


class TestCustomerSearchCaching:
    """Test customer search result caching functionality."""

    @pytest.mark.unit
    def test_get_customer_search_cache_hit(self, mock_cache_manager):
        """Test successful cache hit for customer search."""
        test_data = {"customer": "data", "found": True}
        mock_cache_manager.redis_client.get.return_value = json.dumps(test_data)

        result = mock_cache_manager.get_customer_search("search_hash_123")

        assert result == test_data
        mock_cache_manager.redis_client.get.assert_called_once_with("tilores:search:search_hash_123")

    @pytest.mark.unit
    def test_set_customer_search_successful(self, mock_cache_manager):
        """Test successful caching of customer search results."""
        test_data = {"customer": "data", "found": True}

        mock_cache_manager.set_customer_search("search_hash_123", test_data)

        expected_json = json.dumps(test_data)
        mock_cache_manager.redis_client.setex.assert_called_once_with(
            "tilores:search:search_hash_123", 3600, expected_json
        )

    @pytest.mark.unit
    def test_customer_search_json_serialization_error(self, mock_cache_manager):
        """Test handling of JSON serialization errors in customer search."""
        mock_cache_manager.redis_client.get.return_value = "invalid json"

        result = mock_cache_manager.get_customer_search("search_hash")

        assert result is None

    @pytest.mark.unit
    def test_customer_search_1_hour_ttl(self, mock_cache_manager):
        """Test customer search TTL is set to 1 hour."""
        test_data = {"test": "data"}
        mock_cache_manager.set_customer_search("hash", test_data)

        # Check that TTL is set to 3600 seconds (1 hour)
        call_args = mock_cache_manager.redis_client.setex.call_args
        assert call_args[0][1] == 3600


class TestCreditReportCaching:
    """Test credit report caching functionality."""

    @pytest.mark.unit
    def test_get_credit_report_cache_hit(self, mock_cache_manager):
        """Test successful cache hit for credit report."""
        test_report = "Detailed credit report content"
        mock_cache_manager.redis_client.get.return_value = test_report

        result = mock_cache_manager.get_credit_report("customer_123")

        assert result == test_report
        mock_cache_manager.redis_client.get.assert_called_once_with("tilores:credit:customer_123")

    @pytest.mark.unit
    def test_set_credit_report_successful(self, mock_cache_manager):
        """Test successful caching of credit report."""
        test_report = "Detailed credit report content"

        mock_cache_manager.set_credit_report("customer_123", test_report)

        mock_cache_manager.redis_client.setex.assert_called_once_with("tilores:credit:customer_123", 3600, test_report)


class TestCacheUtilities:
    """Test cache utility functions."""

    @pytest.mark.unit
    def test_generate_query_hash_consistent(self):
        """Test query hash generation is consistent."""
        cache_manager = RedisCacheManager()

        hash1 = cache_manager.generate_query_hash("test query", "gpt-4", "context")
        hash2 = cache_manager.generate_query_hash("test query", "gpt-4", "context")

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hash length

    @pytest.mark.unit
    def test_generate_query_hash_different_inputs(self):
        """Test query hash generation produces different hashes for different inputs."""
        cache_manager = RedisCacheManager()

        hash1 = cache_manager.generate_query_hash("query1", "model1", "context1")
        hash2 = cache_manager.generate_query_hash("query2", "model2", "context2")

        assert hash1 != hash2

    @pytest.mark.unit
    def test_generate_search_hash_consistent(self):
        """Test search hash generation is consistent."""
        cache_manager = RedisCacheManager()
        params = {"EMAIL": "test@example.com", "CLIENT_ID": "123"}

        hash1 = cache_manager.generate_search_hash(params)
        hash2 = cache_manager.generate_search_hash(params)

        assert hash1 == hash2

    @pytest.mark.unit
    def test_generate_search_hash_order_independent(self):
        """Test search hash is independent of parameter order."""
        cache_manager = RedisCacheManager()

        params1 = {"EMAIL": "test@example.com", "CLIENT_ID": "123"}
        params2 = {"CLIENT_ID": "123", "EMAIL": "test@example.com"}

        hash1 = cache_manager.generate_search_hash(params1)
        hash2 = cache_manager.generate_search_hash(params2)

        assert hash1 == hash2


class TestCacheStatistics:
    """Test cache statistics and monitoring functionality."""

    @pytest.mark.unit
    def test_get_cache_stats_redis_available(self, mock_cache_manager):
        """Test cache statistics when Redis is available."""
        stats = mock_cache_manager.get_cache_stats()

        assert stats["status"] == "available"
        assert stats["cache_available"] is True
        assert stats["redis_connected"] is True
        assert "redis_info" in stats

    @pytest.mark.unit
    def test_get_cache_stats_redis_unavailable(self, mock_cache_manager_unavailable):
        """Test cache statistics when Redis is unavailable."""
        stats = mock_cache_manager_unavailable.get_cache_stats()

        assert stats["status"] == "unavailable"
        assert stats["cache_available"] is False
        assert stats["redis_connected"] is False

    @pytest.mark.unit
    def test_get_cache_stats_redis_error(self, mock_cache_manager):
        """Test cache statistics when Redis throws an error."""
        mock_cache_manager.redis_client = MagicMock()
        mock_cache_manager.redis_client.info.side_effect = Exception("Redis error")

        stats = mock_cache_manager.get_cache_stats()

        assert stats["status"] == "available"  # Still marked as available
        assert stats["cache_available"] is True


class TestCacheClear:
    """Test cache clearing functionality."""

    @pytest.mark.unit
    def test_clear_cache_all_entries(self, mock_cache_manager):
        """Test clearing all cache entries."""
        mock_cache_manager.redis_client.keys.return_value = [
            "tilores:fields:api1",
            "tilores:llm:hash1",
            "tilores:search:search1",
        ]

        count = mock_cache_manager.clear_cache()

        assert count == 3
        mock_cache_manager.redis_client.keys.assert_called_once_with("tilores:*")
        assert mock_cache_manager.redis_client.delete.call_count == 3

    @pytest.mark.unit
    def test_clear_cache_specific_pattern(self, mock_cache_manager):
        """Test clearing cache entries with specific pattern."""
        mock_cache_manager.redis_client.keys.return_value = ["tilores:fields:api1", "tilores:fields:api2"]

        count = mock_cache_manager.clear_cache("fields")

        assert count == 2
        mock_cache_manager.redis_client.keys.assert_called_once_with("tilores:fields:*")

    @pytest.mark.unit
    def test_clear_cache_redis_unavailable(self, mock_cache_manager_unavailable):
        """Test cache clearing when Redis is unavailable."""
        count = mock_cache_manager_unavailable.clear_cache()

        assert count == 0

    @pytest.mark.unit
    def test_clear_cache_no_keys_found(self, mock_cache_manager):
        """Test cache clearing when no keys match pattern."""
        mock_cache_manager.redis_client.keys.return_value = []

        count = mock_cache_manager.clear_cache("nonexistent")

        assert count == 0
        mock_cache_manager.redis_client.delete.assert_not_called()
