#!/usr/bin/env python3
"""
Email MCP Server for Personal AI Employee

Provides tools for sending and searching emails via Gmail API.

Configuration:
- Set GMAIL_CREDENTIALS_PATH environment variable to path of credentials.json
- Set GMAIL_TOKEN_PATH environment variable to path of token.json
- Set VAULT_PATH environment variable to vault directory

Run:
    python mcp/email/server.py
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email-mcp")

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

class GmailService:
    """Service for Gmail API operations."""

    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None

        # In dry_run mode, skip authentication
        if os.getenv('DRY_RUN', 'true').lower() == 'true':
            logger.info("DRY_RUN mode - skipping Gmail authentication")
            return

        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None

        # Try to load token from environment or default location
        token_file = None
        if self.token_path:
            token_file = Path(self.token_path)
        else:
            # Check environment variable
            token_path = os.getenv('GMAIL_TOKEN_PATH')
            if token_path:
                token_file = Path(token_path)
            else:
                # Default location
                token_file = Path.home() / '.qwen' / 'gmail_token.json'

        if token_file and token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
            except Exception as e:
                logger.warning(f"Failed to load token: {e}")

        # If no valid credentials, run OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Token refresh failed: {e}")
                    creds = None

            if not creds:
                # Get credentials path
                creds_path = self.credentials_path or os.getenv('GMAIL_CREDENTIALS_PATH')
                if not creds_path:
                    raise ValueError(
                        "Gmail credentials not found. Set GMAIL_CREDENTIALS_PATH environment variable "
                        "or provide credentials_path."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=8080)

            # Save credentials for next run
            if token_file:
                token_file.parent.mkdir(parents=True, exist_ok=True)
                with open(token_file, 'w') as f:
                    f.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail authentication successful")

    def send_email(self, to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> Dict[str, Any]:
        """Send an email via Gmail API."""
        if self.service is None:
            # DRY_RUN mode
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would send email to {to} with subject '{subject}'",
                "to": to,
                "subject": subject,
                "body_preview": body[:200],
                "note": "DRY_RUN mode - set DRY_RUN=false to actually send"
            }

        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            message['from'] = 'me'

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            logger.info(f"Email sent to {to} with subject '{subject}'")
            return {
                "success": True,
                "message_id": result.get('id'),
                "thread_id": result.get('threadId'),
                "timestamp": datetime.now().isoformat()
            }
        except HttpError as e:
            logger.error(f"Failed to send email: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return {"success": False, "error": str(e)}

    def search_emails(self, query: str = "is:unread", max_results: int = 10) -> List[Dict[str, Any]]:
        """Search emails using Gmail query syntax."""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            detailed_messages = []

            for msg in messages[:max_results]:
                msg_details = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()

                headers = {h['name']: h['value'] for h in msg_details['payload']['headers']}
                detailed_messages.append({
                    "id": msg['id'],
                    "thread_id": msg_details.get('threadId'),
                    "from": headers.get('From', ''),
                    "to": headers.get('To', ''),
                    "subject": headers.get('Subject', ''),
                    "date": headers.get('Date', ''),
                    "snippet": msg_details.get('snippet', ''),
                    "labels": msg_details.get('labelIds', [])
                })

            return detailed_messages
        except HttpError as e:
            logger.error(f"Failed to search emails: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching emails: {e}")
            return []

    def get_email(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get full email content by ID."""
        try:
            msg = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract headers
            headers = {}
            for part in msg['payload'].get('headers', []):
                headers[part['name']] = part['value']

            # Extract body
            body = ""
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'body' in part:
                        data = part['body'].get('data', '')
                        if data:
                            body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            elif 'body' in msg['payload']:
                data = msg['payload']['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

            return {
                "id": msg['id'],
                "thread_id": msg.get('threadId'),
                "from": headers.get('From', ''),
                "to": headers.get('To', ''),
                "subject": headers.get('Subject', ''),
                "date": headers.get('Date', ''),
                "body": body,
                "snippet": msg.get('snippet', ''),
                "labels": msg.get('labelIds', [])
            }
        except Exception as e:
            logger.error(f"Failed to get email {message_id}: {e}")
            return None

    def mark_as_read(self, message_id: str) -> bool:
        """Mark an email as read."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.info(f"Marked email {message_id} as read")
            return True
        except Exception as e:
            logger.error(f"Failed to mark email as read: {e}")
            return False

# Create FastMCP server
server = FastMCP("email", instructions="Gmail email sending and searching for Personal AI Employee")

# Initialize Gmail service (lazy initialization)
_gmail_service = None

def get_gmail_service():
    """Get or create Gmail service instance."""
    global _gmail_service
    if _gmail_service is None:
        try:
            # Get paths from environment
            credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH')
            token_path = os.getenv('GMAIL_TOKEN_PATH')

            _gmail_service = GmailService(
                credentials_path=credentials_path,
                token_path=token_path
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {e}")
            raise
    return _gmail_service

@server.tool()
def send_email(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> Dict[str, Any]:
    """
    Send an email via Gmail.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)

    Returns:
        Dict with success status and message details
    """
    service = get_gmail_service()
    return service.send_email(to, subject, body, cc, bcc)

@server.tool()
def search_emails(query: str = "is:unread", max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search emails using Gmail query syntax.

    Args:
        query: Gmail search query (default: "is:unread")
        max_results: Maximum number of results (default: 10)

    Returns:
        List of email metadata
    """
    service = get_gmail_service()
    return service.search_emails(query, max_results)

