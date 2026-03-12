# Agent Teams Guide - Personal AI Employee

This guide explains how to use agent teams in your Personal AI Employee system for coordinated multi-agent workflows.

## Overview

Agent teams allow multiple Claude Code instances to work together as a coordinated team, perfect for your multi-domain AI employee system. Each teammate specializes in different areas while sharing a common task list and communication system.

## Team Configurations

### 1. Business Operations Team

**Use Case**: Handle daily business operations across multiple domains
```
Create an agent team for business operations with 4 teammates:
- Email specialist: Handle email processing, responses, and follow-ups
- Social media manager: Manage LinkedIn, Twitter, Instagram posts and engagement
- Accounting specialist: Process invoices, track expenses, update Odoo
- Research analyst: Gather market intelligence and competitive analysis
```

### 2. Development & Maintenance Team

**Use Case**: Software development, bug fixes, and system maintenance
```
Spawn a development team with 3 teammates:
- Backend developer: Focus on MCP servers, orchestrator, and API integrations
- Frontend developer: Handle vault UI, dashboards, and user interfaces
- DevOps engineer: Manage deployment, monitoring, and system health
```

### 3. Content & Communication Team

**Use Case**: Content creation, communication, and customer engagement
```
Create a content team with 4 specialists:
- Content writer: Create blog posts, documentation, and marketing materials
- Social media strategist: Plan campaigns and engagement strategies
- Customer support: Handle inquiries, complaints, and support tickets
- Brand manager: Ensure consistent messaging and brand voice
```

### 4. Analysis & Intelligence Team

**Use Case**: Data analysis, reporting, and strategic insights
```
Form an intelligence team with 3 analysts:
- Data analyst: Process metrics, generate reports, identify trends
- Market researcher: Analyze competitors, market conditions, opportunities
- Business strategist: Provide recommendations and strategic planning
```

## Team Coordination Patterns

### Parallel Processing Pattern
```
I need to process 50 emails, update social media, and generate invoices.
Create a team where each teammate handles one domain simultaneously.
```

### Research & Debate Pattern
```
We're considering a new AI integration. Spawn 3 teammates to research different
approaches and debate the pros/cons: OpenAI GPT-4, Anthropic Claude, and local LLMs.
Have them challenge each other's findings.
```

### Review & Quality Assurance Pattern
```
Create a review team for the new MCP server code:
- Security reviewer: Check for vulnerabilities and security issues
- Performance reviewer: Analyze efficiency and optimization opportunities
- Code quality reviewer: Ensure best practices and maintainability
```

## Specialized Team Skills

### Email Processing Team
- One teammate for urgent emails (< 2 hours response time)
- One teammate for routine emails (newsletters, notifications)
- One teammate for business emails (partnerships, sales)
- One teammate for technical emails (support, bug reports)

### Social Media Team
- LinkedIn specialist: Professional content, networking, B2B engagement
- Twitter specialist: Quick updates, industry news, thought leadership
- Instagram specialist: Visual content, behind-the-scenes, company culture
- Content coordinator: Ensure consistent messaging across platforms

### Financial Team
- Invoice processor: Handle incoming invoices, payment tracking
- Expense tracker: Categorize and record business expenses
- Revenue analyst: Track income, identify trends, forecast
- Compliance checker: Ensure tax compliance, regulatory requirements

## Team Communication Examples

### Direct Teammate Messaging
```
@email-specialist: Please prioritize the partnership inquiry from InnovateAI
@social-media: Create a LinkedIn post about our new MCP integration
@accounting: Update the Q1 revenue projections based on recent contracts
```

### Broadcast Messages
```
Team update: We've received a high-priority client request. All teammates should
prioritize tasks related to the TechCorp project for the next 2 hours.
```

### Task Dependencies
```
Task 1: Research competitor pricing (assigned to market-researcher)
Task 2: Draft pricing proposal (depends on Task 1, assigned to business-strategist)
Task 3: Create presentation slides (depends on Task 2, assigned to content-writer)
```

## Quality Gates & Hooks

### Approval Workflows
```
Spawn a social media teammate with plan approval required.
Only approve posts that:
- Align with brand voice guidelines
- Include relevant hashtags
- Have proper grammar and spelling
- Don't contain sensitive information
```

### Quality Checks
```
TeammateIdle hook: Before going idle, teammates must:
- Update task status to completed
- Document any blockers or issues
- Hand off work to appropriate teammate if needed
```

## Best Practices

### Team Size Guidelines
- **Small tasks (< 2 hours)**: 2-3 teammates
- **Medium projects (2-8 hours)**: 3-5 teammates
- **Large initiatives (1+ days)**: 4-6 teammates
- **Research projects**: 3-4 teammates for diverse perspectives

### Task Sizing
- **Ideal task size**: 30-60 minutes of focused work
- **Too small**: < 15 minutes (coordination overhead exceeds benefit)
- **Too large**: > 2 hours (risk of wasted effort, lack of check-ins)

### Communication Patterns
- Use direct messages for specific instructions
- Use broadcasts sparingly (costs scale with team size)
- Encourage teammates to challenge each other's assumptions
- Regular status updates prevent duplicate work

### Domain Separation
- Assign clear ownership boundaries (email vs social vs accounting)
- Avoid file conflicts by having teammates work on different files
- Use shared resources (vault, task list) for coordination
- Establish handoff protocols between domains

## Troubleshooting

### Common Issues
1. **Teammates not appearing**: Check that task complexity warrants a team
2. **Permission prompts**: Pre-approve common operations in settings
3. **Task conflicts**: Ensure clear task ownership and dependencies
4. **Communication gaps**: Use explicit handoff messages between teammates

### Recovery Strategies
- If teammate stops: Spawn replacement and reassign tasks
- If lead shuts down early: Tell it to wait for teammates to finish
- If tasks get stuck: Manually update task status or reassign
- If coordination fails: Clean up team and restart with clearer instructions

## Integration with Personal AI Employee

### Vault Integration
- All teammates read from the same Obsidian vault
- Shared access to Company_Handbook.md for rules and guidelines
- Common task list in vault/Tasks/ directory
- Coordinated updates to Dashboard.md

### MCP Server Coordination
- Email teammate uses email MCP server exclusively
- Social media teammates share social MCP servers
- Accounting teammate has dedicated access to Odoo MCP
- No conflicts through clear domain boundaries

### Approval Workflows
- High-risk actions still require human approval
- Teammates can request approvals through vault/Pending_Approval/
- Lead coordinates approval requests and responses
- Audit trail maintained in vault/Logs/

This agent teams setup transforms your Personal AI Employee from a single agent into a coordinated workforce, dramatically increasing parallel processing capabilities while maintaining quality and oversight.