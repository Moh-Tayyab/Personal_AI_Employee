#!/usr/bin/env python3
"""
Integration Tests - Personal AI Employee

Tests the complete workflow from email receipt to action execution.

Usage:
    python tests/test_integration.py
"""

import unittest
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestClaudeIntegration(unittest.TestCase):
    """Test Claude API integration."""

    def setUp(self):
        """Set up test environment."""
        from dotenv import load_dotenv
        load_dotenv()

        self.vault_path = Path('./vault')
        os.environ['DRY_RUN'] = 'true'

    def test_orchestrator_calls_claude(self):
        """Test that orchestrator can call Claude API."""
        from orchestrator import Orchestrator

        orch = Orchestrator(str(self.vault_path), dry_run=True)

        test_prompt = """
---
type: email
from: test@example.com
subject: Test Email
---

This is a test email to verify Claude integration.
"""

        result = orch.trigger_claude(test_prompt)
        self.assertTrue(result, "Orchestrator should successfully call Claude")

    def test_claude_creates_plan(self):
        """Test that Claude creates action plans."""
        from orchestrator import Orchestrator

        orch = Orchestrator(str(self.vault_path), dry_run=False)

        # Create test email
        test_email = self.vault_path / 'Needs_Action' / 'test_integration.md'
        test_email.write_text("""---
type: email
from: test@example.com
subject: Urgent: Need Response
---

This is an urgent test email requiring immediate response.
""")

        # Process it
        result = orch.trigger_claude(test_email.read_text())

        # Check that a plan was created
        plans = list((self.vault_path / 'Plans').glob('CLAUDE_PLAN_*.md'))
        self.assertGreater(len(plans), 0, "Claude should create a plan file")

        # Clean up
        test_email.unlink(missing_ok=True)
        for plan in plans:
            plan.unlink(missing_ok=True)

class TestEmailOperations(unittest.TestCase):
    """Test email MCP server operations."""

    def setUp(self):
        """Set up test environment."""
        os.environ['DRY_RUN'] = 'true'
        os.environ['VAULT_PATH'] = './vault'

    def test_email_server_initialization(self):
        """Test email server can be initialized."""
        from mcp.email.server import EmailMCPServer

        server = EmailMCPServer()
        self.assertIsNotNone(server, "Email server should initialize")

    def test_send_email_dry_run(self):
        """Test email sending in dry-run mode."""
        from mcp.email.server import EmailMCPServer

        server = EmailMCPServer()
        result = server.send_email({
            'to': 'test@example.com',
            'subject': 'Test Email',
            'body': 'This is a test email.'
        })

        self.assertIn('status', result, "Result should have status")
        self.assertIn(result['status'], ['sent', 'dry_run', 'created'],
                     "Status should be valid")

    def test_search_emails(self):
        """Test email search functionality."""
        from mcp.email.server import EmailMCPServer

        server = EmailMCPServer()
        result = server.search_emails({
            'query': 'is:unread',
            'max_results': 5
        })

        self.assertIn('status', result, "Result should have status")
        # Status can be 'success' or 'error' (if not authenticated)
        self.assertIn(result['status'], ['success', 'error'])

    def test_draft_email(self):
        """Test email draft creation."""
        from mcp.email.server import EmailMCPServer

        server = EmailMCPServer()
        result = server.draft_email({
            'to': 'test@example.com',
            'subject': 'Test Draft',
            'body': 'This is a test draft.'
        })

        self.assertEqual(result['status'], 'created', "Draft should be created")
        self.assertIn('draft_path', result, "Result should include draft path")

        # Clean up
        draft_path = Path(result['draft_path'])
        draft_path.unlink(missing_ok=True)

class TestApprovalWorkflow(unittest.TestCase):
    """Test approval workflow."""

    def setUp(self):
        """Set up test environment."""
        self.vault_path = Path('./vault')
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'

        # Ensure folders exist
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        self.approved.mkdir(parents=True, exist_ok=True)
        self.rejected.mkdir(parents=True, exist_ok=True)

    def test_approval_notification(self):
        """Test approval notification system."""
        from orchestrator import Orchestrator

        orch = Orchestrator(str(self.vault_path), dry_run=True)

        # Create test approval item
        test_item = self.pending_approval / 'test_approval.md'
        test_item.write_text("Test approval item")

        # Test notification (should not raise exception)
        try:
            orch.notify_approval_needed(test_item, {
                'priority': 'high',
                'category': 'finance'
            })
            success = True
        except Exception as e:
            success = False
            print(f"Notification error: {e}")

        self.assertTrue(success, "Notification should not raise exception")

        # Clean up
        test_item.unlink(missing_ok=True)

    def test_move_to_done(self):
        """Test moving items to Done folder."""
        from orchestrator import Orchestrator

        orch = Orchestrator(str(self.vault_path), dry_run=True)

        # Create test item
        test_item = self.approved / 'test_done.md'
        test_item.write_text("Test item")

        # Move to done
        orch.move_to_done(test_item)

        # Check it was moved
        self.assertFalse(test_item.exists(), "Item should be moved from Approved")

        # Clean up
        done_items = list((self.vault_path / 'Done').glob('test_done_*.md'))
        for item in done_items:
            item.unlink(missing_ok=True)

class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflow."""

    def setUp(self):
        """Set up test environment."""
        from dotenv import load_dotenv
        load_dotenv()

        self.vault_path = Path('./vault')
        os.environ['DRY_RUN'] = 'false'

    def test_complete_workflow(self):
        """Test complete workflow from email to action."""
        from orchestrator import Orchestrator

        # Skip if no API key
        if not os.getenv('ANTHROPIC_API_KEY'):
            self.skipTest("ANTHROPIC_API_KEY not set")

        orch = Orchestrator(str(self.vault_path), dry_run=False)

        # 1. Create test email in Needs_Action
        test_email = self.vault_path / 'Needs_Action' / f'test_e2e_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        test_email.write_text("""---
type: email
from: test@example.com
subject: Test End-to-End Workflow
date: 2026-03-10
---

This is a test email to verify the complete workflow.

Please acknowledge receipt.
""")

        # 2. Process with Claude
        result = orch.trigger_claude(test_email.read_text())
        self.assertTrue(result, "Claude should process email")

        # 3. Check that a plan was created
        plans = list((self.vault_path / 'Plans').glob('CLAUDE_PLAN_*.md'))
        self.assertGreater(len(plans), 0, "Plan should be created")

        # 4. Check plan content
        latest_plan = max(plans, key=lambda p: p.stat().st_mtime)
        plan_content = latest_plan.read_text()
        self.assertIn('Analysis', plan_content, "Plan should contain analysis")

        # Clean up
        test_email.unlink(missing_ok=True)
        latest_plan.unlink(missing_ok=True)

def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestClaudeIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEmailOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestApprovalWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndWorkflow))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
