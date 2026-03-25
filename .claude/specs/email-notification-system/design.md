---
spec_id: SPEC-001
title: Email Notification System
status: approved
created: 2026-03-18
last_updated: 2026-03-18
phase: design_approved
---

# Email Notification System - Design

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Gmail API      │────▶│  Email Watcher   │────▶│  Classifier     │
│  (External)     │     │  (Python)        │     │  (Rules Engine) │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                    ┌─────────────────────────────────────┼─────────────────────────────────────┐
                    │                                     │                                     │
                    ▼                                     ▼                                     ▼
          ┌──────────────────┐                  ┌──────────────────┐                  ┌──────────────────┐
          │   Urgent Email   │                  │   Invoice Email  │                  │   Normal Email   │
          │   Handler        │                  │   Handler        │                  │   Handler        │
          └────────┬─────────┘                  └────────┬─────────┘                  └────────┬─────────┘
                   │                                     │                                     │
                   ▼                                     ▼                                     ▼
          ┌──────────────────┐                  ┌──────────────────┐                  ┌──────────────────┐
          │   WhatsApp       │                  │   Needs_Action   │                  │   Dashboard      │
          │   Notification   │                  │   File Created   │                  │   Update         │
          └──────────────────┘                  └──────────────────┘                  └──────────────────┘
```

## Component Diagram

### 1. Email Watcher Component
**File**: `watchers/email_watcher.py`

**Responsibilities**:
- Poll Gmail API every 5 minutes
- Detect new emails using message ID tracking
- Extract email metadata (sender, subject, timestamp, attachments)
- Handle authentication and token refresh

**Key Classes**:
```python
class EmailWatcher:
    - __init__(config: dict)
    - check_new_emails() -> List[Email]
    - mark_as_processed(message_id: str)
    - get_unread_count() -> int

class Email:
    - message_id: str
    - sender: str
    - subject: str
    - body: str
    - attachments: List[Attachment]
    - timestamp: datetime
    - is_read: bool
```

### 2. Email Classifier Component
**File**: `watchers/email_classifier.py`

**Responsibilities**:
- Apply categorization rules
- Detect invoices and financial emails
- Calculate sender priority
- Determine notification urgency

**Categorization Rules**:
```python
CATEGORIES = {
    "urgent": {
        "keywords": ["urgent", "asap", "emergency", "critical"],
        "senders": "vip_list",
        "notification": "whatsapp"
    },
    "invoice": {
        "keywords": ["invoice", "payment", "receipt", "bill"],
        "attachments": ["pdf"],
        "notification": "needs_action"
    },
    "important": {
        "senders": "contact_list",
        "notification": "dashboard"
    },
    "promotional": {
        "keywords": ["unsubscribe", "promotion", "sale"],
        "notification": "ignore"
    }
}
```

### 3. Notification Handler Component
**File**: `watchers/notification_handler.py`

**Responsibilities**:
- Send WhatsApp notifications via MCP
- Update Dashboard.md
- Create action files in vault
- Log all notification activities

**Notification Flow**:
```python
def handle_urgent_email(email: Email):
    # 1. Send WhatsApp notification
    whatsapp_message = format_urgent_notification(email)
    await mcp_whatsapp.send(whatsapp_message)
    
    # 2. Update Dashboard
    update_dashboard_status(email)
    
    # 3. Log activity
    log_email_activity(email, action="whatsapp_notification")
```

## Data Models

### Email Metadata Schema
```json
{
  "message_id": "string",
  "thread_id": "string",
  "sender": {
    "email": "string",
    "name": "string",
    "priority": "high|medium|low"
  },
  "subject": "string",
  "snippet": "string",
  "body": "string",
  "attachments": [
    {
      "filename": "string",
      "mime_type": "string",
      "size": "integer"
    }
  ],
  "timestamp": "ISO8601",
  "labels": ["string"],
  "category": "urgent|invoice|important|normal|promotional",
  "processed": "boolean"
}
```

### Configuration Schema
```yaml
# config/email_watcher.yaml
gmail:
  credentials_file: ".credentials/gmail_credentials.json"
  token_file: ".credentials/gmail_token.json"
  poll_interval_seconds: 300
  max_results: 50

notifications:
  whatsapp:
    enabled: true
    recipient: "+1234567890"
    urgent_keywords: ["urgent", "asap", "emergency"]
  
  dashboard:
    enabled: true
    update_interval: 60

