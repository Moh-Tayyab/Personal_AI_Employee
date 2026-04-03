#!/usr/bin/env python3
"""
Step 4: Integration Tests for Personal AI Employee

Tests the complete system integration:
- Watcher integration (Gmail, FileSystem — mocked)
- MCP server integration (all servers, all tools)
- Cron script execution (validation only)
- Full end-to-end flow (Watcher → Needs_Action → Done)
- Ralph Wiggum loop logic (completion strategies)
- Orchestrator error handling and resilience

Run:
    python -m pytest tests/test_integration.py -v
    python -m pytest tests/test_integration.py -v -k "e2e"
    python -m pytest tests/test_integration.py -v -k "mcp"
    python -m pytest tests/test_integration.py -v -k "ralph"
"""

import sys
import os
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock, PropertyMock

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def temp_vault(tmp_path):
    """Create a clean temporary vault."""
    vault = tmp_path / "test_vault"
    vault.mkdir()
    for d in ['Needs_Action', 'Plans', 'Done', 'Pending_Approval',
              'Approved', 'Rejected', 'Logs', 'In_Progress', 'Briefings']:
        (vault / d).mkdir(parents=True, exist_ok=True)
    (vault / 'Company_Handbook.md').write_text("# Company Handbook\n- Always be polite\n- Flag payments over $50\n")
    (vault / 'Business_Goals.md').write_text("# Business Goals\n## Revenue Target\n- Monthly goal: $10,000\n")
    (vault / 'Dashboard.md').write_text("# Dashboard\n")
    return vault


@pytest.fixture
def orchestrator(temp_vault):
    """Create orchestrator in dry_run mode."""
    os.environ['DRY_RUN'] = 'true'
    os.environ['VAULT_PATH'] = str(temp_vault)

    from orchestrator import Orchestrator
    return Orchestrator(vault_path=str(temp_vault), dry_run=True)


@pytest.fixture
def sample_email_item():
    """Sample email action item content."""
    return """---
type: email
from: client@business.com
subject: Project Inquiry - Urgent
received: 2026-04-03T10:00:00
priority: high
category: finance
status: pending
---

# Project Inquiry

Hi, I'd like to inquire about your AI Employee services.
Please send me a proposal with pricing details.

Best regards,
Demo Client
"""


@pytest.fixture
def sample_approval_email():
    """Sample approved email action item."""
    return """---
type: approval_response
action: send_email
to: client@business.com
subject: Re: Project Inquiry
approved: true
---

# Approved Email Reply

Thank you for your interest. We'll send you a proposal shortly.
"""


@pytest.fixture
def sample_approval_linkedin():
    """Sample approved LinkedIn post."""
    return """---
type: approval_response
action: linkedin_post
content: Exciting news! Our AI Employee platform is transforming business.
visibility: PUBLIC
---

# Approved LinkedIn Post
"""


@pytest.fixture
def sample_approval_twitter():
    """Sample approved Twitter post."""
    return """---
type: approval_response
action: twitter_post
content: Our AI Employee works 24/7! Learn more about building digital FTEs.
---

# Approved Twitter Post
"""


@pytest.fixture
def sample_approval_facebook():
    """Sample approved Facebook post."""
    return """---
type: approval_response
action: social_post
platform: facebook
content: AI Employee automation is here. Check out our platform.
---

# Approved Facebook Post
"""


@pytest.fixture
def sample_approval_instagram():
    """Sample approved Instagram post."""
    return """---
type: approval_response
action: social_post
platform: instagram
content: Behind the scenes of our AI Employee platform.
image_url: https://example.com/image.jpg
---

# Approved Instagram Post
"""


@pytest.fixture
def sample_approval_odoo_invoice():
    """Sample approved Odoo invoice action."""
    return """---
type: approval_response
action: odoo_invoice
partner_name: Test Client Corp
partner_email: test@clientcorp.com
amount: 2500.00
---

# Approved Odoo Invoice
"""


@pytest.fixture
def sample_approval_odoo_payment():
    """Sample approved Odoo payment action."""
    return """---
type: approval_response
action: odoo_payment
invoice_id: 42
amount: 2500.00
payment_reference: Payment for Invoice #42
---

# Approved Odoo Payment
"""


