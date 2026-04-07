# WhatsApp Automation - Complete Implementation Guide

## Overview

This implementation provides **full WhatsApp automation** for the Personal AI Employee system. It enables:

- **Real-time message monitoring** via WhatsApp Web
- **Automatic action file creation** for Claude Code processing
- **Human-in-the-loop approval workflow** for sensitive actions
- **Automated message sending** via Playwright browser automation
- **Integration with existing vault structure** (Needs_Action, Plans, Approved, Done)

## Architecture

```
WhatsApp Web → Playwright Browser → WhatsApp Watcher → Needs_Action/ → Claude Code → Plans/ → Approval → MCP Server → Send Message
```

### Components

| Component | File | Purpose |
|-----------|------|---------|
| **WhatsApp Watcher** | `watchers/whatsapp_watcher.py` | Monitors WhatsApp Web for new messages |
| **WhatsApp Orchestrator** | `watchers/whatsapp_orchestrator.py` | Manages workflow and AI integration |
| **WhatsApp MCP Server** | `mcp_servers/whatsapp_mcp.py` | Provides WhatsApp capabilities to Claude Code |
| **Start Script** | `scripts/start_whatsapp.sh` | Launches the automation |
| **Stop Script** | `scripts/stop_whatsapp.sh` | Gracefully stops automation |

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
python3 -m playwright install chromium

# Verify installation
python3 -c "import playwright; print('✓ Playwright installed')"
python3 -c "import mcp; print('✓ MCP installed')"
```

### 2. Configure Vault Path

```bash
# Set environment variable (optional)
export OBSIDIAN_VAULT_PATH="/path/to/your/vault"

# Or use default (current directory)
export OBSIDIAN_VAULT_PATH="."
```

### 3. Start WhatsApp Automation

```bash
# Start the automation
bash scripts/start_whatsapp.sh
```

### 4. Login to WhatsApp

1. A Chrome browser window will open with WhatsApp Web
2. **Scan the QR code with your mobile phone**
3. Wait for "WhatsApp login successful!" message in terminal
4. The watcher will begin monitoring for new messages

### 5. Monitor Activity

```bash
# Check logs
tail -f vault/Logs/whatsapp_*.md

# Check dashboard
cat vault/Dashboard.md

# View pending actions
ls -la vault/Needs_Action/WHATSAPP_*.md
```

## How It Works

### Message Flow

1. **Detection**: WhatsApp Watcher checks WhatsApp Web every 30 seconds
2. **Extraction**: New messages are extracted with chat name, content, timestamp
3. **Classification**: Messages are checked for trigger keywords (urgent, invoice, payment, etc.)
4. **Action File**: Created in `Needs_Action/WHATSAPP_<sender>_<timestamp>.md`
5. **AI Processing**: Claude Code analyzes and creates response plan
6. **Approval**: Response requires human approval (move to Approved/)
7. **Execution**: MCP server sends the message via WhatsApp Web

### Trigger Keywords

Messages containing these keywords trigger immediate AI processing:

- `urgent`, `asap`, `invoice`, `payment`, `help`
- `emergency`, `deadline`, `important`, `check this`
- `review`, `approve`, `send`, `transfer`, `money`, `bank`, `account`

### Action File Format

```markdown
---
type: whatsapp_message
from: John Doe
received: 2026-04-06T12:00:00
priority: HIGH
status: pending
trigger_keywords: true
created: 2026-04-06T12:00:00
---

# WhatsApp Message

## Sender
John Doe

## Message Content
Hi, I need the invoice for last month urgently.

## Classification
- **Priority**: HIGH
- **Contains Trigger Words**: true

## Suggested Actions
- [ ] Review message content
- [ ] Draft response (if needed)
- [ ] Move to Approved folder to send response
- [ ] Archive after processing
```

## Approval Workflow

### For Claude Code (AI)

When Claude needs to send a WhatsApp message:

1. **Create Approval Request**:
   ```
   Use MCP tool: create_whatsapp_approval_request
   - recipient: "John Doe"
   - message: "Here's your invoice..."
   - reason: "Response to urgent request"
   ```

2. **File Created**: `Pending_Approval/WHATSAPP_MSG_John_Doe_<timestamp>.md`

3. **Human Review**: User reviews the approval request

4. **Approve**: Move file to `Approved/` folder
   ```bash
   mv vault/Pending_Approval/WHATSAPP_MSG_*.md vault/Approved/
   ```

5. **Execution**: Orchestrator detects approved file and sends message via MCP

6. **Completion**: File moved to `Done/SENT_WHATSAPP_MSG_*.md`

### Manual WhatsApp Actions

You can also create approval requests manually:

```bash
# Create manual approval request
cat > vault/Pending_Approval/MANUAL_WHATSAPP_test.md << EOF
---
type: whatsapp_approval_request
action: send_whatsapp_message
recipient: John Doe
created: $(date -Iseconds)
status: pending
---

