#!/usr/bin/env python3
"""
Multi-Provider Direct Credit Analysis API - LangChain-Free Implementation
Supports OpenAI, Anthropic, Google Gemini, and other providers
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

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
    stream: bool = False

class MultiProviderCreditAPI:
    def __init__(self):
        self.tilores_token = None
        self.token_expires_at = None

        # Tilores API configuration
        self.tilores_api_url = os.getenv("TILORES_GRAPHQL_API_URL")
        self.tilores_client_id = os.getenv("TILORES_CLIENT_ID")
        self.tilores_client_secret = os.getenv("TILORES_CLIENT_SECRET")
        self.tilores_token_url = os.getenv("TILORES_OAUTH_TOKEN_URL")

        # Provider configurations
        self.providers = {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
            },
            # "anthropic": {
            #     "api_key": os.getenv("ANTHROPIC_API_KEY"),
            #     "base_url": "https://api.anthropic.com/v1",
            #     "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307", "claude-3-opus-20240229"]
            # },
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

    def _fetch_credit_data(self):
        """Fetch credit data from Tilores API using proven working logic"""
        try:
            token = self.get_tilores_token()

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

            response = requests.post(
                self.tilores_api_url,
                json={"query": query, "variables": {"id": KNOWN_ENTITY_ID}},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            if "errors" in result:
                raise Exception(f"GraphQL errors: {result['errors']}")

            return result.get("data", {}).get("entity", {}).get("entity", {}).get("records", [])

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch credit data: {str(e)}")

    def extract_temporal_credit_data(self, records):
        """Extract and categorize temporal credit data using proven working logic"""
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

    def _analyze_credit_data(self, records):
        """Analyze credit data using proven working logic"""
        if not records:
            return "No credit data available."

        # Extract temporal data using proven logic
        temporal_data = self.extract_temporal_credit_data(records)

        # Create comprehensive analysis
        analysis = []
        analysis.append("## Credit Analysis Summary\n")

        # Add bureau-specific analysis
        for bureau, bureau_data in temporal_data.items():
            analysis.append(f"### {bureau} Credit Data:")

            for date, date_data in bureau_data.items():
                analysis.append(f"\n**Date: {date}**")

                # Add scores
                scores = date_data.get('scores', [])
                if scores:
                    analysis.append("Credit Scores:")
                    for score in scores:
                        analysis.append(f"- {score['value']} ({score['model']})")

                # Add key metrics
                if date_data.get('utilization') is not None:
                    analysis.append(f"Utilization: {date_data['utilization']}%")
                if date_data.get('inquiries') is not None:
                    analysis.append(f"Inquiries: {date_data['inquiries']}")
                if date_data.get('accounts') is not None:
                    analysis.append(f"Accounts: {date_data['accounts']}")
                if date_data.get('payments') is not None:
                    analysis.append(f"Payments: {date_data['payments']}")
                if date_data.get('delinquencies') is not None:
                    analysis.append(f"Delinquencies: {date_data['delinquencies']}")

        return "\n".join(analysis)

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
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

    # def _call_anthropic(self, messages, model, temperature=0.7, max_tokens=None):
    #     """Call Anthropic API - DEPRECATED"""
    #     try:
    #         import anthropic
    #         client = anthropic.Anthropic(api_key=self.providers["anthropic"]["api_key"])
    #
    #         # Convert messages to Anthropic format
    #         anthropic_messages = []
    #         for msg in messages:
    #             if msg.role == "user":
    #                 anthropic_messages.append({"role": "user", "content": msg.content})
    #             elif msg.role == "assistant":
    #                 anthropic_messages.append({"role": "assistant", "content": msg.content})
    #
    #         response = client.messages.create(
    #             model=model,
    #             max_tokens=max_tokens or 1000,
    #             messages=anthropic_messages,
    #             temperature=temperature
    #         )
    #
    #         return response.content[0].text
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=f"Anthropic API error: {str(e)}")

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
            raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")

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
            raise HTTPException(status_code=500, detail=f"Google API error: {str(e)}")

    def process_chat_request(self, messages: List[ChatMessage], model: str, temperature: float = 0.7, max_tokens: Optional[int] = None):
        """Process chat request with credit data analysis using proven working logic"""
        try:
            # Fetch credit data using proven working logic
            records = self._fetch_credit_data()

            if not records:
                return "No credit data found for the requested customer."

            # Extract temporal data using proven working logic
            temporal_data = self.extract_temporal_credit_data(records)

            # Prepare context for AI analysis (same as working direct API)
            context = {
                "temporal_credit_data": temporal_data,
                "query": messages[-1].content if messages else "",
                "analysis_timestamp": datetime.now().isoformat()
            }

            # Create system prompt for credit analysis (same as working direct API)
            system_prompt = """You are a Credit Pros advisor with access to comprehensive credit data.
            Analyze the provided temporal credit data to answer the user's question accurately and professionally.

            Available data includes:
            - Credit scores across multiple bureaus (Equifax, Experian, TransUnion) over time
            - Summary parameters including utilization rates, inquiry counts, account counts, payment amounts, and delinquencies
            - Temporal progression showing changes over time

            Provide detailed, accurate analysis based on the actual data provided."""

            # Prepare messages for AI
            ai_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {messages[-1].content if messages else ''}\n\nCredit Data: {json.dumps(context, indent=2)}"}
            ]

            # Determine provider and call appropriate API
            if model.startswith("gpt-") or model in self.providers["openai"]["models"]:
                return self._call_openai_with_context(ai_messages, model, temperature, max_tokens)
            elif model.startswith("gemini-") or model in self.providers["google"]["models"]:
                return self._call_google_with_context(ai_messages, model, temperature, max_tokens)
            elif model in self.providers["groq"]["models"]:
                return self._call_groq_with_context(ai_messages, model, temperature, max_tokens)
            else:
                # Default to OpenAI
                return self._call_openai_with_context(ai_messages, "gpt-4o-mini", temperature, max_tokens)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# Initialize the API
api = MultiProviderCreditAPI()

# Create FastAPI app
app = FastAPI(title="Multi-Provider Credit Analysis API", version="1.0.0")

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
    return {"status": "ok", "service": "multi-provider-credit-api", "version": "1.0.0"}

@app.get("/v1/models")
async def get_models():
    """Get available models from all providers"""
    models = []

    # OpenAI models
    for model in api.providers["openai"]["models"]:
        models.append({
            "id": model,
            "object": "model",
            "created": 1677610602,
            "owned_by": "openai"
        })

    # Groq models
    for model in api.providers["groq"]["models"]:
        models.append({
            "id": model,
            "object": "model",
            "created": 1677610602,
            "owned_by": "groq"
        })

    # Google models
    for model in api.providers["google"]["models"]:
        models.append({
            "id": model,
            "object": "model",
            "created": 1677610602,
            "owned_by": "google"
        })

    return {"object": "list", "data": models}

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Chat completions endpoint supporting multiple providers"""
    try:
        # Process the request
        response_content = api.process_chat_request(
            request.messages,
            request.model,
            request.temperature,
            request.max_tokens
        )

        # Create OpenAI-compatible response
        response = {
            "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": request.model,
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
                "prompt_tokens": 0,  # Would need to implement token counting
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
