"""
Enhanced Monitoring and Observability for Tilores API
Tracks performance, errors, and usage metrics
"""

import json
import logging
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# Redis cache for metrics storage (optional)
try:
    from redis_cache import cache_manager
    CACHE_AVAILABLE = True
except ImportError:
    cache_manager = None
    CACHE_AVAILABLE = False


class TiloresMonitor:
    """Enhanced monitoring for Tilores operations with metrics tracking"""

    def __init__(self, max_history: int = 1000):
        self.logger = logging.getLogger(__name__)
        self.max_history = max_history

        # In-memory metrics storage
        self.api_calls = deque(maxlen=max_history)
        self.error_log = deque(maxlen=max_history)
        self.performance_metrics = defaultdict(list)
        self.field_coverage_stats = defaultdict(int)

        # Timing storage
        self.active_timers = {}

        # Request counters
        self.request_counts = defaultdict(int)
        self.provider_usage = defaultdict(int)

        # Initialize start time
        self.start_time = time.time()

    def start_timer(self, operation_name: str, metadata: Optional[Dict] = None) -> str:
        """Start timing an operation"""
        timer_id = f"{operation_name}_{int(time.time() * 1000)}"
        self.active_timers[timer_id] = {
            "start": time.time(),
            "operation": operation_name,
            "metadata": metadata or {}
        }
        return timer_id

    def end_timer(
        self,
        timer_id: str,
        success: bool = True,
        error: Optional[str] = None
    ) -> float:
        """End timing an operation and record metrics"""
        if timer_id not in self.active_timers:
            self.logger.warning(f"Timer {timer_id} not found")
            return 0.0

        timer_info = self.active_timers.pop(timer_id)
        duration = time.time() - timer_info["start"]
        operation = timer_info["operation"]

        # Record performance metrics
        self.performance_metrics[operation].append(duration)

        # Record API call
        self.api_calls.append({
            "operation": operation,
            "duration": duration,
            "success": success,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "metadata": timer_info["metadata"]
        })

        # Log the operation
        if success:
            self.logger.info(f"✅ {operation} completed in {duration:.3f}s")
        else:
            self.logger.warning(f"⚠️ {operation} failed in {duration:.3f}s: {error}")
            self.record_error(operation, error, timer_info["metadata"])

        # Store in Redis if available
        if CACHE_AVAILABLE and cache_manager:
            try:
                metrics_key = f"metrics:{operation}:{datetime.now().strftime('%Y%m%d')}"
                cache_manager.redis_client.hincrby(metrics_key, "count", 1)
                cache_manager.redis_client.hincrbyfloat(metrics_key, "total_time", duration)
                if not success:
                    cache_manager.redis_client.hincrby(metrics_key, "errors", 1)
                cache_manager.redis_client.expire(metrics_key, 86400 * 7)  # Keep for 7 days
            except Exception as e:
                self.logger.debug(f"Could not store metrics in Redis: {e}")

        return duration

    def track_api_call(
        self,
        function_name: str,
        execution_time: float,
        success: bool,
        error: str = None,
        **kwargs
    ):
        """Track API call metrics"""
        self.request_counts[function_name] += 1

        # Track provider usage if provided
        if "provider" in kwargs:
            self.provider_usage[kwargs["provider"]] += 1

        # Record the call
        self.api_calls.append({
            "function": function_name,
            "execution_time": execution_time,
            "success": success,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        })

        if success:
            self.logger.info(
                f"✅ {function_name} completed successfully in {execution_time:.3f}s"
            )
        else:
            self.logger.warning(
                f"⚠️ {function_name} failed in {execution_time:.3f}s: {error}"
            )

    def record_error(
        self,
        function_name: str,
        error_msg: str,
        context: Dict[str, Any] = None
    ):
        """Record error information"""
        error_entry = {
            "function": function_name,
            "error": error_msg,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }

        self.error_log.append(error_entry)
        self.logger.error(f"❌ {function_name} error: {error_msg}")

        if context:
            self.logger.error(f"Context: {json.dumps(context, indent=2)}")

    def track_field_coverage(self, result_data: Dict[str, Any]):
        """Track field coverage analytics"""
        if isinstance(result_data, dict):
            field_count = len(result_data.keys())
            self.field_coverage_stats["total_calls"] += 1
            self.field_coverage_stats["total_fields"] += field_count

            # Track individual field usage
            for field in result_data.keys():
                self.field_coverage_stats[f"field_{field}"] += 1

            self.logger.info(f"📊 Field coverage: {field_count} fields returned")

    def track_tilores_connectivity(self) -> Dict[str, Any]:
        """Monitor Tilores API connectivity"""
        try:
            from core_app import engine

            if engine and engine.tilores:
                return {
                    "status": "connected",
                    "api_url": getattr(engine.tilores.api, 'api_url', 'unknown'),
                    "tools_available": len(engine.tools) if engine.tools else 0,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "disconnected",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        uptime = time.time() - self.start_time

        # Calculate average response times
        avg_times = {}
        for operation, times in self.performance_metrics.items():
            if times:
                avg_times[operation] = {
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "count": len(times)
                }

        # Calculate success rate
        total_calls = len(self.api_calls)
        successful_calls = sum(1 for call in self.api_calls if call.get("success", False))
        success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 100

        # Get recent errors
        recent_errors = list(self.error_log)[-10:]  # Last 10 errors

        return {
            "status": "operational",
            "uptime_seconds": uptime,
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "timestamp": datetime.now().isoformat(),
            "total_requests": total_calls,
            "success_rate": f"{success_rate:.2f}%",
            "request_counts": dict(self.request_counts),
            "provider_usage": dict(self.provider_usage),
            "average_response_times": avg_times,
            "recent_errors": recent_errors,
            "field_coverage": {
                "avg_fields_per_call": (
                    self.field_coverage_stats["total_fields"] /
                    self.field_coverage_stats["total_calls"]
                ) if self.field_coverage_stats["total_calls"] > 0 else 0
            },
            "tilores_connectivity": self.track_tilores_connectivity()
        }

    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        metrics = self.get_metrics()

        # Determine health based on metrics
        health = "healthy"
        issues = []

        # Check success rate
        success_rate = float(metrics["success_rate"].rstrip('%'))
        if success_rate < 95:
            health = "degraded" if success_rate > 80 else "unhealthy"
            issues.append(f"Low success rate: {metrics['success_rate']}")

        # Check Tilores connectivity
        if metrics["tilores_connectivity"]["status"] != "connected":
            health = "unhealthy"
            issues.append("Tilores API disconnected")

        # Check recent errors
        if len(metrics["recent_errors"]) > 5:
            health = "degraded" if health == "healthy" else health
            issues.append(f"High error rate: {len(metrics['recent_errors'])} recent errors")

        return {
            "health": health,
            "uptime": metrics["uptime_formatted"],
            "issues": issues,
            "metrics_summary": {
                "total_requests": metrics["total_requests"],
                "success_rate": metrics["success_rate"],
                "tilores_status": metrics["tilores_connectivity"]["status"]
            },
            "timestamp": metrics["timestamp"]
        }


# Global monitor instance
monitor = TiloresMonitor()
