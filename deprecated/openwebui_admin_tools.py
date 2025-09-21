#!/usr/bin/env python3
"""
Open WebUI Admin Tools - CLI utilities for team evaluation setup
"""

import requests
import json
import sys
from datetime import datetime

class OpenWebUIAdmin:
    def __init__(self, base_url="http://localhost:3000", email="damon@thecreditpros.com", password="Credit@123"):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.token = None
        self.headers = {"Content-Type": "application/json"}

    def login(self):
        """Login and get authentication token"""
        try:
            login_data = {"email": self.email, "password": self.password}
            response = requests.post(f"{self.base_url}/api/v1/auths/signin", json=login_data)
            if response.status_code == 200:
                self.token = response.json().get("token", "")
                self.headers["Authorization"] = f"Bearer {self.token}"
                print("✅ Successfully logged in to Open WebUI")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def get_models(self):
        """Get all available models"""
        try:
            response = requests.get(f"{self.base_url}/api/models", headers=self.headers)
            if response.status_code == 200:
                models = response.json().get("data", [])
                print(f"\n📊 Available Models ({len(models)} total):")

                tilores_models = [m for m in models if "tilores" in m.get("owned_by", "")]
                other_models = [m for m in models if "tilores" not in m.get("owned_by", "")]

                print(f"\n🚀 Tilores Models ({len(tilores_models)}):")
                for model in tilores_models:
                    print("  ✅ {} - {}".format(model['id'], model.get('owned_by', 'unknown')))

                print(f"\n📦 Other Models ({len(other_models)}):")
                for model in other_models:
                    print("  - {} - {}".format(model['id'], model.get('owned_by', 'unknown')))

                return models
            else:
                print(f"❌ Failed to get models: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting models: {e}")
            return []

    def test_chat(self, model="gpt-4o-mini", message="Hello, this is a test message"):
        """Test chat functionality with a specific model"""
        try:
            chat_data = {
                "model": model,
                "messages": [{"role": "user", "content": message}],
                "max_tokens": 100
            }

            print(f"\n🧪 Testing chat with {model}...")
            response = requests.post(f"{self.base_url}/api/chat/completions",
                                   json=chat_data, headers=self.headers)

            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "No response")
                print("✅ Chat test successful!")
                print("📝 Response: {}...".format(content[:100]))
                return True
            else:
                print(f"❌ Chat test failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Chat test error: {e}")
            return False

    def get_webhook_logs(self):
        """Check webhook logs from our FastAPI server"""
        try:
            # Check if webhook log file exists
            import os
            log_file = "webhook_logs.jsonl"
            if os.path.exists(log_file):
                print("\n📋 Recent Webhook Events:")
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-5:]:  # Show last 5 events
                        try:
                            event = json.loads(line)
                            timestamp = event.get('timestamp', 'unknown')
                            rating = event.get('rating', 'unknown')
                            model = event.get('model', 'unknown')
                            print("  {}: {} rating for {}".format(timestamp, rating, model))
                        except json.JSONDecodeError:
                            continue
            else:
                print("📋 No webhook logs found yet")
        except Exception as e:
            print(f"❌ Error reading webhook logs: {e}")

    def health_check(self):
        """Comprehensive health check"""
        print(f"\n🏥 Open WebUI Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Check Open WebUI
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Open WebUI: Healthy")
            else:
                print(f"⚠️  Open WebUI: Status {response.status_code}")
        except requests.RequestException:
            print("❌ Open WebUI: Not responding")

        # Check Tilores API
        try:
            response = requests.get("http://localhost:8080/health", timeout=5)
            if response.status_code == 200:
                print("✅ Tilores API: Healthy")
            else:
                print(f"⚠️  Tilores API: Status {response.status_code}")
        except requests.RequestException:
            print("❌ Tilores API: Not responding")

        # Check models endpoint
        try:
            response = requests.get("http://localhost:8080/v1/models", timeout=5)
            if response.status_code == 200:
                models = response.json().get("data", [])
                print(f"✅ Tilores Models Endpoint: {len(models)} models available")
            else:
                print(f"⚠️  Tilores Models Endpoint: Status {response.status_code}")
        except requests.RequestException:
            print("❌ Tilores Models Endpoint: Not responding")

def main():
    if len(sys.argv) < 2:
        print("""
🛠️  Open WebUI Admin Tools

Usage:
  python3 openwebui_admin_tools.py <command>

Commands:
  health      - Run comprehensive health check
  models      - List all available models
  test        - Test chat functionality
  logs        - Show recent webhook logs
  all         - Run all checks

Examples:
  python3 openwebui_admin_tools.py health
  python3 openwebui_admin_tools.py models
  python3 openwebui_admin_tools.py test
        """)
        return

    command = sys.argv[1].lower()
    admin = OpenWebUIAdmin()

    if not admin.login():
        return

    if command == "health":
        admin.health_check()
    elif command == "models":
        admin.get_models()
    elif command == "test":
        admin.test_chat()
    elif command == "logs":
        admin.get_webhook_logs()
    elif command == "all":
        admin.health_check()
        admin.get_models()
        admin.test_chat()
        admin.get_webhook_logs()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
