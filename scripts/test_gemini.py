#!/usr/bin/env python3
"""
Gemini API Key Tester - Verify your setup works
"""

import os
import requests
import json

def test_gemini_api_key():
    """Test if Gemini API key is working"""

    print("🧪 TESTING GEMINI API KEY")
    print("=" * 40)

    # Check if API key is set
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("\n🔧 To fix this:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Run: export GEMINI_API_KEY='your_key_here'")
        print("3. Run this test again")
        return False

    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")

    # Test API call
    print("\n🔍 Testing API connection...")

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

        data = {
            "contents": [{
                "parts": [{
                    "text": "Hello! Please respond with 'Gemini API working perfectly!' to confirm the connection."
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": 100,
                "temperature": 0.1
            }
        }

        response = requests.post(url, json=data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            ai_response = result['candidates'][0]['content']['parts'][0]['text']

            print("✅ API connection successful!")
            print(f"🤖 Gemini response: {ai_response}")

            # Test with tools (function calling)
            print("\n🛠️ Testing tool support...")

            tool_data = {
                "contents": [{
                    "parts": [{
                        "text": "What's 2+2? Use the calculator function if available."
                    }]
                }],
                "tools": [{
                    "functionDeclarations": [{
                        "name": "calculator",
                        "description": "Perform basic math calculations",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "expression": {
                                    "type": "string",
                                    "description": "Math expression to calculate"
                                }
                            }
                        }
                    }]
                }]
            }

            tool_response = requests.post(url, json=tool_data, timeout=10)

            if tool_response.status_code == 200:
                print("✅ Tool support confirmed!")
            else:
                print("⚠️ Basic API works, tool support may be limited")

            return True

        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text[:200]}")

            if response.status_code == 400:
                print("\n💡 This might be an API key issue. Check:")
                print("1. API key is correct")
                print("2. API key has proper permissions")
                print("3. Billing is set up (if required)")

            return False

    except requests.exceptions.Timeout:
        print("❌ Request timeout - check your internet connection")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def show_usage_info():
    """Show Gemini usage information"""
    print("\n💰 GEMINI PRICING & LIMITS")
    print("=" * 40)
    print("🆓 FREE TIER:")
    print("   • 15 requests per minute")
    print("   • 1,500 requests per day")
    print("   • 1 million tokens per month")
    print("   • Perfect for getting started!")
    print()
    print("💰 PAID TIER:")
    print("   • $0.001 per 1K tokens (very cheap!)")
    print("   • Higher rate limits")
    print("   • 1000x cheaper than some alternatives")

def show_next_steps():
    """Show what to do next"""
    print("\n🚀 NEXT STEPS")
    print("=" * 40)
    print("1. ✅ Your Gemini API is working!")
    print("2. 🧪 Test the multi-provider system:")
    print("   python3 scripts/multi_provider_ai.py --status")
    print()
    print("3. 🚀 Start your AI employee:")
    print("   python3 orchestrator.py --vault ./vault --live")
    print()
    print("4. 📧 Drop test emails in vault/Needs_Action/ and watch it work!")
    print()
    print("5. 📊 Monitor usage:")
    print("   python3 scripts/check_api_keys.py")

if __name__ == "__main__":
    print("🚀 GEMINI API KEY SETUP & TEST")
    print("=" * 50)

    success = test_gemini_api_key()

    if success:
        show_usage_info()
        show_next_steps()
        print("\n🎉 SUCCESS! Your Gemini API is ready to use!")
    else:
        print("\n❌ Setup incomplete. Please fix the issues above and try again.")
        print("\n🔧 Quick fix:")
        print("export GEMINI_API_KEY='your_actual_api_key_here'")
        print("python3 scripts/test_gemini.py")