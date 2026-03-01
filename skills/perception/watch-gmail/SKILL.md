---
name: watch-gmail
description: |
  Monitors Gmail inbox for new messages and creates action items in the
  vault. Filters by importance, extracts metadata, and triggers processing
  workflow. Runs as a continuous background process or scheduled task.
allowed-tools: [Read, Write, Glob, Bash]
---

# Watch Gmail - Professional Skill

Monitors Gmail for new messages using Gmail API, creates structured action items in the Obsidian vault for processing.

## When to Use

- As a background process: `python scripts/gmail_watcher.py`
- Scheduled via cron: Every 2-5 minutes
- Manual trigger: `/watch-gmail --once`
- Orchestrator-managed: Started by main orchestrator

## Before Implementation

| Source | Gather |
|--------|--------|
| **Gmail API credentials** | OAuth tokens, credentials.json |
| **vault/Needs_Action/** | Check for existing unprocessed items |
| **vault/.processed_ids.json** | Track processed message IDs |
| **Company_Handbook.md** | Priority rules, keyword triggers |

## Workflow

### Phase 1: Authentication

```python
# Check for valid credentials
credentials = load_credentials()

if credentials.expired:
    credentials = refresh_credentials()
    save_credentials(credentials)

service = build('gmail', 'v1', credentials=credentials)
```

### Phase 2: Message Discovery

```python
# Query for new messages
query = build_query(filters)

# Default query
default_query = "is:unread -in:spam -in:trash"

# With importance filter
importance_query = "is:unread is:important -in:spam -in:trash"

# Custom query from config
custom_query = config.get('gmail_query', default_query)

results = service.users().messages().list(
    userId='me',
    q=query,
    maxResults=50
).execute()
```

### Phase 3: Message Processing

```python
for message_id in new_messages:
    # Skip if already processed
    if is_processed(message_id):
        continue

    # Fetch full message
    message = fetch_message(message_id)

    # Extract metadata
    email_data = extract_email_data(message)

    # Classify priority and category
    priority = classify_priority(email_data)
    category = classify_category(email_data)

    # Create action item
    create_action_item(email_data, priority, category)

    # Mark as processed
    mark_processed(message_id)
```

### Phase 4: Item Creation

```python
def create_action_item(email_data, priority, category):
    filename = f"EMAIL_{timestamp}_{email_data['id'][:8]}.md"

    content = f"""---
type: email
id: {email_data['id']}
from: {email_data['from']}
to: {email_data['to']}
subject: {email_data['subject']}
received: {email_data['date']}
priority: {priority}
category: {category}
status: pending
processed: {datetime.now().isoformat()}
---

# Email Content

## From
{email_data['from_name']} <{email_data['from_email']}>

## Subject
{email_data['subject']}

## Body
{email_data['body']}

## Suggested Actions
- [ ] Read and categorize
- [ ] Determine response needed
- [ ] Check for attachments

## Metadata
- Thread ID: {email_data['thread_id']}
- Labels: {email_data['labels']}
- Attachments: {len(email_data['attachments'])}
"""

    write_file(f"vault/Needs_Action/{filename}", content)
```

## Configuration

```yaml
# vault/.config/gmail_watcher.yaml

gmail:
  # API Configuration
  credentials_path: ".credentials/gmail_credentials.json"
  token_path: ".credentials/gmail_token.json"

  # Polling Configuration
  poll_interval: 120  # seconds
  batch_size: 50  # messages per API call

  # Query Filters
  query: "is:unread -in:spam -in:trash"

  # Label Filters (only process these labels)
  include_labels:
    - IMPORTANT
    - INBOX
    - CATEGORY_PERSONAL
    - CATEGORY_UPDATES

  # Exclude Labels
  exclude_labels:
    - SPAM
    - TRASH
    - CATEGORY_PROMOTIONS
    - CATEGORY_SOCIAL

  # Priority Detection
  priority_keywords:
    urgent:
      - "ASAP"
      - "urgent"
      - "critical"
      - "emergency"
    high:
      - "invoice"
      - "payment"
      - "meeting"
      - "deadline"

  # Auto-Archive Rules
  auto_archive:
    enabled: false  # Require approval first
    after_processing: true
    labels_to_apply:
      - "AI-Processed"

  # Rate Limiting
  rate_limit:
    max_messages_per_poll: 50
    max_api_calls_per_hour: 100
```

## Gmail API Setup

### Prerequisites

```bash
# 1. Create Google Cloud Project
# Go to console.cloud.google.com

# 2. Enable Gmail API
# APIs & Services → Enable APIs → Gmail API

# 3. Create OAuth 2.0 Credentials
# APIs & Services → Credentials → Create Credentials → OAuth client ID
# Application type: Desktop app

# 4. Download credentials.json
# Save to .credentials/gmail_credentials.json

# 5. Run initial authentication
python scripts/gmail_auth.py
```

### Authentication Script

```python
# scripts/gmail_auth.py

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from pathlib import Path

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    creds_path = Path('.credentials/gmail_credentials.json')
    token_path = Path('.credentials/gmail_token.json')

    flow = InstalledAppFlow.from_client_secrets_file(
        creds_path, SCOPES
    )

    credentials = flow.run_local_server(port=0)

    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(credentials.to_json())

    print("Authentication successful!")
    print(f"Token saved to {token_path}")

if __name__ == "__main__":
    authenticate()
```

## Watcher Script

```python
# scripts/gmail_watcher.py

#!/usr/bin/env python3
"""
Gmail Watcher - Monitors Gmail for new messages and creates action items.

Usage:
    python scripts/gmail_watcher.py --vault ./vault
    python scripts/gmail_watcher.py --once  # Single run
    python scripts/gmail_watcher.py --dry-run  # No file creation
"""

import argparse
import logging
import json
import time
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GmailWatcher:
    def __init__(self, vault_path: str, dry_run: bool = False):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.processed_ids_path = self.vault_path / ".processed_ids.json"
        self.dry_run = dry_run
        self.processed_ids = self._load_processed_ids()
        self.credentials = self._load_credentials()
        self.service = build('gmail', 'v1', credentials=self.credentials)
        self.logger = logging.getLogger(__name__)

    def _load_processed_ids(self) -> set:
        if self.processed_ids_path.exists():
            return set(json.loads(self.processed_ids_path.read_text()))
        return set()

    def _save_processed_ids(self):
        if not self.dry_run:
            self.processed_ids_path.write_text(
                json.dumps(list(self.processed_ids))
            )

    def _load_credentials(self) -> Credentials:
        token_path = Path(".credentials/gmail_token.json")
        return Credentials.from_authorized_user_file(token_path)

    def check_for_messages(self) -> list:
        results = self.service.users().messages().list(
            userId='me',
            q='is:unread -in:spam -in:trash',
            maxResults=50
        ).execute()

        messages = results.get('messages', [])
        return [m for m in messages if m['id'] not in self.processed_ids]

    def fetch_message(self, message_id: str) -> dict:
        return self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()

    def extract_email_data(self, message: dict) -> dict:
        headers = {h['name']: h['value'] for h in message['payload']['headers']}

        # Extract body
        body = self._extract_body(message['payload'])

        return {
            'id': message['id'],
            'thread_id': message['thread_id'],
            'from': headers.get('From', 'Unknown'),
            'to': headers.get('To', ''),
            'subject': headers.get('Subject', 'No Subject'),
            'date': headers.get('Date', ''),
            'body': body,
            'labels': message.get('labelIds', []),
            'attachments': self._extract_attachments(message['payload'])
        }

    def _extract_body(self, payload: dict) -> str:
        if 'body' in payload and 'data' in payload['body']:
            import base64
            return base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8')

        if 'parts' in payload:
            for part in payload['parts']:
                body = self._extract_body(part)
                if body:
                    return body

        return message.get('snippet', '')

    def _extract_attachments(self, payload: dict) -> list:
        attachments = []
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('filename'):
                    attachments.append({
                        'filename': part['filename'],
                        'mime_type': part['mimeType'],
                        'size': part['body'].get('size', 0)
                    })
        return attachments

    def create_action_item(self, email_data: dict, priority: str, category: str):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"EMAIL_{timestamp}_{email_data['id'][:8]}.md"

        content = f"""---
type: email
id: {email_data['id']}
from: {email_data['from']}
subject: {email_data['subject']}
received: {email_data['date']}
priority: {priority}
category: {category}
status: pending
processed: {datetime.now().isoformat()}
---

## Email Content

**From:** {email_data['from']}
**Subject:** {email_data['subject']}
**Date:** {email_data['date']}

{email_data['body'][:2000]}

---
*Email ID: {email_data['id']}*
*Labels: {', '.join(email_data['labels'])}*
*Attachments: {len(email_data['attachments'])}*
"""

        if not self.dry_run:
            self.needs_action.mkdir(parents=True, exist_ok=True)
            (self.needs_action / filename).write_text(content)
            self.logger.info(f"Created action item: {filename}")
        else:
            self.logger.info(f"[DRY RUN] Would create: {filename}")

    def run_once(self):
        self.logger.info("Checking for new messages...")
        messages = self.check_for_messages()
        self.logger.info(f"Found {len(messages)} new messages")

        for msg in messages:
            try:
                email_data = self.fetch_message(msg['id'])
                priority = self._classify_priority(email_data)
                category = self._classify_category(email_data)
                self.create_action_item(email_data, priority, category)
                self.processed_ids.add(msg['id'])
            except Exception as e:
                self.logger.error(f"Error processing {msg['id']}: {e}")

        self._save_processed_ids()

    def run_forever(self, interval: int = 120):
        self.logger.info(f"Starting Gmail watcher (interval: {interval}s)")
        while True:
            try:
                self.run_once()
            except Exception as e:
                self.logger.error(f"Error in watch cycle: {e}")

            time.sleep(interval)

    def _classify_priority(self, email_data: dict) -> str:
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        combined = subject + ' ' + body

        urgent_keywords = ['asap', 'urgent', 'critical', 'emergency']
        high_keywords = ['invoice', 'payment', 'meeting', 'deadline']

        if any(kw in combined for kw in urgent_keywords):
            return 'urgent'
        if any(kw in combined for kw in high_keywords):
            return 'high'
        return 'normal'

    def _classify_category(self, email_data: dict) -> str:
        combined = (email_data.get('subject', '') + ' ' +
                   email_data.get('body', '')).lower()

        categories = {
            'invoice': ['invoice', 'payment', 'bill', 'receipt'],
            'meeting': ['meeting', 'schedule', 'call', 'zoom'],
            'support': ['help', 'issue', 'problem', 'bug'],
            'legal': ['legal', 'contract', 'attorney', 'lawsuit']
        }

        for category, keywords in categories.items():
            if any(kw in combined for kw in keywords):
                return category

        return 'general'

def main():
    parser = argparse.ArgumentParser(description='Gmail Watcher')
    parser.add_argument('--vault', default='./vault', help='Vault path')
    parser.add_argument('--once', action='store_true', help='Run once')
    parser.add_argument('--dry-run', action='store_true', help='No file creation')
    parser.add_argument('--interval', type=int, default=120, help='Poll interval')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    watcher = GmailWatcher(args.vault, args.dry_run)

    if args.once:
        watcher.run_once()
    else:
        watcher.run_forever(args.interval)

if __name__ == "__main__":
    main()
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Credentials expired | Refresh token automatically |
| API rate limit | Backoff and retry |
| Network timeout | Retry with exponential backoff |
| Quota exceeded | Wait until quota reset, alert human |
| Invalid message | Log error, skip message, continue |

## Monitoring

```yaml
health_check:
  endpoint: /health
  response:
    status: ok|degraded|error
    last_check: timestamp
    messages_processed: count
    errors_last_hour: count
    uptime_seconds: duration

metrics:
  - messages_processed_total
  - messages_processed_last_hour
  - api_calls_total
  - api_errors_total
  - processing_time_seconds
```

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Action Items | `Needs_Action/EMAIL_*.md` | Processing queue |
| Processed IDs | `.processed_ids.json` | Deduplication |
| Watcher Log | `Logs/gmail_watcher.log` | Debugging |
| Metrics | `Logs/gmail_metrics.json` | Monitoring |

## References

| File | Purpose |
|------|---------|
| `references/gmail-api.md` | Gmail API documentation |
| `references/authentication.md` | OAuth setup guide |
| `references/filters.md` | Query filter reference |