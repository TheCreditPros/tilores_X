#!/usr/bin/env python3
"""
Quick Start Script for Tilores_X Auto-Restart Daemon

Usage:
    python start_daemon.py

This will start the auto-restart daemon that monitors code changes
and automatically restarts the server when Python files are modified.
"""

import subprocess
import sys

def main():
    """Start the auto-restart daemon."""
    print("🚀 Starting Tilores_X Auto-Restart Daemon...")
    print("This will monitor code changes and auto-restart the server")
    print("Press Ctrl+C to stop the daemon")
    print("=" * 60)

    try:
        # Run the daemon
        result = subprocess.run([
            sys.executable, "auto_restart_daemon.py"
        ], cwd=".")

        # Check exit code
        if result.returncode == 0:
            print("✅ Daemon exited cleanly")
        else:
            print(f"❌ Daemon exited with code: {result.returncode}")

    except KeyboardInterrupt:
        print("\n✅ Daemon stopped by user")
    except Exception as e:
        print(f"❌ Error starting daemon: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
