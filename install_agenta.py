#!/usr/bin/env python3
"""
Install Agenta.ai SDK and test basic functionality
"""

import subprocess
import sys
import os

def install_agenta_sdk():
    """Install the Agenta SDK"""
    try:
        print("📦 Installing Agenta.ai SDK...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-U", "agenta"
        ], capture_output=True, text=True, check=True)

        print("✅ Agenta SDK installed successfully!")
        print(f"Output: {result.stdout}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Agenta SDK: {e}")
        print(f"Error output: {e.stderr}")
        return False

def test_agenta_import():
    """Test if Agenta can be imported"""
    try:
        import agenta as ag
        print("✅ Agenta SDK imported successfully!")
        print(f"Agenta version: {getattr(ag, '__version__', 'Unknown')}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Agenta: {e}")
        return False

def setup_environment():
    """Setup environment variables for Agenta"""
    # Check if API key is already set
    api_key = os.getenv("AGENTA_API_KEY")
    host = os.getenv("AGENTA_HOST")

    print("🔧 Environment Configuration:")
    print(f"  - AGENTA_API_KEY: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"  - AGENTA_HOST: {host or 'Not set (will use default)'}")

    if not api_key:
        print("⚠️ AGENTA_API_KEY not found in environment")
        print("Please set it in your .env file or environment")

if __name__ == "__main__":
    print("🚀 Setting up Agenta.ai SDK...")

    # Install SDK
    if install_agenta_sdk():
        # Test import
        if test_agenta_import():
            # Setup environment
            setup_environment()
            print("\n✅ Agenta.ai SDK setup complete!")
        else:
            print("\n❌ SDK installation succeeded but import failed")
    else:
        print("\n❌ SDK installation failed")
