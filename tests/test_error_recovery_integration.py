"""
Tests for Error Recovery Integration.

Covers: CircuitBreaker, RecoveryContext, decorators, quarantine,
and orchestrator wiring.
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from error_recovery_integration import (
    CircuitBreaker,
    RecoveryContext,
    with_circuit_breaker,
    with_ralph_retry,
    _categorize_error,
    ErrorCategory,
    ErrorSeverity,
)


class TestCircuitBreaker:
    """Tests for circuit breaker pattern."""

    def test_starts_closed(self):
        cb = CircuitBreaker("test", failure_threshold=3)
        assert cb.state == "closed"
        assert cb.can_execute() is True

    def test_opens_after_threshold(self):
        cb = CircuitBreaker("test", failure_threshold=3)

        for _ in range(3):
            cb.record_failure()

        assert cb.state == "open"
        assert cb.can_execute() is False

    def test_resets_on_success(self):
        cb = CircuitBreaker("test", failure_threshold=3)
        cb.record_failure()
        cb.record_failure()

        cb.record_success()
        assert cb.failure_count == 0
        assert cb.state == "closed"

    def test_half_open_after_recovery_timeout(self):
        cb = CircuitBreaker("test", failure_threshold=2, recovery_timeout=0)

        cb.record_failure()
        cb.record_failure()
        assert cb.state == "open"

        # recovery_timeout=0 means immediately half-open
        assert cb.can_execute() is True
        assert cb.state == "half-open"

    def test_tracks_total_calls(self):
        cb = CircuitBreaker("test")
        for _ in range(5):
            cb.record_success()
        for _ in range(3):
            cb.record_failure()

        assert cb.total_successes == 5
        assert cb.total_failures == 3

    def test_status_report(self):
        cb = CircuitBreaker("test")
        cb.record_success()
        cb.record_failure()

        status = cb.get_status()
        assert status["name"] == "test"
        assert status["total_successes"] == 1
        assert status["total_failures"] == 1
        assert status["state"] == "closed"


class TestErrorCategorization:
    """Tests for error categorization."""

    def test_auth_error(self):
        assert _categorize_error(Exception("401 Unauthorized")) == ErrorCategory.AUTHENTICATION
        assert _categorize_error(Exception("token expired")) == ErrorCategory.AUTHENTICATION

    def test_transient_error(self):
        assert _categorize_error(Exception("connection timeout")) == ErrorCategory.TRANSIENT
        assert _categorize_error(Exception("rate limit exceeded")) == ErrorCategory.TRANSIENT

    def test_data_error(self):
        assert _categorize_error(Exception("invalid JSON format")) == ErrorCategory.DATA
        assert _categorize_error(Exception("missing field")) == ErrorCategory.DATA

    def test_system_error(self):
        assert _categorize_error(Exception("disk full")) == ErrorCategory.SYSTEM
        assert _categorize_error(Exception("fatal crash")) == ErrorCategory.SYSTEM

    def test_default_logic_error(self):
        assert _categorize_error(Exception("unexpected result")) == ErrorCategory.LOGIC


class TestRecoveryContext:
    """Tests for RecoveryContext."""

    def test_initializes_all_breakers(self, temp_vault):
        ctx = RecoveryContext(temp_vault)
        expected = {"qwen_api", "gemini_api", "anthropic_api", "openrouter_api",
                    "gmail", "odoo", "linkedin", "twitter", "facebook", "filesystem"}
        assert set(ctx.breakers.keys()) == expected

    def test_get_breaker(self, temp_vault):
        ctx = RecoveryContext(temp_vault)
        breaker = ctx.get_breaker("odoo")
        assert breaker.name == "odoo"

    def test_get_unknown_breaker(self, temp_vault):
        ctx = RecoveryContext(temp_vault)
        breaker = ctx.get_breaker("unknown_service")
        assert breaker.name == "unknown_service"

    def test_circuit_breakers_healthy(self, temp_vault):
        ctx = RecoveryContext(temp_vault)
        assert ctx.all_circuit_breakers_healthy() is True

    def test_unhealthy_when_qwen_open(self, temp_vault):
        ctx = RecoveryContext(temp_vault)
        ctx.breakers["qwen_api"].state = "open"
        assert ctx.all_circuit_breakers_healthy() is False

    def test_unhealthy_when_gmail_open(self, temp_vault):
        ctx = RecoveryContext(temp_vault)
        ctx.breakers["gmail"].state = "open"
        assert ctx.all_circuit_breakers_healthy() is False

    def test_status_report_structure(self, temp_vault):
        ctx = RecoveryContext(temp_vault)
        report = ctx.get_status_report()

        assert "timestamp" in report
        assert "ralph_mode" in report
        assert "circuit_breakers" in report
        assert "quarantined_items" in report
        assert report["ralph_mode"]["active"] is False

    def test_ralph_mode_tracking(self, temp_vault):
        ctx = RecoveryContext(temp_vault)
        ctx.ralph_active = True
        ctx.ralph_iterations = 3

        report = ctx.get_status_report()
        assert report["ralph_mode"]["active"] is True
        assert report["ralph_mode"]["iterations"] == 3


class TestQuarantine:
    """Tests for item quarantine."""

    def test_quarantine_creates_file(self, temp_vault):
        ctx = RecoveryContext(temp_vault)
        item = temp_vault / "Needs_Action" / "test_item.md"
        item.parent.mkdir(parents=True, exist_ok=True)
        item.write_text("# Test Item")

        ctx.quarantine_item(item, "Too many failures")

        assert item.exists() is False
        quarantine_files = list(ctx.quarantine_dir.glob("*.md"))
        assert len(quarantine_files) == 1
        assert "quarantined" in quarantine_files[0].name

    def test_quarantine_adds_metadata(self, temp_vault):
        ctx = RecoveryContext(temp_vault)
        item = temp_vault / "Needs_Action" / "test_item.md"
        item.parent.mkdir(parents=True, exist_ok=True)
        item.write_text("# Content")

        ctx.quarantine_item(item, "Repeated timeout")

        quarantine_files = list(ctx.quarantine_dir.glob("*.md"))
        content = quarantine_files[0].read_text()
        assert "quarantined" in content
        assert "Repeated timeout" in content

    def test_quarantine_nonexistent_item(self, temp_vault):
        """Should handle gracefully if item doesn't exist."""
        ctx = RecoveryContext(temp_vault)
        item = temp_vault / "Needs_Action" / "nonexistent.md"

        # Should not raise
        ctx.quarantine_item(item, "Does not exist")

        quarantine_files = list(ctx.quarantine_dir.glob("*.md"))
        assert len(quarantine_files) == 1


