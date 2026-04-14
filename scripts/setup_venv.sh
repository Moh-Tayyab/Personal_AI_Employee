#!/bin/bash
# Setup Python Virtual Environment and Dependencies
# Usage: ./scripts/setup_venv.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "============================================================"
echo "  Personal AI Employee - Python Environment Setup"
echo "============================================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python version: $PYTHON_VERSION"

# Check if .venv already exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "⚠️  Virtual environment already exists"
    read -p "Do you want to recreate it? (y/N): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing virtual environment..."
        source "$PROJECT_ROOT/.venv/bin/activate"
        echo "✅ Virtual environment activated"
        echo ""
        echo "Installing/updating dependencies..."
        pip install -r requirements.txt
        echo ""
        echo "✅ Dependencies installed!"
        exit 0
    fi
    echo "Removing old virtual environment..."
    rm -rf "$PROJECT_ROOT/.venv"
fi

echo ""
echo "Creating virtual environment..."
python3 -m venv "$PROJECT_ROOT/.venv"

# Activate virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

echo ""
echo "Upgrading pip..."
pip install --upgrade pip

echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r "$PROJECT_ROOT/requirements.txt"

echo ""
echo "============================================================"
echo "  Environment Setup Complete!"
echo "============================================================"
echo ""
echo "Virtual Environment: $PROJECT_ROOT/.venv"
echo "Python: $(which python)"
echo "Pip: $(which pip)"
echo ""
echo "To activate manually:"
echo "  source $PROJECT_ROOT/.venv/bin/activate"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
echo "============================================================"
