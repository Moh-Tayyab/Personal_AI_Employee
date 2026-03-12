---
name: fix-ticket
description: Autonomous bug fixer - reads bug reports, reproduces with Playwright, plans fixes, implements with code review, verifies, commits, and deploys. Full end-to-end automation from bug report to production.
allowed-tools: Bash(playwright-cli:*), Bash(git:*), Bash(npm:*), Bash(npx:*), Bash(vercel:*), Glob, Grep, Read, Write, Edit, NotebookEdit, NotebookRead, Agent
---

# 🎫 Fix Ticket - Autonomous Bug Fixing Agent

## Overview

This skill transforms Claude Code into an autonomous software engineer that can:
1. Read bug reports from `/vault/Needs_Action/bugs/`
2. Reproduce bugs using Playwright CLI
3. Research and plan fixes
4. Implement fixes with multi-agent code review
5. Verify fixes in browser
6. Commit and deploy to Vercel
7. Move ticket to `/vault/Done/`

## Quick Start

```bash
# Place bug report in Needs_Action
# Then run:
claude --prompt "Process bug reports in /vault/Needs_Action/bugs/"
```

## Bug Report Format

Create bug reports in `/vault/Needs_Action/bugs/BUG-YYYY-MM-DD.md`:

```markdown
---
type: bug_report
priority: P1
url: https://your-app.com/page
created: 2026-03-12T10:00:00Z
status: new
---

## Bug Description
Button click doesn't work on homepage

## Steps to Reproduce
1. Go to https://your-app.com
2. Click "Get Started" button
3. Nothing happens

## Expected Behavior
Should navigate to /get-started page

## Actual Behavior
No action, console shows: "Uncaught TypeError: Cannot read property..."

## Environment
- Browser: Chrome 122
- OS: Windows 11
- Screen: 1920x1080

## Attachments
- Screenshot: /vault/Attachments/bug-screenshot.png
```

## Execution Flow

### Phase 1: Triage
```bash
# 1. Read bug report
# 2. Classify priority:
#    P0 - Critical (system down, data loss)
#    P1 - High (feature broken, user blocked)
#    P2 - Normal (minor bug, workaround exists)
#    P3 - Low (cosmetic, nice-to-have)
# 3. Check if reproducible
# 4. Create Plan.md
```

### Phase 2: Reproduction
```bash
# Use Playwright CLI to reproduce:
playwright-cli open <url>
playwright-cli snapshot
playwright-cli click <button-ref>
playwright-cli screenshot
playwright-cli console
```

### Phase 3: Research & Plan
```bash
# 1. Search codebase for related code
# 2. Identify root cause
# 3. Create detailed fix plan
# 4. Request approval for P0/P1 bugs
```

### Phase 4: Implementation
```bash
# 1. Create feature branch
# 2. Implement fix
# 3. Run tests
# 4. Create code review request
```

### Phase 5: Code Review (Multi-Agent)
```bash
# Agent 1: Security Review
# - Check for vulnerabilities
# - Validate input sanitization

# Agent 2: Code Quality Review
# - Style guide compliance
# - Best practices

# Agent 3: Functional Review
# - Edge cases covered
# - Tests included
```

### Phase 6: Verification
```bash
# 1. Open fixed page in browser
# 2. Run same reproduction steps
# 3. Verify bug is fixed
# 4. Take screenshot for evidence
```

### Phase 7: Deploy
```bash
# 1. Commit changes
# 2. Push to main
# 3. Deploy to Vercel
# 4. Verify production
```

## Commands

### Start Bug Fix Flow
```bash
/fix-ticket process-all
```

### Reproduce Specific Bug
```bash
/fix-ticket reproduce /vault/Needs_Action/bugs/BUG-001.md
```

### Generate Fix Plan
```bash
/fix-ticket plan /vault/Needs_Action/bugs/BUG-001.md
```

### Execute Fix
```bash
/fix-ticket execute /vault/Plans/PLAN-BUG-001.md
```

### Verify Fix
```bash
/fix-ticket verify /vault/Plans/PLAN-BUG-001.md
```

### Deploy
```bash
/fix-ticket deploy /vault/Plans/PLAN-BUG-001.md
```

## Configuration

### Priority Rules
```yaml
P0:
  response_time: immediate
  auto_approve: false
  keywords: [down, crash, data-loss, security, breach]
  
P1:
  response_time: <4 hours
  auto_approve: false
  keywords: [broken, blocked, cannot, urgent]
  
P2:
  response_time: <24 hours
  auto_approve: true
  default: true
  
P3:
  response_time: <1 week
  auto_approve: true
  keywords: [cosmetic, minor, nice-to-have]
```

