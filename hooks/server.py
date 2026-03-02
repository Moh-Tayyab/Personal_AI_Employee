"""
HTTP Hook Server - Enables external integrations via webhooks

Provides:
- Webhook endpoints for external services
- Real-time status updates
- Approval notifications via HTTP
- Integration with CI/CD pipelines

Usage:
    from hooks import run_server
    run_server(port=8080, vault_path='./vault')
"""

import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime
from typing import Callable, Dict, Optional
from urllib.parse import urlparse, parse_qs
import hashlib
import hmac

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HookServer")


class HookHandler(BaseHTTPRequestHandler):
    """Base HTTP request handler with routing."""

    # Class-level configuration
    vault_path: Path = None
    webhook_secret: str = None
    approval_callback: Callable = None
    status_callback: Callable = None
    routes: Dict[str, Callable] = {}

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info("%s - %s", self.client_address[0], format % args)

    def send_json_response(self, status: int, data: dict):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def send_error_response(self, status: int, message: str):
        """Send error response."""
        self.send_json_response(status, {'error': message, 'status': 'error'})

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature for security."""
        if not self.webhook_secret:
            return True  # No secret configured, allow all

        expected = 'sha256=' + hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Signature')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Route: /health - Health check
        if path == '/health':
            self.send_json_response(200, {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
            return

        # Route: /status - System status
        if path == '/status':
            if self.status_callback:
                try:
                    status = self.status_callback()
                    self.send_json_response(200, status)
                except Exception as e:
                    self.send_error_response(500, str(e))
            else:
                self.send_json_response(200, self._get_default_status())
            return

        # Route: /pending - Items pending approval
        if path == '/pending':
            pending = self._get_pending_items()
            self.send_json_response(200, {
                'count': len(pending),
                'items': pending
            })
            return

        # Route: /dashboard - Dashboard data
        if path == '/dashboard':
            dashboard = self._get_dashboard_data()
            self.send_json_response(200, dashboard)
            return

        # Unknown route
        self.send_error_response(404, f'Not found: {path}')

    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        # Read body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else b''

        # Verify signature if present
        signature = self.headers.get('X-Signature', '')
        if not self.verify_signature(body, signature):
            self.send_error_response(401, 'Invalid signature')
            return

        # Route: /webhook/email - Email webhook
        if path == '/webhook/email':
            try:
                data = json.loads(body)
                result = self._handle_email_webhook(data)
                self.send_json_response(200, result)
            except Exception as e:
                self.send_error_response(400, str(e))
            return

        # Route: /webhook/approval - Approval callback
        if path == '/webhook/approval':
            try:
                data = json.loads(body)
                result = self._handle_approval_webhook(data)
                self.send_json_response(200, result)
            except Exception as e:
                self.send_error_response(400, str(e))
            return

        # Route: /webhook/github - GitHub webhook
        if path == '/webhook/github':
            try:
                data = json.loads(body)
                result = self._handle_github_webhook(data)
                self.send_json_response(200, result)
            except Exception as e:
                self.send_error_response(400, str(e))
            return

        # Route: /trigger/process - Trigger processing
        if path == '/trigger/process':
            try:
                data = json.loads(body) if body else {}
                result = self._handle_process_trigger(data)
                self.send_json_response(200, result)
            except Exception as e:
                self.send_error_response(400, str(e))
            return

        # Unknown route
        self.send_error_response(404, f'Not found: {path}')

    def _get_default_status(self) -> dict:
        """Get default system status."""
        if not self.vault_path:
            return {'status': 'error', 'message': 'Vault not configured'}

        return {
            'status': 'running',
            'vault_path': str(self.vault_path),
            'needs_action': len(list((self.vault_path / 'Needs_Action').glob('*.md'))),
            'pending_approval': len(list((self.vault_path / 'Pending_Approval').glob('*.md'))),
            'done_today': self._count_done_today(),
            'timestamp': datetime.now().isoformat()
        }

    def _get_pending_items(self) -> list:
        """Get items pending approval."""
        if not self.vault_path:
            return []

        pending_dir = self.vault_path / 'Pending_Approval'
        items = []

        for f in pending_dir.glob('*.md'):
            content = f.read_text()
            items.append({
                'id': f.stem,
                'filename': f.name,
                'created': datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                'preview': content[:200] + '...' if len(content) > 200 else content
            })

        return sorted(items, key=lambda x: x['created'], reverse=True)

    def _get_dashboard_data(self) -> dict:
        """Get dashboard data for web UI."""
        if not self.vault_path:
            return {'error': 'Vault not configured'}

        # Read dashboard file if exists
        dashboard_file = self.vault_path / 'Dashboard.md'
        if dashboard_file.exists():
            dashboard_content = dashboard_file.read_text()
        else:
            dashboard_content = None

        return {
            'needs_action': len(list((self.vault_path / 'Needs_Action').glob('*.md'))),
            'pending_approval': len(list((self.vault_path / 'Pending_Approval').glob('*.md'))),
            'done_today': self._count_done_today(),
            'plans_today': self._count_plans_today(),
            'dashboard_content': dashboard_content,
            'timestamp': datetime.now().isoformat()
        }

    def _count_done_today(self) -> int:
        """Count items done today."""
        if not self.vault_path:
            return 0

        today = datetime.now().strftime('%Y%m%d')
        done_dir = self.vault_path / 'Done'
        count = 0

        for f in done_dir.glob('*.md'):
            if today in f.name:
                count += 1

        return count

    def _count_plans_today(self) -> int:
        """Count plans created today."""
        if not self.vault_path:
            return 0

        today = datetime.now().strftime('%Y%m%d')
        plans_dir = self.vault_path / 'Plans'
        count = 0

        for f in plans_dir.glob('*.md'):
            if today in f.name:
                count += 1

        return count

    def _handle_email_webhook(self, data: dict) -> dict:
        """Handle incoming email webhook."""
        logger.info(f"Email webhook received: {data.get('type', 'unknown')}")

        # Create file in Needs_Action
        if self.vault_path and data.get('type') == 'new_email':
            needs_action = self.vault_path / 'Needs_Action'
            needs_action.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            email_id = data.get('id', timestamp)

            filename = f"EMAIL_{email_id}_{timestamp}.md"
            filepath = needs_action / filename

            # Extract email data
            from_addr = data.get('from', 'Unknown')
            subject = data.get('subject', 'No Subject')
            body = data.get('body', '')

            content = f"""---
