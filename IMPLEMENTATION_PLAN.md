# Implementation Plan - Complete Silver & Gold Tiers
**Based on:** TIER_AUDIT.md findings
**Goal:** Transform from automation framework to actual AI Employee

---

## Phase 1: Critical Foundation (MUST DO FIRST)

### 1.1 Implement Claude Code Integration
**Current:** `trigger_claude()` uses rule-based processing
**Required:** Actual Claude API calls

**Implementation:**
```python
# orchestrator.py - Replace trigger_claude()

import anthropic
import os

def trigger_claude(self, prompt: str) -> bool:
    """Actually call Claude API for reasoning."""
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    # Read context from vault
    handbook = (self.vault_path / "Company_Handbook.md").read_text()
    goals = (self.vault_path / "Business_Goals.md").read_text()

    system_prompt = f"""You are a Personal AI Employee managing business affairs.

{handbook}

{goals}

Process the following item and determine the appropriate action."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )

        response = message.content[0].text
        self.logger.info(f"Claude response: {response[:200]}...")

        # Parse response and execute actions
        return self._execute_claude_response(response)

    except Exception as e:
        self.logger.error(f"Claude API error: {e}")
        return False
```

**Files to modify:**
- `orchestrator.py` - Replace `trigger_claude()` method
- Create `.env.example` with `ANTHROPIC_API_KEY=your_key_here`

**Estimated time:** 2-3 hours

---

### 1.2 Create requirements.txt
**Current:** Missing
**Required:** Document all dependencies

**Implementation:**
```txt
# Core
anthropic>=0.40.0
python-dotenv>=1.0.0

# Email & Auth
google-auth>=2.35.0
google-auth-oauthlib>=1.2.0
google-auth-httplib2>=0.2.0
google-api-python-client>=2.150.0

# Browser Automation
playwright>=1.48.0

# MCP & APIs
mcp>=1.0.0
requests>=2.32.0
tweepy>=4.14.0  # Twitter API (optional, using browser instead)

# Odoo Integration
xmlrpc2>=0.3.1  # or use built-in xmlrpc.client

# Utilities
watchdog>=5.0.0  # File watching
schedule>=1.2.0  # Task scheduling
pyyaml>=6.0.2
markdown>=3.7
```

**Files to create:**
- `requirements.txt`
- `.env.example`

**Estimated time:** 30 minutes

---

### 1.3 Implement Email Sending
**Current:** Only creates drafts
**Required:** Actually send via Gmail API

**Implementation:**
```python
# mcp/email/server.py - Replace send_email()

def send_email(self, params: dict) -> dict:
    """Actually send an email via Gmail API."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    import base64
    from email.mime.text import MIMEText

    # Load credentials
    creds_path = self.vault_path / 'secrets' / 'gmail_token.json'
    if not creds_path.exists():
        return {"error": "Gmail credentials not found"}

    creds = Credentials.from_authorized_user_file(str(creds_path))
    service = build('gmail', 'v1', credentials=creds)

    # Create message
    message = MIMEText(params['body'])
    message['to'] = params['to']
    message['subject'] = params['subject']
    if params.get('cc'):
        message['cc'] = params['cc']

    # Encode and send
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        sent = service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()

        self.logger.info(f"Email sent: {sent['id']}")
        return {
            "status": "sent",
            "message_id": sent['id']
        }
    except Exception as e:
        self.logger.error(f"Send error: {e}")
        return {"error": str(e)}
```

**Files to modify:**
- `mcp/email/server.py` - Replace `send_email()` method

**Estimated time:** 1-2 hours

---

### 1.4 Implement Email Search
**Current:** Returns "not_implemented"
**Required:** Search via Gmail API

**Implementation:**
```python
# mcp/email/server.py - Replace search_emails()

def search_emails(self, params: dict) -> dict:
    """Search emails via Gmail API."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds_path = self.vault_path / 'secrets' / 'gmail_token.json'
    if not creds_path.exists():
        return {"error": "Gmail credentials not found"}

    creds = Credentials.from_authorized_user_file(str(creds_path))
    service = build('gmail', 'v1', credentials=creds)

    query = params.get('query', '')
    max_results = params.get('max_results', 10)

    try:
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()

        messages = results.get('messages', [])

        # Fetch full message details
        emails = []
        for msg in messages:
            full_msg = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()

            headers = {h['name']: h['value'] for h in full_msg['payload']['headers']}
            emails.append({
                'id': msg['id'],
                'from': headers.get('From'),
                'subject': headers.get('Subject'),
                'date': headers.get('Date')
            })

        return {
            "status": "success",
            "count": len(emails),
            "emails": emails
        }
    except Exception as e:
        return {"error": str(e)}
```

**Files to modify:**
- `mcp/email/server.py` - Replace `search_emails()` method

**Estimated time:** 1-2 hours

---

## Phase 2: Complete Approval Workflow

### 2.1 Add Approval Notifications
**Current:** User must manually check folders
**Required:** Notify user when approval needed

**Implementation:**
```python
# orchestrator.py - Add notification method

def notify_approval_needed(self, item: Path):
    """Notify user that approval is needed."""
    import json

    # Load webhook config
    webhook_config = self.vault_path / 'secrets' / 'webhooks.json'
    if webhook_config.exists():
        config = json.loads(webhook_config.read_text())

        # Send to Slack
        if config.get('webhooks', {}).get('slack'):
            self._send_slack_notification(
                config['webhooks']['slack'],
                f"⚠️ Approval needed: {item.name}"
            )

        # Send to Discord
        if config.get('webhooks', {}).get('discord'):
            self._send_discord_notification(
                config['webhooks']['discord'],
                f"⚠️ Approval needed: {item.name}"
            )

    # Also log to activity
    self.log_activity('approval_requested', {
        'item': item.name,
        'timestamp': datetime.now().isoformat()
    })

def _send_slack_notification(self, webhook_url: str, message: str):
    """Send Slack notification."""
    import requests
    requests.post(webhook_url, json={'text': message})

def _send_discord_notification(self, webhook_url: str, message: str):
    """Send Discord notification."""
    import requests
    requests.post(webhook_url, json={'content': message})
```

