#!/bin/bash
# Quick Setup Script for Multi-Provider AI System

echo "🚀 Setting up Multi-Provider AI System..."

# Create a test email to process
mkdir -p vault/Needs_Action

cat > vault/Needs_Action/TEST_EMAIL_001.md << 'EOF'
---
type: email
from: test@example.com
subject: Test Multi-Provider Processing
received: 2026-03-11T22:00:00Z
priority: medium
---

# Test Email for Multi-Provider AI System

From: test@example.com
Subject: Test Multi-Provider Processing

Hi Muhammad,

This is a test email to demonstrate the multi-provider AI system.

Please:
1. Analyze this email
2. Create an action plan
3. Show which tools and providers you would use
4. Demonstrate the fallback system

This will help verify that all Claude Code functionality is maintained across providers.

Best regards,
Test User
EOF

echo "✅ Test email created in vault/Needs_Action/"

# Create a simple API key check script
cat > scripts/check_api_keys.py << 'EOF'
#!/usr/bin/env python3
import os

print("🔑 API Key Status Check:")
print("-" * 30)

keys = {
    "ANTHROPIC_API_KEY": "Anthropic (Primary - thinking mode)",
    "OPENROUTER_API_KEY": "OpenRouter (Secondary - cost effective)",
    "GEMINI_API_KEY": "Gemini (Tertiary - very cheap)"
}

available_count = 0
for key, description in keys.items():
    if os.getenv(key):
        print(f"✅ {key}: Available - {description}")
        available_count += 1
    else:
        print(f"❌ {key}: Missing - {description}")

print(f"\n📊 Summary: {available_count}/3 providers configured")

if available_count == 0:
    print("\n⚠️  No API keys found. System will use fallback mode.")
    print("   Set at least one API key for full functionality:")
    print("   export ANTHROPIC_API_KEY='your_key'")
    print("   export OPENROUTER_API_KEY='your_key'")
    print("   export GEMINI_API_KEY='your_key'")
elif available_count < 3:
    print(f"\n💡 Tip: Add more API keys for better fallback coverage")
else:
    print(f"\n🎉 All providers configured! Full multi-provider functionality available.")
EOF

chmod +x scripts/check_api_keys.py

echo "✅ API key checker created"

# Test the system
echo ""
echo "🧪 Testing Multi-Provider System..."
python3 scripts/check_api_keys.py

echo ""
echo "🎯 Next Steps:"
echo "1. Set API keys: export ANTHROPIC_API_KEY='your_key'"
echo "2. Test system: python3 orchestrator.py --vault ./vault --dry-run"
echo "3. Go live: python3 orchestrator.py --vault ./vault --live"