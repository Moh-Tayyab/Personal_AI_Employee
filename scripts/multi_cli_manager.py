"""
Multi-CLI Manager - Routes tasks between multiple CLI instances

Manages routing of tasks between different CLI tools (Qwen Code, Claude Code,
Codex CLI) based on availability, quota status, and task type. Provides automatic
fallback when a CLI is unavailable or quota-exhausted.

CLIs managed:
- qwen (Qwen Code) - Primary reasoning engine
- claude (Claude Code) - Backup for complex reasoning
- codex (OpenAI Codex CLI) - Backup for code tasks
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("MultiCLIManager")


class MultiCLIManager:
    """Manages multiple CLI instances with routing and fallback."""

    # CLI configuration
    CLI_COMMANDS = {
        "qwen": {
            "command": "qwen",
            "args": ["--prompt"],
            "env_vars": ["QWEN_API_KEY", "OPENAI_API_KEY"],
            "max_tokens": 8192,
            "timeout": 300,
        },
        "claude": {
            "command": "claude",
            "args": ["-p"],
            "env_vars": ["ANTHROPIC_API_KEY"],
            "max_tokens": 8192,
            "timeout": 300,
        },
        "codex": {
            "command": "codex",
            "args": ["-p"],
            "env_vars": ["OPENAI_API_KEY"],
            "max_tokens": 4096,
            "timeout": 180,
        },
    }

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.available_clis = {}
        self._detect_available_clis()
        self._log_dir = self.vault_path / "Logs" / "cli_usage"
        self._log_dir.mkdir(parents=True, exist_ok=True)

    def _detect_available_clis(self):
        """Detect which CLI tools are installed and configured."""
        for name, config in self.CLI_COMMANDS.items():
            # Check if command exists in PATH
            cmd_exists = self._command_exists(config["command"])

            # Check if environment variables are set
            has_credentials = any(os.getenv(var) for var in config["env_vars"])

            if cmd_exists and has_credentials:
                self.available_clis[name] = {
                    "command": config["command"],
                    "status": "available",
                    "last_used": None,
                    "call_count": 0,
                }
                logger.info(f"✅ {name} CLI detected and configured")
            else:
                logger.debug(
                    f"❌ {name} CLI unavailable: "
                    f"command={'yes' if cmd_exists else 'no'}, "
                    f"creds={'yes' if has_credentials else 'no'}"
                )

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        try:
            subprocess.run(
                ["which", command],
                capture_output=True,
                check=True,
                timeout=5,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def select_cli(self, task_type: str = "general") -> Optional[str]:
        """
        Select the best CLI for the given task type.

        Priority: qwen > claude > codex (with task-type adjustments)
        """
        # For code tasks, prefer codex if available
        if task_type == "code" and "codex" in self.available_clis:
            return "codex"

        # Default: use first available in priority order
        for cli_name in ("qwen", "claude", "codex"):
            if cli_name in self.available_clis:
                return cli_name

        return None

    def run_prompt(
        self,
        prompt: str,
        task_type: str = "general",
        working_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run a prompt through the best available CLI.

        Args:
            prompt: The prompt to execute
            task_type: Type of task for CLI selection
            working_dir: Working directory for the CLI process

        Returns:
            Dict with success, output, cli_used, duration
        """
        selected_cli = self.select_cli(task_type)

        if not selected_cli:
            logger.error("No CLI instances available")
            return {
                "success": False,
                "output": "",
                "cli_used": "none",
                "duration": 0,
                "error": "No CLI available",
            }

        return self._run_with_cli(selected_cli, prompt, working_dir)

    def _run_with_cli(
        self,
        cli_name: str,
        prompt: str,
        working_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute prompt using a specific CLI."""
        config = self.CLI_COMMANDS[cli_name]
        cwd = working_dir or str(self.vault_path)

        cmd = [config["command"]] + config["args"] + [prompt]

        env = os.environ.copy()
        env["CLAUDE_CODE"] = "1" if cli_name == "claude" else env.get("CLAUDE_CODE", "")

        start_time = datetime.now()
        try:
            logger.info(f"🚀 Running prompt via {cli_name} CLI (timeout={config['timeout']}s)")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config["timeout"],
                cwd=cwd,
                env=env,
            )

            duration = (datetime.now() - start_time).total_seconds()
            output = result.stdout

            # Update stats
            self.available_clis[cli_name]["last_used"] = datetime.now().isoformat()
            self.available_clis[cli_name]["call_count"] += 1

            # Log usage
            self._log_usage(cli_name, task_type="direct", duration=duration, success=True)

            return {
                "success": result.returncode == 0,
                "output": output,
                "cli_used": cli_name,
                "duration": round(duration, 2),
                "error": result.stderr if result.returncode != 0 else "",
            }

        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"⏰ {cli_name} CLI timed out after {duration}s")
            self._log_usage(cli_name, task_type="direct", duration=duration, success=False)
            return {
                "success": False,
                "output": "",
                "cli_used": cli_name,
                "duration": round(duration, 2),
                "error": f"Timeout after {config['timeout']}s",
            }

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ {cli_name} CLI failed: {e}")
            self._log_usage(cli_name, task_type="direct", duration=duration, success=False)
            return {
                "success": False,
                "output": "",
                "cli_used": cli_name,
                "duration": round(duration, 2),
                "error": str(e),
            }

    def run_with_fallback(
        self,
        prompt: str,
        task_type: str = "general",
        working_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run prompt with automatic fallback to other CLIs.

        Tries the best CLI first, then falls back to others in priority order.
        """
        tried = set()

        # Build priority list based on task type
        priority_order = self._get_priority_order(task_type)

        for cli_name in priority_order:
            if cli_name in tried or cli_name not in self.available_clis:
                continue

            tried.add(cli_name)
            result = self._run_with_cli(cli_name, prompt, working_dir)

            if result["success"]:
                return result

            logger.warning(f"{cli_name} failed, trying next CLI...")

        return {
            "success": False,
            "output": "",
            "cli_used": "none",
            "duration": 0,
            "error": "All CLI instances failed",
        }

    def _get_priority_order(self, task_type: str) -> List[str]:
        """Get CLI priority order for a task type."""
        if task_type == "code":
            return ["codex", "qwen", "claude"]
        elif task_type == "reasoning":
            return ["qwen", "claude", "codex"]
        else:
            return ["qwen", "claude", "codex"]

    def get_status(self) -> Dict[str, Any]:
        """Get status of all CLI instances."""
        return {
            "available": list(self.available_clis.keys()),
            "total_available": len(self.available_clis),
            "instances": {
                name: {
                    "status": info["status"],
                    "last_used": info["last_used"],
                    "call_count": info["call_count"],
                }
                for name, info in self.available_clis.items()
            },
        }

    def _log_usage(self, cli_name: str, task_type: str, duration: float, success: bool):
        """Log CLI usage for monitoring."""
        log_file = self._log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "cli": cli_name,
            "task_type": task_type,
            "duration_seconds": round(duration, 2),
            "success": success,
        }

        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.warning(f"Failed to log CLI usage: {e}")
