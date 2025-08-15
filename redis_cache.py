"""
Redis Cache Manager for Tilores Unified API.

Provides intelligent caching for customer data, field discovery,
LLM responses, and credit reports with graceful fallback.
"""
import hashlib
import json
import os
from typing import Any, Dict, Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisCacheManager:
    """
    Redis cache manager with intelligent TTL management.

    Gracefully degrades when Redis is unavailable, ensuring system
    continues to work without caching infrastructure.
    """

    def __init__(self):
        """Initialize Redis connection with graceful fallback."""
        self.redis_client: Any = None
        self.cache_available = False

        if REDIS_AVAILABLE:
            self._connect_to_redis()

    def _connect_to_redis(self):
        """Connect to Redis with Railway and local environment support."""
        try:
            # Railway Redis URL (production)
            redis_url = os.getenv('REDIS_URL')
            if redis_url:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            else:
                # Local Redis (development)
                self.redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    password=os.getenv('REDIS_PASSWORD'),
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )

            # Test connection
            if self.redis_client:
                self.redis_client.ping()
                self.cache_available = True
                print("✅ Redis cache connected and ready")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            self.redis_client = None
            self.cache_available = False

    def _generate_cache_key(self, prefix: str, identifier: str) -> str:
        """Generate consistent cache key with namespace."""
        # Hash long identifiers for consistent key length
        if len(identifier) > 100:
            identifier = hashlib.md5(identifier.encode()).hexdigest()
        return f"tilores:{prefix}:{identifier}"

    def get_tilores_fields(self, api_instance_id: str) -> Optional[str]:
        """Get cached Tilores field discovery results."""
        if not self.cache_available or not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key("fields", api_instance_id)
            result = self.redis_client.get(cache_key)

            if result:
                print(f"🎯 Cache HIT: Tilores fields for {api_instance_id}")
                return str(result)
            return None
        except Exception as e:
            print(f"⚠️ Cache read error: {e}")
            return None

    def set_tilores_fields(self, api_instance_id: str, fields_data: str):
        """Cache Tilores field discovery results (1 hour TTL)."""
        if not self.cache_available or not self.redis_client:
            return

        try:
            cache_key = self._generate_cache_key("fields", api_instance_id)
            # 1 hour TTL for field discovery data
            self.redis_client.setex(cache_key, 3600, str(fields_data))
            print(f"💾 Cached Tilores fields for {api_instance_id}")
        except Exception as e:
            print(f"⚠️ Cache write error: {e}")

    def get_llm_response(self, query_hash: str) -> Optional[str]:
        """Get cached LLM response."""
        if not self.cache_available or not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key("llm", query_hash)
            result = self.redis_client.get(cache_key)

            if result:
                print(f"🎯 Cache HIT: LLM response for {query_hash[:12]}...")
                return str(result)
            return None
        except Exception as e:
            print(f"⚠️ Cache read error: {e}")
            return None

    def set_llm_response(self, query_hash: str, response: str):
        """Cache LLM response (24 hour TTL)."""
        if not self.cache_available or not self.redis_client:
            return

        try:
            cache_key = self._generate_cache_key("llm", query_hash)
            # 24 hour TTL for LLM responses
            self.redis_client.setex(cache_key, 86400, str(response))
            print(f"💾 Cached LLM response for {query_hash[:12]}...")
        except Exception as e:
            print(f"⚠️ Cache write error: {e}")

    def get_customer_search(self, search_params_hash: str) -> Optional[Dict]:
        """Get cached customer search results."""
        if not self.cache_available or not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key("search", search_params_hash)
            result = self.redis_client.get(cache_key)

            if result:
                print(f"🎯 Cache HIT: Customer search {search_params_hash[:12]}")  # noqa: E501
                return json.loads(str(result))
            return None
        except Exception as e:
            print(f"⚠️ Cache read error: {e}")
            return None

    def set_customer_search(self, search_params_hash: str,
                            search_results: Dict):
        """Cache customer search results (1 hour TTL)."""
        if not self.cache_available or not self.redis_client:
            return

        try:
            cache_key = self._generate_cache_key("search", search_params_hash)
            # 1 hour TTL for customer search results
            self.redis_client.setex(
                cache_key,
                3600,
                json.dumps(search_results)
            )
            print(f"💾 Cached customer search {search_params_hash[:12]}")
        except Exception as e:
            print(f"⚠️ Cache write error: {e}")

    def get_credit_report(self, customer_id: str) -> Optional[str]:
        """Get cached credit report."""
        if not self.cache_available or not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key("credit", customer_id)
            result = self.redis_client.get(cache_key)

            if result:
                print(f"🎯 Cache HIT: Credit report for {customer_id}")
                return str(result)
            return None
        except Exception as e:
            print(f"⚠️ Cache read error: {e}")
            return None

    def set_credit_report(self, customer_id: str, report: str):
        """Cache credit report (1 hour TTL)."""
        if not self.cache_available or not self.redis_client:
            return

        try:
            cache_key = self._generate_cache_key("credit", customer_id)
            # 1 hour TTL for credit reports
            self.redis_client.setex(cache_key, 3600, str(report))
            print(f"💾 Cached credit report for {customer_id}")
        except Exception as e:
            print(f"⚠️ Cache write error: {e}")

    def generate_query_hash(self, query: str, model: str = "",
                            context: str = "") -> str:
        """Generate consistent hash for LLM query caching."""
        # Combine query, model, and context for unique cache key
        combined = f"{query}|{model}|{context}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def generate_search_hash(self, search_params: Dict[str, Any]) -> str:
        """Generate consistent hash for customer search caching."""
        # Sort parameters for consistent hashing
        sorted_params = json.dumps(search_params, sort_keys=True)
        return hashlib.sha256(sorted_params.encode()).hexdigest()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring."""
        if not self.cache_available or not self.redis_client:
            return {
                "status": "unavailable",
                "cache_available": False,
                "redis_connected": False
            }

        try:
            # Get basic Redis stats
            return {
                "status": "available",
                "cache_available": True,
                "redis_connected": True,
                "redis_info": "available"
            }
        except Exception as e:
            return {
                "status": "error",
                "cache_available": False,
                "redis_connected": False,
                "error": str(e)
            }

    def clear_cache(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries matching pattern or all if no pattern."""
        if not self.cache_available or not self.redis_client:
            return 0

        try:
            if pattern:
                key_pattern = f"tilores:{pattern}:*"
            else:
                key_pattern = "tilores:*"

            # Get keys and clear them
            keys = self.redis_client.keys(key_pattern)
            count = 0
            if keys:
                # Delete keys individually to avoid type issues
                for key in keys:
                    self.redis_client.delete(key)
                count = len(keys)

            print(f"🧹 Cleared {count} cache entries")
            return count
        except Exception as e:
            print(f"⚠️ Cache clear error: {e}")
            return 0


# Global instance for easy access
cache_manager = RedisCacheManager()
