#!/usr/bin/env python3
import os

print("🔑 API Key Status Check - Gemini + OpenRouter + OpenAI Setup:")
print("-" * 60)

keys = {
    "GEMINI_API_KEY": "Gemini (Primary - FREE/very cheap, excellent performance)",
    "OPENROUTER_API_KEY": "OpenRouter (Secondary - Claude 3.5 Sonnet access)",
    "OPENAI_API_KEY": "OpenAI (Tertiary - GPT-4o for code tasks)"
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
    print("   🎯 RECOMMENDED: Start with Gemini (FREE tier):")
    print("   1. Go to https://makersuite.google.com/app/apikey")
    print("   2. Create API key")
    print("   3. export GEMINI_API_KEY='your_key'")
elif available_count == 1:
    print(f"\n💡 Great start! Consider adding more providers for better fallback:")
    if not os.getenv("OPENROUTER_API_KEY"):
        print("   🥈 Add OpenRouter for Claude 3.5 Sonnet access")
    if not os.getenv("OPENAI_API_KEY"):
        print("   🥉 Add OpenAI for superior code generation")
elif available_count == 2:
    print(f"\n🎉 Excellent setup! You have great fallback coverage.")
    if not os.getenv("GEMINI_API_KEY"):
        print("   💡 Consider adding Gemini for cost savings (FREE tier)")
    elif not os.getenv("OPENROUTER_API_KEY"):
        print("   💡 Consider adding OpenRouter for Claude access")
    elif not os.getenv("OPENAI_API_KEY"):
        print("   💡 Consider adding OpenAI for code tasks")
else:
    print(f"\n🚀 PERFECT! All providers configured!")
    print("   🎯 Your setup is enterprise-grade with maximum cost savings!")

print(f"\n💰 Cost Comparison:")
print("   🥇 Gemini: $0.001/1K tokens (FREE tier available)")
print("   🥈 OpenRouter: $0.012/1K tokens (Claude 3.5 Sonnet)")
print("   🥉 OpenAI: $0.010/1K tokens (GPT-4o)")
print("   💡 Estimated monthly cost: $3-18 (vs $30-45 with other setups)")

print(f"\n🚀 Next Steps:")
print("   1. Test system: python3 scripts/multi_provider_ai.py --status")
print("   2. Run demo: python3 scripts/demo_multi_provider.py")
print("   3. Go live: python3 orchestrator.py --vault ./vault --live")
