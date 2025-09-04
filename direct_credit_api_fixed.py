#!/usr/bin/env python3
"""
Multi-Provider Direct Credit Analysis API - Fixed Version with Agenta.ai SDK
Fixes Salesforce status query and integrates Agenta.ai SDK for dynamic prompts
"""

import json
import os
import uuid
import hashlib
import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import List, Optional, Dict

import requests
import redis
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our Agenta SDK manager
try:
    from agenta_sdk_manager import agenta_manager
    AGENTA_INTEGRATION = True
    print("✅ Agenta SDK manager imported")
except ImportError as e:
    print(f"⚠️ Agenta SDK manager not available: {e}")
    AGENTA_INTEGRATION = False

# Import enhanced chat webhook
try:
    from enhanced_chat_webhook import chat_webhook_router
    ENHANCED_CHAT_LOGGING = True
    print("✅ Enhanced chat webhook imported")
except ImportError as e:
    print(f"⚠️ Enhanced chat webhook not available: {e}")
    ENHANCED_CHAT_LOGGING = False
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
        self.query_cache = {}
        self.cache_ttl = 300  # 5 minutes

        # Redis caching for Tilores responses
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            print("✅ Redis connected successfully")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
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
                "models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp", "gemini-2.5-flash"]
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
                           prompt_id: str = None, prompt_version: str = None) -> str:
        """Process chat request with dynamic prompt selection and fixed Salesforce status"""
        start_time = time.time()
        self.request_counter += 1
        request_id = self.request_counter

        print(f"🔄 Processing request #{request_id} started at {datetime.now().strftime('%H:%M:%S')}")

        try:
            # Detect query type for prompt routing
            query_type = self.detect_query_type(query)
            print(f"🎯 Detected query type: {query_type}")

            # Get appropriate prompt from Agenta SDK or local store
            if AGENTA_INTEGRATION and agenta_manager:
                prompt_config = agenta_manager.get_prompt_config(query_type, query)
                print(f"📝 Using prompt: {prompt_config.get('variant_slug', 'unknown')} (source: {prompt_config.get('source', 'unknown')})")
            else:
                # Fallback prompt configuration
                prompt_config = {
                    "source": "fallback",
                    "system_prompt": "You are a helpful AI assistant analyzing customer data.",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
                print("📝 Using fallback prompt configuration")

            # Create cache key
            cache_key = hashlib.md5(f"{query}_{model}_{query_type}_{prompt_config.get('variant_slug', '')}".encode()).hexdigest()

            # Check cache first
            redis_cached = self._get_redis_cache(cache_key)
            if redis_cached:
                duration = time.time() - start_time
                print(f"✅ Request #{request_id} completed in {duration:.1f}s (cached)")
                return redis_cached

            # Check memory cache
            if cache_key in self.query_cache:
                cached_data = self.query_cache[cache_key]
                if datetime.now().timestamp() - cached_data['timestamp'] < self.cache_ttl:
                    duration = time.time() - start_time
                    print(f"🚀 Memory cache hit: {cache_key[:8]}...")
                    print(f"✅ Request #{request_id} completed in {duration:.1f}s (memory cached)")
                    return cached_data['response']

            # Process based on query type
            if query_type == "status":
                response = self._process_status_query(query)
            else:
                # For other query types, use the full data analysis with dynamic prompt
                response = self._process_data_analysis_query(query, query_type, prompt_config, model, temperature, max_tokens)

            # Cache the response
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
        """Process data analysis queries with dynamic prompts and REAL customer data"""

        # Parse customer information from query
        customer_info = self._parse_query_for_customer(query)
        if not customer_info:
            return "I need customer information (email, phone, name, or client ID) to analyze their data."

        # Search for customer
        entity_id = self._search_for_customer(customer_info)
        if not entity_id:
            return "No customer records found for the provided information."

        # CRITICAL FIX: Fetch REAL customer data based on query type
        data_context = self._fetch_comprehensive_customer_data(entity_id, query_type)
        
        if not data_context or "No data found" in data_context:
            return f"No {query_type} data found for this customer."

        # Use dynamic prompt from Agenta
        system_prompt = prompt_config.get('system_prompt', 'You are a helpful AI assistant.')

        # Override temperature and max_tokens from prompt config if not explicitly set
        if temperature == 0.7:  # Default value
            temperature = prompt_config.get('temperature', 0.7)
        if max_tokens is None:
            max_tokens = prompt_config.get('max_tokens', 1000)

        # Create the full prompt with REAL data context
        full_prompt = f"{system_prompt}\n\n**CUSTOMER DATA:**\n{data_context}\n\n**USER QUERY:** {query}"

        # Call LLM with dynamic prompt
        return self._call_llm(full_prompt, model, temperature, max_tokens)

    def _fetch_comprehensive_customer_data(self, entity_id: str, query_type: str) -> str:
        """Fetch comprehensive customer data from Tilores API - CRITICAL FIX"""
        try:
            # Build comprehensive GraphQL query using WORKING format
            query_gql = """
            query($id: ID!) {
              entity(input: { id: $id }) {
                entity {
                  id
                  records {
                    id
                    EMAIL
                    FIRST_NAME
                    LAST_NAME
                    CLIENT_ID
                    PHONE_EXTERNAL
                    STATUS
                    ACTIVE
                    ENROLL_DATE
                    CREATED_DATE
                    CURRENT_PRODUCT
                    PRODUCT_NAME
                    TRANSACTION_AMOUNT
                    PAYMENT_METHOD
                    LAST_APPROVED_TRANSACTION
                    LAST_APPROVED_TRANSACTION_AMOUNT
                    CARD_LAST_4
                    CARD_TYPE
                    CALL_ID
                    CALL_DURATION
                    TICKETNUMBER
                    ZOHO_STATUS
                    CREDIT_RESPONSE {
                      CREDIT_BUREAU
                      CreditReportFirstIssuedDate
                      CREDIT_SCORE {
                        Value
                        ModelNameType
                        CreditRepositorySourceType
                      }
                    }
                  }
                  recordInsights {
                    totalRecords: count
                    creditScores: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_SCORE.Value")
                    creditBureaus: valuesDistinct(field: "CREDIT_RESPONSE.CREDIT_BUREAU")
                  }
                }
              }
            }
            """

            token = self.get_tilores_token()
            response = requests.post(
                self.tilores_api_url,
                json={"query": query_gql, "variables": {"id": entity_id}},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            if "errors" in result:
                print(f"GraphQL errors: {result['errors']}")
                return "Error fetching customer data from Tilores API."

            entity = result.get("data", {}).get("entity", {}).get("entity")
            if not entity:
                return "No customer data found for this entity ID."

            records = entity.get("records", [])
            insights = entity.get("recordInsights", {})

            if not records:
                return "No customer records found."

            # Format comprehensive customer data
            data_summary = self._format_customer_data_summary(records, insights, query_type)
            return data_summary

        except Exception as e:
            print(f"❌ Error fetching comprehensive customer data: {e}")
            return f"Error retrieving customer data: {str(e)}"

    def _format_customer_data_summary(self, records: list, insights: dict, query_type: str) -> str:
        """Format customer data into comprehensive summary"""
        
        # Extract key customer information
        customer_info = {}
        credit_data = []
        transaction_data = []
        contact_data = []
        
        for record in records:
            # Basic customer info
            if record.get("EMAIL"):
                customer_info["email"] = record["EMAIL"]
            if record.get("FIRST_NAME"):
                customer_info["first_name"] = record["FIRST_NAME"]
            if record.get("LAST_NAME"):
                customer_info["last_name"] = record["LAST_NAME"]
            if record.get("CLIENT_ID"):
                customer_info["client_id"] = record["CLIENT_ID"]
            if record.get("STATUS"):
                customer_info["status"] = record["STATUS"]
            if record.get("CURRENT_PRODUCT"):
                customer_info["current_product"] = record["CURRENT_PRODUCT"]
            if record.get("ENROLL_DATE"):
                customer_info["enroll_date"] = record["ENROLL_DATE"]
                
            # Credit information
            if record.get("CREDIT_RESPONSE"):
                credit_data.append(record["CREDIT_RESPONSE"])
                
            # Transaction information
            if record.get("TRANSACTION_AMOUNT"):
                transaction_data.append({
                    "amount": record.get("TRANSACTION_AMOUNT"),
                    "method": record.get("PAYMENT_METHOD"),
                    "date": record.get("CREATED_DATE")
                })
                
            # Contact information
            if record.get("PHONE_NUMBER"):
                contact_data.append({
                    "phone": record["PHONE_NUMBER"],
                    "call_id": record.get("CALL_ID"),
                    "call_duration": record.get("CALL_DURATION")
                })

        # Build comprehensive data summary
        summary = f"""
CUSTOMER PROFILE:
- Name: {customer_info.get('first_name', 'N/A')} {customer_info.get('last_name', 'N/A')}
- Email: {customer_info.get('email', 'N/A')}
- Client ID: {customer_info.get('client_id', 'N/A')}
- Status: {customer_info.get('status', 'N/A')}
- Product: {customer_info.get('current_product', 'N/A')}
- Enrolled: {customer_info.get('enroll_date', 'N/A')}

ACCOUNT INFORMATION:
- Total Records: {insights.get('totalRecords', len(records))}
- Entity ID: {records[0].get('id', 'N/A') if records else 'N/A'}

CREDIT ANALYSIS:
"""
        
        if credit_data:
            summary += f"- Credit Bureaus: {insights.get('creditBureaus', 'N/A')}\n"
            summary += f"- Credit Scores Available: {insights.get('creditScores', 'N/A')}\n"
            
            for i, credit in enumerate(credit_data[:3]):  # Show first 3 credit records
                bureau = credit.get('CREDIT_BUREAU', 'Unknown')
                score_info = credit.get('CREDIT_SCORE', {})
                score = score_info.get('Value') if isinstance(score_info, dict) else 'N/A'
                date = score_info.get('Date') if isinstance(score_info, dict) else 'N/A'
                
                summary += f"- {bureau} Credit Score: {score} (Date: {date})\n"
                
                if credit.get('CREDIT_UTILIZATION_RATE'):
                    summary += f"- {bureau} Utilization: {credit['CREDIT_UTILIZATION_RATE']}\n"
        else:
            summary += "- No credit data available\n"

        summary += f"\nTRANSACTION ANALYSIS:\n"
        if transaction_data:
            summary += f"- Transaction Methods: {insights.get('paymentMethods', 'N/A')}\n"
            summary += f"- Transaction Amounts: {insights.get('transactionAmounts', 'N/A')}\n"
            
            for i, trans in enumerate(transaction_data[:5]):  # Show first 5 transactions
                summary += f"- Transaction {i+1}: ${trans.get('amount', 'N/A')} via {trans.get('method', 'N/A')} on {trans.get('date', 'N/A')}\n"
        else:
            summary += "- No transaction data available\n"

        summary += f"\nCONTACT HISTORY:\n"
        if contact_data:
            for i, contact in enumerate(contact_data[:3]):  # Show first 3 contacts
                summary += f"- Contact {i+1}: {contact.get('phone', 'N/A')}"
                if contact.get('call_duration'):
                    summary += f" (Call Duration: {contact['call_duration']})"
                summary += "\n"
        else:
            summary += "- No contact history available\n"

        return summary.strip()

    def _call_llm(self, prompt: str, model: str, temperature: float, max_tokens: int) -> str:
        """Call appropriate LLM API based on model"""
        try:
            # Convert prompt to messages format
            ai_messages = [{"role": "system", "content": prompt}]

            # Determine provider and call appropriate API
            if model.startswith("gpt-") or model in self.providers["openai"]["models"]:
                return self._call_openai_with_context(ai_messages, model, temperature, max_tokens)
            elif model.startswith("gemini-") or model in self.providers["google"]["models"]:
                return self._call_google_with_context(ai_messages, model, temperature, max_tokens)
            elif model in self.providers["groq"]["models"]:
                return self._call_groq_with_context(ai_messages, model, temperature, max_tokens)
            else:
                # Default to OpenAI
                return self._call_openai_with_context(ai_messages, model, temperature, max_tokens)

        except Exception as e:
            return f"Error calling LLM: {str(e)}"

    def _call_openai_with_context(self, ai_messages, model, temperature=0.7, max_tokens=None):
        """Call OpenAI API with context"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.providers["openai"]["api_key"])

            response = client.chat.completions.create(
                model=model,
                messages=ai_messages,
                temperature=temperature,
                max_tokens=max_tokens or 1000
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI API error: {str(e)}"

    def _call_groq_with_context(self, ai_messages, model, temperature=0.7, max_tokens=None):
        """Call Groq API with context"""
        try:
            import openai
            client = openai.OpenAI(
                api_key=self.providers["groq"]["api_key"],
                base_url=self.providers["groq"]["base_url"]
            )

            response = client.chat.completions.create(
                model=model,
                messages=ai_messages,
                temperature=temperature,
                max_tokens=max_tokens or 1000
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Groq API error: {str(e)}"

    def _call_google_with_context(self, ai_messages, model, temperature=0.7, max_tokens=None):
        """Call Google Gemini API with context"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.providers["google"]["api_key"])

            # Convert messages to single prompt
            prompt = ""
            for msg in ai_messages:
                if msg["role"] == "system":
                    prompt += f"System: {msg['content']}\n"
                elif msg["role"] == "user":
                    prompt += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n"

            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens or 1000
                )
            )

            return response.text
        except Exception as e:
            return f"Google API error: {str(e)}"

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

