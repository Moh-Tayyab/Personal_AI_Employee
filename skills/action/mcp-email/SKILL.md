---
name: mcp-email
description: |
  Handles email operations through the Email MCP server including sending, drafting,
  searching, and managing emails. Use when execute-action skill calls for email
  operations, user requests email actions with commands like /send-email or /draft-email,
  or when responding to processed emails requiring reply.
allowed-tools: [Read, Write, Glob, Grep, Bash]
---

# MCP Email Handler

Execute email operations through the Model Context Protocol (MCP) email server with full error handling, rate limiting, and audit logging.

## When to Use

- User commands: `/send-email`, `/draft-email`, `/search-email`
- Execute-action skill calls with `action_type: send_email`
- Processing email action items from Plans/
- Responding to emails requiring reply
- Scheduled email campaigns (with approval)

## Before Implementation

| Source | Gather |
|--------|--------|
| **MCP Configuration** | Email MCP server connection details |
| **Company_Handbook.md** | Email sending rules, signatures |
| **Pending_Approval/** | Check for approved email actions |
| **Drafts/** | Check for existing drafts |

## Available Operations

### 1. Send Email

```yaml
operation: send_email
description: Send an email immediately
requires_approval: depends on autonomy level

parameters:
  to:
    type: string|array
    required: true
    description: Recipient email address(es)

  subject:
    type: string
    required: true
    description: Email subject line

  body:
    type: string
    required: true
    description: Email body (plain text or HTML)

  cc:
    type: string|array
    required: false
    description: CC recipients

  attachments:
    type: array
    required: false
    description: File paths to attach

autonomy_rules:
  known_contact:
    level: 2
    auto_send: true
    notify: true

  new_contact:
    level: 3
    requires_approval: true
```

### 2. Draft Email

```yaml
operation: draft_email
description: Create email draft without sending
requires_approval: false

parameters:
  to: string|array
  subject: string
  body: string
  cc: string|array (optional)
  attachments: array (optional)

output:
  location: vault/Drafts/DRAFT_email_{timestamp}.md
  returns: draft_id
```

### 3. Search Email

```yaml
operation: search_email
description: Search email history
requires_approval: false

parameters:
  query:
    type: string
    required: true
    description: Gmail search query

  max_results:
    type: integer
    default: 10
    max: 100

output:
  returns: array of email objects
```

## Workflow

### Phase 1: Pre-flight Check

```
1. Verify MCP server is available
2. Check rate limits (10/hour, 50/day for send)
3. Validate parameters (to, subject, body)
4. Check autonomy level for recipient
5. If level 3+ and new contact → request approval
```

### Phase 2: Execute Operation

```
1. Call MCP server with operation
2. Log action with redacted params
3. Return result
```

### Phase 3: Post-operation

```
1. Write audit log
2. Move approval file to Done/ if applicable
3. Update dashboard
4. Send notification if configured
```

## Error Handling

| Error Code | Description | Recovery |
|------------|-------------|----------|
| `AUTH_FAILED` | Authentication failed | Refresh token, retry |
| `RATE_LIMIT` | API rate limit exceeded | Wait, exponential backoff |
| `INVALID_RECIPIENT` | Invalid email address | Return error to user |
| `ATTACHMENT_TOO_LARGE` | File exceeds 25MB | Compress or reject |
| `QUOTA_EXCEEDED` | Daily sending quota exceeded | Queue for next day |
| `NETWORK_ERROR` | Network timeout | Retry with backoff |
| `MCP_UNAVAILABLE` | MCP server down | Alert, queue operation |

## Definition of Done

An email operation is complete when:

- [ ] MCP server call succeeded OR error was handled gracefully
- [ ] Action logged to `vault/Logs/email_operations.json`
- [ ] For sent emails: Confirmation received with message ID
- [ ] For drafts: File created in `vault/Drafts/`
- [ ] For approvals: File moved to appropriate folder
- [ ] Dashboard updated with operation count

## Evaluation Criteria

### Outcome Goals (Must Pass)

| Criterion | Check |
|-----------|-------|
| Email sent/drafted | `command_execution` event with send/draft call |
| MCP response received | JSON response with status field |
| No unhandled errors | Error events have recovery actions |
| Audit log created | File exists in `vault/Logs/email_operations.json` |

### Process Goals

| Criterion | Check |
|-----------|-------|
| Pre-flight checks run | Verify rate limit and validation steps |
| Autonomy level checked | Level 3+ recipients require approval |
| MCP server called | `handle_request` method invoked |
| Post-operation completed | Dashboard updated, logs written |

### Style Goals

| Criterion | Check |
|-----------|-------|
| Professional tone | Email body follows Company_Handbook.md tone |
| Signature included | Signature matches template |
| Subject clear | Subject is descriptive and appropriate |
| No sensitive data | No passwords, tokens in email content |

### Efficiency Goals

| Criterion | Check |
|-----------|-------|
| Token count | < 2000 tokens for send operation |
| Commands executed | < 5 commands for simple send |
| No redundant reads | Don't re-read same files |
| Batch operations | Use batch for multiple recipients |

## Deterministic Checks

Run with structured output to verify:

```bash
# Verify email was sent
codex exec --json 2>/dev/null | jq 'select(.type == "command_execution") | select(.command | contains("send_email"))'

# Verify MCP server was called
codex exec --json 2>/dev/null | jq 'select(.type == "command_execution") | select(.command | contains("mcp_call"))'

# Verify audit log created
codex exec --json 2>/dev/null | jq 'select(.type == "file_write") | select(.path | contains("Logs/email"))'
```

## Quality Rubric

| Criterion | Score | Description |
|-----------|-------|-------------|
| Correctness | 5 | Email sent to correct recipient with correct content |
| Completeness | 5 | All required fields present, attachments included |
| Timeliness | 5 | Sent within expected timeframe |
| Professionalism | 5 | Follows company communication guidelines |
| Audit Trail | 5 | Complete log with all required fields |

**Passing Score:** 20/25 minimum

## Usage Examples

### Send Email

```bash
/send-email --to client@example.com --subject "Re: Invoice Inquiry" --body "Thank you for your email..."
```

### Search Email

```bash
/search-email --query "from:client@example.com" --max-results 20 --include-body
```

### Draft Email

```bash
/draft-email --to team@company.com --subject "Weekly Update" --body "Here's the weekly update..."
```

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Sent Email Record | `Done/EMAIL_*.md` | Completed record |
| Draft | `Drafts/DRAFT_*.md` | Pending drafts |
| Audit Log | `Logs/email_operations.json` | Compliance trail |
| Error Log | `Logs/email_errors.json` | Error tracking |

## References

| File | Purpose |
|------|---------|
| `references/gmail-api.md` | Gmail API reference |
| `references/oauth-setup.md` | OAuth configuration guide |
| `references/error-codes.md` | Complete error code reference |
| `references/templates.md` | Email template library |