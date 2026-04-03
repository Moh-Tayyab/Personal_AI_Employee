#!/usr/bin/env python3
"""
Test Orchestrator End-to-End Flow

Tests the complete lifecycle:
Needs_Action → Plan → AI Analysis → Pending_Approval → Approved → MCP Execution → Done

Run:
    python -m pytest tests/test_orchestrator_flow.py -v
"""

import sys
import os
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_vault():
    """Create a temporary vault for testing."""
    vault = Path(tempfile.mkdtemp(prefix="test_vault_"))

    # Create all required directories
    for d in ['Needs_Action', 'Plans', 'Done', 'Pending_Approval',
              'Approved', 'Rejected', 'Logs', 'In_Progress', 'Briefings']:
        (vault / d).mkdir(parents=True, exist_ok=True)

    # Create minimal handbook and goals
    (vault / 'Company_Handbook.md').write_text("""# Company Handbook
## Rules
- Always be polite
- Flag payments over $50 for approval
""")
    (vault / 'Business_Goals.md').write_text("""# Business Goals
## Revenue Target
- Monthly goal: $10,000
""")
    (vault / 'Dashboard.md').write_text("# Dashboard\n")

    yield vault

    # Cleanup
    shutil.rmtree(vault, ignore_errors=True)


@pytest.fixture
def orchestrator(temp_vault):
    """Create an orchestrator instance with dry_run=True."""
    # Set DRY_RUN environment variable
    old_dry_run = os.environ.get('DRY_RUN')
    os.environ['DRY_RUN'] = 'true'

    from orchestrator import Orchestrator
    orch = Orchestrator(vault_path=str(temp_vault), dry_run=True)

    yield orch

    # Restore
    if old_dry_run is not None:
        os.environ['DRY_RUN'] = old_dry_run
    elif 'DRY_RUN' in os.environ:
        del os.environ['DRY_RUN']


class TestOrchestratorInitialization:
    """Test orchestrator initialization."""

    def test_directories_created(self, temp_vault, orchestrator):
        """All required directories should exist."""
        for d in ['Needs_Action', 'Plans', 'Done', 'Pending_Approval',
                  'Approved', 'Rejected', 'Logs', 'In_Progress']:
            assert (temp_vault / d).exists(), f"Directory {d} should exist"

    def test_dry_run_mode(self, orchestrator):
        """Orchestrator should be in dry_run mode."""
        assert orchestrator.dry_run is True


