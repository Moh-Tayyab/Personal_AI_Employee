#!/bin/bash
# Silver Tier Demo Script
#
# Demonstrates:
# - Filesystem watcher detecting a new file
# - Orchestrator processing the item
# - Plan creation
# - Approval workflow
# - Email MCP (dry_run)
#
# Usage: ./scripts/silver_tier_demo.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VAULT_PATH="${PROJECT_ROOT}/vault"
PYTHON="${PROJECT_ROOT}/.venv/bin/python"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Silver Tier Demo${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "This demo shows:"
echo "  1. File drop detection"
echo "  2. Orchestrator processing"
echo "  3. Plan creation"
echo "  4. Approval workflow"
echo "  5. Email MCP (dry_run)"
echo ""
echo -e "${YELLOW}All actions run in DRY_RUN mode — no real emails sent.${NC}"
echo ""
read -p "Press Enter to begin..."

cd "$PROJECT_ROOT"
export VAULT_PATH="$VAULT_PATH"
export DRY_RUN="true"

# ============================================================
# Step 1: Create a sample item in Needs_Action
# ============================================================
echo ""
echo -e "${GREEN}── Step 1: Creating test item in Needs_Action ──${NC}"

cat > "$VAULT_PATH/Needs_Action/EMAIL_silver_demo.md" << 'EOF'
---
type: email
source: demo
from: client@business.com
subject: Silver Tier Demo - Project Inquiry
received: 2026-04-03T10:00:00
priority: high
category: general
status: pending
---

# Silver Tier Demo - Project Inquiry

Hi,

I'm interested in your AI Employee automation services.
Could you send me a proposal with pricing?

Looking forward to hearing from you.

Best regards,
Demo Client
EOF

echo "✅ Created: Needs_Action/EMAIL_silver_demo.md"
echo "   From: client@business.com"
echo "   Subject: Silver Tier Demo - Project Inquiry"

# ============================================================
# Step 2: Orchestrator processes the item
# ============================================================
echo ""
echo -e "${GREEN}── Step 2: Orchestrator processing ──${NC}"

"$PYTHON" -c "
import sys, os
sys.path.insert(0, '.')
from orchestrator import Orchestrator

orch = Orchestrator(vault_path='$VAULT_PATH', dry_run=True)

# Check Needs_Action
items = orch.check_needs_action()
print(f'  Items in Needs_Action: {len(items)}')

# Process the demo item
demo_item = next((f for f in items if 'silver_demo' in f.name), None)
if demo_item:
    print(f'  Processing: {demo_item.name}')

    # Create plan
    plan = orch.create_plan(demo_item)
    print(f'  ✅ Plan created: {plan.name}')

    # Trigger AI analysis
    content = demo_item.read_text()
    orch.trigger_ai(f'Analyze and process: {demo_item.name}')
    print(f'  ✅ AI analysis triggered')

    # Move to In_Progress
    orch.move_to_in_progress(demo_item)
    print(f'  ✅ Moved to In_Progress')
else:
    print('  ❌ Demo item not found')
"

# ============================================================
# Step 3: Create approval request (simulating AI decision)
# ============================================================
echo ""
echo -e "${GREEN}── Step 3: Creating approval request ──${NC}"

cat > "$VAULT_PATH/Pending_Approval/APPROVAL_silver_demo_reply.md" << 'EOF'
---
type: approval_request
action: send_email
to: client@business.com
subject: Re: Silver Tier Demo - Project Inquiry
approved: false
created: 2026-04-03T10:05:00
---

# Approval Request: Email Reply

## Details
- **To:** client@business.com
- **Subject:** Re: Silver Tier Demo - Project Inquiry
- **Reason:** Client requested a proposal

## Proposed Reply
Thank you for your interest in our AI Employee automation services.

I'd be happy to send you a proposal with pricing details.
Could you please share more about your specific requirements?

Best regards,
AI Employee Team
EOF

echo "✅ Created: Pending_Approval/APPROVAL_silver_demo_reply.md"

# ============================================================
# Step 4: Approve and execute (simulating human approval)
# ============================================================
echo ""
echo -e "${GREEN}── Step 4: Simulating human approval ──${NC}"

cp "$VAULT_PATH/Pending_Approval/APPROVAL_silver_demo_reply.md" \
   "$VAULT_PATH/Approved/APPROVAL_silver_demo_reply.md"

echo "✅ Moved to Approved/"

"$PYTHON" -c "
import sys, os
sys.path.insert(0, '.')
from orchestrator import Orchestrator
from pathlib import Path

orch = Orchestrator(vault_path='$VAULT_PATH', dry_run=True)

approved = orch.check_approved()
for item in approved:
    if 'silver_demo' in item.name:
        print(f'  Executing: {item.name}')
        success = orch.process_approved_item(item)
        if success:
            orch.move_to_done(item)
            print(f'  ✅ Executed and moved to Done')
        else:
            print(f'  ❌ Execution failed')
"

# ============================================================
# Step 5: Show results
# ============================================================
echo ""
echo -e "${GREEN}── Step 5: Results ──${NC}"

echo "  Vault folders:"
for dir in Needs_Action In_Progress Pending_Approval Approved Done Plans; do
    count=$(find "$VAULT_PATH/$dir" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
    echo "    $dir: $count file(s)"
done

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Silver Tier Demo Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "To clean up demo files:"
echo "  rm vault/Needs_Action/*silver* vault/In_Progress/*silver* vault/Done/*silver* vault/Plans/*silver*"
echo ""
