"""
Cache Pre-warming System for Tilores_X
Pre-loads known customers for instant access in phone applications
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import schedule
import threading

logger = logging.getLogger(__name__)


class CachePrewarmer:
    """
    Pre-warms cache with known customer data for instant access
    Critical for phone applications where latency matters
    """
    
    def __init__(self, tilores_api, cache_manager, batch_processor=None):
        """
        Initialize cache pre-warmer
        
        Args:
            tilores_api: Tilores API instance
            cache_manager: Cache manager with tiered cache
            batch_processor: Optional batch processor for parallel warming
        """
        self.tilores_api = tilores_api
        self.cache_manager = cache_manager
        self.batch_processor = batch_processor
        
        # Pre-warm configuration
        self.config = {
            "batch_size": 5,
            "parallel_workers": 3,
            "ttl_minutes": 30,
            "retry_failed": True,
            "max_retries": 2
        }
        
        # Statistics
        self.stats = {
            "total_warmed": 0,
            "successful": 0,
            "failed": 0,
            "last_warm_time": None,
            "avg_warm_time_ms": 0
        }
        
        # Background thread for scheduled warming
        self.scheduler_thread = None
        self.stop_scheduler = False
        
        logger.info("🔥 Cache pre-warmer initialized")
    
    def warm_single_customer(self, identifier: str, search_type: str = "all") -> bool:
        """
        Pre-warm cache for a single customer
        
        Args:
            identifier: Customer identifier (email, phone, etc.)
            search_type: Type of search to cache
            
        Returns:
            True if successful, False otherwise
        """
        try:
            start_time = time.time()
            
            # Check if already cached
            if self.cache_manager and hasattr(self.cache_manager, 'tiered_cache'):
                cached, source = self.cache_manager.tiered_cache.get_tilores_search(
                    identifier, search_type
                )
                if cached and source == "l1":
                    logger.debug(f"✓ {identifier} already in L1 cache")
                    return True
            
            # Fetch from Tilores
            logger.debug(f"Warming cache for {identifier}...")
            
            # Build search query
            search_params = self._build_search_params(identifier)
            query = self._build_graphql_query(search_params)
            
            # Execute search
            result = self.tilores_api.execute(query)
            
            if result:
                # Cache the result
                if self.cache_manager and hasattr(self.cache_manager, 'tiered_cache'):
                    ttl = self.config["ttl_minutes"] * 60
                    self.cache_manager.tiered_cache.set_tilores_search(
                        identifier, result, search_type, ttl
                    )
                
                elapsed_ms = (time.time() - start_time) * 1000
                self.stats["successful"] += 1
                self.stats["avg_warm_time_ms"] = (
                    (self.stats["avg_warm_time_ms"] + elapsed_ms) / 2
                )
                
                logger.debug(f"✅ Warmed {identifier} in {elapsed_ms:.0f}ms")
                return True
            else:
                self.stats["failed"] += 1
                logger.warning(f"❌ Failed to warm {identifier}")
                return False
                
        except Exception as e:
            self.stats["failed"] += 1
            logger.error(f"Error warming {identifier}: {e}")
            return False
    
    def warm_batch(self, identifiers: List[str], use_parallel: bool = True) -> Dict[str, bool]:
        """
        Pre-warm cache for multiple customers
        
        Args:
            identifiers: List of customer identifiers
            use_parallel: Whether to use parallel processing
            
        Returns:
            Dictionary of identifier -> success status
        """
        start_time = time.time()
        self.stats["total_warmed"] += len(identifiers)
        
        logger.info(f"🔥 Pre-warming {len(identifiers)} customers...")
        
        results = {}
        
        if use_parallel and self.batch_processor:
            # Use batch processor for parallel warming
            batch_results = self.batch_processor.batch_search(identifiers)
            
            for i, identifier in enumerate(identifiers):
                if batch_results[i] and not batch_results[i].get("error"):
                    results[identifier] = True
                    self.stats["successful"] += 1
                else:
                    results[identifier] = False
                    self.stats["failed"] += 1
        else:
            # Sequential warming
            for identifier in identifiers:
                results[identifier] = self.warm_single_customer(identifier)
        
        elapsed = time.time() - start_time
        self.stats["last_warm_time"] = datetime.now()
        
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"✅ Pre-warmed {success_count}/{len(identifiers)} in {elapsed:.2f}s")
        
        return results
    
    def warm_from_config(self, config: Dict[str, Any]) -> Dict[str, bool]:
        """
        Pre-warm cache based on configuration
        
        Args:
            config: Pre-warm configuration with customer lists
            
        Returns:
            Results dictionary
        """
        all_results = {}
        
        # High priority customers first
        if "high_priority_customers" in config:
            logger.info("🎯 Warming high-priority customers...")
            results = self.warm_batch(
                config["high_priority_customers"],
                use_parallel=config.get("use_parallel", True)
            )
            all_results.update(results)
        
        # Common searches
        if "common_searches" in config:
            logger.info("🔍 Warming common searches...")
            results = self.warm_batch(
                config["common_searches"],
                use_parallel=config.get("use_parallel", True)
            )
            all_results.update(results)
        
        return all_results
    
    def schedule_warming(self, interval_minutes: int = 30, 
                         customer_list: List[str] = None):
        """
        Schedule periodic cache warming
        
        Args:
            interval_minutes: How often to refresh cache
            customer_list: List of customers to keep warm
        """
        if not customer_list:
            logger.warning("No customers provided for scheduled warming")
            return
        
        def warm_job():
            """Job to run periodically"""
            if not self.stop_scheduler:
                logger.info(f"⏰ Scheduled cache warming at {datetime.now()}")
                self.warm_batch(customer_list)
        
        # Schedule the job
        schedule.every(interval_minutes).minutes.do(warm_job)
        
        # Run in background thread
        def run_scheduler():
            while not self.stop_scheduler:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info(f"📅 Scheduled warming every {interval_minutes} minutes for {len(customer_list)} customers")
    
    def stop_scheduled_warming(self):
        """Stop scheduled warming"""
        self.stop_scheduler = True
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("🛑 Scheduled warming stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pre-warming statistics"""
        return {
            "total_warmed": self.stats["total_warmed"],
            "successful": self.stats["successful"],
            "failed": self.stats["failed"],
            "success_rate": (
                (self.stats["successful"] / max(1, self.stats["total_warmed"])) * 100
            ),
            "avg_warm_time_ms": round(self.stats["avg_warm_time_ms"], 1),
            "last_warm_time": self.stats["last_warm_time"].isoformat() if self.stats["last_warm_time"] else None
        }
    
    def _build_search_params(self, identifier: str) -> Dict[str, str]:
        """Build search parameters from identifier"""
        if "@" in identifier:
            return {"EMAIL": identifier}
        elif identifier.replace("-", "").replace(" ", "").isdigit():
            return {"PHONE_EXTERNAL": identifier}
        elif identifier.startswith("003"):
            return {"SALESFORCE_ID": identifier}
        elif identifier.isdigit():
            return {"CLIENT_ID": identifier}
        else:
            # Assume name
            parts = identifier.split()
            if len(parts) >= 2:
                return {"FIRST_NAME": parts[0], "LAST_NAME": parts[-1]}
            return {"LAST_NAME": identifier}
    
    def _build_graphql_query(self, search_params: Dict[str, str]) -> str:
        """Build GraphQL query for search"""
        conditions = " AND ".join([
            f'{field}: "{value}"' for field, value in search_params.items()
        ])
        
        return f"""
        {{
            search(query: "{conditions}") {{
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
                            MAILING_STREET
                            MAILING_CITY
                            MAILING_STATE
                            MAILING_ZIP
                        }}
                    }}
                }}
            }}
        }}
        """


