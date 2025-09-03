#!/usr / bin / env python3
"""
Agenta Evaluation Framework

Core testing engine that provides field - level accuracy scoring, LLM judge integration,
and multi - variant testing capabilities for Agenta.ai prompt optimization.
"""

import json
import os
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from difflib import SequenceMatcher
import statistics


class AgentaEvaluationFramework:
    """Core evaluation framework for Agenta.ai prompt variant testing"""

    def __init__(self, config_file: str = None):
        """Initialize the evaluation framework"""
        self.config = self._load_config(config_file)
        self.field_weights = self.config.get('field_weights', {})
        self.tolerance_settings = self.config.get('tolerance_settings', {})
        self.promotion_rules = self.config.get('promotion_rules', {})

        # Environment configuration
        self.agenta_api_key = os.getenv("AGENTA_API_KEY")
        self.judge_base_url = os.getenv("JUDGE_BASE_URL", "https://api.openai.com / v1")
        self.judge_api_key = os.getenv("JUDGE_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.judge_model = os.getenv("JUDGE_MODEL", "gpt - 4o - mini")

        # Variant endpoints (to be configured)
        self.variant_endpoints = {
            "baseline": os.getenv("APP_URL_BASELINE"),
            "challenger": os.getenv("APP_URL_CHALLENGER")
        }

        print("🎯 Agenta Evaluation Framework Initialized")
        print(f"  - API Key: {'✅ Set' if self.agenta_api_key else '❌ Missing'}")
        print(f"  - Judge Model: {self.judge_model}")
        print(f"  - Field Weights: {len(self.field_weights)} configured")
        print(f"  - Variants: {list(self.variant_endpoints.keys())}")

    def _load_config(self, config_file: str = None) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            "field_weights": {
                # Exact Match Fields (Weight 3.0)
                "customer_name": 3.0,
                "customer_email": 3.0,
                "client_id": 3.0,
                "entity_id": 3.0,
                "total_credit_reports": 3.0,
                "total_transactions": 3.0,

                # Numeric Tolerance Fields (Weight 2.0)
                "latest_credit_score": 2.0,
                "total_transaction_amount": 2.0,
                "average_transaction_amount": 2.0,
                "contact_records_count": 2.0,
                "total_cards": 2.0,

                # Boolean Fields (Weight 2.0)
                "has_credit_data": 2.0,
                "has_transaction_data": 2.0,
                "has_phone_data": 2.0,
                "has_card_data": 2.0,
                "customer_found": 2.0,
                "data_available": 2.0,

                # Categorical Fields (Weight 2.0)
                "risk_level": 2.0,
                "credit_bureau": 2.0,
                "account_status": 2.0,

                # Free Text Fields (Weight 1.0)
                "explanation": 1.0,
                "risk_assessment": 1.0,
                "analysis_summary": 1.0
            },
            "tolerance_settings": {
                "numeric_percent": 0.02,  # ±2%
                "numeric_absolute": 5.0,  # ±5 points for scores
                "similarity_threshold": 0.85  # 85% similarity for LLM judge bypass
            },
            "promotion_rules": {
                "min_score_improvement": 0.03,  # 3% improvement required
                "max_latency_increase": 0.10,   # Max 10% latency increase
                "min_test_cases": 5             # Minimum test cases for promotion
            }
        }

        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                # Merge user config with defaults
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in default_config:
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
            except Exception as e:
                print(f"⚠️ Error loading config file: {e}, using defaults")

        return default_config

    def call_agenta_variant(self, endpoint: str, inputs: Dict) -> Dict:
        """Call an Agenta variant endpoint"""
        if not endpoint:
            raise ValueError("Endpoint not configured")

        headers = {
            "Authorization": f"Bearer {self.agenta_api_key}",
            "Content - Type": "application / json"
        }

        payload = {"inputs": inputs}

        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Agenta API call failed: {e}")

    def call_llm_judge(self, expected_text: str, model_text: str) -> Tuple[float, str]:
        """Call LLM judge for free - text evaluation"""
        system_prompt = """You are an objective evaluator for credit analysis responses.
Given EXPECTED (ground truth) and MODEL outputs, evaluate factual alignment.

Focus on:
- Factual accuracy of data points
- Completeness of required information
- Professional tone and clarity
- Absence of hallucinations

Penalize:
- Incorrect data values
- Missing key information
- Unprofessional language
- Unsupported claims

Return JSON with:
- "score": 0.0 - 1.0 (0.0=completely wrong, 1.0=perfect match)
- "rationale": brief explanation of score"""

        user_prompt = """EXPECTED:
{expected_text}

MODEL:
{model_text}

Return compact JSON evaluation."""

        try:
            headers = {
                "Authorization": f"Bearer {self.judge_api_key}",
                "Content - Type": "application / json"
            }

            payload = {
                "model": self.judge_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.0
            }

            response = requests.post(
                f"{self.judge_base_url}/chat / completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Parse JSON response
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                judge_result = json.loads(content[start:end + 1])
                score = float(judge_result.get("score", 0.0))
                rationale = judge_result.get("rationale", "")
                return score, rationale
            else:
                # Fallback to similarity if JSON parsing fails
                similarity = SequenceMatcher(None, str(expected_text), str(model_text)).ratio()
                return similarity, "judge_parse_fallback_similarity"

        except Exception as e:
            print(f"⚠️ LLM judge failed: {e}, using similarity fallback")
            similarity = SequenceMatcher(None, str(expected_text), str(model_text)).ratio()
            return similarity, f"judge_error_fallback: {str(e)[:50]}"

    def try_parse_json_response(self, response: Any) -> Dict:
        """Try to parse model response as JSON"""
        if isinstance(response, dict):
            return response

        if isinstance(response, list):
            return {"_list": response}

        text = response if isinstance(response, str) else json.dumps(response)

        # Try to extract JSON block
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass

        # Fallback: return as text
        return {"_text": text.strip()}

    def score_field(self, field_name: str, expected: Any, actual: Any) -> Tuple[float, str]:
        """Score a single field comparison"""
        weight = self.field_weights.get(field_name, 1.0)

        # Handle missing values
        if expected is None and actual is None:
            return 1.0, "both_null"
        if expected is None or actual is None:
            return 0.0, "missing_value"

        # Free text fields - use LLM judge or similarity
        if field_name in ["explanation", "risk_assessment", "analysis_summary"]:
            # Quick similarity check first
            similarity = SequenceMatcher(None, str(expected), str(actual)).ratio()

            if similarity >= self.tolerance_settings.get("similarity_threshold", 0.85):
                return similarity, "high_similarity_bypass"
            else:
                # Use LLM judge for low similarity
                score, rationale = self.call_llm_judge(str(expected), str(actual))
                return score, f"llm_judge: {rationale}"

        # Numeric fields with tolerance
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            if expected == 0:
                score = 1.0 if abs(actual) < 0.01 else 0.0
            else:
                rel_error = abs(actual - expected) / abs(expected)
                abs_error = abs(actual - expected)

                # Check both relative and absolute tolerance
                rel_tolerance = self.tolerance_settings.get("numeric_percent", 0.02)
                abs_tolerance = self.tolerance_settings.get("numeric_absolute", 5.0)

                if rel_error <= rel_tolerance or abs_error <= abs_tolerance:
                    score = 1.0
                else:
                    # Gradual penalty for larger errors
                    score = max(0.0, 1.0 - min(1.0, rel_error))

            return score, f"numeric_tolerance (rel: {rel_error:.3f}, abs: {abs_error:.1f})"

        # List / array fields - Jaccard similarity
        if isinstance(expected, list) and isinstance(actual, list):
            expected_set = set(str(x) for x in expected)
            actual_set = set(str(x) for x in actual)

            intersection = len(expected_set & actual_set)
            union = len(expected_set | actual_set)

            score = intersection / union if union > 0 else 1.0
            return score, f"jaccard_similarity ({intersection}/{union})"

        # String / categorical fields
        expected_str = str(expected).strip().lower()
        actual_str = str(actual).strip().lower()

        if expected_str == actual_str:
            return 1.0, "exact_match"
        else:
            # Use string similarity for partial credit
            similarity = SequenceMatcher(None, expected_str, actual_str).ratio()
            return similarity, f"string_similarity ({similarity:.3f})"

    def score_record(self, expected: Dict, actual: Dict) -> Tuple[float, List[Dict]]:
        """Score a complete record comparison"""
        total_weight = sum(self.field_weights.values())
        weighted_score = 0.0
        field_breakdown = []

        # Score each field that has a weight
        for field_name, weight in self.field_weights.items():
            expected_value = expected.get(field_name)
            actual_value = actual.get(field_name)

            field_score, rationale = self.score_field(field_name, expected_value, actual_value)

            weighted_score += weight * field_score

            field_breakdown.append({
                "field": field_name,
                "weight": weight,
                "expected": expected_value,
                "actual": actual_value,
                "score": field_score,
                "rationale": rationale
            })

        overall_score = weighted_score / total_weight if total_weight > 0 else 0.0

        return round(overall_score, 4), field_breakdown

    def evaluate_test_case(self, test_case: Dict) -> Dict:
        """Evaluate a single test case against all variants"""
        case_id = test_case.get("id", "unknown")
        inputs = test_case.get("inputs", {})
        expected = test_case.get("expected", {})

        results = []

        for variant_name, endpoint in self.variant_endpoints.items():
            if not endpoint:
                print(f"⚠️ Skipping variant {variant_name}: endpoint not configured")
                continue

            start_time = time.time()

            try:
                # Call Agenta variant
                response = self.call_agenta_variant(endpoint, inputs)
                latency = time.time() - start_time

                # Parse response
                parsed_response = self.try_parse_json_response(response)

                # Score the response
                overall_score, field_breakdown = self.score_record(expected, parsed_response)

                results.append({
                    "case_id": case_id,
                    "variant": variant_name,
                    "latency_s": round(latency, 3),
                    "overall_score": overall_score,
                    "field_breakdown": field_breakdown,
                    "raw_response": response,
                    "parsed_response": parsed_response,
                    "success": True
                })

            except Exception as e:
                results.append({
                    "case_id": case_id,
                    "variant": variant_name,
                    "latency_s": None,
                    "overall_score": 0.0,
                    "field_breakdown": [],
                    "error": str(e),
                    "success": False
                })

        return {
            "case_id": case_id,
            "inputs": inputs,
            "expected": expected,
            "results": results
        }

    def evaluate_test_suite(self, test_cases: List[Dict]) -> Dict:
        """Evaluate a complete test suite"""
        print(f"🚀 Evaluating {len(test_cases)} test cases...")

        all_results = []
        variant_summaries = {}

        for i, test_case in enumerate(test_cases, 1):
            print(f"  📝 Test case {i}/{len(test_cases)}: {test_case.get('id', 'unknown')}")

            case_result = self.evaluate_test_case(test_case)
            all_results.append(case_result)

            # Aggregate results by variant
            for result in case_result["results"]:
                variant = result["variant"]
                if variant not in variant_summaries:
                    variant_summaries[variant] = {
                        "scores": [],
                        "latencies": [],
                        "successes": 0,
                        "failures": 0
                    }

                if result["success"]:
                    variant_summaries[variant]["scores"].append(result["overall_score"])
                    variant_summaries[variant]["latencies"].append(result["latency_s"])
                    variant_summaries[variant]["successes"] += 1
                else:
                    variant_summaries[variant]["failures"] += 1

        # Calculate summary statistics
        summary_stats = {}
        for variant, data in variant_summaries.items():
            scores = data["scores"]
            latencies = [l for item in data["latencies"] if l is not None]

            summary_stats[variant] = {
                "test_cases": len(test_cases),
                "successes": data["successes"],
                "failures": data["failures"],
                "success_rate": data["successes"] / len(test_cases) if test_cases else 0.0,
                "avg_score": statistics.mean(scores) if scores else 0.0,
                "median_score": statistics.median(scores) if scores else 0.0,
                "min_score": min(scores) if scores else 0.0,
                "max_score": max(scores) if scores else 0.0,
                "avg_latency_s": statistics.mean(latencies) if latencies else None,
                "p90_latency_s": sorted(latencies)[int(0.9 * len(latencies))] if latencies else None,
                "p95_latency_s": sorted(latencies)[int(0.95 * len(latencies))] if latencies else None
            }

        return {
            "metadata": {
                "evaluation_timestamp": datetime.now().isoformat(),
                "total_test_cases": len(test_cases),
                "total_variants": len(self.variant_endpoints),
                "config": self.config
            },
            "detailed_results": all_results,
            "summary_statistics": summary_stats
        }

    def check_promotion_rules(self, evaluation_results: Dict) -> Dict:
        """Check if challenger meets promotion criteria"""
        summary_stats = evaluation_results.get("summary_statistics", {})

        baseline_stats = summary_stats.get("baseline")
        challenger_stats = summary_stats.get("challenger")

        if not baseline_stats or not challenger_stats:
            return {
                "promote": False,
                "reason": "Missing baseline or challenger results"
            }

        # Check minimum test cases
        min_cases = self.promotion_rules.get("min_test_cases", 5)
        if baseline_stats["test_cases"] < min_cases:
            return {
                "promote": False,
                "reason": f"Insufficient test cases ({baseline_stats['test_cases']} < {min_cases})"
            }

        # Check score improvement
        score_improvement = challenger_stats["avg_score"] - baseline_stats["avg_score"]
        min_improvement = self.promotion_rules.get("min_score_improvement", 0.03)

        if score_improvement < min_improvement:
            return {
                "promote": False,
                "reason": f"Insufficient score improvement ({score_improvement:.4f} < {min_improvement})",
                "score_improvement": score_improvement
            }

        # Check latency increase
        if baseline_stats["avg_latency_s"] and challenger_stats["avg_latency_s"]:
            latency_increase = (challenger_stats["avg_latency_s"] - baseline_stats["avg_latency_s"]) / baseline_stats["avg_latency_s"]
            max_latency_increase = self.promotion_rules.get("max_latency_increase", 0.10)

            if latency_increase > max_latency_increase:
                return {
                    "promote": False,
                    "reason": f"Excessive latency increase ({latency_increase:.2%} > {max_latency_increase:.2%})",
                    "latency_increase": latency_increase
                }

        return {
            "promote": True,
            "reason": "All promotion criteria met",
            "score_improvement": score_improvement,
            "baseline_score": baseline_stats["avg_score"],
            "challenger_score": challenger_stats["avg_score"]
        }

    def save_results(self, results: Dict, output_file: str = None) -> str:
        """Save evaluation results to file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"tests / agenta / evaluation_results_{timestamp}.json"

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf - 8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        print(f"✅ Results saved to: {output_file}")
        return output_file


def main():
    """Main execution for testing"""
    print("🚀 AGENTA EVALUATION FRAMEWORK")
    print("=" * 50)

    # Initialize framework
    framework = AgentaEvaluationFramework()

    # Example test case
    example_test_case = {
        "id": "example_test",
        "inputs": {
            "customer_id": "e.j.price1986@gmail.com",
            "query": "What is the account status?"
        },
        "expected": {
            "customer_found": True,
            "customer_name": "Esteban Price",
            "client_id": "1747598",
            "has_credit_data": True,
            "explanation": "Customer found with complete data"
        }
    }

    print("\n📝 Example evaluation (requires configured endpoints):")
    print(f"Test case: {example_test_case['id']}")

    if framework.variant_endpoints.get("baseline"):
        try:
            result = framework.evaluate_test_case(example_test_case)
            print("✅ Evaluation completed successfully")
            print(f"Results: {len(result['results'])} variants tested")
        except Exception as e:
            print(f"⚠️ Evaluation failed: {e}")
    else:
        print("⚠️ No endpoints configured - skipping evaluation")
        print("Set APP_URL_BASELINE and APP_URL_CHALLENGER environment variables")

    return framework


if __name__ == "__main__":
    main()


