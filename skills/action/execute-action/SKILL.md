---
name: execute-action
description: |
  Executes approved actions through MCP servers. Validates approvals,
  calls appropriate MCP tools, handles errors with retry logic, and
  maintains audit trail. Triggers when items appear in Approved/ folder
  or user requests action execution.
allowed-tools: [Read, Write, Glob, Grep, Edit, Bash]
---

# Execute Action - Professional Skill

Executes approved actions safely with full validation, error handling, and audit logging.

## When to Use

- Items appear in `vault/Approved/` folder
- User commands: `/execute-action`, "execute approved items", "run pending actions"
- Orchestrator triggers after approval detected
- Ralph Wiggum loop iteration

## Before Implementation

| Source | Gather |
|--------|--------|
| **Approved/** | Read approved action files |
| **Pending_Approval/** | Verify no duplicates |
| **Company_Handbook.md** | Execution limits, safety rules |
| **MCP Configuration** | Available MCP servers and tools |

## Workflow

### Phase 1: Validation

```
1. Read approved action file
2. Verify approval status (must be in Approved/)
3. Check expiration (not past deadline)
4. Validate action parameters
5. Confirm MCP server availability
```

### Phase 2: Pre-Execution

```yaml
Pre-Execution Checklist:
  - [ ] Approval file is valid
  - [ ] Action type is supported
  - [ ] MCP server is available
  - [ ] Parameters are complete
  - [ ] Rate limits not exceeded
  - [ ] Dry-run flag considered
```

### Phase 3: Execution

```
1. Log execution start
2. Call appropriate MCP tool
3. Handle response:
   - Success: Record result, move files
   - Failure: Retry with backoff, then escalate
   - Timeout: Log and alert
4. Update audit trail
```

### Phase 4: Post-Execution

```
1. Move approved file to Done/
2. Update Plan.md status to completed
3. Update Dashboard.md
4. Create completion log entry
```

## Action Types and MCP Mapping

### Send Email

```yaml
action_type: send_email
mcp_server: email-mcp
mcp_tool: send_email
parameters:
  to: "{recipient_email}"
  subject: "{subject_line}"
  body: "{email_body}"
  attachments: ["{attachment_paths}"]

validation:
  - recipient is valid email
  - subject is not empty
  - body is not empty

rate_limit:
  per_hour: 10
  per_day: 50

retry:
  max_attempts: 3
  backoff: exponential
  initial_delay: 5s
```

### Post Social Media

```yaml
action_type: post_social
mcp_server: social-mcp
mcp_tool: post
parameters:
  platform: "linkedin|twitter|facebook|instagram"
  content: "{post_content}"
  schedule: "{scheduled_time}"  # optional

validation:
  - platform is supported
  - content within character limits
  - media attachments valid (if any)

rate_limit:
  per_hour: 5
  per_day: 20

retry:
  max_attempts: 2
  backoff: fixed
  delay: 30s
```

### Make Payment

```yaml
action_type: make_payment
mcp_server: payment-mcp
mcp_tool: send_payment
parameters:
  recipient: "{recipient_details}"
  amount: "{amount}"
  currency: "USD"
  reference: "{invoice_reference}"
  method: "{payment_method}"

validation:
  - amount is positive
  - recipient details complete
  - budget available
  - not duplicate payment

rate_limit:
  per_hour: 3
  per_day: 10

retry:
  max_attempts: 1  # Don't retry payments
  require_fresh_approval: true  # Re-approve on failure
```

### Schedule Calendar Event

```yaml
action_type: schedule_event
mcp_server: calendar-mcp
mcp_tool: create_event
parameters:
  title: "{event_title}"
  datetime: "{event_datetime}"
  duration: "{duration_minutes}"
  attendees: ["{attendee_emails}"]
  location: "{location_or_link}"

validation:
  - datetime is future
  - duration is reasonable
  - attendees are valid emails

rate_limit:
  per_hour: 10
  per_day: 50

retry:
  max_attempts: 3
  backoff: exponential
```

### File Operations

```yaml
action_type: file_operation
mcp_server: filesystem  # built-in
mcp_tool: read|write|move|delete
parameters:
  operation: "{operation_type}"
  source: "{source_path}"
  destination: "{destination_path}"  # for move/copy

validation:
  - paths are within vault
  - no overwrite without approval
  - delete only approved files

rate_limit:
  per_hour: 100
  per_day: 1000

retry:
  max_attempts: 3
  backoff: exponential
```

## Error Handling

### Error Categories

| Category | Examples | Recovery |
|----------|----------|----------|
| **Transient** | Network timeout, API rate limit | Retry with backoff |
| **Authentication** | Expired token, revoked access | Alert, pause, require human |
| **Validation** | Invalid parameters, missing fields | Log, reject, notify |
| **System** | MCP server down, disk full | Alert, queue for retry |

### Retry Logic

```python
async def execute_with_retry(action, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            result = await execute_mcp_action(action)
            return Success(result)
        except TransientError as e:
            if attempt < max_attempts - 1:
                delay = calculate_backoff(attempt)
                await sleep(delay)
                continue
            return Failure(e)
        except AuthenticationError as e:
            alert_human("Authentication failed", e)
            return Failure(e)
        except ValidationError as e:
            log_error("Validation failed", e)
            return Failure(e)
```

### Backoff Strategy

```yaml
backoff:
  strategy: exponential
  base_delay: 5s
  max_delay: 60s
  multipliers:
    attempt_1: 5s
    attempt_2: 10s
    attempt_3: 20s
```

## Execution States

```yaml
states:
  pending:
    description: "Action queued for execution"
    next: executing

  executing:
    description: "MCP call in progress"
    next: success|failed|timeout

  success:
    description: "Action completed successfully"
    next: cleanup

  failed:
    description: "Execution failed after retries"
    next: escalation

  timeout:
    description: "Execution exceeded time limit"
    next: escalation

  escalation:
    description: "Human intervention required"
    next: resolved

  resolved:
    description: "Issue resolved, action complete"
    next: cleanup

  cleanup:
    description: "Moving files, updating logs"
    next: done
```

## Audit Logging

Every execution creates detailed audit trail:

```json
{
  "execution_id": "EXEC_20260301_100001",
  "timestamp": "2026-03-01T10:30:00Z",
  "action_type": "send_email",
  "approval_id": "APPROVAL_20260301_100000_EMAIL_client",
  "mcp_server": "email-mcp",
  "mcp_tool": "send_email",
  "parameters": {
    "to": "client@example.com",
    "subject": "Re: Invoice Inquiry",
    "body_length": 245
  },
  "result": "success",
  "response_time_ms": 523,
  "retry_count": 0,
  "artifacts": {
    "approved_file": "Approved/EMAIL_client_approval.md",
    "moved_to": "Done/EMAIL_client_20260301.md"
  }
}
```

## Dry Run Mode

For testing without actual execution:

```yaml
dry_run:
  enabled: true  # Set via environment or config
  behavior:
    - Log intended action
    - Skip MCP call
    - Return simulated success
    - Mark files with DRY_RUN prefix
  logging:
    level: debug
    prefix: "[DRY RUN]"
```

## Safety Checks

```yaml
safety_checks:
  pre_execution:
    - name: rate_limit_check
      description: "Ensure rate limits not exceeded"
      action: abort_if_exceeded

    - name: approval_validity
      description: "Verify approval not expired"
      action: abort_if_expired

    - name: parameter_validation
      description: "Validate all required parameters"
      action: abort_if_invalid

    - name: mcp_availability
      description: "Check MCP server is responsive"
      action: retry_or_abort

  post_execution:
    - name: result_verification
      description: "Verify action completed successfully"
      action: log_and_cleanup

    - name: file_movement
      description: "Move processed files correctly"
      action: retry_on_failure
```

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Execution Log | `Logs/executions.json` | Audit trail |
| Done Item | `Done/{item_id}.md` | Completed record |
| Error Report | `Logs/errors.json` | Failure tracking |
| Dashboard Update | `Dashboard.md` | Status display |

## Example Usage

```
User: /execute-action

Claude: Checking Approved/ folder...

Found 2 approved actions:
1. EMAIL_client_approval.md - Send email to client@example.com
2. PAYMENT_vendor_approval.md - Process $500 payment

Validating approvals...
✓ All approvals valid and not expired

Executing in order of priority:

[1/2] Sending email to client@example.com...
✓ Success (523ms)
→ Moved to Done/EMAIL_client_20260301.md

[2/2] Processing payment to Vendor B LLC...
✓ Success (1.2s)
→ Moved to Done/PAYMENT_vendor_20260301.md

Execution complete. Audit log updated.
```

## References

| File | Purpose |
|------|---------|
| `references/mcp-tools.md` | Complete MCP tool reference |
| `references/rate-limits.md` | Rate limit configurations |
| `references/error-codes.md` | Error code reference |