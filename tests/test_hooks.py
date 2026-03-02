"""
Tests for HTTP Hook Handlers

Run with: python -m pytest tests/test_hooks.py -v
"""

import json
import tempfile
import pytest
from pathlib import Path
from datetime import datetime

# Import hooks module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from hooks.server import HookServer, HookHandler
from hooks.handlers import (
    ApprovalHookHandler,
    StatusHookHandler,
    EmailHookHandler,
    WebhookNotifier
)


class TestApprovalHookHandler:
    """Tests for approval hook handler."""

    @pytest.fixture
    def temp_vault(self):
        """Create a temporary vault for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            for d in ['Pending_Approval', 'Approved', 'Rejected', 'Needs_Action']:
                (vault / d).mkdir(parents=True, exist_ok=True)
            yield vault

    def test_create_approval_request(self, temp_vault):
        """Test creating an approval request."""
        handler = ApprovalHookHandler(str(temp_vault))

        result = handler.create_approval_request(
            item_type='email',
            item_data={
                'summary': 'Send email to new client',
                'to': 'client@example.com',
                'subject': 'Proposal'
            },
            urgency='normal'
        )

        assert result['status'] == 'created'
        assert 'request_id' in result

        # Check file was created
        pending = list((temp_vault / 'Pending_Approval').glob('*.md'))
        assert len(pending) == 1

    def test_approve_request(self, temp_vault):
        """Test approving a request."""
        handler = ApprovalHookHandler(str(temp_vault))

        # Create a request
        create_result = handler.create_approval_request(
            item_type='email',
            item_data={'summary': 'Test'},
            urgency='normal'
        )
        request_id = create_result['request_id']

        # Approve it
        approve_result = handler.approve(request_id, approved_by='test_user')

        assert approve_result['status'] == 'approved'

        # Check file moved
        approved = list((temp_vault / 'Approved').glob('*.md'))
        pending = list((temp_vault / 'Pending_Approval').glob('*.md'))
        assert len(approved) == 1
        assert len(pending) == 0

    def test_reject_request(self, temp_vault):
        """Test rejecting a request."""
        handler = ApprovalHookHandler(str(temp_vault))

        # Create a request
        create_result = handler.create_approval_request(
            item_type='email',
            item_data={'summary': 'Test'},
            urgency='normal'
        )
        request_id = create_result['request_id']

        # Reject it
        reject_result = handler.reject(request_id, rejected_by='test_user', reason='Not approved')

        assert reject_result['status'] == 'rejected'

        # Check file moved
        rejected = list((temp_vault / 'Rejected').glob('*.md'))
        pending = list((temp_vault / 'Pending_Approval').glob('*.md'))
        assert len(rejected) == 1
        assert len(pending) == 0


class TestStatusHookHandler:
    """Tests for status hook handler."""

    @pytest.fixture
    def temp_vault(self):
        """Create a temporary vault for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            for d in ['Needs_Action', 'Pending_Approval', 'Approved', 'Done', 'Rejected']:
                (vault / d).mkdir(parents=True, exist_ok=True)
            yield vault

    def test_get_status(self, temp_vault):
        """Test getting system status."""
        handler = StatusHookHandler(str(temp_vault))
        result = handler.handle({})

        assert result['status'] == 'healthy'
        assert 'counts' in result
        assert 'needs_action' in result['counts']
        assert 'pending_approval' in result['counts']

    def test_status_with_items(self, temp_vault):
        """Test status with items in folders."""
        # Create test files
        (temp_vault / 'Needs_Action' / 'test1.md').write_text('test')
        (temp_vault / 'Pending_Approval' / 'test2.md').write_text('test')
        (temp_vault / 'Done' / 'test3.md').write_text('test')

        handler = StatusHookHandler(str(temp_vault))
        result = handler.handle({})

        assert result['counts']['needs_action'] == 1
        assert result['counts']['pending_approval'] == 1
        assert result['counts']['done'] == 1


class TestEmailHookHandler:
    """Tests for email hook handler."""

    @pytest.fixture
    def temp_vault(self):
        """Create a temporary vault for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            (vault / 'Needs_Action').mkdir(parents=True, exist_ok=True)
            yield vault

    def test_handle_gmail_webhook(self, temp_vault):
        """Test handling Gmail webhook."""
        handler = EmailHookHandler(str(temp_vault))

        result = handler.handle({
            'source': 'gmail',
            'emailId': 'test123',
            'threadId': 'thread456'
        })

        assert result['status'] == 'received'
        assert 'email_id' in result

        # Check file created
        files = list((temp_vault / 'Needs_Action').glob('EMAIL_*.md'))
        assert len(files) == 1

    def test_handle_sendgrid_webhook(self, temp_vault):
        """Test handling SendGrid webhook."""
        handler = EmailHookHandler(str(temp_vault))

        result = handler.handle({
            'source': 'sendgrid',
            'from': 'sender@example.com',
            'subject': 'Test Subject',
            'text': 'Test body'
        })

        assert result['status'] == 'received'

    def test_handle_generic_webhook(self, temp_vault):
        """Test handling generic webhook."""
        handler = EmailHookHandler(str(temp_vault))

        result = handler.handle({
            'source': 'custom',
            'from': 'custom@example.com',
            'subject': 'Custom Email',
            'body': 'Content'
        })

        assert result['status'] == 'received'


class TestWebhookNotifier:
    """Tests for webhook notifier."""

    def test_notify_without_webhooks(self):
        """Test notification without configured webhooks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            (vault / 'secrets').mkdir(parents=True, exist_ok=True)
            (vault / 'secrets' / 'webhooks.json').write_text('{}')

            notifier = WebhookNotifier(str(vault))
            result = notifier.notify_approval_request('test123', 'email', 'normal')

            # Should succeed even without webhooks
            assert result is True


class TestHookServer:
    """Tests for HTTP hook server."""

    @pytest.fixture
    def temp_vault(self):
        """Create a temporary vault for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)
            for d in ['Needs_Action', 'Pending_Approval', 'Approved', 'Done', 'Rejected']:
                (vault / d).mkdir(parents=True, exist_ok=True)
            yield vault

    def test_server_creation(self, temp_vault):
        """Test creating hook server."""
        server = HookServer(str(temp_vault), port=8080)
        assert server.vault_path == temp_vault
        assert server.port == 8080

    def test_server_with_secret(self, temp_vault):
        """Test creating server with webhook secret."""
        server = HookServer(str(temp_vault), port=8080, webhook_secret='test_secret')
        assert server.webhook_secret == 'test_secret'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])