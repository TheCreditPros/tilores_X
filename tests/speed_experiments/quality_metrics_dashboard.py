#!/usr/bin/env python3
"""
Quality Metrics Dashboard for 90%+ Achievement System.

This module implements a comprehensive quality metrics dashboard targeting
90%+ quality achievement across the 7-model LangSmith framework with
real-time monitoring, alerting, and performance analytics.

Author: Roo (tilores_X Development Team)
Date: August 16, 2025
Version: 1.0.0
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
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


class MetricType(Enum):
    """Types of quality metrics tracked by the system."""

    OVERALL_QUALITY = "overall_quality"
    MODEL_PERFORMANCE = "model_performance"
    SPECTRUM_ACCURACY = "spectrum_accuracy"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    USER_SATISFACTION = "user_satisfaction"
    DATA_COMPLETENESS = "data_completeness"
    CONSISTENCY_SCORE = "consistency_score"


class AlertLevel(Enum):
    """Alert severity levels for quality monitoring."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class TrendDirection(Enum):
    """Trend direction indicators for metrics."""

    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"


@dataclass
class QualityMetric:
    """Individual quality metric data point."""

    metric_id: str
    metric_type: MetricType
    value: float
    target: float
    timestamp: datetime
    model_name: Optional[str] = None
    spectrum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def achievement_rate(self) -> float:
        """Calculate achievement rate as percentage of target."""
        return (self.value / self.target) * 100 if self.target > 0 else 0.0

    @property
    def meets_target(self) -> bool:
        """Check if metric meets or exceeds target."""
        return self.value >= self.target

    @property
    def deviation_from_target(self) -> float:
        """Calculate deviation from target (positive = above target)."""
        return self.value - self.target


