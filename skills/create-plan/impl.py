"""
Create Plan Skill Implementation

This skill creates structured plan files for actionable items in the vault.
"""

from pathlib import Path
from datetime import datetime
import re


class CreatePlanSkill:
    """Skill for creating execution plans from action items."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.handbook = self.vault_path / 'Company_Handbook.md'

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

    def _determine_item_type(self, frontmatter: dict, filename: str) -> str:
        """Determine the type of action item."""
        if 'type' in frontmatter:
            return frontmatter['type']
        if filename.startswith('EMAIL_'):
            return 'email'
        if filename.startswith('WHATSAPP_'):
            return 'whatsapp'
        if filename.startswith('FILE_'):
            return 'file_drop'
        if filename.startswith('PAYMENT_'):
            return 'payment'
        if filename.startswith('INVOICE_'):
            return 'invoice'
        return 'general'

    def _extract_actions(self, body: str, item_type: str) -> list:
        """Extract suggested actions from the item content."""
        actions = []
        body_lower = body.lower()

        # Check for existing action items in the content
        checkbox_pattern = r'-\s*\[\s*\]\s*(.+)'
        existing_actions = re.findall(checkbox_pattern, body)
        if existing_actions:
            actions.extend(existing_actions)

        # Generate actions based on type and content
        if item_type == 'email':
            if 'invoice' in body_lower or 'payment' in body_lower:
                actions.append('Process invoice/payment request')
            if 'meeting' in body_lower or 'schedule' in body_lower:
                actions.append('Schedule meeting')
            if 'urgent' in body_lower:
                actions.append('Mark as high priority')
            if not actions:
                actions.append('Draft reply')

        elif item_type == 'whatsapp':
            if 'urgent' in body_lower:
                actions.append('Respond immediately')
            if 'quote' in body_lower or 'price' in body_lower:
                actions.append('Prepare quote')
            if not actions:
                actions.append('Draft response')

        elif item_type == 'file_drop':
            actions.append('Analyze file contents')
            actions.append('Determine required action')
            actions.append('File in appropriate location')

        elif item_type == 'payment':
            actions.append('Verify payment details')
            actions.append('Check approval status')
            actions.append('Execute or request approval')

        return list(set(actions))  # Remove duplicates

    def _determine_priority(self, frontmatter: dict, body: str) -> str:
        """Determine priority level."""
        if 'priority' in frontmatter:
            return frontmatter['priority']

        body_lower = body.lower()
        high_keywords = ['urgent', 'asap', 'emergency', 'critical', 'immediately']

        if any(kw in body_lower for kw in high_keywords):
            return 'high'
        return 'normal'

    def _requires_approval(self, item_type: str, body: str) -> bool:
        """Determine if this item requires human approval."""
        body_lower = body.lower()

        # Always require approval for payments
        if item_type == 'payment':
            return True

        # Require approval for legal matters
        if 'contract' in body_lower or 'legal' in body_lower or 'agreement' in body_lower:
            return True

        # Require approval for large amounts
        amount_pattern = r'\$[\d,]+|\d+\s*(dollars|usd)'
        amounts = re.findall(amount_pattern, body_lower)
        for amt in amounts:
            try:
                value = int(re.sub(r'[^\d]', '', amt))
                if value > 50:
                    return True
            except:
                pass

        return False

    def create_plan(self, item_path: str) -> dict:
        """Create a plan file for an action item."""
        item_file = Path(item_path)
        if not item_file.exists():
            # Try relative to vault
            item_file = self.needs_action / item_path
            if not item_file.exists():
                return {"status": "error", "message": f"Item not found: {item_path}"}

        content = item_file.read_text()
        frontmatter, body = self._parse_frontmatter(content)

        item_type = self._determine_item_type(frontmatter, item_file.name)
        priority = self._determine_priority(frontmatter, body)
        actions = self._extract_actions(body, item_type)
        needs_approval = self._requires_approval(item_type, body)

        # Generate plan filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', item_file.stem)[:50]
        plan_file = self.plans / f"PLAN_{timestamp}_{item_type}_{safe_name}.md"

        # Create plan content
        plan_content = f"""---
created: {datetime.now().isoformat()}
status: {'pending_approval' if needs_approval else 'pending'}
type: {item_type}
source_file: {item_file.name}
priority: {priority}
needs_approval: {needs_approval}
---

# Plan: {frontmatter.get('subject', frontmatter.get('from', item_file.stem))}

## Objective
Process {item_type} item: {item_file.name}

## Source Details
"""
        # Add relevant frontmatter
        for key in ['from', 'to', 'subject', 'date', 'sender', 'received']:
            if key in frontmatter:
                plan_content += f"- **{key.title()}**: {frontmatter[key]}\n"

        plan_content += f"""
## Priority
{priority.upper()}

## Steps
"""
        for i, action in enumerate(actions, 1):
            plan_content += f"- [ ] Step {i}: {action}\n"

        if not actions:
            plan_content += "- [ ] Step 1: Analyze and determine required action\n"

        plan_content += f"""
## Required Resources
- Access to {item_type} processing tools
- Company Handbook reference

## Approval Required
{'Yes - See /Pending_Approval/ folder' if needs_approval else 'No'}

## Estimated Time
{'30 minutes' if priority == 'high' else '1-2 hours'}

## Notes
_AI Employee: Process this item according to Company Handbook rules._

---
*Plan created by AI Employee at {datetime.now().isoformat()}*
"""

        plan_file.write_text(plan_content)

        # Update source item status
        updated_content = content.replace('status: pending', 'status: planned', 1)
        if updated_content != content:
            item_file.write_text(updated_content)

        return {
            "status": "created",
            "plan_file": str(plan_file.name),
            "item_type": item_type,
            "priority": priority,
            "actions_count": len(actions),
            "needs_approval": needs_approval
        }

    def run(self, item_path: str = None):
        """Execute the skill."""
        if item_path:
            return self.create_plan(item_path)

        # Process all items in Needs_Action
        results = []
        for item in self.needs_action.glob('*.md'):
            result = self.create_plan(str(item))
            results.append(result)

        if not results:
            return {"status": "no_items", "message": "No items to plan"}

        return {
            "status": "processed",
            "count": len(results),
            "plans": results
        }


def execute(vault_path: str, item_path: str = None):
    """Main entry point for the skill."""
    skill = CreatePlanSkill(vault_path)
    return skill.run(item_path)