"""
Optimized Timeout Configuration for Phone Application Latency
Target: <2 second total response time for phone interactions
"""

import os
from typing import Dict

def get_environment() -> str:
    """Detect current environment"""
    if os.getenv("RAILWAY_ENVIRONMENT"):
        return "production"
    elif os.getenv("CI"):
        return "ci"
    else:
        return "local"


# Optimized timeout configurations (in milliseconds)
TIMEOUT_CONFIGS = {
    "local": {
        "tilores_init": 3000,        # 3s (was 30s) - fail fast locally
        "field_discovery": 2000,      # 2s (was 15s) - cached after first
        "search_operation": 3000,     # 3s (was 30s) - most important for phone
        "llm_generation": 5000,       # 5s - LLM response timeout
        "redis_connect": 1000,        # 1s - Redis connection
        "api_request": 3000,          # 3s - General API requests
    },
    "production": {
        "tilores_init": 8000,        # 8s (was 120s) - network latency
        "field_discovery": 5000,      # 5s (was 30s) - cached after first
        "search_operation": 5000,     # 5s (was 30s) - critical for phone UX
        "llm_generation": 8000,       # 8s - LLM response timeout
        "redis_connect": 2000,        # 2s - Redis connection
        "api_request": 5000,          # 5s - General API requests
    },
    "ci": {
        "tilores_init": 5000,        # 5s - CI environment
        "field_discovery": 3000,      # 3s
        "search_operation": 4000,     # 4s
        "llm_generation": 6000,       # 6s
        "redis_connect": 1500,        # 1.5s
        "api_request": 4000,          # 4s
    }
}

# Retry configuration with faster backoff
RETRY_CONFIGS = {
    "local": {
        "initial_delay": 0.2,         # 200ms (was 2s)
        "max_delay": 2.0,             # 2s (was 8s)
        "max_retries": 2,             # 2 (was 5) - fail faster
        "exponential_base": 1.5,      # Less aggressive backoff
    },
    "production": {
        "initial_delay": 0.3,         # 300ms (was 2s)
        "max_delay": 3.0,             # 3s (was 8s)
        "max_retries": 3,             # 3 (was 5)
        "exponential_base": 2.0,      # Standard exponential
    },
    "ci": {
        "initial_delay": 0.25,        # 250ms
        "max_delay": 2.5,             # 2.5s
        "max_retries": 2,             # 2
        "exponential_base": 1.5,      # Less aggressive
    }
}


class TimeoutManager:
    """Manages timeouts optimized for phone application latency"""
    
    def __init__(self, environment: str = None):
        """Initialize with environment-specific timeouts"""
        self.environment = environment or get_environment()
        self.timeouts = TIMEOUT_CONFIGS[self.environment]
        self.retry_config = RETRY_CONFIGS[self.environment]
        
        # Apply any environment variable overrides
        self._apply_overrides()
        
        print(f"⏱️  Timeout Manager initialized for {self.environment} environment")
        print(f"   Search timeout: {self.timeouts['search_operation']}ms")
        print(f"   LLM timeout: {self.timeouts['llm_generation']}ms")
    
    def _apply_overrides(self):
        """Apply environment variable overrides if present"""
        # Allow manual override via environment variables
        overrides = {
            "TILORES_TIMEOUT": "search_operation",
            "LLM_TIMEOUT": "llm_generation",
            "REDIS_TIMEOUT": "redis_connect",
        }
        
        for env_var, config_key in overrides.items():
            value = os.getenv(env_var)
            if value:
                try:
                    self.timeouts[config_key] = int(value)
                    print(f"   Override: {config_key} = {value}ms")
                except ValueError:
                    pass
    
    def get_timeout(self, operation: str) -> float:
        """
        Get timeout in seconds for an operation
        
        Args:
            operation: Operation name (e.g., 'search_operation')
            
        Returns:
            Timeout in seconds
        """
        timeout_ms = self.timeouts.get(operation, 5000)  # Default 5s
        return timeout_ms / 1000.0
    
    def get_retry_config(self) -> Dict:
        """Get retry configuration for current environment"""
        return self.retry_config.copy()
    
    def calculate_max_total_time(self, operation: str) -> float:
        """
        Calculate maximum total time including retries
        
        Args:
            operation: Operation name
            
        Returns:
            Maximum total time in seconds
        """
        timeout = self.get_timeout(operation)
        config = self.retry_config
        
        total_time = 0
        delay = config["initial_delay"]
        
        for attempt in range(config["max_retries"]):
            total_time += timeout + delay
            delay = min(delay * config["exponential_base"], config["max_delay"])
        
        return total_time
    
    def is_phone_compatible(self, operation: str) -> bool:
        """
        Check if timeout is compatible with phone UX (<2s total)
        
        Args:
            operation: Operation name
            
        Returns:
            True if compatible with phone latency requirements
        """
        max_time = self.calculate_max_total_time(operation)
        return max_time <= 2.0  # 2 second maximum for phone
    
    def optimize_for_phone(self):
        """Optimize all timeouts for phone application (aggressive)"""
        print("📱 Optimizing timeouts for phone application...")
        
        # Ultra-aggressive timeouts for phone
        phone_timeouts = {
            "tilores_init": 2000,      # 2s max
            "field_discovery": 1000,    # 1s - should be cached
            "search_operation": 1500,   # 1.5s - critical
            "llm_generation": 2000,     # 2s - use fast models
            "redis_connect": 500,       # 500ms
            "api_request": 1500,        # 1.5s
        }
        
        self.timeouts.update(phone_timeouts)
        
        # Minimal retries for phone
        self.retry_config = {
            "initial_delay": 0.1,       # 100ms
            "max_delay": 0.5,           # 500ms max
            "max_retries": 1,           # Single retry only
            "exponential_base": 2.0,
        }
        
        print("   ✅ Phone optimization applied:")
        print(f"   • Search: {self.timeouts['search_operation']}ms")
        print(f"   • LLM: {self.timeouts['llm_generation']}ms")
        print(f"   • Max retries: {self.retry_config['max_retries']}")


# Global instance
_timeout_manager = None


def get_timeout_manager() -> TimeoutManager:
    """Get or create global timeout manager"""
    global _timeout_manager
    if _timeout_manager is None:
        _timeout_manager = TimeoutManager()
    return _timeout_manager


def optimize_for_phone():
    """Global function to optimize for phone latency"""
    manager = get_timeout_manager()
    manager.optimize_for_phone()
    return manager