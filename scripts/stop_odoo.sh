#!/bin/bash
# Stop Odoo Community Edition
# Usage: ./scripts/stop_odoo.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ODOO_DIR="$PROJECT_ROOT/docker/odoo"

echo "============================================================"
echo "  Stopping Odoo Community Edition"
echo "============================================================"

if [ ! -d "$ODOO_DIR" ]; then
    echo "❌ Odoo Docker directory not found: $ODOO_DIR"
    exit 1
fi

cd "$ODOO_DIR"

# Determine which docker-compose command to use
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo ""
echo "Stopping Odoo services..."
$COMPOSE_CMD down

echo ""
echo "✅ Odoo stopped successfully!"
echo ""
echo "To start again: ./scripts/start_odoo.sh"
echo "============================================================"
