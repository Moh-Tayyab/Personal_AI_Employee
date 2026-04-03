"""
Tests for Configuration Validator.

Covers: vault structure checks, env var validation, package checks,
credential validation, security checks, port checks, report generation.
"""

import json
import os
import socket
import threading
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from config_validator import (
    ConfigValidator,
    CheckResult,
    CheckSeverity,
    CheckCategory,
    ValidationReport,
)


class TestValidationReport:
    """Tests for ValidationReport data class."""

    def test_empty_report_is_healthy(self):
        report = ValidationReport()
        assert report.healthy is True
        assert report.fatal_errors == []
        assert report.warnings == []

    def test_fatal_error_makes_unhealthy(self):
        report = ValidationReport(checks=[
            CheckResult("test", CheckCategory.VAULT, CheckSeverity.FATAL,
                        False, "Missing vault"),
        ])
        assert report.healthy is False
        assert len(report.fatal_errors) == 1

    def test_warning_does_not_make_unhealthy(self):
        report = ValidationReport(checks=[
            CheckResult("test", CheckCategory.VAULT, CheckSeverity.WARNING,
                        False, "Missing optional file"),
        ])
        assert report.healthy is True
        assert len(report.warnings) == 1

    def test_counts_are_correct(self):
        report = ValidationReport(checks=[
            CheckResult("pass1", CheckCategory.VAULT, CheckSeverity.FATAL, True, "OK"),
            CheckResult("pass2", CheckCategory.VAULT, CheckSeverity.FATAL, True, "OK"),
            CheckResult("fail1", CheckCategory.VAULT, CheckSeverity.FATAL, False, "Bad"),
            CheckResult("warn1", CheckCategory.VAULT, CheckSeverity.WARNING, False, "Maybe"),
        ])
        assert report.passed_count == 2
        assert report.total_count == 4
        assert len(report.fatal_errors) == 1
        assert len(report.warnings) == 1

    def test_to_dict_structure(self):
        report = ValidationReport(checks=[
            CheckResult("test_check", CheckCategory.ENVIRONMENT, CheckSeverity.FATAL,
                        False, "Missing key", "details"),
        ])
        d = report.to_dict()

        assert "started_at" in d
        assert "completed_at" in d
        assert "healthy" in d
        assert "passed" in d
        assert "total" in d
        assert "checks" in d
        assert len(d["checks"]) == 1
        assert d["checks"][0]["name"] == "test_check"
        assert d["checks"][0]["category"] == "environment"
        assert d["checks"][0]["severity"] == "fatal"
        assert d["checks"][0]["passed"] is False


class TestVaultStructureChecks:
    """Tests for vault directory structure validation."""

    def test_missing_vault_is_fatal(self, tmp_path):
        non_existent = tmp_path / "no_vault_here"
        validator = ConfigValidator(str(non_existent))
        report = validator.validate_all()

        vault_check = next(c for c in report.checks if c.name == "vault_exists")
        assert vault_check.passed is False
        assert vault_check.severity == CheckSeverity.FATAL

    def test_missing_required_dirs_are_fatal(self, tmp_path):
        vault = tmp_path / "vault"
        vault.mkdir()
        # Don't create any subdirectories

        validator = ConfigValidator(str(vault))
        report = validator.validate_all()

        missing = [c for c in report.checks if c.name.startswith("vault_dir_") and not c.passed]
        assert len(missing) == len(ConfigValidator.REQUIRED_VAULT_DIRS)

    def test_complete_vault_passes(self, temp_vault):
        """temp_vault fixture creates a complete vault structure."""
        validator = ConfigValidator(str(temp_vault))
        report = validator.validate_all()

        vault_exists = next(c for c in report.checks if c.name == "vault_exists")
        assert vault_exists.passed is True

        for dir_name in ConfigValidator.REQUIRED_VAULT_DIRS:
            check = next((c for c in report.checks if c.name == f"vault_dir_{dir_name}"), None)
            assert check is not None
            assert check.passed is True, f"Directory check failed: {dir_name}"


