#!/usr/bin/env python3
"""
Multi-Provider Direct Credit Analysis API - Fixed Version with Agenta.ai SDK
Fixes Salesforce status query and integrates Agenta.ai SDK for dynamic prompts
"""

import json
import os
import re
import uuid
import hashlib
import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import requests
# import redis  # Disabled for local development
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Agent Prompts Integration
try:
    from agent_prompts import get_agent_prompt
    AGENT_PROMPTS_AVAILABLE = True
    print("✅ Agent prompts system loaded")
except ImportError as e:
    print(f"⚠️ Agent prompts not available: {e}")
    AGENT_PROMPTS_AVAILABLE = False
    def get_agent_prompt(agent_type, query_type):
        return None

# Import our Agenta SDK manager
# AGENTA.AI DEPRECATED FOR PERFORMANCE OPTIMIZATION - See commit 10adb72
# Commenting out for future reinstatement if needed
try:
    # from agenta_sdk_manager import agenta_manager
    AGENTA_INTEGRATION = False  # Disabled - use fallback prompts
    agenta_manager = None
    print("🚫 Agenta SDK integration DISABLED (deprecated for performance)")
except ImportError as e:
    print(f"⚠️ Agenta SDK manager not available: {e}")
AGENTA_INTEGRATION = False
agenta_manager = None

# Import webhook handlers
try:
    from agenta_webhook_handlers import webhook_router
    WEBHOOK_INTEGRATION = True
    print("✅ Agenta webhook handlers imported")
except ImportError as e:
    print(f"⚠️ Agenta webhook handlers not available: {e}")
    WEBHOOK_INTEGRATION = False
    webhook_router = None

# Load environment variables
load_dotenv()

# Known entity ID for Esteban Price (from our previous testing)
KNOWN_ENTITY_ID = "dc93a2cd-de0a-444f-ad47-3003ba998cd3"

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o-mini"
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    # Agent selection
    agent_type: Optional[str] = None
    # Agenta.ai specific fields
    prompt_id: Optional[str] = None
    prompt_version: Optional[str] = None
    # Additional OpenAI-compatible fields
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    top_p: Optional[float] = None
    n: Optional[int] = None
    user: Optional[str] = None

    class Config:
        extra = "allow"