# WhatsApp Message Approval Request

## Message Details
- **To**: John Doe
- **Message**: Hello! This is a test message from AI Employee.

## To Approve
Move this file to the `Approved` folder.
EOF

# Approve by moving to Approved
mv vault/Pending_Approval/MANUAL_WHATSAPP_test.md vault/Approved/
```

## MCP Tools Available

### send_whatsapp_message

Send a WhatsApp message (with optional approval requirement).

```python
# Direct send (not recommended for production)
{
    "tool": "send_whatsapp_message",
    "arguments": {
        "recipient": "John Doe",
        "message": "Hello!",
        "requires_approval": false
    }
}

# With approval (recommended)
{
    "tool": "send_whatsapp_message",
    "arguments": {
        "recipient": "John Doe",
        "message": "Hello!",
        "requires_approval": true
    }
}
```

### read_whatsapp_messages

Read recent messages from WhatsApp.

```python
{
    "tool": "read_whatsapp_messages",
    "arguments": {
        "chat_name": "John Doe",  # Optional
        "limit": 10
    }
}
```

### get_whatsapp_status

Get current WhatsApp connection status.

```python
{
    "tool": "get_whatsapp_status",
    "arguments": {}
}
```

### create_whatsapp_approval_request

Create an approval request for sending a message.

```python
{
    "tool": "create_whatsapp_approval_request",
    "arguments": {
        "recipient": "John Doe",
        "message": "Invoice attached",
        "reason": "Monthly invoice delivery"
    }
}
```

### process_whatsapp_approval

Process a pending approval request.

```python
{
    "tool": "process_whatsapp_approval",
    "arguments": {
        "approval_id": "WHATSAPP_MSG_John_Doe_20260406_120000.md",
        "action": "approve"  # or "reject"
    }
}
```

## Configuration

### Environment Variables

```bash
# Vault path (default: current directory)
export OBSIDIAN_VAULT_PATH="/path/to/vault"

# Session storage (default: $VAULT_PATH/.whatsapp_session)
export WHATSAPP_SESSION_PATH="/path/to/session"

# Check interval in seconds (default: 30)
export WHATSAPP_CHECK_INTERVAL=60

