"""
LinkedIn MCP Server - Post to LinkedIn using Playwright

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    python -m mcp.linkedin.server
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.base import BaseMCPServer, MCPTool
from mcp.linkedin.browser import LinkedInBrowserSync


class LinkedInMCPServer(BaseMCPServer):
    """MCP server for LinkedIn operations."""

    def __init__(self, config: dict = None):
        super().__init__("linkedin", config)
        self.session_path = os.getenv('LINKEDIN_SESSION_PATH', './vault/secrets/linkedin_session')
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self._browser = None

    def _get_browser(self) -> LinkedInBrowserSync:
        """Get or create browser instance."""
        if self._browser is None:
            self._browser = LinkedInBrowserSync(self.session_path)
        return self._browser

    def get_tools(self):
        """Return available tools."""
        return [
            MCPTool(
                name="create_post",
                description="Create a LinkedIn post",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Post content (text)"},
                        "media_path": {"type": "string", "description": "Path to media file (image/video)"}
                    },
                    "required": ["content"]
                }
            ),
            MCPTool(
                name="get_profile",
                description="Get LinkedIn profile info",
                input_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            MCPTool(
                name="schedule_post",
                description="Schedule a LinkedIn post for later",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Post content"},
                        "scheduled_time": {"type": "string", "description": "ISO timestamp"},
                        "media_path": {"type": "string", "description": "Path to media file"}
                    },
                    "required": ["content", "scheduled_time"]
                }
            ),
            MCPTool(
                name="check_session",
                description="Check if LinkedIn session is valid",
                input_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            MCPTool(
                name="login",
                description="Login to LinkedIn with credentials",
                input_schema={
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "LinkedIn email"},
                        "password": {"type": "string", "description": "LinkedIn password"}
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
        """Create a LinkedIn post."""
        content = params.get('content', '')
        media_path = params.get('media_path')

        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would post to LinkedIn: {content[:50]}...")
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
            result = browser.create_post(content, media_path)
            
            if result.get('status') == 'posted':
                self.logger.info(f"Successfully posted to LinkedIn: {content[:50]}...")
                return result
            else:
                self.logger.error(f"Post failed: {result}")
                return result

        except Exception as e:
            self.logger.error(f"Error creating LinkedIn post: {e}")
            return {"error": str(e)}
        finally:
            if browser:
                browser.close()

    def get_profile(self, params: dict) -> dict:
        """Get LinkedIn profile info."""
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
        """Schedule a LinkedIn post."""
        content = params.get('content', '')
        scheduled_time = params.get('scheduled_time', '')
        media_path = params.get('media_path')

        # Save to scheduled posts
        scheduled_dir = Path('./vault/Scheduled')
        scheduled_dir.mkdir(parents=True, exist_ok=True)

        filename = f"linkedin_scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        scheduled_content = f"""---
type: scheduled_post
platform: linkedin
scheduled_time: {scheduled_time}
created: {datetime.now().isoformat()}
status: pending
media_path: {media_path or 'none'}
---

{content}
"""
        (scheduled_dir / filename).write_text(scheduled_content)

        return {"status": "scheduled", "file": str(scheduled_dir / filename)}

    def check_session(self, params: dict) -> dict:
        """Check if LinkedIn session is valid."""
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
        """Login to LinkedIn."""
        email = params.get('email', '')
        password = params.get('password', '')

        if not email or not password:
            return {"error": "Email and password are required"}

        browser = None
        try:
            browser = self._get_browser()
            result = browser.login(email, password)
            
            if result.get('status') in ['logged_in', 'already_logged_in']:
                self.logger.info(f"LinkedIn login successful: {email}")
                return result
            else:
                self.logger.error(f"LinkedIn login failed: {result}")
                return result
        except Exception as e:
            self.logger.error(f"Error during LinkedIn login: {e}")
            return {"error": str(e)}
        finally:
            if browser:
                browser.close()


def main():
    """Main entry point."""
    server = LinkedInMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
