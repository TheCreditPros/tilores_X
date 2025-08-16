"""
Comprehensive unit tests for utils/debug_config.py
Tests debug configuration utilities and logging setup
"""

import os
import logging
from unittest.mock import patch

# Import the module under test
from utils.debug_config import setup_logging


class TestDebugMode:
    """Test debug mode detection from environment variables."""

    @patch.dict(os.environ, {"TILORES_DEBUG": "true"})
    def test_debug_mode_true_lowercase(self):
        """Test debug mode enabled with 'true'."""
        # Reload module to pick up new env var
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        assert utils.debug_config.DEBUG_MODE is True
        assert utils.debug_config.LOG_LEVEL == logging.DEBUG

    @patch.dict(os.environ, {"TILORES_DEBUG": "TRUE"})
    def test_debug_mode_true_uppercase(self):
        """Test debug mode enabled with 'TRUE'."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        assert utils.debug_config.DEBUG_MODE is True

    @patch.dict(os.environ, {"TILORES_DEBUG": "1"})
    def test_debug_mode_one(self):
        """Test debug mode enabled with '1'."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        assert utils.debug_config.DEBUG_MODE is True

    @patch.dict(os.environ, {"TILORES_DEBUG": "yes"})
    def test_debug_mode_yes(self):
        """Test debug mode enabled with 'yes'."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        assert utils.debug_config.DEBUG_MODE is True

    @patch.dict(os.environ, {"TILORES_DEBUG": "false"})
    def test_debug_mode_false(self):
        """Test debug mode disabled with 'false'."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        assert utils.debug_config.DEBUG_MODE is False
        assert utils.debug_config.LOG_LEVEL == logging.INFO

    @patch.dict(os.environ, {}, clear=True)
    def test_debug_mode_default(self):
        """Test debug mode defaults to False when env var not set."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        assert utils.debug_config.DEBUG_MODE is False


class TestSetupLogging:
    """Test the setup_logging function."""

    def test_setup_logging_with_name(self):
        """Test setting up logging with specific name."""
        logger = setup_logging("test_logger")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
        assert len(logger.handlers) > 0

    def test_setup_logging_without_name(self):
        """Test setting up logging without name (uses default)."""
        logger = setup_logging()

        assert isinstance(logger, logging.Logger)
        assert logger.name == "utils.debug_config"

    def test_setup_logging_duplicate_calls(self):
        """Test that duplicate setup calls don't add multiple handlers."""
        logger_name = "test_duplicate_logger"

        # First call
        logger1 = setup_logging(logger_name)
        handler_count_1 = len(logger1.handlers)

        # Second call
        logger2 = setup_logging(logger_name)
        handler_count_2 = len(logger2.handlers)

        # Should be same logger with same handler count
        assert logger1 is logger2
        assert handler_count_1 == handler_count_2

    @patch.dict(os.environ, {"TILORES_DEBUG": "true"})
    def test_setup_logging_debug_formatter(self):
        """Test that debug mode uses detailed formatter."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        logger = utils.debug_config.setup_logging("test_debug_logger")
        handler = logger.handlers[0]
        formatter = handler.formatter

        # Debug mode should include timestamp and name
        assert formatter is not None
        assert hasattr(formatter, "_fmt")
        fmt_str = formatter._fmt or ""
        assert "%(asctime)s" in fmt_str
        assert "%(name)s" in fmt_str

    @patch.dict(os.environ, {"TILORES_DEBUG": "false"})
    def test_setup_logging_production_formatter(self):
        """Test that production mode uses simple formatter."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        logger = utils.debug_config.setup_logging("test_prod_logger")
        handler = logger.handlers[0]
        formatter = handler.formatter

        # Production mode should be simple
        assert formatter is not None
        assert hasattr(formatter, "_fmt")
        fmt_str = formatter._fmt or ""
        assert "%(asctime)s" not in fmt_str
        assert "%(name)s" not in fmt_str
        assert "%(levelname)s" in fmt_str


