#!/usr/bin/env python3
"""
Direct Credit Analysis API - LangChain-Free Implementation
Replaces LangChain tool calling with direct OpenAI API calls and GraphQL queries
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

import openai
import requests
from fastapi import FastAPI, HTTPException
# from fastapi.responses import JSONResponse  # Not currently used
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Tilores API configuration
TILORES_API_URL = os.getenv("TILORES_GRAPHQL_API_URL")
TILORES_CLIENT_ID = os.getenv("TILORES_CLIENT_ID")
TILORES_CLIENT_SECRET = os.getenv("TILORES_CLIENT_SECRET")
TILORES_TOKEN_URL = os.getenv("TILORES_OAUTH_TOKEN_URL")

# Known entity ID for Esteban Price (from our previous testing)
KNOWN_ENTITY_ID = "dc93a2cd-de0a-444f-ad47-3003ba998cd3"

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "gpt - 4o-mini"
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False

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

# Create FastAPI app
app = FastAPI(
    title="Direct Credit Analysis API",
    description="LangChain-free credit analysis with direct OpenAI and Tilores integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/v1 / chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Direct credit analysis endpoint"""
    try:
        # Extract the user's query
        user_message = None
        for message in request.messages:
            if message.role == "user":
                user_message = message.content
                break

        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")

        # Analyze the credit query
        analysis = await credit_api.analyze_credit_query(user_message)

        # Return OpenAI-compatible response
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:20]}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": analysis
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_message.split()) * 2,  # Rough estimate
                "completion_tokens": len(analysis.split()),
                "total_tokens": len(user_message.split()) * 2 + len(analysis.split())
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "direct-credit-api", "version": "1.0.0"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
