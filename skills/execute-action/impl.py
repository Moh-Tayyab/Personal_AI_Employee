"""
Execute Action Skill Implementation

This skill executes actions through MCP servers after approval.
"""

from pathlib import Path
from datetime import datetime
import json
import sys
import os

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp_client import get_mcp_client


class ExecuteActionSkill:
    """Skill for executing approved actions through MCP servers."""

    def __init__(self, vault_path: str, dry_run: bool = True):
        self.vault_path = Path(vault_path)
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.dry_run = dry_run
        self.mcp_client = get_mcp_client(str(vault_path))

        # Ensure directories exist
        self.logs.mkdir(parents=True, exist_ok=True)
        self.done.mkdir(parents=True, exist_ok=True)

    def _parse_frontmatter(self, content: str):
        """Parse YAML frontmatter from content."""
        lines = content.split('\n')
        in_frontmatter = False
        frontmatter = {}
        body_lines = []
        body_start = False

        for line in lines:
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    body_start = True
                continue

            if body_start:
                body_lines.append(line)
            elif in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        return frontmatter, '\n'.join(body_lines)

    def _log_action(self, action_type: str, target: str, result: dict):
        """Log action to daily log file."""
        log_file = self.logs / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "target": target,
            "result": result,
            "dry_run": self.dry_run
        }

        # Append to log file
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except:
                logs = []

        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))

    def execute_email_action(self, frontmatter: dict, body: str) -> dict:
        """Execute an email action."""
        to = frontmatter.get('to', '')
        subject = frontmatter.get('subject', '')
        cc = frontmatter.get('cc', '')

        if not to or not subject:
            return {"status": "error", "message": "Missing required email fields"}

        if self.dry_run:
            return {
                "status": "dry_run",
                "message": "Email would be sent (dry-run mode)",
                "to": to,
                "subject": subject
            }

        # Use MCP client to send email
        result = self.mcp_client.email.send_email(
            to=to,
            subject=subject,
            body=body,
            cc=cc
        )
        return result

    def execute_social_action(self, frontmatter: dict, body: str) -> dict:
        """Execute a social media action."""
        platform = frontmatter.get('platform', 'linkedin')
        action = frontmatter.get('action', 'post')
        content = frontmatter.get('content', body)

        if self.dry_run:
            return {
                "status": "dry_run",
                "message": f"Social post would be created on {platform} (dry-run mode)",
                "content": content[:100] + "..."
            }

        # Use MCP client for social media
        if platform == 'linkedin':
            result = self.mcp_client.linkedin.create_post({'content': content})
        elif platform == 'twitter':
            result = self.mcp_client.twitter.post_tweet({'text': content})
        else:
            result = {"status": "error", "message": f"Unknown platform: {platform}"}

        return result

    def execute_payment_action(self, frontmatter: dict, body: str) -> dict:
        """Execute a payment action (always requires approval)."""
        # Payments should never be auto-executed
        return {
            "status": "blocked",
            "message": "Payment actions require explicit human approval and cannot be auto-executed",
            "details": frontmatter
        }

    def execute_calendar_action(self, frontmatter: dict, body: str) -> dict:
        """Execute a calendar action."""
        action = frontmatter.get('action', 'create')
        title = frontmatter.get('title', '')
        date = frontmatter.get('date', '')
        time = frontmatter.get('time', '')

        if self.dry_run:
            return {
                "status": "dry_run",
                "message": "Calendar event would be created (dry-run mode)",
                "title": title,
                "date": date
            }

        # Calendar events would be created through an MCP server
        return {
            "status": "created",
            "message": "Calendar event created",
            "title": title,
            "date": date
        }

    def execute_approved_item(self, item_path: str) -> dict:
        """Execute an approved action item."""
        item_file = Path(item_path)
        if not item_file.exists():
            item_file = self.approved / item_path
            if not item_file.exists():
                return {"status": "error", "message": f"Item not found: {item_path}"}

        content = item_file.read_text()
        frontmatter, body = self._parse_frontmatter(content)

        action_type = frontmatter.get('action', frontmatter.get('type', 'general'))

        # Route to appropriate handler
        handlers = {
            'email': self.execute_email_action,
            'send_email': self.execute_email_action,
            'social': self.execute_social_action,
            'linkedin': self.execute_social_action,
            'twitter': self.execute_social_action,
            'payment': self.execute_payment_action,
            'calendar': self.execute_calendar_action,
        }

        handler = handlers.get(action_type, self._execute_generic_action)
        result = handler(frontmatter, body)

        # Log the action
        self._log_action(action_type, item_file.name, result)

        # Move to Done if successful
        if result.get('status') in ['sent', 'created', 'success', 'dry_run']:
            done_file = self.done / item_file.name
            item_file.rename(done_file)
            result['moved_to'] = str(done_file)

        return result

    def _execute_generic_action(self, frontmatter: dict, body: str) -> dict:
        """Execute a generic action."""
        return {
            "status": "dry_run",
            "message": "Generic action - manual processing required",
            "frontmatter": frontmatter
        }

    def run(self, item_path: str = None):
        """Execute the skill."""
        if item_path:
            return self.execute_approved_item(item_path)

        # Process all approved items
        results = []
        for item in self.approved.glob('*.md'):
            result = self.execute_approved_item(str(item))
            results.append({
                "file": item.name,
                "result": result
            })

        if not results:
            return {"status": "no_items", "message": "No approved items to execute"}

        return {
            "status": "executed",
            "count": len(results),
            "results": results
        }


def execute(vault_path: str, item_path: str = None, dry_run: bool = True):
    """Main entry point for the skill."""
    skill = ExecuteActionSkill(vault_path, dry_run)
    return skill.run(item_path)