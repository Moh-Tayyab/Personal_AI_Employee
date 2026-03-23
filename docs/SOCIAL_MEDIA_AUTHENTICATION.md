# Social Media Authentication Guide

This guide explains how to authenticate Twitter/X, LinkedIn, and Facebook for automated posting via the Personal AI Employee agent teams.

---

## Overview

The Personal AI Employee uses **browser automation** (Playwright) to post to social media platforms. Each platform requires an authenticated browser session that is saved and reused for subsequent posts.

```
┌─────────────────────────────────────────────────────────────┐
│              Social Media Authentication Flow                │
└─────────────────────────────────────────────────────────────┘

1. Run authentication script (one-time setup)
         │
         ▼
2. Browser opens → Enter credentials
         │
         ▼
3. Complete any 2FA/captcha manually
         │
         ▼
4. Session saved to vault/secrets/{platform}_session/
         │
         ▼
5. Agent teams use saved session for automated posting
```

---

## Quick Start

### One-Time Authentication

```bash
# Authenticate all platforms (interactive)
python scripts/authenticate_social_media.py

# Or authenticate specific platforms
python scripts/authenticate_social_media.py --platform twitter
python scripts/authenticate_social_media.py --platform linkedin
python scripts/authenticate_social_media.py --platform facebook
```

### Check Session Status

```bash
# Check if session is still valid
python scripts/authenticate_social_media.py --platform twitter --check-session
python scripts/authenticate_social_media.py --platform linkedin --check-session
python scripts/authenticate_social_media.py --platform facebook --check-session
```

---

## Platform-Specific Instructions

### Twitter/X Authentication

**What you need:**
- Twitter/X username (not email)
- Password
- Phone/email for verification (if 2FA triggered)

**Steps:**

```bash
# Method 1: Interactive
python scripts/authenticate_social_media.py --platform twitter

# Method 2: With environment variables
export TWITTER_EMAIL=your_username
export TWITTER_PASSWORD=your_password
python scripts/authenticate_social_media.py --platform twitter
```

**Expected flow:**
1. Browser opens to twitter.com/login
2. Enter username → Click Next
3. Enter password → Click Login
4. If 2FA required: Complete verification manually
5. Session saved to `vault/secrets/twitter_session/`

**Common issues:**

| Issue | Solution |
|-------|----------|
| "Unusual activity detected" | Complete the captcha/verification manually |
| "Phone verification required" | Enter your phone number when prompted |
| "Login failed" | Check username (not email) and password |
| Session expires quickly | Twitter may require frequent re-authentication |

---

### LinkedIn Authentication

**What you need:**
- LinkedIn email
- Password
- Access to email for 2FA (if enabled)

**Steps:**

```bash
# Method 1: Interactive
python scripts/authenticate_social_media.py --platform linkedin

# Method 2: With environment variables
export LINKEDIN_EMAIL=your@email.com
export LINKEDIN_PASSWORD=your_password
python scripts/authenticate_social_media.py --platform linkedin
```

**Expected flow:**
1. Browser opens to linkedin.com/login
2. Enter email and password
3. If 2FA required: Check email for code
4. Session saved to `vault/secrets/linkedin_session/`

**Current session status:**

```bash
# Check existing session
ls -la vault/secrets/linkedin_session/
cat vault/secrets/linkedin_session/storage.json | head -20

# Verify session is valid
python scripts/authenticate_social_media.py --platform linkedin --check-session
```

**Common issues:**

| Issue | Solution |
|-------|----------|
| "Checkpoint challenge" | Complete security verification manually |
| "Wrong password" | Reset password on LinkedIn |
| Session expires | Re-run authentication script |

---

### Facebook Authentication

**What you need:**
- Facebook email/phone
- Password
- Access to email/SMS for 2FA (if enabled)

**Steps:**

```bash
# Method 1: Interactive
python scripts/authenticate_social_media.py --platform facebook

# Method 2: With environment variables
export FACEBOOK_EMAIL=your@email.com
export FACEBOOK_PASSWORD=your_password
python scripts/authenticate_social_media.py --platform facebook
```

**Expected flow:**
1. Browser opens to facebook.com
2. Accept cookies if prompted
3. Enter email and password
4. If 2FA required: Complete verification
5. Session saved to `vault/secrets/facebook_session/`

