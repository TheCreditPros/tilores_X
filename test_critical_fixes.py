#!/usr/bin/env python3
"""
Test Critical Fixes for QA Issues
Focus on the specific failures identified in comprehensive testing
"""

import requests
import json
import time
import subprocess

def start_server():
    """Start local server"""
    print("🚀 Starting server for critical fix testing...")
    process = subprocess.Popen(
        ["python3", "direct_credit_api_with_phone.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(4)
    return process

def make_request(messages, test_name):
    """Make a test request"""
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
            "http://localhost:8080/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            print(f"✅ {test_name}: {response.status_code} ({duration:.1f}s)")
            print(f"   📝 Response: {content[:100]}...")
            return True, duration, content
        else:
            print(f"❌ {test_name}: {response.status_code}")
            print(f"   🚨 Error: {response.text}")
            return False, duration, response.text
            
    except Exception as e:
        print(f"❌ {test_name}: Exception - {str(e)}")
        return False, 30, str(e)

def test_follow_up_queries():
    """Test the specific follow-up query failures"""
    print("\n🔍 Testing Follow-up Query Fixes...")
    
    customer_email = "e.j.price1986@gmail.com"
    
    # Test 1: Multi-turn conversation that was failing
    messages1 = [
        {"role": "system", "content": "You are a helpful customer service chatbot for TheCreditPros."},
        {"role": "user", "content": [{"type": "text", "text": f"Show me the credit profile for {customer_email}"}]}
    ]
    
    success1, duration1, response1 = make_request(messages1, "Initial Credit Profile Query")
    
    if success1:
        # Follow-up query that was failing
        messages2 = [
            {"role": "system", "content": "You are a helpful customer service chatbot for TheCreditPros."},
            {"role": "user", "content": [{"type": "text", "text": f"Show me the credit profile for {customer_email}"}]},
            {"role": "assistant", "content": response1[:500] + "..."},  # Truncated previous response
            {"role": "user", "content": [{"type": "text", "text": "What are the biggest issues I should focus on?"}]}
        ]
        
        success2, duration2, response2 = make_request(messages2, "Follow-up: Focus Areas")
        return success1 and success2, [duration1, duration2]
    
    return False, [duration1]

def test_performance_improvements():
    """Test performance improvements with caching"""
    print("\n🔍 Testing Performance Improvements...")
    
    customer_email = "e.j.price1986@gmail.com"
    
    # First request (should be slow)
    messages = [
        {"role": "system", "content": "You are a helpful customer service chatbot."},
        {"role": "user", "content": [{"type": "text", "text": f"Analyze credit for {customer_email}"}]}
    ]
    
    success1, duration1, _ = make_request(messages, "First Request (No Cache)")
    
    if success1:
        # Second identical request (should be fast due to cache)
        success2, duration2, _ = make_request(messages, "Second Request (Cached)")
        
        if success2:
            cache_improvement = duration1 - duration2
            print(f"   🚀 Cache Performance: {duration1:.1f}s → {duration2:.1f}s (saved {cache_improvement:.1f}s)")
            return True, [duration1, duration2]
    
    return False, [duration1]

def test_company_questions():
    """Test company/service questions that were misidentified"""
    print("\n🔍 Testing Company Question Handling...")
    
    test_cases = [
        "What is the current status with thecreditpros?",
        "How does TheCreditPros work?",
        "What services does the company provide?",
        "Can you help me understand your process?"
    ]
    
    results = []
    for query in test_cases:
        messages = [
            {"role": "system", "content": "You are a helpful customer service chatbot."},
            {"role": "user", "content": [{"type": "text", "text": query}]}
        ]
        
        success, duration, response = make_request(messages, f"Company Q: {query[:30]}...")
        results.append(success)
        
        # Check if response is appropriate (not trying to search for customer)
        if success and "no records found" not in response.lower():
            print(f"   ✅ Proper company response")
        elif success:
            print(f"   ⚠️  Still treating as customer search")
    
    return all(results), []

def test_rapid_sequential():
    """Test rapid sequential requests"""
    print("\n🔍 Testing Rapid Sequential Requests...")
    
    customer_email = "e.j.price1986@gmail.com"
    results = []
    durations = []
    
    for i in range(3):
        messages = [
            {"role": "user", "content": [{"type": "text", "text": f"Quick credit check {i+1} for {customer_email}"}]}
        ]
        
        success, duration, _ = make_request(messages, f"Rapid Sequential {i+1}")
        results.append(success)
        durations.append(duration)
        time.sleep(0.5)  # Small delay
    
    return all(results), durations

def main():
    """Run all critical fix tests"""
    print("🧪 CRITICAL FIXES VALIDATION TEST")
    print("="*60)
    
    server = start_server()
    
    try:
        # Test all critical fixes
        follow_up_success, follow_up_durations = test_follow_up_queries()
        performance_success, performance_durations = test_performance_improvements()
        company_success, _ = test_company_questions()
        rapid_success, rapid_durations = test_rapid_sequential()
        
        # Summary
        print("\n" + "="*60)
        print("📊 CRITICAL FIXES SUMMARY")
        print("="*60)
        
        all_tests = [follow_up_success, performance_success, company_success, rapid_success]
        success_rate = sum(all_tests) / len(all_tests) * 100
        
        print(f"✅ Follow-up Queries: {'PASS' if follow_up_success else 'FAIL'}")
        print(f"🚀 Performance/Caching: {'PASS' if performance_success else 'FAIL'}")
        print(f"🏢 Company Questions: {'PASS' if company_success else 'FAIL'}")
        print(f"⚡ Rapid Sequential: {'PASS' if rapid_success else 'FAIL'}")
        print(f"\n📈 Overall Success Rate: {success_rate:.0f}%")
        
        # Performance analysis
        all_durations = follow_up_durations + performance_durations + rapid_durations
        if all_durations:
            avg_duration = sum(all_durations) / len(all_durations)
            max_duration = max(all_durations)
            print(f"⏱️  Average Response Time: {avg_duration:.1f}s")
            print(f"⏱️  Slowest Response: {max_duration:.1f}s")
            
            if avg_duration > 15:
                print("⚠️  WARNING: Average response time still too high")
            elif avg_duration > 10:
                print("⚠️  CAUTION: Response time needs improvement")
            else:
                print("✅ Response times acceptable")
        
        print("\n" + "="*60)
        
        if success_rate >= 100:
            print("🎉 ALL CRITICAL FIXES WORKING!")
            return True
        else:
            print("🚨 SOME FIXES STILL NEEDED")
            return False
            
    finally:
        server.terminate()
        server.wait()
        print("🛑 Server stopped")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