# Include enhanced chat webhook router if available
if ENHANCED_CHAT_LOGGING and chat_webhook_router:
    app.include_router(chat_webhook_router)
    print("✅ Enhanced chat logging endpoints registered")

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

async def _get_models_list():
    """
    Helper function to generate the models list
    """
    models = []

    # Get current timestamp
    created_timestamp = int(time.time())

    # Add OpenAI models
    openai_models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
    for model_id in openai_models:
        models.append({
            "id": model_id,
            "object": "model",
            "created": created_timestamp,
            "owned_by": "tilores-openai"
        })

    # Add Google Gemini models
    gemini_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp", "gemini-2.5-flash"]
    for model_id in gemini_models:
        models.append({
            "id": model_id,
            "object": "model",
            "created": created_timestamp,
            "owned_by": "tilores-google"
        })

    # Add Groq models
    groq_models = ["llama-3.3-70b-versatile", "deepseek-r1-distill-llama-70b"]
    for model_id in groq_models:
        models.append({
            "id": model_id,
            "object": "model",
            "created": created_timestamp,
            "owned_by": "tilores-groq"
        })

    return {
        "object": "list",
        "data": models
    }

@app.get("/api/models")
async def list_models():
    """
    OpenAI-compatible models endpoint for Open WebUI integration
    Returns all available Tilores models across providers
    """
    return await _get_models_list()

@app.get("/v1/models")
async def list_models_v1():
    """
    OpenAI v1 models endpoint - standard OpenAI API endpoint
    Returns all available Tilores models across providers
    """
    return await _get_models_list()

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

        # Agenta.ai specific fields
        prompt_id = request_data.get("prompt_id")
        prompt_version = request_data.get("prompt_version")

        print(f"🔍 DEBUG: Extracted - Model: {model}, Messages: {len(messages)}, Temp: {temperature}")
        if prompt_id:
            print(f"🔍 DEBUG: Agenta.ai - Prompt ID: {prompt_id}, Version: {prompt_version}")

        if not messages:
            raise HTTPException(status_code=400, detail="Messages are required")

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

        # Process the request with Agenta.ai integration
        response_content = api.process_chat_request(
            query=query,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_id=prompt_id,
            prompt_version=prompt_version
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