# Browser mode (default: false = visible)
export WHATSAPP_HEADLESS=true
```

### Custom Trigger Keywords

Edit `watchers/whatsapp_watcher.py`:

```python
self.trigger_keywords = [
    'urgent', 'asap', 'invoice', 'payment', 'help',
    # Add your custom keywords here
    'custom_keyword'
]
```

## Troubleshooting

### QR Code Not Appearing

```bash
# Clear session and restart
rm -rf vault/.whatsapp_session/*
bash scripts/start_whatsapp.sh
```

### WhatsApp Web Not Loading

```bash
# Check Playwright installation
python3 -m playwright install chromium

# Test browser
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://web.whatsapp.com')
    import time; time.sleep(5)
    browser.close()
print('✓ Browser test successful')
"
```

### Messages Not Being Detected

```bash
# Check watcher logs
tail -f vault/Logs/whatsapp_*.md

# Test watcher manually
python3 watchers/whatsapp_watcher.py --vault . --test

# Verify WhatsApp is logged in
# Browser should show chat list, not QR code
```

### Approval Not Being Processed

```bash
# Check approved folder
ls -la vault/Approved/

# Check orchestrator logs
tail -f vault/Logs/whatsapp_orchestrator_*.md

# Verify file format
cat vault/Approved/WHATSAPP_*.md
```

## Security Considerations

### What's Stored Locally

- **WhatsApp Session**: Browser cookies and session data in `.whatsapp_session/`
- **Messages**: Only processed messages are stored in vault (markdown files)
- **No Cloud Storage**: All data stays on your machine

### What's NOT Stored

- Full message history (only action files)
- Media files (images, videos, voice messages)
- Contact lists
- Phone numbers

### Best Practices

1. **Never commit session data to Git**:
   ```bash
   echo ".whatsapp_session/" >> .gitignore
   ```

2. **Use approval workflow for all messages**:
   - Set `requires_approval: true` in MCP calls
   - Review all approval requests before approving

3. **Monitor logs regularly**:
   ```bash
   tail -f vault/Logs/whatsapp_*.md
   ```

4. **Limit trigger keywords** to reduce false positives

## Advanced Usage

### Custom Response Templates

Create response templates in `vault/Templates/`:

```markdown
# vault/Templates/invoice_response.md
---
type: response_template
category: invoice
---

Hi {name},

Thank you for your request. Please find the invoice attached.

Best regards,
AI Employee
```

### Integration with Odoo

Link WhatsApp automation with Odoo accounting:

```python
# Example: Send invoice via WhatsApp
from watchers.whatsapp_watcher import WhatsAppWatcher

watcher = WhatsAppWatcher(vault_path=".")

# Get invoice from Odoo
invoice_data = get_invoice_from_odoo(customer_email)

# Send via WhatsApp
watcher._send_message(
    chat_name=customer_name,
    message=f"Hi {customer_name},\n\nYour invoice #{invoice_data['number']} is ready.\nAmount: ${invoice_data['amount']}"
)
```

### Scheduled Reports

Create a cron job for weekly WhatsApp reports:

```bash
# Add to crontab
0 9 * * 1 bash scripts/whatsapp_weekly_report.sh
```

## Performance Tuning

### Reduce Check Interval

For faster response (more CPU usage):

```bash
export WHATSAPP_CHECK_INTERVAL=10  # Check every 10 seconds
```

### Headless Mode

For server deployment (no GUI):

```bash
export WHATSAPP_HEADLESS=true
```

**Warning**: You'll need to scan QR code via VNC or similar tool.

### Batch Processing

Process multiple messages in batch:

```python
# Modify orchestrator to process in batches
def _process_needs_action(self):
    whatsapp_files = list(self.needs_action.glob("WHATSAPP_*.md"))
    
    # Process in batches of 5
    for i in range(0, len(whatsapp_files), 5):
        batch = whatsapp_files[i:i+5]
        for action_file in batch:
            self._process_action_file(action_file)
```

## Production Deployment

### Using PM2 (Process Manager)

```bash
# Install PM2
npm install -g pm2

# Start with PM2
pm2 start scripts/start_whatsapp.sh --name whatsapp-automation

# Monitor
pm2 monit

# Auto-restart on boot
pm2 startup
pm2 save
```

### Docker Deployment

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m playwright install chromium

COPY . .

CMD ["bash", "scripts/start_whatsapp.sh"]
```

## Monitoring & Alerts

### Health Check Script

```bash
#!/bin/bash
# scripts/whatsapp_health_check.sh

# Check if processes are running
if ! kill -0 $(cat /tmp/whatsapp_watcher.pid) 2>/dev/null; then
    echo "❌ WhatsApp Watcher is not running!"
    # Restart
    bash scripts/start_whatsapp.sh
fi

# Check for stuck approvals
STUCK=$(find vault/Pending_Approval -name "WHATSAPP_*.md" -mtime +1 | wc -l)
if [ $STUCK -gt 0 ]; then
    echo "⚠️  $STUCK approvals pending for more than 1 day"
fi

# Check disk space
DISK=$(df -h vault | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK -gt 90 ]; then
    echo "⚠️  Vault disk usage: $DISK%"
fi
```

## Next Steps

1. ✅ **Core Implementation**: WhatsApp Watcher, Orchestrator, MCP Server
2. 🔄 **Testing**: Test with real WhatsApp account
3. 🔄 **Integration**: Connect with existing AI Employee features
4. 🔄 **Enhancement**: Add media support, group chat handling
5. 🔄 **Production**: Deploy with monitoring and alerts

## Support

For issues or questions:

- Check logs in `vault/Logs/`
- Review troubleshooting section above
- Refer to `requirements.md` for architecture details
- Check Playwright documentation for browser automation

## License

Same as Personal AI Employee project.
