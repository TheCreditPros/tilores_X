#!/usr/bin/env python3
"""
Tilores Direct Credit Analysis API - LangChain-Free Implementation
Replaces LangChain with direct OpenAI API calls and GraphQL queries
"""

import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

import openai
import requests
import tiktoken
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
except Exception:
    RateLimitExceeded = Exception  # type: ignore
    SlowAPIMiddleware = None  # type: ignore

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Tilores API configuration
TILORES_API_URL = os.getenv("TILORES_GRAPHQL_API_URL")
TILORES_CLIENT_ID = os.getenv("TILORES_CLIENT_ID")
TILORES_CLIENT_SECRET = os.getenv("TILORES_CLIENT_SECRET")
TILORES_TOKEN_URL = os.getenv("TILORES_OAUTH_TOKEN_URL")

# Known entity ID for Esteban Price (from our previous testing)
KNOWN_ENTITY_ID = "dc93a2cd-de0a - 444f-ad47 - 3003ba998cd3"

# Configure rate limiting
storage_uri = os.getenv("REDIS_URL", "memory://")
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per minute", "3000 per hour"],
    storage_uri=storage_uri,
)

# Warn when running in production without Redis-backed limits
if os.getenv("RAILWAY_ENVIRONMENT") and storage_uri.startswith("memory://"):
    print("⚠️  Production environment detected without Redis rate-limit storage. Limits will be per-process only.")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "gpt - 4o-mini"
    messages: List[ChatMessage]
    tools: Optional[List[dict]] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]
    usage: dict
    system_fingerprint: Optional[str] = None

class EmbeddingsRequest(BaseModel):
    input: str
    model: str = "text-embedding-ada - 002"
    encoding_format: str = "float"

class CompletionRequest(BaseModel):
    model: str = "gpt - 3.5 - turbo-instruct"
    prompt: str
    max_tokens: Optional[int] = 16
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: bool = False
    stop: Optional[str] = None

