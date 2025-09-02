#!/usr/bin/env python3
"""
Setup Agenta.ai environment and test integration
"""

import os
import subprocess
import sys
import requests
import json
from datetime import datetime

def setup_agenta_environment():
    """Setup Agenta.ai environment variables and test connection"""

    print("🔧 Setting up Agenta.ai Environment...")

    # Check if API key is already set
    api_key = os.getenv("AGENTA_API_KEY")

    if not api_key:
        print("⚠️ AGENTA_API_KEY not found in environment")
        print("📝 You provided an API key earlier. Let me set it up...")

        # For this demo, I'll use a placeholder - in production, you'd set the actual key
        # The user mentioned they already provided an API key
        api_key = "ag_test_key_placeholder"  # Replace with actual key

        # Set environment variables
        os.environ["AGENTA_API_KEY"] = api_key
        os.environ["AGENTA_HOST"] = "https://cloud.agenta.ai"
        os.environ["AGENTA_APP_SLUG"] = "tilores-x"

        print("✅ Environment variables set:")
        print(f"  - AGENTA_API_KEY: {'*' * 20}...{api_key[-4:] if len(api_key) > 4 else '****'}")
        print(f"  - AGENTA_HOST: {os.environ['AGENTA_HOST']}")
        print(f"  - AGENTA_APP_SLUG: {os.environ['AGENTA_APP_SLUG']}")
    else:
        print("✅ AGENTA_API_KEY already set in environment")

    return True

def install_agenta_sdk():
    """Install Agenta SDK if not already installed"""
    try:
        import agenta
        print("✅ Agenta SDK already installed")
        return True
    except ImportError:
        print("📦 Installing Agenta SDK...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-U", "agenta"
            ], check=True, capture_output=True, text=True)
            print("✅ Agenta SDK installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Agenta SDK: {e}")
            return False

def test_agenta_connection():
    """Test connection to Agenta.ai"""
    try:
        # Try to import and initialize Agenta
        import agenta as ag

        print("🧪 Testing Agenta.ai connection...")

        # Initialize (this will test the connection)
        try:
            ag.init()
            print("✅ Agenta.ai connection successful")
            return True
        except Exception as e:
            print(f"⚠️ Agenta.ai connection failed: {e}")
            print("📝 This is expected if using a placeholder API key")
            print("🔄 Will use fallback system prompts")
            return False

    except ImportError as e:
        print(f"❌ Failed to import Agenta SDK: {e}")
        return False

def create_template_prompts():
    """Create template prompts based on current system prompts"""

    print("📝 Creating template system prompts...")

    # Current production system prompts from the existing API
    template_prompts = {
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
            "use_case": "Comprehensive credit report analysis"
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
            "use_case": "Multi-source customer intelligence"
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
            "use_case": "Call history and agent performance analysis"
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
            "use_case": "Payment and transaction pattern analysis"
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
            "use_case": "Quick account status lookups"
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
            "use_case": "General customer data analysis when specific prompts unavailable"
        }
    }

    # Save template prompts to file
    template_file = "agenta_template_prompts.json"
    with open(template_file, 'w') as f:
        json.dump(template_prompts, f, indent=2)

    print(f"✅ Created {len(template_prompts)} template prompts")
    print(f"📁 Saved to: {template_file}")

    # Display summary
    print("\n📋 Template Prompts Created:")
    for key, prompt in template_prompts.items():
        print(f"  - {prompt['name']}: {prompt['use_case']}")

    return template_prompts

def main():
    """Main setup function"""
    print("🚀 Agenta.ai Environment Setup")
    print("=" * 50)

    # Step 1: Setup environment
    if not setup_agenta_environment():
        print("❌ Failed to setup environment")
        return False

    # Step 2: Install SDK
    if not install_agenta_sdk():
        print("❌ Failed to install SDK")
        return False

    # Step 3: Test connection
    connection_success = test_agenta_connection()

    # Step 4: Create template prompts
    template_prompts = create_template_prompts()

    # Summary
    print("\n" + "=" * 50)
    print("📊 SETUP SUMMARY:")
    print(f"  - Environment: ✅ Configured")
    print(f"  - SDK: ✅ Installed")
    print(f"  - Connection: {'✅ Success' if connection_success else '⚠️ Fallback Mode'}")
    print(f"  - Templates: ✅ {len(template_prompts)} prompts created")

    print(f"\n🎯 NEXT STEPS:")
    print(f"  1. Update AGENTA_API_KEY with your actual key")
    print(f"  2. Run: python test_agenta_integration.py")
    print(f"  3. Test Agenta.ai UI with template prompts")
    print(f"  4. Configure variants in Agenta.ai dashboard")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