class TestCircuitBreakerDecorator:
    """Tests for the with_circuit_breaker decorator."""

    def test_decorator_passes_on_success(self, temp_vault):
        ctx = RecoveryContext(temp_vault)

        class FakeOrchestrator:
            recovery_ctx = ctx

            @with_circuit_breaker("test_service", max_retries=1)
            def working_method(self):
                return "success"

        obj = FakeOrchestrator()
        result = obj.working_method()
        assert result == "success"

    def test_decorator_retries_on_failure(self, temp_vault):
        ctx = RecoveryContext(temp_vault)
        call_count = 0

        class FakeOrchestrator:
            recovery_ctx = ctx

            @with_circuit_breaker("test_service", max_retries=3, base_delay=0.01)
            def flaky_method(self):
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    raise Exception("timeout")  # Transient
                return "recovered"

        obj = FakeOrchestrator()
        result = obj.flaky_method()
        assert result == "recovered"
        assert call_count == 3

    def test_decorator_no_retry_for_auth_errors(self, temp_vault):
        ctx = RecoveryContext(temp_vault)
        call_count = 0

        class FakeOrchestrator:
            recovery_ctx = ctx

            @with_circuit_breaker("test_service", max_retries=3, base_delay=0.01)
            def auth_method(self):
                nonlocal call_count
                call_count += 1
                raise Exception("401 token expired")

        obj = FakeOrchestrator()
        with pytest.raises(Exception, match="401"):
            obj.auth_method()

        assert call_count == 1  # No retry

    def test_decorator_respects_circuit_open(self, temp_vault):
        ctx = RecoveryContext(temp_vault)
        ctx.breakers["guarded_service"] = CircuitBreaker("guarded_service", failure_threshold=1)
        ctx.breakers["guarded_service"].record_failure()  # Opens circuit
        call_count = 0

        class FakeOrchestrator:
            recovery_ctx = ctx

            @with_circuit_breaker("guarded_service", max_retries=3)
            def guarded_method(self):
                nonlocal call_count
                call_count += 1
                return "called"

        obj = FakeOrchestrator()
        result = obj.guarded_method()  # Circuit is open

        assert result is None  # Blocked by circuit
        assert call_count == 0

    def test_decorator_falls_through_without_ctx(self):
        """Should work normally when no recovery_ctx is present."""
        class FakeOrchestrator:
            recovery_ctx = None

            @with_circuit_breaker("test", max_retries=1)
            def simple_method(self):
                return "ok"

        obj = FakeOrchestrator()
        result = obj.simple_method()
        assert result == "ok"


class TestRalphRetryDecorator:
    """Tests for the with_ralph_retry decorator."""

    def test_ralph_retry_retries_when_active(self, temp_vault):
        ctx = RecoveryContext(temp_vault)
        ctx.ralph_active = True
        call_count = 0

        class FakeOrchestrator:
            recovery_ctx = ctx

            @with_ralph_retry(max_iterations=3)
            def ralph_method(self):
                nonlocal call_count
                call_count += 1
                return True  # Success on first try

        obj = FakeOrchestrator()
        result = obj.ralph_method()
        assert result is True
        assert call_count == 1

    def test_ralph_retry_skipped_when_inactive(self, temp_vault):
        """Should not retry when ralph_active is False."""
        ctx = RecoveryContext(temp_vault)
        ctx.ralph_active = False
        call_count = 0

        class FakeOrchestrator:
            recovery_ctx = ctx

            @with_ralph_retry(max_iterations=5)
            def direct_method(self):
                nonlocal call_count
                call_count += 1
                return False

        obj = FakeOrchestrator()
        result = obj.direct_method()
        assert result is False
        assert call_count == 1  # No retry

    def test_ralph_retry_without_ctx(self):
        """Should work when no recovery_ctx."""
        class FakeOrchestrator:
            recovery_ctx = None

            @with_ralph_retry(max_iterations=3)
            def simple_method(self):
                return "ok"

        obj = FakeOrchestrator()
        result = obj.simple_method()
        assert result == "ok"