### Approval Thresholds
| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| P2/P3 fixes | ✅ Yes | ❌ No |
| P0/P1 fixes | ❌ No | ✅ Yes |
| Database changes | ❌ No | ✅ Always |
| API changes | ❌ No | ✅ Always |
| Security fixes | ✅ Yes* | ⚠️ Log only |

*Security fixes auto-approved but must be logged

## Playwright Commands Reference

### Navigation
```bash
playwright-cli open <url>
playwright-cli goto <url>
playwright-cli go-back
playwright-cli reload
```

### Interaction
```bash
playwright-cli click <ref>
playwright-cli type <text>
playwright-cli fill <ref> <text>
playwright-cli press <key>
playwright-cli hover <ref>
```

### Debugging
```bash
playwright-cli snapshot
playwright-cli screenshot [ref]
playwright-cli console
playwright-cli network
```

### Example: Bug Reproduction Script
```bash
# Open the page
playwright-cli open https://your-app.com

# Take snapshot to get element refs
playwright-cli snapshot

# Try to click the button
playwright-cli click e15

# Check if navigation occurred
playwright-cli snapshot

# Check console for errors
playwright-cli console

# Take screenshot for report
playwright-cli screenshot bug-repro.png
```

## File Templates

### Plan Template
```markdown
---
type: fix_plan
bug_id: BUG-001
priority: P1
status: in_progress
created: 2026-03-12T10:00:00Z
---

## Bug Summary
Button click doesn't work on homepage

## Root Cause
Event handler not attached due to null reference

## Fix Strategy
1. Add null check before attaching event listener
2. Add error logging for debugging
3. Add test case for edge condition

## Files to Change
- src/components/Homepage.tsx
- src/components/__tests__/Homepage.test.tsx

## Steps
- [ ] Create branch: fix/BUG-001
- [ ] Implement fix
- [ ] Run tests
- [ ] Code review
- [ ] Verify in browser
- [ ] Deploy to production

## Approval
Move to /Approved/ to proceed with fix.
```

### Code Review Template
```markdown
---
type: code_review
plan_id: PLAN-BUG-001
reviewer: security-agent
status: pending
---

## Security Review

### Checklist
- [ ] No SQL injection vulnerabilities
- [ ] Input validation present
- [ ] No hardcoded secrets
- [ ] XSS prevention in place

### Findings
None

### Approval
✅ Approved
```

## Error Handling

### Retry Logic
```python
# If Playwright fails to connect:
# 1. Wait 5 seconds
# 2. Retry up to 3 times
# 3. If still failing, create error report
```

### Escalation
```markdown
---
type: escalation
bug_id: BUG-001
reason: Could not reproduce bug
---

## Issue
Unable to reproduce bug after 3 attempts

## Attempts
1. Chrome - Failed to load page
2. Firefox - Page loads but button works
3. Safari - Same as Firefox

## Recommendation
Bug may be environment-specific.
Request more details from reporter.
```

## Logging Format

```json
{
  "timestamp": "2026-03-12T10:30:00Z",
  "action": "bug_fix",
  "bug_id": "BUG-001",
  "phase": "reproduction",
  "status": "success",
  "details": {
    "url": "https://your-app.com",
    "browser": "chromium",
    "result": "Bug reproduced - TypeError on button click"
  }
}
```

## Integration with Personal AI Employee

### Folder Structure
```
/vault/
├── Needs_Action/
│   └── bugs/
│       └── BUG-001.md
├── Plans/
│   └── PLAN-BUG-001.md
├── In_Progress/
│   └── fix-ticket/
│       └── BUG-001/
├── Pending_Approval/
│   └── FIX-APPROVAL-001.md
├── Approved/
├── Done/
│   └── BUG-001-fixed.md
└── Logs/
    └── fix-ticket/
        └── 2026-03-12.json
```

### Dashboard Updates
After each phase, update `/vault/Dashboard.md`:

```markdown
## Active Bug Fixes
| Bug ID | Priority | Phase | Status |
|--------|----------|-------|--------|
| BUG-001 | P1 | Verification | 🟡 In Progress |

## Completed Today
| Bug ID | Fixed At | Deployed |
|--------|----------|----------|
| BUG-000 | 10:00 AM | ✅ Yes |
```

## Success Criteria

- [ ] Bug reproduced and documented
- [ ] Root cause identified
- [ ] Fix implemented and tested
- [ ] Code review completed
- [ ] Fix verified in browser
- [ ] Deployed to production
- [ ] Bug report updated with resolution
- [ ] All logs written

## Metrics to Track

| Metric | Target | Current |
|--------|--------|---------|
| Avg fix time (P0) | <1 hour | - |
| Avg fix time (P1) | <4 hours | - |
| Avg fix time (P2) | <24 hours | - |
| First-time fix rate | >90% | - |
| Regression rate | <5% | - |

---

*Skill Version: 1.0*
*Last Updated: 2026-03-12*
