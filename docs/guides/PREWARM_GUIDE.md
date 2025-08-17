# Cache Pre-warming Guide for Phone Applications

## Overview

Cache pre-warming is critical for phone applications where every millisecond counts. By pre-loading customer data before calls, we can achieve <100ms response times for known customers.

## Quick Start

### 1. Basic Pre-warming (One-time)

```python
from utils.cache_prewarm import prewarm_customers
from core_app import engine
from redis_cache import cache_manager

# List of high-priority customers
customers = [
    "john.smith@techcorp.com",
    "sarah.johnson@healthcare.org",
    "555-123-4567",
    "1881899"  # Client ID
]

# Pre-warm the cache
results = prewarm_customers(
    tilores_api=engine.tilores,
    cache_manager=cache_manager,
    customer_list=customers
)

print(f"Pre-warmed {sum(1 for v in results.values() if v)}/{len(customers)} customers")
```

### 2. Scheduled Pre-warming (Continuous)

```python
from utils.cache_prewarm import setup_scheduled_warming
from core_app import engine
from redis_cache import cache_manager

# High-value customers to keep warm
vip_customers = [
    "john.smith@techcorp.com",
    "sarah.johnson@healthcare.org",
    "mike.brown@retail.com"
]

# Setup 30-minute refresh
warmer = setup_scheduled_warming(
    tilores_api=engine.tilores,
    cache_manager=cache_manager,
    customer_list=vip_customers,
    interval_minutes=30
)

# Check stats anytime
stats = warmer.get_stats()
print(f"Success rate: {stats['success_rate']:.1f}%")
```

### 3. Advanced Pre-warming with Configuration

```python
from utils.cache_prewarm import CachePrewarmer
from utils.batch_processor import TiloresBatchProcessor
from core_app import engine
from redis_cache import cache_manager

# Create components
batch_processor = TiloresBatchProcessor(
    tilores_api=engine.tilores,
    cache_manager=cache_manager,
    max_workers=5
)

warmer = CachePrewarmer(
    tilores_api=engine.tilores,
    cache_manager=cache_manager,
    batch_processor=batch_processor
)

# Configuration
config = {
    "high_priority_customers": [
        "john.smith@techcorp.com",
        "sarah.johnson@healthcare.org",
        "mike.brown@retail.com"
    ],
    "common_searches": [
        "555-123-4567",
        "555-987-6543",
        "1881899"
    ],
    "use_parallel": True,
    "batch_size": 5
}

# Pre-warm from config
results = warmer.warm_from_config(config)
```

## Integration with FastAPI

### Add Pre-warming Endpoint

```python
# In main_enhanced.py

@app.post("/admin/prewarm")
@limiter.limit("10/hour")
async def prewarm_cache(request: Request, customers: List[str]):
    """Pre-warm cache for specified customers (admin only)"""

    from utils.cache_prewarm import prewarm_customers
    from core_app import engine
    from redis_cache import cache_manager

    results = prewarm_customers(
        tilores_api=engine.tilores,
        cache_manager=cache_manager,
        customer_list=customers
    )

    success_count = sum(1 for v in results.values() if v)

    return {
        "status": "success",
        "pre_warmed": success_count,
        "total": len(customers),
        "success_rate": (success_count / len(customers)) * 100
    }

@app.on_event("startup")
async def startup_prewarm():
    """Pre-warm cache on application startup"""
    from utils.cache_prewarm import PHONE_APP_PREWARM_CONFIG, prewarm_customers
    from core_app import engine
    from redis_cache import cache_manager

    # Pre-warm high priority customers
    customers = PHONE_APP_PREWARM_CONFIG["high_priority_customers"]

    print(f"🔥 Pre-warming {len(customers)} customers on startup...")
    results = prewarm_customers(
        tilores_api=engine.tilores,
        cache_manager=cache_manager,
        customer_list=customers
    )

    success = sum(1 for v in results.values() if v)
    print(f"✅ Pre-warmed {success}/{len(customers)} customers")
```

## Phone Application Integration

### Before Call Starts

```python
def prepare_for_call(phone_number: str):
    """Prepare cache before phone call"""

    # Check if already cached
    cached, source = cache_manager.tiered_cache.get_tilores_search(phone_number)

    if not cached or source != "l1":
        # Pre-warm this specific customer
        warmer.warm_single_customer(phone_number)

    return cached is not None

# In your phone app
phone_number = "555-123-4567"
if prepare_for_call(phone_number):
    print("✅ Ready for instant response")
else:
    print("⚠️ Customer not found, will search on demand")
```

### Batch Pre-warming for Call Queue

```python
def prepare_call_queue(queue: List[str]):
    """Pre-warm entire call queue"""

    from utils.batch_processor import TiloresBatchProcessor

    processor = TiloresBatchProcessor(
        tilores_api=engine.tilores,
        cache_manager=cache_manager,
        max_workers=5
    )

    # Warm all customers in parallel
    results = processor.batch_search(queue)

    # Count successes
    ready = sum(1 for r in results if not r.get("error"))

    print(f"📞 Call queue ready: {ready}/{len(queue)} customers cached")
    return results

# Example: Morning call queue
morning_queue = [
    "555-123-4567",
    "john.smith@techcorp.com",
    "1881899",
    "sarah.johnson@healthcare.org"
]

prepare_call_queue(morning_queue)
```

## Performance Impact

