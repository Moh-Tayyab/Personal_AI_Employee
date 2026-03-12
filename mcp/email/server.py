"""
Email MCP Server - Send emails via Claude Code

This MCP server allows Claude Code to send emails through Gmail.

Usage:
    python -m mcp.email.server
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.base import BaseMCPServer, MCPTool


class EmailMCPServer(BaseMCPServer):
    """MCP server for email operations."""

    def __init__(self, config: dict = None):
        super().__init__("email", config)
        self.vault_path = Path(os.getenv('VAULT_PATH', './vault'))

    def get_tools(self):
        """Return available tools."""
        return [
            MCPTool(
                name="send_email",
                description="Send an email to a recipient",
                input_schema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body"},
                        "cc": {"type": "string", "description": "CC recipients"},
                        "attachments": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File paths to attach"
                        }
                    },
                    "required": ["to", "subject", "body"]
                }
            ),
            MCPTool(
                name="draft_email",
                description="Create a draft email (doesn't send)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body"}
                    },
                    "required": ["to", "subject", "body"]
                }
            ),
            MCPTool(
                name="search_emails",
                description="Search emails in Gmail",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Gmail search query"},
                        "max_results": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                }
            )
        ]

    def handle_request(self, method: str, params: dict = None):
        """Handle MCP request."""
        params = params or {}

        if method == "send_email":
            return self.send_email(params)
        elif method == "draft_email":
            return self.draft_email(params)
        elif method == "search_emails":
            return self.search_emails(params)
        elif method == "list_tools":
            return [t.to_dict() for t in self.get_tools()]
        else:
            return {"error": f"Unknown method: {method}"}

    def send_email(self, params: dict) -> dict:
        """Send an email via Gmail API."""
        self.logger.info(f"Sending email to: {params.get('to')}")

        # Check dry-run mode
        dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'

        if dry_run:
            self.logger.info(f"[DRY RUN] Would send email: {params}")
            return {
                "status": "dry_run",
                "message": "Email not sent (dry-run mode)",
                "params": params
            }

        # Try to send via Gmail API
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            import base64
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            # Load credentials
            token_path = os.getenv('GMAIL_TOKEN_PATH', './vault/secrets/gmail_token.json')
            if not os.path.exists(token_path):
                self.logger.warning("Gmail token not found - creating draft instead")
                return self.draft_email(params)

            creds = Credentials.from_authorized_user_file(token_path)
            service = build('gmail', 'v1', credentials=creds)

            # Create message
            message = MIMEMultipart() if params.get('attachments') else MIMEText(params['body'])

            if isinstance(message, MIMEMultipart):
                message.attach(MIMEText(params['body'], 'plain'))

            message['to'] = params['to']
            message['subject'] = params['subject']

            if params.get('cc'):
                message['cc'] = params['cc']

            # Encode and send
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            sent = service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            self.logger.info(f"Email sent successfully: {sent['id']}")
            return {
                "status": "sent",
                "message_id": sent['id'],
                "to": params['to'],
                "subject": params['subject']
            }

        except ImportError as e:
            self.logger.error(f"Gmail API libraries not installed: {e}")
            self.logger.info("Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
            return self.draft_email(params)

        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            self.logger.info("Falling back to draft creation")
            return self.draft_email(params)

    def draft_email(self, params: dict) -> dict:
        """Create a draft email."""
        drafts_folder = self.vault_path / 'Drafts'
        drafts_folder.mkdir(parents=True, exist_ok=True)

        from datetime import datetime
        filename = f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""---
type: email_draft
to: {params.get('to')}
subject: {params.get('subject')}
created: {datetime.now().isoformat()}
status: draft
---

{params.get('body')}
"""

        draft_path = drafts_folder / filename
        draft_path.write_text(content)

        return {
            "status": "created",
            "draft_path": str(draft_path)
        }

    def search_emails(self, params: dict) -> dict:
        """Search emails via Gmail API."""
        query = params.get('query', '')
        max_results = params.get('max_results', 10)

        self.logger.info(f"Searching emails: query='{query}', max={max_results}")

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            # Load credentials
            token_path = os.getenv('GMAIL_TOKEN_PATH', './vault/secrets/gmail_token.json')
            if not os.path.exists(token_path):
                return {
                    "status": "error",
                    "message": "Gmail token not found. Run gmail_watcher.py first to authenticate."
                }

            creds = Credentials.from_authorized_user_file(token_path)
            service = build('gmail', 'v1', credentials=creds)

            # Search messages
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return {
                    "status": "success",
                    "count": 0,
                    "emails": []
                }

            # Fetch full message details
            emails = []
            for msg in messages:
                try:
                    full_msg = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['From', 'Subject', 'Date']
                    ).execute()

                    headers = {h['name']: h['value'] for h in full_msg['payload']['headers']}

                    emails.append({
                        'id': msg['id'],
                        'from': headers.get('From', 'Unknown'),
                        'subject': headers.get('Subject', 'No subject'),
                        'date': headers.get('Date', 'Unknown'),
                        'snippet': full_msg.get('snippet', '')
                    })
                except Exception as e:
                    self.logger.error(f"Error fetching message {msg['id']}: {e}")
                    continue

            self.logger.info(f"Found {len(emails)} emails")
            return {
                "status": "success",
                "count": len(emails),
                "emails": emails,
                "query": query
            }

        except ImportError as e:
            self.logger.error(f"Gmail API libraries not installed: {e}")
            return {
                "status": "error",
                "message": "Install Gmail API: pip install google-auth google-auth-oauthlib google-api-python-client"
            }

        except Exception as e:
            self.logger.error(f"Error searching emails: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


def main():
    """Main entry point."""
    server = EmailMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
