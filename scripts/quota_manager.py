#!/usr/bin/env python3
"""
Quota Manager for Multi-CLI Fallback System
Tracks API quotas and determines available CLIs
"""

import json
import datetime
import requests
import subprocess
from pathlib import Path
from typing import Dict, Optional

class QuotaManager:
    def __init__(self, vault_path: str = "./vault"):
        self.vault_path = Path(vault_path)
        self.config_dir = self.vault_path / "config"
        self.config_dir.mkdir(exist_ok=True)

        self.quota_file = self.config_dir / "quota_status.json"
        self.load_quota_status()

    def load_quota_status(self):
        """Load current quota status from file"""
        if self.quota_file.exists():
            with open(self.quota_file) as f:
                self.quota_data = json.load(f)
        else:
            self.quota_data = {
                "claude": {
                    "remaining": 1000,
                    "exhausted": False,
                    "last_check": None,
                    "reset_time": None
                },
                "qwen": {
                    "available": True,
                    "local": True,
                    "last_check": None
                },
                "codex": {
                    "remaining": 500,
                    "exhausted": False,
                    "last_check": None,
                    "reset_time": None
                }
            }
            self.save_quota_status()

    def save_quota_status(self):
        """Save quota status to file"""
        with open(self.quota_file, 'w') as f:
            json.dump(self.quota_data, f, indent=2)

    def check_claude_quota(self) -> bool:
        """Check if Claude API quota is available"""
        try:
            # Simple test call to Claude API
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.quota_data["claude"]["exhausted"] = False
                self.quota_data["claude"]["last_check"] = datetime.datetime.now().isoformat()
                self.save_quota_status()
                return True
            else:
                # Check if error is quota-related
                error_msg = result.stderr.lower()
                if any(word in error_msg for word in ["quota", "limit", "exceeded", "rate"]):
                    self.quota_data["claude"]["exhausted"] = True
                    self.save_quota_status()
                    return False
                return True

        except Exception as e:
            print(f"⚠️  Claude quota check failed: {e}")
            # Don't mark as exhausted on connection errors
            return not self.quota_data["claude"]["exhausted"]

    def check_qwen_availability(self) -> bool:
        """Check if Qwen CLI is available"""
        try:
            result = subprocess.run(
                ["qwen", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            available = result.returncode == 0
            self.quota_data["qwen"]["available"] = available
            self.quota_data["qwen"]["last_check"] = datetime.datetime.now().isoformat()
            self.save_quota_status()
            return available
        except Exception:
            # Qwen might not be installed, but that's ok
            return False

    def check_codex_quota(self) -> bool:
        """Check if GitHub Copilot CLI quota is available"""
        try:
            result = subprocess.run(
                ["gh", "copilot", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.quota_data["codex"]["exhausted"] = False
                self.quota_data["codex"]["last_check"] = datetime.datetime.now().isoformat()
                self.save_quota_status()
                return True
            else:
                error_msg = result.stderr.lower()
                if any(word in error_msg for word in ["quota", "limit", "exceeded"]):
                    self.quota_data["codex"]["exhausted"] = True
                    self.save_quota_status()
                    return False
                return True

        except Exception as e:
            print(f"⚠️  Codex quota check failed: {e}")
            return not self.quota_data["codex"]["exhausted"]

    def get_best_available_cli(self) -> str:
        """Return the best available CLI based on current status"""
        # Check all quotas
        claude_ok = self.check_claude_quota()
        qwen_ok = self.check_qwen_availability()
        codex_ok = self.check_codex_quota()

        # Priority order: Claude > Qwen > Codex
        if claude_ok:
            return "claude"
        elif qwen_ok:
            return "qwen"
        elif codex_ok:
            return "codex"
        else:
            # Fallback to qwen even if not detected (might be local)
            return "qwen"

    def get_status_report(self) -> Dict:
        """Get comprehensive status report"""
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "recommended_cli": self.get_best_available_cli(),
            "claude": {
                "available": not self.quota_data["claude"]["exhausted"],
                "last_check": self.quota_data["claude"]["last_check"]
            },
            "qwen": {
                "available": self.quota_data["qwen"]["available"],
                "local": self.quota_data["qwen"]["local"],
                "last_check": self.quota_data["qwen"]["last_check"]
            },
            "codex": {
                "available": not self.quota_data["codex"]["exhausted"],
                "last_check": self.quota_data["codex"]["last_check"]
            }
        }

if __name__ == "__main__":
    import sys

    quota_manager = QuotaManager()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            status = quota_manager.get_status_report()
            print(json.dumps(status, indent=2))
        elif sys.argv[1] == "--best-cli":
            print(quota_manager.get_best_available_cli())
        elif sys.argv[1] == "--reset":
            quota_manager.quota_data["claude"]["exhausted"] = False
            quota_manager.quota_data["codex"]["exhausted"] = False
            quota_manager.save_quota_status()
            print("✅ Quota status reset")
    else:
        print("Usage: python quota_manager.py [--status|--best-cli|--reset]")