#!/usr/bin/env python3
"""
Agenta.ai Production Configuration with Best Practices
Leverages ground truth dataset and comprehensive testing framework
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class AgentaProductionConfig:
    """
    Production-ready Agenta.ai configuration using best practices
    """
    
    def __init__(self):
        """Initialize with ground truth dataset and testing configuration"""
        self.ground_truth_file = "MASTER_COMPLETE_DATA_WITH_FULL_PHONE_20250902_155645.json"
        self.testing_config_file = "tests/agenta/agenta_testing_config.json"
        self.template_prompts_file = "agenta_template_prompts.json"
        
        # Load configurations
        self.ground_truth_data = self._load_ground_truth()
        self.testing_config = self._load_testing_config()
        self.template_prompts = self._load_template_prompts()
        
        # Agenta.ai configuration
        self.agenta_config = {
            "api_key": os.getenv("AGENTA_API_KEY"),
            "host": os.getenv("AGENTA_HOST", "https://cloud.agenta.ai"),
            "app_slug": os.getenv("AGENTA_APP_SLUG", "tilores-x"),
            "environment": os.getenv("AGENTA_ENVIRONMENT", "production")
        }
    
    def _load_ground_truth(self) -> Dict[str, Any]:
        """Load ground truth dataset"""
        try:
            with open(self.ground_truth_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Ground truth file not found: {self.ground_truth_file}")
            return {}
    
    def _load_testing_config(self) -> Dict[str, Any]:
        """Load testing configuration"""
        try:
            with open(self.testing_config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Testing config file not found: {self.testing_config_file}")
            return {}
    
    def _load_template_prompts(self) -> Dict[str, Any]:
        """Load template prompts"""
        try:
            with open(self.template_prompts_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Template prompts file not found: {self.template_prompts_file}")
            return {}
    
    def generate_variant_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate Agenta.ai variant configurations with best practices
        """
        variants = {}
        
        # Base configuration for all variants
        base_config = {
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        # Generate variants for each template prompt
        for prompt_key, prompt_data in self.template_prompts.items():
            variant_name = f"{prompt_key.replace('_', '-')}-v1"
            
            variants[variant_name] = {
                **base_config,
                "system_prompt": prompt_data.get("system_prompt", ""),
                "description": prompt_data.get("description", f"Production variant for {prompt_key}"),
                "use_case": prompt_data.get("use_case", ""),
                "routing_keywords": prompt_data.get("routing_keywords", []),
                "expected_data_types": prompt_data.get("expected_data_types", []),
                "performance_target": {
                    "response_time_ms": prompt_data.get("target_response_time", 5000),
                    "accuracy_threshold": 0.85,
                    "success_rate_threshold": 0.90
                }
            }
        
        return variants
    
    def generate_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate comprehensive test cases using ground truth data
        """
        test_cases = []
        
        # Extract key data from ground truth for testing
        if self.ground_truth_data:
            customer_email = self.ground_truth_data.get("metadata", {}).get("customer_email", "e.j.price1986@gmail.com")
            customer_name = f"{self.ground_truth_data.get('customer_identity', {}).get('first_name', 'Esteban')} {self.ground_truth_data.get('customer_identity', {}).get('last_name', 'Price')}"
            
            # Credit Analysis Test Cases
            test_cases.extend([
                {
                    "name": "credit_score_query",
                    "input": f"What is the credit score for {customer_email}?",
                    "expected_variant": "credit-analysis-comprehensive-v1",
                    "expected_fields": ["customer_name", "latest_credit_score", "credit_bureau"],
                    "ground_truth": {
                        "customer_name": customer_name,
                        "customer_email": customer_email,
                        "latest_credit_score": self.ground_truth_data.get("credit_analysis", {}).get("latest_score"),
                        "has_credit_data": True
                    }
                },
                {
                    "name": "credit_improvement_query",
                    "input": f"How can {customer_email} improve their credit score?",
                    "expected_variant": "credit-analysis-comprehensive-v1",
                    "expected_fields": ["explanation", "risk_assessment"],
                    "ground_truth": {
                        "customer_name": customer_name,
                        "has_credit_data": True
                    }
                }
            ])
            
            # Account Status Test Cases
            test_cases.extend([
                {
                    "name": "account_status_query",
                    "input": f"What is the account status for {customer_email}?",
                    "expected_variant": "account-status-v1",
                    "expected_fields": ["account_status", "customer_name"],
                    "ground_truth": {
                        "customer_name": customer_name,
                        "account_status": "Active"
                    }
                }
            ])
            
            # Multi-Data Analysis Test Cases
            test_cases.extend([
                {
                    "name": "comprehensive_analysis",
                    "input": f"Give me comprehensive analysis for {customer_email}",
                    "expected_variant": "multi-data-analysis-v1",
                    "expected_fields": ["customer_name", "analysis_summary", "has_credit_data", "has_transaction_data"],
                    "ground_truth": {
                        "customer_name": customer_name,
                        "has_credit_data": True,
                        "has_transaction_data": True,
                        "total_credit_reports": self.ground_truth_data.get("credit_analysis", {}).get("total_reports"),
                        "total_transactions": self.ground_truth_data.get("transaction_analysis", {}).get("total_transactions")
                    }
                }
            ])
            
            # Transaction Analysis Test Cases
            test_cases.extend([
                {
                    "name": "payment_history_query",
                    "input": f"Show me payment history for {customer_email}",
                    "expected_variant": "transaction-analysis-v1",
                    "expected_fields": ["customer_name", "total_transactions", "total_transaction_amount"],
                    "ground_truth": {
                        "customer_name": customer_name,
                        "has_transaction_data": True,
                        "total_transactions": self.ground_truth_data.get("transaction_analysis", {}).get("total_transactions"),
                        "total_transaction_amount": self.ground_truth_data.get("transaction_analysis", {}).get("total_amount")
                    }
                }
            ])
            
            # Edge Cases
            test_cases.extend([
                {
                    "name": "invalid_customer",
                    "input": "Show data for invalid@nonexistent.com",
                    "expected_variant": "multi-data-analysis-v1",
                    "expected_fields": ["customer_found"],
                    "ground_truth": {
                        "customer_found": False
                    }
                },
                {
                    "name": "empty_query",
                    "input": "",
                    "expected_variant": "fallback-default-v1",
                    "expected_fields": ["explanation"],
                    "ground_truth": {
                        "explanation": "customer information required"
                    }
                }
            ])
        
        return test_cases
    
    def generate_evaluation_config(self) -> Dict[str, Any]:
        """
        Generate evaluation configuration using testing framework
        """
        return {
            "evaluators": [
                {
                    "name": "field_accuracy_evaluator",
                    "type": "custom",
                    "settings": {
                        "field_weights": self.testing_config.get("field_weights", {}),
                        "tolerance_settings": self.testing_config.get("tolerance_settings", {}),
                        "judge_model": self.testing_config.get("evaluation_settings", {}).get("judge_model", "gpt-4o-mini")
                    }
                },
                {
                    "name": "response_quality_evaluator",
                    "type": "llm_judge",
                    "settings": {
                        "model": "gpt-4o-mini",
                        "temperature": 0.0,
                        "criteria": [
                            "accuracy",
                            "completeness",
                            "relevance",
                            "clarity"
                        ]
                    }
                },
                {
                    "name": "performance_evaluator",
                    "type": "performance",
                    "settings": {
                        "max_response_time": 30000,
                        "min_success_rate": 0.90
                    }
                }
            ],
            "promotion_rules": self.testing_config.get("promotion_rules", {}),
            "reporting": self.testing_config.get("reporting", {})
        }
    
    def export_configuration(self) -> Dict[str, Any]:
        """
        Export complete Agenta.ai configuration
        """
        config = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "ground_truth_source": self.ground_truth_file,
                "testing_config_source": self.testing_config_file,
                "agenta_environment": self.agenta_config["environment"]
            },
            "agenta_settings": self.agenta_config,
            "variants": self.generate_variant_configs(),
            "test_cases": self.generate_test_cases(),
            "evaluation_config": self.generate_evaluation_config()
        }
        
        return config
    
    def save_configuration(self, filename: str = None) -> str:
        """
        Save configuration to file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agenta_production_config_{timestamp}.json"
        
        config = self.export_configuration()
        
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Agenta.ai production configuration saved to: {filename}")
        return filename

if __name__ == "__main__":
    # Generate production configuration
    config_manager = AgentaProductionConfig()
    config_file = config_manager.save_configuration()
    
    # Display summary
    config = config_manager.export_configuration()
    print(f"\n📊 AGENTA.AI PRODUCTION CONFIGURATION SUMMARY")
    print(f"=" * 60)
    print(f"✅ Variants configured: {len(config['variants'])}")
    print(f"✅ Test cases generated: {len(config['test_cases'])}")
    print(f"✅ Evaluators configured: {len(config['evaluation_config']['evaluators'])}")
    print(f"✅ Ground truth integration: {'✅' if config_manager.ground_truth_data else '❌'}")
    print(f"✅ Testing framework integration: {'✅' if config_manager.testing_config else '❌'}")
    print(f"\n🎯 Ready for Agenta.ai deployment!")