@dataclass
class QualityAlert:
    """Quality alert for monitoring system."""

    alert_id: str
    level: AlertLevel
    metric_type: MetricType
    message: str
    current_value: float
    target_value: float
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Trend analysis for quality metrics."""

    metric_type: MetricType
    direction: TrendDirection
    slope: float
    confidence: float
    data_points: int
    time_period: timedelta
    prediction: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)


class QualityMetricsCollector:
    """Collector for quality metrics from various sources."""

    def __init__(self):
        """Initialize the quality metrics collector."""
        self.metrics: List[QualityMetric] = []
        self.collection_interval = 60  # seconds
        self.max_history = 10000  # maximum metrics to keep in memory

        logger.info("Initialized QualityMetricsCollector")

    def collect_metric(
        self,
        metric_type: MetricType,
        value: float,
        target: float,
        model_name: Optional[str] = None,
        spectrum: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QualityMetric:
        """
        Collect a quality metric data point.

        Args:
            metric_type: Type of metric being collected
            value: Current metric value
            target: Target value for the metric
            model_name: Optional model name for model-specific metrics
            spectrum: Optional spectrum name for spectrum-specific metrics
            metadata: Optional additional metadata

        Returns:
            QualityMetric object representing the collected data point
        """
        metric_id = f"{metric_type.value}_{int(time.time())}"

        metric = QualityMetric(
            metric_id=metric_id,
            metric_type=metric_type,
            value=value,
            target=target,
            timestamp=datetime.now(),
            model_name=model_name,
            spectrum=spectrum,
            metadata=metadata or {},
        )

        self.metrics.append(metric)

        # Maintain maximum history size
        if len(self.metrics) > self.max_history:
            self.metrics = self.metrics[-self.max_history:]

        logger.debug(f"Collected metric {metric_id}: {value:.3f} " f"(target: {target:.3f})")

        return metric

    def get_metrics_by_type(self, metric_type: MetricType, hours: int = 24) -> List[QualityMetric]:
        """Get metrics of a specific type within time window."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self.metrics if m.metric_type == metric_type and m.timestamp >= cutoff_time]

    def get_metrics_by_model(self, model_name: str, hours: int = 24) -> List[QualityMetric]:
        """Get metrics for a specific model within time window."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self.metrics if m.model_name == model_name and m.timestamp >= cutoff_time]

    def get_latest_metrics(self, count: int = 100) -> List[QualityMetric]:
        """Get the most recent metrics."""
        return sorted(self.metrics, key=lambda x: x.timestamp, reverse=True)[:count]


class TrendAnalyzer:
    """Analyzer for quality metric trends and predictions."""

    def __init__(self):
        """Initialize the trend analyzer."""
        self.min_data_points = 5
        self.confidence_threshold = 0.7

        logger.info("Initialized TrendAnalyzer")

    def analyze_trend(self, metrics: List[QualityMetric]) -> Optional[TrendAnalysis]:
        """
        Analyze trend for a list of metrics.

        Args:
            metrics: List of quality metrics to analyze

        Returns:
            TrendAnalysis object or None if insufficient data
        """
        if len(metrics) < self.min_data_points:
            return None

        # Sort metrics by timestamp
        sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)

        # Extract values and timestamps
        values = [m.value for m in sorted_metrics]
        timestamps = [(m.timestamp - sorted_metrics[0].timestamp).total_seconds() for m in sorted_metrics]

        # Calculate trend using linear regression
        slope, confidence = self._calculate_linear_trend(timestamps, values)

        # Determine trend direction
        direction = self._determine_trend_direction(slope, confidence)

        # Calculate time period
        time_period = sorted_metrics[-1].timestamp - sorted_metrics[0].timestamp

        # Generate prediction for next data point
        prediction = None
        if confidence >= self.confidence_threshold:
            # Predict value 1 hour ahead
            prediction = values[-1] + (slope * 3600)

        return TrendAnalysis(
            metric_type=sorted_metrics[0].metric_type,
            direction=direction,
            slope=slope,
            confidence=confidence,
            data_points=len(metrics),
            time_period=time_period,
            prediction=prediction,
        )

    def _calculate_linear_trend(self, x_values: List[float], y_values: List[float]) -> tuple[float, float]:
        """Calculate linear trend slope and confidence."""
        if NUMPY_AVAILABLE:
            # Use numpy for more accurate calculation
            x_array = np.array(x_values)
            y_array = np.array(y_values)

            # Calculate linear regression
            coeffs = np.polyfit(x_array, y_array, 1)
            slope = coeffs[0]

            # Calculate R-squared for confidence
            y_pred = np.polyval(coeffs, x_array)
            ss_res = np.sum((y_array - y_pred) ** 2)
            ss_tot = np.sum((y_array - np.mean(y_array)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            confidence = max(0.0, min(1.0, r_squared))
        else:
            # Fallback to simple linear regression
            n = len(x_values)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)

            # Calculate slope
            denominator = n * sum_x2 - sum_x * sum_x
            if denominator == 0:
                slope = 0.0
                confidence = 0.0
            else:
                slope = (n * sum_xy - sum_x * sum_y) / denominator

                # Simple confidence based on data consistency
                mean_y = sum_y / n
                variance = sum((y - mean_y) ** 2 for y in y_values) / n
                confidence = max(0.0, min(1.0, 1.0 - (variance / (mean_y**2)) if mean_y != 0 else 0.0))

        return slope, confidence

    def _determine_trend_direction(self, slope: float, confidence: float) -> TrendDirection:
        """Determine trend direction based on slope and confidence."""
        if confidence < 0.5:
            return TrendDirection.VOLATILE

        if abs(slope) < 0.001:  # Very small slope
            return TrendDirection.STABLE
        elif slope > 0:
            return TrendDirection.IMPROVING
        else:
            return TrendDirection.DECLINING


class AlertSystem:
    """Alert system for quality monitoring."""

    def __init__(self, target_quality: float = 0.90):
        """
        Initialize the alert system.

        Args:
            target_quality: Overall target quality threshold
        """
        self.target_quality = target_quality
        self.alerts: List[QualityAlert] = []
        self.alert_thresholds = {
            AlertLevel.INFO: 0.05,  # 5% below target
            AlertLevel.WARNING: 0.10,  # 10% below target
            AlertLevel.CRITICAL: 0.15,  # 15% below target
            AlertLevel.EMERGENCY: 0.20,  # 20% below target
        }

        logger.info(f"Initialized AlertSystem with target quality: {target_quality}")

    def check_metric_alerts(self, metric: QualityMetric) -> Optional[QualityAlert]:
        """
        Check if a metric triggers any alerts.

        Args:
            metric: Quality metric to check

        Returns:
            QualityAlert if alert is triggered, None otherwise
        """
        if metric.meets_target:
            return None

        # Calculate deviation percentage
        deviation = abs(metric.deviation_from_target) / metric.target

        # Determine alert level
        alert_level = None
        for level in [AlertLevel.EMERGENCY, AlertLevel.CRITICAL, AlertLevel.WARNING, AlertLevel.INFO]:
            if deviation >= self.alert_thresholds[level]:
                alert_level = level
                break

        if alert_level is None:
            return None

        # Create alert
        alert_id = f"alert_{metric.metric_id}_{int(time.time())}"
        message = self._generate_alert_message(metric, alert_level, deviation)

        alert = QualityAlert(
            alert_id=alert_id,
            level=alert_level,
            metric_type=metric.metric_type,
            message=message,
            current_value=metric.value,
            target_value=metric.target,
            metadata={
                "metric_id": metric.metric_id,
                "model_name": metric.model_name,
                "spectrum": metric.spectrum,
                "deviation_percent": deviation * 100,
            },
        )

        self.alerts.append(alert)

        logger.warning(f"Alert triggered: {alert.level.value} - {message}")

        return alert

    def _generate_alert_message(self, metric: QualityMetric, level: AlertLevel, deviation: float) -> str:
        """Generate alert message based on metric and level."""
        base_msg = f"{metric.metric_type.value} below target"

        if metric.model_name:
            base_msg += f" for model {metric.model_name}"

        if metric.spectrum:
            base_msg += f" in spectrum {metric.spectrum}"

        base_msg += f": {metric.value:.3f} vs target {metric.target:.3f}"
        base_msg += f" ({deviation * 100:.1f}% below)"

        return base_msg

    def get_active_alerts(self, level: Optional[AlertLevel] = None) -> List[QualityAlert]:
        """Get active (unresolved) alerts, optionally filtered by level."""
        active_alerts = [a for a in self.alerts if not a.resolved]

        if level:
            active_alerts = [a for a in active_alerts if a.level == level]

        return sorted(active_alerts, key=lambda x: x.timestamp, reverse=True)

    def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved."""
        for alert in self.alerts:
            if alert.alert_id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolution_timestamp = datetime.now()
                logger.info(f"Alert {alert_id} resolved")
                return True
        return False


