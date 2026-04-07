#!/usr/bin/env python3
"""
Send introduction message to Bootlogix - Automation Team via WhatsApp
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path (scripts is inside Personal_AI_Employee)
project_root = Path(__file__).parent.parent  # Go up one level from scripts/
sys.path.insert(0, str(project_root))

from mcp_servers.whatsapp_mcp import WhatsAppMCPServer

# Introduction message
INTRO_MESSAGE = """👋 *Hello Bootlogix - Automation Team!*

I'm your *AI Employee Assistant* - an autonomous WhatsApp automation system built with Claude Code + Obsidian + Playwright.

*🤖 What I Can Do:*

✅ *Message Detection* - Automatically detect incoming WhatsApp messages
✅ *Smart Classification* - Identify urgent, invoice, payment keywords
✅ *AI Processing* - Analyze messages and create action plans
✅ *Approval Workflow* - Human-in-the-loop approval for sensitive actions
✅ *Automated Sending* - Send replies via WhatsApp Web automation
✅ *Session Persistence* - Login once, works across restarts
✅ *Health Monitoring* - Real-time system health checks & alerts
✅ *Audit Logging* - Complete activity trail for compliance

*🛠️ Tech Stack:*
• Brain: Claude Code (AI reasoning)
• Memory: Obsidian (local Markdown database)
• Senses: Python Watchers (Playwright automation)
• Hands: MCP Servers (external integrations)

*📊 Architecture:*
WhatsApp Web → Watcher → Action Files → AI Processing → Approval → Send

*🎯 Ready for:*
• Automated customer responses
• Invoice/payment processing
• Lead capture & qualification
• Business workflow automation

Built as part of the Panaversity Digital FTE Hackathon 2026.

*Need automation? I'm here to help!* 🚀"""

async def send_introduction():
    """Send the introduction message"""
    try:
        print("=" * 60)
        print("  Sending Introduction to Bootlogix - Automation Team")
        print("=" * 60)
        
        # Initialize MCP server
        mcp_server = WhatsAppMCPServer(vault_path=".")
        
        print(f"\n📝 Message Preview:")
        print(f"   To: Bootlogix - Automation Team")
        print(f"   Length: {len(INTRO_MESSAGE)} characters")
        print(f"   Lines: {len(INTRO_MESSAGE.splitlines())}")
        
        print(f"\n⏳ Sending message...")
        
        # Send message via Playwright
        success = await mcp_server._send_via_playwright(
            recipient="Bootlogix - Automation Team",
            message=INTRO_MESSAGE
        )
        
        if success:
            print(f"\n✅ SUCCESS!")
            print(f"   Message sent to: Bootlogix - Automation Team")
            print(f"   Delivery confirmed via WhatsApp Web")
        else:
            print(f"\n❌ FAILED")
            print(f"   Message could not be sent")
            print(f"   Check: Is WhatsApp Web logged in?")
            print(f"   Check: Is the contact name exactly 'Bootlogix - Automation Team'?")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(send_introduction())
    sys.exit(0 if success else 1)
