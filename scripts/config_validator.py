"""
Startup Configuration Validator for Personal AI Employee

Runs comprehensive pre-flight checks before the orchestrator starts.
Validates environment, credentials, dependencies, vault structure,
network connectivity, and port availability.

Usage:
    # In orchestrator main():
    from config_validator import ConfigValidator

    validator = ConfigValidator(vault_path="./vault")
    report = validator.validate_all()

    if report.fatal_errors:
        print("❌ Fatal configuration errors:")
        for err in report.fatal_errors:
            print(f"  - {err}")
        return 1

    # Optionally run checks that don't block startup
    validator.print_summary()

Exit codes:
    0 - All checks passed (or only warnings)
    1 - Fatal errors found (system should not start)
    2 - Validation could not complete (e.g., vault not accessible)
"""

import os
import sys
import json
import socket
import shutil
import importlib
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("ConfigValidator")


class CheckSeverity(Enum):
    FATAL = "fatal"       # System cannot start
    WARNING = "warning"   # System can start but may not function fully
    INFO = "info"         # Informational only


class CheckCategory(Enum):
    ENVIRONMENT = "environment"
    CREDENTIALS = "credentials"
    DEPENDENCIES = "dependencies"
    VAULT = "vault"
    NETWORK = "network"
    PORTS = "ports"
    SECURITY = "security"
    CONFIGURATION = "configuration"


@dataclass
class CheckResult:
    """Result of a single validation check."""
    name: str
    category: CheckCategory
    severity: CheckSeverity
    passed: bool
    message: str
    details: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ValidationReport:
    """Complete validation report."""
    checks: List[CheckResult] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    @property
    def fatal_errors(self) -> List[CheckResult]:
        return [c for c in self.checks if not c.passed and c.severity == CheckSeverity.FATAL]

    @property
    def warnings(self) -> List[CheckResult]:
        return [c for c in self.checks if not c.passed and c.severity == CheckSeverity.WARNING]

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def total_count(self) -> int:
        return len(self.checks)

    @property
    def healthy(self) -> bool:
        return len(self.fatal_errors) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "healthy": self.healthy,
            "passed": self.passed_count,
            "total": self.total_count,
            "fatal_errors": len(self.fatal_errors),
            "warnings": len(self.warnings),
            "checks": [
                {
                    "name": c.name,
                    "category": c.category.value,
                    "severity": c.severity.value,
                    "passed": c.passed,
                    "message": c.message,
                    "details": c.details,
                }
                for c in self.checks
            ],
        }


