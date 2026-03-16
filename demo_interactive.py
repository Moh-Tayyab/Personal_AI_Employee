#!/usr/bin/env python3
"""
Personal AI Employee - Interactive Demo
Demonstrates the key capabilities of the Personal AI Employee system
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import time

def print_header(title):
    """Print a nicely formatted header"""
    print("\n" + "="*60)
    print(f"{title:^60}")
    print("="*60)

def print_section(title):
    """Print a section separator"""
    print(f"\n--- {title} ---\n")

def wait_for_demo():
    """Wait a moment for demo effect"""
    time.sleep(2)

def demo_vault_structure():
    """Demonstrate the vault structure"""
    print_section("VAULT STRUCTURE")

    vault_path = Path("./vault")
    if vault_path.exists():
        print("Current vault structure:")
        for item in vault_path.iterdir():
            item_type = "📁" if item.is_dir() else "📄"
            print(f"  {item_type} {item.name}")

        print("\nKey folders and their purposes:")
        print("  📁 Needs_Action/: Items requiring processing")
        print("  📁 Plans/: Generated action plans")
        print("  📁 Pending_Approval/: Items awaiting human approval")
        print("  📁 Approved/: Items approved for execution")
        print("  📁 Done/: Completed tasks")
        print("  📄 Dashboard.md: System status overview")
        print("  📄 Company_Handbook.md: AI rules and autonomy levels")
        print("  📄 Business_Goals.md: Revenue targets and KPIs")
    else:
        print("Vault directory not found. Creating sample structure...")
        vault_path.mkdir(exist_ok=True)

        # Create sample vault structure
        folders = ["Needs_Action", "Plans", "Pending_Approval", "Approved", "Done", "Logs", "Briefings"]
        for folder in folders:
            (vault_path / folder).mkdir(exist_ok=True)

        # Create sample files
        (vault_path / "Dashboard.md").write_text("# System Dashboard\n\nCurrent status: Operational")
        (vault_path / "Company_Handbook.md").write_text("# Company Handbook\n\nRules for AI operations")
        (vault_path / "Business_Goals.md").write_text("# Business Goals\n\nMonthly targets and KPIs")

        print("Sample vault structure created!")
        print("You can now see how the system organizes information.")

def demo_sample_item_processing():
    """Simulate processing of a sample item"""
    print_section("SIMULATED ITEM PROCESSING")

    print("Let's simulate receiving an email that needs processing...")
    time.sleep(1)

    # Create a sample email in Needs_Action
    needs_action_path = Path("./vault/Needs_Action")
    needs_action_path.mkdir(exist_ok=True)

    sample_email = {
        "type": "email",
        "sender": "client@example.com",
        "subject": "Project Proposal Review Needed",
        "body": "Hi Muhammad,\n\nWe'd like you to review our project proposal for the new AI employee system. Please let us know if you'd like to proceed.\n\nBest regards,\nClient Team",
        "received": datetime.now().isoformat(),
        "priority": "high"
    }

    email_filename = f"EMAIL_proposal_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    email_path = needs_action_path / email_filename

    email_content = f"""---
type: email
sender: client@example.com
subject: Project Proposal Review Needed
priority: high
received: {datetime.now().isoformat()}
processed: false
---

# Email from client@example.com

**Subject:** Project Proposal Review Needed

**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

Hi Muhammad,

We'd like you to review our project proposal for the new AI employee system. Please let us know if you'd like to proceed.

Best regards,
Client Team

---

**Action Required:** Analyze and respond appropriately based on company handbook and goals.
"""

    email_path.write_text(email_content)
    print(f"✅ Created sample email: {email_filename}")

    print("\nThe AI Employee would now:")
    print("1. Detect the new item in Needs_Action/")
    print("2. Analyze using Claude API with company context")
    print("3. Generate an action plan based on company handbook")
    print("4. Decide if human approval is needed")
    print("5. Either execute automatically or move to Pending_Approval/")

    wait_for_demo()

def demo_action_planning():
    """Simulate creation of an action plan"""
    print_section("ACTION PLAN GENERATION")

    print("The AI analyzes the email and creates an action plan...")
    time.sleep(1)

    plans_path = Path("./vault/Plans")
    plans_path.mkdir(exist_ok=True)

    plan_filename = f"PLAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}_EMAIL_proposal_review.md"
    plan_path = plans_path / plan_filename

    plan_content = f"""---
