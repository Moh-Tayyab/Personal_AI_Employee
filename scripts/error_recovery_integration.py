"""
Orchestrator Error Recovery Integration

Provides decorators and utilities that embed Ralph Loop persistence and
Error Recovery circuit-breaker patterns directly into the orchestrator's
main orchestration loop.

Usage:
    from scripts.error_recovery_integration import (
        with_circuit_breaker,
        with_ralph_retry,
        RecoveryContext,
    )
"""

import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Callable, Any, Dict, Optional
from functools import wraps
from enum import Enum

logger = logging.getLogger("RecoveryIntegration")


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    TRANSIENT = "transient"
    AUTHENTICATION = "authentication"
    LOGIC = "logic"
    DATA = "data"
    SYSTEM = "system"


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures."""

    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open
        self.total_failures = 0
        self.total_successes = 0

    def record_success(self):
        self.failure_count = 0
        self.state = "closed"
        self.total_successes += 1

    def record_failure(self):
        self.failure_count += 1
        self.total_failures += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"⚡ Circuit breaker '{self.name}' OPEN after {self.failure_count} failures")

    def can_execute(self) -> bool:
        if self.state == "closed":
            return True

        if self.state == "open":
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self.state = "half-open"
                    logger.info(f"🔧 Circuit breaker '{self.name}' HALF-OPEN (testing recovery)")
                    return True
            return False

        return True  # half-open

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self.failure_count,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
        }


class RecoveryContext:
    """
    Central registry of circuit breakers for the orchestrator.

    All orchestrator methods share this context so circuit breakers
    provide system-wide protection, not just per-call protection.
    """

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.breakers: Dict[str, CircuitBreaker] = {
            "qwen_api": CircuitBreaker("qwen_api", failure_threshold=5, recovery_timeout=60),
            "gemini_api": CircuitBreaker("gemini_api", failure_threshold=5, recovery_timeout=60),
            "anthropic_api": CircuitBreaker("anthropic_api", failure_threshold=3, recovery_timeout=120),
            "openrouter_api": CircuitBreaker("openrouter_api", failure_threshold=3, recovery_timeout=60),
            "gmail": CircuitBreaker("gmail", failure_threshold=3, recovery_timeout=30),
            "odoo": CircuitBreaker("odoo", failure_threshold=5, recovery_timeout=60),
            "linkedin": CircuitBreaker("linkedin", failure_threshold=3, recovery_timeout=30),
            "twitter": CircuitBreaker("twitter", failure_threshold=3, recovery_timeout=30),
            "facebook": CircuitBreaker("facebook", failure_threshold=3, recovery_timeout=30),
            "filesystem": CircuitBreaker("filesystem", failure_threshold=10, recovery_timeout=10),
        }
        self.error_log = vault_path / "Logs" / "errors"
        self.error_log.mkdir(parents=True, exist_ok=True)
        self.quarantine_dir = vault_path / "Needs_Action" / "quarantine"
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        self.ralph_iterations = 0
        self.ralph_max_iterations = 10
        self.ralph_active = False

    def get_breaker(self, service: str) -> CircuitBreaker:
        return self.breakers.get(service, CircuitBreaker(service))

    def all_circuit_breakers_healthy(self) -> bool:
        """Check if all critical circuit breakers are closed."""
        critical = {"qwen_api", "gmail", "odoo"}
        for name in critical:
            breaker = self.breakers.get(name)
            if breaker and breaker.state == "open":
                return False
        return True

    def get_status_report(self) -> Dict[str, Any]:
        return {
            "timestamp": datetime.now().isoformat(),
            "ralph_mode": {
                "active": self.ralph_active,
                "iterations": self.ralph_iterations,
                "max_iterations": self.ralph_max_iterations,
            },
            "circuit_breakers": {
                name: cb.get_status() for name, cb in self.breakers.items()
            },
            "quarantined_items": len(list(self.quarantine_dir.glob("*"))) if self.quarantine_dir.exists() else 0,
        }

    def quarantine_item(self, item_path: Path, reason: str):
        """Move a repeatedly-failing item to quarantine."""
        if not self.quarantine_dir.exists():
            self.quarantine_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        quarantine_file = self.quarantine_dir / f"{item_path.stem}_quarantined_{timestamp}{item_path.suffix}"

        # Add quarantine metadata
        content = item_path.read_text() if item_path.exists() else ""
        metadata = f"""---
type: quarantined
original_file: {item_path.name}
reason: {reason}
quarantined_at: {datetime.now().isoformat()}
ralph_iterations: {self.ralph_iterations}
---

