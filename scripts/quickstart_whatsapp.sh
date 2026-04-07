#!/bin/bash
# WhatsApp Automation Quick Start Guide
# Run this script to get started quickly

echo "=========================================="
echo "  WhatsApp Automation - Quick Start"
echo "=========================================="
echo ""

# Step 1: Check Python
echo "Step 1: Checking Python installation..."
python3 --version
echo ""

# Step 2: Install dependencies
echo "Step 2: Installing dependencies..."
pip install playwright mcp
echo ""

# Step 3: Install Playwright browsers
echo "Step 3: Installing Playwright browsers..."
python3 -m playwright install chromium
echo ""

# Step 4: Create vault structure
echo "Step 4: Creating vault structure..."
mkdir -p vault/Needs_Action
mkdir -p vault/Plans
mkdir -p vault/Pending_Approval
mkdir -p vault/Approved
mkdir -p vault/Done
mkdir -p vault/Logs
mkdir -p vault/.whatsapp_session
echo "✓ Vault structure created"
echo ""

# Step 5: Set environment variables
echo "Step 5: Setting environment variables..."
export OBSIDIAN_VAULT_PATH="./vault"
echo "✓ OBSIDIAN_VAULT_PATH=$OBSIDIAN_VAULT_PATH"
echo ""

# Step 6: Start automation
echo "Step 6: Starting WhatsApp automation..."
echo ""
echo "A browser will open with WhatsApp Web QR code."
echo "Please scan it with your phone."
echo ""
echo "Press Ctrl+C to stop the automation."
echo ""
sleep 3

# Start the automation
bash scripts/start_whatsapp.sh
