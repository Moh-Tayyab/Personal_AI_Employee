"""
Hook Handlers - Specialized handlers for different webhook types

Provides handlers for:
- Approval notifications and callbacks
- Status updates and health checks
- Email webhooks
- External notifications (Slack, Discord, etc.)
"""

import json
import logging
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Callable
from abc import ABC, abstractmethod

logger = logging.getLogger("HookHandlers")


class BaseHookHandler(ABC):
    """Abstract base class for hook handlers."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)

    @abstractmethod
    def handle(self, data: dict) -> dict:
        """Process the hook data."""
        pass


class ApprovalHookHandler(BaseHookHandler):
    """
    Handles approval workflow via webhooks.

    Enables:
    - External systems to request approval
    - Mobile/web approval interfaces
    - Real-time approval notifications
    """

    def __init__(self, vault_path: str, notifier: 'WebhookNotifier' = None):
        super().__init__(vault_path)
        self.notifier = notifier
        self.pending_dir = self.vault_path / 'Pending_Approval'
        self.approved_dir = self.vault_path / 'Approved'
        self.rejected_dir = self.vault_path / 'Rejected'

        for d in [self.pending_dir, self.approved_dir, self.rejected_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def create_approval_request(self, item_type: str, item_data: dict,
                                urgency: str = 'normal') -> dict:
        """
        Create a new approval request.

        Args:
            item_type: Type of item (email, payment, social, etc.)
            item_data: Details of the item requiring approval
            urgency: Urgency level (urgent, high, normal, low)

        Returns:
            dict with request_id and status
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        request_id = f"{item_type}_{timestamp}"

        # Create approval request file
        filename = f"APPROVAL_{request_id}.md"
        filepath = self.pending_dir / filename

        # Format as markdown with frontmatter
        content = f"""---
type: approval_request
id: {request_id}
item_type: {item_type}
urgency: {urgency}
created: {datetime.now().isoformat()}
status: pending
---

# Approval Request: {item_type}

## Summary
{item_data.get('summary', 'No summary provided')}

## Details
"""

        # Add all item_data to details section
        for key, value in item_data.items():
            if key != 'summary':
                content += f"- **{key}:** {value}\n"

        content += f"""
## Actions Required
- [ ] Review the request details above
- [ ] Approve or reject via webhook or dashboard

---
*Auto-generated approval request at {datetime.now().isoformat()}*
"""

        filepath.write_text(content)
        logger.info(f"Created approval request: {filename}")

        result = {
            'status': 'created',
            'request_id': request_id,
            'file': filename,
            'urgency': urgency
        }

        # Notify if notifier is configured
        if self.notifier:
            self.notifier.notify_approval_request(request_id, item_type, urgency)

        return result

    def approve(self, request_id: str, approved_by: str = 'webhook',
                comment: str = '') -> dict:
        """
        Approve a pending request.

        Args:
            request_id: ID of the approval request
            approved_by: Who approved (user ID or 'webhook')
            comment: Optional approval comment

        Returns:
            dict with status and result
        """
        # Find the file
        matching = list(self.pending_dir.glob(f'*{request_id}*.md'))

        if not matching:
            return {'status': 'error', 'message': f'Request not found: {request_id}'}

        filepath = matching[0]
        content = filepath.read_text()

        # Update status in content
        updated = content.replace('status: pending', 'status: approved')
        updated += f"\n\n## Approval\n- **Approved by:** {approved_by}\n- **Time:** {datetime.now().isoformat()}\n"
        if comment:
            updated += f"- **Comment:** {comment}\n"

        # Write to approved directory
        new_path = self.approved_dir / filepath.name

        # Update content
        filepath.write_text(updated)

        # Move file
        filepath.rename(new_path)
        logger.info(f"Approved: {filepath.name}")

        if self.notifier:
            self.notifier.notify_approval_result(request_id, True, approved_by)

        return {
            'status': 'approved',
            'request_id': request_id,
            'approved_by': approved_by,
            'timestamp': datetime.now().isoformat()
        }

    def reject(self, request_id: str, rejected_by: str = 'webhook',
                reason: str = '') -> dict:
        """
        Reject a pending request.

        Args:
            request_id: ID of the approval request
            rejected_by: Who rejected (user ID or 'webhook')
            reason: Rejection reason

        Returns:
            dict with status and result
        """
        matching = list(self.pending_dir.glob(f'*{request_id}*.md'))

        if not matching:
            return {'status': 'error', 'message': f'Request not found: {request_id}'}

        filepath = matching[0]
        content = filepath.read_text()

        # Update status
        updated = content.replace('status: pending', 'status: rejected')
        updated += f"\n\n## Rejection\n- **Rejected by:** {rejected_by}\n- **Time:** {datetime.now().isoformat()}\n"
        if reason:
            updated += f"- **Reason:** {reason}\n"

        # Write and move
        new_path = self.rejected_dir / filepath.name
        filepath.write_text(updated)
        filepath.rename(new_path)
        logger.info(f"Rejected: {filepath.name}")

        if self.notifier:
            self.notifier.notify_approval_result(request_id, False, rejected_by)

        return {
            'status': 'rejected',
            'request_id': request_id,
            'rejected_by': rejected_by,
            'timestamp': datetime.now().isoformat()
        }

    def handle(self, data: dict) -> dict:
        """Handle approval webhook data."""
        action = data.get('action')

        if action == 'create':
            return self.create_approval_request(
                item_type=data.get('item_type', 'unknown'),
                item_data=data.get('item_data', {}),
                urgency=data.get('urgency', 'normal')
            )
        elif action == 'approve':
            return self.approve(
                request_id=data.get('request_id'),
                approved_by=data.get('approved_by', 'webhook'),
                comment=data.get('comment', '')
            )
        elif action == 'reject':
            return self.reject(
                request_id=data.get('request_id'),
                rejected_by=data.get('rejected_by', 'webhook'),
                reason=data.get('reason', '')
            )
        else:
            return {'status': 'error', 'message': f'Unknown action: {action}'}