type: email
id: {email_id}
from: {from_addr}
subject: {subject}
received: {datetime.now().isoformat()}
priority: {data.get('priority', 'normal')}
---

# Email from {from_addr}

## Subject
{subject}

## Body
{body}
"""
            filepath.write_text(content)
            logger.info(f"Created {filename} in Needs_Action")

        return {
            'status': 'received',
            'message': 'Email webhook processed',
            'timestamp': datetime.now().isoformat()
        }

    def _handle_approval_webhook(self, data: dict) -> dict:
        """Handle approval callback webhook."""
        logger.info(f"Approval webhook received: {data.get('action', 'unknown')}")

        action = data.get('action')
        item_id = data.get('item_id')
        comment = data.get('comment', '')

        if action == 'approve' and item_id:
            # Move from Pending_Approval to Approved
            if self.vault_path:
                pending = self.vault_path / 'Pending_Approval'
                approved = self.vault_path / 'Approved'
                approved.mkdir(parents=True, exist_ok=True)

                # Find the file
                for f in pending.glob(f'*{item_id}*.md'):
                    dest = approved / f.name
                    f.rename(dest)
                    logger.info(f"Approved: {f.name}")

                    if self.approval_callback:
                        self.approval_callback(item_id, True, comment)

        elif action == 'reject' and item_id:
            # Move from Pending_Approval to Rejected
            if self.vault_path:
                pending = self.vault_path / 'Pending_Approval'
                rejected = self.vault_path / 'Rejected'
                rejected.mkdir(parents=True, exist_ok=True)

                for f in pending.glob(f'*{item_id}*.md'):
                    dest = rejected / f.name
                    f.rename(dest)
                    logger.info(f"Rejected: {f.name}")

                    if self.approval_callback:
                        self.approval_callback(item_id, False, comment)

        return {
            'status': 'processed',
            'action': action,
            'item_id': item_id,
            'timestamp': datetime.now().isoformat()
        }

    def _handle_github_webhook(self, data: dict) -> dict:
        """Handle GitHub webhook."""
        event_type = self.headers.get('X-GitHub-Event', 'unknown')
        logger.info(f"GitHub webhook received: {event_type}")

        # Store GitHub events for processing
        if self.vault_path:
            events_dir = self.vault_path / 'Needs_Action'
            events_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"GITHUB_{event_type}_{timestamp}.md"
            filepath = events_dir / filename

            content = f"""---
