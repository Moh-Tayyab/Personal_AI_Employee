#!/bin/bash
# Quick Start Script for Gold Tier Demo
#
# This script:
# 1. Validates all components
# 2. Runs the end-to-end demo
# 3. Shows final status
#
# Usage: ./demo/quick_start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VAULT_PATH="${PROJECT_ROOT}/vault"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "========================================"
echo "  Personal AI Employee - Gold Tier"
echo "  Quick Start Demo"
echo "========================================"
echo -e "${NC}"

# Check if vault exists
if [ ! -d "$VAULT_PATH" ]; then
    echo -e "${RED}❌ Vault not found at: $VAULT_PATH${NC}"
    echo "Please ensure vault directory exists"
    exit 1
fi

# Step 1: Validation
echo ""
echo -e "${CYAN}Step 1: Validating Gold Tier Components...${NC}"
echo ""

cd "$PROJECT_ROOT"
export VAULT_PATH="$VAULT_PATH"
export DRY_RUN="true"

if python demo/validate_gold_tier.py --vault "$VAULT_PATH"; then
    echo -e "\n${GREEN}✅ Validation passed!${NC}\n"
else
    echo -e "\n${YELLOW}⚠️  Validation had warnings/failures - review above${NC}\n"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 2: End-to-End Demo
echo ""
echo -e "${CYAN}Step 2: Running End-to-End Demo...${NC}"
echo ""

python demo/end_to_end_demo.py --vault "$VAULT_PATH"

# Step 3: Final Status
echo ""
echo -e "${CYAN}Step 3: Final Status...${NC}"
echo ""

python -c "
from pathlib import Path
vault = Path('$VAULT_PATH')

print('Vault Contents:')
for folder in ['Needs_Action', 'In_Progress', 'Pending_Approval', 'Approved', 'Done', 'Plans', 'Briefings', 'Logs']:
    folder_path = vault / folder
    if folder_path.exists():
        count = len(list(folder_path.glob('*.md')))
        print(f'  {folder:25s} {count} file(s)')
    else:
        print(f'  {folder:25s} (not found)')
"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Gold Tier Demo Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next Steps:"
echo "  1. Review the generated files in vault/"
echo "  2. Check vault/Briefings/ for CEO Briefing"
echo "  3. Check vault/Dashboard.md for status"
echo "  4. Check vault/Logs/ for audit trail"
echo ""
echo "To run in LIVE mode (real external actions):"
echo "  export DRY_RUN=false"
echo "  python orchestrator.py --vault ./vault --live"
echo ""