class StatusHookHandler(BaseHookHandler):
    """
    Handles status and health check requests.

    Provides:
    - System health status
    - Item counts by status
    - Performance metrics
    """

    def handle(self, data: dict) -> dict:
        """Get current system status."""
        return {
            'status': 'healthy',
            'vault_path': str(self.vault_path),
            'counts': self._get_counts(),
            'timestamp': datetime.now().isoformat()
        }

    def _get_counts(self) -> dict:
        """Get counts of items in each folder."""
        return {
            'needs_action': len(list((self.vault_path / 'Needs_Action').glob('*.md'))),
            'pending_approval': len(list((self.vault_path / 'Pending_Approval').glob('*.md'))),
            'approved': len(list((self.vault_path / 'Approved').glob('*.md'))),
            'done': len(list((self.vault_path / 'Done').glob('*.md'))),
            'rejected': len(list((self.vault_path / 'Rejected').glob('*.md')))
        }


class EmailHookHandler(BaseHookHandler):
    """
    Handles incoming email webhooks.

    Supports webhooks from:
    - Gmail API push notifications
    - SendGrid inbound parse
    - Custom email forwarders
    """

    def handle(self, data: dict) -> dict:
        """Process incoming email webhook."""
        source = data.get('source', 'unknown')

        if source == 'gmail':
            return self._handle_gmail_webhook(data)
        elif source == 'sendgrid':
            return self._handle_sendgrid_webhook(data)
        else:
            return self._handle_generic_webhook(data)

    def _handle_gmail_webhook(self, data: dict) -> dict:
        """Handle Gmail push notification."""
        needs_action = self.vault_path / 'Needs_Action'
        needs_action.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        email_id = data.get('emailId', data.get('id', timestamp))

        filename = f"EMAIL_{email_id}_{timestamp}.md"
        filepath = needs_action / filename

        # Extract email data from Gmail format
        content = f"""---
type: email
id: {email_id}
source: gmail
received: {datetime.now().isoformat()}
threadId: {data.get('threadId', 'N/A')}
---

# Gmail Notification

## History ID
{data.get('historyId', 'N/A')}

## Raw Data
```json
{json.dumps(data, indent=2)}
```

---
*Process this email using /process-email*
"""

        filepath.write_text(content)
        logger.info(f"Created Gmail webhook file: {filename}")

        return {
            'status': 'received',
            'email_id': email_id,
            'file': filename
        }

    def _handle_sendgrid_webhook(self, data: dict) -> dict:
        """Handle SendGrid inbound parse."""
        needs_action = self.vault_path / 'Needs_Action'
        needs_action.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        email_id = f"sg_{timestamp}"

        filename = f"EMAIL_{email_id}.md"
        filepath = needs_action / filename

        # Extract SendGrid fields
        from_email = data.get('from', data.get('envelope', {}).get('from', 'Unknown'))
        subject = data.get('subject', 'No Subject')
        body = data.get('text', data.get('html', ''))

        content = f"""---
type: email
id: {email_id}
source: sendgrid
from: {from_email}
subject: {subject}
received: {datetime.now().isoformat()}
---

# Email from {from_email}

## Subject
{subject}

## Body
{body}

## Attachments
{json.dumps(data.get('attachments', []), indent=2)}
"""

        filepath.write_text(content)
        logger.info(f"Created SendGrid webhook file: {filename}")

        return {
            'status': 'received',
            'email_id': email_id,
            'file': filename
        }

    def _handle_generic_webhook(self, data: dict) -> dict:
        """Handle generic email webhook."""
        needs_action = self.vault_path / 'Needs_Action'
        needs_action.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        email_id = data.get('id', f"gen_{timestamp}")

        filename = f"EMAIL_{email_id}_{timestamp}.md"
        filepath = needs_action / filename

        content = f"""---
type: email
id: {email_id}
source: {data.get('source', 'generic')}
received: {datetime.now().isoformat()}
from: {data.get('from', 'Unknown')}
subject: {data.get('subject', 'No Subject')}
---

# Email

## From
{data.get('from', 'Unknown')}

## Subject
{data.get('subject', 'No Subject')}

## Body
{data.get('body', data.get('content', 'No content'))}

## Raw Data
```json
{json.dumps(data, indent=2)}
```
"""

        filepath.write_text(content)
        logger.info(f"Created generic webhook file: {filename}")

        return {
            'status': 'received',
            'email_id': email_id,
            'file': filename
        }


