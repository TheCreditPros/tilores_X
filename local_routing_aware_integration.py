#!/usr/bin/env python3
"""
Local Routing-Aware Integration for UI Testing
Integrates routing-aware manager with production API for local testing
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import production API and routing manager
try:
    from direct_credit_api_fixed import MultiProviderCreditAPI
    PRODUCTION_API_AVAILABLE = True
except ImportError:
    print("⚠️ Production API not available")
    PRODUCTION_API_AVAILABLE = False

try:
    from routing_aware_agenta_manager import RoutingAwareAgentaManager
    ROUTING_MANAGER_AVAILABLE = True
except ImportError:
    print("⚠️ Routing manager not available")
    ROUTING_MANAGER_AVAILABLE = False

class LocalRoutingAwareIntegration:
    """
    Local integration of routing-aware features with production API
    """
    
    def __init__(self):
        """Initialize local integration"""
        self.production_api = MultiProviderCreditAPI() if PRODUCTION_API_AVAILABLE else None
        self.routing_manager = RoutingAwareAgentaManager() if ROUTING_MANAGER_AVAILABLE else None
        
        print("🔧 LocalRoutingAwareIntegration initialized")
        print(f"   - Production API: {'✅' if PRODUCTION_API_AVAILABLE else '❌'}")
        print(f"   - Routing Manager: {'✅' if ROUTING_MANAGER_AVAILABLE else '❌'}")
    
    def process_routing_aware_query(self, query: str, model: str = "gpt-4o-mini", temperature: float = 0.7) -> Dict[str, Any]:
        """
        Process query with routing awareness for UI testing simulation
        """
        if not self.production_api or not self.routing_manager:
            return {
                "success": False,
                "error": "Required components not available"
            }
        
        start_time = datetime.now()
        
        try:
            # 1. Get routing-aware prompt configuration
            routing_config = self.routing_manager.get_routing_aware_prompt_config(query)
            
            # 2. Process query with production API
            response = self.production_api.process_chat_request(query, model, temperature, None)
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
            
            # 3. Create comprehensive result with routing context
            result = {
                "success": True,
                "query": query,
                "response": response,
                "routing_context": routing_config["routing_context"],
                "ui_testing_metadata": routing_config["ui_testing_metadata"],
                "performance": {
                    "response_time_ms": response_time,
                    "response_length": len(response),
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                },
                "agenta_simulation": {
                    "expected_variant": routing_config["ui_testing_metadata"]["expected_variant"],
                    "routing_confidence": routing_config["routing_context"]["confidence_score"],
                    "complexity_level": routing_config["ui_testing_metadata"]["complexity_level"],
                    "enhanced_system_prompt": routing_config.get("enhanced_system_prompt", "")[:200] + "..." if len(routing_config.get("enhanced_system_prompt", "")) > 200 else routing_config.get("enhanced_system_prompt", "")
                }
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "response_time_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
    
    def run_ui_testing_simulation(self, test_queries: List[str]) -> Dict[str, Any]:
        """
        Run comprehensive UI testing simulation
        """
        simulation_results = {
            "simulation_id": f"ui_sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "test_queries": test_queries,
            "results": [],
            "summary": {
                "total_queries": len(test_queries),
                "successful_queries": 0,
                "failed_queries": 0,
                "average_response_time": 0,
                "routing_distribution": {},
                "complexity_distribution": {"low": 0, "medium": 0, "high": 0}
            }
        }
        
        total_response_time = 0
        
        print(f"🧪 Running UI Testing Simulation with {len(test_queries)} queries")
        print("-" * 60)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing: {query[:50]}{'...' if len(query) > 50 else ''}")
            
            result = self.process_routing_aware_query(query)
            simulation_results["results"].append(result)
            
            if result["success"]:
                simulation_results["summary"]["successful_queries"] += 1
                total_response_time += result["performance"]["response_time_ms"]
                
                # Update routing distribution
                route = result["routing_context"]["detected_route"]
                simulation_results["summary"]["routing_distribution"][route] = \
                    simulation_results["summary"]["routing_distribution"].get(route, 0) + 1
                
                # Update complexity distribution
                complexity = result["ui_testing_metadata"]["complexity_level"]
                simulation_results["summary"]["complexity_distribution"][complexity] += 1
                
                print(f"   ✅ Route: {route} | Variant: {result['agenta_simulation']['expected_variant']}")
                print(f"   📊 Response: {result['performance']['response_length']} chars in {result['performance']['response_time_ms']:.0f}ms")
                print(f"   🎯 Confidence: {result['routing_context']['confidence_score']:.2f} | Complexity: {complexity}")
                
            else:
                simulation_results["summary"]["failed_queries"] += 1
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Calculate averages
        if simulation_results["summary"]["successful_queries"] > 0:
            simulation_results["summary"]["average_response_time"] = \
                total_response_time / simulation_results["summary"]["successful_queries"]
        
        return simulation_results
    
    def generate_agenta_ui_instructions(self, simulation_results: Dict[str, Any]) -> str:
        """
        Generate instructions for testing in Agenta.ai UI
        """
        instructions = f"""# Agenta.ai UI Testing Instructions

