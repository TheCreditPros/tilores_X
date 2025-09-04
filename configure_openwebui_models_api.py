#!/usr/bin/env python3
"""
Automated Open WebUI Model Configuration
Configures all 9 Tilores models via API
"""

import requests
import json
import time
from datetime import datetime

class OpenWebUIModelConfigurator:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.api_base = "http://host.docker.internal:8080"
        self.admin_email = "damon@thecreditpros.com"
        self.admin_password = "Credit@123"
        self.auth_token = None

        # All 9 Tilores models
        self.models = [
            # OpenAI models
            {"id": "gpt-4o-mini", "name": "Tilores GPT-4o Mini", "provider": "OpenAI"},
            {"id": "gpt-4o", "name": "Tilores GPT-4o", "provider": "OpenAI"},
            {"id": "gpt-3.5-turbo", "name": "Tilores GPT-3.5 Turbo", "provider": "OpenAI"},
            # Google Gemini models
            {"id": "gemini-1.5-flash", "name": "Tilores Gemini 1.5 Flash", "provider": "Google"},
            {"id": "gemini-1.5-pro", "name": "Tilores Gemini 1.5 Pro", "provider": "Google"},
            {"id": "gemini-2.0-flash-exp", "name": "Tilores Gemini 2.0 Flash Experimental", "provider": "Google"},
            {"id": "gemini-2.5-flash", "name": "Tilores Gemini 2.5 Flash", "provider": "Google"},
            # Groq models
            {"id": "llama-3.3-70b-versatile", "name": "Tilores Llama 3.3 70B Versatile", "provider": "Groq"},
            {"id": "deepseek-r1-distill-llama-70b", "name": "Tilores DeepSeek R1 Distill Llama 70B", "provider": "Groq"}
        ]

    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def wait_for_ready(self, max_attempts: int = 30):
        """Wait for Open WebUI to be ready"""
        self.log("Waiting for Open WebUI to be ready...")
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
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

    def add_model(self, model_config):
        """Add a single model configuration"""
        self.log(f"➕ Adding model: {model_config['name']}")

        model_data = {
            "id": model_config["id"],
            "name": model_config["name"],
            "meta": {
                "description": f"{model_config['name']} - Tilores Credit Analysis API",
                "provider": model_config["provider"]
            },
            "base_url": self.api_base,
            "api_key": "dummy"
        }

        try:
            # Try different API endpoints that might work
            endpoints = [
                "/api/v1/models/add",
                "/api/models/add",
                "/api/v1/models",
                "/api/models"
            ]

            for endpoint in endpoints:
                try:
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=model_data,
                        headers=self.get_auth_headers()
                    )

                    if response.status_code in [200, 201]:
                        self.log(f"✅ Model {model_config['name']} added successfully via {endpoint}")
                        return True
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        self.log(f"⚠️ Endpoint {endpoint} returned {response.status_code}: {response.text}")

                except Exception as e:
                    self.log(f"⚠️ Error with endpoint {endpoint}: {e}")
                    continue

            self.log(f"❌ Failed to add model {model_config['name']} - no working endpoint found")
            return False

        except Exception as e:
            self.log(f"❌ Error adding model {model_config['name']}: {e}")
            return False

    def set_default_model(self, model_id: str):
        """Set the default model"""
        self.log(f"🎯 Setting default model: {model_id}")

        try:
            endpoints = [
                "/api/v1/configs/default/update",
                "/api/configs/default/update",
                "/api/v1/settings/default_model",
                "/api/settings/default_model"
            ]

            for endpoint in endpoints:
                try:
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json={"default_model": model_id},
                        headers=self.get_auth_headers()
                    )

                    if response.status_code == 200:
                        self.log(f"✅ Default model set to {model_id}")
                        return True
                    elif response.status_code == 404:
                        continue

                except Exception as e:
                    continue

            self.log(f"⚠️ Could not set default model (API endpoints may not be available)")
            return False

        except Exception as e:
            self.log(f"❌ Error setting default model: {e}")
            return False

    def configure_all_models(self):
        """Configure all Tilores models"""
        self.log("🚀 Starting Tilores Model Configuration...")
        self.log("=" * 60)

        # Step 1: Wait for service
        if not self.wait_for_ready():
            self.log("❌ Open WebUI not ready, aborting")
            return False

        # Step 2: Login
        if not self.login():
            self.log("❌ Login failed, aborting")
            return False

        # Step 3: Add all models
        successful_models = []
        for model_config in self.models:
            if self.add_model(model_config):
                successful_models.append(model_config["id"])

        # Step 4: Set default model
        if successful_models:
            default_model = "gpt-4o-mini"  # Recommended default
            self.set_default_model(default_model)

        # Summary
        self.log("\n" + "=" * 60)
        self.log("📊 CONFIGURATION SUMMARY")
        self.log("=" * 60)
        self.log(f"✅ Models Configured: {len(successful_models)}/{len(self.models)}")

        if successful_models:
            self.log("✅ Successfully configured models:")
            for model_id in successful_models:
                model_name = next(m["name"] for m in self.models if m["id"] == model_id)
                self.log(f"   ✅ {model_id} - {model_name}")

        failed_models = [m["id"] for m in self.models if m["id"] not in successful_models]
        if failed_models:
            self.log("❌ Failed to configure:")
            for model_id in failed_models:
                self.log(f"   ❌ {model_id}")

        if len(successful_models) >= 3:  # At least some models working
            self.log("\n🎉 Model configuration completed! You can now test the models.")
            self.log("🌐 Open WebUI: http://localhost:3000")
            return True
        else:
            self.log("\n⚠️ Model configuration had issues. Manual setup may be required.")
            return False

if __name__ == "__main__":
    configurator = OpenWebUIModelConfigurator()
    success = configurator.configure_all_models()

    if success:
        print(f"\n🎊 SUCCESS! Models are configured and ready!")
        print(f"🌐 Test at: http://localhost:3000")
    else:
        print(f"\n⚠️ Configuration had issues. You may need to add models manually in the UI.")
        print(f"📋 Manual setup guide: COMPLETE_TILORES_MODELS_SETUP.md")
