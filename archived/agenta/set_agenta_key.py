#!/usr / bin / env python3
"""
Set Agenta.ai API Key

Simple script to help set up the Agenta.ai API key in the environment.
The user mentioned they already provided an API key.
"""

import os
import sys

def set_agenta_key():
    """Set the Agenta API key"""

    print("🔐 Agenta.ai API Key Setup")
    print("=" * 40)

    # Check if already set
    current_key = os.getenv("AGENTA_API_KEY")
    if current_key:
        print(f"✅ AGENTA_API_KEY already set: {'*' * 20}...{current_key[-4:] if len(current_key) > 4 else '****'}")

        update = input("🔄 Update existing key? (y / N): ").lower().strip()
        if update != 'y':
            print("✅ Keeping existing key")
            return True

    print("\n📝 You mentioned you already provided an API key.")
    print("Please enter your Agenta.ai API key:")
    print("(You can find this in your Agenta.ai dashboard under Settings > API Keys)")

    # Get API key from user
    api_key = input("\n🔑 API Key: ").strip()

    if not api_key:
        print("❌ No API key provided")
        return False

    if len(api_key) < 10:  # Basic validation
        print("❌ API key seems too short")
        return False

    # Set environment variables
    os.environ["AGENTA_API_KEY"] = api_key
    os.environ["AGENTA_HOST"] = "https://cloud.agenta.ai"
    os.environ["AGENTA_APP_SLUG"] = "tilores - x"

    print("\n✅ Environment variables set:")
    print(f"  - AGENTA_API_KEY: {'*' * 20}...{api_key[-4:]}")
    print(f"  - AGENTA_HOST: {os.environ['AGENTA_HOST']}")
    print(f"  - AGENTA_APP_SLUG: {os.environ['AGENTA_APP_SLUG']}")

    # Save to .env file for persistence
    try:
        env_content = """# Agenta.ai Configuration
AGENTA_API_KEY={api_key}
AGENTA_HOST=https://cloud.agenta.ai
AGENTA_APP_SLUG=tilores - x

# Add your other environment variables below
# TILORES_GRAPHQL_API_URL=...
# TILORES_CLIENT_ID=...
# etc.
"""

        with open(".env", "w") as f:
            f.write(env_content)

        print("\n💾 Saved to .env file for persistence")
        print("⚠️ Make sure to add .env to your .gitignore file!")

    except Exception as e:
        print(f"\n⚠️ Could not save to .env file: {e}")
        print("💡 You may need to set the environment variable manually")

    print("\n🎯 Next steps:")
    print("  1. Run: python test_agenta_ui_integration.py")
    print("  2. Check Agenta.ai dashboard for your app")
    print("  3. Configure prompt variants in Agenta.ai UI")

    return True

def main():
    """Main function"""
    try:
        success = set_agenta_key()
        if success:
            print("\n🎉 Agenta.ai API key setup complete!")
        else:
            print("\n❌ API key setup failed")
        return success
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