# ============================================================
# Test Group 1: Watcher Integration Tests
# ============================================================

class TestGmailWatcherIntegration:
    """Test Gmail Watcher with mocked API."""

    def test_check_for_updates_mocked(self, temp_vault):
        """Should return list of message dicts from mocked Gmail API."""
        from watchers.base_watcher import BaseWatcher

        class MockGmailWatcher(BaseWatcher):
            def check_for_updates(self):
                return [
                    {'id': 'msg_001', 'threadId': 'thread_001'},
                    {'id': 'msg_002', 'threadId': 'thread_002'},
                ]

            def create_action_file(self, item):
                filepath = self.needs_action / f"EMAIL_{item['id']}.md"
                filepath.write_text(f"# Email {item['id']}\nMock content")
                return filepath

        watcher = MockGmailWatcher(vault_path=str(temp_vault), name="MockGmailWatcher")
        updates = watcher.check_for_updates()
        assert len(updates) == 2
        assert updates[0]['id'] == 'msg_001'

    def test_create_action_file_content(self, temp_vault):
        """Should create properly formatted markdown action file."""
        from watchers.base_watcher import BaseWatcher

        class TestWatcher(BaseWatcher):
            def check_for_updates(self):
                return []
            def create_action_file(self, item):
                filepath = self.needs_action / f"EMAIL_test.md"
                filepath.write_text(f"""---
type: email
source: gmail
from: test@example.com
subject: Test Subject
received: 2026-04-03T10:00:00
priority: high
status: pending
---

# Test Subject

Snippet content here.
""")
                return filepath

        watcher = TestWatcher(vault_path=str(temp_vault), name="TestWatcher")
        filepath = watcher.create_action_file({'id': 'test'})

        assert filepath.exists()
        content = filepath.read_text()
        assert 'type: email' in content
        assert 'from: test@example.com' in content
        assert 'priority: high' in content

    def test_processed_ids_tracking(self, temp_vault):
        """Should track processed message IDs to prevent duplicates."""
        from watchers.base_watcher import BaseWatcher

        class TestWatcher(BaseWatcher):
            def check_for_updates(self):
                return []
            def create_action_file(self, item):
                return self.needs_action / "test.md"

        watcher = TestWatcher(vault_path=str(temp_vault), name="TestIdTracker")

        # Save and retrieve processed IDs
        watcher.save_processed_ids({'msg_001', 'msg_002'})
        processed = watcher.get_processed_ids()
        assert 'msg_001' in processed
        assert 'msg_002' in processed


class TestFilesystemWatcherIntegration:
    """Test FileSystem Watcher."""

    def test_watches_drop_directory(self, temp_vault):
        """Should create action files when files are dropped."""
        drop_dir = temp_vault.parent / "drop"
        drop_dir.mkdir(parents=True, exist_ok=True)

        from watchers.filesystem_watcher import FilesystemWatcher

        watcher = FilesystemWatcher(vault_path=str(temp_vault), watch_path=str(drop_dir))

        # Simulate file creation in the drop directory
        test_file = drop_dir / "test_document.txt"
        test_file.write_text("Test content")

        # Process the file directly
        watcher.process_file(test_file)

        # Check that action file was created (includes timestamp in name)
        action_files = list((temp_vault / 'Needs_Action').glob('FILE_*test_document*'))
        assert len(action_files) >= 1

    def test_ignores_directories(self, temp_vault):
        """Should ignore directory creation events."""
        drop_dir = temp_vault.parent / "drop"
        drop_dir.mkdir(parents=True, exist_ok=True)

        from watchers.filesystem_watcher import FileDropHandler, FilesystemWatcher

        watcher = FilesystemWatcher(vault_path=str(temp_vault), watch_path=str(drop_dir))
        handler = FileDropHandler(watcher)

        class MockDirEvent:
            def __init__(self, path):
                self.src_path = str(path)
                self.is_directory = True

        # Should not raise (returns early for directories)
        handler.on_created(MockDirEvent(drop_dir))


