"""
Agent Teams Manager - Coordinates multiple sub-agents for complex tasks

Creates and manages teams of specialized sub-agents that work together on complex,
multi-domain tasks. Each team member handles a specific domain (email, finance,
social media, code, research) and reports back to the orchestrator.

Team roles:
- email_specialist: Handles email processing, drafting, and responses
- finance_specialist: Handles invoices, payments, accounting
- social_specialist: Handles social media posts and engagement
- code_specialist: Handles code generation, debugging, and refactoring
- research_specialist: Handles web research and data gathering
- generalist: Handles general tasks that don't fit other categories
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("AgentTeamsManager")


class AgentTeamsManager:
    """Manages creation and coordination of agent teams."""

    # Role definitions with specialization triggers
    ROLES = {
        "email_specialist": {
            "keywords": ["email", "inbox", "reply", "draft", "message", "correspondence", "mail"],
            "skills": ["process-emails"],
            "description": "Processes emails, drafts replies, manages inbox",
        },
        "finance_specialist": {
            "keywords": ["invoice", "payment", "billing", "accounting", "revenue", "expense", "odoo", "finance", "money"],
            "skills": [],
            "description": "Handles financial operations, invoices, and payments",
        },
        "social_specialist": {
            "keywords": ["social", "linkedin", "twitter", "facebook", "instagram", "post", "tweet", "engagement"],
            "skills": [],
            "description": "Manages social media posting and engagement",
        },
        "code_specialist": {
            "keywords": ["code", "debug", "function", "class", "script", "api", "database", "programming", "bug", "fix"],
            "skills": [],
            "description": "Handles code generation, debugging, and refactoring",
        },
        "research_specialist": {
            "keywords": ["research", "search", "investigate", "analyze", "find", "gather", "study", "report"],
            "skills": ["browsing-with-playwright"],
            "description": "Conducts web research and data gathering",
        },
        "generalist": {
            "keywords": [],  # Catches everything else
            "skills": [],
            "description": "Handles general tasks and coordination",
        },
    }

    # Team size thresholds
    MIN_ITEMS_FOR_TEAM = 3  # Minimum items in Needs_Action to justify a team
    MAX_TEAM_SIZE = 5  # Maximum agents in a team

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.teams_dir = self.vault_path / "Teams"
        self.teams_dir.mkdir(parents=True, exist_ok=True)
        self.active_teams_dir = self.teams_dir / "Active"
        self.active_teams_dir.mkdir(parents=True, exist_ok=True)
        self.completed_teams_dir = self.teams_dir / "Completed"
        self.completed_teams_dir.mkdir(parents=True, exist_ok=True)
        self.teams_log = self.teams_dir / "teams_log.jsonl"

    def should_create_team(self, prompt: str, needs_action_count: int) -> bool:
        """
        Determine if an agent team should be created for the current work.

        Args:
            prompt: The current task prompt
            needs_action_count: Number of items in Needs_Action folder

        Returns:
            True if a team should be created
        """
        # Disabled by default (per AGENTS.md: "currently disabled")
        # Enable by setting env var: AGENT_TEAMS_ENABLED=true
        if not os.getenv("AGENT_TEAMS_ENABLED", "").lower() == "true":
            return False

        # Need minimum items to justify a team
        if needs_action_count < self.MIN_ITEMS_FOR_TEAM:
            return False

        # Check if prompt suggests multi-domain work
        domains_detected = self._detect_domains(prompt)
        if len(domains_detected) >= 2:
            return True

        # Or if there are many items
        if needs_action_count >= self.MIN_ITEMS_FOR_TEAM * 2:
            return True

        return False

    def suggest_team_composition(self, items: List[str]) -> Dict[str, Any]:
        """
        Suggest team composition based on items in Needs_Action.

        Args:
            items: List of item filenames/descriptions

        Returns:
            Dict with recommended team size, roles, and task distribution
        """
        # Analyze items to determine needed roles
        role_scores = {role: 0 for role in self.ROLES}

        for item in items:
            item_lower = item.lower()
            for role, config in self.ROLES.items():
                for keyword in config["keywords"]:
                    if keyword in item_lower:
                        role_scores[role] += 1

        # Select roles with scores > 0
        recommended_roles = [role for role, score in role_scores.items() if score > 0]

        # Always include at least one generalist
        if "generalist" not in recommended_roles:
            recommended_roles.append("generalist")

        # Cap team size
        if len(recommended_roles) > self.MAX_TEAM_SIZE:
            # Keep top roles by score
            sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
            recommended_roles = [role for role, _ in sorted_roles[:self.MAX_TEAM_SIZE]]

        # Distribute tasks among roles
        task_distribution = self._distribute_tasks(items, recommended_roles)

        return {
            "recommended_size": len(recommended_roles),
            "roles": recommended_roles,
            "total_tasks": len(items),
            "task_distribution": task_distribution,
            "role_scores": {role: role_scores[role] for role in recommended_roles},
        }

    def create_team_prompt(self, team_suggestion: Dict[str, Any]) -> str:
        """Create a prompt for the AI to form and coordinate the team."""
        roles_info = []
        for role in team_suggestion["roles"]:
            role_config = self.ROLES.get(role, {})
            roles_info.append(f"- **{role}**: {role_config.get('description', 'General purpose')}")

        distribution_str = json.dumps(team_suggestion["task_distribution"], indent=2)

        prompt = f"""You are forming an agent team to process {team_suggestion['total_tasks']} pending items.