type: ai_plan
created: {datetime.now().isoformat()}
status: pending_execution
related_to: EMAIL_proposal_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md
---

# AI Action Plan

## Analysis
The client is requesting a review of their project proposal for an AI employee system. Based on the company handbook, we should evaluate proposals that align with our automation goals.

## Recommended Actions
1. **Research client**: Check if this client has worked with us before
2. **Evaluate proposal**: Assess technical feasibility and business value
3. **Request additional information**: Ask for project timeline and budget
4. **Schedule discussion**: Propose a meeting next week

## Approval Required
NO - This is within standard operating parameters per Company Handbook section 3.2

## Priority
HIGH - Client relations are important

## Category
BUSINESS_DEVELOPMENT

## Tools/Skills Needed
- MCP Email server to send response
- MCP LinkedIn to research client profile
- Claude API for analysis

## Context from Company Handbook
According to section 2.1: 'Engage with clients who propose projects aligned with our automation goals.'
Section 3.2: 'Proposals under $50k can be approved automatically.'
"""

    plan_path.write_text(plan_content)
    print(f"✅ Created action plan: {plan_filename}")

    print("\nThe plan shows:")
    print("- How the AI thinks through the problem")
    print("- What actions it recommends")
    print("- Whether approval is needed")
    print("- What tools it will use")
    print("- Reference to company guidelines")

def demo_approval_workflow():
    """Demonstrate the approval workflow"""
    print_section("APPROVAL WORKFLOW")

    # Create a sensitive action that needs approval
    pending_path = Path("./vault/Pending_Approval")
    pending_path.mkdir(exist_ok=True)

    approval_filename = f"APPROVAL_payment_to_vendor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    approval_path = pending_path / approval_filename

    approval_content = f"""---
type: approval_request
created: {datetime.now().isoformat()}
status: pending
critical: true
---

# Payment Approval Request

## Transaction Details
- **Vendor:** ACME Services Inc.
- **Amount:** $2,450.00
- **Description:** Annual software license renewal
- **Due Date:** {datetime.now().strftime('%Y-%m-%d')}

## AI Recommendation
Based on vendor history and business necessity, this payment should be processed. The renewal is critical for continued operations.

## Approval Options
1. **APPROVE**: Move to Approved/ folder to execute
2. **REJECT**: Move to Rejected/ folder
3. **REQUEST_INFO**: Move to Needs_Info/ folder for clarification

## Notification
Webhook notification sent to Slack channel #finance-alerts
"""

    approval_path.write_text(approval_content)
    print(f"✅ Created approval request: {approval_filename}")

    print("\nThe approval workflow ensures:")
    print("1. Critical actions require human oversight")
    print("2. Notifications via Slack/Discord webhooks")
    print("3. Clear approval process through file movement")
    print("4. Audit trail of all decisions")

def demo_ceo_briefing():
    """Showcase the CEO briefing capability"""
    print_section("CEO BRIEFING GENERATOR")

    briefings_path = Path("./vault/Briefings")
    briefings_path.mkdir(exist_ok=True)

    briefing_filename = f"2026-03-16_Monday_Briefing.md"
    briefing_path = briefings_path / briefing_filename

    briefing_content = f"""---
type: ceo_briefing
date: {datetime.now().strftime('%Y-%m-%d')}
generated: {datetime.now().isoformat()}
author: Personal_AI_Employee
---

# Monday Morning CEO Briefing - {datetime.now().strftime('%A, %B %d, %Y')}

## 📊 Revenue Summary
- **Weekly Revenue:** $12,450 (↑ 12% from last week)
- **Pipeline Value:** $89,200
- **Active Projects:** 7

## ✅ Completed Tasks
- Responded to 23 client emails
- Posted 3 LinkedIn updates
- Processed 12 routine approvals
- Updated CRM records

