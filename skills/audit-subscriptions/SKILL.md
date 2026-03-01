---
name: audit-subscriptions
description: |
  Analyzes subscriptions and recurring expenses to identify optimization opportunities.
  Scans transaction logs, identifies recurring charges, categorizes subscriptions,
  calculates costs, and creates cancellation approval requests for unused services.
allowed-tools: [Read, Write, Glob, Grep]
model: sonnet
---

# Audit Subscriptions - Agent Skill

Analyzes recurring expenses and subscriptions to identify cost optimization opportunities, unused services, and potential cancellations.

## When to Use

- Monthly subscription audit (first of each month)
- User commands: `/audit-subscriptions`, "check subscriptions", "audit expenses"
- Quarterly cost review
- Before budget planning

## Before Implementation

| Source | Gather |
|--------|--------|
| **Logs/** | Transaction history, expense logs |
| **Company_Handbook.md** | Budget limits, approved services |
| **Business_Goals.md** | Priority services, cost targets |
| **Previous Audits/** | Historical subscription data |

## Workflow

### Phase 1: Data Collection
1. Scan `Logs/` for transaction records
2. Extract recurring charges with pattern matching
3. Check `Accounting/` for existing subscription records
4. Read approved services list from Company_Handbook.md

### Phase 2: Pattern Recognition
Identify recurring charges:
- Same vendor, similar amount, regular interval
- Keywords: monthly, subscription, recurring, renewal
- Known service patterns (Netflix, Spotify, SaaS tools)

### Phase 3: Categorization
Group subscriptions by category:
```yaml
categories:
  entertainment:
    - Netflix, Spotify, Hulu, Disney+, YouTube Premium
  software:
    - Adobe, Microsoft 365, Figma, Notion
  productivity:
    - Slack, Zoom, Dropbox, Google Workspace
  development:
    - GitHub, AWS, DigitalOcean, Cursor
  ai:
    - Claude, ChatGPT, Midjourney, Copilot
  business:
    - CRM, invoicing, email tools
```

### Phase 4: Analysis
For each subscription:
- Calculate monthly and annual cost
- Check usage indicators (if available)
- Compare to approved services list
- Identify potential cancellations

### Phase 5: Report Generation
Create audit report with recommendations

## Subscription Detection Patterns

```yaml
patterns:
  monthly_subscription:
    - pattern: "\\$\\d+\\.\\d{2}/mo"
    - pattern: "monthly.*subscription"
    - pattern: "recurring.*\\$\\d+"

  annual_subscription:
    - pattern: "\\$\\d+\\.\\d{2}/yr"
    - pattern: "annual.*subscription"
    - pattern: "yearly.*renewal"

  known_services:
    netflix:
      patterns: ["Netflix", "NETFLIX.COM"]
      typical_cost: "$15.99/mo"
    spotify:
      patterns: ["Spotify", "SPOTIFY"]
      typical_cost: "$9.99/mo"
    github:
      patterns: ["GitHub", "GITHUB"]
      typical_cost: "$4-21/mo"
```

## Usage Detection Heuristics

```yaml
usage_indicators:
  active:
    - Login in last 30 days
    - API calls recorded
    - Files created/modified
    - Active sessions

  inactive:
    - No login > 60 days
    - No API activity
    - No file activity
    - Storage not accessed

  potentially_unused:
    - No login > 30 days
    - Minimal activity
    - Below threshold usage
```

## Audit Report Template

```markdown
# Subscription Audit - <Date>

## Executive Summary
- **Total Monthly Spend:** $XXX.XX
- **Total Annual Spend:** $X,XXX.XX
- **Potential Savings:** $XXX.XX/month
- **Unused Services:** X

## All Subscriptions

### Entertainment
| Service | Monthly | Annual | Status | Recommendation |
|---------|---------|--------|--------|----------------|
| Netflix | $15.99 | $191.88 | Active | Keep |
| Spotify | $9.99 | $119.88 | Inactive | Review |

### Software
| Service | Monthly | Annual | Status | Recommendation |
|---------|---------|--------|--------|----------------|
| Adobe CC | $54.99 | $659.88 | Active | Keep |
| Notion | $8.00 | $96.00 | Active | Keep |

### Development
| Service | Monthly | Annual | Status | Recommendation |
|---------|---------|--------|--------|----------------|
| GitHub Pro | $4.00 | $48.00 | Active | Keep |
| Cursor | $20.00 | $240.00 | Active | Keep |

## Potential Cancellations

### High Priority (Unused)
1. **Spotify** - $9.99/mo - No usage in 60 days
   - Annual savings: $119.88
   - [ ] Create cancellation request

2. **[Service]** - $X/mo - [Reason]
   - Annual savings: $X

### Medium Priority (Underutilized)
1. **[Service]** - $X/mo - Minimal usage
   - Annual savings: $X
   - Recommendation: Downgrade to free tier

## Cost Optimization Suggestions

1. **Bundle Opportunities**
   - Consider [bundle] instead of separate services
   - Potential savings: $X/mo

2. **Annual vs Monthly**
   - Switch to annual billing: [services]
   - Potential savings: $X/mo

3. **Tier Downgrades**
   - [Service]: Current tier underutilized
   - Recommend downgrade to [lower tier]

## Comparison to Last Audit
| Metric | This Month | Last Month | Change |
|--------|------------|------------|--------|
| Total Spend | $XXX | $YYY | +/- $Z |
| Services | X | Y | +/- Z |
| Unused | X | Y | +/- Z |

## Actions Required

### Cancellation Approvals Needed
- [ ] Spotify - $9.99/mo - Create request
- [ ] [Service] - $X/mo - Create request

### Review Needed
- [ ] [Service] - Check if still needed
- [ ] [Service] - Consider downgrade

---
*Generated by Personal AI Employee*
*Next audit: <next month>*
```

## Error Handling

| Error | Recovery Action |
|-------|-----------------|
| No transaction logs found | Report "No transaction data available" |
| Cannot determine cost | Estimate from known service prices, flag |
| Service not recognized | Add to "Unknown" category for review |
| Cannot write to Accounting/ | Create directory, retry |

## Security Considerations

### Never Do
- Share financial data outside vault
- Auto-cancel without approval
- Store payment credentials

### Always Do
- Create approval requests for cancellations
- Preserve audit history
- Redact sensitive account details

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Audit Report | `Accounting/SUBSCRIPTION_AUDIT_YYYYMMDD.md` | Full audit |
| Cancellation Requests | `Pending_Approval/SUB_CANCEL_*.md` | Cancellation approvals |
| Metrics | `Logs/metrics/subscriptions_YYYYMMDD.json` | Historical data |

## Definition of Done

- [ ] All transaction logs scanned
- [ ] Recurring charges identified
- [ ] Subscriptions categorized
- [ ] Costs calculated (monthly/annual)
- [ ] Unused services identified
- [ ] Cancellation requests created
- [ ] Audit report written
- [ ] Dashboard updated

## Example Usage

```
User: /audit-subscriptions

Claude: Running subscription audit...

Scanning transaction logs...
- Found 156 transactions in last 90 days

Identifying recurring charges...
- Found 12 recurring subscriptions

Categorizing...
- Entertainment: 3 services ($35.97/mo)
- Software: 4 services ($95.98/mo)
- Development: 3 services ($28.00/mo)
- AI: 2 services ($40.00/mo)

Analyzing usage...
- Active: 9 services
- Inactive: 3 services (no usage > 30 days)

Total Monthly: $199.95
Total Annual: $2,399.40
Potential Savings: $29.97/mo ($359.64/yr)

Created:
- Accounting/SUBSCRIPTION_AUDIT_20260301.md
- Pending_Approval/SUB_CANCEL_spotify.md

Summary:
📊 12 subscriptions found
💰 $199.95/month total
⚠️ 3 potentially unused
💡 $359.64 annual savings potential
```

## References

| File | Purpose |
|------|---------|
| `references/service-database.md` | Known service pricing |
| `references/usage-metrics.md` | Usage detection rules |
| `references/cancellation-procedures.md` | How to cancel services |

---
*Version: 1.0.0 | Last Updated: 2026-03-01*