class DirectCreditAPI:
    def __init__(self):
        self.tilores_token = None
        self.token_expires_at = None

    async def get_tilores_token(self) -> str:
        """Get fresh Tilores API token"""
        if self.tilores_token and self.token_expires_at and datetime.now().timestamp() < self.token_expires_at:
            return self.tilores_token

        try:
            response = requests.post(TILORES_TOKEN_URL, data={
                'grant_type': 'client_credentials',
                'client_id': TILORES_CLIENT_ID,
                'client_secret': TILORES_CLIENT_SECRET
            })
            response.raise_for_status()

            token_data = response.json()
            self.tilores_token = token_data['access_token']
            # Set expiration 5 minutes before actual expiration
            expires_in = token_data.get('expires_in', 3600) - 300
            self.token_expires_at = datetime.now().timestamp() + expires_in

            return self.tilores_token
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get Tilores token: {str(e)}")

    async def query_tilores(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute GraphQL query against Tilores API"""
        token = await self.get_tilores_token()

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'query': query,
            'variables': variables or {}
        }

        try:
            response = requests.post(TILORES_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Tilores query failed: {str(e)}")

    async def get_credit_data(self, entity_id: str = None) -> Dict[str, Any]:
        """Get comprehensive credit data using our proven robust system"""
        entity_id = entity_id or KNOWN_ENTITY_ID

        query = """
        query($id:ID!){
          entity(input:{id:$id}){
            entity{
              records {
                CREDIT_RESPONSE {
                  CREDIT_BUREAU
                  CreditReportFirstIssuedDate
                  Report_ID
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
                }
              }
            }
          }
        }
        """

        result = await self.query_tilores(query, {"id": entity_id})

        if result.get("errors"):
            raise HTTPException(status_code=500, detail=f"GraphQL errors: {result['errors']}")

        return result.get("data", {}).get("entity", {}).get("entity", {})

    def extract_temporal_credit_data(self, records: List[Dict]) -> Dict[str, Any]:
        """Extract and categorize temporal credit data"""
        temporal_data = {}

        for record in records:
            credit_response = record.get('CREDIT_RESPONSE', {})
            if not credit_response:
                continue

            bureau = credit_response.get('CREDIT_BUREAU', 'Unknown')
            report_date = credit_response.get('CreditReportFirstIssuedDate', 'Unknown')

            if bureau not in temporal_data:
                temporal_data[bureau] = {}
            if report_date not in temporal_data[bureau]:
                temporal_data[bureau][report_date] = {
                    'scores': [],
                    'summary_parameters': {},
                    'utilization': None,
                    'inquiries': None,
                    'accounts': None,
                    'payments': None,
                    'delinquencies': None
                }

            # Extract credit scores
            scores = credit_response.get('CREDIT_SCORE', [])
            for score in scores:
                if score.get('Value'):
                    temporal_data[bureau][report_date]['scores'].append({
                        'value': score.get('Value'),
                        'model': score.get('ModelNameType', 'Unknown'),
                        'source': score.get('CreditRepositorySourceType', 'Unknown')
                    })

            # Extract summary parameters
            summary = credit_response.get('CREDIT_SUMMARY', {})
            data_set = summary.get('DATA_SET', [])

            for param in data_set:
                param_name = param.get('Name')
                param_value = param.get('Value')

                if param_name and param_value and param_value not in ['N/A', 'None', '']:
                    temporal_data[bureau][report_date]['summary_parameters'][param_name] = param_value

                    # Categorize key parameters
                    if 'utilization' in param_name.lower():
                        try:
                            temporal_data[bureau][report_date]['utilization'] = float(param_value)
                        except (ValueError, TypeError):
                            pass
                    elif 'inquir' in param_name.lower():
                        try:
                            temporal_data[bureau][report_date]['inquiries'] = int(param_value)
                        except (ValueError, TypeError):
                            pass
                    elif 'tradeline' in param_name.lower() or 'account' in param_name.lower():
                        try:
                            temporal_data[bureau][report_date]['accounts'] = int(param_value)
                        except (ValueError, TypeError):
                            pass
                    elif 'payment' in param_name.lower():
                        try:
                            temporal_data[bureau][report_date]['payments'] = float(param_value)
                        except (ValueError, TypeError):
                            pass
                    elif 'delinq' in param_name.lower():
                        try:
                            temporal_data[bureau][report_date]['delinquencies'] = int(param_value)
                        except (ValueError, TypeError):
                            pass

        return temporal_data

    async def analyze_credit_query(self, query: str) -> str:
        """Analyze credit query using OpenAI and return structured response"""

        # First, get the credit data
        credit_data = await self.get_credit_data()
        records = credit_data.get('records', [])

        if not records:
            return "No credit data found for the requested customer."

        # Extract temporal data
        temporal_data = self.extract_temporal_credit_data(records)

        # Prepare context for OpenAI
        context = {
            "temporal_credit_data": temporal_data,
            "query": query,
            "analysis_timestamp": datetime.now().isoformat()
        }

        # Create system prompt for credit analysis
        system_prompt = """You are a Credit Pros advisor with access to comprehensive credit data.
        Analyze the provided temporal credit data to answer the user's question accurately and professionally.

        Available data includes:
        - Credit scores across multiple bureaus (Equifax, Experian, TransUnion) over time
        - Summary parameters including utilization rates, inquiry counts, account counts, payment amounts, and delinquencies
        - Temporal progression showing changes over time

        Provide detailed, accurate analysis based on the actual data provided."""

        try:
            response = client.chat.completions.create(
                model="gpt - 4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Query: {query}\n\nCredit Data: {json.dumps(context, indent=2)}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error analyzing credit data: {str(e)}"

# Initialize the API
credit_api = DirectCreditAPI()

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    print("🚀 Starting Tilores Direct Credit Analysis API (LangChain-Free)")
    yield
    # Shutdown
    print("🛑 Shutting down Tilores Direct Credit Analysis API")

# Create FastAPI app
app = FastAPI(
    title="Tilores Direct Credit Analysis API",
    description="LangChain-free credit analysis with direct OpenAI and Tilores integration",
    version="2.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://tilores-x.up.railway.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach limiter and middleware
app.state.limiter = limiter
if SlowAPIMiddleware is not None:
    app.add_middleware(SlowAPIMiddleware)

# Rate limit exception handler for JSON responses
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc):
    """Return JSON error for rate limit exceeded instead of HTML."""
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "message": f"Rate limit exceeded: {exc.detail}",
                "type": "rate_limit_exceeded",
                "code": "rate_limit_exceeded",
            }
        },
        headers={"Retry-After": "60"},
    )

# Dashboard mounting removed - using OpenWebUI instead
print("ℹ️ Dashboard mounting skipped - using OpenWebUI for frontend interface")

# Token counting utilities for OpenAI compliance
def count_tokens(text: str, model: str = "gpt - 4") -> int:
    """Count tokens in text using tiktoken (OpenAI's tokenizer)"""
    try:
        # Map model names to tiktoken encodings
        encoding_map = {
            "gpt - 4o": "o200k_base",
            "gpt - 4o-mini": "o200k_base",
            "gpt - 5 - mini": "o200k_base",
            "gpt - 4": "cl100k_base",
            "gpt - 3.5 - turbo": "cl100k_base",
        }

        encoding_name = encoding_map.get(model, "cl100k_base")  # Default fallback
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(str(text)))
    except Exception:
        # Fallback: estimate 4 characters per token, minimum 1 for non-empty
        text_len = len(str(text))
        if text_len == 0:
            return 0
        return max(1, text_len // 4)

def count_messages_tokens(messages: List, model: str = "gpt - 4") -> int:
    """Count tokens for a list of messages following OpenAI's counting rules"""
    total = 0

    for message in messages:
        # Each message has overhead tokens
        total += 4  # <|start|>assistant<|message|>content<|end|>
        total += count_tokens(message.role, model)
        total += count_tokens(message.content, model)

    total += 2  # Every conversation has 2 additional tokens
    return total

def generate_unique_id(prefix: str = "chatcmpl") -> str:
    """Generate unique ID for OpenAI compliance"""
    return f"{prefix}-{uuid.uuid4().hex[:20]}"

def get_system_fingerprint() -> str:
    """Generate system fingerprint for version tracking"""
    return f"fp_{uuid.uuid4().hex[:10]}"

def determine_finish_reason(content: str, max_tokens: Optional[int] = None) -> str:
    """Determine finish reason based on response content"""
    if max_tokens and count_tokens(content) >= max_tokens:
        return "length"
    return "stop"

async def generate_streaming_response(request: ChatCompletionRequest, content: str):
    """Generate Server-Sent Events for streaming responses"""

    # Generate unique ID and metadata
    response_id = generate_unique_id()
    created = int(datetime.now().timestamp())
    system_fp = get_system_fingerprint()

    # Split content into chunks for streaming
    words = content.split()
    chunk_size = max(1, len(words) // 10)  # ~10 chunks

    # Send opening chunk
    opening_chunk = {
        "id": response_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": request.model,
        "system_fingerprint": system_fp,
        "choices": [{"index": 0, "delta": {"role": "assistant"}, "logprobs": None, "finish_reason": None}],
    }
    yield f"data: {json.dumps(opening_chunk)}\n\n"

    # Send content chunks
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i : i + chunk_size]
        chunk_content = " ".join(chunk_words)
        if i > 0:  # Add space before non-first chunks
            chunk_content = " " + chunk_content

        chunk_data = {
            "id": response_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": request.model,
            "system_fingerprint": system_fp,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": chunk_content},
                    "logprobs": None,
                    "finish_reason": None,
                }
            ],
        }

        yield f"data: {json.dumps(chunk_data)}\n\n"
        await asyncio.sleep(0.02)  # Optimized 20ms delay for faster streaming

    # Send final chunk with finish reason
    final_chunk = {
        "id": response_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": request.model,
        "system_fingerprint": system_fp,
        "choices": [
            {
                "index": 0,
                "delta": {},
                "logprobs": None,
                "finish_reason": determine_finish_reason(content, request.max_tokens),
            }
        ],
    }

    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"