**Common issues:**

| Issue | Solution |
|-------|----------|
| "Security checkpoint" | Complete the security questions/captcha |
| "Unrecognized login" | Approve login from your email/phone |
| Cookie banner blocks login | Script auto-accepts, but may need manual click |

---

## Session Management

### Session File Locations

| Platform | Session Path | Storage File |
|----------|--------------|--------------|
| Twitter | `vault/secrets/twitter_session/` | `storage.json` |
| LinkedIn | `vault/secrets/linkedin_session/` | `storage.json` |
| Facebook | `vault/secrets/facebook_session/` | `storage.json` |

### Check Session Validity

```bash
# Quick check
python scripts/authenticate_social_media.py --platform twitter --check-session

# Manual inspection
cat vault/secrets/twitter_session/storage.json | python -m json.tool | head -30
```

### Session Expiry

Sessions may expire due to:
- Platform security policies
- Password changes
- Extended inactivity
- Platform updates

**Recommended:** Re-authenticate weekly or when posts fail.

### Delete and Re-authenticate

```bash
# Delete existing session
rm -rf vault/secrets/twitter_session/
rm -rf vault/secrets/linkedin_session/
rm -rf vault/secrets/facebook_session/

# Re-authenticate
python scripts/authenticate_social_media.py --platform twitter
```

---

## Using Authenticated Sessions with Agent Teams

Once authenticated, the agent teams automatically use the saved sessions:

```bash
# Run social media agent
./scripts/run_agent_teams.sh --social --report

# Or run specific platform
python scripts/agents/social_media_manager.py --vault ./vault --no-dry-run
```

The agent will:
1. Load session from `vault/secrets/{platform}_session/storage.json`
2. Verify session is valid
3. Post content using the authenticated browser
4. Save any updated session data

---

## Troubleshooting

### "Session expired" Error

**Symptoms:** Agent reports "not authenticated" or "session expired"

**Solutions:**
1. Re-authenticate:
   ```bash
   python scripts/authenticate_social_media.py --platform twitter
   ```

2. Check session file:
   ```bash
   ls -la vault/secrets/twitter_session/
   cat vault/secrets/twitter_session/storage.json
   ```

3. Delete and re-create session:
   ```bash
   rm -rf vault/secrets/twitter_session/
   python scripts/authenticate_social_media.py --platform twitter
   ```

### "Two-factor authentication required"

**Symptoms:** Login stops at 2FA screen

**Solutions:**
1. Complete 2FA manually in the browser window
2. The session will be saved after successful 2FA
3. Next automated posts will use the saved session

**Alternative:** Disable 2FA temporarily (not recommended for security)

### "Unusual activity detected" / Captcha

**Symptoms:** Platform shows captcha or security challenge

**Solutions:**
1. Complete the captcha manually in the browser
2. Wait 24 hours before trying again
3. Use a different IP/network
4. Authenticate from a familiar location/device

### Browser Issues

**Symptoms:** Browser doesn't open or crashes

**Solutions:**
1. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

2. Try non-headless mode:
   ```bash
   python scripts/authenticate_social_media.py --platform twitter
   # (remove --headless flag)
   ```

3. Check for display issues (Linux):
   ```bash
   # Install dependencies
   sudo apt-get install libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2
   ```

### Posts Not Appearing

**Symptoms:** Agent reports success but post doesn't appear

**Possible causes:**
1. Session expired mid-post
2. Platform rate limiting
3. Content violated platform policies
4. Shadowban/account restriction

**Solutions:**
1. Check session status
2. Verify post manually on platform
3. Wait and try again (rate limiting)
4. Review platform content policies

---

## Security Best Practices

### Credential Storage

**DO:**
- Use environment variables for credentials
- Keep `.env` file secure (not in version control)
- Use app-specific passwords if available

**DON'T:**
- Store passwords in plain text files
- Commit credentials to git
- Share session files with others

### Session Security

- Session files contain authentication cookies
- Treat them like passwords
- Don't share `vault/secrets/` folder
- Re-authenticate if you suspect compromise

### 2FA Recommendations

- Keep 2FA enabled for account security
- Use authenticator apps over SMS when possible
- Save backup codes in a secure location
- Expect to complete 2FA occasionally during automation

