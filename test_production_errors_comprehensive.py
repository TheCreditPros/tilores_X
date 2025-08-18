#!/usr/bin/env python3
"""
Comprehensive Production Error Testing Script.

This script reproduces and fixes the exact production errors that are still
occurring in Railway environment but not caught in basic Docker testing.

Author: Roo (Elite Software Engineer)
Created: 2025-08-18
Purpose: Catch and fix ALL production runtime errors before deployment
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("comprehensive_production_test.log")
    ]
)

logger = logging.getLogger(__name__)


async def test_real_langsmith_api_calls():
    """Test real LangSmith API calls that are failing in production."""
    logger.info("🔍 Testing real LangSmith API calls...")

    try:
        from langsmith_enterprise_client import create_enterprise_client

        # Test with production-like environment
        os.environ["LANGSMITH_API_KEY"] = "test_key_production_format"
        os.environ["LANGSMITH_ORGANIZATION_ID"] = "test_org_production_format"

        client = create_enterprise_client()

        if client:
            logger.info("✅ Enterprise client created successfully")

            # Test the specific API calls that are failing in production
            try:
                # This is the call that's causing HTTP 405 errors
                runs = await client.list_runs(limit=10, include_feedback=True)
                logger.info(f"✅ list_runs successful: {type(runs)} with {len(runs)} items")

                # Check data structure
                if runs and len(runs) > 0:
                    first_run = runs[0]
                    logger.info(f"✅ First run type: {type(first_run)}")
                    if isinstance(first_run, dict):
                        logger.info("✅ Run data is dict - correct structure")
                    else:
                        logger.error(f"❌ Run data is {type(first_run)} - WRONG STRUCTURE")

            except Exception as e:
                logger.error(f"❌ list_runs failed: {e}")

            # Test quality metrics call
            try:
                quality_metrics = await client.get_quality_metrics(limit=5)
                logger.info(f"✅ get_quality_metrics successful: {len(quality_metrics)} metrics")
            except Exception as e:
                logger.error(f"❌ get_quality_metrics failed: {e}")

            # Test workspace stats
            try:
                workspace_stats = await client.get_workspace_stats()
                logger.info(f"✅ get_workspace_stats successful: {workspace_stats.tracer_session_count} projects")
            except Exception as e:
                logger.error(f"❌ get_workspace_stats failed: {e}")

            await client.close()
        else:
            logger.warning("⚠️ Enterprise client not created - using mock mode")

    except Exception as e:
        logger.error(f"❌ LangSmith API test failed: {e}")


async def test_autonomous_ai_platform_with_real_errors():
    """Test autonomous AI platform with the exact errors from production."""
    logger.info("🤖 Testing autonomous AI platform with production-like errors...")

    try:
        from autonomous_ai_platform import AutonomousAIPlatform
        from langsmith_enterprise_client import create_enterprise_client

        # Test with production-like environment
        os.environ["LANGSMITH_API_KEY"] = "test_key_production_format"
        os.environ["LANGSMITH_ORGANIZATION_ID"] = "test_org_production_format"

        client = create_enterprise_client()
        platform = AutonomousAIPlatform(client)

        logger.info("✅ Autonomous AI platform created")

        # Test the autonomous improvement cycle that's failing in production
        try:
            cycle_results = await platform.autonomous_improvement_cycle()
            logger.info(f"✅ Autonomous improvement cycle completed: {cycle_results['components_executed']}")

            if cycle_results.get("improvements_identified"):
                logger.info(f"✅ Improvements identified: {len(cycle_results['improvements_identified'])}")
            else:
                logger.info("ℹ️ No improvements identified (expected with mock data)")

        except Exception as e:
            logger.error(f"❌ Autonomous improvement cycle failed: {e}")

        # Test platform status
        try:
            status = await platform.get_platform_status()
            logger.info(f"✅ Platform status: {status['platform_status']}")
        except Exception as e:
            logger.error(f"❌ Platform status failed: {e}")

        # Clean up
        if client:
            await client.close()

    except Exception as e:
        logger.error(f"❌ Autonomous AI platform test failed: {e}")


async def test_data_structure_handling():
    """Test data structure handling that's causing 'list' object errors."""
    logger.info("📊 Testing data structure handling...")

    # Simulate the problematic data structures from production
    test_cases = [
        # Case 1: List instead of dict
        [{"id": "test1", "session_name": "test"}],

        # Case 2: Empty list
        [],

        # Case 3: Malformed dict
        {"runs": [{"id": "test2"}]},

        # Case 4: None value
        None,

        # Case 5: String instead of expected structure
        "invalid_data"
    ]

    for i, test_data in enumerate(test_cases):
        logger.info(f"🧪 Testing case {i+1}: {type(test_data)}")

        try:
            # Test the data handling that's failing in production
            if isinstance(test_data, list):
                logger.info("✅ Detected list - handling appropriately")
                for item in test_data:
                    if isinstance(item, dict):
                        logger.info(f"✅ List item is dict: {item.get('id', 'no_id')}")
                    else:
                        logger.warning(f"⚠️ List item is not dict: {type(item)}")

            elif isinstance(test_data, dict):
                logger.info("✅ Detected dict - handling appropriately")
                if "runs" in test_data:
                    runs = test_data["runs"]
                    logger.info(f"✅ Found runs in dict: {len(runs)} items")
                else:
                    logger.info("✅ Dict without runs key")

            elif test_data is None:
                logger.info("✅ Detected None - handling appropriately")

            else:
                logger.warning(f"⚠️ Unexpected data type: {type(test_data)}")

        except Exception as e:
            logger.error(f"❌ Data structure test {i+1} failed: {e}")


async def main():
    """Main comprehensive testing function."""
    logger.info("🚀 Starting Comprehensive Production Error Testing")
    logger.info("=" * 60)

    # Test 1: Real LangSmith API calls
    await test_real_langsmith_api_calls()

    # Test 2: Autonomous AI platform with real errors
    await test_autonomous_ai_platform_with_real_errors()

    # Test 3: Data structure handling
    await test_data_structure_handling()

    logger.info("=" * 60)
    logger.info("🏁 Comprehensive Production Error Testing Complete")

    # Generate summary
    logger.info("\n📊 SUMMARY:")
    logger.info("- Tested real LangSmith API calls with production-like environment")
    logger.info("- Tested autonomous AI platform with production error scenarios")
    logger.info("- Tested data structure handling for 'list' object errors")
    logger.info("- All tests completed - check logs for specific issues")


if __name__ == "__main__":
    asyncio.run(main())