### Without Pre-warming
- First query: 500-2000ms (Tilores API call)
- Subsequent queries: 10-50ms (Redis cache)
- Phone experience: Noticeable delay

### With Pre-warming
- First query: 1-5ms (L1 memory cache)
- Subsequent queries: 1-5ms (L1 memory cache)
- Phone experience: Instant response

## Best Practices

### 1. Identify High-Value Customers
```python
# Analytics to find frequently accessed customers
def get_top_customers(limit=20):
    """Get most frequently accessed customers"""
    # This would query your analytics/logs
    return [
        "john.smith@techcorp.com",
        "sarah.johnson@healthcare.org",
        # ... more customers
    ]

# Pre-warm top customers daily
top_customers = get_top_customers(20)
warmer.warm_batch(top_customers)
```

### 2. Time-based Pre-warming
```python
import schedule

# Pre-warm before business hours
schedule.every().day.at("07:30").do(
    lambda: warmer.warm_batch(vip_customers)
)

# Refresh at lunch
schedule.every().day.at("12:00").do(
    lambda: warmer.warm_batch(vip_customers)
)

# Evening refresh
schedule.every().day.at("17:00").do(
    lambda: warmer.warm_batch(vip_customers)
)
```

### 3. Event-driven Pre-warming
```python
def on_customer_update(customer_id: str):
    """Refresh cache when customer data changes"""

    # Invalidate old cache
    cache_key = f"tilores:search:{customer_id}"
    cache_manager.redis_client.delete(cache_key)

    # Pre-warm with fresh data
    warmer.warm_single_customer(customer_id)

# Webhook endpoint
@app.post("/webhook/customer-updated")
async def customer_updated(customer_id: str):
    on_customer_update(customer_id)
    return {"status": "cache refreshed"}
```

### 4. Monitor Cache Performance
```python
def get_cache_metrics():
    """Get cache performance metrics"""

    tiered_stats = cache_manager.tiered_cache.get_stats()
    warmer_stats = warmer.get_stats()

    return {
        "cache_hit_rate": tiered_stats["hit_rate"],
        "l1_hit_rate": tiered_stats["l1_hit_rate"],
        "avg_l1_latency_ms": tiered_stats["avg_l1_latency_ms"],
        "total_pre_warmed": warmer_stats["total_warmed"],
        "pre_warm_success_rate": warmer_stats["success_rate"],
        "last_warm_time": warmer_stats["last_warm_time"]
    }

# Check metrics periodically
metrics = get_cache_metrics()
if metrics["cache_hit_rate"] < 80:
    print("⚠️ Low cache hit rate - consider pre-warming more customers")
```

## Configuration Options

### Environment Variables
```bash
# Cache configuration
CACHE_PREWARM_ENABLED=true
CACHE_PREWARM_INTERVAL=30  # minutes
CACHE_PREWARM_BATCH_SIZE=10
CACHE_PREWARM_TTL=1800  # seconds

# Customer lists (comma-separated)
PREWARM_VIP_CUSTOMERS=john@example.com,sarah@example.com
PREWARM_COMMON_SEARCHES=555-1234,555-5678
```

### Dynamic Configuration
```python
# Load from database or config file
def load_prewarm_config():
    """Load pre-warm configuration dynamically"""

    # Could load from database, Redis, or file
    return {
        "customers": get_vip_customers_from_db(),
        "interval": get_config_value("prewarm_interval", 30),
        "batch_size": get_config_value("prewarm_batch_size", 5)
    }

# Apply dynamic config
config = load_prewarm_config()
warmer.config.update(config)
```

## Troubleshooting

### Issue: Low cache hit rate
```python
# Diagnose cache misses
def analyze_cache_misses():
    stats = cache_manager.tiered_cache.get_stats()

    if stats["l1_hit_rate"] < 50:
        print("L1 cache too small - increase l1_max_size")

    if stats["l2_hit_rate"] < 70:
        print("TTL too short - increase cache TTL")

    return stats
```

### Issue: Pre-warming too slow
```python
# Optimize pre-warming speed
def optimize_prewarm():
    # Increase parallel workers
    warmer.config["parallel_workers"] = 10

    # Reduce data fetched
    warmer.config["fields_to_cache"] = ["EMAIL", "PHONE", "NAME"]

    # Use batch processor
    if not warmer.batch_processor:
        warmer.batch_processor = TiloresBatchProcessor(
            tilores_api=engine.tilores,
            cache_manager=cache_manager,
            max_workers=10
        )
```

### Issue: Cache memory usage
```python
# Monitor and manage cache size
def manage_cache_size():
    stats = cache_manager.tiered_cache.get_stats()

    if stats["cache_size_kb"] > 10000:  # 10MB
        print("⚠️ Cache using significant memory")

        # Reduce L1 size
        cache_manager.tiered_cache.l1_max_size = 25

        # Clear old entries
        cache_manager.tiered_cache.clear_l1()
```

## Summary

Pre-warming is essential for phone applications where latency matters:

1. **Identify** high-value customers
2. **Pre-warm** before peak times
3. **Monitor** cache performance
4. **Refresh** periodically
5. **Optimize** based on usage patterns

With proper pre-warming, you can achieve:
- ✅ <5ms response times for known customers
- ✅ 90%+ cache hit rates
- ✅ Instant phone application responses
- ✅ Happy customers and support agents
