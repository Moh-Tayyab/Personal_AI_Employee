#!/bin/bash
# Stop WhatsApp Automation Script

echo "Stopping WhatsApp Automation..."

# Kill watcher
if [ -f /tmp/whatsapp_watcher.pid ]; then
    WATCHER_PID=$(cat /tmp/whatsapp_watcher.pid)
    kill $WATCHER_PID 2>/dev/null || echo "Watcher already stopped"
    rm /tmp/whatsapp_watcher.pid
    echo "✓ Watcher stopped"
fi

# Kill orchestrator
if [ -f /tmp/whatsapp_orchestrator.pid ]; then
    ORCHESTRATOR_PID=$(cat /tmp/whatsapp_orchestrator.pid)
    kill $ORCHESTRATOR_PID 2>/dev/null || echo "Orchestrator already stopped"
    rm /tmp/whatsapp_orchestrator.pid
    echo "✓ Orchestrator stopped"
fi

echo ""
echo "WhatsApp Automation stopped successfully"
