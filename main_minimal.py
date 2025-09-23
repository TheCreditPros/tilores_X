"""
Minimal Tilores API for Railway Deployment
This is a stripped-down version that can successfully deploy to Railway.
Full functionality is available in main_enhanced.py for local development.
"""

import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Minimal FastAPI app for Railway deployment
app = FastAPI(
    title="Tilores API - Railway Deployment",
    description="Minimal deployment mode - full functionality in local development",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "tilores-railway-deployment",
        "version": "1.0.0",
        "message": "Railway deployment successful - full features in local development"
    }

@app.post("/v1/chat/completions")
async def chat_completions(chat_request: dict):
    """Ultra-minimal chat completions endpoint for Railway deployment"""
    try:
        # Get user input safely
        user_input = ""
        if "messages" in chat_request and chat_request["messages"]:
            user_input = chat_request["messages"][-1].get("content", "")

        # Simple response
        if user_input.strip().startswith('/'):
            response = f"Railway Deployment Mode - Command: {user_input[:30]}... Full features in local development."
        else:
            response = "Tilores LLM API - Railway deployment. Full features available locally."

        # Simple response format
        return {
            "id": "railway-deployment",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": chat_request.get("model", "gpt-4o-mini"),
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(user_input.split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(user_input.split()) + len(response.split())
            }
        }

    except Exception as e:
        return {
            "error": f"Railway deployment error: {str(e)}",
            "status": "deployment_mode"
        }

@app.get("/v1/models")
async def list_models():
    """List available models"""
    return {
        "object": "list",
        "data": [
            {
                "id": "gpt-4o-mini",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "railway-deployment"
            },
            {
                "id": "llama-3.3-70b-versatile",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "railway-deployment"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
