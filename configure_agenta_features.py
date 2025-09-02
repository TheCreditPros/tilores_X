#!/usr/bin/env python3
"""
Advanced Agenta.ai Features Configuration

Configures evaluators, deployments, observability, and other advanced features.
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class AgentaFeaturesConfigurator:
    def __init__(self):
        """Initialize Agenta API client with advanced features"""
        self.base_url = "https://cloud.agenta.ai/api"
        self.api_key = os.getenv("AGENTA_API_KEY", "your_api_key_here")
        self.app_slug = os.getenv("AGENTA_APP_SLUG", "tilores-x")
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'ApiKey {self.api_key}'
        }

        print(f"🔧 Advanced Agenta Configuration:")
        print(f"  - Base URL: {self.base_url}")
        print(f"  - App Slug: {self.app_slug}")
        print(f"  - API Key: {'✅ Set' if self.api_key != 'your_api_key_here' else '❌ Missing'}")

    def create_custom_evaluators(self) -> bool:
        """Create custom evaluators for response quality assessment"""
        print(f"\n🧪 Creating Custom Evaluators...")

        evaluators = [
            {
                "name": "Response_Quality_Evaluator",
                "description": "Evaluates response quality for customer service interactions",
                "type": "custom",
                "config": {
                    "criteria": [
                        "accuracy",
                        "completeness",
                        "professionalism",
                        "response_time"
                    ],
                    "scoring": "1-10",
                    "weight_accuracy": 0.4,
                    "weight_completeness": 0.3,
                    "weight_professionalism": 0.2,
                    "weight_response_time": 0.1
                }
            },
            {
                "name": "Account_Status_Accuracy",
                "description": "Validates account status query accuracy",
                "type": "exact_match",
                "config": {
                    "expected_fields": ["status", "customer", "product"],
                    "format_validation": "bullet_points",
                    "required_keywords": ["Status:", "Customer:", "Product:"]
                }
            },
            {
                "name": "Credit_Analysis_Completeness",
                "description": "Ensures credit analysis includes all required components",
                "type": "contains",
                "config": {
                    "required_sections": [
                        "CUSTOMER PROFILE",
                        "ACCOUNT INFORMATION",
                        "PRODUCT ANALYSIS",
                        "FINANCIAL ANALYSIS"
                    ],
                    "minimum_length": 500,
                    "data_validation": True
                }
            },
            {
                "name": "Performance_Benchmark",
                "description": "Measures response performance metrics",
                "type": "performance",
                "config": {
                    "max_response_time": 15,
                    "max_tokens": 2000,
                    "min_tokens": 50,
                    "timeout_threshold": 30
                }
            }
        ]

        success_count = 0
        for evaluator in evaluators:
            try:
                url = f"{self.base_url}/evaluators"
                response = requests.post(
                    url,
                    data=json.dumps(evaluator),
                    headers=self.headers,
                    timeout=30
                )

                if response.status_code in [200, 201]:
                    print(f"   ✅ {evaluator['name']} created")
                    success_count += 1
                else:
                    print(f"   ❌ {evaluator['name']} failed: {response.status_code}")

            except Exception as e:
                print(f"   ❌ {evaluator['name']} error: {e}")

        print(f"📊 Evaluators Created: {success_count}/{len(evaluators)}")
        return success_count == len(evaluators)

    def create_prompt_variants(self) -> bool:
        """Upload prompt variants via API"""
        print(f"\n📝 Creating Prompt Variants...")

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
                variant_data = {
                    "variant_name": prompt_config.get("variant_slug", prompt_id),
                    "parameters": {
                        "system_prompt": prompt_config.get("system_prompt", ""),
                        "temperature": prompt_config.get("temperature", 0.7),
                        "max_tokens": prompt_config.get("max_tokens", 1500),
                        "model": "gpt-4o-mini"
                    },
                    "description": prompt_config.get("description", ""),
                    "use_case": prompt_config.get("use_case", "")
                }

                url = f"{self.base_url}/apps/{self.app_slug}/variants"
                response = requests.post(
                    url,
                    data=json.dumps(variant_data),
                    headers=self.headers,
                    timeout=30
                )

                if response.status_code in [200, 201]:
                    print(f"   ✅ {prompt_config.get('name', prompt_id)} variant created")
                    success_count += 1
                else:
                    print(f"   ❌ {prompt_config.get('name', prompt_id)} failed: {response.status_code}")

            except Exception as e:
                print(f"   ❌ {prompt_id} error: {e}")

        print(f"📊 Variants Created: {success_count}/{len(template_prompts)}")
        return success_count > 0

    def setup_deployments(self) -> bool:
        """Configure deployment environments"""
        print(f"\n🚀 Setting Up Deployments...")

        deployments = [
            {
                "name": "production",
                "description": "Production deployment for live customer interactions",
                "environment": "production",
                "auto_deploy": False,
                "approval_required": True,
                "config": {
                    "rate_limit": 1000,
                    "timeout": 30,
                    "retry_attempts": 3,
                    "monitoring": True
                }
            },
            {
                "name": "staging",
                "description": "Staging environment for testing new variants",
                "environment": "staging",
                "auto_deploy": True,
                "approval_required": False,
                "config": {
                    "rate_limit": 100,
                    "timeout": 15,
                    "retry_attempts": 2,
                    "monitoring": True
                }
            },
            {
                "name": "development",
                "description": "Development environment for rapid iteration",
                "environment": "development",
                "auto_deploy": True,
                "approval_required": False,
                "config": {
                    "rate_limit": 50,
                    "timeout": 10,
                    "retry_attempts": 1,
                    "monitoring": False
                }
            }
        ]

        success_count = 0
        for deployment in deployments:
            try:
                url = f"{self.base_url}/apps/{self.app_slug}/deployments"
                response = requests.post(
                    url,
                    data=json.dumps(deployment),
                    headers=self.headers,
                    timeout=30
                )

                if response.status_code in [200, 201]:
                    print(f"   ✅ {deployment['name']} deployment created")
                    success_count += 1
                else:
                    print(f"   ❌ {deployment['name']} failed: {response.status_code}")

            except Exception as e:
                print(f"   ❌ {deployment['name']} error: {e}")

        print(f"📊 Deployments Created: {success_count}/{len(deployments)}")
        return success_count > 0

    def configure_observability(self) -> bool:
        """Set up logging, monitoring, and analytics"""
        print(f"\n📊 Configuring Observability...")

        observability_config = {
            "logging": {
                "enabled": True,
                "level": "INFO",
                "include_requests": True,
                "include_responses": True,
                "include_errors": True,
                "retention_days": 30
            },
            "monitoring": {
                "enabled": True,
                "metrics": [
                    "response_time",
                    "token_usage",
                    "error_rate",
                    "request_volume",
                    "user_satisfaction"
                ],
                "alerts": {
                    "response_time_threshold": 20,
                    "error_rate_threshold": 0.05,
                    "token_usage_threshold": 2500
                }
            },
            "analytics": {
                "enabled": True,
                "track_user_interactions": True,
                "track_variant_performance": True,
                "generate_reports": True,
                "report_frequency": "daily"
            }
        }

        try:
            url = f"{self.base_url}/apps/{self.app_slug}/observability"
            response = requests.post(
                url,
                data=json.dumps(observability_config),
                headers=self.headers,
                timeout=30
            )

            if response.status_code in [200, 201]:
                print(f"   ✅ Observability configured successfully")
                print(f"   📈 Logging: Enabled (30-day retention)")
                print(f"   📊 Monitoring: 5 key metrics tracked")
                print(f"   🔔 Alerts: Response time, error rate, token usage")
                print(f"   📋 Analytics: Daily reports enabled")
                return True
            else:
                print(f"   ❌ Observability configuration failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"   ❌ Observability error: {e}")
            return False

    def setup_webhooks(self) -> bool:
        """Configure webhooks for automated workflows"""
        print(f"\n🔗 Setting Up Webhooks...")

        webhooks = [
            {
                "name": "evaluation_complete",
                "description": "Triggered when test evaluation completes",
                "url": "https://tilores-x.up.railway.app/webhooks/evaluation-complete",
                "events": ["evaluation.completed", "evaluation.failed"],
                "headers": {
                    "Authorization": "Bearer webhook-secret-key",
                    "Content-Type": "application/json"
                },
                "active": True
            },
            {
                "name": "deployment_status",
                "description": "Triggered on deployment status changes",
                "url": "https://tilores-x.up.railway.app/webhooks/deployment-status",
                "events": ["deployment.started", "deployment.completed", "deployment.failed"],
                "headers": {
                    "Authorization": "Bearer webhook-secret-key",
                    "Content-Type": "application/json"
                },
                "active": True
            },
            {
                "name": "performance_alert",
                "description": "Triggered when performance thresholds are exceeded",
                "url": "https://tilores-x.up.railway.app/webhooks/performance-alert",
                "events": ["alert.performance", "alert.error_rate", "alert.token_usage"],
                "headers": {
                    "Authorization": "Bearer webhook-secret-key",
                    "Content-Type": "application/json"
                },
                "active": True
            }
        ]

        success_count = 0
        for webhook in webhooks:
            try:
                url = f"{self.base_url}/apps/{self.app_slug}/webhooks"
                response = requests.post(
                    url,
                    data=json.dumps(webhook),
                    headers=self.headers,
                    timeout=30
                )

                if response.status_code in [200, 201]:
                    print(f"   ✅ {webhook['name']} webhook created")
                    success_count += 1
                else:
                    print(f"   ❌ {webhook['name']} failed: {response.status_code}")

            except Exception as e:
                print(f"   ❌ {webhook['name']} error: {e}")

        print(f"📊 Webhooks Created: {success_count}/{len(webhooks)}")
        return success_count > 0

    def create_ab_test_experiments(self) -> bool:
        """Set up A/B testing experiments"""
        print(f"\n🧪 Creating A/B Test Experiments...")

        experiments = [
            {
                "name": "Account_Status_Response_Format",
                "description": "Test bullet points vs paragraph format for account status",
                "variants": ["account-status-v1", "account-status-v2"],
                "traffic_split": {"account-status-v1": 50, "account-status-v2": 50},
                "success_metrics": ["accuracy", "user_satisfaction", "response_time"],
                "duration_days": 14,
                "minimum_sample_size": 100
            },
            {
                "name": "Credit_Analysis_Detail_Level",
                "description": "Test comprehensive vs concise credit analysis",
                "variants": ["credit-analysis-comprehensive-v1", "credit-analysis-concise-v1"],
                "traffic_split": {"credit-analysis-comprehensive-v1": 70, "credit-analysis-concise-v1": 30},
                "success_metrics": ["completeness", "user_engagement", "token_efficiency"],
                "duration_days": 21,
                "minimum_sample_size": 200
            },
            {
                "name": "Multi_Data_Performance_Test",
                "description": "Test performance optimization for multi-data queries",
                "variants": ["multi-data-analysis-v1", "multi-data-optimized-v1"],
                "traffic_split": {"multi-data-analysis-v1": 80, "multi-data-optimized-v1": 20},
                "success_metrics": ["response_time", "accuracy", "resource_usage"],
                "duration_days": 7,
                "minimum_sample_size": 50
            }
        ]

        success_count = 0
        for experiment in experiments:
            try:
                url = f"{self.base_url}/apps/{self.app_slug}/experiments"
                response = requests.post(
                    url,
                    data=json.dumps(experiment),
                    headers=self.headers,
                    timeout=30
                )

                if response.status_code in [200, 201]:
                    print(f"   ✅ {experiment['name']} experiment created")
                    success_count += 1
                else:
                    print(f"   ❌ {experiment['name']} failed: {response.status_code}")

            except Exception as e:
                print(f"   ❌ {experiment['name']} error: {e}")

        print(f"📊 Experiments Created: {success_count}/{len(experiments)}")
        return success_count > 0

    def configure_all_features(self) -> Dict[str, bool]:
        """Configure all advanced Agenta features"""
        print("🚀 Configuring Advanced Agenta.ai Features...")
        print("=" * 60)

        results = {}

        # 1. Create Custom Evaluators
        results['evaluators'] = self.create_custom_evaluators()

        # 2. Create Prompt Variants
        results['variants'] = self.create_prompt_variants()

        # 3. Setup Deployments
        results['deployments'] = self.setup_deployments()

        # 4. Configure Observability
        results['observability'] = self.configure_observability()

        # 5. Setup Webhooks
        results['webhooks'] = self.setup_webhooks()

        # 6. Create A/B Test Experiments
        results['experiments'] = self.create_ab_test_experiments()

        # Summary
        print(f"\n📊 ADVANCED FEATURES CONFIGURATION SUMMARY:")
        print("=" * 50)

        successful = sum(1 for success in results.values() if success)
        total = len(results)

        for feature, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {feature.title()}")

        print(f"\n🎯 Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")

        if successful == total:
            print("🎉 All advanced features configured successfully!")
            print("\n🚀 Your Agenta.ai setup now includes:")
            print("  ✅ Custom evaluators for quality assessment")
            print("  ✅ Prompt variants for A/B testing")
            print("  ✅ Multi-environment deployments")
            print("  ✅ Comprehensive observability")
            print("  ✅ Automated webhook workflows")
            print("  ✅ A/B testing experiments")
        else:
            print("⚠️ Some features failed. Check API permissions and endpoints.")

        return results

def main():
    """Main function"""
    print("🔧 Advanced Agenta.ai Features Configurator")
    print("=" * 50)

    # Check API key
    api_key = os.getenv("AGENTA_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ AGENTA_API_KEY not found")
        print("🔧 Set AGENTA_API_KEY environment variable first")
        return False

    # Configure all features
    configurator = AgentaFeaturesConfigurator()
    results = configurator.configure_all_features()

    return all(results.values())

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