type: github_webhook
event: {event_type}
received: {datetime.now().isoformat()}
---

# GitHub Event: {event_type}

```json
{json.dumps(data, indent=2)}
```
"""
            filepath.write_text(content)
            logger.info(f"Created {filename} for GitHub event")

        return {
            'status': 'received',
            'event': event_type,
            'timestamp': datetime.now().isoformat()
        }

    def _handle_process_trigger(self, data: dict) -> dict:
        """Handle processing trigger."""
        logger.info(f"Process trigger received: {data}")

        # Create trigger file
        if self.vault_path:
            triggers_dir = self.vault_path / 'Triggers'
            triggers_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            trigger_type = data.get('type', 'manual')
            filename = f"TRIGGER_{trigger_type}_{timestamp}.md"
            filepath = triggers_dir / filename

            content = f"""---
type: trigger
trigger_type: {trigger_type}
received: {datetime.now().isoformat()}
parameters: {json.dumps(data)}
---

# Processing Trigger

Type: {trigger_type}
Parameters: {json.dumps(data, indent=2)}
"""
            filepath.write_text(content)

        return {
            'status': 'triggered',
            'message': 'Processing triggered',
            'timestamp': datetime.now().isoformat()
        }


class HookServer:
    """HTTP Hook Server for Personal AI Employee."""

    def __init__(self, vault_path: str, port: int = 8080,
                 webhook_secret: str = None):
        self.vault_path = Path(vault_path)
        self.port = port
        self.webhook_secret = webhook_secret
        self.server: Optional[HTTPServer] = None
        self.approval_callback: Callable = None
        self.status_callback: Callable = None

    def set_approval_callback(self, callback: Callable):
        """Set callback for approval webhooks."""
        self.approval_callback = callback
        HookHandler.approval_callback = callback

    def set_status_callback(self, callback: Callable):
        """Set callback for status requests."""
        self.status_callback = callback
        HookHandler.status_callback = callback

    def start(self, blocking: bool = True):
        """Start the HTTP server."""
        HookHandler.vault_path = self.vault_path
        HookHandler.webhook_secret = self.webhook_secret

        self.server = HTTPServer(('0.0.0.0', self.port), HookHandler)
        logger.info(f"Hook server started on port {self.port}")
        logger.info(f"Vault path: {self.vault_path}")

        if blocking:
            self.server.serve_forever()
        else:
            thread = threading.Thread(target=self.server.serve_forever)
            thread.daemon = True
            thread.start()
            logger.info("Hook server running in background")

    def stop(self):
        """Stop the HTTP server."""
        if self.server:
            self.server.shutdown()
            logger.info("Hook server stopped")


def run_server(port: int = 8080, vault_path: str = './vault',
               webhook_secret: str = None, blocking: bool = True):
    """
    Run the HTTP hook server.

    Args:
        port: Port to listen on (default: 8080)
        vault_path: Path to Obsidian vault
        webhook_secret: Optional secret for webhook signature verification
        blocking: Whether to block (default: True)
    """
    server = HookServer(vault_path=vault_path, port=port,
                        webhook_secret=webhook_secret)
    server.start(blocking=blocking)
    return server


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='HTTP Hook Server')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--vault', required=True)
    parser.add_argument('--secret', default=None)

    args = parser.parse_args()

    run_server(port=args.port, vault_path=args.vault,
               webhook_secret=args.secret)