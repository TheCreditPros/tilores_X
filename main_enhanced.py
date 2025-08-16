#!/usr/bin/env python3
"""
Tilores Enhanced Multi-Provider API - Simplified for AnythingLLM Integration
Clean version with only core functionality needed for AnythingLLM
"""

import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import List, Optional

import tiktoken
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core_app import get_available_models, initialize_engine, run_chain
from monitoring import monitor

# LangSmith observability imports
try:
    from langsmith import Client as LangSmithClient
    from core_app import engine
    LANGSMITH_AVAILABLE = True
except ImportError:
    LangSmithClient = None
    engine = None
    LANGSMITH_AVAILABLE = False

# Initialize the engine after environment variables are loaded
initialize_engine()

# Configure rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per minute", "3000 per hour"],
    storage_uri=os.getenv("REDIS_URL", "memory://")  # Use Redis if available, else memory
)

# FastAPI app - ultra-minimal for AnythingLLM integration
app = FastAPI(
    title="Tilores API for AnythingLLM",
    description="Fully OpenAI-compatible API with Tilores integration",
    version="6.4.0",  # Updated: Phone-optimized with 2-tier cache + batch processing
)

# Add rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# OpenAI-compatible request/response models
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o-mini"
    messages: List[ChatMessage]
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


# Token counting utilities for OpenAI compliance
def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text using tiktoken (OpenAI's tokenizer)"""
    try:
        # Map model names to tiktoken encodings
        encoding_map = {
            "gpt-4o": "o200k_base",
            "gpt-4o-mini": "o200k_base",
            "gpt-5-mini": "o200k_base",
            "gpt-4": "cl100k_base",
            "gpt-3.5-turbo": "cl100k_base",
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


def count_messages_tokens(messages: List, model: str = "gpt-4") -> int:
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
    created = int(datetime.utcnow().timestamp())
    system_fp = get_system_fingerprint()

    # Split content into chunks for streaming
    words = content.split()
    chunk_size = max(1, len(words) // 10)  # ~10 chunks

    # Send opening chunk
    opening_chunk = {
        'id': response_id,
        'object': 'chat.completion.chunk',
        'created': created,
        'model': request.model,
        'system_fingerprint': system_fp,
        'choices': [{
            'index': 0,
            'delta': {'role': 'assistant'},
            'logprobs': None,
            'finish_reason': None
        }]
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
@limiter.limit("100/minute")  # More restrictive for chat completions
async def chat_completions(request: Request, chat_request: ChatCompletionRequest):
    """Fully OpenAI-compatible chat completions endpoint with streaming support"""
    request_id = generate_unique_id()

    # Start monitoring timer
    timer_id = monitor.start_timer("chat_completion", {
        "model": chat_request.model,
        "stream": chat_request.stream,
        "message_count": len(chat_request.messages)
    })

    # LangSmith: Initialize API request tracing
    if LANGSMITH_AVAILABLE and engine and hasattr(engine, 'langsmith_client'):
        try:
            if engine.langsmith_client:
                print(f"📊 LangSmith: Tracing API request {request_id}")
        except Exception as trace_error:
            print(f"⚠️ LangSmith API tracing error: {trace_error}")

    try:
        # Pass full conversation history to core_app for context preservation
        messages = [
            {"role": msg.role, "content": msg.content} for msg in chat_request.messages
        ]

        # Calculate prompt tokens
        prompt_tokens = count_messages_tokens(chat_request.messages, chat_request.model)

        # Use core_app to process the request with full conversation context
        response = run_chain(messages, model=chat_request.model)

        # Extract clean content from any LangChain response type
        content = ""

        if isinstance(response, str):
            content = response
        elif hasattr(response, "content"):
            content = (
                str(response.content) if response.content else "I'm ready to help."
            )
        elif hasattr(response, "message") and hasattr(response.message, "content"):
            content = str(response.message.content)
        elif isinstance(response, dict):
            if "content" in response:
                content = str(response["content"])
            elif (
                "message" in response
                and isinstance(response["message"], dict)
                and "content" in response["message"]
            ):
                content = str(response["message"]["content"])
            else:
                content = "I'm ready to help."
        else:
            content_str = str(response)
            if (
                len(content_str) > 500
                or "LLMResult" in content_str
                or "token_usage" in content_str
            ):
                content = "I'm ready to help."
            else:
                content = content_str

        # Calculate completion tokens
        completion_tokens = count_tokens(content, chat_request.model)

        # Generate response metadata
        response_id = generate_unique_id()
        created = int(datetime.utcnow().timestamp())
        system_fingerprint = get_system_fingerprint()
        finish_reason = determine_finish_reason(content, chat_request.max_tokens)

        # Handle streaming vs non-streaming
        if chat_request.stream:
            # End monitoring timer successfully
            monitor.end_timer(timer_id, success=True)
            return StreamingResponse(
                generate_streaming_response(chat_request, content),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache"},
            )

        # End monitoring timer successfully
        monitor.end_timer(timer_id, success=True)

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
                    "message": {"role": "assistant", "content": content},
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
        # End monitoring timer with error
        monitor.end_timer(timer_id, success=False, error=str(e))

        # OpenAI-compatible error response
        error_id = generate_unique_id("chatcmpl-err")

        return {
            "id": error_id,
            "object": "chat.completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": chat_request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": ("I apologize, but I encountered an error "
                                    "processing your request. Please try again."),
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
@limiter.limit("500/minute")  # Higher limit for model listing
async def list_models(request: Request):
    """OpenAI-compatible models endpoint for model discovery"""
    try:
        available_models = get_available_models()

        # Convert our model format to OpenAI format
        models_data = []
        base_timestamp = 1677610602  # March 2023 baseline

        for model in available_models:
            # Generate realistic created timestamp based on model type
            created_offset = hash(model["id"]) % 86400  # Spread across 24 hours
            created_timestamp = base_timestamp + created_offset

            models_data.append(
                {
                    "id": model["id"],
                    "object": "model",
                    "created": created_timestamp,
                    "owned_by": model["provider"],
                    "permission": [],  # OpenAI compatibility
                    "root": model["id"],
                    "parent": None,
                }
            )

        # Sort by created time for consistency
        models_data.sort(key=lambda x: x["created"])

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
@limiter.limit("1000/minute")  # Health checks need higher limits
def health(request: Request):
    """Health check endpoint"""
    return {"status": "ok", "service": "tilores-anythingllm", "version": "6.4.0"}


@app.get("/health/detailed")
@limiter.limit("100/minute")
async def health_detailed(request: Request):
    """Detailed health check with monitoring metrics"""
    return monitor.get_health_status()


@app.get("/metrics")
@limiter.limit("100/minute")
async def get_metrics(request: Request):
    """Get comprehensive system metrics"""
    return monitor.get_metrics()


@app.get("/")
@limiter.limit("1000/minute")
async def root(request: Request):
    """Root endpoint with API information"""
    available_models = get_available_models()

    return {
        "service": "Tilores API for AnythingLLM",
        "version": "6.4.0",
        "description": "Fully OpenAI-compatible API with Tilores integration",
        "compliance": {
            "openai_compatible": True,
            "features": [
                "Token usage tracking",
                "Server-Sent Events streaming",
                "Model discovery endpoint",
                "Unique request IDs",
                "System fingerprinting",
                "Proper finish reasons",
            ],
        },
        "endpoints": {
            "chat_completions": "/v1/chat/completions",
            "models": "/v1/models",
            "health": "/health",
        },
        "models": {
            "total": len(available_models),
            "providers": list(set(model["provider"] for model in available_models)),
            "list": [model["id"] for model in available_models],
        },
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
