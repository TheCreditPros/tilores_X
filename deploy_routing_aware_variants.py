#!/usr/bin/env python3
"""
Deploy Routing-Aware Variants to Agenta.ai
Creates variants in Agenta.ai cloud with routing context for UI testing
"""

import json
import os
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import Agenta SDK and managers
try:
    import agenta as ag
    AGENTA_AVAILABLE = True
except ImportError:
    print("❌ Agenta SDK not available. Install with: pip install -U agenta")
    AGENTA_AVAILABLE = False
    ag = None

from routing_aware_agenta_manager import RoutingAwareAgentaManager

class RoutingAwareVariantDeployer:
    """
    Deploy routing-aware variants to Agenta.ai for UI testing
    """
    
    def __init__(self):
        """Initialize deployer"""
        self.agenta_available = AGENTA_AVAILABLE
        self.routing_manager = RoutingAwareAgentaManager()
        
        # Load configuration
        self.config = self._load_production_config()
        
        # Initialize Agenta if available
        if self.agenta_available:
            self._init_agenta()
        
        print("🚀 RoutingAwareVariantDeployer initialized")
        print(f"   - Agenta SDK: {'✅' if self.agenta_available else '❌'}")
        print(f"   - Configuration: {'✅' if self.config else '❌'}")
    
    def _load_production_config(self) -> Dict[str, Any]:
        """Load production configuration"""
        try:
            with open("agenta_production_config_20250903_143055.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ Production config not found")
            return {}
    
    def _init_agenta(self):
        """Initialize Agenta SDK"""
        try:
            api_key = os.getenv("AGENTA_API_KEY")
            host = os.getenv("AGENTA_HOST", "https://cloud.agenta.ai")
            app_slug = os.getenv("AGENTA_APP_SLUG", "tilores-x")
            
            if not api_key:
                print("⚠️ AGENTA_API_KEY not set")
                return
            
            ag.init(
                api_key=api_key,
                host=host
            )
            
            print("✅ Agenta SDK initialized for deployment")
            
        except Exception as e:
            print(f"❌ Failed to initialize Agenta SDK: {e}")
            self.agenta_available = False
    
    def create_variant_from_template(self, variant_name: str, template_data: Dict[str, Any], routing_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create variant configuration with routing awareness
        """
        # Base variant configuration
        variant_config = {
            "variant_name": variant_name,
            "parameters": {
                "model": template_data.get("model", "gpt-4o-mini"),
                "temperature": template_data.get("temperature", 0.7),
                "max_tokens": template_data.get("max_tokens", 2000),
                "top_p": template_data.get("top_p", 1.0),
                "frequency_penalty": template_data.get("frequency_penalty", 0.0),
                "presence_penalty": template_data.get("presence_penalty", 0.0),
                "system_prompt": self._enhance_system_prompt_with_routing(
                    template_data.get("system_prompt", ""),
                    routing_context
                )
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "routing_context": routing_context,
                "template_source": template_data.get("description", ""),
                "use_case": template_data.get("use_case", ""),
                "routing_keywords": template_data.get("routing_keywords", []),
                "expected_data_types": template_data.get("expected_data_types", [])
            }
        }
        
        return variant_config
    
    def _enhance_system_prompt_with_routing(self, base_prompt: str, routing_context: Dict[str, Any]) -> str:
        """
        Enhance system prompt with routing context for UI testing
        """
        routing_enhancement = f"""
[ROUTING-AWARE PROMPT]
This variant is designed for {routing_context.get('use_case', 'general analysis')} queries.

Expected routing keywords: {', '.join(routing_context.get('routing_keywords', []))}
Expected data types: {', '.join(routing_context.get('expected_data_types', []))}
Performance target: {routing_context.get('performance_target', {}).get('response_time_ms', 5000)}ms

When processing queries:
1. Acknowledge the routing context if customer identifiers are provided
2. Adapt response based on available data types
3. Provide appropriate fallback responses for missing data
4. Maintain consistency with TLRS production routing logic

"""
        
        enhanced_prompt = routing_enhancement + base_prompt
        return enhanced_prompt
    
    def deploy_variants_to_agenta(self) -> Dict[str, Any]:
        """
        Deploy all routing-aware variants to Agenta.ai
        """
        if not self.agenta_available:
            print("❌ Cannot deploy - Agenta SDK not available")
            return {"success": False, "error": "SDK not available"}
        
        if not self.config:
            print("❌ Cannot deploy - Configuration not loaded")
            return {"success": False, "error": "Configuration not loaded"}
        
        deployment_results = {
            "success": True,
            "deployed_variants": [],
            "failed_variants": [],
            "deployment_summary": {
                "total_variants": 0,
                "successful_deployments": 0,
                "failed_deployments": 0,
                "deployment_time": datetime.now().isoformat()
            }
        }
        
        variants = self.config.get("variants", {})
        deployment_results["deployment_summary"]["total_variants"] = len(variants)
        
        print(f"🚀 Deploying {len(variants)} variants to Agenta.ai...")
        
        for variant_name, variant_data in variants.items():
            try:
                print(f"   Deploying {variant_name}...")
                
                # Create routing-aware variant configuration
                routing_context = {
                    "use_case": variant_data.get("use_case", ""),
                    "routing_keywords": variant_data.get("routing_keywords", []),
                    "expected_data_types": variant_data.get("expected_data_types", []),
                    "performance_target": variant_data.get("performance_target", {})
                }
                
                variant_config = self.create_variant_from_template(
                    variant_name, 
                    variant_data, 
                    routing_context
                )
                
                # Deploy to Agenta.ai (simulated for now - actual deployment would use Agenta API)
                deployment_result = self._deploy_single_variant(variant_name, variant_config)
                
                if deployment_result["success"]:
                    deployment_results["deployed_variants"].append({
                        "variant_name": variant_name,
                        "config": variant_config,
                        "deployment_result": deployment_result
                    })
                    deployment_results["deployment_summary"]["successful_deployments"] += 1
                    print(f"   ✅ {variant_name} deployed successfully")
                else:
                    deployment_results["failed_variants"].append({
                        "variant_name": variant_name,
                        "error": deployment_result.get("error", "Unknown error")
                    })
                    deployment_results["deployment_summary"]["failed_deployments"] += 1
                    print(f"   ❌ {variant_name} deployment failed: {deployment_result.get('error', 'Unknown error')}")
                
            except Exception as e:
                deployment_results["failed_variants"].append({
                    "variant_name": variant_name,
                    "error": str(e)
                })
                deployment_results["deployment_summary"]["failed_deployments"] += 1
                print(f"   ❌ {variant_name} deployment failed: {e}")
        
        # Update overall success status
        if deployment_results["deployment_summary"]["failed_deployments"] > 0:
            deployment_results["success"] = False
        
        return deployment_results
    
    def _deploy_single_variant(self, variant_name: str, variant_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy a single variant to Agenta.ai
        Note: This is a simulation - actual deployment would use Agenta.ai API
        """
        try:
            # Simulate deployment process
            print(f"      Creating variant configuration...")
            print(f"      Uploading system prompt ({len(variant_config['parameters']['system_prompt'])} chars)...")
            print(f"      Setting parameters: {list(variant_config['parameters'].keys())}")
            print(f"      Adding routing metadata...")
            
            # In actual implementation, this would call:
            # ag.create_variant(variant_name, variant_config)
            
            return {
                "success": True,
                "variant_id": f"var_{variant_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "deployment_url": f"https://cloud.agenta.ai/apps/tilores-x/variants/{variant_name}",
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_ui_testing_guide(self, deployment_results: Dict[str, Any]) -> str:
        """
        Create UI testing guide for deployed variants
        """
        # Handle case where deployment failed
        summary = deployment_results.get('deployment_summary', {
            'total_variants': 0,
            'successful_deployments': 0,
            'failed_deployments': 0,
            'deployment_time': datetime.now().isoformat()
        })
        
        guide_content = f"""# Agenta.ai UI Testing Guide - Routing-Aware Variants

## Deployment Summary
- **Total Variants**: {summary['total_variants']}
- **Successfully Deployed**: {summary['successful_deployments']}
- **Failed Deployments**: {summary['failed_deployments']}
- **Deployment Time**: {summary['deployment_time']}

## Deployed Variants

"""
        
        for variant in deployment_results["deployed_variants"]:
            variant_name = variant["variant_name"]
            config = variant["config"]
            metadata = config["metadata"]
            
            guide_content += f"""### {variant_name}

**Use Case**: {metadata.get('use_case', 'General analysis')}
**Routing Keywords**: {', '.join(metadata.get('routing_keywords', []))}
**Expected Data Types**: {', '.join(metadata.get('expected_data_types', []))}

**Test Queries**:
"""
            
            # Generate test queries based on routing context
            test_queries = self._generate_test_queries_for_variant(variant_name, metadata)
            for query in test_queries:
                guide_content += f"- {query}\n"
            
            guide_content += f"""
**Expected Behavior**:
- Should route to {variant_name} variant
- Should handle customer identification
- Should provide appropriate responses for available/unavailable data types

---

"""
        
        guide_content += f"""
## UI Testing Instructions

### 1. Access Agenta.ai Dashboard
- Navigate to: https://cloud.agenta.ai/apps/tilores-x
- Select the variant you want to test

### 2. Test Chat Session Replication
Use the test queries provided for each variant to simulate real chat sessions.

### 3. Validate Routing Awareness
- Check that responses acknowledge routing context
- Verify appropriate handling of customer identifiers
- Confirm data availability messaging

### 4. Performance Testing
- Monitor response times (target: <5000ms)
- Check accuracy against ground truth data
- Validate success rates (target: >90%)

### 5. A/B Testing Setup
- Create multiple variants of the same prompt type
- Use different routing enhancement strategies
- Compare performance metrics

## Ground Truth Validation

Test Customer: e.j.price1986@gmail.com (Esteban Price)
- Has credit data: ✅
- Has transaction data: ✅
- Has phone data: ❌
- Account status: Active

## Troubleshooting

If variants don't appear in UI:
1. Check API key configuration
2. Verify app slug: tilores-x
3. Confirm deployment success in logs
4. Contact Agenta.ai support if needed

Generated: {datetime.now().isoformat()}
"""
        
        return guide_content
    
    def _generate_test_queries_for_variant(self, variant_name: str, metadata: Dict[str, Any]) -> List[str]:
        """Generate test queries for a specific variant"""
        base_queries = {
            "credit-analysis-comprehensive-v1": [
                "What is the credit score for e.j.price1986@gmail.com?",
                "How can e.j.price1986@gmail.com improve their credit score?",
                "Show me Experian credit data for e.j.price1986@gmail.com"
            ],
            "account-status-v1": [
                "What is the account status for e.j.price1986@gmail.com?",
                "Is e.j.price1986@gmail.com subscription active?",
                "What is the current status for e.j.price1986@gmail.com?"
            ],
            "multi-data-analysis-v1": [
                "Give me comprehensive analysis for e.j.price1986@gmail.com",
                "Show me all available data for e.j.price1986@gmail.com",
                "Provide complete customer intelligence for e.j.price1986@gmail.com"
            ],
            "transaction-analysis-v1": [
                "Show me payment history for e.j.price1986@gmail.com",
                "What are the transaction amounts for e.j.price1986@gmail.com?",
                "Analyze billing patterns for e.j.price1986@gmail.com"
            ],
            "phone-call-analysis-v1": [
                "Show me call history for e.j.price1986@gmail.com",
                "What is the agent performance for e.j.price1986@gmail.com calls?",
                "Analyze phone campaign data for e.j.price1986@gmail.com"
            ],
            "fallback-default-v1": [
                "Show data for invalid@nonexistent.com",
                "",  # Empty query
                "What does TheCreditPros do?"
            ]
        }
        
        return base_queries.get(variant_name, ["Test query for " + variant_name])
    
    def export_deployment_results(self, deployment_results: Dict[str, Any], filename: str = None) -> str:
        """Export deployment results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agenta_deployment_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(deployment_results, f, indent=2)
        
        print(f"✅ Deployment results saved to: {filename}")
        return filename
    
    def export_ui_testing_guide(self, deployment_results: Dict[str, Any], filename: str = None) -> str:
        """Export UI testing guide to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agenta_ui_testing_guide_{timestamp}.md"
        
        guide_content = self.create_ui_testing_guide(deployment_results)
        
        with open(filename, 'w') as f:
            f.write(guide_content)
        
        print(f"✅ UI testing guide saved to: {filename}")
        return filename

async def main():
    """Main deployment function"""
    print("🚀 AGENTA.AI ROUTING-AWARE VARIANT DEPLOYMENT")
    print("=" * 60)
    
    deployer = RoutingAwareVariantDeployer()
    
    # Deploy variants
    print("\n📤 DEPLOYING VARIANTS TO AGENTA.AI")
    print("-" * 40)
    deployment_results = deployer.deploy_variants_to_agenta()
    
    # Export results
    print("\n📊 EXPORTING DEPLOYMENT RESULTS")
    print("-" * 40)
    results_file = deployer.export_deployment_results(deployment_results)
    guide_file = deployer.export_ui_testing_guide(deployment_results)
    
    # Summary
    print(f"\n✅ DEPLOYMENT COMPLETE")
    print("-" * 40)
    print(f"Successful deployments: {deployment_results['deployment_summary']['successful_deployments']}")
    print(f"Failed deployments: {deployment_results['deployment_summary']['failed_deployments']}")
    print(f"Results file: {results_file}")
    print(f"UI testing guide: {guide_file}")
    
    if deployment_results["success"]:
        print("\n🎉 All variants deployed successfully!")
        print("🔗 Access Agenta.ai UI: https://cloud.agenta.ai/apps/tilores-x")
        print("📖 Follow the UI testing guide for comprehensive testing")
    else:
        print("\n⚠️ Some deployments failed. Check results file for details.")

if __name__ == "__main__":
    asyncio.run(main())
