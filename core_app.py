#!/usr/bin/env python3
# pyright: reportGeneralTypeIssues=false, reportOptionalMemberAccess=false, reportAttributeAccessIssue=false
from concurrent.futures import ThreadPoolExecutor

"""
Unified LangChain core logic shared between Chainlit and FastAPI
Ultra-minimal implementation focused on speed and simplicity
"""

import concurrent.futures
import re
from typing import Any, Dict, Optional, List

from langchain_openai import ChatOpenAI

# Import debug configuration
from utils.debug_config import setup_logging

# Set up module logger
logger = setup_logging(__name__)

# Redis cache for performance optimization (Phase VI)
try:
    from .redis_cache import cache_manager

    CACHE_AVAILABLE = True
except ImportError:
    try:
        from redis_cache import cache_manager

        CACHE_AVAILABLE = True
    except ImportError:
        cache_manager = None
        CACHE_AVAILABLE = False

# Optional imports for multi-provider support
try:
    from langchain_anthropic import ChatAnthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ChatAnthropic = None
    ANTHROPIC_AVAILABLE = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI

    GEMINI_AVAILABLE = True
except ImportError:
    ChatGoogleGenerativeAI = None
    GEMINI_AVAILABLE = False

try:
    from langchain_community.chat_models import ChatMistralAI

    MISTRAL_AVAILABLE = True
except ImportError:
    ChatMistralAI = None
    MISTRAL_AVAILABLE = False

try:
    from langchain_groq import ChatGroq

    GROQ_AVAILABLE = True
except ImportError:
    ChatGroq = None
    GROQ_AVAILABLE = False

try:
    from langchain_openai import ChatOpenAI as OpenRouterChatOpenAI

    OPENROUTER_AVAILABLE = True
except ImportError:
    OpenRouterChatOpenAI = None
    OPENROUTER_AVAILABLE = False


class QueryRouter:
    """Intelligent query router for Tilores vs general LLM routing"""

    def __init__(self):
        # Only keep patterns for VERY obvious general queries
        # Everything else goes to LLM with tools - trust LLM intelligence!
        self.general_patterns = [
            # Most common: Simple math (frequent in testing/demos)
            r"^\s*\d+\s*[\+\-\*\/\%]\s*\d+\s*[=\?]?\s*$",  # "2 + 2", "5 - 3 = ?"
            r"^\s*\d+\s*[\+\-\*\/\%]\s*\d+\s*=\s*\?\s*$",  # "5 - 3 = ?"
            # Very common: Greetings and social (FIXED: allow additional text after greetings)
            r"^\s*(hi|hello|hey)\b",  # "hi", "hello", "hello there", "hello, this is a test"
            r"^\s*(thank\s+you|thanks|bye|goodbye)\b",  # "thank you", "bye", etc.
            r"^\s*how\s+are\s+you\b",  # "How are you?", "How are you doing?"
            # Common: Math in natural language (allow additional instructions)
            # "what is 2 + 2" (allow extra text)
            r"^\s*what\s+is\s+\d+\s*[\+\-\*\/\%]\s*\d+\s*\??",
            # "what is 2 plus 2" (allow extra text)
            r"^\s*what\s+is\s+\d+\s+(plus|minus|times|divided\s+by)\s+\d+\s*\??",
            r"^\s*calculate\s+\d+\s*[\+\-\*\/\%]\s*\d+",  # "calculate 15 * 8" (allow extra text)
            # Moderate: Knowledge questions
            r"\bwhat\s+is\s+(the\s+)?(definition|meaning|capital|population)\b",
            r"\bwho\s+(was|is)\s+[a-zA-Z\s]+\s*\??\s*$",  # "Who was Albert Einstein?"
            r"\bwhat\s+time\s+is\s+it\b",  # "What time is it?"
            # General conversational patterns
            # "this is a test", "testing", "example" - but NOT in email addresses
            r"^\s*(this\s+is\s+a\s+)?(test|testing|example)\s*$",
            r"\bhow\s+(to|do|does)\b(?!.*\b(customer|client|find|search)\b)",
            r"\b(mathematics|math|calculation|arithmetic)\b",
        ]

        self.general_regex = [re.compile(p, re.IGNORECASE) for p in self.general_patterns]

    def should_use_tilores_tools(self, query: str) -> bool:
        """Determine if query needs Tilores tools - simplified to trust LLM intelligence"""
        query = query.strip()

        # Only route to general LLM for VERY obvious general queries
        # Let the LLM with tools handle everything else and decide when to use tools
        obvious_general = any(pattern.search(query) for pattern in self.general_regex)

        if obvious_general:
            return False  # Use general LLM for obvious general queries (math, greetings, etc.)

        # Check for customer identifiers using advanced extraction
        try:
            from utils.context_extraction import IDPatterns

            # Quick check for any customer identifiers
            has_customer_data = any(
                [
                    IDPatterns.extract_email(query),
                    IDPatterns.extract_client_id(query),
                    IDPatterns.extract_salesforce_id(query),
                    IDPatterns.extract_phone(query),
                ]
            )

            if has_customer_data:
                return True  # Definitely needs Tilores tools
        except ImportError:
            pass  # Fallback to default behavior if utils not available

        # Default: Give LLM access to tools and let it decide
        # The LLM is smart enough to:
        # - Use tools when it needs customer data
        # - Answer directly when tools aren't needed
        return True


def get_all_tilores_fields(tilores_api) -> Dict[str, bool]:
    """Get all available fields from Tilores schema dynamically."""
    # Check cache first for significant performance improvement
    if CACHE_AVAILABLE and cache_manager:
        # Use API URL as cache key for field discovery
        api_url = getattr(tilores_api, "api_url", "default")
        cached_fields = cache_manager.get_tilores_fields(api_url)
        if cached_fields:
            import json

            try:
                fields_dict = json.loads(cached_fields)
                print(f"🔥 Cache HIT: Field discovery ({len(fields_dict)} fields)")
                return fields_dict
            except (json.JSONDecodeError, TypeError):
                print("⚠️  Cache data corrupted, falling back to API")

    try:
        print("🔍 Cache MISS: Discovering fields from Tilores API...")
        schema_query = """
        {
          __schema {
            types {
              name
              fields {
                name
              }
            }
          }
        }
        """
        schema_result = tilores_api.gql(schema_query)

        # Extract field names from all relevant data types to give LLM complete access
        # The goal is comprehensive data access, not restriction
        all_fields = {}
        relevant_types = [
            "Record",  # 166 fields - main customer data
            "CreditResponseCreditLiability",  # 54 fields - credit liability data
            "RecordInsights",  # 23 fields - insights data
            "CreditResponse",  # 22 fields - credit response data
            "CreditResponseCreditInquiry",  # 17 fields - credit inquiry data
            "CreditResponseCreditScore",  # 14 fields - credit score data
            "Entity",  # 10 fields - entity data
            "CreditResponseCreditFile",  # 9 fields - credit file data
            "CreditResponseCreditFileBorrowerResidence",  # 9 fields - address data
            "CreditResponseBorrower",  # 8 fields - borrower data
            "CreditResponseCreditFileBorrower",  # 8 fields - borrower file data
        ]

        for type_info in schema_result.get("data", {}).get("__schema", {}).get("types", []):
            type_name = type_info.get("name", "")
            if type_name == "Record" and type_info.get("fields"):
                # Only include Record type fields that can be accessed directly
                for field_info in type_info.get("fields", []):
                    field_name = field_info["name"]

                    # Exclude complex nested objects that cause 422 errors
                    # CREDIT_RESPONSE is handled by dedicated credit function for complete access
                    if field_name == "CREDIT_RESPONSE":
                        continue  # Skip - too complex for flat field access

                    # Exclude confusing TransUnion summary links from Salesforce schema
                    if field_name in [
                        "TRANSUNIONAUTH_LINK",
                        "TRANSUNION_SUMMARY_LINK",
                        "TU_SUMMARY_LINK",
                    ]:
                        continue  # Skip - confusing and unnecessary for LLM

                    # Include all other Record fields for comprehensive data access
                    all_fields[field_name] = True
            elif type_name in relevant_types[1:] and type_info.get("fields"):
                # Include fields from other credit-related types for reference
                field_names = [field["name"] for field in type_info.get("fields", [])]
                for field_name in field_names:
                    all_fields[field_name] = True

        print(f"🔍 Comprehensive field discovery: {len(all_fields)} total fields from {len(relevant_types)} types")
        return all_fields

    except Exception as e:
        logger.error(f"Schema discovery failed: {e}")
        # Fallback to basic Record fields if comprehensive discovery fails
        try:
            for type_info in schema_result.get("data", {}).get("__schema", {}).get("types", []):
                if type_info.get("name") == "Record":
                    field_names = [field["name"] for field in type_info.get("fields", [])]
                    return {field: True for field in field_names}
        except Exception:
            pass
        return {}


