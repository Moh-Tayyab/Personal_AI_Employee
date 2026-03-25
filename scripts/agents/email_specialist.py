#!/usr/bin/env python3
"""
Email Specialist Agent - Silver Tier

This agent handles all email-related operations:
- Processing emails from vault/Needs_Action/
- Drafting responses
- Sending emails via Gmail MCP server
- Managing approval workflow
"""

import argparse
import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vault/Logs/email_specialist.log')
    ]
)
logger = logging.getLogger("EmailSpecialist")


class EmailSpecialistAgent:
    """Specialized agent for email processing."""

    def __init__(self, vault_path: str, dry_run: bool = True):
        self.vault_path = Path(vault_path).resolve()
        self.dry_run = dry_run
        
        # Vault directories
        self.needs_action = self.vault_path / "Needs_Action"
        self.email_dir = self.needs_action / "email"
        self.drafts = self.vault_path / "Drafts"
        self.pending_approval = self.vault_path / "Pending_Approval" / "Emails"
        self.approved = self.vault_path / "Approved" / "Emails"
        self.done = self.vault_path / "Done" / "Emails"
        self.logs = self.vault_path / "Logs"
        
        # Ensure directories exist
        for dir_path in [self.email_dir, self.drafts, self.pending_approval, 
                         self.approved, self.done, self.logs]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Approval thresholds
        self.approval_thresholds = {
            "max_recipients": 10,
            "sensitive_keywords": ["partnership", "investment", "contract", "legal", "confidential"],
            "auto_approve_patterns": ["thank", "confirm", "acknowledge", "received"]
        }
        
        logger.info(f"Email Specialist initialized - Vault: {self.vault_path}")
        logger.info(f"Dry run mode: {self.dry_run}")

    def parse_email_file(self, file_path: Path) -> Dict:
        """Parse a markdown email file and extract metadata."""
        content = file_path.read_text(encoding='utf-8')
        
        # Extract frontmatter
        frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
        metadata = {}
        body = content
        
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
            body = content[frontmatter_match.end():].strip()
        
        return {
            "file_path": file_path,
            "metadata": metadata,
            "body": body,
            "content": content
        }

    def analyze_email(self, email_data: Dict) -> Dict:
        """Analyze email and determine required action."""
        metadata = email_data["metadata"]
        body = email_data["body"]
        
        analysis = {
            "type": metadata.get("type", "email"),
            "from": metadata.get("from", "unknown"),
            "subject": metadata.get("subject", "No subject"),
            "priority": metadata.get("priority", "medium"),
            "requires_response": True,
            "requires_approval": False,
            "approval_reason": None,
            "sentiment": "neutral",
            "category": "general",
            "suggested_action": "draft_response"
        }
        
        # Check for sensitive keywords
        content_lower = (body + " " + analysis["subject"]).lower()
        for keyword in self.approval_thresholds["sensitive_keywords"]:
            if keyword in content_lower:
                analysis["requires_approval"] = True
                analysis["approval_reason"] = f"Contains sensitive keyword: {keyword}"
                break
        
        # Check recipient count (if available)
        recipients = metadata.get("to", "").split(",")
        if len(recipients) > self.approval_thresholds["max_recipients"]:
            analysis["requires_approval"] = True
            analysis["approval_reason"] = f"Too many recipients: {len(recipients)}"
        
        # Check for auto-approve patterns
        for pattern in self.approval_thresholds["auto_approve_patterns"]:
            if pattern in content_lower:
                analysis["requires_approval"] = False
                analysis["suggested_action"] = "send_direct"
                break
        
        # Categorize email
        if "partnership" in content_lower or "collaboration" in content_lower:
            analysis["category"] = "partnership"
            analysis["requires_approval"] = True
        elif "invoice" in content_lower or "payment" in content_lower:
            analysis["category"] = "financial"
            analysis["requires_approval"] = True
        elif "support" in content_lower or "help" in content_lower:
            analysis["category"] = "support"
            analysis["suggested_action"] = "draft_response"
        elif "meeting" in content_lower or "schedule" in content_lower:
            analysis["category"] = "meeting"
            analysis["suggested_action"] = "draft_response"
        
        return analysis

    def draft_response(self, email_data: Dict, analysis: Dict) -> str:
        """Draft an appropriate response based on email analysis."""
        metadata = email_data["metadata"]
        body = email_data["body"]
        
        # Generate context-aware response
        category = analysis["category"]
        
        responses = {
            "partnership": f"""Dear {metadata.get('from', 'Sender')},

Thank you for reaching out regarding the partnership opportunity mentioned in your email: "{analysis['subject']}".

I've reviewed your proposal and am interested in exploring this further. Could we schedule a call next week to discuss the details?

Please let me know your availability.

Best regards,
AI Employee Assistant""",
            
            "financial": f"""Dear {metadata.get('from', 'Sender')},

Thank you for your email regarding: "{analysis['subject']}".

I've received your message and it has been forwarded to our accounting department for processing. We will respond within 2 business days.

Best regards,
AI Employee Assistant""",
            
            "support": f"""Dear {metadata.get('from', 'Sender')},

Thank you for contacting us. I understand you need assistance.

I've reviewed your request and am working on a solution. I'll get back to you with a resolution within 24 hours.

If this is urgent, please don't hesitate to follow up.

Best regards,
AI Employee Assistant""",
            
            "meeting": f"""Dear {metadata.get('from', 'Sender')},

Thank you for your email regarding scheduling a meeting.

I'd be happy to arrange a time to discuss "{analysis['subject']}". Could you please share your availability for next week?

Looking forward to our conversation.

Best regards,
AI Employee Assistant""",
            
            "general": f"""Dear {metadata.get('from', 'Sender')},

Thank you for your email: "{analysis['subject']}".

I've received your message and will respond with more details shortly.

Best regards,
AI Employee Assistant"""
        }
        
        return responses.get(category, responses["general"])

    def create_approval_request(self, email_data: Dict, analysis: Dict, draft: str) -> Path:
        """Create an approval request file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_file = self.pending_approval / f"APPROVAL_{timestamp}_{Path(email_data['file_path']).stem}.md"
        
        approval_content = f"""---