class WebhookNotifier:
    """
    Sends webhook notifications to external services.

    Supports:
    - Slack webhooks
    - Discord webhooks
    - Generic HTTP webhooks
    - Email notifications via MCP
    """

    def __init__(self, vault_path: str, config: dict = None):
        self.vault_path = Path(vault_path)
        self.config = config or {}
        self.webhooks = self._load_webhooks()

    def _load_webhooks(self) -> dict:
        """Load webhook URLs from config."""
        config_file = self.vault_path / 'secrets' / 'webhooks.json'
        if config_file.exists():
            return json.loads(config_file.read_text())
        return {}

    def notify_approval_request(self, request_id: str, item_type: str,
                                  urgency: str) -> bool:
        """Send notification about new approval request."""
        message = f"🔔 **New Approval Request**\n"
        message += f"Type: {item_type}\n"
        message += f"ID: `{request_id}`\n"
        message += f"Urgency: {urgency}\n"
        message += f"Time: {datetime.now().isoformat()}"

        return self._send_notification(message, urgency == 'urgent')

    def notify_approval_result(self, request_id: str, approved: bool,
                                 by: str) -> bool:
        """Send notification about approval result."""
        status = "✅ Approved" if approved else "❌ Rejected"
        message = f"{status}\n"
        message += f"Request: `{request_id}`\n"
        message += f"By: {by}\n"
        message += f"Time: {datetime.now().isoformat()}"

        return self._send_notification(message, approved)

    def notify_error(self, error_type: str, message: str,
                      details: dict = None) -> bool:
        """Send error notification."""
        content = f"🚨 **Error: {error_type}**\n"
        content += f"Message: {message}\n"
        content += f"Time: {datetime.now().isoformat()}\n"
        if details:
            content += f"Details: ```json\n{json.dumps(details, indent=2)}\n```"

        return self._send_notification(content, urgent=True)

    def _send_notification(self, message: str, urgent: bool = False) -> bool:
        """Send notification to all configured webhooks."""
        success = True

        # Slack webhook
        if self.webhooks.get('slack'):
            success &= self._send_slack(message, urgent)

        # Discord webhook
        if self.webhooks.get('discord'):
            success &= self._send_discord(message, urgent)

        # Generic webhook
        if self.webhooks.get('generic'):
            success &= self._send_generic(message, urgent)

        return success

    def _send_slack(self, message: str, urgent: bool = False) -> bool:
        """Send to Slack webhook."""
        url = self.webhooks.get('slack')
        if not url:
            return True

        color = "danger" if urgent else "good"
        payload = {
            "attachments": [{
                "color": color,
                "text": message,
                "fallback": message
            }]
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=10)
            return True
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            return False

    def _send_discord(self, message: str, urgent: bool = False) -> bool:
        """Send to Discord webhook."""
        url = self.webhooks.get('discord')
        if not url:
            return True

        color = 15158332 if urgent else 3066993  # Red if urgent, green otherwise
        payload = {
            "embeds": [{
                "description": message,
                "color": color
            }]
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=10)
            return True
        except Exception as e:
            logger.error(f"Discord notification failed: {e}")
            return False

    def _send_generic(self, message: str, urgent: bool = False) -> bool:
        """Send to generic webhook."""
        url = self.webhooks.get('generic')
        if not url:
            return True

        payload = {
            "message": message,
            "urgent": urgent,
            "timestamp": datetime.now().isoformat()
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=10)
            return True
        except Exception as e:
            logger.error(f"Generic webhook failed: {e}")
            return False