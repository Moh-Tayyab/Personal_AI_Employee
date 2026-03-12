# Agent Teams Quick Start Guide

## Overview

Agent teams allow multiple Claude Code instances to work together as a coordinated team, dramatically increasing your Personal AI Employee's capability to handle complex, multi-domain tasks efficiently.

## Prerequisites

1. **Claude Code installed** with agent teams enabled
2. **Personal AI Employee project** set up and running
3. **MCP servers configured** (email, social media, accounting)

## Quick Setup (5 minutes)

### 1. Verify Agent Teams are Enabled

Check your `.claude/settings.json`:
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### 2. Test the Setup

```bash
# Check if agent teams are properly configured
./scripts/manage_teams.sh check

# Should output: "Agent teams configuration is valid"
```

### 3. Run a Demo

```bash
# Create sample work items and see team suggestions
python scripts/demo_agent_teams.py --scenario business-ops --interactive

# Or run non-interactively
python scripts/demo_agent_teams.py --scenario business-ops
```

## Your First Agent Team

### Scenario: Morning Business Operations

1. **Start Claude Code**:
   ```bash
   claude --vault ./vault
   ```

2. **Create sample work** (or use real items in `vault/Needs_Action/`):
   ```bash
   python scripts/demo_agent_teams.py --scenario business-ops
   ```

3. **Create the team** in Claude Code:
   ```
   Create a business operations team with 4 specialists:
   - Email specialist: Handle email processing and customer communications using email MCP server
   - Social media manager: Create and schedule posts, manage engagement using social MCP servers
   - Accounting specialist: Process invoices and expenses using Odoo MCP server
   - Research analyst: Gather market intelligence and competitive analysis

   Each teammate should work independently while coordinating through shared tasks.
   ```

4. **Monitor the team**:
   ```bash
   # List active teams
   ./scripts/manage_teams.sh list

   # Check team tasks
   ./scripts/manage_teams.sh tasks business-operations

   # View team logs
   cat vault/Teams/Logs/business-operations_*.md
   ```

## Team Templates

### Business Operations Team
```
Create a business operations team with 4 specialists:
- Email specialist: Handle email processing, responses, and follow-ups using email MCP server
- Social media manager: Manage LinkedIn, Twitter, Instagram posts and engagement using social MCP servers
- Accounting specialist: Process invoices, track expenses, update Odoo using accounting MCP server
- Research analyst: Gather market intelligence and competitive analysis

Each teammate should work independently while coordinating through shared tasks.
```

### Development Team
```
Spawn a development team with 3 teammates:
- Backend developer: Focus on MCP servers, orchestrator, and API integrations
- Frontend developer: Handle vault UI, dashboards, and user interfaces
- DevOps engineer: Manage deployment, monitoring, and system health

Require plan approval for any production changes.
```

### Content Creation Team
```
Create a content team with 4 specialists:
- Content writer: Create blog posts, documentation, and marketing materials
- Social media strategist: Plan campaigns and engagement strategies
- Customer support: Handle inquiries, complaints, and support tickets
- Brand manager: Ensure consistent messaging and brand voice

All content must be approved by brand manager before publication.
```

## Team Communication

### Direct Messages
```
@email-specialist: Please prioritize the partnership inquiry from TechCorp
@social-media: Create a LinkedIn post about our new agent teams feature
@accounting: Update Q1 revenue projections based on recent contracts
```

### Broadcast Messages (use sparingly)
```
Team update: Client meeting moved to 3 PM - all deliverables need ready by 2:30 PM
```

## Monitoring and Management

### Check Team Status
```bash
# List all active teams
./scripts/manage_teams.sh list

# Show tasks for specific team
./scripts/manage_teams.sh tasks team-name

# Clean up completed teams
./scripts/manage_teams.sh cleanup
```

### Team Health Monitoring
- Teams are monitored every 5 minutes by the orchestrator
- Quality checks run when teammates go idle
- Status reports saved to `vault/Teams/team_status_report.md`

## Best Practices

### When to Use Agent Teams
- ✅ **Multiple domains**: Email + social + accounting tasks
- ✅ **Parallel work**: 5+ independent tasks
- ✅ **Research projects**: Need diverse perspectives
- ✅ **Complex workflows**: Multi-step processes with handoffs

### When NOT to Use Agent Teams
- ❌ **Single domain**: Only email or only social media
- ❌ **Sequential tasks**: Each step depends on the previous
- ❌ **Simple tasks**: Can be completed in <15 minutes
- ❌ **File conflicts**: Multiple teammates editing same files

### Team Size Guidelines
- **2-3 teammates**: Small tasks (<2 hours)
- **3-5 teammates**: Medium projects (2-8 hours)
- **4-6 teammates**: Large initiatives (1+ days)

## Troubleshooting

### Teams Not Appearing
```bash
# Check if agent teams are enabled
grep -r "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" .claude/settings.json

# Verify task complexity warrants a team
# Teams are only created for sufficiently complex work
```

### Permission Issues
```bash
# Pre-approve common operations in .claude/settings.json
{
  "permissions": {
    "allow": ["mcp__*", "Read", "Write", "Edit"]
  }
}
```

### Team Coordination Issues
```bash
# Check team logs
cat vault/Teams/Logs/team-name_*.md

# Monitor task status
./scripts/manage_teams.sh tasks team-name

# Clean up if needed
./scripts/manage_teams.sh cleanup
```

## Advanced Usage

### Custom Team Hooks
Add quality gates in `.claude/settings.json`:
```json
{
  "hooks": {
    "TeammateIdle": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python scripts/team_quality_check.py --teammate-id $TEAMMATE_ID --team-name $TEAM_NAME --last-action $LAST_ACTION"
          }
        ]
      }
    ]
  }
}
```

### Integration with Orchestrator
The orchestrator automatically:
- Detects when agent teams should be used
- Creates teams for batch processing
- Monitors team health every 5 minutes
- Cleans up completed teams

## Next Steps

1. **Try the demo scenarios**: business-ops, development, content
2. **Create your own team templates** in `templates/agent_teams/`
3. **Set up quality hooks** for your specific workflows
4. **Monitor team performance** and optimize team composition

## Support

- **Documentation**: `docs/AGENT_TEAMS_GUIDE.md`
- **Workflows**: `docs/AGENT_TEAMS_WORKFLOWS.md`
- **Templates**: `templates/agent_teams/`
- **Scripts**: `scripts/manage_teams.sh`, `scripts/demo_agent_teams.py`

---

**🎯 Goal**: Transform your Personal AI Employee from a single agent into a coordinated workforce capable of handling complex, multi-domain business operations efficiently and reliably.