# Convenience functions for easy usage

def create_prewarmer(tilores_api, cache_manager, batch_processor=None):
    """Create a cache pre-warmer instance"""
    return CachePrewarmer(tilores_api, cache_manager, batch_processor)


def prewarm_customers(tilores_api, cache_manager, customer_list: List[str]):
    """
    Quick function to pre-warm a list of customers
    
    Args:
        tilores_api: Tilores API instance
        cache_manager: Cache manager
        customer_list: List of customer identifiers
        
    Returns:
        Dictionary of results
    """
    warmer = CachePrewarmer(tilores_api, cache_manager)
    return warmer.warm_batch(customer_list)


def setup_scheduled_warming(tilores_api, cache_manager, customer_list: List[str], 
                          interval_minutes: int = 30):
    """
    Setup scheduled cache warming
    
    Args:
        tilores_api: Tilores API instance
        cache_manager: Cache manager
        customer_list: Customers to keep warm
        interval_minutes: Refresh interval
        
    Returns:
        CachePrewarmer instance with scheduling active
    """
    warmer = CachePrewarmer(tilores_api, cache_manager)
    warmer.schedule_warming(interval_minutes, customer_list)
    return warmer


# Example usage for phone application
PHONE_APP_PREWARM_CONFIG = {
    "high_priority_customers": [
        "john.smith@techcorp.com",
        "sarah.johnson@healthcare.org",
        "mike.brown@retail.com",
        "emily.davis@finance.io",
        "david.wilson@startup.tech"
    ],
    "common_searches": [
        "555-123-4567",
        "555-987-6543",
        "555-555-0123",
        "1881899",
        "1992837"
    ],
    "refresh_interval_minutes": 30,
    "batch_size": 5,
    "use_parallel": True
}