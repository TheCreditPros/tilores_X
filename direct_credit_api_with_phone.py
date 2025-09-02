#!/usr/bin/env python3
"""
Multi-Provider Direct Credit Analysis API - LangChain-Free Implementation
Supports OpenAI, Anthropic, Google Gemini, and other providers
"""

import json
import os
import uuid
import hashlib
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import requests
import redis
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
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
    stream: Optional[bool] = False
    # Additional OpenAI-compatible fields that Agenta.ai might send
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    top_p: Optional[float] = None
    n: Optional[int] = None
    user: Optional[str] = None

    class Config:
        # Allow extra fields that we don't explicitly define
        extra = "allow"

class MultiProviderCreditAPI:
    def __init__(self):
        self.tilores_token = None
        self.token_expires_at = None

        # Performance optimization - simple in-memory cache for recent queries
        self.query_cache = {}
        self.cache_ttl = 300  # 5 minutes cache for repeated queries

        # Performance tracking
        self.active_requests = 0

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

    def _parse_query_for_customer(self, query: str) -> dict:
        """Parse query to extract customer search parameters"""
        import re

        # Skip ONLY truly general questions that don't reference specific customers
        # IMPORTANT: Don't block customer status queries that contain identifiers
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

        # Email extraction (most reliable identifier)
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', query)
        if email_match:
            return {"EMAIL": email_match.group()}

        # Phone extraction (basic pattern)
        phone_match = re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', query)
        if phone_match:
            return {"PHONE_NUMBER": phone_match.group()}

        # Client ID extraction (numeric only, 4-15 digits, but avoid years/dates)
        client_id_match = re.search(r'\b\d{4,15}\b', query)
        if client_id_match:
            # Avoid matching years (1900-2100) or common numbers
            number = client_id_match.group()
            if not (1900 <= int(number) <= 2100 and len(number) == 4):
                return {"CLIENT_ID": number}

        # Salesforce ID pattern (more specific)
        salesforce_match = re.search(r'\b003[A-Za-z0-9]{15}\b', query)
        if salesforce_match:
            return {"SALESFORCE_ID": salesforce_match.group()}

        return {}

    def _search_for_customer(self, search_params: dict) -> str:
        """Search for customer and return entity ID"""
        try:
            token = self.get_tilores_token()

            # Build search query
            params_str = ', '.join([f'{k}: "{v}"' for k, v in search_params.items()])
            query = f"""
            query {{
                search(input: {{ parameters: {{ {params_str} }} }}) {{
                    entities {{
                        id
                        records {{ id }}
                    }}
                }}
            }}
            """

            response = requests.post(
                self.tilores_api_url,
                json={"query": query},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            if "errors" in result:
                return None

            entities = result.get("data", {}).get("search", {}).get("entities", [])
            if entities and entities[0].get("records"):
                return entities[0].get("id")

            return None
        except Exception as e:
            print(f"Error searching for customer: {e}")
            return None

    

    async def _fetch_credit_data_async(self, entity_id: str) -> Optional[List[Dict]]:
        """Async version of credit data fetch for parallel processing with caching"""
        # Check cache first
        cached_data = self._get_cached_tilores_data(entity_id, "credit")
        if cached_data:
            return cached_data.get("records")

        # Fetch from API
        result = await asyncio.to_thread(self._fetch_credit_data, entity_id)

        # Cache the result
        if result:
            self._cache_tilores_data(entity_id, "credit", {"records": result})

        return result

    def _fetch_credit_data(self, entity_id=None):
        """Fetch credit data from Tilores API using proven working logic"""
        if not entity_id:
            entity_id = KNOWN_ENTITY_ID
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
                json={"query": query, "variables": {"id": entity_id}},
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

    async def get_phone_call_data(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get phone call data for a specific entity using the correct filtering approach"""
        query = """
        query PhoneCallDataByEntity($id: ID!) {
          entity(input: { id: $id }) {
            entity {
              id
              recordInsights {
                emails: valuesDistinct(field: "EMAIL")
                agents: valuesDistinct(field: "AGENT_USERNAME")
                call_ids: valuesDistinct(field: "CALL_ID")
              }
              records {
                id
                CALL_ID
                AGENT_USERNAME
                CALL_DURATION
                CALL_START_TIME
                CALL_HANGUP_TIME
                CALL_TYPE
                CAMPAIGN_NAME
                PHONE_NUMBER
              }
            }
          }
        }
        """

        try:
            token = self.get_tilores_token()
            response = requests.post(
                self.tilores_api_url,
                json={"query": query, "variables": {"id": entity_id}},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            if "errors" in result:
                return None

            entity = result.get("data", {}).get("entity", {}).get("entity")
            if not entity:
                return None

            records = entity.get("records", [])

            # Filter for records with call data (CALL_ID not null)
            call_records = [r for r in records if r.get("CALL_ID") is not None]

            if not call_records:
                return None

            # Extract call facts server-side
            call_facts = self._extract_call_facts_server_side(call_records)

            # Aggregate call data using golden pattern
            call_aggregation = self._aggregate_calls_golden_pattern(call_records, call_facts)

            return {
                "entity_id": entity_id,
                "call_records_count": len(call_records),
                "call_facts": call_facts,
                "call_aggregation": call_aggregation,
                "record_insights": entity.get("recordInsights", {})
            }

        except Exception as e:
            print(f"Error fetching phone call data: {e}")
            return None

    def _extract_call_facts_server_side(self, records: list) -> dict:
        """Extract call facts server-side (mirrors credit golden pattern)"""
        try:
            phones = set()
            agents = {}
            types = {}
            campaigns = {}
            latest_call = None
            latest_time = None

            for r in records:
                p = r.get("PHONE_NUMBER")
                a = r.get("AGENT_USERNAME")
                t = r.get("CALL_TYPE")
                c = r.get("CAMPAIGN_NAME")
                s = r.get("CALL_START_TIME")

                if p:
                    phones.add(p)
                if a:
                    agents[a] = agents.get(a, 0) + 1
                if t:
                    types[t] = types.get(t, 0) + 1
                if c:
                    campaigns[c] = campaigns.get(c, 0) + 1
                if s and (not latest_time or s > latest_time):
                    latest_time = s
                    latest_call = {
                        "CALL_START_TIME": s,
                        "CALL_ID": r.get("CALL_ID"),
                        "CALL_TYPE": t,
                        "AGENT_USERNAME": a,
                        "CAMPAIGN_NAME": c,
                    }

            return {
                "phones": sorted(phones),
                "topAgents": sorted(agents.items(), key=lambda x: (-x[1], x[0])),
                "callTypes": sorted(types.items(), key=lambda x: (-x[1], x[0])),
                "campaigns": sorted(campaigns.items(), key=lambda x: (-x[1], x[0])),
                "latest": latest_call or {},
            }
        except Exception as e:
            print(f"⚠️ Call facts extraction error: {e}")
            return {}

    def _aggregate_calls_golden_pattern(self, records: list, call_facts: dict) -> dict:
        """Aggregate call data using golden pattern (mirrors credit aggregation)"""
        try:
            from collections import defaultdict

            total_calls = 0
            total_secs = 0.0
            per_day = defaultdict(int)
            per_agent = defaultdict(int)
            per_type = defaultdict(int)
            per_campaign = defaultdict(int)
            timeline = []

            def _to_secs(v):
                if v is None or v == "":
                    return 0.0
                s = str(v)
                if ":" in s:
                    parts = [float(x) for x in s.split(":")]
                    if len(parts) == 3:
                        h, m, sec = parts
                    elif len(parts) == 2:
                        h, m, sec = 0, parts[0], parts[1]
                    else:
                        return 0.0
                    return h * 3600 + m * 60 + sec
                try:
                    return float(s)
                except (ValueError, TypeError):
                    return 0.0

            def _date_only(dt):
                if not dt:
                    return "unknown"
                return dt.split("T")[0]

            for r in records:
                start = r.get("CALL_START_TIME")
                dsecs = _to_secs(r.get("CALL_DURATION"))
                agent = r.get("AGENT_USERNAME") or "Unknown"
                ctype = r.get("CALL_TYPE") or "Unknown"
                camp = r.get("CAMPAIGN_NAME") or "Unknown"

                total_calls += 1
                total_secs += dsecs
                per_day[_date_only(start)] += 1
                per_agent[agent] += 1
                per_type[ctype] += 1
                per_campaign[camp] += 1

                timeline.append({
                    "date": start,
                    "duration_secs": dsecs,
                    "type": ctype,
                    "agent": agent,
                    "campaign": camp,
                })

            timeline.sort(key=lambda x: x["date"] or "1900-01-01")
            avg_secs = (total_secs / total_calls) if total_calls else 0.0

            return {
                "totals": {
                    "calls": total_calls,
                    "duration_secs": round(total_secs, 2),
                    "avg_duration_secs": round(avg_secs, 2),
                },
                "by_day": dict(sorted(per_day.items())),
                "by_agent": dict(sorted(per_agent.items(), key=lambda x: (-x[1], x[0]))),
                "by_type": dict(sorted(per_type.items(), key=lambda x: (-x[1], x[0]))),
                "by_campaign": dict(sorted(per_campaign.items(), key=lambda x: (-x[1], x[0]))),
                "timeline": timeline,
                "golden_pattern_optimized": True,
                "call_facts": call_facts,
            }
        except Exception as e:
            print(f"⚠️ Call aggregation error: {e}")
            return {}

    async def get_transaction_data(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction data for a specific entity using the golden pattern"""
        query = """
        query TransactionDataByEntity($id: ID!) {
          entity(input: { id: $id }) {
            entity {
              id
              recordInsights {
                transaction_amounts: valuesDistinct(field: "TRANSACTION_AMOUNT")
                payment_methods: valuesDistinct(field: "PAYMENT_METHOD")
                transaction_types: valuesDistinct(field: "TYPE")
              }
              records {
                id
                TRANSACTION_AMOUNT
                CARD_EXPIRED
                CARD_FIRST_6_DIGIT
                CARD_LAST_4
                CHARGEBACK
                CHARGEBACK_CREDITED
                CONTACT_NEW
                TRANSACTION_CREATED_DATE
                CURRENT_PRODUCT
                DISCOUNT_AMOUNT
                EMAIL_CONFIRMATION_DATE
                ENROLLMENT_FEE
                GATEWAY_DATE
                GATEWAY_RESPONSE
                IS_FULLY_REFUNDED
                PAYMENT_METHOD
                RE_ENROLLMENT
                RECURRING
                REFUND_CONFIRMATION_SENT
                RESPONSE_MESSAGE
                RESPONSE_STATUS
                SECOND_FEE_TRANSACTION
                TYPE
              }
            }
          }
        }
        """

        try:
            token = self.get_tilores_token()
            response = requests.post(
                self.tilores_api_url,
                json={"query": query, "variables": {"id": entity_id}},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            if "errors" in result:
                return None

            entity = result.get("data", {}).get("entity", {}).get("entity")
            if not entity:
                return None

            records = entity.get("records", [])

            # Filter for records with transaction data (TRANSACTION_AMOUNT not null)
            transaction_records = [r for r in records if r.get("TRANSACTION_AMOUNT") is not None]

            if not transaction_records:
                return None

            # Extract transaction facts server-side
            transaction_facts = self._extract_transaction_facts_server_side(transaction_records)

            # Aggregate transaction data using golden pattern
            transaction_aggregation = self._aggregate_transactions_golden_pattern(transaction_records, transaction_facts)

            return {
                "entity_id": entity_id,
                "transaction_records_count": len(transaction_records),
                "transaction_facts": transaction_facts,
                "transaction_aggregation": transaction_aggregation,
                "record_insights": entity.get("recordInsights", {})
            }

        except Exception as e:
            print(f"Error fetching transaction data: {e}")
            return None

    def _extract_transaction_facts_server_side(self, records: list) -> dict:
        """Extract transaction facts server-side (mirrors credit golden pattern)"""
        try:
            amounts = []
            payment_methods = {}
            types = {}
            products = {}
            latest_transaction = None
            latest_date = None
            total_amount = 0.0

            for r in records:
                amount = r.get("TRANSACTION_AMOUNT")
                method = r.get("PAYMENT_METHOD")
                ttype = r.get("TYPE")
                product = r.get("CURRENT_PRODUCT")
                date = r.get("TRANSACTION_CREATED_DATE")

                if amount:
                    try:
                        amount_float = float(str(amount).replace('$', '').replace(',', ''))
                        amounts.append(amount_float)
                        total_amount += amount_float
                    except (ValueError, TypeError):
                        pass

                if method:
                    payment_methods[method] = payment_methods.get(method, 0) + 1
                if ttype:
                    types[ttype] = types.get(ttype, 0) + 1
                if product:
                    products[product] = products.get(product, 0) + 1
                if date and (not latest_date or date > latest_date):
                    latest_date = date
                    latest_transaction = {
                        "TRANSACTION_CREATED_DATE": date,
                        "TRANSACTION_AMOUNT": amount,
                        "PAYMENT_METHOD": method,
                        "TYPE": ttype,
                        "CURRENT_PRODUCT": product,
                    }

            return {
                "total_amount": round(total_amount, 2),
                "transaction_count": len(amounts),
                "average_amount": round(total_amount / len(amounts), 2) if amounts else 0,
                "payment_methods": sorted(payment_methods.items(), key=lambda x: (-x[1], x[0])),
                "transaction_types": sorted(types.items(), key=lambda x: (-x[1], x[0])),
                "products": sorted(products.items(), key=lambda x: (-x[1], x[0])),
                "latest": latest_transaction or {},
            }
        except Exception as e:
            print(f"⚠️ Transaction facts extraction error: {e}")
            return {}

    def _aggregate_transactions_golden_pattern(self, records: list, transaction_facts: dict) -> dict:
        """Aggregate transaction data using golden pattern"""
        try:
            from collections import defaultdict

            per_day = defaultdict(float)
            per_month = defaultdict(float)
            per_method = defaultdict(float)
            per_type = defaultdict(float)
            timeline = []

            def _date_only(dt):
                if not dt:
                    return "unknown"
                return dt.split("T")[0]

            def _month_only(dt):
                if not dt:
                    return "unknown"
                return dt.split("T")[0][:7]  # YYYY-MM

            for r in records:
                date = r.get("TRANSACTION_CREATED_DATE")
                amount = r.get("TRANSACTION_AMOUNT")
                method = r.get("PAYMENT_METHOD") or "Unknown"
                ttype = r.get("TYPE") or "Unknown"

                try:
                    amount_float = float(str(amount).replace('$', '').replace(',', '')) if amount else 0.0
                except (ValueError, TypeError):
                    amount_float = 0.0

                per_day[_date_only(date)] += amount_float
                per_month[_month_only(date)] += amount_float
                per_method[method] += amount_float
                per_type[ttype] += amount_float

                timeline.append({
                    "date": date,
                    "amount": amount_float,
                    "method": method,
                    "type": ttype,
                })

            timeline.sort(key=lambda x: x["date"] or "1900-01-01")

            return {
                "by_day": dict(sorted(per_day.items())),
                "by_month": dict(sorted(per_month.items())),
                "by_method": dict(sorted(per_method.items(), key=lambda x: (-x[1], x[0]))),
                "by_type": dict(sorted(per_type.items(), key=lambda x: (-x[1], x[0]))),
                "timeline": timeline,
                "golden_pattern_optimized": True,
                "transaction_facts": transaction_facts,
            }
        except Exception as e:
            print(f"⚠️ Transaction aggregation error: {e}")
            return {}

    async def get_credit_card_data(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get credit card data for a specific entity using the golden pattern"""
        query = """
        query CreditCardDataByEntity($id: ID!) {
          entity(input: { id: $id }) {
            entity {
              id
              recordInsights {
                card_numbers: valuesDistinct(field: "CARD_NUMBER")
                card_types: valuesDistinct(field: "CARD_TYPE")
                bins: valuesDistinct(field: "BIN")
              }
              records {
                id
                ACTIVE
                BIN
                CARD_NUMBER
                CVV
                EXPIRATION_MONTH
                EXPIRATION_YEAR
                INVALID_CARD
                PREPAID
              }
            }
          }
        }
        """

        try:
            token = self.get_tilores_token()
            response = requests.post(
                self.tilores_api_url,
                json={"query": query, "variables": {"id": entity_id}},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            if "errors" in result:
                return None

            entity = result.get("data", {}).get("entity", {}).get("entity")
            if not entity:
                return None

            records = entity.get("records", [])

            # Filter for records with card data (CARD_NUMBER not null)
            card_records = [r for r in records if r.get("CARD_NUMBER") is not None]

            if not card_records:
                return None

            # Extract card facts server-side
            card_facts = self._extract_card_facts_server_side(card_records)

            # Aggregate card data using golden pattern
            card_aggregation = self._aggregate_cards_golden_pattern(card_records, card_facts)

            return {
                "entity_id": entity_id,
                "card_records_count": len(card_records),
                "card_facts": card_facts,
                "card_aggregation": card_aggregation,
                "record_insights": entity.get("recordInsights", {})
            }

        except Exception as e:
            print(f"Error fetching credit card data: {e}")
            return None

    def _extract_card_facts_server_side(self, records: list) -> dict:
        """Extract credit card facts server-side (mirrors credit golden pattern)"""
        try:
            card_numbers = set()
            bins = set()
            active_cards = 0
            expired_cards = 0
            prepaid_cards = 0
            invalid_cards = 0

            for r in records:
                card_num = r.get("CARD_NUMBER")
                bin_num = r.get("BIN")
                active = r.get("ACTIVE")
                exp_month = r.get("EXPIRATION_MONTH")
                exp_year = r.get("EXPIRATION_YEAR")
                prepaid = r.get("PREPAID")
                invalid = r.get("INVALID_CARD")

                if card_num:
                    # Mask card number for security
                    masked = f"****-****-****-{str(card_num)[-4:]}" if len(str(card_num)) >= 4 else "****"
                    card_numbers.add(masked)
                if bin_num:
                    bins.add(bin_num)
                if active:
                    active_cards += 1
                if prepaid:
                    prepaid_cards += 1
                if invalid:
                    invalid_cards += 1

                # Check if card is expired
                if exp_month and exp_year:
                    try:
                        from datetime import datetime
                        current_date = datetime.now()
                        exp_date = datetime(int(exp_year), int(exp_month), 1)
                        if exp_date < current_date:
                            expired_cards += 1
                    except (ValueError, TypeError):
                        pass

            return {
                "card_numbers": sorted(card_numbers),
                "bins": sorted(bins),
                "total_cards": len(records),
                "active_cards": active_cards,
                "expired_cards": expired_cards,
                "prepaid_cards": prepaid_cards,
                "invalid_cards": invalid_cards,
            }
        except Exception as e:
            print(f"⚠️ Card facts extraction error: {e}")
            return {}

    def _aggregate_cards_golden_pattern(self, records: list, card_facts: dict) -> dict:
        """Aggregate credit card data using golden pattern"""
        try:
            from collections import defaultdict

            per_bin = defaultdict(int)
            per_status = defaultdict(int)
            timeline = []

            for r in records:
                bin_num = r.get("BIN") or "Unknown"
                active = r.get("ACTIVE")
                exp_month = r.get("EXPIRATION_MONTH")
                exp_year = r.get("EXPIRATION_YEAR")

                per_bin[bin_num] += 1

                status = "Unknown"
                if active:
                    status = "Active"
                elif exp_month and exp_year:
                    try:
                        from datetime import datetime
                        current_date = datetime.now()
                        exp_date = datetime(int(exp_year), int(exp_month), 1)
                        status = "Expired" if exp_date < current_date else "Valid"
                    except (ValueError, TypeError):
                        pass

                per_status[status] += 1

                timeline.append({
                    "bin": bin_num,
                    "status": status,
                    "expiration": f"{exp_month}/{exp_year}" if exp_month and exp_year else "Unknown",
                })

            return {
                "by_bin": dict(sorted(per_bin.items(), key=lambda x: (-x[1], x[0]))),
                "by_status": dict(sorted(per_status.items(), key=lambda x: (-x[1], x[0]))),
                "timeline": timeline,
                "golden_pattern_optimized": True,
                "card_facts": card_facts,
            }
        except Exception as e:
            print(f"⚠️ Card aggregation error: {e}")
            return {}

    async def get_zoho_ticket_data(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get Zoho ticket data for a specific entity using the golden pattern"""
        query = """
        query ZohoTicketDataByEntity($id: ID!) {
          entity(input: { id: $id }) {
            entity {
              id
              recordInsights {
                zoho_ids: valuesDistinct(field: "ZOHO_ID")
                ticket_numbers: valuesDistinct(field: "TICKETNUMBER")
                statuses: valuesDistinct(field: "ZOHO_STATUS")
                categories: valuesDistinct(field: "CATEGORY")
              }
              records {
                id
                ZOHO_ID
                ZOHO_EMAIL
                TICKETNUMBER
                ZOHO_PHONE
                SUBJECT
                ZOHO_STATUS
                STATUSTYPE
                CREATEDTIME
                CATEGORY
                LANGUAGE
                SUBCATEGORY
                PRIORITY
                DUEDATE
                RESPONSEDUEDATE
                COMMENTCOUNT
                SENTIMENT
                THREADCOUNT
                SOURCE_TYPE
                CLOSEDTIME
              }
            }
          }
        }
        """

        try:
            token = self.get_tilores_token()
            response = requests.post(
                self.tilores_api_url,
                json={"query": query, "variables": {"id": entity_id}},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            if "errors" in result:
                return None

            entity = result.get("data", {}).get("entity", {}).get("entity")
            if not entity:
                return None

            records = entity.get("records", [])

            # Filter for records with Zoho data (ZOHO_ID not null)
            ticket_records = [r for r in records if r.get("ZOHO_ID") is not None]

            if not ticket_records:
                return None

            # Extract ticket facts server-side
            ticket_facts = self._extract_ticket_facts_server_side(ticket_records)

            # Aggregate ticket data using golden pattern
            ticket_aggregation = self._aggregate_tickets_golden_pattern(ticket_records, ticket_facts)

            return {
                "entity_id": entity_id,
                "ticket_records_count": len(ticket_records),
                "ticket_facts": ticket_facts,
                "ticket_aggregation": ticket_aggregation,
                "record_insights": entity.get("recordInsights", {})
            }

        except Exception as e:
            print(f"Error fetching Zoho ticket data: {e}")
            return None

    def _extract_ticket_facts_server_side(self, records: list) -> dict:
        """Extract Zoho ticket facts server-side (mirrors credit golden pattern)"""
        try:
            categories = {}
            statuses = {}
            priorities = {}
            sentiments = {}
            latest_ticket = None
            latest_date = None

            for r in records:
                category = r.get("CATEGORY")
                status = r.get("ZOHO_STATUS")
                priority = r.get("PRIORITY")
                sentiment = r.get("SENTIMENT")
                created = r.get("CREATEDTIME")

                if category:
                    categories[category] = categories.get(category, 0) + 1
                if status:
                    statuses[status] = statuses.get(status, 0) + 1
                if priority:
                    priorities[priority] = priorities.get(priority, 0) + 1
                if sentiment:
                    sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
                if created and (not latest_date or created > latest_date):
                    latest_date = created
                    latest_ticket = {
                        "CREATEDTIME": created,
                        "ZOHO_ID": r.get("ZOHO_ID"),
                        "TICKETNUMBER": r.get("TICKETNUMBER"),
                        "SUBJECT": r.get("SUBJECT"),
                        "ZOHO_STATUS": status,
                        "CATEGORY": category,
                        "PRIORITY": priority,
                    }

            return {
                "total_tickets": len(records),
                "categories": sorted(categories.items(), key=lambda x: (-x[1], x[0])),
                "statuses": sorted(statuses.items(), key=lambda x: (-x[1], x[0])),
                "priorities": sorted(priorities.items(), key=lambda x: (-x[1], x[0])),
                "sentiments": sorted(sentiments.items(), key=lambda x: (-x[1], x[0])),
                "latest": latest_ticket or {},
            }
        except Exception as e:
            print(f"⚠️ Ticket facts extraction error: {e}")
            return {}

    def _aggregate_tickets_golden_pattern(self, records: list, ticket_facts: dict) -> dict:
        """Aggregate Zoho ticket data using golden pattern"""
        try:
            from collections import defaultdict

            per_day = defaultdict(int)
            per_month = defaultdict(int)
            per_category = defaultdict(int)
            per_status = defaultdict(int)
            timeline = []

            def _date_only(dt):
                if not dt:
                    return "unknown"
                return dt.split("T")[0]

            def _month_only(dt):
                if not dt:
                    return "unknown"
                return dt.split("T")[0][:7]  # YYYY-MM

            for r in records:
                created = r.get("CREATEDTIME")
                category = r.get("CATEGORY") or "Unknown"
                status = r.get("ZOHO_STATUS") or "Unknown"
                subject = r.get("SUBJECT") or "No Subject"

                per_day[_date_only(created)] += 1
                per_month[_month_only(created)] += 1
                per_category[category] += 1
                per_status[status] += 1

                timeline.append({
                    "date": created,
                    "category": category,
                    "status": status,
                    "subject": subject[:50] + "..." if len(subject) > 50 else subject,
                })

            timeline.sort(key=lambda x: x["date"] or "1900-01-01")

            return {
                "by_day": dict(sorted(per_day.items())),
                "by_month": dict(sorted(per_month.items())),
                "by_category": dict(sorted(per_category.items(), key=lambda x: (-x[1], x[0]))),
                "by_status": dict(sorted(per_status.items(), key=lambda x: (-x[1], x[0]))),
                "timeline": timeline,
                "golden_pattern_optimized": True,
                "ticket_facts": ticket_facts,
            }
        except Exception as e:
            print(f"⚠️ Ticket aggregation error: {e}")
            return {}

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

    def _get_cache_key(self, query: str, search_params: dict) -> str:
        """Generate cache key for query"""
        cache_data = f"{query}:{json.dumps(search_params, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()

    def _check_cache(self, cache_key: str) -> Optional[str]:
        """Check if response is cached"""
        if cache_key in self.query_cache:
            cached_data = self.query_cache[cache_key]
            if datetime.now().timestamp() - cached_data['timestamp'] < self.cache_ttl:
                print(f"🚀 Cache hit for query: {cache_key[:8]}...")
                return cached_data['response']
            else:
                # Remove expired cache
                del self.query_cache[cache_key]
        return None

    def _cache_response(self, cache_key: str, response: str):
        """Cache response in both memory and Redis"""
        # Memory cache
        self.query_cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now().timestamp()
        }

        # Redis cache for Tilores data
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

    def _cache_tilores_data(self, entity_id: str, data_type: str, data: dict):
        """Cache Tilores API responses"""
        if self.redis_client:
            try:
                cache_key = f"tilores:{data_type}:{entity_id}"
                self.redis_client.setex(cache_key, 1800, json.dumps(data))  # 30 min cache
                print(f"💾 Cached Tilores {data_type} data: {entity_id}")
            except Exception as e:
                print(f"⚠️ Tilores cache failed: {e}")

    def _get_cached_tilores_data(self, entity_id: str, data_type: str) -> Optional[dict]:
        """Get cached Tilores data"""
        if self.redis_client:
            try:
                cache_key = f"tilores:{data_type}:{entity_id}"
                cached = self.redis_client.get(cache_key)
                if cached:
                    print(f"🚀 Tilores cache hit ({data_type}): {entity_id}")
                    return json.loads(cached)
            except Exception as e:
                print(f"⚠️ Tilores cache get failed: {e}")
        return None

    async def _generate_streaming_response(self, response_content: str, request_id: str, model: str):
        """Generate streaming response chunks"""
        import time

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

    async def process_chat_request(self, messages: List[ChatMessage], model: str, temperature: float = 0.7, max_tokens: Optional[int] = None):
        """Process chat request with credit data analysis using proven working logic"""
        self.active_requests += 1
        start_time = datetime.now()
        print(f"🔄 Processing request #{self.active_requests} started at {start_time.strftime('%H:%M:%S')}")

        try:
            # Extract query from messages
            query = messages[-1].content if messages else ""

            # Parse query to find customer identifier
            search_params = self._parse_query_for_customer(query)

            # If no customer found in current query, check previous messages for context
            if not search_params and len(messages) > 1:
                # Look for customer identifier in previous messages
                for msg in reversed(messages[:-1]):
                    if hasattr(msg, 'content') and msg.content:
                        prev_params = self._parse_query_for_customer(msg.content)
                        if prev_params:
                            search_params = prev_params
                            print(f"🔍 DEBUG: Found customer context from previous message: {search_params}")
                            break

            # If still no customer found, handle as general question
            if not search_params:
                # Check if this is a general question about the company/service
                if any(keyword in query.lower() for keyword in ['thecreditpros', 'credit pros', 'company', 'service', 'status', 'help']):
                    return "I'm a customer service assistant for TheCreditPros. I can help you analyze customer credit data, transaction history, call records, and support tickets. To get started, please provide a customer identifier such as an email address, phone number, or client ID."
                else:
                    return "Error: Could not identify customer from query. Please provide email, phone number, client ID, or customer name."

            # Check cache for this query + customer combination
            cache_key = self._get_cache_key(query, search_params)

            # Check memory cache first
            cached_response = self._check_cache(cache_key)
            if cached_response:
                return cached_response

            # Check Redis cache
            redis_cached = self._get_redis_cache(cache_key)
            if redis_cached:
                return redis_cached

            # Search for the specific customer
            entity_id = self._search_for_customer(search_params)

            if not entity_id:
                return f"No records found for the specified customer. Searched with parameters: {search_params}"

            # Determine query type and route accordingly
            query_lower = query.lower()
            # Detect account status queries (Salesforce status: active/canceled/past due)
            account_status_keywords = ['account status', 'customer status', 'subscription status', 'enrollment status', 'active', 'canceled', 'cancelled', 'past due', 'current status']
            has_status_keywords = any(keyword in query_lower for keyword in account_status_keywords)
            
            # Exclude credit-related status queries
            credit_status_indicators = ['credit status', 'credit score', 'bureau', 'utilization', 'tradeline']
            is_credit_status_query = any(indicator in query_lower for indicator in credit_status_indicators)
            
            # Only treat as account status if it's not a credit status query
            has_status_keywords = has_status_keywords and not is_credit_status_query
            print(f"🔍 Query analysis: has_status_keywords={has_status_keywords}, query='{query_lower}'")
            has_credit_keywords = any(keyword in query_lower for keyword in ['credit', 'score', 'bureau', 'utilization', 'inquiry'])
            has_phone_keywords = any(keyword in query_lower for keyword in ['call', 'phone', 'agent', 'campaign', 'duration'])
            has_transaction_keywords = any(keyword in query_lower for keyword in ['transaction', 'payment', 'charge', 'refund', 'amount', 'billing'])
            has_card_keywords = any(keyword in query_lower for keyword in ['card', 'credit card', 'bin', 'expiration', 'prepaid'])
            has_zoho_keywords = any(keyword in query_lower for keyword in ['ticket', 'support', 'zoho', 'issue', 'complaint', 'help'])
            has_combined_keywords = any(keyword in query_lower for keyword in ['combined', 'both', 'together', 'profile and', 'history and', 'comprehensive', 'all data'])

            # Fetch data based on query type
            context = {
                "query": query,
                "analysis_timestamp": datetime.now().isoformat(),
                "entity_id": entity_id
            }

            # Handle status queries with concise responses
            if has_status_keywords and not any([has_credit_keywords, has_phone_keywords, has_transaction_keywords, has_card_keywords, has_zoho_keywords, has_combined_keywords]):
                print("🔍 Processing customer status query...")

                # Use transaction data to determine customer status (more reliable)
                try:
                    transaction_data = await self.get_transaction_data(entity_id)
                    print(f"🔍 Transaction data result: {transaction_data is not None}")
                    if transaction_data:
                        print(f"🔍 Transaction data keys: {list(transaction_data.keys())}")
                        print(f"🔍 Records count: {len(transaction_data.get('records', []))}")
                except Exception as e:
                    print(f"⚠️ Error fetching transaction data: {e}")
                    transaction_data = None

                if transaction_data and transaction_data.get("records"):
                    # Extract customer info and status from transaction data
                    current_product = None
                    latest_transaction_date = None
                    total_amount = 0
                    transaction_count = len(transaction_data["records"])
                    recent_transactions = []
                    
                    for record in transaction_data["records"]:
                        if record.get("CURRENT_PRODUCT"):
                            current_product = record.get("CURRENT_PRODUCT")
                        
                        # Get transaction date and amount
                        trans_date = record.get("TRANSACTION_CREATED_DATE")
                        if trans_date and (not latest_transaction_date or trans_date > latest_transaction_date):
                            latest_transaction_date = trans_date
                        
                        amount = record.get("TRANSACTION_AMOUNT")
                        if amount:
                            try:
                                amount_float = float(amount)
                                total_amount += amount_float
                                recent_transactions.append({
                                    "date": trans_date,
                                    "amount": amount_float,
                                    "type": record.get("TYPE", "Unknown")
                                })
                            except (ValueError, TypeError):
                                pass
                    
                    # Sort transactions by date (most recent first)
                    recent_transactions.sort(key=lambda x: x.get("date", ""), reverse=True)
                    
                    # Determine account status based on transaction patterns
                    if transaction_count > 0 and current_product:
                        # Check for recent activity (within last 6 months)
                        from datetime import timedelta
                        six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
                        
                        recent_activity = any(
                            trans.get("date", "") > six_months_ago 
                            for trans in recent_transactions
                        )
                        
                        if recent_activity:
                            # Look for refunds/credits which might indicate cancellation
                            has_refunds = any(
                                trans.get("type", "").lower() in ["credit", "refund"] 
                                for trans in recent_transactions[:3]  # Check last 3 transactions
                            )
                            
                            if has_refunds:
                                inferred_status = "Recently Canceled (refund activity detected)"
                            else:
                                inferred_status = "Active"
                        else:
                            inferred_status = "Inactive (no recent transactions)"
                    elif transaction_count > 0:
                        inferred_status = "Active (transaction history present)"
                    else:
                        inferred_status = "Unknown (no transaction data)"
                    
                    # Create concise status response focused on account status
                    response = "**Salesforce Account Status:**\n\n"
                    response += f"• **Account Status:** {inferred_status}\n"
                    
                    if current_product:
                        response += f"• **Current Product:** {current_product}\n"
                    
                    if latest_transaction_date:
                        response += f"• **Last Activity:** {latest_transaction_date}\n"
                    
                    # Show recent transaction summary
                    if recent_transactions:
                        response += f"• **Recent Transactions:** {len(recent_transactions[:5])} transactions\n"
                        if len(recent_transactions) > 0:
                            latest = recent_transactions[0]
                            response += f"• **Latest Transaction:** ${latest.get('amount', 0):.2f} ({latest.get('type', 'Unknown')})\n"
                    
                    self._cache_response(cache_key, response)
                    return response
                else:
                    return "No transaction data found for the specified customer. Unable to determine account status."

            # Count how many data types are requested
            data_type_count = sum([has_credit_keywords, has_phone_keywords, has_transaction_keywords, has_card_keywords, has_zoho_keywords])

            if has_combined_keywords or data_type_count > 1:
                # Multi-data analysis - fetch all requested data types IN PARALLEL
                print("🚀 Fetching multiple data types in parallel...")
                fetch_start = datetime.now()

                # Create async tasks for parallel execution
                tasks = []

                if has_credit_keywords or has_combined_keywords:
                    tasks.append(self._fetch_credit_data_async(entity_id))
                else:
                    tasks.append(asyncio.create_task(asyncio.sleep(0, result=None)))

                if has_phone_keywords or has_combined_keywords:
                    tasks.append(self.get_phone_call_data(entity_id))
                else:
                    tasks.append(asyncio.create_task(asyncio.sleep(0, result=None)))

                if has_transaction_keywords or has_combined_keywords:
                    tasks.append(self.get_transaction_data(entity_id))
                else:
                    tasks.append(asyncio.create_task(asyncio.sleep(0, result=None)))

                if has_card_keywords or has_combined_keywords:
                    tasks.append(self.get_credit_card_data(entity_id))
                else:
                    tasks.append(asyncio.create_task(asyncio.sleep(0, result=None)))

                if has_zoho_keywords or has_combined_keywords:
                    tasks.append(self.get_zoho_ticket_data(entity_id))
                else:
                    tasks.append(asyncio.create_task(asyncio.sleep(0, result=None)))

                # Execute all data fetches in parallel with timeout
                try:
                    results = await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=15.0  # 15 second timeout for data fetching
                    )
                except asyncio.TimeoutError:
                    print("⚠️ Data fetch timeout - using partial results")
                    results = [None] * len(tasks)

                fetch_duration = (datetime.now() - fetch_start).total_seconds()
                print(f"⚡ Parallel data fetch completed in {fetch_duration:.1f}s")

                # Process results
                credit_records, phone_data, transaction_data, card_data, ticket_data = results

                # Handle credit data
                if credit_records and not isinstance(credit_records, Exception):
                    temporal_data = self.extract_temporal_credit_data(credit_records)
                    context["temporal_credit_data"] = temporal_data
                else:
                    context["temporal_credit_data"] = {}

                # Handle other data types
                context["phone_call_data"] = phone_data if phone_data and not isinstance(phone_data, Exception) else {}
                context["transaction_data"] = transaction_data if transaction_data and not isinstance(transaction_data, Exception) else {}
                context["credit_card_data"] = card_data if card_data and not isinstance(card_data, Exception) else {}
                context["zoho_ticket_data"] = ticket_data if ticket_data and not isinstance(ticket_data, Exception) else {}

                context["data_summary"] = {
                    "has_credit_data": bool(context.get("temporal_credit_data")),
                    "has_phone_data": bool(context.get("phone_call_data", {}).get("call_records_count", 0) > 0),
                    "has_transaction_data": bool(context.get("transaction_data", {}).get("transaction_records_count", 0) > 0),
                    "has_card_data": bool(context.get("credit_card_data", {}).get("card_records_count", 0) > 0),
                    "has_ticket_data": bool(context.get("zoho_ticket_data", {}).get("ticket_records_count", 0) > 0)
                }

            elif has_phone_keywords:
                # Phone-only analysis
                phone_data = await self.get_phone_call_data(entity_id)
                if not phone_data:
                    return f"No phone call data found for the requested customer (Entity ID: {entity_id})."
                context["phone_call_data"] = phone_data

            elif has_transaction_keywords:
                # Transaction-only analysis
                transaction_data = await self.get_transaction_data(entity_id)
                if not transaction_data:
                    return f"No transaction data found for the requested customer (Entity ID: {entity_id})."
                context["transaction_data"] = transaction_data

            elif has_card_keywords:
                # Credit card-only analysis
                card_data = await self.get_credit_card_data(entity_id)
                if not card_data:
                    return f"No credit card data found for the requested customer (Entity ID: {entity_id})."
                context["credit_card_data"] = card_data

            elif has_zoho_keywords:
                # Zoho ticket-only analysis
                ticket_data = await self.get_zoho_ticket_data(entity_id)
                if not ticket_data:
                    return f"No Zoho ticket data found for the requested customer (Entity ID: {entity_id})."
                context["zoho_ticket_data"] = ticket_data

            else:
                # Credit-only analysis (default) - use async for consistency
                print("🚀 Fetching credit data...")
                fetch_start = datetime.now()
                credit_records = await self._fetch_credit_data_async(entity_id)
                fetch_duration = (datetime.now() - fetch_start).total_seconds()
                print(f"⚡ Credit data fetch completed in {fetch_duration:.1f}s")

                if not credit_records:
                    return f"No credit data found for the requested customer (Entity ID: {entity_id})."

                temporal_data = self.extract_temporal_credit_data(credit_records)
                context["temporal_credit_data"] = temporal_data

            # Create system prompt for multi-data analysis
            data_types = []
            if context.get("temporal_credit_data"):
                data_types.append("temporal credit data with scores, utilization, and bureau information")
            if context.get("phone_call_data"):
                data_types.append("phone call history with agent interactions, call duration, and campaign data")
            if context.get("transaction_data"):
                data_types.append("transaction history with payment methods, amounts, and billing data")
            if context.get("credit_card_data"):
                data_types.append("credit card information with BINs, expiration dates, and card status")
            if context.get("zoho_ticket_data"):
                data_types.append("support ticket data with categories, statuses, and customer service interactions")

            if len(data_types) > 1:
                system_prompt = f"""You are a Credit Pros advisor with access to comprehensive customer data across multiple sources.
                Analyze the provided data to answer the user's question accurately and professionally.

                Available data:
                {chr(10).join(f'- {dt}' for dt in data_types)}

                Provide insights that combine multiple data sources when relevant and focus on the specific question asked."""
            elif context.get("phone_call_data"):
                system_prompt = """You are a Credit Pros advisor with access to phone call history data.
                Analyze the provided call data to answer the user's question accurately and professionally.

                Available data:
                - Phone call records with agents, duration, types, and campaigns
                - Call aggregation data with totals, averages, and timelines

                Focus on call patterns, agent performance, and customer interaction insights."""
            elif context.get("transaction_data"):
                system_prompt = """You are a Credit Pros advisor with access to transaction history data.
                Analyze the provided transaction data to answer the user's question accurately and professionally.

                Available data:
                - Transaction records with amounts, payment methods, and billing information
                - Transaction aggregation data with totals, averages, and timelines

                Focus on payment patterns, transaction trends, and financial behavior insights."""
            elif context.get("credit_card_data"):
                system_prompt = """You are a Credit Pros advisor with access to credit card data.
                Analyze the provided card data to answer the user's question accurately and professionally.

                Available data:
                - Credit card records with BINs, expiration dates, and status information
                - Card aggregation data with counts, types, and status summaries

                Focus on card management, expiration tracking, and payment method insights."""
            elif context.get("zoho_ticket_data"):
                system_prompt = """You are a Credit Pros advisor with access to customer support ticket data.
                Analyze the provided ticket data to answer the user's question accurately and professionally.

                Available data:
                - Support ticket records with categories, statuses, and priorities
                - Ticket aggregation data with trends, sentiment analysis, and resolution patterns

                Focus on customer service patterns, issue resolution, and support quality insights."""
            else:
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
                response = self._call_openai_with_context(ai_messages, model, temperature, max_tokens)
            elif model.startswith("gemini-") or model in self.providers["google"]["models"]:
                response = self._call_google_with_context(ai_messages, model, temperature, max_tokens)
            elif model in self.providers["groq"]["models"]:
                response = self._call_groq_with_context(ai_messages, model, temperature, max_tokens)
            else:
                # Default to OpenAI
                response = self._call_openai_with_context(ai_messages, "gpt-4o-mini", temperature, max_tokens)

            # Cache successful response
            self._cache_response(cache_key, response)
            return response

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
        finally:
            self.active_requests -= 1
            duration = (datetime.now() - start_time).total_seconds()
            print(f"✅ Request #{self.active_requests + 1} completed in {duration:.1f}s")

# Initialize the API
api = MultiProviderCreditAPI()

# Define lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Multi-Provider Credit Analysis API starting up...")
    print(f"🌐 Server will bind to 0.0.0.0:{os.environ.get('PORT', 8081)}")
    print("✅ Application startup complete")
    yield
    # Shutdown (if needed)
    print("🛑 Application shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Multi-Provider Credit Analysis API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add validation error handler for debugging
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"🚨 DEBUG: Validation error from {request.client.host}")
    print(f"🚨 DEBUG: Request URL: {request.url}")
    print(f"🚨 DEBUG: Request method: {request.method}")
    print(f"🚨 DEBUG: Validation errors: {exc.errors()}")

    # Try to get the raw request body for debugging
    try:
        body = await request.body()
        print(f"🚨 DEBUG: Request body: {body.decode()}")
    except Exception as e:
        print(f"🚨 DEBUG: Could not read request body: {e}")

    return JSONResponse(
        status_code=422,
        content={"detail": f"Validation error: {exc.errors()}", "body": "Check server logs for details"}
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "multi-provider-credit-api", "version": "1.0.0"}

@app.get("/v1")
async def v1_info():
    """OpenAI-compatible API info endpoint for validation"""
    return {
        "object": "api",
        "version": "v1",
        "service": "tilores-multi-data-analysis",
        "compatible": "openai"
    }

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
async def chat_completions(request: Request):
    """Chat completions endpoint supporting multiple providers"""
    try:
        # Get raw request body and parse it
        body = await request.body()
        request_data = json.loads(body.decode())

        # Debug logging for troubleshooting Agenta.ai requests
        print(f"🔍 DEBUG: Raw request body: {body.decode()}")
        print(f"🔍 DEBUG: Parsed request data: {request_data}")
        print(f"🔍 DEBUG: Request headers: {dict(request.headers)}")

        # Extract required fields with defaults
        model = request_data.get("model", "gpt-4o-mini")
        messages = request_data.get("messages", [])
        temperature = request_data.get("temperature", 0.7)
        max_tokens = request_data.get("max_tokens")
        stream = request_data.get("stream", False)

        print(f"🔍 DEBUG: Extracted - Model: {model}, Messages: {len(messages)}, Temp: {temperature}")

        # Convert messages to our format, handling both string and structured content
        chat_messages = []
        for msg in messages:
            content = msg.get("content", "")

            # Handle structured content (list format) - extract text from ALL text blocks
            if isinstance(content, list):
                print(f"🔍 DEBUG: Converting structured content: {content}")
                text_content = ""
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_content += block.get("text", "")
                content = text_content
                print(f"🔍 DEBUG: Extracted text: '{content}'")

            chat_messages.append(ChatMessage(role=msg.get("role", "user"), content=content))

        # Process the request
        response_content = await api.process_chat_request(
            chat_messages,
            model,
            temperature,
            max_tokens
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
            # Create OpenAI-compatible response
            response = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
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
                    "prompt_tokens": 0,  # Would need to implement token counting
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }

            return response

    except json.JSONDecodeError as je:
        print(f"🚨 DEBUG: JSON decode error: {str(je)}")
        raise HTTPException(status_code=422, detail=f"Invalid JSON: {str(je)}")
    except ValueError as ve:
        print(f"🚨 DEBUG: ValueError in chat_completions: {str(ve)}")
        raise HTTPException(status_code=422, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        print(f"🚨 DEBUG: Exception in chat_completions: {str(e)}")
        print(f"🚨 DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"🚨 DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    # Railway provides PORT environment variable
    port = int(os.environ.get("PORT", 8081))
    uvicorn.run(app, host="0.0.0.0", port=port)
