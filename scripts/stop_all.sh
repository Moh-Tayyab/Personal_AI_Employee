#!/bin/bash
# Personal AI Employee - Stop All Services

set -e

cd /home/Personal_AI_Employee

echo "=== Stopping all services ==="

# Stop PM2 processes first
if command -v pm2 &> /dev/null; then
    echo "Stopping PM2 processes..."
    pm2 stop all 2>/dev/null || true
    pm2 delete all 2>/dev/null || true
    echo "PM2 processes stopped."
fi

# Stop any stray processes by PID files
for pidfile in logs/*.pid; do
    if [ -f "$pidfile" ]; then
        pid=$(cat "$pidfile")
        service=$(basename "$pidfile" .pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo "  Stopped $service (PID: $pid)"
        fi
        rm "$pidfile"
    fi
done

# Kill any remaining Python watcher processes
pkill -f "gmail_watcher" 2>/dev/null || true
pkill -f "whatsapp_watcher" 2>/dev/null || true
pkill -f "filesystem_watcher" 2>/dev/null || true
pkill -f "orchestrator.py" 2>/dev/null || true

echo "All services stopped."