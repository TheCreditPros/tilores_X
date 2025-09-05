#!/usr/bin/env python3
"""
Focused test to measure improvement after prompt optimization
Tests first 20 scenarios to avoid timeouts
"""

import json
import requests
import time
import openai
import os
from datetime import datetime
from typing import Dict, Any

# Configure OpenAI for evaluation
openai.api_key = os.getenv('OPENAI_API_KEY')

def evaluate_response_quality(query: str, response: str) -> Dict[str, Any]:
    """Use AI to evaluate if response contains expected information"""

    evaluation_prompt = f"""
You are evaluating a customer service AI response for quality and completeness.

CUSTOMER QUERY: "{query}"

AI RESPONSE: "{response}"

Please evaluate this response and return a JSON object with:
1. "overall_score": 0-100 (how well does this response answer the query?)
2. "contains_customer_data": true/false (does it have real customer information?)
3. "is_helpful": true/false (would this help a customer service agent?)
4. "completeness": 0-100 (how complete is the information provided?)
5. "overall_assessment": "PASS" or "FAIL" (would you accept this in production?)

Focus on semantic content, not exact keyword matching. A good response should contain relevant customer information and be helpful for the query asked.
"""

    try:
        eval_response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": evaluation_prompt}],
            temperature=0.1,
            max_tokens=500
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
            "overall_assessment": "FAIL",
            "error": str(e)
        }

def test_scenarios():
    """Test focused scenarios to measure improvement"""

    scenarios = [
        {"query": "Who is e.j.price1986@gmail.com?", "category": "Customer Lookup"},
        {"query": "Customer profile for client 1747598", "category": "Customer Lookup"},
        {"query": "Tell me about Esteban Price", "category": "Customer Lookup"},
        {"query": "What is the credit score for e.j.price1986@gmail.com?", "category": "Credit Analysis"},
        {"query": "Show me the Experian credit report for Esteban Price", "category": "Credit Analysis"},
        {"query": "Credit report for e.j.price1986@gmail.com", "category": "Credit Analysis"},
        {"query": "Credit repair progress for e.j.price1986@gmail.com", "category": "Credit Analysis"},
        {"query": "Payment history for Esteban Price", "category": "Payment History"},
        {"query": "What's the billing status for client 1747598?", "category": "Payment History"},
        {"query": "Monthly charges for e.j.price1986@gmail.com", "category": "Payment History"},
        {"query": "Is e.j.price1986@gmail.com account active?", "category": "Account Status"},
        {"query": "Account status for client 1747598", "category": "Account Status"},
        {"query": "What services does e.j.price1986@gmail.com have?", "category": "Service Information"},
        {"query": "Enrollment date for Esteban Price", "category": "Service Information"},
        {"query": "Monthly service cost for Esteban Price", "category": "Service Information"},
        {"query": "Complete overview of e.j.price1986@gmail.com account including credit and payments", "category": "Comprehensive Analysis"},
        {"query": "Full account summary for client 1747598", "category": "Comprehensive Analysis"},
        {"query": "Everything about Esteban Price's account", "category": "Comprehensive Analysis"},
        {"query": "Customer info for Esteban Price and their payment status", "category": "Multi-Part Query"},
        {"query": "Detailed report for e.j.price1986@gmail.com", "category": "Comprehensive Analysis"}
    ]

    results = []

    print("🧠 FOCUSED IMPROVEMENT TEST")
    print("=" * 50)
    print(f"📊 Testing {len(scenarios)} scenarios after prompt optimization")
    print()

    for i, scenario in enumerate(scenarios, 1):
        query = scenario["query"]
        category = scenario["category"]

        print(f"🧪 [{i:2d}/20] Testing: {query[:50]}...")

        try:
            # Make API request
            start_time = time.time()
            response = requests.post(
                "http://localhost:8080/v1/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": query}],
                    "temperature": 0.7
                },
                timeout=15  # Shorter timeout
            )
            response_time = time.time() - start_time

            if response.status_code != 200:
                print(f"  ❌ HTTP {response.status_code}")
                results.append({
                    "query": query,
                    "category": category,
                    "status": "FAIL",
                    "error": f"HTTP {response.status_code}",
                    "evaluation": {"overall_assessment": "FAIL", "overall_score": 0}
                })
                continue

            api_response = response.json()
            content = api_response["choices"][0]["message"]["content"]

            # Use AI to evaluate the response
            evaluation = evaluate_response_quality(query, content)

            result = {
                "query": query,
                "category": category,
                "status": evaluation["overall_assessment"],
                "response": content,
                "response_time": response_time,
                "evaluation": evaluation
            }

            results.append(result)

            status_icon = "✅" if evaluation["overall_assessment"] == "PASS" else "❌"
            score = evaluation.get("overall_score", 0)
            print(f"  {status_icon} Score: {score}/100 - {evaluation['overall_assessment']}")

        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            results.append({
                "query": query,
                "category": category,
                "status": "ERROR",
                "error": str(e),
                "evaluation": {"overall_assessment": "FAIL", "overall_score": 0}
            })

    # Analyze results
    total_tests = len(results)
    passes = sum(1 for r in results if r["evaluation"]["overall_assessment"] == "PASS")
    success_rate = (passes / total_tests) * 100

    scores = [r["evaluation"].get("overall_score", 0) for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0

    # Group by category
    categories = {}
    for result in results:
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

    print()
    print("🧠 FOCUSED IMPROVEMENT RESULTS")
    print("=" * 50)
    print(f"Overall Success Rate: {success_rate:.1f}% ({passes}/{total_tests})")
    print(f"Average Quality Score: {avg_score:.1f}/100")
    print()

    print("📊 Category Breakdown:")
    for cat, data in categories.items():
        status_icon = "✅" if data["success_rate"] >= 80 else "⚠️" if data["success_rate"] >= 60 else "❌"
        print(f"  {status_icon} {cat:<25}: {data['success_rate']:5.1f}% ({data['passed']}/{data['total']}) - Avg Score: {data['avg_score']:.1f}")

    # Show failing tests
    failing_tests = [r for r in results if r["evaluation"]["overall_assessment"] == "FAIL"]
    if failing_tests:
        print()
        print("❌ FAILING TESTS:")
        for test in failing_tests[:5]:
            print(f"  • {test['query'][:60]}... (Score: {test['evaluation'].get('overall_score', 0)}/100)")

    # Production readiness assessment
    production_ready = success_rate >= 90 and avg_score >= 80

    print()
    if production_ready:
        print("🚀 PRODUCTION READY - High success rate and quality scores!")
    else:
        needed_success = max(0, 90 - success_rate)
        needed_quality = max(0, 80 - avg_score)
        print(f"⚠️  IMPROVEMENT NEEDED - Need {needed_success:.1f}% more success rate or {needed_quality:.1f} more quality points")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"focused_improvement_results_{timestamp}.json"

    with open(results_file, 'w') as f:
        json.dump({
            "summary": {
                "success_rate": success_rate,
                "average_score": avg_score,
                "total_tests": total_tests,
                "passes": passes,
                "production_ready": production_ready,
                "categories": categories
            },
            "detailed_results": results,
            "timestamp": timestamp
        }, f, indent=2)

    print(f"\n📄 Results saved to: {results_file}")

    return success_rate >= 85  # Return success if we're close to target

if __name__ == "__main__":
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment")
        exit(1)

    success = test_scenarios()
    exit(0 if success else 1)
