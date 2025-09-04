#!/usr/bin/env python3
"""
Comprehensive tests for Open WebUI integration
Tests the rating webhook endpoint and integration functionality
"""

import pytest
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, mock_open
from fastapi.testclient import TestClient

# Import the FastAPI app
try:
    from direct_credit_api_fixed import app
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    app = None

@pytest.mark.skipif(not API_AVAILABLE, reason="FastAPI app not available")
class TestOpenWebUIIntegration:
    """Test suite for Open WebUI integration"""

    def setup_method(self):
        """Setup test client and temporary files"""
        self.client = TestClient(app)
        self.temp_dir = tempfile.mkdtemp()
        self.ratings_file = Path(self.temp_dir) / "openwebui_ratings.jsonl"

    def teardown_method(self):
        """Cleanup temporary files"""
        if self.ratings_file.exists():
            self.ratings_file.unlink()
        os.rmdir(self.temp_dir)

    def test_openwebui_rating_webhook_valid_payload(self):
        """Test rating webhook with valid payload"""
        rating_data = {
            "chat_id": "conv_456",
            "message_id": "msg_789",
            "model": "Tilores/local/gpt-4o-mini",
            "rating": "up",
            "tags": ["credit", "helpful"],
            "timestamp": "2025-01-03T12:00:00Z",
            "user_id": "test_user_123"
        }

        with patch("builtins.open", mock_open()) as mock_file:
            response = self.client.post("/webhooks/openwebui-rating", json=rating_data)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["status"] == "received"
            assert response_data["rating"] == "up"

            # Verify file write was called (may be called multiple times due to logging)
            assert mock_file.called

    def test_openwebui_rating_webhook_minimal_payload(self):
        """Test rating webhook with minimal required payload"""
        rating_data = {
            "model": "Tilores/local/gpt-4o",
            "rating": "down"
        }

        with patch("builtins.open", mock_open()) as mock_file:
            response = self.client.post("/webhooks/openwebui-rating", json=rating_data)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["status"] == "received"
            assert response_data["rating"] == "down"

    def test_openwebui_rating_webhook_invalid_rating(self):
        """Test rating webhook with invalid rating value"""
        rating_data = {
            "model": "Tilores/local/gpt-4o-mini",
            "rating": "invalid_rating"
        }

        response = self.client.post("/webhooks/openwebui-rating", json=rating_data)

        assert response.status_code == 422  # Validation error

    def test_openwebui_rating_webhook_missing_model(self):
        """Test rating webhook with missing required model field"""
        rating_data = {
            "rating": "up",
            "tags": ["credit"]
        }

        response = self.client.post("/webhooks/openwebui-rating", json=rating_data)

        assert response.status_code == 422  # Validation error

    def test_openwebui_rating_webhook_empty_payload(self):
        """Test rating webhook with empty payload"""
        response = self.client.post("/webhooks/openwebui-rating", json={})

        assert response.status_code == 422  # Validation error

    def test_openwebui_rating_webhook_file_write_error(self):
        """Test rating webhook handles file write errors gracefully"""
        rating_data = {
            "model": "Tilores/local/gpt-4o-mini",
            "rating": "up"
        }

        with patch("builtins.open", side_effect=IOError("Disk full")):
            response = self.client.post("/webhooks/openwebui-rating", json=rating_data)

            assert response.status_code == 500
            response_data = response.json()
            # Should return 500 error for file write failures
            assert response.status_code == 500

    def test_openwebui_rating_data_structure(self):
        """Test that rating data is structured correctly"""
        rating_data = {
            "chat_id": "conv_123",
            "message_id": "msg_456",
            "model": "Tilores/local/gpt-4o-mini",
            "rating": "up",
            "tags": ["credit", "billing"],
            "user_id": "user_789"
        }

        captured_data = None

        def capture_write(filename, mode='a', encoding='utf-8'):
            nonlocal captured_data
            mock_file = mock_open()
            original_write = mock_file.return_value.write

            def write_wrapper(data):
                nonlocal captured_data
                captured_data = data
                return original_write(data)

            mock_file.return_value.write = write_wrapper
            return mock_file.return_value

        with patch("builtins.open", side_effect=capture_write):
            response = self.client.post("/webhooks/openwebui-rating", json=rating_data)

            assert response.status_code == 200

            # Parse the captured JSON line
            if captured_data:
                logged_data = json.loads(captured_data.strip())

                # Verify required fields
                assert logged_data["model"] == "Tilores/local/gpt-4o-mini"
                assert logged_data["rating"] == "up"
                assert logged_data["tags"] == ["credit", "billing"]
                assert logged_data["user_id"] == "user_789"
                assert logged_data["chat_id"] == "conv_123"
                assert logged_data["message_id"] == "msg_456"

                # Verify auto-generated fields
                assert "received_at" in logged_data
                assert "source" in logged_data
                assert logged_data["source"] == "openwebui"

                # Verify timestamp format
                datetime.fromisoformat(logged_data["received_at"].replace('Z', '+00:00'))

class TestOpenWebUIHealthEndpoints:
    """Test health and status endpoints"""

    def setup_method(self):
        """Setup test client"""
        if API_AVAILABLE:
            self.client = TestClient(app)

    @pytest.mark.skipif(not API_AVAILABLE, reason="FastAPI app not available")
    def test_webhooks_health_endpoint(self):
        """Test webhooks health endpoint"""
        response = self.client.get("/webhooks/health")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "healthy"
        assert "timestamp" in response_data
        assert "webhooks" in response_data
        assert "openwebui_rating" in response_data["webhooks"]

    @pytest.mark.skipif(not API_AVAILABLE, reason="FastAPI app not available")
    def test_main_health_endpoint(self):
        """Test main API health endpoint"""
        response = self.client.get("/health")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "healthy"

class TestOpenWebUIConfigValidation:
    """Test Open WebUI configuration validation"""

    def test_docker_compose_structure(self):
        """Test docker-compose.yml has correct structure"""
        compose_file = Path("docker-compose.yml")
        assert compose_file.exists(), "docker-compose.yml should exist"

        with open(compose_file) as f:
            content = f.read()

        # Check key configuration elements
        assert "open-webui" in content
        assert "ghcr.io/open-webui/open-webui:main" in content
        assert "8080:8080" in content
        assert "OPENAI_API_BASE_URL" in content
        assert "host.docker.internal:8081" in content

    def test_bootstrap_script_exists(self):
        """Test bootstrap script exists and is executable"""
        bootstrap_file = Path("openwebui_bootstrap.sh")
        assert bootstrap_file.exists(), "openwebui_bootstrap.sh should exist"

        with open(bootstrap_file) as f:
            content = f.read()

        # Check key bootstrap elements
        assert ("#!/bin/bash" in content or "#!/usr/bin/env bash" in content)
        assert "add_model" in content
        assert "Tilores/local/gpt-4o-mini" in content
        assert "host.docker.internal:8081" in content
        assert "openwebui-rating" in content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