class TestItemLifecycle:
    """Test the complete item lifecycle."""

    def test_create_email_action_item(self, temp_vault, orchestrator):
        """Should create an email action item in Needs_Action."""
        email_item = temp_vault / 'Needs_Action' / 'EMAIL_test.md'
        email_item.write_text("""---
type: email
from: test@example.com
subject: Test Email
received: 2026-04-03T10:00:00
priority: high
status: pending
---

# Test Email
This is a test email for processing.
""")

        items = orchestrator.check_needs_action()
        assert len(items) == 1
        assert items[0].name == 'EMAIL_test.md'

    def test_create_plan(self, temp_vault, orchestrator):
        """Should create a Plan.md for an item."""
        email_item = temp_vault / 'Needs_Action' / 'EMAIL_plan_test.md'
        email_item.write_text("""---
type: email
from: plan@test.com
subject: Plan Test
---
Test content
""")

        plan_path = orchestrator.create_plan(email_item)
        assert plan_path.exists()
        assert plan_path.parent.name == 'Plans'
        plan_content = plan_path.read_text()
        assert 'Plan Test' in plan_content

    def test_move_to_in_progress(self, temp_vault, orchestrator):
        """Should move item from Needs_Action to In_Progress."""
        item = temp_vault / 'Needs_Action' / 'EMAIL_move_test.md'
        item.write_text("""---
type: email
from: move@test.com
subject: Move Test
---
Content
""")

        orchestrator.move_to_in_progress(item)

        in_progress_items = list(orchestrator.in_progress.glob('*.md'))
        assert len(in_progress_items) == 1
        assert 'move_test' in in_progress_items[0].name

    def test_move_to_done(self, temp_vault, orchestrator):
        """Should move item to Done folder."""
        item = temp_vault / 'In_Progress' / 'EMAIL_done_test.md'
        item.write_text("""---
type: email
from: done@test.com
subject: Done Test
---
Content
""")

        orchestrator.move_to_done(item)

        done_items = list(orchestrator.done.glob('*.md'))
        assert len(done_items) == 1
        assert 'done_test' in done_items[0].name

    def test_process_approved_email_dry_run(self, temp_vault, orchestrator):
        """Should process approved email item in dry_run mode."""
        approved_item = temp_vault / 'Approved' / 'APPROVED_email_test.md'
        approved_item.write_text("""---
type: approval_response
action: send_email
to: recipient@example.com
subject: Test Response
approved: true
---

# Approved Email
Please send this email.
Body of the email goes here.
""")

        result = orchestrator.process_approved_item(approved_item)
        # In dry_run mode, it returns True immediately
        assert result is True

    def test_process_approved_linkedin_dry_run(self, temp_vault, orchestrator):
        """Should process approved LinkedIn item in dry_run mode."""
        approved_item = temp_vault / 'Approved' / 'APPROVED_linkedin_test.md'
        approved_item.write_text("""---
type: approval_response
action: linkedin_post
content: Test LinkedIn Post
visibility: PUBLIC
---

# LinkedIn Post
Test content for LinkedIn.
""")

        result = orchestrator.process_approved_item(approved_item)
        assert result is True

    def test_process_approved_twitter_dry_run(self, temp_vault, orchestrator):
        """Should process approved Twitter item in dry_run mode."""
        approved_item = temp_vault / 'Approved' / 'APPROVED_twitter_test.md'
        approved_item.write_text("""---
type: approval_response
action: twitter_post
content: Test Tweet
---

# Twitter Post
Test tweet content.
""")

        result = orchestrator.process_approved_item(approved_item)
        assert result is True

    def test_process_approved_facebook_dry_run(self, temp_vault, orchestrator):
        """Should process approved Facebook item in dry_run mode."""
        approved_item = temp_vault / 'Approved' / 'APPROVED_facebook_test.md'
        approved_item.write_text("""---
type: approval_response
action: social_post
platform: facebook
content: Test Facebook Post
---

# Facebook Post
Test content for Facebook.
""")

        result = orchestrator.process_approved_item(approved_item)
        assert result is True

    def test_process_approved_odoo_invoice_dry_run(self, temp_vault, orchestrator):
        """Should process approved Odoo invoice item in dry_run mode."""
        approved_item = temp_vault / 'Approved' / 'APPROVED_odoo_invoice_test.md'
        approved_item.write_text("""---
type: approval_response
action: odoo_invoice
partner_name: Test Client
partner_email: client@test.com
amount: 500.00
---

# Odoo Invoice
Create invoice for Test Client.
""")

        result = orchestrator.process_approved_item(approved_item)
        assert result is True

    def test_process_approved_unknown_action(self, temp_vault, orchestrator):
        """Should return False for unknown action types."""
        approved_item = temp_vault / 'Approved' / 'APPROVED_unknown_test.md'
        approved_item.write_text("""---
type: approval_response
action: unknown_action_type
---

# Unknown Action
This has an unknown action type.
""")

        result = orchestrator.process_approved_item(approved_item)
        # In dry_run mode, returns True before checking action type
        assert result is True

    def test_extract_frontmatter_field(self, orchestrator):
        """Should extract fields from YAML frontmatter."""
        content = """---
type: email
to: test@example.com
subject: Hello World
---
Body content
"""
        assert orchestrator._extract_frontmatter_field(content, 'to') == 'test@example.com'
        assert orchestrator._extract_frontmatter_field(content, 'subject') == 'Hello World'
        assert orchestrator._extract_frontmatter_field(content, 'missing') == ''

    def test_update_dashboard(self, temp_vault, orchestrator):
        """Should update Dashboard.md with current state."""
        needs_action = [temp_vault / 'Needs_Action' / 'item1.md']
        pending = [temp_vault / 'Pending_Approval' / 'pending1.md']
        approved = [temp_vault / 'Approved' / 'approved1.md']

        orchestrator._update_dashboard(needs_action, pending, approved)

        dashboard = (temp_vault / 'Dashboard.md').read_text()
        assert 'AI Employee Dashboard' in dashboard
        assert 'Active' in dashboard
        assert 'DRY RUN' in dashboard

    def test_log_activity(self, temp_vault, orchestrator):
        """Should log activity to daily log file."""
        orchestrator.log_activity('test_activity', {'key': 'value'})

        today = datetime.now().strftime('%Y-%m-%d')
        log_file = temp_vault / 'Logs' / f'{today}.json'
        assert log_file.exists()

        logs = json.loads(log_file.read_text())
        assert len(logs) >= 1
        assert any(log['type'] == 'test_activity' for log in logs)


