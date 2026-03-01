"""
Request Approval Skill Implementation

This skill creates approval request files for sensitive actions.
"""

from pathlib import Path
from datetime import datetime, timedelta
import re


class RequestApprovalSkill:
    """Skill for creating approval requests for sensitive actions."""

    # Actions that always require approval
    ALWAYS_APPROVAL = ['payment', 'legal', 'contract', 'delete']

    # Actions that may require approval based on context
    CONTEXTUAL_APPROVAL = ['email', 'social', 'calendar', 'file']

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.handbook = self.vault_path / 'Company_Handbook.md'

        # Ensure directories exist
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        self.approved.mkdir(parents=True, exist_ok=True)
        self.rejected.mkdir(parents=True, exist_ok=True)

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

    def _extract_amount(self, text: str) -> float:
        """Extract monetary amount from text."""
        patterns = [
            r'\$([\d,]+\.?\d*)',  # $100 or $1,000.00
            r'(\d+)\s*(dollars?|usd)',  # 100 dollars or 50 USD
            r'(?:amount|total|sum)[:\s]*\$?([\d,]+\.?\d*)',  # amount: $100
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    return float(re.sub(r'[^\d.]', '', match.group(1)))
                except:
                    pass
        return 0.0

    def _check_approval_rules(self, action_type: str, context: dict) -> tuple:
        """Check if approval is required based on rules."""
        # Always require approval for certain types
        if action_type in self.ALWAYS_APPROVAL:
            return True, f"{action_type} actions always require approval"

        # Check amount threshold ($50)
        amount = context.get('amount', 0)
        if amount > 50:
            return True, f"Amount ${amount} exceeds $50 threshold"

        # Check for new contacts
        if action_type == 'email':
            recipient = context.get('to', context.get('recipient', ''))
            known_contacts = self._load_known_contacts()
            if recipient and recipient not in known_contacts:
                return True, f"New contact: {recipient}"

        # Check for legal keywords
        body = context.get('body', '')
        legal_keywords = ['contract', 'legal', 'agreement', 'sue', 'lawsuit', 'attorney']
        if any(kw in body.lower() for kw in legal_keywords):
            return True, "Contains legal-related content"

        # Check for high-risk actions
        if action_type == 'social':
            if context.get('action') in ['reply', 'dm', 'delete']:
                return True, f"Social media {context.get('action')} requires approval"

        return False, "Auto-approved"

    def _load_known_contacts(self) -> set:
        """Load known contacts from vault."""
        contacts_file = self.vault_path / 'contacts.txt'
        if contacts_file.exists():
            return set(contacts_file.read_text().strip().split('\n'))
        return set()

    def create_approval_request(self, action_type: str, details: dict) -> dict:
        """Create an approval request file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Check if approval is required
        requires_approval, reason = self._check_approval_rules(action_type, details)

        if not requires_approval:
            return {
                "status": "auto_approved",
                "message": reason,
                "action_type": action_type
            }

        # Create approval request file
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', details.get('target', details.get('to', 'unknown')))[:30]
        approval_file = self.pending_approval / f"APPROVAL_{timestamp}_{action_type}_{safe_name}.md"

        expiry = datetime.now() + timedelta(hours=24)

        content = f"""---
type: approval_request
action: {action_type}
created: {datetime.now().isoformat()}
expires: {expiry.isoformat()}
status: pending
requires_approval: true
reason: {reason}
---

# Approval Request: {action_type.upper()}

## Action Type
{action_type}

## Reason for Approval
{reason}

## Details
"""
        # Add all details as key-value pairs
        for key, value in details.items():
            if key not in ['body', 'content']:
                content += f"- **{key}**: {value}\n"

        # Add body/content if present
        if 'body' in details:
            content += f"\n## Content/Body\n{details['body'][:1000]}\n"
        if 'content' in details and 'body' not in details:
            content += f"\n## Content\n{details['content'][:1000]}\n"

        content += f"""
## Risk Assessment
- Action Type: {action_type}
- Amount: ${details.get('amount', 0)}
- Recipient: {details.get('to', details.get('recipient', 'N/A'))}

## To Approve
Move this file to the `/Approved` folder.

## To Reject
Move this file to the `/Rejected` folder.

---
*This action requires human approval per Company Handbook rules.*
*Request created: {datetime.now().isoformat()}*
*Expires: {expiry.isoformat()}*
"""

        approval_file.write_text(content)

        return {
            "status": "approval_required",
            "message": "Approval request created",
            "file": str(approval_file.name),
            "action_type": action_type,
            "reason": reason,
            "expires": expiry.isoformat()
        }

    def check_approval_status(self, request_name: str) -> str:
        """Check if an approval request has been approved or rejected."""
        # Check Approved folder
        if (self.approved / request_name).exists():
            return "approved"
        # Check Rejected folder
        if (self.rejected / request_name).exists():
            return "rejected"
        # Still pending
        if (self.pending_approval / request_name).exists():
            return "pending"
        return "not_found"

    def process_plan_for_approval(self, plan_path: str) -> dict:
        """Process a plan file and create approval requests for sensitive steps."""
        plan_file = Path(plan_path)
        if not plan_file.exists():
            plan_file = self.vault_path / 'Plans' / plan_path
            if not plan_file.exists():
                return {"status": "error", "message": f"Plan not found: {plan_path}"}

        content = plan_file.read_text()
        frontmatter, body = self._parse_frontmatter(content)

        if frontmatter.get('needs_approval') != 'true':
            return {"status": "no_approval_needed", "message": "Plan does not require approval"}

        action_type = frontmatter.get('type', 'general')
        details = {
            'target': plan_file.stem,
            'plan_file': plan_file.name,
            'body': body
        }

        return self.create_approval_request(action_type, details)

    def run(self, action_type: str = None, details: dict = None, plan_path: str = None):
        """Execute the skill."""
        if plan_path:
            return self.process_plan_for_approval(plan_path)

        if action_type and details:
            return self.create_approval_request(action_type, details)

        return {"status": "error", "message": "Missing action_type and details or plan_path"}


def execute(vault_path: str, action_type: str = None, details: dict = None, plan_path: str = None):
    """Main entry point for the skill."""
    skill = RequestApprovalSkill(vault_path)
    return skill.run(action_type, details, plan_path)