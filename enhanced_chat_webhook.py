#!/usr/bin/env python3
"""
Enhanced Chat Webhook Handler for Open WebUI
Captures full conversation logs including messages sent and received
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router for enhanced chat webhooks
chat_webhook_router = APIRouter(prefix="/webhooks/chat", tags=["chat-webhooks"])

class ChatMessage(BaseModel):
    """Individual chat message model"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None
    model: Optional[str] = None

class FullChatPayload(BaseModel):
    """Full chat conversation webhook payload"""
    chat_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    model: str
    messages: List[ChatMessage]
    metadata: Optional[Dict[str, Any]] = {}
    timestamp: str
    response_time: Optional[float] = None
    tokens_used: Optional[int] = None

class ChatCompletionPayload(BaseModel):
    """Chat completion event payload"""
    chat_id: str
    message_id: str
    user_id: Optional[str] = None
    model: str
    user_message: str
    assistant_response: str
    timestamp: str
    response_time: Optional[float] = None
    tokens_used: Optional[int] = None
    rating: Optional[str] = None

def _append_jsonl(filename: str, data: dict):
    """Append data to JSONL file"""
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    except Exception as e:
        logger.error(f"Failed to write to {filename}: {e}")

@chat_webhook_router.post("/completion")
async def handle_chat_completion(
    payload: ChatCompletionPayload,
    request: Request
):
    """
    Capture individual chat completion events with full message content.
    This logs each user message and AI response pair.
    """
    try:
        client_ip = request.client.host if request.client else "unknown"

        event = {
            "event_type": "chat_completion",
            "source": "openwebui",
            "received_at": datetime.utcnow().isoformat() + "Z",
            "ip": client_ip,
            "chat_id": payload.chat_id,
            "message_id": payload.message_id,
            "user_id": payload.user_id,
            "model": payload.model,
            "user_message": payload.user_message,
            "assistant_response": payload.assistant_response,
            "timestamp": payload.timestamp,
            "response_time": payload.response_time,
            "tokens_used": payload.tokens_used,
            "rating": payload.rating
        }

        logger.info(f"💬 Chat completion: user={payload.user_id} model={payload.model} chat={payload.chat_id}")
        _append_jsonl("chat_completions.jsonl", event)

        return {"status": "logged", "chat_id": payload.chat_id, "message_id": payload.message_id}

    except Exception as e:
        logger.error(f"❌ Error processing chat completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_webhook_router.post("/conversation")
async def handle_full_conversation(
    payload: FullChatPayload,
    request: Request
):
    """
    Capture full conversation logs with complete message history.
    This logs entire chat sessions with all messages.
    """
    try:
        client_ip = request.client.host if request.client else "unknown"

        event = {
            "event_type": "full_conversation",
            "source": "openwebui",
            "received_at": datetime.utcnow().isoformat() + "Z",
            "ip": client_ip,
            "chat_id": payload.chat_id,
            "user_id": payload.user_id,
            "session_id": payload.session_id,
            "model": payload.model,
            "message_count": len(payload.messages),
            "messages": [msg.dict() for msg in payload.messages],
            "metadata": payload.metadata,
            "timestamp": payload.timestamp,
            "response_time": payload.response_time,
            "tokens_used": payload.tokens_used
        }

        logger.info(f"📚 Full conversation: user={payload.user_id} model={payload.model} messages={len(payload.messages)}")
        _append_jsonl("full_conversations.jsonl", event)

        return {"status": "logged", "chat_id": payload.chat_id, "message_count": len(payload.messages)}

    except Exception as e:
        logger.error(f"❌ Error processing full conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_webhook_router.get("/recent")
async def get_recent_chats(limit: int = 10):
    """
    Get recent chat completions with full message content
    """
    try:
        recent_chats = []

        if os.path.exists("chat_completions.jsonl"):
            with open("chat_completions.jsonl", 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Get the last N lines
            for line in lines[-limit:]:
                try:
                    chat_data = json.loads(line.strip())
                    recent_chats.append(chat_data)
                except json.JSONDecodeError:
                    continue

        return {
            "recent_chats": recent_chats,
            "count": len(recent_chats),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        logger.error(f"❌ Error retrieving recent chats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_webhook_router.get("/conversation/{chat_id}")
async def get_conversation_by_id(chat_id: str):
    """
    Get full conversation by chat ID
    """
    try:
        conversations = []

        # Check both completion logs and full conversation logs
        for filename in ["chat_completions.jsonl", "full_conversations.jsonl"]:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            if data.get("chat_id") == chat_id:
                                conversations.append(data)
                        except json.JSONDecodeError:
                            continue

        if not conversations:
            raise HTTPException(status_code=404, detail=f"No conversation found for chat_id: {chat_id}")

        return {
            "chat_id": chat_id,
            "conversations": conversations,
            "count": len(conversations),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving conversation {chat_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_webhook_router.get("/health")
async def chat_webhook_health():
    """Health check for chat webhook endpoints"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "endpoints": {
            "chat_completion": "/webhooks/chat/completion",
            "full_conversation": "/webhooks/chat/conversation",
            "recent_chats": "/webhooks/chat/recent",
            "get_conversation": "/webhooks/chat/conversation/{chat_id}"
        },
        "log_files": {
            "completions": "chat_completions.jsonl",
            "conversations": "full_conversations.jsonl"
        }
    }

# Export router for integration
__all__ = ["chat_webhook_router"]
