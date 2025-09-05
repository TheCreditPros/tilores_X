#!/usr/bin/env python3
"""
Agenta.ai Dynamic Prompt Management System

Integrates with Agenta.ai API to dynamically manage and test prompts
based on query types and user feedback.
"""

import json
import os
import requests
from typing import Dict, Optional, List
from datetime import datetime
import hashlib

class AgentaPromptManager:
    """
    Manages dynamic prompts using Agenta.ai API for A/B testing and optimization
    """

    def __init__(self):
        """Initialize Agenta.ai prompt manager"""
        self.agenta_api_key = os.getenv("AGENTA_API_KEY")
        self.agenta_base_url = os.getenv("AGENTA_BASE_URL", "https://cloud.agenta.ai/api")
        self.agenta_app_id = os.getenv("AGENTA_APP_ID")

        # Fallback prompt store (JSON file)
        self.prompt_store_file = "prompt_store.json"
        self.prompt_cache = {}

        # Load local prompt store
        self._load_local_prompts()

        print(f"🎯 Agenta.ai Prompt Manager initialized:")
        print(f"  - API Key: {'✅ Set' if self.agenta_api_key else '❌ Missing'}")
        print(f"  - Base URL: {self.agenta_base_url}")
        print(f"  - App ID: {'✅ Set' if self.agenta_app_id else '❌ Missing'}")

    def _load_local_prompts(self):
        """Load prompts from local JSON file"""
        try:
            if os.path.exists(self.prompt_store_file):
                with open(self.prompt_store_file, 'r') as f:
                    self.prompt_cache = json.load(f)
                print(f"📁 Loaded {len(self.prompt_cache)} prompts from local store")
            else:
                # Create default prompts
                self.prompt_cache = self._get_default_prompts()
                self._save_local_prompts()
                print("📁 Created default prompt store")
        except Exception as e:
            print(f"⚠️ Error loading local prompts: {e}")
            self.prompt_cache = self._get_default_prompts()

    def _save_local_prompts(self):
        """Save prompts to local JSON file"""
        try:
            with open(self.prompt_store_file, 'w') as f:
                json.dump(self.prompt_cache, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving local prompts: {e}")

    def _get_default_prompts(self) -> Dict:
        """Get default prompt configurations"""
        return {
            "status_query": {
                "prompt_id": "status_query_v1",
                "version": "1.0",
                "system_prompt": """You are a customer service AI assistant specializing in account status queries.

**PRIMARY FOCUS**: Provide concise, accurate Salesforce account status information.

**RESPONSE FORMAT**:
• **Status**: [Active/Past Due/Canceled]
• **Customer**: [Customer Name]
• **Product**: [Current Product]
• **Enrolled**: [Enrollment Date]

**GUIDELINES**:
- Be direct and factual
- Use bullet points for clarity
- Focus on current account status only
- Avoid lengthy explanations unless requested""",
                "temperature": 0.3,
                "max_tokens": 200,
                "created_at": datetime.now().isoformat()
            },
            "credit_analysis": {
                "prompt_id": "credit_analysis_v1",
                "version": "1.0",
                "system_prompt": """You are an expert credit analyst providing comprehensive credit report analysis.

**ANALYSIS AREAS**:
1. **Credit Profile Summary**
2. **Account Information**
3. **Payment History Analysis**
4. **Credit Utilization Trends**
5. **Score Impact Factors**

**RESPONSE STYLE**:
- Professional and detailed
- Include specific data points
- Highlight key insights and trends
- Provide actionable recommendations""",
                "temperature": 0.5,
                "max_tokens": 1500,
                "created_at": datetime.now().isoformat()
            },
            "transaction_analysis": {
                "prompt_id": "transaction_analysis_v1",
                "version": "1.0",
                "system_prompt": """You are a financial transaction analyst providing detailed payment and billing analysis.

**ANALYSIS FOCUS**:
1. **Payment Patterns**
2. **Transaction History**
3. **Billing Analysis**
4. **Financial Trends**

**RESPONSE FORMAT**:
- Clear section headers
- Quantitative insights with data
- Timeline analysis
- Pattern identification""",
                "temperature": 0.4,
                "max_tokens": 1200,
                "created_at": datetime.now().isoformat()
            },
            "multi_data_analysis": {
                "prompt_id": "multi_data_v1",
                "version": "1.0",
                "system_prompt": """You are a comprehensive customer intelligence analyst with access to multiple data sources.

**DATA INTEGRATION**:
- Credit reports and scores
- Transaction and payment history
- Account and product information
- Support interactions
- Communication history

**ANALYSIS APPROACH**:
1. **Customer Overview**
2. **Cross-Data Insights**
3. **Risk Assessment**
4. **Recommendations**

**RESPONSE STYLE**:
- Holistic perspective
- Connect insights across data types
- Identify correlations and patterns
- Provide strategic recommendations""",
                "temperature": 0.6,
                "max_tokens": 2000,
                "created_at": datetime.now().isoformat()
            }
        }

    def get_prompt_for_query(self, query: str, query_type: str = "general") -> Dict:
        """
        Get the appropriate prompt configuration for a query

        Args:
            query: The user query
            query_type: Detected query type (status, credit, transaction, multi_data)

        Returns:
            Dict containing prompt configuration
        """

        # Try Agenta.ai API first
        if self.agenta_api_key and self.agenta_app_id:
            agenta_prompt = self._get_agenta_prompt(query_type, query)
            if agenta_prompt:
                return agenta_prompt

        # Fallback to local prompts
        prompt_key = self._map_query_type_to_prompt(query_type)

        if prompt_key in self.prompt_cache:
            prompt_config = self.prompt_cache[prompt_key].copy()
            prompt_config["source"] = "local"
            return prompt_config

        # Ultimate fallback
        return {
            "prompt_id": "default_v1",
            "version": "1.0",
            "system_prompt": "You are a helpful AI assistant analyzing customer data.",
            "temperature": 0.7,
            "max_tokens": 1000,
            "source": "fallback"
        }

    def _map_query_type_to_prompt(self, query_type: str) -> str:
        """Map query type to prompt key"""
        mapping = {
            "status": "status_query",
            "credit": "credit_analysis",
            "transaction": "transaction_analysis",
            "multi_data": "multi_data_analysis",
            "combined": "multi_data_analysis",
            "general": "customer_profile"
        }
        return mapping.get(query_type, "customer_profile")

    def _get_agenta_prompt(self, query_type: str, query: str) -> Optional[Dict]:
        """Get prompt from Agenta.ai API"""
        try:
            # Create experiment context
            context = {
                "query_type": query_type,
                "query_hash": hashlib.md5(query.encode()).hexdigest()[:8],
                "timestamp": datetime.now().isoformat()
            }

            # Call Agenta.ai API
            headers = {
                "Authorization": f"Bearer {self.agenta_api_key}",
                "Content-Type": "application/json"
            }

            # Get prompt configuration from Agenta.ai
            response = requests.post(
                f"{self.agenta_base_url}/apps/{self.agenta_app_id}/prompt",
                json={
                    "query_type": query_type,
                    "context": context
                },
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Got prompt from Agenta.ai: {query_type}")
                return {
                    "prompt_id": result.get("prompt_id", f"agenta_{query_type}"),
                    "version": result.get("version", "1.0"),
                    "system_prompt": result.get("system_prompt", ""),
                    "temperature": result.get("temperature", 0.7),
                    "max_tokens": result.get("max_tokens", 1000),
                    "source": "agenta",
                    "experiment_id": result.get("experiment_id")
                }
            else:
                print(f"⚠️ Agenta.ai API error: {response.status_code}")
                return None

        except Exception as e:
            print(f"⚠️ Agenta.ai request failed: {e}")
            return None

    def log_prompt_performance(self, prompt_id: str, query: str, response: str,
                             success: bool, response_time: float):
        """Log prompt performance back to Agenta.ai"""
        try:
            if not (self.agenta_api_key and self.agenta_app_id):
                return

            headers = {
                "Authorization": f"Bearer {self.agenta_api_key}",
                "Content-Type": "application/json"
            }

            # Log performance metrics
            performance_data = {
                "prompt_id": prompt_id,
                "query": query,
                "response_length": len(response),
                "success": success,
                "response_time_ms": response_time * 1000,
                "timestamp": datetime.now().isoformat()
            }

            requests.post(
                f"{self.agenta_base_url}/apps/{self.agenta_app_id}/metrics",
                json=performance_data,
                headers=headers,
                timeout=3
            )

            print(f"📊 Logged performance for prompt: {prompt_id}")

        except Exception as e:
            print(f"⚠️ Failed to log performance: {e}")

    def update_prompt(self, prompt_id: str, new_prompt: str, version: str = None):
        """Update a prompt configuration"""
        try:
            # Update local cache
            for key, prompt_config in self.prompt_cache.items():
                if prompt_config.get("prompt_id") == prompt_id:
                    prompt_config["system_prompt"] = new_prompt
                    if version:
                        prompt_config["version"] = version
                    prompt_config["updated_at"] = datetime.now().isoformat()
                    break

            self._save_local_prompts()

            # Update Agenta.ai if available
            if self.agenta_api_key and self.agenta_app_id:
                headers = {
                    "Authorization": f"Bearer {self.agenta_api_key}",
                    "Content-Type": "application/json"
                }

                requests.put(
                    f"{self.agenta_base_url}/apps/{self.agenta_app_id}/prompts/{prompt_id}",
                    json={
                        "system_prompt": new_prompt,
                        "version": version or "updated"
                    },
                    headers=headers,
                    timeout=5
                )

            print(f"✅ Updated prompt: {prompt_id}")

        except Exception as e:
            print(f"⚠️ Failed to update prompt: {e}")

# Global instance
prompt_manager = AgentaPromptManager()