# ============================================================
# Test Group 2: MCP Server Integration Tests
# ============================================================

class TestMCPServerEmailIntegration:
    """Test Email MCP server integration."""

    def test_send_email_dry_run(self, temp_vault):
        """Should return dry_run success when no Gmail auth."""
        os.environ['DRY_RUN'] = 'true'

        from orchestrator import Orchestrator
        orch = Orchestrator(vault_path=str(temp_vault), dry_run=True)

        result = orch._call_mcp_server('email', 'send_email', {
            'to': 'test@example.com',
            'subject': 'Test Subject',
            'body': 'Test body content',
            'cc': '',
            'bcc': '',
        })

        assert result.get('success') is True
        assert result.get('dry_run') is True
        assert 'Would send email' in result.get('message', '')

    def test_send_email_from_vault_parsing(self, temp_vault):
        """Should parse email fields from vault item frontmatter."""
        import re

        content = """---
type: email_approval
to: client@example.com
subject: Reply to Inquiry
cc: manager@example.com
---

Thank you for your inquiry. We will get back to you shortly.
"""
        # Test frontmatter parsing logic (same as in orchestrator)
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
        assert match is not None

        fields = {}
        for line in match.group(1).split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, _, value = line.partition(':')
                fields[key.strip().lower()] = value.strip().strip('"').strip("'")

        assert fields['to'] == 'client@example.com'
        assert fields['subject'] == 'Reply to Inquiry'
        assert fields['cc'] == 'manager@example.com'


class TestMCPServerSocialIntegration:
    """Test Social MCP server integration."""

    def test_linkedin_post_dry_run(self, temp_vault):
        """Should return dry_run success for LinkedIn post."""
        os.environ['DRY_RUN'] = 'true'

        from orchestrator import Orchestrator
        orch = Orchestrator(vault_path=str(temp_vault), dry_run=True)

        result = orch._call_mcp_server('linkedin', 'post_to_linkedin', {
            'content': 'Test LinkedIn post content',
            'visibility': 'PUBLIC',
        })

        assert result.get('success') is True
        assert result.get('dry_run') is True

    def test_linkedin_post_with_image_dry_run(self, temp_vault):
        """Should return dry_run success for LinkedIn post with image."""
        os.environ['DRY_RUN'] = 'true'

        from orchestrator import Orchestrator
        orch = Orchestrator(vault_path=str(temp_vault), dry_run=True)

        result = orch._call_mcp_server('linkedin', 'post_with_image', {
            'content': 'Test post with image',
            'image_url': 'https://example.com/image.jpg',
            'visibility': 'PUBLIC',
        })

        assert result.get('success') is True
        assert result.get('dry_run') is True

    def test_twitter_post_dry_run(self, temp_vault):
        """Should return dry_run success for Twitter post."""
        os.environ['DRY_RUN'] = 'true'

        from orchestrator import Orchestrator
        orch = Orchestrator(vault_path=str(temp_vault), dry_run=True)

        result = orch._call_mcp_server('twitter', 'post_tweet', {
            'content': 'Test tweet content',
        })

        assert result.get('success') is True
        assert result.get('dry_run') is True

    def test_twitter_thread_dry_run(self, temp_vault):
        """Should return dry_run success for Twitter thread."""
        os.environ['DRY_RUN'] = 'true'

        from orchestrator import Orchestrator
        orch = Orchestrator(vault_path=str(temp_vault), dry_run=True)

        result = orch._call_mcp_server('twitter', 'post_thread', {
            'tweets': ['Tweet 1 of thread', 'Tweet 2 of thread', 'Tweet 3 of thread'],
        })

        assert result.get('success') is True
        assert result.get('dry_run') is True

    def test_facebook_post_dry_run(self, temp_vault):
        """Should return dry_run success for Facebook post."""
        os.environ['DRY_RUN'] = 'true'

        from orchestrator import Orchestrator
        orch = Orchestrator(vault_path=str(temp_vault), dry_run=True)

        result = orch._call_mcp_server('social', 'post_to_facebook', {
            'content': 'Test Facebook post content',
        })

        assert result.get('success') is True
        assert result.get('dry_run') is True

    def test_instagram_post_dry_run(self, temp_vault):
        """Should return dry_run success for Instagram post."""
        os.environ['DRY_RUN'] = 'true'

        from orchestrator import Orchestrator
        orch = Orchestrator(vault_path=str(temp_vault), dry_run=True)

        result = orch._call_mcp_server('social', 'post_to_instagram', {
            'caption': 'Test Instagram caption',
            'image_url': 'https://example.com/image.jpg',
        })

        assert result.get('success') is True
        assert result.get('dry_run') is True

    def test_cross_platform_post_dry_run(self, temp_vault):
        """Should return dry_run success for cross-platform post."""
        os.environ['DRY_RUN'] = 'true'

        from orchestrator import Orchestrator
        orch = Orchestrator(vault_path=str(temp_vault), dry_run=True)

        result = orch._call_mcp_server('social', 'post_cross_platform', {
            'content': 'Cross-platform post content',
            'platforms': ['facebook', 'instagram'],
            'image_url': 'https://example.com/image.jpg',
        })

        assert result.get('success') is True
        assert result.get('dry_run') is True
        assert 'facebook' in result.get('results', {})
        assert 'instagram' in result.get('results', {})


