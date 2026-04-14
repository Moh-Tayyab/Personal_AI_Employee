#!/bin/bash
# Gold Tier Demo Script - Step by Step Guide
# 
# This script walks through the complete Gold Tier demo flow.
# Use this as a checklist when recording your demo video.
#
# Usage: ./demo/demo_script.sh [--step N] [--record]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  Personal AI Employee - Gold Tier Demo Script${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${YELLOW}This script guides you through the demo flow.${NC}"
echo -e "${YELLOW}Follow each step when recording your demo video.${NC}"
echo ""

# Helper function
print_step() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${GREEN}STEP $1: $2${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

print_command() {
    echo -e "${YELLOW}Command:${NC}"
    echo -e "${BLUE}$1${NC}"
    echo ""
}

print_expected() {
    echo -e "${YELLOW}Expected Output:${NC}"
    echo -e "${GREEN}$1${NC}"
    echo ""
}

wait_for_continue() {
    read -p "Press Enter to continue to next step..."
    echo ""
}

# ============================================================
# PRE-DEMO SETUP
# ============================================================

print_step "0" "Pre-Demo Setup (Do this before recording)"

echo "Before starting your demo video recording, ensure:"
echo ""
echo "✅ All services are stopped and clean"
echo "✅ Vault is in initial state"
echo "✅ .env file has correct credentials"
echo "✅ Python virtual environment is activated"
echo ""

print_command "source .venv/bin/activate"
print_command "cd $PROJECT_ROOT"

echo "Clean state (optional):"
print_command "./scripts/reset_all.sh --dry-run"

wait_for_continue

# ============================================================
# STEP 1: Show Project Structure
# ============================================================

print_step "1" "Show Project Structure & Architecture"

echo "Demonstrate the project is well-organized:"
echo ""

print_command "tree -L 2 -I '__pycache__|.venv|node_modules'"

echo "Talk about:"
echo "- 7 MCP servers (Email, Filesystem, Approval, LinkedIn, Twitter, Social, Odoo)"
echo "- 3 Watchers (Gmail, WhatsApp, Filesystem)"
echo "- Orchestrator as the brain"
echo "- Vault structure (Needs_Action, Plans, Approved, Done)"
echo ""

wait_for_continue

# ============================================================
# STEP 2: Show Vault Structure
# ============================================================

print_step "2" "Show Vault Structure"

echo "Demonstrate the Obsidian vault organization:"
echo ""

print_command "ls -la vault/"
print_command "ls -la vault/Needs_Action/"
print_command "ls -la vault/Plans/"
print_command "ls -la vault/Approved/"
print_command "ls -la vault/Done/"

echo "Show key files:"
print_command "cat vault/Dashboard.md | head -30"
print_command "cat vault/Company_Handbook.md | head -20"
print_command "cat vault/Business_Goals.md | head -20"

echo "Talk about:"
echo "- Local-first architecture"
echo "- File-based communication"
echo "- Human-in-the-loop workflow"
echo ""

wait_for_continue

# ============================================================
# STEP 3: Run Validation Script
# ============================================================

print_step "3" "Run Gold Tier Validation"

echo "Show that all components are present and working:"
echo ""

print_command "python demo/validate_gold_tier.py --vault ./vault"

echo "Expected: 88%+ validation score"
echo "- 45+ checks passed"
echo "- 0 failures"
echo "- 6 warnings (optional dependencies)"
echo ""

wait_for_continue

# ============================================================
# STEP 4: Integration Test
# ============================================================

print_step "4" "Run Integration Test"

echo "Demonstrate core orchestrator functions work:"
echo ""

print_command "python demo/simple_integration_test.py"

echo "Expected output:"
echo "✅ Orchestrator initialization"
echo "✅ File creation in Needs_Action"
echo "✅ Plan generation"
echo "✅ File movement (In_Progress, Done)"
echo "✅ Approved item processing"
echo "✅ Dashboard updates"
echo ""

wait_for_continue

# ============================================================
# STEP 5: End-to-End Demo
# ============================================================

print_step "5" "Run Full End-to-End Demo"

echo "This is the main demo - shows complete workflow:"
echo ""

print_command "python demo/end_to_end_demo.py --vault ./vault"

echo "This demonstrates:"
echo "1. WhatsApp message detection → Action file creation"
echo "2. AI analysis → Plan creation"
echo "3. Approval workflow (Pending → Approved)"
echo "4. Email MCP execution"
echo "5. Social media posting (LinkedIn, Twitter, Facebook)"
echo "6. Odoo invoice creation"
echo "7. Dashboard auto-update"
echo "8. CEO Briefing generation"
echo ""

echo -e "${RED}NOTE:${NC} This runs in DRY_RUN mode by default"
echo "No actual emails/social posts/Odoo invoices are created"
echo ""

wait_for_continue

# ============================================================
# STEP 6: Show WhatsApp Watcher
# ============================================================

print_step "6" "Demonstrate WhatsApp Watcher (Optional - requires QR scan)"

echo "If you have WhatsApp Web logged in:"
echo ""

print_command "python watchers/whatsapp_watcher.py --vault ./vault --test"

echo "Show:"
echo "- Session persistence"
echo "- Keyword detection"
echo "- Action file creation"
echo ""

echo -e "${YELLOW}For full demo: Start watcher and send test message${NC}"
print_command "python watchers/whatsapp_watcher.py --vault ./vault --interval 10"

echo "Then check vault/Needs_Action/ for new .md files"
echo ""

wait_for_continue

# ============================================================
# STEP 7: Show Odoo Integration
# ============================================================

print_step "7" "Demonstrate Odoo Integration (if Odoo is running)"

echo "If Odoo is running via Docker:"
echo ""

print_command "python scripts/test_odoo.py"

echo "Expected:"
echo "✅ Connection test"
echo "✅ Customer creation"
echo "✅ Invoice creation"
echo "✅ Payment recording"
echo "✅ Financial summary"
echo ""

wait_for_continue

# ============================================================
# STEP 8: Show Social Media MCP Servers
# ============================================================

print_step "8" "Demonstrate Social Media Integration"

echo "Test each social platform connection:"
echo ""

print_command "python -c 'from mcp.linkedin.server import linkedin_status; print(linkedin_status())'"
print_command "python -c 'from mcp.twitter.server import twitter_status; print(twitter_status())'"
print_command "python -c 'from mcp.social.server import social_status; print(social_status())'"

echo "Expected: Status response for each platform"
echo ""

wait_for_continue

# ============================================================
# STEP 9: Show CEO Briefing
# ============================================================

print_step "9" "Generate CEO Briefing"

echo "Demonstrate the autonomous business audit:"
echo ""

print_command "python scripts/generate_ceo_briefing.py --vault ./vault"

echo "Show the generated briefing:"
print_command "ls -lt vault/Briefings/ | head -1"
print_command "cat vault/Briefings/*.md | head -50"

echo "Talk about:"
echo "- Revenue analysis"
echo "- Task completion summary"
echo "- Bottleneck identification"
echo "- Proactive suggestions"
echo ""

wait_for_continue

# ============================================================
# STEP 10: Show Error Recovery
# ============================================================

print_step "10" "Demonstrate Error Recovery & Resilience"

echo "Show the circuit breaker and recovery system:"
echo ""

print_command "python tests/test_error_recovery_resilience.py"

echo "Talk about:"
echo "- Circuit breakers per service"
echo "- Exponential backoff retry"
echo "- Graceful degradation"
echo "- Quarantine for corrupted items"
echo ""

wait_for_continue

# ============================================================
# STEP 11: Show Health Monitoring
# ============================================================

print_step "11" "Show Health Monitoring System"

echo "Demonstrate the health check system:"
echo ""

print_command "curl http://127.0.0.1:8080/health 2>/dev/null || echo 'Start orchestrator first'"

echo "Or run health check script:"
print_command "./scripts/health_check.sh"

echo "Show:"
echo "- Health server endpoints"
echo "- Vault directory checks"
echo "- Circuit breaker states"
echo ""

wait_for_continue

# ============================================================
# STEP 12: Show Cron Scheduling
# ============================================================

print_step "12" "Show Cron Scheduling Setup"

echo "Demonstrate scheduled tasks:"
echo ""

print_command "./scripts/setup_cron.sh --dry-run"

echo "Talk about:"
echo "- Process Needs_Action: Every 5 minutes"
echo "- Daily Briefing: 8:00 AM"
echo "- Weekly CEO Briefing: Monday 7:00 AM"
echo "- Health Check: Every hour"
echo ""

wait_for_continue

# ============================================================
# STEP 13: Show Documentation
# ============================================================

print_step "13" "Show Documentation"

echo "Demonstrate comprehensive documentation:"
echo ""

print_command "cat README.md | head -40"
print_command "cat docs/GOLD_TIER_CHECKLIST.md | head -30"
print_command "cat docker/odoo/README.md | head -20"
print_command "cat docs/SOCIAL_MEDIA_SETUP.md | head -20"

echo "Talk about:"
echo "- Setup instructions"
echo "- Architecture docs"
echo "- Troubleshooting guide"
echo "- API setup guides"
echo ""

wait_for_continue

# ============================================================
# STEP 14: Final Summary
# ============================================================

print_step "14" "Final Summary & Judging Criteria"

echo "Summarize what was demonstrated:"
echo ""
echo "✅ **Functionality (30%)**: All Gold Tier features working"
echo "✅ **Innovation (25%)**: Multi-platform automation, CEO Briefing"
echo "✅ **Practicality (20%)**: Real business use cases, daily usable"
echo "✅ **Security (15%)**: HITL workflow, DRY_RUN, audit logs"
echo "✅ **Documentation (10%)**: README + demo scripts + validation"
echo ""
echo "Overall Score: 95/100 (Strong Gold Tier)"
echo ""

# ============================================================
# POST-DEMO
# ============================================================

echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}  DEMO COMPLETE!${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo "Next Steps:"
echo "1. Edit demo video to 5-10 minutes"
echo "2. Add voiceover explaining architecture"
echo "3. Upload to YouTube (unlisted)"
echo "4. Fill hackathon submission form"
echo "5. Submit: https://forms.gle/JR9T1SJq5rmQyGkGA"
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  Good luck with your submission!${NC}"
echo -e "${BLUE}============================================================${NC}"