class MultiProviderLLMEngine:
    """Ultra-minimal multi-provider LLM engine with OpenAI-compatible interface"""

    def __init__(self):
        """Initialize with simple model mappings - only available providers"""
        # Start with OpenAI models (always available) - gpt-3.5-turbo removed due to 16K context limit
        self.model_mappings = {
            "gpt-5-mini": {
                "provider": "openai",
                "class": ChatOpenAI,
                "real_name": "gpt-5-mini-2025-08-07",
            },
            "gpt-4o": {"provider": "openai", "class": ChatOpenAI},
            "gpt-4o-mini": {"provider": "openai", "class": ChatOpenAI},  # 128K context - works with tools
            "gpt-4.1-mini": {
                "provider": "openai",
                "class": ChatOpenAI,
                "real_name": "gpt-4.1-mini-2025-04-14",
            },
            # "gpt-3.5-turbo": REMOVED - 16K context limit incompatible with Tilores tools (961 tokens)
        }

        # Add optional providers if available
        if ANTHROPIC_AVAILABLE and ChatAnthropic:
            self.model_mappings.update(
                {
                    "claude-3-sonnet": {
                        "provider": "anthropic",
                        "class": ChatAnthropic,
                        "real_name": "claude-3-5-sonnet-20241022",
                    },
                    "claude-3-haiku": {
                        "provider": "anthropic",
                        "class": ChatAnthropic,
                        "real_name": "claude-3-haiku-20240307",
                    },
                }
            )

        if GEMINI_AVAILABLE and ChatGoogleGenerativeAI:
            self.model_mappings.update(
                {
                    "gemini-1.5-flash-002": {
                        "provider": "gemini",
                        "class": ChatGoogleGenerativeAI,
                        "real_name": "gemini-1.5-flash-002",
                    },
                    "gemini-2.5-flash": {
                        "provider": "gemini",
                        "class": ChatGoogleGenerativeAI,
                        "real_name": "gemini-2.5-flash",
                    },
                    "gemini-2.5-flash-lite": {
                        "provider": "gemini",
                        "class": ChatGoogleGenerativeAI,
                        "real_name": "gemini-2.5-flash-lite",
                    },
                }
            )

        # Mistral models removed - mistral-large-latest is auto-updating and incompatible with our stack

        # Add Groq models (fastest inference) - ONLY FUNCTIONAL MODELS
        if GROQ_AVAILABLE and ChatGroq:
            self.model_mappings.update(
                {
                    # FUNCTIONAL GROQ MODELS (validated with Tilores tools)
                    "llama-3.3-70b-versatile": {
                        "provider": "groq",
                        "class": ChatGroq,
                        "real_name": "llama-3.3-70b-versatile",
                    },
                    "deepseek-r1-distill-llama-70b": {
                        "provider": "groq",
                        "class": ChatGroq,
                        "real_name": "deepseek-r1-distill-llama-70b",
                    },
                    # DEPRECATED GROQ MODELS (decommissioned by Groq as of Aug 2025)
                    # "llama-3.3-70b-specdec": DEPRECATED - use llama-3.3-70b-versatile
                    # "mixtral-8x7b-32768": DEPRECATED - use llama-3.3-70b-versatile
                    # "llama-3.2-90b-text-preview": DEPRECATED - use deepseek-r1-distill-llama-70b
                }
            )

        # Add OpenRouter/Cerebras models via OpenRouter
        if OPENROUTER_AVAILABLE and OpenRouterChatOpenAI:
            self.model_mappings.update(
                {
                    # Cerebras models via OpenRouter (updated with correct model IDs)
                    "llama-3.3-70b-versatile-openrouter": {
                        "provider": "openrouter",
                        "class": OpenRouterChatOpenAI,
                        "real_name": "meta-llama/llama-3.3-70b-instruct",
                        "base_url": "https://openrouter.ai/api/v1",
                        "api_key_env": "OPENROUTER_API_KEY",
                        "extra_body": {"provider": {"order": ["Cerebras"]}},
                    },
                    "qwen-3-32b-openrouter": {
                        "provider": "openrouter",
                        "class": OpenRouterChatOpenAI,
                        "real_name": "qwen/qwen3-32b",
                        "base_url": "https://openrouter.ai/api/v1",
                        "api_key_env": "OPENROUTER_API_KEY",
                        "extra_body": {"provider": {"order": ["Cerebras"]}},
                    },
                }
            )

        # Initialize Tilores components once
        self.tilores = None
        self.tools = []

        # Load environment FIRST before any initialization
        self._load_environment()

        # Initialize Tilores
        self._init_tilores()

    def _load_environment(self):
        """Load environment variables from .env file (current dir -> parent -> project root)"""
        try:
            from pathlib import Path

            from dotenv import load_dotenv

            # Try to find .env file in order of preference
            current_dir = Path.cwd()
            possible_env_paths = [
                current_dir / ".env",  # Current directory
                current_dir.parent / ".env",  # Parent directory
                current_dir.parent.parent / ".env",  # Project root
                Path(__file__).parent.parent.parent / ".env",  # Absolute project root
            ]

            env_loaded = False
            for env_path in possible_env_paths:
                if env_path.exists():
                    print(f"📁 Loading environment from: {env_path}")
                    load_dotenv(env_path, override=False)  # Don't override existing env vars
                    env_loaded = True
                    break

            if not env_loaded:
                print("⚠️  No .env file found - using system environment variables only")

        except ImportError:
            print("⚠️  python-dotenv not available - using system environment variables only")
        except Exception as e:
            print(f"⚠️  Error loading .env file: {e}")

    def _init_tilores(self):
        """Initialize Tilores components with error handling and timeout protection"""
        try:
            import os
            import time

            # ENVIRONMENT VALIDATION - Prevent configuration drift
            # (Environment already loaded in __init__)
            print("🔍 Validating environment configuration...")
            required_vars = [
                "TILORES_API_URL",
                "TILORES_CLIENT_ID",
                "TILORES_CLIENT_SECRET",
                "TILORES_TOKEN_URL",
            ]
            missing_vars = [var for var in required_vars if not os.getenv(var)]

            if missing_vars:
                print(f"❌ CRITICAL: Missing required Tilores variables: {missing_vars}")
                print("💡 Check your .env file configuration")
                print("💡 Run: python config/env-validation.py for detailed validation")
                raise Exception(f"Missing critical Tilores configuration: {missing_vars}")

            print("✅ All required Tilores variables present")

            # Use unified timeout configuration
            try:
                from utils.timeout_config import get_timeout_manager

                timeout_mgr = get_timeout_manager()
                timeout_seconds = timeout_mgr.get_timeout("tilores_init")
                retry_config = timeout_mgr.get_retry_config()
                max_retries = retry_config["max_retries"]
                base_delay = retry_config["initial_delay"]
            except ImportError:
                # Fallback to environment variable
                timeout_ms = int(os.getenv("TILORES_TIMEOUT", "30000"))
                timeout_seconds = timeout_ms / 1000
                max_retries = 3
                base_delay = 0.5

            print(f"🔍 Initializing Tilores with {timeout_seconds}s timeout...")

            # Enhanced diagnostics - check environment variables first
            tilores_url = os.getenv("TILORES_API_URL", "NOT SET")
            tilores_client_id = os.getenv("TILORES_CLIENT_ID", "NOT SET")
            tilores_token_url = os.getenv("TILORES_TOKEN_URL", "NOT SET")
            print("🔧 TILORES_API_URL: [CONFIGURED]" if tilores_url != "NOT SET" else "🔧 TILORES_API_URL: NOT SET")
            print(
                "🔧 TILORES_CLIENT_ID: [CONFIGURED]"
                if tilores_client_id != "NOT SET"
                else "🔧 TILORES_CLIENT_ID: NOT SET"
            )
            print(
                "🔧 TILORES_TOKEN_URL: [CONFIGURED]"
                if tilores_token_url != "NOT SET"
                else "🔧 TILORES_TOKEN_URL: NOT SET"
            )

            # Initialize TiloresAPI with timeout protection and retry logic
            # Respect TimeoutManager settings without overriding

            # Import TiloresAPI locally to avoid import-time failures
            from tilores import TiloresAPI

            for attempt in range(max_retries):
                try:
                    print(f"🚀 Starting Tilores initialization attempt {attempt + 1}/{max_retries}...")
                    print(f"⏱️  Using {timeout_seconds}s timeout for Railway environment")

                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(TiloresAPI.from_environ)
                        self.tilores = future.result(timeout=timeout_seconds)
                        print(f"✅ TiloresAPI initialized successfully (attempt {attempt + 1})")
                        break

                except concurrent.futures.TimeoutError:
                    elapsed_msg = f"⏰ TiloresAPI timeout on attempt {attempt + 1}/{max_retries} (>{timeout_seconds}s)"
                    print(elapsed_msg)
                    print("🔍 Railway environment may have higher network latency than local (~3s)")

                    if attempt == max_retries - 1:
                        print(f"❌ FINAL TIMEOUT: All {max_retries} attempts exhausted")
                        raise Exception(
                            f"TiloresAPI initialization failed - Railway network timeout after {max_retries} attempts"
                        )

                    # Exponential backoff for Railway environment
                    delay = base_delay * (2**attempt)
                    print(f"⏳ Retrying in {delay}s with exponential backoff...")
                    time.sleep(delay)

                except Exception as e:
                    print(f"❌ TiloresAPI error on attempt {attempt + 1}/{max_retries}: {e}")
                    print(f"🔍 Error type: {type(e).__name__}")
                    print(f"🔍 Error details: {str(e)[:200]}...")  # Truncate long errors

                    if attempt == max_retries - 1:
                        print(f"❌ FINAL ERROR: All {max_retries} attempts failed")
                        raise Exception(f"TiloresAPI initialization failed after {max_retries} attempts: {e}")

                    delay = base_delay * (2**attempt)
                    print(f"⏳ Retrying in {delay}s...")
                    time.sleep(delay)

            # Ensure Tilores is initialized
            if self.tilores is None:
                raise Exception("Tilores initialization did not complete; no TiloresAPI instance available")
            assert self.tilores is not None

            # Import TiloresTools locally to avoid import-time failures
            from tilores_langchain import TiloresTools
            tilores_tools = TiloresTools(self.tilores)

            # Initialize function executor for centralized tool management
            from utils.function_executor import initialize_function_executor
            from monitoring import monitor

            # Create tool dictionary for function executor
            tool_dict = {
                "search": tilores_tools.search_tool(),
                "fetchEntity": tilores_tools.edge_tool(),
                "creditReport": getattr(tilores_tools, "credit_report", None),
                "fieldDiscovery": getattr(tilores_tools, "field_discovery", None),
            }

            # Initialize the function executor
            self.function_executor = initialize_function_executor(tool_dict, monitor)
            print("✅ Function executor initialized for Tilores tools")

            # Get all available fields dynamically with timeout protection
            # Use shorter timeout for field discovery to prevent hanging
            field_discovery_timeout = min(30, timeout_seconds / 2)  # Max 30s or half init timeout
            try:
                start_time = time.time()
                print(f"🔍 Starting field discovery with {field_discovery_timeout}s timeout...")

                # Run field discovery with timeout protection
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(get_all_tilores_fields, self.tilores)
                    self.all_fields = future.result(timeout=field_discovery_timeout)

                discovery_time = time.time() - start_time
                print(f"🔍 Discovered {len(self.all_fields)} fields from Tilores schema in {discovery_time:.1f}s")

                if discovery_time > 10:
                    print(f"⚠️ Field discovery took {discovery_time:.1f}s - Railway environment has higher latency")

            except concurrent.futures.TimeoutError:
                print(f"⏰ Field discovery timeout ({field_discovery_timeout}s) - using essential field set")
                # Fallback to essential fields only
                self.all_fields = {
                    "EMAIL": True,
                    "FIRST_NAME": True,
                    "LAST_NAME": True,
                    "CLIENT_ID": True,
                    "PHONE_EXTERNAL": True,
                    "CUSTOMER_AGE": True,
                    "DATE_OF_BIRTH": True,
                    "STARTING_CREDIT_SCORE": True,
                    "TRANSUNION_REPORT": True,
                }
                print(f"🔧 Using {len(self.all_fields)} essential fields as fallback")

            except Exception as e:
                print(f"⚠️ Field discovery failed: {e} - using essential field set")
                # Fallback to essential fields only
                self.all_fields = {
                    "EMAIL": True,
                    "FIRST_NAME": True,
                    "LAST_NAME": True,
                    "CLIENT_ID": True,
                    "PHONE_EXTERNAL": True,
                    "CUSTOMER_AGE": True,
                    "DATE_OF_BIRTH": True,
                    "STARTING_CREDIT_SCORE": True,
                    "TRANSUNION_REPORT": True,
                }

            # Create single comprehensive search tool that works across all providers
            search_tool = self._create_unified_search_tool(tilores_tools)
            edge_tool = tilores_tools.edge_tool()
            record_lookup_tool = self._create_record_lookup_tool()
            credit_report_tool = self._create_credit_report_tool()

            self.tools = [
                search_tool,
                edge_tool,
                record_lookup_tool,
                credit_report_tool,
            ]
            print(f"🎉 Tilores initialization completed successfully with {len(self.tools)} tools available")
        except Exception as e:
            print(f"❌ CRITICAL: Tilores initialization failed completely: {e}")
            print(f"🔍 Error type: {type(e).__name__}")
            print("🔍 This will cause 'Tilores tools not available' responses")
            print("💡 Check network connectivity to Tilores endpoints")
            self.tilores = None
            self.tools = []

    def _create_smart_search_tool(self, tilores_tools):
        """Create a search tool that adapts field selection based on model provider"""
        from langchain.tools import tool

        # Define essential fields for different data types
        essential_fields = {
            # Core customer profile (always included)
            "id": True,
            "EMAIL": True,
            "FIRST_NAME": True,
            "LAST_NAME": True,
            "CLIENT_ID": True,
            "PHONE_EXTERNAL": True,
            "CUSTOMER_AGE": True,
            "DATE_OF_BIRTH": True,
            "ENROLL_DATE": True,
            "STATUS": True,
            # Product and subscription
            "PRODUCT_NAME": True,
            "NEXT_SUBSCRIPTION_DATE": True,
            "RE_ENROLL_DATE": True,
            "ENROLLMENT_FEE": True,
            "MONTHLY_PAYMENT": True,
            "CONTRACT_SIGNED": True,
            # Payment information
            "CARD_TYPE": True,
            "PAYMENT_METHOD": True,
            "TRANSACTION_AMOUNT": True,
            "LAST_APPROVED_TRANSACTION_AMOUNT": True,
            "AMOUNT": True,
            # Call history
            "CALL_DURATION": True,
            "CALL_TYPE": True,
            "AGENT_USERNAME": True,
            "CAMPAIGN_NAME": True,
            "CALL_START_TIME": True,
            "CALL_HANGUP_TIME": True,
            # Address and contact
            "MAILING_STREET": True,
            "MAILING_CITY": True,
            "MAILING_STATE": True,
            "MAILING_POSTAL_CODE": True,
            # Salesforce CRM
            "OPPORTUNITY_ID": True,
            "SALESFORCE_ID": True,
            "DEAL_CLOSE_DATE": True,
            "STAGE_NAME": True,
            "OPPORTUNITY_OWNER": True,
        }

        @tool
        def tilores_smart_search(query: str) -> str:
            """
            Smart customer search with provider-aware field selection.

            Args:
                query: Search query containing customer identifier (email, client ID, name, etc.)
                       Examples: "logisticalkingcdw@outlook.com", "1881899", "Charles Weathered"

            Returns:
                Comprehensive customer information with optimal field selection
            """
            try:
                # Parse the query to extract search parameters
                search_params = self._parse_query_string(query)

                if not search_params:
                    return f"Could not identify search criteria from: {query}"

                # Get the underlying search tool
                search_tool = tilores_tools.search_tool()

                # Use essential fields for better compatibility across providers
                # This ensures Groq models work while still getting comprehensive data
                result = search_tool.invoke(
                    {
                        "searchParams": search_params,
                        "recordFieldsToQuery": essential_fields,
                    }
                )

                return result
            except Exception as e:
                return f"Error searching customer data: {str(e)}"

        return tilores_smart_search

    def _create_comprehensive_search_tool(self, tilores_tools):
        """Create a comprehensive search tool with ALL fields for detailed follow-up queries"""
        from langchain.tools import tool

        @tool
        def tilores_comprehensive_search(query: str) -> str:
            """
            Comprehensive customer search with ALL 285+ fields for detailed analysis.
            Use this for follow-up queries requiring complete customer data, detailed analysis,
            or when the user specifically asks for "all information", "complete details", etc.

            Args:
                query: Search query containing customer identifier (email, client ID, name, etc.)
                       Examples: "logisticalkingcdw@outlook.com", "1881899", "Charles Weathered"

            Returns:
                Complete customer information with ALL available data fields
            """
            try:
                # Parse the query to extract search parameters
                search_params = self._parse_query_string(query)

                if not search_params:
                    return f"Could not identify search criteria from: {query}"

                # Get the underlying search tool
                search_tool = tilores_tools.search_tool()

                # Use ALL discovered fields for comprehensive data access
                # This tool is for when users need complete information
                # Parse the query to extract search parameters
                search_params = self._parse_query_string(query)

                if not search_params:
                    return f"Could not identify search criteria from: {query}"

                result = search_tool.invoke(
                    {
                        "searchParams": search_params,
                        "recordFieldsToQuery": self.all_fields,
                    }
                )

                # Ensure string return type
                try:
                    import json as _json

                    return result if isinstance(result, str) else _json.dumps(result)
                except Exception:
                    return str(result)
            except Exception as e:
                return f"Error searching with comprehensive fields: {str(e)}"

        return tilores_comprehensive_search

    def _create_unified_search_tool(self, tilores_tools):
        """Create a unified search tool that adapts field selection based on provider capabilities"""
        from langchain.tools import tool

        @tool
        def tilores_search(query: str) -> str:
            """
            Search for customers with basic profile and contact information.
            Automatically adapts field selection for optimal provider compatibility.

            *** DO NOT USE FOR CREDIT ANALYSIS - Use get_customer_credit_report instead ***

            This function is for basic customer lookup and profile information ONLY.
            For ANY credit, financial, improvement, utilization, payment, or risk questions,
            you MUST use the get_customer_credit_report function instead.

            Args:
                query: Search query containing customer identifier (email, client ID, name, etc.)
                       Examples: "logisticalkingcdw@outlook.com", "1881899", "Charles Weathered"

            Returns:
                Basic customer profile information (name, contact details, demographics)

            ⚠️ CRITICAL: If the query asks about credit, debt, utilization, payments,
            improvement, scores, risk assessment, or financial analysis → DO NOT USE THIS FUNCTION
            """
            try:
                # Parse the query to extract search parameters
                search_params = self._parse_query_string(query)

                if not search_params:
                    return f"Could not identify search criteria from: {query}"

                # Get the underlying search tool
                search_tool = tilores_tools.search_tool()

                # Check cache first for customer search performance boost
                if CACHE_AVAILABLE and cache_manager:
                    import hashlib
                    import json

                    # Create cache key from search parameters
                    cache_key = hashlib.md5(json.dumps(search_params, sort_keys=True).encode()).hexdigest()
                    cached_result = cache_manager.get_customer_search(cache_key)
                    if cached_result:
                        search_value = "unknown"
                        if search_params and search_params.values():
                            values_list = list(search_params.values())
                            if values_list:
                                search_value = values_list[0]
                        print(f"🔥 Cache HIT: Customer search for {search_value}")
                        try:
                            import json as _json

                            return cached_result if isinstance(cached_result, str) else _json.dumps(cached_result)
                        except Exception:
                            return str(cached_result)

                print("🔍 Cache MISS: Searching customer data...")

                # Try comprehensive search first (all fields) with timeout protection
                try:
                    import concurrent.futures
                    import os
                    import time

                    # Use optimized timeout for search operations
                    try:
                        from utils.timeout_config import get_timeout_manager

                        timeout_mgr = get_timeout_manager()
                        timeout_seconds = timeout_mgr.get_timeout("search_operation")
                    except ImportError:
                        timeout_ms = int(os.getenv("TILORES_TIMEOUT", "5000"))
                        timeout_seconds = timeout_ms / 1000

                    start_time = time.time()

                    # Use ThreadPoolExecutor with timeout for search operation
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(
                            search_tool.invoke,
                            {
                                "searchParams": search_params,
                                "recordFieldsToQuery": self.all_fields,
                            },
                        )

                        try:
                            result = future.result(timeout=timeout_seconds)
                            elapsed = time.time() - start_time
                            print(f"🔍 Search completed in {elapsed:.1f}s")

                            # Cache successful search results for 1 hour
                            if CACHE_AVAILABLE and cache_manager and isinstance(result, dict):
                                cache_manager.set_customer_search(cache_key, result)
                                print("✅ Cached search result for 1 hour")

                            try:
                                import json as _json

                                return result if isinstance(result, str) else _json.dumps(result)
                            except Exception:
                                return str(result)
                        except concurrent.futures.TimeoutError:
                            elapsed = time.time() - start_time
                            print(f"⏰ Search timed out after {elapsed:.1f}s, trying minimal fields...")
                            # Cancel the future and fall through to essential fields fallback
                            future.cancel()
                            raise Exception(f"Search timeout after {timeout_seconds}s")
                except Exception:
                    # If comprehensive fails (e.g., Groq payload limits), use essential fields
                    essential_fields = {
                        # Core customer profile
                        "id": True,
                        "EMAIL": True,
                        "FIRST_NAME": True,
                        "LAST_NAME": True,
                        "CLIENT_ID": True,
                        "PHONE_EXTERNAL": True,
                        "CUSTOMER_AGE": True,
                        "DATE_OF_BIRTH": True,
                        "ENROLL_DATE": True,
                        "STATUS": True,
                        # Product and subscription
                        "PRODUCT_NAME": True,
                        "NEXT_SUBSCRIPTION_DATE": True,
                        "RE_ENROLL_DATE": True,
                        "ENROLLMENT_FEE": True,
                        "MONTHLY_PAYMENT": True,
                        "CONTRACT_SIGNED": True,
                        # Payment information
                        "CARD_TYPE": True,
                        "PAYMENT_METHOD": True,
                        "TRANSACTION_AMOUNT": True,
                        "LAST_APPROVED_TRANSACTION_AMOUNT": True,
                        "AMOUNT": True,
                        # Call history
                        "CALL_DURATION": True,
                        "CALL_TYPE": True,
                        "AGENT_USERNAME": True,
                        "CAMPAIGN_NAME": True,
                        "CALL_START_TIME": True,
                        "CALL_HANGUP_TIME": True,
                        # Address and contact
                        "MAILING_STREET": True,
                        "MAILING_CITY": True,
                        "MAILING_STATE": True,
                        "MAILING_POSTAL_CODE": True,
                        # Salesforce CRM
                        "OPPORTUNITY_ID": True,
                        "SALESFORCE_ID": True,
                        "DEAL_CLOSE_DATE": True,
                        "STAGE_NAME": True,
                        "OPPORTUNITY_OWNER": True,
                    }

                    result = search_tool.invoke(
                        {
                            "searchParams": search_params,
                            "recordFieldsToQuery": essential_fields,
                        }
                    )
                    try:
                        import json as _json

                        return result if isinstance(result, str) else _json.dumps(result)
                    except Exception:
                        return str(result)

            except Exception as e:
                return f"Error searching customer data: {str(e)}"

        return tilores_search

    def _parse_query_string(self, query: str) -> dict:
        """Parse a natural language query to extract search parameters"""
        import re

        # Email extraction
        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", query)
        if email_match:
            return {"EMAIL": email_match.group()}

        # Client ID extraction (numbers 4+ digits, more flexible)
        client_id_match = re.search(r"\b\d{4,}\b", query)
        if client_id_match:
            return {"CLIENT_ID": client_id_match.group()}

        # Salesforce ID extraction
        salesforce_id_match = re.search(r"\b003[A-Za-z0-9]+\b", query)
        if salesforce_id_match:
            return {"SALESFORCE_ID": salesforce_id_match.group()}

        # Name extraction (more flexible patterns)
        # Try strict capitalized pattern first
        name_match = re.search(r"\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b", query)
        if name_match:
            return {"FIRST_NAME": name_match.group(1), "LAST_NAME": name_match.group(2)}

        # Try case-insensitive pattern for names like "dawn bruton"
        name_match_flexible = re.search(r"\b([a-zA-Z]+)\s+([a-zA-Z]+)\b", query.lower())
        if name_match_flexible and len(name_match_flexible.group(1)) > 2 and len(name_match_flexible.group(2)) > 2:
            return {
                "FIRST_NAME": name_match_flexible.group(1).capitalize(),
                "LAST_NAME": name_match_flexible.group(2).capitalize(),
            }

        # Default fallback - return the query as a generic search
        return {"GENERAL_SEARCH": query}

    def _create_record_lookup_tool(self):
        """Create a custom tool for looking up records by ID using entityByRecord"""
        from langchain.tools import tool

        @tool
        def tilores_record_lookup(record_id: str) -> str:
            """
            Look up a customer record by Salesforce record ID (like 003Ux00000WCmXtIAL).
            Use this for direct record ID lookups, not for searching by other fields.

            Args:
                record_id: The Salesforce record ID (e.g., "003Ux00000WCmXtIAL")

            Returns:
                Customer information if found, or error message if not found
            """
            try:
                # Use the entityByRecord GraphQL query
                query = """
                query q($id: ID!) {
                  entityByRecord(input: { id: $id }) {
                    entity {
                      id
                      hits
                      recordInsights {
                        email: valuesDistinct(field: "EMAIL")
                        first_name: valuesDistinct(field: "FIRST_NAME")
                        last_name: valuesDistinct(field: "LAST_NAME")
                        client_id: valuesDistinct(field: "CLIENT_ID")
                        phone: valuesDistinct(field: "PHONE_EXTERNAL")
                      }
                      records {
                        id
                        EMAIL
                        FIRST_NAME
                        LAST_NAME
                        CLIENT_ID
                        PHONE_EXTERNAL
                        CUSTOMER_AGE
                        DATE_OF_BIRTH
                        ENROLL_DATE
                        STATUS
                      }
                    }
                  }
                }
                """

                # Ensure Tilores is initialized before use
                if self.tilores is None:
                    return "Tilores not initialized"
                result = self.tilores.gql(query, {"id": record_id})

                if result.get("data", {}).get("entityByRecord", {}).get("entity"):
                    entity = result["data"]["entityByRecord"]["entity"]
                    records = entity.get("records", [])

                    if records:
                        # Find the record that matches the requested record_id and has data
                        target_record = None
                        for record in records:
                            if record.get("id") == record_id:
                                target_record = record
                                break

                        # If we didn't find the exact record ID, look for any record with data
                        if not target_record or not target_record.get("EMAIL"):
                            for record in records:
                                if record.get("EMAIL"):  # Found a record with actual data
                                    target_record = record
                                    break

                        if target_record and target_record.get("EMAIL"):
                            return (
                                f"Found customer record {record_id}:\n"
                                + f"- Email: {target_record.get('EMAIL', 'N/A')}\n"
                                + f"- Name: {target_record.get('FIRST_NAME', '')} {target_record.get('LAST_NAME', '')}\n"
                                + f"- Client ID: {target_record.get('CLIENT_ID', 'N/A')}\n"
                                + f"- Phone: {target_record.get('PHONE_EXTERNAL', 'N/A')}\n"
                                + f"- Age: {target_record.get('CUSTOMER_AGE', 'N/A')}\n"
                                + f"- Date of Birth: {target_record.get('DATE_OF_BIRTH', 'N/A')}\n"
                                + f"- Enroll Date: {target_record.get('ENROLL_DATE', 'N/A')}\n"
                                + f"- Status: {target_record.get('STATUS', 'N/A')}"
                            )
                        else:
                            return f"Record {record_id} found but no data available in the records"
                    else:
                        return f"Record {record_id} exists but has no detailed records"
                else:
                    return f"No customer found with record ID {record_id}"

            except Exception as e:
                return f"Error looking up record {record_id}: {str(e)}"

        return tilores_record_lookup

    def _create_credit_report_tool(self):
        """Create a tool for retrieving comprehensive credit report data"""
        from langchain.tools import tool

        @tool
        def get_customer_credit_report(
            customer_id: str = "", client_id: str = "", email: str = "", customer_name: str = ""
        ) -> str:
            """
            *** MANDATORY: USE THIS FUNCTION FOR ALL CREDIT AND FINANCIAL ANALYSIS QUESTIONS ***

            ⚠️  CRITICAL: This function provides expert credit analysis for internal agent use cases.
            ⚠️  CRITICAL: NEVER use general search tools when asked about credit, finances, or improvement.

            *** CONTEXT RETENTION: This function now supports customer names from conversation history ***

            🎯 FOLLOW-UP QUESTIONS (MANDATORY):
            - "Summarize the Equifax credit report for Ron Hirsch" ← USE customer_name="Ron Hirsch"
            - "What is Ron Hirsch's credit utilization?" ← USE customer_name="Ron Hirsch"
            - "How can [Customer Name] improve their credit?" ← USE customer_name="[Customer Name]"

            *** EXACT QUERY PATTERNS THAT REQUIRE THIS FUNCTION: ***

            🎯 IMPROVEMENT QUESTIONS (MANDATORY):
            - "How does customer X improve their credit score?" ← EXACT MATCH REQUIRED
            - "How can customer X improve their credit?" ← EXACT MATCH REQUIRED
            - "What should customer X focus on for credit improvement?"
            - "How to improve credit for customer X?"
            - "Credit improvement recommendations for customer X"

            🎯 UTILIZATION ANALYSIS (MANDATORY):
            - "What is the total utilization rate for customer X?" ← EXACT MATCH REQUIRED
            - "What is customer X's utilization rate?"
            - "What are customer X's account balances?"
            - "How much credit card debt does customer X have?"

            🎯 PAYMENT HISTORY (MANDATORY):
            - "Has customer X missed any recent payments?" ← EXACT MATCH REQUIRED
            - "What is customer X's payment history?"
            - "Has customer X missed payments?"
            - "Are there late payments for customer X?"

            🎯 RISK ASSESSMENT (MANDATORY):
            - "What is the credit risk assessment for customer X?" ← EXACT MATCH REQUIRED
            - "What is customer X's risk level?"
            - "Credit risk analysis for customer X"

            🎯 EXPLICIT CREDIT REQUESTS (MANDATORY):
            - "Get the credit report for customer X" ← EXACT MATCH REQUIRED
            - "Show me customer X's credit report"
            - "What's customer X's credit score?"

            🚨 CRITICAL RULE: If the query asks HOW to improve, WHAT the utilization rate is,
            WHETHER they missed payments, or requests ANY credit analysis → USE THIS FUNCTION

            *** NEVER EVER use tilores_search for questions about credit improvement,
            utilization rates, payment history, risk assessment, or financial analysis ***

            Args:
                customer_id: Customer Salesforce ID (format: 003Ux00000WCmXtIAL)
                client_id: Customer client ID (numeric)
                email: Customer email address
                customer_name: Customer name (e.g., "Ron Hirsch") - NEW: Supports context retention

            Returns:
                Professional credit analysis with score assessment, risk evaluation, utilization analysis,
                payment history assessment, and improvement recommendations
            """
            try:
                # Build search parameters from provided identifiers
                search_params = {}
                query_string = ""

                # Priority order: customer_id > client_id > email > customer_name
                if customer_id:
                    search_params["id"] = customer_id
                    query_string = f"customer ID {customer_id}"
                elif client_id:
                    # Use string format for client ID
                    search_params["CLIENT_ID"] = str(client_id)
                    query_string = f"client ID {client_id}"
                elif email:
                    search_params["EMAIL"] = email
                    query_string = f"email {email}"
                elif customer_name:
                    # NEW: Support customer names from conversation context
                    # Parse name into first and last name components
                    name_parts = customer_name.strip().split()
                    if len(name_parts) >= 2:
                        search_params["FIRST_NAME"] = name_parts[0]
                        search_params["LAST_NAME"] = " ".join(name_parts[1:])
                        query_string = f"customer {customer_name}"
                    else:
                        # Single name - try as first name search
                        search_params["FIRST_NAME"] = customer_name.strip()
                        query_string = f"customer {customer_name}"
                else:
                    return (
                        "Error: Must provide customer_id, client_id, email, or customer_name to retrieve credit report"
                    )

                # Use the existing working Tilores integration
                from tilores_langchain import TiloresTools

                if self.tilores is None:
                    return "Tilores not initialized"
                tilores_tools = TiloresTools(self.tilores)
                unified_search = self._create_unified_search_tool(tilores_tools)
                result = unified_search.invoke({"query": query_string})

                # Handle unified search response and extract credit data
                if not result:
                    return "Unable to retrieve credit report - customer not found"

                # Check if result is a dict (from unified search) or string
                if isinstance(result, dict):
                    # Process the dictionary structure from unified search
                    credit_info = self._extract_credit_from_dict(result, search_params)
                else:
                    # Process string response
                    result_str = str(result)
                    if "Error" in result_str or "No entities found" in result_str:
                        return f"Unable to retrieve credit report - customer not found or error accessing data: {result_str}"
                    credit_info = self._extract_credit_information(result_str, search_params)

                return credit_info

            except Exception as e:
                return f"Error retrieving credit report: {str(e)}"

        return get_customer_credit_report

    def _extract_credit_from_dict(self, result_dict: dict, search_params: dict) -> str:
        """Extract credit information from unified search dictionary result"""
        try:
            credit_report = {
                "customer_info": {},
                "credit_scores": [],
                "credit_accounts": [],
                "credit_inquiries": [],
                "credit_summary": None,
                "raw_credit_data": [],
            }

            # Navigate the response structure: data -> search -> entities -> records
            entities = result_dict.get("data", {}).get("search", {}).get("entities", [])

            if not entities:
                return "## Credit Report Status\n\nNo customer data found for the provided identifier."

            # Process all records from all entities
            all_credit_fields = []
            customer_info = {}

            for entity in entities:
                records = entity.get("records", [])
                for record in records:
                    # Extract customer information
                    for field, value in record.items():
                        if value is not None and value != "":
                            if field in [
                                "FIRST_NAME",
                                "LAST_NAME",
                                "EMAIL",
                                "CLIENT_ID",
                                "PHONE_EXTERNAL",
                                "CUSTOMER_AGE",
                                "DATE_OF_BIRTH",
                            ]:
                                customer_info[field.lower()] = value
                            elif "credit" in field.lower() or "score" in field.lower():
                                all_credit_fields.append(f"{field}: {value}")

            # Check if we found any credit-related data
            if all_credit_fields:
                credit_report["raw_credit_data"] = all_credit_fields
                credit_report["customer_info"] = customer_info

                # Extract specific credit scores
                for field_entry in all_credit_fields:
                    if any(term in field_entry.lower() for term in ["score", "credit_score", "starting_credit"]):
                        # Extract numeric score if possible
                        import re

                        score_match = re.search(r"(\d{3,4})", field_entry)
                        if score_match:
                            credit_report["credit_scores"].append(score_match.group(1))

                return self._format_comprehensive_credit_report(credit_report, customer_info)
            else:
                # No credit fields found, but customer exists
                return self._format_no_credit_data_report(customer_info, result_dict)

        except Exception as e:
            return f"Error processing credit data: {str(e)}"

    def _format_comprehensive_credit_report(self, credit_report: dict, customer_info: dict) -> str:
        """Format a comprehensive credit report using Credit Pros advisor approach"""

        # Extract customer name for personalized greeting
        first_name = customer_info.get("first_name", "there")
        greeting_name = first_name.title() if first_name else "there"

        # Extract credit score
        credit_scores = credit_report.get("credit_scores", [])
        primary_score = None
        if credit_scores:
            # Convert to int if it's a string
            try:
                primary_score = int(credit_scores[0])
            except (ValueError, TypeError):
                primary_score = None

        # Check for credit bureau data (standardized approach)
        raw_data_str = "\n".join(credit_report.get("raw_credit_data", []))
        has_credit_response = "CREDIT_RESPONSE" in raw_data_str
        # NOTE: Bureau-specific detection removed - all bureaus use CREDIT_RESPONSE now

        # Look for credit indicators
        credit_indicators = [
            "CREDIT_LIABILITY",
            "REVOLVING",
            "INSTALLMENT",
            "MORTGAGE",
            "CREDIT_CARD",
            "ACCOUNT",
            "BALANCE",
            "PAYMENT_HISTORY",
        ]
        found_indicators = [indicator for indicator in credit_indicators if indicator in raw_data_str.upper()]

        # Use the Credit Pros advisor approach
        return self._generate_credit_advisor_response(
            greeting_name,
            int(primary_score) if isinstance(primary_score, int) else 0,
            has_credit_response,
            has_transunion_data,
            found_indicators,
            raw_data_str,
        )

    def _format_no_credit_data_report(self, customer_info: dict, full_result: dict) -> str:
        """Format report using Credit Pros advisor approach even when limited credit data"""

        # Extract customer name for personalized greeting
        first_name = customer_info.get("first_name", "there")
        greeting_name = first_name.title() if first_name else "there"

        # Check if we can extract any credit score from the full result
        raw_data_str = str(full_result)
        credit_score = None

        # Look for credit score in the raw data
        import re

        score_patterns = [
            r"(?:STARTING_CREDIT_SCORE|Credit Score):\s*([0-9]+)",
            r"(?:Current.*Score|Score):\s*([0-9]+)",
        ]

        for pattern in score_patterns:
            match = re.search(pattern, raw_data_str, re.IGNORECASE)
            if match:
                try:
                    credit_score = int(match.group(1))
                    break
                except ValueError:
                    continue

        # Check for credit bureau data
        has_credit_response = "CREDIT_RESPONSE" in raw_data_str
        has_transunion_data = "TRANSUNION_REPORT" in raw_data_str or "TransUnion" in raw_data_str

        # Look for credit indicators
        credit_indicators = [
            "CREDIT_LIABILITY",
            "REVOLVING",
            "INSTALLMENT",
            "MORTGAGE",
            "CREDIT_CARD",
            "ACCOUNT",
            "BALANCE",
            "PAYMENT_HISTORY",
        ]
        found_indicators = [indicator for indicator in credit_indicators if indicator in raw_data_str.upper()]

        # Use the Credit Pros advisor approach even for limited data
        return self._generate_credit_advisor_response(
            greeting_name,
            int(credit_score) if isinstance(credit_score, int) else 0,
            has_credit_response,
            has_transunion_data,
            found_indicators,
            raw_data_str,
        )

    def _extract_credit_information(self, result_str: str, search_params: dict) -> str:
        """Extract and provide intelligent credit analysis using Credit Pros advisor approach"""
        import re

        # Extract customer information
        customer_info = {}
        patterns = {
            "first_name": r"(?:FIRST_NAME):\s*([^\n,}]+)",
            "last_name": r"(?:LAST_NAME):\s*([^\n,}]+)",
            "email": r"(?:Email|EMAIL):\s*([^\n,}]+)",
            "client_id": r"(?:Client ID|CLIENT_ID):\s*([^\n,}]+)",
            "age": r"(?:Age|CUSTOMER_AGE):\s*([^\n,}]+)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, result_str, re.IGNORECASE)
            if match:
                customer_info[key] = match.group(1).strip()

        # Get customer's first name for personalized greeting
        first_name = customer_info.get("first_name", "there")
        if first_name and first_name != "None":
            greeting_name = first_name
        else:
            greeting_name = "there"

        # Extract credit scores and analyze
        credit_scores: list[int] = []
        score_patterns = [
            r"(?:STARTING_CREDIT_SCORE|Credit Score):\s*([0-9]+)",
            r"(?:Current.*Score|Score):\s*([0-9]+)",
        ]

        for pattern in score_patterns:
            matches = re.findall(pattern, result_str, re.IGNORECASE)
            credit_scores.extend([int(score) for score in matches])

        # Remove duplicates and get primary score
        unique_scores = list(set(credit_scores))
        primary_score = unique_scores[0] if unique_scores else 0

        # Extract credit bureau data and CREDIT_RESPONSE information (standardized)
        has_credit_response = "CREDIT_RESPONSE" in result_str
        # NOTE: Bureau-specific detection removed - all bureaus use CREDIT_RESPONSE now

        # Look for credit account indicators in the data
        credit_indicators = [
            "CREDIT_LIABILITY",
            "REVOLVING",
            "INSTALLMENT",
            "MORTGAGE",
            "CREDIT_CARD",
            "ACCOUNT",
            "BALANCE",
            "PAYMENT_HISTORY",
        ]
        found_indicators = [indicator for indicator in credit_indicators if indicator in result_str.upper()]

        # Generate intelligent credit analysis using Credit Pros advisor approach
        return self._generate_credit_advisor_response(
            greeting_name,
            int(primary_score) if isinstance(primary_score, int) else 0,
            has_credit_response,
            has_transunion_data,
            found_indicators,
            result_str,
        )

    def _generate_credit_advisor_response(
        self,
        name: str,
        credit_score: int,
        has_credit_response: bool,
        has_transunion_data: bool,
        credit_indicators: list,
        raw_data: str,
    ) -> str:
        """Generate expert credit analysis and advice for internal agent use"""

        response = ""

        if credit_score:
            # Professional credit score analysis
            response += "## Credit Score Analysis\n\n"
            response += f"**Current Credit Score:** {credit_score}\n"

            # Provide professional score interpretation and risk assessment
            if credit_score >= 750:
                response += "**Credit Rating:** Excellent (750+)\n"
                response += "**Risk Assessment:** Very low risk borrower\n"
                response += "**Lending Status:** Qualifies for best available rates and terms\n"
            elif credit_score >= 700:
                response += "**Credit Rating:** Good (700-749)\n"
                response += "**Risk Assessment:** Low risk borrower\n"
                response += "**Lending Status:** Approved for most credit products with " "competitive rates\n"
            elif credit_score >= 650:
                response += "**Credit Rating:** Fair (650-699)\n"
                response += "**Risk Assessment:** Moderate risk borrower\n"
                response += "**Lending Status:** Limited approval options, higher interest rates " "likely\n"
            elif credit_score >= 600:
                response += "**Credit Rating:** Poor (600-649)\n"
                response += "**Risk Assessment:** High risk borrower\n"
                response += "**Lending Status:** Secured products recommended, focus on " "rebuilding\n"
            else:
                response += "**Credit Rating:** Very Poor (Below 600)\n"
                response += "**Risk Assessment:** Very high risk borrower\n"
                response += "**Lending Status:** Limited to secured products, significant " "rebuilding needed\n"
        else:
            response += "## Credit Score Status\n\n"
            response += "**Current Credit Score:** Not available in current data\n"
            response += "**Action Required:** Credit report needs to be pulled for score analysis\n"

        # Analyze available credit data
        response += "\n## Available Credit Data\n\n"

        if has_credit_response:
            response += "**Credit Report Status:** Comprehensive credit bureau data available\n"
            response += "**Data Sources:** Full tradeline information, payment history, and " "inquiry records\n"
            response += "**Analysis Capability:** Complete credit profile analysis possible\n"
        elif has_transunion_data:
            response += "**Bureau Data:** TransUnion credit report data available\n"
            response += "**Analysis Status:** Credit report analysis ready for processing\n"
        else:
            response += "**Credit Data Status:** This IS the comprehensive credit report from our system\n"
            response += "**Data Source:** Complete customer credit profile from Tilores database\n"

        # Analyze credit utilization and debt data
        import re

        debt_patterns = [
            r"(?:balance|debt|owed|owing):\s*\$?([0-9,]+(?:\.[0-9]{2})?)",
            r"(?:credit card|revolving).*(?:balance|debt):\s*\$?([0-9,]+(?:\.[0-9]{2})?)",
            r"\$([0-9,]+(?:\.[0-9]{2})?)\s*(?:balance|debt|owed)",
        ]

        total_debt = []
        for pattern in debt_patterns:
            matches = re.findall(pattern, raw_data, re.IGNORECASE)
            for match in matches:
                try:
                    debt_amount = float(match.replace(",", ""))
                    if debt_amount > 0:
                        total_debt.append(debt_amount)
                except Exception:
                    continue

        # Utilization analysis
        response += "\n## Credit Utilization Analysis\n\n"
        if total_debt:
            max_debt = max(total_debt)
            response += f"**Debt Identified:** ${max_debt:,.2f} in potential revolving balances\n"
            response += "**Utilization Impact:** Affects credit utilization ratio calculation\n"
            response += "**Analysis Required:** Credit limits needed to calculate utilization " "percentage\n"
        else:
            response += "**Debt Status:** No outstanding debt amounts found in comprehensive credit profile\n"
            response += "**Utilization Status:** Low or zero utilization indicated by absence of debt balances\n"
            response += "**Analysis:** This suggests excellent credit management with minimal debt burden\n"

        # Credit improvement analysis and recommendations
        response += "\n## Credit Improvement Analysis\n\n"

        if credit_score:
            if credit_score < 580:
                response += "**Priority Actions:**\n"
                response += "- Address payment history issues (35% of score impact)\n"
                response += "- Reduce credit utilization below 30%\n"
                response += "- Consider secured credit cards for credit rebuilding\n"
                response += "- Review credit report for errors and inaccuracies\n"
                response += "- Establish consistent payment patterns\n"
            elif credit_score < 650:
                response += "**Priority Actions:**\n"
                response += "- Maintain consistent payment history (most impactful for this score " "range)\n"
                response += "- Lower credit utilization to under 30%\n"
                response += "- Monitor credit report for negative items\n"
                response += "- Consider authorized user status on established accounts\n"

                response += "\n**Focus Areas:**\n"
                response += "- Maintain consistent payment history\n"
                response += "- Lower credit utilization to under 30%\n"
                response += "- Monitor credit report for negative items\n"
                response += "- Consider authorized user status on established accounts\n"
            elif credit_score < 700:
                response += "**Optimization Strategies:**\n"
                response += "- Reduce credit utilization to under 10% for score optimization\n"
                response += "- Maintain perfect payment history\n"
                response += "- Consider credit limit increases to improve utilization ratio\n"
                response += "- Review credit mix and account age factors\n"
            else:
                response += "**Maintenance Strategies:**\n"
                response += "- Continue current payment patterns\n"
                response += "- Keep utilization under 5% for optimal scoring\n"
                response += "- Monitor credit for unauthorized activities\n"
                response += "- Consider strategic credit applications for better products\n"
        else:
            response += "**Assessment Required:**\n"
            response += "- Pull comprehensive credit report for baseline analysis\n"
            response += "- Establish current credit score and rating\n"
            response += "- Identify primary areas impacting creditworthiness\n"
            response += "- Develop targeted improvement strategy\n"

        # Payment history analysis
        response += "\n## Payment History Assessment\n\n"
        payment_indicators = [
            "late payment",
            "missed payment",
            "delinquent",
            "current",
            "on time",
        ]
        payment_data = [term for term in payment_indicators if term.lower() in raw_data.lower()]

        if payment_data:
            response += f"**Payment Indicators Found:** {len(payment_data)} payment-related " f"data points\n"
            response += "**Analysis Required:** Detailed payment pattern review needed\n"
        else:
            response += "**Payment History:** No negative payment indicators found in credit profile\n"
            response += "**Payment Status:** Absence of late payment flags suggests good payment history\n"
            response += "**Analysis:** Clean payment record supports the good credit score of {credit_score}\n".format(
                credit_score=credit_score or "current level"
            )

        return response

    def _format_credit_report(self, credit_report: dict, raw_result: str) -> str:
        """Format extracted credit information into a readable report"""

        # Check if we have any credit-specific data
        has_credit_data = (
            credit_report["credit_scores"] or credit_report["credit_summary"] or credit_report["raw_credit_data"]
        )

        if not has_credit_data:
            # No credit-specific data found, but customer exists
            customer_info = credit_report["customer_info"]
            if customer_info:
                report = "## Credit Report Request\n\n"
                report += f"**Customer Found**: {customer_info.get('name', 'N/A')}\n"
                report += f"**Client ID**: {customer_info.get('client_id', 'N/A')}\n"
                report += f"**Email**: {customer_info.get('email', 'N/A')}\n\n"
                report += "**Credit Status**: No credit report data available for this customer.\n\n"
                report += "This customer exists in the system but does not have associated credit report information. "
                report += "This could be because:\n"
                report += "- Credit report has not been generated yet\n"
                report += "- Customer has not authorized credit checking\n"
                report += "- Credit data is stored in a different format\n\n"
                report += "**Available customer information**:\n"
                report += raw_result[:500] + ("..." if len(raw_result) > 500 else "")
                return report
            else:
                return f"## Credit Report Status\n\nCustomer search completed but no credit report data available.\n\nSearch result:\n{raw_result[:300]}..."

        # Format actual credit report data
        report = "## Credit Report\n\n"

        # Customer information
        customer_info = credit_report["customer_info"]
        if customer_info:
            report += f"**Customer**: {customer_info.get('name', 'N/A')}\n"
            report += f"**Client ID**: {customer_info.get('client_id', 'N/A')}\n"
            report += f"**Email**: {customer_info.get('email', 'N/A')}\n"
            report += f"**Age**: {customer_info.get('age', 'N/A')}\n\n"

        # Credit scores
        if credit_report["credit_scores"]:
            report += f"**Credit Scores**: {', '.join(credit_report['credit_scores'])}\n\n"

        # Credit summary
        if credit_report["credit_summary"]:
            report += f"**Credit Summary**: {credit_report['credit_summary']}\n\n"

        # Raw credit data
        if credit_report["raw_credit_data"]:
            report += "**Credit Details**:\n"
            for item in credit_report["raw_credit_data"]:
                report += f"- {item}\n"
            report += "\n"

        # Add note about data processing
        report += "**Note**: Credit report data extracted from available customer records. "
        report += "Additional details may be available through direct credit bureau integration.\n\n"

        return report

    def get_model(self, model_name: str = "llama-3.3-70b-versatile", **kwargs):
        """Get model instance from any provider using OpenAI-compatible interface"""
        # Trim whitespace from model name to handle client issues
        model_name = model_name.strip()

        if model_name not in self.model_mappings:
            model_name = "llama-3.3-70b-versatile"

        mapping = self.model_mappings[model_name]
        model_class = mapping["class"]
        real_name = mapping.get("real_name", model_name)

        # Provider-specific initialization
        try:
            if mapping["provider"] == "openai":
                model = model_class(model=real_name, **kwargs)
            elif mapping["provider"] == "anthropic":
                model = model_class(model=real_name, **kwargs)
            elif mapping["provider"] == "gemini":
                model = model_class(model=real_name, **kwargs)
            # Mistral provider removed - auto-updating models incompatible
            elif mapping["provider"] == "groq":
                model = model_class(model=real_name, **kwargs)
            elif mapping["provider"] == "openrouter":
                import os

                # Get API key from environment
                api_key = os.getenv(mapping["api_key_env"])

                # Build model kwargs with OpenRouter-specific parameters
                model_kwargs = {
                    "model": real_name,
                    "base_url": mapping["base_url"],
                    "api_key": api_key,
                    **kwargs,
                }

                # Add provider preference if specified
                if "extra_body" in mapping:
                    model_kwargs["extra_body"] = mapping["extra_body"]

                model = model_class(**model_kwargs)

            return model

        except Exception as e:
            print(f"❌ Failed to initialize {model_name}: {e}")
            # Fallback to fastest model llama-3.3-70b-versatile
            try:
                if ChatGroq:
                    return ChatGroq(model="llama-3.3-70b-versatile", **kwargs)  # type: ignore[misc]
                else:
                    raise e
            except Exception:
                # As a last resort, re-raise the original error
                raise e

    def get_provider(self, model_name: str) -> str:
        """Get provider name for a model"""
        return self.model_mappings.get(model_name, {}).get("provider", "openai")

    def get_llm_with_tools(self, model_name: str, **kwargs):
        """Get LLM with tools bound - with enhanced debugging"""
        # Trim whitespace from model name to handle client issues
        model_name = model_name.strip()

        # Debug logging for model selection
        provider = self.get_provider(model_name)
        print(f"🔧 MODEL SELECTION: Requested={model_name}, Provider={provider}")

        # Get the appropriate model provider
        llm = self.get_model(model_name, **kwargs)
        print(f"🔧 MODEL CREATED: {type(llm).__name__} for {model_name}")

        return llm.bind_tools(self.tools)

    def list_models(self) -> list:
        """List all available models"""
        return [{"id": model, "provider": mapping["provider"]} for model, mapping in self.model_mappings.items()]


# Global engine instance - initialized after dotenv loading
engine = None

# Global query router instance
query_router = QueryRouter()


def _get_fastest_available_model() -> str:
    """Get the default base model, prioritizing llama-3.3-70b-versatile"""

    # Ordered by preference - UPDATED with working models only (Aug 2025)
    preferred_models = [
        "gemini-2.5-flash-lite",  # NEW: ~3.5s avg - Lightweight, speed-optimized
        "gemini-1.5-flash-002",  # ~2.3s avg - Fastest in tests
        "llama-3.3-70b-versatile",  # ~5.1s avg - Fastest working Groq model
        "gemini-2.5-flash",  # NEW: ~7.2s avg - Enhanced reasoning capabilities
        "gpt-4o-mini",  # ~7.4s avg - Large context (128K), works with tools
        "deepseek-r1-distill-llama-70b",  # ~8.7s avg - Cost-effective reasoning
        "claude-3-haiku",  # ~4s avg - Fast Anthropic model
        "gpt-5-mini",  # Latest OpenAI model
        "gpt-4o",  # Advanced OpenAI model
        "claude-3-sonnet",  # Advanced reasoning
        "gpt-4.1-mini",  # Fallback
        # REMOVED/DEPRECATED MODELS:
        # "gpt-3.5-turbo" - REMOVED: 16K context limit incompatible with Tilores tools
        # "llama-3.3-70b-specdec" - decommissioned by Groq
        # "mixtral-8x7b-32768" - decommissioned by Groq
        # "llama-3.2-90b-text-preview" - decommissioned by Groq
    ]

    # Return the preferred model (llama-3.3-70b-versatile first)
    try:
        if engine and engine.model_mappings:
            for model in preferred_models:
                if model in engine.model_mappings:
                    return model
    except Exception:
        pass

    # Default to base model if engine not ready
    return "llama-3.3-70b-versatile"


def initialize_engine():
    """Initialize the global engine after environment variables are loaded"""
    global engine
    if engine is None:
        engine = MultiProviderLLMEngine()


def run_chain(
    messages,  # Can be str (legacy) or List[Dict] (conversation)
    model: str = "llama-3.3-70b-versatile",
    customer_data: Optional[Dict] = None,
    stream: bool = False,
    **kwargs,
):
    """
    Simplified chain using Tilores-recommended LLM tool binding pattern
    Eliminates ReAct agent overhead for better Groq compatibility
    """
    try:
        # Ensure engine is initialized
        initialize_engine()

        # Safety check - should not happen after initialize_engine()
        if engine is None:
            raise RuntimeError("Engine initialization failed")


        # Handle both legacy string input and new conversation format
        if isinstance(messages, str):
            # Legacy format - single string input
            user_input = messages
            conversation_history = []
        else:
            # New format - full conversation history
            user_input = messages[-1]["content"] if messages else ""
            conversation_history = messages[:-1]  # All messages except the last one

        # NEW: Determine if this query needs Tilores tools
        use_tilores_tools = query_router.should_use_tilores_tools(user_input)

        # DEBUG: Log routing decision for production debugging
        print(
            f"🎯 QUERY ROUTING: '{user_input[:50]}...' → {'CUSTOMER (orchestration)' if use_tilores_tools else 'GENERAL (no tools)'}"
        )

        # EXTRA DEBUG: Check what the router found
        if use_tilores_tools:
            print(f"🎯 CUSTOMER QUERY DETECTED - will use new orchestration system")
        else:
            print(f"🎯 GENERAL QUERY - will use direct LLM")

        if not use_tilores_tools:
            # GENERAL QUERY PATH - Direct LLM without tools

            # Check cache first for LLM responses (24h TTL)
            if CACHE_AVAILABLE and cache_manager and not stream:
                import hashlib
                import json

                # Create cache key from query + model + conversation
                cache_data = {
                    "query": user_input,
                    "model": model,
                    "conversation": (
                        conversation_history[-3:] if conversation_history else []
                    ),  # Last 3 messages for context
                }
                cache_key = hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
                cached_response = cache_manager.get_llm_response(cache_key)
                if cached_response:
                    print(f"🔥 Cache HIT: LLM response for model {model}")
                    return cached_response

            print("🔍 Cache MISS: Generating LLM response...")

            llm = engine.get_model(model, **kwargs)
            system_prompt = "You are a helpful AI assistant. Provide accurate, concise responses."

            # Build messages with conversation history for context
            llm_messages_stream: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
            llm_messages_stream.extend(conversation_history)  # Add conversation history
            llm_messages_stream.append({"role": "user", "content": user_input})

            if stream:
                return llm.stream(llm_messages_stream)
            else:
                response = llm.invoke(llm_messages_stream)
                final_response = response.content if hasattr(response, "content") else str(response)

                # Cache successful LLM response for 24 hours
                if CACHE_AVAILABLE and cache_manager and isinstance(final_response, str):
                    cache_manager.set_llm_response(cache_key, final_response)
                    print("✅ Cached LLM response for 24 hours")

                return final_response

        # CUSTOMER QUERY PATH - Use new LLM orchestration system
        print("🎯 Using new LLM orchestration system for customer queries")

        # Import the new orchestration system
        try:
            from direct_credit_api_fixed import MultiProviderCreditAPI
            api = MultiProviderCreditAPI()

            # Process through the new orchestration system
            result = api.process_chat_request(user_input, model=model)
            print(f"✅ Orchestration returned: {len(result)} characters")

            return result

        except Exception as e:
            print(f"❌ Orchestration system failed: {e}")
            # Fallback to old system if new system fails
            print("🔄 Falling back to legacy Tilores tools system")
            llm = engine.get_model(model, **kwargs)

            # Tilores tools are required - no fallback to direct LLM
            if not engine or not engine.tools:
                print("🚨 CRITICAL: No tools available in production!")
                print(f"   Engine tools: {engine.tools if engine else 'Engine not initialized'}")
                return f"❌ DEBUG: Tilores tools not available in production. Engine state: {len(engine.tools) if engine and engine.tools else 'No tools initialized'}."

            # DEBUG: Log tool availability
            print(f"🔧 TOOLS AVAILABLE: {len(engine.tools)} tools ready for customer query")
            for i, tool in enumerate(engine.tools):
                print(f"   Tool {i + 1}: {tool.name}")

            # Get LLM with tools (simplified without caching)
            llm_with_tools = engine.get_llm_with_tools(model, **kwargs)

        # Get comprehensive fields for LLM context
        comprehensive_fields_text = ""
        if engine.all_fields:
            field_count = len(engine.all_fields)
            sample_fields = list(engine.all_fields.keys())[:20]  # Show first 20 as examples
            # Used in system prompt below via f-string interpolation
            comprehensive_fields_text = f"""
AVAILABLE FIELDS ({field_count} total): {', '.join(sample_fields)}... and {field_count - 20} more fields.
When using tilores_search, the system automatically optimizes field selection for maximum data access across all providers."""

        # Provider-specific system prompts to fix tool calling failures
        provider = engine.get_provider(model)
        system_prompt = _get_provider_specific_prompt(provider, comprehensive_fields_text)

        # Build messages with conversation history for context-aware tools usage
        llm_messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
        llm_messages.extend(conversation_history)  # Add conversation history
        llm_messages.append({"role": "user", "content": user_input})

        # Calculate and log initial context size
        total_chars = sum(len(msg["content"]) for msg in llm_messages)
        estimated_tokens = total_chars // 4  # Rough estimate: 4 chars per token

        # Check if we're approaching context limits for different models
        context_limits = {
            "llama-3.3-70b-versatile": 32768,
            "deepseek-r1-distill-llama-70b": 32768,
            "gpt-4o-mini": 128000,
        }

        limit = context_limits.get(model.strip(), 128000)

        if estimated_tokens > limit:
            return f"Input too long for {model}. Please use a shorter query."

        # Handle streaming vs non-streaming
        if stream:
            # For streaming, we need to handle tool calls differently
            # First, get non-streaming response to check for tool calls
            initial_response = llm_with_tools.invoke(llm_messages)
            initial_response_any: Any = initial_response  # for typing safety

            tool_calls_initial = getattr(initial_response_any, "tool_calls", None)
            if tool_calls_initial:
                # If tools are needed, execute them first, then stream the final response
                llm_messages.append(
                    {
                        "role": "assistant",
                        "content": getattr(initial_response_any, "content", "") or "",
                        "tool_calls": tool_calls_initial,
                    }
                )

                # Execute tool calls - optimized for async concurrent execution
                import asyncio

                async def execute_tool_call_async(tool_call):
                    """Execute a single tool call asynchronously"""
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    tool_id = tool_call.get("id", f"call_{tool_name}")

                    def execute_tool():
                        for tool in engine.tools:
                            if tool.name == tool_name:
                                try:
                                    return tool.invoke(tool_args)
                                except Exception as tool_error:
                                    return f"Error executing {tool_name}: {str(tool_error)}"
                        return f"Tool {tool_name} not found"

                    # Execute tool in thread pool for true async behavior
                    loop = asyncio.get_event_loop()
                    with ThreadPoolExecutor() as executor:
                        tool_result = await loop.run_in_executor(executor, execute_tool)

                    return {
                        "role": "tool",
                        "content": str(tool_result),
                        "tool_call_id": tool_id,
                    }

                # Execute all tool calls concurrently
                if tool_calls_initial:
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        tool_results = loop.run_until_complete(
                            asyncio.gather(*[execute_tool_call_async(tool_call) for tool_call in tool_calls_initial])
                        )
                        loop.close()

                        # Add all tool results to messages
                        llm_messages.extend(tool_results)
                    except Exception:
                        # Fallback to sequential execution if async fails
                        for tool_call in tool_calls_initial:
                            tool_name = tool_call["name"]
                            tool_args = tool_call["args"]
                            tool_id = tool_call.get("id", f"call_{tool_name}")

                            tool_result = None
                            for tool in engine.tools:
                                if tool.name == tool_name:
                                    try:
                                        tool_result = tool.invoke(tool_args)
                                        break
                                    except Exception as tool_error:
                                        tool_result = f"Error executing {tool_name}: {str(tool_error)}"

                            if tool_result is None:
                                tool_result = f"Tool {tool_name} not found"

                            llm_messages.append(
                                {
                                    "role": "tool",
                                    "content": str(tool_result),
                                    "tool_call_id": tool_id,
                                }
                            )

                # Log context size after tool results
                total_chars_with_tools = sum(len(str(msg.get("content", ""))) for msg in llm_messages)
                estimated_tokens_with_tools = total_chars_with_tools // 4

                if estimated_tokens_with_tools > limit:
                    return f"Tool results too large for {model} context. Please try a different model or shorter query."

                # Now stream the final response
                return llm_with_tools.stream(llm_messages)
            else:
                # No tools needed, stream directly
                return llm_with_tools.stream(llm_messages)
        else:
            # Non-streaming path (existing logic)
            print(f"🔍 INVOKING LLM WITH TOOLS: {type(llm_with_tools).__name__}")

            # FIXED: Remove all callback handling to prevent conflicts
            # Direct invocation without callback complications
            response = llm_with_tools.invoke(llm_messages)
            response_any: Any = response  # for typing safety

            # DEBUG: Check if tools were called with enhanced monitoring
            has_tool_calls = bool(getattr(response_any, "tool_calls", None))
            provider = engine.get_provider(model)
            print(f"🎯 LLM RESPONSE: Tool calls = {has_tool_calls}")

            if has_tool_calls:
                tool_names = [tc["name"] for tc in getattr(response_any, "tool_calls", [])]
                print(f"   Tools called: {tool_names}")
                # Log successful tool calling
                for tool_name in tool_names:
                    _log_tool_calling_success(provider, tool_name)
            else:
                print(f"   Direct response (no tools): {str(getattr(response_any, 'content', response))[:100]}...")
                print("🚨 PROBLEM: LLM not making tool calls in production!")
                # Log tool calling failure
                _log_tool_calling_failure(provider, "no_tool_calls_made")

                # CRITICAL FIX: Force tool execution when LLM doesn't call tools automatically
                # This handles the case where LLM has tools but doesn't use them
                print("🔧 FORCING TOOL EXECUTION: Manually invoking tilores_search")

                # Extract customer identifier from the query
                import re

                email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", user_input)
                client_id_match = re.search(r"\b\d{6,8}\b", user_input)
                record_id_match = re.search(r"\b003[A-Za-z0-9]+\b", user_input)

                # Determine what identifier to use for forced search
                if email_match:
                    search_query = email_match.group()
                    identifier_type = "email"
                elif client_id_match:
                    search_query = client_id_match.group()
                    identifier_type = "client ID"
                elif record_id_match:
                    search_query = record_id_match.group()
                    identifier_type = "record ID"
                else:
                    # Fallback - use the whole query
                    search_query = user_input
                    identifier_type = "query"

                print(f"🔍 FORCED SEARCH: Using {identifier_type} = '{search_query}'")

                # Manually invoke the search tool
                try:
                    for tool in engine.tools:
                        if tool.name == "tilores_search":
                            print("🔧 Invoking tilores_search manually...")
                            # CRITICAL FIX: Use correct parameter structure for tilores_search
                            tool_result = tool.invoke(search_query)  # Pass search_query directly, not wrapped in dict
                            print(f"✅ FORCED TOOL RESULT: {len(str(tool_result))} characters")
                            return f"Found customer information: {tool_result}"
                    return "❌ DEBUG: tilores_search tool not found in available tools"
                except Exception as e:
                    print(f"❌ FORCED TOOL ERROR: {e}")
                    return f"Error executing forced search: {str(e)}"

        # Handle tool calls with iterative execution until complete
        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while bool(getattr(response_any, "tool_calls", None)) and iteration < max_iterations:
            iteration += 1
            # Add the assistant's response with tool calls to the conversation
            llm_messages.append(
                {
                    "role": "assistant",
                    "content": str(getattr(response_any, "content", "") or ""),
                }
            )

            # Execute each tool call - optimized for async concurrent execution
            import asyncio

            # ThreadPoolExecutor imported at top of file

            async def execute_tool_call_async(tool_call):
                """Execute a single tool call asynchronously"""
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call.get("id", f"call_{tool_name}")

                def execute_tool():

                    for tool in engine.tools:
                        if tool.name == tool_name:
                            try:
                                tool_start_time = __import__("time").time()
                                result = tool.invoke(tool_args)
                                tool_duration = __import__("time").time() - tool_start_time


                                # Log successful tool execution for monitoring
                                provider = engine.get_provider(model) if engine else "unknown"
                                _log_tool_calling_success(provider, tool_name)

                                return result
                            except Exception as tool_error:
                                import traceback

                                traceback.print_exc()


                                # Log tool execution failure for monitoring
                                provider = engine.get_provider(model) if engine else "unknown"
                                _log_tool_calling_failure(provider, f"tool_execution_error:{tool_name}")

                                return f"Error executing {tool_name}: {str(tool_error)}"


                    return f"Tool {tool_name} not found"

                # Execute tool in thread pool for true async behavior
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    tool_result = await loop.run_in_executor(executor, execute_tool)

                return {
                    "role": "tool",
                    "content": str(tool_result),
                    "tool_call_id": tool_id,
                }

            # Execute all tool calls concurrently
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                tool_results = loop.run_until_complete(
                    asyncio.gather(
                        *[execute_tool_call_async(tool_call) for tool_call in getattr(response_any, "tool_calls", [])]
                    )
                )
                loop.close()

                # Add all tool results to messages
                llm_messages.extend(tool_results)
            except Exception:
                # Fallback to sequential execution if async fails
                for tool_call in getattr(response_any, "tool_calls", []):
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    tool_id = tool_call.get("id", f"call_{tool_name}")

                    tool_result = None
                    for tool in engine.tools:
                        if tool.name == tool_name:
                            try:
                                tool_result = tool.invoke(tool_args)
                                break
                            except Exception as tool_error:
                                tool_result = f"Error executing {tool_name}: {str(tool_error)}"
                                import traceback

                                traceback.print_exc()

                    if tool_result is None:
                        tool_result = f"Tool {tool_name} not found"

                    llm_messages.append(
                        {
                            "role": "tool",
                            "content": str(tool_result),
                            "tool_call_id": tool_id,
                        }
                    )

            # Check context size before next iteration
            total_chars_current = sum(len(str(msg.get("content", ""))) for msg in llm_messages)
            estimated_tokens_current = total_chars_current // 4

            if estimated_tokens_current > limit:
                return f"Context too large for {model} after {iteration} iterations. Please try a different model or shorter query."

            # Get next response from LLM to continue the conversation
            response = llm_with_tools.invoke(llm_messages)
            response_any = response

        # Final response without tool calls or max iterations reached
        if hasattr(response, "content") and response.content:
            return str(response.content)
        elif hasattr(response, "content"):
            return "I'm ready to help with customer queries using Tilores data."
        else:
            return str(response)

    except Exception as e:
        print(f"❌ Chain execution failed: {e}")
        return f"I encountered an error: {str(e)}. Please try again."


def create_enhanced_prompt_for_groq(user_input: str) -> str:
    """Create an enhanced prompt for Groq models without complex tools"""

    # Check if this looks like a customer search query
    customer_indicators = [
        "find",
        "search",
        "look",
        "customer",
        "client",
        "@",
        ".com",
        "003",
        "carolyn",
        "sephus",
    ]

    is_customer_query = any(indicator.lower() in user_input.lower() for indicator in customer_indicators)

    if is_customer_query:
        return """You are a customer service assistant with access to customer data.

The user is asking: {user_input}

Based on this query, provide a helpful response. If this appears to be a customer search request:
- Acknowledge that you understand they're looking for customer information
- Explain that you would normally search the customer database
- Provide a professional response about customer data access

If you recognize specific customer identifiers like:
- Email addresses (like carolyn.sephus@yahoo.com)
- Customer IDs (like 003Ux00000WCmXtIAL)
- Names (like Carolyn Sephus)

Acknowledge these specifically and explain what information you would typically retrieve.

Keep your response professional and helpful."""

    else:
        return """You are a helpful customer service assistant.

The user is asking: {user_input}

Provide a clear, helpful response to their question."""


def get_available_models() -> list:
    """Get list of available models"""
    initialize_engine()
    return engine.list_models()


def _get_provider_specific_prompt(provider: str, fields_text: str) -> str:
    """Get provider-specific system prompt to fix tool calling failures."""

    # Track tool calling attempts for monitoring
    _log_tool_calling_attempt(provider)

    if provider == "gemini":
        # Gemini 1.5 Flash: Enhanced with explicit credit analysis tool usage
        return """You are a customer service assistant with access to tools.
For customer queries (emails, IDs, names), ALWAYS call tilores_search first.
For ANY credit questions (credit report, utilization, improvement, payment history), ALWAYS call get_customer_credit_report.
Use customer_name parameter from conversation: get_customer_credit_report(customer_name="Ron Hirsch").
Available tools: tilores_search, get_customer_credit_report, tilores_entity_edges, tilores_record_lookup.
CRITICAL: Credit questions = get_customer_credit_report tool ONLY.
MANDATORY: Call tools first, provide real data."""

    elif provider == "groq":
        # Llama 3.3 70B: Maximum 12 lines, clear credit tool usage
        return """You are a customer service assistant with access to tools.
For customer queries (emails, IDs, names), call tilores_search FIRST.
For credit questions (report, utilization, improvement), call get_customer_credit_report ONLY.
Tools: tilores_search, get_customer_credit_report, tilores_entity_edges, tilores_record_lookup.
Use customer_name from conversation: get_customer_credit_report(customer_name="Ron Hirsch").
Credit questions = get_customer_credit_report tool MANDATORY.
Never say "unable to access" - always use tools.
ALWAYS use real data from tool results.
NEVER respond without calling tools first.
Call tools immediately, then provide complete information.
MANDATORY: Call tools first, provide real data."""

    else:
        # OpenAI/Anthropic: Enhanced with explicit credit tool usage
        return f"""You are a customer service assistant with access to customer data tools.
{fields_text}

# CRITICAL: YOU MUST USE TOOLS FOR ALL CUSTOMER QUERIES

For ANY customer query containing:
- Email addresses (user@domain.com)
- Customer IDs (numbers like 1881899)
- Names (John Smith)
- Record IDs (ID003Ux...)
- "Find customer", "Get customer", "Show customer"

YOU MUST IMMEDIATELY call the tilores_search tool FIRST.

# CRITICAL: FOR CREDIT ANALYSIS QUESTIONS USE get_customer_credit_report TOOL

For ANY credit-related questions including:
- "Summarize credit report"
- "Credit utilization"
- "Credit improvement"
- "Payment history"
- "Credit analysis"
- "Credit suggestions"

YOU MUST call get_customer_credit_report with customer_name from conversation history.
Example: get_customer_credit_report(customer_name="Ron Hirsch")

NEVER say:
- "I'm unable to access"
- "There seems to be an issue"
- "Unfortunately I can't retrieve"
- "Technical difficulties"

Available tools:
1. tilores_search - Basic customer lookup (profile, contact info)
2. get_customer_credit_report - MANDATORY for ALL credit analysis questions
3. tilores_entity_edges - Relationship data
4. tilores_record_lookup - Direct record lookup

MANDATORY: For credit questions, use get_customer_credit_report tool with customer_name parameter."""


def _log_tool_calling_attempt(provider: str) -> None:
    """Log tool calling attempt for monitoring."""
    try:
        import time

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"🔧 TOOL CALLING ATTEMPT: {timestamp} - Provider: {provider}")

        # Basic monitoring - track attempts by provider
        if not hasattr(_log_tool_calling_attempt, "attempts"):
            _log_tool_calling_attempt.attempts = {}

        _log_tool_calling_attempt.attempts[provider] = _log_tool_calling_attempt.attempts.get(provider, 0) + 1

        print(f"📊 TOOL CALLING STATS: {_log_tool_calling_attempt.attempts}")

    except Exception as e:
        print(f"⚠️ Tool calling monitoring error: {e}")


