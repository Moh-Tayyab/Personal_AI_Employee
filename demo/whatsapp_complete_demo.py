#!/usr/bin/env python3
"""
WhatsApp Automation Complete Demo Script
Demonstrates the full end-to-end automation flow:
1. Message Detection (simulated)
2. AI Processing & Plan Creation
3. Approval Request Generation
4. User Approval (simulated)
5. Message Sending via MCP
6. Health Monitoring & Reporting

Usage:
    python3 demo/whatsapp_complete_demo.py
"""

import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_step(step_num, text):
    """Print step indicator"""
    print(f"\n{'─'*70}")
    print(f"  Step {step_num}: {text}")
    print(f"{'─'*70}")


def print_success(text):
    """Print success message"""
    print(f"  ✅ {text}")


def print_info(text):
    """Print info message"""
    print(f"  ℹ️  {text}")


def print_warning(text):
    """Print warning message"""
    print(f"  ⚠️  {text}")


def setup_demo_environment():
    """Create clean demo environment"""
    demo_dir = Path("demo_whatsapp")
    
    # Clean if exists
    if demo_dir.exists():
        shutil.rmtree(demo_dir)
    
    # Create vault structure
    for folder in ["Needs_Action", "Plans", "Pending_Approval", 
                   "Approved", "Done", "Logs", "Rejected"]:
        (demo_dir / folder).mkdir(parents=True, exist_ok=True)
    
    print_success(f"Demo environment created at: {demo_dir}")
    return demo_dir


def demo_step_1_message_detection(demo_dir: Path):
    """Demo Step 1: Simulate WhatsApp message detection"""
    print_step(1, "Message Detection by WhatsApp Watcher")
    
    from watchers.whatsapp_watcher import WhatsAppWatcher
    
    # Initialize watcher
    watcher = WhatsAppWatcher(
        vault_path=str(demo_dir),
        session_path=str(demo_dir / ".whatsapp_session")
    )
    
    print_info("Simulating WhatsApp Web message detection...")
    time.sleep(1)
    
    # Simulate detected message
    incoming_message = {
        'chat_name': 'Client - Ahmed Khan',
        'last_message': 'Hi, I need the invoice for last month urgently. Can you send it ASAP?',
        'timestamp': datetime.now().isoformat(),
        'is_trigger': True,  # Contains "invoice" and "urgently"
        'raw_data': 'Hi, I need the invoice for last month urgently. Can you send it ASAP?'
    }
    
    print_info(f"Message received from: {incoming_message['chat_name']}")
    print_info(f"Message: '{incoming_message['last_message']}'")
    time.sleep(1)
    
    # Create action file
    action_file = watcher._create_action_file(incoming_message)
    
    print_success(f"Action file created: {action_file.name}")
    print_success(f"Priority: HIGH (trigger keywords detected)")
    print_success(f"Location: Needs_Action/")
    
    return action_file


def demo_step_2_orchestrator_processing(demo_dir: Path):
    """Demo Step 2: Orchestrator processes the message"""
    print_step(2, "AI Orchestrator Processing")
    
    from watchers.whatsapp_orchestrator import WhatsAppOrchestrator
    
    # Initialize orchestrator
    orchestrator = WhatsAppOrchestrator(vault_path=str(demo_dir))
    
    print_info("Orchestrator detecting new action files...")
    time.sleep(1)
    
    # Process the action file
    action_file = list(demo_dir.glob("Needs_Action/WHATSAPP_*.md"))[0]
    orchestrator._process_action_file(action_file)
    
    print_success("Message analyzed and classified")
    
    # Check if plan was created
    plan_files = list(orchestrator.plans.glob("PLAN_*.md"))
    if plan_files:
        plan_file = plan_files[0]
        print_success(f"Processing plan created: {plan_file.name}")
        
        plan_content = plan_file.read_text()
        print_info("Plan includes:")
        if "Analyze message intent" in plan_content:
            print_info("  ✓ Message intent analysis")
        if "Draft appropriate response" in plan_content:
            print_info("  ✓ Response drafting")
        if "Create approval request" in plan_content:
            print_info("  ✓ Approval workflow")
    
    return orchestrator


