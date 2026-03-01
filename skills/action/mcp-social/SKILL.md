---
name: mcp-social
description: |
  Handles social media operations through the Social MCP servers including LinkedIn,
  Twitter/X, Facebook, and Instagram. Posts content, schedules posts, and manages
  social presence. Use when execute-action calls for social operations, user requests
  posting with commands like /post-linkedin or /post-twitter, or processing approved
  social content from Drafts/.
allowed-tools: [Read, Write, Glob, Grep, Bash]
---

# MCP Social Handler

Execute social media operations through the Model Context Protocol (MCP) social servers with multi-platform support, scheduling, and engagement tracking.

## When to Use

- User commands: `/post-linkedin`, `/post-twitter`, `/schedule-social`
- Execute-action skill calls with `action_type: social_*`
- Processing approved social media content from Drafts/
- Scheduled social posts from Scheduled/
- CEO Briefing mentions social media activity

## Before Implementation

| Source | Gather |
|--------|--------|
| **MCP Configuration** | Social MCP server connection details |
| **Company_Handbook.md** | Social media policies, brand guidelines |
| **Pending_Approval/** | Check for approved social posts |
| **Drafts/** | Check for existing social drafts |
| **Scheduled/** | Check for pending scheduled posts |

## Supported Platforms

| Platform | MCP Server | Operations | HITL Required |
|----------|-----------|------------|---------------|
| LinkedIn | linkedin-server | create_post, get_profile, schedule | For new content |
| Twitter/X | twitter-server | post_tweet, schedule_tweet | For new content |
| Facebook | social-server | post_facebook, schedule_social | Always |
| Instagram | social-server | post_instagram, schedule_social | Always |

## Available Operations

### 1. LinkedIn Post

```yaml
operation: create_linkedin_post
description: Create a LinkedIn post
requires_approval: true (for new content)

parameters:
  content:
    type: string
    required: true
    description: Post content (max 3000 chars)

  media_path:
    type: string
    required: false
    description: Path to image or video file

autonomy_rules:
  personal_brand:
    level: 2
    auto_post: true
    notify: true

  company_brand:
    level: 3
    requires_approval: true
```

### 2. Twitter Post

```yaml
operation: post_tweet
description: Post to Twitter/X
requires_approval: true (for new content)

parameters:
  content:
    type: string
    required: true
    description: Tweet content (max 280 chars)

  media_paths:
    type: array
    required: false
    description: Paths to images (max 4)

autonomy_rules:
  reply_to_known:
    level: 2
    auto_post: true

  new_tweet:
    level: 3
    requires_approval: true
```

### 3. Facebook Post

```yaml
operation: post_facebook
description: Post to Facebook page
requires_approval: true

parameters:
  content:
    type: string
    required: true

  page_id:
    type: string
    required: false
    description: Facebook page ID
```

### 4. Instagram Post

```yaml
operation: post_instagram
description: Post to Instagram (requires image)
requires_approval: true

parameters:
  caption:
    type: string
    required: true
    description: Image caption (max 2200 chars)

  image_path:
    type: string
    required: true
    description: Path to image file
```

### 5. Schedule Social Post

```yaml
operation: schedule_social
description: Schedule a post for later
requires_approval: false (drafting)

parameters:
  platform:
    type: string
    required: true
    enum: [linkedin, twitter, facebook, instagram]

  content:
    type: string
    required: true

  scheduled_time:
    type: string
    required: true
    description: ISO 8601 timestamp

output:
  location: vault/Scheduled/{platform}_scheduled_{timestamp}.md
  returns: schedule_id, scheduled_time
```

## Workflow

### Phase 1: Pre-flight Check

```
1. Verify MCP server availability for platform
2. Check authentication status (session valid)
3. Validate content against platform limits
4. Check for restricted content
5. Check autonomy level for content type
6. Return Ready() or ApprovalRequired()
```

### Phase 2: Execute Operation

```
1. Get appropriate MCP server for platform
2. Execute operation (create_post, post_tweet, etc.)
3. Log action with content preview
4. Return result
```

### Phase 3: Post-operation

```
1. Update audit log
2. If scheduled: create Scheduled/ file
3. If posted: move approval file to Done/
4. Update dashboard
5. Schedule engagement check (async)
```

## Error Handling

| Error Code | Description | Recovery |
|------------|-------------|----------|
| `AUTH_REQUIRED` | Session expired/not authenticated | Prompt for re-auth |
| `CONTENT_TOO_LONG` | Exceeds platform character limit | Truncate or reject |
| `MEDIA_UPLOAD_FAILED` | Failed to upload media | Retry with smaller file |
| `RATE_LIMITED` | Platform rate limit hit | Queue for retry |
| `PLATFORM_ERROR` | Platform returned error | Log and alert |
| `NETWORK_ERROR` | Network timeout | Retry with backoff |
| `MCP_UNAVAILABLE` | MCP server down | Alert, queue operation |

## Definition of Done

A social media operation is complete when:

- [ ] MCP server call succeeded OR error was handled gracefully
- [ ] Action logged to `vault/Logs/social_operations.json`
- [ ] For posts: Confirmation received with post ID
- [ ] For scheduled: File created in `vault/Scheduled/`
- [ ] For drafts: File created in `vault/Drafts/`
- [ ] Dashboard updated with post count

## Evaluation Criteria

### Outcome Goals (Must Pass)

| Criterion | Check |
|-----------|-------|
| Content posted/scheduled | `command_execution` event with platform call |
| MCP response received | JSON response with status field |
| Content validated | Length within platform limits |
| Audit log created | File exists in `vault/Logs/social_operations.json` |

### Process Goals

| Criterion | Check |
|-----------|-------|
| Platform selected | Correct MCP server called |
| Authentication verified | Session checked before post |
| Content guidelines followed | No prohibited content |
| Approval flow respected | Level 3+ content requires approval |

### Style Goals

| Criterion | Check |
|-----------|-------|
| Brand voice consistent | Content matches Company_Handbook.md tone |
| Hashtags appropriate | Platform-specific hashtag limits |
| Media attached correctly | Correct format and size |
| Links valid | No broken links in content |

### Efficiency Goals

| Criterion | Check |
|-----------|-------|
| Token count | < 1500 tokens for simple post |
| No redundant API calls | Single post per content |
| Media optimized | Compressed before upload |
| Batch scheduling | Group scheduled posts |

## Deterministic Checks

```bash
# Verify LinkedIn post
codex exec --json 2>/dev/null | jq 'select(.type == "command_execution") | select(.command | contains("create_post"))'

# Verify Twitter post
codex exec --json 2>/dev/null | jq 'select(.type == "command_execution") | select(.command | contains("post_tweet"))'

# Verify content validation
codex exec --json 2>/dev/null | jq 'select(.type == "command_execution") | select(.command | contains("validate_content"))'

# Verify scheduled post
codex exec --json 2>/dev/null | jq 'select(.type == "file_write") | select(.path | contains("Scheduled"))'
```

## Quality Rubric

| Criterion | Score | Description |
|-----------|-------|-------------|
| Correctness | 5 | Posted to correct platform with correct content |
| Brand Safety | 5 | Follows brand guidelines, no violations |
| Timeliness | 5 | Posted at optimal time for platform |
| Engagement | 5 | Content designed for engagement |
| Auditability | 5 | Complete log with all required fields |

**Passing Score:** 20/25 minimum

## Content Guidelines

### Prohibited Content

```
❌ Personal attacks or criticism of individuals
❌ Confidential or proprietary information
❌ Legal advice or medical claims
❌ Discriminatory language
❌ Spam or misleading content
❌ Unverified claims as facts
```

### Content Categories

| Category | Autonomy | Approval | Frequency |
|----------|----------|----------|-----------|
| Educational | Level 2 | No | 40% |
| Behind-the-scenes | Level 2 | No | 20% |
| Engagement | Level 2 | No | 15% |
| Announcement | Level 3 | Yes | 15% |
| Promotional | Level 3 | Yes | 10% |

### Platform Limits

| Platform | Max Length | Hashtags | Media |
|----------|------------|----------|-------|
| LinkedIn | 3000 chars | 5-10 recommended | Images, videos |
| Twitter | 280 chars | 1-2 recommended | Up to 4 images |
| Facebook | 63206 chars | 2-3 recommended | Images, videos |
| Instagram | 2200 chars | 10-20 recommended | Required |

## Usage Examples

### Post to LinkedIn

```bash
/post-linkedin --content "Excited to share our latest project update..." --media ./images/project.png
```

### Schedule Twitter Post

```bash
/schedule-social --platform twitter --content "Big announcement coming tomorrow!" --time "2026-03-02T09:00:00Z"
```

### Post to Multiple Platforms

```bash
/post-social --platforms linkedin,twitter --content "Check out our new blog post!" --link https://example.com/blog
```

### Check Platform Status

```bash
/social-status --platform linkedin
# Returns: authenticated, profile_name, last_post
```

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Posted Record | `Done/SOCIAL_*.md` | Completed post record |
| Draft | `Drafts/DRAFT_social_*.md` | Pending drafts |
| Scheduled | `Scheduled/{platform}_*.md` | Scheduled posts |
| Audit Log | `Logs/social_operations.json` | Compliance trail |
| Error Log | `Logs/social_errors.json` | Error tracking |

## References

| File | Purpose |
|------|---------|
| `references/linkedin-api.md` | LinkedIn posting guide |
| `references/twitter-api.md` | Twitter API reference |
| `references/content-guidelines.md` | Brand voice and guidelines |
| `references/error-codes.md` | Complete error code reference |
| `references/scheduling.md` | Best posting times by platform |