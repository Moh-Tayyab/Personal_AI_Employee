#!/usr/bin/env python3
"""
Ollama Integration for AI Employee

Free, local LLM integration using Ollama (runs on 4GB RAM)

Usage:
    python3 scripts/ollama_integration.py
"""

import json
import requests
from pathlib import Path

# Ollama API endpoint
OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"  # Lightweight model for 4GB RAM


def check_ollama():
    """Check if Ollama is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
            models = response.json().get('models', [])
            print(f"   Available models: {[m['name'] for m in models]}")
            return True
        else:
            print("❌ Ollama API returned error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama is not running. Start with: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False


def query_ollama(prompt: str, system_prompt: str = None) -> str:
    """
    Query Ollama LLM.
    
    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
    
    Returns:
        Generated response text
    """
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "max_tokens": 500
        }
    }
    
    if system_prompt:
        payload["system"] = system_prompt
    
    try:
        response = requests.post(OLLAMA_API, json=payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '')
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


def process_email(email_content: str) -> dict:
    """
    Process email and determine response.
    
    Args:
        email_content: Email content to process
    
    Returns:
        Dictionary with priority, category, and response
    """
    system_prompt = """You are an AI email assistant. Analyze emails and provide:
1. Priority: urgent, high, normal, or low
2. Category: invoice, meeting, support, sales, personal, legal, spam
3. Suggested response (brief and professional)

Respond in JSON format:
{
  "priority": "normal",
  "category": "general",
  "response": "Thank you for your email..."
}"""
    
    response = query_ollama(
        f"Analyze this email:\n\n{email_content}",
        system_prompt
    )
    
    try:
        # Try to parse JSON from response
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except:
        pass
    
    # Default response if parsing fails
    return {
        "priority": "normal",
        "category": "general",
        "response": "Thank you for your email. I will review and respond shortly."
    }


def test_ollama():
    """Test Ollama integration."""
    print("=" * 60)
    print("Testing Ollama Integration")
    print("=" * 60)
    print()
    
    if not check_ollama():
        print("\n❌ Ollama is not available. Please:")
        print("   1. Start Ollama: ollama serve")
        print("   2. Pull model: ollama pull llama3.2:3b")
        return False
    
    print("\n📝 Testing with simple query...")
    response = query_ollama("Hello! Who are you?")
    print(f"Response: {response[:200]}...")
    
    print("\n📧 Testing email processing...")
    test_email = """
    Subject: Meeting Tomorrow
    From: john@example.com
    
    Hi,
    
    Can we meet tomorrow at 2 PM to discuss the project?
    
    Thanks,
    John
    """
    
    result = process_email(test_email)
    print(f"Priority: {result.get('priority', 'unknown')}")
    print(f"Category: {result.get('category', 'unknown')}")
    print(f"Response: {result.get('response', '')[:100]}...")
    
    print("\n✅ Ollama integration test complete!")
    return True


if __name__ == "__main__":
    test_ollama()
