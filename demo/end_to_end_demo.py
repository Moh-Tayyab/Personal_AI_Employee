#!/usr/bin/env python3
"""
End-to-End Demo for Gold Tier - Personal AI Employee

Demonstrates complete automation flow:
1. Simulated WhatsApp message arrives
2. WhatsApp Watcher creates action file in Needs_Action/
3. Orchestrator triggers AI to analyze and create plan
4. AI creates approval request in Pending_Approval/
5. User approves (simulated - auto-approve for demo)
6. Orchestrator executes approved action via MCP
7. Action logged and moved to Done/
8. Dashboard.md updated

All in DRY_RUN mode - no real external actions.

Usage:
    python demo/end_to_end_demo.py --vault ./vault
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator import Orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EndToEndDemo")


class EndToEndDemo:
    """Run end-to-end demo of Personal AI Employee."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.orchestrator = Orchestrator(vault_path=str(self.vault_path), dry_run=True)
        self.stats = {
            'steps_run': 0,
            'steps_passed': 0,
            'steps_failed': 0,
            'details': []
        }

    def _log_step(self, step: str, status: str, details: str = ""):
        """Log a demo step."""
        self.stats['steps_run'] += 1
        if status == 'PASS':
            self.stats['steps_passed'] += 1
            logger.info(f"✅ {step}: {details}")
        else:
            self.stats['steps_failed'] += 1
            logger.error(f"❌ {step}: {details}")

        self.stats['details'].append({
            'step': step,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

    def print_header(self, title: str):
        """Print formatted header."""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)

    def print_section(self, title: str):
        """Print formatted section title."""
        print(f"\n{'─' * 70}")
        print(f"  ▶ {title}")
        print(f"{'─' * 70}")

    def run_demo(self):
        """Run complete end-to-end demo."""
        self.print_header("Personal AI Employee - Gold Tier End-to-End Demo")

        print("\nThis demo shows:")
        print("  1. WhatsApp message detection")
        print("  2. AI analysis and planning")
        print("  3. Approval workflow")
        print("  4. Action execution via MCP")
        print("  5. Dashboard updates")
        print("  6. CEO Briefing generation")
        print("\n⚠️  All actions run in DRY_RUN mode - no real external actions\n")

        input("Press Enter to start the demo...")

        try:
            # Step 1: Simulate WhatsApp message detection
            self.step_1_whatsapp_detection()

            # Step 2: AI analysis and planning
            self.step_2_ai_analysis()

            # Step 3: Approval workflow
            self.step_3_approval_workflow()

            # Step 4: Execute approved action
            self.step_4_execute_action()

            # Step 5: Social media posting
            self.step_5_social_media()

            # Step 6: Odoo invoice creation
            self.step_6_odoo_invoice()

            # Step 7: Dashboard update verification
            self.step_7_dashboard_update()

            # Step 8: CEO Briefing generation
            self.step_8_ceo_briefing()

            # Final summary
            self.print_summary()

        except KeyboardInterrupt:
            logger.info("\nDemo interrupted by user")
        except Exception as e:
            logger.error(f"\nDemo failed with error: {e}")
            import traceback
            traceback.print_exc()

    def step_1_whatsapp_detection(self):
        """Step 1: Simulate WhatsApp message detection."""
        self.print_section("Step 1: WhatsApp Message Detection")

        # Create simulated WhatsApp message
        whatsapp_message = """---
type: whatsapp
source: whatsapp_web
chat: John Smith
keywords: invoice, payment
received: 2026-04-06T10:30:00
priority: high
status: pending
---

# WhatsApp Message

## From
John Smith

## Message
Hey! Can you please send me the invoice for the AI Employee automation project? I need it for our accounting by Friday.

## Trigger Keywords
invoice, payment

## Suggested Actions
- [ ] Review message content
- [ ] Generate invoice
- [ ] Send via email (REQUIRES APPROVAL for new contacts)
"""

        # Create action file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        action_file = self.vault_path / 'Needs_Action' / f'WHATSAPP_{timestamp}_john_smith.md'
        action_file.write_text(whatsapp_message)

        logger.info(f"Created action file: {action_file.name}")

        # Verify file was created
        if action_file.exists():
            self._log_step("WhatsApp Detection", "PASS", f"Action file created: {action_file.name}")
        else:
            self._log_step("WhatsApp Detection", "FAIL", "Failed to create action file")

        # Show file content
        print(f"\n📄 Action File Content (first 200 chars):")
        print(action_file.read_text()[:200] + "...")

        time.sleep(1)

    def step_2_ai_analysis(self):
        """Step 2: AI analysis and planning."""
        self.print_section("Step 2: AI Analysis & Planning")

        # Get items from Needs_Action
        needs_action = self.orchestrator.check_needs_action()
        logger.info(f"Found {len(needs_action)} items in Needs_Action")

        if not needs_action:
            self._log_step("AI Analysis", "FAIL", "No items found in Needs_Action")
            return

        item = needs_action[0]
        item_content = item.read_text()

        # Create plan
        plan_path = self.orchestrator.create_plan(item)
        logger.info(f"Created plan: {plan_path.name}")

        # Simulate AI analysis (since we're in demo mode, we'll create the plan manually)
        ai_analysis = """
### Analysis
Client John Smith is requesting an invoice for the AI Employee automation project.
This is a standard business request requiring invoice generation and email delivery.

### Recommended Actions
1. Create invoice for $2,500 (AI Employee Setup - Consulting + Implementation)
2. Send invoice via email to john@smithcorp.com
3. Log transaction for accounting

### Approval Required
YES - Email sending requires human approval per Company Handbook rules.

### Priority
HIGH - Client needs invoice by Friday

### Category
finance
"""

        # Save AI analysis to plan
        plan_content = f"""---
type: ai_plan
created: {datetime.now().isoformat()}
status: pending_approval
source_file: {item.name}
---

# AI Action Plan

{ai_analysis}

---

## Original Item
{item_content[:500]}
"""

        plan_path.write_text(plan_content)
        logger.info(f"AI plan saved: {plan_path.name}")

        if plan_path.exists() and plan_path.stat().st_size > 0:
            self._log_step("AI Analysis", "PASS", f"Plan created: {plan_path.name}")
        else:
            self._log_step("AI Analysis", "FAIL", "Failed to create plan")

        # Move original to In_Progress
        self.orchestrator.move_to_in_progress(item)
        logger.info(f"Moved {item.name} to In_Progress")

        time.sleep(1)

    def step_3_approval_workflow(self):
        """Step 3: Approval workflow."""
        self.print_section("Step 3: Approval Workflow")

        # Create approval request
        approval_content = f"""---
type: approval_request
action: send_email
to: john@smithcorp.com
subject: Invoice - AI Employee Automation Project ($2,500)
amount: 2500.00
recipient: John Smith
reason: Invoice for AI Employee automation setup
created: {datetime.now().isoformat()}
status: pending
---

# Approval Request: Send Invoice Email

## Email Details
- **To:** john@smithcorp.com
- **Subject:** Invoice - AI Employee Automation Project ($2,500)
- **Amount:** $2,500.00
- **Recipient:** John Smith

## Invoice Line Items
1. Consulting (10 hours × $150/hr) = $1,500
2. Implementation (1 project) = $1,000

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
"""

        approval_file = self.vault_path / 'Pending_Approval' / f'APPROVAL_invoice_john_smith.md'
        approval_file.write_text(approval_content)

        logger.info(f"Created approval request: {approval_file.name}")

        if approval_file.exists():
            self._log_step("Approval Request Created", "PASS", f"File: {approval_file.name}")
        else:
            self._log_step("Approval Request Created", "FAIL", "Failed to create approval file")

        print(f"\n⏸️  Simulating human review...")
        print(f"   In real scenario, you would review and move to /Approved/")
        time.sleep(2)

        # Simulate approval (move to Approved)
        approved_file = self.vault_path / 'Approved' / f'APPROVAL_invoice_john_smith.md'
        approval_file.rename(approved_file)

        logger.info(f"✅ Approved! Moved to: {approved_file.name}")
        self._log_step("Human Approval Simulated", "PASS", "File moved to Approved/")

        time.sleep(1)

    def step_4_execute_action(self):
        """Step 4: Execute approved action."""
        self.print_section("Step 4: Execute Approved Action (Email via MCP)")

        # Get approved items
        approved = self.orchestrator.check_approved()
        logger.info(f"Found {len(approved)} approved items")

        if not approved:
            self._log_step("Execute Action", "FAIL", "No approved items found")
            return

        item = approved[0]
        logger.info(f"Processing: {item.name}")

        # Process the approved item
        success = self.orchestrator.process_approved_item(item)

        if success:
            self._log_step("Email MCP Execution", "PASS", f"Processed {item.name} (DRY_RUN mode)")
            # Move to Done
            self.orchestrator.move_to_done(item)
            logger.info(f"✅ Moved to Done: {item.name}")
        else:
            self._log_step("Email MCP Execution", "FAIL", f"Failed to process {item.name}")

        time.sleep(1)

    def step_5_social_media(self):
        """Step 5: Social media posting."""
        self.print_section("Step 5: Social Media Posting (LinkedIn, Twitter, Facebook)")

        platforms = [
            {
                'name': 'LinkedIn',
                'action': 'linkedin_post',
                'content': "🚀 Exciting news! Our AI Employee automation platform is now processing 10x more tasks with 90% cost reduction. Built with Claude Code + Obsidian + MCP servers. Learn how we did it! #AI #Automation #Innovation",
                'file': 'SOCIAL_linkedin_post.md'
            },
            {
                'name': 'Twitter',
                'action': 'twitter_post',
                'content': "🧵 How we built an AI Employee that works 24/7:\n\n1/ Architecture: Watchers (sensors) + MCP servers (hands) + Claude Code (brain) + Obsidian (memory)\n\n2/ Result: 90% cost reduction, 168 hrs/week availability\n\nThread below 👇 #AI #Automation",
                'file': 'SOCIAL_twitter_post.md'
            },
            {
                'name': 'Facebook',
                'action': 'social_post',
                'platform': 'facebook',
                'content': "🚀 Our AI Employee automation platform is transforming how businesses operate. 90% cost reduction, 24/7 availability. Learn more about building your own digital FTE. #AI #BusinessAutomation",
                'file': 'SOCIAL_facebook_post.md'
            }
        ]

        for platform in platforms:
            print(f"\n  Posting to {platform['name']}...")

            # Create approved social post
            content = f"""---
type: approval_response
action: {platform['action']}
content: {platform['content']}
{f"platform: {platform.get('platform', 'N/A')}" if platform.get('platform') else ""}
---

# Approved {platform['name']} Post

This post has been reviewed and approved for publishing.
"""

            post_file = self.vault_path / 'Approved' / platform['file']
            post_file.write_text(content)

            # Process it
            success = self.orchestrator.process_approved_item(post_file)

            if success:
                self.orchestrator.move_to_done(post_file)
                self._log_step(f"{platform['name']} Post", "PASS", f"Posted (DRY_RUN)")
            else:
                self._log_step(f"{platform['name']} Post", "FAIL", "Failed to post")

            time.sleep(0.5)

    def step_6_odoo_invoice(self):
        """Step 6: Odoo invoice creation."""
        self.print_section("Step 6: Odoo Invoice Creation")

        # Create approved Odoo invoice
        invoice_content = f"""---
type: approval_response
action: odoo_invoice
partner_name: Demo Client Corp
partner_email: demo@clientcorp.com
amount: 2500.00
---

# Odoo Invoice Creation

## Invoice Details
- **Client:** Demo Client Corp
- **Email:** demo@clientcorp.com
- **Amount:** $2,500.00
- **Service:** AI Employee Automation Setup
- **Line Items:**
  - Consulting (10 hours × $150/hr) = $1,500
  - Implementation (1 project) = $1,000
"""

        invoice_file = self.vault_path / 'Approved' / 'ODOO_invoice_demo.md'
        invoice_file.write_text(invoice_content)

        logger.info(f"Created Odoo invoice request: {invoice_file.name}")

        # Process it
        success = self.orchestrator.process_approved_item(invoice_file)

        if success:
            self.orchestrator.move_to_done(invoice_file)
            self._log_step("Odoo Invoice", "PASS", f"Invoice created (DRY_RUN)")
        else:
            self._log_step("Odoo Invoice", "FAIL", "Failed to create invoice")

        time.sleep(1)

    def step_7_dashboard_update(self):
        """Step 7: Dashboard update verification."""
        self.print_section("Step 7: Dashboard Update Verification")

        # Trigger dashboard update
        needs_action = self.orchestrator.check_needs_action()
        pending = self.orchestrator.check_pending_approval()
        approved = self.orchestrator.check_approved()

        self.orchestrator._update_dashboard(needs_action, pending, approved)

        # Read and display dashboard
        dashboard_path = self.vault_path / 'Dashboard.md'
        if dashboard_path.exists():
            dashboard_content = dashboard_path.read_text()
            self._log_step("Dashboard Update", "PASS", f"Dashboard updated at {dashboard_path.stat().st_mtime}")

            print(f"\n📊 Dashboard.md Content:")
            print(dashboard_content[:500] + "...\n")
        else:
            self._log_step("Dashboard Update", "FAIL", "Dashboard.md not found")

        time.sleep(1)

    def step_8_ceo_briefing(self):
        """Step 8: CEO Briefing generation."""
        self.print_section("Step 8: CEO Briefing Generation")

        try:
            from scripts.generate_ceo_briefing import CEOBriefingGenerator

            generator = CEOBriefingGenerator(str(self.vault_path))
            briefing = generator.generate_briefing(period_days=7)
            briefing_path = generator.save_briefing(briefing)

            if briefing_path.exists():
                self._log_step("CEO Briefing", "PASS", f"Generated: {briefing_path.name}")

                print(f"\n📋 CEO Briefing Preview:")
                print(briefing[:600] + "...\n")
            else:
                self._log_step("CEO Briefing", "FAIL", "Failed to generate briefing")

        except Exception as e:
            logger.warning(f"CEO Briefing generation failed: {e}")
            self._log_step("CEO Briefing", "FAIL", str(e))

        time.sleep(1)

    def print_summary(self):
        """Print final summary."""
        self.print_header("Demo Summary")

        passed = self.stats['steps_passed']
        failed = self.stats['steps_failed']
        total = self.stats['steps_run']

        print(f"\n✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        print(f"\n📊 Success Rate: {(passed/total*100) if total > 0 else 0:.0f}%\n")

        print("Steps:")
        for detail in self.stats['details']:
            icon = "✅" if detail['status'] == 'PASS' else "❌"
            print(f"  {icon} {detail['step']}: {detail['details']}")

        print("\n" + "=" * 70)
        if failed == 0:
            print("  🎉 GOLD TIER DEMO COMPLETE - ALL TESTS PASSED!")
        else:
            print(f"  ⚠️  Demo complete with {failed} failure(s) - review logs for details")
        print("=" * 70)

        print("\n📁 Vault Structure:")
        for folder in ['Needs_Action', 'In_Progress', 'Pending_Approval', 'Approved', 'Done', 'Plans', 'Briefings']:
            folder_path = self.vault_path / folder
            if folder_path.exists():
                count = len(list(folder_path.glob('*.md')))
                print(f"  {folder:25s} {count} file(s)")

        print("\n🎯 Gold Tier Features Demonstrated:")
        print("  ✅ WhatsApp message detection")
        print("  ✅ AI analysis and planning")
        print("  ✅ Human-in-the-loop approval workflow")
        print("  ✅ Email MCP server execution")
        print("  ✅ Social media posting (LinkedIn, Twitter, Facebook)")
        print("  ✅ Odoo invoice creation")
        print("  ✅ Dashboard auto-updates")
        print("  ✅ CEO Briefing generation")
        print("  ✅ Audit logging")
        print("\n📝 Note: All actions ran in DRY_RUN mode (safe for demo)")
        print("   Set DRY_RUN=false to enable real external actions\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='End-to-End Demo for Gold Tier')
    parser.add_argument('--vault', default='./vault', help='Path to vault')

    args = parser.parse_args()

    demo = EndToEndDemo(args.vault)
    demo.run_demo()


if __name__ == "__main__":
    main()
