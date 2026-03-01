---
name: mcp-browser
description: |
  Handles browser automation operations through the Browser MCP server for navigating
  websites, filling forms, clicking elements, and extracting data. Primary use cases
  include payment portal interaction, form submission, and web scraping. Use when
  execute-action requires browser automation or user requests browser-based actions.
allowed-tools: [Read, Write, Glob, Grep, Bash]
---

# MCP Browser Handler

Execute browser automation through the Model Context Protocol (MCP) browser server for navigating websites, filling forms, extracting data, and payment portal interactions.

## When to Use

- Payment processing through web portals
- Form submission on websites
- Web scraping for data extraction
- User commands: `/browse-url`, `/fill-form`, `/click-element`
- Execute-action calls with `action_type: browser_*`

## Before Implementation

| Source | Gather |
|--------|--------|
| **MCP Configuration** | Browser MCP server settings |
| **Company_Handbook.md** | Allowed websites, approval rules |
| **Pending_Approval/** | Approved browser actions |
| **Browser Sessions** | Active session status |

## Available Operations

### 1. Navigate

```yaml
operation: navigate
description: Navigate to a URL
requires_approval: false (for allowed sites)

parameters:
  url:
    type: string
    required: true
    description: URL to navigate to

  wait_until:
    type: string
    enum: [load, domcontentloaded, networkidle]
    default: load
    description: Wait condition

  timeout:
    type: integer
    default: 30000
    description: Timeout in milliseconds

allowed_sites:
  - "*.mybank.com"
  - "*.payment-portal.com"
  - "*.vendor-site.com"

blocked_sites:
  - "*.social-media.com"
  - "*.gambling.com"
```

### 2. Fill Form

```yaml
operation: fill_form
description: Fill form fields on current page
requires_approval: true (for sensitive fields)

parameters:
  fields:
    type: array
    required: true
    items:
      selector: string
      value: string
      field_type: text|password|email|number|select

  submit:
    type: boolean
    default: false
    description: Submit form after filling

sensitive_fields:
  - password
  - credit_card
  - ssn
  - account_number
```

### 3. Extract Data

```yaml
operation: extract
description: Extract data from page
requires_approval: false

parameters:
  selectors:
    type: array
    required: true
    items:
      name: string
      selector: string
      attribute: text|href|src|value
      multiple: boolean

  format:
    type: string
    enum: [json, csv, markdown]
    default: json

output:
  returns: extracted data in specified format
```

### 4. Payment Portal

```yaml
operation: payment_portal
description: Complete payment through web portal
requires_approval: always

parameters:
  portal_url:
    type: string
    required: true

  credentials:
    type: object
    required: true
    properties:
      username: string
      password: string  # Never stored

  payment:
    type: object
    required: true
    properties:
      recipient: string
      amount: number
      account: string
      reference: string

workflow:
  1. Navigate to portal
  2. Wait for login page
  3. Fill credentials (requires approval)
  4. Navigate to payment section
  5. Fill payment details
  6. Review (pause for human verification)
  7. Submit payment
  8. Capture confirmation
  9. Log transaction
```

## Workflow

### Phase 1: Pre-flight Check

```
1. Verify MCP server is available
2. Check site permissions (allowed/blocked lists)
3. Check for sensitive fields (require approval)
4. Payment operations always require approval
5. Return Ready() or ApprovalRequired()
```

### Phase 2: Execute Operation

```
1. Get or create browser session
2. Execute browser operation
3. Take screenshot on error
4. Log action with redacted params
5. Return result
```

### Phase 3: Post-operation

```
1. Update audit log
2. Save screenshot if captured
3. Move approval file to Done/ if applicable
4. Update dashboard
```

## Error Handling

| Error Code | Description | Recovery |
|------------|-------------|----------|
| `NAVIGATION_FAILED` | Page failed to load | Retry with timeout |
| `ELEMENT_NOT_FOUND` | Selector not found | Take screenshot, alert |
| `TIMEOUT` | Operation timed out | Increase timeout, retry |
| `AUTH_FAILED` | Login failed | Alert human, don't retry |
| `FORM_VALIDATION` | Form validation error | Screenshot, alert |
| `PAYMENT_FAILED` | Payment rejected | Screenshot, alert |
| `SESSION_EXPIRED` | Browser session ended | Create new session |

## Definition of Done

A browser operation is complete when:

- [ ] Navigation completed OR timeout with retry exhausted
- [ ] Screenshot captured (for errors or payments)
- [ ] Action logged to `vault/Logs/browser_operations.json`
- [ ] For payments: Confirmation captured with transaction ID
- [ ] For extractions: Data saved to specified format
- [ ] Browser session cleaned up

## Evaluation Criteria

### Outcome Goals (Must Pass)

| Criterion | Check |
|-----------|-------|
| Operation completed | `command_execution` event with browser call |
| Screenshot captured | File exists in `Logs/screenshots/` for errors/payments |
| No unhandled errors | Error events have recovery actions |
| Audit log created | File exists in `vault/Logs/browser_operations.json` |

### Process Goals

| Criterion | Check |
|-----------|-------|
| Site permission checked | Allowed/blocked list verified |
| Sensitive fields handled | Approval flow for passwords/payments |
| Human verification for payments | Pause before submission |
| Session cleaned up | Browser closed after operation |

### Style Goals

| Criterion | Check |
|-----------|-------|
| Credentials masked | Passwords never in logs |
| Screenshots professional | No sensitive data visible |
| Audit trail complete | All actions recorded |
| Error messages clear | Human-readable error descriptions |

### Efficiency Goals

| Criterion | Check |
|-----------|-------|
| Token count | < 3000 tokens for navigation |
| Page loads minimized | Single navigation where possible |
| Selectors optimized | Efficient CSS selectors used |
| Screenshots captured | Only when necessary |

## Deterministic Checks

```bash
# Verify navigation occurred
codex exec --json 2>/dev/null | jq 'select(.type == "command_execution") | select(.command | contains("navigate"))'

# Verify form filled
codex exec --json 2>/dev/null | jq 'select(.type == "command_execution") | select(.command | contains("fill_form"))'

# Verify screenshot captured
codex exec --json 2>/dev/null | jq 'select(.type == "file_write") | select(.path | contains("screenshots"))'

# Verify payment approval
codex exec --json 2>/dev/null | jq 'select(.type == "file_move") | select(.destination | contains("Approved"))'
```

## Quality Rubric

| Criterion | Score | Description |
|-----------|-------|-------------|
| Correctness | 5 | Correct page loaded, correct data extracted |
| Safety | 5 | Credentials protected, approvals required |
| Auditability | 5 | Complete audit trail with screenshots |
| Reliability | 5 | Handles errors gracefully |
| Performance | 5 | Efficient page loads and operations |

**Passing Score:** 20/25 minimum

## Security

### Credential Handling

```yaml
credentials:
  storage: vault/.secrets/
  encryption: at-rest
  never_log: true
  never_screenshot: true

  masking:
    - field: password
      mask: "****"
    - field: credit_card
      mask: "****-****-****-{last4}"
```

### Site Restrictions

```yaml
allowed_sites:
  banking:
    - "*.mybank.com"
    - "*.chase.com"

  payments:
    - "*.payment-portal.com"
    - "*.stripe.com"

blocked_sites:
  - "*.facebook.com"
  - "*.twitter.com"
  - "*.gambling.*"
  - "*.adult.*"
```

## Usage Examples

### Navigate to Site

```bash
/browse-url --url "https://vendor-portal.example.com/invoices" --wait-until networkidle
```

### Fill and Submit Form

```bash
/fill-form --fields '[{"selector": "#email", "value": "user@example.com"},
                      {"selector": "#message", "value": "Hello"}]' --submit
```

### Extract Data

```bash
/extract-data --selectors '[{"name": "title", "selector": "h1"},
                            {"name": "price", "selector": ".price"}]' --format json
```

### Process Payment

```bash
/payment --portal "https://bank.example.com" --recipient "Vendor A" --amount 500.00
# Creates approval request for human verification
```

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Screenshots | `Logs/screenshots/*.png` | Debugging & verification |
| Audit Log | `Logs/browser_operations.json` | Compliance trail |
| Error Log | `Logs/browser_errors.json` | Error tracking |
| Page HTML | `Logs/browser_html/*.html` | Debug captures |

## References

| File | Purpose |
|------|---------|
| `references/playwright-api.md` | Playwright API reference |
| `references/selectors.md` | Selector patterns guide |
| `references/payment-workflows.md` | Common payment portal patterns |
| `references/error-codes.md` | Complete error code reference |