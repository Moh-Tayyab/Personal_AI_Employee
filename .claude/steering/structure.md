# Structure Steering

## Repository Layout

```
Personal_AI_Employee/
├── .claude/                    # Kiro configuration
│   ├── specs/                  # Feature specifications
│   ├── agents/kfc/             # Built-in workflow agents
│   ├── steering/               # AI guidance documents
│   └── settings/               # Extension settings
├── vault/                      # Obsidian vault (AI memory)
│   ├── Dashboard.md            # Real-time status
│   ├── Company_Handbook.md     # AI behavior rules
│   ├── Business_Goals.md       # Objectives and KPIs
│   ├── Needs_Action/           # Items requiring attention
│   ├── Plans/                  # Generated plan files
│   ├── Done/                   # Completed tasks
│   ├── Pending_Approval/       # Awaiting human approval
│   ├── Approved/               # Ready for execution
│   ├── Rejected/               # Rejected items
│   ├── Logs/                   # Activity audit logs
│   └── Briefings/              # CEO reports
├── watchers/                   # Python watcher scripts
│   ├── gmail_watcher.py
│   ├── whatsapp_watcher.py
│   └── file_watcher.py
├── orchestrators/              # Agent coordination scripts
│   ├── local_orchestrator.py
│   └── cloud_orchestrator.py
├── mcp_servers/                # MCP server configurations
├── scripts/                    # Utility scripts
├── docs/                       # Documentation
└── tests/                      # Test suite
```

## File Naming Conventions

### Watchers
- `{source}_watcher.py` - e.g., `gmail_watcher.py`
- Clear, descriptive names
- Lowercase with underscores

### Plans
- `Plan-{YYYY-MM-DD}-{description}.md`
- Stored in `vault/Plans/`
- Include creation date

### Logs
- `log-{YYYY-MM-DD}.md`
- Daily rotation
- Stored in `vault/Logs/`

### Action Files
- `{timestamp}-{source}-{type}.md`
- e.g., `20250318-143022-email-invoice.md`
- Include metadata in frontmatter

## Directory Ownership

| Directory | Primary Writer | Purpose |
|-----------|---------------|---------|
| `Needs_Action/` | Watchers | New items needing attention |
| `Plans/` | Claude Code | Generated action plans |
| `Pending_Approval/` | Claude Code | Awaiting human decision |
| `Approved/` | Human | Ready for execution |
| `Rejected/` | Human | Declined items |
| `Done/` | Orchestrator | Completed tasks |
| `Logs/` | All Agents | Activity records |

## Metadata Standards

### YAML Frontmatter
All action files must include:
```yaml
---
created: YYYY-MM-DD HH:MM:SS
source: gmail|whatsapp|file|manual
type: email|invoice|message|task
status: new|in_progress|pending_approval|approved|rejected|done
priority: high|medium|low
assigned_to: agent_name
---
```

### Tags
Use consistent tags for categorization:
- `#watcher/{source}` - Origin tracking
- `#status/{status}` - Current state
- `#priority/{level}` - Urgency
- `#agent/{name}` - Assigned agent

## Integration Points

### MCP Servers
- Configuration in `mcp_servers/`
- One config per integration
- Document required credentials

### External APIs
- Wrapper modules in `integrations/`
- Consistent error handling
- Rate limiting built-in

### Cloud Sync
- Git-based synchronization
- Exclude `.env` and secrets
- Conflict resolution strategy

## Version Control

### Git Strategy
- `main` - Stable releases
- `develop` - Integration branch
- Feature branches for new watchers
- PRs for all changes

### Commit Messages
- Conventional Commits format
- Reference issues and specs
- Clear, imperative mood

## Documentation

### README Files
Every directory should have a README.md explaining:
- Purpose of the directory
- File formats used
- Who writes/reads files
- Integration points

### Inline Documentation
- Code comments for complex logic
- Docstrings for all public functions
- Type hints throughout
