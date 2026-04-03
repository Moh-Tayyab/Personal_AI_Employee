"""
Tests for QuotaManager.

Covers: initialization, usage recording, quota exhaustion detection,
status reporting, manual reset, and daily counter reset.
"""

import json
import time
from datetime import datetime
from pathlib import Path

import pytest

from quota_manager import QuotaManager


class TestQuotaManagerInit:
    """Tests for QuotaManager initialization."""

    def test_creates_quota_file(self, temp_vault):
        """QuotaManager should create quota_status.json on init."""
        qm = QuotaManager(str(temp_vault))
        assert qm.quota_file.exists()
        assert qm.quota_file.name == "quota_status.json"

    def test_initializes_all_services(self, temp_vault):
        """All default services should be initialized."""
        qm = QuotaManager(str(temp_vault))
        expected_services = {"qwen", "claude", "codex", "gemini", "openrouter"}
        actual_services = set(qm.quota_data["services"].keys())
        assert expected_services == actual_services

    def test_sets_default_limits(self, temp_vault):
        """Default limits should match environment or class defaults."""
        qm = QuotaManager(str(temp_vault))
        gemini = qm.quota_data["services"]["gemini"]
        assert gemini["daily_limit"] == 1500
        assert gemini["cost_limit_usd"] == 0.0
        assert gemini["exhausted"] is False

    def test_loads_existing_quota_file(self, temp_vault):
        """Should load and merge existing quota data."""
        today = datetime.now().strftime("%Y-%m-%d")
        quota_file = temp_vault / "secrets" / "quota_status.json"
        existing = {
            "last_reset": today,
            "services": {
                "qwen": {
                    "current_usage": 42,
                    "exhausted": False,
                    "daily_limit": 100,
                    "cost_limit_usd": 10,
                    "current_cost_usd": 0,
                    "total_requests_today": 0,
                    "total_requests_all_time": 0,
                    "last_request": None,
                },
            },
        }
        quota_file.parent.mkdir(parents=True, exist_ok=True)
        quota_file.write_text(json.dumps(existing))

        qm = QuotaManager(str(temp_vault))
        assert qm.quota_data["services"]["qwen"]["current_usage"] == 42

    def test_sets_last_reset_date(self, temp_vault):
        """last_reset should be set to today's date."""
        qm = QuotaManager(str(temp_vault))
        today = datetime.now().strftime("%Y-%m-%d")
        assert qm.quota_data["last_reset"] == today


class TestQuotaManagerRecordUsage:
    """Tests for usage recording."""

    def test_records_single_usage(self, temp_vault):
        """Should increment counters on record_usage."""
        qm = QuotaManager(str(temp_vault))
        result = qm.record_usage("qwen", tokens_used=100, estimated_cost_usd=0.01)

        assert result["status"] == "ok"
        assert result["service"] == "qwen"
        assert result["requests_today"] == 1
        assert result["remaining_requests"] == 99

    def test_accumulates_cost(self, temp_vault):
        """Costs should accumulate across multiple calls."""
        qm = QuotaManager(str(temp_vault))
        qm.record_usage("claude", estimated_cost_usd=0.05)
        result = qm.record_usage("claude", estimated_cost_usd=0.03)

        assert result["cost_usd_today"] == pytest.approx(0.08, abs=0.0001)

    def test_detects_request_limit_exceeded(self, temp_vault):
        """Should flag exhausted when daily_limit is reached."""
        qm = QuotaManager(str(temp_vault))
        # Set low limit for testing
        qm.quota_data["services"]["gemini"]["daily_limit"] = 3

        qm.record_usage("gemini")
        qm.record_usage("gemini")
        result = qm.record_usage("gemini")

        assert result["status"] == "exhausted"
        assert result["exhausted"] is True
        assert len(result["warnings"]) > 0

    def test_detects_cost_limit_exceeded(self, temp_vault):
        """Should flag exhausted when cost limit is reached."""
        qm = QuotaManager(str(temp_vault))
        qm.quota_data["services"]["codex"]["cost_limit_usd"] = 0.10

        qm.record_usage("codex", estimated_cost_usd=0.06)
        result = qm.record_usage("codex", estimated_cost_usd=0.05)

        assert result["status"] == "exhausted"
        assert result["exhausted"] is True
        assert "cost limit exceeded" in " ".join(result["warnings"]).lower()

    def test_warns_at_80_percent(self, temp_vault):
        """Should warn when approaching 80% of limit."""
        qm = QuotaManager(str(temp_vault))
        qm.quota_data["services"]["qwen"]["daily_limit"] = 10

        for _ in range(8):
            qm.record_usage("qwen")

        result = qm.record_usage("qwen")
        assert result["status"] == "ok"  # Not yet exhausted
        assert any("approaching" in w.lower() or "80" in w for w in result["warnings"])

    def test_unknown_service_returns_warning(self, temp_vault):
        """Unknown services should return a warning."""
        qm = QuotaManager(str(temp_vault))
        result = qm.record_usage("unknown_service")

        assert result["status"] == "unknown_service"
        assert "warning" in result

    def test_persists_to_disk(self, temp_vault):
        """Quota data should be saved to disk after each record."""
        qm = QuotaManager(str(temp_vault))
        qm.record_usage("qwen")

        with open(qm.quota_file) as f:
            saved = json.load(f)

        assert saved["services"]["qwen"]["current_usage"] == 1


