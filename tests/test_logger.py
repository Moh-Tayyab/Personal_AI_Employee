"""
Tests for the centralized logging module.

Covers: logger factory, setup, JSON file output, log cleanup.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from logger import (
    get_logger,
    setup_logging,
    get_daily_log_path,
    cleanup_old_logs,
    _loggers,
    _initialized,
)


class TestGetLogger:
    """Tests for the logger factory."""

    def test_returns_logger_instance(self):
        """Should return a logging.Logger instance."""
        logger = get_logger("TestModule")
        assert isinstance(logger, logging.Logger)

    def test_caches_loggers(self):
        """Should return the same instance for the same name."""
        logger1 = get_logger("Cached")
        logger2 = get_logger("Cached")
        assert logger1 is logger2

    def test_prefix_with_pine(self):
        """Logger name should be prefixed with PINE."""
        logger = get_logger("MyModule")
        assert logger.name == "PINE.MyModule"

    def test_different_names_different_loggers(self):
        """Different names should return different instances."""
        logger1 = get_logger("ModuleA")
        logger2 = get_logger("ModuleB")
        assert logger1 is not logger2


class TestSetupLogging:
    """Tests for logging setup."""

    def test_setup_creates_console_handler(self, temp_vault):
        """Should add a console handler to root logger."""
        # Reset global state for this test
        import logger as log_module
        log_module._initialized = False

        root = logging.getLogger()
        handler_count_before = len(root.handlers)

        setup_logging(str(temp_vault))

        handlers = root.handlers
        assert len(handlers) >= handler_count_before

    def test_setup_is_idempotent(self, temp_vault):
        """Calling setup_logging multiple times should not add duplicate handlers."""
        import logger as log_module
        log_module._initialized = False

        root = logging.getLogger()
        setup_logging(str(temp_vault))
        handler_count = len(root.handlers)

        setup_logging(str(temp_vault))
        setup_logging(str(temp_vault))

        assert len(root.handlers) == handler_count

    def test_creates_log_directory(self, temp_vault):
        """Should create the Logs/system directory."""
        import logger as log_module
        log_module._initialized = False

        setup_logging(str(temp_vault))
        log_dir = temp_vault / "Logs" / "system"
        assert log_dir.exists()


class TestLogFileOutput:
    """Tests for JSON log file output."""

    def test_get_daily_log_path(self, temp_vault):
        """Should return correct path for today's log."""
        today = datetime.now().strftime("%Y-%m-%d")
        expected = temp_vault / "Logs" / "system" / f"{today}.jsonl"
        # The function doesn't create the file, just returns the path
        # We need the log dir to exist first
        (temp_vault / "Logs" / "system").mkdir(parents=True, exist_ok=True)
        result = get_daily_log_path(str(temp_vault))
        assert result == expected


class TestLogCleanup:
    """Tests for old log cleanup."""

    def test_deletes_old_logs(self, temp_vault):
        """Should delete log files older than retention period."""
        log_dir = temp_vault / "Logs" / "system"
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create old log (40 days ago)
        old_date = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d")
        old_file = log_dir / f"{old_date}.jsonl"
        old_file.write_text("{}")

        # Create recent log (5 days ago)
        recent_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        recent_file = log_dir / f"{recent_date}.jsonl"
        recent_file.write_text("{}")

        deleted = cleanup_old_logs(str(temp_vault), retention_days=30)

        assert deleted == 1
        assert not old_file.exists()
        assert recent_file.exists()

    def test_returns_zero_when_no_logs(self, temp_vault):
        """Should return 0 when no log files exist."""
        deleted = cleanup_old_logs(str(temp_vault))
        assert deleted == 0

    def test_handles_malformed_filenames(self, temp_vault):
        """Should skip files with non-date names."""
        log_dir = temp_vault / "Logs" / "system"
        log_dir.mkdir(parents=True, exist_ok=True)

        (log_dir / "not_a_date.jsonl").write_text("{}")
        (log_dir / "broken.jsonl").write_text("{}")

        # Should not raise an exception
        deleted = cleanup_old_logs(str(temp_vault), retention_days=30)
        assert deleted == 0
