#!/usr/bin/env python3
"""
Langfuse Trace Retrieval Script
Retrieves and analyzes Langfuse traces for debugging production issues.

Usage:
    python langfuse_trace_retriever.py <trace_id>

Environment Variables Required:
    LANGFUSE_SECRET_KEY
    LANGFUSE_PUBLIC_KEY  
    LANGFUSE_HOST
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional

class LangfuseTraceRetriever:
    def __init__(self):
        self.secret_key = os.getenv('LANGFUSE_SECRET_KEY')
        self.public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
        self.host = os.getenv('LANGFUSE_HOST', 'https://us.cloud.langfuse.com')
        
        if not all([self.secret_key, self.public_key]):
            raise ValueError("Missing Langfuse credentials. Set LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY")
    
    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific trace from Langfuse using basic auth"""
        url = f"{self.host}/api/public/traces/{trace_id}"
        
        try:
            # Use basic auth with public_key:secret_key
            response = requests.get(url, auth=(self.public_key, self.secret_key), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            return None
    
    def analyze_trace(self, trace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trace data and extract key insights"""
        analysis = {
            'trace_id': trace_data.get('id'),
            'name': trace_data.get('name'),
            'timestamp': trace_data.get('timestamp'),
            'user_id': trace_data.get('userId'),
            'session_id': trace_data.get('sessionId'),
            'tags': trace_data.get('tags', []),
            'input': trace_data.get('input', {}),
            'output': trace_data.get('output', {}),
            'metadata': trace_data.get('metadata', {}),
            'latency': trace_data.get('latency'),
            'total_cost': trace_data.get('totalCost'),
            'observations': trace_data.get('observations', [])
        }
        
        # Check for errors or issues
        issues = []
        
        # Check if response contains GraphQL suggestions (indicates incomplete analysis)
        output_text = str(analysis['output'].get('response', ''))
        if 'GRAPHQL_QUERY:' in output_text or 'query GetCreditRepairData' in output_text:
            issues.append("INCOMPLETE_ANALYSIS: Response contains GraphQL query suggestions instead of complete analysis")
        
        # Check if analysis section exists
        if 'ANALYSIS SECTION:' not in output_text:
            issues.append("MISSING_ANALYSIS: No ANALYSIS SECTION found in response")
        
        # Check for credit score information
        if 'credit score' not in output_text.lower():
            issues.append("MISSING_CREDIT_SCORES: No credit score information in analysis")
        
        analysis['issues'] = issues
        
        return analysis
    
    def display_trace_analysis(self, trace_id: str):
        """Retrieve and display comprehensive trace analysis"""
        print(f"🔍 Analyzing Langfuse Trace: {trace_id}")
        print("=" * 60)
        
        # Get trace data
        trace_data = self.get_trace(trace_id)
        if not trace_data:
            print("❌ Failed to retrieve trace data")
            return
        
        # Analyze trace
        analysis = self.analyze_trace(trace_data)
        
        # Display overview
        print(f"📊 Trace Overview:")
        print(f"   ID: {analysis['trace_id']}")
        print(f"   Name: {analysis['name'] or 'N/A'}")
        print(f"   Timestamp: {analysis['timestamp'] or 'N/A'}")
        print(f"   User ID: {analysis['user_id'] or 'N/A'}")
        print(f"   Session ID: {analysis['session_id'] or 'N/A'}")
        print(f"   Latency: {analysis['latency']}ms")
        print(f"   Cost: ${analysis['total_cost']}")
        
        # Display input
        input_data = analysis['input']
        if input_data:
            print(f"\n📥 Input:")
            print(f"   Command: {input_data.get('command', 'N/A')}")
            print(f"   Query: {input_data.get('query', 'N/A')}")
        
        # Display issues
        if analysis['issues']:
            print(f"\n🚨 Issues Detected:")
            for issue in analysis['issues']:
                print(f"   ❌ {issue}")
        else:
            print(f"\n✅ No issues detected")
        
        # Display output preview
        output_data = analysis['output']
        if output_data and 'response' in output_data:
            response = output_data['response']
            print(f"\n📤 Output Preview (first 500 chars):")
            print(f"   {response[:500]}{'...' if len(response) > 500 else ''}")
            
            # Check response structure
            if '**CUSTOMER PROFILE:**' in response:
                print(f"   ✅ Has Customer Profile section")
            else:
                print(f"   ❌ Missing Customer Profile section")
                
            if '**ANALYSIS SECTION:**' in response:
                print(f"   ✅ Has Analysis section")
            else:
                print(f"   ❌ Missing Analysis section")
                
            if '**RECOMMENDATIONS:**' in response:
                print(f"   ✅ Has Recommendations section")
            else:
                print(f"   ❌ Missing Recommendations section")
        
        # Display observations
        observations = analysis['observations']
        if observations:
            print(f"\n🔬 Observations ({len(observations)}):")
            for obs in observations[:3]:  # Show first 3
                name = obs.get('name', 'Unknown')
                obs_type = obs.get('type', 'Unknown')
                latency = obs.get('latency', 'N/A')
                print(f"   • {name} ({obs_type}) - {latency}ms")
        
        print(f"\n🔗 Full Trace URL: {self.host}/trace/{trace_id}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python langfuse_trace_retriever.py <trace_id>")
        print("Environment variables required:")
        print("  LANGFUSE_PUBLIC_KEY")
        print("  LANGFUSE_SECRET_KEY")
        print("  LANGFUSE_HOST (optional, defaults to https://us.cloud.langfuse.com)")
        sys.exit(1)
    
    trace_id = sys.argv[1]
    
    try:
        retriever = LangfuseTraceRetriever()
        retriever.display_trace_analysis(trace_id)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