@app.post("/v1/chat/completions")
@limiter.limit("100 / minute")  # More restrictive for chat completions
async def chat_completions(request: Request, chat_request: ChatCompletionRequest):
    """Fully OpenAI-compatible chat completions endpoint with streaming support"""
    # request_id = generate_unique_id()  # Not currently used

    try:
        # Extract the user's query
        user_message = None
        for message in chat_request.messages:
            if message.role == "user":
                user_message = message.content
                break

        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")

        # Analyze the credit query
        analysis = await credit_api.analyze_credit_query(user_message)

        # Calculate prompt tokens
        prompt_tokens = count_messages_tokens(chat_request.messages, chat_request.model)

        # Calculate completion tokens
        completion_tokens = count_tokens(analysis, chat_request.model)

        # Generate response metadata
        response_id = generate_unique_id()
        created = int(datetime.now().timestamp())
        system_fingerprint = get_system_fingerprint()
        finish_reason = determine_finish_reason(analysis, chat_request.max_tokens)

        # Handle streaming vs non-streaming
        if chat_request.stream:
            return StreamingResponse(
                generate_streaming_response(chat_request, analysis),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache"},
            )

        # Non-streaming response with full OpenAI compliance
        return {
            "id": response_id,
            "object": "chat.completion",
            "created": created,
            "model": chat_request.model,
            "system_fingerprint": system_fingerprint,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": analysis},
                    "logprobs": None,
                    "finish_reason": finish_reason,
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        }

    except Exception as e:
        # OpenAI-compatible error response
        error_id = generate_unique_id("chatcmpl-err")

        return {
            "id": error_id,
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": chat_request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": (
                            "I apologize, but I encountered an error "
                            "processing your request. Please try again."
                        ),
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "error": {
                "message": str(e),
                "type": "internal_error",
                "code": "processing_error",
            },
        }