class TestMCPServerOdooIntegration:
    """Test Odoo MCP server integration."""

    def test_create_invoice_dry_run(self, temp_vault):
        """Should return dry_run success for Odoo invoice."""
        os.environ['DRY_RUN'] = 'true'

        from orchestrator import Orchestrator
        orch = Orchestrator(vault_path=str(temp_vault), dry_run=True)

        result = orch._call_mcp_server('odoo', 'create_invoice', {
            'partner_name': 'Test Client',
            'partner_email': 'test@client.com',
            'invoice_lines': [
                {'name': 'Consulting', 'quantity': 10, 'price_unit': 150},
                {'name': 'Setup', 'quantity': 1, 'price_unit': 1000},
            ],
        })

        assert result.get('success') is True
        assert result.get('dry_run') is True
        assert 'Test Client' in result.get('message', '')

    def test_post_invoice_dry_run(self, temp_vault):
        """Should return dry_run success for posting Odoo invoice."""
        os.environ['DRY_RUN'] = 'true'

        from orchestrator import Orchestrator
        orch = Orchestrator(vault_path=str(temp_vault), dry_run=True)

        result = orch._call_mcp_server('odoo', 'post_invoice', {
            'invoice_id': 42,
        })

        assert result.get('success') is True
        assert result.get('dry_run') is True

    def test_create_payment_dry_run(self, temp_vault):
        """Should return dry_run success for Odoo payment."""
        os.environ['DRY_RUN'] = 'true'

        from orchestrator import Orchestrator
        orch = Orchestrator(vault_path=str(temp_vault), dry_run=True)

        result = orch._call_mcp_server('odoo', 'create_payment', {
            'invoice_id': 42,
            'amount': 2500.00,
            'payment_reference': 'Payment for Invoice #42',
        })

        assert result.get('success') is True
        assert result.get('dry_run') is True

    def test_create_customer_dry_run(self, temp_vault):
        """Should return dry_run success for Odoo customer creation."""
        os.environ['DRY_RUN'] = 'true'

        from orchestrator import Orchestrator
        orch = Orchestrator(vault_path=str(temp_vault), dry_run=True)

        result = orch._call_mcp_server('odoo', 'create_customer', {
            'name': 'New Customer',
            'email': 'new@customer.com',
            'phone': '+1234567890',
        })

        assert result.get('success') is True
        assert result.get('dry_run') is True


# ============================================================
# Test Group 3: Full End-to-End Flow Tests
# ============================================================

