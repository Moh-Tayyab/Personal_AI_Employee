#!/bin/bash
# WhatsApp Automation Startup Script
# Starts both the WhatsApp Watcher and Orchestrator

set -e

echo "=================================="
echo "  WhatsApp Automation Starting"
echo "=================================="

# Configuration
VAULT_PATH="${OBSIDIAN_VAULT_PATH:-.}"
SESSION_PATH="${WHATSAPP_SESSION_PATH:-$VAULT_PATH/.whatsapp_session}"
CHECK_INTERVAL="${WHATSAPP_CHECK_INTERVAL:-30}"

echo "Vault Path: $VAULT_PATH"
echo "Session Path: $SESSION_PATH"
echo "Check Interval: ${CHECK_INTERVAL}s"

# Create necessary directories
mkdir -p "$VAULT_PATH/Needs_Action"
mkdir -p "$VAULT_PATH/Plans"
mkdir -p "$VAULT_PATH/Pending_Approval"
mkdir -p "$VAULT_PATH/Approved"
mkdir -p "$VAULT_PATH/Done"
mkdir -p "$VAULT_PATH/Logs"

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Python Version: $PYTHON_VERSION"

# Check required packages
echo "Checking required packages..."
python3 -c "import playwright; print('✓ Playwright installed')" 2>/dev/null || {
    echo "✗ Playwright not found. Installing..."
    pip install playwright
}

python3 -c "import mcp; print('✓ MCP installed')" 2>/dev/null || {
    echo "✗ MCP not found. Installing..."
    pip install mcp
}

# Install Playwright browsers if needed
echo "Installing Playwright browsers..."
python3 -m playwright install chromium

# Start WhatsApp Watcher in background
echo ""
echo "Starting WhatsApp Watcher..."
python3 watchers/whatsapp_watcher.py \
    --vault "$VAULT_PATH" \
    --session "$SESSION_PATH" \
    --interval "$CHECK_INTERVAL" &
WATCHER_PID=$!
echo "Watcher PID: $WATCHER_PID"

# Start Orchestrator in background
echo ""
echo "Starting WhatsApp Orchestrator..."
python3 watchers/whatsapp_orchestrator.py \
    --vault "$VAULT_PATH" &
ORCHESTRATOR_PID=$!
echo "Orchestrator PID: $ORCHESTRATOR_PID"

# Save PIDs for cleanup
echo "$WATCHER_PID" > /tmp/whatsapp_watcher.pid
echo "$ORCHESTRATOR_PID" > /tmp/whatsapp_orchestrator.pid

echo ""
echo "=================================="
echo "  WhatsApp Automation Running"
echo "=================================="
echo ""
echo "Next Steps:"
echo "1. Scan the QR code that appears in the browser"
echo "2. WhatsApp messages will be automatically monitored"
echo "3. Action files will be created in Needs_Action/"
echo "4. Approve responses by moving files to Approved/"
echo ""
echo "To stop: kill $WATCHER_PID $ORCHESTRATOR_PID"
echo "Or run: bash scripts/stop_whatsapp.sh"

# Wait for processes
wait $WATCHER_PID $ORCHESTRATOR_PID
