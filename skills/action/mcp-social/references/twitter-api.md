# Twitter/X API Reference

## Overview

Twitter MCP Server handles posting to Twitter/X. Currently operates in draft mode with session-based automation ready for implementation.

## Authentication

### Session Setup

```bash
# Initialize Twitter session
python -m mcp.twitter.server --setup

# Check session status
python -m mcp.twitter.server --check
```

### Session Storage

```
vault/secrets/twitter_session/
├── Default/
├── Cookies/
└── Local Storage/
```

## Available Tools

### post_tweet

Post a tweet to Twitter/X.

```json
{
  "name": "post_tweet",
  "description": "Post a tweet to Twitter/X",
  "input_schema": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "Tweet content (max 280 chars)"
      }
    },
    "required": ["content"]
  }
}
```

**Example Request:**

```json
{
  "method": "post_tweet",
  "params": {
    "content": "Excited to share our latest update! #innovation"
  }
}
```

**Example Response:**

```json
{
  "status": "posted",
  "tweet_id": "1234567890",
  "url": "https://twitter.com/user/status/1234567890"
}
```

### schedule_tweet

Schedule a tweet for later.

```json
{
  "name": "schedule_tweet",
  "description": "Schedule a tweet for later",
  "input_schema": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "Tweet content"
      },
      "scheduled_time": {
        "type": "string",
        "description": "ISO 8601 timestamp"
      }
    },
    "required": ["content", "scheduled_time"]
  }
}
```

**Example Request:**

```json
{
  "method": "schedule_tweet",
  "params": {
    "content": "Good morning! Starting the day right.",
    "scheduled_time": "2026-03-02T08:00:00Z"
  }
}
```

**Example Response:**

```json
{
  "status": "scheduled",
  "file": "vault/Scheduled/twitter_scheduled_20260302_080000.md",
  "scheduled_time": "2026-03-02T08:00:00Z"
}
```

### get_timeline

Get recent tweets from timeline.

```json
{
  "name": "get_timeline",
  "description": "Get recent tweets from timeline",
  "input_schema": {
    "type": "object",
    "properties": {
      "count": {
        "type": "integer",
        "default": 10
      }
    }
  }
}
```

## Content Limits

| Element | Limit |
|---------|-------|
| Tweet text | 280 characters |
| Images | Up to 4 per tweet |
| Video | Up to 2:20 (140 seconds) |
| GIF | Up to 15MB |

### Twitter Blue / Premium Features

| Feature | Limit |
|---------|-------|
| Long tweets | 4,000 characters |
| Longer video | Up to 10 minutes |

## Tweet Composition Best Practices

### Character Count

```python
# Max 280 characters
# Use URL shortener for links (counts as 23 chars)
# Mention limit: 50 users

def validate_tweet(content):
    if len(content) > 280:
        return {"error": "Tweet exceeds 280 characters"}

    # Count mentions
    mentions = content.count('@')
    if mentions > 50:
        return {"error": "Too many mentions"}

    return {"valid": True}
```

### Hashtags

```python
# Recommended: 1-2 hashtags per tweet
# Maximum: No hard limit, but readability suffers

tweet = """
Big announcement! We're launching our new product next week.

Stay tuned for more details.

#LaunchDay #Innovation
"""
```

### Threads

```python
def create_thread(tweets):
    """
    Create a thread of connected tweets.
    Each tweet replies to the previous one.
    """
    thread_id = None
    results = []

    for tweet in tweets:
        result = post_tweet({
            'content': tweet['content'],
            'reply_to': thread_id
        })
        thread_id = result.get('tweet_id')
        results.append(result)

    return results
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `content_too_long` | Over 280 chars | Truncate or thread |
| `duplicate_tweet` | Same content recently posted | Modify content |
| `rate_limit` | Tweet limit reached | Wait 15 min |
| `not_authenticated` | Session expired | Re-authenticate |
| `media_upload_failed` | Invalid media | Check format/size |

## Rate Limits

| Action | Limit | Window |
|--------|-------|--------|
| Tweets | 2,400 | per day |
| Updates | 1 | per 2 min |
| API calls | 900 | per 15 min |

## Code Examples

### Python Integration

```python
from mcp.twitter.server import TwitterMCPServer

server = TwitterMCPServer()

# Post tweet
result = server.post_tweet({
    'content': 'Hello Twitter! #firstTweet'
})

if result['status'] == 'posted':
    print(f"Tweet posted: {result['url']}")
else:
    print(f"Error: {result.get('error')}")
```

### Thread Creation

```python
def create_announcement_thread():
    tweets = [
        {"content": "Big announcement! 🧵"},
        {"content": "We're launching our new product next week!"},
        {"content": "Key features:\n- Fast\n- Reliable\n- Easy to use"},
        {"content": "Stay tuned for the official launch! #LaunchDay"}
    ]

    return create_thread(tweets)
```

### Dry Run Mode

```python
# Set DRY_RUN=true for testing
import os
os.environ['DRY_RUN'] = 'true'

# Creates draft instead of posting
result = server.post_tweet({
    'content': 'Test tweet'
})

# Returns draft file
print(result['file'])  # vault/Drafts/twitter_draft_xxx.md
```