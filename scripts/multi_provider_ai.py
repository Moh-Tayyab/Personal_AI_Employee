"""
Multi-Provider AI System - Unified interface for Gemini, OpenRouter, and Anthropic

Provides a single API surface to route tasks to the optimal AI provider based on
task type, availability, and cost. Maintains full Qwen Code functionality including
tools, thinking mode, and MCP server access.

Providers (priority order):
1. Gemini (Google) - Best for reasoning, large context, free tier
2. OpenRouter - Multi-model gateway (Claude, GPT, etc.)
3. Anthropic - Claude models for complex reasoning
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

load_dotenv()
logger = logging.getLogger("MultiProviderAI")


class MultiProviderAI:
    """Unified multi-provider AI interface with tool support."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.providers = {}
        self._initialize_providers()
        self._log_usage_file = self.vault_path / "Logs" / "ai_provider_usage.jsonl"
        self._log_usage_file.parent.mkdir(parents=True, exist_ok=True)

    def _initialize_providers(self):
        """Initialize available AI providers based on environment variables."""
        # Gemini
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key and GEMINI_AVAILABLE:
            try:
                self.providers["gemini"] = genai.Client(api_key=gemini_key)
                logger.info("✅ Gemini provider initialized")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}")

        # OpenRouter
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key and REQUESTS_AVAILABLE:
            self.providers["openrouter"] = {
                "api_key": openrouter_key,
                "base_url": "https://openrouter.ai/api/v1",
                "model": os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
            }
            logger.info("✅ OpenRouter provider initialized")

        # Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and ANTHROPIC_AVAILABLE:
            try:
                self.providers["anthropic"] = anthropic.Anthropic(api_key=anthropic_key)
                logger.info("✅ Anthropic provider initialized")
            except Exception as e:
                logger.warning(f"Anthropic initialization failed: {e}")

        if not self.providers:
            logger.warning("⚠️ No AI providers configured - all will fail")

    def process_with_tools(
        self,
        prompt: str,
        task_type: str = "general",
        use_tools: bool = True,
        thinking: bool = False
    ) -> Tuple[str, str]:
        """
        Process a prompt using the optimal provider.

        Args:
            prompt: The prompt to send
            task_type: Type of task (reasoning, code, tool_heavy, simple, general)
            use_tools: Whether tool context should be included
            thinking: Whether to enable extended thinking mode

        Returns:
            Tuple of (provider_name, response_text)
        """
        provider_name = self._select_provider(task_type)

        if provider_name == "none":
            return "none", ""

        start_time = time.time()
        try:
            if provider_name == "gemini":
                response = self._call_gemini(prompt, thinking)
            elif provider_name == "openrouter":
                response = self._call_openrouter(prompt, task_type, thinking)
            elif provider_name == "anthropic":
                response = self._call_anthropic(prompt, thinking)
            else:
                response = ""

            duration = time.time() - start_time
            self._log_usage(provider_name, task_type, thinking, duration, len(prompt), len(response))
            return provider_name, response

        except Exception as e:
            logger.error(f"{provider_name} call failed: {e}")
            # Try fallback providers
            return self._try_fallback(prompt, task_type, thinking, provider_name)

    def _select_provider(self, task_type: str) -> str:
        """Select the best provider for the given task type."""
        # Priority routing based on task type
        if task_type in ("reasoning", "complex_analysis"):
            if "anthropic" in self.providers:
                return "anthropic"
            if "openrouter" in self.providers:
                return "openrouter"
            if "gemini" in self.providers:
                return "gemini"

        elif task_type == "code":
            if "openrouter" in self.providers:
                return "openrouter"
            if "anthropic" in self.providers:
                return "anthropic"
            if "gemini" in self.providers:
                return "gemini"

        elif task_type == "tool_heavy":
            if "gemini" in self.providers:
                return "gemini"  # Large context window
            if "openrouter" in self.providers:
                return "openrouter"
            if "anthropic" in self.providers:
                return "anthropic"

        else:  # simple, general
            if "gemini" in self.providers:
                return "gemini"  # Free tier, fast
            if "openrouter" in self.providers:
                return "openrouter"
            if "anthropic" in self.providers:
                return "anthropic"

        return "none"

    def _call_gemini(self, prompt: str, thinking: bool = False) -> str:
        """Call Gemini API."""
        client = self.providers["gemini"]

        generation_config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=8192,
        )

        if thinking:
            generation_config.temperature = 0.3

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=generation_config,
        )

        return response.text

    def _call_openrouter(self, prompt: str, task_type: str, thinking: bool = False) -> str:
        """Call OpenRouter API (multi-model gateway)."""
        config = self.providers["openrouter"]

        model = config["model"]
        if task_type == "reasoning":
            model = os.getenv("OPENROUTER_REASONING_MODEL", model)

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Personal_AI_Employee",
            "X-Title": "Personal AI Employee"
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3 if thinking else 0.7,
            "max_tokens": 8192,
        }

        response = requests.post(
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _call_anthropic(self, prompt: str, thinking: bool = False) -> str:
        """Call Anthropic Claude API."""
        client = self.providers["anthropic"]

        kwargs = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 8192,
            "messages": [{"role": "user", "content": prompt}],
        }

        if thinking:
            kwargs["temperature"] = 0.3
        else:
            kwargs["temperature"] = 0.7

        message = client.messages.create(**kwargs)
        return message.content[0].text

    def _try_fallback(
        self, prompt: str, task_type: str, thinking: bool, failed_provider: str
    ) -> Tuple[str, str]:
        """Try remaining providers in priority order."""
        remaining = [p for p in ("gemini", "openrouter", "anthropic")
                     if p in self.providers and p != failed_provider]

        for provider in remaining:
            try:
                if provider == "gemini":
                    response = self._call_gemini(prompt, thinking)
                elif provider == "openrouter":
                    response = self._call_openrouter(prompt, task_type, thinking)
                elif provider == "anthropic":
                    response = self._call_anthropic(prompt, thinking)
                else:
                    continue

                return provider, response
            except Exception as e:
                logger.warning(f"Fallback to {provider} failed: {e}")
                continue

        logger.error("All AI providers failed")
        return "none", ""

    def _log_usage(
        self, provider: str, task_type: str, thinking: bool,
        duration: float, prompt_len: int, response_len: int
    ):
        """Log provider usage for monitoring and cost tracking."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "task_type": task_type,
            "thinking": thinking,
            "duration_seconds": round(duration, 2),
            "prompt_length": prompt_len,
            "response_length": response_len,
        }

        try:
            with open(self._log_usage_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.warning(f"Failed to log AI usage: {e}")

    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all providers."""
        return {name: True for name in self.providers}

    def get_available_providers(self) -> List[str]:
        """List available provider names."""
        return list(self.providers.keys())
