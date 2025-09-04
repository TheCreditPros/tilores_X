#!/usr/bin/env python3
"""
Multi-threaded routing logic testing to identify prompt configuration issues
Following prevention strategy: Test routing + prompts first before touching data logic
"""

import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple

sys.path.append('.')
from direct_credit_api_fixed import MultiProviderCreditAPI

class RoutingTester:
    def __init__(self):
        self.api = MultiProviderCreditAPI()
        self.results = []
        self.lock = threading.Lock()
    
    def test_single_query(self, query: str, expected_type: str = None) -> Dict:
        """Test a single query and return routing results"""
        try:
            start_time = time.time()
            
            # Test routing detection
            detected_type = self.api.detect_query_type(query)
            
            # Test prompt selection (without full API call)
            if hasattr(self.api, 'agenta_manager') and self.api.agenta_manager:
                try:
                    prompt_config = self.api.agenta_manager.get_prompt_config(detected_type, query)
                    prompt_source = prompt_config.get('source', 'unknown')
                    prompt_variant = prompt_config.get('variant_slug', 'unknown')
                    system_prompt_preview = prompt_config.get('system_prompt', '')[:100] + '...'
                except:
                    prompt_source = 'error'
                    prompt_variant = 'error'
                    system_prompt_preview = 'error'
            else:
                prompt_source = 'no_agenta'
                prompt_variant = 'no_agenta'
                system_prompt_preview = 'no_agenta'
            
            duration = time.time() - start_time
            
            result = {
                'query': query,
                'expected_type': expected_type,
                'detected_type': detected_type,
                'prompt_source': prompt_source,
                'prompt_variant': prompt_variant,
                'system_prompt_preview': system_prompt_preview,
                'duration': duration,
                'correct_routing': detected_type == expected_type if expected_type else None
            }
            
            with self.lock:
                self.results.append(result)
                print(f"✅ {query[:30]:<30} → {detected_type:<12} ({prompt_variant})")
            
            return result
            
        except Exception as e:
            error_result = {
                'query': query,
                'expected_type': expected_type,
                'detected_type': 'ERROR',
                'error': str(e),
                'duration': 0,
                'correct_routing': False
            }
            
            with self.lock:
                self.results.append(error_result)
                print(f"❌ {query[:30]:<30} → ERROR: {str(e)}")
            
            return error_result

def run_comprehensive_routing_tests():
    """Run comprehensive multi-threaded routing tests"""
    
    print("🧪 COMPREHENSIVE ROUTING LOGIC TESTING")
    print("=" * 60)
    
    # Test cases covering all routing scenarios
    test_cases = [
        # Customer profile queries (the problematic ones)
        ("who is e.j.price1986@gmail.com", "customer_profile"),
        ("tell me about e.j.price1986@gmail.com", "customer_profile"), 
        ("customer profile for e.j.price1986@gmail.com", "customer_profile"),
        ("profile of client 1747598", "customer_profile"),
        
        # Account status queries (working correctly)
        ("account status for e.j.price1986@gmail.com", "status"),
        ("customer status e.j.price1986@gmail.com", "status"),
        ("subscription status for e.j.price1986@gmail.com", "status"),
        ("is e.j.price1986@gmail.com active", "status"),
        
        # Credit analysis queries
        ("credit score for e.j.price1986@gmail.com", "credit"),
        ("credit report e.j.price1986@gmail.com", "credit"),
        ("experian score for e.j.price1986@gmail.com", "credit"),
        ("utilization rate e.j.price1986@gmail.com", "credit"),
        
        # Transaction queries
        ("transaction history e.j.price1986@gmail.com", "transaction"),
        ("payment history for e.j.price1986@gmail.com", "transaction"),
        ("billing information e.j.price1986@gmail.com", "transaction"),
        
        # Multi-data queries
        ("comprehensive analysis e.j.price1986@gmail.com", "multi_data"),
        ("full analysis e.j.price1986@gmail.com", "multi_data"),
        ("credit and transaction data e.j.price1986@gmail.com", "multi_data"),
        
        # Edge cases
        ("e.j.price1986@gmail.com", "general"),
        ("hello", "general"),
        ("what can you do", "general"),
    ]
    
    tester = RoutingTester()
    
    print(f"🚀 Running {len(test_cases)} routing tests with {min(8, len(test_cases))} threads...")
    print()
    
    # Run tests in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(tester.test_single_query, query, expected)
            for query, expected in test_cases
        ]
        
        # Wait for all tests to complete
        for future in as_completed(futures):
            future.result()  # This will raise any exceptions
    
    print()
    print("📊 ROUTING TEST ANALYSIS")
    print("=" * 60)
    
    # Analyze results
    total_tests = len(tester.results)
    correct_routing = sum(1 for r in tester.results if r.get('correct_routing') == True)
    errors = sum(1 for r in tester.results if r.get('detected_type') == 'ERROR')
    
    print(f"Total Tests: {total_tests}")
    print(f"Correct Routing: {correct_routing}/{total_tests}")
    print(f"Errors: {errors}")
    print()
    
    # Group by detected type
    type_groups = {}
    for result in tester.results:
        detected = result['detected_type']
        if detected not in type_groups:
            type_groups[detected] = []
        type_groups[detected].append(result)
    
    print("🎯 ROUTING DISTRIBUTION:")
    for route_type, results in type_groups.items():
        print(f"  {route_type}: {len(results)} queries")
        for r in results[:3]:  # Show first 3 examples
            print(f"    - {r['query'][:40]}")
        if len(results) > 3:
            print(f"    ... and {len(results) - 3} more")
        print()
    
    # Identify the problematic routing
    print("🚨 PROBLEMATIC ROUTING ANALYSIS:")
    customer_profile_queries = [r for r in tester.results if 'who is' in r['query'] or 'tell me about' in r['query']]
    
    for result in customer_profile_queries:
        print(f"Query: {result['query']}")
        print(f"  Detected Type: {result['detected_type']}")
        print(f"  Prompt Variant: {result.get('prompt_variant', 'unknown')}")
        print(f"  Prompt Source: {result.get('prompt_source', 'unknown')}")
        print(f"  System Prompt Preview: {result.get('system_prompt_preview', 'unknown')}")
        print()
    
    return tester.results

if __name__ == "__main__":
    results = run_comprehensive_routing_tests()
    
    print("🔍 KEY FINDINGS:")
    print("- Check which queries are being routed as 'general' vs expected types")
    print("- Identify which prompt variants are being used for customer profile queries")
    print("- Determine if the issue is routing classification or prompt selection")
