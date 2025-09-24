#!/usr/bin/env python3
"""
Agent Prompts - Langfuse-powered prompt management system
Integrates with Langfuse for version control, testing, and deployment of agent prompts
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Langfuse integration
try:
    from langfuse import Langfuse
    from langfuse.api.resources.prompts.types.create_prompt_request import CreatePromptRequest
    LANGFUSE_AVAILABLE = True
except ImportError:
    Langfuse = None
    LANGFUSE_AVAILABLE = False
    logging.warning("Langfuse not available - using fallback prompts")

logger = logging.getLogger(__name__)

# Fallback prompts if Langfuse is unavailable
FALLBACK_PROMPTS = {
    "zoho_cs_agent": {
        "system_prompt": """You are a Zoho Desk Customer Service Agent for The Credit Pros with access to comprehensive customer data through Tilores GraphQL API.

MANDATORY SLASH COMMANDS:
• `/cs status` - Account status, enrollment, subscription queries
• `/cs credit` - Credit scores, reports, bureau data queries
• `/cs billing` - Transaction history, payment, billing queries

If a user query does not start with a slash command, respond with available commands.

## AVAILABLE DATA SOURCES (Tilores GraphQL Schema):

### IDENTITY DATA (Personal Information):
- FIRST_NAME, LAST_NAME, EMAIL, CLIENT_ID, MIDDLE_NAME
- AGENT_USERNAME, CAMPAIGN_NAME, PRODUCT_NAME, SPOUSE_FULL_NAME

### SYSTEM DATA (Account & Business Logic):
- STATUS, ACTIVE, ENROLL_DATE, CREATED_DATE, CANCEL_DATE
- ENROLLMENT_BALANCE, NET_BALANCE_DUE, RECURRING_MONTHLY_FEE
- ENROLLMENT_FEE, COUPON_AMOUNT, DISCOUNT_AMOUNT, AMOUNT
- CURRENT_PRODUCT, CURRENT_PRODUCT_TYPE, OPPORTUNITY_ID
- KYC_STATUS, TCPA, SMS_OPT_OUT, LANGUAGE, SPANISH_SPEAKER

### TRANSACTION DATA (Payment History):
- TRANSACTION_AMOUNT, PAYMENT_METHOD, PAYMENT_START_DATE, PAYMENT_END_DATE
- LAST_APPROVED_TRANSACTION, LAST_APPROVED_TRANSACTION_AMOUNT
- LAST_FAILED_TRANSACTION, UPCOMING_SCHEDULED_PAYMENT, UPCOMING_SCHEDULED_PAYMENT_AMOUNT
- CHARGEBACK, DEBT_PAYMENT, DEBT_PAYMENT_DATE, REFUND_CONFIRMATION_SENT
- TRANSACTION_CREATED_DATE, DAYS_SINCE_LAST_APPROVED_TRANSACTION, NEXT_TRANSACTION_DATE

### CARD DATA (Payment Methods):
- CARD_NUMBER, CARD_TYPE, CARD_EXPIRED, CARD_FIRST_6_DIGIT, CARD_LAST_4
- EXPIRATION_MONTH, EXPIRATION_YEAR, BIN, INVALID_CARD

### PHONE DATA (Communication):
- PHONE_NUMBER, CALL_DURATION, CALL_START_TIME, CALL_HANGUP_TIME
- CALL_ID, CALL_TYPE, CONTACT_NEW, CONTACT_TYPE, ZOHO_CONTACT_ID

### CREDIT DATA (Bureau Reports):
- CREDIT_RESPONSE (Complete credit reports from Experian, Equifax, TransUnion)
- CREDIT_SCORE, CREDIT_SUMMARY, CREDIT_LIABILITY (tradelines)
- CREDIT_INQUIRY, CREDIT_FROZEN_STATUS, ALERT_MESSAGE

### TICKET DATA (Support History):
- TICKETNUMBER, ZOHO_ID, ZOHO_STATUS, ZOHO_EMAIL

## CRITICAL: EMAIL QUERY HANDLING - NO GRAPHQL SUGGESTIONS ALLOWED

⚠️ ABSOLUTELY CRITICAL: When processing `/cs email@domain.com` commands, you MUST provide a complete customer analysis with NO GraphQL suggestions whatsoever. Never include "GRAPHQL_QUERY:" or suggest additional queries in your response.

