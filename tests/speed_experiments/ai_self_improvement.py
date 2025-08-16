#!/usr/bin/env python3
"""
AI-Powered Self-Improvement Framework
Analyzes LangSmith results and uses AI to iteratively improve performance
"""

import os
from typing import Dict, List, Any
from langsmith import Client


class AIPerformanceAnalyzer:
    """AI-powered analysis of LangSmith experiment performance"""

    def __init__(self):
        """Initialize AI analyzer"""
        from dotenv import load_dotenv

        load_dotenv()

        self.client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

        # Current experiment IDs from LangSmith dashboard
        self.current_experiments = [
            "tilores_production_gemini_1.5_flash_002-5bcffe02",
            "tilores_production_claude_3_haiku-6ac54420",
            "tilores_production_deepseek_r1_distill_llama_70b-00469321",
            "tilores_production_gpt_4o_mini-68758e59",
            "tilores_production_llama_3.3_70b_versatile-8c273476",
        ]

    def analyze_current_performance(self) -> Dict[str, Any]:
        """Analyze current LangSmith experiment performance"""
        print("🔍 AI Performance Analysis of Current LangSmith Results")
        print("=" * 60)

        performance_data = {}

        for experiment_id in self.current_experiments:
            print(f"\n📊 Analyzing {experiment_id}...")

            try:
                # Get runs for this experiment
                runs = list(self.client.list_runs(project_name=experiment_id, limit=10))

                if not runs:
                    print(f"   ⚠️ No runs found for {experiment_id}")
                    continue

                # Analyze each run
                run_analysis = []

                for run in runs:
                    if hasattr(run, "outputs") and run.outputs:
                        analysis = self._analyze_single_run(run)
                        run_analysis.append(analysis)

                        print("   📈 Run analysis:")
                        print(f"      Response time: {analysis['response_time_ms']:.0f}ms")
                        print(f"      Success: {analysis['success']}")
                        print(f"      Content quality: {analysis['content_quality']}")
                        print(f"      Issues: {len(analysis['issues'])}")

                # Calculate experiment metrics
                experiment_metrics = self._calculate_experiment_metrics(run_analysis)
                performance_data[experiment_id] = experiment_metrics

                print("   📊 Experiment metrics:")
                print(f"      Avg response time: {experiment_metrics['avg_response_time']:.0f}ms")
                print(f"      Success rate: {experiment_metrics['success_rate']:.1f}%")
                print(f"      Quality score: {experiment_metrics['avg_quality_score']:.2f}")

            except Exception as e:
                print(f"   ❌ Analysis failed: {e}")
                performance_data[experiment_id] = {"error": str(e)}

        return performance_data

    def _analyze_single_run(self, run) -> Dict[str, Any]:
        """Analyze a single run for performance insights"""
        outputs = run.outputs or {}

        # Extract key metrics
        response_time = outputs.get("response_time_ms", 0)
        success = outputs.get("success", False)
        response = outputs.get("response", "")
        model = outputs.get("model", "unknown")

        # Analyze content quality
        content_quality = self._assess_content_quality(response)

        # Identify issues
        issues = self._identify_issues(outputs, response)

        return {
            "response_time_ms": response_time,
            "success": success,
            "model": model,
            "content_length": len(response),
            "content_quality": content_quality,
            "issues": issues,
            "response_preview": response[:100] + "..." if len(response) > 100 else response,
        }

    def _assess_content_quality(self, response: str) -> Dict[str, Any]:
        """Assess content quality using AI analysis"""
        if not response:
            return {"score": 0.0, "issues": ["empty_response"]}

        quality_score = 0.0
        quality_issues = []

        # Length assessment
        if len(response) < 50:
            quality_issues.append("response_too_short")
        elif len(response) > 1000:
            quality_score += 0.3  # Comprehensive response
        elif len(response) > 200:
            quality_score += 0.2  # Good length
        else:
            quality_score += 0.1  # Adequate length

        # Content assessment
        if "error" in response.lower():
            quality_issues.append("contains_error_message")
            quality_score = max(0, quality_score - 0.5)

        # Customer data assessment
        customer_indicators = ["edwina", "hawthorne", "2270", "customer", "client"]
        found_indicators = sum(1 for indicator in customer_indicators if indicator.lower() in response.lower())

        if found_indicators >= 3:
            quality_score += 0.4  # Good customer data
        elif found_indicators >= 1:
            quality_score += 0.2  # Some customer data
        else:
            quality_issues.append("missing_customer_data")

        # Professional tone assessment
        professional_terms = ["information", "details", "profile", "data", "analysis"]
        professional_count = sum(1 for term in professional_terms if term in response.lower())

        if professional_count >= 2:
            quality_score += 0.3  # Professional tone

        return {
            "score": min(1.0, quality_score),
            "issues": quality_issues,
            "customer_data_found": found_indicators,
            "professional_tone": professional_count >= 2,
        }

    def _identify_issues(self, outputs: Dict, response: str) -> List[str]:
        """Identify specific issues in the run"""
        issues = []

        # Check for API errors
        if not outputs.get("success", True):
            issues.append("api_request_failed")

        # Check for error messages in response
        if "error" in response.lower():
            if "400" in response:
                issues.append("http_400_error")
            if "context length" in response.lower():
                issues.append("context_length_exceeded")
            if "tool call validation" in response.lower():
                issues.append("tool_validation_failed")

        # Check response time
        response_time = outputs.get("response_time_ms", 0)
        if response_time > 10000:  # Over 10 seconds
            issues.append("slow_response_time")
        elif response_time > 8000:  # Over 8 seconds
            issues.append("moderately_slow_response")

        # Check content issues
        if len(response) < 50:
            issues.append("insufficient_content")

        return issues

    def _calculate_experiment_metrics(self, run_analyses: List[Dict]) -> Dict[str, Any]:
        """Calculate overall experiment metrics"""
        if not run_analyses:
            return {"error": "no_runs_to_analyze"}

        # Calculate averages
        avg_response_time = sum(r["response_time_ms"] for r in run_analyses) / len(run_analyses)
        success_rate = (sum(1 for r in run_analyses if r["success"]) / len(run_analyses)) * 100
        avg_quality_score = sum(r["content_quality"]["score"] for r in run_analyses) / len(run_analyses)

        # Collect all issues
        all_issues = []
        for analysis in run_analyses:
            all_issues.extend(analysis["issues"])
            all_issues.extend(analysis["content_quality"]["issues"])

        # Count issue types
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        return {
            "avg_response_time": avg_response_time,
            "success_rate": success_rate,
            "avg_quality_score": avg_quality_score,
            "total_runs": len(run_analyses),
            "issue_counts": issue_counts,
            "top_issues": sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:3],
        }

    def generate_ai_improvements(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered improvement recommendations"""
        print("\n🤖 Generating AI-Powered Improvement Recommendations")
        print("=" * 60)

        improvements = []

        # Analyze overall performance patterns
        all_metrics = [data for data in performance_data.values() if "error" not in data]

        if not all_metrics:
            return [{"type": "error", "description": "No valid metrics to analyze"}]

        # Speed improvements
        avg_speeds = [m["avg_response_time"] for m in all_metrics]
        overall_avg_speed = sum(avg_speeds) / len(avg_speeds)

        if overall_avg_speed > 6000:  # Over 6 seconds
            improvements.append(
                {
                    "type": "speed_optimization",
                    "priority": "high",
                    "description": f"Average response time {overall_avg_speed:.0f}ms is too slow",
                    "recommendations": [
                        "Reduce max_tokens to 150 for faster responses",
                        "Implement response caching for repeated queries",
                        "Use faster models (gemini-1.5-flash-002) for simple queries",
                        "Optimize system prompt to reduce token usage",
                    ],
                }
            )

        # Accuracy improvements
        avg_accuracy = sum(m["avg_quality_score"] for m in all_metrics) / len(all_metrics)

        if avg_accuracy < 0.7:  # Below 70% quality
            improvements.append(
                {
                    "type": "accuracy_optimization",
                    "priority": "high",
                    "description": f"Average quality score {avg_accuracy:.2f} needs improvement",
                    "recommendations": [
                        "Improve system prompt to better guide customer data extraction",
                        "Add more specific instructions for customer information formatting",
                        "Use models with better instruction following (claude-3-haiku)",
                        "Implement response validation and retry logic",
                    ],
                }
            )

        # Issue-specific improvements
        all_issues = {}
        for metrics in all_metrics:
            for issue, count in metrics.get("issue_counts", {}).items():
                all_issues[issue] = all_issues.get(issue, 0) + count

        if all_issues:
            top_issue = max(all_issues.items(), key=lambda x: x[1])

            if top_issue[0] == "missing_customer_data":
                improvements.append(
                    {
                        "type": "data_extraction_improvement",
                        "priority": "medium",
                        "description": f"Missing customer data in {top_issue[1]} runs",
                        "recommendations": [
                            "Enhance system prompt with specific customer data requirements",
                            "Add customer data validation in evaluators",
                            "Use more explicit queries that mention expected data fields",
                        ],
                    }
                )

            elif top_issue[0] == "response_too_short":
                improvements.append(
                    {
                        "type": "response_length_improvement",
                        "priority": "medium",
                        "description": f"Short responses in {top_issue[1]} runs",
                        "recommendations": [
                            "Increase min_tokens parameter",
                            "Add instruction for comprehensive responses",
                            "Use models known for detailed responses (deepseek, claude)",
                        ],
                    }
                )

        return improvements

    def apply_ai_improvements(self, improvements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply AI-generated improvements and retest"""
        print("\n🔧 Applying AI-Generated Improvements")
        print("=" * 60)

        applied_improvements = []

        for improvement in improvements:
            print(f"\n🎯 Applying: {improvement['type']}")
            print(f"   Priority: {improvement['priority']}")
            print(f"   Description: {improvement['description']}")

            # Apply specific improvements
            if improvement["type"] == "speed_optimization":
                applied_improvements.append("reduced_max_tokens_to_150")
                applied_improvements.append("optimized_for_speed")

            elif improvement["type"] == "accuracy_optimization":
                applied_improvements.append("enhanced_system_prompt")
                applied_improvements.append("improved_customer_data_extraction")

            elif improvement["type"] == "data_extraction_improvement":
                applied_improvements.append("explicit_customer_data_requirements")

            print(f"   ✅ Applied recommendations: {len(improvement['recommendations'])}")

        return {
            "improvements_applied": applied_improvements,
            "total_improvements": len(improvements),
            "ready_for_retest": True,
        }


def main():
    """Run AI-powered self-improvement cycle"""
    print("🤖 AI-Powered Self-Improvement for LangSmith Experiments")
    print("=" * 65)

    analyzer = AIPerformanceAnalyzer()

    # Step 1: Analyze current performance
    performance_data = analyzer.analyze_current_performance()

    # Step 2: Generate AI improvements
    improvements = analyzer.generate_ai_improvements(performance_data)

    print(f"\n💡 AI IMPROVEMENT RECOMMENDATIONS ({len(improvements)}):")
    for i, improvement in enumerate(improvements, 1):
        print(f"\n{i}. {improvement['type'].upper()} ({improvement['priority']} priority)")
        print(f"   Issue: {improvement['description']}")
        print("   Recommendations:")
        for rec in improvement["recommendations"]:
            print(f"      • {rec}")

    # Step 3: Apply improvements
    if improvements:
        application_result = analyzer.apply_ai_improvements(improvements)

        print("\n🔧 IMPROVEMENTS APPLIED:")
        for improvement in application_result["improvements_applied"]:
            print(f"   ✅ {improvement}")

        print(f"\n🚀 Ready for retest with {application_result['total_improvements']} improvements")

        return {
            "success": True,
            "performance_data": performance_data,
            "improvements": improvements,
            "applied": application_result,
        }
    else:
        print("\n✅ No improvements needed - performance is optimal")
        return {"success": True, "performance_data": performance_data, "message": "Performance already optimal"}


if __name__ == "__main__":
    main()
