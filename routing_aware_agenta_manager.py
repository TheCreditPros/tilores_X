#!/usr/bin/env python3
"""
Routing-Aware Agenta.ai Manager
Provides intelligent routing context for UI-based testing that replicates chat session behavior
"""

import json
import os
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

# Import base Agenta manager
try:
    from agenta_sdk_manager_enhanced import EnhancedAgentaManager
    BASE_MANAGER_AVAILABLE = True
except ImportError:
    try:
        from agenta_sdk_manager import AgentaSDKManager as EnhancedAgentaManager
        BASE_MANAGER_AVAILABLE = True
    except ImportError:
        print("⚠️ Base Agenta manager not available")
        BASE_MANAGER_AVAILABLE = False
        EnhancedAgentaManager = object

@dataclass
class RoutingContext:
    """
    Comprehensive routing context for intelligent prompt selection
    """
    query: str
    detected_route: str
    routing_keywords: List[str]
    customer_identifiers: List[str]
    data_types_requested: List[str]
    complexity_score: float
    multi_data_flag: bool
    fallback_reason: Optional[str] = None
    confidence_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "query": self.query,
            "detected_route": self.detected_route,
            "routing_keywords": self.routing_keywords,
            "customer_identifiers": self.customer_identifiers,
            "data_types_requested": self.data_types_requested,
            "complexity_score": self.complexity_score,
            "multi_data_flag": self.multi_data_flag,
            "fallback_reason": self.fallback_reason,
            "confidence_score": self.confidence_score
        }