class QualityDashboard:
    """
    Comprehensive quality metrics dashboard for 90%+ achievement system.

    Provides real-time monitoring, trend analysis, and alerting for quality
    metrics across the 7-model LangSmith framework.
    """

    def __init__(self, target_quality: float = 0.90):
        """
        Initialize the quality dashboard.

        Args:
            target_quality: Overall target quality threshold (default: 0.90)
        """
        self.target_quality = target_quality
        self.collector = QualityMetricsCollector()
        self.trend_analyzer = TrendAnalyzer()
        self.alert_system = AlertSystem(target_quality)

        # Model configuration
        self.models = [
            "gemini-1.5-flash-002",
            "claude-3-haiku",
            "llama-3.3-70b-versatile",
            "gpt-4o-mini",
            "deepseek-r1-distill-llama-70b",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
        ]

        # Data spectrum configuration
        self.spectrums = [
            "customer_identity",
            "financial_profile",
            "contact_information",
            "transaction_history",
            "relationship_mapping",
            "risk_assessment",
            "behavioral_analytics",
        ]

        logger.info(f"Initialized QualityDashboard with target: {target_quality}")

    async def collect_system_metrics(self) -> Dict[str, Any]:
        """
        Collect comprehensive system metrics.

        Returns:
            Dictionary containing collected metrics summary
        """
        logger.info("Collecting system metrics")

        collected_metrics = []

        # Collect overall quality metrics
        overall_quality = await self._simulate_overall_quality()
        metric = self.collector.collect_metric(
            MetricType.OVERALL_QUALITY,
            overall_quality,
            self.target_quality,
            metadata={"collection_type": "system_wide"},
        )
        collected_metrics.append(metric)

        # Check for alerts
        alert = self.alert_system.check_metric_alerts(metric)
        if alert:
            collected_metrics.append(f"Alert: {alert.message}")

        # Collect model-specific metrics
        for model in self.models:
            model_quality = await self._simulate_model_quality(model)
            metric = self.collector.collect_metric(
                MetricType.MODEL_PERFORMANCE,
                model_quality,
                self.target_quality,
                model_name=model,
                metadata={"collection_type": "model_specific"},
            )
            collected_metrics.append(metric)

            # Check for model-specific alerts
            alert = self.alert_system.check_metric_alerts(metric)
            if alert:
                collected_metrics.append(f"Model Alert: {alert.message}")

        # Collect spectrum-specific metrics
        for spectrum in self.spectrums:
            spectrum_quality = await self._simulate_spectrum_quality(spectrum)
            metric = self.collector.collect_metric(
                MetricType.SPECTRUM_ACCURACY,
                spectrum_quality,
                self.target_quality,
                spectrum=spectrum,
                metadata={"collection_type": "spectrum_specific"},
            )
            collected_metrics.append(metric)

        return {
            "collection_timestamp": datetime.now().isoformat(),
            "metrics_collected": len([m for m in collected_metrics if isinstance(m, QualityMetric)]),
            "alerts_generated": len([m for m in collected_metrics if isinstance(m, str)]),
            "overall_quality": overall_quality,
            "target_achieved": overall_quality >= self.target_quality,
        }

    async def _simulate_overall_quality(self) -> float:
        """Simulate overall system quality (replace with real metrics)."""
        # Simulate quality with some variance around target
        import random

        base_quality = self.target_quality
        variance = random.uniform(-0.05, 0.08)  # Slight positive bias
        return max(0.0, min(1.0, base_quality + variance))

    async def _simulate_model_quality(self, model_name: str) -> float:
        """Simulate model-specific quality (replace with real metrics)."""
        import random

        # Different models have different baseline performance
        model_baselines = {
            "gemini-1.5-flash-002": 0.95,
            "claude-3-haiku": 0.92,
            "llama-3.3-70b-versatile": 0.90,
            "gpt-4o-mini": 0.94,
            "deepseek-r1-distill-llama-70b": 0.89,
            "gemini-2.5-flash": 0.96,
            "gemini-2.5-flash-lite": 0.93,
        }

        baseline = model_baselines.get(model_name, self.target_quality)
        variance = random.uniform(-0.03, 0.02)
        return max(0.0, min(1.0, baseline + variance))

    async def _simulate_spectrum_quality(self, spectrum: str) -> float:
        """Simulate spectrum-specific quality (replace with real metrics)."""
        import random

        # Different spectrums have different complexity/quality profiles
        spectrum_baselines = {
            "customer_identity": 0.95,
            "financial_profile": 0.92,
            "contact_information": 0.88,
            "transaction_history": 0.85,
            "relationship_mapping": 0.80,
            "risk_assessment": 0.90,
            "behavioral_analytics": 0.75,
        }

        baseline = spectrum_baselines.get(spectrum, self.target_quality)
        variance = random.uniform(-0.04, 0.03)
        return max(0.0, min(1.0, baseline + variance))

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """
        Generate comprehensive dashboard data.

        Returns:
            Dictionary containing complete dashboard information
        """
        logger.info("Generating dashboard data")

        # Get recent metrics
        recent_metrics = self.collector.get_latest_metrics(100)

        # Calculate overall statistics
        overall_metrics = self.collector.get_metrics_by_type(MetricType.OVERALL_QUALITY, 24)
        current_quality = overall_metrics[-1].value if overall_metrics else 0.0

        # Model performance breakdown
        model_performance = {}
        for model in self.models:
            model_metrics = self.collector.get_metrics_by_model(model, 24)
            if model_metrics:
                avg_quality = sum(m.value for m in model_metrics) / len(model_metrics)
                model_performance[model] = {
                    "average_quality": avg_quality,
                    "meets_target": avg_quality >= self.target_quality,
                    "data_points": len(model_metrics),
                }

        # Spectrum performance breakdown
        spectrum_performance = {}
        for spectrum in self.spectrums:
            spectrum_metrics = [m for m in recent_metrics if m.spectrum == spectrum]
            if spectrum_metrics:
                avg_quality = sum(m.value for m in spectrum_metrics) / len(spectrum_metrics)
                spectrum_performance[spectrum] = {
                    "average_quality": avg_quality,
                    "meets_target": avg_quality >= self.target_quality,
                    "data_points": len(spectrum_metrics),
                }

        # Trend analysis
        trend_analysis = {}
        if len(overall_metrics) >= 5:
            trend = self.trend_analyzer.analyze_trend(overall_metrics)
            if trend:
                trend_analysis = {
                    "direction": trend.direction.value,
                    "confidence": trend.confidence,
                    "prediction": trend.prediction,
                }

        # Active alerts
        active_alerts = self.alert_system.get_active_alerts()
        alert_summary = {
            "total_active": len(active_alerts),
            "by_level": {level.value: len([a for a in active_alerts if a.level == level]) for level in AlertLevel},
        }

        # Achievement statistics
        total_metrics = len(recent_metrics)
        meeting_target = len([m for m in recent_metrics if m.meets_target])
        achievement_rate = (meeting_target / total_metrics * 100) if total_metrics > 0 else 0

        return {
            "dashboard_timestamp": datetime.now().isoformat(),
            "target_quality": self.target_quality,
            "current_quality": current_quality,
            "achievement_rate": achievement_rate,
            "target_achieved": current_quality >= self.target_quality,
            "model_performance": model_performance,
            "spectrum_performance": spectrum_performance,
            "trend_analysis": trend_analysis,
            "alert_summary": alert_summary,
            "recent_metrics_count": len(recent_metrics),
            "models_above_target": len([m for m, p in model_performance.items() if p["meets_target"]]),
            "spectrums_above_target": len([s for s, p in spectrum_performance.items() if p["meets_target"]]),
        }

    def export_dashboard_data(self, filename: str) -> None:
        """Export dashboard data to JSON file."""
        dashboard_data = self.generate_dashboard_data()

        # Add detailed metrics for export
        dashboard_data["detailed_metrics"] = [
            {
                "metric_id": m.metric_id,
                "type": m.metric_type.value,
                "value": m.value,
                "target": m.target,
                "achievement_rate": m.achievement_rate,
                "model_name": m.model_name,
                "spectrum": m.spectrum,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in self.collector.get_latest_metrics(500)
        ]

        # Add alert details
        dashboard_data["detailed_alerts"] = [
            {
                "alert_id": a.alert_id,
                "level": a.level.value,
                "metric_type": a.metric_type.value,
                "message": a.message,
                "current_value": a.current_value,
                "target_value": a.target_value,
                "resolved": a.resolved,
                "timestamp": a.timestamp.isoformat(),
            }
            for a in self.alert_system.alerts
        ]

        with open(filename, "w") as f:
            json.dump(dashboard_data, f, indent=2)

        logger.info(f"Dashboard data exported to {filename}")


# Example usage and testing
async def main():
    """Example usage of the Quality Metrics Dashboard."""
    # Initialize dashboard
    dashboard = QualityDashboard(target_quality=0.90)

    # Simulate metric collection over time
    print("=== Quality Metrics Dashboard - 90%+ Achievement System ===")
    print("Collecting system metrics...")

    # Collect metrics multiple times to simulate real usage
    for i in range(5):
        metrics_summary = await dashboard.collect_system_metrics()
        print(f"\nCollection {i + 1}:")
        print(f"  Overall Quality: {metrics_summary['overall_quality']:.3f}")
        print(f"  Target Achieved: {metrics_summary['target_achieved']}")
        print(f"  Metrics Collected: {metrics_summary['metrics_collected']}")
        print(f"  Alerts Generated: {metrics_summary['alerts_generated']}")

        # Small delay to simulate time passage
        await asyncio.sleep(0.1)

    # Generate comprehensive dashboard
    dashboard_data = dashboard.generate_dashboard_data()

    print("\n=== Dashboard Summary ===")
    print(f"Current Quality: {dashboard_data['current_quality']:.3f}")
    print(f"Achievement Rate: {dashboard_data['achievement_rate']:.1f}%")
    print(f"Models Above Target: {dashboard_data['models_above_target']}/7")
    print(f"Spectrums Above Target: {dashboard_data['spectrums_above_target']}/7")

    print("\nModel Performance:")
    for model, perf in dashboard_data["model_performance"].items():
        status = "✅" if perf["meets_target"] else "❌"
        print(f"  {status} {model}: {perf['average_quality']:.3f}")

    print("\nSpectrum Performance:")
    for spectrum, perf in dashboard_data["spectrum_performance"].items():
        status = "✅" if perf["meets_target"] else "❌"
        print(f"  {status} {spectrum}: {perf['average_quality']:.3f}")

    # Show active alerts
    active_alerts = dashboard.alert_system.get_active_alerts()
    if active_alerts:
        print(f"\nActive Alerts ({len(active_alerts)}):")
        for alert in active_alerts[:5]:  # Show first 5
            print(f"  {alert.level.value.upper()}: {alert.message}")
    else:
        print("\nNo active alerts - system performing well!")

    # Export dashboard data
    dashboard.export_dashboard_data("quality_dashboard_export.json")
    print("\nDashboard data exported to quality_dashboard_export.json")

    return dashboard


if __name__ == "__main__":
    asyncio.run(main())
