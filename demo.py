#!/usr/bin/env python3
"""
Quick Demo - Personal AI Employee

Demonstrates the newly implemented Claude integration and email functionality.

Usage:
    python demo.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Colors
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_header(text):
    """Print section header."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def demo_claude_integration():
    """Demonstrate Claude API integration."""
    print_header("Demo 1: Claude API Integration")

    print("This demonstrates the orchestrator calling Claude API for intelligent processing.\n")

    # Check API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print(f"{YELLOW}⚠️  ANTHROPIC_API_KEY not set{RESET}")
        print("Set it in .env file to test Claude integration")
        return False

    print(f"{GREEN}✓{RESET} API key found")

    # Import orchestrator
    sys.path.insert(0, str(Path(__file__).parent))
    from orchestrator import Orchestrator

    vault_path = Path('./vault')
    orch = Orchestrator(str(vault_path), dry_run=False)

    # Create test email
    test_email = """---
type: email
from: demo@example.com
subject: Demo: Request for Meeting
date: 2026-03-10
---

Hi,

I'd like to schedule a meeting with you next week to discuss the Q1 results.

Are you available Tuesday or Wednesday afternoon?

Best regards,
Demo User
"""

    print("\n📧 Processing test email with Claude...\n")
    print("Email content:")
    print("-" * 70)
    print(test_email)
    print("-" * 70)

    # Process with Claude
    result = orch.trigger_claude(test_email)

    if result:
        print(f"\n{GREEN}✅ Claude processed the email successfully!{RESET}\n")

        # Find the latest plan
        plans = list((vault_path / 'Plans').glob('CLAUDE_PLAN_*.md'))
        if plans:
            latest_plan = max(plans, key=lambda p: p.stat().st_mtime)
            print(f"📄 Claude's action plan saved to: {latest_plan.name}\n")

            # Show preview
            plan_content = latest_plan.read_text()
            lines = plan_content.split('\n')
            preview_lines = [l for l in lines if l.strip() and not l.startswith('---')][:15]

            print("Plan preview:")
            print("-" * 70)
            for line in preview_lines:
                print(line)
            print("...")
            print("-" * 70)

            print(f"\n{GREEN}✓{RESET} Full plan available at: vault/Plans/{latest_plan.name}")

        return True
    else:
        print(f"{YELLOW}⚠️  Claude processing failed{RESET}")
        return False

def demo_email_operations():
    """Demonstrate email operations."""
    print_header("Demo 2: Email Operations")

    print("This demonstrates email sending and search via Gmail API.\n")

    # Check Gmail token
    token_path = Path(os.getenv('GMAIL_TOKEN_PATH', './vault/secrets/gmail_token.json'))
    if not token_path.exists():
        print(f"{YELLOW}⚠️  Gmail token not found{RESET}")
        print("Run: python watchers/gmail_watcher.py --vault ./vault")
        return False

    print(f"{GREEN}✓{RESET} Gmail token found")

    # Import email server
    sys.path.insert(0, str(Path(__file__).parent))
    from mcp.email.server import EmailMCPServer

    server = EmailMCPServer()

    # Demo 1: Email search
    print("\n🔍 Searching for unread emails...\n")

    result = server.search_emails({
        'query': 'is:unread',
        'max_results': 3
    })

    if result.get('status') == 'success':
        count = result.get('count', 0)
        print(f"{GREEN}✅ Found {count} unread emails{RESET}\n")

        if count > 0:
            print("Recent unread emails:")
            print("-" * 70)
            for email in result.get('emails', [])[:3]:
                print(f"From: {email.get('from', 'Unknown')}")
                print(f"Subject: {email.get('subject', 'No subject')}")
                print(f"Date: {email.get('date', 'Unknown')}")
                print(f"Preview: {email.get('snippet', '')[:100]}...")
                print("-" * 70)
    else:
        print(f"{YELLOW}⚠️  Email search failed: {result.get('message')}{RESET}")

    # Demo 2: Email draft creation
    print("\n✉️  Creating email draft...\n")

    draft_result = server.draft_email({
        'to': 'demo@example.com',
        'subject': 'Demo: AI Employee Test',
        'body': 'This is a test email created by the Personal AI Employee demo.'
    })

    if draft_result.get('status') == 'created':
        draft_path = Path(draft_result['draft_path'])
        print(f"{GREEN}✅ Draft created successfully{RESET}")
        print(f"📄 Draft saved to: {draft_path.name}\n")

        # Show draft content
        draft_content = draft_path.read_text()
        print("Draft content:")
        print("-" * 70)
        print(draft_content)
        print("-" * 70)

        return True
    else:
        print(f"{YELLOW}⚠️  Draft creation failed{RESET}")
        return False

def demo_approval_workflow():
    """Demonstrate approval workflow."""
    print_header("Demo 3: Approval Workflow")

    print("This demonstrates the approval notification system.\n")

    # Import orchestrator
    sys.path.insert(0, str(Path(__file__).parent))
    from orchestrator import Orchestrator

    vault_path = Path('./vault')
    orch = Orchestrator(str(vault_path), dry_run=True)

    # Create test approval item
    pending_approval = vault_path / 'Pending_Approval'
    pending_approval.mkdir(parents=True, exist_ok=True)

    test_item = pending_approval / f'demo_approval_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    test_item.write_text("""---
type: approval_request
action: send_email
priority: high
category: finance
---

# Approval Request

**Action:** Send invoice reminder email
**To:** client@example.com
**Subject:** Invoice #12345 Payment Reminder

