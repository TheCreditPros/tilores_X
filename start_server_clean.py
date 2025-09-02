#!/usr/bin/env python3
"""
Clean server startup script
"""

import subprocess
import time
import sys
import os

def kill_existing_processes():
    """Kill any existing server processes"""
    try:
        subprocess.run(["pkill", "-f", "direct_credit_api_with_phone.py"],
                      capture_output=True, text=True)
        print("🧹 Killed existing processes")
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Error killing processes: {e}")

def start_server():
    """Start the server"""
    try:
        print("🚀 Starting server...")
        # Start server in background
        process = subprocess.Popen(
            [sys.executable, "direct_credit_api_with_phone.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Wait for startup and show logs
        startup_timeout = 10
        start_time = time.time()

        while time.time() - start_time < startup_timeout:
            if process.poll() is not None:
                # Process ended
                output, _ = process.communicate()
                print(f"❌ Server failed to start:\n{output}")
                return None

            # Check if server is responding
            try:
                import requests
                response = requests.get("http://localhost:8080/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Server is running!")
                    return process
            except:
                pass

            time.sleep(0.5)

        print("⚠️ Server startup timeout")
        return process

    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

if __name__ == "__main__":
    kill_existing_processes()
    server_process = start_server()

    if server_process:
        print(f"🎯 Server PID: {server_process.pid}")
        print("📝 Server is running. Use Ctrl+C to stop or run test_status_fix.py")

        try:
            # Keep the script running to monitor the server
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()
            print("✅ Server stopped")
    else:
        print("❌ Failed to start server")
        sys.exit(1)
