"""
Agent Teams Integration for Personal AI Employee Orchestrator

This module extends the orchestrator to support agent teams coordination,
including team lifecycle management, task distribution, and quality monitoring.
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger("AgentTeamsManager")

class AgentTeamsManager:
    """Manages agent teams lifecycle and coordination."""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.teams_dir = Path.home() / ".claude" / "teams"
        self.tasks_dir = Path.home() / ".claude" / "tasks"
        self.active_teams = {}

        # Ensure directories exist
        self.teams_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

        # Create team coordination directories in vault
        (self.vault_path / "Teams").mkdir(exist_ok=True)
        (self.vault_path / "Teams" / "Active").mkdir(exist_ok=True)
        (self.vault_path / "Teams" / "Completed").mkdir(exist_ok=True)
        (self.vault_path / "Teams" / "Logs").mkdir(exist_ok=True)

    def should_create_team(self, task_description: str, items_count: int) -> bool:
        """Determine if a task warrants creating an agent team."""
        team_indicators = [
            "multiple domains", "parallel", "simultaneously", "team", "coordinate",
            "email and social", "accounting and", "research and", "different perspectives",
            "review from multiple", "cross-functional", "multi-domain"
        ]

        # Check for team indicators in task description
        has_indicators = any(indicator in task_description.lower() for indicator in team_indicators)

        # Check if we have enough items to warrant parallel processing
        enough_items = items_count >= 5

        # Check if we have multiple types of items
        needs_action_dir = self.vault_path / "Needs_Action"
        if needs_action_dir.exists():
            item_types = set()
            for item_file in needs_action_dir.glob("*.md"):
                if "EMAIL_" in item_file.name:
                    item_types.add("email")
                elif "SOCIAL_" in item_file.name:
                    item_types.add("social")
                elif "INVOICE_" in item_file.name:
                    item_types.add("accounting")
                elif "RESEARCH_" in item_file.name:
                    item_types.add("research")

            multiple_types = len(item_types) >= 2
        else:
            multiple_types = False

        return has_indicators or (enough_items and multiple_types)

    def suggest_team_composition(self, items: List[str]) -> Dict[str, Any]:
        """Suggest team composition based on available work items."""
        item_types = {"email": 0, "social": 0, "accounting": 0, "research": 0, "general": 0}

        for item in items:
            item_lower = item.lower()
            if "email" in item_lower:
                item_types["email"] += 1
            elif "social" in item_lower or "linkedin" in item_lower or "twitter" in item_lower:
                item_types["social"] += 1
            elif "invoice" in item_lower or "accounting" in item_lower or "expense" in item_lower:
                item_types["accounting"] += 1
            elif "research" in item_lower or "analysis" in item_lower:
                item_types["research"] += 1
            else:
                item_types["general"] += 1

        # Suggest team based on work distribution
        suggested_team = []

        if item_types["email"] >= 1:
            suggested_team.append({
                "role": "email-specialist",
                "description": "Handle email processing, responses, and follow-ups using email MCP server",
                "estimated_tasks": item_types["email"]
            })

        if item_types["social"] >= 1:
            suggested_team.append({
                "role": "social-media-manager",
                "description": "Manage social media posts, engagement, and content using social MCP servers",
                "estimated_tasks": item_types["social"]
            })

        if item_types["accounting"] >= 1:
            suggested_team.append({
                "role": "accounting-specialist",
                "description": "Process invoices, expenses, and financial data using Odoo MCP server",
                "estimated_tasks": item_types["accounting"]
            })

        if item_types["research"] >= 1:
            suggested_team.append({
                "role": "research-analyst",
                "description": "Gather intelligence, analyze data, and provide insights",
                "estimated_tasks": item_types["research"]
            })

        if item_types["general"] >= 3 or len(suggested_team) == 0:
            suggested_team.append({
                "role": "general-assistant",
                "description": "Handle general tasks and coordination",
                "estimated_tasks": item_types["general"]
            })

        return {
            "suggested_team": suggested_team,
            "total_tasks": sum(item_types.values()),
            "task_distribution": item_types,
            "recommended_size": min(len(suggested_team), 5)  # Cap at 5 teammates
        }

    def create_team_prompt(self, team_suggestion: Dict[str, Any]) -> str:
        """Generate a team creation prompt for Claude."""
        team_members = team_suggestion["suggested_team"]
        total_tasks = team_suggestion["total_tasks"]

        prompt = f"Create an agent team to handle {total_tasks} items efficiently with {len(team_members)} teammates:\n\n"

        for i, member in enumerate(team_members, 1):
            prompt += f"- {member['role']}: {member['description']} (estimated {member['estimated_tasks']} tasks)\n"

        prompt += f"\nEach teammate should work independently on their domain while coordinating through the shared task list. "
        prompt += f"Use the vault structure at {self.vault_path} for coordination and handoffs."

        return prompt

    def monitor_team_health(self, team_name: str) -> Dict[str, Any]:
        """Monitor the health and progress of an active team."""
        team_config_path = self.teams_dir / team_name / "config.json"
        tasks_path = self.tasks_dir / team_name

        health_status = {
            "team_name": team_name,
            "status": "unknown",
            "members": [],
            "tasks": {"pending": 0, "in_progress": 0, "completed": 0},
            "last_activity": None,
            "issues": []
        }

        # Check team configuration
        if not team_config_path.exists():
            health_status["status"] = "missing_config"
            health_status["issues"].append("Team configuration file missing")
            return health_status

        try:
            with open(team_config_path, 'r') as f:
                team_config = json.load(f)

            health_status["members"] = team_config.get("members", [])
            health_status["status"] = "active"

        except Exception as e:
            health_status["status"] = "config_error"
            health_status["issues"].append(f"Error reading team config: {e}")
            return health_status

        # Check task status
        if tasks_path.exists():
            for task_file in tasks_path.glob("*.json"):
                try:
                    with open(task_file, 'r') as f:
                        task = json.load(f)

                    status = task.get("status", "unknown")
                    if status in health_status["tasks"]:
                        health_status["tasks"][status] += 1

                    # Track last activity
                    updated_at = task.get("updatedAt")
                    if updated_at:
                        if not health_status["last_activity"] or updated_at > health_status["last_activity"]:
                            health_status["last_activity"] = updated_at

                except Exception as e:
                    health_status["issues"].append(f"Error reading task {task_file.name}: {e}")

        # Check for stale teams (no activity in last hour)
        if health_status["last_activity"]:
            try:
                last_activity = datetime.fromisoformat(health_status["last_activity"])
                if datetime.now() - last_activity > timedelta(hours=1):
                    health_status["issues"].append("No recent activity (>1 hour)")
            except:
                pass

        # Check for stuck tasks
        if health_status["tasks"]["in_progress"] > 0 and health_status["tasks"]["completed"] == 0:
            health_status["issues"].append("Tasks in progress but none completed")

        return health_status

    def get_active_teams(self) -> List[Dict[str, Any]]:
        """Get list of all active teams with their status."""
        active_teams = []

        if not self.teams_dir.exists():
            return active_teams

        for team_dir in self.teams_dir.iterdir():
            if team_dir.is_dir():
                team_health = self.monitor_team_health(team_dir.name)
                active_teams.append(team_health)

        return active_teams

    def log_team_activity(self, team_name: str, activity: str, details: Dict[str, Any] = None):
        """Log team activity to vault logs."""
        log_dir = self.vault_path / "Teams" / "Logs"
        log_file = log_dir / f"{team_name}_{datetime.now().strftime('%Y%m%d')}.md"

        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"## {timestamp} - {activity}\n\n"

        if details:
            for key, value in details.items():
                log_entry += f"- **{key}**: {value}\n"

        log_entry += "\n---\n\n"

        # Append to daily log file
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def cleanup_completed_teams(self):
        """Clean up teams that have completed all their tasks."""
        for team_dir in self.teams_dir.iterdir():
            if team_dir.is_dir():
                team_name = team_dir.name
                health = self.monitor_team_health(team_name)

                # If all tasks are completed and no pending/in-progress tasks
                if (health["tasks"]["completed"] > 0 and
                    health["tasks"]["pending"] == 0 and
                    health["tasks"]["in_progress"] == 0):

                    logger.info(f"Moving completed team {team_name} to archive")

                    # Move team info to completed directory in vault
                    completed_dir = self.vault_path / "Teams" / "Completed"
                    team_summary = {
                        "team_name": team_name,
                        "completed_at": datetime.now().isoformat(),
                        "final_status": health,
                        "total_tasks_completed": health["tasks"]["completed"]
                    }

                    with open(completed_dir / f"{team_name}_summary.json", 'w') as f:
                        json.dump(team_summary, f, indent=2)

                    self.log_team_activity(team_name, "Team Completed", {
                        "Total Tasks": health["tasks"]["completed"],
                        "Team Members": len(health["members"]),
                        "Status": "Successfully completed all assigned tasks"
                    })

    def create_team_status_report(self) -> str:
        """Create a comprehensive status report for all teams."""
        active_teams = self.get_active_teams()

        if not active_teams:
            return "No active agent teams currently running."

        report = f"# Agent Teams Status Report\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for team in active_teams:
            report += f"## Team: {team['team_name']}\n\n"
            report += f"- **Status**: {team['status']}\n"
            report += f"- **Members**: {len(team['members'])}\n"
            report += f"- **Tasks**: {team['tasks']['pending']} pending, {team['tasks']['in_progress']} in progress, {team['tasks']['completed']} completed\n"

            if team['last_activity']:
                report += f"- **Last Activity**: {team['last_activity']}\n"

            if team['issues']:
                report += f"- **Issues**: {', '.join(team['issues'])}\n"

            report += "\n"

        return report