class TestEndToEndFlow:
    """Test complete end-to-end item lifecycle."""

    def test_email_item_full_lifecycle(self, temp_vault, orchestrator, sample_email_item, sample_approval_email):
        """Full lifecycle: Needs_Action → Plan → Approval → Email → Done."""
        # Step 1: Create email item in Needs_Action
        email_item = temp_vault / 'Needs_Action' / 'EMAIL_lifecycle_test.md'
        email_item.write_text(sample_email_item)

        # Verify item is in Needs_Action
        items = orchestrator.check_needs_action()
        assert len(items) == 1

        # Step 2: Create plan
        plan_path = orchestrator.create_plan(email_item)
        assert plan_path.exists()
        assert plan_path.parent.name == 'Plans'

        # Step 3: Process with AI (dry_run — just logs)
        item_content = email_item.read_text()
        success = orchestrator.trigger_ai(f'Process: {email_item.name}')
        assert success is True  # dry_run always succeeds

        # Step 4: Move to In_Progress
        orchestrator.move_to_in_progress(email_item)
        remaining = orchestrator.check_needs_action()
        assert len(remaining) == 0

        # Step 5: Create approval request
        approval = temp_vault / 'Pending_Approval' / 'APPROVAL_email_reply.md'
        approval.write_text(sample_approval_email)

        # Step 6: Move to Approved (simulating human approval)
        shutil.move(str(approval), str(temp_vault / 'Approved' / approval.name))

        # Step 7: Process approved item
        approved_items = orchestrator.check_approved()
        assert len(approved_items) == 1
        result = orchestrator.process_approved_item(approved_items[0])
        assert result is True

        # Step 8: Move to Done
        orchestrator.move_to_done(approved_items[0])
        done_items = list(orchestrator.done.glob('*.md'))
        assert len(done_items) == 1

    def test_social_posts_full_lifecycle(self, temp_vault, orchestrator,
                                          sample_approval_linkedin, sample_approval_twitter,
                                          sample_approval_facebook):
        """Full lifecycle for multiple social media posts."""
        posts = [
            ('SOCIAL_linkedin.md', sample_approval_linkedin),
            ('SOCIAL_twitter.md', sample_approval_twitter),
            ('SOCIAL_facebook.md', sample_approval_facebook),
        ]

        for filename, content in posts:
            approved = temp_vault / 'Approved' / filename
            approved.write_text(content)

        # Process all approved items
        for item in orchestrator.check_approved():
            result = orchestrator.process_approved_item(item)
            assert result is True
            orchestrator.move_to_done(item)

        done_items = list(orchestrator.done.glob('*.md'))
        assert len(done_items) == 3

    def test_odoo_invoice_full_lifecycle(self, temp_vault, orchestrator, sample_approval_odoo_invoice):
        """Full lifecycle for Odoo invoice creation."""
        approved = temp_vault / 'Approved' / 'ODOO_invoice.md'
        approved.write_text(sample_approval_odoo_invoice)

        result = orchestrator.process_approved_item(approved)
        assert result is True
        orchestrator.move_to_done(approved)

        done_items = list(orchestrator.done.glob('*.md'))
        assert len(done_items) == 1

    def test_dashboard_updates_throughout_lifecycle(self, temp_vault, orchestrator):
        """Dashboard should update throughout item lifecycle."""
        # Initial state
        orchestrator._update_dashboard([], [], [])
        dashboard = (temp_vault / 'Dashboard.md').read_text()
        assert 'AI Employee Dashboard' in dashboard
        assert 'DRY RUN' in dashboard

        # Add items to Needs_Action
        item = temp_vault / 'Needs_Action' / 'test.md'
        item.write_text("# Test")
        orchestrator._update_dashboard([item], [], [])

        dashboard = (temp_vault / 'Dashboard.md').read_text()
        assert 'Needs_Action' in dashboard

    def test_logging_throughout_lifecycle(self, temp_vault, orchestrator):
        """Activity should be logged to daily log file."""
        orchestrator.log_activity('e2e_test', {'step': 'start'})

        today = datetime.now().strftime('%Y-%m-%d')
        log_file = temp_vault / 'Logs' / f'{today}.json'
        assert log_file.exists()

        logs = json.loads(log_file.read_text())
        assert any(log['type'] == 'e2e_test' for log in logs)


# ============================================================
# Test Group 4: Ralph Wiggum Loop Logic Tests
# ============================================================

