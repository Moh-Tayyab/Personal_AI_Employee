# Personal AI Employee - System Architecture & Code Overview

## Core Components

### 1. Orchestrator (orchestrator.py)
The orchestrator is the central nervous system of the Personal AI Employee. Key responsibilities:

- Monitors vault folders (Needs_Action, Pending_Approval, Approved)
- Processes items using AI (Claude via Multi-Provider system)
- Coordinates with MCP servers for external actions
- Manages approval workflows with Slack/Discord notifications
- Implements Ralph Wiggum persistence loops for task completion

Key functions:
- `trigger_ai()`: Processes items with Claude API
- `run_ralph_loop()`: Persistent task completion
- `notify_approval_needed()`: Webhook notifications for approvals
- `run()`: Main orchestration loop

### 2. Multi-Provider AI System (scripts/multi_provider_ai.py)
Provides intelligent routing across different AI providers while maintaining Claude Code functionality:

- Supports Gemini, OpenRouter, OpenAI (with Anthropic Claude as primary)
- Maintains tool access (bash, read, write, edit, glob, grep, web_search, etc.)
- Supports MCP servers and skills
- Implements provider quotas and fallback mechanisms
- Preserves Claude Code functionality across providers

### 3. Watcher System (watchers/)
Monitors external sources and creates action items in the vault:

**Gmail Watcher (watchers/gmail_watcher.py):**
- Uses Gmail API with OAuth authentication
- Monitors for important/unread emails
- Creates structured markdown files in Needs_Action folder
- Supports priority and category detection
- Marks emails as read after processing

**WhatsApp Watcher (watchers/whatsapp_watcher.py):**
- Uses Playwright for browser automation
- Monitors WhatsApp Web for messages
- Processes business communications

**Filesystem Watcher (watchers/filesystem_watcher.py):**
- Monitors designated folders for new files
- Processes documents and uploads automatically

### 4. MCP (Model Context Protocol) Servers (mcp/)
Enable Claude to interact with external systems:

**Email MCP Server (mcp/email/server.py):**
- Send emails via Gmail API
- Search and read emails
- Create email drafts
- Full integration with Claude's tool access

**LinkedIn MCP Server (mcp/linkedin/server.py):**
- Create professional posts
- Access profile information
- Schedule content posting
- Browser automation integration

**Twitter MCP Server (mcp/twitter/server.py):**
- Post tweets
- Access timeline and profile
- Schedule tweets
- Session management

### 5. Vault System (./vault/)
Local-first storage system based on Obsidian principles:

- **Needs_Action/**: Items requiring processing
- **Plans/**: AI-generated action plans
- **Pending_Approval/**: Items needing human approval
- **Approved/**: Items approved for execution
- **Done/**: Completed tasks
- **Logs/**: Activity logs
- **Briefings/**: CEO briefings and reports

### 6. Agent Teams System
Coordinated multi-agent workflows for complex tasks:

- Spawns specialized agents for different domains
- Coordinates activities between team members
- Shares context between agents
- Consolidates results from different domains

## How the System Works

### Email Processing Workflow
1. **Gmail Watcher** detects new important email via Gmail API
2. Creates structured markdown file in `vault/Needs_Action/`
3. **Orchestrator** detects new item and triggers Claude AI
4. **Multi-Provider AI** analyzes email using company handbook
5. If routine: executes action automatically via MCP server
6. If sensitive: creates approval request in `Pending_Approval/`
7. **Approval System** sends Slack/Discord notification
8. Human moves file to `Approved/` folder to authorize
9. **Orchestrator** executes approved action via MCP server
10. Result logged to `Done/` folder

### Ralph Wiggum Persistence Loop
1. Complex task assigned to system
2. Task broken into smaller steps
3. AI works on each step persistently
4. System verifies completion
5. If incomplete, continues working
6. Only escalates when truly stuck

### CEO Briefing Generation
1. Daily scan of completed tasks
2. Audit of business transactions
3. Identification of bottlenecks
4. Generation of weekly report
5. Proactive suggestions for improvements

## Technical Architecture

### Security & Privacy
- All data stored locally in vault
- OAuth 2.0 for external service access
- Human approval for sensitive operations
- Complete audit trail of all actions
- Dry-run mode for testing

### Extensibility
- Plugin-style MCP servers
- Modular watcher system
- Configurable AI routing
- Flexible approval workflows

### Reliability
- Graceful error handling
- Provider fallback mechanisms
- Quota management
- Health monitoring
- Process supervision

## Key Features

1. **24/7 Operation**: Runs continuously monitoring and processing
2. **Intelligent Reasoning**: Claude AI for complex decision-making
3. **Human Oversight**: Approval system for sensitive operations
4. **Multi-Source Input**: Email, WhatsApp, filesystem monitoring
5. **Multi-Service Output**: Email, social media, accounting integrations
6. **Business Intelligence**: CEO briefings and insights
7. **Persistence**: Ralph Wiggum loops ensure task completion
8. **Extensibility**: Easy addition of new MCP servers and watchers

The Personal AI Employee is a comprehensive system that combines Claude's reasoning power with local-first architecture and safe automation patterns to create a true digital employee that can manage personal and business affairs autonomously.