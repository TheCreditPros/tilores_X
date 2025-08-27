#!/usr/bin/env python3
"""
Simplified OpenWebUI for TILORES X Integration
Provides real LLM chat functionality with model selection
"""

import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


# Models
class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4"
    provider: str = "openai"
    temperature: float = 0.7
    max_tokens: int = 1000


class ChatResponse(BaseModel):
    response: str
    model: str
    provider: str
    tokens_used: int
    response_time: float


# Create FastAPI app
app = FastAPI(title="TILORES X OpenWebUI", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
TILORES_API_URL = os.getenv("TILORES_API_URL", "https://tilores-x.up.railway.app")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Available models
AVAILABLE_MODELS = {
    "openai": {
        "gpt-4": {"description": "Most capable GPT model", "max_tokens": 8192},
        "gpt-3.5-turbo": {"description": "Fast and efficient", "max_tokens": 4096},
    },
    "anthropic": {
        "claude-3-opus": {"description": "Most capable Claude model", "max_tokens": 200000},
        "claude-3-sonnet": {"description": "Balanced performance", "max_tokens": 200000},
        "claude-3-haiku": {"description": "Fastest Claude model", "max_tokens": 200000},
    },
    "google": {
        "gemini-pro": {"description": "Advanced reasoning", "max_tokens": 30720},
        "gemini-pro-vision": {"description": "Multimodal capabilities", "max_tokens": 30720},
    },
}


@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """Serve the chat interface"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TILORES X OpenWebUI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .chat-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 90vw;
            max-width: 900px;
            height: 85vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }

        .chat-header h1 {
            font-size: 24px;
            font-weight: 600;
        }

        .chat-header p {
            opacity: 0.9;
            margin-top: 5px;
        }

        .model-controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            padding: 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }

        .model-selector, .provider-selector {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
        }

        .model-selector label, .provider-selector label {
            font-size: 12px;
            font-weight: 600;
            color: #666;
            text-transform: uppercase;
        }

        .model-selector select, .provider-selector select {
            padding: 8px 15px;
            border: 2px solid #e9ecef;
            border-radius: 15px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
            min-width: 150px;
        }

        .model-selector select:focus, .provider-selector select:focus {
            border-color: #667eea;
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }

        .message {
            margin-bottom: 20px;
            display: flex;
            align-items: flex-start;
        }

        .message.user {
            justify-content: flex-end;
        }

        .message-content {
            max-width: 70%;
            padding: 15px 20px;
            border-radius: 20px;
            word-wrap: break-word;
            white-space: pre-wrap;
        }

        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 5px;
        }

        .message.assistant .message-content {
            background: white;
            color: #333;
            border: 1px solid #e9ecef;
            border-bottom-left-radius: 5px;
        }

        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin: 0 10px;
        }

        .message.user .message-avatar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .message.assistant .message-avatar {
            background: #28a745;
            color: white;
        }

        .message-meta {
            font-size: 11px;
            color: #666;
            margin-top: 5px;
            opacity: 0.8;
        }

        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e9ecef;
        }

        .chat-input-form {
            display: flex;
            gap: 10px;
        }

        .chat-input {
            flex: 1;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }

        .chat-input:focus {
            border-color: #667eea;
        }

        .send-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }

        .send-button:hover {
            transform: translateY(-2px);
        }

        .send-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .status-indicator {
            text-align: center;
            padding: 10px;
            font-size: 14px;
            color: #666;
        }

        .status-indicator.connected {
            color: #28a745;
        }

        .status-indicator.error {
            color: #dc3545;
        }

        .typing-indicator {
            display: none;
            padding: 15px 20px;
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 20px;
            margin-bottom: 20px;
            color: #666;
            font-style: italic;
        }

        .typing-indicator.show {
            display: block;
        }

        .welcome-message {
            text-align: center;
            padding: 20px;
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 TILORES X OpenWebUI</h1>
            <p>Real LLM Chat Interface with Model Selection</p>
        </div>

        <div class="model-controls">
            <div class="provider-selector">
                <label>Provider</label>
                <select id="providerSelector">
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="google">Google</option>
                </select>
            </div>

            <div class="model-selector">
                <label>Model</label>
                <select id="modelSelector">
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                </select>
            </div>
        </div>

        <div class="status-indicator" id="statusIndicator">
            Connecting to TILORES X...
        </div>

        <div class="chat-messages" id="chatMessages">
            <div class="welcome-message">
                Welcome! Select a provider and model above, then start chatting with real AI models.
            </div>
        </div>

        <div class="typing-indicator" id="typingIndicator">
            AI is thinking...
        </div>

        <div class="chat-input-container">
            <form class="chat-input-form" id="chatForm">
                <input
                    type="text"
                    class="chat-input"
                    id="chatInput"
                    placeholder="Ask me anything! I'll respond using the selected AI model..."
                    autocomplete="off"
                >
                <button type="submit" class="send-button" id="sendButton">
                    Send
                </button>
            </form>
        </div>
    </div>

    <script>
        class TILORESOpenWebUI {
            constructor() {
                this.apiBaseUrl = window.location.origin;
                this.chatMessages = document.getElementById('chatMessages');
                this.chatInput = document.getElementById('chatInput');
                this.sendButton = document.getElementById('sendButton');
                this.chatForm = document.getElementById('chatForm');
                this.statusIndicator = document.getElementById('statusIndicator');
                this.typingIndicator = document.getElementById('typingIndicator');
                this.modelSelector = document.getElementById('modelSelector');
                this.providerSelector = document.getElementById('providerSelector');

                this.initializeEventListeners();
                this.updateModelOptions();
                this.checkConnection();
            }

            initializeEventListeners() {
                this.chatForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.sendMessage();
                });

                this.chatInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.sendMessage();
                    }
                });

                this.providerSelector.addEventListener('change', () => {
                    this.updateModelOptions();
                });
            }

            updateModelOptions() {
                const provider = this.providerSelector.value;
                const modelSelector = this.modelSelector;

                // Clear existing options
                modelSelector.innerHTML = '';

                // Add provider-specific models
                if (provider === 'openai') {
                    modelSelector.add(new Option('GPT-4', 'gpt-4'));
                    modelSelector.add(new Option('GPT-3.5 Turbo', 'gpt-3.5-turbo'));
                } else if (provider === 'anthropic') {
                    modelSelector.add(new Option('Claude 3 Opus', 'claude-3-opus'));
                    modelSelector.add(new Option('Claude 3 Sonnet', 'claude-3-sonnet'));
                    modelSelector.add(new Option('Claude 3 Haiku', 'claude-3-haiku'));
                } else if (provider === 'google') {
                    modelSelector.add(new Option('Gemini Pro', 'gemini-pro'));
                    modelSelector.add(new Option('Gemini Pro Vision', 'gemini-pro-vision'));
                }
            }

            async checkConnection() {
                try {
                    const response = await fetch(`${this.apiBaseUrl}/health`);
                    if (response.ok) {
                        this.statusIndicator.textContent = '✅ Connected to TILORES X OpenWebUI - Ready to chat!';
                        this.statusIndicator.className = 'status-indicator connected';
                    } else {
                        throw new Error('Health check failed');
                    }
                } catch (error) {
                    this.statusIndicator.textContent = '❌ Connection failed - check your deployment';
                    this.statusIndicator.className = 'status-indicator error';
                }
            }

            async sendMessage() {
                const message = this.chatInput.value.trim();
                if (!message) return;

                const selectedModel = this.modelSelector.value;
                const selectedProvider = this.providerSelector.value;

                // Add user message
                this.addMessage(message, 'user');
                this.chatInput.value = '';

                // Show typing indicator
                this.showTypingIndicator();

                try {
                    // Send to LLM chat endpoint
                    const response = await this.sendToLLM(message, selectedModel, selectedProvider);
                    this.addMessage(response.response, 'assistant', {
                        model: response.model,
                        provider: response.provider,
                        tokens: response.tokens_used,
                        responseTime: response.response_time
                    });
                } catch (error) {
                    // Fallback response
                    const fallbackResponse = `I'm sorry, I encountered an error while processing your request. Error: ${error.message}\n\nThis might be because:\n• The selected model is not yet fully configured\n• API keys need to be set up\n• The model is temporarily unavailable\n\nTry selecting a different model or provider.`;
                    this.addMessage(fallbackResponse, 'assistant', {
                        model: selectedModel,
                        provider: selectedProvider,
                        error: true
                    });
                }

                this.hideTypingIndicator();
            }

            async sendToLLM(message, model, provider) {
                try {
                    const response = await fetch(`${this.apiBaseUrl}/v1/chat`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            message: message,
                            model: model,
                            provider: provider,
                            temperature: 0.7,
                            max_tokens: 1000
                        })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    return await response.json();
                } catch (error) {
                    throw new Error(`Chat request failed: ${error.message}`);
                }
            }

            addMessage(content, sender, meta = {}) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}`;

                const avatar = document.createElement('div');
                avatar.className = 'message-avatar';
                avatar.textContent = sender === 'user' ? '👤' : '🤖';

                const messageContent = document.createElement('div');
                messageContent.className = 'message-content';
                messageContent.textContent = content;

                // Add metadata for assistant messages
                if (sender === 'assistant' && meta.model) {
                    const metaDiv = document.createElement('div');
                    metaDiv.className = 'message-meta';

                    if (meta.error) {
                        metaDiv.textContent = `⚠️ Error with ${meta.provider}/${meta.model}`;
                    } else {
                        metaDiv.textContent = `🤖 ${meta.provider}/${meta.model} • ${meta.tokens} tokens • ${meta.responseTime.toFixed(2)}s`;
                    }

                    messageContent.appendChild(metaDiv);
                }

                messageDiv.appendChild(avatar);
                messageDiv.appendChild(messageContent);

                this.chatMessages.appendChild(messageDiv);
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }

            showTypingIndicator() {
                this.typingIndicator.classList.add('show');
                this.sendButton.disabled = true;
            }

            hideTypingIndicator() {
                this.typingIndicator.classList.remove('show');
                this.sendButton.disabled = false;
            }
        }

        // Initialize the chat interface when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            new TILORESOpenWebUI();
        });
    </script>
</body>
</html>
"""


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "TILORES X OpenWebUI"}


