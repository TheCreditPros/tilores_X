#!/usr/bin/env python3
"""
Agenta.ai SDK-Based Configuration

Configures Agenta.ai features using the official SDK instead of direct API calls.
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

class AgentaSDKConfiguration:
    def __init__(self):
        """Initialize Agenta SDK configuration"""
        self.api_key = os.getenv("AGENTA_API_KEY", "your_api_key_here")
        self.host = os.getenv("AGENTA_HOST", "https://cloud.agenta.ai")
        self.app_slug = os.getenv("AGENTA_APP_SLUG", "tilores-x")
        self.sdk_available = False
        self.ag = None
        
        self._initialize_sdk()
        
        print(f"🔧 Agenta SDK Configuration:")
        print(f"  - Host: {self.host}")
        print(f"  - App Slug: {self.app_slug}")
        print(f"  - API Key: {'✅ Set' if self.api_key != 'your_api_key_here' else '❌ Missing'}")
        print(f"  - SDK Available: {'✅' if self.sdk_available else '❌'}")
    
    def _initialize_sdk(self):
        """Initialize the Agenta SDK"""
        if self.api_key == "your_api_key_here":
            print("⚠️ AGENTA_API_KEY not found in environment")
            return
        
        try:
            import agenta as ag
            ag.init(
                api_key=self.api_key,
                host=self.host
            )
            self.ag = ag
            self.sdk_available = True
            print("✅ Agenta SDK initialized successfully")
        except ImportError:
            print("⚠️ Agenta SDK not available: No module named 'agenta'")
            print("📦 Install with: pip install -U agenta")
        except Exception as e:
            print(f"⚠️ Agenta SDK initialization failed: {e}")
    
    def configure_observability(self) -> bool:
        """Configure observability and tracing"""
        if not self.sdk_available:
            print("❌ SDK not available for observability configuration")
            return False
        
        print("\n📊 Configuring Observability...")
        
        try:
            # Enable tracing for the application
            self.ag.tracing.enable()
            print("   ✅ Tracing enabled")
            
            # Configure logging
            self.ag.logging.configure(
                level="INFO",
                include_requests=True,
                include_responses=True
            )
            print("   ✅ Logging configured")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Observability configuration failed: {e}")
            return False
    
    def create_evaluation_configs(self) -> bool:
        """Create evaluation configurations using SDK"""
        if not self.sdk_available:
            print("❌ SDK not available for evaluation configuration")
            return False
        
        print("\n🧪 Creating Evaluation Configurations...")
        
        try:
            # Define evaluation configurations
            eval_configs = [
                {
                    "name": "response_quality",
                    "description": "Evaluates response quality and accuracy",
                    "evaluator_type": "custom",
                    "settings": {
                        "criteria": ["accuracy", "completeness", "professionalism"],
                        "scoring_method": "1-10"
                    }
                },
                {
                    "name": "performance_metrics",
                    "description": "Measures response time and token usage",
                    "evaluator_type": "performance",
                    "settings": {
                        "max_response_time": 15,
                        "max_tokens": 2000,
                        "timeout_threshold": 30
                    }
                }
            ]
            
            success_count = 0
            for config in eval_configs:
                try:
                    # Create evaluation configuration
                    result = self.ag.evaluations.create_config(config)
                    print(f"   ✅ {config['name']} evaluation config created")
                    success_count += 1
                except Exception as e:
                    print(f"   ❌ {config['name']} failed: {e}")
            
            print(f"📊 Evaluation Configs: {success_count}/{len(eval_configs)}")
            return success_count > 0
            
        except Exception as e:
            print(f"   ❌ Evaluation configuration failed: {e}")
            return False
    
    def setup_prompt_management(self) -> bool:
        """Set up prompt management and versioning"""
        if not self.sdk_available:
            print("❌ SDK not available for prompt management")
            return False
        
        print("\n📝 Setting Up Prompt Management...")
        
        try:
            # Load template prompts
            try:
                with open("agenta_template_prompts.json", "r") as f:
                    template_prompts = json.load(f)
            except FileNotFoundError:
                print("   ⚠️ agenta_template_prompts.json not found")
                return False
            
            success_count = 0
            for prompt_id, prompt_config in template_prompts.items():
                try:
                    # Register prompt with Agenta
                    prompt_data = {
                        "name": prompt_config.get("name", prompt_id),
                        "description": prompt_config.get("description", ""),
                        "system_prompt": prompt_config.get("system_prompt", ""),
                        "temperature": prompt_config.get("temperature", 0.7),
                        "max_tokens": prompt_config.get("max_tokens", 1500),
                        "use_case": prompt_config.get("use_case", "")
                    }
                    
                    result = self.ag.prompts.register(prompt_id, prompt_data)
                    print(f"   ✅ {prompt_config.get('name', prompt_id)} registered")
                    success_count += 1
                    
                except Exception as e:
                    print(f"   ❌ {prompt_id} failed: {e}")
            
            print(f"📊 Prompts Registered: {success_count}/{len(template_prompts)}")
            return success_count > 0
            
        except Exception as e:
            print(f"   ❌ Prompt management setup failed: {e}")
            return False
    
    def configure_deployment_environments(self) -> bool:
        """Configure deployment environments"""
        if not self.sdk_available:
            print("❌ SDK not available for deployment configuration")
            return False
        
        print("\n🚀 Configuring Deployment Environments...")
        
        try:
            environments = [
                {
                    "name": "production",
                    "description": "Production environment for live customer interactions",
                    "config": {
                        "auto_deploy": False,
                        "approval_required": True,
                        "monitoring": True
                    }
                },
                {
                    "name": "staging",
                    "description": "Staging environment for testing",
                    "config": {
                        "auto_deploy": True,
                        "approval_required": False,
                        "monitoring": True
                    }
                }
            ]
            
            success_count = 0
            for env in environments:
                try:
                    result = self.ag.deployments.create_environment(env)
                    print(f"   ✅ {env['name']} environment configured")
                    success_count += 1
                except Exception as e:
                    print(f"   ❌ {env['name']} failed: {e}")
            
            print(f"📊 Environments Configured: {success_count}/{len(environments)}")
            return success_count > 0
            
        except Exception as e:
            print(f"   ❌ Deployment configuration failed: {e}")
            return False
    
    def run_test_evaluation(self) -> bool:
        """Run a test evaluation to verify setup"""
        if not self.sdk_available:
            print("❌ SDK not available for test evaluation")
            return False
        
        print("\n🧪 Running Test Evaluation...")
        
        try:
            # Create a simple test case
            test_case = {
                "input": "What is the account status for e.j.price1986@gmail.com?",
                "expected_output": "Status information with customer details",
                "metadata": {
                    "test_type": "account_status",
                    "priority": "high"
                }
            }
            
            # Run evaluation
            result = self.ag.evaluations.run_test(test_case)
            print(f"   ✅ Test evaluation completed")
            print(f"   📊 Result: {result}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Test evaluation failed: {e}")
            return False
    
    def configure_all_features(self) -> Dict[str, bool]:
        """Configure all available SDK features"""
        print("🚀 Configuring Agenta.ai Features via SDK...")
        print("=" * 60)
        
        if not self.sdk_available:
            print("❌ Agenta SDK not available. Cannot configure features.")
            return {}
        
        results = {}
        
        # 1. Configure Observability
        results['observability'] = self.configure_observability()
        
        # 2. Set up Prompt Management
        results['prompt_management'] = self.setup_prompt_management()
        
        # 3. Create Evaluation Configurations
        results['evaluations'] = self.create_evaluation_configs()
        
        # 4. Configure Deployment Environments
        results['deployments'] = self.configure_deployment_environments()
        
        # 5. Run Test Evaluation
        results['test_evaluation'] = self.run_test_evaluation()
        
        # Summary
        print(f"\n📊 SDK FEATURES CONFIGURATION SUMMARY:")
        print("=" * 50)
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        for feature, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {feature.replace('_', ' ').title()}")
        
        print(f"\n🎯 Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
        
        if successful > 0:
            print(f"\n🎉 {successful} features configured successfully!")
            print("\n🚀 Your Agenta.ai SDK integration now includes:")
            if results.get('observability'):
                print("  ✅ Observability and tracing")
            if results.get('prompt_management'):
                print("  ✅ Prompt management and versioning")
            if results.get('evaluations'):
                print("  ✅ Evaluation configurations")
            if results.get('deployments'):
                print("  ✅ Deployment environments")
            if results.get('test_evaluation'):
                print("  ✅ Test evaluation capabilities")
        else:
            print("⚠️ No features could be configured. Check SDK installation and API key.")
        
        return results

def main():
    """Main function"""
    print("🔧 Agenta.ai SDK Configuration")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("AGENTA_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ AGENTA_API_KEY not found")
        print("🔧 Set AGENTA_API_KEY environment variable first")
        return False
    
    # Configure SDK features
    configurator = AgentaSDKConfiguration()
    results = configurator.configure_all_features()
    
    return len(results) > 0 and any(results.values())

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
