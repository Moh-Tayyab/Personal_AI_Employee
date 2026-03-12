"""
Social Media MCP Server - Post to Facebook and Instagram using Playwright

This server provides unified access to Facebook and Instagram posting.
For more control, use the dedicated mcp.facebook and mcp.instagram servers.

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    python -m mcp.social.server
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.base import BaseMCPServer, MCPTool
from mcp.facebook.browser import FacebookBrowserSync
from mcp.instagram.browser import InstagramBrowserSync


class SocialMCPServer(BaseMCPServer):
    """MCP server for Facebook/Instagram operations."""

    def __init__(self, config: dict = None):
        super().__init__("social", config)
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self._facebook_browser = None
        self._instagram_browser = None

    def _get_facebook_browser(self) -> FacebookBrowserSync:
        """Get or create Facebook browser instance."""
        if self._facebook_browser is None:
            session_path = os.getenv('FACEBOOK_SESSION_PATH', './vault/secrets/facebook_session')
            self._facebook_browser = FacebookBrowserSync(session_path)
        return self._facebook_browser

    def _get_instagram_browser(self) -> InstagramBrowserSync:
        """Get or create Instagram browser instance."""
        if self._instagram_browser is None:
            session_path = os.getenv('INSTAGRAM_SESSION_PATH', './vault/secrets/instagram_session')
            self._instagram_browser = InstagramBrowserSync(session_path)
        return self._instagram_browser

    def get_tools(self):
        return [
            # Facebook tools
            MCPTool(
                name="post_facebook",
                description="Post to Facebook",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Post content"},
                        "page_id": {"type": "string", "description": "Facebook page ID (optional)"}
                    },
                    "required": ["content"]
                }
            ),
            MCPTool(
                name="check_facebook_session",
                description="Check if Facebook session is valid",
                input_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            MCPTool(
                name="login_facebook",
                description="Login to Facebook",
                input_schema={
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Facebook email"},
                        "password": {"type": "string", "description": "Facebook password"}
                    },
                    "required": ["email", "password"]
                }
            ),
            # Instagram tools
            MCPTool(
                name="post_instagram",
                description="Post to Instagram (requires image)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "caption": {"type": "string", "description": "Image caption"},
                        "image_path": {"type": "string", "description": "Path to image file"}
                    },
                    "required": ["caption", "image_path"]
                }
            ),
            MCPTool(
                name="check_instagram_session",
                description="Check if Instagram session is valid",
                input_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            MCPTool(
                name="login_instagram",
                description="Login to Instagram",
                input_schema={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "Instagram username"},
                        "password": {"type": "string", "description": "Instagram password"}
                    },
                    "required": ["username", "password"]
                }
            ),
            # Scheduling (still file-based for cross-platform)
            MCPTool(
                name="schedule_social",
                description="Schedule a social media post for later",
                input_schema={
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": ["facebook", "instagram", "linkedin", "twitter"]},
                        "content": {"type": "string", "description": "Post content"},
                        "scheduled_time": {"type": "string", "description": "ISO timestamp"},
                        "image_path": {"type": "string", "description": "Path to image (for Instagram)"}
                    },
                    "required": ["platform", "content", "scheduled_time"]
                }
            )
        ]

    def handle_request(self, method: str, params: dict = None):
        params = params or {}

        # Facebook methods
        if method == "post_facebook":
            return self.post_facebook(params)
        elif method == "check_facebook_session":
            return self.check_facebook_session(params)
        elif method == "login_facebook":
            return self.login_facebook(params)
        # Instagram methods
        elif method == "post_instagram":
            return self.post_instagram(params)
        elif method == "check_instagram_session":
            return self.check_instagram_session(params)
        elif method == "login_instagram":
            return self.login_instagram(params)
        # Scheduling
        elif method == "schedule_social":
            return self.schedule_social(params)
        elif method == "list_tools":
            return [t.to_dict() for t in self.get_tools()]
        else:
            return {"error": f"Unknown method: {method}"}

    # ==================== Facebook ====================

    def post_facebook(self, params: dict) -> dict:
        content = params.get('content', '')
        page_id = params.get('page_id')

        if self.dry_run:
            return {"status": "dry_run", "message": f"[DRY RUN] Would post to Facebook: {content[:50]}..."}

        browser = None
        try:
            browser = self._get_facebook_browser()

            # Check session first
            session_status = browser.check_session()
            if session_status.get('status') != 'authenticated':
                return {
                    "status": "not_authenticated",
                    "message": "Please login first using login_facebook",
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

    def check_facebook_session(self, params: dict) -> dict:
        browser = None
        try:
            browser = self._get_facebook_browser()
            return browser.check_session()
        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            if browser:
                browser.close()

    def login_facebook(self, params: dict) -> dict:
        email = params.get('email', '')
        password = params.get('password', '')

        if not email or not password:
            return {"error": "Email and password are required"}

        browser = None
        try:
            browser = self._get_facebook_browser()
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

    # ==================== Instagram ====================

    def post_instagram(self, params: dict) -> dict:
        caption = params.get('caption', '')
        image_path = params.get('image_path')

        if not image_path:
            return {"error": "image_path is required for Instagram posts"}

        if self.dry_run:
            return {"status": "dry_run", "message": f"[DRY RUN] Would post to Instagram: {caption[:50]}..."}

        browser = None
        try:
            browser = self._get_instagram_browser()

            # Check session first
            session_status = browser.check_session()
            if session_status.get('status') != 'authenticated':
                return {
                    "status": "not_authenticated",
                    "message": "Please login first using login_instagram",
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

    def check_instagram_session(self, params: dict) -> dict:
        browser = None
        try:
            browser = self._get_instagram_browser()
            return browser.check_session()
        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            if browser:
                browser.close()

    def login_instagram(self, params: dict) -> dict:
        username = params.get('username', '')
        password = params.get('password', '')

        if not username or not password:
            return {"error": "Username and password are required"}

        browser = None
        try:
            browser = self._get_instagram_browser()
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

    # ==================== Scheduling ====================

    def schedule_social(self, params: dict) -> dict:
        platform = params.get('platform', '')
        content = params.get('content', '')
        scheduled_time = params.get('scheduled_time', '')
        image_path = params.get('image_path', '')

        scheduled_dir = Path('./vault/Scheduled')
        scheduled_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{platform}_scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        (scheduled_dir / filename).write_text(f"""---
type: scheduled_post
platform: {platform}
scheduled_time: {scheduled_time}
created: {datetime.now().isoformat()}
status: pending
image_path: {image_path or 'none'}
---

{content}
""")

        return {"status": "scheduled", "file": str(scheduled_dir / filename)}


def main():
    server = SocialMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()