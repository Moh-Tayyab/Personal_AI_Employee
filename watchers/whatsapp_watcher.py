"""
WhatsApp Watcher - Monitors WhatsApp Web for new messages

Requirements:
    pip install playwright
    playwright install chromium

Note: This uses WhatsApp Web automation. Be aware of WhatsApp's terms of service.
This is for educational/personal use only.

Usage:
    python -m watchers.whatsapp_watcher --vault ./vault --session-path ./session
"""

import os
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

import time
import signal

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchers.base_watcher import BaseWatcher


class WhatsAppWatcher(BaseWatcher):
    """Watches WhatsApp Web for new messages with specific keywords."""

    def __init__(
        self,
        vault_path: str,
        session_path: str = None,
        headless: bool = True,
        check_interval: int = 30
    ):
        super().__init__(vault_path, check_interval=check_interval, name="WhatsAppWatcher")
        self.session_path = Path(session_path) if session_path else None
        self.headless = headless
        self.keywords = [
            'urgent', 'asap', 'invoice', 'payment', 'help',
            'price', 'pricing', 'quote', 'meeting', 'deadline',
            'important', 'emergency', 'critical'
        ]
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def _setup_browser(self):
        """Initialize Playwright browser."""
        self.playwright = sync_playwright().start()
        if self.session_path and self.session_path.exists():
            # Use existing session
            self.context = self.playwright.chromium.launch_persistent_context(
                str(self.session_path),
                headless=self.headless,
                args=['--no-sandbox']
            )
            if self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = self.context.new_page()
        else:
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox']
            )
            self.page = self.browser.new_page()

    def _ensure_logged_in(self):
        """Ensure WhatsApp Web is logged in."""
        try:
            self.page.goto('https://web.whatsapp.com')
            # Wait for QR code or main chat list
            self.page.wait_for_selector(
                '[data-testid="chat-list"], [data-testid="qr-code"]',
                timeout=30000
            )

            # Check if QR code is present (not logged in)
            qr_code = self.page.query_selector('[data-testid="qr-code"]')
            if qr_code:
                self.logger.warning("Please scan QR code to login. Waiting...")
                self.page.wait_for_selector(
                    '[data-testid="chat-list"]',
                    timeout=120000  # 2 minutes to scan
                )
                self.logger.info("Logged in successfully")

                # Save session for next time
                if self.session_path:
                    self.session_path.parent.mkdir(parents=True, exist_ok=True)
                    self.context.storage_state(path=str(self.session_path))

        except Exception as e:
            self.logger.error(f"Error ensuring WhatsApp login: {e}")
            raise

    def check_for_updates(self) -> list:
        """Check for new messages with keywords."""
        messages = []

        try:
            if not self.page:
                self._setup_browser()
                self._ensure_logged_in()

            # Refresh to get latest messages
            self.page.reload()
            self.page.wait_for_timeout(2000)

            # Find chat list
            chat_list = self.page.query_selector_all('[data-testid="chat-list"] > div > div')

            for chat in chat_list:
                try:
                    # Get chat name
                    name_elem = chat.query_selector('span[title]')
                    if not name_elem:
                        continue
                    chat_name = name_elem.get_attribute('title') or "Unknown"

                    # Check for unread indicator
                    unread = chat.query_selector('[aria-label*="unread"], [data-testid="unread-count"]')
                    if not unread:
                        continue

                    # Click on chat to see messages
                    chat.click()
                    self.page.wait_for_timeout(1000)

                    # Get last message
                    messages_container = self.page.query_selector('[data-testid="message-list"]')
                    if not messages_container:
                        continue

                    last_msg = messages_container.query_selector('div.message:last-child')
                    if not last_msg:
                        continue

                    msg_text = last_msg.inner_text().lower()

                    # Check for keywords
                    found_keywords = [kw for kw in self.keywords if kw in msg_text]
                    if found_keywords:
                        messages.append({
                            'id': f"{chat_name}_{datetime.now().timestamp()}",
                            'chat': chat_name,
                            'message': last_msg.inner_text(),
                            'keywords': found_keywords,
                            'timestamp': datetime.now().isoformat()
                        })
                        self.logger.info(f"Found keyword in message from {chat_name}: {found_keywords}")

                    # Go back to chat list
                    self.page.go_back()
                    self.page.wait_for_timeout(500)

                except Exception as e:
                    self.logger.error(f"Error processing chat: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
            # Try to reinitialize on error
            self._cleanup()
            self._setup_browser()
            self._ensure_logged_in()

        return messages

    def _cleanup(self):
        """Cleanup browser resources."""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except:
            pass
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None

    def create_action_file(self, message) -> Path:
        """Create action file for a WhatsApp message."""
        content = f"""---
type: whatsapp
source: whatsapp_web
chat: {message['chat']}
keywords: {', '.join(message['keywords'])}
received: {message['timestamp']}
priority: high
status: pending
---

# WhatsApp Message

## From
{message['chat']}

## Message
{message['message']}

## Trigger Keywords
{', '.join(message['keywords'])}

## Suggested Actions

- [ ] Review message content
- [ ] Respond if needed (REQUIRES APPROVAL for new contacts)
- [ ] Create follow-up task (if applicable)
- [ ] Mark as processed

## Notes
_AI Employee: Process this message according to Company Handbook rules._
_WhatsApp messages require approval before sending responses._
"""

        # Create filename
        safe_name = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in message['chat'][:20])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'WHATSAPP_{timestamp}_{safe_name}.md'

        filepath = self.needs_action / filename
        filepath.write_text(content)

        return filepath

    def run(self):
        """Run the WhatsApp watcher."""
        self.logger.info("Starting WhatsApp watcher")

        # Setup signal handlers
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down...")
            self.running = False
            self._cleanup()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Initialize browser
        try:
            self._setup_browser()
            self._ensure_logged_in()
        except Exception as e:
            self.logger.error(f"Failed to setup WhatsApp: {e}")
            return

        processed_ids = self.get_processed_ids()

        while self.running:
            try:
                items = self.check_for_updates()
                new_items = [i for i in items if i['id'] not in processed_ids]

                for item in new_items:
                    try:
                        filepath = self.create_action_file(item)
                        processed_ids.add(item['id'])
                        self.save_processed_ids(processed_ids)
                        self.logger.info(f"Created action file: {filepath}")
                    except Exception as e:
                        self.logger.error(f"Error processing item: {e}")

            except Exception as e:
                self.logger.error(f"Error in check loop: {e}")

            time.sleep(self.check_interval)

        self._cleanup()
        self.logger.info("WhatsApp watcher stopped")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='WhatsApp Watcher')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--session-path', help='Path to session storage')
    parser.add_argument('--headless', action='store_true', default=True, help='Run in headless mode')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')

    args = parser.parse_args()

    watcher = WhatsAppWatcher(
        vault_path=args.vault,
        session_path=args.session_path,
        headless=args.headless,
        check_interval=args.interval
    )
    watcher.run()


if __name__ == "__main__":
    main()
