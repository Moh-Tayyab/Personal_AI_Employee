#!/usr/bin/env python3
"""
Multi-CLI Manager for Personal AI Employee
Handles Claude, Qwen, and Codex CLI calls with Windows/Linux compatibility
"""

import subprocess
import platform
import json
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple
from quota_manager import QuotaManager

class MultiCLIManager:
    def __init__(self, vault_path: str = "./vault"):
        self.vault_path = Path(vault_path)
        self.is_windows = platform.system() == "Windows"
        self.quota_manager = QuotaManager(vault_path)
        self.setup_cli_commands()

    def setup_cli_commands(self):
        """Setup CLI commands based on operating system"""
        if self.is_windows:
            self.claude_cmd = "claude.exe"
            self.qwen_cmd = "qwen.exe"
            self.codex_cmd = "gh.exe"
            self.shell = True
        else:
            self.claude_cmd = "claude"
            self.qwen_cmd = "qwen"
            self.codex_cmd = "gh"
            self.shell = False

    def call_claude(self, prompt: str, context: str = "", max_tokens: int = 4000) -> Tuple[bool, str]:
        """Call Claude CLI with prompt"""
        try:
            # Check quota first
            if not self.quota_manager.check_claude_quota():
                return False, "Claude quota exhausted"

            # Handle nested Claude session issue
            if "Claude Code cannot be launched inside another Claude Code session" in str(subprocess.run([self.claude_cmd, "--version"], capture_output=True, text=True).stderr):
                return False, "Cannot run Claude CLI inside Claude Code session - use API fallback"

            # Create temporary file for long prompts
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                full_prompt = f"{context}\n\n{prompt}" if context else prompt
                f.write(full_prompt)
                temp_file = f.name

            # Use simpler Claude CLI command structure
            cmd = [self.claude_cmd, "--file", temp_file]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                shell=self.shell
            )

            # Clean up temp file
            Path(temp_file).unlink(missing_ok=True)

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                error_msg = result.stderr.strip()
                # Handle nested session specifically
                if "cannot be launched inside another" in error_msg.lower():
                    return False, "Nested Claude session detected - use API fallback"
                # Check if quota-related error
                if any(word in error_msg.lower() for word in ["quota", "limit", "exceeded"]):
                    self.quota_manager.quota_data["claude"]["exhausted"] = True
                    self.quota_manager.save_quota_status()
                return False, f"Claude error: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Claude timeout"
        except Exception as e:
            return False, f"Claude exception: {str(e)}"

    def call_qwen(self, prompt: str, context: str = "", max_tokens: int = 2000) -> Tuple[bool, str]:
        """Call Qwen CLI with prompt"""
        try:
            # Qwen CLI has different command structure
            full_prompt = f"{context}\n\n{prompt}" if context else prompt

            # Try different Qwen CLI command patterns
            cmd_patterns = [
                # Pattern 1: Standard chat
                [self.qwen_cmd, "chat", "--prompt", full_prompt],
                # Pattern 2: Direct prompt
                [self.qwen_cmd, "--prompt", full_prompt],
                # Pattern 3: Interactive mode with input
                [self.qwen_cmd, "ask", full_prompt],
                # Pattern 4: Simple command
                [self.qwen_cmd, full_prompt]
            ]

            for cmd in cmd_patterns:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        shell=self.shell
                    )

                    if result.returncode == 0 and result.stdout.strip():
                        return True, result.stdout.strip()
                    elif "Unknown arguments" not in result.stderr:
                        # If it's not a command structure issue, break and report error
                        break

                except subprocess.TimeoutExpired:
                    return False, "Qwen timeout"
                except Exception:
                    continue

            # If all patterns failed, return the last error
            return False, f"Qwen error: {result.stderr.strip() if 'result' in locals() else 'All command patterns failed'}"

        except Exception as e:
            return False, f"Qwen exception: {str(e)}"

    def call_codex(self, prompt: str, task_type: str = "general", language: str = "python") -> Tuple[bool, str]:
        """Call GitHub Copilot CLI with prompt"""
        try:
            # Check quota first
            if not self.quota_manager.check_codex_quota():
                return False, "Codex quota exhausted"

            # Check if GitHub Copilot CLI is actually installed
            check_cmd = [self.codex_cmd, "copilot", "--version"]
            check_result = subprocess.run(check_cmd, capture_output=True, text=True, shell=self.shell)

            if check_result.returncode != 0:
                return False, "GitHub Copilot CLI not installed. Install with: gh extension install github/gh-copilot"

            # Different command patterns based on task type
            if task_type == "code" or "code" in prompt.lower():
                # For code generation
                cmd = [self.codex_cmd, "copilot", "suggest", prompt]
            else:
                # For explanations and general tasks
                cmd = [self.codex_cmd, "copilot", "explain", prompt]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                shell=self.shell
            )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                error_msg = result.stderr.strip()
                if any(word in error_msg.lower() for word in ["quota", "limit", "exceeded"]):
                    self.quota_manager.quota_data["codex"]["exhausted"] = True
                    self.quota_manager.save_quota_status()
                return False, f"Codex error: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Codex timeout"
        except Exception as e:
            return False, f"Codex exception: {str(e)}"

    def determine_task_type(self, content: str) -> str:
        """Determine task type from content"""
        content_lower = content.lower()

        # Code-related keywords
        code_keywords = [
            "function", "class", "def ", "import", "from ", "return",
            "if __name__", "#!/", "```python", "```javascript", "```bash",
            "debug", "error", "exception", "traceback", "syntax"
        ]

        # Reasoning-related keywords
        reasoning_keywords = [
            "analyze", "plan", "strategy", "decision", "approve", "reject",
            "consider", "evaluate", "assess", "recommend", "suggest"
        ]

        # Simple processing keywords
        simple_keywords = [
            "extract", "summarize", "list", "count", "find", "search",
            "format", "convert", "translate"
        ]

        if any(keyword in content_lower for keyword in code_keywords):
            return "code"
        elif any(keyword in content_lower for keyword in reasoning_keywords):
            return "reasoning"
        elif any(keyword in content_lower for keyword in simple_keywords):
            return "simple"
        else:
            return "general"

    def process_with_best_cli(self, prompt: str, context: str = "") -> Tuple[str, str]:
        """Process with the best available CLI"""
        task_type = self.determine_task_type(prompt + " " + context)

        # Get recommended CLI order based on task type
        cli_order = self.get_cli_priority(task_type)

        for cli_name in cli_order:
            print(f"🔄 Trying {cli_name}...")

            success, result = self.call_cli(cli_name, prompt, context, task_type)

            if success:
                print(f"✅ Success with {cli_name}")
                return cli_name, result
            else:
                print(f"❌ {cli_name} failed: {result}")
                continue

        # All failed
        return "none", "All CLIs failed"

    def get_cli_priority(self, task_type: str) -> list:
        """Get CLI priority order based on task type"""
        if task_type == "code":
            return ["codex", "claude", "qwen"]
        elif task_type == "reasoning":
            return ["claude", "qwen", "codex"]
        elif task_type == "simple":
            return ["qwen", "claude", "codex"]
        else:
            # General tasks - use availability-based priority
            best_cli = self.quota_manager.get_best_available_cli()
            all_clis = ["claude", "qwen", "codex"]
            # Put best CLI first, others follow
            priority = [best_cli] + [cli for cli in all_clis if cli != best_cli]
            return priority

    def call_cli(self, cli_name: str, prompt: str, context: str, task_type: str) -> Tuple[bool, str]:
        """Call specific CLI"""
        if cli_name == "claude":
            return self.call_claude(prompt, context)
        elif cli_name == "qwen":
            return self.call_qwen(prompt, context)
        elif cli_name == "codex":
            return self.call_codex(prompt, task_type)
        else:
            return False, f"Unknown CLI: {cli_name}"

    def get_status(self) -> Dict:
        """Get status of all CLIs"""
        return {
            "platform": platform.system(),
            "quota_status": self.quota_manager.get_status_report(),
            "cli_commands": {
                "claude": self.claude_cmd,
                "qwen": self.qwen_cmd,
                "codex": self.codex_cmd
            }
        }

if __name__ == "__main__":
    import sys

    manager = MultiCLIManager()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            status = manager.get_status()
            print(json.dumps(status, indent=2))
        elif sys.argv[1] == "--test":
            # Test all CLIs
            test_prompt = "Hello, please respond with 'CLI working'"

            print("Testing Claude...")
            success, result = manager.call_claude(test_prompt)
            print(f"Claude: {'✅' if success else '❌'} {result[:100]}")

            print("\nTesting Qwen...")
            success, result = manager.call_qwen(test_prompt)
            print(f"Qwen: {'✅' if success else '❌'} {result[:100]}")

            print("\nTesting Codex...")
            success, result = manager.call_codex(test_prompt)
            print(f"Codex: {'✅' if success else '❌'} {result[:100]}")

        elif sys.argv[1] == "--process" and len(sys.argv) > 2:
            prompt = sys.argv[2]
            cli_used, result = manager.process_with_best_cli(prompt)
            print(f"Used CLI: {cli_used}")
            print(f"Result: {result}")
    else:
        print("Usage: python multi_cli_manager.py [--status|--test|--process 'prompt']")