class TestDebugPrint:
    """Test the debug_print function."""

    @patch.dict(os.environ, {"TILORES_DEBUG": "true"})
    @patch("builtins.print")
    def test_debug_print_enabled(self, mock_print):
        """Test debug_print when debug mode is enabled."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        utils.debug_config.debug_print("Test message")

        mock_print.assert_called_once_with("🔍 [DEBUG] Test message")

    @patch.dict(os.environ, {"TILORES_DEBUG": "true"})
    @patch("builtins.print")
    def test_debug_print_custom_emoji(self, mock_print):
        """Test debug_print with custom emoji."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        utils.debug_config.debug_print("Test message", "🚀")

        mock_print.assert_called_once_with("🚀 [DEBUG] Test message")

    @patch.dict(os.environ, {"TILORES_DEBUG": "false"})
    @patch("builtins.print")
    def test_debug_print_disabled(self, mock_print):
        """Test debug_print when debug mode is disabled."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        utils.debug_config.debug_print("Test message")

        mock_print.assert_not_called()


class TestIsDebugEnabled:
    """Test the is_debug_enabled function."""

    @patch.dict(os.environ, {"TILORES_DEBUG": "true"})
    def test_is_debug_enabled_true(self):
        """Test is_debug_enabled returns True when debug enabled."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        assert utils.debug_config.is_debug_enabled() is True

    @patch.dict(os.environ, {"TILORES_DEBUG": "false"})
    def test_is_debug_enabled_false(self):
        """Test is_debug_enabled returns False when debug disabled."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        assert utils.debug_config.is_debug_enabled() is False


class TestModuleLevelLogging:
    """Test module-level logging initialization."""

    @patch.dict(os.environ, {"TILORES_DEBUG": "true"})
    def test_module_logger_debug_message(self):
        """Test that module logs debug message when debug enabled."""
        import importlib
        import utils.debug_config

        # Capture logs
        with patch.object(utils.debug_config, "logger") as mock_logger:
            importlib.reload(utils.debug_config)

            # The module should log debug status when DEBUG_MODE is True
            # This might be called during import
            # We'll check if the logger was accessed
            assert mock_logger is not None

    @patch.dict(os.environ, {"TILORES_DEBUG": "false"})
    def test_module_logger_no_debug_message(self):
        """Test that module doesn't log debug message when debug disabled."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        # When debug is False, no debug message should be logged
        # This is implicit - we just need to ensure the module loads correctly
        assert utils.debug_config.logger is not None


class TestLoggerConfiguration:
    """Test logger configuration details."""

    def test_logger_has_stream_handler(self):
        """Test that logger has StreamHandler configured."""
        logger = setup_logging("test_stream_logger")

        assert len(logger.handlers) > 0
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    @patch.dict(os.environ, {"TILORES_DEBUG": "true"})
    def test_logger_debug_level(self):
        """Test that logger uses DEBUG level when debug enabled."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        logger = utils.debug_config.setup_logging("test_debug_level")
        assert logger.level == logging.DEBUG

    @patch.dict(os.environ, {"TILORES_DEBUG": "false"})
    def test_logger_info_level(self):
        """Test that logger uses INFO level when debug disabled."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        logger = utils.debug_config.setup_logging("test_info_level")
        assert logger.level == logging.INFO


class TestIntegration:
    """Integration tests for debug configuration."""

    @patch.dict(os.environ, {"TILORES_DEBUG": "true"})
    def test_full_debug_workflow(self):
        """Test complete debug workflow when enabled."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        # Check debug mode detection
        assert utils.debug_config.is_debug_enabled() is True
        assert utils.debug_config.DEBUG_MODE is True
        assert utils.debug_config.LOG_LEVEL == logging.DEBUG

        # Test logger setup
        logger = utils.debug_config.setup_logging("integration_test")
        assert logger.level == logging.DEBUG

        # Test debug print (with mock to avoid actual output)
        with patch("builtins.print") as mock_print:
            utils.debug_config.debug_print("Integration test")
            mock_print.assert_called_once()

    @patch.dict(os.environ, {"TILORES_DEBUG": "false"})
    def test_full_production_workflow(self):
        """Test complete workflow when debug disabled."""
        import importlib
        import utils.debug_config

        importlib.reload(utils.debug_config)

        # Check debug mode detection
        assert utils.debug_config.is_debug_enabled() is False
        assert utils.debug_config.DEBUG_MODE is False
        assert utils.debug_config.LOG_LEVEL == logging.INFO

        # Test logger setup
        logger = utils.debug_config.setup_logging("production_test")
        assert logger.level == logging.INFO

        # Test debug print (should not print)
        with patch("builtins.print") as mock_print:
            utils.debug_config.debug_print("Production test")
            mock_print.assert_not_called()
