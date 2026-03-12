#!/usr/bin/env python3
"""
Test Gemini API Integration

This script tests if Gemini API is working correctly.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_gemini():
    """Test Gemini API integration."""
    print("="*70)
    print("Testing Gemini API Integration")
    print("="*70)
    print()

    # Check for API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found in .env")
        print()
        print("Get a free API key:")
        print("1. Visit: https://makersuite.google.com/app/apikey")
        print("2. Create API key")
        print("3. Add to .env: GEMINI_API_KEY=your_key_here")
        return False

    print(f"✅ API key found: {gemini_key[:20]}...")
    print()

    # Test API call
    print("📡 Testing API call...")
    try:
        import requests

        data = {
            "contents": [{
                "parts": [{
                    "text": "Say 'Hello! I am working correctly.' if you can read this."
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": 100,
                "temperature": 0.7
            }
        }

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={gemini_key}",
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ Gemini API works!")
            print()
            print("Response:")
            print("-"*70)
            print(text)
            print("-"*70)
            print()
            return True
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_orchestrator():
    """Test orchestrator with Gemini."""
    print()
    print("="*70)
    print("Testing Orchestrator with Gemini")
    print("="*70)
    print()

    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from orchestrator import Orchestrator

        orch = Orchestrator('./vault', dry_run=False)

        test_email = """---
type: email
from: test@example.com
subject: Test Email for Gemini
date: 2026-03-10
---

Hi Muhammad,

This is a test email to verify that Gemini AI integration is working.

Can you confirm receipt?

Thanks!
"""

        print("📧 Processing test email with Gemini...")
        print()

        result = orch.trigger_claude(test_email)

        if result:
            print()
            print("✅ Orchestrator processed email successfully!")
            print()

            # Check for plan file
            plans = list(Path('./vault/Plans').glob('AI_PLAN_*.md'))
            if plans:
                latest = max(plans, key=lambda p: p.stat().st_mtime)
                print(f"📄 Plan created: {latest.name}")
                print()

                # Show preview
                content = latest.read_text()
                print("Plan preview:")
                print("-"*70)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if i < 35:
                        print(line)
                print("...")
                print("-"*70)

            return True
        else:
            print("❌ Orchestrator failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║              Gemini API Integration Test                            ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()

    # Test 1: Direct API call
    api_works = test_gemini()

    if not api_works:
        print()
        print("❌ Gemini API test failed. Fix the API key and try again.")
        sys.exit(1)

    # Test 2: Orchestrator integration
    orch_works = test_orchestrator()

    print()
    print("="*70)
    print("Test Summary")
    print("="*70)
    print(f"Gemini API: {'✅ PASS' if api_works else '❌ FAIL'}")
    print(f"Orchestrator: {'✅ PASS' if orch_works else '❌ FAIL'}")
    print()

    if api_works and orch_works:
        print("🎉 All tests passed! Your AI Employee is ready to use.")
        print()
        print("Next steps:")
        print("  1. Run: python demo.py")
        print("  2. Start: python orchestrator.py --vault ./vault")
        print("  3. Process real emails!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