✅ CORRECT: Provide complete analysis in the required format
❌ WRONG: Suggest GraphQL queries or additional data requests

For email queries: Complete analysis only. No exceptions.

## RESPONSE FORMATTING:

Use third-person language ("Customer has..." not "You have...").
Format with bullet points using "•".
Structure as:

**CUSTOMER PROFILE:**
• Name: [extract from data]
• Email: [from query]
• Enrollment: [from data]
• Status: [from data]

**ANALYSIS SECTION:**
• [relevant analysis based on query type]
• For comprehensive summaries: Always include starting credit scores and current/ending credit scores for each bureau (Experian, Equifax, TransUnion)

**RECOMMENDATIONS:**
• [2-3 key actions]

Be concise but comprehensive. Use actual data from customer records.""",

        "temperature": 0.1,
        "max_tokens": 1200
    },

    "client_chat_agent": {
        "system_prompt": """You are a consumer credit advisor for The Credit Pros with access to comprehensive customer data through Tilores GraphQL API.

MANDATORY SLASH COMMANDS:
• `/client credit` - Credit scores, reports, analysis queries
• `/client status` - Account status, enrollment queries
• `/client billing` - Transaction history, payment queries

If a user query does not start with a slash command, respond with available commands.

## AVAILABLE DATA SOURCES (Tilores GraphQL Schema):

### IDENTITY DATA (Personal Information):
- FIRST_NAME, LAST_NAME, EMAIL, CLIENT_ID, MIDDLE_NAME
- AGENT_USERNAME, CAMPAIGN_NAME, PRODUCT_NAME, SPOUSE_FULL_NAME

### SYSTEM DATA (Account & Business Logic):
- STATUS, ACTIVE, ENROLL_DATE, CREATED_DATE, CANCEL_DATE
- ENROLLMENT_BALANCE, NET_BALANCE_DUE, RECURRING_MONTHLY_FEE
- ENROLLMENT_FEE, COUPON_AMOUNT, DISCOUNT_AMOUNT, AMOUNT
- CURRENT_PRODUCT, CURRENT_PRODUCT_TYPE, OPPORTUNITY_ID
- KYC_STATUS, TCPA, SMS_OPT_OUT, LANGUAGE, SPANISH_SPEAKER

### TRANSACTION DATA (Payment History):
- TRANSACTION_AMOUNT, PAYMENT_METHOD, PAYMENT_START_DATE, PAYMENT_END_DATE
- LAST_APPROVED_TRANSACTION, LAST_APPROVED_TRANSACTION_AMOUNT
- LAST_FAILED_TRANSACTION, UPCOMING_SCHEDULED_PAYMENT, UPCOMING_SCHEDULED_PAYMENT_AMOUNT
- CHARGEBACK, DEBT_PAYMENT, DEBT_PAYMENT_DATE, REFUND_CONFIRMATION_SENT
- TRANSACTION_CREATED_DATE, DAYS_SINCE_LAST_APPROVED_TRANSACTION, NEXT_TRANSACTION_DATE

### CARD DATA (Payment Methods):
- CARD_NUMBER, CARD_TYPE, CARD_EXPIRED, CARD_FIRST_6_DIGIT, CARD_LAST_4
- EXPIRATION_MONTH, EXPIRATION_YEAR, BIN, INVALID_CARD

### PHONE DATA (Communication):
- PHONE_NUMBER, CALL_DURATION, CALL_START_TIME, CALL_HANGUP_TIME
- CALL_ID, CALL_TYPE, CONTACT_NEW, CONTACT_TYPE, ZOHO_CONTACT_ID

### CREDIT DATA (Bureau Reports):
- CREDIT_RESPONSE (Complete credit reports from Experian, Equifax, TransUnion)
- CREDIT_SCORE, CREDIT_SUMMARY, CREDIT_LIABILITY (tradelines)
- CREDIT_INQUIRY, CREDIT_FROZEN_STATUS, ALERT_MESSAGE

### TICKET DATA (Support History):
- TICKETNUMBER, ZOHO_ID, ZOHO_STATUS, ZOHO_EMAIL

## INTELLIGENT DATA ORCHESTRATION

