#!/usr/bin/env python3
"""
Automatic Open WebUI Configuration Script
Pre-configures all LLM models to work out of the box
"""

import requests
import json
import time
import sys
from datetime import datetime

class OpenWebUIConfigurator:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.api_base = "http://host.docker.internal:8080"
        self.webhook_url = "http://host.docker.internal:8080/webhooks/openwebui-rating"
        self.admin_email = "admin@tilores.com"
        self.admin_password = "TiloresAdmin123!"
        self.auth_token = None

    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def wait_for_ready(self, max_attempts: int = 30):
        """Wait for Open WebUI to be ready"""
        self.log("Waiting for Open WebUI to be ready...")
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{self.base_url}/api/config", timeout=5)
                if response.status_code == 200:
                    self.log("✅ Open WebUI is ready!")
                    return True
            except Exception as e:
                if attempt < max_attempts - 1:
                    self.log(f"Attempt {attempt + 1}/{max_attempts}: Not ready yet, waiting...")
                    time.sleep(2)
                else:
                    self.log(f"❌ Failed to connect after {max_attempts} attempts: {e}")
                    return False
        return False

    def check_onboarding_status(self):
        """Check if onboarding is needed"""
        try:
            response = requests.get(f"{self.base_url}/api/config")
            if response.status_code == 200:
                config = response.json()
                needs_onboarding = config.get("onboarding", False)
                self.log(f"Onboarding needed: {needs_onboarding}")
                return needs_onboarding
        except Exception as e:
            self.log(f"❌ Error checking onboarding status: {e}")
            return True

    def complete_onboarding(self):
        """Complete initial onboarding and create admin user"""
        self.log("🚀 Starting onboarding process...")

        # Try to register admin user
        register_data = {
            "name": "Tilores Admin",
            "email": self.admin_email,
            "password": self.admin_password,
            "role": "admin"
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auths/signup",
                json=register_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code in [200, 201]:
                self.log("✅ Admin user created successfully")
                return True
            elif response.status_code == 400:
                # User might already exist, try to login
                self.log("ℹ️ Admin user may already exist, attempting login...")
                return self.login()
            else:
                self.log(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.log(f"❌ Registration error: {e}")
            return False

    def login(self):
        """Login and get authentication token"""
        self.log("🔐 Logging in...")

        login_data = {
            "email": self.admin_email,
            "password": self.admin_password
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auths/signin",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                if self.auth_token:
                    self.log("✅ Login successful, token obtained")
                    return True
                else:
                    self.log("❌ Login successful but no token received")
                    return False
            else:
                self.log(f"❌ Login failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.log(f"❌ Login error: {e}")
            return False

    def get_auth_headers(self):
        """Get headers with authentication"""
        if not self.auth_token:
            return {"Content-Type": "application/json"}
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}"
        }

    def add_model(self, model_id: str, model_name: str):
        """Add a model configuration"""
        self.log(f"➕ Adding model: {model_name}")

        model_data = {
            "id": model_id,
            "name": model_name,
            "meta": {
                "description": f"Tilores {model_name} - Credit Analysis API",
                "capabilities": {
                    "vision": False,
                    "usage": True
                }
            },
            "base_url": self.api_base,
            "api_key": "dummy",
            "api_type": "openai"
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/models/add",
                json=model_data,
                headers=self.get_auth_headers()
            )

            if response.status_code in [200, 201]:
                self.log(f"✅ Model {model_name} added successfully")
                return True
            else:
                self.log(f"❌ Failed to add model {model_name}: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.log(f"❌ Error adding model {model_name}: {e}")
            return False

    def set_default_model(self, model_id: str):
        """Set the default model"""
        self.log(f"🎯 Setting default model: {model_id}")

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/configs/default/update",
                json={"default_models": [model_id]},
                headers=self.get_auth_headers()
            )

            if response.status_code == 200:
                self.log(f"✅ Default model set to {model_id}")
                return True
            else:
                self.log(f"❌ Failed to set default model: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.log(f"❌ Error setting default model: {e}")
            return False

    def configure_webhook(self):
        """Configure rating webhook"""
        self.log("🔗 Configuring rating webhook...")

        webhook_data = {
            "url": self.webhook_url,
            "events": ["rating.created"]
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/configs/webhook/update",
                json=webhook_data,
                headers=self.get_auth_headers()
            )

            if response.status_code == 200:
                self.log("✅ Rating webhook configured")
                return True
            else:
                self.log(f"⚠️ Webhook configuration may not be supported: {response.status_code}")
                return False

        except Exception as e:
            self.log(f"⚠️ Webhook configuration error (may not be supported): {e}")
            return False

    def test_model(self, model_id: str):
        """Test a model with a simple query"""
        self.log(f"🧪 Testing model: {model_id}")

        test_data = {
            "model": model_id,
            "messages": [
                {"role": "user", "content": "What is the account status for e.j.price1986@gmail.com?"}
            ],
            "stream": False
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/chat/completions",
                json=test_data,
                headers=self.get_auth_headers(),
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if "Active" in content and "Esteban" in content:
                    self.log(f"✅ Model {model_id} test successful - returned valid response")
                    return True
                else:
                    self.log(f"⚠️ Model {model_id} responded but content may be incorrect")
                    return False
            else:
                self.log(f"❌ Model {model_id} test failed: {response.status_code}")
                return False

        except Exception as e:
            self.log(f"❌ Model {model_id} test error: {e}")
            return False

    def run_full_configuration(self):
        """Run complete configuration process"""
        self.log("🚀 Starting Open WebUI Full Configuration...")
        self.log("=" * 60)

        # Step 1: Wait for service
        if not self.wait_for_ready():
            self.log("❌ Open WebUI not ready, aborting")
            return False

        # Step 2: Check onboarding
        needs_onboarding = self.check_onboarding_status()

        # Step 3: Complete onboarding if needed
        if needs_onboarding:
            if not self.complete_onboarding():
                self.log("❌ Onboarding failed, aborting")
                return False
        else:
            # Try to login with existing credentials
            if not self.login():
                self.log("❌ Login failed, aborting")
                return False

        # Step 4: Add models (matching Tilores API configuration)
        models = [
            ("gpt-4o-mini", "Tilores GPT-4o Mini"),
            ("gpt-4o", "Tilores GPT-4o"),
            ("gpt-3.5-turbo", "Tilores GPT-3.5 Turbo")
        ]

        successful_models = []
        for model_id, model_name in models:
            if self.add_model(model_id, model_name):
                successful_models.append(model_id)

        if not successful_models:
            self.log("❌ No models were added successfully")
            return False

        # Step 5: Set default model
        default_model = successful_models[0]  # Use first successful model
        self.set_default_model(default_model)

        # Step 6: Configure webhook (optional)
        self.configure_webhook()

        # Step 7: Test models
        self.log("\n🧪 Testing Models...")
        working_models = []
        for model_id in successful_models:
            if self.test_model(model_id):
                working_models.append(model_id)

        # Summary
        self.log("\n" + "=" * 60)
        self.log("📊 CONFIGURATION SUMMARY")
        self.log("=" * 60)
        self.log(f"✅ Models Added: {len(successful_models)}")
        self.log(f"✅ Models Working: {len(working_models)}")
        self.log(f"🎯 Default Model: {default_model}")
        self.log(f"🔐 Admin Credentials: {self.admin_email} / {self.admin_password}")

        if working_models:
            self.log("\n🎉 Configuration Complete! Open WebUI is ready to use.")
            self.log(f"🌐 Access at: {self.base_url}")
            self.log("📋 Test Queries:")
            self.log('   - "What is the account status for e.j.price1986@gmail.com?"')
            self.log('   - "What is the credit analysis for e.j.price1986@gmail.com?"')
            return True
        else:
            self.log("\n❌ Configuration completed but no models are working properly")
            return False

if __name__ == "__main__":
    configurator = OpenWebUIConfigurator()
    success = configurator.run_full_configuration()

    if success:
        print(f"\n🎊 SUCCESS! Open WebUI is fully configured and ready!")
        print(f"🌐 Open: http://localhost:3000")
        print(f"🔐 Login: {configurator.admin_email} / {configurator.admin_password}")
    else:
        print(f"\n⚠️ Configuration had issues. Check the logs above.")
        sys.exit(1)