class ConfigValidator:
    """
    Validates system configuration before startup.

    All checks are independent — one failure doesn't prevent others from running.
    """

    # Required vault directory structure
    REQUIRED_VAULT_DIRS = [
        "Needs_Action",
        "Plans",
        "Done",
        "Pending_Approval",
        "Approved",
        "Rejected",
        "Logs",
        "Briefings",
        "secrets",
    ]

    # Required vault files
    REQUIRED_VAULT_FILES = [
        "Dashboard.md",
        "Company_Handbook.md",
        "Business_Goals.md",
    ]

    # Optional but recommended files
    OPTIONAL_VAULT_FILES = [
        "secrets/gmail_credentials.json",
        "secrets/webhooks.json",
    ]

    # Critical environment variables (at least one AI provider must be configured)
    AI_PROVIDER_VARS = ["ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY"]

    # Watcher-specific env vars
    WATCHER_VARS = {
        "gmail_watcher": ["GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET"],  # or credentials file
        "whatsapp_watcher": [],  # Uses playwright, no env vars needed
        "filesystem_watcher": [],  # No env vars needed
    }

    # MCP server dependencies
    MCP_SERVERS = {
        "email": {"module": "googleapiclient.discovery", "description": "Gmail API"},
        "approval": {"module": None, "description": "Approval workflow"},
        "filesystem": {"module": None, "description": "File operations"},
        "linkedin": {"module": None, "description": "LinkedIn posting"},
        "twitter": {"module": None, "description": "Twitter/X posting"},
        "social": {"module": None, "description": "Facebook/Instagram posting"},
        "odoo": {"module": "xmlrpc.client", "description": "Odoo accounting"},
    }

    # Core Python packages
    CORE_PACKAGES = [
        "dotenv",
        "requests",
        "watchdog",
        "googleapiclient",
        "playwright",
    ]

    # Recommended ports (for health server)
    HEALTH_PORT = 8080

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.results: List[CheckResult] = []

    def _add_result(self, name: str, category: CheckCategory, severity: CheckSeverity,
                    passed: bool, message: str, details: Optional[str] = None):
        """Add a check result."""
        self.results.append(CheckResult(
            name=name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details=details,
        ))

    def validate_all(self, run_network_checks: bool = False) -> ValidationReport:
        """
        Run all validation checks.

        Args:
            run_network_checks: If True, also test network connectivity
                to external services (slower, may require internet).

        Returns:
            ValidationReport with all check results.
        """
        self.results = []

        self._check_vault_structure()
        self._check_vault_files()
        self._check_environment_vars()
        self._check_python_packages()
        self._check_credentials()
        self._check_mcp_servers()
        self._check_security()
        self._check_health_port()
        self._check_configuration_files()

        if run_network_checks:
            self._check_network_connectivity()

        report = ValidationReport(checks=self.results)
        report.completed_at = datetime.now().isoformat()
        return report

    # ─── Vault Structure Checks ───────────────────────────────────────

    def _check_vault_structure(self):
        """Validate vault directory structure exists."""
        if not self.vault_path.exists():
            self._add_result(
                "vault_exists", CheckCategory.VAULT, CheckSeverity.FATAL,
                False, f"Vault directory does not exist: {self.vault_path}",
                f"Create it with: mkdir -p {self.vault_path}",
            )
            return

        self._add_result(
            "vault_exists", CheckCategory.VAULT, CheckSeverity.FATAL,
            True, f"Vault directory exists: {self.vault_path}",
        )

        # Check required subdirectories
        missing_dirs = []
        for dir_name in self.REQUIRED_VAULT_DIRS:
            dir_path = self.vault_path / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
                self._add_result(
                    f"vault_dir_{dir_name}", CheckCategory.VAULT, CheckSeverity.FATAL,
                    False, f"Missing required directory: {dir_name}",
                )
            else:
                self._add_result(
                    f"vault_dir_{dir_name}", CheckCategory.VAULT, CheckSeverity.FATAL,
                    True, f"Directory exists: {dir_name}",
                )

        if missing_dirs:
            self._add_result(
                "vault_dirs_summary", CheckCategory.VAULT, CheckSeverity.FATAL,
                False, f"{len(missing_dirs)} missing directories",
                f"Create with: mkdir -p {' '.join(str(self.vault_path / d) for d in missing_dirs)}",
            )

    def _check_vault_files(self):
        """Validate required vault files exist."""
        for file_name in self.REQUIRED_VAULT_FILES:
            file_path = self.vault_path / file_name
            if not file_path.exists():
                self._add_result(
                    f"vault_file_{file_name}", CheckCategory.VAULT, CheckSeverity.WARNING,
                    False, f"Missing recommended file: {file_name}",
                )
            else:
                content = file_path.read_text().strip()
                is_empty = len(content) < 20
                self._add_result(
                    f"vault_file_{file_name}", CheckCategory.VAULT,
                    CheckSeverity.WARNING if is_empty else CheckSeverity.INFO,
                    True,
                    f"File exists: {file_name}" + (" (appears empty)" if is_empty else ""),
                )

        # Check optional files
        for file_name in self.OPTIONAL_VAULT_FILES:
            file_path = self.vault_path / file_name
            exists = file_path.exists()
            self._add_result(
                f"vault_optional_{file_name}", CheckCategory.VAULT, CheckSeverity.INFO,
                exists,
                f"Optional file {'found' if exists else 'not found'}: {file_name}",
            )

    # ─── Environment Variable Checks ──────────────────────────────────

    def _check_environment_vars(self):
        """Validate required environment variables."""
        # Check AI provider keys
        ai_keys_found = []
        for var in self.AI_PROVIDER_VARS:
            value = os.getenv(var)
            if value:
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                ai_keys_found.append(var)
                self._add_result(
                    f"env_{var}", CheckCategory.ENVIRONMENT, CheckSeverity.INFO,
                    True, f"Environment variable set: {var}={masked}",
                )
            else:
                self._add_result(
                    f"env_{var}", CheckCategory.ENVIRONMENT, CheckSeverity.WARNING,
                    False, f"Environment variable not set: {var}",
                )

        # At least one AI provider must be configured
        if ai_keys_found:
            self._add_result(
                "ai_provider_configured", CheckCategory.ENVIRONMENT, CheckSeverity.FATAL,
                True, f"AI provider(s) configured: {', '.join(ai_keys_found)}",
            )
        else:
            self._add_result(
                "ai_provider_configured", CheckCategory.ENVIRONMENT, CheckSeverity.FATAL,
                False, "No AI provider configured",
                f"Set at least one of: {', '.join(self.AI_PROVIDER_VARS)}",
            )

        # Check watcher-specific vars
        for watcher, vars_list in self.WATCHER_VARS.items():
            for var in vars_list:
                if os.getenv(var):
                    self._add_result(
                        f"env_{watcher}_{var}", CheckCategory.ENVIRONMENT, CheckSeverity.INFO,
                        True, f"Watcher env var set: {var}",
                    )

    # ─── Python Package Checks ────────────────────────────────────────

    def _check_python_packages(self):
        """Validate required Python packages are installed."""
        for package in self.CORE_PACKAGES:
            try:
                importlib.import_module(package)
                self._add_result(
                    f"package_{package}", CheckCategory.DEPENDENCIES, CheckSeverity.FATAL,
                    True, f"Package installed: {package}",
                )
            except ImportError:
                self._add_result(
                    f"package_{package}", CheckCategory.DEPENDENCIES, CheckSeverity.FATAL,
                    False, f"Package not installed: {package}",
                    f"Install with: pip install {package.replace('.', '-')}",
                )

    # ─── Credential Checks ────────────────────────────────────────────

    def _check_credentials(self):
        """Validate credential files."""
        creds_dir = self.vault_path / "secrets"
        if not creds_dir.exists():
            return  # Already checked in vault structure

        # Check for Gmail credentials
        gmail_creds = creds_dir / "gmail_credentials.json"
        if gmail_creds.exists():
            try:
                content = json.loads(gmail_creds.read_text())
                has_client_id = "installed" in content or "web" in content
                self._add_result(
                    "gmail_credentials", CheckCategory.CREDENTIALS,
                    CheckSeverity.WARNING if not has_client_id else CheckSeverity.INFO,
                    has_client_id,
                    f"Gmail credentials {'valid' if has_client_id else 'may be incomplete'}",
                )
            except json.JSONDecodeError:
                self._add_result(
                    "gmail_credentials", CheckCategory.CREDENTIALS, CheckSeverity.FATAL,
                    False, "Gmail credentials file is invalid JSON",
                )

        # Check for token files (Gmail OAuth)
        gmail_token = creds_dir / "gmail_token.json"
        if gmail_token.exists():
            self._add_result(
                "gmail_token", CheckCategory.CREDENTIALS, CheckSeverity.INFO,
                True, "Gmail OAuth token found",
            )

    # ─── MCP Server Checks ────────────────────────────────────────────

    def _check_mcp_servers(self):
        """Validate MCP server dependencies."""
        for server_name, config in self.MCP_SERVERS.items():
            module = config.get("module")
            description = config.get("description", server_name)

            if module is None:
                # No module dependency (uses stdlib or is pure Python)
                self._add_result(
                    f"mcp_{server_name}", CheckCategory.CONFIGURATION, CheckSeverity.INFO,
                    True, f"MCP server configured: {server_name} ({description})",
                )
                continue

            try:
                importlib.import_module(module)
                self._add_result(
                    f"mcp_{server_name}", CheckCategory.CONFIGURATION, CheckSeverity.INFO,
                    True, f"MCP server ready: {server_name} ({description})",
                )
            except ImportError:
                self._add_result(
                    f"mcp_{server_name}", CheckCategory.CONFIGURATION, CheckSeverity.WARNING,
                    False, f"MCP server may not work: {server_name} (missing {module})",
                )

    # ─── Security Checks ─────────────────────────────────────────────

    def _check_security(self):
        """Validate security configuration."""
        # Check .env file is NOT in git
        env_file = self.vault_path.parent / ".env"
        if env_file.exists():
            # Check if .env is in .gitignore
            gitignore = self.vault_path.parent / ".gitignore"
            if gitignore.exists():
                gitignore_content = gitignore.read_text()
                if ".env" in gitignore_content:
                    self._add_result(
                        "security_env_gitignored", CheckCategory.SECURITY, CheckSeverity.INFO,
                        True, ".env file is in .gitignore",
                    )
                else:
                    self._add_result(
                        "security_env_gitignored", CheckCategory.SECURITY, CheckSeverity.WARNING,
                        False, ".env file exists but is NOT in .gitignore",
                        "Add '.env' to .gitignore to prevent accidental commits",
                    )
            else:
                self._add_result(
                    "security_env_gitignored", CheckCategory.SECURITY, CheckSeverity.WARNING,
                    False, ".env file exists but no .gitignore found",
                )

        # Check vault secrets directory permissions
        secrets_dir = self.vault_path / "secrets"
        if secrets_dir.exists():
            stat = secrets_dir.stat()
            # On Unix, check if world-readable (mode & 0o077)
            if stat.st_mode & 0o077:
                self._add_result(
                    "secrets_permissions", CheckCategory.SECURITY, CheckSeverity.WARNING,
                    False, "Secrets directory is world-readable",
                    f"Fix with: chmod 700 {secrets_dir}",
                )
            else:
                self._add_result(
                    "secrets_permissions", CheckCategory.SECURITY, CheckSeverity.INFO,
                    True, "Secrets directory has correct permissions",
                )

    # ─── Port Availability Checks ─────────────────────────────────────

    def _check_health_port(self):
        """Check if health server port is available."""
        port = int(os.getenv("HEALTH_PORT", str(self.HEALTH_PORT)))

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(2)
            result = sock.connect_ex(("127.0.0.1", port))
            if result == 0:
                self._add_result(
                    "health_port_available", CheckCategory.PORTS, CheckSeverity.WARNING,
                    False, f"Port {port} is already in use (health server may fail to start)",
                    f"Change port: export HEALTH_PORT={port + 1}",
                )
            else:
                self._add_result(
                    "health_port_available", CheckCategory.PORTS, CheckSeverity.INFO,
                    True, f"Health server port {port} is available",
                )
        except Exception as e:
            self._add_result(
                "health_port_available", CheckCategory.PORTS, CheckSeverity.WARNING,
                False, f"Could not check port {port}: {e}",
            )
        finally:
            sock.close()

    # ─── Configuration File Checks ────────────────────────────────────

    def _check_configuration_files(self):
        """Validate MCP and other configuration files."""
        # Check .mcp.json
        mcp_config = self.vault_path.parent / ".mcp.json"
        if mcp_config.exists():
            try:
                content = json.loads(mcp_config.read_text())
                server_count = len(content.get("mcpServers", {}))
                self._add_result(
                    "mcp_config_valid", CheckCategory.CONFIGURATION, CheckSeverity.INFO,
                    True, f"MCP config valid: {server_count} servers configured",
                )
            except json.JSONDecodeError:
                self._add_result(
                    "mcp_config_valid", CheckCategory.CONFIGURATION, CheckSeverity.WARNING,
                    False, "MCP config file is invalid JSON",
                )

        # Check pyproject.toml
        pyproject = self.vault_path.parent / "pyproject.toml"
        if pyproject.exists():
            self._add_result(
                "pyproject_exists", CheckCategory.CONFIGURATION, CheckSeverity.INFO,
                True, "pyproject.toml found (dependency source of truth)",
            )

    # ─── Network Connectivity Checks (optional, slower) ───────────────

    def _check_network_connectivity(self):
        """Test connectivity to external services."""
        services = {
            "google_api": ("www.googleapis.com", 443),
            "anthropic_api": ("api.anthropic.com", 443),
            "openrouter": ("openrouter.ai", 443),
        }

        for name, (host, port) in services.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            try:
                result = sock.connect_ex((host, port))
                self._add_result(
                    f"network_{name}", CheckCategory.NETWORK, CheckSeverity.WARNING,
                    result == 0,
                    f"{'Can' if result == 0 else 'Cannot'} reach {host}:{port}",
                )
            except Exception as e:
                self._add_result(
                    f"network_{name}", CheckCategory.NETWORK, CheckSeverity.WARNING,
                    False, f"Network check failed for {host}: {e}",
                )
            finally:
                sock.close()

    # ─── Reporting ────────────────────────────────────────────────────

    def print_summary(self):
        """Print a human-readable validation summary."""
        report = ValidationReport(checks=self.results)
        report.completed_at = datetime.now().isoformat()

        print()
        print("=" * 60)
        print("🔍 Configuration Validation Report")
        print("=" * 60)

        if report.healthy:
            print(f"✅ System is {'READY' if report.passed_count == report.total_count else 'READY (with warnings)'}")
        else:
            print(f"❌ System is NOT READY — {len(report.fatal_errors)} fatal error(s)")

        print(f"   {report.passed_count}/{report.total_count} checks passed")
        print()

        # Fatal errors
        if report.fatal_errors:
            print("🚨 FATAL ERRORS (must fix before starting):")
            for check in report.fatal_errors:
                print(f"  ❌ {check.name}: {check.message}")
                if check.details:
                    print(f"     → {check.details}")
            print()

        # Warnings
        if report.warnings:
            print("⚠️  WARNINGS (system will start but may not function fully):")
            for check in report.warnings:
                print(f"  ⚠️  {check.name}: {check.message}")
                if check.details:
                    print(f"     → {check.details}")
            print()

        # Info items
        info_checks = [c for c in self.results if c.passed and c.severity == CheckSeverity.INFO]
        if info_checks:
            print("ℹ️  INFORMATIONAL:")
            for check in info_checks[:5]:  # Limit output
                print(f"  ℹ️  {check.name}: {check.message}")
            if len(info_checks) > 5:
                print(f"  ... and {len(info_checks) - 5} more")
            print()

        print("=" * 60)

    def print_json_report(self) -> str:
        """Print JSON validation report."""
        report = ValidationReport(checks=self.results)
        report.completed_at = datetime.now().isoformat()
        return json.dumps(report.to_dict(), indent=2)
