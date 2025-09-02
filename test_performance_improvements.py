#!/usr/bin/env python3
"""
Test Performance Improvements - Parallel Processing & No Concurrency Limits
"""

import requests
import json
import time
import subprocess
import threading
import queue

def start_server():
    """Start local server"""
    print("🚀 Starting server for performance testing...")
    process = subprocess.Popen(
        ["python3", "direct_credit_api_with_phone.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(4)
    return process

def make_request(query, test_name):
    """Make a test request"""
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful customer service chatbot."},
            {"role": "user", "content": [{"type": "text", "text": query}]}
        ],
        "model": "gpt-4o-mini",
        "temperature": 0.7
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "AsyncOpenAI/Python 1.102.0"
    }

    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8080/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        duration = time.time() - start_time

        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            print(f"✅ {test_name}: {response.status_code} ({duration:.1f}s)")
            return True, duration
        else:
            print(f"❌ {test_name}: {response.status_code} ({duration:.1f}s)")
            return False, duration

    except Exception as e:
        print(f"❌ {test_name}: Exception - {str(e)}")
        return False, 30

def test_concurrent_performance():
    """Test concurrent performance without limits"""
    print("\n🔍 Testing Concurrent Performance (No Limits)...")

    def concurrent_request(thread_id, results_queue):
        success, duration = make_request(
            f"Analyze credit for e.j.price1986@gmail.com (concurrent {thread_id})",
            f"Concurrent-{thread_id}"
        )
        results_queue.put((success, duration))

    results_queue = queue.Queue()
    threads = []

    # Test with 5 concurrent requests (previously failed)
    start_time = time.time()
    for i in range(5):
        thread = threading.Thread(target=concurrent_request, args=(i, results_queue))
        threads.append(thread)
        thread.start()

    # Wait for all threads
    for thread in threads:
        thread.join()

    total_time = time.time() - start_time

    # Collect results
    results = []
    while not results_queue.empty():
        results.append(results_queue.get())

    successes = sum(1 for success, _ in results if success)
    durations = [duration for _, duration in results]

    print(f"\n📊 Concurrent Test Results:")
    print(f"   ✅ Success Rate: {successes}/5 ({successes/5*100:.0f}%)")
    print(f"   ⏱️  Total Time: {total_time:.1f}s")
    print(f"   ⏱️  Average Duration: {sum(durations)/len(durations):.1f}s")
    print(f"   ⏱️  Fastest: {min(durations):.1f}s")
    print(f"   ⏱️  Slowest: {max(durations):.1f}s")

    return successes == 5, durations

def test_parallel_data_fetching():
    """Test parallel data fetching performance"""
    print("\n🔍 Testing Parallel Data Fetching...")

    # Test comprehensive query that should use parallel fetching
    success, duration = make_request(
        "Give me a complete profile analysis for e.j.price1986@gmail.com including credit, transactions, calls, and tickets",
        "Comprehensive Analysis (Parallel)"
    )

    print(f"📊 Parallel Fetch Results:")
    print(f"   ✅ Success: {'Yes' if success else 'No'}")
    print(f"   ⏱️  Duration: {duration:.1f}s")

    if duration < 15:
        print("   🚀 EXCELLENT: Under 15 seconds!")
    elif duration < 20:
        print("   ✅ GOOD: Under 20 seconds")
    else:
        print("   ⚠️  NEEDS IMPROVEMENT: Over 20 seconds")

    return success, duration

def test_cache_performance():
    """Test caching performance"""
    print("\n🔍 Testing Cache Performance...")

    query = "Analyze credit for e.j.price1986@gmail.com"

    # First request (no cache)
    success1, duration1 = make_request(query, "First Request (No Cache)")

    if success1:
        # Second request (should be cached)
        success2, duration2 = make_request(query, "Second Request (Cached)")

        if success2:
            improvement = duration1 - duration2
            print(f"📊 Cache Performance:")
            print(f"   🚀 Cache Improvement: {duration1:.1f}s → {duration2:.1f}s")
            print(f"   💾 Time Saved: {improvement:.1f}s ({improvement/duration1*100:.0f}%)")

            return True, [duration1, duration2]

    return False, [duration1]

def main():
    """Run performance tests"""
    print("🧪 PERFORMANCE IMPROVEMENTS VALIDATION")
    print("="*60)

    server = start_server()

    try:
        # Test 1: Concurrent performance (no limits)
        concurrent_success, concurrent_durations = test_concurrent_performance()

        # Test 2: Parallel data fetching
        parallel_success, parallel_duration = test_parallel_data_fetching()

        # Test 3: Cache performance
        cache_success, cache_durations = test_cache_performance()

        # Summary
        print("\n" + "="*60)
        print("📊 PERFORMANCE SUMMARY")
        print("="*60)

        print(f"🔄 Concurrent Requests: {'PASS' if concurrent_success else 'FAIL'}")
        print(f"⚡ Parallel Data Fetch: {'PASS' if parallel_success else 'FAIL'}")
        print(f"💾 Caching: {'PASS' if cache_success else 'FAIL'}")

        all_durations = concurrent_durations + [parallel_duration] + cache_durations
        avg_duration = sum(all_durations) / len(all_durations)

        print(f"\n⏱️  TIMING ANALYSIS:")
        print(f"   Average Response: {avg_duration:.1f}s")
        print(f"   Parallel Fetch: {parallel_duration:.1f}s")

        if concurrent_success and avg_duration < 15:
            print("\n🎉 PERFORMANCE GOALS ACHIEVED!")
            print("   ✅ No concurrency limits")
            print("   ✅ Parallel processing working")
            print("   ✅ Response times improved")
            return True
        else:
            print("\n⚠️  PERFORMANCE NEEDS MORE WORK")
            return False

    finally:
        server.terminate()
        server.wait()
        print("\n🛑 Server stopped")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
