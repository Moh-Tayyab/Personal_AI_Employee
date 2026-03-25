---
spec_id: SPEC-001
title: Email Notification System
status: approved
created: 2026-03-18
last_updated: 2026-03-18
phase: tasks_approved
---

# Email Notification System - Implementation Tasks

## Implementation Phases

### Phase 1: Foundation (Days 1-3)
Core email watching infrastructure

### Phase 2: Classification (Days 4-6)
Email categorization and rules engine

### Phase 3: Notifications (Days 7-9)
WhatsApp and Dashboard integration

### Phase 4: Polish (Days 10-12)
Testing, documentation, and optimization

## Task List

---

### TSK-001: Gmail MCP Configuration
**Title**: Set up Gmail MCP server integration
**Description**: 
- Create Gmail MCP configuration file
- Document OAuth setup process
- Test Gmail API connectivity
- Implement token refresh logic

**Acceptance Criteria**:
- [ ] `mcp_servers/gmail-mcp.json` created with proper config
- [ ] OAuth credentials working
- [ ] Can fetch unread emails via MCP
- [ ] Token refresh tested and working

**Estimated Effort**: M
**Dependencies**: None
**Status**: Pending
**Assigned To**: Integration Agent

---

### TSK-002: Email Watcher Core
**Title**: Implement EmailWatcher class
**Description**:
- Create `watchers/email_watcher.py`
- Implement `EmailWatcher` class with poll functionality
- Track processed message IDs
- Handle pagination for large inboxes

**Acceptance Criteria**:
- [ ] EmailWatcher class implemented
- [ ] Polls Gmail every 5 minutes
- [ ] Tracks processed emails in `.state/processed_emails.json`
- [ ] Unit tests with >80% coverage

**Estimated Effort**: M
**Dependencies**: TSK-001
**Status**: Pending
**Assigned To**: Backend Agent

---

### TSK-003: Email Data Model
**Title**: Define Email data structures
**Description**:
- Create `models/email.py`
- Define `Email` class with all metadata fields
- Define `Attachment` class
- Implement serialization/deserialization

**Acceptance Criteria**:
- [ ] Email class with all required fields
- [ ] Type hints for all attributes
- [ ] JSON serialization working
- [ ] Docstrings complete

**Estimated Effort**: S
**Dependencies**: None
**Status**: Pending
**Assigned To**: Backend Agent

---

### TSK-004: Email Classifier
**Title**: Implement email categorization engine
**Description**:
- Create `watchers/email_classifier.py`
- Implement rule-based categorization
- Support keyword matching
- Support sender priority lists

**Acceptance Criteria**:
- [ ] Classifier categorizes emails correctly
- [ ] Configurable rules via YAML
- [ ] VIP sender detection working
- [ ] Invoice keyword detection working

**Estimated Effort**: M
**Dependencies**: TSK-003
**Status**: Pending
**Assigned To**: Backend Agent

---

### TSK-005: Configuration System
**Title**: Build configuration management
**Description**:
- Create `config/email_watcher.yaml` template
- Implement config loader with validation
- Support hot-reload of configuration
- Create `.env.example` for secrets

**Acceptance Criteria**:
- [ ] YAML config file with all options
- [ ] Config validation on load
- [ ] Hot-reload without restart
- [ ] `.env.example` documented

**Estimated Effort**: S
**Dependencies**: None
**Status**: Pending
**Assigned To**: Backend Agent

---

### TSK-006: WhatsApp Notification Handler
**Title**: Integrate WhatsApp MCP for notifications
**Description**:
- Create `handlers/whatsapp_handler.py`
- Format urgent email notifications
- Send via WhatsApp MCP
- Handle delivery failures

**Acceptance Criteria**:
- [ ] WhatsApp notifications sent for urgent emails
- [ ] Message formatting includes sender, subject, time
- [ ] Error handling for unavailable WhatsApp
- [ ] Delivery confirmation logged

**Estimated Effort**: M
**Dependencies**: TSK-002
**Status**: Pending
**Assigned To**: Integration Agent

---

### TSK-007: Dashboard Update Handler
**Title**: Implement Dashboard.md updates
**Description**:
- Create `handlers/dashboard_handler.py`
- Update Dashboard.md with new emails
- Maintain email status table
- Handle concurrent writes safely

**Acceptance Criteria**:
- [ ] Dashboard.md updated with important emails
- [ ] Email table shows status, sender, subject, time
- [ ] File locking prevents corruption
- [ ] Rollback on write failure

**Estimated Effort**: M
**Dependencies**: TSK-002
**Status**: Pending
**Assigned To**: Backend Agent

---

### TSK-008: Action File Creator
**Title**: Create vault action files for invoices
**Description**:
- Create `handlers/action_file_handler.py`
- Generate markdown files in `vault/Needs_Action/`
- Include email metadata in frontmatter
- Link back to original email

**Acceptance Criteria**:
- [ ] Action files created for invoice emails
- [ ] Proper YAML frontmatter
- [ ] File naming convention followed
- [ ] Email content excerpt included

