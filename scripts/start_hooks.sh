#!/bin/bash
# Start Hook Server for Personal AI Employee
# Enables HTTP endpoints and webhook integrations

set -e

# Configuration
VAULT_PATH="${VAULT_PATH:-./vault}"
PORT="${HOOK_PORT:-8080}"
SECRET="${WEBHOOK_SECRET:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting Personal AI Employee Hook Server...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required${NC}"
    exit 1
fi

# Check vault exists
if [ ! -d "$VAULT_PATH" ]; then
    echo -e "${YELLOW}Warning: Vault path does not exist: $VAULT_PATH${NC}"
    echo "Creating vault directory..."
    mkdir -p "$VAULT_PATH"
    mkdir -p "$VAULT_PATH/Needs_Action"
    mkdir -p "$VAULT_PATH/Pending_Approval"
    mkdir -p "$VAULT_PATH/Approved"
    mkdir -p "$VAULT_PATH/Done"
    mkdir -p "$VAULT_PATH/Logs"
fi

# Check for webhook config
if [ ! -f "$VAULT_PATH/secrets/webhooks.json" ]; then
    echo -e "${YELLOW}No webhook config found. Creating example...${NC}"
    mkdir -p "$VAULT_PATH/secrets"
    cat > "$VAULT_PATH/secrets/webhooks.json" << 'EOF'
{
  "webhooks": {
    "slack": "",
    "discord": "",
    "generic": ""
  },
  "http_server": {
    "port": 8080,
    "enabled": true,
    "secret": ""
  }
}
EOF
    echo "Created $VAULT_PATH/secrets/webhooks.json"
    echo "Edit this file to configure webhooks"
fi

# Start the server
echo -e "${GREEN}Starting HTTP hook server on port $PORT${NC}"
echo "Vault: $VAULT_PATH"
echo ""
echo "Available endpoints:"
echo "  GET  /health         - Health check"
echo "  GET  /status         - System status"
echo "  GET  /pending        - Pending approvals"
echo "  GET  /dashboard      - Dashboard data"
echo "  POST /webhook/email  - Email webhook"
echo "  POST /webhook/approval - Approval callback"
echo "  POST /webhook/github - GitHub webhook"
echo "  POST /trigger/process - Trigger processing"
echo ""

# Run the server
python3 -c "
from hooks import run_server
run_server(port=$PORT, vault_path='$VAULT_PATH', webhook_secret='$SECRET')
"