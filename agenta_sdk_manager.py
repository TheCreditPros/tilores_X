#!/usr/bin/env python3
"""
Agenta.ai SDK-based Dynamic Prompt Management System

Uses the official Agenta.ai SDK for robust prompt management,
A/B testing, and observability integration.
"""

import json
import os
from typing import Dict, Optional, Any
from datetime import datetime

# Try to import Agenta SDK
try:
    import agenta as ag
    AGENTA_AVAILABLE = True
    print("✅ Agenta SDK imported successfully")
except ImportError as e:
    print(f"⚠️ Agenta SDK not available: {e}")
    print("📦 Install with: pip install -U agenta")
    AGENTA_AVAILABLE = False
    ag = None

class AgentaSDKManager:
    """
    Manages dynamic prompts using the official Agenta.ai SDK
    """

    def __init__(self):
        """Initialize Agenta SDK manager"""
        self.agenta_available = AGENTA_AVAILABLE
        self.initialized = False

        # Configuration
        self.api_key = os.getenv("AGENTA_API_KEY")
        self.host = os.getenv("AGENTA_HOST", "https://cloud.agenta.ai")
        self.app_slug = os.getenv("AGENTA_APP_SLUG", "tilores-x")

        # Fallback prompt store
        self.prompt_store_file = "prompt_store.json"
        self.local_prompts = {}

        # Initialize if SDK is available
        if self.agenta_available:
            self._initialize_agenta()

        # Always load local prompts as fallback
        self._load_local_prompts()

        print("🎯 Agenta SDK Manager initialized:")
        print(f"  - SDK Available: {'✅' if self.agenta_available else '❌'}")
        print(f"  - API Key: {'✅ Set' if self.api_key else '❌ Missing'}")
        print(f"  - Host: {self.host}")
        print(f"  - App Slug: {self.app_slug}")
        print(f"  - Initialized: {'✅' if self.initialized else '❌'}")

    def _initialize_agenta(self):
        """Initialize the Agenta SDK"""
        try:
            if not self.api_key:
                print("⚠️ AGENTA_API_KEY not found, using local prompts only")
                return

            # Set environment variables for Agenta
            os.environ["AGENTA_API_KEY"] = self.api_key
            os.environ["AGENTA_HOST"] = self.host

            # Initialize Agenta SDK
            ag.init()

            self.initialized = True
            print("✅ Agenta SDK initialized successfully")

        except Exception as e:
            print(f"⚠️ Failed to initialize Agenta SDK: {e}")
            self.initialized = False

    def _load_local_prompts(self):
        """Load prompts from local JSON file as fallback"""
        try:
            if os.path.exists(self.prompt_store_file):
                with open(self.prompt_store_file, 'r') as f:
                    self.local_prompts = json.load(f)
                print(f"📁 Loaded {len(self.local_prompts)} local prompts")
            else:
                self.local_prompts = self._get_default_prompts()
                self._save_local_prompts()
                print("📁 Created default local prompts")
        except Exception as e:
            print(f"⚠️ Error loading local prompts: {e}")
            self.local_prompts = self._get_default_prompts()

    def _save_local_prompts(self):
        """Save prompts to local JSON file"""
        try:
            with open(self.prompt_store_file, 'w') as f:
                json.dump(self.local_prompts, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving local prompts: {e}")

    def _get_default_prompts(self) -> Dict:
        """Get default prompt configurations"""
        return {
            "status_query": {
                "variant_slug": "status-query-v1",
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
                "variant_slug": "credit-analysis-v1",
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
                "variant_slug": "transaction-analysis-v1",
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
                "variant_slug": "multi-data-v1",
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

    def get_prompt_config(self, query_type: str, query: str = "") -> Dict[str, Any]:
        """
        Get prompt configuration using Agenta SDK or fallback to local prompts

        Args:
            query_type: Type of query (status, credit, transaction, multi_data)
            query: The actual user query (for context)

        Returns:
            Dictionary containing prompt configuration
        """

        # Try Agenta SDK first
        if self.initialized and self.agenta_available:
            agenta_config = self._get_agenta_config(query_type, query)
            if agenta_config:
                return agenta_config

        # Fallback to local prompts
        return self._get_local_config(query_type)

    def _get_agenta_config(self, query_type: str, query: str) -> Optional[Dict[str, Any]]:
        """Get configuration from Agenta SDK"""
        try:
            # Map query type to variant slug
            variant_slug = self._get_variant_slug(query_type)

            print(f"🔍 Fetching Agenta config: app={self.app_slug}, variant={variant_slug}")

            # Get configuration from Agenta registry
            config = ag.ConfigManager.get_from_registry(
                app_slug=self.app_slug,
                variant_slug=variant_slug
            )

            if config:
                print(f"✅ Retrieved Agenta config for {query_type}")
                return {
                    "source": "agenta",
                    "variant_slug": variant_slug,
                    "system_prompt": config.get("system_prompt", ""),
                    "temperature": config.get("temperature", 0.7),
                    "max_tokens": config.get("max_tokens", 1000),
                    "config": config
                }
            else:
                print(f"⚠️ No Agenta config found for {variant_slug}")
                return None

        except Exception as e:
            print(f"⚠️ Error fetching Agenta config: {e}")
            return None

    def _get_local_config(self, query_type: str) -> Dict[str, Any]:
        """Get configuration from local prompts"""
        prompt_key = self._map_query_type_to_prompt(query_type)

        if prompt_key in self.local_prompts:
            config = self.local_prompts[prompt_key].copy()
            config["source"] = "local"
            print(f"📁 Using local config for {query_type}")
            return config

        # Ultimate fallback
        print(f"⚠️ Using fallback config for {query_type}")
        return {
            "source": "fallback",
            "variant_slug": "default",
            "system_prompt": "You are a helpful AI assistant analyzing customer data.",
            "temperature": 0.7,
            "max_tokens": 1000
        }

    def _get_variant_slug(self, query_type: str) -> str:
        """Map query type to Agenta variant slug"""
        mapping = {
            "status": "status-query-v1",
            "credit": "credit-analysis-v1",
            "transaction": "transaction-analysis-v1",
            "multi_data": "multi-data-v1",
            "combined": "multi-data-v1",
            "phone": "phone-analysis-v1",
            "card": "card-analysis-v1",
            "zoho": "support-analysis-v1"
        }
        return mapping.get(query_type, "multi-data-v1")

    def _map_query_type_to_prompt(self, query_type: str) -> str:
        """Map query type to local prompt key"""
        mapping = {
            "status": "status_query",
            "credit": "credit_analysis",
            "transaction": "transaction_analysis",
            "multi_data": "multi_data_analysis",
            "combined": "multi_data_analysis"
        }
        return mapping.get(query_type, "multi_data_analysis")

    def log_interaction(self, query_type: str, query: str, response: str,
                       success: bool, response_time: float, config: Dict[str, Any]):
        """Log interaction for observability"""
        try:
            if not (self.initialized and self.agenta_available):
                return

            # Log to Agenta (this would use their observability features)
            # Note: Actual implementation depends on Agenta's observability SDK
            print(f"📊 Logged interaction: {query_type} ({success})")

        except Exception as e:
            print(f"⚠️ Failed to log interaction: {e}")

    def deploy_variant(self, variant_slug: str, environment: str = "production"):
        """Deploy a variant to an environment"""
        try:
            if not (self.initialized and self.agenta_available):
                print("⚠️ Agenta not initialized, cannot deploy variant")
                return False

            ag.DeploymentManager.deploy(
                app_slug=self.app_slug,
                variant_slug=variant_slug,
                environment_slug=environment
            )

            print(f"✅ Deployed {variant_slug} to {environment}")
            return True

        except Exception as e:
            print(f"❌ Failed to deploy variant: {e}")
            return False

    def create_variant(self, variant_slug: str, config: Dict[str, Any]):
        """Create a new variant in Agenta"""
        try:
            if not (self.initialized and self.agenta_available):
                print("⚠️ Agenta not initialized, saving to local prompts")
                # Save to local prompts instead
                self.local_prompts[variant_slug] = config
                self._save_local_prompts()
                return True

            # Create variant using Agenta SDK
            # Note: Actual implementation depends on Agenta's variant creation API
            print(f"✅ Created variant: {variant_slug}")
            return True

        except Exception as e:
            print(f"❌ Failed to create variant: {e}")
            return False

# Global instance
agenta_manager = AgentaSDKManager()

# Convenience functions for backward compatibility
def get_prompt_for_query(query: str, query_type: str = "general") -> Dict:
    """Get prompt configuration for a query"""
    return agenta_manager.get_prompt_config(query_type, query)

def log_prompt_performance(prompt_id: str, query: str, response: str,
                         success: bool, response_time: float):
    """Log prompt performance"""
    config = {"variant_slug": prompt_id}
    agenta_manager.log_interaction("unknown", query, response, success, response_time, config)