## Team Composition
{chr(10).join(roles_info)}

## Task Distribution
{distribution_str}

## Instructions
1. Assign each role to a sub-agent
2. Each sub-agent processes its assigned items independently
3. Report back with results for each item
4. Flag any items that need human approval
5. Move completed items to Done/ folder
6. Create Plans/ for complex items

Proceed with team coordination and task processing.
"""
        return prompt

    def _detect_domains(self, prompt: str) -> List[str]:
        """Detect which domains are involved in a prompt."""
        prompt_lower = prompt.lower()
        detected = []

        for role, config in self.ROLES.items():
            for keyword in config["keywords"]:
                if keyword and keyword in prompt_lower:
                    detected.append(role)
                    break

        return detected if detected else ["generalist"]

    def _distribute_tasks(
        self, items: List[str], roles: List[str]
    ) -> Dict[str, List[str]]:
        """Distribute items among team roles."""
        distribution = {role: [] for role in roles}

        for item in items:
            item_lower = item.lower()
            assigned = False

            # Find best matching role
            for role in roles:
                if role == "generalist":
                    continue

                role_config = self.ROLES.get(role, {})
                for keyword in role_config["keywords"]:
                    if keyword and keyword in item_lower:
                        distribution[role].append(item)
                        assigned = True
                        break

                if assigned:
                    break

            # Unassigned items go to generalist
            if not assigned:
                distribution["generalist"].append(item)

        return distribution

    def get_active_teams(self) -> List[Dict[str, Any]]:
        """Get list of active teams from the vault."""
        teams = []

        if not self.active_teams_dir.exists():
            return teams

        for team_file in self.active_teams_dir.glob("*.json"):
            try:
                with open(team_file, "r") as f:
                    team_data = json.load(f)
                teams.append(team_data)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to read team file {team_file}: {e}")

        return teams

    def log_team_activity(
        self,
        team_name: str,
        action: str,
        details: Dict[str, Any],
    ):
        """Log team activity to the teams log."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "team_name": team_name,
            "action": action,
            "details": details,
        }

        try:
            with open(self.teams_log, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.warning(f"Failed to log team activity: {e}")

    def create_team_status_report(self) -> str:
        """Generate a markdown status report of all active teams."""
        active_teams = self.get_active_teams()

        if not active_teams:
            return "# Agent Team Status\n\nNo active teams.\n"

        report = "# Agent Team Status\n\n"
        report += f"**Active Teams:** {len(active_teams)}\n\n"
        report += "## Teams\n\n"

        for team in active_teams:
            report += f"### {team.get('team_name', 'Unknown')}\n\n"
            report += f"- **Created:** {team.get('created', 'Unknown')}\n"
            report += f"- **Roles:** {', '.join(team.get('roles', []))}\n"
            report += f"- **Tasks:** "
            tasks = team.get("tasks", {})
            report += (
                f"{tasks.get('completed', 0)} completed, "
                f"{tasks.get('in_progress', 0)} in progress, "
                f"{tasks.get('pending', 0)} pending\n"
            )
            report += f"- **Status:** {team.get('status', 'Unknown')}\n\n"

            if team.get("issues"):
                report += "**Issues:**\n"
                for issue in team["issues"]:
                    report += f"- ⚠️ {issue}\n"
                report += "\n"

        return report

    def cleanup_completed_teams(self):
        """Move completed teams from Active to Completed directory."""
        if not self.active_teams_dir.exists():
            return

        completed_count = 0
        for team_file in self.active_teams_dir.glob("*.json"):
            try:
                with open(team_file, "r") as f:
                    team_data = json.load(f)

                tasks = team_data.get("tasks", {})
                if tasks.get("pending", 0) == 0 and tasks.get("in_progress", 0) == 0:
                    # Team is complete, move to completed directory
                    dest = self.completed_teams_dir / team_file.name
                    team_file.rename(dest)
                    completed_count += 1
                    logger.info(f"✅ Moved completed team {team_file.name} to Completed/")

            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to process team file {team_file}: {e}")

        if completed_count > 0:
            logger.info(f"Cleaned up {completed_count} completed teams")