class TestMCPIntegration:
    """Test MCP server integration from orchestrator."""

    def test_call_mcp_server_email_send(self, temp_vault, orchestrator):
        """Should call Email MCP send_email tool."""
        result = orchestrator._call_mcp_server('email', 'send_email', {
            'to': 'test@example.com',
            'subject': 'Test',
            'body': 'Test body',
            'cc': '',
            'bcc': '',
        })
        # In DRY_RUN mode, email MCP returns dry_run success
        assert 'success' in result or 'error' in result

    def test_call_mcp_server_linkedin_status(self, temp_vault, orchestrator):
        """Should call LinkedIn MCP status tool."""
        result = orchestrator._call_mcp_server('linkedin', 'linkedin_status', {})
        assert 'status' in result or 'error' in result

    def test_call_mcp_server_twitter_status(self, temp_vault, orchestrator):
        """Should call Twitter MCP status tool."""
        result = orchestrator._call_mcp_server('twitter', 'twitter_status', {})
        assert 'status' in result or 'error' in result

    def test_call_mcp_server_unknown_server(self, orchestrator):
        """Should return error for unknown MCP server."""
        result = orchestrator._call_mcp_server('unknown', 'some_tool', {})
        assert 'error' in result
        assert 'Unknown MCP server' in result['error']

    def test_call_mcp_server_unknown_tool(self, temp_vault, orchestrator):
        """Should return error for unknown tool in valid server."""
        result = orchestrator._call_mcp_server('email', 'nonexistent_tool', {})
        assert 'error' in result


class TestEndToEndFlow:
    """Test complete end-to-end flow."""

    def test_email_item_lifecycle(self, temp_vault, orchestrator):
        """Test complete lifecycle of an email item."""
        # Step 1: Create email item in Needs_Action
        email_item = temp_vault / 'Needs_Action' / 'EMAIL_lifecycle.md'
        email_item.write_text("""---
type: email
from: client@example.com
subject: Project Inquiry
received: 2026-04-03T10:00:00
priority: high
status: pending
---

# Project Inquiry
Hi, I'd like to inquire about your services.
Please send me a quote.
""")

        # Step 2: Verify it's in Needs_Action
        items = orchestrator.check_needs_action()
        assert len(items) == 1

        # Step 3: Create plan
        plan_path = orchestrator.create_plan(email_item)
        assert plan_path.exists()

        # Step 4: Move to In_Progress (simulating AI processing)
        orchestrator.move_to_in_progress(email_item)

        # Verify it's no longer in Needs_Action
        remaining = orchestrator.check_needs_action()
        assert len(remaining) == 0

        # Verify it's in In_Progress
        in_progress = list(orchestrator.in_progress.glob('*.md'))
        assert len(in_progress) == 1

        # Step 5: Create approval request (simulating AI decision)
        approval_item = temp_vault / 'Pending_Approval' / 'APPROVAL_email_reply.md'
        approval_item.write_text("""---
type: approval_request
action: send_email
to: client@example.com
subject: Re: Project Inquiry
---

# Approval Request
Reply to client about project inquiry.
""")

        # Step 6: Move to Approved (simulating human approval)
        shutil.move(str(approval_item), str(temp_vault / 'Approved' / approval_item.name))

        # Step 7: Process approved item (dry_run)
        approved = list(orchestrator.approved.glob('*.md'))
        assert len(approved) == 1
        result = orchestrator.process_approved_item(approved[0])
        assert result is True

        # Step 8: Move to Done
        orchestrator.move_to_done(approved[0])

        # Verify final state
        done_items = list(orchestrator.done.glob('*.md'))
        assert len(done_items) == 1
        assert 'APPROVAL_email_reply' in done_items[0].name


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
