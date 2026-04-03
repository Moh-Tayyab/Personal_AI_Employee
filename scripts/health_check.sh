#!/bin/bash
# Health Check Validation — Validate System Health
#
# Checks:
# - Health server endpoint responds with valid JSON
# - All required vault directories exist
# - No stale In_Progress items (older than 24h)
# - Disk space under threshold
# - Python environment intact
# - MCP server scripts present and valid
# - No corrupted log files
#
# Usage:
#   ./scripts/health_check.sh [--strict] [--json]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VAULT_PATH="${PROJECT_ROOT}/vault"
HEALTH_PORT="${HEALTH_PORT:-8080}"
PYTHON="${PROJECT_ROOT}/.venv/bin/python"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

STRICT=false
JSON_MODE=false
ISSUES=0
WARNINGS=0

if [[ "$1" == "--strict" ]]; then STRICT=true; fi
if [[ "$1" == "--json" ]] || [[ "$2" == "--json" ]]; then JSON_MODE=true; fi

RESULTS=()

check_pass() {
    if [ "$JSON_MODE" = false ]; then
        echo -e "  ${GREEN}✅ $1${NC}"
    fi
    RESULTS+=("PASS:$1")
}

check_warn() {
    WARNINGS=$((WARNINGS + 1))
    if [ "$JSON_MODE" = false ]; then
        echo -e "  ${YELLOW}⚠️  $1${NC}"
    fi
    RESULTS+=("WARN:$1")
}

check_fail() {
    ISSUES=$((ISSUES + 1))
    if [ "$JSON_MODE" = false ]; then
        echo -e "  ${RED}❌ $1${NC}"
    fi
    RESULTS+=("FAIL:$1")
}

if [ "$JSON_MODE" = false ]; then
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Health Check Validation${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
fi

# ---- 1. Health Server Endpoint ----
if [ "$JSON_MODE" = false ]; then echo -e "${BLUE}── Health Server ──${NC}"; fi

HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "http://127.0.0.1:${HEALTH_PORT}/health/status" 2>/dev/null || echo -e "\n000")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -1)
BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    # Validate JSON response
    if echo "$BODY" | python3 -m json.tool > /dev/null 2>&1; then
        check_pass "Health server responding with valid JSON (HTTP $HTTP_CODE)"
    else
        check_warn "Health server responding but JSON invalid"
    fi
else
    check_fail "Health server not responding (HTTP $HTTP_CODE)"
fi

# ---- 2. Vault Directory Integrity ----
if [ "$JSON_MODE" = false ]; then echo -e "\n${BLUE}── Vault Directories ──${NC}"; fi

REQUIRED_DIRS="Needs_Action In_Progress Pending_Approval Approved Rejected Plans Done Logs Briefings"
for dir in $REQUIRED_DIRS; do
    if [ -d "$VAULT_PATH/$dir" ]; then
        count=$(find "$VAULT_PATH/$dir" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
        check_pass "$dir exists ($count files)"
    else
        check_fail "$dir MISSING"
    fi
done

# ---- 3. Stale In_Progress Items ----
if [ "$JSON_MODE" = false ]; then echo -e "\n${BLUE}── Stale Items ──${NC}"; fi

stale_items=$(find "$VAULT_PATH/In_Progress" -maxdepth 1 -name "*.md" -mtime +1 2>/dev/null | wc -l)
if [ "$stale_items" -gt 0 ]; then
    check_warn "$stale_items item(s) in In_Progress for >24h (may be stalled)"
else
    check_pass "No stale In_Progress items"
fi

# ---- 4. Disk Space ----
if [ "$JSON_MODE" = false ]; then echo -e "\n${BLUE}── Disk Space ──${NC}"; fi

DISK_USAGE=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    check_fail "Disk usage critical: ${DISK_USAGE}%"
elif [ "$DISK_USAGE" -gt 80 ]; then
    check_warn "Disk usage high: ${DISK_USAGE}%"
else
    check_pass "Disk usage healthy: ${DISK_USAGE}%"
fi

# ---- 5. Python Environment ----
if [ "$JSON_MODE" = false ]; then echo -e "\n${BLUE}── Python Environment ──${NC}"; fi

if [ -f "$PYTHON" ]; then
    PY_VER=$("$PYTHON" --version 2>&1)
    check_pass "Python available: $PY_VER"

    # Check key imports
    for module in "orchestrator" "mcp.server.fastmcp"; do
        if "$PYTHON" -c "import $module" 2>/dev/null; then
            check_pass "Module available: $module"
        else
            if [ "$STRICT" = true ]; then
                check_fail "Module missing: $module"
            else
                check_warn "Module missing: $module (non-critical)"
            fi
        fi
    done
else
    check_fail "Python not found at $PYTHON"
fi

# ---- 6. MCP Server Scripts ----
if [ "$JSON_MODE" = false ]; then echo -e "\n${BLUE}── MCP Servers ──${NC}"; fi

for server in email filesystem approval linkedin twitter social odoo; do
    server_file="$PROJECT_ROOT/mcp/$server/server.py"
    if [ -f "$server_file" ]; then
        # Syntax check
        if "$PYTHON" -m py_compile "$server_file" 2>/dev/null; then
            check_pass "$server/server.py (syntax OK)"
        else
            check_fail "$server/server.py (syntax error)"
        fi
    else
        check_fail "$server/server.py MISSING"
    fi
done

# ---- 7. Log File Integrity ----
if [ "$JSON_MODE" = false ]; then echo -e "\n${BLUE}── Log Files ──${NC}"; fi

TODAY=$(date '+%Y-%m-%d')
if [ -f "$VAULT_PATH/Logs/${TODAY}.json" ]; then
    if python3 -c "import json; json.load(open('$VAULT_PATH/Logs/${TODAY}.json'))" 2>/dev/null; then
        check_pass "Today's log valid JSON"
    else
        check_fail "Today's log corrupted JSON"
    fi
else
    check_warn "No log entries today yet (normal for first run)"
fi

# ---- Summary ----
echo ""
if [ "$JSON_MODE" = true ]; then
    echo "{"
    echo "  \"timestamp\": \"$(date -Iseconds)\","
    echo "  \"status\": \"$([ $ISSUES -eq 0 ] && echo 'healthy' || echo 'degraded')\","
    echo "  \"issues\": $ISSUES,"
    echo "  \"warnings\": $WARNINGS,"
    echo "  \"checks\": ["
    for result in "${RESULTS[@]}"; do
        type="${result%%:*}"
        msg="${result#*:}"
        echo "    {\"status\": \"$type\", \"message\": \"$msg\"},"
    done
    echo "  ]"
    echo "}"
else
    echo "========================================"
    if [ $ISSUES -eq 0 ]; then
        echo -e "${GREEN}  ✅ HEALTHY — $ISSUES issues, $WARNINGS warning(s)${NC}"
    elif [ $ISSUES -le 2 ]; then
        echo -e "${YELLOW}  ⚠️  DEGRADED — $ISSUES issues, $WARNINGS warning(s)${NC}"
    else
        echo -e "${RED}  ❌ UNHEALTHY — $ISSUES issues, $WARNINGS warning(s)${NC}"
    fi
    echo "========================================"
fi

exit $ISSUES