## ⚠️ Bottlenecks Identified
- Invoice #INV-2026-0315 delayed (awaiting client approval)
- LinkedIn ad campaign needs optimization
- New lead qualification backlog (4 items)

## 🎯 This Week's Focus
1. Follow up on outstanding invoices
2. Optimize underperforming marketing campaigns
3. Clear lead qualification backlog
4. Prepare quarterly forecast

## 📈 Performance Metrics
- **Email Response Time:** Avg 2.3 hours (Target: <4 hours)
- **Lead Conversion Rate:** 15% (Target: >12%)
- **Customer Satisfaction:** 4.7/5.0

## 💡 Proactive Suggestions
1. Schedule meeting with marketing team for campaign review
2. Implement lead scoring system to prioritize qualification
3. Negotiate extended terms with key supplier to improve cash flow

---
*Generated automatically by Personal AI Employee*
*Next briefing: Tomorrow at 8:00 AM*
"""

    briefing_path.write_text(briefing_content)
    print(f"✅ Created CEO briefing: {briefing_filename}")

    print("\nThe CEO briefing demonstrates:")
    print("- Automated business intelligence gathering")
    print("- Revenue and performance tracking")
    print("- Proactive bottleneck identification")
    print("- Strategic recommendations")
    print("- Transformation from reactive assistant to proactive partner")

def demo_mcp_servers():
    """Demonstrate MCP server concepts"""
    print_section("MCP SERVERS - EXTENDED CAPABILITIES")

    print("MCP (Model Context Protocol) servers extend Claude's capabilities:")
    print("")

    print("📧 Email MCP Server:")
    print("  • send_email({'to': 'user@email.com', 'subject': 'Hello', 'body': 'Message'})")
    print("  • search_emails({'query': 'invoice from ACME', 'max_results': 5})")
    print("  • draft_email({'to': 'user@email.com', 'subject': 'Draft', 'body': 'Content'})")
    print("")

    print("👔 LinkedIn MCP Server:")
    print("  • create_post({'content': 'Exciting project update!', 'media_path': '/img.jpg'})")
    print("  • get_profile({})")
    print("  • schedule_post({'content': 'Later post', 'scheduled_time': '2026-03-17T14:00:00Z'})")
    print("")

    print("💰 Odoo MCP Server:")
    print("  • get_invoices({})")
    print("  • create_invoice({'customer_id': 123, 'amount': 500.00})")
    print("  • get_account_balance({'account_id': 456})")
    print("")

    print("These servers let Claude take real-world actions on your behalf!")

def main():
    """Main demo function"""
    print_header("PERSONAL AI EMPLOYEE - INTERACTIVE DEMO")

    print("\nWelcome to the Personal AI Employee demo!")
    print("This demonstration will showcase the key capabilities of your digital employee.")

    input("\nPress Enter to begin the demo...")

    demo_vault_structure()
    input("\nPress Enter to continue...")

    demo_sample_item_processing()
    input("\nPress Enter to continue...")

    demo_action_planning()
    input("\nPress Enter to continue...")

    demo_approval_workflow()
    input("\nPress Enter to continue...")

    demo_ceo_briefing()
    input("\nPress Enter to continue...")

    demo_mcp_servers()
    input("\nPress Enter to continue...")

    print_section("DEMO SUMMARY")

    print("🎉 Demo Complete! You've seen the Personal AI Employee in action.")
    print("")
    print("Key Capabilities Demonstrated:")
    print("✅ Intelligent item processing with Claude API")
    print("✅ Automated action planning with context awareness")
    print("✅ Secure approval workflow for sensitive operations")
    print("✅ Proactive CEO briefings with business insights")
    print("✅ Extended capabilities through MCP servers")
    print("✅ Human-in-the-loop safety controls")
    print("")
    print("The Personal AI Employee:")
    print("• Acts as your 24/7 digital employee")
    print("• Handles routine tasks autonomously")
    print("• Escalates important decisions for approval")
    print("• Provides business intelligence and insights")
    print("• Maintains privacy with local data storage")
    print("")
    print("Ready to automate your personal and business affairs!")

if __name__ == "__main__":
    main()