class RoutingAwareAgentaManager(EnhancedAgentaManager if BASE_MANAGER_AVAILABLE else object):
    """
    Enhanced Agenta.ai manager with intelligent routing awareness
    Replicates TLRS routing logic for UI testing
    """
    
    def __init__(self):
        """Initialize routing-aware manager"""
        if BASE_MANAGER_AVAILABLE:
            super().__init__()
        else:
            # Minimal initialization if base manager not available
            self.agenta_available = False
            self.initialized = False
        
        # Load routing configuration
        self.routing_config = self._load_routing_config()
        
        # Initialize routing patterns (mirrors TLRS production logic)
        self._init_routing_patterns()
        
        print("🎯 RoutingAwareAgentaManager initialized")
        print(f"   - Base Manager: {'✅' if BASE_MANAGER_AVAILABLE else '❌'}")
        print(f"   - Routing Patterns: {len(self.routing_patterns)} configured")
    
    def _load_routing_config(self) -> Dict[str, Any]:
        """Load routing configuration"""
        try:
            with open("agenta_production_config_20250903_143055.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ Routing config not found, using defaults")
            return {}
    
    def _init_routing_patterns(self):
        """Initialize routing patterns that mirror TLRS production logic"""
        self.routing_patterns = {
            "status": {
                "keywords": ['account status', 'customer status', 'subscription status', 
                           'enrollment status', 'active', 'canceled', 'past due'],
                "exclusions": ['credit status', 'credit score', 'bureau', 'utilization'],
                "variant": "account-status-v1",
                "priority": 1,
                "bypass_ai": True  # Direct database query
            },
            "credit": {
                "keywords": ['credit', 'score', 'bureau', 'experian', 'transunion', 'equifax',
                           'utilization', 'improve', 'repair', 'report'],
                "variant": "credit-analysis-comprehensive-v1",
                "priority": 3,
                "data_types": ["credit_data"]
            },
            "transaction": {
                "keywords": ['transaction', 'payment', 'charge', 'refund', 'amount', 
                           'billing', 'history', 'patterns'],
                "variant": "transaction-analysis-v1",
                "priority": 3,
                "data_types": ["transaction_data"]
            },
            "phone": {
                "keywords": ['call', 'phone', 'agent', 'campaign', 'duration', 'contact'],
                "variant": "phone-call-analysis-v1",
                "priority": 3,
                "data_types": ["phone_data"]
            },
            "multi_data": {
                "keywords": ['comprehensive', 'complete', 'all data', 'everything', 
                           'combined', 'both', 'together'],
                "variant": "multi-data-analysis-v1",
                "priority": 2,
                "data_types": ["credit_data", "transaction_data", "phone_data", "card_data"]
            },
            "general": {
                "keywords": [],  # Fallback
                "variant": "multi-data-analysis-v1",
                "priority": 4,
                "fallback": True
            }
        }
        
        # Customer identification patterns
        self.customer_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            "client_id": r'\b(?:client[_\s]?id|customer[_\s]?id)[\s:]*([A-Za-z0-9-]+)\b',
            "name": r'\b(?:for|customer|client)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        }
    
    def analyze_query_routing(self, query: str) -> RoutingContext:
        """
        Analyze query and determine routing context (mirrors TLRS logic)
        """
        query_lower = query.lower()
        
        # 1. Extract customer identifiers
        customer_identifiers = self._extract_customer_identifiers(query)
        
        # 2. Detect routing based on keywords and priority
        detected_route, routing_keywords, confidence = self._detect_route(query_lower)
        
        # 3. Determine data types requested
        data_types_requested = self._determine_data_types(detected_route, query_lower)
        
        # 4. Calculate complexity score
        complexity_score = self._calculate_complexity_score(query, routing_keywords, data_types_requested)
        
        # 5. Check for multi-data flag
        multi_data_flag = self._check_multi_data_flag(query_lower, data_types_requested)
        
        # 6. Determine fallback reason if applicable
        fallback_reason = self._determine_fallback_reason(detected_route, customer_identifiers)
        
        return RoutingContext(
            query=query,
            detected_route=detected_route,
            routing_keywords=routing_keywords,
            customer_identifiers=customer_identifiers,
            data_types_requested=data_types_requested,
            complexity_score=complexity_score,
            multi_data_flag=multi_data_flag,
            fallback_reason=fallback_reason,
            confidence_score=confidence
        )
    
    def _extract_customer_identifiers(self, query: str) -> List[str]:
        """Extract customer identifiers from query"""
        identifiers = []
        
        for id_type, pattern in self.customer_patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else match[1] if len(match) > 1 else ""
                if match and len(match.strip()) > 2:
                    identifiers.append(f"{id_type}:{match.strip()}")
        
        return identifiers
    
    def _detect_route(self, query_lower: str) -> Tuple[str, List[str], float]:
        """Detect route based on keywords and priority"""
        route_scores = {}
        
        for route_name, config in self.routing_patterns.items():
            score = 0
            matched_keywords = []
            
            # Check keywords
            for keyword in config["keywords"]:
                if keyword in query_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            # Check exclusions (for status queries)
            if "exclusions" in config:
                for exclusion in config["exclusions"]:
                    if exclusion in query_lower:
                        score = 0  # Exclude this route
                        matched_keywords = []
                        break
            
            # Apply priority weighting
            priority_weight = 1.0 / config["priority"]
            route_scores[route_name] = {
                "score": score * priority_weight,
                "keywords": matched_keywords,
                "priority": config["priority"]
            }
        
        # Find best route
        best_route = "general"
        best_keywords = []
        best_confidence = 0.5
        
        for route_name, data in route_scores.items():
            if data["score"] > 0:
                confidence = min(data["score"] / len(self.routing_patterns[route_name]["keywords"]), 1.0) if self.routing_patterns[route_name]["keywords"] else 0.5
                if data["score"] > route_scores[best_route]["score"] or (data["score"] == route_scores[best_route]["score"] and data["priority"] < route_scores[best_route]["priority"]):
                    best_route = route_name
                    best_keywords = data["keywords"]
                    best_confidence = confidence
        
        return best_route, best_keywords, best_confidence
    
    def _determine_data_types(self, route: str, query_lower: str) -> List[str]:
        """Determine what data types are requested"""
        route_config = self.routing_patterns.get(route, {})
        data_types = route_config.get("data_types", [])
        
        # Additional data type detection based on query content
        additional_types = []
        if any(word in query_lower for word in ['credit', 'score', 'bureau']):
            additional_types.append("credit_data")
        if any(word in query_lower for word in ['transaction', 'payment', 'billing']):
            additional_types.append("transaction_data")
        if any(word in query_lower for word in ['call', 'phone', 'contact']):
            additional_types.append("phone_data")
        if any(word in query_lower for word in ['card', 'credit card']):
            additional_types.append("card_data")
        
        # Combine and deduplicate
        all_types = list(set(data_types + additional_types))
        return all_types
    
    def _calculate_complexity_score(self, query: str, keywords: List[str], data_types: List[str]) -> float:
        """Calculate query complexity score"""
        base_score = 0.3
        
        # Length factor
        length_factor = min(len(query) / 100, 0.3)
        
        # Keyword factor
        keyword_factor = min(len(keywords) * 0.1, 0.2)
        
        # Data type factor
        data_type_factor = min(len(data_types) * 0.1, 0.2)
        
        return base_score + length_factor + keyword_factor + data_type_factor
    
    def _check_multi_data_flag(self, query_lower: str, data_types: List[str]) -> bool:
        """Check if this is a multi-data query"""
        # Multi-data keywords
        multi_keywords = ['comprehensive', 'complete', 'all data', 'everything', 'combined', 'both', 'together']
        has_multi_keywords = any(keyword in query_lower for keyword in multi_keywords)
        
        # Multiple data types requested
        multiple_data_types = len(data_types) > 1
        
        return has_multi_keywords or multiple_data_types
    
    def _determine_fallback_reason(self, route: str, customer_identifiers: List[str]) -> Optional[str]:
        """Determine fallback reason if applicable"""
        if not customer_identifiers:
            return "no_customer_identified"
        
        if route == "general":
            return "no_specific_keywords_detected"
        
        return None
    
    def get_routing_aware_prompt_config(self, query: str) -> Dict[str, Any]:
        """
        Get prompt configuration with routing context for UI testing
        """
        # Analyze routing
        routing_context = self.analyze_query_routing(query)
        
        # Get base prompt configuration
        route_config = self.routing_patterns.get(routing_context.detected_route, {})
        variant_name = route_config.get("variant", "multi-data-analysis-v1")
        
        # Get prompt config from base manager if available
        if BASE_MANAGER_AVAILABLE and hasattr(self, 'get_prompt_config'):
            base_config = self.get_prompt_config(routing_context.detected_route, query)
        else:
            base_config = {
                "source": "routing_aware",
                "variant_slug": variant_name,
                "system_prompt": f"You are analyzing a {routing_context.detected_route} query.",
                "temperature": 0.7,
                "max_tokens": 2000
            }
        
        # Enhance with routing context
        routing_context_text = self._generate_routing_context_text(routing_context)
        
        enhanced_config = {
            **base_config,
            "routing_context": routing_context.to_dict(),
            "routing_context_text": routing_context_text,
            "enhanced_system_prompt": self._inject_routing_context(
                base_config.get("system_prompt", ""), 
                routing_context_text
            ),
            "ui_testing_metadata": {
                "expected_variant": variant_name,
                "routing_confidence": routing_context.confidence_score,
                "complexity_level": "high" if routing_context.complexity_score > 0.7 else "medium" if routing_context.complexity_score > 0.4 else "low",
                "multi_data_query": routing_context.multi_data_flag,
                "customer_identified": len(routing_context.customer_identifiers) > 0
            }
        }
        
        return enhanced_config
    
    def _generate_routing_context_text(self, context: RoutingContext) -> str:
        """Generate human-readable routing context"""
        lines = []
        
        lines.append(f"[ROUTING CONTEXT: This query was routed to {context.detected_route} analysis")
        
        if context.routing_keywords:
            lines.append(f" based on detected keywords: {', '.join(context.routing_keywords)}")
        
        if context.fallback_reason:
            lines.append(f" (fallback reason: {context.fallback_reason})")
        
        lines.append("]")
        
        if context.customer_identifiers:
            lines.append(f"[CUSTOMER CONTEXT: Identified - {', '.join(context.customer_identifiers)}]")
        else:
            lines.append("[CUSTOMER CONTEXT: No customer identifiers found]")
        
        if context.data_types_requested:
            available_types = [dt for dt in context.data_types_requested if dt != "phone_data"]  # Phone data not available
            unavailable_types = [dt for dt in context.data_types_requested if dt == "phone_data"]
            
            data_availability = []
            if available_types:
                data_availability.append(f"Available - {', '.join(available_types)}")
            if unavailable_types:
                data_availability.append(f"Unavailable - {', '.join(unavailable_types)}")
            
            if data_availability:
                lines.append(f"[DATA AVAILABILITY: {'; '.join(data_availability)}]")
        
        return "\n".join(lines)
    
    def _inject_routing_context(self, base_prompt: str, routing_context_text: str) -> str:
        """Inject routing context into system prompt"""
        if not base_prompt:
            return routing_context_text
        
        # Inject at the beginning of the prompt
        enhanced_prompt = f"{routing_context_text}\n\n{base_prompt}"
        
        return enhanced_prompt
    
    def create_ui_test_session(self, queries: List[str]) -> Dict[str, Any]:
        """
        Create a UI test session that replicates chat behavior
        """
        session_id = f"ui_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "queries": [],
            "routing_analysis": [],
            "expected_variants": [],
            "test_metadata": {
                "total_queries": len(queries),
                "unique_routes": set(),
                "complexity_distribution": {"low": 0, "medium": 0, "high": 0}
            }
        }
        
        for i, query in enumerate(queries):
            config = self.get_routing_aware_prompt_config(query)
            routing_context = config["routing_context"]
            
            session_data["queries"].append({
                "index": i,
                "query": query,
                "config": config
            })
            
            session_data["routing_analysis"].append(routing_context)
            session_data["expected_variants"].append(config["ui_testing_metadata"]["expected_variant"])
            
            # Update metadata
            session_data["test_metadata"]["unique_routes"].add(routing_context["detected_route"])
            complexity = config["ui_testing_metadata"]["complexity_level"]
            session_data["test_metadata"]["complexity_distribution"][complexity] += 1
        
        # Convert set to list for JSON serialization
        session_data["test_metadata"]["unique_routes"] = list(session_data["test_metadata"]["unique_routes"])
        
        return session_data
    
    def export_ui_test_session(self, queries: List[str], filename: str = None) -> str:
        """Export UI test session to file"""
        session_data = self.create_ui_test_session(queries)
        
        if not filename:
            filename = f"ui_test_session_{session_data['session_id']}.json"
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"✅ UI test session exported to: {filename}")
        return filename

