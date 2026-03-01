# LinkedIn API Reference

## Overview

LinkedIn MCP Server uses Playwright-based browser automation to interact with LinkedIn. This approach provides full functionality without requiring LinkedIn API approval.

## Authentication

### Session Setup

```bash
# Initialize LinkedIn session
python -m mcp.linkedin.server --setup

# Check session status
python -m mcp.linkedin.server --check
```

### Session Storage

```
vault/secrets/linkedin_session/
├── Default/
├── Local Storage/
├── Session Storage/
└── Cookies
```

## Available Tools

### create_post

Create a LinkedIn post with optional media.

```json
{
  "name": "create_post",
  "description": "Create a LinkedIn post",
  "input_schema": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "Post content (max 3000 chars)"
      },
      "media_path": {
        "type": "string",
        "description": "Path to media file (image/video)"
      }
    },
    "required": ["content"]
  }
}
```

**Example Request:**

```json
{
  "method": "create_post",
  "params": {
    "content": "Excited to share our latest project milestone! #innovation #teamwork",
    "media_path": "/vault/media/project_photo.jpg"
  }
}
```

**Example Response:**

```json
{
  "status": "posted",
  "message": "Successfully posted to LinkedIn",
  "content": "Excited to share our latest project milestone!..."
}
```

### get_profile

Get current LinkedIn profile information.

```json
{
  "name": "get_profile",
  "description": "Get current LinkedIn profile info",
  "input_schema": {
    "type": "object",
    "properties": {}
  }
}
```

**Example Response:**

```json
{
  "status": "success",
  "profile_url": "https://linkedin.com/in/username",
  "name": "John Doe"
}
```

### schedule_post

Schedule a LinkedIn post for later.

```json
{
  "name": "schedule_post",
  "description": "Schedule a LinkedIn post",
  "input_schema": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "Post content"
      },
      "scheduled_time": {
        "type": "string",
        "description": "ISO 8601 timestamp"
      },
      "media_path": {
        "type": "string",
        "description": "Path to media file"
      }
    },
    "required": ["content", "scheduled_time"]
  }
}
```

**Example Request:**

```json
{
  "method": "schedule_post",
  "params": {
    "content": "Morning motivation! Starting the week strong.",
    "scheduled_time": "2026-03-02T09:00:00Z"
  }
}
```

### check_session

Verify LinkedIn session is valid.

```json
{
  "name": "check_session",
  "description": "Check if LinkedIn session is valid",
  "input_schema": {
    "type": "object",
    "properties": {}
  }
}
```

**Example Response:**

```json
{
  "status": "authenticated",
  "profile_name": "John Doe",
  "profile_url": "https://linkedin.com/in/johndoe"
}
```

## Content Limits

| Element | Limit |
|---------|-------|
| Post text | 3,000 characters |
| Hashtags | Recommended 3-5, Max 30 |
| Images | Up to 9 (album) |
| Video | Up to 10 minutes, 200MB |
| Documents | Up to 100MB |

## Best Practices

### Post Length

- Optimal: 150-300 characters
- Maximum engagement: 1,200-1,500 characters
- Use line breaks for readability

### Hashtags

```python
# Recommended: 3-5 hashtags
content = """
Excited to share our latest project milestone!

Key achievements:
- 50% improvement in efficiency
- Team collaboration at its best
- Innovation driving results

#innovation #teamwork #projectmanagement
"""
```

### Media

```python
# Supported formats
images = ['.jpg', '.jpeg', '.png', '.gif']
videos = ['.mp4', '.mov']

# Optimal image size: 1200x1200 pixels
# Max file size: 8MB for images, 200MB for videos
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `not_authenticated` | Session expired | Re-run setup |
| `post_failed` | LinkedIn error | Check content |
| `media_upload_failed` | File too large | Compress media |
| `rate_limit` | Too many posts | Wait and retry |

## Code Examples

### Python Integration

```python
from mcp.linkedin.server import LinkedInMCPServer

server = LinkedInMCPServer()

# Check session
status = server.check_session()
if status['status'] != 'authenticated':
    print("Please run setup first")
    exit(1)

# Create post
result = server.create_post({
    'content': 'Hello LinkedIn!',
    'media_path': '/path/to/image.jpg'
})

print(f"Post status: {result['status']}")
```

### Integration with Skill

```python
# In execute-action skill
def handle_linkedin_post(action):
    # Verify approval
    if not has_approval(action):
        return create_approval_request(action)

    # Get MCP server
    server = get_mcp_server('linkedin')

    # Execute post
    result = server.handle_request('create_post', {
        'content': action['params']['content'],
        'media_path': action['params'].get('media_path')
    })

    # Log result
    log_action('linkedin_post', result)

    return result
```