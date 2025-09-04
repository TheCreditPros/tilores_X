#!/usr/bin/env python3
"""
Conversational Validation Test - Multi-Turn Conversation Testing
Tests the system's ability to handle conversational context and follow-up queries
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple

class ConversationalValidator:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results = []
        
        # Multi-turn conversation scenarios
        self.conversation_scenarios = [
            {
                "name": "Basic Customer Identification Flow",
                "turns": [
                    {
                        "user": "who is e.j.price1986@gmail.com",
                        "expected_contains": ["Status:", "Customer:", "Esteban Price", "Active"],
                        "expected_not_contains": ["No customer records found"]
                    },
                    {
                        "user": "what is their credit score",
                        "expected_contains": ["Status:", "Customer:", "Esteban Price"],
                        "expected_not_contains": ["I need customer information"]
                    },
                    {
                        "user": "show me their transaction history",
                        "expected_contains": ["Status:", "Customer:", "Esteban Price"],
                        "expected_not_contains": ["I need customer information"]
                    }
                ]
            },
            {
                "name": "Client ID Context Flow",
                "turns": [
                    {
                        "user": "account status for client 1747598",
                        "expected_contains": ["Status:", "Active", "Esteban Price"],
                        "expected_not_contains": ["No customer records found"]
                    },
                    {
                        "user": "what about their credit report",
                        "expected_contains": ["Status:", "Customer:", "Esteban Price"],
                        "expected_not_contains": ["I need customer information"]
                    },
                    {
                        "user": "their latest billing information",
                        "expected_contains": ["Status:", "Customer:", "Esteban Price"],
                        "expected_not_contains": ["I need customer information"]
                    }
                ]
            },
            {
                "name": "Mixed Pronoun References",
                "turns": [
                    {
                        "user": "customer profile for e.j.price1986@gmail.com",
                        "expected_contains": ["Status:", "Customer:", "Esteban Price"],
                        "expected_not_contains": ["No customer records found"]
                    },
                    {
                        "user": "what is his current status",
                        "expected_contains": ["Status:", "Active", "Esteban Price"],
                        "expected_not_contains": ["I need customer information"]
                    },
                    {
                        "user": "show me his credit analysis",
                        "expected_contains": ["Status:", "Customer:", "Esteban Price"],
                        "expected_not_contains": ["I need customer information"]
                    }
                ]
            },
            {
                "name": "Non-existent Customer Context",
                "turns": [
                    {
                        "user": "who is john.doe@example.com",
                        "expected_contains": ["No customer records found"],
                        "expected_not_contains": ["Status:", "Active"]
                    },
                    {
                        "user": "what about their credit score",
                        "expected_contains": ["No customer records found"],
                        "expected_not_contains": ["Status:", "Active"]
                    }
                ]
            },
            {
                "name": "Context Switch Between Customers",
                "turns": [
                    {
                        "user": "who is e.j.price1986@gmail.com",
                        "expected_contains": ["Status:", "Customer:", "Esteban Price"],
                        "expected_not_contains": ["No customer records found"]
                    },
                    {
                        "user": "what about client 999888",
                        "expected_contains": ["No customer records found"],
                        "expected_not_contains": ["Esteban Price", "Active"]
                    },
                    {
                        "user": "back to e.j.price1986@gmail.com status",
                        "expected_contains": ["Status:", "Customer:", "Esteban Price"],
                        "expected_not_contains": ["No customer records found"]
                    }
                ]
            },
            {
                "name": "Complex Contextual Queries",
                "turns": [
                    {
                        "user": "information about client 1747598",
                        "expected_contains": ["Status:", "Customer:", "Esteban Price"],
                        "expected_not_contains": ["No customer records found"]
                    },
                    {
                        "user": "compare their newest vs second newest experian report",
                        "expected_contains": ["Status:", "Customer:", "Esteban Price"],
                        "expected_not_contains": ["I need customer information"]
                    },
                    {
                        "user": "what changed in this customer's credit profile",
                        "expected_contains": ["Status:", "Customer:", "Esteban Price"],
                        "expected_not_contains": ["I need customer information"]
                    }
                ]
            }
        ]

    def test_conversation_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test a complete conversation scenario"""
        print(f"\n🗣️  Testing: {scenario['name']}")
        
        conversation_messages = []
        turn_results = []
        scenario_success = True
        
        for i, turn in enumerate(scenario['turns']):
            print(f"   Turn {i+1}: {turn['user'][:50]}...")
            
            # Add user message to conversation
            conversation_messages.append({
                "role": "user",
                "content": turn['user']
            })
            
            # Send request with full conversation history
            turn_result = self.send_conversation_request(conversation_messages, turn)
            turn_results.append(turn_result)
            
            if turn_result['success']:
                # Add assistant response to conversation history
                conversation_messages.append({
                    "role": "assistant", 
                    "content": turn_result['response']
                })
                print(f"      ✅ Turn {i+1} passed")
            else:
                scenario_success = False
                print(f"      ❌ Turn {i+1} failed: {turn_result['issues']}")
        
        return {
            "scenario_name": scenario['name'],
            "success": scenario_success,
            "total_turns": len(scenario['turns']),
            "successful_turns": sum(1 for r in turn_results if r['success']),
            "turn_results": turn_results,
            "conversation_messages": conversation_messages
        }

    def send_conversation_request(self, messages: List[Dict], expected: Dict) -> Dict[str, Any]:
        """Send a conversation request and validate response"""
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": messages
                },
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                assistant_response = response_data["choices"][0]["message"]["content"]
                
                validation_result = self.validate_conversational_response(
                    assistant_response, expected
                )
                
                return {
                    "user_message": messages[-1]["content"],
                    "response": assistant_response,
                    "response_time": response_time,
                    "validation": validation_result,
                    "success": validation_result["passed"],
                    "issues": validation_result["issues"]
                }
            else:
                return {
                    "user_message": messages[-1]["content"],
                    "response": f"HTTP {response.status_code}",
                    "response_time": response_time,
                    "validation": {"passed": False, "issues": ["HTTP_ERROR"]},
                    "success": False,
                    "issues": ["HTTP_ERROR"]
                }
                
        except Exception as e:
            return {
                "user_message": messages[-1]["content"],
                "response": f"ERROR: {str(e)}",
                "response_time": 0,
                "validation": {"passed": False, "issues": ["EXCEPTION"]},
                "success": False,
                "issues": ["EXCEPTION"]
            }

    def validate_conversational_response(self, response: str, expected: Dict) -> Dict[str, Any]:
        """Validate conversational response"""
        issues = []
        passed = True
        
        # Check required content
        for required in expected.get("expected_contains", []):
            if required not in response:
                issues.append(f"MISSING_REQUIRED: {required}")
                passed = False
        
        # Check prohibited content
        for prohibited in expected.get("expected_not_contains", []):
            if prohibited in response:
                issues.append(f"CONTAINS_PROHIBITED: {prohibited}")
                passed = False
        
        # Check response length
        if len(response) < 20:
            issues.append("RESPONSE_TOO_SHORT")
            passed = False
        
        return {
            "passed": passed,
            "issues": issues,
            "response_length": len(response)
        }

    def run_conversational_validation(self) -> Dict[str, Any]:
        """Run comprehensive conversational validation"""
        print("🗣️  Starting Conversational Validation Test")
        print("=" * 60)
        print("Testing multi-turn conversations and context management")
        print()
        
        scenario_results = []
        total_scenarios = len(self.conversation_scenarios)
        successful_scenarios = 0
        total_turns = 0
        successful_turns = 0
        
        for scenario in self.conversation_scenarios:
            result = self.test_conversation_scenario(scenario)
            scenario_results.append(result)
            
            total_turns += result['total_turns']
            successful_turns += result['successful_turns']
            
            if result['success']:
                successful_scenarios += 1
                print(f"   ✅ Scenario passed: {result['successful_turns']}/{result['total_turns']} turns")
            else:
                print(f"   ❌ Scenario failed: {result['successful_turns']}/{result['total_turns']} turns")
        
        # Calculate success rates
        scenario_success_rate = (successful_scenarios / total_scenarios) * 100
        turn_success_rate = (successful_turns / total_turns) * 100
        
        # Print summary
        print("\n" + "=" * 60)
        print("🗣️  CONVERSATIONAL VALIDATION RESULTS")
        print("=" * 60)
        print(f"Scenario Success Rate: {scenario_success_rate:.1f}% ({successful_scenarios}/{total_scenarios})")
        print(f"Turn Success Rate: {turn_success_rate:.1f}% ({successful_turns}/{total_turns})")
        print()
        
        for result in scenario_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['scenario_name']:35s}: {result['successful_turns']}/{result['total_turns']} turns")
        
        overall_success = scenario_success_rate >= 90 and turn_success_rate >= 90
        
        return {
            "overall_success": overall_success,
            "scenario_success_rate": scenario_success_rate,
            "turn_success_rate": turn_success_rate,
            "total_scenarios": total_scenarios,
            "successful_scenarios": successful_scenarios,
            "total_turns": total_turns,
            "successful_turns": successful_turns,
            "scenario_results": scenario_results,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

def main():
    validator = ConversationalValidator()
    results = validator.run_conversational_validation()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"conversational_validation_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: conversational_validation_{timestamp}.json")
    
    if results["overall_success"]:
        print("\n🎉 SUCCESS! Conversational context is working properly!")
    else:
        print(f"\n⚠️  Conversational issues detected:")
        print(f"   - Scenario success: {results['scenario_success_rate']:.1f}%")
        print(f"   - Turn success: {results['turn_success_rate']:.1f}%")

if __name__ == "__main__":
    main()