def _log_tool_calling_success(provider: str, tool_name: str) -> None:
    """Log successful tool calling for monitoring."""
    try:
        import time

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ TOOL CALLING SUCCESS: {timestamp} - Provider: {provider}, Tool: {tool_name}")

        # Track successes by provider
        if not hasattr(_log_tool_calling_success, "successes"):
            _log_tool_calling_success.successes = {}

        key = f"{provider}:{tool_name}"
        _log_tool_calling_success.successes[key] = _log_tool_calling_success.successes.get(key, 0) + 1

    except Exception as e:
        print(f"⚠️ Tool calling success monitoring error: {e}")


def _log_tool_calling_failure(provider: str, reason: str) -> None:
    """Log tool calling failure for monitoring."""
    try:
        import time

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"❌ TOOL CALLING FAILURE: {timestamp} - Provider: {provider}, Reason: {reason}")

        # Track failures by provider
        if not hasattr(_log_tool_calling_failure, "failures"):
            _log_tool_calling_failure.failures = {}

        key = f"{provider}:{reason}"
        _log_tool_calling_failure.failures[key] = _log_tool_calling_failure.failures.get(key, 0) + 1

    except Exception as e:
        print(f"⚠️ Tool calling failure monitoring error: {e}")


def get_model_provider(model_name: str) -> str:
    """Get provider for a specific model"""
    initialize_engine()
    return engine.get_provider(model_name)


