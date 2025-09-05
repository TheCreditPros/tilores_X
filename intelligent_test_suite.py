#!/usr/bin/env python3
"""
Intelligent AI-Powered Test Suite for TLRS API
Uses LLM evaluation instead of rigid keyword matching
"""

import json
import requests
import time
import threading
from datetime import datetime
from typing import Dict, List, Any
import openai
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure OpenAI for evaluation
openai.api_key = os.getenv('OPENAI_API_KEY')

class IntelligentTestEvaluator:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results = []
        self.lock = threading.Lock()
        
    def evaluate_response_quality(self, query: str, response: str, expected_info: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to evaluate if response contains expected information"""
        
        evaluation_prompt = f"""
You are evaluating a customer service AI response for quality and completeness.

CUSTOMER QUERY: "{query}"

AI RESPONSE: "{response}"

EXPECTED INFORMATION CATEGORIES:
{json.dumps(expected_info, indent=2)}

Please evaluate this response and return a JSON object with:
1. "overall_score": 0-100 (how well does this response answer the query?)
2. "contains_customer_data": true/false (does it have real customer information?)
3. "is_helpful": true/false (would this help a customer service agent?)
4. "completeness": 0-100 (how complete is the information provided?)
5. "accuracy": 0-100 (is the information accurate and relevant?)
6. "missing_elements": list of important things that should be included but aren't
7. "strengths": list of what the response does well
8. "overall_assessment": "PASS" or "FAIL" (would you accept this in production?)

Focus on semantic content, not exact keyword matching. A good response should contain relevant customer information and be helpful for the query asked.
"""

        try:
            eval_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": evaluation_prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            eval_content = eval_response.choices[0].message.content
            
            # Try to extract JSON from the response
            if "```json" in eval_content:
                json_start = eval_content.find("```json") + 7
                json_end = eval_content.find("```", json_start)
                json_content = eval_content[json_start:json_end].strip()
            else:
                # Look for JSON-like content
                json_content = eval_content
                
            evaluation = json.loads(json_content)
            return evaluation
            
        except Exception as e:
            print(f"❌ Evaluation error: {e}")
            return {
                "overall_score": 0,
                "contains_customer_data": False,
                "is_helpful": False,
                "completeness": 0,
                "accuracy": 0,
                "missing_elements": ["Evaluation failed"],
                "strengths": [],
                "overall_assessment": "FAIL",
                "error": str(e)
            }

    def test_query(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single query scenario"""
        query = scenario["query"]
        expected = scenario["expected_info"]
        category = scenario["category"]
        
        print(f"🧪 Testing: {query[:60]}...")
        
        try:
            # Make API request
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": query}],
                    "temperature": 0.7
                },
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                return {
                    "query": query,
                    "category": category,
                    "status": "FAIL",
                    "error": f"HTTP {response.status_code}",
                    "response_time": response_time,
                    "evaluation": {"overall_assessment": "FAIL", "overall_score": 0}
                }
            
            api_response = response.json()
            content = api_response["choices"][0]["message"]["content"]
            
            # Use AI to evaluate the response
            evaluation = self.evaluate_response_quality(query, content, expected)
            
            result = {
                "query": query,
                "category": category,
                "status": evaluation["overall_assessment"],
                "response": content,
                "response_time": response_time,
                "evaluation": evaluation,
                "timestamp": datetime.now().isoformat()
            }
            
            with self.lock:
                self.results.append(result)
                
            status_icon = "✅" if evaluation["overall_assessment"] == "PASS" else "❌"
            score = evaluation.get("overall_score", 0)
            print(f"  {status_icon} Score: {score}/100 - {evaluation['overall_assessment']}")
            
            return result
            
        except Exception as e:
            error_result = {
                "query": query,
                "category": category,
                "status": "ERROR",
                "error": str(e),
                "response_time": 0,
                "evaluation": {"overall_assessment": "FAIL", "overall_score": 0},
                "timestamp": datetime.now().isoformat()
            }
            
            with self.lock:
                self.results.append(error_result)
                
            print(f"  ❌ ERROR: {str(e)}")
            return error_result

    def run_test_suite(self, scenarios: List[Dict[str, Any]], max_workers: int = 5) -> Dict[str, Any]:
        """Run the complete test suite with intelligent evaluation"""
        
        print("🧠 INTELLIGENT AI-POWERED TEST SUITE")
        print("=" * 60)
        print(f"📊 Testing {len(scenarios)} scenarios with AI evaluation")
        print()
        
        # Run tests in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_scenario = {executor.submit(self.test_query, scenario): scenario for scenario in scenarios}
            
            for future in as_completed(future_to_scenario):
                try:
                    future.result()
                except Exception as e:
                    print(f"❌ Test execution error: {e}")
        
        # Analyze results
        return self.analyze_results()
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze test results with AI-powered evaluation"""
        
        total_tests = len(self.results)
        if total_tests == 0:
            return {"error": "No test results to analyze"}
        
        # Count passes/fails
        passes = sum(1 for r in self.results if r["evaluation"]["overall_assessment"] == "PASS")
        fails = total_tests - passes
        success_rate = (passes / total_tests) * 100
        
        # Calculate average scores
        scores = [r["evaluation"].get("overall_score", 0) for r in self.results]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Group by category
        categories = {}
        for result in self.results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "passed": 0, "scores": []}
            
            categories[cat]["total"] += 1
            if result["evaluation"]["overall_assessment"] == "PASS":
                categories[cat]["passed"] += 1
            categories[cat]["scores"].append(result["evaluation"].get("overall_score", 0))
        
        # Calculate category success rates
        for cat in categories:
            cat_data = categories[cat]
            cat_data["success_rate"] = (cat_data["passed"] / cat_data["total"]) * 100
            cat_data["avg_score"] = sum(cat_data["scores"]) / len(cat_data["scores"])
        
        # Find common issues
        all_missing = []
        all_strengths = []
        for result in self.results:
            eval_data = result["evaluation"]
            all_missing.extend(eval_data.get("missing_elements", []))
            all_strengths.extend(eval_data.get("strengths", []))
        
        print()
        print("🧠 INTELLIGENT TEST RESULTS")
        print("=" * 60)
        print(f"Overall Success Rate: {success_rate:.1f}% ({passes}/{total_tests})")
        print(f"Average Quality Score: {avg_score:.1f}/100")
        print()
        
        print("📊 Category Breakdown:")
        for cat, data in categories.items():
            status_icon = "✅" if data["success_rate"] >= 80 else "⚠️" if data["success_rate"] >= 60 else "❌"
            print(f"  {status_icon} {cat:<25}: {data['success_rate']:5.1f}% ({data['passed']}/{data['total']}) - Avg Score: {data['avg_score']:.1f}")
        
        print()
        
        # Show failing tests
        failing_tests = [r for r in self.results if r["evaluation"]["overall_assessment"] == "FAIL"]
        if failing_tests:
            print("❌ FAILING TESTS:")
            for test in failing_tests[:5]:  # Show first 5 failures
                print(f"  • {test['query'][:50]}... (Score: {test['evaluation'].get('overall_score', 0)}/100)")
                missing = test['evaluation'].get('missing_elements', [])
                if missing:
                    print(f"    Missing: {', '.join(missing[:3])}")
        
        # Production readiness assessment
        production_ready = success_rate >= 90 and avg_score >= 80
        
        print()
        if production_ready:
            print("🚀 PRODUCTION READY - High success rate and quality scores!")
        else:
            print(f"⚠️  NOT PRODUCTION READY - Need {90 - success_rate:.1f}% more success rate or {80 - avg_score:.1f} more quality points")
        
        return {
            "total_tests": total_tests,
            "passes": passes,
            "fails": fails,
            "success_rate": success_rate,
            "average_score": avg_score,
            "categories": categories,
            "production_ready": production_ready,
            "failing_tests": len(failing_tests),
            "timestamp": datetime.now().isoformat()
        }

def create_client_success_scenarios() -> List[Dict[str, Any]]:
    """Create 50 realistic client success agent scenarios"""
    
    return [
        # Basic Customer Lookup (8 scenarios)
        {
            "query": "Who is e.j.price1986@gmail.com?",
            "category": "Customer Lookup",
            "expected_info": {
                "customer_name": "Should contain customer name",
                "account_status": "Should show account status",
                "basic_info": "Should provide basic customer information"
            }
        },
        {
            "query": "Customer profile for client 1747598",
            "category": "Customer Lookup", 
            "expected_info": {
                "customer_details": "Should provide customer profile information",
                "account_info": "Should include account details"
            }
        },
        {
            "query": "Tell me about Esteban Price",
            "category": "Customer Lookup",
            "expected_info": {
                "customer_info": "Should provide customer information",
                "account_details": "Should include relevant account details"
            }
        },
        {
            "query": "Customer information for e.j.price1986@gmail.com",
            "category": "Customer Lookup",
            "expected_info": {
                "customer_data": "Should provide comprehensive customer information"
            }
        },
        {
            "query": "Profile of client 1747598",
            "category": "Customer Lookup",
            "expected_info": {
                "profile_info": "Should provide customer profile details"
            }
        },
        {
            "query": "Who is client ID 1747598?",
            "category": "Customer Lookup",
            "expected_info": {
                "customer_identification": "Should identify the customer"
            }
        },
        {
            "query": "Customer details for Esteban Price",
            "category": "Customer Lookup",
            "expected_info": {
                "customer_details": "Should provide detailed customer information"
            }
        },
        {
            "query": "Show me information about e.j.price1986@gmail.com",
            "category": "Customer Lookup",
            "expected_info": {
                "customer_info": "Should display customer information"
            }
        },
        
        # Credit Information (12 scenarios)
        {
            "query": "What is the credit score for e.j.price1986@gmail.com?",
            "category": "Credit Analysis",
            "expected_info": {
                "credit_info": "Should discuss credit score or credit-related information",
                "customer_data": "Should reference specific customer data",
                "helpful_response": "Should be helpful for credit inquiries"
            }
        },
        {
            "query": "Show me the Experian credit report for Esteban Price",
            "category": "Credit Analysis",
            "expected_info": {
                "bureau_info": "Should discuss credit bureau information",
                "customer_specific": "Should be specific to the customer"
            }
        },
        {
            "query": "What's the credit utilization for client 1747598?",
            "category": "Credit Analysis",
            "expected_info": {
                "utilization_info": "Should discuss credit utilization",
                "specific_data": "Should provide customer-specific information"
            }
        },
        {
            "query": "Credit report for e.j.price1986@gmail.com",
            "category": "Credit Analysis",
            "expected_info": {
                "credit_report": "Should provide credit report information"
            }
        },
        {
            "query": "TransUnion report for Esteban Price",
            "category": "Credit Analysis",
            "expected_info": {
                "bureau_report": "Should discuss TransUnion credit information"
            }
        },
        {
            "query": "Equifax credit score for client 1747598",
            "category": "Credit Analysis",
            "expected_info": {
                "credit_score": "Should discuss Equifax credit score"
            }
        },
        {
            "query": "Credit history for e.j.price1986@gmail.com",
            "category": "Credit Analysis",
            "expected_info": {
                "credit_history": "Should provide credit history information"
            }
        },
        {
            "query": "What's the current credit status for Esteban Price?",
            "category": "Credit Analysis",
            "expected_info": {
                "credit_status": "Should discuss current credit status"
            }
        },
        {
            "query": "Bureau reports for client 1747598",
            "category": "Credit Analysis",
            "expected_info": {
                "bureau_reports": "Should discuss credit bureau reports"
            }
        },
        {
            "query": "Credit repair progress for e.j.price1986@gmail.com",
            "category": "Credit Analysis",
            "expected_info": {
                "repair_progress": "Should discuss credit repair progress"
            }
        },
        {
            "query": "Latest credit score for Esteban Price",
            "category": "Credit Analysis",
            "expected_info": {
                "latest_score": "Should provide latest credit score information"
            }
        },
        {
            "query": "Credit monitoring status for client 1747598",
            "category": "Credit Analysis",
            "expected_info": {
                "monitoring_status": "Should discuss credit monitoring"
            }
        },
        
        # Payment & Transaction Queries (10 scenarios)
        {
            "query": "When was the last payment for e.j.price1986@gmail.com?",
            "category": "Payment History",
            "expected_info": {
                "payment_info": "Should discuss payment information",
                "customer_data": "Should reference customer account"
            }
        },
        {
            "query": "Payment history for Esteban Price",
            "category": "Payment History",
            "expected_info": {
                "payment_history": "Should provide payment-related information",
                "customer_specific": "Should be specific to customer"
            }
        },
        {
            "query": "What's the billing status for client 1747598?",
            "category": "Payment History",
            "expected_info": {
                "billing_info": "Should discuss billing or payment status",
                "account_status": "Should reference account information"
            }
        },
        {
            "query": "Transaction history for e.j.price1986@gmail.com",
            "category": "Payment History",
            "expected_info": {
                "transaction_history": "Should provide transaction information"
            }
        },
        {
            "query": "When is the next payment due for Esteban Price?",
            "category": "Payment History",
            "expected_info": {
                "payment_due": "Should discuss next payment due date"
            }
        },
        {
            "query": "Payment method for client 1747598",
            "category": "Payment History",
            "expected_info": {
                "payment_method": "Should discuss payment method information"
            }
        },
        {
            "query": "Billing history for e.j.price1986@gmail.com",
            "category": "Payment History",
            "expected_info": {
                "billing_history": "Should provide billing history"
            }
        },
        {
            "query": "Outstanding balance for Esteban Price",
            "category": "Payment History",
            "expected_info": {
                "balance_info": "Should discuss account balance"
            }
        },
        {
            "query": "Payment status for client 1747598",
            "category": "Payment History",
            "expected_info": {
                "payment_status": "Should provide payment status information"
            }
        },
        {
            "query": "Monthly charges for e.j.price1986@gmail.com",
            "category": "Payment History",
            "expected_info": {
                "monthly_charges": "Should discuss monthly charges"
            }
        },
        
        # Account Status Queries (6 scenarios)
        {
            "query": "Is e.j.price1986@gmail.com account active?",
            "category": "Account Status",
            "expected_info": {
                "account_status": "Should clearly indicate account status",
                "customer_specific": "Should be specific to the customer"
            }
        },
        {
            "query": "Account status for client 1747598",
            "category": "Account Status",
            "expected_info": {
                "status_info": "Should provide account status information",
                "clear_answer": "Should clearly answer the status question"
            }
        },
        {
            "query": "Is Esteban Price's account current?",
            "category": "Account Status",
            "expected_info": {
                "account_current": "Should indicate if account is current"
            }
        },
        {
            "query": "Account standing for e.j.price1986@gmail.com",
            "category": "Account Status",
            "expected_info": {
                "account_standing": "Should provide account standing information"
            }
        },
        {
            "query": "Status check for client 1747598",
            "category": "Account Status",
            "expected_info": {
                "status_check": "Should provide status check information"
            }
        },
        {
            "query": "Account health for Esteban Price",
            "category": "Account Status",
            "expected_info": {
                "account_health": "Should discuss account health"
            }
        },
        
        # Service Information (8 scenarios)
        {
            "query": "What services does e.j.price1986@gmail.com have?",
            "category": "Service Information",
            "expected_info": {
                "service_details": "Should describe customer services in detail",
                "product_info": "Should mention products or services",
                "service_description": "Should explain what the service includes"
            }
        },
        {
            "query": "Enrollment date for Esteban Price",
            "category": "Service Information",
            "expected_info": {
                "enrollment_info": "Should provide enrollment information",
                "date_info": "Should include relevant dates"
            }
        },
        {
            "query": "What product is client 1747598 enrolled in?",
            "category": "Service Information",
            "expected_info": {
                "product_enrollment": "Should specify the enrolled product"
            }
        },
        {
            "query": "Service plan for e.j.price1986@gmail.com",
            "category": "Service Information",
            "expected_info": {
                "service_plan": "Should describe the service plan"
            }
        },
        {
            "query": "When did Esteban Price start service?",
            "category": "Service Information",
            "expected_info": {
                "service_start": "Should provide service start date"
            }
        },
        {
            "query": "Product details for client 1747598",
            "category": "Service Information",
            "expected_info": {
                "product_details": "Should provide product details"
            }
        },
        {
            "query": "Service type for e.j.price1986@gmail.com",
            "category": "Service Information",
            "expected_info": {
                "service_type": "Should specify the type of service"
            }
        },
        {
            "query": "Monthly service cost for Esteban Price",
            "category": "Service Information",
            "expected_info": {
                "service_cost": "Should provide monthly service cost"
            }
        },
        
        # Multi-Part & Complex Queries (6 scenarios)
        {
            "query": "Tell me about e.j.price1986@gmail.com and then what is their credit score?",
            "category": "Multi-Part Query",
            "expected_info": {
                "customer_info": "Should provide customer information",
                "credit_info": "Should also address credit score question",
                "comprehensive": "Should handle both parts of the query"
            }
        },
        {
            "query": "Customer info for Esteban Price and their payment status",
            "category": "Multi-Part Query", 
            "expected_info": {
                "customer_details": "Should provide customer information",
                "payment_status": "Should address payment/billing status"
            }
        },
        {
            "query": "Complete overview of e.j.price1986@gmail.com account including credit and payments",
            "category": "Comprehensive Analysis",
            "expected_info": {
                "comprehensive_info": "Should provide detailed account overview",
                "credit_info": "Should include credit information",
                "payment_info": "Should include payment information"
            }
        },
        {
            "query": "Full account summary for client 1747598",
            "category": "Comprehensive Analysis",
            "expected_info": {
                "full_summary": "Should provide complete account summary"
            }
        },
        {
            "query": "Everything about Esteban Price's account",
            "category": "Comprehensive Analysis",
            "expected_info": {
                "complete_info": "Should provide all available account information"
            }
        },
        {
            "query": "Detailed report for e.j.price1986@gmail.com",
            "category": "Comprehensive Analysis",
            "expected_info": {
                "detailed_report": "Should provide detailed account report"
            }
        }
    ]

def main():
    """Run the intelligent test suite"""
    
    # Load environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    # Create test scenarios
    scenarios = create_client_success_scenarios()
    
    # Run intelligent test suite
    evaluator = IntelligentTestEvaluator()
    results = evaluator.run_test_suite(scenarios, max_workers=3)
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"intelligent_test_results_{timestamp}.json"
    
    detailed_results = {
        "summary": results,
        "detailed_results": evaluator.results,
        "test_config": {
            "total_scenarios": len(scenarios),
            "evaluation_method": "AI-powered semantic evaluation",
            "timestamp": timestamp
        }
    }
    
    with open(results_file, 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    # Return success code based on production readiness
    return 0 if results.get("production_ready", False) else 1

if __name__ == "__main__":
    exit(main())
