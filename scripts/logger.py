"""
Centralized Logging Module for Personal AI Employee

Provides a single entry point for all logging across the system.
Replaces individual logging.basicConfig() calls in each module with
a unified configuration.

Usage:
    from logger import get_logger

    logger = get_logger("MyModule")
    logger.info("Something happened")
    logger.error("Something failed", exc_info=True)

Features:
- Single logger factory (prevents duplicate handlers)
- Structured JSON log output for audit trail
- Per-module log levels
- Daily rotating log files in vault/Logs/
- Console output with colored levels (when supported)
"""

import sys
import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


# Module-level cache to prevent duplicate loggers
_loggers = {}
_initialized = False


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured processing."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data

        return json.dumps(log_entry)


class ColoredFormatter(logging.Formatter):
    """Console formatter with ANSI color codes for log levels."""

    COLORS = {
        "DEBUG": "\033[36m",       # Cyan
        "INFO": "\033[32m",        # Green
        "WARNING": "\033[33m",     # Yellow
        "ERROR": "\033[31m",       # Red
        "CRITICAL": "\033[35m",    # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        return (
            f"{color}{record.levelname:<8}{self.RESET} "
            f"[{record.name}] {record.getMessage()}"
        )


def setup_logging(
    vault_path: Optional[str] = None,
    level: int = logging.INFO,
    console_level: int = logging.INFO,
    json_log_file: bool = True,
) -> None:
    """
    Configure centralized logging for the entire application.

    Call this ONCE at application startup. Subsequent calls are no-ops.

    Args:
        vault_path: Path to the vault directory (for file logging)
        level: File log level (default: INFO)
        console_level: Console log level (default: INFO)
        json_log_file: Whether to write JSON log files (default: True)
    """
    global _initialized
    if _initialized:
        return

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture everything

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(ColoredFormatter("%(message)s"))
    root_logger.addHandler(console_handler)

    # File handler (JSON format, daily rotation)
    if json_log_file and vault_path:
        log_dir = Path(vault_path) / "Logs" / "system"
        log_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"{today}.jsonl"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)

    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module/component name (e.g., "Orchestrator", "GmailWatcher")

    Returns:
        Configured logger instance
    """
    if name not in _loggers:
        logger = logging.getLogger(f"PINE.{name}")
        # Don't propagate to root logger's handlers multiple times
        # (setup_logging adds handlers to root, so this is fine)
        _loggers[name] = logger

    return _loggers[name]


def get_daily_log_path(vault_path: str) -> Path:
    """Get the path to today's system log file."""
    today = datetime.now().strftime("%Y-%m-%d")
    return Path(vault_path) / "Logs" / "system" / f"{today}.jsonl"


def cleanup_old_logs(vault_path: str, retention_days: int = 30) -> int:
    """
    Remove log files older than retention period.

    Args:
        vault_path: Path to the vault
        retention_days: Number of days to keep logs

    Returns:
        Number of files deleted
    """
    log_dir = Path(vault_path) / "Logs" / "system"
    if not log_dir.exists():
        return 0

    cutoff = datetime.now()
    from datetime import timedelta
    cutoff = cutoff - timedelta(days=retention_days)

    deleted = 0
    for log_file in log_dir.glob("*.jsonl"):
        # Parse date from filename (YYYY-MM-DD.jsonl)
        try:
            file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
            if file_date < cutoff:
                log_file.unlink()
                deleted += 1
        except (ValueError, OSError):
            continue

    return deleted
