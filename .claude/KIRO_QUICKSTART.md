# Kiro for Claude Code - Quick Start Guide

## Overview

Kiro for Claude Code is a VSCode extension that brings spec-driven development to your Personal AI Employee project. It provides specialized agents for requirements, design, and task generation with parallel processing capabilities.

## Installation

### Option 1: VSCode Marketplace
1. Open VSCode
2. Go to Extensions (Cmd+Shift+X)
3. Search for "Kiro for Claude Code"
4. Click Install

### Option 2: Command Line
```bash
code --install-extension heisebaiyun.kiro-for-cc
```

### Option 3: Cursor
1. Open Cursor
2. Go to Extensions
3. Search for "Kiro for Claude Code"
4. Click Install

## Project Setup (Complete ✅)

This project is already configured with Kiro. The following structure exists:

```
.claude/
├── specs/                      # Feature specifications
├── agents/kfc/                 # Built-in workflow agents (7 agents)
├── steering/                   # AI guidance documents (3 docs)
└── settings/kfc-settings.json  # Configuration
```

## Usage

### Creating a Spec with Sub-Agents (Recommended)

1. **Open Kiro Panel**
   - Click the "Kiro for CC" icon in the VSCode activity bar

2. **Start New Spec**
   - In the SPEC view header, click "New Spec with Agents" button (✨)
   - Enter your feature description, e.g.:
     ```
     Build a WhatsApp watcher that detects messages containing
     "invoice" and creates action files in the vault
     ```

3. **Watch Agents Work**
   - **Requirements Agent**: Analyzes your description, creates user stories
   - **Design Agent**: Architects the solution in parallel
   - **Tasks Agent**: Breaks down implementation into steps
   - **Judge Agent**: Reviews all outputs for quality

4. **Review Outputs**
   - Check `.claude/specs/{spec-name}/requirements.md`
   - Review `.claude/specs/{spec-name}/design.md`
   - Examine `.claude/specs/{spec-name}/tasks.md`

5. **Implement**
   - Pick tasks from `tasks.md`
   - Update task status as you work
   - Mark complete when done

### Traditional Method (Sequential)

1. Click "+" in SPEC view
2. Enter feature description
3. Review generated requirements
4. Approve to generate design
5. Review design
6. Approve to generate tasks

## Sample Spec

A complete sample spec is provided: `Email Notification System`

View it at:
- `.claude/specs/email-notification-system/requirements.md`
- `.claude/specs/email-notification-system/design.md`
- `.claude/specs/email-notification-system/tasks.md`

## Steering Documents

These guide AI behavior across all specs:

| Document | Purpose |
|----------|---------|
| `product.md` | Product vision, user personas, principles |
| `tech.md` | Technology stack, coding standards, security |
| `structure.md` | Repository layout, file conventions |

## Workflow Agents

### 1. Requirements Agent (`spec-requirements.md`)
**Focus**: WHAT to build
- User personas
- User stories
- Functional requirements
- Acceptance criteria

### 2. Design Agent (`spec-design.md`)
**Focus**: HOW to build
- Architecture overview
- Data models
- API contracts
- Security considerations

### 3. Tasks Agent (`spec-tasks.md`)
**Focus**: Implementation steps
- Task breakdown
- Dependencies
- Effort estimates
- Critical path

### 4. Judge Agent (`spec-judge.md`)
**Focus**: Quality assurance
- Reviews requirements
- Validates design
- Approves tasks
- Provides feedback

### 5. Implementation Agent (`spec-impl.md`)
**Focus**: Code execution
- Follows design
- Writes clean code
- Updates task status

### 6. Test Agent (`spec-test.md`)
**Focus**: Validation
- Test plans
- Coverage verification
- Sign-off decisions

### 7. System Prompt Loader (`spec-system-prompt-loader.md`)
**Focus**: Coordination
- Manages sub-agents
- Handles context windows
- Orchestrates handoffs

## Configuration

Edit `.claude/settings/kfc-settings.json`:

```json
{
  "paths": {
    "specs": ".claude/specs",
    "steering": ".claude/steering",
    "agents": ".claude/agents"
  },
  "workflow": {
    "enable_sub_agents": true,
    "parallel_processing": true
  }
}
```

## Best Practices

### Writing Good Feature Descriptions
✅ **Good**:
```
Build a Gmail watcher that monitors for invoices,
categorizes emails by urgency, and sends WhatsApp
notifications for urgent messages
```

❌ **Bad**:
```
Add email stuff
```

### Reviewing Agent Outputs
1. **Requirements**: Are all user personas identified?
2. **Design**: Does it follow existing architecture?
3. **Tasks**: Are tasks appropriately sized (1-4 hours)?

### Task Execution
1. Move task to "In Progress" when starting
2. Add implementation notes
3. Reference commit hashes
4. Move to "Done" when complete

## Troubleshooting

### Sub-agents taking too long
- This is a known issue mentioned in the extension docs
- Use traditional method as fallback
- Check Claude API status

### Specs not appearing
- Verify `.claude/specs/` directory exists
- Check Kiro settings in `.claude/settings/kfc-settings.json`
- Reload VSCode window

### Agent configurations missing
- Re-run this setup script
- Check `.claude/agents/kfc/` directory
- Compare with sample configs

## Next Steps

1. **Try the sample spec**: Review `email-notification-system` spec
2. **Create your first spec**: Use sub-agents for a new feature
3. **Implement a task**: Pick a task and complete it
4. **Customize agents**: Edit agent configs for your needs

## Resources

- [Kiro GitHub Repository](https://github.com/notdp/kiro-for-cc)
- [VSCode Marketplace](https://marketplace.visualstudio.com/items?itemName=heisebaiyun.kiro-for-cc)
- [Sample Spec](.claude/specs/email-notification-system/)
- [Workflow Agents](.claude/agents/kfc/)
