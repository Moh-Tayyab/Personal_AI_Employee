#!/usr/bin/env python3
"""
Gold Tier Validation Script

Quickly validates all Gold Tier components are working.
Run this before the demo to ensure everything is ready.

Usage:
    python demo/validate_gold_tier.py
"""

import os
import sys
import importlib.util
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class GoldTierValidator:
    """Validate all Gold Tier components."""

    def __init__(self, vault_path: str = './vault'):
        self.vault_path = Path(vault_path)
        self.project_root = Path(__file__).parent.parent
        self.results = {
            'checks': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'details': []
        }

    def _check(self, name: str, condition: bool, message: str, is_warning: bool = False):
        """Record a check result."""
        self.results['checks'] += 1

        if is_warning:
            self.results['warnings'] += 1
            status = "⚠️"
            print(f"  ⚠️  {name}: {message}")
        elif condition:
            self.results['passed'] += 1
            status = "✅"
            print(f"  ✅ {name}: {message}")
        else:
            self.results['failed'] += 1
            status = "❌"
            print(f"  ❌ {name}: {message}")

        self.results['details'].append({
            'name': name,
            'status': 'WARNING' if is_warning else ('PASS' if condition else 'FAIL'),
            'message': message
        })

    def validate_vault_structure(self):
        """Validate vault directory structure."""
        print("\n📁 Vault Structure:")

        required_dirs = [
            'Needs_Action', 'Plans', 'Done', 'Pending_Approval',
            'Approved', 'Rejected', 'Logs', 'Briefings', 'In_Progress'
        ]

        for dir_name in required_dirs:
            dir_path = self.vault_path / dir_name
            exists = dir_path.exists()
            self._check(
                dir_name,
                exists,
                f"{'Exists' if exists else 'Missing'}",
                is_warning=not exists
            )

        # Check required files
        required_files = ['Company_Handbook.md', 'Business_Goals.md', 'Dashboard.md']
        for file_name in required_files:
            file_path = self.vault_path / file_name
            exists = file_path.exists()
            self._check(
                file_name,
                exists,
                f"{'Exists' if exists else 'Missing'}"
            )

    def validate_watchers(self):
        """Validate watcher scripts."""
        print("\n👁️  Watchers:")

        watchers = [
            ('watchers/gmail_watcher.py', 'Gmail Watcher'),
            ('watchers/whatsapp_watcher.py', 'WhatsApp Watcher'),
            ('watchers/filesystem_watcher.py', 'Filesystem Watcher'),
            ('watchers/base_watcher.py', 'Base Watcher'),
        ]

        for path, name in watchers:
            watcher_path = self.project_root / path
            exists = watcher_path.exists()
            self._check(
                name,
                exists,
                f"{'Found' if exists else 'Not found'}"
            )

            # Try to import
            if exists:
                try:
                    spec = importlib.util.spec_from_file_location(name, watcher_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        self._check(f"{name} Import", True, "Importable")
                    else:
                        self._check(f"{name} Import", False, "Failed to create spec", is_warning=True)
                except Exception as e:
                    self._check(f"{name} Import", False, str(e), is_warning=True)

    def validate_mcp_servers(self):
        """Validate MCP server scripts."""
        print("\n🔌 MCP Servers:")

        servers = [
            ('mcp_local/email/server.py', 'Email MCP'),
            ('mcp_local/linkedin/server.py', 'LinkedIn MCP'),
            ('mcp_local/twitter/server.py', 'Twitter MCP'),
            ('mcp_local/social/server.py', 'Social MCP (Facebook/Instagram)'),
            ('mcp_local/filesystem/server.py', 'Filesystem MCP'),
            ('mcp_local/odoo/server.py', 'Odoo MCP'),
        ]

        for path, name in servers:
            server_path = self.project_root / path
            exists = server_path.exists()
            self._check(
                name,
                exists,
                f"{'Found' if exists else 'Not found'}"
            )

    def validate_orchestrator(self):
        """Validate orchestrator."""
        print("\n🎯 Orchestrator:")

        orchestrator_path = self.project_root / 'orchestrator.py'
        exists = orchestrator_path.exists()
        self._check(
            'Orchestrator',
            exists,
            f"{'Found' if exists else 'Not found'}"
        )

        if exists:
            try:
                from orchestrator import Orchestrator
                self._check("Orchestrator Import", True, "Importable")

                # Try to instantiate
                try:
                    orch = Orchestrator(vault_path=str(self.vault_path), dry_run=True)
                    self._check("Orchestrator Init", True, "Initialized (DRY_RUN)")
                except Exception as e:
                    self._check("Orchestrator Init", False, str(e))

            except Exception as e:
                self._check("Orchestrator Import", False, str(e))

    def validate_scripts(self):
        """Validate helper scripts."""
        print("\n🛠️  Helper Scripts:")

        scripts = [
            ('scripts/generate_ceo_briefing.py', 'CEO Briefing Generator'),
            ('scripts/ralph_loop.py', 'Ralph Wiggum Loop'),
            ('scripts/start_all.sh', 'Start All Script'),
            ('scripts/health_server.py', 'Health Server'),
            ('scripts/error_recovery_integration.py', 'Error Recovery'),
        ]

        for path, name in scripts:
            script_path = self.project_root / path
            exists = script_path.exists()
            self._check(
                name,
                exists,
                f"{'Found' if exists else 'Not found'}",
                is_warning=not exists
            )

    def validate_dependencies(self):
        """Validate Python dependencies."""
        print("\n📦 Dependencies:")

        dependencies = [
            ('anthropic', 'Anthropic SDK'),
            ('google.oauth2', 'Google Auth'),
            ('googleapiclient', 'Google API Client'),
            ('playwright', 'Playwright'),
            ('mcp', 'MCP SDK'),
            ('requests', 'Requests'),
            ('flask', 'Flask'),
            ('watchdog', 'Watchdog'),
            ('schedule', 'Schedule'),
            ('pyyaml', 'PyYAML'),
            ('dotenv', 'python-dotenv'),
        ]

        for module_name, name in dependencies:
            try:
                importlib.import_module(module_name)
                self._check(name, True, "Installed")
            except ImportError:
                self._check(name, False, "Not installed", is_warning=True)

    def validate_env_config(self):
        """Validate environment configuration."""
        print("\n⚙️  Environment Configuration:")

        # Check for .env file
        env_path = self.project_root / '.env'
        if env_path.exists():
            self._check(".env File", True, "Found")

            # Check for API keys (don't print them)
            from dotenv import load_dotenv
            load_dotenv(env_path)

            api_keys = {
                'ANTHROPIC_API_KEY': 'Anthropic API Key',
                'GEMINI_API_KEY': 'Gemini API Key',
                'OPENROUTER_API_KEY': 'OpenRouter API Key',
                'DRY_RUN': 'DRY_RUN Mode',
            }

            for key, name in api_keys.items():
                value = os.getenv(key)
                if value:
                    display = value[:10] + '...' if len(value) > 10 else value
                    self._check(name, True, f"Set ({display})")
                else:
                    self._check(name, False, "Not set", is_warning=True)
        else:
            self._check(".env File", False, "Not found - create from .env.example", is_warning=True)

    def validate_demo_scripts(self):
        """Validate demo scripts."""
        print("\n🎬 Demo Scripts:")

        demos = [
            ('demo/end_to_end_demo.py', 'End-to-End Demo'),
        ]

        for path, name in demos:
            demo_path = self.project_root / path
            exists = demo_path.exists()
            self._check(
                name,
                exists,
                f"{'Found' if exists else 'Not found'}"
            )

    def run_full_validation(self):
        """Run complete validation."""
        print("=" * 70)
        print("  Gold Tier Validation")
        print("=" * 70)
        print(f"\n  Vault Path: {self.vault_path}")
        print(f"  Timestamp: {datetime.now().isoformat()}")

        try:
            self.validate_vault_structure()
            self.validate_watchers()
            self.validate_mcp_servers()
            self.validate_orchestrator()
            self.validate_scripts()
            self.validate_dependencies()
            self.validate_env_config()
            self.validate_demo_scripts()

            # Summary
            print("\n" + "=" * 70)
            print(f"  Validation Summary")
            print("=" * 70)

            passed = self.results['passed']
            failed = self.results['failed']
            warnings = self.results['warnings']
            total = self.results['checks']

            print(f"\n  ✅ Passed: {passed}")
            print(f"  ❌ Failed: {failed}")
            print(f"  ⚠️  Warnings: {warnings}")
            print(f"  📊 Total: {total}")
            print(f"\n  Success Rate: {(passed/total*100) if total > 0 else 0:.0f}%")

            if failed == 0 and warnings <= 2:
                print("\n  🎉 VALIDATION PASSED - Ready for Gold Tier Demo!")
            elif failed == 0:
                print(f"\n  ⚠️  VALIDATION PASSED WITH {warnings} WARNING(S) - Demo can proceed")
            else:
                print(f"\n  ❌ VALIDATION FAILED - Fix {failed} issue(s) before demo")

            print("=" * 70)

            return failed == 0

        except Exception as e:
            print(f"\n  ❌ Validation failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Gold Tier Validation')
    parser.add_argument('--vault', default='./vault', help='Path to vault')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    validator = GoldTierValidator(args.vault)
    success = validator.run_full_validation()

    if args.json:
        import json
        print("\nValidation Results (JSON):")
        print(json.dumps(validator.results, indent=2))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