type: email_approval
created: {datetime.now().isoformat()}
status: pending
category: {analysis['category']}
reason: {analysis['approval_reason']}
original_from: {analysis['from']}
original_subject: {analysis['subject']}
---

# Email Approval Request

## Reason for Approval
{analysis['approval_reason']}

## Original Email
**From:** {analysis['from']}
**Subject:** {analysis['subject']}
**Priority:** {analysis['priority']}

---

{email_data['content']}

---

## Proposed Response

{draft}

---

## Action Required

Please review and:
- Move to `../Approved/Emails/` to send
- Move to `../Rejected/` to decline
- Add comments for modifications

**File:** {approval_file.name}
"""
        
        approval_file.write_text(approval_content, encoding='utf-8')
        logger.info(f"Created approval request: {approval_file}")
        
        return approval_file

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email via Gmail MCP server."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would send email to {to}")
            logger.info(f"[DRY RUN] Subject: {subject}")
            return True
        
        try:
            # Use Gmail MCP server
            from mcp.email.server import EmailMCPServer
            
            server = EmailMCPServer()
            result = server.send_email({
                "to": to,
                "subject": subject,
                "body": body
            })
            
            logger.info(f"Email sent successfully to {to}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def process_email(self, file_path: Path) -> Dict:
        """Process a single email file."""
        logger.info(f"Processing email: {file_path.name}")
        
        try:
            # Parse email
            email_data = self.parse_email_file(file_path)
            
            # Analyze email
            analysis = self.analyze_email(email_data)
            logger.info(f"Analysis: Category={analysis['category']}, Approval={analysis['requires_approval']}")
            
            # Draft response
            draft = self.draft_response(email_data, analysis)
            
            if analysis["requires_approval"]:
                # Create approval request
                approval_file = self.create_approval_request(email_data, analysis, draft)
                
                result = {
                    "status": "pending_approval",
                    "file": str(file_path),
                    "approval_file": str(approval_file),
                    "reason": analysis["approval_reason"]
                }
            else:
                # Send or draft
                to_address = email_data["metadata"].get("from", "")
                subject = f"Re: {analysis['subject']}"
                
                if self.dry_run:
                    # Save draft
                    draft_file = self.drafts / f"DRAFT_{file_path.stem}.md"
                    draft_file.write_text(f"""---