@app.get("/v1/models")
@limiter.limit("500 / minute")  # Higher limit for model listing
async def list_models(request: Request):
    """OpenAI-compatible models endpoint for model discovery"""
    try:
        # Return available models
        models_data = [
            {
                "id": "gpt - 4o-mini",
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai",
                "permission": [],
                "root": "gpt - 4o-mini",
                "parent": None,
            },
            {
                "id": "gpt - 4o",
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai",
                "permission": [],
                "root": "gpt - 4o",
                "parent": None,
            }
        ]

        return {"object": "list", "data": models_data}

    except Exception as e:
        return {
            "object": "error",
            "error": {
                "message": f"Failed to retrieve models: {str(e)}",
                "type": "internal_error",
                "code": "model_list_error",
            },
        }

@app.get("/health")
@limiter.limit("1000 / minute")  # Health checks need higher limits
def health(request: Request):
    """Health check endpoint"""
    return {"status": "ok", "service": "tilores-direct-credit-api", "version": "2.0.0"}

@app.get("/test")
async def test_credit_data():
    """Test endpoint to verify credit data access"""
    try:
        credit_data = await credit_api.get_credit_data()
        records = credit_data.get('records', [])
        temporal_data = credit_api.extract_temporal_credit_data(records)

        return {
            "status": "success",
            "records_found": len(records),
            "bureaus": list(temporal_data.keys()),
            "sample_data": {
                bureau: {
                    date: {
                        "scores": len(data.get('scores', [])),
                        "parameters": len(data.get('summary_parameters', {}))
                    }
                    for date, data in dates.items()
                }
                for bureau, dates in temporal_data.items()
            }
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/v1/embeddings")
@limiter.limit("100 / minute")
async def create_embeddings(request: Request, embeddings_request: EmbeddingsRequest):
    """OpenAI-compatible embeddings endpoint"""
    # Mock embeddings response for compatibility
    return {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "index": 0,
                "embedding": [0.0] * 1536,  # Standard embedding dimension
            }
        ],
        "model": embeddings_request.model,
        "usage": {
            "prompt_tokens": count_tokens(embeddings_request.input),
            "total_tokens": count_tokens(embeddings_request.input),
        },
    }

@app.post("/v1/completions")
@limiter.limit("100 / minute")
async def create_completion(request: Request, completion_request: CompletionRequest):
    """OpenAI-compatible legacy completions endpoint"""
    # Convert to chat format for processing
    # messages = [{"role": "user", "content": completion_request.prompt}]  # Not currently used

    try:
        analysis = await credit_api.analyze_credit_query(completion_request.prompt)

        return {
            "id": generate_unique_id("cmpl"),
            "object": "text_completion",
            "created": int(datetime.now().timestamp()),
            "model": completion_request.model,
            "choices": [
                {
                    "text": analysis,
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": determine_finish_reason(analysis, completion_request.max_tokens),
                }
            ],
            "usage": {
                "prompt_tokens": count_tokens(completion_request.prompt),
                "completion_tokens": count_tokens(analysis),
                "total_tokens": count_tokens(completion_request.prompt) + count_tokens(analysis),
            },
        }
    except Exception as e:
        return {
            "error": {
                "message": str(e),
                "type": "internal_error",
                "code": "completion_error",
            }
        }

@app.get("/")
@limiter.limit("1000 / minute")
async def root(request: Request):
    """Root endpoint with API information"""
    return {
        "service": "Tilores Direct Credit Analysis API",
        "version": "2.0.0",
        "description": "LangChain-free credit analysis with direct OpenAI and Tilores integration",
        "compliance": {
            "openai_compatible": True,
            "features": [
                "Token usage tracking",
                "Server-Sent Events streaming",
                "Model discovery endpoint",
                "Unique request IDs",
                "System fingerprinting",
                "Proper finish reasons",
                "Embeddings API",
                "Legacy completions API",
            ],
        },
        "endpoints": {
            "chat_completions": "/v1 / chat/completions",
            "completions": "/v1 / completions",
            "embeddings": "/v1 / embeddings",
            "models": "/v1 / models",
            "health": "/health",
            "test": "/test",
        },
        "models": {
            "total": 2,
            "providers": ["openai"],
            "list": ["gpt - 4o-mini", "gpt - 4o"],
        },
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