if __name__ == "__main__":
    # Test the routing-aware manager
    manager = RoutingAwareAgentaManager()
    
    # Test queries that replicate chat session behavior
    test_queries = [
        "What is the credit score for e.j.price1986@gmail.com?",
        "What is the account status for e.j.price1986@gmail.com?",
        "Give me comprehensive analysis for e.j.price1986@gmail.com",
        "Show me payment history for e.j.price1986@gmail.com",
        "How can e.j.price1986@gmail.com improve their credit score?",
        "Show data for invalid@nonexistent.com",
        ""  # Empty query
    ]
    
    print(f"\n🧪 TESTING ROUTING-AWARE MANAGER")
    print(f"=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query[:50]}{'...' if len(query) > 50 else ''}")
        config = manager.get_routing_aware_prompt_config(query)
        
        print(f"   Route: {config['routing_context']['detected_route']}")
        print(f"   Variant: {config['ui_testing_metadata']['expected_variant']}")
        print(f"   Confidence: {config['routing_context']['confidence_score']:.2f}")
        print(f"   Complexity: {config['ui_testing_metadata']['complexity_level']}")
    
    # Export UI test session
    session_file = manager.export_ui_test_session(test_queries)
    print(f"\n✅ UI test session ready for Agenta.ai testing!")
