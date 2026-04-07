#!/usr/bin/env python3
"""
WhatsApp Automation Orchestrator
Integrates WhatsApp watcher with Personal AI Employee orchestrator.
Manages the flow from message detection → AI processing → action execution.
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import subprocess
import threading


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WhatsAppOrchestrator')


class WhatsAppOrchestrator:
    """
    Orchestrates WhatsApp automation workflow:
    1. Monitor Needs_Action folder for WhatsApp messages
    2. Trigger Claude Code for processing
    3. Handle approval workflow
    4. Execute actions via MCP
    """
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs_path = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Create directories
        for folder in [self.needs_action, self.plans, self.pending_approval, 
                      self.approved, self.done, self.logs_path]:
            folder.mkdir(parents=True, exist_ok=True)
            
        # State tracking
        self.processing_files: set = set()
        self.is_running = False
        
        logger.info(f"WhatsApp Orchestrator initialized")
        logger.info(f"Vault: {self.vault_path}")
        
    def start(self) -> None:
        """Start the orchestrator loop"""
        logger.info("Starting WhatsApp Orchestrator...")
        self.is_running = True
        
        while self.is_running:
            try:
                self._process_needs_action()
                self._process_approved()
                self._update_dashboard()
                time.sleep(10)  # Check every 10 seconds
                
            except KeyboardInterrupt:
                logger.info("Orchestrator stopped by user")
                self.stop()
                break
                
            except Exception as e:
                logger.error(f"Error in orchestrator loop: {e}")
                time.sleep(5)
                
    def stop(self) -> None:
        """Stop the orchestrator"""
        logger.info("Stopping WhatsApp Orchestrator...")
        self.is_running = False
        
    def _process_needs_action(self) -> None:
        """Process items in Needs_Action folder"""
        try:
            # Find WhatsApp action files
            whatsapp_files = list(self.needs_action.glob("WHATSAPP_*.md"))
            
            if not whatsapp_files:
                return
                
            logger.info(f"Found {len(whatsapp_files)} WhatsApp action files")
            
            for action_file in whatsapp_files:
                if action_file.name in self.processing_files:
                    continue
                    
                self.processing_files.add(action_file.name)
                self._process_action_file(action_file)
                self.processing_files.remove(action_file.name)
                
        except Exception as e:
            logger.error(f"Error processing Needs_Action: {e}")
            
    def _process_action_file(self, action_file: Path) -> None:
        """Process a single WhatsApp action file"""
        try:
            logger.info(f"Processing action file: {action_file.name}")
            
            # Read action file
            content = action_file.read_text()
            
            # Check if it's a trigger message (high priority)
            is_trigger = "priority: HIGH" in content
            
            if is_trigger:
                # Create plan for AI processing
                self._create_plan(action_file, content)
                
                # Trigger Claude Code if configured
                if self._should_trigger_claude(content):
                    self._trigger_claude_processing(action_file)
                    
            # Log the action
            self._log_processing(action_file, content)
            
        except Exception as e:
            logger.error(f"Error processing action file {action_file.name}: {e}")
            
    def _create_plan(self, action_file: Path, content: str) -> Path:
        """Create a Plan.md for the action file"""
        try:
            # Extract message details
            lines = content.split('\n')
            sender = "Unknown"
            message = ""
            
            for line in lines:
                if line.startswith("from:"):
                    sender = line.split(":", 1)[1].strip()
                elif line.startswith("## Message Content"):
                    # Get next line as message
                    idx = lines.index(line)
                    if idx + 1 < len(lines):
                        message = lines[idx + 1].strip()
                        
            # Create plan file
            plan_name = f"PLAN_{action_file.stem}.md"
            plan_path = self.plans / plan_name
            
            plan_content = f"""---
type: whatsapp_plan
created: {datetime.now().isoformat()}
status: pending
action_file: {action_file.name}
---

# WhatsApp Message Processing Plan

## Message Details
- **From**: {sender}
- **Message**: {message[:100]}{'...' if len(message) > 100 else ''}
- **Priority**: High (trigger message detected)