@server.tool()
def get_email(message_id: str) -> Dict[str, Any]:
    """
    Get full email content by ID.

    Args:
        message_id: Gmail message ID

    Returns:
        Full email details including body
    """
    service = get_gmail_service()
    result = service.get_email(message_id)
    if result is None:
        return {"error": f"Email {message_id} not found"}
    return result

@server.tool()
def mark_email_as_read(message_id: str) -> Dict[str, Any]:
    """
    Mark an email as read.

    Args:
        message_id: Gmail message ID

    Returns:
        Success status
    """
    service = get_gmail_service()
    success = service.mark_as_read(message_id)
    return {"success": success, "message_id": message_id}

@server.tool()
def send_email_from_vault(vault_path: str, item_id: str) -> Dict[str, Any]:
    """
    Send an email based on a vault item in Approved folder.

    Reads a markdown file from the Approved folder, extracts email fields
    from the YAML frontmatter (to, subject, body, cc, bcc), and sends it.

    Args:
        vault_path: Path to vault directory
        item_id: Item ID (filename) in Approved folder

    Returns:
        Send result
    """
    try:
        vault_dir = Path(vault_path)
        item_file = vault_dir / "Approved" / item_id

        if not item_file.exists():
            # Also check Pending_Approval for dry_run
            item_file = vault_dir / "Pending_Approval" / item_id
            if not item_file.exists():
                return {"error": f"Item {item_id} not found in Approved or Pending_Approval folders"}

        content = item_file.read_text(encoding='utf-8', errors='ignore')

        # Parse YAML frontmatter
        import re
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)

        if not frontmatter_match:
            return {"error": "No YAML frontmatter found in vault item"}

        frontmatter_text = frontmatter_match.group(1)
        body = frontmatter_match.group(2).strip()

        # Parse frontmatter key-value pairs
        fields = {}
        for line in frontmatter_text.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, _, value = line.partition(':')
                fields[key.strip().lower()] = value.strip().strip('"').strip("'")

        # Extract email fields
        to_addr = fields.get('to') or fields.get('recipient') or fields.get('to_email')
        subject = fields.get('subject') or fields.get('email_subject') or item_id
        cc_addr = fields.get('cc', '')
        bcc_addr = fields.get('bcc', '')

        # Use body from frontmatter if not extracted, use remaining content as body
        if not to_addr:
            return {
                "error": "No 'to' field found in vault item frontmatter",
                "hint": "Add 'to: recipient@example.com' to the frontmatter"
            }

        # Check dry_run mode
        dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        if dry_run or fields.get('status', '').lower() == 'draft':
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would send email to {to_addr} with subject '{subject}'",
                "to": to_addr,
                "subject": subject,
                "cc": cc_addr,
                "bcc": bcc_addr,
                "body_preview": body[:200] if body else content[:200],
                "source_file": str(item_file.relative_to(vault_dir))
            }

        # Actually send
        service = get_gmail_service()
        email_body = body if body else content
        return service.send_email(to_addr, subject, email_body, cc_addr, bcc_addr)

    except Exception as e:
        logger.error(f"Error sending email from vault: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Run the server over stdio (default for MCP)
    logger.info("Starting Email MCP Server...")
    server.run()