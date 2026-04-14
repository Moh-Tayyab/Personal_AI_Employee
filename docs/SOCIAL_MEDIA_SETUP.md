# Social Media MCP Servers - Setup Guide

This guide covers setup for all social media integrations: LinkedIn, Twitter/X, Facebook, and Instagram.

---

## 📋 Overview

| Platform | MCP Server | File | Tools |
|----------|-----------|------|-------|
| LinkedIn | linkedin | `mcp/linkedin/server.py` | post, post_with_image, post_business_update, get_profile, status |
| Twitter/X | twitter | `mcp/twitter/server.py` | post_tweet, post_thread, get_timeline, search_tweets, post_business_update, status |
| Facebook | social | `mcp/social/server.py` | post_to_facebook, post_cross_platform, get_insights, list_pages, status |
| Instagram | social | `mcp/social/server.py` | post_to_instagram, get_insights, list_accounts, status |

---

## 🔗 LinkedIn Setup

### 1. Create LinkedIn App

1. Go to: https://www.linkedin.com/developers/apps
2. Click **Create App**
3. Fill in:
   - App name: "Personal AI Employee"
   - Company: Your company (or personal)
   - Privacy Policy URL: (optional for personal use)
4. Note your **Client ID** and **Client Secret**

### 2. Get Access Token

```bash
# OAuth 2.0 Authorization URL
# Replace CLIENT_ID with your app's client ID
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8080/auth&state=foobar&wsignin=1

# After authorization, exchange code for token
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_AUTH_CODE" \
  -d "redirect_uri=http://localhost:8080/auth" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

### 3. Configure Environment

Add to `.env` file:

```bash
# LinkedIn Configuration
LINKEDIN_ACCESS_TOKEN=your_access_token_here
```

### 4. Test Connection

```bash
# Test LinkedIn MCP server
python -c "from mcp.linkedin.server import linkedin_status; print(linkedin_status())"
```

---

## 🐦 Twitter/X Setup

### 1. Create Twitter Developer Account

1. Go to: https://developer.twitter.com/en/portal/dashboard
2. Apply for developer account (if not already approved)
3. Create a new **Project** and **App**
4. Note your:
   - API Key
   - API Key Secret
   - Bearer Token
   - Access Token
   - Access Token Secret

### 2. Set App Permissions

In your Twitter App settings:
1. Go to **App Permissions**
2. Set to **Read and Write**
3. Save changes

### 3. Configure Environment

Add to `.env` file:

```bash
# Twitter/X Configuration
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### 4. Test Connection

```bash
# Test Twitter MCP server
python -c "from mcp.twitter.server import twitter_status; print(twitter_status())"
```

---

## 📘 Facebook Setup

### 1. Create Facebook Developer Account

1. Go to: https://developers.facebook.com/
2. Create a **Business App**
3. Add **Facebook Login** product
4. Add **Instagram Graph API** product (if using Instagram)

### 2. Configure App Settings

1. In your Facebook App dashboard:
   - Go to **Settings** → **Basic**
   - Note your **App ID** and **App Secret**
   
2. Add **Facebook Login** product:
   - Go to **Products** → **Facebook Login** → **Settings**
   - Set **Valid OAuth Redirect URIs**: `http://localhost:8080/auth`

### 3. Get Page Access Token

1. Go to **Graph API Explorer**: https://developers.facebook.com/tools/explorer/
2. Select your app
3. Click **Generate Access Token**
4. Grant permissions:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `pages_manage_engagement`
5. Copy the **Page Access Token** (not User Access Token)

### 4. Configure Environment

Add to `.env` file:

```bash
# Facebook Configuration
META_ACCESS_TOKEN=your_page_access_token
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
```

### 5. Test Connection

```bash
# Test Facebook MCP server
python -c "from mcp.social.server import social_status; print(social_status())"
```

---

## 📷 Instagram Setup

### 1. Convert to Business Account

1. Open Instagram app
2. Go to **Settings** → **Account**
3. Tap **Switch to Professional Account**
4. Select **Business** category
5. Connect to Facebook Page (from step above)

### 2. Get Instagram Account ID

Use Graph API Explorer:

```bash
# Get Instagram Business Account ID
curl -i -X GET "https://graph.facebook.com/v18.0/me?fields=instagram_business_account&access_token=YOUR_PAGE_ACCESS_TOKEN"
```

The response will include your `instagram_business_account.id`.

### 3. Configure Environment

Add to `.env` file:

```bash
# Instagram Configuration
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id
# Uses same META_ACCESS_TOKEN as Facebook
```

### 4. Test Connection

```bash
# Test Instagram MCP server
python -c "from mcp.social.server import social_status; print(social_status())"
```

---

## 🧪 Testing All Social Media MCPs

### Quick Test Script

