"""
Twitter (X) MCP Server - Post to Twitter using Playwright

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    python -m mcp.twitter.server
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.base import BaseMCPServer, MCPTool
from mcp.twitter.browser import TwitterBrowserSync


class TwitterMCPServer(BaseMCPServer):
    """MCP server for Twitter/X operations."""

    def __init__(self, config: dict = None):
        super().__init__("twitter", config)
        self.session_path = os.getenv('TWITTER_SESSION_PATH', './vault/secrets/twitter_session')
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self._browser = None

    def _get_browser(self) -> TwitterBrowserSync:
        """Get or create browser instance."""
        if self._browser is None:
            self._browser = TwitterBrowserSync(self.session_path)
        return self._browser

    def get_tools(self):
        """Return available tools."""
        return [
            MCPTool(
                name="post_tweet",
                description="Post a tweet to Twitter/X (max 280 characters)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Tweet content (max 280 characters)"}
                    },
                    "required": ["content"]
                }
            ),
            MCPTool(
                name="get_timeline",
                description="Get recent tweets from your timeline",
                input_schema={
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "default": 10, "description": "Number of tweets to retrieve"}
                    }
                }
            ),
            MCPTool(
                name="get_profile",
                description="Get your Twitter/X profile information",
                input_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            MCPTool(
                name="schedule_tweet",
                description="Schedule a tweet for later posting",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Tweet content"},
                        "scheduled_time": {"type": "string", "description": "ISO timestamp"}
                    },
                    "required": ["content", "scheduled_time"]
                }
            ),
            MCPTool(
                name="check_session",
                description="Check if Twitter/X session is valid",
                input_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            MCPTool(
                name="login",
                description="Login to Twitter/X with credentials",
                input_schema={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "Twitter username or email"},
                        "password": {"type": "string", "description": "Twitter password"}
                    },
                    "required": ["username", "password"]
                }
            )
        ]

    def handle_request(self, method: str, params: dict = None):
        """Handle MCP request."""
        params = params or {}

        if method == "post_tweet":
            return self.post_tweet(params)
        elif method == "get_timeline":
            return self.get_timeline(params)
        elif method == "get_profile":
            return self.get_profile(params)
        elif method == "schedule_tweet":
            return self.schedule_tweet(params)
        elif method == "check_session":
            return self.check_session(params)
        elif method == "login":
            return self.login(params)
        elif method == "list_tools":
            return [t.to_dict() for t in self.get_tools()]
        else:
            return {"error": f"Unknown method: {method}"}

    def post_tweet(self, params: dict) -> dict:
        """Post a tweet."""
        content = params.get('content', '')

        if len(content) > 280:
            return {"error": "Tweet exceeds 280 characters"}

        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would post tweet: {content[:50]}...")
            return {"status": "dry_run", "message": "Tweet not sent (dry-run mode)"}

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

            # Post tweet
            result = browser.post_tweet(content)

            if result.get('status') == 'posted':
                self.logger.info(f"Successfully posted tweet: {content[:50]}...")
                return result
            else:
                self.logger.error(f"Tweet failed: {result}")
                return result

        except Exception as e:
            self.logger.error(f"Error posting tweet: {e}")
            return {"error": str(e)}
        finally:
            if browser:
                browser.close()

    def get_timeline(self, params: dict) -> dict:
        """Get timeline."""
        count = params.get('count', 10)

        browser = None
        try:
            browser = self._get_browser()
            return browser.get_timeline(count)
        except Exception as e:
            return {"error": str(e)}
        finally:
            if browser:
                browser.close()

    def get_profile(self, params: dict) -> dict:
        """Get profile info."""
        browser = None
        try:
            browser = self._get_browser()
            return browser.get_profile()
        except Exception as e:
            return {"error": str(e)}
        finally:
            if browser:
                browser.close()

    def schedule_tweet(self, params: dict) -> dict:
        """Schedule a tweet."""
        content = params.get('content', '')
        scheduled_time = params.get('scheduled_time', '')

        if len(content) > 280:
            return {"error": "Tweet exceeds 280 characters"}

        scheduled_dir = Path('./vault/Scheduled')
        scheduled_dir.mkdir(parents=True, exist_ok=True)

        filename = f"twitter_scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        (scheduled_dir / filename).write_text(f"""---
type: scheduled_post
platform: twitter
scheduled_time: {scheduled_time}
created: {datetime.now().isoformat()}
status: pending
---

{content}
""")

        return {"status": "scheduled", "file": str(scheduled_dir / filename)}

    def check_session(self, params: dict) -> dict:
        """Check if Twitter/X session is valid."""
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
        """Login to Twitter/X."""
        username = params.get('username', '')
        password = params.get('password', '')

        if not username or not password:
            return {"error": "Username and password are required"}

        browser = None
        try:
            browser = self._get_browser()
            result = browser.login(username, password)

            if result.get('status') in ['logged_in', 'already_logged_in']:
                self.logger.info(f"Twitter login successful: {username}")
                return result
            else:
                self.logger.error(f"Twitter login failed: {result}")
                return result
        except Exception as e:
            self.logger.error(f"Error during Twitter login: {e}")
            return {"error": str(e)}
        finally:
            if browser:
                browser.close()


def main():
    """Main entry point."""
    server = TwitterMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()