## Simulation Results Summary
- **Total Queries Tested**: {simulation_results['summary']['total_queries']}
- **Success Rate**: {(simulation_results['summary']['successful_queries'] / simulation_results['summary']['total_queries'] * 100):.1f}%
- **Average Response Time**: {simulation_results['summary']['average_response_time']:.0f}ms

## Routing Distribution
"""
        
        for route, count in simulation_results['summary']['routing_distribution'].items():
            percentage = (count / simulation_results['summary']['total_queries']) * 100
            instructions += f"- **{route}**: {count} queries ({percentage:.1f}%)\n"
        
        instructions += f"""
## Complexity Distribution
- **Low**: {simulation_results['summary']['complexity_distribution']['low']} queries
- **Medium**: {simulation_results['summary']['complexity_distribution']['medium']} queries  
- **High**: {simulation_results['summary']['complexity_distribution']['high']} queries

## UI Testing Steps

### 1. Access Agenta.ai Dashboard
Navigate to: https://cloud.agenta.ai/apps/tilores-x

### 2. Test Each Variant
For each successful query result, test in the corresponding variant:

"""
        
        # Group results by expected variant
        variant_groups = {}
        for result in simulation_results['results']:
            if result['success']:
                variant = result['agenta_simulation']['expected_variant']
                if variant not in variant_groups:
                    variant_groups[variant] = []
                variant_groups[variant].append(result)
        
        for variant, results in variant_groups.items():
            instructions += f"""#### {variant}
**Test Queries**:
"""
            for result in results[:3]:  # Show first 3 queries for each variant
                instructions += f"- {result['query']}\n"
            
            instructions += f"""
**Expected Behavior**:
- Route: {results[0]['routing_context']['detected_route']}
- Response time: ~{results[0]['performance']['response_time_ms']:.0f}ms
- Customer identification: {'✅' if results[0]['ui_testing_metadata']['customer_identified'] else '❌'}

"""
        
        instructions += f"""
### 3. Validation Checklist
For each test query:
- [ ] Correct variant selected automatically
- [ ] Response includes customer identification
- [ ] Appropriate data availability messaging
- [ ] Response time within acceptable range
- [ ] Content matches expected routing context

### 4. A/B Testing Setup
1. Create variant copies with different routing enhancements
2. Test same queries across variants
3. Compare response quality and performance
4. Use ground truth data for validation

## Ground Truth Customer
**Email**: e.j.price1986@gmail.com  
**Name**: Esteban Price  
**Available Data**: Credit ✅, Transactions ✅, Phone ❌  
**Account Status**: Active

Generated: {datetime.now().isoformat()}
"""
        
        return instructions
    
    def export_simulation_results(self, simulation_results: Dict[str, Any], filename: str = None) -> str:
        """Export simulation results to file"""
        if not filename:
            filename = f"ui_simulation_results_{simulation_results['simulation_id']}.json"
        
        with open(filename, 'w') as f:
            json.dump(simulation_results, f, indent=2)
        
        print(f"✅ Simulation results exported to: {filename}")
        return filename
    
    def export_ui_instructions(self, simulation_results: Dict[str, Any], filename: str = None) -> str:
        """Export UI testing instructions to file"""
        if not filename:
            filename = f"agenta_ui_instructions_{simulation_results['simulation_id']}.md"
        
        instructions = self.generate_agenta_ui_instructions(simulation_results)
        
        with open(filename, 'w') as f:
            f.write(instructions)
        
        print(f"✅ UI testing instructions exported to: {filename}")
        return filename

def main():
    """Main function for local routing-aware integration testing"""
    print("🚀 LOCAL ROUTING-AWARE INTEGRATION TESTING")
    print("=" * 60)
    
    integration = LocalRoutingAwareIntegration()
    
    if not integration.production_api or not integration.routing_manager:
        print("❌ Required components not available. Cannot proceed.")
        return
    
    # Test queries that replicate UI testing scenarios
    test_queries = [
        "What is the credit score for e.j.price1986@gmail.com?",
        "What is the account status for e.j.price1986@gmail.com?", 
        "Give me comprehensive analysis for e.j.price1986@gmail.com",
        "Show me payment history for e.j.price1986@gmail.com",
        "How can e.j.price1986@gmail.com improve their credit score?",
        "Compare credit bureaus for e.j.price1986@gmail.com",
        "Show data for invalid@nonexistent.com",
        "",  # Empty query
        "What does TheCreditPros do?",
        "E.J.PRICE1986@GMAIL.COM"  # Mixed case
    ]
    
    # Run simulation
    simulation_results = integration.run_ui_testing_simulation(test_queries)
    
    # Export results
    print(f"\n📊 EXPORTING RESULTS")
    print("-" * 30)
    results_file = integration.export_simulation_results(simulation_results)
    instructions_file = integration.export_ui_instructions(simulation_results)
    
    # Summary
    print(f"\n✅ LOCAL INTEGRATION TESTING COMPLETE")
    print("-" * 40)
    print(f"Success Rate: {(simulation_results['summary']['successful_queries'] / simulation_results['summary']['total_queries'] * 100):.1f}%")
    print(f"Average Response Time: {simulation_results['summary']['average_response_time']:.0f}ms")
    print(f"Results: {results_file}")
    print(f"UI Instructions: {instructions_file}")
    print(f"\n🎯 Ready for Agenta.ai UI testing!")

if __name__ == "__main__":
    main()
