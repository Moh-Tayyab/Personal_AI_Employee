#!/usr/bin/env python3
"""
Multi-Provider AI System with Full Claude Code Functionality
Maintains tools, skills, MCP servers across different AI providers
"""

import os
import json
import requests
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

class MultiProviderAI:
    """
    Multi-provider AI system that maintains Claude Code functionality
    across different AI providers (Anthropic, OpenRouter, Gemini, etc.)
    """

    def __init__(self, vault_path: str = "./vault"):
        self.vault_path = Path(vault_path)
        self.config_path = self.vault_path / "config" / "ai_providers.yaml"
        self.quota_path = self.vault_path / "config" / "quota_status.json"

        # Load configuration
        self.load_config()
        self.load_quota_status()

        # Available tools and capabilities (same as Claude Code)
        self.available_tools = [
            "bash", "read", "write", "edit", "glob", "grep",
            "web_search", "web_fetch", "playwright", "agent"
        ]

        # MCP servers (same as Claude Code)
        self.mcp_servers = {
            "email": "mcp/email/server.py",
            "social": "mcp/social/server.py",
            "linkedin": "mcp/linkedin/server.py",
            "twitter": "mcp/twitter/server.py"
        }

        # Skills (same as Claude Code)
        self.skills = {
            "process-emails": ".claude/skills/process-emails/",
            "multi-cli-processor": ".claude/skills/multi-cli-processor/",
            "pdf": ".claude/skills/pdf/",
            "browsing-with-playwright": ".claude/skills/browsing-with-playwright/"
        }

    def load_config(self):
        """Load AI provider configuration"""
        default_config = {
            "providers": {
                "gemini": {
                    "api_key_env": "GEMINI_API_KEY",
                    "model": "gemini-2.5-flash",
                    "max_tokens": 4096,
                    "priority": 1,
                    "supports_tools": True,
                    "supports_thinking": False
                },
                "openrouter": {
                    "api_key_env": "OPENROUTER_API_KEY",
                    "model": "anthropic/claude-3.5-sonnet",
                    "max_tokens": 4000,
                    "priority": 2,
                    "supports_tools": True,
                    "supports_thinking": False
                },
                "openai": {
                    "api_key_env": "OPENAI_API_KEY",
                    "model": "gpt-4o",
                    "max_tokens": 4000,
                    "priority": 3,
                    "supports_tools": True,
                    "supports_thinking": False
                }
            },
            "routing": {
                "simple_tasks": ["gemini", "openrouter", "openai"],
                "code_tasks": ["openai", "openrouter", "gemini"],
                "reasoning_tasks": ["openrouter", "openai", "gemini"],
                "general": ["gemini", "openrouter", "openai"]
            }
        }

        if self.config_path.exists():
            import yaml
            with open(self.config_path) as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = default_config
            self.save_config()

    def save_config(self):
        """Save configuration"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        import yaml
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, indent=2)

    def load_quota_status(self):
        """Load quota status"""
        if self.quota_path.exists():
            with open(self.quota_path) as f:
                self.quota_status = json.load(f)
        else:
            self.quota_status = {
                "gemini": {"exhausted": False, "remaining": 10000},
                "openrouter": {"exhausted": False, "remaining": 2000},
                "openai": {"exhausted": False, "remaining": 1000}
            }

    def get_best_provider(self, task_type: str = "general") -> str:
        """Get best available provider for task type"""
        # Get providers for this task type
        if task_type in self.config["routing"]:
            preferred_providers = self.config["routing"][task_type]
        else:
            preferred_providers = ["anthropic", "openrouter", "gemini"]

        # Find first available provider
        for provider in preferred_providers:
            if not self.quota_status.get(provider, {}).get("exhausted", False):
                api_key = os.getenv(self.config["providers"][provider]["api_key_env"])
                if api_key:
                    return provider

        # Fallback to any available provider
        for provider in self.config["providers"]:
            if not self.quota_status.get(provider, {}).get("exhausted", False):
                api_key = os.getenv(self.config["providers"][provider]["api_key_env"])
                if api_key:
                    return provider

        return None

    def call_anthropic_api(self, messages: list, tools: list = None, thinking: bool = False) -> Tuple[bool, str]:
        """Call Anthropic API with full Claude Code functionality"""
        try:
            import anthropic

            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                return False, "No Anthropic API key"

            client = anthropic.Anthropic(api_key=api_key)

            # Build request
            request_params = {
                "model": "claude-sonnet-4-6",
                "max_tokens": 4096,
                "messages": messages
            }

            # Add tools if provided
            if tools:
                request_params["tools"] = tools

            # Add thinking mode if requested
            if thinking:
                request_params["thinking"] = True

            response = client.messages.create(**request_params)

            return True, response.content[0].text

        except Exception as e:
            if "quota" in str(e).lower():
                self.quota_status["anthropic"]["exhausted"] = True
                self.save_quota_status()
            return False, f"Anthropic error: {str(e)}"

    def call_openrouter_api(self, messages: list, tools: list = None) -> Tuple[bool, str]:
        """Call OpenRouter API with tool support"""
        try:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                return False, "No OpenRouter API key"

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/personal-ai-employee",
                "X-Title": "Personal AI Employee"
            }

            data = {
                "model": "anthropic/claude-3.5-sonnet",
                "messages": messages,
                "max_tokens": 4000
            }

            # Add tools if provided
            if tools:
                data["tools"] = tools

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return True, result['choices'][0]['message']['content']
            else:
                if "quota" in response.text.lower():
                    self.quota_status["openrouter"]["exhausted"] = True
                    self.save_quota_status()
                return False, f"OpenRouter error: {response.status_code}"

        except Exception as e:
            return False, f"OpenRouter exception: {str(e)}"

    def call_openai_api(self, messages: list, tools: list = None) -> Tuple[bool, str]:
        """Call OpenAI API with tool support"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return False, "No OpenAI API key"

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "gpt-4o",
                "messages": messages,
                "max_tokens": 4000,
                "temperature": 0.7
            }

            # Add tools if provided (OpenAI function calling)
            if tools:
                data["tools"] = [{"type": "function", "function": tool} for tool in tools]

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return True, result['choices'][0]['message']['content']
            else:
                if "quota" in response.text.lower() or "limit" in response.text.lower():
                    self.quota_status["openai"]["exhausted"] = True
                    self.save_quota_status()
                return False, f"OpenAI error: {response.status_code}"

        except Exception as e:
            return False, f"OpenAI exception: {str(e)}"

    def call_gemini_api(self, messages: list, tools: list = None) -> Tuple[bool, str]:
        """Call Gemini API with tool support"""
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return False, "No Gemini API key"

            # Convert messages to Gemini format
            prompt = "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "maxOutputTokens": 4096,
                    "temperature": 0.7
                }
            }

            # Add tools if provided (Gemini function calling)
            if tools:
                data["tools"] = [{"functionDeclarations": tools}]

            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return True, result['candidates'][0]['content']['parts'][0]['text']
            else:
                if "quota" in response.text.lower():
                    self.quota_status["gemini"]["exhausted"] = True
                    self.save_quota_status()
                return False, f"Gemini error: {response.status_code}"

        except Exception as e:
            return False, f"Gemini exception: {str(e)}"

    def process_with_tools(self, prompt: str, task_type: str = "general",
                          use_tools: bool = True, thinking: bool = False) -> Tuple[str, str]:
        """
        Process prompt with full Claude Code functionality:
        - Tools (bash, read, write, etc.)
        - MCP servers
        - Skills
        - Thinking mode
        """

        # Get best provider
        provider = self.get_best_provider(task_type)
        if not provider:
            return "none", "No providers available"

        # Build messages
        messages = [
            {
                "role": "system",
                "content": f"""You are Claude Code running in a Personal AI Employee system.

You have access to all Claude Code tools and capabilities:
- Tools: {', '.join(self.available_tools)}
- MCP Servers: {', '.join(self.mcp_servers.keys())}
- Skills: {', '.join(self.skills.keys())}

Current provider: {provider}
Task type: {task_type}
Tools enabled: {use_tools}
Thinking mode: {thinking}

Process the user's request using appropriate tools and capabilities."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Build tools list (if supported) - TEMPORARILY DISABLED FOR DEBUGGING
        tools = None
        # TODO: Fix tools format conversion for different providers
        # For now, disable tools to get basic AI processing working
        if False and use_tools and self.config["providers"][provider].get("supports_tools", False):
            tools = [
                {
                    "name": "bash",
                    "description": "Execute bash commands",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string"}
                        }
                    }
                },
                {
                    "name": "read_file",
                    "description": "Read file contents",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"}
                        }
                    }
                },
                {
                    "name": "write_file",
                    "description": "Write file contents",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "content": {"type": "string"}
                        }
                    }
                }
                # Add more tools as needed
            ]

        # Call appropriate API
        if provider == "gemini":
            success, result = self.call_gemini_api(messages, tools)
        elif provider == "openrouter":
            success, result = self.call_openrouter_api(messages, tools)
        elif provider == "openai":
            success, result = self.call_openai_api(messages, tools)
        else:
            return "none", f"Unknown provider: {provider}"

        if success:
            return provider, result
        else:
            # Try fallback provider
            fallback_provider = self.get_best_provider("general")
            if fallback_provider and fallback_provider != provider:
                print(f"🔄 {provider} failed, trying {fallback_provider}...")
                if fallback_provider == "gemini":
                    success, result = self.call_gemini_api(messages, tools)
                elif fallback_provider == "openrouter":
                    success, result = self.call_openrouter_api(messages, tools)
                elif fallback_provider == "openai":
                    success, result = self.call_openai_api(messages, tools)

                if success:
                    return fallback_provider, result

            return "none", result

    def save_quota_status(self):
        """Save quota status"""
        self.quota_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.quota_path, 'w') as f:
            json.dump(self.quota_status, f, indent=2)

    def get_status(self) -> Dict:
        """Get comprehensive status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "providers": {
                provider: {
                    "available": not self.quota_status.get(provider, {}).get("exhausted", False),
                    "api_key_set": bool(os.getenv(config["api_key_env"])),
                    "supports_tools": config.get("supports_tools", False),
                    "supports_thinking": config.get("supports_thinking", False)
                }
                for provider, config in self.config["providers"].items()
            },
            "tools_available": self.available_tools,
            "mcp_servers": list(self.mcp_servers.keys()),
            "skills": list(self.skills.keys())
        }

if __name__ == "__main__":
    import sys

    ai = MultiProviderAI()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            status = ai.get_status()
            print(json.dumps(status, indent=2))
        elif sys.argv[1] == "--test":
            # Test with thinking mode
            provider, result = ai.process_with_tools(
                "Create a simple Python function to add two numbers",
                task_type="code",
                use_tools=True,
                thinking=True
            )
            print(f"Used provider: {provider}")
            print(f"Result: {result}")
        elif sys.argv[1] == "--process" and len(sys.argv) > 2:
            prompt = sys.argv[2]
            provider, result = ai.process_with_tools(prompt)
            print(f"Used provider: {provider}")
            print(f"Result: {result}")
    else:
        print("Usage: python multi_provider_ai.py [--status|--test|--process 'prompt']")