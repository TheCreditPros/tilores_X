#!/usr/bin/env python3
"""
Multi-Tier Quality Threshold and Alerting System

Implements enterprise-grade quality monitoring with configurable thresholds,
alerting, and dashboard integration for the Virtuous Cycle framework.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from collections import deque
import json
import asyncio

# Optional imports for Redis and notifications
try:
    from redis_cache import cache_manager

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    cache_manager = None

try:
    import smtplib  # noqa: F401
    from email.mime.text import MIMEText  # noqa: F401
    from email.mime.multipart import MIMEMultipart  # noqa: F401

    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False


class QualityLevel(Enum):
    """Quality level enumeration for threshold classification."""

    CRITICAL = "critical"  # Below 85% - Immediate action required
    WARNING = "warning"  # 85-90% - Attention needed
    TARGET = "target"  # 90-95% - Meeting expectations
    EXCELLENT = "excellent"  # 95%+ - Exceeding expectations


class AlertSeverity(Enum):
    """Alert severity levels for notification prioritization."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class QualityThreshold:
    """Configuration for a quality threshold level."""

    level: QualityLevel
    min_value: float
    max_value: float
    alert_severity: AlertSeverity
    alert_message: str
    cooldown_minutes: int = 60
    notification_channels: List[str] = field(default_factory=list)


@dataclass
class QualityAlert:
    """Quality alert with metadata and tracking."""

    alert_id: str
    threshold_level: QualityLevel
    severity: AlertSeverity
    current_value: float
    threshold_value: float
    message: str
    timestamp: datetime
    spectrum: str = "overall"
    provider: str = "unknown"
    resolved: bool = False
    resolved_timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityMetrics:
    """Quality metrics snapshot for dashboard and monitoring."""

    timestamp: datetime
    overall_quality: float
    spectrum_qualities: Dict[str, float] = field(default_factory=dict)
    provider_qualities: Dict[str, float] = field(default_factory=dict)
    active_alerts: List[QualityAlert] = field(default_factory=list)
    trend_direction: str = "stable"  # up, down, stable
    last_optimization: Optional[datetime] = None


