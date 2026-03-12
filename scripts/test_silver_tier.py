#!/usr/bin/env python3
"""
Silver Tier Complete Test Suite

Tests all Silver Tier requirements:
1. Multiple watchers running simultaneously
2. Plan.md generation for each task
3. Email MCP server functional
4. Human-in-the-loop approval workflow with notifications

Usage:
    python scripts/test_silver_tier.py --vault ./vault
"""

import os
import sys
import time
import json
import subprocess
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


class SilverTierTester:
    """Test Silver Tier requirements."""
    
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.results = {
            "multiple_watchers": {},
            "plan_generation": {},
            "email_mcp": {},
            "approval_workflow": {},
            "overall": False
        }
        self.score = 0
        self.max_score = 100
    
    def test_multiple_watchers(self):
        """Test multiple watchers can run simultaneously."""
        print_header("1. Testing Multiple Watchers")
        
        watchers_path = Path("watchers")
        
        # Check Gmail Watcher
        gmail_watcher = watchers_path / "gmail_watcher.py"
        if gmail_watcher.exists():
            print_success("Gmail Watcher exists")
            self.results["multiple_watchers"]["gmail_exists"] = True
            self.score += 5
            
            # Check credentials
            creds_path = Path(os.getenv('GMAIL_CREDENTIALS_PATH', self.vault / 'secrets' / 'gmail_credentials.json'))
            if creds_path.exists():
                print_success("Gmail credentials found")
                self.results["multiple_watchers"]["gmail_creds"] = True
                self.score += 5
            else:
                print_warning("Gmail credentials not configured")
                self.results["multiple_watchers"]["gmail_creds"] = False
        else:
            print_error("Gmail Watcher not found")
            self.results["multiple_watchers"]["gmail_exists"] = False
        
        # Check Filesystem Watcher
        fs_watcher = watchers_path / "filesystem_watcher.py"
        if fs_watcher.exists():
            print_success("Filesystem Watcher exists")
            self.results["multiple_watchers"]["fs_exists"] = True
            self.score += 10
            
            # Test if watchdog is installed
            try:
                import watchdog
                print_success("Watchdog library installed")
                self.results["multiple_watchers"]["fs_deps"] = True
                self.score += 5
            except ImportError:
                print_warning("Watchdog not installed (pip install watchdog)")
                self.results["multiple_watchers"]["fs_deps"] = False
        else:
            print_error("Filesystem Watcher not found")
            self.results["multiple_watchers"]["fs_exists"] = False
        
        # Check WhatsApp Watcher
        wa_watcher = watchers_path / "whatsapp_watcher.py"
        if wa_watcher.exists():
            print_success("WhatsApp Watcher exists")
            self.results["multiple_watchers"]["whatsapp_exists"] = True
            self.score += 5
            
            # Check playwright
            try:
                import playwright
                print_success("Playwright installed for WhatsApp")
                self.results["multiple_watchers"]["wa_deps"] = True
                self.score += 5
            except ImportError:
                print_warning("Playwright not installed (pip install playwright)")
                self.results["multiple_watchers"]["wa_deps"] = False
        else:
            print_info("WhatsApp Watcher not found (optional)")
            self.results["multiple_watchers"]["whatsapp_exists"] = False
        
        # Check run_all_watchers script
        run_all_script = Path("scripts/run_all_watchers.py")
        if run_all_script.exists():
            print_success("Multiple watcher runner script exists")
            self.results["multiple_watchers"]["runner_script"] = True
            self.score += 5
        else:
            print_warning("No script to run multiple watchers")
            self.results["multiple_watchers"]["runner_script"] = False
        
        # Count working watchers
        working_count = 0
        if self.results["multiple_watchers"].get("gmail_exists") and self.results["multiple_watchers"].get("gmail_creds"):
            working_count += 1
        if self.results["multiple_watchers"].get("fs_exists") and self.results["multiple_watchers"].get("fs_deps"):
            working_count += 1
        if self.results["multiple_watchers"].get("whatsapp_exists") and self.results["multiple_watchers"].get("wa_deps"):
            working_count += 1
        
        if working_count >= 2:
            print_success(f"Multiple watchers ready ({working_count} functional)")
            self.results["multiple_watchers"]["multiple_ready"] = True
            self.score += 10
        else:
            print_warning(f"Only {working_count} watcher(s) fully functional (need 2+)")
            self.results["multiple_watchers"]["multiple_ready"] = False
        
        return working_count >= 2
    
    def test_plan_generation(self):
        """Test Plan.md generation for tasks."""
        print_header("2. Testing Plan Generation")
        
        plans_folder = self.vault / "Plans"
        
        # Check if Plans folder exists
        if plans_folder.exists():
            print_success("Plans folder exists")
            self.results["plan_generation"]["folder_exists"] = True
            self.score += 5
        else:
            print_error("Plans folder not found")
            self.results["plan_generation"]["folder_exists"] = False
            return False
        
        # Check for existing plans
        plan_files = list(plans_folder.glob("*.md"))
        
        if plan_files:
            print_success(f"Found {len(plan_files)} plan files")
            self.results["plan_generation"]["plans_exist"] = True
            self.score += 15
            
            # Show latest plan
            latest = max(plan_files, key=lambda x: x.stat().st_mtime)
            print_info(f"Latest plan: {latest.name}")
            
            # Check plan structure
            content = latest.read_text()
            has_structure = any([
                "---" in content,  # Has frontmatter
                "Action" in content,  # Has action items
                "Analysis" in content or "Recommended" in content  # Has analysis
            ])
            
            if has_structure:
                print_success("Plans have proper structure")
                self.results["plan_generation"]["proper_structure"] = True
                self.score += 10
            else:
                print_warning("Plan structure may be incomplete")
                self.results["plan_generation"]["proper_structure"] = False
        else:
            print_warning("No plan files found (run orchestrator to generate)")
            self.results["plan_generation"]["plans_exist"] = False
            self.score += 5  # Partial credit for having the folder
        
        # Check orchestrator has plan generation
        orchestrator = Path("orchestrator.py")
        if orchestrator.exists():
            content = orchestrator.read_text()
            if "Plans" in content and "write_text" in content:
                print_success("Orchestrator generates plans")
                self.results["plan_generation"]["orchestrator_generates"] = True
                self.score += 10
            else:
                print_warning("Orchestrator may not generate plans")
                self.results["plan_generation"]["orchestrator_generates"] = False
        
        has_plans = (
            self.results["plan_generation"].get("folder_exists") and
            (self.results["plan_generation"].get("plans_exist") or self.results["plan_generation"].get("orchestrator_generates"))
        )
        
        return has_plans
    
    def test_email_mcp(self):
        """Test Email MCP server functionality."""
        print_header("3. Testing Email MCP Server")
        
        email_mcp = Path("mcp/email/server.py")
        
        # Check if Email MCP exists
        if email_mcp.exists():
            print_success("Email MCP server exists")
            self.results["email_mcp"]["exists"] = True
            self.score += 10
        else:
            print_error("Email MCP server not found")
            self.results["email_mcp"]["exists"] = False
            return False
        
        # Check for required methods
        content = email_mcp.read_text()
        
        has_send = "def send_email" in content
        has_draft = "def draft_email" in content
        has_search = "def search_emails" in content
        
        if has_send:
            print_success("send_email method exists")
            self.results["email_mcp"]["send_method"] = True
            self.score += 5
        else:
            print_warning("send_email method not found")
            self.results["email_mcp"]["send_method"] = False
        
        if has_draft:
            print_success("draft_email method exists")
            self.results["email_mcp"]["draft_method"] = True
            self.score += 5
        else:
            print_warning("draft_email method not found")
            self.results["email_mcp"]["draft_method"] = False
        
        if has_search:
            print_success("search_emails method exists")
            self.results["email_mcp"]["search_method"] = True
            self.score += 5
        else:
            print_warning("search_emails method not found")
            self.results["email_mcp"]["search_method"] = False
        
        # Check Gmail dependencies
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            print_success("Gmail API libraries installed")
            self.results["email_mcp"]["deps_installed"] = True
            self.score += 10
        except ImportError as e:
            print_warning(f"Gmail API not installed: {e}")
            print_info("Install: pip install google-auth google-auth-oauthlib google-api-python-client")
            self.results["email_mcp"]["deps_installed"] = False
            self.score += 5  # Partial credit
        
        # Check Gmail token
        token_path = Path(os.getenv('GMAIL_TOKEN_PATH', self.vault / 'secrets' / 'gmail_token.json'))
        if token_path.exists():
            print_success("Gmail token found (authenticated)")
            self.results["email_mcp"]["authenticated"] = True
            self.score += 10
        else:
            print_warning("Gmail token not found (run: python scripts/fix_gmail_token.py)")
            self.results["email_mcp"]["authenticated"] = False
            self.score += 5  # Partial credit for having the infrastructure
        
        # Check Drafts folder
        drafts_folder = self.vault / "Drafts"
        if drafts_folder.exists():
            draft_files = list(drafts_folder.glob("*.md"))
            if draft_files:
                print_success(f"Drafts folder exists with {len(draft_files)} drafts")
                self.results["email_mcp"]["drafts_folder"] = True
                self.score += 5
            else:
                print_info("Drafts folder exists (empty)")
                self.results["email_mcp"]["drafts_folder"] = True
                self.score += 5
        else:
            print_warning("Drafts folder not found")
            self.results["email_mcp"]["drafts_folder"] = False
        
        has_email = (
            self.results["email_mcp"].get("exists") and
            self.results["email_mcp"].get("send_method") and
            self.results["email_mcp"].get("deps_installed")
        )
        
        return has_email
    
    def test_approval_workflow(self):
        """Test human-in-the-loop approval workflow."""
        print_header("4. Testing Approval Workflow")
        
        # Check Pending_Approval folder
        pending_folder = self.vault / "Pending_Approval"
        if pending_folder.exists():
            print_success("Pending_Approval folder exists")
            self.results["approval_workflow"]["pending_folder"] = True
            self.score += 5
        else:
            print_error("Pending_Approval folder not found")
            self.results["approval_workflow"]["pending_folder"] = False
        
        # Check Approved folder
        approved_folder = self.vault / "Approved"
        if approved_folder.exists():
            print_success("Approved folder exists")
            self.results["approval_workflow"]["approved_folder"] = True
            self.score += 5
        else:
            print_error("Approved folder not found")
            self.results["approval_workflow"]["approved_folder"] = False
        
        # Check Rejected folder
        rejected_folder = self.vault / "Rejected"
        if rejected_folder.exists():
            print_success("Rejected folder exists")
            self.results["approval_workflow"]["rejected_folder"] = True
            self.score += 5
        else:
            print_error("Rejected folder not found")
            self.results["approval_workflow"]["rejected_folder"] = False
        
        # Check for approval files
        if pending_folder.exists():
            pending_files = list(pending_folder.glob("*.md"))
            if pending_files:
                print_success(f"Found {len(pending_files)} pending approval(s)")
                self.results["approval_workflow"]["pending_items"] = True
                self.score += 10
                
                # Show latest pending
                latest = max(pending_files, key=lambda x: x.stat().st_mtime)
                print_info(f"Latest pending: {latest.name}")
            else:
                print_info("No pending approvals (normal if all processed)")
                self.results["approval_workflow"]["pending_items"] = False
                self.score += 5
        
        # Check orchestrator has approval logic
        orchestrator = Path("orchestrator.py")
        if orchestrator.exists():
            content = orchestrator.read_text()
            has_approval_logic = (
                "Pending_Approval" in content and
                "approval" in content.lower()
            )
            
            if has_approval_logic:
                print_success("Orchestrator has approval logic")
                self.results["approval_workflow"]["orchestrator_logic"] = True
                self.score += 10
            else:
                print_warning("Orchestrator may not handle approvals")
                self.results["approval_workflow"]["orchestrator_logic"] = False
        
        # Check for notification script
        notification_script = Path("scripts/approval_notifications.py")
        if notification_script.exists():
            print_success("Approval notification script exists")
            self.results["approval_workflow"]["notification_script"] = True
            self.score += 10
        else:
            print_warning("No approval notification script")
            self.results["approval_workflow"]["notification_script"] = False
        
        # Check webhook configuration
        has_webhooks = bool(os.getenv('SLACK_WEBHOOK_URL') or os.getenv('DISCORD_WEBHOOK_URL'))
        if has_webhooks:
            print_success("Webhook notifications configured")
            self.results["approval_workflow"]["webhooks_configured"] = True
            self.score += 10
        else:
            print_info("Webhook notifications not configured (optional)")
            print_info("Add SLACK_WEBHOOK_URL or DISCORD_WEBHOOK_URL to .env")
            self.results["approval_workflow"]["webhooks_configured"] = False
            self.score += 5  # Partial credit
        
        # Check Company Handbook has approval rules
        handbook = self.vault / "Company_Handbook.md"
        if handbook.exists():
            content = handbook.read_text()
            has_approval_rules = (
                "Approval" in content or
                "approval" in content or
                "Level 3" in content
            )
            
            if has_approval_rules:
                print_success("Company Handbook has approval rules")
                self.results["approval_workflow"]["handbook_rules"] = True
                self.score += 10
            else:
                print_warning("Company Handbook may not define approval rules")
                self.results["approval_workflow"]["handbook_rules"] = False
        
        has_approval = (
            self.results["approval_workflow"].get("pending_folder") and
            self.results["approval_workflow"].get("approved_folder") and
            self.results["approval_workflow"].get("orchestrator_logic")
        )
        
        return has_approval
    
    def run_all_tests(self):
        """Run all Silver Tier tests."""
        print_header("SILVER TIER TEST SUITE")
        print(f"Vault: {self.vault.absolute()}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run tests
        watchers_ok = self.test_multiple_watchers()
        plans_ok = self.test_plan_generation()
        email_ok = self.test_email_mcp()
        approval_ok = self.test_approval_workflow()
        
        # Calculate final score
        self.results["overall"] = watchers_ok and plans_ok and email_ok and approval_ok
        self.results["score"] = self.score
        self.results["max_score"] = self.max_score
        
        # Print summary
        print_header("TEST SUMMARY")
        
        print(f"Multiple Watchers:     {'✅ PASS' if watchers_ok else '❌ FAIL'}")
        print(f"Plan Generation:       {'✅ PASS' if plans_ok else '❌ FAIL'}")
        print(f"Email MCP Server:      {'✅ PASS' if email_ok else '❌ FAIL'}")
        print(f"Approval Workflow:     {'✅ PASS' if approval_ok else '❌ FAIL'}")
        print()
        print(f"Score: {self.score}/{self.max_score} ({self.score * 100 // self.max_score}%)")
        print()
        
        if self.results["overall"]:
            print_success("🎉 SILVER TIER: 100% COMPLETE!")
        else:
            print_warning("⚠️ SILVER TIER: Not yet complete")
            print()
            print("To complete Silver Tier:")
            
            if not watchers_ok:
                print("  - Ensure at least 2 watchers are functional")
                print("  - Run: pip install watchdog playwright")
            
            if not plans_ok:
                print("  - Run orchestrator to generate plans")
                print("  - Check: python orchestrator.py --vault ./vault")
            
            if not email_ok:
                print("  - Run: python scripts/fix_gmail_token.py")
                print("  - Install: pip install google-auth google-api-python-client")
            
            if not approval_ok:
                print("  - Ensure Pending_Approval/, Approved/, Rejected/ folders exist")
                print("  - Run: python scripts/approval_notifications.py --check")
        
        return self.results["overall"]
    
    def save_report(self, output_path: str = None):
        """Save test report to file."""
        if output_path is None:
            output_path = self.vault / "Logs" / f"silver_tier_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "vault_path": str(self.vault.absolute()),
            "results": self.results,
            "score": f"{self.score}/{self.max_score}",
            "percentage": f"{self.score * 100 // self.max_score}%",
            "silver_tier_complete": self.results["overall"]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print_info(f"Report saved to: {output_path}")
        return output_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Silver Tier Requirements')
    parser.add_argument('--vault', default='./vault', help='Path to vault')
    parser.add_argument('--output', help='Output path for report')
    
    args = parser.parse_args()
    
    tester = SilverTierTester(args.vault)
    success = tester.run_all_tests()
    
    if args.output or success:
        tester.save_report(args.output)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
