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
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core_app import get_available_models, initialize_engine, run_chain
from monitoring import monitor
from virtuous_cycle_api import virtuous_cycle_manager

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
    storage_uri=os.getenv("REDIS_URL", "memory://"),  # Use Redis if available, else memory
)

# FastAPI app - ultra-minimal for AnythingLLM integration
app = FastAPI(
    title="Tilores API for AnythingLLM",
    description="Fully OpenAI-compatible API with Tilores integration",
    version="6.4.0",  # Updated: Phone-optimized with 2-tier cache + batch processing
)

# Add CORS middleware for dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


class EmbeddingsRequest(BaseModel):
    input: str
    model: str = "text-embedding-ada-002"
    encoding_format: str = "float"


class CompletionRequest(BaseModel):
    model: str = "gpt-3.5-turbo-instruct"
    prompt: str
    max_tokens: Optional[int] = 16
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: bool = False
    stop: Optional[str] = None


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
@limiter.limit("100/minute")  # More restrictive for chat completions
async def chat_completions(request: Request, chat_request: ChatCompletionRequest):
    """Fully OpenAI-compatible chat completions endpoint with streaming support"""
    request_id = generate_unique_id()

    # Start monitoring timer
    timer_id = monitor.start_timer(
        "chat_completion",
        {"model": chat_request.model, "stream": chat_request.stream, "message_count": len(chat_request.messages)},
    )

    # LangSmith: Initialize API request tracing
    if LANGSMITH_AVAILABLE and engine and hasattr(engine, "langsmith_client"):
        try:
            if engine.langsmith_client:
                print(f"📊 LangSmith: Tracing API request {request_id}")
        except Exception as trace_error:
            print(f"⚠️ LangSmith API tracing error: {trace_error}")

    try:
        # Pass full conversation history to core_app for context preservation
        messages = [{"role": msg.role, "content": msg.content} for msg in chat_request.messages]

        # Calculate prompt tokens
        prompt_tokens = count_messages_tokens(chat_request.messages, chat_request.model)

        # Use core_app to process the request with full conversation context
        response = run_chain(messages, model=chat_request.model)

        # Extract clean content from any LangChain response type
        content = ""

        if isinstance(response, str):
            content = response
        elif hasattr(response, "content"):
            content = str(response.content) if response.content else "I'm ready to help."
        elif hasattr(response, "message") and hasattr(response.message, "content"):
            content = str(response.message.content)
        elif isinstance(response, dict):
            if "content" in response:
                content = str(response["content"])
            elif "message" in response and isinstance(response["message"], dict) and "content" in response["message"]:
                content = str(response["message"]["content"])
            else:
                content = "I'm ready to help."
        elif hasattr(response, "generations") and response.generations:
            # Handle LLMResult format - extract from generations
            try:
                first_generation = response.generations[0]
                if hasattr(first_generation, "text"):
                    content = str(first_generation.text)
                elif isinstance(first_generation, list) and len(first_generation) > 0:
                    first_item = first_generation[0]
                    if hasattr(first_item, "text"):
                        content = str(first_item.text)
                    elif hasattr(first_item, "message") and hasattr(first_item.message, "content"):
                        content = str(first_item.message.content)
                    else:
                        content = str(first_item)
                else:
                    content = str(first_generation)
            except (AttributeError, IndexError, TypeError):
                content = "I'm ready to help."
        else:
            content_str = str(response)
            if len(content_str) > 500 or "LLMResult" in content_str or "token_usage" in content_str:
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
                        "content": (
                            "I apologize, but I encountered an error " "processing your request. Please try again."
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


@app.get("/v1/virtuous-cycle/status")
@limiter.limit("100/minute")
async def virtuous_cycle_status(request: Request):
    """Get Virtuous Cycle monitoring and optimization status"""
    return virtuous_cycle_manager.get_status()


@app.post("/v1/virtuous-cycle/trigger")
@limiter.limit("10/minute")  # Lower limit for manual optimization triggers
async def trigger_virtuous_cycle(request: Request):
    """Manually trigger Virtuous Cycle optimization"""
    try:
        # Get request body for trigger reason
        body = await request.json() if request.headers.get("content-type") == "application/json" else {}
        reason = body.get("reason", "Manual API trigger")

        result = await virtuous_cycle_manager.trigger_manual_optimization(reason)
        return result

    except Exception as e:
        return {"success": False, "reason": f"Trigger failed: {str(e)}", "timestamp": datetime.utcnow().isoformat()}


@app.get("/v1")
@limiter.limit("1000/minute")
async def v1_root(request: Request):
    """OpenAI v1 API root endpoint for AnythingLLM validation"""
    available_models = get_available_models()

    return {
        "object": "api",
        "version": "v1",
        "service": "Tilores API for AnythingLLM",
        "openai_compatible": True,
        "endpoints": {"chat_completions": "/v1/chat/completions", "models": "/v1/models"},
        "models": {"total": len(available_models), "available": [model["id"] for model in available_models]},
    }


@app.post("/v1/embeddings")
@limiter.limit("100/minute")
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
@limiter.limit("100/minute")
async def create_completion(request: Request, completion_request: CompletionRequest):
    """OpenAI-compatible legacy completions endpoint"""
    # Convert to chat format for processing
    messages = [{"role": "user", "content": completion_request.prompt}]

    try:
        response = run_chain(messages, model=completion_request.model)
        content = (
            str(response) if isinstance(response, str) else str(getattr(response, "content", "Response generated"))
        )

        return {
            "id": generate_unique_id("cmpl"),
            "object": "text_completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": completion_request.model,
            "choices": [
                {
                    "text": content,
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": determine_finish_reason(content, completion_request.max_tokens),
                }
            ],
            "usage": {
                "prompt_tokens": count_tokens(completion_request.prompt),
                "completion_tokens": count_tokens(content),
                "total_tokens": count_tokens(completion_request.prompt) + count_tokens(content),
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
                "Embeddings API",
                "Legacy completions API",
            ],
        },
        "endpoints": {
            "chat_completions": "/v1/chat/completions",
            "completions": "/v1/completions",
            "embeddings": "/v1/embeddings",
            "models": "/v1/models",
            "health": "/health",
            "v1_root": "/v1",
        },
        "models": {
            "total": len(available_models),
            "providers": list(set(model["provider"] for model in available_models)),
            "list": [model["id"] for model in available_models],
        },
    }


# Background task management
background_tasks = []


async def startup_background_tasks():
    """Start background tasks for Virtuous Cycle monitoring."""
    try:
        # Start Virtuous Cycle monitoring
        monitoring_task = asyncio.create_task(virtuous_cycle_manager.start_monitoring())
        background_tasks.append(monitoring_task)

        print("🚀 Virtuous Cycle monitoring started")

    except Exception as e:
        print(f"⚠️ Failed to start background tasks: {e}")


async def shutdown_background_tasks():
    """Shutdown background tasks gracefully."""
    try:
        # Stop Virtuous Cycle monitoring
        await virtuous_cycle_manager.stop_monitoring()

        # Cancel all background tasks
        for task in background_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        print("🛑 Background tasks stopped")

    except Exception as e:
        print(f"⚠️ Error stopping background tasks: {e}")


# Add startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    print("🚀 Starting Tilores API with Virtuous Cycle integration")
    await startup_background_tasks()


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    print("🛑 Shutting down Tilores API")
    await shutdown_background_tasks()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
