#!/usr / bin / env python3
"""
Agenta Test Runner

Automated test runner that orchestrates the complete Agenta testing pipeline:
ground truth extraction, test case generation, evaluation execution, and reporting.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import framework components
from ground_truth_extractor import GroundTruthExtractor
from test_case_generator import TestCaseGenerator
from agenta_evaluation_framework import AgentaEvaluationFramework
from results_analyzer import ResultsAnalyzer


class AgentaTestRunner:
    """Orchestrate complete Agenta testing pipeline"""

    def __init__(self, config: Dict = None):
        """Initialize test runner"""
        self.config = config or self._load_default_config()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"tests / agenta / run_{self.timestamp}"

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        print("🚀 Agenta Test Runner Initialized")
        print(f"  - Output Directory: {self.output_dir}")
        print(f"  - Timestamp: {self.timestamp}")

    def _load_default_config(self) -> Dict:
        """Load default configuration"""
        return {
            "master_data_file": None,  # Auto - detect
            "test_case_limit": None,   # No limit
            "variants": {
                "baseline": os.getenv("APP_URL_BASELINE"),
                "challenger": os.getenv("APP_URL_CHALLENGER")
            },
            "field_weights": {
                # High importance fields
                "customer_name": 3.0,
                "customer_email": 3.0,
                "client_id": 3.0,
                "total_credit_reports": 3.0,
                "latest_credit_score": 2.0,
                "has_credit_data": 2.0,
                "has_transaction_data": 2.0,
                "risk_level": 2.0,
                # Medium importance fields
                "total_transactions": 2.0,
                "account_status": 2.0,
                "customer_found": 2.0,
                # Lower importance fields
                "explanation": 1.0
            },
            "promotion_rules": {
                "min_score_improvement": 0.03,
                "max_latency_increase": 0.10,
                "min_test_cases": 5
            },
            "generate_reports": True,
            "save_intermediate_files": True
        }

    def run_complete_pipeline(self) -> Dict:
        """Run the complete testing pipeline"""
        print("\n🎯 STARTING COMPLETE AGENTA TESTING PIPELINE")
        print("=" * 60)

        pipeline_results = {
            "timestamp": self.timestamp,
            "output_dir": self.output_dir,
            "steps_completed": [],
            "files_generated": [],
            "errors": []
        }

        try:
            # Step 1: Extract Ground Truth
            print("\n📊 STEP 1: Extracting Ground Truth")
            print("-" * 40)

            ground_truth_file = self._extract_ground_truth()
            pipeline_results["steps_completed"].append("ground_truth_extraction")
            pipeline_results["files_generated"].append(ground_truth_file)

            # Step 2: Generate Test Cases
            print("\n📝 STEP 2: Generating Test Cases")
            print("-" * 40)

            test_cases_file = self._generate_test_cases(ground_truth_file)
            pipeline_results["steps_completed"].append("test_case_generation")
            pipeline_results["files_generated"].append(test_cases_file)

            # Step 3: Run Evaluation
            print("\n🔄 STEP 3: Running Evaluation")
            print("-" * 40)

            evaluation_results_file = self._run_evaluation(test_cases_file)
            pipeline_results["steps_completed"].append("evaluation")
            pipeline_results["files_generated"].append(evaluation_results_file)

            # Step 4: Analyze Results
            print("\n📈 STEP 4: Analyzing Results")
            print("-" * 40)

            analysis_files = self._analyze_results(evaluation_results_file)
            pipeline_results["steps_completed"].append("analysis")
            pipeline_results["files_generated"].extend(analysis_files)

            # Step 5: Generate Reports
            if self.config.get("generate_reports", True):
                print("\n📋 STEP 5: Generating Reports")
                print("-" * 40)

                report_files = self._generate_reports(analysis_files[0])  # Analysis JSON file
                pipeline_results["steps_completed"].append("reporting")
                pipeline_results["files_generated"].extend(report_files)

            pipeline_results["success"] = True

        except Exception as e:
            error_msg = f"Pipeline failed: {str(e)}"
            pipeline_results["errors"].append(error_msg)
            pipeline_results["success"] = False
            print(f"\n❌ {error_msg}")

        # Save pipeline summary
        summary_file = self._save_pipeline_summary(pipeline_results)
        pipeline_results["files_generated"].append(summary_file)

        return pipeline_results

    def _extract_ground_truth(self) -> str:
        """Extract ground truth from master data"""
        try:
            extractor = GroundTruthExtractor(self.config.get("master_data_file"))
            extractor.print_summary()

            # Save to output directory
            output_file = os.path.join(self.output_dir, "ground_truth.json")
            return extractor.save_ground_truth(output_file)

        except Exception as e:
            raise Exception(f"Ground truth extraction failed: {e}")

    def _generate_test_cases(self, ground_truth_file: str) -> str:
        """Generate test cases from ground truth"""
        try:
            generator = TestCaseGenerator(ground_truth_file)
            test_cases = generator.generate_all_test_cases()

            # Apply test case limit if specified
            limit = self.config.get("test_case_limit")
            if limit and len(test_cases) > limit:
                test_cases = test_cases[:limit]
                print(f"⚠️ Limited to {limit} test cases")

            generator.test_cases = test_cases
            generator.print_summary()

            # Save to output directory
            output_file = os.path.join(self.output_dir, "test_cases.jsonl")
            return generator.save_test_cases_jsonl(output_file)

        except Exception as e:
            raise Exception(f"Test case generation failed: {e}")

    def _run_evaluation(self, test_cases_file: str) -> str:
        """Run evaluation against test cases"""
        try:
            # Load test cases
            test_cases = []
            with open(test_cases_file, 'r', encoding='utf - 8') as f:
                for line in f:
                    if line.strip():
                        test_cases.append(json.loads(line))

            # Create evaluation framework with config
            framework_config = {
                "field_weights": self.config.get("field_weights", {}),
                "promotion_rules": self.config.get("promotion_rules", {})
            }

            # Save framework config
            config_file = os.path.join(self.output_dir, "framework_config.json")
            with open(config_file, 'w') as f:
                json.dump(framework_config, f, indent=2)

            framework = AgentaEvaluationFramework(config_file)

            # Update variant endpoints
            variants = self.config.get("variants", {})
            framework.variant_endpoints.update(variants)

            # Check if endpoints are configured
            configured_variants = {k: v for k, v in framework.variant_endpoints.items() if v}
            if not configured_variants:
                raise Exception("No variant endpoints configured. Set APP_URL_BASELINE and APP_URL_CHALLENGER environment variables.")

            print(f"Testing {len(configured_variants)} variants: {list(configured_variants.keys())}")

            # Run evaluation
            results = framework.evaluate_test_suite(test_cases)

            # Save results
            output_file = os.path.join(self.output_dir, "evaluation_results.json")
            return framework.save_results(results, output_file)

        except Exception as e:
            raise Exception(f"Evaluation failed: {e}")

    def _analyze_results(self, results_file: str) -> List[str]:
        """Analyze evaluation results"""
        try:
            analyzer = ResultsAnalyzer(results_file)
            analysis = analyzer.analyze_results()

            # Print summary
            analyzer.print_summary()

            # Save analysis
            analysis_file = os.path.join(self.output_dir, "analysis_results.json")
            analyzer.save_analysis(analysis_file)

            return [analysis_file]

        except Exception as e:
            raise Exception(f"Results analysis failed: {e}")

    def _generate_reports(self, analysis_file: str) -> List[str]:
        """Generate comprehensive reports"""
        try:
            analyzer = ResultsAnalyzer()

            # Load analysis data
            with open(analysis_file, 'r') as f:
                analyzer.analysis = json.load(f)

            # Generate markdown report
            report_file = os.path.join(self.output_dir, "evaluation_report.md")
            analyzer.generate_markdown_report(report_file)

            return [report_file]

        except Exception as e:
            raise Exception(f"Report generation failed: {e}")

    def _save_pipeline_summary(self, pipeline_results: Dict) -> str:
        """Save pipeline execution summary"""
        summary_file = os.path.join(self.output_dir, "pipeline_summary.json")

        with open(summary_file, 'w', encoding='utf - 8') as f:
            json.dump(pipeline_results, f, indent=2, ensure_ascii=False, default=str)

        return summary_file

    def run_quick_test(self, test_case_limit: int = 5) -> Dict:
        """Run a quick test with limited test cases"""
        print(f"\n⚡ RUNNING QUICK TEST ({test_case_limit} test cases)")
        print("=" * 50)

        # Update config for quick test
        original_limit = self.config.get("test_case_limit")
        self.config["test_case_limit"] = test_case_limit

        try:
            results = self.run_complete_pipeline()
            return results
        finally:
            # Restore original config
            self.config["test_case_limit"] = original_limit

    def validate_environment(self) -> Dict:
        """Validate environment configuration"""
        validation = {
            "valid": True,
            "checks": {},
            "warnings": [],
            "errors": []
        }

        print("\n🔍 VALIDATING ENVIRONMENT")
        print("-" * 30)

        # Check for master data file
        try:
            extractor = GroundTruthExtractor()
            validation["checks"]["master_data"] = "✅ Found"
        except Exception as e:
            validation["checks"]["master_data"] = f"❌ {str(e)}"
            validation["errors"].append(f"Master data file: {str(e)}")
            validation["valid"] = False

        # Check Agenta API key
        agenta_key = os.getenv("AGENTA_API_KEY")
        if agenta_key:
            validation["checks"]["agenta_api_key"] = "✅ Set"
        else:
            validation["checks"]["agenta_api_key"] = "❌ Missing"
            validation["warnings"].append("AGENTA_API_KEY not set - evaluation will fail")

        # Check LLM judge configuration
        judge_key = os.getenv("JUDGE_API_KEY") or os.getenv("OPENAI_API_KEY")
        if judge_key:
            validation["checks"]["judge_api_key"] = "✅ Set"
        else:
            validation["checks"]["judge_api_key"] = "❌ Missing"
            validation["warnings"].append("Judge API key not set - free text evaluation will use similarity fallback")

        # Check variant endpoints
        baseline_url = os.getenv("APP_URL_BASELINE")
        challenger_url = os.getenv("APP_URL_CHALLENGER")

        if baseline_url:
            validation["checks"]["baseline_endpoint"] = "✅ Set"
        else:
            validation["checks"]["baseline_endpoint"] = "❌ Missing"
            validation["errors"].append("APP_URL_BASELINE not set")
            validation["valid"] = False

        if challenger_url:
            validation["checks"]["challenger_endpoint"] = "✅ Set"
        else:
            validation["checks"]["challenger_endpoint"] = "❌ Missing"
            validation["errors"].append("APP_URL_CHALLENGER not set")
            validation["valid"] = False

        # Print validation results
        for check, status in validation["checks"].items():
            print(f"  {check}: {status}")

        if validation["warnings"]:
            print("\n⚠️ WARNINGS:")
            for warning in validation["warnings"]:
                print(f"  - {warning}")

        if validation["errors"]:
            print("\n❌ ERRORS:")
            for error in validation["errors"]:
                print(f"  - {error}")

        if validation["valid"]:
            print("\n✅ Environment validation passed")
        else:
            print("\n❌ Environment validation failed")

        return validation

    def print_usage_guide(self):
        """Print usage guide"""
        print("\n📖 AGENTA TEST RUNNER USAGE GUIDE")
        print("=" * 50)

        print("\n🔧 ENVIRONMENT SETUP:")
        print("  export AGENTA_API_KEY='your - agenta - api - key'")
        print("  export APP_URL_BASELINE='https://cloud.agenta.ai / api/.../baseline'")
        print("  export APP_URL_CHALLENGER='https://cloud.agenta.ai / api/.../challenger'")
        print("  export OPENAI_API_KEY='your - openai - key'  # For LLM judge")

        print("\n🚀 BASIC USAGE:")
        print("  runner = AgentaTestRunner()")
        print("  runner.validate_environment()")
        print("  results = runner.run_complete_pipeline()")

        print("\n⚡ QUICK TEST:")
        print("  results = runner.run_quick_test(test_case_limit=5)")

        print("\n📁 OUTPUT FILES:")
        print("  - ground_truth.json: Extracted ground truth data")
        print("  - test_cases.jsonl: Generated test cases")
        print("  - evaluation_results.json: Raw evaluation results")
        print("  - analysis_results.json: Detailed analysis")
        print("  - evaluation_report.md: Human - readable report")
        print("  - pipeline_summary.json: Execution summary")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Agenta Testing Framework Runner")
    parser.add_argument("--validate", action="store_true", help="Validate environment only")
    parser.add_argument("--quick", type=int, metavar="N", help="Run quick test with N test cases")
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument("--limit", type=int, help="Limit number of test cases")
    parser.add_argument("--output - dir", type=str, help="Output directory")

    args = parser.parse_args()

    # Load configuration
    config = None
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)

    # Initialize runner
    runner = AgentaTestRunner(config)

    # Apply CLI overrides
    if args.limit:
        runner.config["test_case_limit"] = args.limit

    if args.output_dir:
        runner.output_dir = args.output_dir
        os.makedirs(runner.output_dir, exist_ok=True)

    # Execute based on arguments
    if args.validate:
        validation = runner.validate_environment()
        sys.exit(0 if validation["valid"] else 1)

    elif args.quick:
        results = runner.run_quick_test(args.quick)
        print(f"\n🎯 Quick test completed: {'✅ SUCCESS' if results['success'] else '❌ FAILED'}")

    else:
        # Show usage guide if no specific action
        runner.print_usage_guide()

        # Validate environment
        validation = runner.validate_environment()

        if validation["valid"]:
            print("\n🚀 Ready to run complete pipeline!")
            print("Use: python agenta_test_runner.py --quick 5")
        else:
            print("\n❌ Fix environment issues before running tests")
            sys.exit(1)


if __name__ == "__main__":
    main()


