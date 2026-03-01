# Social Media MCP Error Codes Reference

## Error Categories

### Authentication Errors (AUTH_*)

| Code | Description | Recovery |
|------|-------------|----------|
| `AUTH_REQUIRED` | Session not authenticated | Run setup_session |
| `AUTH_EXPIRED` | Session has expired | Re-authenticate |
| `AUTH_INVALID` | Invalid session data | Delete and recreate session |
| `AUTH_RATE_LIMITED` | Too many auth attempts | Wait 1 hour |
| `AUTH_FAILED` | General auth failure | Check credentials |

```python
def handle_auth_error(error):
    if error.code == 'AUTH_EXPIRED':
        return prompt_reauth()
    elif error.code == 'AUTH_REQUIRED':
        return run_setup()
    else:
        return log_and_alert(error)
```

### Content Errors (CONTENT_*)

| Code | Description | Recovery |
|------|-------------|----------|
| `CONTENT_TOO_LONG` | Exceeds platform limit | Truncate content |
| `CONTENT_EMPTY` | No content provided | Request content |
| `CONTENT_INVALID` | Invalid characters/format | Sanitize content |
| `CONTENT_BLOCKED` | Content violates policy | Review and modify |
| `CONTENT_DUPLICATE` | Duplicate post | Wait or modify |

```python
def handle_content_error(error, content, platform):
    limits = get_platform_limits(platform)

    if error.code == 'CONTENT_TOO_LONG':
        # Truncate to limit
        truncated = content[:limits['max_length']-3] + '...'
        return {'content': truncated, 'status': 'modified'}

    elif error.code == 'CONTENT_BLOCKED':
        # Flag for review
        return create_approval_request(
            reason='Content policy violation',
            content=content
        )
```

### Media Errors (MEDIA_*)

| Code | Description | Recovery |
|------|-------------|----------|
| `MEDIA_NOT_FOUND` | File not found | Check path |
| `MEDIA_TOO_LARGE` | Exceeds size limit | Compress media |
| `MEDIA_INVALID_TYPE` | Unsupported format | Convert format |
| `MEDIA_UPLOAD_FAILED` | Upload failed | Retry |
| `MEDIA_PROCESSING` | Processing timeout | Wait and retry |

```python
def handle_media_error(error, media_path):
    if error.code == 'MEDIA_TOO_LARGE':
        # Compress image
        compressed = compress_image(media_path, max_size=8*1024*1024)
        return {'path': compressed, 'status': 'compressed'}

    elif error.code == 'MEDIA_INVALID_TYPE':
        # Convert to supported format
        supported = ['jpg', 'png', 'gif', 'mp4']
        converted = convert_media(media_path, target='jpg')
        return {'path': converted, 'status': 'converted'}
```

### Rate Limit Errors (RATE_*)

| Code | Description | Recovery |
|------|-------------|----------|
| `RATE_LIMITED` | Rate limit hit | Wait and retry |
| `RATE_DAILY_LIMIT` | Daily quota exceeded | Queue for tomorrow |
| `RATE_API_LIMIT` | API limit hit | Wait 15 minutes |

```python
def handle_rate_limit(error, platform):
    wait_times = {
        'RATE_LIMITED': 900,      # 15 minutes
        'RATE_DAILY_LIMIT': 86400, # 24 hours
        'RATE_API_LIMIT': 900     # 15 minutes
    }

    wait_seconds = wait_times.get(error.code, 60)

    return {
        'status': 'rate_limited',
        'retry_after': wait_seconds,
        'message': f'Please wait {wait_seconds//60} minutes'
    }
```

### Platform Errors (PLATFORM_*)

| Code | Description | Recovery |
|------|-------------|----------|
| `PLATFORM_ERROR` | General platform error | Retry |
| `PLATFORM_MAINTENANCE` | Platform under maintenance | Wait |
| `PLATFORM_UNAVAILABLE` | Platform not responding | Retry with backoff |
| `PLATFORM_CHANGED` | Platform UI changed | Alert for update |

```python
def handle_platform_error(error, operation, params):
    if error.code == 'PLATFORM_CHANGED':
        # Critical: requires code update
        alert_maintainer(
            f"Platform {platform} UI may have changed",
            operation=operation,
            error=error
        )
        return {'status': 'error', 'message': 'Platform requires update'}

    elif error.code == 'PLATFORM_MAINTENANCE':
        return schedule_retry(operation, params, delay=3600)
```

### Network Errors (NETWORK_*)

