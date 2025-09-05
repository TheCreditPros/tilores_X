#!/usr/bin/env python3
"""
Enhanced Agenta.ai SDK Manager with Robust Fallback System and Template Prompts

Provides comprehensive prompt management with multiple fallback layers and
production-ready template prompts based on current system.
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

class EnhancedAgentaManager:
    """
    Enhanced Agenta SDK manager with robust fallback system and template prompts
    """

    def __init__(self):
        """Initialize enhanced Agenta manager"""
        self.agenta_available = AGENTA_AVAILABLE
        self.initialized = False

        # Configuration
        self.api_key = os.getenv("AGENTA_API_KEY")
        self.host = os.getenv("AGENTA_HOST", "https://cloud.agenta.ai")
        self.app_slug = os.getenv("AGENTA_APP_SLUG", "tilores-x")

        # Fallback system
        self.template_prompts_file = "agenta_template_prompts.json"
        self.local_prompts_file = "prompt_store.json"

        # Load prompts in order of preference
        self.template_prompts = self._load_template_prompts()
        self.local_prompts = self._load_local_prompts()

        # Initialize Agenta if available
        if self.agenta_available:
            self._initialize_agenta()

        print("🎯 Enhanced Agenta Manager initialized:")
        print(f"  - SDK Available: {'✅' if self.agenta_available else '❌'}")
        print(f"  - API Key: {'✅ Set' if self.api_key else '❌ Missing'}")
        print(f"  - Host: {self.host}")
        print(f"  - App Slug: {self.app_slug}")
        print(f"  - Initialized: {'✅' if self.initialized else '❌'}")
        print(f"  - Template Prompts: {len(self.template_prompts)}")
        print(f"  - Local Prompts: {len(self.local_prompts)}")

    def _initialize_agenta(self):
        """Initialize the Agenta SDK"""
        try:
            if not self.api_key:
                print("⚠️ AGENTA_API_KEY not found, using fallback prompts only")
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
            print("🔄 Will use fallback prompt system")
            self.initialized = False

    def _load_template_prompts(self) -> Dict:
        """Load production template prompts"""
        try:
            if os.path.exists(self.template_prompts_file):
                with open(self.template_prompts_file, 'r') as f:
                    templates = json.load(f)
                print(f"📁 Loaded {len(templates)} template prompts")
                return templates
            else:
                # Create default template prompts if file doesn't exist
                templates = self._create_default_template_prompts()
                self._save_template_prompts(templates)
                return templates
        except Exception as e:
            print(f"⚠️ Error loading template prompts: {e}")
            return self._create_default_template_prompts()

    def _load_local_prompts(self) -> Dict:
        """Load local custom prompts"""
        try:
            if os.path.exists(self.local_prompts_file):
                with open(self.local_prompts_file, 'r') as f:
                    local = json.load(f)
                print(f"📁 Loaded {len(local)} local prompts")
                return local
            else:
                return {}
        except Exception as e:
            print(f"⚠️ Error loading local prompts: {e}")
            return {}

    def _create_default_template_prompts(self) -> Dict:
        """Create default template prompts based on current production system"""
        return {
            "credit_analysis_comprehensive": {
                "name": "Credit Analysis - Comprehensive",
                "description": "Current production prompt for comprehensive credit analysis",
                "system_prompt": """You are a Credit Pros advisor with access to comprehensive credit data.
Analyze the provided temporal credit data to answer the user's question accurately and professionally.

Available data includes:
- Credit scores across multiple bureaus (Equifax, Experian, TransUnion) over time
- Summary parameters including utilization rates, inquiry counts, account counts, payment amounts, and delinquencies
- Historical credit report data with temporal analysis capabilities

Provide detailed insights that help customers understand their credit profile and improvement opportunities.""",
                "temperature": 0.5,
                "max_tokens": 1500,
                "use_case": "Comprehensive credit report analysis",
                "variant_slug": "credit-analysis-comprehensive-v1",
                "created_at": datetime.now().isoformat()
            },

            "multi_data_analysis": {
                "name": "Multi-Data Analysis",
                "description": "Current production prompt for multi-source data analysis",
                "system_prompt": """You are a Credit Pros advisor with access to comprehensive customer data across multiple sources.
Analyze the provided data to answer the user's question accurately and professionally.

Available data sources:
- Temporal credit data with scores, utilization, and bureau information
- Phone call history with agent interactions, call duration, and campaign data
- Transaction records with amounts, payment methods, and billing information
- Credit card data with BINs, expiration dates, and status information
- Support ticket data with categories, statuses, and resolution patterns

