# Setup Guide - Personal AI Employee

This guide will help you set up and run the Personal AI Employee with the newly implemented Claude integration and email functionality.

---

## Prerequisites

### Required
- Python 3.11 or higher
- pip (Python package manager)
- Git
- A Gmail account (for email operations)
- Anthropic API key (for Claude AI)

### Optional
- Node.js 20+ and PM2 (for production deployment)
- Playwright browsers (for social media automation)
- Odoo instance (for accounting integration)

---

## Step 1: Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd Personal_AI_Employee

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (optional, for social media)
playwright install chromium
```

---

## Step 2: Get API Keys

### Anthropic API Key (REQUIRED)

1. Go to https://console.anthropic.com
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-`)

### Gmail API Credentials (REQUIRED for email)

1. Go to https://console.cloud.google.com
2. Create a new project or select existing
3. Enable Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "Personal AI Employee"
   - Download the JSON file
5. Save as `vault/secrets/gmail_credentials.json`

---

## Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Minimum required configuration:**

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-your-key-here
GMAIL_CREDENTIALS_PATH=./vault/secrets/gmail_credentials.json
GMAIL_TOKEN_PATH=./vault/secrets/gmail_token.json
VAULT_PATH=./vault
DRY_RUN=false
```

**Optional configurations:**

```bash
# Webhook notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK

# Odoo ERP
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_API_KEY=your_odoo_key

# Social media
TWITTER_SESSION_PATH=./vault/secrets/twitter_session
LINKEDIN_SESSION_PATH=./vault/secrets/linkedin_session
```

---

## Step 4: Authenticate Gmail

Run the Gmail watcher once to authenticate:

```bash
# This will open a browser for OAuth authentication
python watchers/gmail_watcher.py --vault ./vault

# Follow the prompts:
# 1. Browser will open
# 2. Select your Google account
# 3. Grant permissions
# 4. Token will be saved to vault/secrets/gmail_token.json
```

**Verify authentication:**
```bash
# Check that token file exists
ls -la vault/secrets/gmail_token.json

# Should see a file with recent timestamp
```

---

## Step 5: Test the System

### Test 1: Verify Claude Integration

```bash
# Run orchestrator in dry-run mode
python orchestrator.py --vault ./vault --dry-run

# Expected output:
# - "Starting Orchestrator (dry_run=True)"
# - No errors about missing API key
# - System should start successfully
```

### Test 2: Test Claude API Call

Create a test email file:

```bash
# Create test email
cat > vault/Needs_Action/test_email.md << 'EOF'
---
type: email
from: test@example.com
subject: Test Email for AI Processing
date: 2026-03-10
---

Hi,

This is a test email to verify the AI Employee is working correctly.

Please acknowledge receipt and let me know the next steps.

Thanks!
EOF

# Run orchestrator to process it
python orchestrator.py --vault ./vault --dry-run

# Check results
ls -la vault/Plans/CLAUDE_PLAN_*.md
cat vault/Plans/CLAUDE_PLAN_*.md
```

**Expected result:**
- A new file in `vault/Plans/` with Claude's analysis
- The plan should contain structured analysis and recommended actions

### Test 3: Test Email Sending (Dry Run)

```bash
# Test email MCP server
python -c "
from mcp.email.server import EmailMCPServer
import os
os.environ['DRY_RUN'] = 'true'

server = EmailMCPServer()
result = server.send_email({
    'to': 'test@example.com',
    'subject': 'Test Email',
    'body': 'This is a test email from the AI Employee.'
})

print('Result:', result)
"

# Expected output:
# Result: {'status': 'dry_run', 'message': 'Email not sent (dry-run mode)', ...}
```

### Test 4: Test Email Search

```bash
# Test email search
python -c "
from mcp.email.server import EmailMCPServer

server = EmailMCPServer()
result = server.search_emails({
    'query': 'is:unread',
    'max_results': 5
})

print('Found emails:', result.get('count', 0))
"

# Expected output:
# Found emails: <number>
```

---

## Step 6: Run the System

### Option 1: Manual Start (Development)

```bash
# Terminal 1: Start orchestrator
python orchestrator.py --vault ./vault

# Terminal 2: Start Gmail watcher
python watchers/gmail_watcher.py --vault ./vault

# Terminal 3: Start filesystem watcher (optional)
python watchers/filesystem_watcher.py --vault ./vault --watch-path ./drop
```

### Option 2: PM2 (Production)

```bash
# Install PM2 globally
npm install -g pm2

# Start all services
pm2 start ecosystem.config.js

# Check status
pm2 status

# View logs
pm2 logs

# Stop all
pm2 stop all
```

### Option 3: All-in-One Script

```bash
# Start everything
./scripts/start_all.sh

