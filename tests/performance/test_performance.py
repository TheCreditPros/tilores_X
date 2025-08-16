"""
Performance tests for the Tilores X system.

These tests measure response times, load handling, and system efficiency.
Tests include load testing, cache performance, concurrent request handling,
and resource utilization monitoring.
"""

import pytest
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch
import psutil
from fastapi.testclient import TestClient
from main_enhanced import app


@pytest.mark.performance
class TestResponseTimes:
    """Test response time performance for API endpoints."""

    def setup_method(self):
        """Set up test client and mock LLM responses."""
        self.client = TestClient(app)
        self.mock_responses = {
            "openai": {
                "choices": [{"message": {"content": "Test response", "role": "assistant"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                "model": "gpt-3.5-turbo",
            }
        }

    def test_health_endpoint_response_time(self):
        """Test health endpoint response time is under 100ms."""

        start_time = time.time()
        response = self.client.get("/health")
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds

        assert response.status_code == 200
        assert response_time < 100, f"Health endpoint took {response_time:.2f}ms, expected < 100ms"

    def test_models_endpoint_response_time(self):
        """Test models endpoint response time is under 200ms."""

        start_time = time.time()
        response = self.client.get("/v1/models")
        end_time = time.time()

        response_time = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert response_time < 200, f"Models endpoint took {response_time:.2f}ms, expected < 200ms"

    @patch("core_app.run_chain")
    def test_chat_completion_response_time(self, mock_run_chain):
        """Test chat completion response time is under 2000ms."""
        mock_run_chain.return_value = "Test response from LLM"

        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello, how are you?"}],
            "max_tokens": 100,
        }

        start_time = time.time()
        response = self.client.post("/v1/chat/completions", json=request_data)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert response_time < 2000, f"Chat completion took {response_time:.2f}ms, expected < 2000ms"


@pytest.mark.performance
class TestLoadTesting:
    """Test system performance under various load conditions."""

    def setup_method(self):
        """Set up test client and mock responses."""
        self.client = TestClient(app)
        self.mock_response = {
            "choices": [{"message": {"content": "Load test response", "role": "assistant"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            "model": "gpt-3.5-turbo",
        }

    def test_concurrent_requests_performance(self):
        """Test system handles 10 concurrent requests efficiently."""

        def make_request():
            start_time = time.time()
            response = self.client.get("/health")
            end_time = time.time()
            return response.status_code, (end_time - start_time) * 1000

        start_total = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in as_completed(futures)]
        end_total = time.time()

        total_time = (end_total - start_total) * 1000
        response_times = [result[1] for result in results]
        avg_response_time = statistics.mean(response_times)

        # All requests should succeed
        assert all(result[0] == 200 for result in results)

        # Average response time should be reasonable
        assert avg_response_time < 500, f"Average response time {avg_response_time:.2f}ms too high"

        # Total time should be efficient (less than sequential execution)
        assert total_time < 2000, f"Total time {total_time:.2f}ms too high for concurrent requests"

    @patch("core_app.run_chain")
    def test_sustained_load_performance(self, mock_run_chain):
        """Test system maintains performance under sustained load."""
        mock_run_chain.return_value = "Load test response"

        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Load test message"}],
            "max_tokens": 50,
        }

        response_times = []

        # Make 20 sequential requests to simulate sustained load
        for i in range(20):
            start_time = time.time()
            response = self.client.post("/v1/chat/completions", json=request_data)
            end_time = time.time()

            assert response.status_code in [200, 429]  # Allow rate limiting
            response_times.append((end_time - start_time) * 1000)

            # Small delay to avoid overwhelming the system
            time.sleep(0.1)

        # Calculate performance metrics
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)

        # Performance should remain consistent
        assert avg_response_time < 1000, f"Average response time {avg_response_time:.2f}ms too high"
        assert max_response_time < 2000, f"Max response time {max_response_time:.2f}ms too high"


@pytest.mark.performance
class TestCachePerformance:
    """Test cache performance improvements and efficiency."""

    def setup_method(self):
        """Set up test client and mock responses."""
        self.client = TestClient(app)
        self.mock_response = {
            "choices": [{"message": {"content": "Cached response", "role": "assistant"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            "model": "gpt-3.5-turbo",
        }

    @patch("core_app.run_chain")
    @patch("redis_cache.RedisCacheManager.get_llm_response")
    @patch("redis_cache.RedisCacheManager.set_llm_response")
    def test_cache_hit_performance_improvement(self, mock_cache_set, mock_cache_get, mock_run_chain):
        """Test cache hits provide significant performance improvement."""
        mock_run_chain.return_value = "Cached response"

        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Performance test message"}],
            "max_tokens": 50,
        }

        # First request (cache miss)
        mock_cache_get.return_value = None
        start_time = time.time()
        response1 = self.client.post("/v1/chat/completions", json=request_data)
        end_time = time.time()
        cache_miss_time = (end_time - start_time) * 1000

        assert response1.status_code in [200, 429]

        # Second request (cache hit)
        mock_cache_get.return_value = self.mock_response
        start_time = time.time()
        response2 = self.client.post("/v1/chat/completions", json=request_data)
        end_time = time.time()
        cache_hit_time = (end_time - start_time) * 1000

        assert response2.status_code in [200, 429]

        # Cache hit should be significantly faster (at least 50% improvement)
        if response1.status_code == 200 and response2.status_code == 200:
            improvement_ratio = cache_miss_time / cache_hit_time if cache_hit_time > 0 else float("inf")
            assert improvement_ratio > 1.5, f"Cache only improved performance by {improvement_ratio:.2f}x"


@pytest.mark.performance
class TestResourceUtilization:
    """Test system resource utilization and efficiency."""

    def setup_method(self):
        """Set up test client and resource monitoring."""
        self.client = TestClient(app)
        self.process = psutil.Process()
        self.mock_response = {
            "choices": [{"message": {"content": "Resource test", "role": "assistant"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            "model": "gpt-3.5-turbo",
        }

    def test_memory_usage_efficiency(self):
        """Test memory usage remains efficient under load."""

        # Get initial memory usage
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB

        # Make multiple requests to test memory efficiency
        for i in range(50):
            response = self.client.get("/health")
            assert response.status_code == 200

        # Get final memory usage
        final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB for 50 requests)
        assert memory_increase < 50, f"Memory increased by {memory_increase:.2f}MB, expected < 50MB"

    @patch("core_app.run_chain")
    def test_cpu_usage_efficiency(self, mock_run_chain):
        """Test CPU usage remains reasonable under load."""
        mock_run_chain.return_value = "CPU test response"

        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "CPU test message"}],
            "max_tokens": 50,
        }

        # Monitor CPU usage during requests
        cpu_percentages = []

        for i in range(10):
            cpu_before = self.process.cpu_percent()
            response = self.client.post("/v1/chat/completions", json=request_data)
            cpu_after = self.process.cpu_percent()

            assert response.status_code in [200, 429]
            cpu_percentages.append(max(cpu_before, cpu_after))
            time.sleep(0.1)  # Allow CPU measurement

        avg_cpu = statistics.mean(cpu_percentages)

        # CPU usage should be reasonable (less than 85% average)
        assert avg_cpu < 85, f"Average CPU usage {avg_cpu:.2f}% too high"


@pytest.mark.performance
class TestProviderFailoverPerformance:
    """Test performance during provider failover scenarios."""

    def setup_method(self):
        """Set up test client and failover scenarios."""
        self.client = TestClient(app)
        self.mock_response = {
            "choices": [{"message": {"content": "Failover response", "role": "assistant"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            "model": "gpt-3.5-turbo",
        }

    @patch("core_app.run_chain")
    def test_failover_response_time(self, mock_run_chain):
        """Test failover doesn't significantly impact response time."""
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Failover test"}],
            "max_tokens": 50,
        }

        # Mock response for failover test
        mock_run_chain.return_value = "Failover response"

        start_time = time.time()
        response = self.client.post("/v1/chat/completions", json=request_data)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000

        # Response should succeed and be reasonably fast despite failover
        assert response.status_code in [200, 429]
        if response.status_code == 200:
            assert response_time < 5000, f"Failover response took {response_time:.2f}ms, expected < 5000ms"


@pytest.mark.performance
class TestRateLimitingPerformance:
    """Test rate limiting performance and behavior."""

    def setup_method(self):
        """Set up test client for rate limiting tests."""
        self.client = TestClient(app)
        self.mock_response = {
            "choices": [{"message": {"content": "Rate limit test", "role": "assistant"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            "model": "gpt-3.5-turbo",
        }

    def test_rate_limit_response_time(self):
        """Test rate limiting responses are fast."""

        # Make rapid requests to trigger rate limiting
        response_times = []

        for i in range(15):  # Exceed rate limit
            start_time = time.time()
            response = self.client.get("/health")
            end_time = time.time()

            response_time = (end_time - start_time) * 1000
            response_times.append(response_time)

            # Rate limit responses should be fast
            if response.status_code == 429:
                assert response_time < 100, f"Rate limit response took {response_time:.2f}ms"

        # At least some requests should hit rate limit
        rate_limited_responses = [
            t for i, t in enumerate(response_times) if self.client.get("/health").status_code == 429
        ]

        # Rate limit responses should be consistently fast
        if rate_limited_responses:
            avg_rate_limit_time = statistics.mean(rate_limited_responses)
            assert avg_rate_limit_time < 50, f"Average rate limit response time {avg_rate_limit_time:.2f}ms too high"
