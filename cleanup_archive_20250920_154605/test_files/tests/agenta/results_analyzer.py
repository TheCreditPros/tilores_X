#!/usr / bin / env python3
"""
Results Analyzer for Agenta Testing Framework

Analyzes evaluation results, generates comprehensive reports, and provides
promotion recommendations based on configurable rules and performance metrics.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import statistics


class ResultsAnalyzer:
    """Analyze Agenta evaluation results and generate reports"""

    def __init__(self, results_file: str = None):
        """Initialize results analyzer"""
        self.results_file = results_file
        self.results_data = None
        self.analysis = {}

        if results_file and os.path.exists(results_file):
            self._load_results()

        print("📊 Results Analyzer initialized")
        if self.results_data:
            print(f"  - Results file: {results_file}")
            print(f"  - Test cases: {self.results_data.get('metadata', {}).get('total_test_cases', 0)}")
            print(f"  - Variants: {len(self.results_data.get('summary_statistics', {}))}")

    def _load_results(self):
        """Load evaluation results from file"""
        try:
            with open(self.results_file, 'r', encoding='utf - 8') as f:
                self.results_data = json.load(f)
            print(f"✅ Loaded results from: {self.results_file}")
        except Exception as e:
            raise Exception(f"Failed to load results: {e}")

    def analyze_results(self, results_data: Dict = None) -> Dict:
        """Perform comprehensive analysis of results"""
        if results_data:
            self.results_data = results_data

        if not self.results_data:
            raise ValueError("No results data available for analysis")

        print("🔄 Analyzing evaluation results...")

        # Extract key data
        metadata = self.results_data.get('metadata', {})
        detailed_results = self.results_data.get('detailed_results', [])
        summary_stats = self.results_data.get('summary_statistics', {})

        # Perform analysis
        self.analysis = {
            "metadata": metadata,
            "variant_comparison": self._analyze_variant_comparison(summary_stats),
            "field_accuracy_analysis": self._analyze_field_accuracy(detailed_results),
            "performance_analysis": self._analyze_performance(summary_stats),
            "category_breakdown": self._analyze_by_category(detailed_results),
            "failure_analysis": self._analyze_failures(detailed_results),
            "promotion_recommendation": self._generate_promotion_recommendation(summary_stats),
            "improvement_suggestions": self._generate_improvement_suggestions(detailed_results, summary_stats)
        }

        print("✅ Analysis complete")
        return self.analysis

    def _analyze_variant_comparison(self, summary_stats: Dict) -> Dict:
        """Analyze comparison between variants"""
        comparison = {
            "variants": list(summary_stats.keys()),
            "winner": None,
            "score_differences": {},
            "performance_differences": {}
        }

        if len(summary_stats) >= 2:
            # Find best performing variant by average score
            best_variant = max(summary_stats.items(), key=lambda x: x[1].get('avg_score', 0))
            comparison["winner"] = best_variant[0]

            # Calculate differences between variants
            baseline_stats = summary_stats.get('baseline', {})
            challenger_stats = summary_stats.get('challenger', {})

            if baseline_stats and challenger_stats:
                score_diff = challenger_stats.get('avg_score', 0) - baseline_stats.get('avg_score', 0)
                comparison["score_differences"]["challenger_vs_baseline"] = {
                    "absolute_difference": round(score_diff, 4),
                    "percentage_improvement": round((score_diff / baseline_stats.get('avg_score', 1)) * 100, 2) if baseline_stats.get('avg_score', 0) > 0 else 0,
                    "baseline_score": baseline_stats.get('avg_score', 0),
                    "challenger_score": challenger_stats.get('avg_score', 0)
                }

                # Performance comparison
                if baseline_stats.get('avg_latency_s') and challenger_stats.get('avg_latency_s'):
                    latency_diff = challenger_stats['avg_latency_s'] - baseline_stats['avg_latency_s']
                    comparison["performance_differences"]["latency"] = {
                        "absolute_difference_s": round(latency_diff, 3),
                        "percentage_change": round((latency_diff / baseline_stats['avg_latency_s']) * 100, 2),
                        "baseline_latency_s": baseline_stats['avg_latency_s'],
                        "challenger_latency_s": challenger_stats['avg_latency_s']
                    }

        return comparison

    def _analyze_field_accuracy(self, detailed_results: List[Dict]) -> Dict:
        """Analyze accuracy by field across all test cases"""
        field_scores = {}
        field_counts = {}

        for case_result in detailed_results:
            for result in case_result.get('results', []):
                if not result.get('success', False):
                    continue

                for field_breakdown in result.get('field_breakdown', []):
                    field_name = field_breakdown['field']
                    field_score = field_breakdown['score']
                    variant = result['variant']

                    # Initialize field tracking
                    if field_name not in field_scores:
                        field_scores[field_name] = {}
                        field_counts[field_name] = {}

                    if variant not in field_scores[field_name]:
                        field_scores[field_name][variant] = []
                        field_counts[field_name][variant] = 0

                    field_scores[field_name][variant].append(field_score)
                    field_counts[field_name][variant] += 1

        # Calculate field statistics
        field_analysis = {}
        for field_name, variant_scores in field_scores.items():
            field_analysis[field_name] = {}

            for variant, scores in variant_scores.items():
                if scores:
                    field_analysis[field_name][variant] = {
                        "avg_score": round(statistics.mean(scores), 4),
                        "median_score": round(statistics.median(scores), 4),
                        "min_score": round(min(scores), 4),
                        "max_score": round(max(scores), 4),
                        "std_dev": round(statistics.stdev(scores), 4) if len(scores) > 1 else 0.0,
                        "count": len(scores),
                        "perfect_scores": sum(1 for s in scores if s >= 0.99)
                    }

        return field_analysis

    def _analyze_performance(self, summary_stats: Dict) -> Dict:
        """Analyze performance metrics"""
        performance = {
            "latency_analysis": {},
            "success_rate_analysis": {},
            "throughput_estimates": {}
        }

        for variant, stats in summary_stats.items():
            # Latency analysis
            if stats.get('avg_latency_s'):
                performance["latency_analysis"][variant] = {
                    "avg_latency_s": stats['avg_latency_s'],
                    "p90_latency_s": stats.get('p90_latency_s'),
                    "p95_latency_s": stats.get('p95_latency_s'),
                    "latency_category": self._categorize_latency(stats['avg_latency_s'])
                }

                # Estimate throughput (requests per minute)
                if stats['avg_latency_s'] > 0:
                    throughput_rpm = 60 / stats['avg_latency_s']
                    performance["throughput_estimates"][variant] = {
                        "requests_per_minute": round(throughput_rpm, 1),
                        "requests_per_hour": round(throughput_rpm * 60, 0)
                    }

            # Success rate analysis
            performance["success_rate_analysis"][variant] = {
                "success_rate": stats.get('success_rate', 0.0),
                "successes": stats.get('successes', 0),
                "failures": stats.get('failures', 0),
                "reliability_category": self._categorize_reliability(stats.get('success_rate', 0.0))
            }

        return performance

    def _analyze_by_category(self, detailed_results: List[Dict]) -> Dict:
        """Analyze results by test case category"""
        category_analysis = {}

        for case_result in detailed_results:
            # Extract category from test case (if available)
            category = "unknown"
            case_id = case_result.get('case_id', '')

            # Infer category from case ID
            if 'account_status' in case_id:
                category = 'account_status'
            elif 'credit_analysis' in case_id or 'credit_score' in case_id or 'risk_assessment' in case_id:
                category = 'credit_analysis'
            elif 'transaction' in case_id or 'payment' in case_id:
                category = 'transaction_analysis'
            elif 'phone' in case_id or 'contact' in case_id:
                category = 'phone_analysis'
            elif 'comprehensive' in case_id or 'multi_data' in case_id or '360' in case_id:
                category = 'multi_data_analysis'
            elif 'edge_case' in case_id or 'nonexistent' in case_id or 'malformed' in case_id:
                category = 'edge_cases'

            if category not in category_analysis:
                category_analysis[category] = {}

            for result in case_result.get('results', []):
                variant = result['variant']

                if variant not in category_analysis[category]:
                    category_analysis[category][variant] = {
                        'scores': [],
                        'successes': 0,
                        'failures': 0,
                        'latencies': []
                    }

                if result.get('success', False):
                    category_analysis[category][variant]['scores'].append(result['overall_score'])
                    category_analysis[category][variant]['successes'] += 1
                    if result.get('latency_s'):
                        category_analysis[category][variant]['latencies'].append(result['latency_s'])
                else:
                    category_analysis[category][variant]['failures'] += 1

        # Calculate category statistics
        for category, variants in category_analysis.items():
            for variant, data in variants.items():
                scores = data['scores']
                latencies = data['latencies']

                data['avg_score'] = statistics.mean(scores) if scores else 0.0
                data['success_rate'] = data['successes'] / (data['successes'] + data['failures']) if (data['successes'] + data['failures']) > 0 else 0.0
                data['avg_latency_s'] = statistics.mean(latencies) if latencies else None
                data['test_count'] = data['successes'] + data['failures']

        return category_analysis

    def _analyze_failures(self, detailed_results: List[Dict]) -> Dict:
        """Analyze failure patterns"""
        failures = {
            "total_failures": 0,
            "failure_by_variant": {},
            "failure_patterns": {},
            "common_errors": {}
        }

        for case_result in detailed_results:
            for result in case_result.get('results', []):
                variant = result['variant']

                if not result.get('success', False):
                    failures["total_failures"] += 1

                    if variant not in failures["failure_by_variant"]:
                        failures["failure_by_variant"][variant] = 0
                    failures["failure_by_variant"][variant] += 1

                    # Analyze error patterns
                    error = result.get('error', 'Unknown error')
                    error_type = self._categorize_error(error)

                    if error_type not in failures["failure_patterns"]:
                        failures["failure_patterns"][error_type] = 0
                    failures["failure_patterns"][error_type] += 1

                    # Track common errors
                    error_key = error[:100]  # First 100 chars
                    if error_key not in failures["common_errors"]:
                        failures["common_errors"][error_key] = 0
                    failures["common_errors"][error_key] += 1

        return failures

    def _generate_promotion_recommendation(self, summary_stats: Dict) -> Dict:
        """Generate promotion recommendation"""
        recommendation = {
            "promote": False,
            "confidence": "low",
            "reason": "Insufficient data",
            "criteria_met": {},
            "risks": [],
            "benefits": []
        }

        baseline_stats = summary_stats.get('baseline', {})
        challenger_stats = summary_stats.get('challenger', {})

        if not baseline_stats or not challenger_stats:
            recommendation["reason"] = "Missing baseline or challenger results"
            return recommendation

        # Check promotion criteria
        criteria = {
            "score_improvement": False,
            "acceptable_latency": False,
            "sufficient_test_cases": False,
            "acceptable_success_rate": False
        }

        # Score improvement check (3% minimum)
        score_improvement = challenger_stats.get('avg_score', 0) - baseline_stats.get('avg_score', 0)
        if score_improvement >= 0.03:
            criteria["score_improvement"] = True
            recommendation["benefits"].append(f"Score improvement: +{score_improvement:.4f} ({score_improvement / baseline_stats.get('avg_score', 1)*100:.1f}%)")
        else:
            recommendation["risks"].append(f"Insufficient score improvement: {score_improvement:.4f} < 0.03")

        # Latency check (max 10% increase)
        if baseline_stats.get('avg_latency_s') and challenger_stats.get('avg_latency_s'):
            latency_increase = (challenger_stats['avg_latency_s'] - baseline_stats['avg_latency_s']) / baseline_stats['avg_latency_s']
            if latency_increase <= 0.10:
                criteria["acceptable_latency"] = True
                if latency_increase < 0:
                    recommendation["benefits"].append(f"Latency improvement: {latency_increase:.1%}")
                else:
                    recommendation["benefits"].append(f"Acceptable latency increase: {latency_increase:.1%}")
            else:
                recommendation["risks"].append(f"Excessive latency increase: {latency_increase:.1%} > 10%")
        else:
            criteria["acceptable_latency"] = True  # No latency data available

        # Test case count check (minimum 5)
        test_count = challenger_stats.get('test_cases', 0)
        if test_count >= 5:
            criteria["sufficient_test_cases"] = True
        else:
            recommendation["risks"].append(f"Insufficient test cases: {test_count} < 5")

        # Success rate check (minimum 90%)
        success_rate = challenger_stats.get('success_rate', 0.0)
        if success_rate >= 0.90:
            criteria["acceptable_success_rate"] = True
        else:
            recommendation["risks"].append(f"Low success rate: {success_rate:.1%} < 90%")

        recommendation["criteria_met"] = criteria

        # Make recommendation
        criteria_met_count = sum(criteria.values())
        total_criteria = len(criteria)

        if criteria_met_count == total_criteria:
            recommendation["promote"] = True
            recommendation["confidence"] = "high"
            recommendation["reason"] = "All promotion criteria met"
        elif criteria_met_count >= total_criteria * 0.75:
            recommendation["promote"] = True
            recommendation["confidence"] = "medium"
            recommendation["reason"] = f"Most criteria met ({criteria_met_count}/{total_criteria})"
        else:
            recommendation["promote"] = False
            recommendation["confidence"] = "high"
            recommendation["reason"] = f"Insufficient criteria met ({criteria_met_count}/{total_criteria})"

        return recommendation

    def _generate_improvement_suggestions(self, detailed_results: List[Dict], summary_stats: Dict) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []

        # Analyze field accuracy patterns
        field_analysis = self._analyze_field_accuracy(detailed_results)

        # Find consistently low - scoring fields
        low_scoring_fields = []
        for field_name, variants in field_analysis.items():
            for variant, stats in variants.items():
                if stats.get('avg_score', 1.0) < 0.7:
                    low_scoring_fields.append((field_name, variant, stats['avg_score']))

        if low_scoring_fields:
            suggestions.append(f"Improve accuracy for low - scoring fields: {', '.join([f'{field} ({score:.2f})' for field, variant, score in low_scoring_fields[:3]])}")

        # Check for high latency
        for variant, stats in summary_stats.items():
            if stats.get('avg_latency_s', 0) > 10:
                suggestions.append(f"Optimize {variant} variant for latency (current: {stats['avg_latency_s']:.1f}s)")

        # Check for low success rates
        for variant, stats in summary_stats.items():
            if stats.get('success_rate', 1.0) < 0.95:
                suggestions.append(f"Improve {variant} variant reliability (current: {stats['success_rate']:.1%})")

        # Analyze category performance
        category_analysis = self._analyze_by_category(detailed_results)
        weak_categories = []
        for category, variants in category_analysis.items():
            for variant, stats in variants.items():
                if stats.get('avg_score', 1.0) < 0.8:
                    weak_categories.append((category, variant, stats['avg_score']))

        if weak_categories:
            suggestions.append(f"Focus prompt optimization on weak categories: {', '.join([f'{cat} ({score:.2f})' for cat, variant, score in weak_categories[:2]])}")

        # General suggestions
        if not suggestions:
            suggestions.append("Consider A / B testing additional prompt variants to find further improvements")
            suggestions.append("Expand test case coverage to include more edge cases and scenarios")

        return suggestions

    def _categorize_latency(self, latency_s: float) -> str:
        """Categorize latency performance"""
        if latency_s < 2.0:
            return "excellent"
        elif latency_s < 5.0:
            return "good"
        elif latency_s < 10.0:
            return "acceptable"
        else:
            return "poor"

    def _categorize_reliability(self, success_rate: float) -> str:
        """Categorize reliability performance"""
        if success_rate >= 0.99:
            return "excellent"
        elif success_rate >= 0.95:
            return "good"
        elif success_rate >= 0.90:
            return "acceptable"
        else:
            return "poor"

    def _categorize_error(self, error: str) -> str:
        """Categorize error types"""
        error_lower = error.lower()

        if "timeout" in error_lower or "timed out" in error_lower:
            return "timeout"
        elif "401" in error or "403" in error or "unauthorized" in error_lower:
            return "authentication"
        elif "422" in error or "400" in error or "bad request" in error_lower:
            return "request_format"
        elif "500" in error or "502" in error or "503" in error:
            return "server_error"
        elif "connection" in error_lower or "network" in error_lower:
            return "network"
        else:
            return "other"

    def generate_markdown_report(self, output_file: str = None) -> str:
        """Generate comprehensive markdown report"""
        if not self.analysis:
            raise ValueError("No analysis data available. Run analyze_results() first.")

        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"tests / agenta / evaluation_report_{timestamp}.md"

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Generate report content
        report_lines = []

        # Header
        report_lines.extend([
            "# 🎯 Agenta Evaluation Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Test Cases:** {self.analysis['metadata'].get('total_test_cases', 0)}",
            f"**Variants:** {len(self.analysis['variant_comparison']['variants'])}",
            ""
        ])

        # Executive Summary
        promotion = self.analysis['promotion_recommendation']
        report_lines.extend([
            "## 📊 Executive Summary",
            "",
            f"**Recommendation:** {'✅ PROMOTE' if promotion['promote'] else '❌ DO NOT PROMOTE'}",
            f"**Confidence:** {promotion['confidence'].upper()}",
            f"**Reason:** {promotion['reason']}",
            ""
        ])

        # Variant Comparison
        comparison = self.analysis['variant_comparison']
        if comparison['winner']:
            report_lines.extend([
                "## 🏆 Variant Comparison",
                "",
                f"**Winner:** {comparison['winner']}",
                ""
            ])

            if 'challenger_vs_baseline' in comparison['score_differences']:
                score_diff = comparison['score_differences']['challenger_vs_baseline']
                report_lines.extend([
                    "### Score Comparison",
                    "",
                    f"- **Baseline Score:** {score_diff['baseline_score']:.4f}",
                    f"- **Challenger Score:** {score_diff['challenger_score']:.4f}",
                    f"- **Improvement:** {score_diff['absolute_difference']:+.4f} ({score_diff['percentage_improvement']:+.1f}%)",
                    ""
                ])

            if 'latency' in comparison['performance_differences']:
                latency_diff = comparison['performance_differences']['latency']
                report_lines.extend([
                    "### Performance Comparison",
                    "",
                    f"- **Baseline Latency:** {latency_diff['baseline_latency_s']:.2f}s",
                    f"- **Challenger Latency:** {latency_diff['challenger_latency_s']:.2f}s",
                    f"- **Change:** {latency_diff['absolute_difference_s']:+.2f}s ({latency_diff['percentage_change']:+.1f}%)",
                    ""
                ])

        # Promotion Criteria
        criteria = promotion['criteria_met']
        report_lines.extend([
            "## ✅ Promotion Criteria",
            "",
            f"- **Score Improvement:** {'✅' if criteria.get('score_improvement') else '❌'}",
            f"- **Acceptable Latency:** {'✅' if criteria.get('acceptable_latency') else '❌'}",
            f"- **Sufficient Test Cases:** {'✅' if criteria.get('sufficient_test_cases') else '❌'}",
            f"- **Acceptable Success Rate:** {'✅' if criteria.get('acceptable_success_rate') else '❌'}",
            ""
        ])

        # Benefits and Risks
        if promotion['benefits']:
            report_lines.extend([
                "### 🎉 Benefits",
                ""
            ])
            for benefit in promotion['benefits']:
                report_lines.append(f"- {benefit}")
            report_lines.append("")

        if promotion['risks']:
            report_lines.extend([
                "### ⚠️ Risks",
                ""
            ])
            for risk in promotion['risks']:
                report_lines.append(f"- {risk}")
            report_lines.append("")

        # Performance Analysis
        performance = self.analysis['performance_analysis']
        report_lines.extend([
            "## 📈 Performance Analysis",
            ""
        ])

        for variant, latency_data in performance['latency_analysis'].items():
            report_lines.extend([
                f"### {variant.title()} Variant",
                "",
                f"- **Average Latency:** {latency_data['avg_latency_s']:.2f}s ({latency_data['latency_category']})",
                f"- **P90 Latency:** {latency_data.get('p90_latency_s', 'N / A')}s",
                f"- **Success Rate:** {performance['success_rate_analysis'][variant]['success_rate']:.1%}",
                ""
            ])

            if variant in performance['throughput_estimates']:
                throughput = performance['throughput_estimates'][variant]
                report_lines.extend([
                    f"- **Estimated Throughput:** {throughput['requests_per_minute']} req / min",
                    ""
                ])

        # Category Breakdown
        category_analysis = self.analysis['category_breakdown']
        if category_analysis:
            report_lines.extend([
                "## 📋 Category Performance",
                ""
            ])

            for category, variants in category_analysis.items():
                report_lines.extend([
                    f"### {category.replace('_', ' ').title()}",
                    ""
                ])

                for variant, stats in variants.items():
                    report_lines.extend([
                        f"**{variant.title()}:**",
                        f"- Score: {stats['avg_score']:.3f}",
                        f"- Success Rate: {stats['success_rate']:.1%}",
                        f"- Test Cases: {stats['test_count']}",
                        ""
                    ])

        # Improvement Suggestions
        suggestions = self.analysis['improvement_suggestions']
        if suggestions:
            report_lines.extend([
                "## 💡 Improvement Suggestions",
                ""
            ])

            for i, suggestion in enumerate(suggestions, 1):
                report_lines.append(f"{i}. {suggestion}")

            report_lines.append("")

        # Footer
        report_lines.extend([
            "---",
            "",
            f"*Report generated by Agenta Testing Framework at {datetime.now().isoformat()}*"
        ])

        # Write report
        with open(output_file, 'w', encoding='utf - 8') as f:
            f.write('\n'.join(report_lines))

        print(f"✅ Markdown report saved to: {output_file}")
        return output_file

    def save_analysis(self, output_file: str = None) -> str:
        """Save analysis results to JSON file"""
        if not self.analysis:
            raise ValueError("No analysis data available. Run analyze_results() first.")

        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"tests / agenta / analysis_results_{timestamp}.json"

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf - 8') as f:
            json.dump(self.analysis, f, indent=2, ensure_ascii=False, default=str)

        print(f"✅ Analysis saved to: {output_file}")
        return output_file

    def print_summary(self):
        """Print analysis summary"""
        if not self.analysis:
            print("❌ No analysis data available")
            return

        print("\n📊 EVALUATION RESULTS ANALYSIS")
        print("=" * 50)

        # Basic info
        metadata = self.analysis['metadata']
        print(f"📁 Test Cases: {metadata.get('total_test_cases', 0)}")
        print(f"🔄 Variants: {len(self.analysis['variant_comparison']['variants'])}")

        # Winner
        winner = self.analysis['variant_comparison']['winner']
        if winner:
            print(f"🏆 Winner: {winner}")

        # Promotion recommendation
        promotion = self.analysis['promotion_recommendation']
        print("\n🎯 PROMOTION RECOMMENDATION:")
        print(f"  Decision: {'✅ PROMOTE' if promotion['promote'] else '❌ DO NOT PROMOTE'}")
        print(f"  Confidence: {promotion['confidence'].upper()}")
        print(f"  Reason: {promotion['reason']}")

        # Performance summary
        performance = self.analysis['performance_analysis']
        print("\n📈 PERFORMANCE SUMMARY:")
        for variant, data in performance['success_rate_analysis'].items():
            print(f"  {variant}: {data['success_rate']:.1%} success rate")

        # Top suggestions
        suggestions = self.analysis['improvement_suggestions']
        if suggestions:
            print("\n💡 TOP SUGGESTIONS:")
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"  {i}. {suggestion}")


def main():
    """Main execution for testing"""
    print("🚀 RESULTS ANALYZER")
    print("=" * 40)

    # Example usage
    analyzer = ResultsAnalyzer()

    print("\n📝 Results analyzer ready")
    print("Usage:")
    print("  1. Load results: analyzer = ResultsAnalyzer('results_file.json')")
    print("  2. Analyze: analyzer.analyze_results()")
    print("  3. Generate report: analyzer.generate_markdown_report()")

    return analyzer


if __name__ == "__main__":
    main()