categories:
  vip_senders:
    - "boss@company.com"
    - "client@important.com"
  
  invoice_keywords:
    - "invoice"
    - "payment"
    - "receipt"
  
  promotional_keywords:
    - "unsubscribe"
    - "promotion"

daily_summary:
  enabled: true
  time: "20:00"
  timezone: "UTC"
```

## API Design

### Gmail API Integration
```python
# Use Gmail API for email fetching
GET /gmail/v1/users/me/messages
  - q: "is:unread"
  - maxResults: 50

GET /gmail/v1/users/me/messages/{messageId}
  - format: "full"
  - fields: "id,threadId,labelIds,snippet,internalDate,payload"
```

### MCP WhatsApp Integration
```python
# Use WhatsApp MCP for notifications
await mcp.whatsapp.send_message(
    recipient="+1234567890",
    message="🚨 Urgent Email from boss@company.com\nSubject: Critical Issue\nTime: 2:30 PM"
)
```

## Integration Points

### Gmail MCP Server
- Configuration: `mcp_servers/gmail-mcp.json`
- Handles OAuth authentication
- Manages API rate limits
- Caches email metadata

### WhatsApp MCP Server
- Configuration: `mcp_servers/whatsapp-mcp.json`
- Sends notifications to user
- Supports markdown formatting
- Delivery confirmation

### File System Watcher
- Monitors config changes
- Updates behavior without restart
- Hot-reload support

## Security Considerations

### Authentication
- OAuth 2.0 for Gmail API
- Token stored encrypted in `.credentials/`
- Automatic token refresh
- Never commit credentials to git

### Data Protection
- Email content encrypted at rest
- Sensitive data excluded from logs
- Secure deletion of processed emails
- Access control on vault files

### Rate Limiting
- Gmail API: 1 billion requests/day (generous limit)
- WhatsApp: Respect user limits
- Exponential backoff on errors

## Error Handling

### Error Categories
```python
class EmailWatcherError(Exception):
    pass

class GmailAPIError(EmailWatcherError):
    - rate_limit_exceeded
    - authentication_failed
    - quota_exceeded

class NotificationError(EmailWatcherError):
    - whatsapp_unavailable
    - dashboard_write_failed
    - log_write_failed
```

### Recovery Strategy
```python
async def check_emails_with_retry():
    max_retries = 3
    backoff_seconds = 120
    
    for attempt in range(max_retries):
        try:
            return await email_watcher.check_new_emails()
        except GmailAPIError as e:
            if attempt == max_retries - 1:
                log_error("Max retries exceeded", e)
                update_dashboard_error()
                return []
            await asyncio.sleep(backoff_seconds * (attempt + 1))
```

## Testing Strategy

### Unit Tests
```python
# tests/test_email_classifier.py
def test_urgent_email_detection():
    email = Email(subject="URGENT: Server Down", sender="boss@company.com")
    assert classifier.categorize(email) == "urgent"

def test_invoice_detection():
    email = Email(subject="Invoice #123", attachments=[Attachment("invoice.pdf")])
    assert classifier.categorize(email) == "invoice"
```

### Integration Tests
```python
# tests/test_email_watcher_integration.py
async def test_end_to_end_flow():
    # Setup test email
    # Run watcher
    # Verify WhatsApp notification
    # Verify Dashboard update
    # Verify log entry
```

### E2E Tests
```python
# tests/test_email_notification_e2e.py
async def test_urgent_email_notification():
    # Send real email to test account
    # Wait for watcher to detect
    # Verify WhatsApp message received
    # Verify Dashboard.md updated
```

## Migration Plan

### Phase 1: Setup (Week 1)
- Create Gmail MCP configuration
- Set up OAuth credentials
- Implement basic email fetching

### Phase 2: Classification (Week 2)
- Implement categorization rules
- Build sender priority system
- Test classification accuracy

### Phase 3: Notifications (Week 3)
- Integrate WhatsApp MCP
- Implement Dashboard updates
- Build logging system

### Phase 4: Polish (Week 4)
- Add daily summary feature
- Implement error recovery
- Performance optimization
- Documentation

---

**Status**: ✅ Design Approved
**Next Phase**: Task Generation
**Approved By**: Judge Agent
**Approval Date**: 2026-03-18
