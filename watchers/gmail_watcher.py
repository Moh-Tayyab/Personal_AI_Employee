"""
Gmail Watcher - Monitors Gmail for new important emails

Requirements:
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
    Enable Gmail API in Google Cloud Console

Usage:
    python -m watchers.gmail_watcher --vault ./vault --credentials ./secrets/credentials.json
"""

import os
import sys
from datetime import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchers.base_watcher import BaseWatcher


# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GmailWatcher(BaseWatcher):
    """Watches Gmail for new important/unread emails."""

    def __init__(self, vault_path: str, credentials_path: str = None, token_path: str = None):
        super().__init__(vault_path, check_interval=120, name="GmailWatcher")
        self.credentials_path = credentials_path
        self.token_path = token_path or vault_path + '/secrets/gmail_token.json'
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None

        # Load existing token if available
        token_file = Path(self.token_path)
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

        # If no valid credentials, run OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            else:
                if not self.credentials_path:
                    raise ValueError("No credentials provided and no token found")

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=8080)

            # Save credentials for next run
            token_file.parent.mkdir(parents=True, exist_ok=True)
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)

    def check_for_updates(self) -> list:
        """Check for new unread important emails."""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread is:important',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            return messages

        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            # Try to re-authenticate on auth errors
            if '401' in str(e) or '403' in str(e):
                self.logger.info("Attempting re-authentication...")
                Path(self.token_path).unlink(missing_ok=True)
                self._authenticate()
            return []
        except Exception as e:
            # Handle token expiry during runtime
            if 'Token expired' in str(e) or 'invalid_grant' in str(e):
                self.logger.info("Token expired, attempting refresh...")
                from google.auth.transport.requests import Request
                try:
                    self.service._credentials.refresh(Request())
                except:
                    Path(self.token_path).unlink(missing_ok=True)
                    self._authenticate()
            return []

    def create_action_file(self, message) -> Path:
        """Create action file for a Gmail message."""
        msg = self.service.users().messages().get(
            userId='me',
            id=message['id']
        ).execute()

        # Extract headers
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}

        # Determine priority based on keywords
        subject = headers.get('Subject', '').lower()
        snippet = msg.get('snippet', '').lower()

        priority = 'normal'
        for keyword in ['urgent', 'asap', 'emergency', 'critical']:
            if keyword in subject or keyword in snippet:
                priority = 'high'
                break

        # Determine category
        category = 'general'
        for keyword in ['invoice', 'payment', 'bill']:
            if keyword in subject or keyword in snippet:
                category = 'finance'
                break
        for keyword in ['meeting', 'schedule', 'call']:
            if keyword in subject or keyword in snippet:
                category = 'calendar'
                break

        content = f"""---
type: email
source: gmail
message_id: {message['id']}
from: {headers.get('From', 'Unknown')}
to: {headers.get('To', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
date: {headers.get('Date', 'Unknown')}
received: {datetime.now().isoformat()}
priority: {priority}
category: {category}
status: pending
---

# Email Content

{msg.get('snippet', '')}

## Headers
- **From:** {headers.get('From', 'Unknown')}
- **To:** {headers.get('To', 'Unknown')}
- **Subject:** {headers.get('Subject', 'No Subject')}
- **Date:** {headers.get('Date', 'Unknown')}

# Suggested Actions

- [ ] Read and understand the email
- [ ] Draft reply (if needed)
- [ ] Create follow-up task (if needed)
- [ ] Archive after processing

## Notes
_AI Employee: Process this email according to Company Handbook rules._
"""

        # Create filename from subject (sanitized)
        safe_subject = headers.get('Subject', 'No Subject')[:50]
        safe_subject = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in safe_subject)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        filename = f'EMAIL_{timestamp}_{safe_subject}.md'
        filepath = self.needs_action / filename
        filepath.write_text(content)

        # Mark email as read
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message['id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
        except Exception as e:
            self.logger.warning(f"Could not mark email as read: {e}")

        return filepath


def main():
    """Main entry point for Gmail Watcher."""
    import argparse

    parser = argparse.ArgumentParser(description='Gmail Watcher')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--credentials', help='Path to credentials.json')
    parser.add_argument('--token', help='Path to token.json')
    parser.add_argument('--interval', type=int, default=120, help='Check interval in seconds')

    args = parser.parse_args()

    watcher = GmailWatcher(
        vault_path=args.vault,
        credentials_path=args.credentials,
        token_path=args.token
    )
    watcher.check_interval = args.interval
    watcher.run()


if __name__ == "__main__":
    main()
