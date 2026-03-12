# Gmail Email Setup Guide

Complete setup for Gmail integration with Personal AI Employee.

---

## Prerequisites

- Python 3.10+ installed
- Google account with Gmail
- Access to Google Cloud Console

---

## Step 1: Get Gmail API Credentials

### 1.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Create Project"** or select existing project
3. Name it (e.g., "Personal AI Employee")
4. Click **"Create"**

### 1.2 Enable Gmail API

1. In your project, go to **"APIs & Services"** → **"Library"**
2. Search for **"Gmail API"**
3. Click on it and press **"Enable"**

### 1.3 Create OAuth Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. If prompted, configure **"OAuth consent screen"**:
   - User Type: **External**
   - App name: **Personal AI Employee**
   - User support email: Your email
   - Developer contact: Your email
   - Click **"Save and Continue"**
   - Scopes: Skip this step
   - Test users: Add your Gmail address
   - Click **"Save and Continue"**

4. Now create OAuth client:
   - Application type: **Desktop app**
   - Name: **Personal AI Employee CLI**
   - Click **"Create"**

5. Download the credentials:
   - Click **"Download JSON"**
   - Save as: `vault/secrets/gmail_credentials.json`

---

## Step 2: Run OAuth Setup

### Option A: Automatic Browser Flow (Recommended)

```bash
cd /home/muhammad_tayyab/hackathon/Personal_AI_Employee
python3 scripts/gmail_oauth_setup.py
```

This will:
1. Open browser automatically
2. Ask you to sign in
3. Request Gmail permissions
4. Save the token

### Option B: Manual Mode (If automatic fails)

```bash
cd /home/muhammad_tayyab/hackathon/Personal_AI_Employee
python3 scripts/gmail_oauth_manual.py
```

This will:
1. Give you a URL to open
2. Ask for authorization code
3. Exchange code for token

---

## Step 3: Verify Token

After successful OAuth, verify the token was created:

```bash
ls -la vault/secrets/gmail_token.json
```

You should see the file with recent timestamp.

---

## Step 4: Configure MCP in Claude Code

### 4.1 Create MCP Configuration

The configuration file is ready at: `claude_mcp_config.json`

### 4.2 Copy to Claude Code Config

**Option 1: Merge with existing config**

```bash
# Backup existing config
cp ~/.config/claude-code/mcp.json ~/.config/claude-code/mcp.json.backup

# View our config
cat claude_mcp_config.json

# Manually merge into ~/.config/claude-code/mcp.json
```

**Option 2: Use our config directly**

```bash
mkdir -p ~/.config/claude-code
cp claude_mcp_config.json ~/.config/claude-code/mcp.json
```

### 4.3 Verify Configuration

```bash
cat ~/.config/claude-code/mcp.json
```

Should show email and filesystem MCP servers.

---

## Step 5: Test Email Integration

### 5.1 Start Claude Code

```bash
claude
```

### 5.2 Test Commands

Try these commands:

```
List available MCP servers

Send a test email to yourself with subject "Test from Personal AI Employee"

Draft an email to test@example.com saying hello
```

### 5.3 Check DRY_RUN Mode

The configuration has `DRY_RUN=true` which means:
- Emails are prepared but NOT actually sent
- Good for testing without consequences

To send real emails, change to `DRY_RUN=false` in MCP config.

---

## Troubleshooting

### Problem: "No credentials found"

**Solution**: Make sure `vault/secrets/gmail_credentials.json` exists with valid OAuth client credentials.

### Problem: "Token expired"

**Solution**: Re-run OAuth setup:
```bash
python3 scripts/gmail_oauth_setup.py
```

### Problem: "MCP server not found"

**Solution**: Check MCP config location:
```bash
# Should be at:
~/.config/claude-code/mcp.json

# Verify syntax:
python3 -c "import json; json.load(open('~/.config/claude-code/mcp.json'))"
```

### Problem: "Gmail API not enabled"

**Solution**: 
1. Go to Google Cloud Console
2. Enable Gmail API for your project
3. Wait 5 minutes for propagation

### Problem: Browser doesn't open

**Solution**: Use manual mode:
```bash
python3 scripts/gmail_oauth_manual.py
```

---

## Security Notes

### Token Storage

- Token saved to: `vault/secrets/gmail_token.json`
- This file contains access credentials
- **Never commit to git** (already in .gitignore)
- Keep file permissions restricted

### Scopes Granted

The OAuth requests these permissions:
- `gmail.readonly` - Read emails
- `gmail.modify` - Label/mark as read
- `gmail.send` - Send emails

### DRY_RUN Mode

- Default: `DRY_RUN=true` (safe mode)
- Emails prepared but not sent
- Change to `false` when ready for production

---

## File Locations

| File | Purpose |
|------|---------|
| `vault/secrets/gmail_credentials.json` | OAuth client credentials |
| `vault/secrets/gmail_token.json` | Access token (auto-generated) |
| `mcp/email/server.py` | Email MCP server |
| `scripts/gmail_oauth_setup.py` | OAuth setup script |
| `~/.config/claude-code/mcp.json` | Claude Code MCP config |

---

## Quick Reference

### Re-run OAuth
```bash
python3 scripts/gmail_oauth_setup.py
```

### Check Token
```bash
cat vault/secrets/gmail_token.json | python3 -m json.tool
```

### Test Email MCP
```bash
python3 mcp/email/server.py --test
```

### View Logs
```bash
tail -f vault/Logs/email.log
```

---

## Next Steps

After email is working:

1. **Set up Gmail Watcher** for incoming emails:
   ```bash
   python3 watchers/gmail_watcher.py --vault ./vault
   ```

2. **Configure process-email skill** to handle incoming emails

3. **Set up approval workflow** for outgoing emails

---

## Help

If you encounter issues:

1. Check logs: `vault/Logs/*.log`
2. Verify credentials are valid
3. Re-run OAuth setup
4. Check MCP config syntax
