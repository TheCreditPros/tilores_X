#!/usr/bin/env python3
"""
Production Endpoint Configuration

Configures all services to use production endpoints instead of localhost.
"""

import os
import json
from typing import Dict, List

class ProductionEndpointConfig:
    def __init__(self):
        """Initialize production endpoint configuration"""
        self.production_base_url = "https://tilores-x.up.railway.app"
        self.local_base_url = "http://localhost:8080"
        
        print(f"🚀 Production Endpoint Configuration")
        print(f"  - Production URL: {self.production_base_url}")
        print(f"  - Local URL: {self.local_base_url}")
    
    def get_production_endpoints(self) -> Dict[str, str]:
        """Get all production endpoints"""
        return {
            "api_base": self.production_base_url,
            "chat_completions": f"{self.production_base_url}/v1/chat/completions",
            "health": f"{self.production_base_url}/health",
            "webhook_evaluation": f"{self.production_base_url}/webhooks/evaluation-complete",
            "webhook_deployment": f"{self.production_base_url}/webhooks/deployment-status",
            "webhook_performance": f"{self.production_base_url}/webhooks/performance-alert",
            "webhook_health": f"{self.production_base_url}/webhooks/health"
        }
    
    def validate_production_endpoints(self) -> Dict[str, bool]:
        """Validate that production endpoints are accessible"""
        print(f"\n🔍 Validating Production Endpoints...")
        
        import requests
        endpoints = self.get_production_endpoints()
        results = {}
        
        for name, url in endpoints.items():
            try:
                if "webhook" in name and name != "webhook_health":
                    # Skip webhook endpoints (they require POST with specific data)
                    print(f"   ⏭️ {name}: Skipped (webhook endpoint)")
                    results[name] = True
                    continue
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ {name}: {url}")
                    results[name] = True
                else:
                    print(f"   ❌ {name}: {url} (Status: {response.status_code})")
                    results[name] = False
                    
            except Exception as e:
                print(f"   ❌ {name}: {url} (Error: {e})")
                results[name] = False
        
        return results
    
    def create_production_test_script(self) -> bool:
        """Create a test script that uses production endpoints"""
        print(f"\n📝 Creating Production Test Script...")
        
        test_script = f'''#!/usr/bin/env python3
"""
Production API Test Script

Tests the production deployment endpoints.
"""

import requests
import json
import time

class ProductionAPITest:
    def __init__(self):
        self.base_url = "{self.production_base_url}"
        self.endpoints = {{
            "health": f"{{self.base_url}}/health",
            "chat": f"{{self.base_url}}/v1/chat/completions",
            "webhook_health": f"{{self.base_url}}/webhooks/health"
        }}
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        print("🔍 Testing Health Endpoint...")
        try:
            response = requests.get(self.endpoints["health"], timeout=10)
            if response.status_code == 200:
                print("   ✅ Health endpoint working")
                return True
            else:
                print(f"   ❌ Health endpoint failed: {{response.status_code}}")
                return False
        except Exception as e:
            print(f"   ❌ Health endpoint error: {{e}}")
            return False
    
    def test_chat_endpoint(self):
        """Test chat completions endpoint"""
        print("🔍 Testing Chat Endpoint...")
        try:
            payload = {{
                "model": "gpt-4o-mini",
                "messages": [
                    {{"role": "user", "content": [
                        {{"type": "text", "text": "What is the account status for e.j.price1986@gmail.com?"}}
                    ]}}
                ],
                "temperature": 0.7
            }}
            
            response = requests.post(
                self.endpoints["chat"],
                headers={{"Content-Type": "application/json"}},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ Chat endpoint working")
                print(f"   📊 Response length: {{len(result.get('choices', [{{}}])[0].get('message', {{}}).get('content', ''))}}")
                return True
            else:
                print(f"   ❌ Chat endpoint failed: {{response.status_code}}")
                print(f"   📋 Response: {{response.text[:200]}}")
                return False
                
        except Exception as e:
            print(f"   ❌ Chat endpoint error: {{e}}")
            return False
    
    def test_webhook_health(self):
        """Test webhook health endpoint"""
        print("🔍 Testing Webhook Health...")
        try:
            response = requests.get(self.endpoints["webhook_health"], timeout=10)
            if response.status_code == 200:
                result = response.json()
                print("   ✅ Webhook health working")
                print(f"   📋 Endpoints: {{len(result.get('endpoints', []))}}")
                return True
            else:
                print(f"   ❌ Webhook health failed: {{response.status_code}}")
                return False
        except Exception as e:
            print(f"   ❌ Webhook health error: {{e}}")
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
            print(f"\\n{{test_name}}:")
            result = test_func()
            results.append((test_name, result))
        
        # Summary
        print(f"\\n📊 PRODUCTION TEST SUMMARY:")
        print("=" * 30)
        
        successful = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅" if success else "❌"
            print(f"  {{status}} {{test_name}}")
        
        print(f"\\n🎯 Success Rate: {{successful}}/{{total}} ({{successful/total*100:.1f}}%)")
        
        if successful == total:
            print("🎉 All production endpoints working!")
        else:
            print("⚠️ Some endpoints failed. Check deployment status.")
        
        return successful == total

if __name__ == "__main__":
    tester = ProductionAPITest()
    success = tester.run_all_tests()
    exit(0 if success else 1)
'''
        
        try:
            with open("test_production_endpoints.py", "w") as f:
                f.write(test_script)
            print(f"   ✅ Production test script created: test_production_endpoints.py")
            return True
        except Exception as e:
            print(f"   ❌ Failed to create test script: {e}")
            return False
    
    def update_agenta_webhooks_config(self) -> bool:
        """Update Agenta webhook configurations to use production URLs"""
        print(f"\n🔗 Updating Agenta Webhook Configuration...")
        
        webhook_config = {
            "webhooks": [
                {
                    "name": "evaluation_complete",
                    "url": f"{self.production_base_url}/webhooks/evaluation-complete",
                    "events": ["evaluation.completed", "evaluation.failed"],
                    "active": True
                },
                {
                    "name": "deployment_status", 
                    "url": f"{self.production_base_url}/webhooks/deployment-status",
                    "events": ["deployment.started", "deployment.completed", "deployment.failed"],
                    "active": True
                },
                {
                    "name": "performance_alert",
                    "url": f"{self.production_base_url}/webhooks/performance-alert",
                    "events": ["alert.performance", "alert.error_rate", "alert.token_usage"],
                    "active": True
                }
            ]
        }
        
        try:
            with open("agenta_production_webhooks.json", "w") as f:
                json.dump(webhook_config, f, indent=2)
            print(f"   ✅ Webhook configuration saved: agenta_production_webhooks.json")
            return True
        except Exception as e:
            print(f"   ❌ Failed to save webhook config: {e}")
            return False
    
    def create_environment_config(self) -> bool:
        """Create environment configuration for production"""
        print(f"\n⚙️ Creating Environment Configuration...")
        
        env_config = {
            "production": {
                "API_BASE_URL": self.production_base_url,
                "CHAT_ENDPOINT": f"{self.production_base_url}/v1/chat/completions",
                "HEALTH_ENDPOINT": f"{self.production_base_url}/health",
                "WEBHOOK_BASE": f"{self.production_base_url}/webhooks",
                "ENVIRONMENT": "production"
            },
            "development": {
                "API_BASE_URL": self.local_base_url,
                "CHAT_ENDPOINT": f"{self.local_base_url}/v1/chat/completions", 
                "HEALTH_ENDPOINT": f"{self.local_base_url}/health",
                "WEBHOOK_BASE": f"{self.local_base_url}/webhooks",
                "ENVIRONMENT": "development"
            }
        }
        
        try:
            with open("environment_config.json", "w") as f:
                json.dump(env_config, f, indent=2)
            print(f"   ✅ Environment config saved: environment_config.json")
            return True
        except Exception as e:
            print(f"   ❌ Failed to save environment config: {e}")
            return False
    
    def configure_production_setup(self) -> Dict[str, bool]:
        """Configure complete production setup"""
        print("🚀 Configuring Production Endpoint Setup...")
        print("=" * 60)
        
        results = {}
        
        # 1. Validate Production Endpoints
        endpoint_results = self.validate_production_endpoints()
        results['endpoint_validation'] = all(endpoint_results.values())
        
        # 2. Create Production Test Script
        results['test_script'] = self.create_production_test_script()
        
        # 3. Update Agenta Webhook Configuration
        results['webhook_config'] = self.update_agenta_webhooks_config()
        
        # 4. Create Environment Configuration
        results['environment_config'] = self.create_environment_config()
        
        # Summary
        print(f"\n📊 PRODUCTION SETUP SUMMARY:")
        print("=" * 50)
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        for feature, success in results.items():
            status = "✅" if success else "❌"
            feature_name = feature.replace('_', ' ').title()
            print(f"  {status} {feature_name}")
        
        print(f"\n🎯 Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
        
        if successful == total:
            print(f"\n🎉 Production setup complete!")
            print(f"\n🚀 Production Endpoints:")
            print(f"  - API Base: {self.production_base_url}")
            print(f"  - Chat API: {self.production_base_url}/v1/chat/completions")
            print(f"  - Health: {self.production_base_url}/health")
            print(f"  - Webhooks: {self.production_base_url}/webhooks/*")
            
            print(f"\n📋 Next Steps:")
            print(f"  1. Run: python3 test_production_endpoints.py")
            print(f"  2. Update Agenta.ai webhook URLs in the UI")
            print(f"  3. Test webhook integrations")
            print(f"  4. Monitor production performance")
        else:
            print(f"⚠️ Some configuration failed. Check deployment status.")
        
        return results

def main():
    """Main function"""
    print("🔧 Production Endpoint Configuration")
    print("=" * 50)
    
    configurator = ProductionEndpointConfig()
    results = configurator.configure_production_setup()
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