class MultiTierQualityMonitor:
    """
    Enterprise-grade multi-tier quality threshold monitoring system.

    Features:
    - Configurable threshold levels (critical, warning, target, excellent)
    - Real-time alerting with severity classification
    - Dashboard integration and metrics collection
    - Trend analysis and predictive monitoring
    - Notification system with multiple channels
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the multi-tier quality monitor."""
        self.logger = logging.getLogger(__name__)

        # Load configuration
        self.config = config or self._default_config()

        # Initialize thresholds
        self.thresholds = self._initialize_thresholds()

        # Alert tracking
        self.active_alerts: Dict[str, QualityAlert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        self.cooldown_tracking: Dict[str, datetime] = {}

        # Metrics storage
        self.metrics_history: deque = deque(maxlen=2880)  # 48 hours at 1-min intervals
        self.current_metrics = QualityMetrics(timestamp=datetime.now(), overall_quality=0.0)

        # Notification system
        self.notification_channels = self._initialize_notifications()

        self.logger.info("✅ Multi-tier quality monitor initialized")
        self.logger.info(f"📊 Thresholds: {[t.level.value for t in self.thresholds]}")

    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for quality monitoring."""
        return {
            "thresholds": {
                "critical": {"min": 0.0, "max": 0.85, "cooldown": 30},
                "warning": {"min": 0.85, "max": 0.90, "cooldown": 60},
                "target": {"min": 0.90, "max": 0.95, "cooldown": 120},
                "excellent": {"min": 0.95, "max": 1.0, "cooldown": 240},
            },
            "monitoring": {"trend_analysis_points": 10, "variance_threshold": 0.05, "prediction_window_minutes": 30},
            "notifications": {"email_enabled": False, "dashboard_alerts": True, "redis_persistence": True},
        }

    def _initialize_thresholds(self) -> List[QualityThreshold]:
        """Initialize quality threshold configurations."""
        threshold_configs = self.config.get("thresholds", {})

        thresholds = [
            QualityThreshold(
                level=QualityLevel.CRITICAL,
                min_value=threshold_configs.get("critical", {}).get("min", 0.0),
                max_value=threshold_configs.get("critical", {}).get("max", 0.85),
                alert_severity=AlertSeverity.CRITICAL,
                alert_message="Quality critically low - immediate intervention required",
                cooldown_minutes=threshold_configs.get("critical", {}).get("cooldown", 30),
                notification_channels=["dashboard", "email", "redis"],
            ),
            QualityThreshold(
                level=QualityLevel.WARNING,
                min_value=threshold_configs.get("warning", {}).get("min", 0.85),
                max_value=threshold_configs.get("warning", {}).get("max", 0.90),
                alert_severity=AlertSeverity.HIGH,
                alert_message="Quality below target - optimization recommended",
                cooldown_minutes=threshold_configs.get("warning", {}).get("cooldown", 60),
                notification_channels=["dashboard", "redis"],
            ),
            QualityThreshold(
                level=QualityLevel.TARGET,
                min_value=threshold_configs.get("target", {}).get("min", 0.90),
                max_value=threshold_configs.get("target", {}).get("max", 0.95),
                alert_severity=AlertSeverity.MEDIUM,
                alert_message="Quality meeting target expectations",
                cooldown_minutes=threshold_configs.get("target", {}).get("cooldown", 120),
                notification_channels=["dashboard"],
            ),
            QualityThreshold(
                level=QualityLevel.EXCELLENT,
                min_value=threshold_configs.get("excellent", {}).get("min", 0.95),
                max_value=threshold_configs.get("excellent", {}).get("max", 1.0),
                alert_severity=AlertSeverity.LOW,
                alert_message="Quality exceeding expectations - excellent performance",
                cooldown_minutes=threshold_configs.get("excellent", {}).get("cooldown", 240),
                notification_channels=["dashboard"],
            ),
        ]

        return thresholds

    def _initialize_notifications(self) -> Dict[str, Any]:
        """Initialize notification channels."""
        return {
            "dashboard": True,
            "redis": REDIS_AVAILABLE and self.config.get("notifications", {}).get("redis_persistence", True),
            "email": EMAIL_AVAILABLE and self.config.get("notifications", {}).get("email_enabled", False),
        }

    async def check_quality_thresholds(
        self,
        overall_quality: float,
        spectrum_qualities: Optional[Dict[str, float]] = None,
        provider_qualities: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[QualityAlert]:
        """
        Check quality against all thresholds and generate alerts.

        Args:
            overall_quality: Overall system quality score (0.0-1.0)
            spectrum_qualities: Quality scores by spectrum
            provider_qualities: Quality scores by provider
            metadata: Additional context for alerts

        Returns:
            List of new alerts generated
        """
        alerts_generated = []
        current_time = datetime.now()

        # Update current metrics
        self.current_metrics = QualityMetrics(
            timestamp=current_time,
            overall_quality=overall_quality,
            spectrum_qualities=spectrum_qualities or {},
            provider_qualities=provider_qualities or {},
            trend_direction=self._calculate_trend(),
        )

        # Store metrics for trending
        self.metrics_history.append(self.current_metrics)

        # Check overall quality thresholds
        alert = self._check_single_threshold(
            value=overall_quality, spectrum="overall", provider="system", metadata=metadata or {}
        )

        if alert:
            alerts_generated.append(alert)

        # Check spectrum-specific thresholds
        if spectrum_qualities:
            for spectrum, quality in spectrum_qualities.items():
                alert = self._check_single_threshold(
                    value=quality, spectrum=spectrum, provider="system", metadata=metadata or {}
                )
                if alert:
                    alerts_generated.append(alert)

        # Check provider-specific thresholds
        if provider_qualities:
            for provider, quality in provider_qualities.items():
                alert = self._check_single_threshold(
                    value=quality, spectrum="overall", provider=provider, metadata=metadata or {}
                )
                if alert:
                    alerts_generated.append(alert)

        # Update active alerts
        self.current_metrics.active_alerts = list(self.active_alerts.values())

        # Persist metrics if Redis available
        await self._persist_metrics()

        return alerts_generated

    def _check_single_threshold(
        self, value: float, spectrum: str, provider: str, metadata: Dict[str, Any]
    ) -> Optional[QualityAlert]:
        """Check a single quality value against thresholds."""

        # Find applicable threshold
        applicable_threshold = None
        for threshold in self.thresholds:
            if threshold.min_value <= value < threshold.max_value:
                applicable_threshold = threshold
                break

        if not applicable_threshold:
            return None

        # Check if we need to alert (considering cooldown)
        alert_key = f"{spectrum}:{provider}:{applicable_threshold.level.value}"

        if not self._should_alert(alert_key, applicable_threshold.cooldown_minutes):
            return None

        # Create new alert
        alert_id = f"{alert_key}:{int(time.time())}"
        alert = QualityAlert(
            alert_id=alert_id,
            threshold_level=applicable_threshold.level,
            severity=applicable_threshold.alert_severity,
            current_value=value,
            threshold_value=applicable_threshold.min_value,
            message=f"{applicable_threshold.alert_message} (Quality: {value:.1%})",
            timestamp=datetime.now(),
            spectrum=spectrum,
            provider=provider,
            metadata=metadata,
        )

        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        self.cooldown_tracking[alert_key] = datetime.now()

        # Send notifications
        asyncio.create_task(self._send_notifications(alert))

        self.logger.info(f"🚨 Quality alert: {alert.threshold_level.value} - {alert.message}")

        return alert

    def _should_alert(self, alert_key: str, cooldown_minutes: int) -> bool:
        """Check if we should generate an alert considering cooldown."""
        if alert_key not in self.cooldown_tracking:
            return True

        last_alert_time = self.cooldown_tracking[alert_key]
        cooldown_period = timedelta(minutes=cooldown_minutes)

        return datetime.now() - last_alert_time >= cooldown_period

    def _calculate_trend(self) -> str:
        """Calculate quality trend direction."""
        if len(self.metrics_history) < 5:
            return "stable"

        recent_metrics = list(self.metrics_history)[-5:]
        qualities = [m.overall_quality for m in recent_metrics]

        # Simple trend calculation
        first_half_avg = sum(qualities[:2]) / 2
        second_half_avg = sum(qualities[-2:]) / 2

        difference = second_half_avg - first_half_avg

        if difference > 0.02:  # 2% improvement
            return "up"
        elif difference < -0.02:  # 2% degradation
            return "down"
        else:
            return "stable"

    async def _send_notifications(self, alert: QualityAlert):
        """Send notifications for an alert."""
        try:
            applicable_threshold = next(t for t in self.thresholds if t.level == alert.threshold_level)

            # Dashboard notification (always enabled)
            if "dashboard" in applicable_threshold.notification_channels:
                await self._notify_dashboard(alert)

            # Redis notification
            if "redis" in applicable_threshold.notification_channels and self.notification_channels["redis"]:
                await self._notify_redis(alert)

            # Email notification
            if "email" in applicable_threshold.notification_channels and self.notification_channels["email"]:
                await self._notify_email(alert)

        except Exception as e:
            self.logger.error(f"Failed to send notifications: {e}")

    async def _notify_dashboard(self, alert: QualityAlert):
        """Send notification to dashboard system."""
        # This would integrate with your dashboard system
        self.logger.info(f"📊 Dashboard notification: {alert.message}")

    async def _notify_redis(self, alert: QualityAlert):
        """Persist alert to Redis for dashboard consumption."""
        if not REDIS_AVAILABLE or not cache_manager:
            return

        try:
            alert_data = {
                "alert_id": alert.alert_id,
                "level": alert.threshold_level.value,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "spectrum": alert.spectrum,
                "provider": alert.provider,
                "current_value": alert.current_value,
                "metadata": alert.metadata,
            }

            # Store in Redis with 7-day expiry
            cache_key = f"quality_alert:{alert.alert_id}"
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: cache_manager.redis_client.setex(cache_key, 7 * 24 * 3600, json.dumps(alert_data)),  # 7 days
            )

            # Add to alerts list
            alerts_list_key = "quality_alerts:active"
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: cache_manager.redis_client.lpush(alerts_list_key, alert.alert_id)
            )

            self.logger.debug(f"✅ Alert persisted to Redis: {alert.alert_id}")

        except Exception as e:
            self.logger.error(f"Failed to persist alert to Redis: {e}")

    async def _notify_email(self, alert: QualityAlert):
        """Send email notification for critical alerts."""
        # Email notification implementation would go here
        # This is a placeholder for future implementation
        self.logger.info(f"📧 Email notification: {alert.message}")

    async def _persist_metrics(self):
        """Persist current metrics to Redis for dashboard."""
        if not REDIS_AVAILABLE or not cache_manager:
            return

        try:
            metrics_data = {
                "timestamp": self.current_metrics.timestamp.isoformat(),
                "overall_quality": self.current_metrics.overall_quality,
                "spectrum_qualities": self.current_metrics.spectrum_qualities,
                "provider_qualities": self.current_metrics.provider_qualities,
                "trend_direction": self.current_metrics.trend_direction,
                "active_alerts_count": len(self.current_metrics.active_alerts),
            }

            # Store current metrics
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: cache_manager.redis_client.setex(
                    "quality_metrics:current", 3600, json.dumps(metrics_data)  # 1 hour
                ),
            )

        except Exception as e:
            self.logger.error(f"Failed to persist metrics: {e}")

    def get_current_status(self) -> Dict[str, Any]:
        """Get current quality monitoring status."""
        return {
            "current_quality": self.current_metrics.overall_quality,
            "quality_level": self._get_quality_level(self.current_metrics.overall_quality).value,
            "trend": self.current_metrics.trend_direction,
            "active_alerts": len(self.active_alerts),
            "total_alerts_today": len([a for a in self.alert_history if a.timestamp.date() == datetime.now().date()]),
            "last_update": self.current_metrics.timestamp.isoformat(),
            "spectrum_qualities": self.current_metrics.spectrum_qualities,
            "provider_qualities": self.current_metrics.provider_qualities,
        }

    def _get_quality_level(self, quality: float) -> QualityLevel:
        """Get quality level for a given quality score."""
        for threshold in self.thresholds:
            if threshold.min_value <= quality < threshold.max_value:
                return threshold.level
        return QualityLevel.TARGET  # Default fallback

    async def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_timestamp = datetime.now()

            # Remove from active alerts
            del self.active_alerts[alert_id]

            self.logger.info(f"✅ Alert resolved: {alert_id}")
            return True

        return False

    def get_alert_history(self, hours: int = 24) -> List[QualityAlert]:
        """Get alert history for the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.timestamp >= cutoff_time]

    def get_quality_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get quality trends for the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]

        if not recent_metrics:
            return {"error": "No metrics available"}

        qualities = [m.overall_quality for m in recent_metrics]

        return {
            "timeframe_hours": hours,
            "data_points": len(qualities),
            "average_quality": sum(qualities) / len(qualities),
            "min_quality": min(qualities),
            "max_quality": max(qualities),
            "current_trend": self.current_metrics.trend_direction,
            "quality_variance": max(qualities) - min(qualities) if qualities else 0,
        }


# Global instance for easy access
_quality_monitor = None


def get_quality_monitor(config: Optional[Dict[str, Any]] = None) -> MultiTierQualityMonitor:
    """Get or create the global quality monitor instance."""
    global _quality_monitor
    if _quality_monitor is None:
        _quality_monitor = MultiTierQualityMonitor(config)
    return _quality_monitor


# Convenience functions for integration
async def check_quality(
    overall_quality: float,
    spectrum_qualities: Optional[Dict[str, float]] = None,
    provider_qualities: Optional[Dict[str, float]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> List[QualityAlert]:
    """Convenience function to check quality thresholds."""
    monitor = get_quality_monitor()
    return await monitor.check_quality_thresholds(
        overall_quality=overall_quality,
        spectrum_qualities=spectrum_qualities,
        provider_qualities=provider_qualities,
        metadata=metadata,
    )


def get_current_quality_status() -> Dict[str, Any]:
    """Convenience function to get current quality status."""
    monitor = get_quality_monitor()
    return monitor.get_current_status()