**Estimated Effort**: S
**Dependencies**: TSK-004
**Status**: Pending
**Assigned To**: Backend Agent

---

### TSK-009: Activity Logger
**Title**: Implement email activity logging
**Description**:
- Create `utils/email_logger.py`
- Log all email activities to `vault/Logs/email-activity.md`
- Include timestamps and actions taken
- Daily log rotation

**Acceptance Criteria**:
- [ ] All activities logged with timestamps
- [ ] Log includes: detected, categorized, notified
- [ ] Daily rotation at midnight
- [ ] Logs searchable by date

**Estimated Effort**: S
**Dependencies**: None
**Status**: Pending
**Assigned To**: Backend Agent

---

### TSK-010: Daily Summary Generator
**Title**: Build daily email summary feature
**Description**:
- Create `handlers/daily_summary_handler.py`
- Generate summary at 8 PM daily
- Include category counts
- List top 5 important emails

**Acceptance Criteria**:
- [ ] Summary generated at configured time
- [ ] Saved to `vault/Briefings/email-summary-{date}.md`
- [ ] Includes counts by category
- [ ] Lists important emails with subjects

**Estimated Effort**: M
**Dependencies**: TSK-002, TSK-009
**Status**: Pending
**Assigned To**: Backend Agent

---

### TSK-011: Error Recovery System
**Title**: Implement retry and recovery logic
**Description**:
- Add exponential backoff for API failures
- Implement circuit breaker pattern
- Create recovery procedures
- Alert user after max retries

**Acceptance Criteria**:
- [ ] Exponential backoff (120s, 240s, 480s)
- [ ] Max 3 retries before alert
- [ ] Circuit breaker prevents cascade failures
- [ ] User alerted via dashboard on persistent failure

**Estimated Effort**: M
**Dependencies**: TSK-002
**Status**: Pending
**Assigned To**: Backend Agent

---

### TSK-012: Unit Tests
**Title**: Write comprehensive unit tests
**Description**:
- Test EmailWatcher class
- Test EmailClassifier rules
- Test notification handlers
- Test configuration loader

**Acceptance Criteria**:
- [ ] All core classes have unit tests
- [ ] Code coverage >80%
- [ ] Tests run in CI pipeline
- [ ] Mock external dependencies

**Estimated Effort**: L
**Dependencies**: TSK-002, TSK-004, TSK-006
**Status**: Pending
**Assigned To**: Test Agent

---

### TSK-013: Integration Tests
**Title**: Write integration test suite
**Description**:
- Test Gmail → Watcher → Classifier flow
- Test notification delivery
- Test Dashboard updates
- Test action file creation

**Acceptance Criteria**:
- [ ] End-to-end flow tested
- [ ] Test with real Gmail account (test account)
- [ ] Verify WhatsApp notifications
- [ ] Verify file system changes

**Estimated Effort**: L
**Dependencies**: TSK-002, TSK-006, TSK-007
**Status**: Pending
**Assigned To**: Test Agent

---

### TSK-014: Documentation
**Title**: Write user and developer documentation
**Description**:
- Create `docs/email-watcher/README.md`
- Document setup process
- Document configuration options
- Add troubleshooting guide

**Acceptance Criteria**:
- [ ] Setup guide complete
- [ ] Configuration options documented
- [ ] Troubleshooting common issues
- [ ] API reference for developers

**Estimated Effort**: M
**Dependencies**: All implementation tasks
**Status**: Pending
**Assigned To**: Documentation Agent

---

### TSK-015: Performance Optimization
**Title**: Optimize watcher performance
**Description**:
- Profile email fetching
- Optimize classification rules
- Reduce API calls with caching
- Tune poll intervals

**Acceptance Criteria**:
- [ ] Email detection < 60 seconds
- [ ] Notification delivery < 30 seconds
- [ ] API calls minimized with caching
- [ ] Memory usage < 100MB

**Estimated Effort**: S
**Dependencies**: All implementation tasks
**Status**: Pending
**Assigned To**: Backend Agent

---

## Critical Path

```
TSK-001 → TSK-002 → TSK-004 → TSK-006 → TSK-012 → TSK-013
              ↓         ↓
            TSK-007   TSK-008
              ↓         ↓
            TSK-010   TSK-009
```

**Critical Path Tasks**: TSK-001, TSK-002, TSK-004, TSK-006, TSK-012, TSK-013

## Risk Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Gmail API rate limits | High | Low | Implement caching, respect quotas |
| WhatsApp unavailable | Medium | Medium | Fallback to dashboard only |
| OAuth token expiration | High | Medium | Auto-refresh, alert on failure |
| False positive classifications | Medium | High | User feedback loop, tune rules |

## Task Status Summary

| Status | Count |
|--------|-------|
| Pending | 15 |
| In Progress | 0 |
| Done | 0 |

---

**Status**: ✅ Tasks Approved
**Next Phase**: Implementation
**Approved By**: Judge Agent
**Approval Date**: 2026-03-18
