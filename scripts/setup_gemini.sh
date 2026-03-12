#!/bin/bash
# Gemini API Key Setup Guide - Interactive Script

echo "🚀 GEMINI API KEY SETUP GUIDE"
echo "=============================="
echo ""

echo "📋 STEP 1: Get Your FREE Gemini API Key"
echo "----------------------------------------"
echo "1. Open your browser and go to:"
echo "   👉 https://makersuite.google.com/app/apikey"
echo ""
echo "2. Sign in with your Google account"
echo ""
echo "3. Click the 'Create API key' button"
echo ""
echo "4. Copy the API key (it starts with 'AIza...')"
echo ""

read -p "✅ Have you copied your API key? (y/n): " api_key_ready

if [ "$api_key_ready" != "y" ]; then
    echo "❌ Please get your API key first, then run this script again."
    exit 1
fi

echo ""
echo "📋 STEP 2: Enter Your API Key"
echo "------------------------------"
read -p "🔑 Paste your Gemini API key here: " GEMINI_KEY

if [ -z "$GEMINI_KEY" ]; then
    echo "❌ No API key entered. Please try again."
    exit 1
fi

echo ""
echo "📋 STEP 3: Setting Up Environment"
echo "----------------------------------"

# Set the environment variable for current session
export GEMINI_API_KEY="$GEMINI_KEY"

# Add to .bashrc for persistence
echo "export GEMINI_API_KEY=\"$GEMINI_KEY\"" >> ~/.bashrc

# Add to .env file for the project
echo "GEMINI_API_KEY=$GEMINI_KEY" >> .env

echo "✅ API key set for current session"
echo "✅ API key added to ~/.bashrc (permanent)"
echo "✅ API key added to .env file (project)"

echo ""
echo "📋 STEP 4: Testing Your Setup"
echo "------------------------------"

# Test the API key
echo "🧪 Testing your Gemini API key..."

python3 scripts/check_api_keys.py

echo ""
echo "📋 STEP 5: Test Multi-Provider System"
echo "--------------------------------------"

python3 scripts/multi_provider_ai.py --status

echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo ""
echo "Your Gemini API key is now configured and ready to use!"
echo ""
echo "💰 Cost: FREE tier includes:"
echo "   • 15 requests per minute"
echo "   • 1,500 requests per day"
echo "   • 1 million tokens per month"
echo ""
echo "🚀 Next Steps:"
echo "   1. Start your AI employee: python3 orchestrator.py --vault ./vault --live"
echo "   2. Drop emails in vault/Needs_Action/ and watch it work!"
echo "   3. Monitor usage: python3 scripts/multi_provider_ai.py --status"
echo ""
echo "🎯 Your Personal AI Employee is now running on FREE Gemini!"