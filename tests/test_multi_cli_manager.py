"""
Tests for MultiCLIManager.

Covers: CLI detection, selection logic, priority routing by task type,
status reporting, and fallback behavior.
"""

import subprocess
from unittest.mock import patch, MagicMock

import pytest

from multi_cli_manager import MultiCLIManager


class TestMultiCLIManagerInit:
    """Tests for MultiCLIManager initialization."""

    @patch("multi_cli_manager.MultiCLIManager._command_exists")
    def test_detects_available_clis(self, mock_cmd_exists, temp_vault, mock_env_vars):
        """Should detect CLIs that have both command and credentials."""
        mock_cmd_exists.return_value = True
        manager = MultiCLIManager(str(temp_vault))

        # At minimum qwen and claude should be available (env vars set in fixture)
        assert "qwen" in manager.available_clis or "claude" in manager.available_clis

    @patch("multi_cli_manager.MultiCLIManager._command_exists")
    def test_skips_cli_without_credentials(self, mock_cmd_exists, temp_vault, monkeypatch):
        """Should not detect CLI without env credentials."""
        mock_cmd_exists.return_value = True
        monkeypatch.delenv("QWEN_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        manager = MultiCLIManager(str(temp_vault))
        # qwen requires QWEN_API_KEY or OPENAI_API_KEY, both removed
        assert "qwen" not in manager.available_clis

    @patch("multi_cli_manager.MultiCLIManager._command_exists")
    def test_handles_no_clis_available(self, mock_cmd_exists, temp_vault, monkeypatch):
        """Should handle case where no CLIs are available."""
        mock_cmd_exists.return_value = False
        monkeypatch.delenv("QWEN_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        manager = MultiCLIManager(str(temp_vault))
        assert len(manager.available_clis) == 0


class TestCLISelection:
    """Tests for CLI selection logic."""

    @patch("multi_cli_manager.MultiCLIManager._command_exists")
    def test_selects_first_available_by_default(self, mock_cmd_exists, temp_vault, mock_env_vars):
        """Should select first available CLI in priority order."""
        mock_cmd_exists.return_value = True
        manager = MultiCLIManager(str(temp_vault))

        selected = manager.select_cli("general")
        assert selected in manager.available_clis

    @patch("multi_cli_manager.MultiCLIManager._command_exists")
    def test_prefers_codex_for_code_tasks(self, mock_cmd_exists, temp_vault, mock_env_vars):
        """Should prefer codex for code tasks when available."""
        mock_cmd_exists.return_value = True
        manager = MultiCLIManager(str(temp_vault))

        if "codex" in manager.available_clis:
            selected = manager.select_cli("code")
            assert selected == "codex"

    @patch("multi_cli_manager.MultiCLIManager._command_exists")
    def test_prefers_qwen_for_reasoning(self, mock_cmd_exists, temp_vault, mock_env_vars):
        """Should prefer qwen for reasoning tasks."""
        mock_cmd_exists.return_value = True
        manager = MultiCLIManager(str(temp_vault))

        if "qwen" in manager.available_clis:
            selected = manager.select_cli("reasoning")
            assert selected == "qwen"

    def test_returns_none_when_no_clis(self, temp_vault):
        """Should return None when no CLIs are available."""
        manager = MultiCLIManager.__new__(MultiCLIManager)
        manager.vault_path = temp_vault
        manager.available_clis = {}

        assert manager.select_cli("general") is None


class TestPriorityOrder:
    """Tests for task-type-based priority ordering."""

    @patch("multi_cli_manager.MultiCLIManager._command_exists")
    def test_code_priority_order(self, mock_cmd_exists, temp_vault, mock_env_vars):
        """Code tasks should prioritize codex > qwen > claude."""
        mock_cmd_exists.return_value = True
        manager = MultiCLIManager(str(temp_vault))

        order = manager._get_priority_order("code")
        assert order[0] == "codex"

    @patch("multi_cli_manager.MultiCLIManager._command_exists")
    def test_reasoning_priority_order(self, mock_cmd_exists, temp_vault, mock_env_vars):
        """Reasoning tasks should prioritize qwen > claude > codex."""
        mock_cmd_exists.return_value = True
        manager = MultiCLIManager(str(temp_vault))

        order = manager._get_priority_order("reasoning")
        assert order[0] == "qwen"

    @patch("multi_cli_manager.MultiCLIManager._command_exists")
    def test_general_priority_order(self, mock_cmd_exists, temp_vault, mock_env_vars):
        """General tasks should use default priority."""
        mock_cmd_exists.return_value = True
        manager = MultiCLIManager(str(temp_vault))

        order = manager._get_priority_order("general")
        assert order[0] == "qwen"


class TestCLIStatus:
    """Tests for status reporting."""

    @patch("multi_cli_manager.MultiCLIManager._command_exists")
    def test_status_structure(self, mock_cmd_exists, temp_vault, mock_env_vars):
        """Status should include available list and per-instance details."""
        mock_cmd_exists.return_value = True
        manager = MultiCLIManager(str(temp_vault))

        status = manager.get_status()
        assert "available" in status
        assert "total_available" in status
        assert "instances" in status
        assert isinstance(status["available"], list)
        assert isinstance(status["total_available"], int)

    @patch("multi_cli_manager.MultiCLIManager._command_exists")
    def test_status_shows_zero_when_no_clis(self, mock_cmd_exists, temp_vault, monkeypatch):
        """Status should show zero when no CLIs available."""
        mock_cmd_exists.return_value = False
        monkeypatch.delenv("QWEN_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        manager = MultiCLIManager(str(temp_vault))
        status = manager.get_status()
        assert status["total_available"] == 0


class TestRunWithFallback:
    """Tests for the fallback execution."""

    @patch("multi_cli_manager.MultiCLIManager._command_exists")
    def test_fallback_returns_error_when_no_clis(self, mock_cmd_exists, temp_vault, monkeypatch):
        """Should return failure when no CLIs are available."""
        mock_cmd_exists.return_value = False
        monkeypatch.delenv("QWEN_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        manager = MultiCLIManager(str(temp_vault))
        result = manager.run_with_fallback("test prompt")

        assert result["success"] is False
        assert result["cli_used"] == "none"
        assert "failed" in result["error"].lower()