---

## Environment Variables Reference

Add to `.env` file:

```bash
# Twitter/X
TWITTER_EMAIL=your_username
TWITTER_PASSWORD=your_password
TWITTER_SESSION_PATH=./vault/secrets/twitter_session

# LinkedIn
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=your_password
LINKEDIN_SESSION_PATH=./vault/secrets/linkedin_session

# Facebook
FACEBOOK_EMAIL=your@email.com
FACEBOOK_PASSWORD=your_password
FACEBOOK_SESSION_PATH=./vault/secrets/facebook_session
```

---

## Command Reference

### Authentication

```bash
# Interactive authentication (menu)
python scripts/authenticate_social_media.py

# Authenticate specific platform
python scripts/authenticate_social_media.py --platform twitter
python scripts/authenticate_social_media.py --platform linkedin
python scripts/authenticate_social_media.py --platform facebook

# Authenticate all platforms
python scripts/authenticate_social_media.py --platform all

# With credentials from environment
python scripts/authenticate_social_media.py --platform twitter --headless
```

### Session Checking

```bash
# Check session status
python scripts/authenticate_social_media.py --platform twitter --check-session

# View session files
ls -la vault/secrets/*/
cat vault/secrets/twitter_session/storage.json
```

### Agent Teams

```bash
# Run social media agent (dry-run)
./scripts/run_agent_teams.sh --social --report

# Run social media agent (live)
./scripts/run_agent_teams.sh --social --live --report

# Process specific task
python scripts/agents/social_media_manager.py --vault ./vault --no-dry-run
```

---

## Testing Authentication

### Test Twitter Authentication

```bash
# Authenticate
python scripts/authenticate_social_media.py --platform twitter

# Check session
python scripts/authenticate_social_media.py --platform twitter --check-session

# Test post (dry-run)
python -c "
from mcp.twitter.browser import TwitterBrowserSync
browser = TwitterBrowserSync('./vault/secrets/twitter_session')
result = browser.check_session()
print('Session status:', result)
browser.close()
"
```

### Test LinkedIn Authentication

```bash
# Authenticate
python scripts/authenticate_social_media.py --platform linkedin

# Check session
python scripts/authenticate_social_media.py --platform linkedin --check-session

# Test post capability
python -c "
from mcp.linkedin.browser import LinkedInBrowserSync
browser = LinkedInBrowserSync('./vault/secrets/linkedin_session')
result = browser.check_session()
print('Session status:', result)
if result.get('status') == 'authenticated':
    print('Profile:', result.get('profile_name'))
browser.close()
"
```

### Test Facebook Authentication

```bash
# Authenticate
python scripts/authenticate_social_media.py --platform facebook

# Check session
python scripts/authenticate_social_media.py --platform facebook --check-session

# Test session
python -c "
from mcp.facebook.browser import FacebookBrowserSync
browser = FacebookBrowserSync('./vault/secrets/facebook_session')
result = browser.check_session()
print('Session status:', result)
browser.close()
"
```

---

## Current Status

| Platform | MCP Server | Browser Module | Auth Script | Session Status |
|----------|------------|----------------|-------------|----------------|
| Twitter/X | ✅ `mcp/twitter/server.py` | ✅ `mcp/twitter/browser.py` | ✅ Created | ❌ Needs auth |
| LinkedIn | ✅ `mcp/linkedin/server.py` | ✅ `mcp/linkedin/browser.py` | ✅ Created | 🟡 Exists (verify) |
| Facebook | ✅ `mcp/facebook/server.py` | ✅ `mcp/facebook/browser.py` | ✅ Created | 🟡 Exists (verify) |

---

## Next Steps

1. **Authenticate each platform:**
   ```bash
   python scripts/authenticate_social_media.py
   ```

2. **Verify sessions:**
   ```bash
   python scripts/authenticate_social_media.py --platform twitter --check-session
   python scripts/authenticate_social_media.py --platform linkedin --check-session
   python scripts/authenticate_social_media.py --platform facebook --check-session
   ```

3. **Test agent teams:**
   ```bash
   ./scripts/run_agent_teams.sh --social --report
   ```

---

**🎯 Goal:** Have all three social media platforms authenticated and ready for automated posting by the agent teams.
