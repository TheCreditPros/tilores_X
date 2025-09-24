#!/usr/bin/env python3
"""
Langfuse Prompt Migration Script
Run this script to migrate agent prompts from local storage to Langfuse.

Usage:
1. Set your Langfuse credentials in environment variables:
   export LANGFUSE_PUBLIC_KEY="pk-lf-..."
   export LANGFUSE_SECRET_KEY="sk-lf-..."
   export LANGFUSE_HOST="https://us.cloud.langfuse.com"

2. Run the script:
   python migrate_prompts.py
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from agent_prompts import FALLBACK_PROMPTS, LangfusePromptManager

def main():
    print("🚀 Langfuse Prompt Migration Script")
    print("=" * 50)

    # Check environment variables
    required_vars = ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("\nPlease set the following environment variables:")
        for var in missing_vars:
            print(f"  export {var}=\"your-value-here\"")
        return 1

    print("✅ Environment variables configured")

    # Initialize Langfuse manager
    print("\n🔧 Initializing Langfuse connection...")
    manager = LangfusePromptManager()

    if not manager._initialized:
        print("❌ Failed to initialize Langfuse connection")
        return 1

    print("✅ Langfuse connection established")

    # Migrate prompts
    print("\n🔄 Migrating prompts to Langfuse...")
    results = manager.migrate_fallback_prompts()

    # Report results
    successful = sum(results.values())
    total = len(results)

    print(f"\n📊 Migration Results: {successful}/{total} prompts migrated successfully")

    if successful == total:
        print("✅ All prompts migrated successfully!")
        print("\n💡 Next Steps:")
        print("1. Visit your Langfuse dashboard to review the migrated prompts")
        print("2. Test prompts in the Langfuse playground")
        print("3. Set up A/B testing and version control as needed")
    else:
        failed_prompts = [name for name, success in results.items() if not success]
        print(f"⚠️ Some prompts failed to migrate: {failed_prompts}")

    return 0 if successful == total else 1

if __name__ == "__main__":
    exit(main())
