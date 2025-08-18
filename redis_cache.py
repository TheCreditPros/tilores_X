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

# Import debug configuration
from utils.debug_config import setup_logging, debug_print

# Set up module logger
logger = setup_logging(__name__)


class RedisCacheManager:
    """
    Redis cache manager with intelligent TTL management and optional L1 in-memory cache.

    Gracefully degrades when Redis is unavailable, ensuring system
    continues to work without caching infrastructure.
    """

    def __init__(self, enable_l1_cache: bool = True, l1_max_size: int = 100, l1_ttl: int = 300):
        """Initialize Redis connection with graceful fallback and optional L1 cache.

        Args:
            enable_l1_cache: Enable in-memory L1 cache for ultra-fast access
            l1_max_size: Maximum items in L1 memory cache
            l1_ttl: L1 cache TTL in seconds (default 5 minutes)
        """
        self.redis_client: Any = None
        self.cache_available = False

        # L1 in-memory cache configuration
        self.enable_l1 = enable_l1_cache
        self.l1_cache = {} if enable_l1_cache else None
        self.l1_timestamps = {} if enable_l1_cache else None
        self.l1_max_size = l1_max_size
        self.l1_ttl = l1_ttl

        # Performance metrics
        self.stats = {"l1_hits": 0, "l1_misses": 0, "l2_hits": 0, "l2_misses": 0, "total_queries": 0}

        if REDIS_AVAILABLE:
            self._connect_to_redis()

        if enable_l1_cache:
            debug_print(
                f"Two-tier cache initialized (L1: {l1_max_size} items, L2: {'Redis' if self.cache_available else 'Disabled'})",
                "🚀",
            )

    def _connect_to_redis(self):
        """Connect to Redis with Railway and local environment support."""
        try:
            # Railway Redis URL (production)
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                # Use redis.from_url for better Railway compatibility
                debug_print("Connecting to Railway Redis via URL", "🔗")
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=10,
                    socket_timeout=10,
                    retry_on_timeout=True,
                    health_check_interval=30,
                )
            else:
                # Local Redis (development) - gracefully handle missing password
                redis_password = os.getenv("REDIS_PASSWORD")
                debug_print(f"Connecting to local Redis (auth: {'yes' if redis_password else 'no'})", "🔗")

                self.redis_client = redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", 6379)),
                    password=redis_password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )

            # Test connection with retry logic and graceful fallback
            if self.redis_client:
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        self.redis_client.ping()
                        self.cache_available = True
                        logger.info("Redis cache connected and ready")
                        debug_print("Redis connection established", "✅")
                        break
                    except redis.AuthenticationError as auth_error:
                        logger.warning(f"Redis authentication failed: {auth_error}")
                        debug_print("Redis auth failed - falling back to no-cache mode", "⚠️")
                        # Don't raise auth errors in production - graceful fallback
                        self.redis_client = None
                        self.cache_available = False
                        break
                    except Exception as retry_error:
                        if attempt < max_retries - 1:
                            debug_print(f"Redis connection attempt {attempt + 1} failed, retrying...", "⚠️")
                            import time

                            time.sleep(2**attempt)  # Exponential backoff
                        else:
                            logger.warning(f"Redis connection failed after {max_retries} attempts: {retry_error}")
                            debug_print("Redis connection failed - falling back to no-cache mode", "⚠️")
                            self.redis_client = None
                            self.cache_available = False
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            debug_print(f"Redis connection failed - falling back to no-cache mode: {e}", "⚠️")
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
        cache_key = self._generate_cache_key("fields", api_instance_id)

        # Check L1 cache first if enabled
        if self.enable_l1 and cache_key in self.l1_cache:
            if self._is_l1_valid(cache_key):
                self.stats["l1_hits"] += 1
                debug_print(f"L1 Cache HIT: Tilores fields for {api_instance_id}", "⚡")
                return self.l1_cache[cache_key]
            else:
                # Remove expired entry
                del self.l1_cache[cache_key]
                del self.l1_timestamps[cache_key]

        if not self.cache_available or not self.redis_client:
            return None

        try:
            result = self.redis_client.get(cache_key)

            if result:
                self.stats["l2_hits"] += 1
                debug_print(f"L2 Cache HIT: Tilores fields for {api_instance_id}", "🎯")

                # Store in L1 cache if enabled
                if self.enable_l1:
                    self._store_in_l1(cache_key, str(result))

                return str(result)
            return None
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            debug_print(f"Cache read error: {e}", "⚠️")
            return None

    def _is_l1_valid(self, key: str) -> bool:
        """Check if L1 cache entry is still valid."""
        if key not in self.l1_timestamps:
            return False
        import time

        age = time.time() - self.l1_timestamps[key]
        return age < self.l1_ttl

    def _store_in_l1(self, key: str, value: Any):
        """Store value in L1 cache with eviction if needed."""
        if not self.enable_l1:
            return

        # Evict oldest entries if cache is full
        if len(self.l1_cache) >= self.l1_max_size:
            oldest_key = min(self.l1_timestamps, key=self.l1_timestamps.get)
            del self.l1_cache[oldest_key]
            del self.l1_timestamps[oldest_key]

        import time

        self.l1_cache[key] = value
        self.l1_timestamps[key] = time.time()

    def set_tilores_fields(self, api_instance_id: str, fields_data: str):
        """Cache Tilores field discovery results (1 hour TTL)."""
        if not self.cache_available or not self.redis_client:
            return

        try:
            cache_key = self._generate_cache_key("fields", api_instance_id)
            # 1 hour TTL for field discovery data
            self.redis_client.setex(cache_key, 3600, str(fields_data))
            debug_print(f"Cached Tilores fields for {api_instance_id}", "💾")
        except Exception as e:
            logger.error(f"Cache write error: {e}")
            debug_print(f"Cache write error: {e}", "⚠️")

    def get_llm_response(self, query_hash: str) -> Optional[str]:
        """Get cached LLM response."""
        if not self.cache_available or not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key("llm", query_hash)
            result = self.redis_client.get(cache_key)

            if result:
                debug_print(f"Cache HIT: LLM response for {query_hash[:12]}...", "🎯")
                return str(result)
            return None
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            debug_print(f"Cache read error: {e}", "⚠️")
            return None

    def set_llm_response(self, query_hash: str, response: str):
        """Cache LLM response (24 hour TTL)."""
        if not self.cache_available or not self.redis_client:
            return

        try:
            cache_key = self._generate_cache_key("llm", query_hash)
            # 24 hour TTL for LLM responses
            self.redis_client.setex(cache_key, 86400, str(response))
            debug_print(f"Cached LLM response for {query_hash[:12]}...", "💾")
        except Exception as e:
            logger.error(f"Cache write error: {e}")
            debug_print(f"Cache write error: {e}", "⚠️")

    def get_customer_search(self, search_params_hash: str) -> Optional[Dict]:
        """Get cached customer search results."""
        if not self.cache_available or not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key("search", search_params_hash)
            result = self.redis_client.get(cache_key)

            if result:
                debug_print(f"Cache HIT: Customer search {search_params_hash[:12]}", "🎯")  # noqa: E501
                return json.loads(str(result))
            return None
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            debug_print(f"Cache read error: {e}", "⚠️")
            return None

    def set_customer_search(self, search_params_hash: str, search_results: Dict):
        """Cache customer search results (1 hour TTL)."""
        if not self.cache_available or not self.redis_client:
            return

        try:
            cache_key = self._generate_cache_key("search", search_params_hash)
            # 1 hour TTL for customer search results
            self.redis_client.setex(cache_key, 3600, json.dumps(search_results))
            debug_print(f"Cached customer search {search_params_hash[:12]}", "💾")
        except Exception as e:
            logger.error(f"Cache write error: {e}")
            debug_print(f"Cache write error: {e}", "⚠️")

    def get_credit_report(self, customer_id: str) -> Optional[str]:
        """Get cached credit report."""
        if not self.cache_available or not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key("credit", customer_id)
            result = self.redis_client.get(cache_key)

            if result:
                debug_print(f"Cache HIT: Credit report for {customer_id}", "🎯")
                return str(result)
            return None
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            debug_print(f"Cache read error: {e}", "⚠️")
            return None

    def set_credit_report(self, customer_id: str, report: str):
        """Cache credit report (1 hour TTL)."""
        if not self.cache_available or not self.redis_client:
            return

        try:
            cache_key = self._generate_cache_key("credit", customer_id)
            # 1 hour TTL for credit reports
            self.redis_client.setex(cache_key, 3600, str(report))
            debug_print(f"Cached credit report for {customer_id}", "💾")
        except Exception as e:
            logger.error(f"Cache write error: {e}")
            debug_print(f"Cache write error: {e}", "⚠️")

    def generate_query_hash(self, query: str, model: str = "", context: str = "") -> str:
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
            return {"status": "unavailable", "cache_available": False, "redis_connected": False}

        try:
            # Get basic Redis stats
            return {"status": "available", "cache_available": True, "redis_connected": True, "redis_info": "available"}
        except Exception as e:
            return {"status": "error", "cache_available": False, "redis_connected": False, "error": str(e)}

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

            logger.info(f"Cleared {count} cache entries")
            debug_print(f"Cleared {count} cache entries", "🧹")
            return count
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            debug_print(f"Cache clear error: {e}", "⚠️")
            return 0


# Global instance for easy access
cache_manager = RedisCacheManager()
