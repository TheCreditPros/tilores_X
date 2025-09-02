#!/usr/bin/env python3
"""
Production API Test Script

Tests the production deployment endpoints.
"""

import requests
import json
import time

class ProductionAPITest:
    def __init__(self):
        self.base_url = "https://tilores-x.up.railway.app"
        self.endpoints = {
            "health": f"{self.base_url}/health",
            "chat": f"{self.base_url}/v1/chat/completions",
            "webhook_health": f"{self.base_url}/webhooks/health"
        }
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        print("🔍 Testing Health Endpoint...")
        try:
            response = requests.get(self.endpoints["health"], timeout=10)
            if response.status_code == 200:
                print("   ✅ Health endpoint working")
                return True
            else:
                print(f"   ❌ Health endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Health endpoint error: {e}")
            return False
    
    def test_chat_endpoint(self):
        """Test chat completions endpoint"""
        print("🔍 Testing Chat Endpoint...")
        try:
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": [
                        {"type": "text", "text": "What is the account status for e.j.price1986@gmail.com?"}
                    ]}
                ],
                "temperature": 0.7
            }
            
            response = requests.post(
                self.endpoints["chat"],
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ Chat endpoint working")
                print(f"   📊 Response length: {len(result.get('choices', [{}])[0].get('message', {}).get('content', ''))}")
                return True
            else:
                print(f"   ❌ Chat endpoint failed: {response.status_code}")
                print(f"   📋 Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"   ❌ Chat endpoint error: {e}")
            return False
    
    def test_webhook_health(self):
        """Test webhook health endpoint"""
        print("🔍 Testing Webhook Health...")
        try:
            response = requests.get(self.endpoints["webhook_health"], timeout=10)
            if response.status_code == 200:
                result = response.json()
                print("   ✅ Webhook health working")
                print(f"   📋 Endpoints: {len(result.get('endpoints', []))}")
                return True
            else:
                print(f"   ❌ Webhook health failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Webhook health error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all production tests"""
        print("🚀 Running Production API Tests")
        print("=" * 50)
        
        tests = [
            ("Health Endpoint", self.test_health_endpoint),
            ("Chat Endpoint", self.test_chat_endpoint),
            ("Webhook Health", self.test_webhook_health)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n{test_name}:")
            result = test_func()
            results.append((test_name, result))
        
        # Summary
        print(f"\n📊 PRODUCTION TEST SUMMARY:")
        print("=" * 30)
        
        successful = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}")
        
        print(f"\n🎯 Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
        
        if successful == total:
            print("🎉 All production endpoints working!")
        else:
            print("⚠️ Some endpoints failed. Check deployment status.")
        
        return successful == total

if __name__ == "__main__":
    tester = ProductionAPITest()
    success = tester.run_all_tests()
    exit(0 if success else 1)