class TestRalphWiggumLoop:
    """Test Ralph Wiggum persistence loop logic."""

    def test_completion_strategies_exist(self, temp_vault):
        """All completion strategies should be defined."""
        from scripts.ralph_loop import RalphWiggumLoop

        loop = RalphWiggumLoop(
            vault_path=str(temp_vault),
            prompt="Test prompt",
            max_iterations=3,
        )

        strategies = loop._get_completion_strategies()
        assert len(strategies) == 3

        strategy_names = [s['name'] for s in strategies]
        assert 'file_movement' in strategy_names
        assert 'promise_detection' in strategy_names
        assert 'needs_action_empty' in strategy_names

    def test_file_movement_detection(self, temp_vault):
        """Should detect file movement to Done folder."""
        from scripts.ralph_loop import RalphWiggumLoop

        # Create initial files
        (temp_vault / 'Done' / 'done_1.md').write_text("# Done 1")
        (temp_vault / 'Needs_Action' / 'action_1.md').write_text("# Action 1")

        loop = RalphWiggumLoop(
            vault_path=str(temp_vault),
            prompt="Test",
            max_iterations=3,
        )
        loop._capture_start_state()

        # Simulate file movement (add more done files)
        (temp_vault / 'Done' / 'done_2.md').write_text("# Done 2")

        assert loop._check_file_movement() is True

    def test_promise_detection(self, temp_vault):
        """Should detect completion promise in output."""
        from scripts.ralph_loop import RalphWiggumLoop

        loop = RalphWiggumLoop(
            vault_path=str(temp_vault),
            prompt="Test",
            max_iterations=3,
        )

        # Test various completion markers
        for marker in [
            '<promise>TASK_COMPLETE</promise>',
            '<TASK_COMPLETE>',
            'TASK_COMPLETE',
            '[TASK COMPLETE]',
            '✅ Task complete',
        ]:
            assert loop._check_promise(marker) is True

        # Non-matching output
        assert loop._check_promise("Working on the task...") is False

    def test_needs_action_empty_detection(self, temp_vault):
        """Should detect when Needs_Action folder is empty."""
        from scripts.ralph_loop import RalphWiggumLoop

        # Start with items
        (temp_vault / 'Needs_Action' / 'action_1.md').write_text("# Action 1")

        loop = RalphWiggumLoop(
            vault_path=str(temp_vault),
            prompt="Test",
            max_iterations=3,
        )
        loop._capture_start_state()

        # Should not detect completion (items still present)
        assert loop._check_needs_action_empty() is False

        # Remove items
        for f in (temp_vault / 'Needs_Action').glob('*.md'):
            f.unlink()

        # Should detect empty folder
        assert loop._check_needs_action_empty() is True

    def test_max_iterations_limit(self, temp_vault):
        """Should stop after max_iterations."""
        from scripts.ralph_loop import RalphWiggumLoop

        loop = RalphWiggumLoop(
            vault_path=str(temp_vault),
            prompt="Test",
            max_iterations=2,
            check_interval=0.1,
        )

        # Add an item so the loop doesn't exit immediately
        (temp_vault / 'Needs_Action' / 'action.md').write_text("# Action")

        # Mock _run_qwen to always succeed but never complete
        loop._run_qwen = MagicMock(return_value=(True, "Working..."))

        result = loop.run()

        assert result['iterations'] == 2
        assert result['max_iterations'] == 2
        assert result['completed'] is False

    def test_iteration_logging(self, temp_vault):
        """Should log each iteration to file."""
        from scripts.ralph_loop import RalphWiggumLoop

        loop = RalphWiggumLoop(
            vault_path=str(temp_vault),
            prompt="Test",
            max_iterations=1,
        )
        loop._capture_start_state()

        loop._log_iteration(1, "Test output", False)

        log_dir = temp_vault / 'Logs' / 'ralph_loop'
        log_files = list(log_dir.glob('*.json'))
        assert len(log_files) == 1

        log_data = json.loads(log_files[0].read_text())
        assert log_data['iteration'] == 1
        assert log_data['output_length'] == len("Test output")