def demo_step_3_approval_request(demo_dir: Path):
    """Demo Step 3: Create approval request"""
    print_step(3, "Approval Request Generation")
    
    import asyncio
    from mcp_servers.whatsapp_mcp import WhatsAppMCPServer
    
    # Initialize MCP server
    mcp_server = WhatsAppMCPServer(vault_path=str(demo_dir))
    
    print_info("AI drafting response...")
    time.sleep(1)
    
    # Simulated AI-generated response
    ai_response = {
        "recipient": "Client - Ahmed Khan",
        "message": "Hi Ahmed,\n\nThank you for your request. Please find your invoice details below:\n\nInvoice #: INV-2026-0326\nAmount: $1,500.00\nPeriod: March 2026\nDue Date: April 15, 2026\n\nPlease let me know if you need the PDF version.\n\nBest regards,\nAI Employee",
        "reason": "Response to urgent invoice request from client"
    }
    
    print_info(f"Drafted response for: {ai_response['recipient']}")
    print_info(f"Message length: {len(ai_response['message'])} characters")
    time.sleep(1)
    
    # Create approval request
    async def create_approval():
        return await mcp_server._create_approval_request(ai_response)
    
    result = asyncio.run(create_approval())
    result_text = result.content[0].text
    
    print_success("Approval request created")
    
    # Extract filename
    for line in result_text.split('\n'):
        if line.startswith("Approval request created:"):
            filename = line.split(": ", 1)[1].strip()
            break
    
    approval_file = demo_dir / "Pending_Approval" / filename
    print_success(f"File location: Pending_Approval/{filename}")
    
    # Display approval content
    print_info("\nApproval Request Content:")
    print("  " + "-"*60)
    content = approval_file.read_text()
    for line in content.split('\n')[:15]:  # Show first 15 lines
        print(f"  {line}")
    print("  ...")
    print("  " + "-"*60)
    
    return approval_file


def demo_step_4_user_approval(demo_dir: Path, approval_file: Path):
    """Demo Step 4: Simulate user approval"""
    print_step(4, "Human-in-the-Loop Approval")
    
    print_info("Waiting for user approval...")
    time.sleep(1)
    
    print_info("User reviews the approval request")
    time.sleep(1)
    
    print_info("User moves file to Approved folder")
    time.sleep(0.5)
    
    # Simulate user approval
    approved_file = demo_dir / "Approved" / approval_file.name
    approval_file.rename(approved_file)
    
    print_success("✅ APPROVED - File moved to Approved/")
    print_success("Orchestrator will now execute the approved action")
    
    return approved_file


def demo_step_5_message_sending(demo_dir: Path, approved_file: Path):
    """Demo Step 5: Execute approved action (send message)"""
    print_step(5, "Message Execution via MCP Server")
    
    from watchers.whatsapp_orchestrator import WhatsAppOrchestrator
    
    orchestrator = WhatsAppOrchestrator(vault_path=str(demo_dir))
    
    print_info("Orchestrator processing approved actions...")
    time.sleep(1)
    
    print_info("Extracting recipient and message from approval file...")
    time.sleep(0.5)
    
    # Process approved actions
    orchestrator._process_approved()
    
    # Check if file moved to Done
    done_files = list(demo_dir.glob("Done/DONE_*.md"))
    
    if done_files:
        print_success(f"Action completed and logged: {done_files[0].name}")
    else:
        print_warning("Note: Message sending requires active WhatsApp Web session")
        print_info("In production, the message would be sent via Playwright automation")
    
    # Show execution log
    log_files = list(demo_dir.glob("Logs/whatsapp_orchestrator_*.md"))
    if log_files:
        print_info("\nExecution Log:")
        log_content = log_files[-1].read_text()
        for line in log_content.strip().split('\n')[-8:]:  # Show last 8 lines
            print(f"  {line}")
    
    print_info("\nMessage sending flow:")
    print_info("  1. ✅ Approval request created")
    print_info("  2. ✅ User approved action")
    print_info("  3. ✅ MCP server invoked")
    print_info("  4. ⏳ WhatsApp Web automation (requires active session)")
    print_info("  5. ⏳ Message delivery confirmation")


def demo_step_6_health_monitoring(demo_dir: Path):
    """Demo Step 6: Health monitoring and reporting"""
    print_step(6, "Health Monitoring & Reporting")
    
    from watchers.whatsapp_health_monitor import WhatsAppHealthMonitor
    
    # Initialize monitor
    monitor = WhatsAppHealthMonitor(vault_path=str(demo_dir))
    
    # Record demo metrics
    monitor.messages_processed_today = 5
    monitor.messages_sent_today = 3
    monitor.errors_today = 0
    monitor.record_success()
    
    print_info("Running comprehensive health check...")
    time.sleep(1)
    
    # Get health report
    report = monitor.get_health_report()
    print(report)
    
    # Save report
    report_file = monitor.save_health_report()
    print_success(f"Health report saved to: {report_file}")


