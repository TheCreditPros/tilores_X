#!/usr/bin/env python3
"""
AI-Powered Prompt Optimization System
Analyzes failures and iteratively improves system prompts using natural language
"""

import json
import requests
import time
import openai
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime

class PromptOptimizer:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
    def analyze_failures(self, test_results_file: str) -> Dict[str, Any]:
        """Analyze test failures to identify patterns and improvement opportunities"""
        
        with open(test_results_file, 'r') as f:
            results = json.load(f)
        
        failing_tests = []
        for test in results["detailed_results"]:
            if test["evaluation"]["overall_assessment"] == "FAIL":
                failing_tests.append({
                    "query": test["query"],
                    "category": test["category"],
                    "response": test["response"],
                    "score": test["evaluation"]["overall_score"],
                    "missing_elements": test["evaluation"].get("missing_elements", []),
                    "strengths": test["evaluation"].get("strengths", [])
                })
        
        # Group failures by category
        failure_patterns = {}
        for test in failing_tests:
            category = test["category"]
            if category not in failure_patterns:
                failure_patterns[category] = []
            failure_patterns[category].append(test)
        
        return {
            "total_failures": len(failing_tests),
            "failure_patterns": failure_patterns,
            "overall_success_rate": results["summary"]["success_rate"],
            "category_performance": results["summary"]["categories"]
        }
    
    def generate_prompt_improvements(self, failure_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Use AI to generate improved system prompts based on failure analysis"""
        
        improvement_prompt = f"""
You are an expert AI prompt engineer tasked with improving system prompts for a customer service API.

CURRENT PERFORMANCE:
- Overall Success Rate: {failure_analysis['overall_success_rate']:.1f}%
- Total Failures: {failure_analysis['total_failures']}
- Target: 90%+ success rate

FAILURE ANALYSIS BY CATEGORY:
{json.dumps(failure_analysis['failure_patterns'], indent=2)}

CATEGORY PERFORMANCE:
{json.dumps(failure_analysis['category_performance'], indent=2)}

Your task is to create IMPROVED SYSTEM PROMPTS for each failing category. Focus on:

1. **Natural Language Improvements** - Don't hard-code responses, make the AI smarter
2. **Specific Instructions** - Address the exact missing elements identified in failures
3. **Context Awareness** - Help AI understand what customer service agents need
4. **Data Interpretation** - Guide AI to extract and present information more effectively

For each category with failures, provide:
- **Improved System Prompt**: A natural language prompt that addresses the specific failures
- **Key Improvements**: What specific issues this addresses
- **Expected Impact**: How this should improve success rates

Return a JSON object with category names as keys and improved prompts as values.

Example format:
{{
  "Credit Analysis": {{
    "system_prompt": "You are an expert credit analysis assistant...",
    "key_improvements": ["Addresses missing credit score details", "Better bureau report interpretation"],
    "expected_impact": "Should improve success rate from 83% to 95%+"
  }}
}}

Focus on the categories with the lowest success rates first.
"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": improvement_prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON from response
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                json_content = content
            
            improvements = json.loads(json_content)
            return improvements
            
        except Exception as e:
            print(f"❌ Error generating prompt improvements: {e}")
            return {}
    
    def apply_prompt_improvements(self, improvements: Dict[str, Any]) -> bool:
        """Apply the improved prompts to the API configuration"""
        
        print("🔧 APPLYING PROMPT IMPROVEMENTS")
        print("=" * 50)
        
        # Read current API file
        try:
            with open('direct_credit_api_fixed.py', 'r') as f:
                api_content = f.read()
            
            # Find and update prompt_config section
            prompt_config_start = api_content.find('prompt_config = {')
            if prompt_config_start == -1:
                print("❌ Could not find prompt_config in API file")
                return False
            
            # Find the end of prompt_config
            brace_count = 0
            config_start = prompt_config_start
            config_end = config_start
            
            for i, char in enumerate(api_content[config_start:], config_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        config_end = i + 1
                        break
            
            # Generate new prompt config
            new_prompts = {}
            
            # Map category names to prompt config keys
            category_mapping = {
                "Credit Analysis": "credit",
                "Payment History": "transaction", 
                "Service Information": "status",
                "Comprehensive Analysis": "multi_data",
                "Account Status": "status"
            }
            
            for category, improvement in improvements.items():
                if category in category_mapping:
                    prompt_key = category_mapping[category]
                    new_prompts[prompt_key] = improvement["system_prompt"]
                    print(f"✅ Updated {prompt_key} prompt for {category}")
                    print(f"   Key improvements: {', '.join(improvement['key_improvements'])}")
                    print(f"   Expected impact: {improvement['expected_impact']}")
                    print()
            
            # Build new prompt_config
            new_config = """prompt_config = {
    "general": {
        "system_prompt": "You are a helpful AI assistant providing general information about Tilores credit repair services. Be informative and professional.",
        "temperature": 0.7,
        "max_tokens": 500
    },"""
            
            if "credit" in new_prompts:
                new_config += f'''
    "credit": {{
        "system_prompt": "{new_prompts['credit']}",
        "temperature": 0.7,
        "max_tokens": 1000
    }},'''
            else:
                new_config += '''
    "credit": {
        "system_prompt": "You are a credit analysis AI assistant. Analyze the provided customer data and provide detailed credit information including account status, credit scores, bureau reports, and credit service details. Use bullet points and be specific about credit-related information.",
        "temperature": 0.7,
        "max_tokens": 1000
    },'''
            
            if "transaction" in new_prompts:
                new_config += f'''
    "transaction": {{
        "system_prompt": "{new_prompts['transaction']}",
        "temperature": 0.7,
        "max_tokens": 1000
    }},'''
            else:
                new_config += '''
    "transaction": {
        "system_prompt": "You are a transaction analysis AI assistant. Analyze the provided customer data and provide detailed payment and transaction information including payment history, billing status, and transaction records. Use bullet points and be specific about payment-related information.",
        "temperature": 0.7,
        "max_tokens": 1000
    },'''
            
            if "status" in new_prompts:
                new_config += f'''
    "status": {{
        "system_prompt": "{new_prompts['status']}",
        "temperature": 0.7,
        "max_tokens": 800
    }},'''
            else:
                new_config += '''
    "status": {
        "system_prompt": "You are a customer service AI assistant. Provide clear, accurate account status information based on the customer data provided. Be helpful and professional.",
        "temperature": 0.7,
        "max_tokens": 800
    },'''
            
            if "multi_data" in new_prompts:
                new_config += f'''
    "multi_data": {{
        "system_prompt": "{new_prompts['multi_data']}",
        "temperature": 0.7,
        "max_tokens": 1500
    }}
}}'''
            else:
                new_config += '''
    "multi_data": {
        "system_prompt": "You are a comprehensive data analysis AI assistant. Analyze all provided customer data and provide detailed information across all available data types including credit, transactions, account status, and any other relevant information. Use bullet points and be thorough.",
        "temperature": 0.7,
        "max_tokens": 1500
    }
}'''
            
            # Replace the old config with new config
            new_api_content = api_content[:prompt_config_start] + new_config + api_content[config_end:]
            
            # Write back to file
            with open('direct_credit_api_fixed.py', 'w') as f:
                f.write(new_api_content)
            
            print("✅ Successfully applied prompt improvements to API")
            return True
            
        except Exception as e:
            print(f"❌ Error applying improvements: {e}")
            return False
    
    def create_multi_threaded_scenarios(self) -> List[Dict[str, Any]]:
        """Create complex multi-turn conversation scenarios with temporal comparisons"""
        
        return [
            # Temporal Credit Comparisons
            {
                "conversation": [
                    {"role": "user", "content": "Who is e.j.price1986@gmail.com?"},
                    {"role": "user", "content": "What was their first credit report like?"},
                    {"role": "user", "content": "How does that compare to their most recent credit report?"},
                    {"role": "user", "content": "What improvements have been made?"}
                ],
                "category": "Multi-Turn Credit Analysis",
                "expected_info": {
                    "temporal_comparison": "Should compare first vs latest credit reports",
                    "improvement_tracking": "Should identify specific improvements over time",
                    "context_maintenance": "Should maintain customer context across turns"
                }
            },
            {
                "conversation": [
                    {"role": "user", "content": "Customer profile for Esteban Price"},
                    {"role": "user", "content": "What was their Experian score when they started?"},
                    {"role": "user", "content": "What is it now?"},
                    {"role": "user", "content": "Calculate the improvement"}
                ],
                "category": "Multi-Turn Credit Analysis",
                "expected_info": {
                    "score_tracking": "Should track score changes over time",
                    "calculation": "Should calculate score improvements",
                    "bureau_specific": "Should handle bureau-specific data"
                }
            },
            
            # Payment History Conversations
            {
                "conversation": [
                    {"role": "user", "content": "Payment history for client 1747598"},
                    {"role": "user", "content": "When was their last payment?"},
                    {"role": "user", "content": "How much was it?"},
                    {"role": "user", "content": "Is their account current?"}
                ],
                "category": "Multi-Turn Payment Analysis",
                "expected_info": {
                    "payment_details": "Should provide specific payment information",
                    "account_status": "Should determine current account status",
                    "context_flow": "Should maintain payment context across questions"
                }
            },
            
            # Service Evolution Tracking
            {
                "conversation": [
                    {"role": "user", "content": "What services does e.j.price1986@gmail.com have?"},
                    {"role": "user", "content": "When did they enroll?"},
                    {"role": "user", "content": "How long have they been a customer?"},
                    {"role": "user", "content": "What progress have they made since enrollment?"}
                ],
                "category": "Multi-Turn Service Analysis",
                "expected_info": {
                    "service_timeline": "Should track service timeline",
                    "progress_assessment": "Should evaluate customer progress",
                    "duration_calculation": "Should calculate service duration"
                }
            },
            
            # Complex Multi-Data Conversations
            {
                "conversation": [
                    {"role": "user", "content": "Complete overview of Esteban Price"},
                    {"role": "user", "content": "Focus on their credit improvements"},
                    {"role": "user", "content": "How do their payments correlate with credit changes?"},
                    {"role": "user", "content": "What should they focus on next?"}
                ],
                "category": "Multi-Turn Comprehensive Analysis",
                "expected_info": {
                    "comprehensive_view": "Should provide complete customer overview",
                    "correlation_analysis": "Should correlate payments with credit changes",
                    "recommendations": "Should provide actionable recommendations"
                }
            }
        ]
    
    def test_multi_threaded_conversations(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test multi-turn conversation scenarios"""
        
        print("🧵 MULTI-THREADED CONVERSATION TESTING")
        print("=" * 50)
        
        results = []
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"🗣️  Testing Conversation {i}: {scenario['category']}")
            
            # Build conversation context
            messages = []
            conversation_responses = []
            
            for turn in scenario["conversation"]:
                messages.append(turn)
                
                try:
                    # Make API request with full conversation history
                    response = requests.post(
                        f"{self.base_url}/v1/chat/completions",
                        json={
                            "model": "gpt-4o-mini",
                            "messages": messages.copy(),
                            "temperature": 0.7
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        api_response = response.json()
                        content = api_response["choices"][0]["message"]["content"]
                        
                        # Add assistant response to conversation
                        messages.append({"role": "assistant", "content": content})
                        conversation_responses.append({
                            "query": turn["content"],
                            "response": content
                        })
                        
                        print(f"   Turn {len(conversation_responses)}: {turn['content'][:50]}...")
                        
                    else:
                        print(f"   ❌ API Error: {response.status_code}")
                        break
                        
                except Exception as e:
                    print(f"   ❌ Request Error: {e}")
                    break
            
            # Evaluate the complete conversation
            conversation_evaluation = self.evaluate_conversation(
                scenario["conversation"], 
                conversation_responses, 
                scenario["expected_info"]
            )
            
            results.append({
                "scenario": scenario,
                "responses": conversation_responses,
                "evaluation": conversation_evaluation
            })
            
            status = "✅" if conversation_evaluation["overall_assessment"] == "PASS" else "❌"
            score = conversation_evaluation.get("overall_score", 0)
            print(f"   {status} Conversation Score: {score}/100")
            print()
        
        return self.analyze_conversation_results(results)
    
    def evaluate_conversation(self, conversation: List[Dict], responses: List[Dict], expected_info: Dict) -> Dict[str, Any]:
        """Evaluate a multi-turn conversation using AI"""
        
        conversation_text = ""
        for i, (turn, response) in enumerate(zip(conversation, responses), 1):
            conversation_text += f"Turn {i}:\nUser: {turn['content']}\nAssistant: {response['response']}\n\n"
        
        evaluation_prompt = f"""
Evaluate this multi-turn customer service conversation for quality and effectiveness.

CONVERSATION:
{conversation_text}

EXPECTED CAPABILITIES:
{json.dumps(expected_info, indent=2)}

Rate this conversation on:
1. "overall_score": 0-100 (how well does this conversation flow and provide value?)
2. "context_maintenance": 0-100 (does the AI maintain context across turns?)
3. "information_quality": 0-100 (is the information provided accurate and helpful?)
4. "conversation_flow": 0-100 (does the conversation feel natural and coherent?)
5. "completeness": 0-100 (are all parts of the conversation addressed properly?)
6. "strengths": list of what the conversation does well
7. "weaknesses": list of areas for improvement
8. "overall_assessment": "PASS" or "FAIL" (would this satisfy a customer service agent?)

Return JSON format. Focus on whether this conversation would be helpful for a real customer service scenario.
"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": evaluation_prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                json_content = content
            
            return json.loads(json_content)
            
        except Exception as e:
            return {
                "overall_score": 0,
                "context_maintenance": 0,
                "information_quality": 0,
                "conversation_flow": 0,
                "completeness": 0,
                "strengths": [],
                "weaknesses": [f"Evaluation error: {e}"],
                "overall_assessment": "FAIL"
            }
    
    def analyze_conversation_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze multi-turn conversation test results"""
        
        total_conversations = len(results)
        passed_conversations = sum(1 for r in results if r["evaluation"]["overall_assessment"] == "PASS")
        success_rate = (passed_conversations / total_conversations) * 100 if total_conversations > 0 else 0
        
        avg_scores = {
            "overall": sum(r["evaluation"].get("overall_score", 0) for r in results) / total_conversations,
            "context_maintenance": sum(r["evaluation"].get("context_maintenance", 0) for r in results) / total_conversations,
            "information_quality": sum(r["evaluation"].get("information_quality", 0) for r in results) / total_conversations,
            "conversation_flow": sum(r["evaluation"].get("conversation_flow", 0) for r in results) / total_conversations,
            "completeness": sum(r["evaluation"].get("completeness", 0) for r in results) / total_conversations
        }
        
        print("🧵 MULTI-THREADED CONVERSATION RESULTS")
        print("=" * 50)
        print(f"Success Rate: {success_rate:.1f}% ({passed_conversations}/{total_conversations})")
        print(f"Average Scores:")
        for metric, score in avg_scores.items():
            print(f"  {metric.replace('_', ' ').title()}: {score:.1f}/100")
        
        return {
            "success_rate": success_rate,
            "total_conversations": total_conversations,
            "passed_conversations": passed_conversations,
            "average_scores": avg_scores,
            "detailed_results": results
        }

def main():
    """Run the prompt optimization system"""
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment")
        return 1
    
    optimizer = PromptOptimizer()
    
    # Step 1: Analyze recent test failures
    print("📊 ANALYZING TEST FAILURES...")
    failure_analysis = optimizer.analyze_failures("intelligent_test_results_20250904_192101.json")
    
    print(f"Found {failure_analysis['total_failures']} failures across {len(failure_analysis['failure_patterns'])} categories")
    print()
    
    # Step 2: Generate prompt improvements
    print("🧠 GENERATING PROMPT IMPROVEMENTS...")
    improvements = optimizer.generate_prompt_improvements(failure_analysis)
    
    if not improvements:
        print("❌ Failed to generate improvements")
        return 1
    
    print(f"Generated improvements for {len(improvements)} categories")
    print()
    
    # Step 3: Apply improvements
    if optimizer.apply_prompt_improvements(improvements):
        print("✅ Prompt improvements applied successfully")
        print()
        
        # Step 4: Test multi-threaded conversations
        print("🧵 TESTING MULTI-THREADED CONVERSATIONS...")
        scenarios = optimizer.create_multi_threaded_scenarios()
        conversation_results = optimizer.test_multi_threaded_conversations(scenarios)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"optimization_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "failure_analysis": failure_analysis,
                "improvements_applied": improvements,
                "conversation_results": conversation_results,
                "timestamp": timestamp
            }, f, indent=2)
        
        print(f"📄 Results saved to: {results_file}")
        
        # Return success if conversation success rate is good
        return 0 if conversation_results["success_rate"] >= 80 else 1
    
    else:
        print("❌ Failed to apply prompt improvements")
        return 1

if __name__ == "__main__":
    exit(main())