You have access to comprehensive customer data through GraphQL. Your role is to intelligently determine what information the user needs and request the appropriate data.

**WHEN TO REQUEST DATA:**
- If the query asks for specific customer information (payment methods, credit scores, account status, etc.)
- If the query requires factual data from customer records
- If you need to provide detailed analysis based on customer data

**WHEN TO RESPOND DIRECTLY:**
- For general questions about credit concepts
- For policy questions
- For simple acknowledgments

**DATA REQUEST FORMAT:**
When you need customer data, respond with exactly one of these templates - NOTHING ELSE:

```
GRAPHQL_QUERY: billing_payment
```
Use for: payment methods, transaction history, billing details

```
GRAPHQL_QUERY: credit_scores
```
Use for: credit scores, credit reports, bureau data

```
GRAPHQL_QUERY: account_status
```
Use for: enrollment status, account details, product information

```
GRAPHQL_QUERY: billing_credit_combined
```
Use for: queries that need both billing AND credit information

```
GRAPHQL_INTROSPECTION: true
```
Use for: exploring available data fields

**CRITICAL:** Output ONLY the template command. Do NOT add parameters, parentheses, entity IDs, or explanations. The system handles everything automatically.

## INTELLIGENT DATA ANALYSIS:

• Analyze patterns across ALL available data sources
• Synthesize information from transactions, account status, and credit data
• Look for meaningful changes and trends across different data sets
• Identify improvement opportunities by connecting payment history with credit scores
• Explain complex relationships between different data points

## RESPONSE FORMATTING:

Use friendly, educational tone with emojis and encouragement.
Structure responses with clear sections and bullet points.
Always start with a friendly greeting using their first name.

### Response Structure:
• Greeting with first name and encouraging tone
• ### [Relevant Section]: (with **bold** for important info)
• ### Key Insights: (analysis and explanations)
• ### Next Steps: (actionable advice and tips)

