#!/bin/bash
# Multi-CLI Personal AI Employee Startup Script
# Supports Claude, Qwen, and Codex with automatic fallback

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
VAULT_PATH="./vault"
DRY_RUN=true
PRIMARY_CLI="claude"
ENABLE_FALLBACK=true

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if CLI is available
check_cli() {
    local cli_name=$1
    local cli_cmd=$2

    if command -v "$cli_cmd" &> /dev/null; then
        print_success "$cli_name CLI found"
        return 0
    else
        print_warning "$cli_name CLI not found"
        return 1
    fi
}

# Function to test CLI functionality
test_cli() {
    local cli_name=$1
    print_status "Testing $cli_name..."

    if python scripts/multi_cli_manager.py --test 2>/dev/null | grep -q "$cli_name: ✅"; then
        print_success "$cli_name is working"
        return 0
    else
        print_warning "$cli_name test failed"
        return 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --vault)
            VAULT_PATH="$2"
            shift 2
            ;;
        --live)
            DRY_RUN=false
            shift
            ;;
        --primary-cli)
            PRIMARY_CLI="$2"
            shift 2
            ;;
        --force-cli)
            PRIMARY_CLI="$2"
            ENABLE_FALLBACK=false
            shift 2
            ;;
        --no-fallback)
            ENABLE_FALLBACK=false
            shift
            ;;
        --test-only)
            TEST_ONLY=true
            shift
            ;;
        --help)
            echo "Multi-CLI Personal AI Employee Startup Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --vault PATH          Path to vault directory (default: ./vault)"
            echo "  --live                Run in live mode (default: dry-run)"
            echo "  --primary-cli CLI     Primary CLI to use (claude|qwen|codex)"
            echo "  --force-cli CLI       Force specific CLI, disable fallback"
            echo "  --no-fallback         Disable automatic fallback"
            echo "  --test-only           Only test CLIs and exit"
            echo "  --help                Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --vault ./vault --live --primary-cli claude"
            echo "  $0 --force-cli qwen --vault ./vault"
            echo "  $0 --test-only"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_status "🚀 Starting Multi-CLI Personal AI Employee"
print_status "Vault: $VAULT_PATH"
print_status "Mode: $([ "$DRY_RUN" = true ] && echo "DRY-RUN" || echo "LIVE")"
print_status "Primary CLI: $PRIMARY_CLI"
print_status "Fallback: $([ "$ENABLE_FALLBACK" = true ] && echo "ENABLED" || echo "DISABLED")"

# Check Python dependencies
print_status "Checking Python dependencies..."
cd "$(dirname "$0")/.." || exit 1  # Change to project root
if ! python3 -c "import sys; sys.path.append('scripts'); from multi_cli_manager import MultiCLIManager" 2>/dev/null; then
    print_error "Multi-CLI system not available. Please check scripts/multi_cli_manager.py"
    exit 1
fi
print_success "Python dependencies OK"

# Check available CLIs
print_status "Checking available CLIs..."
CLAUDE_AVAILABLE=false
QWEN_AVAILABLE=false
CODEX_AVAILABLE=false

if check_cli "Claude" "claude"; then
    CLAUDE_AVAILABLE=true
fi

if check_cli "Qwen" "qwen"; then
    QWEN_AVAILABLE=true
fi

if check_cli "GitHub Copilot" "gh"; then
    if gh copilot --version &>/dev/null; then
        print_success "GitHub Copilot CLI found"
        CODEX_AVAILABLE=true
    else
        print_warning "GitHub CLI found but Copilot extension not installed"
        print_status "Install with: gh extension install github/gh-copilot"
    fi
fi

# Check if at least one CLI is available
if [ "$CLAUDE_AVAILABLE" = false ] && [ "$QWEN_AVAILABLE" = false ] && [ "$CODEX_AVAILABLE" = false ]; then
    print_error "No CLIs available! Please install at least one:"
    echo "  - Claude CLI: Follow Claude Code installation guide"
    echo "  - Qwen CLI: pip install qwen-cli"
    echo "  - GitHub Copilot: gh extension install github/gh-copilot"
    exit 1
fi

# Validate primary CLI is available
case $PRIMARY_CLI in
    claude)
        if [ "$CLAUDE_AVAILABLE" = false ]; then
            print_error "Primary CLI 'claude' not available"
            if [ "$ENABLE_FALLBACK" = false ]; then
                exit 1
            else
                print_warning "Will fallback to available CLI"
            fi
        fi
        ;;
    qwen)
        if [ "$QWEN_AVAILABLE" = false ]; then
            print_error "Primary CLI 'qwen' not available"
            if [ "$ENABLE_FALLBACK" = false ]; then
                exit 1
            else
                print_warning "Will fallback to available CLI"
            fi
        fi
        ;;
    codex)
        if [ "$CODEX_AVAILABLE" = false ]; then
            print_error "Primary CLI 'codex' not available"
            if [ "$ENABLE_FALLBACK" = false ]; then
                exit 1
            else
                print_warning "Will fallback to available CLI"
            fi
        fi
        ;;
esac

# Test CLIs if requested
if [ "$TEST_ONLY" = true ]; then
    print_status "🧪 Testing CLI functionality..."
    python3 scripts/multi_cli_manager.py --test
    exit 0
fi

# Create vault directories
print_status "Setting up vault structure..."
mkdir -p "$VAULT_PATH"/{Needs_Action,Plans,Done,Pending_Approval,Approved,Rejected,Logs,config}
print_success "Vault structure ready"

# Check quota status
print_status "Checking quota status..."
python scripts/quota_manager.py --status > /tmp/quota_status.json
RECOMMENDED_CLI=$(python scripts/quota_manager.py --best-cli)
print_status "Recommended CLI: $RECOMMENDED_CLI"

# Start the orchestrator
print_status "🎯 Starting orchestrator..."

ORCHESTRATOR_ARGS="--vault $VAULT_PATH --primary-cli $PRIMARY_CLI"

if [ "$DRY_RUN" = false ]; then
    ORCHESTRATOR_ARGS="$ORCHESTRATOR_ARGS --live"
fi

if [ "$ENABLE_FALLBACK" = false ]; then
    ORCHESTRATOR_ARGS="$ORCHESTRATOR_ARGS --force-cli $PRIMARY_CLI"
fi

print_status "Command: python orchestrator.py $ORCHESTRATOR_ARGS"

# Trap signals for graceful shutdown
trap 'print_status "Shutting down..."; exit 0' INT TERM

# Start the orchestrator
exec python orchestrator.py $ORCHESTRATOR_ARGS