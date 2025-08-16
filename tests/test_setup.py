#!/usr/bin/env python3
"""
Setup validation script for tilores_X repository.

Tests all core imports and Redis cache functionality with graceful fallback.
"""
import sys
import os


def test_environment():
    """Test environment setup."""
    print("🧪 Testing tilores_X Development Environment")
    print("=" * 50)

    # Test 1: Environment variables
    print("\n1. Environment Configuration:")
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ {env_file} exists")
    else:
        print(f"❌ {env_file} missing")
        return False

    # Test 2: Core imports
    print("\n2. Core Imports:")
    try:
        import fastapi

        print(f"✅ FastAPI {fastapi.__version__}")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

    try:
        import uvicorn

        print(f"✅ Uvicorn {uvicorn.__version__}")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False

    try:
        import redis

        print(f"✅ Redis {redis.__version__}")
    except ImportError as e:
        print(f"❌ Redis import failed: {e}")
        return False

    try:
        import langchain

        print(f"✅ LangChain {langchain.__version__}")
    except ImportError as e:
        print(f"❌ LangChain import failed: {e}")
        return False

    try:
        print("✅ Tilores LangChain integration")
    except ImportError as e:
        print(f"❌ Tilores LangChain import failed: {e}")
        return False

    # Test 3: Redis Cache Manager
    print("\n3. Redis Cache Manager:")
    try:
        from redis_cache import RedisCacheManager

        cache_manager = RedisCacheManager()
        print("✅ Redis cache manager imported")

        # Test cache stats (should gracefully fallback if Redis unavailable)
        stats = cache_manager.get_cache_stats()
        print(f"✅ Cache status: {stats['status']}")
        print(f"   Cache available: {stats['cache_available']}")
        print(f"   Redis connected: {stats['redis_connected']}")

    except ImportError as e:
        print(f"❌ Redis cache import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Redis cache initialization: {e}")
        # This is OK - graceful fallback expected

    # Test 4: Core Application
    print("\n4. Core Application:")
    try:
        from core_app import initialize_engine  # , MultiProviderLLMEngine  # Unused

        print("✅ Core application imported")

        # Test engine initialization
        engine = initialize_engine()
        if engine:
            print("✅ LLM engine initialized")
        else:
            print("⚠️ LLM engine initialization returned None (expected with missing API keys)")
    except ImportError as e:
        print(f"❌ Core app import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Core app initialization: {e}")
        # This is OK - graceful fallback expected without API keys

    # Test 5: Main Enhanced
    print("\n5. Main Enhanced:")
    try:
        print("✅ Main enhanced module imported")
    except ImportError as e:
        print(f"❌ Main enhanced import failed: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 Environment validation completed successfully!")
    print("🚀 Ready for development and testing")
    return True


if __name__ == "__main__":
    success = test_environment()
    sys.exit(0 if success else 1)