Provide insights that combine multiple data sources when relevant and focus on the specific question asked.""",
                "temperature": 0.6,
                "max_tokens": 2000,
                "use_case": "Multi-source customer intelligence",
                "variant_slug": "multi-data-analysis-v1",
                "created_at": datetime.now().isoformat()
            },

            "account_status": {
                "name": "Account Status Query",
                "description": "Optimized prompt for Salesforce account status queries",
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
                "use_case": "Quick account status lookups",
                "variant_slug": "account-status-v1",
                "created_at": datetime.now().isoformat()
            },

            "transaction_analysis": {
                "name": "Transaction Analysis",
                "description": "Current production prompt for transaction analysis",
                "system_prompt": """You are a Credit Pros advisor with access to transaction history data.
Analyze the provided transaction data to answer the user's question accurately and professionally.

Available data:
- Transaction records with amounts, payment methods, and billing information
- Transaction aggregation data with totals, averages, and timelines
- Payment patterns and financial behavior insights

Focus on payment patterns, transaction trends, and financial behavior insights.""",
                "temperature": 0.4,
                "max_tokens": 1200,
                "use_case": "Payment and transaction pattern analysis",
                "variant_slug": "transaction-analysis-v1",
                "created_at": datetime.now().isoformat()
            },

            "phone_call_analysis": {
                "name": "Phone Call Analysis",
                "description": "Current production prompt for call history analysis",
                "system_prompt": """You are a Credit Pros advisor with access to phone call history data.
Analyze the provided call data to answer the user's question accurately and professionally.

Available data:
- Phone call records with agents, duration, types, and campaigns
- Call aggregation data with totals, averages, and timelines
- Agent performance metrics and customer interaction patterns

Focus on call patterns, agent performance, and customer interaction insights.""",
                "temperature": 0.4,
                "max_tokens": 1200,
                "use_case": "Call history and agent performance analysis",
                "variant_slug": "phone-call-analysis-v1",
                "created_at": datetime.now().isoformat()
            },

            "fallback_default": {
                "name": "Fallback Default",
                "description": "Robust fallback prompt when Agenta.ai is unavailable",
                "system_prompt": """You are an advanced AI assistant with access to comprehensive Tilores customer data and credit analysis capabilities.

Available Tools:
- get_customer_credit_report(client_identifier): Get detailed credit reports
- compare_customer_credit_profiles(client_identifiers): Compare multiple credit profiles
- discover_tilores_fields(category): Discover available data fields
- get_field_discovery_stats(): Get field discovery statistics

You have access to 310+ customer data fields including:
- Customer Information: Names, emails, phones, addresses
- Credit Data: Scores, reports, utilization, payment history
- Transaction Data: Payments, billing, product information
- Interaction Data: Call history, support tickets, communications