{content}
"""
        quarantine_file.write_text(metadata)

        if item_path.exists():
            item_path.unlink()

        self.log_error("item_quarantined", {
            "original": str(item_path),
            "reason": reason,
            "quarantine_file": str(quarantine_file),
        })
        logger.warning(f"🔒 Item quarantined: {item_path.name} → {quarantine_file.name}")

    def log_error(self, category: str, details: Dict[str, Any]):
        """Log error to the error log directory."""
        today = datetime.now().strftime("%Y-%m-%d")
        error_file = self.error_log / f"error_{today}_{self._error_counter():04d}.json"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "details": details,
        }

        try:
            error_file.write_text(json.dumps(entry, indent=2))
        except Exception as e:
            logger.error(f"Failed to write error log: {e}")

    def _error_counter(self) -> int:
        """Count existing error files today."""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.error_log.exists():
            return len(list(self.error_log.glob(f"error_{today}_*.json")))
        return 0


def _categorize_error(error: Exception) -> ErrorCategory:
    """Categorize an exception for appropriate handling."""
    msg = str(error).lower()

    if any(kw in msg for kw in ["auth", "token", "credential", "permission", "401", "403"]):
        return ErrorCategory.AUTHENTICATION
    if any(kw in msg for kw in ["timeout", "rate limit", "temporary", "retry", "503", "504", "connection"]):
        return ErrorCategory.TRANSIENT
    if any(kw in msg for kw in ["corrupt", "invalid", "missing", "parse", "format", "json"]):
        return ErrorCategory.DATA
    if any(kw in msg for kw in ["disk", "memory", "crash", "fatal", "segfault"]):
        return ErrorCategory.SYSTEM
    return ErrorCategory.LOGIC


def with_circuit_breaker(
    service: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
):
    """
    Decorator that wraps a method with circuit breaker + retry logic.

    Usage:
        @with_circuit_breaker("qwen_api", max_retries=3)
        def _process_with_multi_provider_ai(self, prompt):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get recovery context from self.recovery_ctx
            self_obj = args[0]
            ctx: RecoveryContext = getattr(self_obj, "recovery_ctx", None)
            if ctx is None:
                # No recovery context — just call the function directly
                return func(*args, **kwargs)

            breaker = ctx.get_breaker(service)

            # Check circuit breaker
            if not breaker.can_execute():
                logger.warning(f"⚡ Circuit breaker '{service}' is OPEN — skipping {func.__name__}")
                ctx.log_error("circuit_breaker_open", {
                    "function": func.__name__,
                    "service": service,
                    "state": breaker.state,
                })
                return None

            # Execute with retry
            last_error = None
            for attempt in range(1, max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    breaker.record_success()

                    if breaker.total_successes % 10 == 0:
                        logger.info(f"✅ {service} circuit breaker: {breaker.total_successes} successful calls")

                    return result

                except Exception as e:
                    last_error = e
                    category = _categorize_error(e)
                    breaker.record_failure()

                    logger.error(f"❌ {service} error in {func.__name__} (attempt {attempt}/{max_retries}): {e}")
                    ctx.log_error(f"{service}_failure", {
                        "function": func.__name__,
                        "attempt": attempt,
                        "category": category.value,
                        "error": str(e),
                        "circuit_breaker_state": breaker.state,
                    })

                    # Authentication errors should NOT be retried
                    if category == ErrorCategory.AUTHENTICATION:
                        logger.error(f"🔐 Authentication error — not retrying")
                        raise

                    # System errors should NOT be retried
                    if category == ErrorCategory.SYSTEM:
                        logger.error(f"💥 System error — not retrying")
                        raise

                    # Don't retry on last attempt
                    if attempt == max_retries:
                        logger.error(f"💔 {service} exhausted all {max_retries} retries for {func.__name__}")
                        break

                    # Exponential backoff
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.info(f"⏳ Retrying {func.__name__} in {delay:.1f}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)

            # All retries exhausted
            ctx.log_error("retries_exhausted", {
                "function": func.__name__,
                "service": service,
                "max_retries": max_retries,
                "last_error": str(last_error),
            })
            raise last_error

        return wrapper
    return decorator


def with_ralph_retry(max_iterations: int = 10):
    """
    Decorator that marks a method as participating in the Ralph Loop.

    When the orchestrator is in Ralph mode, failed operations will be
    retried up to max_iterations before giving up.

    Usage:
        @with_ralph_retry(max_iterations=10)
        def trigger_ai(self, prompt):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            self_obj = args[0]
            ctx: RecoveryContext = getattr(self_obj, "recovery_ctx", None)
            if ctx is None:
                return func(*args, **kwargs)

            if not ctx.ralph_active:
                # Ralph mode not active — just call directly
                return func(*args, **kwargs)

            last_error = None
            for iteration in range(ctx.ralph_iterations, max_iterations):
                ctx.ralph_iterations = iteration + 1
                logger.info(f"🔄 Ralph Loop iteration {ctx.ralph_iterations}/{max_iterations} for {func.__name__}")

                try:
                    result = func(*args, **kwargs)

                    # Check if the result indicates success
                    if result is True or (isinstance(result, dict) and result.get("success")):
                        logger.info(f"✅ Ralph Loop: {func.__name__} succeeded on iteration {ctx.ralph_iterations}")
                        ctx.ralph_iterations = 0  # Reset counter
                        return result

                    # Result indicates failure — retry
                    logger.warning(f"🔄 Ralph Loop: {func.__name__} returned failure, retrying...")

                except Exception as e:
                    last_error = e
                    category = _categorize_error(e)
                    logger.error(f"❌ Ralph Loop: {func.__name__} error: {e}")

                    if category in (ErrorCategory.AUTHENTICATION, ErrorCategory.SYSTEM):
                        raise  # Don't retry these

                # Backoff before next iteration
                delay = min(2.0 * (2 ** iteration), 30.0)
                time.sleep(delay)

            # All Ralph iterations exhausted
            logger.error(f"💔 Ralph Loop: {func.__name__} exhausted all {max_iterations} iterations")
            ctx.log_error("ralph_loop_exhausted", {
                "function": func.__name__,
                "max_iterations": max_iterations,
                "last_error": str(last_error) if last_error else "returned failure",
            })
            return False

        return wrapper
    return decorator