**Files to modify:**
- `orchestrator.py` - Add notification methods
- Call `notify_approval_needed()` when creating approval requests

**Estimated time:** 2 hours

---

### 2.2 Create Approval Web UI (Optional but Recommended)
**Current:** Manual file moving
**Required:** Web interface for approvals

**Implementation:**
```python
# hooks/approval_ui.py - Simple Flask UI

from flask import Flask, render_template, request, redirect
from pathlib import Path
import json

app = Flask(__name__)
vault_path = Path('./vault')

@app.route('/approvals')
def list_approvals():
    """Show pending approvals."""
    pending = vault_path / 'Pending_Approval'
    items = []

    for f in pending.glob('*.md'):
        content = f.read_text()
        items.append({
            'filename': f.name,
            'content': content,
            'preview': content[:500]
        })

    return render_template('approvals.html', items=items)

@app.route('/approve/<filename>', methods=['POST'])
def approve(filename):
    """Approve an item."""
    pending = vault_path / 'Pending_Approval' / filename
    approved = vault_path / 'Approved' / filename

    if pending.exists():
        pending.rename(approved)
        return redirect('/approvals')

    return "Not found", 404

@app.route('/reject/<filename>', methods=['POST'])
def reject(filename):
    """Reject an item."""
    pending = vault_path / 'Pending_Approval' / filename
    rejected = vault_path / 'Rejected' / filename

    if pending.exists():
        pending.rename(rejected)
        return redirect('/approvals')

    return "Not found", 404

if __name__ == '__main__':
    app.run(port=8081)
```

**Files to create:**
- `hooks/approval_ui.py`
- `hooks/templates/approvals.html`

**Estimated time:** 3-4 hours

---

## Phase 3: Test & Validate

### 3.1 Integration Tests
Create tests to verify each component works:

```python
# tests/test_integration.py

def test_email_sending():
    """Test email MCP server actually sends."""
    from mcp.email.server import EmailMCPServer

    server = EmailMCPServer()
    result = server.send_email({
        'to': 'test@example.com',
        'subject': 'Test',
        'body': 'Test email'
    })

    assert result['status'] == 'sent'
    assert 'message_id' in result

def test_claude_integration():
    """Test orchestrator calls Claude."""
    from orchestrator import Orchestrator

    orch = Orchestrator('./vault', dry_run=False)
    result = orch.trigger_claude("Test prompt")

    assert result == True
    # Verify Claude was actually called

def test_approval_workflow():
    """Test approval notifications work."""
    from orchestrator import Orchestrator
    from pathlib import Path

    orch = Orchestrator('./vault')
    test_file = Path('./vault/Pending_Approval/test.md')
    test_file.write_text('test')

    orch.notify_approval_needed(test_file)
    # Verify notification was sent
```

**Files to create:**
- `tests/test_integration.py`
- `tests/test_mcp_servers.py`
- `tests/test_orchestrator.py`

**Estimated time:** 4-6 hours

---

## Phase 4: Documentation & Polish

### 4.1 Update Documentation
- Update README.md with accurate status
- Update CLAUDE.md with correct implementation details
- Create SETUP.md with step-by-step instructions
- Create TROUBLESHOOTING.md

### 4.2 Add Monitoring
- Health checks for all MCP servers
- Error tracking and alerting
- Performance metrics

---

## Implementation Timeline

### Week 1: Critical Foundation
- Day 1-2: Claude integration (1.1)
- Day 3: Requirements & email sending (1.2, 1.3)
- Day 4: Email search (1.4)
- Day 5: Testing & debugging

### Week 2: Approval Workflow
- Day 1-2: Notifications (2.1)
- Day 3-4: Web UI (2.2)
- Day 5: Testing & integration

### Week 3: Testing & Polish
- Day 1-3: Integration tests (3.1)
- Day 4-5: Documentation (4.1, 4.2)

**Total estimated time:** 60-80 hours

---

## Success Criteria

### Silver Tier Complete When:
- ✅ Claude API integration working
- ✅ Email sending functional
- ✅ Email search functional
- ✅ Approval workflow with notifications
- ✅ Dry-run mode consistent
- ✅ All tests passing

### Gold Tier Complete When:
- ✅ All Silver tier criteria met
- ✅ Odoo integration tested and working
- ✅ Social media posting tested
- ✅ CEO Briefing generates correctly
- ✅ Ralph Wiggum loop calls Claude
- ✅ System operates autonomously for 24 hours

---

## Priority Order

1. **CRITICAL** - Claude integration (without this, it's not an AI employee)
2. **HIGH** - Email sending (core functionality)
3. **HIGH** - Email search (needed for context)
4. **MEDIUM** - Approval notifications (UX improvement)
5. **MEDIUM** - Testing (quality assurance)
6. **LOW** - Web UI (nice to have)
7. **LOW** - Documentation polish

---

## Quick Start (Minimum Viable)

If you only have 8 hours, do this:

1. **Hour 1-3:** Implement Claude integration (1.1)
2. **Hour 4-5:** Implement email sending (1.3)
3. **Hour 6-7:** Test end-to-end workflow
4. **Hour 8:** Update documentation

This gives you a working AI employee that can:
- Read emails
- Use Claude to decide actions
- Send email responses
- Log activities

Everything else is enhancement.
