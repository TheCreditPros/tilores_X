#!/usr/bin/env python3
"""
Lightweight Quality Metrics Collector for Continuous Improvement.

Author: Roo (Claude Sonnet)
Created: 2025-08-16

A lightweight system that collects quality scores from various sources and
feeds them into the virtuous cycle framework for continuous improvement.
Designed to work seamlessly with the existing QualityTrendAnalyzer.
"""

import asyncio
import json
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class QualityMetric:
    """Represents a single quality measurement."""

    def __init__(
        self,
        spectrum: str,
        score: float,
        source: str,
        model: str | None = None,
        timestamp: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ):
        """Initialize a quality metric."""
        self.spectrum = spectrum
        self.score = score
        self.source = source  # 'langsmith', 'direct_test', 'user_feedback'
        self.model = model
        self.timestamp = timestamp or datetime.now().isoformat()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary for storage."""
        return {
            "spectrum": self.spectrum,
            "score": self.score,
            "source": self.source,
            "model": self.model,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QualityMetric":
        """Create metric from dictionary."""
        return cls(
            spectrum=data["spectrum"],
            score=data["score"],
            source=data["source"],
            model=data.get("model"),
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata", {}),
        )


class LightweightMetricsStorage:
    """Lightweight storage for quality metrics using JSON files."""

    def __init__(self, storage_dir: str = "tests/speed_experiments/metrics"):
        """Initialize metrics storage."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.current_file = self.storage_dir / "current_metrics.json"
        self.archive_dir = self.storage_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)

        # In-memory cache for fast access
        self.memory_cache: deque = deque(maxlen=1000)
        self.spectrum_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        # Load existing metrics
        self._load_current_metrics()

    def add_metric(self, metric: QualityMetric):
        """Add a new quality metric."""
        metric_dict = metric.to_dict()

        # Add to memory cache
        self.memory_cache.append(metric_dict)
        self.spectrum_cache[metric.spectrum].append(metric_dict)

        # Persist to storage
        self._save_to_current_file(metric_dict)

    def get_recent_metrics(self, limit: int = 100) -> List[QualityMetric]:
        """Get recent metrics from memory cache."""
        recent = list(self.memory_cache)[-limit:]
        return [QualityMetric.from_dict(m) for m in recent]

    def get_spectrum_metrics(self, spectrum: str, limit: int = 50) -> List[QualityMetric]:
        """Get recent metrics for a specific spectrum."""
        spectrum_data = list(self.spectrum_cache[spectrum])[-limit:]
        return [QualityMetric.from_dict(m) for m in spectrum_data]

    def get_metrics_by_timeframe(self, hours: int = 24) -> List[QualityMetric]:
        """Get metrics from the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()

        filtered_metrics = []
        for metric_dict in self.memory_cache:
            if metric_dict["timestamp"] > cutoff_str:
                filtered_metrics.append(QualityMetric.from_dict(metric_dict))

        return filtered_metrics

    def _load_current_metrics(self):
        """Load existing metrics from storage."""
        if self.current_file.exists():
            try:
                with open(self.current_file, "r") as f:
                    for line in f:
                        metric_dict = json.loads(line.strip())
                        self.memory_cache.append(metric_dict)
                        spectrum = metric_dict["spectrum"]
                        self.spectrum_cache[spectrum].append(metric_dict)
            except (json.JSONDecodeError, FileNotFoundError):
                # Create new file if corrupted
                self.current_file.unlink(missing_ok=True)

    def _save_to_current_file(self, metric_dict: Dict[str, Any]):
        """Append metric to current storage file."""
        with open(self.current_file, "a") as f:
            f.write(json.dumps(metric_dict) + "\n")

    def archive_old_metrics(self, days_to_keep: int = 7):
        """Archive old metrics to reduce current file size."""
        cutoff = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff.isoformat()

        # Read current metrics and split into keep/archive
        current_metrics = []
        archived_metrics = []

        if self.current_file.exists():
            with open(self.current_file, "r") as f:
                for line in f:
                    try:
                        metric_dict = json.loads(line.strip())
                        if metric_dict["timestamp"] > cutoff_str:
                            current_metrics.append(metric_dict)
                        else:
                            archived_metrics.append(metric_dict)
                    except json.JSONDecodeError:
                        continue

        # Save archived metrics
        if archived_metrics:
            archive_file = self.archive_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.json"
            with open(archive_file, "w") as f:
                for metric in archived_metrics:
                    f.write(json.dumps(metric) + "\n")

        # Rewrite current file with only recent metrics
        with open(self.current_file, "w") as f:
            for metric in current_metrics:
                f.write(json.dumps(metric) + "\n")


class QualityAnalytics:
    """Analytics engine for quality metrics."""

    def __init__(self, storage: LightweightMetricsStorage):
        """Initialize analytics engine."""
        self.storage = storage

    def calculate_spectrum_statistics(self, spectrum: str, hours: int = 24) -> Dict[str, Any]:
        """Calculate statistics for a specific spectrum."""
        metrics = self.storage.get_spectrum_metrics(spectrum, limit=200)
        if not metrics:
            return {"error": "no_data", "spectrum": spectrum}

        # Filter by timeframe
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in metrics if (datetime.fromisoformat(m.timestamp.replace("Z", "+00:00")) > cutoff)]

        if not recent_metrics:
            return {"error": "no_recent_data", "spectrum": spectrum}

        scores = [m.score for m in recent_metrics]

        # Calculate statistics
        if NUMPY_AVAILABLE:
            stats = {
                "mean": float(np.mean(scores)),
                "std": float(np.std(scores)),
                "min": float(np.min(scores)),
                "max": float(np.max(scores)),
                "median": float(np.median(scores)),
            }
        else:
            stats = {
                "mean": sum(scores) / len(scores),
                "std": ((sum((x - sum(scores) / len(scores)) ** 2 for x in scores) / len(scores)) ** 0.5),
                "min": min(scores),
                "max": max(scores),
                "median": sorted(scores)[len(scores) // 2],
            }

        # Additional analytics
        additional_stats = {
            "count": len(recent_metrics),
            "spectrum": spectrum,
            "timeframe_hours": hours,
            "latest_score": recent_metrics[-1].score,
            "trend": self._calculate_trend(scores),
            "quality_grade": self._calculate_quality_grade(stats["mean"]),
        }
        stats.update(additional_stats)

        return stats

    def generate_quality_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        # Get all recent metrics
        recent_metrics = self.storage.get_metrics_by_timeframe(hours)

        if not recent_metrics:
            return {"error": "no_recent_data"}

        # Group by spectrum
        spectrum_groups = defaultdict(list)
        for metric in recent_metrics:
            spectrum_groups[metric.spectrum].append(metric)

        # Calculate overall statistics
        all_scores = [m.score for m in recent_metrics]
        overall_stats = self._calculate_basic_stats(all_scores)

        # Calculate per-spectrum statistics
        spectrum_stats = {}
        for spectrum, metrics in spectrum_groups.items():
            scores = [m.score for m in metrics]
            spectrum_stats[spectrum] = {
                **self._calculate_basic_stats(scores),
                "count": len(metrics),
                "latest_score": metrics[-1].score,
            }

        # Identify trends and issues
        issues = self._identify_quality_issues(spectrum_stats)

        report = {
            "report_timestamp": datetime.now().isoformat(),
            "timeframe_hours": hours,
            "overall_statistics": overall_stats,
            "spectrum_statistics": spectrum_stats,
            "quality_issues": issues,
            "total_measurements": len(recent_metrics),
            "spectrums_measured": len(spectrum_groups),
            "recommendations": self._generate_recommendations(spectrum_stats),
        }

        return report

    def _calculate_basic_stats(self, scores: List[float]) -> Dict[str, float]:
        """Calculate basic statistics for a list of scores."""
        if not scores:
            return {}

        if NUMPY_AVAILABLE:
            return {
                "mean": float(np.mean(scores)),
                "std": float(np.std(scores)),
                "min": float(np.min(scores)),
                "max": float(np.max(scores)),
            }
        else:
            mean_val = sum(scores) / len(scores)
            return {
                "mean": mean_val,
                "std": ((sum((x - mean_val) ** 2 for x in scores) / len(scores)) ** 0.5),
                "min": min(scores),
                "max": max(scores),
            }

    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate trend direction for scores."""
        if len(scores) < 3:
            return "insufficient_data"

        # Simple trend calculation using first/last halves
        mid = len(scores) // 2
        first_half_avg = sum(scores[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(scores[mid:]) / (len(scores) - mid)

        diff = second_half_avg - first_half_avg
        if diff > 0.01:
            return "improving"
        elif diff < -0.01:
            return "declining"
        else:
            return "stable"

    def _calculate_quality_grade(self, mean_score: float) -> str:
        """Calculate quality grade based on mean score."""
        if mean_score >= 0.98:
            return "excellent"
        elif mean_score >= 0.95:
            return "good"
        elif mean_score >= 0.90:
            return "acceptable"
        elif mean_score >= 0.80:
            return "needs_improvement"
        else:
            return "poor"

    def _identify_quality_issues(self, spectrum_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify quality issues from spectrum statistics."""
        issues = []

        for spectrum, stats in spectrum_stats.items():
            if stats.get("mean", 1.0) < 0.90:
                issues.append(
                    {
                        "type": "low_quality",
                        "spectrum": spectrum,
                        "severity": "high",
                        "mean_score": stats["mean"],
                        "description": f"Mean quality below 90% ({stats['mean']:.3f})",  # noqa: E501
                    }
                )

            if stats.get("std", 0) > 0.05:
                issues.append(
                    {
                        "type": "high_variance",
                        "spectrum": spectrum,
                        "severity": "medium",
                        "std_score": stats["std"],
                        "description": f"High score variance ({stats['std']:.3f})",
                    }
                )

        return issues

    def _generate_recommendations(self, spectrum_stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on statistics."""
        recommendations = []

        low_quality_spectrums = [
            spectrum for spectrum, stats in spectrum_stats.items() if stats.get("mean", 1.0) < 0.95
        ]

        if low_quality_spectrums:
            recommendations.append(f"Consider optimization for: {', '.join(low_quality_spectrums)}")  # noqa: E501

        high_variance_spectrums = [spectrum for spectrum, stats in spectrum_stats.items() if stats.get("std", 0) > 0.03]

        if high_variance_spectrums:
            recommendations.append(f"Improve consistency for: {', '.join(high_variance_spectrums)}")  # noqa: E501

        if not recommendations:
            recommendations.append("Quality metrics look good! Continue monitoring.")  # noqa: E501

        return recommendations


class QualityMetricsCollector:
    """Main collector that integrates with the virtuous cycle framework."""

    def __init__(self, virtuous_cycle_framework=None):
        """Initialize the quality metrics collector."""
        self.storage = LightweightMetricsStorage()
        self.analytics = QualityAnalytics(self.storage)
        self.virtuous_cycle = virtuous_cycle_framework

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Collection settings
        self.auto_feed_enabled = True
        self.feed_interval_minutes = 15

    def collect_langsmith_metrics(self, langsmith_data: List[Dict[str, Any]]):
        """Collect metrics from LangSmith traces."""
        for trace_data in langsmith_data:
            try:
                # Extract quality score from LangSmith trace
                quality_score = self._extract_quality_from_trace(trace_data)
                if quality_score is not None:
                    spectrum = trace_data.get("metadata", {}).get("spectrum", "general")  # noqa: E501
                    model = trace_data.get("metadata", {}).get("model", "unknown")  # noqa: E501

                    metric = QualityMetric(
                        spectrum=spectrum,
                        score=quality_score,
                        source="langsmith",
                        model=model,
                        metadata=trace_data.get("metadata", {}),
                    )
                    self.storage.add_metric(metric)
                    self.logger.info(f"Collected LangSmith metric: {spectrum} = {quality_score:.3f}")  # noqa: E501

            except Exception as e:
                self.logger.error(f"Error collecting LangSmith metric: {e}")

    def collect_direct_test_result(
        self, spectrum: str, score: float, model: str | None = None, metadata: Dict[str, Any] | None = None
    ):
        """Collect metrics from direct testing."""
        metric = QualityMetric(
            spectrum=spectrum, score=score, source="direct_test", model=model, metadata=metadata or {}
        )
        self.storage.add_metric(metric)
        self.logger.info(f"Collected direct test metric: {spectrum} = {score:.3f}")  # noqa: E501

        # Auto-feed to virtuous cycle if enabled
        if self.auto_feed_enabled and self.virtuous_cycle:
            self._feed_to_virtuous_cycle(metric)

    def collect_user_feedback(self, spectrum: str, satisfaction_score: float, context: Dict[str, Any] | None = None):
        """Collect metrics from user feedback."""
        # Convert satisfaction (1-5) to quality score (0-1)
        quality_score = satisfaction_score / 5.0

        metric = QualityMetric(spectrum=spectrum, score=quality_score, source="user_feedback", metadata=context or {})
        self.storage.add_metric(metric)
        self.logger.info(f"Collected user feedback: {spectrum} = {quality_score:.3f}")  # noqa: E501

    def generate_analytics_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive analytics report."""
        return self.analytics.generate_quality_report(hours)

    def get_spectrum_analytics(self, spectrum: str, hours: int = 24) -> Dict[str, Any]:
        """Get analytics for a specific spectrum."""
        return self.analytics.calculate_spectrum_statistics(spectrum, hours)

    def feed_to_virtuous_cycle(self, spectrum: str | None = None):
        """Manually feed recent metrics to virtuous cycle framework."""
        if not self.virtuous_cycle:
            self.logger.warning("No virtuous cycle framework configured")
            return

        # Get recent metrics
        if spectrum:
            recent_metrics = self.storage.get_spectrum_metrics(spectrum)
        else:
            recent_metrics = self.storage.get_recent_metrics()

        # Feed to virtuous cycle trend analyzer
        trend_analyzer = self.virtuous_cycle.optimization_engine.trend_analyzer

        for metric in recent_metrics:
            trend_analyzer.add_score(
                spectrum=metric.spectrum, score=metric.score, timestamp=metric.timestamp, metadata=metric.metadata
            )

        self.logger.info(f"Fed {len(recent_metrics)} metrics to virtuous cycle")  # noqa: E501

    def _extract_quality_from_trace(self, trace_data: Dict[str, Any]) -> float | None:
        """Extract quality score from LangSmith trace data."""
        # Look for quality indicators in trace
        metadata = trace_data.get("metadata", {})

        # Check for explicit quality score
        if "quality_score" in metadata:
            return float(metadata["quality_score"])

        # Estimate quality from other indicators
        error_count = metadata.get("error_count", 0)
        response_time = metadata.get("response_time", 0)

        if error_count > 0:
            return 0.5  # Poor quality if errors present

        # Simple heuristic based on response time
        if response_time < 1000:  # Fast response
            return 0.95
        elif response_time < 3000:  # Acceptable response
            return 0.90
        else:  # Slow response
            return 0.80

    def _feed_to_virtuous_cycle(self, metric: QualityMetric):
        """Feed individual metric to virtuous cycle."""
        if self.virtuous_cycle:
            trend_analyzer = self.virtuous_cycle.optimization_engine.trend_analyzer
            trend_analyzer.add_score(
                spectrum=metric.spectrum, score=metric.score, timestamp=metric.timestamp, metadata=metric.metadata
            )


async def demo_quality_metrics_collector():
    """Demonstrate the quality metrics collector."""
    print("🔍 Initializing Quality Metrics Collector...")

    # Create collector
    collector = QualityMetricsCollector()

    # Simulate collecting various metrics
    print("📊 Simulating metric collection...")

    # Direct test results
    spectrums = [
        "customer_identity_resolution",
        "financial_analysis_depth",
        "multi_field_data_integration",
        "conversational_context_handling",
    ]

    models = ["gpt-4o-mini", "llama-3.3-70b-versatile"]

    # Collect sample metrics
    for spectrum in spectrums:
        for model in models:
            # Simulate varying quality scores
            base_score = 0.95 + (hash(spectrum + model) % 50) / 1000
            collector.collect_direct_test_result(
                spectrum=spectrum, score=base_score, model=model, metadata={"test_run": "demo", "version": "1.0"}
            )

    # Simulate user feedback
    collector.collect_user_feedback(
        spectrum="professional_communication",
        satisfaction_score=4.5,  # 5-point scale
        context={"user_type": "business", "query_complexity": "medium"},
    )

    # Generate analytics
    print("\n📈 Generating Analytics Report...")
    report = collector.generate_analytics_report(hours=1)

    print("\n" + "=" * 60)
    print("🎯 QUALITY METRICS ANALYTICS REPORT")
    print("=" * 60)
    print(f"📊 Total Measurements: {report['total_measurements']}")
    print(f"🎯 Spectrums Measured: {report['spectrums_measured']}")
    print(f"⭐ Overall Mean Quality: {report['overall_statistics']['mean']:.3f}")  # noqa: E501

    if report["quality_issues"]:
        print(f"\n⚠️  Quality Issues Found: {len(report['quality_issues'])}")
        for issue in report["quality_issues"][:3]:  # Show first 3
            print(f"  • {issue['description']}")

    print("\n💡 Recommendations:")
    for rec in report["recommendations"]:
        print(f"  • {rec}")

    print("=" * 60)

    return collector


if __name__ == "__main__":
    asyncio.run(demo_quality_metrics_collector())
