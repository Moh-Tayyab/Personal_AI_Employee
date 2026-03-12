"""
Instagram MCP Server - Post to Instagram using Playwright

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    python -m mcp.instagram.server
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.base import BaseMCPServer, MCPTool
from mcp.instagram.browser import InstagramBrowserSync


class InstagramMCPServer(BaseMCPServer):
    """MCP server for Instagram operations."""

    def __init__(self, config: dict = None):
        super().__init__("instagram", config)
        self.session_path = os.getenv('INSTAGRAM_SESSION_PATH', './vault/secrets/instagram_session')
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self._browser = None

    def _get_browser(self) -> InstagramBrowserSync:
        """Get or create browser instance."""
        if self._browser is None:
            self._browser = InstagramBrowserSync(self.session_path)
        return self._browser

    def get_tools(self):
        """Return available tools."""
        return [
            MCPTool(
                name="create_post",
                description="Create an Instagram post with image and caption",
                input_schema={
                    "type": "object",
                    "properties": {
                        "caption": {"type": "string", "description": "Post caption (text)"},
                        "image_path": {"type": "string", "description": "Path to image file (required for Instagram posts)"}
                    },
                    "required": ["caption", "image_path"]
                }
            ),
            MCPTool(
                name="get_feed",
                description="Get recent posts from Instagram feed",
                input_schema={
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "default": 10, "description": "Number of posts to retrieve"}
                    }
                }
            ),
            MCPTool(
                name="get_profile",
                description="Get current user's Instagram profile information",
                input_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            MCPTool(
                name="schedule_post",
                description="Schedule an Instagram post for later",
                input_schema={
                    "type": "object",
                    "properties": {
                        "caption": {"type": "string", "description": "Post caption"},
                        "image_path": {"type": "string", "description": "Path to image file"},
                        "scheduled_time": {"type": "string", "description": "ISO timestamp"}
                    },
                    "required": ["caption", "image_path", "scheduled_time"]
                }
            ),
            MCPTool(
                name="check_session",
                description="Check if Instagram session is valid",
                input_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            MCPTool(
                name="login",
                description="Login to Instagram with credentials",
                input_schema={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "Instagram username"},
                        "password": {"type": "string", "description": "Instagram password"}
                    },
                    "required": ["username", "password"]
                }
            )
        ]

    def handle_request(self, method: str, params: dict = None):
        """Handle MCP request."""
        params = params or {}

        if method == "create_post":
            return self.create_post(params)
        elif method == "get_feed":
            return self.get_feed(params)
        elif method == "get_profile":
            return self.get_profile(params)
        elif method == "schedule_post":
            return self.schedule_post(params)
        elif method == "check_session":
            return self.check_session(params)
        elif method == "login":
            return self.login(params)
        elif method == "list_tools":
            return [t.to_dict() for t in self.get_tools()]
        else:
            return {"error": f"Unknown method: {method}"}

    def create_post(self, params: dict) -> dict:
        """Create an Instagram post."""
        caption = params.get('caption', '')
        image_path = params.get('image_path')

        if not image_path:
            return {"error": "image_path is required for Instagram posts"}

        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would post to Instagram: {caption[:50]}...")
            return {"status": "dry_run", "message": "Post not sent (dry-run mode)"}

        browser = None
        try:
            browser = self._get_browser()

            # Check session first
            session_status = browser.check_session()
            if session_status.get('status') != 'authenticated':
                return {
                    "status": "not_authenticated",
                    "message": "Please login first using the login method",
                    "session_status": session_status
                }

            # Create post
            result = browser.create_post(caption, image_path)

            if result.get('status') == 'posted':
                self.logger.info(f"Successfully posted to Instagram: {caption[:50]}...")
                return result
            else:
                self.logger.error(f"Post failed: {result}")
                return result

        except Exception as e:
            self.logger.error(f"Error creating Instagram post: {e}")
            return {"error": str(e)}
        finally:
            if browser:
                browser.close()

    def get_feed(self, params: dict) -> dict:
        """Get Instagram feed."""
        count = params.get('count', 10)

        browser = None
        try:
            browser = self._get_browser()
            return browser.get_feed(count)
        except Exception as e:
            return {"error": str(e)}
        finally:
            if browser:
                browser.close()

    def get_profile(self, params: dict) -> dict:
        """Get Instagram profile."""
        browser = None
        try:
            browser = self._get_browser()
            return browser.get_profile()
        except Exception as e:
            return {"error": str(e)}
        finally:
            if browser:
                browser.close()

    def schedule_post(self, params: dict) -> dict:
        """Schedule an Instagram post."""
        caption = params.get('caption', '')
        image_path = params.get('image_path', '')
        scheduled_time = params.get('scheduled_time', '')

        # Save to scheduled posts
        scheduled_dir = Path('./vault/Scheduled')
        scheduled_dir.mkdir(parents=True, exist_ok=True)

        filename = f"instagram_scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        scheduled_content = f"""---
type: scheduled_post
platform: instagram
scheduled_time: {scheduled_time}
created: {datetime.now().isoformat()}
status: pending
image_path: {image_path}
---

{caption}
"""
        (scheduled_dir / filename).write_text(scheduled_content)

        return {"status": "scheduled", "file": str(scheduled_dir / filename)}

    def check_session(self, params: dict) -> dict:
        """Check if Instagram session is valid."""
        browser = None
        try:
            browser = self._get_browser()
            return browser.check_session()
        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            if browser:
                browser.close()

    def login(self, params: dict) -> dict:
        """Login to Instagram."""
        username = params.get('username', '')
        password = params.get('password', '')

        if not username or not password:
            return {"error": "Username and password are required"}

        browser = None
        try:
            browser = self._get_browser()
            result = browser.login(username, password)

            if result.get('status') in ['logged_in', 'already_logged_in']:
                self.logger.info(f"Instagram login successful: {username}")
                return result
            else:
                self.logger.error(f"Instagram login failed: {result}")
                return result
        except Exception as e:
            self.logger.error(f"Error during Instagram login: {e}")
            return {"error": str(e)}
        finally:
            if browser:
                browser.close()


def main():
    """Main entry point."""
    server = InstagramMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()