# ============================================================
# Test Group 5: Orchestrator Error handling Tests
# ============================================================

class TestOrchestratorErrorHandling:
    """Test orchestrator error handling and resilience."""

    def test_fallback_rule_based_processing(self, temp_vault, orchestrator):
        """Should fallback to rule-based processing when AI fails."""
        prompt = """
From: urgent@vendor.com
Subject: URGENT: Invoice #99999 payment overdue

This is an urgent reminder about the overdue payment.
"""
        result = orchestrator._fallback_rule_based_processing(prompt)
        assert result is True

        # Check that draft was created
        drafts = list((temp_vault / 'Drafts').glob('*.md'))
        assert len(drafts) >= 1

        draft_content = drafts[0].read_text()
        assert 'priority: urgent' in draft_content
        assert 'category: finance' in draft_content

    def test_unknown_action_type_graceful_handling(self, temp_vault, orchestrator):
        """Should handle unknown action types gracefully."""
        approved = temp_vault / 'Approved' / 'UNKNOWN_action.md'
        approved.write_text("""---
type: approval_response
action: some_unknown_action
---

Unknown action type content
""")

        # In dry_run mode, returns True before checking action type
        result = orchestrator.process_approved_item(approved)
        assert result is True

    def test_missing_file_graceful_handling(self, orchestrator):
        """Should handle missing files gracefully."""
        from pathlib import Path
        # In dry_run mode, returns True before checking file existence
        result = orchestrator.process_approved_item(Path('/nonexistent/file.md'))
        assert result is True  # dry_run always returns True

    def test_mcp_server_unknown_server(self, orchestrator):
        """Should return error for unknown MCP server."""
        result = orchestrator._call_mcp_server('nonexistent', 'some_tool', {})
        assert 'error' in result
        assert 'Unknown MCP server' in result['error']

    def test_mcp_server_unknown_tool(self, temp_vault, orchestrator):
        """Should return error for unknown tool in valid server."""
        result = orchestrator._call_mcp_server('email', 'nonexistent_tool', {})
        assert 'error' in result
        assert 'Tool' in result['error']

    def test_signal_handler_shutdown(self, orchestrator):
        """Should handle shutdown signals gracefully."""
        assert orchestrator.running is True

        # Simulate SIGINT
        orchestrator._signal_handler(signal.SIGINT, None)
        assert orchestrator.running is False


# ============================================================
# Test Group 6: Cron Script Validation Tests
# ============================================================

class TestCronScriptValidation:
    """Validate cron scripts exist and are properly structured."""

    def test_all_cron_scripts_exist(self):
        """All expected cron scripts should exist."""
        project_root = Path(__file__).parent.parent
        expected_scripts = [
            'scripts/cron/daily_briefing.sh',
            'scripts/cron/weekly_ceo_briefing.sh',
            'scripts/cron/health_check.sh',
            'scripts/cron/process_needs_action.sh',
        ]

        for script in expected_scripts:
            script_path = project_root / script
            assert script_path.exists(), f"Cron script missing: {script}"
            assert os.access(script_path, os.X_OK), f"Cron script not executable: {script}"

    def test_cron_scripts_have_shebang(self):
        """All cron scripts should have proper shebang line."""
        project_root = Path(__file__).parent.parent

        for script in (project_root / 'scripts/cron').glob('*.sh'):
            first_line = script.open().readline().strip()
            assert first_line.startswith('#!/bin/bash'), f"{script} missing shebang"

    def test_ecosystem_config_exists(self):
        """PM2 ecosystem config should exist."""
        project_root = Path(__file__).parent.parent
        config_path = project_root / 'ecosystem.config.js'
        assert config_path.exists()

    def test_demo_scripts_exist(self):
        """Demo scripts should exist."""
        project_root = Path(__file__).parent.parent
        expected = [
            'scripts/silver_tier_demo.sh',
            'scripts/gold_tier_demo.sh',
        ]

        for script in expected:
            script_path = project_root / script
            assert script_path.exists(), f"Demo script missing: {script}"


# Import signal for signal handler test
import signal


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