## Recommended Actions
1. [ ] Analyze message intent
2. [ ] Draft appropriate response
3. [ ] Create approval request for response
4. [ ] Move approval to Approved folder for execution

## AI Processing Notes
- This message contains trigger keywords
- Requires immediate attention
- Response should be professional and helpful

## Next Steps
- Wait for Claude Code analysis
- Execute approved response via MCP
"""
            
            plan_path.write_text(plan_content)
            logger.info(f"Plan created: {plan_name}")
            
            return plan_path
            
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            raise
            
    def _should_trigger_claude(self, content: str) -> bool:
        """Determine if Claude Code should be triggered"""
        # Check for specific conditions that require AI processing
        trigger_conditions = [
            "trigger_keywords: True",
            "priority: HIGH",
            "invoice" in content.lower(),
            "payment" in content.lower(),
            "urgent" in content.lower()
        ]
        
        return any(condition in content for condition in trigger_conditions)
        
    def _trigger_claude_processing(self, action_file: Path) -> None:
        """Trigger Claude Code to process the action file"""
        try:
            logger.info(f"Triggering Claude Code for {action_file.name}")
            
            # Create a prompt file for Claude
            prompt_file = self.plans / f"CLAUDE_PROMPT_{action_file.stem}.md"
            
            prompt_content = f"""Process this WhatsApp message from Needs_Action folder:

File: {action_file.name}
Action: Analyze and create response plan

Instructions:
1. Read the message content
2. Identify intent and required action
3. Create a professional response draft
4. Generate approval request for the response
5. Update Dashboard.md with activity summary