class TestQuotaManagerQueries:
    """Tests for quota status queries."""

    def test_is_exhausted_false_initially(self, temp_vault):
        """Services should not be exhausted on initialization."""
        qm = QuotaManager(str(temp_vault))
        assert qm.is_exhausted("qwen") is False
        assert qm.is_exhausted("gemini") is False

    def test_is_exhausted_true_after_limit(self, temp_vault):
        """Should return True after limit is reached."""
        qm = QuotaManager(str(temp_vault))
        qm.quota_data["services"]["claude"]["daily_limit"] = 1
        qm.record_usage("claude")

        assert qm.is_exhausted("claude") is True

    def test_is_exhausted_unknown_service(self, temp_vault):
        """Unknown service should return False (not block)."""
        qm = QuotaManager(str(temp_vault))
        assert qm.is_exhausted("nonexistent") is False

    def test_get_available_services_all(self, temp_vault):
        """All services should be available initially."""
        qm = QuotaManager(str(temp_vault))
        available = qm.get_available_services()
        assert len(available) == 5
        assert "qwen" in available
        assert "gemini" in available

    def test_get_available_services_exhausted_excluded(self, temp_vault):
        """Exhausted services should be excluded from available list."""
        qm = QuotaManager(str(temp_vault))
        qm.quota_data["services"]["qwen"]["exhausted"] = True
        qm.quota_data["services"]["claude"]["exhausted"] = True

        available = qm.get_available_services()
        assert "qwen" not in available
        assert "claude" not in available
        assert "gemini" in available

    def test_get_status_report_structure(self, temp_vault):
        """Status report should have expected structure."""
        qm = QuotaManager(str(temp_vault))
        qm.record_usage("gemini", estimated_cost_usd=0.02)

        report = qm.get_status_report()
        assert "timestamp" in report
        assert "services" in report
        assert "gemini" in report["services"]

        gemini = report["services"]["gemini"]
        assert gemini["requests"]["used"] == 1
        assert gemini["requests"]["remaining"] == 1499
        assert gemini["cost"]["used_usd"] == pytest.approx(0.02, abs=0.0001)

    def test_status_report_includes_percentages(self, temp_vault):
        """Status report should include usage percentages."""
        qm = QuotaManager(str(temp_vault))
        qm.quota_data["services"]["qwen"]["daily_limit"] = 10

        for _ in range(5):
            qm.record_usage("qwen")

        report = qm.get_status_report()
        assert report["services"]["qwen"]["requests"]["percentage"] == 50.0


class TestQuotaManagerReset:
    """Tests for quota reset functionality."""

    def test_reset_single_service(self, temp_vault):
        """Should reset a single service's quota."""
        qm = QuotaManager(str(temp_vault))
        qm.record_usage("qwen")
        qm.quota_data["services"]["qwen"]["exhausted"] = True

        result = qm.reset_quota("qwen")
        assert result is True
        assert qm.quota_data["services"]["qwen"]["exhausted"] is False
        assert qm.quota_data["services"]["qwen"]["current_usage"] == 0

    def test_reset_unknown_service(self, temp_vault):
        """Should return False for unknown service."""
        qm = QuotaManager(str(temp_vault))
        result = qm.reset_quota("nonexistent")
        assert result is False

    def test_reset_all_quotas(self, temp_vault):
        """Should reset all quotas to defaults."""
        qm = QuotaManager(str(temp_vault))
        qm.record_usage("qwen")
        qm.record_usage("claude")
        qm.record_usage("gemini")

        qm.reset_all_quotas()
        assert qm.quota_data["services"]["qwen"]["current_usage"] == 0
        assert qm.quota_data["services"]["claude"]["current_usage"] == 0
        assert qm.quota_data["services"]["gemini"]["current_usage"] == 0
