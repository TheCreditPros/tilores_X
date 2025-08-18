#!/usr/bin/env python3
"""
Tilores Autonomous AI Platform - Production Deployment Entry Point
Integrates the complete autonomous AI platform with existing infrastructure
"""

import os
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

# Core application imports
from main_enhanced import app, startup_background_tasks, shutdown_background_tasks
from fastapi import FastAPI

# Autonomous AI Platform imports
from autonomous_ai_platform import AutonomousAIPlatform
from langsmith_enterprise_client import create_enterprise_client
from autonomous_integration import EnhancedVirtuousCycleManager, AutonomousQualityMonitor

# Global autonomous AI platform instance
autonomous_platform: Optional[AutonomousAIPlatform] = None
enhanced_cycle_manager: Optional[EnhancedVirtuousCycleManager] = None
quality_monitor: Optional[AutonomousQualityMonitor] = None


async def initialize_autonomous_platform():
    """Initialize the autonomous AI platform with production configuration"""

    print("🤖 Initializing Autonomous AI Platform for Production...")

    try:
        # Validate environment configuration
        required_vars = [
            "LANGSMITH_API_KEY",
            "LANGSMITH_ORGANIZATION_ID",
            "AUTONOMOUS_AI_ENABLED",
            "AUTONOMOUS_AI_MODE",
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")

        # Convert boolean environment variables to strings for LangSmith compatibility
        bool_vars = [
            "AUTONOMOUS_AI_ENABLED",
            "LANGSMITH_ENTERPRISE_MODE",
            "LANGSMITH_ENTERPRISE_FEATURES",
            "LANGCHAIN_TRACING_V2",
            "LANGSMITH_TRACING",
        ]

        for var in bool_vars:
            value = os.getenv(var)
            if isinstance(value, bool):
                os.environ[var] = str(value).lower()
            elif value and value.lower() in ["true", "false"]:
                os.environ[var] = value.lower()

        # Initialize Enterprise LangSmith Client
        print("📊 Initializing Enterprise LangSmith Client...")
        enterprise_client = create_enterprise_client()

        if enterprise_client:
            # Validate LangSmith connectivity
            print("🔍 Validating LangSmith Enterprise connectivity...")
            try:
                workspace_stats = await enterprise_client.get_workspace_stats()
                print(
                    f"✅ LangSmith connected - Projects: {workspace_stats.tracer_session_count}, "
                    f"Datasets: {workspace_stats.dataset_count}"
                )
            except Exception as e:
                print(f"⚠️ LangSmith connectivity validation failed: {e}")
                print("🔄 Continuing with mock mode...")
        else:
            print("⚠️ Enterprise LangSmith client not available - using mock mode")

        # Initialize Autonomous AI Platform
        print("🧠 Initializing Autonomous AI Platform core...")
        autonomous_platform = AutonomousAIPlatform(enterprise_client)

        # Initialize Enhanced Virtuous Cycle Manager
        print("♻️ Initializing Enhanced Virtuous Cycle Manager...")
        enhanced_cycle_manager = EnhancedVirtuousCycleManager()

        # Initialize Autonomous Quality Monitor
        print("📈 Initializing Autonomous Quality Monitor...")
        # quality_monitor = AutonomousQualityMonitor(enhanced_cycle_manager)  # Reserved for future use

        # Run initial autonomous improvement cycle
        print("🔄 Running initial autonomous improvement cycle...")
        initial_cycle_result = await autonomous_platform.autonomous_improvement_cycle()
        print(
            f"📊 Initial cycle completed - Components: {len(initial_cycle_result['components_executed'])}, "
            f"Improvements: {len(initial_cycle_result['improvements_identified'])}"
        )

        # Get initial platform status
        print("🎯 Getting initial platform status...")
        initial_status = await autonomous_platform.get_platform_status()
        print(
            f"📈 Platform operational - Quality: {initial_status['current_quality']:.1%}, "
            f"Trend: {initial_status['quality_trend']}"
        )

        # Get initial enhanced status
        print("🔍 Getting enhanced integration status...")
        enhanced_status = await enhanced_cycle_manager.get_enhanced_status()
        print(
            f"✅ Enhanced features: {enhanced_status['enhanced_features']}, "
            f"Legacy compatibility: {enhanced_status['legacy_compatibility']}"
        )

        print("✅ Autonomous AI Platform successfully initialized!")
        print(f"🕒 Platform started at: {datetime.utcnow().isoformat()}")

        return True

    except Exception as e:
        print(f"❌ Failed to initialize Autonomous AI Platform: {e}")
        print("🔧 Check environment variables and LangSmith connectivity")
        return False


async def shutdown_autonomous_platform():
    """Gracefully shutdown the autonomous AI platform"""

    print("🛑 Shutting down Autonomous AI Platform...")

    try:
        # Get final platform status
        if autonomous_platform:
            print("📊 Getting final platform status...")
            final_status = await autonomous_platform.get_platform_status()
            print(f"📈 Final quality: {final_status['current_quality']:.1%}")

        # Get final enhanced status
        if enhanced_cycle_manager:
            print("📋 Getting final enhanced status...")
            final_enhanced = await enhanced_cycle_manager.get_enhanced_status()
            print(f"🔄 Enhanced features active: {final_enhanced['enhanced_features']}")

        # Close LangSmith client connections
        if enhanced_cycle_manager:
            print("🔌 Closing LangSmith client connections...")
            await enhanced_cycle_manager.close()

        print("✅ Autonomous AI Platform gracefully shut down")

    except Exception as e:
        print(f"⚠️ Error during autonomous platform shutdown: {e}")


# Enhanced FastAPI lifespan handler (modern approach)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enhanced lifespan handler with autonomous AI platform management"""
    # Startup
    print("🚀 Starting Tilores API with Autonomous AI Platform")

    # Start original background tasks
    await startup_background_tasks()

    # Initialize autonomous AI platform
    if os.getenv("AUTONOMOUS_AI_ENABLED", "false").lower() == "true":
        success = await initialize_autonomous_platform()
        if not success:
            print("❌ Autonomous AI Platform initialization failed")
            print("🔄 Falling back to standard operation mode")
        else:
            print("🤖 Autonomous AI Platform is now active")
    else:
        print("ℹ️ Autonomous AI Platform disabled - running in standard mode")

    yield

    # Shutdown
    print("🛑 Shutting down Tilores API")

    # Shutdown autonomous AI platform
    await shutdown_autonomous_platform()

    # Shutdown original background tasks
    await shutdown_background_tasks()


# Apply the lifespan handler to the app
app.router.lifespan_context = lifespan


# Health check endpoints for autonomous AI platform
@app.get("/health/autonomous")
async def autonomous_health_check():
    """Health check specifically for autonomous AI platform"""

    if not os.getenv("AUTONOMOUS_AI_ENABLED", "false").lower() == "true":
        return {
            "status": "disabled",
            "message": "Autonomous AI Platform is disabled",
            "timestamp": datetime.utcnow().isoformat(),
        }

    health_status = {
        "status": "healthy" if autonomous_platform else "error",
        "autonomous_platform": "active" if autonomous_platform else "inactive",
        "enhanced_cycle_manager": "active" if enhanced_cycle_manager else "inactive",
        "quality_monitor": "active" if quality_monitor else "inactive",
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Get platform metrics if available
    if autonomous_platform:
        try:
            platform_status = await autonomous_platform.get_platform_status()
            health_status.update(platform_status)
        except Exception as e:
            health_status["platform_error"] = str(e)

    return health_status


@app.get("/metrics/autonomous")
async def autonomous_metrics():
    """Get comprehensive autonomous AI platform metrics"""

    if not autonomous_platform:
        return {"error": "Autonomous AI Platform not initialized", "timestamp": datetime.utcnow().isoformat()}

    try:
        # Get platform status
        platform_status = await autonomous_platform.get_platform_status()

        # Get enhanced status
        enhanced_status = {}
        if enhanced_cycle_manager:
            enhanced_status = await enhanced_cycle_manager.get_enhanced_status()

        return {
            "status": "success",
            "platform_status": platform_status,
            "enhanced_status": enhanced_status,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        return {"error": f"Failed to retrieve autonomous metrics: {e}", "timestamp": datetime.utcnow().isoformat()}


@app.post("/autonomous/optimize")
async def trigger_autonomous_optimization():
    """Manually trigger autonomous optimization cycle"""

    if not autonomous_platform:
        return {"error": "Autonomous AI Platform not initialized", "timestamp": datetime.utcnow().isoformat()}

    try:
        # Trigger optimization cycle
        result = await autonomous_platform.autonomous_improvement_cycle()

        return {"status": "success", "optimization_result": result, "timestamp": datetime.utcnow().isoformat()}

    except Exception as e:
        return {"error": f"Optimization cycle failed: {e}", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn

    print("🤖 Starting Tilores Autonomous AI Platform - Production Mode")
    print(f"🔧 Environment: {os.getenv('ENVIRONMENT', 'production')}")
    print(f"🌐 Autonomous AI: {os.getenv('AUTONOMOUS_AI_ENABLED', 'false')}")
    print(f"📊 LangSmith Enterprise: {os.getenv('LANGSMITH_ENTERPRISE_FEATURES', 'false')}")

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
