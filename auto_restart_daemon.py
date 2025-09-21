#!/usr/bin/env python3
"""
Auto-Restart Daemon for Tilores_X Development Server

Monitors code changes and automatically restarts the FastAPI server.
Prevents manual restart issues during development.

Features:
- File change detection for Python files
- Automatic server restart on changes
- Process management with proper cleanup
- Logging of restart events
- Graceful shutdown handling
"""

import os
import sys
import time
import signal
import subprocess
import logging
from pathlib import Path
from typing import Optional, Set
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    # Define dummy classes for fallback
    class Observer:
        def schedule(self, *args, **kwargs): pass
        def start(self): pass
        def stop(self): pass
        def join(self): pass

    class FileSystemEventHandler:
        pass

    WATCHDOG_AVAILABLE = False
    print("⚠️  watchdog not installed. Install with: pip install watchdog")
    print("📝 Falling back to basic file monitoring...")

class ServerRestarter:
    """Manages the FastAPI server process and automatic restarts."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.server_process: Optional[subprocess.Popen] = None
        self.last_restart = datetime.now()

        # Setup logging
        self.logger = logging.getLogger("AutoRestartDaemon")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Files to ignore (logs, caches, etc.)
        self.ignore_patterns = {
            '__pycache__',
            '.git',
            'node_modules',
            '*.pyc',
            '*.log',
            '.pytest_cache',
            'archive',
            'cleanup_archive',
            'dashboard/node_modules',
            'dashboard/build',
            'dashboard/.next'
        }

    def should_ignore_file(self, filepath: str) -> bool:
        """Check if file should be ignored for restart triggers."""
        path = Path(filepath)

        # Check if any ignore pattern matches
        for pattern in self.ignore_patterns:
            if pattern in str(path) or str(path).endswith(pattern):
                return True

        # Only monitor Python files
        return not filepath.endswith('.py')

    def start_server(self) -> bool:
        """Start the FastAPI server process."""
        if self.server_process and self.server_process.poll() is None:
            self.logger.info("Server already running")
            return True

        try:
            cmd = [
                sys.executable, "-m", "uvicorn",
                "main_enhanced:app",
                "--host", self.host,
                "--port", str(self.port),
                "--reload"
            ]

            self.logger.info(f"🚀 Starting server: {' '.join(cmd)}")
            self.server_process = subprocess.Popen(
                cmd,
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait a moment for server to start
            time.sleep(3)

            if self.server_process.poll() is None:
                self.last_restart = datetime.now()
                self.logger.info(f"✅ Server started successfully (PID: {self.server_process.pid})")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                self.logger.error(f"❌ Server failed to start")
                if stderr:
                    self.logger.error(f"Server error: {stderr}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Failed to start server: {e}")
            return False

    def stop_server(self) -> None:
        """Stop the current server process."""
        if self.server_process and self.server_process.poll() is None:
            self.logger.info(f"🛑 Stopping server (PID: {self.server_process.pid})")

            try:
                # Try graceful shutdown first
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                self.logger.warning("Graceful shutdown failed, force killing...")
                self.server_process.kill()
                self.server_process.wait()

            self.logger.info("✅ Server stopped")
        else:
            self.logger.info("Server not running")

    def restart_server(self) -> bool:
        """Restart the server."""
        self.logger.info("🔄 Restarting server due to code changes...")

        self.stop_server()
        time.sleep(2)  # Brief pause

        success = self.start_server()
        if success:
            self.logger.info("🎉 Server restarted successfully!")
        else:
            self.logger.error("❌ Server restart failed!")

        return success

    def cleanup(self) -> None:
        """Clean shutdown of daemon and server."""
        self.logger.info("🧹 Cleaning up daemon...")
        self.stop_server()
        self.logger.info("✅ Cleanup complete")

class FileChangeHandler(FileSystemEventHandler):
    """Handles file system events for auto-restart."""

    def __init__(self, restarter: ServerRestarter):
        self.restarter = restarter
        self.last_event_time = 0
        self.cooldown_seconds = 2  # Prevent rapid restarts

    def on_modified(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        if self.restarter.should_ignore_file(filepath):
            return

        current_time = time.time()
        if current_time - self.last_event_time < self.cooldown_seconds:
            return  # Too soon, ignore

        self.last_event_time = current_time

        # Only restart for Python file changes
        if filepath.endswith('.py'):
            print(f"\n📝 File changed: {filepath}")
            self.restarter.restart_server()

def main():
    """Main daemon function."""
    print("🤖 Tilores_X Auto-Restart Daemon")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("main_enhanced.py").exists():
        print("❌ Error: main_enhanced.py not found. Run from tilores_X directory.")
        sys.exit(1)

    # Initialize restarter
    restarter = ServerRestarter()

    # Start initial server
    if not restarter.start_server():
        print("❌ Failed to start initial server. Exiting.")
        sys.exit(1)

    # Setup file monitoring
    if WATCHDOG_AVAILABLE:
        print("👀 Using watchdog for efficient file monitoring...")
        observer = Observer()
        handler = FileChangeHandler(restarter)
        observer.schedule(handler, ".", recursive=True)
        observer.start()

        print("✅ Auto-restart daemon active!")
        print("📝 Server will automatically restart when Python files change")
        print("🛑 Press Ctrl+C to stop")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down daemon...")
            observer.stop()
            observer.join()
    else:
        print("👀 Using basic file monitoring (less efficient)...")
        print("✅ Auto-restart daemon active!")
        print("📝 Server will automatically restart when Python files change")
        print("⚠️  For better performance, install watchdog: pip install watchdog")

        # Basic polling approach (less efficient)
        monitored_files = {}
        for py_file in Path(".").rglob("*.py"):
            if not restarter.should_ignore_file(str(py_file)):
                monitored_files[str(py_file)] = py_file.stat().st_mtime

        try:
            while True:
                time.sleep(2)  # Check every 2 seconds

                for filepath, last_mtime in monitored_files.items():
                    try:
                        current_mtime = Path(filepath).stat().st_mtime
                        if current_mtime > last_mtime:
                            print(f"\n📝 File changed: {filepath}")
                            monitored_files[filepath] = current_mtime
                            restarter.restart_server()
                            break  # Restart and continue monitoring
                    except FileNotFoundError:
                        # File was deleted, remove from monitoring
                        del monitored_files[filepath]

        except KeyboardInterrupt:
            print("\n🛑 Shutting down daemon...")

    # Cleanup
    restarter.cleanup()

if __name__ == "__main__":
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Received shutdown signal...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    main()
