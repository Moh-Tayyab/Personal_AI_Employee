#!/bin/bash
# Personal AI Employee - Demo Script
# Showcase the capabilities of the Personal AI Employee system

set -e  # Exit on any error

echo "==========================================="
echo "   Personal AI Employee - Live Demo"
echo "==========================================="
echo ""
echo "Welcome to the Personal AI Employee demo!"
echo "This system acts as your digital employee managing personal and business affairs."
echo ""

# Function to show a separator
show_separator() {
    echo ""
    echo "-------------------------------------------"
    echo "$1"
    echo "-------------------------------------------"
    echo ""
}

# Function to simulate a delay for demo effect
wait_for_demo() {
    echo "..."
    sleep 2
}

show_separator "1. SYSTEM ARCHITECTURE OVERVIEW"

echo "The Personal AI Employee consists of:"
echo ""
echo "🧠 BRAIN: Claude Code as the reasoning engine with Ralph Wiggum persistence loops"
echo "🗄️  MEMORY: Obsidian-style Markdown vault for all data and context"
echo "👂 SENSES: Python watchers monitoring Gmail, WhatsApp, and filesystems"
echo "🔌 ACTIONS: MCP servers for email, social media, accounting, and other services"
echo "🛡️  SAFETY: Human-in-the-loop approval system for sensitive operations"
echo ""

wait_for_demo

show_separator "2. VAULT STRUCTURE DEMONSTRATION"

echo "Let's examine the Obsidian-style vault structure:"
echo ""
tree -L 2 ./vault/ 2>/dev/null || find ./vault/ -maxdepth 2 -type d 2>/dev/null | sed 's/^/    /'

echo ""
echo "Key vault components:"
echo "- Dashboard.md: System status overview"
echo "- Company_Handbook.md: AI rules and autonomy levels"
echo "- Business_Goals.md: Revenue targets and KPIs"
echo "- Needs_Action/: Items requiring processing"
echo "- Plans/: Generated action plans"
echo "- Pending_Approval/: Items awaiting human approval"
echo "- Approved/: Items approved for execution"
echo "- Logs/: Daily activity logs"
echo "- Briefings/: CEO briefing reports"
echo ""

wait_for_demo

show_separator "3. WATCHER SYSTEMS"

echo "The system monitors multiple sources simultaneously:"
echo ""
echo "📧 Gmail Watcher: Monitors your inbox via Gmail API"
echo "📱 WhatsApp Watcher: Watches for messages via Playwright automation"
echo "📁 Filesystem Watcher: Monitors designated folders for new files"
echo ""
echo "When any of these sources detect new items, they:"
echo "- Add the item to the 'Needs_Action/' folder in the vault"
echo "- Trigger the orchestrator to process the item"
echo "- Generate plans and execute actions as appropriate"
echo ""

wait_for_demo

show_separator "4. ORCHESTRATOR DEMONSTRATION"

echo "The orchestrator coordinates all system components:"
echo ""
python3 orchestrator.py --help || echo "Orchestrator is available"
echo ""
echo "Key orchestrator capabilities:"
echo "- Processes items from 'Needs_Action/' folder"
echo "- Uses Claude API for intelligent decision making"
echo "- Generates action plans in the 'Plans/' folder"
echo "- Coordinates with MCP servers for external actions"
echo "- Implements Ralph Wiggum loops for persistent task completion"
echo ""

wait_for_demo

show_separator "5. MCP SERVERS (Model Context Protocol)"

echo "MCP servers enable Claude to control external systems:"
echo ""
echo "📧 Email MCP Server:"
echo "  - Send emails via Gmail API"
echo "  - Search and read emails"
echo "  - Create email drafts"
echo ""
echo "👔 LinkedIn MCP Server:"
echo "  - Create professional posts"
echo "  - Access profile information"
echo "  - Schedule content"
echo ""
echo "🐦 Twitter MCP Server:"
echo "  - Post tweets (max 280 chars)"
echo "  - Get timeline and profile"
echo "  - Schedule tweets"
echo ""
echo "💰 Odoo MCP Server:"
echo "  - Fetch invoices and contacts"
echo "  - Query account balances"
echo "  - Access product catalogs"
echo ""
echo "These servers provide Claude with agency to act on your behalf."
echo ""

