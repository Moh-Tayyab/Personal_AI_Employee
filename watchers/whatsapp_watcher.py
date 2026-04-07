#!/usr/bin/env python3
"""
WhatsApp Watcher - Autonomous WhatsApp Web Monitor
Monitors WhatsApp Web for new messages and creates action files for Claude Code.
Integrates with Personal AI Employee vault system.
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WhatsAppWatcher')


class WhatsAppSessionError(Exception):
    """Custom exception for WhatsApp session issues"""
    pass


class WhatsAppWatcher:
    """
    Autonomous WhatsApp Web watcher using Playwright.
    Monitors for new messages, extracts content, and triggers AI processing.
    """
    
    def __init__(self, vault_path: str, session_path: str = None, check_interval: int = 30):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs_path = self.vault_path / 'Logs'
        self.session_path = Path(session_path) if session_path else self.vault_path / '.whatsapp_session'
        self.check_interval = check_interval

        # Create necessary directories
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        self.session_path.mkdir(parents=True, exist_ok=True)

        # WhatsApp Web configuration
        self.whatsapp_url = "https://web.whatsapp.com"
        self.tracked_chats: Dict[str, dict] = {}  # chat_id -> last_message_timestamp
        self.processed_messages: set = set()  # message_ids already processed

        # Keywords that trigger immediate action
        # Using phrases instead of single words to reduce false positives
        self.trigger_keywords = [
            'urgent', 'asap', 'invoice', 'payment',
            'need help', 'help me', 'emergency',
            'deadline', 'important', 'check this', 'review this',
            'please approve', 'send money', 'transfer',
            'bank account', 'pay now', 'due date'
        ]

        # State tracking
        self.is_running = False
        self.playwright = None  # CRITICAL: Must save to prevent garbage collection
        self.browser: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.last_check_time = datetime.now()
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.is_logged_in = False  # Track login state explicitly

        logger.info(f"WhatsApp Watcher initialized")
        logger.info(f"Vault: {self.vault_path}")
        logger.info(f"Session: {self.session_path}")
        logger.info(f"Session will persist across restarts in: {self.session_path}")
        
    def start(self) -> None:
        """Start the WhatsApp watcher loop"""
        logger.info("Starting WhatsApp Watcher...")
        self.is_running = True
        
        # Initialize browser
        self._initialize_browser()
        
        # Main monitoring loop
        while self.is_running:
            try:
                self._check_for_new_messages()
                self.reconnect_attempts = 0  # Reset on successful check
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Watcher interrupted by user")
                self.stop()
                break
                
            except Exception as e:
                logger.error(f"Error in watcher loop: {e}")
                self._handle_error(e)
                
    def stop(self) -> None:
        """Stop the WhatsApp watcher"""
        logger.info("Stopping WhatsApp Watcher...")
        self.is_running = False
        self._close_browser()
        
    def _initialize_browser(self) -> None:
        """Initialize Playwright browser with WhatsApp Web"""
        logger.info("="*60)
        logger.info("Initializing WhatsApp Web Browser")
        logger.info("="*60)
        
        # CRITICAL: Save Playwright instance to prevent garbage collection
        self.playwright = sync_playwright().start()
        logger.info("✅ Playwright started and saved to instance")

        try:
            # Check if session already exists (from previous run)
            session_exists = (self.session_path / "Default").exists() or (self.session_path / "Login Data").exists()
            
            if session_exists:
                logger.info("✅ Found existing WhatsApp Web session - Will attempt to reuse")
                logger.info("If already logged in, QR scan will be skipped")
            else:
                logger.info("⚠️  No existing session found - QR scan will be required")
            
            # Launch browser with persistent context to save session
            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=False,  # Start visible for QR scan, can switch to headless later
                viewport={'width': 1280, 'height': 720},
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-session-crashed-bubble',  # Prevent crash prompts
                ]
            )
            
            logger.info(f"✅ Browser launched with session path: {self.session_path}")

            self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()

            # Navigate to WhatsApp Web
            logger.info("Loading WhatsApp Web...")
            try:
                # Wait a moment for page to stabilize
                time.sleep(2)
                
                # Try to load WhatsApp Web
                self.page.goto(self.whatsapp_url, timeout=60000, wait_until='domcontentloaded')
                
                # Wait for network to settle
                self.page.wait_for_load_state('networkidle', timeout=10000)
            except Exception as nav_error:
                logger.warning(f"Navigation warning: {nav_error}")
                # Page might already be loaded, continue anyway
                pass
            
            # Wait for QR code or chat list (login detection)
            self._wait_for_login()
            
            # Mark as logged in
            self.is_logged_in = True
            logger.info("="*60)
            logger.info("✅✅✅ WHATSAPP LOGIN SUCCESSFUL ✅✅✅")
            logger.info("="*60)
            logger.info("Session saved and will persist across restarts")
            logger.info("Monitoring for new messages...")
            self._save_session_info()

        except Exception as e:
            logger.error(f"❌ Failed to initialize browser: {e}")
            raise WhatsAppSessionError(f"Browser initialization failed: {e}")
            
    def _wait_for_login(self, timeout: int = 180000) -> None:
        """
        Wait for user to complete WhatsApp login via QR code.
        Uses multiple detection methods since WhatsApp Web changes frequently.
        """
        logger.info("="*60)
        logger.info("LOGIN DETECTION SYSTEM")
        logger.info("="*60)
        logger.info("Waiting for WhatsApp Web to load...")
        logger.info("If you see QR code, please scan with your phone")
        logger.info("I'll detect when login is complete...")
        
        start_time = time.time()
        login_detected = False
        check_count = 0
        
        while time.time() - start_time < timeout / 1000:
            try:
                check_count += 1
                
                # Method 1: Check page title (most reliable)
                page_title = self.page.title()
                if page_title and page_title != "WhatsApp":
                    # Title like "(48) WhatsApp Business" means logged in
                    if "whatsapp" in page_title.lower():
                        logger.info("="*60)
                        logger.info("🎉🎉🎉 LOGIN DETECTED! 🎉🎉🎉")
                        logger.info("="*60)
                        logger.info(f"Page title: {page_title}")
                        logger.info(f"Login detection took {int(time.time() - start_time)} seconds")
                        
                        # Wait 3 seconds to confirm page is stable
                        time.sleep(3)
                        current_title = self.page.title()
                        if current_title == page_title:
                            logger.info("✅ Login confirmed - Title stable")
                            login_detected = True
                            break
                        else:
                            logger.info(f"Title changed to: {current_title}, waiting...")
                            continue
                
                # Method 2: Check URL (logged in users have different URL patterns)
                current_url = self.page.url
                if "web.whatsapp.com" in current_url:
                    # Check if there are chats visible
                    try:
                        # Look for any visible chat content
                        chat_indicators = [
                            'div[role="row"]',  # Chat rows
                            '#pane-side',  # Old sidebar
                            'div[aria-label]',  # Any labeled div
                        ]
                        
                        for indicator in chat_indicators:
                            elem = self.page.query_selector(indicator)
                            if elem:
                                logger.info(f"✅ Found chat element: {indicator}")
                                login_detected = True
                                break
                        
                        if login_detected:
                            break
                    except Exception:
                        pass
                
                # Log progress every 15 seconds
                if check_count % 15 == 0:
                    elapsed = int(time.time() - start_time)
                    logger.info(f"Still waiting... ({elapsed}s) Title: {page_title}")
                
                time.sleep(2)

            except Exception as e:
                logger.warning(f"Login check error (will retry): {e}")
                time.sleep(2)
        
        # Final verification
        if login_detected:
            logger.info("="*60)
            logger.info("✅✅✅ LOGIN VERIFIED - WhatsApp Web is ready! ✅✅✅")
            logger.info("="*60)
            return
        
        # If we reach here, login timed out
        logger.error("="*60)
        logger.error("❌ LOGIN TIMEOUT - Login not detected within 3 minutes")
        logger.error("="*60)
        raise WhatsAppSessionError("Login timeout. Please restart and scan QR code.")
        
    def _check_for_new_messages(self) -> List[dict]:
        """Check for new messages in all chats"""
        try:
            # Verify page is still accessible
            if not self.page or self.page.is_closed():
                self._reconnect()
                return []
                
            # Get all chat items
            new_messages = []
            
            try:
                # Find all chat list items
                chat_items = self.page.query_selector_all('[role="row"][aria-label*="unread"]')
                
                if chat_items:
                    logger.info(f"Found {len(chat_items)} chats with unread messages")
                    
                    for chat_item in chat_items:
                        try:
                            # Extract chat info
                            chat_name = self._extract_chat_name(chat_item)
                            last_message = self._extract_last_message(chat_item)
                            timestamp = self._extract_timestamp(chat_item)
                            
                            if chat_name and last_message:
                                chat_id = f"{chat_name}_{timestamp}"
                                
                                if chat_id not in self.processed_messages:
                                    self.processed_messages.add(chat_id)
                                    
                                    message_data = {
                                        'chat_name': chat_name,
                                        'last_message': last_message,
                                        'timestamp': timestamp or datetime.now().isoformat(),
                                        'is_trigger': self._is_trigger_message(last_message),
                                        'raw_data': last_message
                                    }
                                    
                                    new_messages.append(message_data)
                                    self._create_action_file(message_data)
                                    
                        except Exception as e:
                            logger.warning(f"Error processing chat item: {e}")
                            continue
                            
                return new_messages
                
            except PlaywrightTimeoutError:
                logger.warning("Timeout waiting for chat elements")
                return []
                
        except Exception as e:
            logger.error(f"Error checking for messages: {e}")
            return []
            
    def _extract_chat_name(self, chat_item) -> Optional[str]:
        """Extract chat name/title from chat list item"""
        try:
            # Try multiple selectors for chat name
            selectors = [
                '[data-testid="cell-frame-title"]',
                'span[dir="auto"][title]',
                'h2',
                'span[dir="ltr"]'
            ]
            
            for selector in selectors:
                element = chat_item.query_selector(selector)
                if element:
                    name = element.inner_text().strip()
                    if name and len(name) < 50:  # Sanity check
                        return name
                        
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting chat name: {e}")
            return None
            
    def _extract_last_message(self, chat_item) -> Optional[str]:
        """Extract last message preview from chat list item"""
        try:
            # Try multiple selectors for last message
            selectors = [
                '[data-testid="last-msg"]',
                'span[dir="auto"][class*="copyable-text"]',
                'span[class*="emojitext"]'
            ]
            
            for selector in selectors:
                element = chat_item.query_selector(selector)
                if element:
                    message = element.inner_text().strip()
                    if message:
                        return message
                        
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting message: {e}")
            return None
            
    def _extract_timestamp(self, chat_item) -> Optional[str]:
        """Extract message timestamp"""
        try:
            timestamp_element = chat_item.query_selector('[data-testid="chat-timestamp"]')
            if timestamp_element:
                return timestamp_element.inner_text().strip()
            return datetime.now().isoformat()
            
        except Exception:
            return datetime.now().isoformat()
            
    def _is_trigger_message(self, message: str) -> bool:
        """Check if message contains trigger keywords"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.trigger_keywords)
        
    def _create_action_file(self, message_data: dict) -> Path:
        """Create action file in Needs_Action folder"""
        try:
            chat_name = message_data['chat_name']
            timestamp = message_data['timestamp']
            
            # Sanitize filename
            safe_name = "".join(c if c.isalnum() or c in '._- ' else '_' for c in chat_name)
            filename = f"WHATSAPP_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = self.needs_action / filename
            
            # Create action file content
            priority = "HIGH" if message_data['is_trigger'] else "NORMAL"
            
            content = f"""---
type: whatsapp_message
from: {chat_name}
received: {timestamp}
priority: {priority}
status: pending
trigger_keywords: {message_data['is_trigger']}
created: {datetime.now().isoformat()}
---

# WhatsApp Message

## Sender
{chat_name}

## Message Content
{message_data['last_message']}

## Classification
- **Priority**: {priority}
- **Contains Trigger Words**: {message_data['is_trigger']}

## Suggested Actions
- [ ] Review message content
- [ ] Draft response (if needed)
- [ ] Move to Approved folder to send response
- [ ] Archive after processing

## Notes
Message automatically detected by WhatsApp Watcher.
"""
            
            filepath.write_text(content)
            logger.info(f"Action file created: {filepath.name}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error creating action file: {e}")
            raise
            
    def _send_message(self, chat_name: str, message: str) -> bool:
        """Send a message to a specific chat"""
        try:
            logger.info(f"Sending message to {chat_name}")
            
            # Open chat
            self._open_chat(chat_name)
            
            # Find message input box
            message_box = self.page.query_selector(
                '[data-testid="conversation-compose-box-input"]'
            )
            
            if not message_box:
                logger.error("Message input box not found")
                return False
                
            # Type message
            message_box.click()
            message_box.fill(message)
            
            # Click send button
            send_button = self.page.query_selector('[data-testid="compose-btn-send"]')
            if send_button:
                send_button.click()
                logger.info(f"Message sent to {chat_name}")
                return True
            else:
                # Try Enter key as fallback
                self.page.keyboard.press('Enter')
                logger.info(f"Message sent to {chat_name} (via Enter key)")
                return True
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
            
    def _open_chat(self, chat_name: str) -> bool:
        """Open a specific chat"""
        try:
            # Click on chat in list
            chat_element = self.page.query_selector(
                f'[data-testid="cell-frame-title"]:has-text("{chat_name}")'
            )
            
            if chat_element:
                chat_element.click()
                self.page.wait_for_timeout(1000)  # Wait for chat to load
                return True
            else:
                logger.warning(f"Chat '{chat_name}' not found in list")
                return False
                
        except Exception as e:
            logger.error(f"Error opening chat: {e}")
            return False
            
    def _handle_error(self, error: Exception) -> None:
        """Handle errors in the watcher loop"""
        logger.error(f"Handling error: {error}")
        
        self.reconnect_attempts += 1
        
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.critical("Max reconnect attempts reached. Stopping watcher.")
            self.stop()
            return
            
        # Attempt reconnection
        logger.info(f"Reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        self._reconnect()
        
    def _reconnect(self) -> None:
        """Reconnect to WhatsApp Web"""
        try:
            logger.info("Attempting to reconnect...")
            
            # Close existing browser
            self._close_browser()
            
            # Reinitialize
            self._initialize_browser()
            
            logger.info("Reconnection successful")
            
        except Exception as e:
            logger.error(f"Reconnection failed: {e}")
            time.sleep(5)  # Wait before retry
            
    def _close_browser(self) -> None:
        """Close browser and cleanup"""
        try:
            if self.browser:
                logger.info("Closing browser and saving session...")
                self.browser.close()
                logger.info(f"✅ Session saved to: {self.session_path}")
                self.browser = None
                self.page = None
            
            # Don't stop playwright - keep it for potential reuse
            # This ensures session persists properly
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")
        finally:
            self.is_logged_in = False
            
    def _save_session_info(self) -> None:
        """Save session information for debugging"""
        try:
            session_info = {
                'last_login': datetime.now().isoformat(),
                'vault_path': str(self.vault_path),
                'session_path': str(self.session_path),
                'status': 'active',
                'is_logged_in': self.is_logged_in,
                'browser_open': self.browser is not None,
            }

            info_file = self.session_path / 'session_info.json'
            info_file.write_text(json.dumps(session_info, indent=2))
            
            logger.info(f"💾 Session info saved to: {info_file}")
            logger.info(f"   Login Status: {'✅ Logged In' if self.is_logged_in else '❌ Not Logged In'}")
            logger.info(f"   Browser Status: {'✅ Open' if self.browser else '❌ Closed'}")

        except Exception as e:
            logger.warning(f"Could not save session info: {e}")
            
    def get_status(self) -> dict:
        """Get current watcher status"""
        return {
            'running': self.is_running,
            'is_logged_in': self.is_logged_in,
            'session_saved': self.session_path.exists(),
            'reconnect_attempts': self.reconnect_attempts,
            'tracked_chats': len(self.tracked_chats),
            'processed_messages': len(self.processed_messages),
            'last_check': self.last_check_time.isoformat(),
            'browser_open': self.browser is not None,
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Watcher for Personal AI Employee')
    parser.add_argument('--vault', type=str, help='Path to Obsidian vault', 
                       default=os.environ.get('OBSIDIAN_VAULT_PATH', '.'))
    parser.add_argument('--session', type=str, help='Path to session directory',
                       default=None)
    parser.add_argument('--interval', type=int, help='Check interval in seconds',
                       default=30)
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    
    args = parser.parse_args()
    
    # Initialize watcher
    watcher = WhatsAppWatcher(
        vault_path=args.vault,
        session_path=args.session,
        check_interval=args.interval
    )
    
    if args.test:
        print("Test mode - checking basic functionality...")
        print(f"Vault path: {args.vault}")
        print(f"Session path: {watcher.session_path}")
        print("All paths valid. Ready to start.")
        return
    
    # Start watching
    try:
        watcher.start()
    except KeyboardInterrupt:
        print("\nWatcher stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
