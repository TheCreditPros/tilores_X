#!/usr/bin/env python3
"""
Comprehensive Stress Test for Agenta.ai Integration
Tests multi-turn conversations, edge cases, and failure scenarios
"""

import requests
import json
import time
import subprocess
import sys
from typing import List, Dict, Any

class AgentaStressTest:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.server_process = None
        self.test_results = []

    def start_local_server(self):
        """Start local server for testing"""
        print("🚀 Starting local server...")
        self.server_process = subprocess.Popen(
            ["python3", "direct_credit_api_with_phone.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(4)

        # Test server is running
        try:
            response = requests.get(f"{self.base_url}/v1", timeout=5)
            if response.status_code == 200:
                print("✅ Local server started successfully!")
                return True
        except Exception as e:
            print(f"❌ Server failed to start: {e}")
            return False

    def stop_server(self):
        """Clean up server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 Server stopped")

    def make_chat_request(self, messages: List[Dict], test_name: str) -> Dict:
        """Make a chat completion request"""
        payload = {
            "messages": messages,
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
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            duration = time.time() - start_time

            result = {
                "test_name": test_name,
                "status_code": response.status_code,
                "duration": round(duration, 2),
                "success": response.status_code == 200,
                "payload_size": len(json.dumps(payload)),
                "response_size": len(response.content)
            }

            if response.status_code == 200:
                response_data = response.json()
                content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                result["response_preview"] = content[:200] + "..." if len(content) > 200 else content
                result["has_customer_data"] = "e.j.price" in content.lower() or "credit" in content.lower()
            else:
                result["error"] = response.text

            return result

        except Exception as e:
            return {
                "test_name": test_name,
                "status_code": 0,
                "success": False,
                "error": str(e),
                "duration": 0
            }

    def test_structured_content_formats(self):
        """Test different content formats that Agenta.ai might send"""
        print("\n🔍 Testing Structured Content Formats...")

        test_cases = [
            {
                "name": "Simple String Content",
                "messages": [
                    {"role": "user", "content": "Analyze e.j.price1986@gmail.com"}
                ]
            },
            {
                "name": "Structured Content (List)",
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": "Analyze e.j.price1986@gmail.com"}]}
                ]
            },
            {
                "name": "System + User Structured",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": [{"type": "text", "text": "Who is e.j.price1986@gmail.com?"}]}
                ]
            },
            {
                "name": "Multi-block Structured Content",
                "messages": [
                    {"role": "user", "content": [
                        {"type": "text", "text": "Analyze credit for "},
                        {"type": "text", "text": "e.j.price1986@gmail.com"}
                    ]}
                ]
            }
        ]

        for test_case in test_cases:
            result = self.make_chat_request(test_case["messages"], test_case["name"])
            self.test_results.append(result)
            self.print_result(result)

    def test_multi_turn_conversations(self):
        """Test multi-turn conversation scenarios"""
        print("\n🔍 Testing Multi-Turn Conversations...")

        # Scenario 1: Valid customer, then follow-up question
        print("\n📝 Scenario 1: Valid Customer + Follow-up")

        # First message - valid customer
        messages1 = [
            {"role": "system", "content": "You are a helpful customer service chatbot."},
            {"role": "user", "content": [{"type": "text", "text": "Who is e.j.price1986@gmail.com?"}]}
        ]
        result1 = self.make_chat_request(messages1, "Multi-turn: Initial Query")
        self.test_results.append(result1)
        self.print_result(result1)

        # Second message - follow-up (this is where it failed in your test)
        messages2 = [
            {"role": "system", "content": "You are a helpful customer service chatbot."},
            {"role": "user", "content": [{"type": "text", "text": "Who is e.j.price1986@gmail.com?"}]},
            {"role": "assistant", "content": result1.get("response_preview", "Previous analysis...")},
            {"role": "user", "content": [{"type": "text", "text": "What is the current status with thecreditpros?"}]}
        ]
        result2 = self.make_chat_request(messages2, "Multi-turn: Follow-up Query")
        self.test_results.append(result2)
        self.print_result(result2)

        # Scenario 2: Invalid customer, then valid customer
        print("\n📝 Scenario 2: Invalid + Valid Customer")

        messages3 = [
            {"role": "user", "content": [{"type": "text", "text": "Analyze nonexistent@customer.com"}]}
        ]
        result3 = self.make_chat_request(messages3, "Multi-turn: Invalid Customer")
        self.test_results.append(result3)
        self.print_result(result3)

        messages4 = [
            {"role": "user", "content": [{"type": "text", "text": "Analyze nonexistent@customer.com"}]},
            {"role": "assistant", "content": result3.get("response_preview", "No records found...")},
            {"role": "user", "content": [{"type": "text", "text": "Now analyze e.j.price1986@gmail.com"}]}
        ]
        result4 = self.make_chat_request(messages4, "Multi-turn: Recovery Query")
        self.test_results.append(result4)
        self.print_result(result4)

    def test_edge_cases(self):
        """Test edge cases and error scenarios"""
        print("\n🔍 Testing Edge Cases...")

        edge_cases = [
            {
                "name": "Empty Content",
                "messages": [{"role": "user", "content": ""}]
            },
            {
                "name": "Empty Structured Content",
                "messages": [{"role": "user", "content": []}]
            },
            {
                "name": "Invalid Structured Content",
                "messages": [{"role": "user", "content": [{"type": "invalid", "data": "test"}]}]
            },
            {
                "name": "Mixed Content Types",
                "messages": [
                    {"role": "user", "content": "String content"},
                    {"role": "assistant", "content": "Response"},
                    {"role": "user", "content": [{"type": "text", "text": "Structured content"}]}
                ]
            },
            {
                "name": "Very Long Query",
                "messages": [{"role": "user", "content": "Analyze " + "e.j.price1986@gmail.com " * 50}]
            },
            {
                "name": "Special Characters",
                "messages": [{"role": "user", "content": "Analyze e.j.price1986@gmail.com with special chars: !@#$%^&*()"}]
            },
            {
                "name": "Non-existent Customer",
                "messages": [{"role": "user", "content": "Analyze fake@nonexistent.com"}]
            },
            {
                "name": "Company Name Query (Your Failure Case)",
                "messages": [{"role": "user", "content": [{"type": "text", "text": "What is the current status with thecreditpros?"}]}]
            }
        ]

        for test_case in edge_cases:
            result = self.make_chat_request(test_case["messages"], test_case["name"])
            self.test_results.append(result)
            self.print_result(result)

    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        print("\n🔍 Testing Concurrent Requests...")

        import threading
        import queue

        results_queue = queue.Queue()

        def make_concurrent_request(thread_id):
            messages = [{"role": "user", "content": f"Analyze e.j.price1986@gmail.com (thread {thread_id})"}]
            result = self.make_chat_request(messages, f"Concurrent-{thread_id}")
            results_queue.put(result)

        # Start 5 concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_concurrent_request, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Collect results
        while not results_queue.empty():
            result = results_queue.get()
            self.test_results.append(result)
            self.print_result(result)

    def test_performance_scenarios(self):
        """Test performance under different loads"""
        print("\n🔍 Testing Performance Scenarios...")

        # Test rapid sequential requests
        for i in range(3):
            messages = [{"role": "user", "content": f"Quick analysis {i} for e.j.price1986@gmail.com"}]
            result = self.make_chat_request(messages, f"Rapid-Sequential-{i}")
            self.test_results.append(result)
            self.print_result(result)
            time.sleep(0.5)  # Small delay between requests

    def print_result(self, result: Dict):
        """Print test result in a readable format"""
        status_icon = "✅" if result["success"] else "❌"
        print(f"{status_icon} {result['test_name']}: {result['status_code']} ({result.get('duration', 0)}s)")

        if not result["success"]:
            print(f"   🚨 Error: {result.get('error', 'Unknown error')}")
        elif result.get("response_preview"):
            preview = result["response_preview"][:100] + "..." if len(result["response_preview"]) > 100 else result["response_preview"]
            print(f"   📝 Response: {preview}")
            if result.get("has_customer_data"):
                print(f"   ✅ Contains customer data")

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE STRESS TEST SUMMARY")
        print("="*80)

        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - successful_tests

        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(successful_tests/total_tests*100):.1f}%")

        if failed_tests > 0:
            print(f"\n🚨 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test_name']}: {result.get('error', 'Unknown error')}")

        # Performance stats
        durations = [r.get("duration", 0) for r in self.test_results if r.get("duration")]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            print(f"\n⏱️  PERFORMANCE:")
            print(f"   Average Response Time: {avg_duration:.2f}s")
            print(f"   Slowest Response: {max_duration:.2f}s")

        print("\n" + "="*80)

    def run_all_tests(self):
        """Run the complete stress test suite"""
        print("🧪 COMPREHENSIVE AGENTA.AI STRESS TEST")
        print("="*60)

        if not self.start_local_server():
            print("❌ Cannot run tests - server failed to start")
            return False

        try:
            self.test_structured_content_formats()
            self.test_multi_turn_conversations()
            self.test_edge_cases()
            self.test_concurrent_requests()
            self.test_performance_scenarios()

            self.print_summary()

            # Return True if success rate > 80%
            success_rate = sum(1 for r in self.test_results if r["success"]) / len(self.test_results)
            return success_rate > 0.8

        finally:
            self.stop_server()

if __name__ == "__main__":
    tester = AgentaStressTest()
    success = tester.run_all_tests()

    if success:
        print("🎉 STRESS TEST PASSED - System is robust!")
        sys.exit(0)
    else:
        print("🚨 STRESS TEST FAILED - Issues need to be addressed!")
        sys.exit(1)
