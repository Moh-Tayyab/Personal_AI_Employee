#!/bin/bash
# Gold Tier Demo Script
#
# Demonstrates:
# - Full end-to-end automation loop
# - Social media posting (LinkedIn, Twitter, Facebook, Instagram) via MCP
# - Odoo invoice creation via MCP
# - Approval workflow
# - CEO Briefing generation
# - Error recovery and circuit breakers
#
# Usage: ./scripts/gold_tier_demo.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VAULT_PATH="${PROJECT_ROOT}/vault"
PYTHON="${PROJECT_ROOT}/.venv/bin/python"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Gold Tier Demo${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "This demo shows:"
echo "  1. Social media posting (LinkedIn, Twitter, Facebook, Instagram)"
echo "  2. Odoo invoice creation"
echo "  3. Approval workflow"
echo "  4. CEO Briefing generation"
echo "  5. Error recovery status"
echo ""
echo -e "${YELLOW}All actions run in DRY_RUN mode — no real posts or invoices created.${NC}"
echo ""
read -p "Press Enter to begin..."

cd "$PROJECT_ROOT"
export VAULT_PATH="$VAULT_PATH"
export DRY_RUN="true"

# ============================================================
# Step 1: Social Media — LinkedIn Post
# ============================================================
echo ""
echo -e "${GREEN}── Step 1: LinkedIn Post (Approved) ──${NC}"

cat > "$VAULT_PATH/Approved/SOCIAL_linkedin_post.md" << 'EOF'
---
type: approval_response
action: linkedin_post
content: 🚀 Exciting news! Our AI Employee automation platform is now processing 10x more tasks with 90% cost reduction. Learn how we built it: #AI #Automation #Innovation
visibility: PUBLIC
---

# Approved LinkedIn Post

This post has been reviewed and approved for publishing.
EOF

"$PYTHON" -c "
import sys
sys.path.insert(0, '.')
from orchestrator import Orchestrator
from pathlib import Path

orch = Orchestrator(vault_path='$VAULT_PATH', dry_run=True)

item = Path('$VAULT_PATH/Approved/SOCIAL_linkedin_post.md')
if item.exists():
    result = orch.process_approved_item(item)
    if result:
        orch.move_to_done(item)
        print(f'✅ LinkedIn post processed and moved to Done')
    else:
        print(f'❌ LinkedIn post failed')
else:
    print(f'❌ File not found')
"

# ============================================================
# Step 2: Social Media — Twitter Thread
# ============================================================
echo ""
echo -e "${GREEN}── Step 2: Twitter Thread (Approved) ──${NC}"

cat > "$VAULT_PATH/Approved/SOCIAL_twitter_thread.md" << 'EOF'
---
type: approval_response
action: twitter_post
content: 🧵 How we built an AI Employee that works 24/7: 1/ The architecture uses Watchers (sensors) + MCP servers (hands) + Qwen Code (brain) + Obsidian (memory). Here's how it all fits together... #AI #Automation
---

# Approved Twitter Post
EOF

"$PYTHON" -c "
import sys
sys.path.insert(0, '.')
from orchestrator import Orchestrator
from pathlib import Path

orch = Orchestrator(vault_path='$VAULT_PATH', dry_run=True)

item = Path('$VAULT_PATH/Approved/SOCIAL_twitter_thread.md')
if item.exists():
    result = orch.process_approved_item(item)
    if result:
        orch.move_to_done(item)
        print(f'✅ Twitter post processed and moved to Done')
    else:
        print(f'❌ Twitter post failed')
else:
    print(f'❌ File not found')
"

# ============================================================
# Step 3: Social Media — Facebook/Instagram Cross-Platform
# ============================================================
echo ""
echo -e "${GREEN}── Step 3: Facebook Post (Approved) ──${NC}"

cat > "$VAULT_PATH/Approved/SOCIAL_facebook_post.md" << 'EOF'
---
type: approval_response
action: social_post
platform: facebook
content: 🚀 Our AI Employee automation platform is transforming how businesses operate. 90% cost reduction, 24/7 availability. Learn more about building your own digital FTE.
---

# Approved Facebook Post
EOF

"$PYTHON" -c "
import sys
sys.path.insert(0, '.')
from orchestrator import Orchestrator
from pathlib import Path

orch = Orchestrator(vault_path='$VAULT_PATH', dry_run=True)

item = Path('$VAULT_PATH/Approved/SOCIAL_facebook_post.md')
if item.exists():
    result = orch.process_approved_item(item)
    if result:
        orch.move_to_done(item)
        print(f'✅ Facebook post processed and moved to Done')
    else:
        print(f'❌ Facebook post failed')
else:
    print(f'❌ File not found')
"

# ============================================================
# Step 4: Odoo Invoice Creation
# ============================================================
echo ""
echo -e "${GREEN}── Step 4: Odoo Invoice Creation (Approved) ──${NC}"

cat > "$VAULT_PATH/Approved/ODOO_invoice_demo.md" << 'EOF'
---
type: approval_response
action: odoo_invoice
partner_name: Demo Client Corp
partner_email: demo@clientcorp.com
amount: 2500.00
---

# Odoo Invoice Creation

## Invoice Details
- **Client:** Demo Client Corp
- **Email:** demo@clientcorp.com
- **Amount:** $2,500.00
- **Service:** AI Employee Automation Setup
- **Line Items:**
  - line: name=Consulting, quantity=10, price_unit=150
  - line: name=Implementation, quantity=1, price_unit=1000
EOF

"$PYTHON" -c "
import sys
sys.path.insert(0, '.')
from orchestrator import Orchestrator
from pathlib import Path

orch = Orchestrator(vault_path='$VAULT_PATH', dry_run=True)

item = Path('$VAULT_PATH/Approved/ODOO_invoice_demo.md')
if item.exists():
    result = orch.process_approved_item(item)
    if result:
        orch.move_to_done(item)
        print(f'✅ Odoo invoice processed and moved to Done')
    else:
        print(f'❌ Odoo invoice failed')
else:
    print(f'❌ File not found')
"

# ============================================================
# Step 5: Generate CEO Briefing
# ============================================================
echo ""
echo -e "${GREEN}── Step 5: CEO Briefing Generation ──${NC}"

"$PYTHON" scripts/generate_ceo_briefing.py --vault "$VAULT_PATH" --period 7 2>&1 | head -20

echo ""
echo -e "${CYAN}Latest briefing:${NC}"
ls -lt "$VAULT_PATH/Briefings/" 2>/dev/null | head -3 || echo "  No briefings yet"

# ============================================================
# Step 6: Error Recovery Status
# ============================================================
echo ""
echo -e "${GREEN}── Step 6: System Status ──${NC}"

"$PYTHON" -c "
import sys
sys.path.insert(0, '.')
from orchestrator import Orchestrator

orch = Orchestrator(vault_path='$VAULT_PATH', dry_run=True)
report = {
    'vault': str(orch.vault_path),
    'needs_action': len(orch.check_needs_action()),
    'pending_approval': len(orch.check_pending_approval()),
    'approved': len(orch.check_approved()),
    'done': len(list(orch.done.glob('*.md'))),
    'dry_run': orch.dry_run,
}
for k, v in report.items():
    print(f'  {k}: {v}')
"

# ============================================================
# Summary
# ============================================================
echo ""
echo -e "${GREEN}── Vault Summary ──${NC}"

for dir in Needs_Action In_Progress Pending_Approval Approved Done Plans Briefings; do
    count=$(find "$VAULT_PATH/$dir" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
    printf "  %-20s %d file(s)\n" "$dir" "$count"
done

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Gold Tier Demo Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "To clean up demo files:"
echo "  rm vault/Done/*demo* vault/Done/*SOCIAL* vault/Done/*ODOO*"
echo ""
