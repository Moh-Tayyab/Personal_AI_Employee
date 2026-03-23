# Social Media Authentication - Complete Setup Guide

## ✅ What Was Created

I've created a complete authentication system for automating Twitter/X, LinkedIn, and Facebook posting with your Personal AI Employee agent teams.

### New Files Created

| File | Purpose |
|------|---------|
| `scripts/authenticate_social_media.py` | Unified authentication script for all platforms |
| `docs/SOCIAL_MEDIA_AUTHENTICATION.md` | Comprehensive authentication guide |
| `docs/SOCIAL_MEDIA_AUTH_SETUP_SUMMARY.md` | This summary document |

### Existing Infrastructure (Already in Place)

| Component | Status |
|-----------|--------|
| `mcp/twitter/server.py` | ✅ MCP server exists |
| `mcp/twitter/browser.py` | ✅ Browser automation exists |
| `mcp/linkedin/server.py` | ✅ MCP server exists |
| `mcp/linkedin/browser.py` | ✅ Browser automation exists |
| `mcp/facebook/server.py` | ✅ MCP server exists |
| `mcp/facebook/browser.py` | ✅ Browser automation exists |
| `scripts/agents/social_media_manager.py` | ✅ Agent script exists |

---

## 🚀 Quick Start - Authenticate All Platforms

### Option 1: Interactive Mode (Recommended for First Time)

```bash
cd /home/muhammad_tayyab/hackathon/Personal_AI_Employee
source .venv/bin/activate

# Run interactive authentication
python scripts/authenticate_social_media.py
```

This will show a menu where you can select which platform to authenticate.

### Option 2: Authenticate Specific Platform

```bash
# Twitter/X
python scripts/authenticate_social_media.py --platform twitter

# LinkedIn
python scripts/authenticate_social_media.py --platform linkedin

# Facebook
python scripts/authenticate_social_media.py --platform facebook
```

### Option 3: With Environment Variables

```bash
# Set credentials
export TWITTER_EMAIL=your_username
export TWITTER_PASSWORD=your_password

# Authenticate (no prompts)
python scripts/authenticate_social_media.py --platform twitter
```

---

## 📊 Current Session Status

I checked your existing sessions:

| Platform | Session Path | Status |
|----------|--------------|--------|
| **Twitter/X** | `vault/secrets/twitter_session/` | ❌ **Not authenticated** - needs setup |
| **LinkedIn** | `vault/secrets/linkedin_session/` | ⚠️ **Session expired** - needs re-auth |
| **Facebook** | `vault/secrets/facebook_session/` | ⚠️ **Exists** - needs verification |

---

## 📝 Step-by-Step Authentication

### Step 1: Authenticate Twitter/X

```bash
python scripts/authenticate_social_media.py --platform twitter
```

**What happens:**
1. Browser opens to twitter.com/login
2. Enter your username (not email) and password
3. If 2FA/captcha appears, complete it manually
4. Session saved to `vault/secrets/twitter_session/storage.json`

**Expected output:**
```
============================================================
  TWITTER Authentication Result
============================================================

✅ SUCCESS: Authenticated to twitter
   Profile: https://twitter.com/home
```

---

### Step 2: Authenticate LinkedIn

```bash
python scripts/authenticate_social_media.py --platform linkedin
```

**What happens:**
1. Browser opens to linkedin.com/login
2. Enter your email and password
3. If 2FA appears, check your email for code
4. Session saved to `vault/secrets/linkedin_session/storage.json`

---

### Step 3: Authenticate Facebook

```bash
python scripts/authenticate_social_media.py --platform facebook
```

**What happens:**
1. Browser opens to facebook.com
2. Accept cookies if prompted
3. Enter email and password
4. Complete any security checks
5. Session saved to `vault/secrets/facebook_session/storage.json`

---

## ✅ Verify Authentication

After authenticating each platform, verify the session:

```bash
# Check Twitter
python scripts/authenticate_social_media.py --platform twitter --check-session

# Check LinkedIn
python scripts/authenticate_social_media.py --platform linkedin --check-session

# Check Facebook
python scripts/authenticate_social_media.py --platform facebook --check-session
```

**Expected output for valid session:**
```
✅ Session is valid
   Session appears valid
```

---

## 🧪 Test Social Media Agent

Once authenticated, test the agent teams:

```bash
# Dry-run mode (safe test)
./scripts/run_agent_teams.sh --social --report

# Live mode (actual posting)
./scripts/run_agent_teams.sh --social --live --report
```

---

## 🔧 Troubleshooting

### "Session expired"

**Solution:** Re-authenticate
```bash
python scripts/authenticate_social_media.py --platform twitter
```

### "Two-factor authentication required"

**Solution:** Complete 2FA in the browser window when it appears. The session will be saved automatically.

### "Unusual activity detected" / Captcha

**Solution:**
1. Complete the captcha manually
2. Wait 24 hours before retrying
3. Try from a familiar network/location

### Browser doesn't open

**Solution:** Install Playwright browsers
```bash
playwright install chromium
```

---

## 📋 What Happens After Authentication

Once authenticated, your agent teams can automatically:

1. **Create platform-optimized content** from tasks in `vault/Needs_Action/`
2. **Post to LinkedIn** - Professional posts, articles, updates
3. **Post to Twitter** - Short updates, threads
4. **Post to Facebook** - Posts, updates, messaging
5. **Schedule posts** for optimal engagement times
6. **Monitor engagement** and track performance

### Example Workflow

```
1. Task created: vault/Needs_Action/SOCIAL_linkedin_post.md
         ↓
2. Social Media Manager agent picks up task
         ↓
3. Creates LinkedIn-optimized content (150-300 words)
         ↓
4. Loads saved session from vault/secrets/linkedin_session/
         ↓
5. Posts to LinkedIn via browser automation
         ↓
6. Moves task to vault/Done/
7. Logs action to vault/Logs/
```

---

## 🔐 Security Best Practices

### DO:
- ✅ Use environment variables for credentials
- ✅ Keep `.env` file secure (not in git)
- ✅ Re-authenticate regularly (weekly)
- ✅ Monitor session status

### DON'T:
- ❌ Store passwords in plain text files
- ❌ Commit `.env` or session files to git
- ❌ Share session files with others
- ❌ Disable 2FA for automation convenience

---

## 📚 Documentation

For detailed information, see:
- **Full Guide:** `docs/SOCIAL_MEDIA_AUTHENTICATION.md`
- **Agent Teams:** `docs/AGENT_TEAMS_SILVER_GOLD.md`
- **Silver/Gold Completion:** `SILVER_GOLD_TIER_COMPLETION.md`

---

## 🎯 Next Steps

1. **Authenticate all platforms:**
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

4. **Run in live mode:**
   ```bash
   ./scripts/run_agent_teams.sh --social --live --report
   ```

---

## 📞 Support Commands

```bash
# Help
python scripts/authenticate_social_media.py --help

# List available tasks
./scripts/run_agent_teams.sh --list-tasks

# Check all sessions
for platform in twitter linkedin facebook; do
    echo "=== $platform ==="
    python scripts/authenticate_social_media.py --platform $platform --check-session
done

# View logs
tail -f vault/Logs/social_media_manager.log
```

---

**🎉 You now have everything needed to authenticate and automate social media posting!**

Run `python scripts/authenticate_social_media.py` to get started.
