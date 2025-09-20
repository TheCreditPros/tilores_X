#!/usr/bin/env python3
"""
AI-Driven System Prompt Optimization Engine.

This module implements an advanced AI-driven optimization engine for system
prompts, targeting 90%+ quality achievement across the 7-model LangSmith
framework with statistical analysis and continuous improvement.

Author: Roo (tilores_X Development Team)
Date: August 16, 2025
Version: 1.0.0
"""

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Graceful numpy import with fallback
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Optimization strategies for prompt enhancement."""

    CLARITY_ENHANCEMENT = "clarity_enhancement"
    CONTEXT_EXPANSION = "context_expansion"
    INSTRUCTION_REFINEMENT = "instruction_refinement"
    EXAMPLE_INTEGRATION = "example_integration"
    CONSTRAINT_OPTIMIZATION = "constraint_optimization"
    TONE_ADJUSTMENT = "tone_adjustment"
    STRUCTURE_IMPROVEMENT = "structure_improvement"


class QualityMetric(Enum):
    """Quality metrics for prompt evaluation."""

    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    CLARITY = "clarity"
    CONSISTENCY = "consistency"
    PROFESSIONAL_TONE = "professional_tone"
    RESPONSE_TIME = "response_time"


@dataclass
class PromptAnalysis:
    """Analysis results for a system prompt."""

    prompt_id: str
    original_prompt: str
    quality_scores: Dict[QualityMetric, float]
    identified_issues: List[str]
    improvement_opportunities: List[OptimizationStrategy]
    complexity_score: float
    readability_score: float
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def overall_quality(self) -> float:
        """Calculate weighted overall quality score."""
        weights = {
            QualityMetric.ACCURACY: 0.25,
            QualityMetric.RELEVANCE: 0.20,
            QualityMetric.COMPLETENESS: 0.15,
            QualityMetric.CLARITY: 0.15,
            QualityMetric.CONSISTENCY: 0.10,
            QualityMetric.PROFESSIONAL_TONE: 0.10,
            QualityMetric.RESPONSE_TIME: 0.05,
        }

        total_score = 0.0
        total_weight = 0.0

        for metric, score in self.quality_scores.items():
            if metric in weights:
                total_score += score * weights[metric]
                total_weight += weights[metric]

        return total_score / total_weight if total_weight > 0 else 0.0


@dataclass
class OptimizationResult:
    """Result of prompt optimization process."""

    optimization_id: str
    original_prompt: str
    optimized_prompt: str
    strategy_applied: OptimizationStrategy
    expected_improvement: float
    confidence_level: float
    validation_results: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PromptAnalyzer:
    """Advanced prompt analysis engine."""

    def __init__(self):
        """Initialize the prompt analyzer."""
        self.analysis_patterns = self._initialize_analysis_patterns()
        self.quality_thresholds = {
            QualityMetric.ACCURACY: 0.90,
            QualityMetric.RELEVANCE: 0.85,
            QualityMetric.COMPLETENESS: 0.80,
            QualityMetric.CLARITY: 0.85,
            QualityMetric.CONSISTENCY: 0.90,
            QualityMetric.PROFESSIONAL_TONE: 0.95,
            QualityMetric.RESPONSE_TIME: 0.75,
        }

    def _initialize_analysis_patterns(self) -> Dict[str, Dict]:
        """Initialize patterns for prompt analysis."""
        return {
            "clarity_indicators": {
                "positive": [
                    r"\bspecifically\b",
                    r"\bclearly\b",
                    r"\bexactly\b",
                    r"\bprecisely\b",
                    r"\bstep.by.step\b",
                ],
                "negative": [r"\bmaybe\b", r"\bperhaps\b", r"\bsomewhat\b", r"\bkind of\b", r"\bsort of\b"],
            },
            "instruction_quality": {
                "strong_verbs": [
                    r"\banalyze\b",
                    r"\bevaluate\b",
                    r"\bidentify\b",
                    r"\bdetermine\b",
                    r"\bcalculate\b",
                    r"\bgenerate\b",
                ],
                "weak_verbs": [r"\btry\b", r"\battempt\b", r"\bconsider\b", r"\bthink about\b"],
            },
            "context_completeness": {
                "context_markers": [r"\bgiven\b", r"\bcontext\b", r"\bbackground\b", r"\binformation\b", r"\bdata\b"],
                "example_markers": [r"\bfor example\b", r"\bsuch as\b", r"\blike\b", r"\bincluding\b"],
            },
            "professional_tone": {
                "professional": [r"\bplease\b", r"\bkindly\b", r"\bthank you\b", r"\brespectfully\b"],
                "unprofessional": [r"\bhey\b", r"\bguys\b", r"\bokay\b", r"\bawesome\b"],
            },
        }

    def analyze_prompt(self, prompt: str, prompt_id: Optional[str] = None) -> PromptAnalysis:
        """
        Analyze a system prompt for quality and improvement opportunities.

        Args:
            prompt: The system prompt to analyze
            prompt_id: Optional identifier for the prompt

        Returns:
            PromptAnalysis containing detailed analysis results
        """
        if prompt_id is None:
            prompt_id = f"prompt_{int(time.time())}"

        logger.info(f"Analyzing prompt {prompt_id}")

        # Calculate quality scores
        quality_scores = self._calculate_quality_scores(prompt)

        # Identify issues
        issues = self._identify_issues(prompt, quality_scores)

        # Determine improvement opportunities
        opportunities = self._identify_improvement_opportunities(prompt, quality_scores, issues)

        # Calculate complexity and readability
        complexity = self._calculate_complexity(prompt)
        readability = self._calculate_readability(prompt)

        analysis = PromptAnalysis(
            prompt_id=prompt_id,
            original_prompt=prompt,
            quality_scores=quality_scores,
            identified_issues=issues,
            improvement_opportunities=opportunities,
            complexity_score=complexity,
            readability_score=readability,
        )

        logger.info(f"Analysis completed for {prompt_id}: " f"Overall quality={analysis.overall_quality:.3f}")

        return analysis

    def _calculate_quality_scores(self, prompt: str) -> Dict[QualityMetric, float]:
        """Calculate quality scores for different metrics."""
        scores = {}

        # Accuracy score based on specific instructions
        accuracy_indicators = len(re.findall(r"\b(specific|exact|precise|accurate|correct)\b", prompt.lower()))
        scores[QualityMetric.ACCURACY] = min(1.0, accuracy_indicators * 0.2 + 0.5)

        # Relevance score based on context markers
        context_patterns = self.analysis_patterns["context_completeness"]["context_markers"]
        relevance_score = 0.0
        for pattern in context_patterns:
            if re.search(pattern, prompt.lower()):
                relevance_score += 0.2
        scores[QualityMetric.RELEVANCE] = min(1.0, relevance_score + 0.3)

        # Completeness score based on instruction coverage
        instruction_elements = [
            r"\btask\b",
            r"\bgoal\b",
            r"\bobjective\b",
            r"\bformat\b",
            r"\bexample\b",
            r"\bconstraint\b",
        ]
        completeness = sum(1 for pattern in instruction_elements if re.search(pattern, prompt.lower()))
        scores[QualityMetric.COMPLETENESS] = completeness / len(instruction_elements)

        # Clarity score based on clear language patterns
        clarity_positive = sum(
            1
            for pattern in self.analysis_patterns["clarity_indicators"]["positive"]
            if re.search(pattern, prompt.lower())
        )
        clarity_negative = sum(
            1
            for pattern in self.analysis_patterns["clarity_indicators"]["negative"]
            if re.search(pattern, prompt.lower())
        )
        scores[QualityMetric.CLARITY] = max(0.0, min(1.0, 0.7 + (clarity_positive * 0.1) - (clarity_negative * 0.2)))

        # Consistency score based on uniform terminology
        word_count = len(prompt.split())
        unique_words = len(set(prompt.lower().split()))
        consistency_ratio = unique_words / word_count if word_count > 0 else 1.0
        scores[QualityMetric.CONSISTENCY] = max(0.0, min(1.0, 1.2 - consistency_ratio))

        # Professional tone score
        professional_markers = sum(
            1
            for pattern in self.analysis_patterns["professional_tone"]["professional"]
            if re.search(pattern, prompt.lower())
        )
        unprofessional_markers = sum(
            1
            for pattern in self.analysis_patterns["professional_tone"]["unprofessional"]
            if re.search(pattern, prompt.lower())
        )
        scores[QualityMetric.PROFESSIONAL_TONE] = max(
            0.0, min(1.0, 0.8 + (professional_markers * 0.1) - (unprofessional_markers * 0.3))
        )

        # Response time score (estimated based on prompt length)
        prompt_length = len(prompt)
        if prompt_length < 500:
            scores[QualityMetric.RESPONSE_TIME] = 0.9
        elif prompt_length < 1000:
            scores[QualityMetric.RESPONSE_TIME] = 0.8
        elif prompt_length < 2000:
            scores[QualityMetric.RESPONSE_TIME] = 0.7
        else:
            scores[QualityMetric.RESPONSE_TIME] = 0.6

        return scores

    def _identify_issues(self, prompt: str, quality_scores: Dict[QualityMetric, float]) -> List[str]:
        """Identify specific issues in the prompt."""
        issues = []

        for metric, score in quality_scores.items():
            threshold = self.quality_thresholds[metric]
            if score < threshold:
                if metric == QualityMetric.ACCURACY:
                    issues.append("Lacks specific accuracy requirements")
                elif metric == QualityMetric.RELEVANCE:
                    issues.append("Missing contextual information")
                elif metric == QualityMetric.COMPLETENESS:
                    issues.append("Incomplete instruction coverage")
                elif metric == QualityMetric.CLARITY:
                    issues.append("Contains ambiguous language")
                elif metric == QualityMetric.CONSISTENCY:
                    issues.append("Inconsistent terminology usage")
                elif metric == QualityMetric.PROFESSIONAL_TONE:
                    issues.append("Unprofessional tone detected")
                elif metric == QualityMetric.RESPONSE_TIME:
                    issues.append("Prompt may be too lengthy")

        # Additional specific issue detection
        if len(prompt) < 50:
            issues.append("Prompt too short for comprehensive guidance")

        if not re.search(r"\?", prompt):
            issues.append("No clear questions or tasks defined")

        if prompt.count(".") < 2:
            issues.append("Lacks structured instructions")

        return issues

    def _identify_improvement_opportunities(
        self, prompt: str, quality_scores: Dict[QualityMetric, float], issues: List[str]
    ) -> List[OptimizationStrategy]:
        """Identify optimization strategies for improvement."""
        opportunities = []

        # Strategy selection based on quality scores
        if quality_scores.get(QualityMetric.CLARITY, 1.0) < 0.8:
            opportunities.append(OptimizationStrategy.CLARITY_ENHANCEMENT)

        if quality_scores.get(QualityMetric.COMPLETENESS, 1.0) < 0.8:
            opportunities.append(OptimizationStrategy.CONTEXT_EXPANSION)

        if quality_scores.get(QualityMetric.ACCURACY, 1.0) < 0.9:
            opportunities.append(OptimizationStrategy.INSTRUCTION_REFINEMENT)

        if "No clear questions" in " ".join(issues):
            opportunities.append(OptimizationStrategy.STRUCTURE_IMPROVEMENT)

        if quality_scores.get(QualityMetric.PROFESSIONAL_TONE, 1.0) < 0.9:
            opportunities.append(OptimizationStrategy.TONE_ADJUSTMENT)

        # Add example integration if prompt lacks examples
        if not re.search(r"\bexample\b|\bfor instance\b|\bsuch as\b", prompt.lower()):
            opportunities.append(OptimizationStrategy.EXAMPLE_INTEGRATION)

        # Add constraint optimization if prompt is too lengthy
        if len(prompt) > 1500:
            opportunities.append(OptimizationStrategy.CONSTRAINT_OPTIMIZATION)

        return opportunities

    def _calculate_complexity(self, prompt: str) -> float:
        """Calculate prompt complexity score."""
        # Factors contributing to complexity
        word_count = len(prompt.split())
        sentence_count = len(re.findall(r"[.!?]+", prompt))
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else word_count

        # Complex words (more than 6 characters)
        complex_words = len([word for word in prompt.split() if len(word) > 6])
        complex_word_ratio = complex_words / word_count if word_count > 0 else 0

        # Nested instructions (parentheses, colons, semicolons)
        nesting_indicators = prompt.count("(") + prompt.count(":") + prompt.count(";")

        # Normalize complexity score (0-1 scale)
        complexity = min(
            1.0, ((avg_sentence_length / 20) * 0.4 + complex_word_ratio * 0.4 + (nesting_indicators / 10) * 0.2)
        )

        return complexity

    def _calculate_readability(self, prompt: str) -> float:
        """Calculate prompt readability score (simplified Flesch-like)."""
        words = prompt.split()
        sentences = re.findall(r"[.!?]+", prompt)

        if not words or not sentences:
            return 0.5

        avg_sentence_length = len(words) / len(sentences)

        # Count syllables (simplified: vowel groups)
        syllable_count = 0
        for word in words:
            syllable_count += max(1, len(re.findall(r"[aeiouAEIOU]+", word)))

        avg_syllables_per_word = syllable_count / len(words)

        # Simplified readability score (higher is more readable)
        readability = max(0.0, min(1.0, 1.2 - (avg_sentence_length / 25) - (avg_syllables_per_word / 3)))

        return readability


class AIPromptOptimizer:
    """AI-driven prompt optimization engine."""

    def __init__(self, target_quality: float = 0.90):
        """
        Initialize the AI prompt optimizer.

        Args:
            target_quality: Target quality score for optimization
        """
        self.target_quality = target_quality
        self.analyzer = PromptAnalyzer()
        self.optimization_history: List[OptimizationResult] = []
        self.strategy_templates = self._initialize_strategy_templates()

        logger.info(f"Initialized AIPromptOptimizer with target quality: {target_quality}")

    def _initialize_strategy_templates(self) -> Dict[OptimizationStrategy, Dict]:
        """Initialize optimization strategy templates."""
        return {
            OptimizationStrategy.CLARITY_ENHANCEMENT: {
                "patterns": [
                    ("ambiguous", "specific and clear"),
                    ("might", "will"),
                    ("try to", ""),
                    ("kind of", ""),
                    ("sort of", ""),
                ],
                "additions": ["Be specific and precise in your response.", "Provide clear, unambiguous information."],
            },
            OptimizationStrategy.CONTEXT_EXPANSION: {
                "additions": [
                    "Context: You are working with Tilores customer data containing "
                    "310+ fields across multiple data spectrums.",
                    "Background: This system integrates with LangSmith for "
                    "comprehensive monitoring and quality tracking.",
                ]
            },
            OptimizationStrategy.INSTRUCTION_REFINEMENT: {
                "patterns": [
                    ("please try", "please"),
                    ("you should", "you must"),
                    ("consider", "analyze"),
                    ("think about", "evaluate"),
                ],
                "additions": ["Follow these instructions precisely.", "Ensure accuracy in all responses."],
            },
            OptimizationStrategy.EXAMPLE_INTEGRATION: {
                "additions": [
                    "For example: When searching for customer 'John Doe', include client ID, email, and phone number in results.",
                    "Example format: Provide structured data with clear field labels and values.",
                ]
            },
            OptimizationStrategy.CONSTRAINT_OPTIMIZATION: {
                "patterns": [
                    (r"\s+", " "),  # Multiple spaces to single space
                    (r"\n\s*\n", "\n"),  # Multiple newlines to single
                ],
                "removals": ["obviously", "clearly", "of course", "as you know"],
            },
            OptimizationStrategy.TONE_ADJUSTMENT: {
                "patterns": [("hey", ""), ("guys", ""), ("awesome", "excellent"), ("cool", "appropriate")],
                "additions": [
                    "Maintain a professional and helpful tone.",
                    "Provide courteous and respectful responses.",
                ],
            },
            OptimizationStrategy.STRUCTURE_IMPROVEMENT: {
                "structure_template": """
                Task: {task_description}

                Instructions:
                1. {instruction_1}
                2. {instruction_2}
                3. {instruction_3}

                Format: {output_format}

                Constraints: {constraints}
                """
            },
        }

    async def optimize_prompt(
        self, prompt: str, strategies: Optional[List[OptimizationStrategy]] = None
    ) -> OptimizationResult:
        """
        Optimize a system prompt using AI-driven strategies.

        Args:
            prompt: Original prompt to optimize
            strategies: Specific strategies to apply (auto-detected if None)

        Returns:
            OptimizationResult containing optimized prompt and metrics
        """
        optimization_id = f"opt_{int(time.time())}"

        logger.info(f"Starting optimization {optimization_id}")

        # Analyze original prompt
        analysis = self.analyzer.analyze_prompt(prompt, f"{optimization_id}_original")

        # Determine strategies if not provided
        if strategies is None:
            strategies = analysis.improvement_opportunities

        if not strategies:
            logger.info("No optimization strategies needed")
            return OptimizationResult(
                optimization_id=optimization_id,
                original_prompt=prompt,
                optimized_prompt=prompt,
                strategy_applied=OptimizationStrategy.CLARITY_ENHANCEMENT,
                expected_improvement=0.0,
                confidence_level=1.0,
                validation_results={"no_optimization_needed": True},
            )

        # Apply optimization strategies
        optimized_prompt = prompt
        applied_strategies = []

        for strategy in strategies:
            optimized_prompt = await self._apply_strategy(optimized_prompt, strategy)
            applied_strategies.append(strategy)

        # Analyze optimized prompt
        optimized_analysis = self.analyzer.analyze_prompt(optimized_prompt, f"{optimization_id}_optimized")

        # Calculate improvement metrics
        expected_improvement = optimized_analysis.overall_quality - analysis.overall_quality
        confidence_level = self._calculate_confidence(analysis, optimized_analysis)

        # Create optimization result
        result = OptimizationResult(
            optimization_id=optimization_id,
            original_prompt=prompt,
            optimized_prompt=optimized_prompt,
            strategy_applied=applied_strategies[0] if applied_strategies else OptimizationStrategy.CLARITY_ENHANCEMENT,
            expected_improvement=expected_improvement,
            confidence_level=confidence_level,
            validation_results={
                "original_quality": analysis.overall_quality,
                "optimized_quality": optimized_analysis.overall_quality,
                "strategies_applied": [s.value for s in applied_strategies],
                "issues_resolved": len(analysis.identified_issues) - len(optimized_analysis.identified_issues),
            },
            metadata={"original_analysis": analysis, "optimized_analysis": optimized_analysis},
        )

        self.optimization_history.append(result)

        logger.info(
            f"Optimization {optimization_id} completed: "
            f"Improvement={expected_improvement:.3f}, "
            f"Confidence={confidence_level:.3f}"
        )

        return result

    async def _apply_strategy(self, prompt: str, strategy: OptimizationStrategy) -> str:
        """Apply a specific optimization strategy to a prompt."""
        template = self.strategy_templates.get(strategy, {})
        optimized_prompt = prompt

        # Apply pattern replacements
        patterns = template.get("patterns", [])
        for old_pattern, new_pattern in patterns:
            if isinstance(old_pattern, str):
                optimized_prompt = optimized_prompt.replace(old_pattern, new_pattern)
            else:  # regex pattern
                optimized_prompt = re.sub(old_pattern, new_pattern, optimized_prompt)

        # Remove unwanted elements
        removals = template.get("removals", [])
        for removal in removals:
            optimized_prompt = optimized_prompt.replace(removal, "")

        # Add enhancements
        additions = template.get("additions", [])
        if additions:
            optimized_prompt += "\n\n" + "\n".join(additions)

        # Apply structure template if available
        structure_template = template.get("structure_template")
        if structure_template and strategy == OptimizationStrategy.STRUCTURE_IMPROVEMENT:
            # Extract components from original prompt for structured format
            optimized_prompt = self._apply_structure_template(optimized_prompt, structure_template)

        # Clean up extra whitespace
        optimized_prompt = re.sub(r"\s+", " ", optimized_prompt).strip()
        optimized_prompt = re.sub(r"\n\s*\n", "\n\n", optimized_prompt)

        return optimized_prompt

    def _apply_structure_template(self, prompt: str, template: str) -> str:
        """Apply structured template to prompt."""
        # Simple structure application - in production, this would be more sophisticated
        lines = prompt.split("\n")

        # Extract task description (first meaningful line)
        task_description = next((line.strip() for line in lines if line.strip()), "Complete the requested task")

        # Create structured version
        structured_prompt = template.format(
            task_description=task_description,
            instruction_1="Analyze the provided data carefully",
            instruction_2="Apply appropriate processing based on data type",
            instruction_3="Provide accurate and complete results",
            output_format="Structured response with clear field labels",
            constraints="Maintain data accuracy and professional tone",
        )

        return structured_prompt.strip()

    def _calculate_confidence(self, original_analysis: PromptAnalysis, optimized_analysis: PromptAnalysis) -> float:
        """Calculate confidence level for optimization results."""
        # Factors affecting confidence
        quality_improvement = optimized_analysis.overall_quality - original_analysis.overall_quality

        # Higher confidence for larger improvements
        improvement_confidence = min(1.0, max(0.0, quality_improvement * 2))

        # Higher confidence for better readability
        readability_confidence = optimized_analysis.readability_score

        # Lower confidence for high complexity
        complexity_penalty = max(0.0, 1.0 - optimized_analysis.complexity_score)

        # Combined confidence score
        confidence = improvement_confidence * 0.5 + readability_confidence * 0.3 + complexity_penalty * 0.2

        return max(0.1, min(1.0, confidence))

    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report."""
        if not self.optimization_history:
            return {"error": "No optimization history available"}

        # Calculate statistics
        improvements = [r.expected_improvement for r in self.optimization_history]
        confidences = [r.confidence_level for r in self.optimization_history]

        if NUMPY_AVAILABLE:
            avg_improvement = float(np.mean(improvements))
            avg_confidence = float(np.mean(confidences))
            improvement_std = float(np.std(improvements))
        else:
            avg_improvement = sum(improvements) / len(improvements)
            avg_confidence = sum(confidences) / len(confidences)
            improvement_mean = avg_improvement
            improvement_std = (sum((x - improvement_mean) ** 2 for x in improvements) / len(improvements)) ** 0.5

        # Strategy effectiveness analysis
        strategy_performance = {}
        for result in self.optimization_history:
            strategy = result.strategy_applied.value
            if strategy not in strategy_performance:
                strategy_performance[strategy] = []
            strategy_performance[strategy].append(result.expected_improvement)

        # Calculate average performance per strategy
        strategy_averages = {}
        for strategy, improvements in strategy_performance.items():
            if NUMPY_AVAILABLE:
                strategy_averages[strategy] = float(np.mean(improvements))
            else:
                strategy_averages[strategy] = sum(improvements) / len(improvements)

        # Success rate (improvements above threshold)
        successful_optimizations = sum(1 for imp in improvements if imp > 0.05)
        success_rate = successful_optimizations / len(improvements)

        return {
            "total_optimizations": len(self.optimization_history),
            "average_improvement": avg_improvement,
            "improvement_std": improvement_std,
            "average_confidence": avg_confidence,
            "success_rate": success_rate,
            "target_quality": self.target_quality,
            "strategy_performance": strategy_averages,
            "recommendations": self._generate_recommendations(avg_improvement, success_rate, strategy_averages),
        }

    def _generate_recommendations(
        self, avg_improvement: float, success_rate: float, strategy_performance: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations based on optimization history."""
        recommendations = []

        if avg_improvement < 0.05:
            recommendations.append("Average improvement is low. Consider more aggressive optimization strategies.")

        if success_rate < 0.7:
            recommendations.append("Success rate below 70%. Review prompt selection criteria.")

        # Identify best performing strategies
        if strategy_performance:
            best_strategy = max(strategy_performance.items(), key=lambda x: x[1])
            recommendations.append(
                f"Most effective strategy: {best_strategy[0]} " f"(avg improvement: {best_strategy[1]:.3f})"
            )

        if avg_improvement > 0.1:
            recommendations.append("High improvement rates achieved. Consider applying optimizations more broadly.")

        return recommendations

    def export_optimization_history(self, filename: str) -> None:
        """Export optimization history to JSON file."""
        export_data = {
            "optimizer_config": {
                "target_quality": self.target_quality,
                "total_optimizations": len(self.optimization_history),
            },
            "optimizations": [
                {
                    "optimization_id": r.optimization_id,
                    "strategy_applied": r.strategy_applied.value,
                    "expected_improvement": r.expected_improvement,
                    "confidence_level": r.confidence_level,
                    "validation_results": r.validation_results,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in self.optimization_history
            ],
            "export_timestamp": datetime.now().isoformat(),
        }

        with open(filename, "w") as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Optimization history exported to {filename}")


# Example usage and testing
async def main():
    """Example usage of the AI-Driven Optimization Engine."""
    # Initialize optimizer
    optimizer = AIPromptOptimizer(target_quality=0.90)

    # Example prompt to optimize
    sample_prompt = """
    You are a helpful assistant. Try to help the user with their question.
    Maybe you can look at the data and see what you can find.
    Be nice and helpful.
    """

    # Optimize the prompt
    result = await optimizer.optimize_prompt(sample_prompt)

    # Print results
    print("\n=== AI-Driven Prompt Optimization Results ===")
    print(f"Optimization ID: {result.optimization_id}")
    print(f"Strategy Applied: {result.strategy_applied.value}")
    print(f"Expected Improvement: {result.expected_improvement:.3f}")
    print(f"Confidence Level: {result.confidence_level:.3f}")

    print("\nOriginal Prompt:")
    print(f'"{result.original_prompt}"')

    print("\nOptimized Prompt:")
    print(f'"{result.optimized_prompt}"')

    print("\nValidation Results:")
    for key, value in result.validation_results.items():
        print(f"  {key}: {value}")

    # Generate optimization report
    report = optimizer.generate_optimization_report()
    print("\nOptimization Report:")
    print(f"Total Optimizations: {report.get('total_optimizations', 0)}")
    print(f"Average Improvement: {report.get('average_improvement', 0):.3f}")
    print(f"Success Rate: {report.get('success_rate', 0):.3f}")

    # Export results
    optimizer.export_optimization_history("ai_optimization_results.json")

    return optimizer


if __name__ == "__main__":
    asyncio.run(main())