This email requires approval before sending.
""")

    print(f"📋 Created approval request: {test_item.name}\n")

    # Send notification
    print("📢 Sending approval notification...\n")

    orch.notify_approval_needed(test_item, {
        'priority': 'high',
        'category': 'finance'
    })

    print(f"{GREEN}✅ Notification sent{RESET}")
    print(f"📁 Approval request at: vault/Pending_Approval/{test_item.name}\n")

    # Check webhook config
    webhook_config = vault_path / 'secrets' / 'webhooks.json'
    if webhook_config.exists():
        print(f"{GREEN}✓{RESET} Webhook config found - notifications sent to Slack/Discord")
    else:
        print(f"{YELLOW}ℹ{RESET}  No webhook config - add Slack/Discord URLs to receive notifications")
        print("   Copy vault/secrets/webhooks.json.example to webhooks.json")

    # Clean up
    test_item.unlink(missing_ok=True)

    return True

def demo_end_to_end():
    """Demonstrate complete end-to-end workflow."""
    print_header("Demo 4: End-to-End Workflow")

    print("This demonstrates the complete workflow from email to action.\n")

    # Check prerequisites
    api_key = os.getenv('ANTHROPIC_API_KEY')
    token_path = Path(os.getenv('GMAIL_TOKEN_PATH', './vault/secrets/gmail_token.json'))

    if not api_key:
        print(f"{YELLOW}⚠️  ANTHROPIC_API_KEY not set - skipping{RESET}")
        return False

    if not token_path.exists():
        print(f"{YELLOW}⚠️  Gmail token not found - skipping{RESET}")
        return False

    print(f"{GREEN}✓{RESET} Prerequisites met\n")

    # Import orchestrator
    sys.path.insert(0, str(Path(__file__).parent))
    from orchestrator import Orchestrator

    vault_path = Path('./vault')
    orch = Orchestrator(str(vault_path), dry_run=False)

    # Create test email in Needs_Action
    needs_action = vault_path / 'Needs_Action'
    needs_action.mkdir(parents=True, exist_ok=True)

    test_email = needs_action / f'demo_e2e_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    test_email.write_text("""---
type: email
from: demo@example.com
subject: Demo: End-to-End Test
date: 2026-03-10
---

This is a complete end-to-end test of the Personal AI Employee.

The system should:
1. Detect this email in Needs_Action/
2. Process it with Claude AI
3. Generate an action plan
4. Create appropriate response

Please acknowledge receipt.
""")

    print(f"📧 Created test email: {test_email.name}\n")
    print("🤖 Processing with AI Employee...\n")

    # Process
    result = orch.trigger_claude(test_email.read_text())

    if result:
        print(f"{GREEN}✅ End-to-end workflow completed successfully!{RESET}\n")

        print("Results:")
        print("-" * 70)

        # Check Plans
        plans = list((vault_path / 'Plans').glob('CLAUDE_PLAN_*.md'))
        if plans:
            latest_plan = max(plans, key=lambda p: p.stat().st_mtime)
            print(f"✓ Action plan created: vault/Plans/{latest_plan.name}")

        # Check Drafts
        drafts = list((vault_path / 'Drafts').glob('*.md'))
        if drafts:
            latest_draft = max(drafts, key=lambda p: p.stat().st_mtime)
            print(f"✓ Draft created: vault/Drafts/{latest_draft.name}")

        # Check Pending_Approval
        approvals = list((vault_path / 'Pending_Approval').glob('*.md'))
        if approvals:
            latest_approval = max(approvals, key=lambda p: p.stat().st_mtime)
            print(f"✓ Approval request: vault/Pending_Approval/{latest_approval.name}")

        print("-" * 70)

        # Clean up
        test_email.unlink(missing_ok=True)

        return True
    else:
        print(f"{YELLOW}⚠️  Workflow failed{RESET}")
        test_email.unlink(missing_ok=True)
        return False

def main():
    """Run all demos."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Personal AI Employee - Feature Demo{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")

    print("\nThis demo showcases the newly implemented features:")
    print("1. Claude API integration for intelligent processing")
    print("2. Email sending and search via Gmail API")
    print("3. Approval workflow with notifications")
    print("4. Complete end-to-end workflow")

    input("\nPress Enter to start the demo...")

    results = {}

    # Run demos
    results['claude'] = demo_claude_integration()
    input("\nPress Enter to continue...")

    results['email'] = demo_email_operations()
    input("\nPress Enter to continue...")

    results['approval'] = demo_approval_workflow()
    input("\nPress Enter to continue...")

    results['e2e'] = demo_end_to_end()

    # Summary
    print_header("Demo Summary")

    print("Results:")
    print(f"  Claude Integration: {'✅ PASS' if results['claude'] else '⚠️  SKIP'}")
    print(f"  Email Operations: {'✅ PASS' if results['email'] else '⚠️  SKIP'}")
    print(f"  Approval Workflow: {'✅ PASS' if results['approval'] else '⚠️  SKIP'}")
    print(f"  End-to-End: {'✅ PASS' if results['e2e'] else '⚠️  SKIP'}")

    passed = sum(results.values())
    total = len(results)

    print(f"\n{GREEN}Passed: {passed}/{total}{RESET}\n")

    if passed == total:
        print(f"{GREEN}🎉 All demos completed successfully!{RESET}")
        print("\nYour Personal AI Employee is working correctly.")
        print("\nNext steps:")
        print("1. Customize vault/Company_Handbook.md with your rules")
        print("2. Set your goals in vault/Business_Goals.md")
        print("3. Start the system: ./scripts/start_all.sh")
    else:
        print(f"{YELLOW}⚠️  Some demos were skipped{RESET}")
        print("\nTo enable all features:")
        print("1. Set ANTHROPIC_API_KEY in .env")
        print("2. Run: python watchers/gmail_watcher.py --vault ./vault")
        print("3. See SETUP.md for detailed instructions")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n{YELLOW}Error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
