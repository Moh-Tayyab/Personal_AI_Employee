"""
Quota Manager - Tracks API quota usage across providers

Monitors and manages API quota consumption for all AI providers and CLIs.
Prevents quota exhaustion by tracking usage, enforcing limits, and providing
alerts when approaching limits.

Tracked services:
- Qwen Code (OpenAI-compatible API)
- Claude Code (Anthropic API)
- Codex CLI (OpenAI API)
- Gemini (Google AI API)
- OpenRouter
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("QuotaManager")


class QuotaManager:
    """Manages API quota tracking and enforcement."""

    # Default quotas (can be overridden by environment variables)
    DEFAULT_QUOTAS = {
        "qwen": {
            "daily_limit": int(os.getenv("QWEN_DAILY_LIMIT", "100")),  # requests
            "cost_limit_usd": float(os.getenv("QWEN_DAILY_COST_USD", "10")),
            "exhausted": False,
        },
        "claude": {
            "daily_limit": int(os.getenv("CLAUDE_DAILY_LIMIT", "50")),
            "cost_limit_usd": float(os.getenv("CLAUDE_DAILY_COST_USD", "15")),
            "exhausted": False,
        },
        "codex": {
            "daily_limit": int(os.getenv("CODEX_DAILY_LIMIT", "30")),
            "cost_limit_usd": float(os.getenv("CODEX_DAILY_COST_USD", "10")),
            "exhausted": False,
        },
        "gemini": {
            "daily_limit": int(os.getenv("GEMINI_DAILY_LIMIT", "1500")),  # free tier generous
            "cost_limit_usd": float(os.getenv("GEMINI_DAILY_COST_USD", "0")),  # free tier
            "exhausted": False,
        },
        "openrouter": {
            "daily_limit": int(os.getenv("OPENROUTER_DAILY_LIMIT", "100")),
            "cost_limit_usd": float(os.getenv("OPENROUTER_DAILY_COST_USD", "20")),
            "exhausted": False,
        },
    }

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.quota_file = self.vault_path / "secrets" / "quota_status.json"
        self.quota_file.parent.mkdir(parents=True, exist_ok=True)
        self.quota_data = self._load_quota_status()

    def _load_quota_status(self) -> Dict[str, Any]:
        """Load quota status from file or initialize defaults."""
        if self.quota_file.exists():
            try:
                with open(self.quota_file, "r") as f:
                    data = json.load(f)

                # Reset daily counters if new day
                last_reset = data.get("last_reset", "")
                today = datetime.now().strftime("%Y-%m-%d")

                if last_reset != today:
                    logger.info("📅 Resetting daily quota counters")
                    self._reset_daily_counters(data)
                    data["last_reset"] = today
                    self._save_quota_status(data)

                return data
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to load quota status, using defaults: {e}")
                return self._create_default_quota_status()
        else:
            default = self._create_default_quota_status()
            self._save_quota_status(default)
            return default

    def _create_default_quota_status(self) -> Dict[str, Any]:
        """Create default quota status structure."""
        status = {
            "last_reset": datetime.now().strftime("%Y-%m-%d"),
            "services": {},
        }

        for service, config in self.DEFAULT_QUOTAS.items():
            status["services"][service] = {
                "daily_limit": config["daily_limit"],
                "cost_limit_usd": config["cost_limit_usd"],
                "exhausted": config["exhausted"],
                "current_usage": 0,  # request count
                "current_cost_usd": 0.0,  # estimated cost
                "last_request": None,
                "total_requests_today": 0,
                "total_requests_all_time": 0,
            }

        return status

    def _reset_daily_counters(self, data: Dict[str, Any]):
        """Reset daily usage counters."""
        for service in data.get("services", {}):
            if service in data["services"]:
                data["services"][service]["current_usage"] = 0
                data["services"][service]["current_cost_usd"] = 0.0
                data["services"][service]["total_requests_today"] = 0
                data["services"][service]["exhausted"] = False

    def _save_quota_status(self, data: Optional[Dict[str, Any]] = None):
        """Save quota status to file."""
        data_to_save = data or self.quota_data
        try:
            with open(self.quota_file, "w") as f:
                json.dump(data_to_save, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save quota status: {e}")

    def record_usage(
        self,
        service: str,
        tokens_used: int = 0,
        estimated_cost_usd: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Record API usage for a service.

        Args:
            service: Service name (qwen, claude, codex, gemini, openrouter)
            tokens_used: Number of tokens consumed
            estimated_cost_usd: Estimated cost in USD

        Returns:
            Status dict with remaining quota and warnings
        """
        if service not in self.quota_data.get("services", {}):
            logger.warning(f"Unknown service: {service}")
            return {"status": "unknown_service", "warning": f"Service '{service}' not tracked"}

        service_data = self.quota_data["services"][service]

        # Update counters
        service_data["current_usage"] += 1
        service_data["current_cost_usd"] += estimated_cost_usd
        service_data["total_requests_today"] += 1
        service_data["total_requests_all_time"] += 1
        service_data["last_request"] = datetime.now().isoformat()

        # Check if quota exceeded
        warnings = []
        quota_exceeded = False

        # Check request count limit
        if service_data["current_usage"] >= service_data["daily_limit"]:
            service_data["exhausted"] = True
            quota_exceeded = True
            warnings.append(
                f"Daily request limit exceeded: "
                f"{service_data['current_usage']}/{service_data['daily_limit']}"
            )
            logger.warning(f"⚠️ {service} daily request quota EXHAUSTED")

        # Check cost limit
        if service_data["cost_limit_usd"] > 0 and service_data["current_cost_usd"] >= service_data["cost_limit_usd"]:
            service_data["exhausted"] = True
            quota_exceeded = True
            warnings.append(
                f"Daily cost limit exceeded: "
                f"${service_data['current_cost_usd']:.2f}/${service_data['cost_limit_usd']:.2f}"
            )
            logger.warning(f"⚠️ {service} daily cost quota EXHAUSTED")

        # Check approaching limits (80% threshold)
        usage_pct = (service_data["current_usage"] / service_data["daily_limit"]) * 100
        if 80 <= usage_pct < 100:
            warnings.append(f"Approaching request limit: {usage_pct:.0f}%")

        self._save_quota_status()

        remaining = max(0, service_data["daily_limit"] - service_data["current_usage"])
        cost_remaining = max(0, service_data["cost_limit_usd"] - service_data["current_cost_usd"])

        return {
            "status": "exhausted" if quota_exceeded else "ok",
            "service": service,
            "requests_today": service_data["total_requests_today"],
            "remaining_requests": remaining,
            "cost_usd_today": round(service_data["current_cost_usd"], 4),
            "cost_remaining_usd": round(cost_remaining, 4),
            "exhausted": service_data["exhausted"],
            "warnings": warnings,
        }

    def is_exhausted(self, service: str) -> bool:
        """Check if a service's quota is exhausted."""
        if service not in self.quota_data.get("services", {}):
            return False
        return self.quota_data["services"][service].get("exhausted", False)

    def get_available_services(self) -> list:
        """Get list of services that are not exhausted."""
        available = []
        for service, data in self.quota_data.get("services", {}).items():
            if not data.get("exhausted", False):
                available.append(service)
        return available

    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive quota status report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "last_reset": self.quota_data.get("last_reset", "unknown"),
            "services": {},
        }

        for service, data in self.quota_data.get("services", {}).items():
            usage_pct = 0
            if data["daily_limit"] > 0:
                usage_pct = (data["current_usage"] / data["daily_limit"]) * 100

            cost_pct = 0
            if data["cost_limit_usd"] > 0:
                cost_pct = (data["current_cost_usd"] / data["cost_limit_usd"]) * 100

            report["services"][service] = {
                "exhausted": data["exhausted"],
                "requests": {
                    "used": data["current_usage"],
                    "limit": data["daily_limit"],
                    "remaining": max(0, data["daily_limit"] - data["current_usage"]),
                    "percentage": round(usage_pct, 1),
                },
                "cost": {
                    "used_usd": round(data["current_cost_usd"], 4),
                    "limit_usd": data["cost_limit_usd"],
                    "remaining_usd": round(max(0, data["cost_limit_usd"] - data["current_cost_usd"]), 4),
                    "percentage": round(cost_pct, 1),
                },
                "total_requests_today": data["total_requests_today"],
                "total_requests_all_time": data["total_requests_all_time"],
                "last_request": data.get("last_request"),
            }

        return report

    def reset_quota(self, service: str) -> bool:
        """Manually reset quota for a service (admin override)."""
        if service not in self.quota_data.get("services", {}):
            return False

        self.quota_data["services"][service]["exhausted"] = False
        self.quota_data["services"][service]["current_usage"] = 0
        self.quota_data["services"][service]["current_cost_usd"] = 0.0
        self._save_quota_status()

        logger.info(f"✅ {service} quota manually reset")
        return True

    def reset_all_quotas(self):
        """Reset all quotas (typically called at start of new day)."""
        self.quota_data = self._create_default_quota_status()
        self._save_quota_status()
        logger.info("📅 All quotas reset")