def demo_summary(demo_dir: Path):
    """Print demo summary"""
    print_header("Demo Summary - Complete WhatsApp Automation Flow")
    
    print("\n📊 What Just Happened:\n")
    
    flow = [
        ("1", "Message Detection", "WhatsApp Watcher detected incoming message via Playwright"),
        ("2", "Action File Creation", "Created WHATSAPP_*.md in Needs_Action/ folder"),
        ("3", "AI Processing", "Orchestrator analyzed message and created processing plan"),
        ("4", "Approval Request", "MCP Server generated approval request with drafted response"),
        ("5", "Human Approval", "User reviewed and approved the action (moved to Approved/)"),
        ("6", "Message Execution", "Orchestrator invoked MCP to send message via WhatsApp Web"),
        ("7", "Health Monitoring", "System health checked and report generated"),
    ]
    
    for step_num, title, desc in flow:
        print(f"  {step_num}. {title}")
        print(f"     {desc}\n")
    
    print("\n📁 Vault Structure After Demo:\n")
    
    # Show vault structure
    for folder in ["Needs_Action", "Plans", "Pending_Approval", "Approved", "Done", "Logs"]:
        folder_path = demo_dir / folder
        if folder_path.exists():
            files = list(folder_path.glob("*"))
            if files:
                print(f"  📂 {folder}/")
                for f in files[:3]:  # Show max 3 files
                    print(f"     - {f.name}")
                if len(files) > 3:
                    print(f"     ... and {len(files) - 3} more files")
                print()
    
    print("\n🎯 Key Features Demonstrated:\n")
    features = [
        "✅ Automated message detection from WhatsApp Web",
        "✅ Intelligent trigger keyword classification",
        "✅ AI-powered processing plan generation",
        "✅ Human-in-the-loop approval workflow",
        "✅ MCP server integration for sending",
        "✅ Complete audit trail and logging",
        "✅ Health monitoring and reporting",
        "✅ Error handling and graceful degradation",
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n" + "="*70)
    print("  Next Steps for Production Use:")
    print("="*70)
    print("""
  1. Install Playwright browsers:
     python3 -m playwright install chromium

  2. Start WhatsApp Watcher:
     python3 watchers/whatsapp_watcher.py --vault . --interval 30

  3. Scan QR code with your phone (first time only)

  4. The automation will now run autonomously:
     - Detect messages → Create action files
     - AI processes → Create plans
     - Generate approvals → Wait for user
     - Execute approved → Send messages
     - Log everything → Generate reports

  5. Monitor health:
     python3 watchers/whatsapp_health_monitor.py --vault . --report
""")
    print("="*70)


def cleanup_demo(demo_dir: Path):
    """Clean up demo environment"""
    print("\n" + "="*70)
    response = input("Clean up demo environment? (y/n): ").strip().lower()
    
    if response == 'y':
        if demo_dir.exists():
            shutil.rmtree(demo_dir)
            print_success("Demo environment cleaned up")
    else:
        print_info(f"Demo environment preserved at: {demo_dir}")
        print_info("You can explore the vault structure to understand the flow")


def main():
    """Run complete WhatsApp automation demo"""
    print_header("WhatsApp Automation - Complete End-to-End Demo")
    
    print("\n  This demo showcases the complete automation pipeline:")
    print("  Message Detection → AI Processing → Approval → Sending → Monitoring")
    print("\n  Note: This is a simulation. Actual message sending requires")
    print("  an active WhatsApp Web session (QR code scan).\n")
    
    input("  Press Enter to start the demo...")
    
    try:
        # Setup
        demo_dir = setup_demo_environment()
        time.sleep(0.5)
        
        # Run demo steps
        demo_step_1_message_detection(demo_dir)
        time.sleep(0.5)
        
        demo_step_2_orchestrator_processing(demo_dir)
        time.sleep(0.5)
        
        demo_step_3_approval_request(demo_dir)
        time.sleep(0.5)
        
        approval_file = demo_step_4_user_approval(demo_dir, 
            list(demo_dir.glob("Pending_Approval/WHATSAPP_*.md"))[0])
        time.sleep(0.5)
        
        demo_step_5_message_sending(demo_dir, approval_file)
        time.sleep(0.5)
        
        demo_step_6_health_monitoring(demo_dir)
        time.sleep(0.5)
        
        # Summary
        demo_summary(demo_dir)
        
        # Cleanup
        cleanup_demo(demo_dir)
        
        print("\n✅ Demo completed successfully!\n")
        return 0
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
