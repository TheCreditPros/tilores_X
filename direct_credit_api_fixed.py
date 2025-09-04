#!/usr/bin/env python3
"""
Multi-Provider Direct Credit Analysis API - Production Version
Optimized for performance with query-type-specific prompt routing
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

# Agenta.ai Integration - DEPRECATED for performance optimization
# All Agenta functionality has been replaced with optimized fallback system
# Files preserved in deprecated/agenta/ for future reinstatement if needed
AGENTA_INTEGRATION = False
agenta_manager = None
print("📝 Agenta.ai integration disabled - using optimized fallback system")

# Enhanced Chat Webhook Integration (PRESERVED - not Agenta-related)
try:
    from enhanced_chat_webhook import chat_webhook_router
    ENHANCED_CHAT_LOGGING = True
    print("✅ Enhanced chat logging endpoints imported")
except ImportError as e:
    print(f"⚠️ Enhanced chat logging not available: {e}")
    ENHANCED_CHAT_LOGGING = False
    chat_webhook_router = None

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
    # Optional advanced configuration fields
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

        # Critical fix: Validate input query
        if not query or not query.strip():
            print(f"⚠️ Empty query received for request #{request_id}")
            return json.dumps({
                "choices": [{
                    "message": {
                        "content": "Please provide a question or query about customer data. For example: 'who is customer@email.com' or 'credit analysis for John Smith'."
                    }
                }]
            })

        try:
            # Detect query type for prompt routing
            query_type = self.detect_query_type(query)
            print(f"🎯 Detected query type: {query_type}")

            # Use optimized query-type-specific prompts (Agenta.ai deprecated)
            # Query-type-specific prompts optimized for performance
            prompt_config = {
                "status": {
                    "system_prompt": "You are a customer service AI assistant. Provide concise account status information using bullet points.",
                    "temperature": 0.3,
                    "max_tokens": 200
                },
                "general": {
                    "system_prompt": "You are a helpful AI assistant. Provide concise, factual customer profile information using bullet points.",
                    "temperature": 0.3,
                    "max_tokens": 300
                },
                "credit": {
                    "system_prompt": "You are a helpful AI assistant analyzing customer data.",
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                "transaction": {
                    "system_prompt": "You are a helpful AI assistant analyzing customer data.",
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                "multi_data": {
                    "system_prompt": "You are a helpful AI assistant analyzing customer data.",
                    "temperature": 0.7,
                    "max_tokens": 1500
                }
            }.get(query_type, {
                "system_prompt": "You are a helpful AI assistant. Provide concise, factual customer profile information using bullet points.",
                "temperature": 0.3,
                "max_tokens": 300
            })

            prompt_config["source"] = "optimized"
            print(f"📝 Using optimized prompt for {query_type}")

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

            # Performance logging (Agenta.ai deprecated)
            duration = time.time() - start_time

            print(f"✅ Request #{request_id} completed in {duration:.1f}s")
            return response

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Processing error: {str(e)}"
            print(f"❌ Request #{request_id} failed in {duration:.1f}s: {error_msg}")

            # Error logging (Agenta.ai deprecated)

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
        """Process data analysis queries with dynamic prompts"""

        # Parse customer information from query
        customer_info = self._parse_query_for_customer(query)
        if not customer_info:
            return "I need customer information (email, phone, name, or client ID) to analyze their data."

        # Search for customer
        entity_id = self._search_for_customer(customer_info)
        if not entity_id:
            return "No customer records found for the provided information."

        # Use optimized prompt configuration
        system_prompt = prompt_config.get('system_prompt', 'You are a helpful AI assistant.')

        # Override temperature and max_tokens from prompt config if not explicitly set
        if temperature == 0.7:  # Default value
            temperature = prompt_config.get('temperature', 0.7)
        if max_tokens is None:
            max_tokens = prompt_config.get('max_tokens', 1000)

        # Create a simple response for demo
        data_context = f"Customer data analysis for entity {entity_id} - {query_type} analysis requested"

        # Create the full prompt with data context
        full_prompt = f"{system_prompt}\n\n**CUSTOMER DATA:**\n{data_context}\n\n**USER QUERY:** {query}"

        # Call LLM with dynamic prompt
        return self._call_llm(full_prompt, model, temperature, max_tokens)

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
    print("🚀 Multi-Provider Credit Analysis API starting up...")
    print("🌐 Server will bind to 0.0.0.0:8080")
    yield
    print("🛑 Application shutting down...")

app = FastAPI(
    title="Multi-Provider Credit Analysis API",
    description="Advanced credit analysis with optimized query-type-specific routing",
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

# Conversation logging function
def log_conversation(user_message: str, assistant_response: str, model: str, request_id: str = None):
    """Log full conversation to persistent storage"""
    try:
        if not request_id:
            request_id = f"req_{uuid.uuid4().hex[:8]}"
        
        conversation_log = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id,
            "model": model,
            "user_message": user_message,
            "assistant_response": assistant_response,
            "message_length": len(user_message),
            "response_length": len(assistant_response)
        }
        
        # Write to persistent log file
        log_file = "conversation_logs.jsonl"
        os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(conversation_log, ensure_ascii=False) + "\n")
        
        print(f"💾 Conversation logged: {request_id} - User: {len(user_message)} chars, Response: {len(assistant_response)} chars")
        
    except Exception as e:
        print(f"⚠️ Failed to log conversation: {e}")
        # Don't fail the request if logging fails

# Include enhanced chat webhook router (preserved - not Agenta-related)
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
    return {"message": "Multi-Provider Credit Analysis API", "version": "2.1.0"}

@app.get("/v1")
async def v1_root():
    """V1 API root - required for some integrations"""
    return {"message": "Multi-Provider Credit Analysis API v1", "version": "2.1.0"}

@app.get("/v1/models")
async def list_models():
    """List available models - OpenAI compatible endpoint"""
    return {
        "object": "list",
        "data": [
            {
                "id": "gpt-4o",
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai"
            },
            {
                "id": "gpt-4o-mini",
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai"
            },
            {
                "id": "gpt-3.5-turbo",
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai"
            },
            {
                "id": "gemini-1.5-flash",
                "object": "model",
                "created": 1677610602,
                "owned_by": "google"
            },
            {
                "id": "gemini-1.5-pro",
                "object": "model",
                "created": 1677610602,
                "owned_by": "google"
            },
            {
                "id": "gemini-2.0-flash-exp",
                "object": "model",
                "created": 1677610602,
                "owned_by": "google"
            },
            {
                "id": "gemini-2.5-flash",
                "object": "model",
                "created": 1677610602,
                "owned_by": "google"
            },
            {
                "id": "llama-3.3-70b-versatile",
                "object": "model",
                "created": 1677610602,
                "owned_by": "groq"
            },
            {
                "id": "deepseek-r1-distill-llama-70b",
                "object": "model",
                "created": 1677610602,
                "owned_by": "groq"
            }
        ]
    }

@app.get("/v1/conversations/recent")
async def get_recent_conversations(limit: int = 10):
    """Get recent conversation logs"""
    try:
        conversations = []
        log_file = "conversation_logs.jsonl"
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Get the last N lines
            for line in lines[-limit:]:
                try:
                    conversation = json.loads(line.strip())
                    conversations.append(conversation)
                except json.JSONDecodeError:
                    continue
        
        return {
            "conversations": conversations,
            "count": len(conversations),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        print(f"❌ Error retrieving conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """
    OpenAI-compatible chat completions endpoint with optimized query routing
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

        # Optional fields for advanced configuration
        prompt_id = request_data.get("prompt_id")
        prompt_version = request_data.get("prompt_version")

        print(f"🔍 DEBUG: Extracted - Model: {model}, Messages: {len(messages)}, Temp: {temperature}")
        if prompt_id:
            print(f"🔍 DEBUG: Advanced config - Prompt ID: {prompt_id}, Version: {prompt_version}")

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
            # Return helpful message instead of error
            return {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Please provide a question or query about customer data. For example: 'who is customer@email.com' or 'credit analysis for John Smith'."
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 20,
                    "total_tokens": 20
                }
            }

        # Generate unique request ID for logging
        request_id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
        
        # Process the request with optimized routing
        response_content = api.process_chat_request(
            query=query,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_id=prompt_id,
            prompt_version=prompt_version
        )
        
        # Log the complete conversation
        log_conversation(
            user_message=query,
            assistant_response=response_content,
            model=model,
            request_id=request_id
        )

        # Handle streaming vs non-streaming response
        if stream:
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
                "id": request_id,
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
    print("🚀 Starting Multi-Provider Credit Analysis API...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