Be educational, supportive, and comprehensive. Connect data across multiple sources to provide meaningful insights.""",

        "temperature": 0.7,
        "max_tokens": 1200
    }
}


class LangfusePromptManager:
    """Langfuse-powered prompt management for agent prompts"""

    def __init__(self):
        self.client = None
        self._initialized = False
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Langfuse client with graceful degradation"""
        if not LANGFUSE_AVAILABLE:
            logger.warning("Langfuse not available - using fallback prompts")
            return

        try:
            self.client = Langfuse(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                host=os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com")
            )
            self._initialized = True
            logger.info("✅ Langfuse prompt manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ Langfuse initialization failed: {e}")
            self.client = None

    def get_prompt(self, prompt_name: str, version: Optional[str] = None,
                   fallback: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get prompt from Langfuse with fallback to local prompts

        Args:
            prompt_name: Name of the prompt in Langfuse
            version: Specific version to fetch (None for latest)
            fallback: Whether to fall back to local prompts if Langfuse fails

        Returns:
            Prompt configuration or None if not found
        """
        # Try Langfuse first
        if self._initialized and self.client:
            try:
                prompt = self.client.get_prompt(prompt_name)
                if prompt and hasattr(prompt, 'prompt'):
                    logger.info(f"✅ Loaded prompt '{prompt_name}' from Langfuse")
                    config = getattr(prompt, 'config', {}) or {}
                    return {
                        "name": getattr(prompt, 'name', prompt_name),
                        "system_prompt": prompt.prompt,
                        "config": config,
                        "temperature": config.get('temperature', 0.7),
                        "max_tokens": config.get('max_tokens', 1200),
                        "version": getattr(prompt, 'version', None),
                        "source": "langfuse"
                    }
            except Exception as e:
                logger.warning(f"⚠️ Failed to load prompt '{prompt_name}' from Langfuse: {e}")

        # Fallback to local prompts
        if fallback and prompt_name in FALLBACK_PROMPTS:
            logger.info(f"📋 Using fallback prompt for '{prompt_name}'")
            return {
                **FALLBACK_PROMPTS[prompt_name].copy(),
                "source": "fallback"
            }

        logger.error(f"❌ Prompt '{prompt_name}' not found in Langfuse or fallback")
        return None

    def create_or_update_prompt(self, prompt_name: str, prompt_data: Dict[str, Any],
                               labels: Optional[list] = None) -> bool:
        """
        Create or update a prompt in Langfuse

        Args:
            prompt_name: Name of the prompt
            prompt_data: Prompt data with system_prompt, temperature, max_tokens
            labels: Optional labels for deployment targeting

        Returns:
            Success status
        """
        if not self._initialized or not self.client:
            logger.warning("Langfuse not available - cannot create/update prompts")
            return False

        # Skip migration if not properly authenticated (will be done manually via UI)
        if not (os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")):
            logger.info(f"⏭️ Skipping prompt creation for '{prompt_name}' - no valid credentials")
            return False

        try:
            # Extract prompt components
            system_prompt = prompt_data.get("system_prompt", "")
            config = {
                "temperature": prompt_data.get("temperature", 0.7),
                "max_tokens": prompt_data.get("max_tokens", 1200)
            }

            # Create prompt in Langfuse
            # Note: create_prompt will create a new version if prompt already exists
            result = self.client.create_prompt(
                name=prompt_name,
                prompt=system_prompt,
                config=config,
                labels=labels or ["production"],
                type="text"  # Our prompts are text-based system prompts
            )

            if result:
                logger.info(f"✅ Created/updated prompt '{prompt_name}' in Langfuse")
                return True
            else:
                logger.error(f"❌ Prompt creation returned None for '{prompt_name}'")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to create/update prompt '{prompt_name}': {e}")
            return False

    def migrate_fallback_prompts(self) -> Dict[str, bool]:
        """
        Migrate all fallback prompts to Langfuse

        Returns:
            Dict mapping prompt names to success status
        """
        results = {}
        for prompt_name, prompt_data in FALLBACK_PROMPTS.items():
            success = self.create_or_update_prompt(
                prompt_name=prompt_name,
                prompt_data=prompt_data,
                labels=["production", "migrated"]
            )
            results[prompt_name] = success

        successful = sum(results.values())
        total = len(results)
        logger.info(f"✅ Migration complete: {successful}/{total} prompts migrated")
        return results


# Global prompt manager instance
_prompt_manager = None

def get_prompt_manager() -> LangfusePromptManager:
    """Get the global prompt manager instance"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = LangfusePromptManager()
    return _prompt_manager


def get_agent_prompt(agent_type: str, query_type: str = "credit") -> Optional[Dict[str, Any]]:
    """
    Get agent-specific prompt configuration from Langfuse with fallback

    Args:
        agent_type: Type of agent ("zoho_cs_agent", "client_chat_agent")
        query_type: Type of query (credit, status, etc.) - for future expansion

    Returns:
        dict: Prompt configuration with system_prompt, temperature, max_tokens, source
    """
    manager = get_prompt_manager()
    return manager.get_prompt(agent_type)


def list_available_agents() -> list:
    """List all available agent types from both Langfuse and fallback"""
    agents = set(FALLBACK_PROMPTS.keys())

    # Try to get additional agents from Langfuse
    manager = get_prompt_manager()
    if manager._initialized and manager.client:
        try:
            # This would require a method to list prompts from Langfuse
            # For now, we'll just use fallback agents
            pass
        except Exception:
            pass

    return list(agents)


def get_agent_info(agent_type: str) -> dict:
    """Get information about a specific agent"""
    agent_info = {
        "zoho_cs_agent": {
            "name": "Zoho Desk Customer Service Agent",
            "description": "Concise, bullet-point responses for CS agents in Zoho Desk",
            "use_case": "Customer service inquiries, account status checks",
            "format": "Bullet points, brief and actionable",
            "source": "langfuse"
        },
        "client_chat_agent": {
            "name": "Client-Facing Credit Advisor",
            "description": "Friendly, educational credit advisor for end users",
            "use_case": "Credit education, report analysis, improvement advice",
            "format": "Bullet points, encouraging and educational",
            "source": "langfuse"
        }
    }

    info = agent_info.get(agent_type, {})
    if not info:
        # Try to get from Langfuse if not in static info
        prompt = get_agent_prompt(agent_type)
        if prompt:
            info = {
                "name": agent_type.replace("_", " ").title(),
                "description": f"Agent prompt managed via Langfuse",
                "use_case": "Dynamic agent functionality",
                "format": "Langfuse-managed",
                "source": prompt.get("source", "unknown")
            }

    return info


def migrate_prompts_to_langfuse() -> Dict[str, bool]:
    """
    Utility function to migrate all fallback prompts to Langfuse

    Returns:
        Dict mapping prompt names to migration success status
    """
    manager = get_prompt_manager()
    return manager.migrate_fallback_prompts()


def create_migration_script():
    """
    Create a standalone script for migrating prompts to Langfuse
    This can be run manually when proper credentials are available
    """
    script_content = '''#!/usr/bin/env python3
"""
Langfuse Prompt Migration Script
Run this script to migrate agent prompts from local storage to Langfuse.

Usage:
1. Set your Langfuse credentials in environment variables:
   export LANGFUSE_PUBLIC_KEY="pk-lf-..."
   export LANGFUSE_SECRET_KEY="sk-lf-..."
   export LANGFUSE_HOST="https://us.cloud.langfuse.com"

2. Run the script:
   python migrate_prompts.py
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from agent_prompts import FALLBACK_PROMPTS, LangfusePromptManager

def main():
    print("🚀 Langfuse Prompt Migration Script")
    print("=" * 50)

    # Check environment variables
    required_vars = ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("\\nPlease set the following environment variables:")
        for var in missing_vars:
            print(f"  export {var}=\"your-value-here\"")
        return 1

    print("✅ Environment variables configured")

    # Initialize Langfuse manager
    print("\\n🔧 Initializing Langfuse connection...")
    manager = LangfusePromptManager()

    if not manager._initialized:
        print("❌ Failed to initialize Langfuse connection")
        return 1

    print("✅ Langfuse connection established")

    # Migrate prompts
    print("\\n🔄 Migrating prompts to Langfuse...")
    results = manager.migrate_fallback_prompts()

    # Report results
    successful = sum(results.values())
    total = len(results)

    print(f"\\n📊 Migration Results: {successful}/{total} prompts migrated successfully")

    if successful == total:
        print("✅ All prompts migrated successfully!")
        print("\\n💡 Next Steps:")
        print("1. Visit your Langfuse dashboard to review the migrated prompts")
        print("2. Test prompts in the Langfuse playground")
        print("3. Set up A/B testing and version control as needed")
    else:
        failed_prompts = [name for name, success in results.items() if not success]
        print(f"⚠️ Some prompts failed to migrate: {failed_prompts}")

    return 0 if successful == total else 1

if __name__ == "__main__":
    exit(main())
'''

    script_path = Path(__file__).parent / "migrate_prompts_to_langfuse.py"
    with open(script_path, 'w') as f:
        f.write(script_content)

    # Make executable
    script_path.chmod(0o755)

    print(f"✅ Migration script created: {script_path}")
    return script_path


if __name__ == "__main__":
    print("🤖 Langfuse-Powered Agent Prompt System")
    print(f"Langfuse Available: {'✅' if LANGFUSE_AVAILABLE else '❌'}")

    # Test prompt manager
    manager = get_prompt_manager()

    print("\n🤖 Available Agents:")
    for agent_type in list_available_agents():
        info = get_agent_info(agent_type)
        prompt = get_agent_prompt(agent_type)
        print(f"\n📋 {agent_type}:")
        print(f"  Name: {info.get('name', 'Unknown')}")
        print(f"  Description: {info.get('description', 'No description')}")
        print(f"  Source: {prompt.get('source', 'unknown') if prompt else 'not found'}")
        print(f"  Status: {'✅ Loaded' if prompt else '❌ Not found'}")

    # Create migration script
    print("\n🔧 Creating migration utility...")
    migration_script = create_migration_script()

    print("\n📋 Migration Instructions:")
    print("1. Set your Langfuse credentials:")
    print("   export LANGFUSE_PUBLIC_KEY='pk-lf-...'")
    print("   export LANGFUSE_SECRET_KEY='sk-lf-...'")
    print("   export LANGFUSE_HOST='https://us.cloud.langfuse.com'")
    print(f"2. Run migration script: python {migration_script.name}")
    print("3. Visit Langfuse UI to manage prompts")

    print(f"\n✅ Total agents available: {len(list_available_agents())}")
    print("💡 Prompts are now managed via Langfuse with automatic fallback support")
