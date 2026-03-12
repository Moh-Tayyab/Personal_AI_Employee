#!/usr/bin/env python3
"""
Qwen-Claude Bridge

Connects Qwen3.5 API (backend LLM) with Claude Code (interface)

Usage:
    python3 scripts/qwen_claude_bridge.py
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

# Configuration - Uses system-wide environment variables
VAULT_PATH = Path(os.getenv('QWEN_PROJECT', './')) / 'vault'
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
QWEN_MODEL = os.getenv('QWEN_MODEL', 'qwen/qwen-2.5-72b-instruct')


def analyze_email_with_qwen(email_text: str) -> dict:
    """
    Analyze email using Qwen3.5 API.
    
    Returns:
        dict: {priority, category, response}
    """
    
    prompt = f"""You are an AI email assistant. Analyze this email and provide:
1. Priority: urgent, high, normal, or low
2. Category: finance, calendar, career, general, or spam  
3. A brief professional response (2-3 sentences)

Email to analyze:
---
{email_text}
---

Respond in JSON format only:
{{
  "priority": "normal",
  "category": "general",
  "response": "Thank you for your email..."
}}"""

    # Try OpenRouter first (FREE Qwen-72B)
    if OPENROUTER_API_KEY:
        try:
            headers = {
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': QWEN_MODEL,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': float(os.getenv('QWEN_TEMPERATURE', '0.7')),
                'max_tokens': int(os.getenv('QWEN_MAX_TOKENS', '500'))
            }
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse JSON
                import re
                json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                    
        except Exception as e:
            print(f"OpenRouter failed: {e}")
    
    # Fallback to DashScope
    if DASHSCOPE_API_KEY:
        try:
            import dashscope
            dashscope.api_key = DASHSCOPE_API_KEY
            
            response = dashscope.Generation.call(
                model='qwen-plus',
                prompt=prompt
            )
            
            if response.status_code == 200:
                content = response.output.text
                import re
                json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                    
        except Exception as e:
            print(f"DashScope failed: {e}")
    
    # Default fallback
    return {
        'priority': 'normal',
        'category': 'general',
        'response': 'Thank you for your email. I will respond shortly.'
    }


def process_email_file(email_path: Path) -> dict:
    """Process an email file and generate response."""
    
    print(f"Processing: {email_path.name}")
    
    # Read email
    content = email_path.read_text()
    
    # Analyze with Qwen
    print("  Analyzing with Qwen3.5...")
    analysis = analyze_email_with_qwen(content)
    
    # Save analysis
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    analysis_dir = VAULT_PATH / 'Analysis'
    analysis_dir.mkdir(parents=True, exist_ok=True)
    
    analysis_file = analysis_dir / f'QWEN_{timestamp}.json'
    with open(analysis_file, 'w') as f:
        json.dump({
            'email_file': str(email_path),
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis
        }, f, indent=2)
    
    print(f"  Analysis saved: {analysis_file}")
    
    # Create draft reply
    draft_dir = VAULT_PATH / 'Drafts'
    draft_dir.mkdir(parents=True, exist_ok=True)
    
    draft_file = draft_dir / f'QWEN_REPLY_{timestamp}.md'
    draft_content = f"""---
Type: AI Auto-Reply (Qwen3.5)
Priority: {analysis.get('priority', 'normal')}
Category: {analysis.get('category', 'general')}
Generated: {datetime.now().isoformat()}
Model: Qwen-2.5-72B-Instruct
---

# AI-Generated Email Response

{analysis.get('response', 'No response generated')}

---
Powered by Qwen3.5 via Claude Code Integration
"""
    draft_file.write_text(draft_content)
    print(f"  Draft created: {draft_file}")
    
    return analysis


def main():
    """Main function."""
    print("=" * 60)
    print("🤖 QWEN-CLAUDE BRIDGE")
    print("=" * 60)
    print()
    
    # Check API keys
    if not DASHSCOPE_API_KEY and not OPENROUTER_API_KEY:
        print("❌ No API key found!")
        print()
        print("Add to .env file:")
        print("  DASHSCOPE_API_KEY=sk-...  (https://dashscope.console.aliyun.com/)")
        print("  OR")
        print("  OPENROUTER_API_KEY=sk-...  (https://openrouter.ai/)")
        return
    
    print("✅ API Keys configured")
    print()
    
    # Check for emails to process
    needs_action = VAULT_PATH / 'Needs_Action'
    if not needs_action.exists():
        print("⚠️  Needs_Action folder not found")
        return
    
    email_files = list(needs_action.glob('EMAIL_*.md'))
    
    if not email_files:
        print("ℹ️  No emails to process")
        return
    
    print(f"📧 Found {len(email_files)} emails to process")
    print()
    
    # Process each email
    for email_file in email_files[:5]:  # Process max 5 at a time
        try:
            result = process_email_file(email_file)
            print(f"  Priority: {result.get('priority')}")
            print(f"  Category: {result.get('category')}")
            print()
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()
    
    print("=" * 60)
    print("✅ PROCESSING COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
