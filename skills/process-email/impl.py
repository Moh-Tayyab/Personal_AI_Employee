"""
Process Email Skill Implementation

This skill processes incoming emails from the Needs_Action folder.
"""

from pathlib import Path
from datetime import datetime


class ProcessEmailSkill:
    """Skill for processing incoming emails."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.handbook = self.vault_path / 'Company_Handbook.md'

    def get_emails(self):
        """Get all email files from Needs_Action."""
        emails = []
        for f in self.needs_action.glob('EMAIL_*.md'):
            emails.append(f)
        return emails

    def read_handbook(self):
        """Read company handbook for rules."""
        if self.handbook.exists():
            return self.handbook.read_text()
        return ""

    def process_email(self, email_file: Path) -> dict:
        """Process a single email file."""
        content = email_file.read_text()

        # Parse frontmatter
        frontmatter, body = self._parse_frontmatter(content)

        # Analyze email
        result = {
            'file': email_file.name,
            'from': frontmatter.get('from', 'Unknown'),
            'subject': frontmatter.get('subject', 'No Subject'),
            'priority': frontmatter.get('priority', 'normal'),
            'category': frontmatter.get('category', 'general'),
            'actions': []
        }

        # Determine required actions based on content
        body_lower = body.lower()

        if 'invoice' in body_lower or 'payment' in body_lower:
            result['actions'].append('Generate invoice')
        if 'meeting' in body_lower or 'schedule' in body_lower:
            result['actions'].append('Schedule meeting')
        if 'urgent' in body_lower or 'asap' in body_lower:
            result['priority'] = 'high'

        return result

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

    def create_plan(self, email_result: dict) -> Path:
        """Create a plan file for the email."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_file = self.plans / f"PLAN_{timestamp}.md"

        content = f"""---
type: email_plan
email_file: {email_result['file']}
created: {datetime.now().isoformat()}
status: pending
---

# Plan: {email_result['subject']}

## From
{email_result['from']}

## Priority
{email_result['priority']}

## Category
{email_result['category']}

## Required Actions
"""

        for action in email_result['actions']:
            content += f"- [ ] {action}\n"

        content += f"""
## Notes
_AI Employee: Process according to Company Handbook._
"""

        plan_file.write_text(content)
        return plan_file

    def run(self):
        """Execute the skill."""
        emails = self.get_emails()

        if not emails:
            return {"status": "no_emails", "message": "No emails to process"}

        results = []
        for email in emails:
            result = self.process_email(email)
            self.create_plan(result)
            results.append(result)

        return {
            "status": "processed",
            "count": len(results),
            "emails": results
        }


def execute(vault_path: str):
    """Main entry point for the skill."""
    skill = ProcessEmailSkill(vault_path)
    return skill.run()
