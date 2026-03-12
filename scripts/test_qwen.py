#!/usr/bin/env python3
"""
Test Qwen3.5 API Integration

Usage:
    python3 scripts/test_qwen.py
    or simply: qwen-test
"""

import os
import json
import requests

# System-wide environment variables (from ~/.bashrc or qwen-ccr.sh)
QWEN_MODEL = os.getenv('QWEN_MODEL', 'qwen/qwen-2.5-72b-instruct')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')

print("=" * 60)
print("🧪 QWEN3.5 API TEST")
print("=" * 60)
print()

# Check for API keys
dashscope_key = os.getenv('DASHSCOPE_API_KEY', '')
openrouter_key = os.getenv('OPENROUTER_API_KEY', '')

if not dashscope_key and not openrouter_key:
    print("❌ No API key found!")
    print()
    print("Please set one of these in your .env file:")
    print()
    print("Option 1: Alibaba DashScope (FREE Qwen tier)")
    print("  DASHSCOPE_API_KEY=sk-your-key-here")
    print("  Get key from: https://dashscope.console.aliyun.com/")
    print()
    print("Option 2: OpenRouter (FREE Qwen-72B)")
    print("  OPENROUTER_API_KEY=sk-your-key-here")
    print("  Get key from: https://openrouter.ai/")
    print()
    exit(1)

# Test DashScope
if dashscope_key:
    print("Testing DashScope (Alibaba Cloud)...")
    try:
        import dashscope
        
        dashscope.api_key = dashscope_key
        
        response = dashscope.Generation.call(
            model='qwen-plus',
            prompt='Say hello in one sentence'
        )
        
        if response.status_code == 200:
            print("✅ DashScope connected!")
            print(f"   Response: {response.output.text}")
        else:
            print(f"❌ DashScope error: {response.code}")
            print(f"   {response.message}")
            
    except ImportError:
        print("⚠️  dashscope package not installed")
        print("   Install with: pip install dashscope")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

# Test OpenRouter
if openrouter_key:
    print("Testing OpenRouter...")
    try:
        import requests
        
        headers = {
            'Authorization': f'Bearer {openrouter_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': QWEN_MODEL,
            'messages': [
                {'role': 'user', 'content': 'Say hello in one sentence'}
            ]
        }
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print("✅ OpenRouter connected!")
            print(f"   Response: {message}")
            print(f"   Model: {result['model']}")
        else:
            print(f"❌ OpenRouter error: {response.status_code}")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

print("=" * 60)
print("✅ TEST COMPLETE")
print("=" * 60)