When users ask about customers, credit reports, or data analysis, use the appropriate tools to provide comprehensive, professional responses.""",
                "temperature": 0.7,
                "max_tokens": 1000,
                "use_case": "General customer data analysis when specific prompts unavailable",
                "variant_slug": "fallback-default-v1",
                "created_at": datetime.now().isoformat()
            }
        }

    def _save_template_prompts(self, templates: Dict):
        """Save template prompts to file"""
        try:
            with open(self.template_prompts_file, 'w') as f:
                json.dump(templates, f, indent=2)
            print(f"💾 Saved {len(templates)} template prompts")
        except Exception as e:
            print(f"⚠️ Error saving template prompts: {e}")

    def _save_local_prompts(self):
        """Save local prompts to file"""
        try:
            with open(self.local_prompts_file, 'w') as f:
                json.dump(self.local_prompts, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving local prompts: {e}")

    def get_prompt_config(self, query_type: str, query: str = "",
                         prompt_id: str = None) -> Dict[str, Any]:
        """
        Get prompt configuration with robust fallback system

        Fallback order:
        1. Agenta.ai SDK (if available and initialized)
        2. Explicit prompt_id from template prompts
        3. Query type mapping to template prompts
        4. Local custom prompts
        5. Built-in fallback prompt

        Args:
            query_type: Type of query (status, credit, transaction, etc.)
            query: The actual user query (for context)
            prompt_id: Explicit prompt ID to use

        Returns:
            Dictionary containing prompt configuration
        """

        # 1. Try Agenta SDK first (highest priority)
        if self.initialized and self.agenta_available:
            agenta_config = self._get_agenta_config(query_type, query, prompt_id)
            if agenta_config:
                return agenta_config

        # 2. Try explicit prompt_id from templates
        if prompt_id:
            template_config = self._get_template_by_id(prompt_id)
            if template_config:
                return template_config

        # 3. Try query type mapping to templates
        template_config = self._get_template_by_query_type(query_type)
        if template_config:
            return template_config

        # 4. Try local custom prompts
        local_config = self._get_local_config(query_type)
        if local_config:
            return local_config

        # 5. Ultimate fallback
        return self._get_fallback_config()

    def _get_agenta_config(self, query_type: str, query: str,
                          prompt_id: str = None) -> Optional[Dict[str, Any]]:
        """Get configuration from Agenta SDK"""
        try:
            # Determine variant slug
            if prompt_id:
                variant_slug = prompt_id
            else:
                variant_slug = self._get_variant_slug(query_type)

            print(f"🔍 Fetching Agenta config: app={self.app_slug}, variant={variant_slug}")

            # Get configuration from Agenta registry
            config = ag.ConfigManager.get_from_registry(
                app_slug=self.app_slug,
                variant_slug=variant_slug
            )

            if config:
                print(f"✅ Retrieved Agenta config for {variant_slug}")
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

    def _get_template_by_id(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get template prompt by explicit ID"""
        for key, template in self.template_prompts.items():
            if (template.get("variant_slug") == prompt_id or
                key == prompt_id or
                template.get("name", "").lower().replace(" ", "_") == prompt_id.lower()):

                config = template.copy()
                config["source"] = "template_explicit"
                print(f"📋 Using explicit template: {template.get('name', prompt_id)}")
                return config
        return None

    def _get_template_by_query_type(self, query_type: str) -> Optional[Dict[str, Any]]:
        """Get template prompt by query type"""
        # Map query types to template keys
        type_mapping = {
            "status": "account_status",
            "credit": "credit_analysis_comprehensive",
            "transaction": "transaction_analysis",
            "phone": "phone_call_analysis",
            "multi_data": "multi_data_analysis",
            "combined": "multi_data_analysis"
        }

        template_key = type_mapping.get(query_type)
        if template_key and template_key in self.template_prompts:
            config = self.template_prompts[template_key].copy()
            config["source"] = "template_mapped"
            print(f"📋 Using template for {query_type}: {config.get('name', template_key)}")
            return config

        return None

    def _get_local_config(self, query_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration from local prompts"""
        # Try direct query type match
        if query_type in self.local_prompts:
            config = self.local_prompts[query_type].copy()
            config["source"] = "local"
            print(f"📁 Using local config for {query_type}")
            return config

        return None

    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get ultimate fallback configuration"""
        fallback = self.template_prompts.get("fallback_default")
        if fallback:
            config = fallback.copy()
            config["source"] = "fallback_template"
            print("🔄 Using template fallback prompt")
        else:
            # Hard-coded ultimate fallback
            config = {
                "source": "fallback_hardcoded",
                "system_prompt": "You are a helpful AI assistant analyzing customer data. Provide accurate, professional responses based on the available information.",
                "temperature": 0.7,
                "max_tokens": 1000,
                "variant_slug": "ultimate-fallback"
            }
            print("🔄 Using hard-coded fallback prompt")

        return config

    def _get_variant_slug(self, query_type: str) -> str:
        """Map query type to Agenta variant slug"""
        mapping = {
            "status": "account-status-v1",
            "credit": "credit-analysis-comprehensive-v1",
            "transaction": "transaction-analysis-v1",
            "phone": "phone-call-analysis-v1",
            "multi_data": "multi-data-analysis-v1",
            "combined": "multi-data-analysis-v1"
        }
        return mapping.get(query_type, "fallback-default-v1")

    def log_interaction(self, query_type: str, query: str, response: str,
                       success: bool, response_time: float, config: Dict[str, Any]):
        """Log interaction for observability"""
        try:
            if not (self.initialized and self.agenta_available):
                # Log locally if Agenta not available
                self._log_locally(query_type, query, response, success, response_time, config)
                return

            # Log to Agenta observability
            print(f"📊 Logged interaction: {query_type} ({success}) - source: {config.get('source', 'unknown')}")

        except Exception as e:
            print(f"⚠️ Failed to log interaction: {e}")

    def _log_locally(self, query_type: str, query: str, response: str,
                    success: bool, response_time: float, config: Dict[str, Any]):
        """Log interaction locally when Agenta is unavailable"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query_type": query_type,
            "success": success,
            "response_time_ms": response_time * 1000,
            "config_source": config.get("source", "unknown"),
            "variant_slug": config.get("variant_slug", "unknown")
        }

        # Simple local logging (in production, you might use a proper logging system)
        print(f"📝 Local log: {log_entry}")

    def get_available_prompts(self) -> Dict[str, Any]:
        """Get summary of all available prompts"""
        return {
            "agenta_available": self.initialized,
            "template_prompts": {key: prompt.get("name", key) for key, prompt in self.template_prompts.items()},
            "local_prompts": list(self.local_prompts.keys()),
            "total_prompts": len(self.template_prompts) + len(self.local_prompts)
        }

# Global instance
enhanced_agenta_manager = EnhancedAgentaManager()

# Convenience functions for backward compatibility
def get_prompt_for_query(query: str, query_type: str = "general", prompt_id: str = None) -> Dict:
    """Get prompt configuration for a query"""
    return enhanced_agenta_manager.get_prompt_config(query_type, query, prompt_id)

def log_prompt_performance(prompt_id: str, query: str, response: str,
                         success: bool, response_time: float):
    """Log prompt performance"""
    config = {"variant_slug": prompt_id, "source": "external"}
    enhanced_agenta_manager.log_interaction("unknown", query, response, success, response_time, config)
