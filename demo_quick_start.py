#!/usr/bin/env python3
"""
Personal AI Employee - Quick Start Demo
This script demonstrates core capabilities without requiring full setup
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import time

def create_sample_vault():
    """Create a sample vault structure to demonstrate the system"""
    print("🚀 Creating sample vault structure...")

    vault_path = Path("./demo_vault")
    vault_path.mkdir(exist_ok=True)

    # Create essential directories
    dirs = [
        "Needs_Action",
        "Plans",
        "Pending_Approval",
        "Approved",
        "Done",
        "Logs",
        "Briefings",
        "Drafts",
        "Scheduled",
        "secrets"
    ]

    for dir_name in dirs:
        (vault_path / dir_name).mkdir(exist_ok=True)

    # Create sample configuration files
    handbook_content = """
# Company Handbook for Personal AI Employee

## Autonomy Levels
- LOW: Basic email responses, scheduling
- MEDIUM: Social media posts, basic research
- HIGH: Vendor communications, routine purchases under $500
- CRITICAL: All payments over $500, legal documents, major contracts

## Decision Guidelines
1. Always prioritize customer satisfaction
2. Respond to urgent emails within 2 hours
3. Escalate to human for amounts over $500
4. Schedule non-urgent tasks for business hours
"""
    (vault_path / "Company_Handbook.md").write_text(handbook_content.strip())

    goals_content = """
# Business Goals

## Monthly Targets
- Revenue: $25,000
- New Clients: 3
- Customer Satisfaction: 4.5/5.0

## Quarterly Objectives
1. Expand service offerings
2. Improve automation efficiency by 25%
3. Increase customer retention to 90%

## KPIs to Track
- Email response time
- Lead conversion rate
- Invoice collection rate
"""
    (vault_path / "Business_Goals.md").write_text(goals_content.strip())

    dashboard_content = f"""
# Personal AI Employee Dashboard
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Status
- 🟢 Running
- 📨 Email watcher: Active
- 🤖 Claude API: Connected
- 🔐 Approval system: Ready

## Today's Activity
- Items processed: 0
- Actions taken: 0
- Approvals needed: 0
- Errors: 0
"""
    (vault_path / "Dashboard.md").write_text(dashboard_content.strip())

    print(f"✅ Created vault at {vault_path}")
    return vault_path

def simulate_email_receipt(vault_path):
    """Simulate receiving an email that needs processing"""
    print("\n📧 Simulating email receipt...")

    needs_action = vault_path / "Needs_Action"

    # Sample email content
    email_content = f"""---
type: email
sender: vendor@supplier.com
subject: Invoice #INV-2026-0316 for Consulting Services
priority: high
received: {datetime.now().isoformat()}
tags: [finance, invoice, payment]
---

# Invoice from vendor@supplier.com

**Subject:** Invoice #INV-2026-0316 for Consulting Services

**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

Dear Muhammad,

Please find attached invoice #INV-2026-0316 for consulting services rendered in February.

**Amount:** $1,250.00
**Due Date:** {datetime.now().strftime('%Y-%m-%d')}
**Details:** AI system consultation and setup

Payment can be made via bank transfer or credit card.

Best regards,
Supplier Team

---

**Action Required:** Review invoice and process payment if services were rendered.
"""

    email_filename = f"EMAIL_invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    (needs_action / email_filename).write_text(email_content)

    print(f"✅ Created email: {email_filename}")
    print(f"   Located at: {needs_action / email_filename}")

    return needs_action / email_filename

def simulate_ai_reasoning(vault_path, email_file):
    """Simulate Claude's reasoning process"""
    print(f"\n🤖 Simulating Claude AI reasoning...")

    # Read the email content
    with open(email_file, 'r') as f:
        email_content = f.read()

    print("   Reading email content...")
    time.sleep(1)

    print("   Loading company handbook...")
    handbook_path = vault_path / "Company_Handbook.md"
    with open(handbook_path, 'r') as f:
        handbook = f.read()

    print("   Applying decision rules...")
    time.sleep(1)

    # Determine if approval is needed
    needs_approval = True  # Since this is an invoice over $500
    action_decision = "Payment required - move to approval queue"

    print(f"   Decision: {action_decision}")
    print(f"   Approval needed: {'Yes' if needs_approval else 'No'}")

    return needs_approval, action_decision

def create_action_plan(vault_path, email_file, decision):
    """Create an action plan based on AI reasoning"""
    print(f"\n📝 Creating action plan...")

    plans_path = vault_path / "Plans"

    # Create plan content
    plan_content = f"""---
type: ai_plan
created: {datetime.now().isoformat()}
status: pending_approval
email_file: {email_file.name}
decision: needs_human_approval
confidence: high
---

# AI Action Plan for Invoice Processing

## Email Details
- **Sender:** vendor@supplier.com
- **Subject:** Invoice #INV-2026-0316 for Consulting Services
- **Amount:** $1,250.00
- **Due:** {datetime.now().strftime('%Y-%m-%d')}

## Analysis
The email contains an invoice for consulting services. The amount is $1,250.00 which exceeds the $500 threshold for automatic payment according to Company Handbook section CRITICAL.

## Decision
**Requires Human Approval** - Amount exceeds autonomy threshold.

## Recommended Actions
1. Verify services were rendered as described
2. Confirm vendor legitimacy
3. Approve or reject payment

## Relevant Rules
From Company Handbook - CRITICAL level: 'All payments over $500 require human approval'

## Tools Needed
- MCP Email server (for verification emails)
- MCP Odoo server (for vendor lookup)
"""

    plan_filename = f"PLAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}_invoice_approval.md"
    (plans_path / plan_filename).write_text(plan_content)

    print(f"✅ Created action plan: {plan_filename}")
    return plans_path / plan_filename