| Code | Description | Recovery |
|------|-------------|----------|
| `NETWORK_TIMEOUT` | Request timed out | Retry with backoff |
| `NETWORK_ERROR` | Connection failed | Retry |
| `NETWORK_SSL` | SSL certificate error | Check connection |

```python
def handle_network_error(error, operation, params, attempt):
    max_retries = 3
    backoff_base = 5  # seconds

    if attempt >= max_retries:
        return {'status': 'failed', 'message': 'Max retries exceeded'}

    delay = backoff_base * (2 ** attempt)  # Exponential backoff

    return schedule_retry(operation, params, delay=delay)
```

### Session Errors (SESSION_*)

| Code | Description | Recovery |
|------|-------------|----------|
| `SESSION_EXPIRED` | Login session ended | Re-authenticate |
| `SESSION_INVALID` | Corrupted session | Delete and recreate |
| `SESSION_NOT_FOUND` | No session file | Run setup |

```python
def handle_session_error(error, platform):
    session_path = get_session_path(platform)

    if error.code in ['SESSION_EXPIRED', 'SESSION_INVALID', 'SESSION_NOT_FOUND']:
        # Clean up old session
        if session_path.exists():
            shutil.rmtree(session_path)

        # Prompt for new session
        return {
            'status': 'session_required',
            'message': f'Please run: python -m mcp.{platform}.server --setup'
        }
```

## Error Response Format

All errors follow this standard format:

```json
{
  "status": "error",
  "code": "CONTENT_TOO_LONG",
  "platform": "twitter",
  "message": "Tweet exceeds 280 character limit",
  "details": {
    "content_length": 350,
    "max_length": 280,
    "exceeded_by": 70
  },
  "recovery": {
    "suggestion": "Truncate content or create a thread",
    "actions": [
      "truncate_content",
      "create_thread"
    ]
  }
}
```

## Error Recovery Flow

```python
async def execute_with_recovery(operation, params, platform):
    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        try:
            result = await execute_operation(operation, params, platform)
            return result

        except SocialMediaError as e:
            attempt += 1

            # Log error
            log_error(e, operation, params, attempt)

            # Get recovery strategy
            strategy = get_recovery_strategy(e.code)

            if strategy == 'retry':
                await asyncio.sleep(get_backoff_delay(attempt))
                continue

            elif strategy == 'reauth':
                await prompt_reauth(platform)
                continue

            elif strategy == 'modify':
                modified_params = modify_params(params, e)
                return await execute_operation(operation, modified_params, platform)

            elif strategy == 'abort':
                return {
                    'status': 'failed',
                    'error': e.code,
                    'message': e.message
                }

    return {'status': 'failed', 'message': 'Max retries exceeded'}
```

## Error Monitoring

### Alert Thresholds

```yaml
alerts:
  - type: rate_limit
    threshold: 5 per hour
    action: notify_user

  - type: auth_failure
    threshold: 3 per day
    action: notify_admin

  - type: platform_error
    threshold: 2 per hour
    action: notify_maintainer

  - type: network_error
    threshold: 10 per hour
    action: check_connectivity
```

### Error Logging

```python
def log_error(error, operation, params, attempt):
    error_log = {
        'timestamp': now().isoformat(),
        'error_code': error.code,
        'error_message': error.message,
        'operation': operation,
        'platform': params.get('platform'),
        'attempt': attempt,
        'params_redacted': redact_sensitive(params)
    }

    write_to_log(error_log, 'Logs/social_errors.json')

    # Also write to audit log
    audit_log({
        'type': 'error',
        'category': error.category,
        'severity': get_severity(error.code)
    })
```

## Common Error Scenarios

### Scenario 1: LinkedIn Session Expired

```python
# Error
{'code': 'AUTH_EXPIRED', 'platform': 'linkedin'}

# Recovery
result = handle_auth_error({'code': 'AUTH_EXPIRED'})
# Returns: {'status': 'session_required', 'setup_command': '...'}
```

### Scenario 2: Twitter Rate Limited

```python
# Error
{'code': 'RATE_LIMITED', 'platform': 'twitter', 'retry_after': 900}

# Recovery
result = handle_rate_limit({'code': 'RATE_LIMITED'}, 'twitter')
# Returns: {'status': 'rate_limited', 'retry_after': 900}
```

### Scenario 3: Content Too Long

```python
# Error
{'code': 'CONTENT_TOO_LONG', 'platform': 'twitter', 'details': {'content_length': 350}}

# Recovery
result = handle_content_error({'code': 'CONTENT_TOO_LONG'}, content, 'twitter')
# Returns: {'content': 'truncated...', 'status': 'modified'}
```