wait_for_demo

show_separator "6. APPROVAL WORKFLOW"

echo "Sensitive operations require human approval:"
echo ""
echo "1. System identifies sensitive action (payments, important emails, etc.)"
echo "2. Moves item to 'Pending_Approval/' folder in vault"
echo "3. Sends webhook notification to Slack/Discord"
echo "4. Human reviews and approves via vault file movement"
echo "5. System executes approved actions"
echo ""
echo "This maintains human oversight while enabling automation."
echo ""

wait_for_demo

show_separator "7. CEO BRIEFING GENERATOR"

echo "The system generates weekly CEO briefings that:"
echo ""
echo "- Audit business transactions and revenue"
echo "- Identify bottlenecks and issues"
echo "- Summarize completed tasks"
echo "- Highlight upcoming deadlines"
echo "- Provide proactive suggestions"
echo ""
echo "This transforms the AI from a chatbot into a proactive business partner."
echo ""

wait_for_demo

show_separator "8. RALPH WIGGUM PERSISTENCE LOOP"

echo "Named after 'I meant to do that' Ralph Wiggum, the system:"
echo ""
echo "1. Receives a complex task"
echo "2. Breaks it into smaller steps"
echo "3. Works persistently until completion"
echo "4. Self-monitors to verify completion"
echo "5. Asks for help when stuck"
echo ""
echo "This ensures complex multi-step tasks get completed reliably."
echo ""

wait_for_demo

show_separator "9. HTTP WEBHOOK INTEGRATION"

echo "The system exposes HTTP endpoints for external integration:"
echo ""
echo "GET    /health          - Health check"
echo "GET    /status          - System status"
echo "GET    /pending         - List pending approvals"
echo "GET    /dashboard       - Dashboard data"
echo "POST   /webhook/email   - Receive email webhooks"
echo "POST   /webhook/approval - Approval callbacks"
echo "POST   /trigger/process - Trigger processing"
echo "POST   /teams/create    - Create agent teams"
echo "GET    /teams/list      - List active teams"
echo ""

wait_for_demo

show_separator "10. AGENT TEAMS COORDINATION"

echo "For complex multi-domain tasks, the system can:"
echo ""
echo "- Spawn multiple specialized agents"
echo "- Coordinate their activities"
echo "- Share context between team members"
echo "- Consolidate results from different domains"
echo "- Maintain consistent execution standards"
echo ""
echo "This enables handling of sophisticated business operations."
echo ""

wait_for_demo

show_separator "11. DRY-RUN SAFETY MODE"

echo "Before executing any action, the system supports:"
echo ""
echo "- DRY_RUN environment variable"
echo "- Safe simulation of all actions"
echo "- Detailed preview of intended operations"
echo "- Risk assessment and validation"
echo ""
echo "This ensures safety during development and testing."
echo ""

wait_for_demo

show_separator "12. LIVE DEMO SETUP EXAMPLE"

echo "To run the Personal AI Employee, you would typically:"
echo ""
echo "# 1. Set up environment variables"
echo "export ANTHROPIC_API_KEY='your-key'"
echo "export GMAIL_TOKEN_PATH='./vault/secrets/gmail_token.json'"
echo ""
echo "# 2. Install dependencies"
echo "pip install -r requirements.txt"
echo ""
echo "# 3. Start the orchestrator"
echo "python orchestrator.py --vault ./vault --dry-run false"
echo ""
echo "# 4. Or start all services"
echo "./scripts/start_all.sh"
echo ""

wait_for_demo

show_separator "CONCLUSION"

echo "The Personal AI Employee delivers:"
echo ""
echo "✅ AUTONOMOUS: Operates 24/7 without manual intervention"
echo "✅ INTELLIGENT: Uses Claude for human-like reasoning"
echo "✅ SAFE: Human approval for sensitive operations"
echo "✅ FLEXIBLE: MCP servers adapt to various services"
echo "✅ PROACTIVE: CEO briefings and business insights"
echo "✅ SCALABLE: Agent teams handle complex operations"
echo "✅ PRIVATE: All data stored locally in your vault"
echo "✅ EXTENSIBLE: Easy to add new MCP servers and capabilities"
echo ""
echo "This creates a true Digital FTE that manages your personal and business affairs."
echo ""
echo "Demo completed!"