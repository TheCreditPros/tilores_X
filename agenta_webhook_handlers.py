#!/usr/bin/env python3
"""
Agenta.ai Webhook Handlers

Handles webhook callbacks from Agenta.ai for automated workflows.
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router for webhook endpoints
webhook_router = APIRouter(prefix="/webhooks", tags=["webhooks"])

class WebhookPayload(BaseModel):
    """Base webhook payload model"""
    event_type: str
    timestamp: str
    app_slug: str
    data: Dict[str, Any]

class EvaluationCompletePayload(BaseModel):
    """Evaluation complete webhook payload"""
    evaluation_id: str
    test_set_name: str
    variant_name: str
    results: Dict[str, Any]
    status: str
    completion_time: str

class DeploymentStatusPayload(BaseModel):
    """Deployment status webhook payload"""
    deployment_id: str
    environment: str
    variant_name: str
    status: str
    timestamp: str
    logs: Optional[str] = None

class PerformanceAlertPayload(BaseModel):
    """Performance alert webhook payload"""
    alert_type: str
    metric_name: str
    current_value: float
    threshold_value: float
    variant_name: str
    timestamp: str

@webhook_router.post("/evaluation-complete")
async def handle_evaluation_complete(
    payload: EvaluationCompletePayload,
    background_tasks: BackgroundTasks,
    request: Request
):
    """Handle evaluation completion webhook"""
    logger.info(f"📊 Evaluation Complete: {payload.test_set_name} for {payload.variant_name}")

    try:
        # Log evaluation results
        logger.info(f"🎯 Results: {json.dumps(payload.results, indent=2)}")

        # Add background task for processing
        background_tasks.add_task(
            process_evaluation_results,
            payload.evaluation_id,
            payload.variant_name,
            payload.results
        )

        return {
            "status": "received",
            "evaluation_id": payload.evaluation_id,
            "message": f"Evaluation results for {payload.variant_name} received and queued for processing"
        }

    except Exception as e:
        logger.error(f"❌ Error processing evaluation webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@webhook_router.post("/deployment-status")
async def handle_deployment_status(
    payload: DeploymentStatusPayload,
    background_tasks: BackgroundTasks,
    request: Request
):
    """Handle deployment status webhook"""
    logger.info(f"🚀 Deployment Status: {payload.status} for {payload.variant_name} in {payload.environment}")

    try:
        # Log deployment status
        if payload.status == "completed":
            logger.info(f"✅ Deployment successful: {payload.variant_name}")
        elif payload.status == "failed":
            logger.error(f"❌ Deployment failed: {payload.variant_name}")
            if payload.logs:
                logger.error(f"📋 Logs: {payload.logs}")

        # Add background task for processing
        background_tasks.add_task(
            process_deployment_status,
            payload.deployment_id,
            payload.environment,
            payload.status
        )

        return {
            "status": "received",
            "deployment_id": payload.deployment_id,
            "message": f"Deployment status {payload.status} received"
        }

    except Exception as e:
        logger.error(f"❌ Error processing deployment webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@webhook_router.post("/performance-alert")
async def handle_performance_alert(
    payload: PerformanceAlertPayload,
    background_tasks: BackgroundTasks,
    request: Request
):
    """Handle performance alert webhook"""
    logger.warning(f"⚠️ Performance Alert: {payload.alert_type} - {payload.metric_name}")
    logger.warning(f"📊 Current: {payload.current_value}, Threshold: {payload.threshold_value}")

    try:
        # Add background task for alert processing
        background_tasks.add_task(
            process_performance_alert,
            payload.alert_type,
            payload.metric_name,
            payload.current_value,
            payload.threshold_value,
            payload.variant_name
        )

        return {
            "status": "received",
            "alert_type": payload.alert_type,
            "message": f"Performance alert for {payload.variant_name} received"
        }

    except Exception as e:
        logger.error(f"❌ Error processing performance alert webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@webhook_router.get("/health")
async def webhook_health():
    """Health check for webhook endpoints"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/webhooks/evaluation-complete",
            "/webhooks/deployment-status",
            "/webhooks/performance-alert"
        ]
    }

# Background task functions

async def process_evaluation_results(
    evaluation_id: str,
    variant_name: str,
    results: Dict[str, Any]
):
    """Process evaluation results in background"""
    logger.info(f"🔄 Processing evaluation results for {variant_name}")

    try:
        # Extract key metrics
        accuracy = results.get("accuracy", 0)
        response_time = results.get("response_time", 0)
        token_usage = results.get("token_usage", 0)

        # Log performance metrics
        logger.info(f"📊 Variant Performance - {variant_name}:")
        logger.info(f"  - Accuracy: {accuracy}%")
        logger.info(f"  - Response Time: {response_time}s")
        logger.info(f"  - Token Usage: {token_usage}")

        # Here you could:
        # - Store results in database
        # - Send notifications
        # - Trigger automated actions
        # - Update monitoring dashboards

        logger.info(f"✅ Evaluation results processed for {variant_name}")

    except Exception as e:
        logger.error(f"❌ Error processing evaluation results: {e}")

async def process_deployment_status(
    deployment_id: str,
    environment: str,
    status: str
):
    """Process deployment status in background"""
    logger.info(f"🔄 Processing deployment status: {status} in {environment}")

    try:
        if status == "completed":
            # Deployment successful
            logger.info(f"✅ Deployment {deployment_id} completed successfully")

            # Here you could:
            # - Update deployment tracking
            # - Send success notifications
            # - Trigger post-deployment tests
            # - Update monitoring

        elif status == "failed":
            # Deployment failed
            logger.error(f"❌ Deployment {deployment_id} failed")

            # Here you could:
            # - Send failure alerts
            # - Trigger rollback procedures
            # - Log failure details
            # - Notify development team

        logger.info(f"✅ Deployment status processed for {deployment_id}")

    except Exception as e:
        logger.error(f"❌ Error processing deployment status: {e}")

async def process_performance_alert(
    alert_type: str,
    metric_name: str,
    current_value: float,
    threshold_value: float,
    variant_name: str
):
    """Process performance alert in background"""
    logger.warning(f"🔄 Processing performance alert: {alert_type}")

    try:
        # Calculate severity
        if current_value > threshold_value * 1.5:
            severity = "critical"
        elif current_value > threshold_value * 1.2:
            severity = "high"
        else:
            severity = "medium"

        logger.warning(f"⚠️ Alert Severity: {severity}")
        logger.warning(f"📊 Metric: {metric_name} = {current_value} (threshold: {threshold_value})")

        # Here you could:
        # - Send alerts to monitoring systems
        # - Trigger auto-scaling
        # - Send notifications to team
        # - Log performance issues
        # - Trigger circuit breakers

        if severity == "critical":
            logger.critical(f"🚨 CRITICAL ALERT: {metric_name} for {variant_name}")
            # Could trigger immediate actions like:
            # - Automatic failover
            # - Emergency notifications
            # - Circuit breaker activation

        logger.info(f"✅ Performance alert processed for {variant_name}")

    except Exception as e:
        logger.error(f"❌ Error processing performance alert: {e}")

# Utility functions for webhook verification
def verify_webhook_signature(request: Request, secret: str) -> bool:
    """Verify webhook signature for security"""
    # Implementation would depend on Agenta's signature method
    # This is a placeholder for security verification
    return True

def log_webhook_event(event_type: str, payload: Dict[str, Any]):
    """Log webhook events for debugging"""
    logger.info(f"📥 Webhook Event: {event_type}")
    logger.debug(f"📋 Payload: {json.dumps(payload, indent=2)}")