```bash
# Create test script
cat > test_social.py << 'EOF'
#!/usr/bin/env python3
"""Test all social media MCP servers"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_social_platform(name, status_func):
    """Test a social platform connection"""
    print(f"\n{'='*50}")
    print(f"Testing: {name}")
    print(f"{'='*50}")
    try:
        status = status_func()
        print(f"✅ Status: {status.get('status', 'unknown')}")
        print(f"   Connected: {status.get('connected', False)}")
        if 'account' in status:
            print(f"   Account: {status.get('account')}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

# Test all platforms
results = {}

print("\n" + "="*50)
print("SOCIAL MEDIA MCP SERVER TESTS")
print("="*50)

# LinkedIn
try:
    from mcp.linkedin.server import linkedin_status
    results['LinkedIn'] = test_social_platform("LinkedIn", linkedin_status)
except Exception as e:
    print(f"\n❌ LinkedIn test failed: {e}")
    results['LinkedIn'] = False

# Twitter
try:
    from mcp.twitter.server import twitter_status
    results['Twitter'] = test_social_platform("Twitter/X", twitter_status)
except Exception as e:
    print(f"\n❌ Twitter test failed: {e}")
    results['Twitter'] = False

# Facebook/Instagram
try:
    from mcp.social.server import social_status
    results['Facebook/Instagram'] = test_social_platform("Facebook/Instagram", social_status)
except Exception as e:
    print(f"\n❌ Facebook/Instagram test failed: {e}")
    results['Facebook/Instagram'] = False

# Summary
print("\n" + "="*50)
print("TEST SUMMARY")
print("="*50)
for platform, passed in results.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{platform}: {status}")

passed_count = sum(1 for v in results.values() if v)
total_count = len(results)
print(f"\nTotal: {passed_count}/{total_count} platforms working")
EOF

# Run test
python test_social.py
```

---

## 🚀 Usage Examples

### LinkedIn

```python
# Post text update
from mcp.linkedin.server import post_to_linkedin
result = post_to_linkedin(
    content="Excited to announce our new AI Employee product! #AI #Automation",
    visibility="PUBLIC"
)

# Post with image
from mcp.linkedin.server import post_with_image
result = post_with_image(
    content="Check out our latest feature!",
    image_url="https://example.com/image.jpg",
    visibility="PUBLIC"
)

# Post business update
from mcp.linkedin.server import post_business_update
result = post_business_update(
    topic="Q1 Results",
    key_points=["Revenue up 25%", "New product launch", "Team expanded"],
    call_to_action="Learn more at our website"
)
```

### Twitter/X

```python
# Post tweet
from mcp.twitter.server import post_tweet
result = post_tweet(content="Hello from AI Employee! 🤖 #AI #Automation")

# Post thread
from mcp.twitter.server import post_thread
tweets = [
    "🧵 Thread: Building Autonomous AI Employees",
    "1/ First, we need perception layer (watchers)...",
    "2/ Then reasoning layer (Claude Code)...",
    "3/ Finally action layer (MCP servers)..."
]
result = post_thread(tweets=tweets)
```

### Facebook

```python
# Post to Facebook
from mcp.social.server import post_to_facebook
result = post_to_facebook(
    content="Exciting news! Our AI Employee is now live.",
    link="https://example.com"
)
```

### Instagram

```python
# Post to Instagram
from mcp.social.server import post_to_instagram
result = post_to_instagram(
    caption="AI Employee launch! 🚀 #AI #Tech",
    image_url="https://example.com/image.jpg"
)
```

### Cross-Platform Posting

```python
# Post to all platforms at once
from mcp.social.server import post_cross_platform
result = post_cross_platform(
    content="Launching our AI Employee product today!",
    platforms=['facebook', 'instagram'],
    image_url="https://example.com/image.jpg",
    link="https://example.com/launch"
)
```

---

## 🔒 Security Notes

1. **NEVER commit tokens** to version control
2. Use `.env` file (already in `.gitignore`)
3. Rotate tokens every 90 days
4. Use vault secrets for production: `vault/secrets/meta_credentials.json`
5. Keep `DRY_RUN=true` during development

---

## 🐛 Troubleshooting

### LinkedIn Issues

**Error: "Unauthorized" or "403"**
- Token expired or invalid
- Generate new token from LinkedIn Developer
- Check app permissions include `w_member_social`

**Error: "Resource not found"**
- Verify app is approved and active
- Check API version is current (v2)

### Twitter Issues

**Error: "Forbidden" or "403"**
- Check app has Read/Write permissions
- Verify Access Token and Secret are set
- Ensure tweet content doesn't violate Twitter rules

**Error: "Rate limit exceeded"**
- Twitter has strict rate limits
- Wait 15 minutes and retry
- Check your app's rate limit tier

### Facebook/Instagram Issues

**Error: "Invalid OAuth access token"**
- Token expired (Page tokens last 60 days)
- Generate new token from Graph API Explorer
- Verify app is in development mode or approved

**Error: "Unsupported post request"**
- Check you're using Page Token (not User Token)
- Verify Instagram account is Business account
- Ensure Facebook Page is connected to Instagram

---

## 📚 Additional Resources

- [LinkedIn API Docs](https://docs.microsoft.com/en-us/linkedin/)
- [Twitter API v2 Docs](https://developer.twitter.com/en/docs/twitter-api)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)

---

## ✅ Setup Checklist

- [ ] LinkedIn app created and token configured
- [ ] Twitter developer account and app created
- [ ] Facebook developer app created
- [ ] Instagram converted to Business account
- [ ] All tokens added to `.env` file
- [ ] Test scripts pass for all platforms
- [ ] DRY_RUN=true during testing
- [ ] Tokens saved to vault secrets (optional)

---

*Last Updated: 2026-04-13*
