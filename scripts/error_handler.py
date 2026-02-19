"""
Error Handler and Recovery Module

Provides error handling, retry logic, and graceful degradation for the AI Employee.

Usage:
    from scripts.error_handler import ErrorHandler, with_retry
"""

import time
import logging
from functools import wraps
from datetime import datetime
from pathlib import Path
from typing import Callable, Any


class TransientError(Exception):
    """Error that may succeed on retry (network timeout, rate limit, etc.)"""
    pass


class AuthenticationError(Exception):
    """Error requiring re-authentication"""
    pass


class LogicError(Exception):
    """Error requiring human review"""
    pass


class DataError(Exception):
    """Error with data integrity"""
    pass


class SystemError(Exception):
    """System-level error requiring restart"""
    pass


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential: bool = True
):
    """
    Decorator for retry logic with exponential backoff.

    Usage:
        @with_retry(max_attempts=3, base_delay=2)
        def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except TransientError as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        if exponential:
                            delay = min(base_delay * (2 ** attempt), max_delay)
                        else:
                            delay = base_delay
                        logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                except (AuthenticationError, LogicError, DataError):
                    # Don't retry these
                    raise
                except Exception as e:
                    # Unexpected errors - retry once
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logging.warning(f"Unexpected error: {e}. Retrying...")
                        time.sleep(base_delay)

            # All attempts failed
            raise last_exception

        return wrapper
    return decorator


class ErrorHandler:
    """Centralized error handling for the AI Employee."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.error_folder = self.vault_path / 'Errors'
        self.error_folder.mkdir(parents=True, exist_ok=True)

    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: dict = None,
        severity: str = 'medium'
    ):
        """Log an error to the error tracking system."""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': error_message,
            'context': context or {},
            'severity': severity,
            'resolved': False
        }

        # Save to errors folder
        error_file = self.error_folder / f"{error_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        import json
        with open(error_file, 'w') as f:
            json.dump(error_entry, f, indent=2)

        logging.error(f"Error logged: {error_type} - {error_message}")

        return error_file

    def get_recent_errors(self, hours: int = 24, severity: str = None):
        """Get recent errors, optionally filtered by severity."""
        import json
        errors = []
        cutoff = datetime.now().timestamp() - (hours * 3600)

        for error_file in self.error_folder.glob('*.json'):
            try:
                with open(error_file) as f:
                    error = json.load(f)

                error_time = datetime.fromisoformat(error['timestamp']).timestamp()
                if error_time < cutoff:
                    continue

                if severity and error.get('severity') != severity:
                    continue

                errors.append(error)
            except:
                continue

        return sorted(errors, key=lambda x: x['timestamp'], reverse=True)

    def get_unresolved_errors(self):
        """Get all unresolved errors."""
        import json
        errors = []

        for error_file in self.error_folder.glob('*.json'):
            try:
                with open(error_file) as f:
                    error = json.load(f)

                if not error.get('resolved', False):
                    errors.append(error)
            except:
                continue

        return errors


class GracefulDegradation:
    """Handle component failures gracefully."""

    def __init__(self):
        self.failed_components = set()

    def mark_failed(self, component: str):
        """Mark a component as failed."""
        self.failed_components.add(component)
        logging.warning(f"Component '{component}' marked as failed")

    def mark_recovered(self, component: str):
        """Mark a component as recovered."""
        self.failed_components.discard(component)
        logging.info(f"Component '{component}' recovered")

    def is_available(self, component: str) -> bool:
        """Check if a component is available."""
        return component not in self.failed_components

    def get_status(self) -> dict:
        """Get overall system status."""
        return {
            'healthy': len(self.failed_components) == 0,
            'failed_components': list(self.failed_components)
        }


# Singleton instances
_error_handler = None
_degradation = None


def get_error_handler(vault_path: str = None) -> ErrorHandler:
    """Get or create the error handler singleton."""
    global _error_handler
    if _error_handler is None and vault_path:
        _error_handler = ErrorHandler(vault_path)
    return _error_handler


def get_degradation() -> GracefulDegradation:
    """Get or create the degradation handler singleton."""
    global _degradation
    if _degradation is None:
        _degradation = GracefulDegradation()
    return _degradation