@app.post("/v1/chat", response_model=ChatResponse)
async def chat_with_llm(request: ChatRequest):
    """Chat with different LLM models"""
    start_time = time.time()

    try:
        # Route to appropriate provider based on model selection
        if request.provider == "openai":
            if request.model in ["gpt-4", "gpt-3.5-turbo"]:
                response = await chat_with_openai(request)
            else:
                raise HTTPException(status_code=400, detail=f"Model {request.model} not supported for OpenAI")

        elif request.provider == "anthropic":
            if request.model in ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]:
                response = await chat_with_anthropic(request)
            else:
                raise HTTPException(status_code=400, detail=f"Model {request.model} not supported for Anthropic")

        elif request.provider == "google":
            if request.model in ["gemini-pro", "gemini-pro-vision"]:
                response = await chat_with_google(request)
            else:
                raise HTTPException(status_code=400, detail=f"Model {request.model} not supported for Google")

        else:
            raise HTTPException(status_code=400, detail=f"Provider {request.provider} not supported")

        response_time = time.time() - start_time

        return ChatResponse(
            response=response,
            model=request.model,
            provider=request.provider,
            tokens_used=len(response.split()),  # Approximate
            response_time=response_time,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


async def chat_with_openai(request: ChatRequest) -> str:
    """Chat with OpenAI models"""
    if not OPENAI_API_KEY:
        return "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."

    try:
        import requests

        # Make actual OpenAI API call
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}

        payload = {
            "model": request.model,
            "messages": [{"role": "user", "content": request.message}],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"OpenAI API error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"OpenAI API call failed: {str(e)}"


async def chat_with_anthropic(request: ChatRequest) -> str:
    """Chat with Anthropic models"""
    if not ANTHROPIC_API_KEY:
        return "Anthropic API key not configured. Please set ANTHROPIC_API_KEY environment variable."

    try:
        import requests

        # Make actual Anthropic API call
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        payload = {
            "model": request.model,
            "max_tokens": request.max_tokens,
            "messages": [{"role": "user", "content": request.message}],
        }

        response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            return data["content"][0]["text"]
        else:
            return f"Anthropic API error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Anthropic API call failed: {str(e)}"


async def chat_with_google(request: ChatRequest) -> str:
    """Chat with Google models"""
    if not GOOGLE_API_KEY:
        return "Google API key not configured. Please set GOOGLE_API_KEY environment variable."

    try:
        import requests

        # Make actual Google Gemini API call
        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": [{"parts": [{"text": request.message}]}],
            "generationConfig": {"temperature": request.temperature, "maxOutputTokens": request.max_tokens},
        }

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{request.model}:generateContent?key={GOOGLE_API_KEY}",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Google API error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Google API call failed: {str(e)}"


@app.get("/v1/models/available")
async def get_available_models():
    """Get list of available models and providers"""
    return AVAILABLE_MODELS


if __name__ == "__main__":
    print("🚀 Starting TILORES X OpenWebUI")
    print("📱 Chat Interface: http://0.0.0.0:8080")
    print("🔧 API Endpoints: http://0.0.0.0:8080/docs")
    print("\n💡 Features:")
    print("   • Real LLM chat interface")
    print("   • Model selection (OpenAI, Anthropic, Google)")
    print("   • Provider switching")
    print("   • Professional UI comparable to ChatGPT")
    print("\n✅ Note: This version now uses REAL API calls to OpenAI, Anthropic, and Google!")
    print("   Set your API keys as environment variables to enable full functionality.")

    # Use Railway's PORT environment variable or default to 8080
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