to: {to_address}
subject: {subject}
created: {datetime.now().isoformat()}
---

{draft}
""", encoding='utf-8')
                    
                    result = {
                        "status": "draft_created",
                        "file": str(file_path),
                        "draft_file": str(draft_file)
                    }
                else:
                    # Send email
                    success = self.send_email(to_address, subject, draft)
                    
                    if success:
                        # Move to Done
                        done_file = self.done / file_path.name
                        file_path.rename(done_file)
                        
                        result = {
                            "status": "sent",
                            "file": str(file_path),
                            "to": to_address
                        }
                    else:
                        result = {
                            "status": "failed",
                            "file": str(file_path),
                            "error": "Email send failed"
                        }
            
            # Log action
            self.log_action(email_data, analysis, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing email {file_path.name}: {e}")
            return {
                "status": "error",
                "file": str(file_path),
                "error": str(e)
            }

    def log_action(self, email_data: Dict, analysis: Dict, result: Dict):
        """Log the email processing action."""
        log_file = self.logs / f"email_log_{datetime.now().strftime('%Y%m%d')}.json"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "email": {
                "from": analysis["from"],
                "subject": analysis["subject"],
                "category": analysis["category"]
            },
            "analysis": analysis,
            "result": result
        }
        
        # Append to daily log
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except:
                logs = []
        
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))

    def process_all_emails(self) -> List[Dict]:
        """Process all emails in the needs action folder."""
        results = []
        
        # Check both email directory and root needs action
        email_files = []
        if self.email_dir.exists():
            email_files.extend(self.email_dir.glob("*.md"))
        email_files.extend(self.needs_action.glob("EMAIL_*.md"))
        
        logger.info(f"Found {len(email_files)} email files to process")
        
        for email_file in email_files:
            result = self.process_email(email_file)
            results.append(result)
        
        return results

    def generate_report(self, results: List[Dict]) -> str:
        """Generate a processing report."""
        report = f"""# Email Specialist Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Dry Run:** {self.dry_run}

## Summary

| Status | Count |
|--------|-------|
| Sent | {sum(1 for r in results if r['status'] == 'sent')} |
| Draft Created | {sum(1 for r in results if r['status'] == 'draft_created')} |
| Pending Approval | {sum(1 for r in results if r['status'] == 'pending_approval')} |
| Failed | {sum(1 for r in results if r['status'] == 'failed')} |
| Error | {sum(1 for r in results if r['status'] == 'error')} |

## Details

"""
        
        for result in results:
            report += f"### {Path(result['file']).name}\n"
            report += f"- **Status:** {result['status']}\n"
            if 'reason' in result:
                report += f"- **Reason:** {result['reason']}\n"
            if 'error' in result:
                report += f"- **Error:** {result['error']}\n"
            report += "\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Email Specialist Agent')
    parser.add_argument('--vault', default='./vault', help='Vault path')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--no-dry-run', action='store_false', dest='dry_run', help='Live mode')
    parser.add_argument('--file', type=str, help='Process specific file')
    parser.add_argument('--report', action='store_true', help='Generate report')

    args = parser.parse_args()

    agent = EmailSpecialistAgent(vault_path=args.vault, dry_run=args.dry_run)

    if args.file:
        # Process specific file
        result = agent.process_email(Path(args.file))
        print(f"\nResult: {result}")
    else:
        # Process all emails
        results = agent.process_all_emails()
        
        if args.report:
            report = agent.generate_report(results)
            print(report)
            
            # Save report
            report_file = Path(args.vault) / "Logs" / f"email_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            report_file.write_text(report)
            print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    main()
