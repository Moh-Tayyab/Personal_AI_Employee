#!/bin/bash
# Start Odoo Community Edition via Docker
# Usage: ./scripts/start_odoo.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ODOO_DIR="$PROJECT_ROOT/docker/odoo"

echo "============================================================"
echo "  Starting Odoo Community Edition"
echo "============================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Ubuntu: sudo apt install docker.io"
    echo "   macOS: brew install --cask docker"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    echo "   Ubuntu: sudo apt install docker-compose"
    echo "   macOS: brew install docker-compose"
    exit 1
fi

# Check if Odoo directory exists
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
echo "Checking Odoo status..."

# Check if Odoo is already running
if $COMPOSE_CMD ps | grep -q "odoo-community"; then
    echo "✅ Odoo is already running!"
    echo ""
    echo "Odoo URL: http://localhost:8069"
    echo "PostgreSQL: localhost:5432"
    echo ""
    echo "To stop Odoo: ./scripts/stop_odoo.sh"
    echo "To view logs: $COMPOSE_CMD logs -f odoo"
    exit 0
fi

echo ""
echo "Starting Odoo services..."
echo ""

# Start services
$COMPOSE_CMD up -d

echo ""
echo "Waiting for Odoo to be ready..."
sleep 5

# Wait for Odoo to be healthy
MAX_WAIT=120
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8069 > /dev/null 2>&1; then
        echo ""
        echo "✅ Odoo is ready!"
        echo ""
        echo "============================================================"
        echo "  Odoo Community Edition - Started Successfully"
        echo "============================================================"
        echo ""
        echo "🌐 Odoo Web: http://localhost:8069"
        echo "🗄️  PostgreSQL: localhost:5432"
        echo "📊 Database: odoo"
        echo "👤 Default User: admin"
        echo "🔑 Default Password: admin (or set during setup)"
        echo ""
        echo "Next Steps:"
        echo "1. Open http://localhost:8069 in your browser"
        echo "2. Create database (master password: admin)"
        echo "3. Install Accounting module"
        echo "4. Generate API key in Settings → Users"
        echo "5. Update .env file with ODOO_API_KEY"
        echo "6. Test connection: python scripts/test_odoo.py"
        echo ""
        echo "Useful Commands:"
        echo "  View logs:        $COMPOSE_CMD logs -f odoo"
        echo "  Stop Odoo:        ./scripts/stop_odoo.sh"
        echo "  Restart:          $COMPOSE_CMD restart"
        echo "  Reset database:   $COMPOSE_CMD down -v && $COMPOSE_CMD up -d"
        echo ""
        echo "============================================================"
        exit 0
    fi
    
    echo -n "."
    sleep 2
    WAITED=$((WAITED + 2))
done

echo ""
echo "❌ Odoo startup timed out after ${MAX_WAIT}s"
echo ""
echo "Troubleshooting:"
echo "1. Check logs: $COMPOSE_CMD logs odoo"
echo "2. Check status: $COMPOSE_CMD ps"
echo "3. Restart: $COMPOSE_CMD restart"
exit 1