# Stop everything
./scripts/stop_all.sh
```

---

## Step 7: Monitor Activity

### Check Logs

```bash
# View orchestrator logs
tail -f vault/Logs/$(date +%Y-%m-%d).json

# View PM2 logs (if using PM2)
pm2 logs orchestrator
```

### Check Folders

```bash
# Items needing processing
ls -la vault/Needs_Action/

# Claude's action plans
ls -la vault/Plans/

# Items needing approval
ls -la vault/Pending_Approval/

# Completed items
ls -la vault/Done/

# Email drafts
ls -la vault/Drafts/
```

### Dashboard

```bash
# View system dashboard
cat vault/Dashboard.md

# Or open in Obsidian for better viewing
```

---

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check API key is set
grep ANTHROPIC_API_KEY .env

# If missing, add it:
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
```

### Issue: "Gmail token not found"

**Solution:**
```bash
# Re-run Gmail authentication
python watchers/gmail_watcher.py --vault ./vault

# Check token was created
ls -la vault/secrets/gmail_token.json
```

### Issue: "anthropic package not installed"

**Solution:**
```bash
# Install anthropic package
pip install anthropic

# Or reinstall all dependencies
pip install -r requirements.txt
```

### Issue: "Gmail API libraries not installed"

**Solution:**
```bash
# Install Gmail API packages
pip install google-auth google-auth-oauthlib google-api-python-client

# Or reinstall all dependencies
pip install -r requirements.txt
```

### Issue: Claude returns errors

**Check:**
1. API key is valid (not expired)
2. You have API credits remaining
3. Network connection is working
4. Check logs for specific error message

```bash
# Test API key directly
python -c "
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

try:
    message = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=100,
        messages=[{'role': 'user', 'content': 'Hello!'}]
    )
    print('✅ API key works!')
    print('Response:', message.content[0].text)
except Exception as e:
    print('❌ API key error:', e)
"
```

### Issue: Emails not sending

**Check:**
1. Gmail token exists and is valid
2. DRY_RUN is set to 'false' in .env
3. Gmail API is enabled in Google Cloud Console
4. OAuth consent screen is configured

```bash
# Test email sending directly
python -c "
from mcp.email.server import EmailMCPServer
import os

os.environ['DRY_RUN'] = 'false'

server = EmailMCPServer()
result = server.send_email({
    'to': 'your-email@example.com',
    'subject': 'Test from AI Employee',
    'body': 'If you receive this, email sending works!'
})

print('Result:', result)
"
```

---

## Verification Checklist

After setup, verify these work:

- [ ] Orchestrator starts without errors
- [ ] Claude API calls work (check logs for "Claude response received")
- [ ] Gmail authentication works (token file exists)
- [ ] Email search returns results
- [ ] Email sending works (test with your own email)
- [ ] Files in Needs_Action/ get processed
- [ ] Plans appear in Plans/ folder
- [ ] Approval requests appear in Pending_Approval/
- [ ] Logs are created in Logs/ folder

---

## Next Steps

Once setup is complete:

1. **Customize Company Handbook**
   - Edit `vault/Company_Handbook.md`
   - Define your rules and preferences
   - Claude will follow these guidelines

2. **Set Business Goals**
   - Edit `vault/Business_Goals.md`
   - Define revenue targets and KPIs
   - Used for CEO briefings

3. **Configure Webhooks** (Optional)
   - Add Slack/Discord webhook URLs to .env
   - Get notifications for approvals

4. **Test End-to-End**
   - Send yourself a test email
   - Watch it get processed
   - Verify Claude creates a plan
   - Check if approval is requested

5. **Deploy to Production**
   - Use PM2 for process management
   - Set up monitoring
   - Configure backups

---

## Getting Help

- **Documentation:** See TIER_AUDIT.md and IMPLEMENTATION_PLAN.md
- **Status:** See IMPLEMENTATION_STATUS.md for current completion
- **Issues:** Check logs in vault/Logs/
- **Testing:** Run test scripts in tests/ directory

---

## Security Notes

⚠️ **Important:**
- Never commit `.env` file to git
- Never commit `vault/secrets/` to git
- Keep API keys secure
- Review approval requests before approving
- Use dry-run mode for testing

The `.gitignore` file already excludes:
- `.env`
- `vault/secrets/`
- `vault/.processed_ids.json`

---

## Quick Reference

```bash
# Start system
./scripts/start_all.sh

# Stop system
./scripts/stop_all.sh

# Check status
pm2 status

# View logs
pm2 logs

# Test Claude
python orchestrator.py --vault ./vault --dry-run

# Test email
python -m mcp.email.server

# Authenticate Gmail
python watchers/gmail_watcher.py --vault ./vault

# Generate briefing
python scripts/generate_briefing.py --vault ./vault
```

---

**Setup complete! Your AI Employee is ready to work.**
