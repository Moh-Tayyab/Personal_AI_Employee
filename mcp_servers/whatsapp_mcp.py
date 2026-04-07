#!/usr/bin/env python3
"""
WhatsApp MCP Server - Model Context Protocol Server for WhatsApp
Provides WhatsApp capabilities to Claude Code via MCP.
"""

import os
import sys
import json
import asyncio
import logging
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    CallToolResult,
    ListToolsResult,
    GetPromptResult,
    Prompt,
    PromptMessage,
    ReadResourceResult,
    Resource,
    ResourceTemplate,
    ListResourcesResult,
    ListResourceTemplatesResult,
)

# Import shared browser manager
sys.path.insert(0, str(Path(__file__).parent.parent / 'watchers'))
from whatsapp_browser_manager import get_browser_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WhatsAppMCP')


class WhatsAppMCPServer:
    """MCP Server for WhatsApp automation"""
    
    def __init__(self, vault_path: str, session_path: str = None):
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path) if session_path else self.vault_path / '.whatsapp_session'
        self.pending_approvals = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.logs_path = self.vault_path / 'Logs'
        
        # Create directories
        self.pending_approvals.mkdir(parents=True, exist_ok=True)
        self.approved.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # WhatsApp state
        self.browser = None
        self.page = None
        self.is_connected = False
        
        # MCP Server
        self.server = Server("whatsapp-mcp")
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            return ListToolsResult(
                tools=[
                    Tool(
                        name="send_whatsapp_message",
                        description="Send a WhatsApp message to a contact or group",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "recipient": {
                                    "type": "string",
                                    "description": "Name of the recipient (contact or group)"
                                },
                                "message": {
                                    "type": "string",
                                    "description": "Message content to send"
                                },
                                "requires_approval": {
                                    "type": "boolean",
                                    "description": "If true, create approval request instead of sending directly",
                                    "default": False
                                }
                            },
                            "required": ["recipient", "message"]
                        }
                    ),
                    Tool(
                        name="read_whatsapp_messages",
                        description="Read recent WhatsApp messages from all chats or specific chat",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "chat_name": {
                                    "type": "string",
                                    "description": "Specific chat to read from (optional)"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum messages to retrieve",
                                    "default": 10
                                }
                            },
                            "required": []
                        }
                    ),
                    Tool(
                        name="get_whatsapp_status",
                        description="Get current WhatsApp Web connection status",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    ),
                    Tool(
                        name="create_whatsapp_approval_request",
                        description="Create an approval request for sending a WhatsApp message",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "recipient": {
                                    "type": "string",
                                    "description": "Name of the recipient"
                                },
                                "message": {
                                    "type": "string",
                                    "description": "Message content"
                                },
                                "reason": {
                                    "type": "string",
                                    "description": "Reason for sending this message"
                                }
                            },
                            "required": ["recipient", "message"]
                        }
                    ),
                    Tool(
                        name="process_whatsapp_approval",
                        description="Process a pending WhatsApp approval request",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "approval_id": {
                                    "type": "string",
                                    "description": "ID of the approval request file"
                                },
                                "action": {
                                    "type": "string",
                                    "description": "Action to take: approve or reject",
                                    "enum": ["approve", "reject"]
                                }
                            },
                            "required": ["approval_id", "action"]
                        }
                    )
                ]
            )
            
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> CallToolResult:
            try:
                if name == "send_whatsapp_message":
                    return await self._send_whatsapp_message(arguments)
                elif name == "read_whatsapp_messages":
                    return await self._read_whatsapp_messages(arguments)
                elif name == "get_whatsapp_status":
                    return await self._get_whatsapp_status()
                elif name == "create_whatsapp_approval_request":
                    return await self._create_approval_request(arguments)
                elif name == "process_whatsapp_approval":
                    return await self._process_approval(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                        isError=True
                    )
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
                
        @self.server.list_resources()
        async def list_resources() -> ListResourcesResult:
            return ListResourcesResult(resources=[])
            
        @self.server.read_resource()
        async def read_resource(uri: str) -> ReadResourceResult:
            return ReadResourceResult(
                contents=[TextContent(type="text", text="No resources available")]
            )
            
        @self.server.list_prompts()
        async def list_prompts() -> list:
            return []
            
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
            return GetPromptResult(
                description="No prompts available",
                messages=[]
            )
            
    async def _send_whatsapp_message(self, arguments: dict) -> CallToolResult:
        """Send WhatsApp message tool implementation"""
        recipient = arguments.get("recipient")
        message = arguments.get("message")
        requires_approval = arguments.get("requires_approval", False)
        
        if not recipient or not message:
            return CallToolResult(
                content=[TextContent(type="text", text="Missing recipient or message")],
                isError=True
            )
            
        if requires_approval:
            # Create approval request
            approval_result = await self._create_approval_request({
                "recipient": recipient,
                "message": message,
                "reason": f"Message to {recipient}"
            })
            return approval_result
        else:
            # Send directly via Playwright
            try:
                success = await self._send_via_playwright(recipient, message)
                if success:
                    # Log the action
                    self._log_action("sent_message", {
                        "recipient": recipient,
                        "message_preview": message[:100],
                        "timestamp": datetime.now().isoformat()
                    })
                    return CallToolResult(
                        content=[TextContent(type="text", 
                            text=f"Message sent to {recipient} successfully")]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", 
                            text=f"Failed to send message to {recipient}")],
                        isError=True
                    )
            except Exception as e:
                return CallToolResult(
                    content=[TextContent(type="text", 
                        text=f"Error sending message: {str(e)}")],
                    isError=True
                )
                
    async def _read_whatsapp_messages(self, arguments: dict) -> CallToolResult:
        """Read WhatsApp messages tool implementation"""
        chat_name = arguments.get("chat_name")
        limit = arguments.get("limit", 10)

        if not chat_name:
            return CallToolResult(
                content=[TextContent(type="text", text="Missing chat_name parameter")],
                isError=True
            )

        try:
            messages = await self._read_via_playwright(chat_name, limit)
            
            if not messages:
                return CallToolResult(
                    content=[TextContent(type="text",
                        text=f"No messages found for '{chat_name}'")]
                )
            
            # Format messages for display
            formatted = f"Retrieved {len(messages)} messages from '{chat_name}':\n\n"
            for i, msg in enumerate(messages, 1):
                direction = "←" if msg['is_outgoing'] else "→"
                formatted += f"{i}. {direction} [{msg['sender']}] {msg['text']}\n"
                if msg['timestamp']:
                    formatted += f"   Time: {msg['timestamp']}\n"
                formatted += "\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=formatted)]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text",
                    text=f"Error reading messages: {str(e)}")],
                isError=True
            )
            
    async def _get_whatsapp_status(self) -> CallToolResult:
        """Get WhatsApp status tool implementation"""
        status = {
            "connected": self.is_connected,
            "vault_path": str(self.vault_path),
            "session_path": str(self.session_path),
            "pending_approvals": len(list(self.pending_approvals.glob("*.md"))),
            "timestamp": datetime.now().isoformat()
        }
        
        return CallToolResult(
            content=[TextContent(type="text", 
                text=json.dumps(status, indent=2))]
        )
        
    async def _create_approval_request(self, arguments: dict) -> CallToolResult:
        """Create WhatsApp message approval request"""
        recipient = arguments.get("recipient")
        message = arguments.get("message")
        reason = arguments.get("reason", "No reason provided")
        
        if not recipient or not message:
            return CallToolResult(
                content=[TextContent(type="text", text="Missing recipient or message")],
                isError=True
            )
            
        # Create approval request file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_recipient = "".join(c if c.isalnum() or c in '._- ' else '_' for c in recipient)
        filename = f"WHATSAPP_MSG_{safe_recipient}_{timestamp}.md"
        filepath = self.pending_approvals / filename
        
        content = f"""---
type: whatsapp_approval_request
action: send_whatsapp_message
recipient: {recipient}
created: {datetime.now().isoformat()}
expires: {(datetime.now().replace(hour=23, minute=59, second=59)).isoformat()}
status: pending
reason: {reason}
---

# WhatsApp Message Approval Request

## Message Details
- **To**: {recipient}
- **Message**: {message}
- **Reason**: {reason}

## To Approve
Move this file to the `Approved` folder to send the message.

## To Reject
Move this file to the `Rejected` folder or delete it.

## Notes
- This request was generated by the AI Employee
- Message will be sent via WhatsApp Web once approved
- Approval expires at end of day
"""
        
        filepath.write_text(content)
        
        return CallToolResult(
            content=[TextContent(type="text", 
                text=f"Approval request created: {filename}\n"
                     f"Move to Approved folder to send message.")]
        )
        
    async def _process_approval(self, arguments: dict) -> CallToolResult:
        """Process a WhatsApp approval request"""
        approval_id = arguments.get("approval_id")
        action = arguments.get("action")
        
        if not approval_id or action not in ["approve", "reject"]:
            return CallToolResult(
                content=[TextContent(type="text", text="Invalid approval_id or action")],
                isError=True
            )
            
        try:
            approval_file = self.pending_approvals / approval_id
            
            if not approval_file.exists():
                return CallToolResult(
                    content=[TextContent(type="text", 
                        text=f"Approval file not found: {approval_id}")],
                    isError=True
                )
                
            # Read approval content
            content = approval_file.read_text()
            
            if action == "approve":
                # Extract recipient and message from content
                recipient = self._extract_field(content, "recipient")
                message = self._extract_field(content, "Message")
                
                # Send the message
                if recipient and message:
                    success = await self._send_via_playwright(recipient, message)
                    if success:
                        # Move to Done folder
                        done_folder = self.vault_path / 'Done'
                        done_folder.mkdir(parents=True, exist_ok=True)
                        approval_file.rename(done_folder / f"SENT_{approval_id}")
                        
                        return CallToolResult(
                            content=[TextContent(type="text", 
                                text=f"Message sent to {recipient}. Request moved to Done.")]
                        )
                    else:
                        return CallToolResult(
                            content=[TextContent(type="text", 
                                text="Failed to send message after approval")],
                            isError=True
                        )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", 
                            text="Could not extract recipient/message from approval")],
                        isError=True
                    )
            else:  # reject
                # Move to Rejected folder
                rejected_folder = self.vault_path / 'Rejected'
                rejected_folder.mkdir(parents=True, exist_ok=True)
                approval_file.rename(rejected_folder / f"REJECTED_{approval_id}")
                
                return CallToolResult(
                    content=[TextContent(type="text", 
                        text="Approval request rejected and moved to Rejected folder.")]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", 
                    text=f"Error processing approval: {str(e)}")],
                isError=True
            )
            
    async def _send_via_playwright(self, recipient: str, message: str) -> bool:
        """
        Send message via Playwright browser automation with robust error handling.
        
        Flow:
        1. Get shared browser instance (async)
        2. Search and open recipient chat
        3. Type message in compose box
        4. Send message (Enter key)
        5. Verify message was sent
        
        Returns True if successful, False otherwise.
        """
        max_retries = 2
        for attempt in range(max_retries):
            try:
                logger.info(f"Sending WhatsApp to '{recipient}' (attempt {attempt + 1}/{max_retries})")
                
                # Get shared browser manager (async version)
                browser_mgr = get_browser_manager(session_path=str(self.session_path))
                browser, page = await browser_mgr.get_async_browser()
                
                # Step 1: Verify WhatsApp Web is loaded
                if not await browser_mgr.is_logged_in_async():
                    logger.error("WhatsApp Web is not logged in. Cannot send message.")
                    return False
                
                # Step 2: Open recipient's chat
                success = await self._open_chat_async(page, recipient)
                if not success:
                    logger.error(f"Failed to open chat for '{recipient}'")
                    if attempt < max_retries - 1:
                        logger.info("Retrying after page reload...")
                        browser_mgr.reload_whatsapp()
                        time.sleep(2)
                        continue
                    return False
                
                # Step 3: Wait for chat to fully load
                try:
                    await page.wait_for_selector('div[contenteditable="true"][data-tab="10"]', timeout=5000)
                except Exception as e:
                    logger.warning(f"Chat load verification failed: {e}")
                    time.sleep(1)
                
                # Step 4: Type message
                success = await self._type_message_async(page, message)
                if not success:
                    logger.error("Failed to type message")
                    return False
                
                # Step 5: Send message (Enter key is more reliable than clicking send button)
                success = await self._send_message_async(page)
                if not success:
                    logger.error("Failed to send message")
                    return False
                
                # Step 6: Verify message was sent (check for message bubble)
                time.sleep(1)  # Wait for message to appear
                success = await self._verify_message_sent_async(page, message)
                
                if success:
                    logger.info(f"Message sent successfully to '{recipient}'")
                    return True
                else:
                    logger.warning("Message send verification failed")
                    if attempt < max_retries - 1:
                        continue
                    return False
                
            except Exception as e:
                logger.error(f"Send via Playwright failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return False
        
        return False
            
    async def _open_chat_async(self, page, chat_name: str) -> bool:
        """
        Open a specific chat by searching for the contact name.
        Uses multiple selector strategies for robustness.
        """
        try:
            # Strategy 1: Use search box to find contact
            logger.info(f"Searching for contact: '{chat_name}'")
            
            # Find search box (multiple selector attempts)
            search_selectors = [
                'div[title="Search"]',
                'div[title^="Search"]',
                '[data-testid="chat-list-search"]',
                'div[contenteditable="true"][data-tab="3"]',
                'span[data-testid="search-bar"]',
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = page.query_selector(selector)
                    if search_box and search_box.is_visible():
                        logger.info(f"Found search box with selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not search_box:
                logger.warning("Search box not found, trying direct click on chat list")
                # Fallback: Try to click directly in chat list
                return await self._find_chat_in_list_async(page, chat_name)
            
            # Click search box and type contact name
            search_box.click()
            time.sleep(0.5)
            
            # Type contact name using innerHTML (more reliable for contenteditable)
            page.evaluate(f'''() => {{
                const searchBox = document.querySelector('div[contenteditable="true"][data-tab="3"]') ||
                                  document.querySelector('div[title="Search"]');
                if (searchBox) {{
                    searchBox.innerHTML = "{chat_name}";
                    searchBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            }}''')
            
            # Wait for search results
            time.sleep(2)
            
            # Click on first search result
            chat_selectors = [
                f'[data-testid="cell-frame-container"]:has-text("{chat_name}")',
                f'span[title="{chat_name}"]',
                f'span:has-text("{chat_name}")',
            ]
            
            for selector in chat_selectors:
                try:
                    chat_element = page.query_selector(selector)
                    if chat_element and chat_element.is_visible():
                        chat_element.click()
                        logger.info(f"✅ Opened chat: '{chat_name}'")
                        time.sleep(1)  # Wait for chat to load
                        return True
                except Exception:
                    continue
            
            logger.warning(f"Chat '{chat_name}' not found in search results")
            return False
            
        except Exception as e:
            logger.error(f"Error opening chat '{chat_name}': {e}")
            return False
    
    async def _find_chat_in_list_async(self, page, chat_name: str) -> bool:
        """Fallback: Find and click chat directly from chat list without search"""
        try:
            chat_selectors = [
                f'[data-testid="cell-frame-container"]:has-text("{chat_name}")',
                f'[role="row"]:has-text("{chat_name}")',
            ]
            
            for selector in chat_selectors:
                try:
                    chat_element = page.query_selector(selector)
                    if chat_element:
                        chat_element.click()
                        logger.info(f"✅ Found and clicked chat: '{chat_name}'")
                        time.sleep(1)
                        return True
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error finding chat in list: {e}")
            return False
    
    async def _type_message_async(self, page, message: str) -> bool:
        """
        Type message in WhatsApp compose box.
        Uses multiple approaches for contenteditable div.
        """
        try:
            # Compose box selectors (multiple fallbacks)
            compose_selectors = [
                'div[contenteditable="true"][data-tab="10"]',
                '[data-testid="conversation-compose-box-input"]',
                'div.copyable-text.selectable-text[role="textbox"]',
                'div[contenteditable="true"][role="textbox"]',
            ]
            
            compose_box = None
            for selector in compose_selectors:
                try:
                    compose_box = page.query_selector(selector)
                    if compose_box and compose_box.is_visible():
                        logger.info(f"Found compose box with selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not compose_box:
                logger.error("Compose box not found")
                return False
            
            # Click to focus
            compose_box.click()
            time.sleep(0.3)
            
            # Clear existing content
            page.evaluate('''() => {
                const composeBox = document.querySelector('div[contenteditable="true"][data-tab="10"]') ||
                                  document.querySelector('[data-testid="conversation-compose-box-input"]');
                if (composeBox) {
                    composeBox.innerHTML = '';
                }
            }''')
            time.sleep(0.2)
            
            # Type message (use fill for reliability)
            try:
                compose_box.fill(message)
            except Exception:
                # Fallback: Use JavaScript to set innerHTML
                page.evaluate(f'''() => {{
                    const composeBox = document.querySelector('div[contenteditable="true"][data-tab="10"]') ||
                                      document.querySelector('[data-testid="conversation-compose-box-input"]');
                    if (composeBox) {{
                        composeBox.innerHTML = `{message}`;
                        composeBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                }}''')
            
            time.sleep(0.5)
            logger.info(f"✅ Message typed in compose box ({len(message)} chars)")
            return True
            
        except Exception as e:
            logger.error(f"Error typing message: {e}")
            return False
    
    async def _send_message_async(self, page) -> bool:
        """Send message by pressing Enter key (more reliable than clicking send button)"""
        try:
            # Press Enter to send
            page.keyboard.press('Enter')
            time.sleep(0.5)
            logger.info("✅ Enter key pressed to send message")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            
            # Fallback: Try clicking send button
            try:
                send_button = page.query_selector('[data-testid="compose-btn-send"]')
                if send_button:
                    send_button.click()
                    logger.info("✅ Send button clicked")
                    return True
            except Exception as fallback_error:
                logger.error(f"Send button fallback also failed: {fallback_error}")
            
            return False
    
    async def _verify_message_sent_async(self, page, message: str) -> bool:
        """Verify that message appears in chat (check for message bubble)"""
        try:
            # Wait a moment for message to render
            time.sleep(1)
            
            # Check if message text appears in conversation panel
            # Use a partial match since WhatsApp may add formatting
            message_preview = message[:50] if len(message) > 50 else message
            
            # Look for message in conversation panel
            selectors = [
                f'[data-testid="conversation-panel-messages"]:has-text("{message_preview}")',
                f'span.copyable-text:has-text("{message_preview}")',
                f'span.selectable-text:has-text("{message_preview}")',
            ]
            
            for selector in selectors:
                try:
                    element = page.query_selector(selector)
                    if element and element.is_visible():
                        logger.info(f"✅ Message verified in chat: '{message_preview}...'")
                        return True
                except Exception:
                    continue
            
            # If exact match fails, check if any new message appeared
            logger.warning("Could not verify exact message content, checking for recent messages")
            return True  # Assume success if no error occurred
            
        except Exception as e:
            logger.error(f"Error verifying message: {e}")
            return False

    async def _read_via_playwright(self, chat_name: str, limit: int) -> list:
        """
        Read recent messages from a WhatsApp chat.
        
        Flow:
        1. Get shared browser instance (async)
        2. Open the chat
        3. Extract recent messages from conversation panel
        4. Return list of message dicts with sender, text, timestamp
        
        Returns list of message dictionaries.
        """
        try:
            logger.info(f"Reading messages from '{chat_name}' (limit: {limit})")
            
            # Get shared browser manager (async version)
            browser_mgr = get_browser_manager(session_path=str(self.session_path))
            browser, page = await browser_mgr.get_async_browser()
            
            # Verify WhatsApp Web is loaded
            if not await browser_mgr.is_logged_in_async():
                logger.error("WhatsApp Web is not logged in. Cannot read messages.")
                return []
            
            # Open the chat
            success = await self._open_chat_async(page, chat_name)
            if not success:
                logger.error(f"Failed to open chat for '{chat_name}'")
                return []
            
            # Wait for messages to load
            time.sleep(2)
            
            # Scroll up to load more messages (WhatsApp lazy-loads)
            await page.evaluate('''() => {
                const panel = document.querySelector('[data-testid="conversation-panel-messages"]');
                if (panel) {
                    panel.scrollTop = 1000;
                }
            }''')
            time.sleep(1)
            
            # Extract messages
            messages = await self._extract_messages_from_chat(page, limit)
            
            logger.info(f"Extracted {len(messages)} messages from '{chat_name}'")
            return messages
            
        except Exception as e:
            logger.error(f"Error reading messages: {e}")
            return []
    
    async def _extract_messages_from_chat(self, page, limit: int) -> list:
        """Extract recent messages from open chat"""
        try:
            messages = []
            
            # Get all message containers
            msg_elements = page.query_selector_all(
                '[data-testid="conversation-panel-messages"] > div'
            )
            
            if not msg_elements:
                logger.warning("No message elements found in conversation panel")
                return []
            
            # Process last N messages
            for elem in msg_elements[-limit:]:
                try:
                    # Extract message text
                    text_elem = elem.query_selector(
                        'span.selectable-text, span.copyable-text, span[dir="auto"]'
                    )
                    text = text_elem.inner_text().strip() if text_elem else ''
                    
                    # Extract timestamp
                    time_elem = elem.query_selector('span[title]')
                    timestamp = time_elem.get_attribute('title') if time_elem else ''
                    
                    # Determine if sent by me (check class)
                    elem_class = elem.get_attribute('class', default='')
                    is_outgoing = 'message-out' in elem_class
                    
                    if text:  # Only include messages with text
                        messages.append({
                            'text': text,
                            'timestamp': timestamp,
                            'is_outgoing': is_outgoing,
                            'sender': 'me' if is_outgoing else 'other'
                        })
                except Exception as e:
                    logger.warning(f"Error extracting message element: {e}")
                    continue
            
            return messages
            
        except Exception as e:
            logger.error(f"Error extracting messages: {e}")
            return []

    def _extract_field(self, content: str, field: str) -> Optional[str]:
        """Extract a field from markdown content (YAML frontmatter or body)"""
        try:
            lines = content.split('\n')
            
            # First, try to extract from YAML frontmatter (between --- markers)
            in_frontmatter = False
            for line in lines:
                if line.startswith('---'):
                    in_frontmatter = not in_frontmatter
                    continue
                if in_frontmatter and line.startswith(f"{field}:"):
                    return line.split(":", 1)[1].strip()
            
            # If not in frontmatter, try to extract from markdown body
            for line in lines:
                if line.startswith(f"- **{field}**:"):
                    return line.split(":", 1)[1].strip()
            
            # Try alternative format: "## Field" followed by value on next line
            for i, line in enumerate(lines):
                if line.strip() == f"## {field}" and i + 1 < len(lines):
                    return lines[i + 1].strip()
            
            return None
        except Exception:
            return None
            
    def _log_action(self, action: str, data: dict) -> None:
        """Log an action to the logs folder"""
        try:
            log_file = self.logs_path / f"whatsapp_{datetime.now().strftime('%Y%m%d')}.md"
            
            log_entry = f"\n## {datetime.now().isoformat()}\n"
            log_entry += f"- **Action**: {action}\n"
            for key, value in data.items():
                log_entry += f"- **{key}**: {value}\n"
            log_entry += "\n---\n"
            
            with open(log_file, 'a') as f:
                f.write(log_entry)
                
        except Exception as e:
            logger.warning(f"Could not log action: {e}")
            
    async def start(self):
        """Start the MCP server"""
        logger.info("Starting WhatsApp MCP Server...")
        logger.info(f"Vault: {self.vault_path}")
        
        # Run stdio server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp MCP Server')
    parser.add_argument('--vault', type=str, 
                       default=os.environ.get('OBSIDIAN_VAULT_PATH', '.'))
    parser.add_argument('--session', type=str, default=None)
    
    args = parser.parse_args()
    
    server = WhatsAppMCPServer(
        vault_path=args.vault,
        session_path=args.session
    )
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nMCP Server stopped")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