def simulate_approval_process(vault_path, email_file):
    """Move email to approval queue"""
    print(f"\n🔐 Moving to approval queue...")

    pending_approval = vault_path / "Pending_Approval"

    # Copy the email to pending approval
    with open(email_file, 'r') as f:
        email_content = f.read()

    approval_content = f"""{email_content}

---
## Approval Status: PENDING
- **Moved from:** Needs_Action
- **Reason:** Amount exceeds $500 threshold
- **Decision:** Payment requires human approval
- **Recommendation:** Verify services before approving
---
"""

    approval_filename = f"APPROVAL_{email_file.name}"
    (pending_approval / approval_filename).write_text(approval_content)

    # Remove from needs action
    email_file.unlink()

    print(f"✅ Moved to approval queue: {approval_filename}")

    # Simulate webhook notification
    print("🌐 Sending webhook notification to Slack/Discord...")
    print("   Message: '⚠️ Approval needed: Invoice from vendor@supplier.com ($1,250.00)'")

    return pending_approval / approval_filename

def demonstrate_ceo_briefing(vault_path):
    """Create a sample CEO briefing"""
    print(f"\n📋 Generating CEO briefing...")

    briefings_path = vault_path / "Briefings"

    briefing_content = f"""---
type: ceo_briefing
date: {datetime.now().strftime('%Y-%m-%d')}
generated: {datetime.now().isoformat()}
---

# Monday Morning CEO Briefing - {datetime.now().strftime('%A, %B %d, %Y')}

## 📊 Today's Summary
- **New Items:** 1 (Invoice requiring approval)
- **Awaiting Approval:** 1 items
- **Completed Yesterday:** 0 items
- **System Status:** Operational

## ⚠️ Action Required
- **Invoice Approval Needed:** $1,250.00 from vendor@supplier.com
  - Invoice ID: INV-2026-0316
  - Due: {datetime.now().strftime('%Y-%m-%d')}
  - Located in Pending_Approval folder

## 📈 Weekly Metrics
- **Processed:** 0 items
- **Escalated:** 1 items
- **Errors:** 0
- **AI Engagement:** High (complex decision made)

## 💡 Efficiency Tip
Consider increasing autonomy threshold for known vendors to reduce approval burden.

---
*Personal AI Employee*
*Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    briefing_filename = f"CEOBriefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    (briefings_path / briefing_filename).write_text(briefing_content)

    print(f"✅ Created CEO briefing: {briefing_filename}")

def show_vault_summary(vault_path):
    """Show current vault state"""
    print(f"\n🗂️  Current vault status:")

    for folder in ["Needs_Action", "Pending_Approval", "Plans", "Done"]:
        folder_path = vault_path / folder
        if folder_path.exists():
            files = list(folder_path.glob("*.md"))
            print(f"   {folder}: {len(files)} files")

    print(f"\n📁 Vault structure:")
    for item in vault_path.iterdir():
        if item.is_dir():
            files = len(list(item.glob("*.md")))
            print(f"   📁 {item.name}: {files} files")

def main():
    """Run the demo"""
    print("🌟 Personal AI Employee - Quick Demo")
    print("=" * 50)
    print()
    print("This demo shows how the Personal AI Employee processes real-world tasks")
    print("by combining Claude AI reasoning with automated workflows.")
    print()

    input("Press Enter to start the demo...")

    # Step 1: Create sample vault
    vault_path = create_sample_vault()

    input("\nPress Enter to simulate receiving an email...")

    # Step 2: Simulate receiving an email
    email_file = simulate_email_receipt(vault_path)

    input("\nPress Enter to see AI reasoning...")

    # Step 3: Simulate AI reasoning
    needs_approval, decision = simulate_ai_reasoning(vault_path, email_file)

    input("\nPress Enter to see the action plan...")

    # Step 4: Create action plan
    plan_file = create_action_plan(vault_path, email_file, decision)

    input("\nPress Enter to see the approval process...")

    # Step 5: Process approval if needed
    if needs_approval:
        approval_file = simulate_approval_process(vault_path, email_file)

    input("\nPress Enter to see the CEO briefing...")

    # Step 6: Generate CEO briefing
    demonstrate_ceo_briefing(vault_path)

    input("\nPress Enter to see the final vault status...")

    # Step 7: Show final state
    show_vault_summary(vault_path)

    print(f"\n🎉 Demo Complete!")
    print()
    print("Summary of what happened:")
    print("• An invoice email was received and placed in Needs_Action")
    print("• Claude AI analyzed the email using company rules")
    print("• Since amount exceeded $500, it required approval")
    print("• Action plan was created documenting the decision")
    print("• Email moved to Pending_Approval with notification")
    print("• CEO briefing generated with today's activities")
    print()
    print("This demonstrates the core Personal AI Employee workflow:")
    print("Receive → Analyze → Decide → Act (appropriately) → Report")

if __name__ == "__main__":
    main()