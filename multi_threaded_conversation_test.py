#!/usr/bin/env python3
"""
Multi-Threaded Conversation Test with Temporal Data Comparisons
Tests complex conversational scenarios like "first vs last credit report"
"""

import json
import requests
import time
import openai
import os
from datetime import datetime
from typing import Dict, Any, List

# Configure OpenAI for evaluation
openai.api_key = os.getenv('OPENAI_API_KEY')

class MultiThreadedConversationTester:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url

    def create_temporal_conversation_scenarios(self) -> List[Dict[str, Any]]:
        """Create multi-turn conversations with temporal data comparisons"""

        return [
            # Temporal Credit Report Comparisons
            {
                "name": "First vs Latest Credit Report Comparison",
                "conversation": [
                    {"role": "user", "content": "Who is e.j.price1986@gmail.com?"},
                    {"role": "user", "content": "What was their first credit report like when they started?"},
                    {"role": "user", "content": "What does their most recent credit report show?"},
                    {"role": "user", "content": "Compare the two - what improvements have been made?"}
                ],
                "expected_outcomes": [
                    "Should identify customer (Esteban Price)",
                    "Should discuss initial credit status/baseline",
                    "Should provide current credit information",
                    "Should compare and highlight improvements over time"
                ]
            },

            # Bureau-Specific Temporal Analysis
            {
                "name": "Experian Score Tracking Over Time",
                "conversation": [
                    {"role": "user", "content": "Customer profile for Esteban Price"},
                    {"role": "user", "content": "What was their Experian credit score when they first enrolled?"},
                    {"role": "user", "content": "What is their current Experian score?"},
                    {"role": "user", "content": "Calculate the point improvement and timeline"}
                ],
                "expected_outcomes": [
                    "Should provide customer profile",
                    "Should reference initial Experian score or baseline",
                    "Should provide current credit information",
                    "Should calculate improvements and provide timeline"
                ]
            },

            # Payment History Evolution
            {
                "name": "Payment Pattern Analysis",
                "conversation": [
                    {"role": "user", "content": "Payment history for client 1747598"},
                    {"role": "user", "content": "When did they make their first payment?"},
                    {"role": "user", "content": "What was their most recent payment?"},
                    {"role": "user", "content": "How consistent have their payments been?"}
                ],
                "expected_outcomes": [
                    "Should provide payment history overview",
                    "Should identify first payment or enrollment date",
                    "Should provide recent payment information",
                    "Should analyze payment consistency patterns"
                ]
            },

            # Service Progress Tracking
            {
                "name": "Credit Repair Progress Timeline",
                "conversation": [
                    {"role": "user", "content": "What services does e.j.price1986@gmail.com have?"},
                    {"role": "user", "content": "When did they start their credit repair program?"},
                    {"role": "user", "content": "How long have they been enrolled?"},
                    {"role": "user", "content": "What measurable progress have they made since starting?"}
                ],
                "expected_outcomes": [
                    "Should describe credit repair services",
                    "Should provide enrollment/start date",
                    "Should calculate service duration",
                    "Should assess progress and improvements made"
                ]
            },

            # Complex Multi-Data Temporal Analysis
            {
                "name": "Comprehensive Progress Assessment",
                "conversation": [
                    {"role": "user", "content": "Complete overview of Esteban Price's account"},
                    {"role": "user", "content": "Focus on their credit score improvements over time"},
                    {"role": "user", "content": "How do their payment patterns correlate with credit changes?"},
                    {"role": "user", "content": "What should be their next steps for continued improvement?"}
                ],
                "expected_outcomes": [
                    "Should provide comprehensive account overview",
                    "Should track credit improvements over time",
                    "Should correlate payments with credit changes",
                    "Should provide actionable next steps"
                ]
            },

            # Bureau Comparison Analysis
            {
                "name": "Multi-Bureau Credit Analysis",
                "conversation": [
                    {"role": "user", "content": "Credit reports for client 1747598"},
                    {"role": "user", "content": "How does their Experian report compare to TransUnion?"},
                    {"role": "user", "content": "Which bureau shows the most improvement?"},
                    {"role": "user", "content": "What accounts for the differences between bureaus?"}
                ],
                "expected_outcomes": [
                    "Should provide credit report information",
                    "Should compare different bureau reports",
                    "Should identify which bureau shows most progress",
                    "Should explain bureau differences"
                ]
            }
        ]

    def conduct_conversation(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct a multi-turn conversation and track context"""

        print(f"🗣️  Testing: {scenario['name']}")

        messages = []
        conversation_log = []

        for i, turn in enumerate(scenario["conversation"], 1):
            messages.append(turn)

            try:
                # Make API request with full conversation history
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    json={
                        "model": "gpt-4o-mini",
                        "messages": messages.copy(),
                        "temperature": 0.7
                    },
                    timeout=20
                )
                response_time = time.time() - start_time

                if response.status_code == 200:
                    api_response = response.json()
                    content = api_response["choices"][0]["message"]["content"]

                    # Add assistant response to conversation
                    messages.append({"role": "assistant", "content": content})

                    conversation_log.append({
                        "turn": i,
                        "user_query": turn["content"],
                        "assistant_response": content,
                        "response_time": response_time,
                        "expected_outcome": scenario["expected_outcomes"][i-1]
                    })

                    print(f"   Turn {i}: {turn['content'][:50]}... ({response_time:.1f}s)")

                else:
                    print(f"   ❌ Turn {i} failed: HTTP {response.status_code}")
                    return {
                        "scenario_name": scenario["name"],
                        "status": "FAILED",
                        "error": f"HTTP {response.status_code} on turn {i}",
                        "conversation_log": conversation_log
                    }

            except Exception as e:
                print(f"   ❌ Turn {i} error: {str(e)}")
                return {
                    "scenario_name": scenario["name"],
                    "status": "FAILED",
                    "error": f"Exception on turn {i}: {str(e)}",
                    "conversation_log": conversation_log
                }

        return {
            "scenario_name": scenario["name"],
            "status": "COMPLETED",
            "conversation_log": conversation_log,
            "total_turns": len(conversation_log)
        }

    def evaluate_conversation_quality(self, conversation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to evaluate the quality of a multi-turn conversation"""

        if conversation_result["status"] != "COMPLETED":
            return {
                "overall_score": 0,
                "context_maintenance": 0,
                "temporal_analysis": 0,
                "information_quality": 0,
                "conversation_flow": 0,
                "overall_assessment": "FAIL",
                "feedback": f"Conversation failed: {conversation_result.get('error', 'Unknown error')}"
            }

        # Build conversation text for evaluation
        conversation_text = f"SCENARIO: {conversation_result['scenario_name']}\n\n"

        for turn in conversation_result["conversation_log"]:
            conversation_text += f"Turn {turn['turn']}:\n"
            conversation_text += f"User: {turn['user_query']}\n"
            conversation_text += f"Assistant: {turn['assistant_response']}\n"
            conversation_text += f"Expected: {turn['expected_outcome']}\n\n"

        evaluation_prompt = f"""
Evaluate this multi-turn customer service conversation for a credit repair service.

{conversation_text}

Rate this conversation on a scale of 0-100 for each criterion:

1. "overall_score": How well does this conversation provide value to a customer service agent?
2. "context_maintenance": Does the AI maintain customer context and conversation flow across turns?
3. "temporal_analysis": Does the AI handle time-based comparisons (first vs latest, improvements over time)?
4. "information_quality": Is the information provided accurate, helpful, and specific?
5. "conversation_flow": Does the conversation feel natural and coherent?

Also provide:
6. "strengths": List what the conversation does well
7. "weaknesses": List areas for improvement
8. "overall_assessment": "PASS" or "FAIL" (would this satisfy a customer service agent?)
9. "feedback": Specific feedback on temporal analysis and multi-turn handling

Return JSON format. Focus on whether this conversation demonstrates good temporal data analysis and context maintenance.
"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": evaluation_prompt}],
                temperature=0.1,
                max_tokens=1000
            )

            content = response.choices[0].message.content

            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                json_content = content

            evaluation = json.loads(json_content)
            return evaluation

        except Exception as e:
            return {
                "overall_score": 0,
                "context_maintenance": 0,
                "temporal_analysis": 0,
                "information_quality": 0,
                "conversation_flow": 0,
                "overall_assessment": "FAIL",
                "feedback": f"Evaluation error: {str(e)}",
                "strengths": [],
                "weaknesses": [f"Could not evaluate: {str(e)}"]
            }

    def run_multi_threaded_test(self) -> Dict[str, Any]:
        """Run the complete multi-threaded conversation test suite"""

        print("🧵 MULTI-THREADED CONVERSATION TEST")
        print("=" * 60)
        print("Testing complex temporal data comparisons and context maintenance")
        print()

        scenarios = self.create_temporal_conversation_scenarios()
        results = []

        for scenario in scenarios:
            # Conduct the conversation
            conversation_result = self.conduct_conversation(scenario)

            # Evaluate the conversation quality
            evaluation = self.evaluate_conversation_quality(conversation_result)

            # Combine results
            full_result = {
                **conversation_result,
                "evaluation": evaluation
            }
            results.append(full_result)

            # Display results
            status_icon = "✅" if evaluation["overall_assessment"] == "PASS" else "❌"
            score = evaluation.get("overall_score", 0)
            context_score = evaluation.get("context_maintenance", 0)
            temporal_score = evaluation.get("temporal_analysis", 0)

            print(f"   {status_icon} Overall: {score}/100 | Context: {context_score}/100 | Temporal: {temporal_score}/100")
            if evaluation.get("feedback"):
                print(f"      💬 {evaluation['feedback'][:80]}...")
            print()

        # Analyze overall results
        return self.analyze_multi_threaded_results(results)

    def analyze_multi_threaded_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the results of multi-threaded conversation tests"""

        total_conversations = len(results)
        completed_conversations = sum(1 for r in results if r["status"] == "COMPLETED")
        passed_conversations = sum(1 for r in results if r["evaluation"]["overall_assessment"] == "PASS")

        completion_rate = (completed_conversations / total_conversations) * 100
        success_rate = (passed_conversations / total_conversations) * 100

        # Calculate average scores
        avg_scores = {}
        score_fields = ["overall_score", "context_maintenance", "temporal_analysis", "information_quality", "conversation_flow"]

        for field in score_fields:
            scores = [r["evaluation"].get(field, 0) for r in results if r["status"] == "COMPLETED"]
            avg_scores[field] = sum(scores) / len(scores) if scores else 0

        print("🧵 MULTI-THREADED CONVERSATION RESULTS")
        print("=" * 60)
        print(f"Completion Rate: {completion_rate:.1f}% ({completed_conversations}/{total_conversations})")
        print(f"Success Rate: {success_rate:.1f}% ({passed_conversations}/{total_conversations})")
        print()

        print("📊 Average Scores:")
        for field, score in avg_scores.items():
            field_name = field.replace('_', ' ').title()
            print(f"  {field_name:<20}: {score:.1f}/100")

        # Show failing conversations
        failing_conversations = [r for r in results if r["evaluation"]["overall_assessment"] == "FAIL"]
        if failing_conversations:
            print()
            print("❌ FAILING CONVERSATIONS:")
            for conv in failing_conversations:
                print(f"  • {conv['scenario_name']}")
                if conv["evaluation"].get("weaknesses"):
                    print(f"    Issues: {', '.join(conv['evaluation']['weaknesses'][:2])}")

        # Production readiness for multi-threaded conversations
        multi_threaded_ready = success_rate >= 80 and avg_scores.get("context_maintenance", 0) >= 75 and avg_scores.get("temporal_analysis", 0) >= 70

        print()
        if multi_threaded_ready:
            print("🚀 MULTI-THREADED READY - Good conversation handling and temporal analysis!")
        else:
            print(f"⚠️  MULTI-THREADED NEEDS WORK - Success: {success_rate:.1f}%, Context: {avg_scores.get('context_maintenance', 0):.1f}%, Temporal: {avg_scores.get('temporal_analysis', 0):.1f}%")

        return {
            "total_conversations": total_conversations,
            "completion_rate": completion_rate,
            "success_rate": success_rate,
            "average_scores": avg_scores,
            "multi_threaded_ready": multi_threaded_ready,
            "detailed_results": results
        }

def main():
    """Run the multi-threaded conversation test"""

    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment")
        return 1

    tester = MultiThreadedConversationTester()
    results = tester.run_multi_threaded_test()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"multi_threaded_results_{timestamp}.json"

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Detailed results saved to: {results_file}")

    # Return success if multi-threaded conversations are working well
    return 0 if results.get("multi_threaded_ready", False) else 1

if __name__ == "__main__":
    exit(main())
