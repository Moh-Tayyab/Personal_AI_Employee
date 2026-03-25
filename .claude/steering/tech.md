# Technical Steering

## Technology Stack

### Core Components
| Component | Technology | Version |
|-----------|------------|---------|
| Reasoning Engine | Claude Code | Latest |
| Knowledge Base | Obsidian | Markdown |
| Watchers | Python | 3.13+ |
| Automation | MCP Servers | Latest |
| Process Manager | PM2 | Latest |

### Architecture Patterns

#### Watcher Pattern
```python
# Watchers monitor external sources and wake the agent
class Watcher:
    - Poll external sources (email, files, APIs)
    - Detect changes/events
    - Create action files in Needs_Action/
    - Log all observations
```

#### Ralph Wiggum Loop
- Persistent agent that keeps working until tasks complete
- Checks vault for new items regularly
- Processes items through approval workflow
- Logs all actions for audit

#### Claim-by-Move
- First agent to move item from Needs_Action to In_Progress owns it
- Prevents duplicate processing
- File-based distributed coordination

#### Single-Writer
- Only Local agent writes to Dashboard.md
- Prevents race conditions
- Clear ownership of shared state

## Coding Standards

### Python (Watchers)
- Type hints required for all functions
- Docstrings for public APIs
- Error handling with logging
- Configuration via environment variables
- Secrets never committed

### Markdown (Vault)
- YAML frontmatter for metadata
- Consistent heading hierarchy
- Links use relative paths
- Tags for categorization

### Shell Scripts
- Use `set -euo pipefail`
- Quote all variables
- Provide clear error messages
- Log all operations

## Security Guidelines

### Secrets Management
- Use environment variables
- `.env` files excluded from git
- Never log sensitive data
- Rotate credentials regularly

### Human-in-the-Loop
- All external actions require approval
- Approval via file movement
- Rejected items logged with reason
- Audit trail for all actions

### Data Privacy
- Local-first storage
- Cloud sync excludes secrets
- User controls all data
- Transparent data flows

## Testing Strategy

### Unit Tests
- Test watcher detection logic
- Validate file operations
- Test parsing functions

### Integration Tests
- Test watcher → vault flow
- Test approval workflow
- Test MCP integrations

### E2E Tests
- Full task completion flow
- Error recovery scenarios
- Multi-agent coordination

## Observability

### Logging
- Structured JSON logs
- Log levels: DEBUG, INFO, WARN, ERROR
- Include correlation IDs
- Rotate logs daily

### Monitoring
- Dashboard shows agent status
- Track task completion rates
- Alert on repeated failures
- Health check endpoints

## Error Handling

### Retry Strategy
- Exponential backoff
- Max 3 retries
- Log all failures
- Escalate to user after retries

### Recovery Patterns
- Idempotent operations
- Checkpoint state periodically
- Resume from last checkpoint
- Manual intervention fallback
