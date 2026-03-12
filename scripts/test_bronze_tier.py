#!/usr/bin/env python3
"""
Bronze Tier Complete Test Suite

Tests all Bronze Tier requirements:
1. Obsidian vault structure (Dashboard.md, Company_Handbook.md, Business_Goals.md)
2. At least one working watcher (Gmail or Filesystem)
3. Claude Code integration (via orchestrator)

Usage:
    python scripts/test_bronze_tier.py --vault ./vault
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text):
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text):
    print(f"{YELLOW}⚠️ {text}{RESET}")


def print_info(text):
    print(f"{BLUE}ℹ️ {text}{RESET}")


class BronzeTierTester:
    """Test Bronze Tier requirements."""
    
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.results = {
            "vault_structure": {},
            "watchers": {},
            "claude_integration": {},
            "overall": False
        }
        self.score = 0
        self.max_score = 100
    
    def test_vault_structure(self):
        """Test vault structure requirements."""
        print_header("1. Testing Vault Structure")
        
        # Test Dashboard.md
        dashboard = self.vault / "Dashboard.md"
        if dashboard.exists():
            content = dashboard.read_text()
            if "status:" in content.lower() or "Personal AI Employee" in content:
                print_success("Dashboard.md exists and is valid")
                self.results["vault_structure"]["dashboard"] = True
                self.score += 10
            else:
                print_warning("Dashboard.md exists but may be empty or invalid")
                self.results["vault_structure"]["dashboard"] = False
                self.score += 5
        else:
            print_error("Dashboard.md not found")
            self.results["vault_structure"]["dashboard"] = False
        
        # Test Company_Handbook.md
        handbook = self.vault / "Company_Handbook.md"
        if handbook.exists():
            content = handbook.read_text()
            if "autonomy" in content.lower() or "approval" in content.lower():
                print_success("Company_Handbook.md exists with autonomy rules")
                self.results["vault_structure"]["handbook"] = True
                self.score += 10
            else:
                print_warning("Company_Handbook.md exists but may be missing rules")
                self.results["vault_structure"]["handbook"] = False
                self.score += 5
        else:
            print_error("Company_Handbook.md not found")
            self.results["vault_structure"]["handbook"] = False
        
        # Test Business_Goals.md
        goals = self.vault / "Business_Goals.md"
        if goals.exists():
            content = goals.read_text()
            if "goal" in content.lower() or "kpi" in content.lower():
                print_success("Business_Goals.md exists with goals/KPIs")
                self.results["vault_structure"]["goals"] = True
                self.score += 10
            else:
                print_warning("Business_Goals.md exists but may be missing goals")
                self.results["vault_structure"]["goals"] = False
                self.score += 5
        else:
            print_error("Business_Goals.md not found")
            self.results["vault_structure"]["goals"] = False
        
        # Test folder structure
        required_folders = [
            "Needs_Action",
            "Plans",
            "Done",
            "Pending_Approval",
            "Approved",
            "Logs"
        ]
        
        folders_ok = 0
        for folder in required_folders:
            if (self.vault / folder).exists():
                folders_ok += 1
        
        if folders_ok == len(required_folders):
            print_success(f"All {len(required_folders)} required folders exist")
            self.results["vault_structure"]["folders"] = True
            self.score += 10
        else:
            print_warning(f"Only {folders_ok}/{len(required_folders)} folders exist")
            self.results["vault_structure"]["folders"] = False
            self.score += 5
        
        return self.score >= 35  # 35 out of 40 points
    
    def test_watchers(self):
        """Test watcher availability and functionality."""
        print_header("2. Testing Watchers")
        
        watchers_path = Path("watchers")
        
        # Check Gmail Watcher
        gmail_watcher = watchers_path / "gmail_watcher.py"
        if gmail_watcher.exists():
            print_success("Gmail Watcher exists")
            self.results["watchers"]["gmail_exists"] = True
            self.score += 5
            
            # Check if credentials exist
            creds_path = Path(os.getenv('GMAIL_CREDENTIALS_PATH', self.vault / 'secrets' / 'gmail_credentials.json'))
            token_path = Path(os.getenv('GMAIL_TOKEN_PATH', self.vault / 'secrets' / 'gmail_token.json'))
            
            if creds_path.exists():
                print_success("Gmail credentials found")
                self.results["watchers"]["gmail_creds"] = True
                self.score += 5
            else:
                print_warning("Gmail credentials not found (run: python scripts/fix_gmail_token.py)")
                self.results["watchers"]["gmail_creds"] = False
            
            if token_path.exists():
                print_success("Gmail token found (authenticated)")
                self.results["watchers"]["gmail_token"] = True
                self.score += 10
            else:
                print_warning("Gmail token not found (needs authentication)")
                self.results["watchers"]["gmail_token"] = False
        else:
            print_error("Gmail Watcher not found")
            self.results["watchers"]["gmail_exists"] = False
        
        # Check Filesystem Watcher
        fs_watcher = watchers_path / "filesystem_watcher.py"
        if fs_watcher.exists():
            print_success("Filesystem Watcher exists")
            self.results["watchers"]["fs_exists"] = True
            self.score += 10
            
            # Test if watchdog is installed
            try:
                import watchdog
                print_success("Watchdog library installed")
                self.results["watchers"]["fs_deps"] = True
                self.score += 5
            except ImportError:
                print_warning("Watchdog not installed (pip install watchdog)")
                self.results["watchers"]["fs_deps"] = False
        else:
            print_error("Filesystem Watcher not found")
            self.results["watchers"]["fs_exists"] = False
        
        # Check WhatsApp Watcher
        wa_watcher = watchers_path / "whatsapp_watcher.py"
        if wa_watcher.exists():
            print_success("WhatsApp Watcher exists (bonus)")
            self.results["watchers"]["whatsapp_exists"] = True
            self.score += 5
        else:
            print_info("WhatsApp Watcher not found (optional)")
            self.results["watchers"]["whatsapp_exists"] = False
        
        # At least one watcher should be functional
        has_working_watcher = (
            (self.results["watchers"].get("gmail_exists") and self.results["watchers"].get("gmail_token")) or
            (self.results["watchers"].get("fs_exists") and self.results["watchers"].get("fs_deps"))
        )
        
        if has_working_watcher:
            print_success("At least one watcher is functional")
            self.results["watchers"]["has_working"] = True
            self.score += 10
        else:
            print_warning("No fully functional watcher (need auth or dependencies)")
            self.results["watchers"]["has_working"] = False
        
        return has_working_watcher
    
    def test_claude_integration(self):
        """Test Claude Code integration."""
        print_header("3. Testing Claude Code Integration")
        
        # Check orchestrator exists
        orchestrator = Path("orchestrator.py")
        if orchestrator.exists():
            print_success("Orchestrator exists")
            self.results["claude_integration"]["orchestrator"] = True
            self.score += 5
        else:
            print_error("Orchestrator not found")
            self.results["claude_integration"]["orchestrator"] = False
            return False
        
        # Check for multi-provider AI system
        multi_provider = Path("scripts/multi_provider_ai.py")
        if multi_provider.exists():
            print_success("Multi-Provider AI system exists")
            self.results["claude_integration"]["multi_provider"] = True
            self.score += 10
        else:
            print_warning("Multi-Provider AI not found")
            self.results["claude_integration"]["multi_provider"] = False
        
        # Check for Anthropic API key
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key and anthropic_key != 'your_anthropic_api_key_here':
            print_success("Anthropic API key configured")
            self.results["claude_integration"]["api_key"] = True
            self.score += 15
        else:
            print_warning("Anthropic API key not configured (set ANTHROPIC_API_KEY in .env)")
            self.results["claude_integration"]["api_key"] = False
            self.score += 5  # Partial credit for having the integration
        
        # Check orchestrator has AI integration
        content = orchestrator.read_text()
        if "multi_provider_ai" in content or "trigger_ai" in content or "claude" in content.lower():
            print_success("Orchestrator has AI integration")
            self.results["claude_integration"]["integration"] = True
            self.score += 10
        else:
            print_error("Orchestrator missing AI integration")
            self.results["claude_integration"]["integration"] = False
        
        # Check requirements.txt has anthropic
        req_file = Path("requirements.txt")
        if req_file.exists():
            req_content = req_file.read_text()
            if "anthropic" in req_content:
                print_success("Anthropic package in requirements.txt")
                self.results["claude_integration"]["requirements"] = True
                self.score += 5
            else:
                print_warning("Anthropic package not in requirements.txt")
                self.results["claude_integration"]["requirements"] = False
        
        # Check if anthropic is installed
        try:
            import anthropic
            print_success("Anthropic library installed")
            self.results["claude_integration"]["installed"] = True
            self.score += 5
        except ImportError:
            print_warning("Anthropic not installed (pip install anthropic)")
            self.results["claude_integration"]["installed"] = False
        
        has_claude = (
            self.results["claude_integration"].get("orchestrator") and
            self.results["claude_integration"].get("integration")
        )
        
        return has_claude
    
    def run_all_tests(self):
        """Run all Bronze Tier tests."""
        print_header("BRONZE TIER TEST SUITE")
        print(f"Vault: {self.vault.absolute()}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run tests
        vault_ok = self.test_vault_structure()
        watcher_ok = self.test_watchers()
        claude_ok = self.test_claude_integration()
        
        # Calculate final score
        self.results["overall"] = vault_ok and watcher_ok and claude_ok
        self.results["score"] = self.score
        self.results["max_score"] = self.max_score
        
        # Print summary
        print_header("TEST SUMMARY")
        
        print(f"Vault Structure:     {'✅ PASS' if vault_ok else '❌ FAIL'}")
        print(f"Watchers:            {'✅ PASS' if watcher_ok else '❌ FAIL'}")
        print(f"Claude Integration:  {'✅ PASS' if claude_ok else '❌ FAIL'}")
        print()
        print(f"Score: {self.score}/{self.max_score} ({self.score * 100 // self.max_score}%)")
        print()
        
        if self.results["overall"]:
            print_success("🎉 BRONZE TIER: 100% COMPLETE!")
        else:
            print_warning("⚠️ BRONZE TIER: Not yet complete")
            print()
            print("To complete Bronze Tier:")
            
            if not vault_ok:
                print("  - Ensure Dashboard.md, Company_Handbook.md, Business_Goals.md exist")
            
            if not watcher_ok:
                print("  - Run: python scripts/fix_gmail_token.py")
                print("  - Or ensure Filesystem Watcher has: pip install watchdog")
            
            if not claude_ok:
                print("  - Set ANTHROPIC_API_KEY in .env file")
                print("  - Run: pip install anthropic")
        
        return self.results["overall"]
    
    def save_report(self, output_path: str = None):
        """Save test report to file."""
        if output_path is None:
            output_path = self.vault / "Logs" / f"bronze_tier_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "vault_path": str(self.vault.absolute()),
            "results": self.results,
            "score": f"{self.score}/{self.max_score}",
            "percentage": f"{self.score * 100 // self.max_score}%",
            "bronze_tier_complete": self.results["overall"]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print_info(f"Report saved to: {output_path}")
        return output_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Bronze Tier Requirements')
    parser.add_argument('--vault', default='./vault', help='Path to vault')
    parser.add_argument('--output', help='Output path for report')
    
    args = parser.parse_args()
    
    tester = BronzeTierTester(args.vault)
    success = tester.run_all_tests()
    
    if args.output or success:
        tester.save_report(args.output)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
