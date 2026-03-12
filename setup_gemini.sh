#!/bin/bash
# Quick Setup Script - Get Gemini API Key and Test

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║          Personal AI Employee - Gemini Setup (FREE)                  ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Gemini key already exists
if grep -q "GEMINI_API_KEY=" .env 2>/dev/null; then
    echo "✅ GEMINI_API_KEY already exists in .env"
    GEMINI_KEY=$(grep "GEMINI_API_KEY=" .env | cut -d'=' -f2)
    if [ "$GEMINI_KEY" != "your_gemini_api_key_here" ] && [ ! -z "$GEMINI_KEY" ]; then
        echo "✅ Key is set: ${GEMINI_KEY:0:20}..."
        echo ""
        echo "Testing Gemini integration..."
        source .venv/bin/activate
        python test_gemini.py
        exit 0
    fi
fi

echo "📋 Steps to get FREE Gemini API key:"
echo ""
echo "1. Open browser: https://makersuite.google.com/app/apikey"
echo "2. Sign in with your Google account"
echo "3. Click 'Create API Key'"
echo "4. Select or create a Google Cloud project"
echo "5. Copy the API key"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Paste your Gemini API key here: " GEMINI_KEY
echo ""

if [ -z "$GEMINI_KEY" ]; then
    echo "❌ No key provided. Exiting."
    exit 1
fi

# Add to .env
echo "Adding GEMINI_API_KEY to .env..."
if grep -q "GEMINI_API_KEY=" .env 2>/dev/null; then
    # Replace existing
    sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$GEMINI_KEY/" .env
else
    # Add new
    echo "GEMINI_API_KEY=$GEMINI_KEY" >> .env
fi

echo "✅ API key added to .env"
echo ""
echo "Testing Gemini integration..."
echo ""

# Test the integration
source .venv/bin/activate
python test_gemini.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Run: python test_setup.py"
echo "  2. Run: python demo.py"
echo "  3. Start: python orchestrator.py --vault ./vault"
echo ""