Start processing now.
"""
            
            prompt_file.write_text(prompt_content)
            
            # In production, this would execute Claude Code
            # subprocess.run(["claude", "--prompt-file", str(prompt_file)])
            
            logger.info("Claude Code trigger created")
            
        except Exception as e:
            logger.error(f"Error triggering Claude: {e}")
            
    def _process_approved(self) -> None:
        """Process approved WhatsApp actions"""
        try:
            approved_files = list(self.approved.glob("WHATSAPP_*.md"))
            
            for approved_file in approved_files:
                logger.info(f"Processing approved action: {approved_file.name}")
                
                # Execute the approved action via MCP
                self._execute_approved_action(approved_file)
                
                # Move to Done folder
                done_path = self.done / f"DONE_{approved_file.name}"
                approved_file.rename(done_path)
                
                logger.info(f"Action completed and moved to Done: {done_path.name}")
                
        except Exception as e:
            logger.error(f"Error processing approved actions: {e}")
            
    def _execute_approved_action(self, approved_file: Path) -> bool:
        """Execute an approved WhatsApp action via MCP"""
        try:
            content = approved_file.read_text()

            # Extract action details
            recipient = self._extract_field(content, "recipient")
            message = self._extract_field(content, "message")

            if not recipient or not message:
                logger.error("Missing recipient or message in approved file")
                return False

            # Execute via MCP (using async approach)
            logger.info(f"Executing approved action: Send to '{recipient}'")
            
            try:
                import asyncio
                from mcp_servers.whatsapp_mcp import WhatsAppMCPServer
                
                # Create MCP server instance
                mcp_server = WhatsAppMCPServer(vault_path=str(self.vault_path))
                
                # Send message via async MCP
                async def send_message():
                    return await mcp_server._send_via_playwright(recipient, message)
                
                success = asyncio.run(send_message())
                
                if success:
                    logger.info(f"✅ Message sent successfully to '{recipient}'")
                    self._log_execution(approved_file, recipient, message)
                    return True
                else:
                    logger.error(f"Failed to send message to '{recipient}'")
                    return False
                    
            except Exception as mcp_error:
                logger.error(f"MCP execution failed: {mcp_error}")
                # Log the error but don't fail the entire process
                self._log_execution_error(approved_file, str(mcp_error))
                return False

        except Exception as e:
            logger.error(f"Error executing approved action: {e}")
            return False
            
    def _update_dashboard(self) -> None:
        """Update Dashboard.md with WhatsApp activity"""
        try:
            # Count pending items
            pending_whatsapp = len(list(self.needs_action.glob("WHATSAPP_*.md")))
            pending_approvals = len(list(self.pending_approval.glob("WHATSAPP_*.md")))
            completed = len(list(self.done.glob("DONE_WHATSAPP_*.md")))
            
            # Update dashboard
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            dashboard_update = f"""
## WhatsApp Activity ({timestamp})
- **Pending Messages**: {pending_whatsapp}
- **Pending Approvals**: {pending_approvals}
- **Completed Today**: {completed}
"""
            
            # Append to dashboard (or create if doesn't exist)
            if not self.dashboard.exists():
                self.dashboard.write_text(f"# AI Employee Dashboard\n\n{dashboard_update}")
            else:
                with open(self.dashboard, 'a') as f:
                    f.write(dashboard_update)
                    
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            
    def _extract_field(self, content: str, field: str) -> Optional[str]:
        """Extract a field from markdown content"""
        try:
            lines = content.split('\n')
            for line in lines:
                if line.startswith(f"{field}:") or line.startswith(f"- **{field}**:"):
                    return line.split(":", 1)[1].strip()
            return None
        except Exception:
            return None
            
    def _log_processing(self, action_file: Path, content: str) -> None:
        """Log processing activity"""
        try:
            log_file = self.logs_path / f"whatsapp_orchestrator_{datetime.now().strftime('%Y%m%d')}.md"
            
            log_entry = f"\n## {datetime.now().isoformat()}\n"
            log_entry += f"- **File**: {action_file.name}\n"
            log_entry += f"- **Action**: Processing started\n"
            log_entry += f"- **Status**: In progress\n\n"
            
            with open(log_file, 'a') as f:
                f.write(log_entry)
                
        except Exception as e:
            logger.warning(f"Could not log processing: {e}")
            
    def _log_execution(self, approved_file: Path, recipient: str, message: str) -> None:
        """Log message execution"""
        try:
            log_file = self.logs_path / f"whatsapp_orchestrator_{datetime.now().strftime('%Y%m%d')}.md"

            log_entry = f"\n## {datetime.now().isoformat()}\n"
            log_entry += f"- **File**: {approved_file.name}\n"
            log_entry += f"- **Action**: Message sent\n"
            log_entry += f"- **Recipient**: {recipient}\n"
            log_entry += f"- **Message Preview**: {message[:50]}...\n"
            log_entry += f"- **Status**: Completed\n\n"

            with open(log_file, 'a') as f:
                f.write(log_entry)

        except Exception as e:
            logger.warning(f"Could not log execution: {e}")
    
    def _log_execution_error(self, approved_file: Path, error: str) -> None:
        """Log execution error"""
        try:
            log_file = self.logs_path / f"whatsapp_orchestrator_{datetime.now().strftime('%Y%m%d')}.md"

            log_entry = f"\n## {datetime.now().isoformat()}\n"
            log_entry += f"- **File**: {approved_file.name}\n"
            log_entry += f"- **Action**: Message send FAILED\n"
            log_entry += f"- **Error**: {error[:200]}\n"
            log_entry += f"- **Status**: Error\n\n"

            with open(log_file, 'a') as f:
                f.write(log_entry)

        except Exception as e:
            logger.warning(f"Could not log error: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Automation Orchestrator')
    parser.add_argument('--vault', type=str,
                       default=os.environ.get('OBSIDIAN_VAULT_PATH', '.'))
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    
    args = parser.parse_args()
    
    orchestrator = WhatsAppOrchestrator(vault_path=args.vault)
    
    if args.test:
        print("Test mode - checking orchestrator setup...")
        print(f"Vault: {args.vault}")
        print("All directories created successfully.")
        return
    
    try:
        orchestrator.start()
    except KeyboardInterrupt:
        print("\nOrchestrator stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
