"""
Batch Processing for Tilores Queries
Optimized for handling multiple customer searches in parallel
Designed for phone application latency requirements
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


class TiloresBatchProcessor:
    """
    Batch processor for Tilores queries with parallel execution
    Reduces latency when searching for multiple customers
    """
    
    def __init__(self, tilores_api, cache_manager=None, max_workers: int = 5):
        """
        Initialize batch processor
        
        Args:
            tilores_api: Tilores API instance
            cache_manager: Optional cache manager for fast lookups
            max_workers: Maximum parallel workers (default 5)
        """
        self.tilores_api = tilores_api
        self.cache_manager = cache_manager
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Performance metrics
        self.stats = {
            "total_batches": 0,
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_query_time": 0,
            "avg_batch_time": 0,
        }
        
        logger.info(f"🚀 Batch processor initialized with {max_workers} workers")
    
    def _search_single(self, identifier: str, search_type: str = "all") -> Dict[str, Any]:
        """
        Execute single search with caching
        
        Args:
            identifier: Customer identifier
            search_type: Type of search
            
        Returns:
            Search result dictionary
        """
        start_time = time.time()
        
        # Check cache first if available
        if self.cache_manager:
            # Try tiered cache for ultra-fast access
            if hasattr(self.cache_manager, 'tiered_cache') and self.cache_manager.tiered_cache:
                cached, source = self.cache_manager.tiered_cache.get_tilores_search(
                    identifier, search_type
                )
                if cached:
                    elapsed = (time.time() - start_time) * 1000
                    self.stats["cache_hits"] += 1
                    logger.debug(f"⚡ Cache hit ({source}) for {identifier[:20]}... - {elapsed:.1f}ms")
                    return cached
            
            # Try regular cache
            search_hash = self.cache_manager.generate_search_hash({
                "identifier": identifier,
                "type": search_type
            })
            cached = self.cache_manager.get_customer_search(search_hash)
            if cached:
                elapsed = (time.time() - start_time) * 1000
                self.stats["cache_hits"] += 1
                logger.debug(f"🎯 Cache hit for {identifier[:20]}... - {elapsed:.1f}ms")
                return cached
        
        self.stats["cache_misses"] += 1
        
        # Execute actual Tilores search
        try:
            # Build search query based on identifier type
            search_params = self._build_search_params(identifier)
            
            # Execute search with timeout protection
            from utils.timeout_config import get_timeout_manager
            timeout_mgr = get_timeout_manager()
            timeout = timeout_mgr.get_timeout("search_operation")
            
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._execute_tilores_search, search_params)
                result = future.result(timeout=timeout)
            
            elapsed = (time.time() - start_time) * 1000
            logger.debug(f"✅ Tilores search for {identifier[:20]}... - {elapsed:.1f}ms")
            
            # Cache the result
            if self.cache_manager and result:
                if hasattr(self.cache_manager, 'tiered_cache') and self.cache_manager.tiered_cache:
                    self.cache_manager.tiered_cache.set_tilores_search(
                        identifier, result, search_type, ttl=1800
                    )
                else:
                    search_hash = self.cache_manager.generate_search_hash({
                        "identifier": identifier,
                        "type": search_type
                    })
                    self.cache_manager.set_customer_search(search_hash, result)
            
            return result
            
        except concurrent.futures.TimeoutError:
            logger.warning(f"⏰ Search timeout for {identifier[:20]}...")
            return {"error": "timeout", "identifier": identifier}
        except Exception as e:
            logger.error(f"❌ Search error for {identifier[:20]}...: {e}")
            return {"error": str(e), "identifier": identifier}
    
    def _build_search_params(self, identifier: str) -> Dict[str, Any]:
        """Build search parameters based on identifier type"""
        # Detect identifier type
        if "@" in identifier:
            return {"EMAIL": identifier}
        elif identifier.replace("-", "").replace(" ", "").isdigit():
            return {"PHONE_EXTERNAL": identifier}
        elif identifier.startswith("003"):
            return {"SALESFORCE_ID": identifier}
        elif identifier.isdigit() and len(identifier) >= 7:
            return {"CLIENT_ID": identifier}
        else:
            # Assume it's a name
            parts = identifier.split()
            if len(parts) >= 2:
                return {"FIRST_NAME": parts[0], "LAST_NAME": parts[-1]}
            else:
                return {"LAST_NAME": identifier}
    
    def _execute_tilores_search(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute actual Tilores GraphQL search"""
        # Build GraphQL query
        field_conditions = " AND ".join([
            f'{field}: "{value}"' for field, value in search_params.items()
        ])
        
        query = f"""
        {{
            search(query: "{field_conditions}") {{
                entities {{
                    id
                    records {{
                        ... on CustomerRecord {{
                            EMAIL
                            FIRST_NAME
                            LAST_NAME
                            PHONE_EXTERNAL
                            CLIENT_ID
                            SALESFORCE_ID
                        }}
                    }}
                }}
            }}
        }}
        """
        
        # Execute query
        result = self.tilores_api.execute(query)
        
        if result and "search" in result:
            return result["search"]
        return {}
    
    def batch_search(self, identifiers: List[str], search_type: str = "all") -> List[Dict[str, Any]]:
        """
        Execute batch search for multiple identifiers in parallel
        
        Args:
            identifiers: List of customer identifiers
            search_type: Type of search for all
            
        Returns:
            List of search results in same order as identifiers
        """
        start_time = time.time()
        self.stats["total_batches"] += 1
        self.stats["total_queries"] += len(identifiers)
        
        logger.info(f"🔄 Starting batch search for {len(identifiers)} identifiers...")
        
        # Submit all searches in parallel
        futures = {}
        for identifier in identifiers:
            future = self.executor.submit(self._search_single, identifier, search_type)
            futures[future] = identifier
        
        # Collect results maintaining order
        results = {}
        completed = 0
        
        for future in as_completed(futures):
            identifier = futures[future]
            try:
                result = future.result(timeout=5.0)  # 5s timeout per query
                results[identifier] = result
                completed += 1
                
                if completed % 5 == 0:
                    logger.debug(f"   Completed {completed}/{len(identifiers)} searches...")
                    
            except Exception as e:
                logger.error(f"Failed to search {identifier}: {e}")
                results[identifier] = {"error": str(e), "identifier": identifier}
        
        # Return results in original order
        ordered_results = [results.get(id, {"error": "not_found", "identifier": id}) 
                          for id in identifiers]
        
        elapsed = time.time() - start_time
        self.stats["avg_batch_time"] = (self.stats["avg_batch_time"] + elapsed) / 2
        
        cache_rate = (self.stats["cache_hits"] / max(1, self.stats["total_queries"])) * 100
        
        logger.info(f"✅ Batch search completed in {elapsed:.2f}s")
        logger.info(f"   • Processed: {len(identifiers)} queries")
        logger.info(f"   • Cache hit rate: {cache_rate:.1f}%")
        logger.info(f"   • Avg time per query: {(elapsed/len(identifiers)*1000):.0f}ms")
        
        return ordered_results
    
    async def batch_search_async(self, identifiers: List[str], 
                                search_type: str = "all") -> List[Dict[str, Any]]:
        """
        Async version of batch search for even better performance
        
        Args:
            identifiers: List of customer identifiers
            search_type: Type of search
            
        Returns:
            List of search results
        """
        loop = asyncio.get_event_loop()
        
        # Create tasks for all searches
        tasks = [
            loop.run_in_executor(self.executor, self._search_single, id, search_type)
            for id in identifiers
        ]
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed.append({"error": str(result), "identifier": identifiers[i]})
            else:
                processed.append(result)
        
        return processed
    
    def optimize_for_phone(self):
        """Optimize batch processor for phone latency"""
        logger.info("📱 Optimizing batch processor for phone...")
        
        # Reduce workers to prevent overload
        self.max_workers = 3
        
        # Recreate executor with fewer workers
        self.executor.shutdown(wait=False)
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        logger.info(f"   ✅ Optimized: {self.max_workers} parallel workers")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get batch processing statistics"""
        return {
            "total_batches": self.stats["total_batches"],
            "total_queries": self.stats["total_queries"],
            "cache_hit_rate": (self.stats["cache_hits"] / max(1, self.stats["total_queries"])) * 100,
            "avg_query_time_ms": self.stats["avg_query_time"] * 1000,
            "avg_batch_time_s": self.stats["avg_batch_time"],
            "workers": self.max_workers
        }
    
    def shutdown(self):
        """Shutdown the batch processor cleanly"""
        self.executor.shutdown(wait=True)
        logger.info("Batch processor shut down")


# Convenience function for one-off batch searches
def batch_search_customers(tilores_api, identifiers: List[str], 
                          cache_manager=None) -> List[Dict[str, Any]]:
    """
    Convenience function for batch searching customers
    
    Args:
        tilores_api: Tilores API instance
        identifiers: List of customer identifiers
        cache_manager: Optional cache manager
        
    Returns:
        List of search results
    """
    processor = TiloresBatchProcessor(tilores_api, cache_manager, max_workers=5)
    try:
        results = processor.batch_search(identifiers)
        return results
    finally:
        processor.shutdown()