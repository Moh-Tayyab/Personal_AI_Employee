"""
Facebook MCP Server - Post to Facebook using Playwright

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    python -m mcp.facebook.server
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.base import BaseMCPServer, MCPTool
from mcp.facebook.browser import FacebookBrowserSync


class FacebookMCPServer(BaseMCPServer):
    """MCP server for Facebook operations."""

    def __init__(self, config: dict = None):
        super().__init__("facebook", config)
        self.session_path = os.getenv('FACEBOOK_SESSION_PATH', './vault/secrets/facebook_session')
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self._browser = None

    def _get_browser(self) -> FacebookBrowserSync:
        """Get or create browser instance."""
        if self._browser is None:
            self._browser = FacebookBrowserSync(self.session_path)
        return self._browser

    def get_tools(self):
        """Return available tools."""
        return [
            MCPTool(
                name="create_post",
                description="Create a Facebook post",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Post content (text)"},
                        "page_id": {"type": "string", "description": "Facebook page ID (optional, for page posts)"}
                    },
                    "required": ["content"]
                }
            ),
            MCPTool(
                name="get_feed",
                description="Get recent posts from Facebook feed",
                input_schema={
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "default": 10, "description": "Number of posts to retrieve"}
                    }
                }
            ),
            MCPTool(
                name="schedule_post",
                description="Schedule a Facebook post for later",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Post content"},
                        "scheduled_time": {"type": "string", "description": "ISO timestamp"},
                        "page_id": {"type": "string", "description": "Facebook page ID (optional)"}
                    },
                    "required": ["content", "scheduled_time"]
                }
            ),
            MCPTool(
                name="check_session",
                description="Check if Facebook session is valid",
                input_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            MCPTool(
                name="login",
                description="Login to Facebook with credentials",
                input_schema={
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Facebook email"},
                        "password": {"type": "string", "description": "Facebook password"}
                    },
                    "required": ["email", "password"]
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
        """Create a Facebook post."""
        content = params.get('content', '')
        page_id = params.get('page_id')

        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would post to Facebook: {content[:50]}...")
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
            result = browser.create_post(content, page_id)

            if result.get('status') == 'posted':
                self.logger.info(f"Successfully posted to Facebook: {content[:50]}...")
                return result
            else:
                self.logger.error(f"Post failed: {result}")
                return result

        except Exception as e:
            self.logger.error(f"Error creating Facebook post: {e}")
            return {"error": str(e)}
        finally:
            if browser:
                browser.close()

    def get_feed(self, params: dict) -> dict:
        """Get Facebook feed."""
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

    def schedule_post(self, params: dict) -> dict:
        """Schedule a Facebook post."""
        content = params.get('content', '')
        scheduled_time = params.get('scheduled_time', '')
        page_id = params.get('page_id')

        # Save to scheduled posts
        scheduled_dir = Path('./vault/Scheduled')
        scheduled_dir.mkdir(parents=True, exist_ok=True)

        filename = f"facebook_scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        scheduled_content = f"""---
type: scheduled_post
platform: facebook
scheduled_time: {scheduled_time}
created: {datetime.now().isoformat()}
status: pending
page_id: {page_id or 'none'}
---

{content}
"""
        (scheduled_dir / filename).write_text(scheduled_content)

        return {"status": "scheduled", "file": str(scheduled_dir / filename)}

    def check_session(self, params: dict) -> dict:
        """Check if Facebook session is valid."""
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
        """Login to Facebook."""
        email = params.get('email', '')
        password = params.get('password', '')

        if not email or not password:
            return {"error": "Email and password are required"}

        browser = None
        try:
            browser = self._get_browser()
            result = browser.login(email, password)

            if result.get('status') in ['logged_in', 'already_logged_in']:
                self.logger.info(f"Facebook login successful: {email}")
                return result
            else:
                self.logger.error(f"Facebook login failed: {result}")
                return result
        except Exception as e:
            self.logger.error(f"Error during Facebook login: {e}")
            return {"error": str(e)}
        finally:
            if browser:
                browser.close()


def main():
    """Main entry point."""
    server = FacebookMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()