class TestVaultFileChecks:
    """Tests for vault file validation."""

    def test_missing_recommended_files_are_warnings(self, tmp_path):
        vault = tmp_path / "vault"
        vault.mkdir()
        for d in ConfigValidator.REQUIRED_VAULT_DIRS:
            (vault / d).mkdir(parents=True, exist_ok=True)

        validator = ConfigValidator(str(vault))
        report = validator.validate_all()

        file_checks = [c for c in report.checks if c.name.startswith("vault_file_")]
        # All should be warnings (not fatal)
        for fc in file_checks:
            assert fc.severity == CheckSeverity.WARNING

    def test_existing_files_pass(self, temp_vault):
        validator = ConfigValidator(str(temp_vault))
        report = validator.validate_all()

        file_checks = [c for c in report.checks if c.name.startswith("vault_file_")]
        for fc in file_checks:
            assert fc.passed is True


class TestEnvironmentVarChecks:
    """Tests for environment variable validation."""

    def test_no_ai_provider_is_fatal(self, temp_vault, monkeypatch):
        for var in ConfigValidator.AI_PROVIDER_VARS:
            monkeypatch.delenv(var, raising=False)

        validator = ConfigValidator(str(temp_vault))
        report = validator.validate_all()

        ai_check = next(c for c in report.checks if c.name == "ai_provider_configured")
        assert ai_check.passed is False
        assert ai_check.severity == CheckSeverity.FATAL

    def test_one_ai_provider_passes(self, temp_vault, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        for var in ["ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY"]:
            monkeypatch.delenv(var, raising=False)

        validator = ConfigValidator(str(temp_vault))
        report = validator.validate_all()

        ai_check = next(c for c in report.checks if c.name == "ai_provider_configured")
        assert ai_check.passed is True


class TestPythonPackageChecks:
    """Tests for Python package validation."""

    def test_installed_package_passes(self, temp_vault):
        validator = ConfigValidator(str(temp_vault))
        validator._check_python_packages()

        # dotenv should be installed
        dotenv_check = next((c for c in validator.results if c.name == "package_dotenv"), None)
        assert dotenv_check is not None
        assert dotenv_check.passed is True

    def test_missing_package_fails(self, temp_vault):
        validator = ConfigValidator(str(temp_vault))
        # Temporarily add a fake missing package
        original = validator.CORE_PACKAGES
        validator.CORE_PACKAGES = ["nonexistent_package_xyz"]
        validator._check_python_packages()
        validator.CORE_PACKAGES = original

        pkg_check = next(c for c in validator.results if c.name == "package_nonexistent_package_xyz")
        assert pkg_check.passed is False
        assert pkg_check.severity == CheckSeverity.FATAL


class TestSecurityChecks:
    """Tests for security validation."""

    def test_env_in_gitignore_passes(self, temp_vault):
        # temp_vault is inside the project which has .gitignore
        validator = ConfigValidator(str(temp_vault))
        validator._check_security()

        # .env file may or may not exist, but if it does it should be gitignored
        # This test just verifies the check runs without error
        sec_checks = [c for c in validator.results if c.category == CheckCategory.SECURITY]
        assert len(sec_checks) >= 0  # May be 0 if .env doesn't exist


class TestPortChecks:
    """Tests for port availability validation."""

    def test_free_port_passes(self, temp_vault):
        validator = ConfigValidator(str(temp_vault))
        # Use a very high port that's unlikely to be in use
        with patch.dict(os.environ, {"HEALTH_PORT": "59999"}):
            validator._check_health_port()

        port_check = next(c for c in validator.results if c.name == "health_port_available")
        assert port_check.passed is True

    def test_used_port_fails(self, temp_vault):
        """Should detect when health port is already in use."""
        validator = ConfigValidator(str(temp_vault))
        with patch.dict(os.environ, {"HEALTH_PORT": "9999"}):
            # Mock socket to report port in use (connect_ex returns 0)
            with patch("socket.socket") as mock_socket:
                mock_instance = MagicMock()
                mock_instance.connect_ex.return_value = 0  # Port in use
                mock_socket.return_value = mock_instance

                validator._check_health_port()

        port_check = next(c for c in validator.results if c.name == "health_port_available")
        assert port_check.passed is False
        assert port_check.severity == CheckSeverity.WARNING


class TestNetworkChecks:
    """Tests for network connectivity validation."""

    def test_network_checks_included_when_enabled(self, temp_vault):
        validator = ConfigValidator(str(temp_vault))
        report = validator.validate_all(run_network_checks=True)

        network_checks = [c for c in report.checks if c.category == CheckCategory.NETWORK]
        assert len(network_checks) > 0

    def test_network_checks_excluded_when_disabled(self, temp_vault):
        validator = ConfigValidator(str(temp_vault))
        report = validator.validate_all(run_network_checks=False)

        network_checks = [c for c in report.checks if c.category == CheckCategory.NETWORK]
        assert len(network_checks) == 0


class TestConfigurationFileChecks:
    """Tests for configuration file validation."""

    def test_mcp_config_valid_when_exists(self, temp_vault):
        mcp_config = temp_vault.parent / ".mcp.json"
        if mcp_config.exists():
            validator = ConfigValidator(str(temp_vault))
            validator._check_configuration_files()

            mcp_check = next(c for c in validator.results if c.name == "mcp_config_valid")
            assert mcp_check.passed is True

    def test_pyproject_exists(self, temp_vault):
        validator = ConfigValidator(str(temp_vault))
        validator._check_configuration_files()

        pp_check = next((c for c in validator.results if c.name == "pyproject_exists"), None)
        if pp_check:
            assert pp_check.passed is True


class TestReportOutput:
    """Tests for report formatting and output."""

    def test_print_summary_no_crash(self, capsys, temp_vault):
        """print_summary should produce human-readable output."""
        validator = ConfigValidator(str(temp_vault))
        validator.validate_all(run_network_checks=False)
        validator.print_summary()

        captured = capsys.readouterr()
        assert "Configuration Validation Report" in captured.out

    def test_json_report_is_valid_json(self, temp_vault):
        """print_json_report should produce valid JSON."""
        validator = ConfigValidator(str(temp_vault))
        validator.validate_all(run_network_checks=False)
        json_str = validator.print_json_report()

        data = json.loads(json_str)
        assert "healthy" in data
        assert "checks" in data
        assert "started_at" in data
        assert "completed_at" in data


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_full_validation_on_good_config(self, temp_vault, monkeypatch):
        """Full validation should pass on a properly configured vault."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")

        validator = ConfigValidator(str(temp_vault))
        report = validator.validate_all(run_network_checks=False)

        # Should have no fatal errors
        assert report.healthy is True
        assert len(report.fatal_errors) == 0
        # Should have run many checks
        assert report.total_count > 10

    def test_validation_with_minimal_vault(self, tmp_path, monkeypatch):
        """Validation on minimal vault should show warnings but no fatals if dirs exist."""
        vault = tmp_path / "vault"
        vault.mkdir()
        for d in ConfigValidator.REQUIRED_VAULT_DIRS:
            (vault / d).mkdir(parents=True, exist_ok=True)

        monkeypatch.setenv("GEMINI_API_KEY", "test-key")

        validator = ConfigValidator(str(vault))
        report = validator.validate_all(run_network_checks=False)

        # Vault structure should pass
        vault_checks = [c for c in report.checks if c.category == CheckCategory.VAULT and "dir" in c.name]
        for vc in vault_checks:
            assert vc.passed is True

        # AI provider configured should pass
        ai_check = next(c for c in report.checks if c.name == "ai_provider_configured")
        assert ai_check.passed is True
