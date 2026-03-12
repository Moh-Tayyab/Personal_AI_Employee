#!/bin/bash

# Agent Teams Management Script for Personal AI Employee
# Usage: ./scripts/manage_teams.sh [command] [options]

set -e

VAULT_DIR="./vault"
TEAMS_DIR="$HOME/.claude/teams"
TASKS_DIR="$HOME/.claude/tasks"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if agent teams are enabled
check_agent_teams_enabled() {
    if [ ! -f ".claude/settings.json" ]; then
        log_error "Claude settings not found. Run from project root."
        exit 1
    fi

    if ! grep -q "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" .claude/settings.json; then
        log_error "Agent teams not enabled. Please enable in .claude/settings.json"
        exit 1
    fi

    log_info "Agent teams are enabled ✓"
}

# List active teams
list_teams() {
    log_info "Active Agent Teams:"
    if [ -d "$TEAMS_DIR" ]; then
        for team_dir in "$TEAMS_DIR"/*; do
            if [ -d "$team_dir" ]; then
                team_name=$(basename "$team_dir")
                config_file="$team_dir/config.json"
                if [ -f "$config_file" ]; then
                    member_count=$(jq -r '.members | length' "$config_file" 2>/dev/null || echo "0")
                    echo -e "  ${GREEN}$team_name${NC} ($member_count members)"

                    # Show team members
                    if [ "$member_count" -gt 0 ]; then
                        jq -r '.members[] | "    - \(.name) (\(.agentType))"' "$config_file" 2>/dev/null || true
                    fi
                else
                    echo -e "  ${YELLOW}$team_name${NC} (config missing)"
                fi
            fi
        done
    else
        echo "  No active teams found"
    fi
}

# Show team tasks
show_team_tasks() {
    local team_name="$1"
    if [ -z "$team_name" ]; then
        log_error "Team name required"
        exit 1
    fi

    local tasks_dir="$TASKS_DIR/$team_name"
    if [ ! -d "$tasks_dir" ]; then
        log_warning "No tasks found for team: $team_name"
        return
    fi

    log_info "Tasks for team: $team_name"

    # Count tasks by status
    local pending=$(find "$tasks_dir" -name "*.json" -exec jq -r 'select(.status == "pending") | .id' {} \; 2>/dev/null | wc -l)
    local in_progress=$(find "$tasks_dir" -name "*.json" -exec jq -r 'select(.status == "in_progress") | .id' {} \; 2>/dev/null | wc -l)
    local completed=$(find "$tasks_dir" -name "*.json" -exec jq -r 'select(.status == "completed") | .id' {} \; 2>/dev/null | wc -l)

    echo -e "  Pending: ${YELLOW}$pending${NC}"
    echo -e "  In Progress: ${BLUE}$in_progress${NC}"
    echo -e "  Completed: ${GREEN}$completed${NC}"

    # Show recent tasks
    echo -e "\n  Recent Tasks:"
    find "$tasks_dir" -name "*.json" -exec jq -r '"\(.id): \(.subject) [\(.status)]"' {} \; 2>/dev/null | head -10 | while read line; do
        echo "    $line"
    done
}

# Clean up inactive teams
cleanup_teams() {
    log_info "Cleaning up inactive teams..."

    if [ -d "$TEAMS_DIR" ]; then
        for team_dir in "$TEAMS_DIR"/*; do
            if [ -d "$team_dir" ]; then
                team_name=$(basename "$team_dir")
                config_file="$team_dir/config.json"

                # Check if team has active members
                if [ -f "$config_file" ]; then
                    # This is a simplified check - in practice, you'd want to check if processes are running
                    log_warning "Found team: $team_name - manual cleanup may be required"
                else
                    log_info "Removing empty team directory: $team_name"
                    rm -rf "$team_dir"
                fi
            fi
        done
    fi

    # Clean up orphaned task directories
    if [ -d "$TASKS_DIR" ]; then
        for task_dir in "$TASKS_DIR"/*; do
            if [ -d "$task_dir" ]; then
                task_team=$(basename "$task_dir")
                if [ ! -d "$TEAMS_DIR/$task_team" ]; then
                    log_info "Removing orphaned task directory: $task_team"
                    rm -rf "$task_dir"
                fi
            fi
        done
    fi

    log_success "Cleanup completed"
}

# Create team template
create_team_template() {
    local template_name="$1"
    local template_dir="./templates/agent_teams"

    if [ -z "$template_name" ]; then
        log_error "Template name required"
        exit 1
    fi

    mkdir -p "$template_dir"

    case "$template_name" in
        "business-ops")
            cat > "$template_dir/business-operations-team.md" << 'EOF'
# Business Operations Team Template

## Team Composition
- **Email Specialist**: Handle email processing, responses, and follow-ups
- **Social Media Manager**: Manage LinkedIn, Twitter, Instagram posts and engagement
- **Accounting Specialist**: Process invoices, track expenses, update Odoo
- **Research Analyst**: Gather market intelligence and competitive analysis

## Spawn Command
```
Create an agent team for business operations with 4 teammates:
- Email specialist: Handle email processing, responses, and follow-ups using the email MCP server. Focus on urgent emails, partnership inquiries, and customer communications.
- Social media manager: Manage LinkedIn, Twitter, Instagram posts and engagement using social MCP servers. Create content, respond to mentions, track engagement.
- Accounting specialist: Process invoices, track expenses, update Odoo using accounting MCP. Handle financial data entry, expense categorization, revenue tracking.
- Research analyst: Gather market intelligence and competitive analysis. Use web search and data analysis tools to provide business insights.

Each teammate should work independently on their domain while coordinating through the shared task list.
```

## Task Examples
1. Process morning email batch (Email Specialist)
2. Create LinkedIn post about new feature (Social Media Manager)
3. Update Q1 expense report (Accounting Specialist)
4. Research competitor pricing (Research Analyst)

## Quality Gates
- Email responses must be reviewed before sending
- Social media posts require brand voice compliance
- Financial data must be double-checked for accuracy
- Research findings should include sources and confidence levels
EOF
            ;;
        "development")
            cat > "$template_dir/development-team.md" << 'EOF'
# Development Team Template

## Team Composition
- **Backend Developer**: Focus on MCP servers, orchestrator, and API integrations
- **Frontend Developer**: Handle vault UI, dashboards, and user interfaces
- **DevOps Engineer**: Manage deployment, monitoring, and system health

## Spawn Command
```
Spawn a development team with 3 teammates:
- Backend developer: Focus on MCP servers, orchestrator, and API integrations. Handle Python code, server logic, database operations, and API endpoints.
- Frontend developer: Handle vault UI, dashboards, and user interfaces. Work on HTML, CSS, JavaScript, and user experience improvements.
- DevOps engineer: Manage deployment, monitoring, and system health. Handle Docker, CI/CD, logging, and infrastructure automation.

Require plan approval for any changes that affect production systems.
```

## Task Examples
1. Fix email MCP server authentication bug (Backend Developer)
2. Create dashboard for team metrics (Frontend Developer)
3. Set up monitoring for MCP server health (DevOps Engineer)
4. Implement new social media integration (Backend Developer)

## Quality Gates
- All code changes require testing
- Production deployments need approval
- Security vulnerabilities must be addressed immediately
- Performance impacts should be measured
EOF
            ;;
        "content")
            cat > "$template_dir/content-team.md" << 'EOF'
# Content & Communication Team Template

## Team Composition
- **Content Writer**: Create blog posts, documentation, and marketing materials
- **Social Media Strategist**: Plan campaigns and engagement strategies
- **Customer Support**: Handle inquiries, complaints, and support tickets
- **Brand Manager**: Ensure consistent messaging and brand voice

## Spawn Command
```
Create a content team with 4 specialists:
- Content writer: Create blog posts, documentation, and marketing materials. Focus on technical writing, SEO optimization, and engaging content.
- Social media strategist: Plan campaigns and engagement strategies. Develop content calendars, analyze metrics, optimize posting schedules.
- Customer support: Handle inquiries, complaints, and support tickets. Provide helpful responses, escalate issues, track satisfaction.
- Brand manager: Ensure consistent messaging and brand voice. Review all content for brand compliance, tone, and messaging alignment.

All content must be approved by brand manager before publication.
```

## Task Examples
1. Write blog post about AI automation benefits (Content Writer)
2. Plan Q2 social media campaign (Social Media Strategist)
3. Respond to customer support tickets (Customer Support)
4. Review marketing materials for brand compliance (Brand Manager)

## Quality Gates
- All content must pass brand voice review
- Customer responses should be empathetic and helpful
- Social media content needs engagement optimization
- Documentation should be clear and actionable
EOF
            ;;
        *)
            log_error "Unknown template: $template_name"
            log_info "Available templates: business-ops, development, content"
            exit 1
            ;;
    esac

    log_success "Created team template: $template_dir/$template_name-team.md"
}

# Show help
show_help() {
    echo "Agent Teams Management Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  list                    List all active teams"
    echo "  tasks <team_name>       Show tasks for a specific team"
    echo "  cleanup                 Clean up inactive teams and orphaned tasks"
    echo "  template <name>         Create a team template (business-ops, development, content)"
    echo "  check                   Check if agent teams are properly configured"
    echo "  help                    Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 tasks business-operations"
    echo "  $0 template business-ops"
    echo "  $0 cleanup"
}

# Main script logic
case "${1:-help}" in
    "list")
        check_agent_teams_enabled
        list_teams
        ;;
    "tasks")
        check_agent_teams_enabled
        show_team_tasks "$2"
        ;;
    "cleanup")
        check_agent_teams_enabled
        cleanup_teams
        ;;
    "template")
        create_team_template "$2"
        ;;
    "check")
        check_agent_teams_enabled
        log_success "Agent teams configuration is valid"
        ;;
    "help"|*)
        show_help
        ;;
esac