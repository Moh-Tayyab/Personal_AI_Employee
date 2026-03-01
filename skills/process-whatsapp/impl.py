"""
Process WhatsApp Skill Implementation

This skill processes incoming WhatsApp messages from the Needs_Action folder.
"""

from pathlib import Path
from datetime import datetime
import re


class ProcessWhatsAppSkill:
    """Skill for processing incoming WhatsApp messages."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.handbook = self.vault_path / 'Company_Handbook.md'

    def get_messages(self):
        """Get all WhatsApp message files from Needs_Action."""
        messages = []
        for f in self.needs_action.glob('WHATSAPP_*.md'):
            messages.append(f)
        return messages

    def read_handbook(self):
        """Read company handbook for rules."""
        if self.handbook.exists():
            return self.handbook.read_text()
        return ""

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

    def analyze_message(self, message_file: Path) -> dict:
        """Analyze a WhatsApp message for urgency and required actions."""
        content = message_file.read_text()
        frontmatter, body = self._parse_frontmatter(content)

        result = {
            'file': message_file.name,
            'from': frontmatter.get('from', 'Unknown'),
            'sender': frontmatter.get('sender', frontmatter.get('from', 'Unknown')),
            'priority': frontmatter.get('priority', 'normal'),
            'category': 'general',
            'actions': [],
            'needs_approval': False,
            'body': body[:500]  # First 500 chars
        }

        body_lower = body.lower()

        # Urgency detection
        urgent_keywords = ['urgent', 'asap', 'emergency', 'critical', 'immediately', 'help']
        if any(kw in body_lower for kw in urgent_keywords):
            result['priority'] = 'high'
            result['actions'].append('Flag as urgent - immediate attention needed')

        # Category detection
        if 'invoice' in body_lower or 'payment' in body_lower or 'bill' in body_lower:
            result['category'] = 'finance'
            result['actions'].append('Process payment/invoice request')
            result['needs_approval'] = True

        if 'meeting' in body_lower or 'schedule' in body_lower or 'call' in body_lower:
            result['category'] = 'calendar'
            result['actions'].append('Schedule meeting/call')

        if 'quote' in body_lower or 'pricing' in body_lower or 'price' in body_lower:
            result['category'] = 'sales'
            result['actions'].append('Prepare quote/pricing information')

        if 'contract' in body_lower or 'agreement' in body_lower or 'legal' in body_lower:
            result['category'] = 'legal'
            result['needs_approval'] = True
            result['actions'].append('Review legal document')

        # Default action if no specific category
        if not result['actions']:
            result['actions'].append('Draft reply')

        return result

    def create_plan(self, message_result: dict) -> Path:
        """Create a plan file for the WhatsApp message."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_sender = re.sub(r'[^a-zA-Z0-9]', '_', message_result['from'])[:30]
        plan_file = self.plans / f"PLAN_{timestamp}_WHATSAPP_{safe_sender}.md"

        content = f"""---
type: whatsapp_plan
message_file: {message_result['file']}
created: {datetime.now().isoformat()}
status: pending
priority: {message_result['priority']}
category: {message_result['category']}
needs_approval: {message_result['needs_approval']}
---

# Plan: WhatsApp from {message_result['from']}

## Sender
{message_result['from']}

## Priority
{message_result['priority']}

## Category
{message_result['category']}

## Message Preview
{message_result['body'][:300]}...

## Required Actions
"""
        for i, action in enumerate(message_result['actions'], 1):
            content += f"- [ ] {action}\n"

        if message_result['needs_approval']:
            content += """
## ⚠️ Approval Required
This message requires human approval before taking action.
See /Pending_Approval/ folder.
"""

        content += f"""
## Notes
_AI Employee: Process according to Company Handbook rules._
"""
        plan_file.write_text(content)
        return plan_file

    def create_approval_request(self, message_result: dict) -> Path:
        """Create an approval request for sensitive messages."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_file = self.pending_approval / f"WHATSAPP_{timestamp}_{message_result['category']}.md"

        content = f"""---
type: approval_request
source: whatsapp
message_file: {message_result['file']}
created: {datetime.now().isoformat()}
expires: {(datetime.now()).strftime('%Y-%m-%d')} 23:59:59
status: pending
action: reply
---

# WhatsApp Approval Request

## From
{message_result['from']}

## Category
{message_result['category']}

## Priority
{message_result['priority']}

## Message Preview
{message_result['body'][:500]}

## Proposed Actions
"""
        for action in message_result['actions']:
            content += f"- {action}\n"

        content += """
## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.

---
_This action requires human approval per Company Handbook rules._
"""
        approval_file.write_text(content)
        return approval_file

    def run(self):
        """Execute the skill."""
        messages = self.get_messages()

        if not messages:
            return {"status": "no_messages", "message": "No WhatsApp messages to process"}

        results = []
        for message in messages:
            result = self.analyze_message(message)
            plan_file = self.create_plan(result)

            if result['needs_approval']:
                approval_file = self.create_approval_request(result)
                result['approval_file'] = str(approval_file.name)

            result['plan_file'] = str(plan_file.name)
            results.append(result)

        return {
            "status": "processed",
            "count": len(results),
            "messages": results
        }


def execute(vault_path: str):
    """Main entry point for the skill."""
    skill = ProcessWhatsAppSkill(vault_path)
    return skill.run()