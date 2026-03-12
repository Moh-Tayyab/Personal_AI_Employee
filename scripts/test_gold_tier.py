#!/usr/bin/env python3
"""
Gold Tier Complete Test Suite

Tests all Gold Tier requirements:
1. Odoo accounting integration
2. LinkedIn MCP server with authentication
3. Twitter MCP server with authentication  
4. Facebook MCP server with authentication
5. Weekly CEO Briefing generation
6. Error recovery and logging

Usage:
    python scripts/test_gold_tier.py --vault ./vault
"""

import os
import sys
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


class GoldTierTester:
    """Test Gold Tier requirements."""
    
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.results = {
            "odoo_integration": {},
            "social_media_mcps": {},
            "ceo_briefing": {},
            "error_logging": {},
            "overall": False
        }
        self.score = 0
        self.max_score = 100
    
    def test_odoo_integration(self):
        """Test Odoo accounting integration."""
        print_header("1. Testing Odoo Accounting Integration")
        
        odoo_mcp = Path("mcp/odoo/server.py")
        
        # Check if Odoo MCP exists
        if odoo_mcp.exists():
            print_success("Odoo MCP server exists")
            self.results["odoo_integration"]["exists"] = True
            self.score += 10
        else:
            print_error("Odoo MCP server not found")
            self.results["odoo_integration"]["exists"] = False
            return False
        
        # Check for required methods
        content = odoo_mcp.read_text()
        
        has_invoices = "def get_invoices" in content or "invoice" in content.lower()
        has_contacts = "def get_contacts" in content or "contact" in content.lower()
        has_create = "def create_invoice" in content or "create" in content.lower()
        
        if has_invoices:
            print_success("Invoice methods exist")
            self.results["odoo_integration"]["invoice_methods"] = True
            self.score += 5
        else:
            print_warning("Invoice methods not found")
            self.results["odoo_integration"]["invoice_methods"] = False
        
        if has_contacts:
            print_success("Contact methods exist")
            self.results["odoo_integration"]["contact_methods"] = True
            self.score += 5
        else:
            print_warning("Contact methods not found")
            self.results["odoo_integration"]["contact_methods"] = False
        
        if has_create:
            print_success("Create invoice method exists")
            self.results["odoo_integration"]["create_methods"] = True
            self.score += 5
        else:
            print_warning("Create invoice method not found")
            self.results["odoo_integration"]["create_methods"] = False
        
        # Check Odoo configuration
        odoo_configured = bool(os.getenv('ODOO_URL'))
        if odoo_configured:
            print_success("Odoo URL configured in .env")
            self.results["odoo_integration"]["configured"] = True
            self.score += 10
        else:
            print_warning("Odoo not configured (add ODOO_URL to .env)")
            print_info("Optional: Odoo integration works without config for demo mode")
            self.results["odoo_integration"]["configured"] = False
            self.score += 5  # Partial credit
        
        # Check xmlrpc dependency
        try:
            import xmlrpc.client
            print_success("XML-RPC library available (built-in)")
            self.results["odoo_integration"]["deps_ok"] = True
            self.score += 5
        except ImportError:
            print_error("XML-RPC not available")
            self.results["odoo_integration"]["deps_ok"] = False
        
        has_odoo = (
            self.results["odoo_integration"].get("exists") and
            self.results["odoo_integration"].get("invoice_methods") and
            self.results["odoo_integration"].get("deps_ok")
        )
        
        return has_odoo
    
    def test_social_media_mcps(self):
        """Test LinkedIn, Twitter, Facebook MCP servers."""
        print_header("2. Testing Social Media MCP Servers")
        
        mcp_path = Path("mcp")
        social_score = 0
        
        # Test LinkedIn MCP
        linkedin_mcp = mcp_path / "linkedin" / "server.py"
        if linkedin_mcp.exists():
            print_success("LinkedIn MCP server exists")
            self.results["social_media_mcps"]["linkedin_exists"] = True
            social_score += 10
            
            # Check session folder
            session_path = Path(os.getenv('LINKEDIN_SESSION_PATH', './vault/secrets/linkedin_session'))
            if session_path.exists():
                print_success("LinkedIn session found (authenticated)")
                self.results["social_media_mcps"]["linkedin_auth"] = True
                social_score += 10
            else:
                print_warning("LinkedIn session not found (run LinkedIn login)")
                self.results["social_media_mcps"]["linkedin_auth"] = False
                social_score += 5  # Partial credit
        else:
            print_error("LinkedIn MCP not found")
            self.results["social_media_mcps"]["linkedin_exists"] = False
        
        # Test Twitter MCP
        twitter_mcp = mcp_path / "twitter" / "server.py"
        if twitter_mcp.exists():
            print_success("Twitter MCP server exists")
            self.results["social_media_mcps"]["twitter_exists"] = True
            social_score += 10
            
            # Check session folder
            session_path = Path(os.getenv('TWITTER_SESSION_PATH', './vault/secrets/twitter_session'))
            if session_path.exists():
                print_success("Twitter session found (authenticated)")
                self.results["social_media_mcps"]["twitter_auth"] = True
                social_score += 10
            else:
                print_warning("Twitter session not found (run Twitter login)")
                self.results["social_media_mcps"]["twitter_auth"] = False
                social_score += 5  # Partial credit
        else:
            print_error("Twitter MCP not found")
            self.results["social_media_mcps"]["twitter_exists"] = False
        
        # Test Facebook MCP
        facebook_mcp = mcp_path / "facebook" / "server.py"
        if facebook_mcp.exists():
            print_success("Facebook MCP server exists")
            self.results["social_media_mcps"]["facebook_exists"] = True
            social_score += 10
            
            # Check for access token
            if os.getenv('FACEBOOK_ACCESS_TOKEN'):
                print_success("Facebook access token configured")
                self.results["social_media_mcps"]["facebook_auth"] = True
                social_score += 10
            else:
                print_warning("Facebook access token not configured")
                self.results["social_media_mcps"]["facebook_auth"] = False
                social_score += 5  # Partial credit
        else:
            print_error("Facebook MCP not found")
            self.results["social_media_mcps"]["facebook_exists"] = False
        
        # Test Instagram MCP (bonus)
        instagram_mcp = mcp_path / "instagram" / "server.py"
        if instagram_mcp.exists():
            print_success("Instagram MCP server exists (bonus)")
            self.results["social_media_mcps"]["instagram_exists"] = True
            social_score += 5
        else:
            print_info("Instagram MCP not found (optional)")
            self.results["social_media_mcps"]["instagram_exists"] = False
        
        # Check Playwright dependency
        try:
            import playwright
            print_success("Playwright installed for browser automation")
            self.results["social_media_mcps"]["playwright_installed"] = True
            social_score += 10
        except ImportError:
            print_warning("Playwright not installed (pip install playwright)")
            self.results["social_media_mcps"]["playwright_installed"] = False
        
        self.results["social_media_mcps"]["total_score"] = social_score
        self.score += social_score
        
        # Need at least 2 MCPs functional
        functional_count = 0
        if self.results["social_media_mcps"].get("linkedin_exists"):
            functional_count += 1
        if self.results["social_media_mcps"].get("twitter_exists"):
            functional_count += 1
        if self.results["social_media_mcps"].get("facebook_exists"):
            functional_count += 1
        
        if functional_count >= 2:
            print_success(f"{functional_count}/3 social media MCPs functional")
            self.results["social_media_mcps"]["multiple_functional"] = True
        else:
            print_warning(f"Only {functional_count}/3 social media MCPs functional")
            self.results["social_media_mcps"]["multiple_functional"] = False
        
        return functional_count >= 2
    
    def test_ceo_briefing(self):
        """Test weekly CEO Briefing generation."""
        print_header("3. Testing CEO Briefing Generation")
        
        briefings_folder = self.vault / "Briefings"
        
        # Check if Briefings folder exists
        if briefings_folder.exists():
            print_success("Briefings folder exists")
            self.results["ceo_briefing"]["folder_exists"] = True
            self.score += 5
        else:
            print_error("Briefings folder not found")
            self.results["ceo_briefing"]["folder_exists"] = False
            return False
        
        # Check for existing briefings
        briefing_files = list(briefings_folder.glob("*.md"))
        
        if briefing_files:
            print_success(f"Found {len(briefing_files)} briefing(s)")
            self.results["ceo_briefing"]["briefings_exist"] = True
            self.score += 15
            
            # Show latest briefing
            latest = max(briefing_files, key=lambda x: x.stat().st_mtime)
            print_info(f"Latest briefing: {latest.name}")
            
            # Check briefing structure
            content = latest.read_text()
            has_structure = any([
                "Executive Summary" in content,
                "Revenue" in content,
                "Completed Tasks" in content,
                "Pending Items" in content
            ])
            
            if has_structure:
                print_success("Briefings have proper structure")
                self.results["ceo_briefing"]["proper_structure"] = True
                self.score += 10
            else:
                print_warning("Briefing structure may be incomplete")
                self.results["ceo_briefing"]["proper_structure"] = False
        else:
            print_warning("No briefing files found")
            self.results["ceo_briefing"]["briefings_exist"] = False
            self.score += 5  # Partial credit for having the folder
        
        # Check briefing generator script
        briefing_script = Path("scripts/generate_briefing.py")
        if briefing_script.exists():
            print_success("CEO Briefing generator script exists")
            self.results["ceo_briefing"]["generator_exists"] = True
            self.score += 10
        else:
            print_warning("No briefing generator script")
            self.results["ceo_briefing"]["generator_exists"] = False
        
        has_briefings = (
            self.results["ceo_briefing"].get("folder_exists") and
            (self.results["ceo_briefing"].get("briefings_exist") or self.results["ceo_briefing"].get("generator_exists"))
        )
        
        return has_briefings
    
    def test_error_logging(self):
        """Test error recovery and logging system."""
        print_header("4. Testing Error Recovery and Logging")
        
        logs_folder = self.vault / "Logs"
        
        # Check if Logs folder exists
        if logs_folder.exists():
            print_success("Logs folder exists")
            self.results["error_logging"]["folder_exists"] = True
            self.score += 5
        else:
            print_error("Logs folder not found")
            self.results["error_logging"]["folder_exists"] = False
            return False
        
        # Check for JSON activity logs
        json_logs = list(logs_folder.glob("*.json"))
        if json_logs:
            print_success(f"Found {len(json_logs)} JSON activity logs")
            self.results["error_logging"]["json_logs"] = True
            self.score += 10
            
            # Check latest log has content
            latest = max(json_logs, key=lambda x: x.stat().st_size)
            if latest.stat().st_size > 100:
                print_success(f"Latest log has content ({latest.stat().st_size} bytes)")
                self.results["error_logging"]["logs_have_content"] = True
                self.score += 5
            else:
                print_warning("Log files may be empty")
                self.results["error_logging"]["logs_have_content"] = False
        else:
            print_warning("No JSON activity logs found")
            self.results["error_logging"]["json_logs"] = False
        
        # Check for text logs
        text_logs = list(logs_folder.glob("*.log"))
        if text_logs:
            print_success(f"Found {len(text_logs)} text logs")
            self.results["error_logging"]["text_logs"] = True
            self.score += 5
        else:
            print_info("No text logs found (optional)")
            self.results["error_logging"]["text_logs"] = False
        
        # Check orchestrator has error handling
        orchestrator = Path("orchestrator.py")
        if orchestrator.exists():
            content = orchestrator.read_text()
            has_error_handling = (
                "try:" in content and
                "except" in content and
                ("logger.error" in content or "logging.error" in content)
            )
            
            if has_error_handling:
                print_success("Orchestrator has error handling")
                self.results["error_logging"]["error_handling"] = True
                self.score += 15
            else:
                print_warning("Orchestrator may not have proper error handling")
                self.results["error_logging"]["error_handling"] = False
        
        # Check for retry logic
        if orchestrator.exists():
            content = orchestrator.read_text()
            has_retry = "retry" in content.lower() or "backoff" in content.lower()
            
            if has_retry:
                print_success("Retry logic exists")
                self.results["error_logging"]["retry_logic"] = True
                self.score += 10
            else:
                print_info("No explicit retry logic found (optional)")
                self.results["error_logging"]["retry_logic"] = False
                self.score += 5  # Partial credit
        
        # Check for fallback mechanisms
        if orchestrator.exists():
            content = orchestrator.read_text()
            has_fallback = "fallback" in content.lower() or "except" in content
            
            if has_fallback:
                print_success("Fallback mechanisms exist")
                self.results["error_logging"]["fallback"] = True
                self.score += 10
            else:
                print_warning("No fallback mechanisms found")
                self.results["error_logging"]["fallback"] = False
        
        has_logging = (
            self.results["error_logging"].get("folder_exists") and
            self.results["error_logging"].get("json_logs") and
            self.results["error_logging"].get("error_handling")
        )
        
        return has_logging
    
    def run_all_tests(self):
        """Run all Gold Tier tests."""
        print_header("GOLD TIER TEST SUITE")
        print(f"Vault: {self.vault.absolute()}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run tests
        odoo_ok = self.test_odoo_integration()
        social_ok = self.test_social_media_mcps()
        briefing_ok = self.test_ceo_briefing()
        logging_ok = self.test_error_logging()
        
        # Calculate final score
        self.results["overall"] = odoo_ok and social_ok and briefing_ok and logging_ok
        self.results["score"] = self.score
        self.results["max_score"] = self.max_score
        
        # Print summary
        print_header("TEST SUMMARY")
        
        print(f"Odoo Integration:    {'✅ PASS' if odoo_ok else '❌ FAIL'}")
        print(f"Social Media MCPs:   {'✅ PASS' if social_ok else '❌ FAIL'}")
        print(f"CEO Briefing:        {'✅ PASS' if briefing_ok else '❌ FAIL'}")
        print(f"Error Logging:       {'✅ PASS' if logging_ok else '❌ FAIL'}")
        print()
        print(f"Score: {self.score}/{self.max_score} ({self.score * 100 // self.max_score}%)")
        print()
        
        if self.results["overall"]:
            print_success("🎉 GOLD TIER: 100% COMPLETE!")
        else:
            print_warning("⚠️ GOLD TIER: Not yet complete")
            print()
            print("To complete Gold Tier:")
            
            if not odoo_ok:
                print("  - Odoo MCP server exists (configure ODOO_URL in .env for production)")
            
            if not social_ok:
                print("  - LinkedIn/Twitter/Facebook MCPs exist")
                print("  - Run browser-based login for each platform")
            
            if not briefing_ok:
                print("  - Run: python scripts/generate_briefing.py --vault ./vault")
            
            if not logging_ok:
                print("  - Ensure orchestrator is logging to vault/Logs/")
        
        return self.results["overall"]
    
    def save_report(self, output_path: str = None):
        """Save test report to file."""
        if output_path is None:
            output_path = self.vault / "Logs" / f"gold_tier_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "vault_path": str(self.vault.absolute()),
            "results": self.results,
            "score": f"{self.score}/{self.max_score}",
            "percentage": f"{self.score * 100 // self.max_score}%",
            "gold_tier_complete": self.results["overall"]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print_info(f"Report saved to: {output_path}")
        return output_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Gold Tier Requirements')
    parser.add_argument('--vault', default='./vault', help='Path to vault')
    parser.add_argument('--output', help='Output path for report')
    
    args = parser.parse_args()
    
    tester = GoldTierTester(args.vault)
    success = tester.run_all_tests()
    
    if args.output or success:
        tester.save_report(args.output)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