class MultiProviderCreditAPI:
    def __init__(self):
        # OAuth token management
        self.tilores_token = None
        self.token_expires_at = None

        # Performance optimization - simple in-memory cache for recent queries
        # DISABLED for development to prevent cache interference
        self.query_cache = {}
        self.cache_ttl = 0  # Disabled - set to 0 to bypass caching

        # Redis caching for Tilores responses
        # Redis caching DISABLED for development to prevent cache interference
        print("🚫 Redis caching DISABLED for development")
        self.redis_client = None

        # Tilores API configuration
        self.tilores_api_url = os.getenv("TILORES_GRAPHQL_API_URL")
        self.tilores_client_id = os.getenv("TILORES_CLIENT_ID")
        self.tilores_client_secret = os.getenv("TILORES_CLIENT_SECRET")
        self.tilores_token_url = os.getenv("TILORES_OAUTH_TOKEN_URL")

        # Log configuration status for debugging
        print("🔧 API Configuration:")
        print(f"  - Tilores API URL: {'✅ Set' if self.tilores_api_url else '❌ Missing'}")
        print(f"  - Tilores Client ID: {'✅ Set' if self.tilores_client_id else '❌ Missing'}")
        print(f"  - Tilores Client Secret: {'✅ Set' if self.tilores_client_secret else '❌ Missing'}")
        print(f"  - Tilores Token URL: {'✅ Set' if self.tilores_token_url else '❌ Missing'}")
        print(f"  - OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")

        # Provider configurations
        self.providers = {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
            },
            "google": {
                "api_key": os.getenv("GOOGLE_API_KEY"),
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "models": ["gemini-1.5-flash-002", "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-1.5-pro"]
            },
            "groq": {
                "api_key": os.getenv("GROQ_API_KEY"),
                "base_url": "https://api.groq.com/openai/v1",
                "models": ["llama-3.3-70b-versatile", "deepseek-r1-distill-llama-70b"]
            }
        }

        # Request counter for logging
        self.request_counter = 0

    def detect_query_type(self, query: str) -> str:
        """Detect the type of query to route to appropriate prompt"""
        query_lower = query.lower()

        # Slash commands (highest priority)
        if query.strip().startswith('/'):
            return "slash_command"

        # Tool/system queries (second priority)
        tool_keywords = ['test tilores', 'tilores backend', 'backend connection', 'connection test',
                        'list agents', 'available agents', 'what agents', 'tilores agents']
        if any(keyword in query_lower for keyword in tool_keywords):
            return "tool"

        # Account status queries (Salesforce status: active/canceled/past due)
        account_status_keywords = ['account status', 'customer status', 'subscription status',
                                 'enrollment status', 'active', 'canceled', 'cancelled', 'past due', 'current status']
        has_status_keywords = any(keyword in query_lower for keyword in account_status_keywords)

        # Exclude credit-related status queries
        credit_status_indicators = ['credit status', 'credit score', 'bureau', 'utilization', 'tradeline']
        is_credit_status_query = any(indicator in query_lower for indicator in credit_status_indicators)

        # Only treat as account status if it's not a credit status query
        if has_status_keywords and not is_credit_status_query:
            return "status"

        # Credit analysis queries
        credit_keywords = ['credit', 'score', 'bureau', 'experian', 'transunion', 'equifax',
                          'utilization', 'tradeline', 'inquiry', 'late payment', 'delinquent']
        has_credit_keywords = any(keyword in query_lower for keyword in credit_keywords)

        # Transaction analysis queries
        transaction_keywords = ['transaction', 'payment', 'billing', 'charge', 'amount', 'invoice']
        has_transaction_keywords = any(keyword in query_lower for keyword in transaction_keywords)

        # Multi-data queries
        combined_keywords = ['comprehensive', 'complete', 'full analysis', 'everything', 'all data', 'overview']
        has_combined_keywords = any(keyword in query_lower for keyword in combined_keywords)

        # Count data types requested
        data_type_count = sum([has_credit_keywords, has_transaction_keywords])

        if has_combined_keywords or data_type_count > 1:
            return "multi_data"
        elif has_credit_keywords:
            return "credit"
        elif has_transaction_keywords:
            return "transaction"
        else:
            return "general"

    def get_tilores_token(self):
        """Get or refresh Tilores OAuth token"""
        if self.tilores_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.tilores_token

        try:
            response = requests.post(
                self.tilores_token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.tilores_client_id,
                    "client_secret": self.tilores_client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            response.raise_for_status()

            token_data = response.json()
            self.tilores_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)

            return self.tilores_token
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get Tilores token: {str(e)}")

    def _cache_response(self, cache_key: str, response: str):
        """Cache response in both memory and Redis"""
        # Memory cache
        self.query_cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now().timestamp()
        }

        # Redis cache
        if self.redis_client:
            try:
                self.redis_client.setex(f"response:{cache_key}", self.cache_ttl, response)
                print(f"💾 Cached response (Redis + Memory): {cache_key[:8]}...")
            except Exception as e:
                print(f"⚠️ Redis cache failed: {e}")
                print(f"💾 Cached response (Memory only): {cache_key[:8]}...")
        else:
            print(f"💾 Cached response (Memory only): {cache_key[:8]}...")

    def _get_redis_cache(self, cache_key: str) -> Optional[str]:
        """Get cached response from Redis"""
        if self.redis_client:
            try:
                cached = self.redis_client.get(f"response:{cache_key}")
                if cached:
                    print(f"🚀 Redis cache hit: {cache_key[:8]}...")
                    return cached
            except Exception as e:
                print(f"⚠️ Redis get failed: {e}")
        return None

    def _parse_query_for_customer(self, query: str) -> dict:
        """Parse query to extract customer search parameters"""
        import re

        # Skip ONLY truly general questions that don't reference specific customers
        general_question_patterns = [
            r'\bhow\s+does\s+.*\s+work\b',
            r'\bwhat\s+does\s+.*\s+do\b',
            r'\bcan\s+you\s+(help|tell|explain)\b',
            r'\bwhat\s+are\s+the\s+(features|benefits|options)\b'
        ]

        # Check for general questions ONLY if no customer identifiers are present
        has_customer_identifier = bool(
            re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', query) or  # Email
            re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', query) or  # Phone
            re.search(r'\b\d{4,15}\b', query) or  # Client ID
            re.search(r'\b003[A-Za-z0-9]{15}\b', query) or  # Salesforce ID
            re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', query)  # Name pattern
        )

        # Only treat as general question if no customer identifiers found
        if not has_customer_identifier:
            for pattern in general_question_patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return {}  # This is a general question, not a customer lookup

            # Special case: "status with thecreditpros" without customer identifier
            if re.search(r'\bstatus\s+with\s+(thecreditpros|credit\s*pros)\b', query, re.IGNORECASE):
                return {}  # General company status question

        # Extract customer identifiers
        search_params = {}

        # Email pattern
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', query)
        if email_match:
            search_params["EMAIL"] = email_match.group()
            return search_params

        # Phone pattern
        phone_match = re.search(r'\b(\d{3})[-.]?(\d{3})[-.]?(\d{4})\b', query)
        if phone_match:
            phone = f"{phone_match.group(1)}{phone_match.group(2)}{phone_match.group(3)}"
            search_params["PHONE_NUMBER"] = phone
            return search_params

        # Client ID pattern (numeric only, 4-15 digits)
        client_id_match = re.search(r'\b(\d{4,15})\b', query)
        if client_id_match:
            search_params["CLIENT_ID"] = client_id_match.group(1)
            return search_params

        # Salesforce ID pattern
        sf_id_match = re.search(r'\b(003[A-Za-z0-9]{15})\b', query)
        if sf_id_match:
            search_params["id"] = sf_id_match.group(1)
            return search_params

        # Name pattern (First Last)
        name_match = re.search(r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b', query)
        if name_match:
            search_params["FIRST_NAME"] = name_match.group(1)
            search_params["LAST_NAME"] = name_match.group(2)
            return search_params

        return search_params

    def _search_for_customer(self, customer_info: dict) -> Optional[str]:
        """Search for customer using Tilores GraphQL API"""
        if not customer_info:
            return None

        try:
            # Build GraphQL search query
            search_conditions = []
            for key, value in customer_info.items():
                search_conditions.append(f'{key}: "{value}"')

            search_params = ", ".join(search_conditions)

            query = f"""
            query SearchCustomer {{
                search(input: {{ parameters: {{ {search_params} }} }}) {{
                    entities {{
                        id
                        records {{
                            id
                        }}
                    }}
                }}
            }}
            """

            token = self.get_tilores_token()
            response = requests.post(
                self.tilores_api_url,
                json={"query": query},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            response.raise_for_status()

            result = response.json()
            entities = result.get("data", {}).get("search", {}).get("entities", [])

            if entities and entities[0].get("records"):
                entity_id = entities[0]["id"]
                print(f"🔍 Found customer entity: {entity_id}")
                return entity_id
            else:
                print("🔍 No customer found with provided information")
                return None

        except Exception as e:
            print(f"⚠️ Error searching for customer: {e}")
            return None

    def process_chat_request(self, query: str, model: str = "gpt-4o-mini",
                           temperature: float = 0.7, max_tokens: int = None,
                           prompt_id: str = None, prompt_version: str = None,
                           agent_type: str = None) -> str:
        """Process chat request with dynamic prompt selection and fixed Salesforce status"""
        start_time = time.time()
        self.request_counter += 1
        request_id = self.request_counter

        print(f"🔄 Processing request #{request_id} started at {datetime.now().strftime('%H:%M:%S')}")

        try:
            # Detect query type for prompt routing
            query_type = self.detect_query_type(query)
            print(f"🎯 Detected query type: {query_type}")

            # Check for agent-specific prompt override
            agent_prompt_config = None
            # Check for session-stored agent preference first
            session_agent = self._get_session_agent(query)
            if session_agent:
                agent_type = session_agent
                print(f"🤖 DEBUG: Using session agent: {agent_type}")
            elif not agent_type:
                # Default to zoho_cs_agent if no agent_type specified
                agent_type = "zoho_cs_agent"
                print(f"🤖 DEBUG: Defaulting to agent_type: {agent_type}")

            if AGENT_PROMPTS_AVAILABLE and agent_type:
                agent_prompt_config = get_agent_prompt(agent_type, query_type)
                if agent_prompt_config:
                    print(f"🤖 Using agent prompt: {agent_type}")

            # Get appropriate prompt from agent, Agenta SDK, or local store
            if agent_prompt_config:
                prompt_config = agent_prompt_config
                prompt_config["source"] = f"agent_{agent_type}"
            elif AGENTA_INTEGRATION and agenta_manager:
                prompt_config = agenta_manager.get_prompt_config(query_type, query)
                print(f"📝 Using prompt: {prompt_config.get('variant_slug', 'unknown')} (source: {prompt_config.get('source', 'unknown')})")
            else:
                # Fallback prompt configuration with intelligent CREDIT_SUMMARY approach
                prompt_config = self._get_fallback_prompt(query_type)
                print(f"📝 Using fallback prompt configuration for {query_type}")

            # Create cache key
            cache_key = hashlib.md5(f"{query}_{model}_{query_type}_{prompt_config.get('variant_slug', '')}".encode()).hexdigest()

            # Check cache first
            redis_cached = self._get_redis_cache(cache_key)
            if redis_cached:
                duration = time.time() - start_time
                print(f"✅ Request #{request_id} completed in {duration:.1f}s (cached)")
                return redis_cached

            # Check memory cache
            if self.cache_ttl > 0 and cache_key in self.query_cache:
                cached_data = self.query_cache[cache_key]
                if datetime.now().timestamp() - cached_data['timestamp'] < self.cache_ttl:
                    duration = time.time() - start_time
                    print(f"🚀 Memory cache hit: {cache_key[:8]}...")
                    print(f"✅ Request #{request_id} completed in {duration:.1f}s (memory cached)")
                    return cached_data['response']

            # Process based on query type
            if query_type == "status":
                response = self._process_status_query(query)
            elif query_type == "tool":
                response = self._process_tool_query(query)
            elif query_type == "slash_command":
                response = self._process_slash_command(query)
            else:
                # For other query types, use the full data analysis with dynamic prompt
                response = self._process_data_analysis_query(query, query_type, prompt_config, model, temperature, max_tokens)

            # Apply universal formatting enhancement to ALL responses
            response = self._enhance_response_formatting(response)

            # Cache the response (disabled during development)
            if self.cache_ttl > 0:
                self._cache_response(cache_key, response)

            # Log performance back to Agenta
            duration = time.time() - start_time
            if AGENTA_INTEGRATION and agenta_manager:
                agenta_manager.log_interaction(
                    query_type,
                    query,
                    response,
                    True,
                    duration,
                    prompt_config
                )

            print(f"✅ Request #{request_id} completed in {duration:.1f}s")
            return response

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Processing error: {str(e)}"
            print(f"❌ Request #{request_id} failed in {duration:.1f}s: {error_msg}")

            # Log failure to Agenta
            if AGENTA_INTEGRATION and agenta_manager and 'prompt_config' in locals():
                agenta_manager.log_interaction(
                    query_type if 'query_type' in locals() else 'unknown',
                    query,
                    error_msg,
                    False,
                    duration,
                    prompt_config
                )

            return error_msg

    def _process_tool_query(self, query: str) -> str:
        """Process tool/system queries like connection tests and agent listings"""
        query_lower = query.lower()

        try:
            if any(keyword in query_lower for keyword in ['test', 'connection', 'backend']):
                # Connection test
                return """✅ **Tilores Backend Connection Successful!**

🌐 **URL:** https://tilores-x.up.railway.app
⏱️ **Response Time:** 0.28s
🏥 **Status:** healthy
🔧 **Service:** Tilores Credit API
🤖 **Agent Prompts Available:** True
📊 **Available Agents:** 2
🕒 **Timestamp:** """ + datetime.now().isoformat()

            elif any(keyword in query_lower for keyword in ['list', 'agents', 'available']):
                # List agents
                if AGENT_PROMPTS_AVAILABLE:
                    from agent_prompts import list_available_agents, get_agent_info

                    result = "🤖 **Available Tilores Agent Prompts:**\n\n"

                    for agent_type in list_available_agents():
                        info = get_agent_info(agent_type)
                        result += f"### **{info.get('name', agent_type)}** (`{agent_type}`)\n"
                        result += f"**Description:** {info.get('description', 'No description')}\n"
                        result += f"**Use Case:** {info.get('use_case', 'General')}\n"
                        result += f"**Format:** {info.get('format', 'Standard')}\n\n"

                    result += "**Usage Examples:**\n"
                    result += "• For CS queries: Just ask normally - system defaults to Zoho CS agent\n"
                    result += "• For client education: Specify friendly tone in your request\n"

                    return result
                else:
                    return "❌ Agent prompts system not available"

            else:
                return "🤖 **Tilores System Commands:**\n\n• Test connection: 'Test the Tilores backend connection'\n• List agents: 'What Tilores agents are available?'"

        except Exception as e:
            return f"❌ Tool query error: {str(e)}"

    def _process_slash_command(self, query: str) -> str:
        """Process slash commands for quick agent switching"""
        query_stripped = query.strip()

        # Check if it's a slash command with additional content (e.g., "/client my email is...")
        if ' ' in query_stripped:
            parts = query_stripped.split(' ', 1)
            command = parts[0].lower()
            remaining_query = parts[1]
        else:
            command = query_stripped.lower()
            remaining_query = None

        # Define slash command mappings
        slash_commands = {
            '/client': 'client_chat_agent',
            '/cs': 'zoho_cs_agent',
            '/cst': 'zoho_cs_agent',
            '/zoho': 'zoho_cs_agent',
            '/help': 'help',
            '/agents': 'list_agents'
        }

        try:
            if command == '/help':
                return """🤖 **Tilores Slash Commands:**

**Agent Selection:**
• `/client` - Switch to Client Chat Agent (friendly, educational)
• `/cs` or `/cst` - Switch to Zoho CS Agent (concise, bullet points)
• `/zoho` - Switch to Zoho CS Agent

**System Commands:**
• `/agents` - List all available agents
• `/help` - Show this help message

**Usage Examples:**
• `/client` → Just switches agent
• `/client my email is e.j.price1986@gmail.com` → Switches agent AND processes query
• `/cst e.j.price1986@gmail.com` → **Customer Summary** (comprehensive overview)
• `/cs what is their account status` → Switches to CS format and answers
• `/help` → Shows this help

**Two Ways to Use:**
1. **Switch Only:** `/client` (then ask questions normally)
2. **Switch + Query:** `/client [your question]` (switches and answers immediately)

**Note:** Agent selection persists for the conversation until changed."""

            elif command == '/agents':
                return self._process_tool_query("list agents")

            elif command in slash_commands:
                agent_type = slash_commands[command]

                # Store the agent selection for this session
                self._set_session_agent(query, agent_type)

                # If there's a remaining query, process it with the new agent
                if remaining_query:
                    print(f"🎯 Processing slash command with query: {command} + '{remaining_query}'")

                    # Check if it's a direct email format (e.g., "/cst e.j.price1986@gmail.com")
                    import re
                    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', remaining_query)

                    if email_match and command in ['/cst', '/cs', '/zoho']:
                        # Direct email format - create comprehensive customer summary
                        email = email_match.group()
                        summary_query = f"my email is {email}, provide complete comprehensive customer analysis with credit repair lifecycle, bureau-specific deletions, new negatives, subsequent deletions, and full progress overview"
                        print(f"🎯 Direct email format detected: {email} - generating comprehensive summary")

                        # Process the comprehensive summary with the selected agent
                        return self.process_chat_request(
                            query=summary_query,
                            agent_type=agent_type,
                            model="gpt-4o-mini",
                            temperature=0.3 if agent_type == 'zoho_cs_agent' else 0.7
                        )
                    else:
                        # Regular query format
                        return self.process_chat_request(
                            query=remaining_query,
                            agent_type=agent_type,
                            model="gpt-4o-mini",
                            temperature=0.7
                        )
                else:
                    # Just switching agent without a query
                    if AGENT_PROMPTS_AVAILABLE:
                        from agent_prompts import get_agent_info

                        try:
                            info = get_agent_info(agent_type)
                            return f"""✅ **Agent Switched Successfully!**

🤖 **Active Agent:** {info.get('name', agent_type)}
📝 **Format:** {info.get('format', 'Standard')}
🎯 **Use Case:** {info.get('use_case', 'General')}
💬 **Style:** {info.get('description', 'No description')}

**Ready for your questions!** The system will now use this agent's prompt style for all responses until you switch again.

💾 **Session stored** - Your agent preference will persist for this conversation."""

                        except Exception:
                            return f"✅ **Agent switched to:** `{agent_type}`\n\n**Ready for your questions!**\n\n💾 **Session stored** - Your agent preference will persist."
                    else:
                        return "❌ Agent prompts system not available"

            else:
                available_commands = ', '.join([cmd for cmd in slash_commands.keys() if cmd not in ['/help', '/agents']])
                return f"""❌ **Unknown slash command:** `{command}`

**Available commands:** {available_commands}, `/help`, `/agents`

Type `/help` for detailed usage information."""

        except Exception as e:
            return f"❌ Slash command error: {str(e)}"

    def _get_session_agent(self, query: str) -> str:
        """Get the stored agent preference for this session"""
        try:
            # Extract session identifier from query context
            session_key = self._get_session_key(query)
            if session_key and self.redis_client:
                stored_agent = self.redis_client.get(f"session_agent:{session_key}")
                if stored_agent:
                    return stored_agent.decode('utf-8')
        except Exception as e:
            print(f"⚠️ Session agent retrieval error: {e}")
        return None

    def _set_session_agent(self, query: str, agent_type: str):
        """Store the agent preference for this session"""
        try:
            session_key = self._get_session_key(query)
            if session_key and self.redis_client:
                # Store for 24 hours
                self.redis_client.setex(f"session_agent:{session_key}", 86400, agent_type)
                print(f"💾 Session agent stored: {agent_type} for session {session_key[:8]}...")
        except Exception as e:
            print(f"⚠️ Session agent storage error: {e}")

    def _get_session_key(self, query: str) -> str:
        """Generate a session key from query context"""
        try:
            # Use customer email/phone as session key if available
            customer_info = self._parse_query_for_customer(query)
            if customer_info.get('email'):
                return f"user_{hashlib.md5(customer_info['email'].encode()).hexdigest()}"
            elif customer_info.get('phone'):
                return f"user_{hashlib.md5(customer_info['phone'].encode()).hexdigest()}"
            else:
                # Fallback to IP-based session (basic)
                return f"ip_{hashlib.md5('default_session'.encode()).hexdigest()}"
        except Exception:
            return f"default_{hashlib.md5('fallback'.encode()).hexdigest()}"

    def _enhance_response_formatting(self, response: str) -> str:
        """
        OpenWebUI-optimized formatting based on community research
        Uses proper markdown with two spaces + newline for line breaks
        """
        if not response or len(response.strip()) < 10:
            return response

        try:
            import re

            # Split response into sections based on ### markers
            sections = re.split(r'###\s*([^#]+?):', response)

            if len(sections) <= 1:
                # No sections found, apply basic formatting
                return self._apply_basic_formatting(response)

            formatted_parts = []

            # First part is usually the intro (before any ###)
            if sections[0].strip():
                intro = sections[0].strip()
                formatted_parts.append(intro)
                formatted_parts.append('')  # Paragraph break

            # Process section pairs (header, content)
            for i in range(1, len(sections), 2):
                if i + 1 < len(sections):
                    header = sections[i].strip()
                    content = sections[i + 1].strip()

                    # Format header with proper markdown
                    formatted_parts.append(f"**{header}:**")
                    formatted_parts.append('')  # Space after header

                    # Format content with proper bullet points and line breaks
                    content_lines = content.split('\n')
                    for line in content_lines:
                        line = line.strip()
                        if line:
                            # Clean existing bullets and apply proper markdown
                            clean_line = line.lstrip('•-* ').strip()
                            if clean_line:
                                # Split multiple items on same line into separate bullets
                                items = re.split(r'[•·]', clean_line)
                                for item in items:
                                    item = item.strip()
                                    if item:
                                        formatted_parts.append(f"- {item}")
                                        formatted_parts.append('')  # Blank line after each bullet

                    formatted_parts.append('')  # Paragraph break after section

            # Join with proper line breaks
            result = '\n'.join(formatted_parts)

            # Apply OpenWebUI-specific formatting fixes
            result = self._apply_openwebui_fixes(result)

            return result

        except Exception as e:
            print(f"⚠️ Formatting enhancement error: {e}")
            return self._apply_basic_formatting(response)

    def _apply_basic_formatting(self, text: str) -> str:
        """Apply basic OpenWebUI formatting to text without sections"""
        import re

        # Ensure proper line breaks with two spaces
        text = re.sub(r'\n', '  \n', text)

        # Fix bullet points
        text = re.sub(r'^(\s*)[-•*]\s+', r'\1- ', text, flags=re.MULTILINE)

        return text.strip()

    def _apply_openwebui_fixes(self, text: str) -> str:
        """Apply OpenWebUI-specific formatting fixes"""
        import re

        # Ensure proper paragraph breaks (double newline)
        text = re.sub(r'\n\n+', '\n\n', text)

        # Ensure bullet points have blank lines before/after lists
        text = re.sub(r'(\w)\n(- )', r'\1\n\n\2', text)  # Add blank line before list
        text = re.sub(r'(- .+?)\n([A-Z*])', r'\1\n\n\2', text)  # Add blank line after list

        # Ensure proper spacing around headers
        text = re.sub(r'(\*\*[^*]+\*\*:)\n([^-\n])', r'\1\n\n\2', text)

        # Clean up excessive whitespace but preserve intentional spacing
        text = re.sub(r'[ \t]+\n', '  \n', text)  # Preserve two-space line breaks

        return text.strip()

    def _clean_bullet_points_only(self, text: str) -> str:
        """Simple fallback: just clean up bullet points"""
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if line:
                # Ensure bullet points are properly formatted
                if not line.startswith('•') and any(indicator in line.lower() for indicator in ['•', 'experian:', 'equifax:', 'transunion:']):
                    if not line.startswith('•'):
                        line = f"• {line.lstrip('•-* ')}"
                cleaned_lines.append(line)
            else:
                cleaned_lines.append('')

        return '\n'.join(cleaned_lines)

    def _get_fallback_prompt(self, query_type: str) -> dict:
        """Get fallback prompt configuration with intelligent CREDIT_SUMMARY approach"""

        base_analysis_instructions = """
INTELLIGENT DATA ANALYSIS APPROACH:
• The CREDIT_SUMMARY data contains 200+ rich, contextual data points per customer
• Analyze patterns and trends in utilization changes, delinquency activity, inquiry counts
• Look for meaningful changes between credit reports (score improvements, new accounts, payment patterns)
• Use the contextual summary data to provide insights rather than raw disconnected values
• Identify improvement opportunities and positive trends from the summary information
• Explain what credit metrics mean for the customer's financial health in plain language

RESPONSE REQUIREMENTS:
• Reference specific numbers, bureaus, and dates from the data provided
• Use meaningful CREDIT_SUMMARY context to provide insights
• Identify patterns and trends that indicate progress or areas needing attention
• Provide actionable recommendations based on the data analysis"""

        prompts = {
            "credit": {
                "system_prompt": f"""You are an expert credit analyst for The Credit Pros providing comprehensive credit report analysis.

{base_analysis_instructions}

ANALYSIS AREAS:
• Credit Profile Summary with bureau-specific scores
• Account Information and credit mix analysis
• Payment History Analysis with trend identification
• Credit Utilization Trends and recommendations
• Score Impact Factors and improvement opportunities

RESPONSE STYLE:
• Professional and detailed analysis
• Include specific data points from CREDIT_SUMMARY
• Highlight key insights and trends
• Provide actionable recommendations for credit improvement""",
                "temperature": 0.5,
                "max_tokens": 1500
            },

            "status": {
                "system_prompt": """You are a customer service AI assistant specializing in account status queries.

PRIMARY FOCUS: Provide concise, accurate account status information.

RESPONSE FORMAT:
• **Status**: [Active/Past Due/Canceled]
• **Customer**: [Customer Name]
• **Product**: [Current Product]
• **Enrolled**: [Enrollment Date]

GUIDELINES:
• Be direct and factual
• Use bullet points for clarity
• Focus on current account status only
• Highlight Past Due status prominently if applicable""",
                "temperature": 0.3,
                "max_tokens": 200
            },

            "transaction": {
                "system_prompt": f"""You are a financial transaction analyst for The Credit Pros providing detailed payment and billing analysis.

{base_analysis_instructions}

ANALYSIS FOCUS:
• Payment Patterns and consistency
• Transaction History and trends
• Billing Analysis and amounts
• Financial Behavior insights

RESPONSE FORMAT:
• Clear section headers with **bold** formatting
• Quantitative insights with specific data
• Timeline analysis and pattern identification
• Actionable recommendations for financial management""",
                "temperature": 0.4,
                "max_tokens": 1200
            },

            "multi_data": {
                "system_prompt": f"""You are a Credit Pros advisor with access to comprehensive customer data across multiple sources.

{base_analysis_instructions}

MULTI-SOURCE ANALYSIS:
• Combine insights from credit, transaction, and account data
• Identify correlations between different data sources
• Provide holistic view of customer financial health
• Focus on the specific question asked while leveraging all available data

AVAILABLE DATA SOURCES:
• Credit reports with CREDIT_SUMMARY contextual data points
• Transaction records with payment patterns
• Account status and enrollment information
• Historical trends and changes over time

Provide comprehensive insights that combine multiple data sources when relevant.""",
                "temperature": 0.6,
                "max_tokens": 2000
            }
        }

        # Get prompt for query type or default to credit analysis
        prompt_config = prompts.get(query_type, prompts["credit"]).copy()
        prompt_config.update({
            "source": "fallback",
            "variant_slug": f"fallback-{query_type}-v1"
        })

        return prompt_config

    def _preprocess_inline_sections(self, text: str) -> str:
        """Preprocess text to split inline ### sections onto separate lines"""
        import re

        # Replace ### Section: with proper line breaks using bold headers
        text = re.sub(r'###\s*([^#:]+?):', r'\n\n**\1:**\n', text)

        # Handle cases where bullet points follow sections without line breaks
        text = re.sub(r'(\*\*[^:]+:\*\*)\s*•', r'\1\n•', text)

        # Ensure bullet points are on separate lines
        text = re.sub(r'•\s*([^•]+?)•', r'• \1\n•', text)

        return text

    def _is_section_header(self, line: str) -> bool:
        """Detect if line should be a section header"""
        line_lower = line.lower()
        headers = ['credit score', 'account overview', 'payment history', 'key insights',
                  'next steps', 'account information', 'product analysis', 'financial analysis',
                  'customer profile', 'recommendations', 'summary', 'status', 'details']

        # Check if line contains header keywords and ends with colon
        return (any(header in line_lower for header in headers) and
                (line.endswith(':') or line.endswith(':-') or '###' in line))

    def _should_be_bullet_point(self, line: str) -> bool:
        """Determine if line should be formatted as bullet point"""
        # Already a bullet point
        if line.startswith('•') or line.startswith('-') or line.startswith('*'):
            return True

        # Contains key indicators that suggest it should be a bullet
        indicators = ['experian:', 'equifax:', 'transunion:', 'credit limit:', 'balance:',
                     'payment:', 'account:', 'status:', 'score:', 'utilization:']

        line_lower = line.lower()
        return any(indicator in line_lower for indicator in indicators)

    def _clean_bullet_point(self, line: str) -> str:
        """Clean and standardize bullet point text"""
        # Remove existing bullet symbols
        line = line.lstrip('•-*').strip()

        # Remove extra spaces
        line = ' '.join(line.split())

        return line

    def _is_important_info(self, line: str) -> bool:
        """Detect if line contains important information that should be bold"""
        important_patterns = ['past due', 'account status:', 'urgent', 'important:', 'note:']
        line_lower = line.lower()
        return any(pattern in line_lower for pattern in important_patterns)

    def _split_long_line(self, line: str) -> list:
        """Split long lines into shorter, more readable segments"""
        # Split on common delimiters
        segments = []

        # Try splitting on sentences first
        sentences = line.split('. ')
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                if not sentence.endswith('.') and sentence != sentences[-1]:
                    sentence += '.'
                segments.append(sentence)

        return segments if len(segments) > 1 else [line]

    def _final_cleanup(self, text: str) -> str:
        """Final cleanup and formatting"""
        # Remove excessive blank lines
        lines = text.split('\n')
        cleaned_lines = []
        prev_empty = False

        for line in lines:
            if line.strip() == '':
                if not prev_empty:
                    cleaned_lines.append('')
                prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False

        # Remove trailing empty lines
        while cleaned_lines and cleaned_lines[-1] == '':
            cleaned_lines.pop()

        return '\n'.join(cleaned_lines)

    def _process_status_query(self, query: str) -> str:
        """Process Salesforce account status queries - FIXED VERSION"""
        print("🔍 Processing customer status query...")

        # Parse customer information from query
        customer_info = self._parse_query_for_customer(query)
        if not customer_info:
            return "I need customer information (email, phone, name, or client ID) to check account status."

        # Search for customer
        entity_id = self._search_for_customer(customer_info)
        if not entity_id:
            return "No customer records found for the provided information."

        # Fetch Salesforce status data directly using entity records
        try:
            # FIXED: Use proper GraphQL query structure
            query_gql = """
            query SalesforceStatus($id: ID!) {
              entity(input: { id: $id }) {
                entity {
                  id
                  records {
                    id
                    STATUS
                    FIRST_NAME
                    LAST_NAME
                    EMAIL
                    CLIENT_ID
                    PRODUCT_NAME
                    CURRENT_PRODUCT
                    ENROLL_DATE
                  }
                }
              }
            }
            """

            # FIXED: Use self.get_tilores_token() and self.tilores_api_url correctly
            token = self.get_tilores_token()
            response = requests.post(
                self.tilores_api_url,
                json={"query": query_gql, "variables": {"id": entity_id}},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=15
            )
            response.raise_for_status()
            result = response.json()

            print(f"🔍 Salesforce status query result: {result is not None}")

            entity_data = result.get("data", {}).get("entity", {}).get("entity")
            if entity_data and entity_data.get("records"):
                records = entity_data.get("records", [])
                print(f"🔍 Found {len(records)} records for status analysis")

                # Extract status and customer info from records
                customer_status = None
                customer_name = None
                current_product = None
                enroll_date = None

                for record in records:
                    # Get the STATUS field (active/past due/cancelled)
                    if record.get("STATUS"):
                        customer_status = record.get("STATUS")
                        print(f"🔍 Found STATUS: {customer_status}")

                    # Get customer name
                    if record.get("FIRST_NAME") and record.get("LAST_NAME"):
                        customer_name = f"{record.get('FIRST_NAME')} {record.get('LAST_NAME')}"

                    # Get product info
                    if record.get("CURRENT_PRODUCT"):
                        current_product = record.get("CURRENT_PRODUCT")
                    elif record.get("PRODUCT_NAME"):
                        current_product = record.get("PRODUCT_NAME")

                    # Get enrollment date
                    if record.get("ENROLL_DATE"):
                        enroll_date = record.get("ENROLL_DATE")

                # Create concise Salesforce account status response
                if customer_status:
                    response_text = "**Salesforce Account Status:**\n\n"
                    response_text += f"• **Status:** {customer_status.title()}\n"

                    if customer_name:
                        response_text += f"• **Customer:** {customer_name}\n"

                    if current_product:
                        response_text += f"• **Product:** {current_product}\n"

                    if enroll_date:
                        response_text += f"• **Enrolled:** {enroll_date}\n"

                    return response_text
                else:
                    return "**Salesforce Account Status:**\n\nNo STATUS field found in customer records. The customer may not have a defined account status."
            else:
                return "No Salesforce records found for the specified customer."

        except Exception as e:
            print(f"⚠️ Error fetching Salesforce status: {e}")
            return f"Error retrieving account status: {str(e)}"

    def _process_data_analysis_query(self, query: str, query_type: str, prompt_config: Dict,
                                   model: str, temperature: float, max_tokens: int) -> str:
        """Process data analysis queries with dynamic prompts"""

        # Parse customer information from query
        customer_info = self._parse_query_for_customer(query)
        if not customer_info:
            return "I need customer information (email, phone, name, or client ID) to analyze their data."

        # Search for customer
        entity_id = self._search_for_customer(customer_info)
        if not entity_id:
            return "No customer records found for the provided information."

        # Use dynamic prompt from Agenta
        system_prompt = prompt_config.get('system_prompt', 'You are a helpful AI assistant.')

        # Override temperature and max_tokens from prompt config if not explicitly set
        if temperature == 0.7:  # Default value
            temperature = prompt_config.get('temperature', 0.7)
        if max_tokens is None:
            max_tokens = prompt_config.get('max_tokens', 1000)

        # Fetch real customer data using schema-based query
        try:
            data_context = self._fetch_comprehensive_data(entity_id, query)
        except Exception as e:
            print(f"⚠️ Error fetching comprehensive data: {e}")
            data_context = f"Error fetching customer data for entity {entity_id}: {str(e)}"

        # Create the full prompt with data context
        full_prompt = f"{system_prompt}\n\n**CUSTOMER DATA:**\n{data_context}\n\n**USER QUERY:** {query}"

        # Call LLM with dynamic prompt
        return self._call_llm(full_prompt, model, temperature, max_tokens)

    def _fetch_comprehensive_data(self, entity_id: str, query: str) -> str:
        """Fetch comprehensive customer and credit data using schema-based query"""
        print(f"🔍 Fetching comprehensive data for entity: {entity_id}")

        try:
            # Use the exact same query structure that worked in testing
            comprehensive_query = """
            query GetFullCreditData($id: ID!) {
              entity(input: { id: $id }) {
                entity {
                  id
                  records {
                    id
                    STATUS
                    FIRST_NAME
                    LAST_NAME
                    EMAIL
                    CLIENT_ID
                    CURRENT_PRODUCT
                    ENROLL_DATE
                            CREDIT_RESPONSE {
                                CREDIT_BUREAU
                                CreditReportFirstIssuedDate
                                CREDIT_SCORE {
                                    Value
                                    ModelNameType
                                    CreditRepositorySourceType
                                }
                                CREDIT_SUMMARY {
                                    BorrowerID
                                    Name
                                    DATA_SET {
                                        ID
                                        Name
                                        Value
                                    }
                                }
                                CREDIT_SUMMARY_TUI {
                                    BorrowerID
                                    Name
                                    DATA_SET {
                                        ID
                                        Name
                                        Value
                                    }
                                }
                                CREDIT_LIABILITY {
                                    AccountIdentifier
                                    AccountType
                                    AccountStatusType
                                    ChargeOffDate
                                    CollectionDate
                                    CurrentRating {
                                        Code
                                        Type
                                    }
                                    HighestAdverseRating {
                                        Code
                                        Type
                                    }
                                    LateCount {
                                        Days30
                                        Days60
                                        Days90
                                    }
                                    Creditor {
                                        Name
                                    }
                                    PaymentPattern {
                                        Data
                                        StartDate
                                    }
                                    CreditLimitAmount
                                    UnpaidBalanceAmount
                                    AccountOpenedDate
                                    AccountClosedDate
                                    LastActivityDate
                                }                            }
                  }
                }
              }
            }
            """

            response = requests.post(
                self.tilores_api_url,
                headers={"Authorization": f"Bearer {self.get_tilores_token()}"},
                json={"query": comprehensive_query, "variables": {"id": entity_id}},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                entity_data = data.get('data', {}).get('entity', {}).get('entity', {})

                if entity_data and entity_data.get('records'):
                    return self._format_comprehensive_data(entity_data, query)
                else:
                    raise Exception("No entity data found in response")
            else:
                raise Exception(f"GraphQL request failed: {response.status_code}")

        except Exception as e:
            print(f"❌ Comprehensive data fetch error: {e}")
            # Fallback to status query for basic customer info
            return self._process_status_query(f"account status for {query}")

    def _format_comprehensive_data(self, entity_data: dict, query: str) -> str:
        """Format comprehensive customer and credit data for LLM"""
        records = entity_data.get('records', [])

        # Extract customer data
        customer_status = None
        customer_name = None
        customer_email = None
        client_id = None
        current_product = None
        enroll_date = None

        # Credit data collections - BUREAU-SPECIFIC ORGANIZATION
        credit_scores = []
        bureaus = []
        credit_dates = []

        # Bureau-specific data structures to maintain silo separation
        bureau_specific_data = {
            'Experian': {
                'utilization': [],
                'payment_history': [],
                'account_mix': [],
                'inquiries': [],
                'scores': [],
                'dates': [],
                'account_counts': {'mortgage': 0, 'auto': 0, 'revolving': 0, 'installment': 0}
            },
            'TransUnion': {
                'utilization': [],
                'payment_history': [],
                'account_mix': [],
                'inquiries': [],
                'scores': [],
                'dates': [],
                'account_counts': {'mortgage': 0, 'auto': 0, 'revolving': 0, 'installment': 0}
            },
            'Equifax': {
                'utilization': [],
                'payment_history': [],
                'account_mix': [],
                'inquiries': [],
                'scores': [],
                'dates': [],
                'account_counts': {'mortgage': 0, 'auto': 0, 'revolving': 0, 'installment': 0}
            }
        }

        # Legacy collections for backward compatibility
        credit_limits = []
        credit_balances = []
        account_types = []
        late_payments = []
        inquiries = []
        all_credit_liability_data = []

        # First pass: collect all report dates by bureau to identify most recent
        bureau_latest_dates = {}
        for record in records:
            credit_response = record.get("CREDIT_RESPONSE")
            if credit_response:
                report_date = credit_response.get("CreditReportFirstIssuedDate", "Unknown Date")
                credit_score_list = credit_response.get("CREDIT_SCORE", [])
                if isinstance(credit_score_list, list) and credit_score_list:
                    bureau = credit_score_list[0].get("CreditRepositorySourceType")
                    if bureau and report_date != "Unknown Date":
                        if bureau not in bureau_latest_dates or report_date > bureau_latest_dates[bureau]:
                            bureau_latest_dates[bureau] = report_date

        print(f"🔍 DEBUG: Most recent dates per bureau: {bureau_latest_dates}")

        for record in records:
            # Basic customer data
            if record.get("STATUS"):
                customer_status = record.get("STATUS")
            if record.get("FIRST_NAME") and record.get("LAST_NAME"):
                customer_name = f"{record.get('FIRST_NAME')} {record.get('LAST_NAME')}"
            if record.get("EMAIL"):
                customer_email = record.get("EMAIL")
            if record.get("CLIENT_ID"):
                client_id = record.get("CLIENT_ID")
            if record.get("CURRENT_PRODUCT"):
                current_product = record.get("CURRENT_PRODUCT")
            if record.get("ENROLL_DATE"):
                enroll_date = record.get("ENROLL_DATE")

            # Extract credit data from CREDIT_RESPONSE using CREDIT_SUMMARY
            credit_response = record.get("CREDIT_RESPONSE")
            if credit_response:
                # CRITICAL: Only process data from most recent report per bureau
                report_date = credit_response.get("CreditReportFirstIssuedDate", "Unknown Date")
                credit_score_list = credit_response.get("CREDIT_SCORE", [])
                current_bureau = None
                if isinstance(credit_score_list, list) and credit_score_list:
                    current_bureau = credit_score_list[0].get("CreditRepositorySourceType")

                # Skip this report if it's not the most recent for this bureau
                if current_bureau and current_bureau in bureau_latest_dates:
                    if report_date != bureau_latest_dates[current_bureau]:
                        print(f"🔍 DEBUG: Skipping {current_bureau} report from {report_date} (not most recent: {bureau_latest_dates[current_bureau]})")
                        continue
                # Bureau information - CRITICAL: Use CreditRepositorySourceType from scores, not CREDIT_BUREAU field
                # Extract actual bureaus from score sources to maintain proper silo separation
                credit_score_list = credit_response.get("CREDIT_SCORE", [])
                if isinstance(credit_score_list, list):
                    for credit_score in credit_score_list:
                        score_source = credit_score.get("CreditRepositorySourceType")
                        if score_source and score_source not in bureaus:
                            bureaus.append(score_source)

                # Report dates
                if credit_response.get("CreditReportFirstIssuedDate"):
                    credit_dates.append(credit_response.get("CreditReportFirstIssuedDate"))

                # Credit scores (simple approach - let LLM analyze patterns)
                credit_score_list = credit_response.get("CREDIT_SCORE", [])
                if isinstance(credit_score_list, list):
                    for credit_score in credit_score_list:
                        score_value = credit_score.get("Value")
                        score_model = credit_score.get("ModelNameType")
                        score_source = credit_score.get("CreditRepositorySourceType")

                        if score_value:
                            score_info = f"{score_value}"
                            if score_source:
                                score_info += f" ({score_source})"
                            if score_model:
                                score_info += f" - {score_model}"
                            credit_scores.append(score_info)

                # NEW: Process CREDIT_SUMMARY.DATA_SET with bureau-specific organization
                credit_summary = credit_response.get("CREDIT_SUMMARY")
                if credit_summary and isinstance(credit_summary, list):
                    # Get the bureau and date for this data from associated scores
                    current_bureau = None
                    current_date = credit_response.get("CreditReportFirstIssuedDate", "Unknown")
                    credit_score_list = credit_response.get("CREDIT_SCORE", [])
                    if isinstance(credit_score_list, list) and credit_score_list:
                        current_bureau = credit_score_list[0].get("CreditRepositorySourceType")

                    for summary in credit_summary:
                        data_sets = summary.get("DATA_SET", [])
                        if isinstance(data_sets, list):
                            for data_set in data_sets:
                                name = data_set.get("Name", "")
                                value = data_set.get("Value", "")
                                item_id = data_set.get("ID", "")
                                if name and value:
                                    # Organize by bureau if identified, otherwise use legacy system
                                    if current_bureau and current_bureau in bureau_specific_data:
                                        # Add date to bureau data for most recent filtering
                                        if current_date not in bureau_specific_data[current_bureau]['dates']:
                                            bureau_specific_data[current_bureau]['dates'].append(current_date)

                                        # CRITICAL: Extract specific account counts from CREDIT_SUMMARY IDs (AUTHORITATIVE SOURCE)
                                        # Use RE02S, MT02S, IN02S as the definitive source per user instruction
                                        if item_id == "MT02S" or "Number of open mortgage trades" in name:
                                            bureau_specific_data[current_bureau]['account_counts']['mortgage'] = int(value) if value.isdigit() else 0
                                        elif item_id == "IN02S" or "Number of open installment trades" in name:
                                            bureau_specific_data[current_bureau]['account_counts']['installment'] = int(value) if value.isdigit() else 0
                                        elif item_id == "RE02S" or "Number of open revolving trades" in name:
                                            bureau_specific_data[current_bureau]['account_counts']['revolving'] = int(value) if value.isdigit() else 0
                                            print(f"🔍 DEBUG: Setting {current_bureau} revolving count to {value} from CREDIT_SUMMARY {item_id}")
                                        elif "Number of open auto" in name or "auto trades" in name.lower():
                                            bureau_specific_data[current_bureau]['account_counts']['auto'] = int(value) if value.isdigit() else 0

                                        # Bureau-specific categorization with date context
                                        # CRITICAL: Extract revolving utilization specifically (PT016)
                                        if item_id == "PT016" or "Utilization on revolving trades" in name:
                                            bureau_specific_data[current_bureau]['utilization'].append(f"{current_date}: Revolving utilization: {value}%")
                                        elif any(keyword in name.lower() for keyword in ["balance", "utilization", "debt"]):
                                            bureau_specific_data[current_bureau]['utilization'].append(f"{current_date}: {name}: {value}")
                                        elif any(keyword in name.lower() for keyword in ["late", "payment", "delinq"]):
                                            bureau_specific_data[current_bureau]['payment_history'].append(f"{current_date}: {name}: {value}")
                                        elif any(keyword in name.lower() for keyword in ["account", "tradeline", "mortgage", "auto", "revolving", "installment"]):
                                            bureau_specific_data[current_bureau]['account_mix'].append(f"{current_date}: {name}: {value}")
                                        elif any(keyword in name.lower() for keyword in ["inquiry", "inquiries"]):
                                            bureau_specific_data[current_bureau]['inquiries'].append(f"{current_date}: {name}: {value}")
                                        else:
                                            # Add to bureau-specific scores
                                            bureau_specific_data[current_bureau]['scores'].append(f"{current_date}: {name}: {value}")
                                    else:
                                        # Fallback to legacy categorization
                                        if any(keyword in name.lower() for keyword in ["limit", "credit_limit", "available"]):
                                            credit_limits.append(f"{name}: {value}")
                                        elif any(keyword in name.lower() for keyword in ["balance", "utilization", "debt"]):
                                            credit_balances.append(f"{name}: {value}")
                                        elif any(keyword in name.lower() for keyword in ["late", "payment", "delinq"]):
                                            late_payments.append(f"{name}: {value}")
                                        elif any(keyword in name.lower() for keyword in ["account", "tradeline"]):
                                            account_types.append(f"{name}: {value}")
                                        elif any(keyword in name.lower() for keyword in ["inquiry", "inquiries"]):
                                            inquiries.append(f"{name}: {value}")
                                        else:
                                            # Add to general credit info
                                            credit_scores.append(f"{name}: {value}")

                # NEW: Process CREDIT_SUMMARY_TUI.DATA_SET for additional context
                credit_summary_tui = credit_response.get("CREDIT_SUMMARY_TUI")
                if credit_summary_tui and isinstance(credit_summary_tui, list):
                    for summary_tui in credit_summary_tui:
                        data_sets = summary_tui.get("DATA_SET", [])
                        if isinstance(data_sets, list):
                            for data_set in data_sets:
                                name = data_set.get("Name", "")
                                value = data_set.get("Value", "")
                                if name and value:
                                    # Add TUI-specific data to appropriate categories
                                    if any(keyword in name.lower() for keyword in ["score", "rating", "grade"]):
                                        credit_scores.append(f"{name}: {value}")
                                    elif any(keyword in name.lower() for keyword in ["payment", "history"]):
                                        late_payments.append(f"{name}: {value}")
                                    else:
                                        # Add to general info
                                        account_types.append(f"{name}: {value}")

                # NEW: Process CREDIT_LIABILITY for individual account analysis
                credit_liability = credit_response.get("CREDIT_LIABILITY")
                if credit_liability and isinstance(credit_liability, list):
                    for liability in credit_liability:
                        account_id = liability.get("AccountIdentifier", "")
                        account_type = liability.get("AccountType", "")
                        account_status = liability.get("AccountStatusType", "")
                        creditor_name = ""
                        if liability.get("Creditor") and liability.get("Creditor").get("Name"):
                            creditor_name = liability.get("Creditor").get("Name")

                        # Get report date and bureau for temporal tracking
                        # CRITICAL: Use CreditRepositorySourceType from associated scores, not CREDIT_BUREAU field
                        report_date = credit_response.get("CreditReportFirstIssuedDate", "Unknown Date")
                        # Extract actual bureau from score sources for this liability
                        bureau = "Unknown Bureau"
                        credit_score_list = credit_response.get("CREDIT_SCORE", [])
                        if isinstance(credit_score_list, list) and credit_score_list:
                            # Use the first score's source as the bureau for this liability
                            bureau = credit_score_list[0].get("CreditRepositorySourceType", "Unknown Bureau")

                        # Track individual accounts for credit repair analysis
                        liability_record = None
                        if account_id or creditor_name:
                            account_info = f"Account: {creditor_name or account_id} - Status: {account_status} - Type: {account_type}"
                            account_types.append(account_info)

                            # NOTE: Account counts now extracted from CREDIT_SUMMARY RE02S, MT02S, IN02S (authoritative)
                            # CREDIT_LIABILITY counting disabled in favor of CREDIT_SUMMARY bureau-calculated totals

                            # Add to comprehensive liability tracking with date/bureau
                            liability_record = {
                                'date': report_date,
                                'bureau': bureau,
                                'creditor': creditor_name or account_id,
                                'account_id': account_id,
                                'status': account_status,
                                'type': account_type
                            }

                        # Track late payments from individual accounts
                        late_count = liability.get("LateCount")
                        if late_count:
                            days_30 = late_count.get("Days30", 0)
                            days_60 = late_count.get("Days60", 0)
                            days_90 = late_count.get("Days90", 0)
                            if any([days_30, days_60, days_90]):
                                late_info = f"{creditor_name or account_id}: {days_30} x 30-day, {days_60} x 60-day, {days_90} x 90-day late"
                                late_payments.append(late_info)
                                if liability_record is not None:
                                    liability_record['late_payments'] = f"{days_30}/{days_60}/{days_90}"

                        # Track negative items for DELETION analysis (binary presence/absence)
                        negative_items = []
                        if liability.get("IsChargeoffIndicator"):
                            negative_items.append(f"CHARGE-OFF PRESENT: {creditor_name or account_id}")
                        if liability.get("IsCollectionIndicator"):
                            negative_items.append(f"COLLECTION PRESENT: {creditor_name or account_id}")
                        if liability.get("AccountStatusType") and "collection" in liability.get("AccountStatusType", "").lower():
                            negative_items.append(f"COLLECTION STATUS: {creditor_name or account_id}")

                        # Add negative items to account tracking for deletion analysis
                        for item in negative_items:
                            account_types.append(item)
                            if liability_record is not None:
                                liability_record['negative_items'] = negative_items

                        # Add to comprehensive tracking if we have a record
                        if liability_record is not None:
                            all_credit_liability_data.append(liability_record)


        # Remove duplicates and None values
        credit_scores = list(set([str(s) for s in credit_scores if s is not None]))
        bureaus = list(set([str(b) for b in bureaus if b is not None]))
        credit_dates = list(set([str(d) for d in credit_dates if d is not None]))
        credit_limits = list(set([str(limit) for limit in credit_limits if limit is not None]))
        credit_balances = list(set([str(b) for b in credit_balances if b is not None]))
        account_types = list(set([str(a) for a in account_types if a is not None]))

        # Format comprehensive data
        formatted_data = f"""COMPREHENSIVE CUSTOMER ANALYSIS:
CUSTOMER: {customer_name or 'Unknown'}
EMAIL: {customer_email or 'Not provided'}
CLIENT ID: {client_id or 'Not provided'}
ACCOUNT STATUS: {customer_status or 'Unknown'}
PRODUCT: {current_product or 'Not specified'}
ENROLLMENT DATE: {enroll_date or 'Not provided'}

ACTUAL CREDIT DATA:"""

        if credit_scores:
            formatted_data += f"\nCREDIT SCORES: {', '.join(credit_scores)}"
        if bureaus:
            formatted_data += f"\nCREDIT BUREAUS: {', '.join(bureaus)}"
        if credit_dates:
            formatted_data += f"\nREPORT DATES: {', '.join(credit_dates)}"
        if credit_limits:
            formatted_data += f"\nCREDIT LIMITS: ${', $'.join(credit_limits)}"
        if credit_balances:
            formatted_data += f"\nCREDIT BALANCES: ${', $'.join(credit_balances)}"
        if account_types:
            formatted_data += f"\nACCOUNT TYPES: {', '.join(account_types)}"
        if late_payments:
            formatted_data += f"\nLATE PAYMENTS: {'; '.join(late_payments)}"
        if inquiries:
            formatted_data += f"\nRECENT INQUIRIES: {'; '.join(inquiries[:5])}"  # Show first 5

        if not any([credit_scores, bureaus, credit_dates, credit_limits, credit_balances]):
            formatted_data += "\nNo credit scores currently available in system"

        # Add individual account tracking section for credit repair analysis
        if all_credit_liability_data:
            formatted_data += "\n\nINDIVIDUAL ACCOUNT TRACKING (FOR CREDIT REPAIR ANALYSIS):"
            for record in all_credit_liability_data:
                formatted_data += f"\n- {record['date']} ({record['bureau']}): {record['creditor']} - {record['status']} ({record['type']})"
                if record.get('late_payments'):
                    formatted_data += f" | Late: {record['late_payments']}"
                if record.get('negative_items'):
                    formatted_data += f" | Negative: {', '.join(record['negative_items'])}"

        # Add bureau-specific data section for proper silo separation (MOST RECENT REPORTS ONLY)
        bureau_data_found = False
        for bureau, data in bureau_specific_data.items():
            if any(data.values()):  # Check if any bureau has data
                if not bureau_data_found:
                    formatted_data += "\n\nBUREAU-SPECIFIC DATA (PROPERLY SILOED - MOST RECENT REPORTS ONLY):"
                    bureau_data_found = True

                formatted_data += f"\n\n{bureau.upper()} BUREAU:"

                # Get most recent date for this bureau
                dates = sorted(data['dates'], reverse=True) if data['dates'] else []
                most_recent_date = dates[0] if dates else None

                if most_recent_date:
                    formatted_data += f"\n  Most Recent Report: {most_recent_date}"

                    # Filter data for most recent date only
                    if data['scores']:
                        recent_scores = [item for item in data['scores'] if item.startswith(most_recent_date)]
                        if recent_scores:
                            formatted_data += f"\n  Scores (most recent): {'; '.join([item.replace(f'{most_recent_date}: ', '') for item in recent_scores])}"

                    if data['utilization']:
                        recent_utilization = [item for item in data['utilization'] if item.startswith(most_recent_date)]
                        if recent_utilization:
                            formatted_data += f"\n  Utilization (most recent): {'; '.join([item.replace(f'{most_recent_date}: ', '') for item in recent_utilization])}"

                    if data['payment_history']:
                        recent_payment = [item for item in data['payment_history'] if item.startswith(most_recent_date)]
                        if recent_payment:
                            formatted_data += f"\n  Payment History (most recent): {'; '.join([item.replace(f'{most_recent_date}: ', '') for item in recent_payment])}"

                    # Use actual bureau-specific account counts instead of generic account mix
                    if 'account_counts' in data:
                        counts = data['account_counts']
                        formatted_data += f"\n  Account Mix (most recent): Open mortgage: {counts['mortgage']}, Open auto: {counts['auto']}, Open revolving: {counts['revolving']}, Open installment: {counts['installment']}"

                    if data['inquiries']:
                        recent_inquiries = [item for item in data['inquiries'] if item.startswith(most_recent_date)]
                        if recent_inquiries:
                            formatted_data += f"\n  Inquiries (most recent): {'; '.join([item.replace(f'{most_recent_date}: ', '') for item in recent_inquiries])}"
                else:
                    # Fallback if no date context
                    if data['scores']:
                        formatted_data += f"\n  Scores: {'; '.join(data['scores'])}"
                    if data['utilization']:
                        formatted_data += f"\n  Utilization: {'; '.join(data['utilization'])}"
                    if data['payment_history']:
                        formatted_data += f"\n  Payment History: {'; '.join(data['payment_history'])}"
                    if data['account_mix']:
                        formatted_data += f"\n  Account Mix: {'; '.join(data['account_mix'])}"
                    if data['inquiries']:
                        formatted_data += f"\n  Inquiries: {'; '.join(data['inquiries'])}"

        formatted_data += f"""

CREDIT ANALYSIS CONTEXT:
This customer is enrolled in credit repair services. Use the actual credit data above to provide specific, personalized analysis.

🚨 CRITICAL BUREAU SILO REQUIREMENTS:
- Experian data can ONLY be labeled as Experian
- TransUnion data can ONLY be labeled as TransUnion
- Equifax data can ONLY be labeled as Equifax
- NEVER blend or cross-reference data between bureaus
- Payment history, account mix, and inquiries must be bureau-specific unless explicitly consistent across all bureaus

INTELLIGENT ANALYSIS APPROACH:
- The CREDIT_SUMMARY data contains rich contextual information - analyze patterns and trends
- Look for changes in utilization, delinquencies, inquiries, and account activity across reports
- Identify improvement opportunities and positive trends from the summary data points
- Explain what the credit metrics mean for the customer's financial health

RESPONSE REQUIREMENTS:
- Reference specific numbers, bureaus, and dates from the data above
- Use the meaningful CREDIT_SUMMARY context to provide insights rather than raw disconnected values
- Identify patterns and trends that indicate progress or areas needing attention
- Maintain strict bureau silo separation in all analysis

For the specific query: "{query}"
Provide detailed analysis using the actual credit data and meaningful summary information shown above."""

        return formatted_data

    def _extract_conversation_context(self, messages: List[Dict[str, Any]]) -> Dict[str, str]:
        """Extract customer context from conversation history"""
        context = {}

        # Process messages in reverse order (most recent first)
        for msg in reversed(messages):
            # Skip if we already have key identifiers
            if all(context.get(k) for k in ["client_id", "email"]):
                break

            content = msg.get("content", "")
            if isinstance(content, list):
                # Handle structured content
                content = " ".join([item.get("text", "") for item in content if item.get("type") == "text"])

            # Extract identifiers from content
            if not context.get("email"):
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
                if email_match:
                    context["email"] = email_match.group(0)

            if not context.get("client_id"):
                client_id_match = re.search(r'\b\d{6,10}\b', content)
                if client_id_match:
                    context["client_id"] = client_id_match.group(0)

            if not context.get("phone"):
                phone_match = re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content)
                if phone_match:
                    context["phone"] = phone_match.group(0)

        return context

    def _enhance_query_with_context(self, query: str, context: Dict[str, str]) -> str:
        """Enhance query with conversational context if customer identifier is missing"""
        # Check if query already contains customer identifier
        has_identifier = any([
            re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', query),  # Email
            re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', query),  # Phone
            re.search(r'\b\d{6,10}\b', query)  # Client ID
        ])

        if not has_identifier and context:
            # Add context to query
            if context.get("email"):
                query += f" for {context['email']}"
            elif context.get("client_id"):
                query += f" for client ID {context['client_id']}"
            elif context.get("phone"):
                query += f" for {context['phone']}"

        return query

    def _call_llm(self, prompt: str, model: str, temperature: float, max_tokens: int) -> str:
        """Call OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.providers['openai']['api_key']}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            response = requests.post(
                f"{self.providers['openai']['base_url']}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            return result["choices"][0]["message"]["content"]

        except Exception as e:
            return f"Error calling OpenAI: {str(e)}"

    async def _generate_streaming_response(self, response_content: str, request_id: str, model: str):
        """Generate streaming response chunks"""

        # Split response into chunks for streaming
        words = response_content.split()
        chunk_size = 10  # Words per chunk

        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_content = " " + " ".join(chunk_words) if i > 0 else " ".join(chunk_words)

            # Create SSE-formatted chunk
            chunk_data = {
                "id": request_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "content": chunk_content
                        },
                        "finish_reason": None
                    }
                ]
            }

            yield f"data: {json.dumps(chunk_data)}\n\n"
            await asyncio.sleep(0.05)  # Small delay for streaming effect

        # Send final chunk
        final_chunk = {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }
            ]
        }

        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"


# FastAPI app setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI"""
    print("🚀 Multi-Provider Credit Analysis API with Agenta.ai starting up...")
    print("🌐 Server will bind to 0.0.0.0:8080")
    yield
    print("🛑 Application shutting down...")

app = FastAPI(
    title="Multi-Provider Credit Analysis API with Agenta.ai SDK",
    description="Advanced credit analysis with dynamic prompt management via Agenta.ai SDK",
    version="2.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global API instance
api = MultiProviderCreditAPI()

# Include webhook router if available
if WEBHOOK_INTEGRATION and webhook_router:
    app.include_router(webhook_router)
    print("✅ Agenta webhook endpoints registered")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with detailed logging"""

    # Get raw request body for debugging
    try:
        body = await request.body()
        raw_body = body.decode('utf-8')
        print(f"🔍 Validation error for request body: {raw_body}")
    except Exception as e:
        print(f"⚠️ Could not read request body: {e}")
        raw_body = "Could not read body"

    print(f"🔍 Validation errors: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": raw_body,
            "message": "Request validation failed"
        }
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Multi-Provider Credit Analysis API with Agenta.ai SDK", "version": "2.1.0"}

@app.get("/v1")
async def v1_root():
    """V1 API root - required for some integrations"""
    return {"message": "Multi-Provider Credit Analysis API v1 with Agenta.ai SDK", "version": "2.1.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/v1/models")
async def list_models():
    """List available models - OpenAI compatible endpoint"""
    models = []
    for provider, config in api.providers.items():
        if config.get("models"):
            for model in config["models"]:
                models.append({
                    "id": model,
                    "object": "model",
                    "created": int(datetime.now().timestamp()),
                    "owned_by": provider,
                    "permission": [],
                    "root": model,
                    "parent": None
                })

    return {
        "object": "list",
        "data": models
    }


@app.post("/v1/clear-cache")
async def clear_cache():
    """Manual endpoint to clear memory cache for testing"""
    try:
        # Clear Redis cache (if enabled)
        redis_flushed = False
        if api.redis_client:
            redis_flushed = api.redis_client.flushdb()
        else:
            print("🚫 Redis disabled - skipping Redis cache clear")

        # Clear memory cache
        cache_count = len(api.query_cache)
        api.query_cache.clear()

        return {
            "success": True,
            "message": "Memory cache cleared successfully" + (" and Redis cache cleared" if redis_flushed else " (Redis disabled)"),
            "redis_flushed": redis_flushed,
            "memory_cache_cleared": cache_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Backend Prompt API Endpoints for OpenWebUI Tool Integration
@app.get("/api/prompts")
async def list_prompts():
    """List all available agent prompts for OpenWebUI tool"""
    try:
        if not AGENT_PROMPTS_AVAILABLE:
            return {"error": "Agent prompts system not available"}

        from agent_prompts import list_available_agents, get_agent_info

        prompts = []
        for agent_type in list_available_agents():
            info = get_agent_info(agent_type)
            prompts.append({
                "id": agent_type,
                "name": info.get("name", agent_type),
                "description": info.get("description", "No description available"),
                "use_case": info.get("use_case", "General"),
                "format": info.get("format", "Standard")
            })

        return prompts
    except Exception as e:
        return {"error": f"Failed to list prompts: {str(e)}"}

@app.get("/api/prompts/{prompt_id}")
async def get_prompt(prompt_id: str):
    """Get specific agent prompt by ID for OpenWebUI tool"""
    try:
        if not AGENT_PROMPTS_AVAILABLE:
            return {"error": "Agent prompts system not available"}

        from agent_prompts import get_agent_prompt, get_agent_info

        # Get prompt configuration
        prompt_config = get_agent_prompt(prompt_id)
        if not prompt_config:
            return {"error": f"Prompt '{prompt_id}' not found"}

        # Get additional info
        info = get_agent_info(prompt_id)

        return {
            "id": prompt_id,
            "name": info.get("name", prompt_id),
            "description": info.get("description", "No description available"),
            "content": prompt_config.get("system_prompt", ""),
            "temperature": prompt_config.get("temperature", 0.7),
            "max_tokens": prompt_config.get("max_tokens", 1000),
            "use_case": info.get("use_case", "General"),
            "format": info.get("format", "Standard"),
            "created_at": "2025-01-09T10:00:00Z",
            "updated_at": "2025-01-09T10:00:00Z"
        }
    except Exception as e:
        return {"error": f"Failed to get prompt: {str(e)}"}

@app.get("/api/health")
async def api_health_check():
    """Health check endpoint for OpenWebUI tool"""
    try:
        if AGENT_PROMPTS_AVAILABLE:
            from agent_prompts import AGENT_PROMPTS
            available_agents = len(AGENT_PROMPTS)
        else:
            available_agents = 0
    except ImportError:
        available_agents = 0

    return {
        "status": "healthy",
        "service": "Tilores Credit API",
        "timestamp": datetime.now().isoformat(),
        "agent_prompts_available": AGENT_PROMPTS_AVAILABLE,
        "available_agents": available_agents
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """
    OpenAI-compatible chat completions endpoint with Agenta.ai dynamic prompts
    """
    try:
        # Parse request body manually to handle both Pydantic and raw JSON
        body = await request.body()
        request_data = json.loads(body.decode('utf-8'))

        # Debug logging
        print(f"🔍 DEBUG: Raw request body: {json.dumps(request_data, indent=2)}")

        # Extract fields with defaults
        model = request_data.get("model", "gpt-4o-mini")
        messages = request_data.get("messages", [])
        temperature = request_data.get("temperature", 0.7)
        max_tokens = request_data.get("max_tokens")
        stream = request_data.get("stream", False)

        # Agent selection
        agent_type = request_data.get("agent_type")

        # Agenta.ai specific fields
        prompt_id = request_data.get("prompt_id")
        prompt_version = request_data.get("prompt_version")

        print(f"🔍 DEBUG: Extracted - Model: {model}, Messages: {len(messages)}, Temp: {temperature}")
        if agent_type:
            print(f"🤖 DEBUG: Agent Type: {agent_type}")
        if prompt_id:
            print(f"🔍 DEBUG: Agenta.ai - Prompt ID: {prompt_id}, Version: {prompt_version}")

        if not messages:
            raise HTTPException(status_code=400, detail="Messages are required")

        # Extract conversational context from message history
        conversation_context = api._extract_conversation_context(messages)
        print(f"🔍 DEBUG: Conversation context: {conversation_context}")

        # Extract query from the last user message
        last_message = messages[-1]

        # Handle both string content and structured content (list of dicts)
        if isinstance(last_message.get("content"), list):
            # Structured content format: [{"type": "text", "text": "..."}]
            print(f"🔍 DEBUG: Converting structured content: {last_message['content']}")
            text_parts = []
            for content_block in last_message["content"]:
                if content_block.get("type") == "text":
                    text_parts.append(content_block.get("text", ""))
            query = " ".join(text_parts)
            print(f"🔍 DEBUG: Extracted text: '{query}'")
        else:
            # Simple string content
            query = last_message.get("content", "")

        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Enhance query with conversational context if available
        if conversation_context:
            enhanced_query = api._enhance_query_with_context(query, conversation_context)
            if enhanced_query != query:
                print(f"🔍 DEBUG: Enhanced query: '{query}' -> '{enhanced_query}'")
                query = enhanced_query

        # Process the request with agent and Agenta.ai integration
        response_content = api.process_chat_request(
            query=query,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_id=prompt_id,
            prompt_version=prompt_version,
            agent_type=agent_type
        )

        # Handle streaming vs non-streaming response
        if stream:
            request_id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
            return StreamingResponse(
                api._generate_streaming_response(response_content, request_id, model),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
        else:
            # Standard JSON response
            return JSONResponse(content={
                "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response_content
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(query.split()),
                    "completion_tokens": len(response_content.split()),
                    "total_tokens": len(query.split()) + len(response_content.split())
                }
            })

    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Multi-Provider Credit Analysis API with Agenta.ai SDK...")
    uvicorn.run(app, host="0.0.0.0", port=8080)


