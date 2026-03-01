---
name: execute-action
description: |
  Executes approved actions through MCP servers. Reads items from Approved folder,
  routes to appropriate MCP (email, browser, social, calendar), executes with retry
  logic, logs results, and moves completed items to Done folder.
allowed-tools: [Read, Write, Glob, Grep, Bash]
model: sonnet
---

# Execute Action - Agent Skill

Executes approved actions through MCP servers with full audit logging, error recovery, and human-in-the-loop enforcement.

## When to Use

- Items moved to `vault/Approved/` folder
- User commands: `/execute-action`, "run this", "execute the plan"
- Orchestrator triggers for approved items
- After human approval of Level 3 actions

## Before Implementation

| Source | Gather |
|--------|--------|
| **Approved/** | Read all approved action items |
| **mcp_config.json** | Available MCP servers and endpoints |
| **Company_Handbook.md** | Execution limits, safety rules |
| **Logs/** | Check for retry state, previous attempts |

## Workflow

### Phase 1: Discovery
1. Scan `Approved/` for action items
2. Parse action type and target MCP server
3. Verify approval status and timestamp
4. Check for expired approvals (>24h old)

### Phase 2: Routing
Match action to MCP server:

| Action Type | MCP Server | Endpoint |
|-------------|------------|----------|
| send_email | email-mcp | /send |
| post_linkedin | linkedin-mcp | /post |
| post_twitter | twitter-mcp | /post |
| create_event | calendar-mcp | /create |
| make_payment | browser-mcp | /payment |
| browse_web | browser-mcp | /navigate |

### Phase 3: Execution
For each approved action:
1. Validate action parameters
2. Call MCP server with retry logic (3 attempts, exponential backoff)
3. Capture response and result
4. Log to audit log

### Phase 4: Documentation
1. Move completed items to `Done/`
2. Update Dashboard.md with execution status
3. Write detailed log to `Logs/YYYY-MM-DD.json`

## Action Types Supported

### Email Actions
```yaml
action: send_email
parameters:
  to: recipient@example.com
  subject: "Re: Your inquiry"
  body: |
    Dear Sender,
    <email body>
  draft_id: DRAFT_20260301_xxx
```

### LinkedIn Actions
```yaml
action: post_linkedin
parameters:
  content: "Post content here..."
  scheduled_time: "2026-03-01T10:00:00Z"
  media: /path/to/image.png  # optional
```

### Calendar Actions
```yaml
action: create_event
parameters:
  title: "Meeting with Client"
  start: "2026-03-01T14:00:00Z"
  end: "2026-03-01T15:00:00Z"
  attendees:
    - client@example.com
  description: "Quarterly review"
```

### Payment Actions (Always Requires Manual Confirmation)
```yaml
action: make_payment
parameters:
  amount: 150.00
  currency: USD
  recipient: vendor@example.com
  reference: "Invoice #1234"
  requires_manual_step: true  # Opens browser for user to complete
```

## Retry Logic

```yaml
retry_policy:
  max_attempts: 3
  backoff: exponential
  base_delay: 1s
  max_delay: 30s

  retryable_errors:
    - "network_timeout"
    - "rate_limit"
    - "server_error"
    - "temporary_failure"

  non_retryable_errors:
    - "authentication_failed"
    - "invalid_parameters"
    - "permission_denied"
    - "not_found"
```

## Error Handling

| Error | Recovery Action |
|-------|-----------------|
| MCP server unavailable | Retry with backoff, alert after 3 failures |
| Authentication failed | Alert human immediately, do not retry |
| Rate limited | Wait for reset time, queue for retry |
| Invalid parameters | Log error, alert human, skip |
| Network timeout | Retry up to 3 times with exponential backoff |
| Permission denied | Move to Rejected/, alert human |
| Payment blocked | Always requires manual step - open browser |

## Security Considerations

### Never Do
- Execute items not in Approved/ folder
- Bypass approval for payments (always manual)
- Store credentials in action files
- Execute expired approvals (>24h)

### Always Do
- Verify approval status before execution
- Log all actions with full audit trail
- Use secure credential handling via MCP
- Respect rate limits and quotas

## MCP Server Configuration

```json
// mcp_config.json
{
  "mcpServers": {
    "email-mcp": {
      "command": "python",
      "args": ["mcp/email/server.py"],
      "env": {
        "GMAIL_CREDENTIALS": "${GMAIL_CREDENTIALS_PATH}"
      }
    },
    "linkedin-mcp": {
      "command": "python",
      "args": ["mcp/linkedin/server.py"],
      "env": {
        "LINKEDIN_TOKEN": "${LINKEDIN_TOKEN}"
      }
    },
    "browser-mcp": {
      "command": "python",
      "args": ["mcp/browser/server.py"]
    }
  }
}
```

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Completed Action | `Done/<item>.md` | Archive of executed action |
| Audit Log | `Logs/<date>.json` | Full execution log |
| Error Log | `Logs/errors/<date>.json` | Failed execution details |
| Dashboard | `Dashboard.md` | Status update |

## Definition of Done

- [ ] All Approved/ items processed
- [ ] Actions routed to correct MCP server
- [ ] Execution completed or properly failed
- [ ] Results logged to audit log
- [ ] Completed items moved to Done/
- [ ] Failed items moved to Rejected/ with reason
- [ ] Dashboard updated

## Example Usage

```
User: /execute-action vault/Approved/EMAIL_client_a.md

Claude: Loading approved action from Approved/EMAIL_client_a.md...

Action: send_email
To: client@example.com
Subject: Re: Invoice Inquiry
Server: email-mcp

Executing via email-mcp...
Attempt 1/3: Success!

Response:
- Message ID: msg_abc123
- Sent at: 2026-03-01T10:30:00Z

Moving to Done/EMAIL_client_a.md
Logging to Logs/2026-03-01.json
Updating Dashboard.md

Action completed successfully.
```

## References

| File | Purpose |
|------|---------|
| `references/mcp-endpoints.md` | MCP server API documentation |
| `references/error-codes.md` | Error code reference |
| `references/rate-limits.md` | Rate limiting configuration |

---
*Version: 1.0.0 | Last Updated: 2026-03-01*