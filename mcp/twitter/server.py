"""
Twitter (X) MCP Server - Post to Twitter using Playwright

Requirements:
    pip install playwright

Usage:
    python -m mcp.twitter.server
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.base import BaseMCPServer, MCPTool


class TwitterMCPServer(BaseMCPServer):
    """MCP server for Twitter/X operations."""

    def __init__(self, config: dict = None):
        super().__init__("twitter", config)
        self.session_path = os.getenv('TWITTER_SESSION_PATH', './vault/secrets/twitter_session')
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

    def get_tools(self):
        """Return available tools."""
        return [
            MCPTool(
                name="post_tweet",
                description="Post a tweet to Twitter/X",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Tweet content (max 280 chars)"}
                    },
                    "required": ["content"]
                }
            ),
            MCPTool(
                name="schedule_tweet",
                description="Schedule a tweet for later",
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
                name="get_timeline",
                description="Get recent tweets from timeline",
                input_schema={
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "default": 10}
                    }
                }
            )
        ]

    def handle_request(self, method: str, params: dict = None):
        """Handle MCP request."""
        params = params or {}

        if method == "post_tweet":
            return self.post_tweet(params)
        elif method == "schedule_tweet":
            return self.schedule_tweet(params)
        elif method == "get_timeline":
            return self.get_timeline(params)
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

        # Save as draft for now
        drafts_dir = Path('./vault/Drafts')
        drafts_dir.mkdir(parents=True, exist_ok=True)

        filename = f"twitter_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        (drafts_dir / filename).write_text(f"""---
type: twitter_draft
created: {datetime.now().isoformat()}
status: draft
platform: twitter
---

{content}
""")

        return {"status": "draft_created", "file": str(drafts_dir / filename)}

    def schedule_tweet(self, params: dict) -> dict:
        """Schedule a tweet."""
        content = params.get('content', '')
        scheduled_time = params.get('scheduled_time', '')

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

    def get_timeline(self, params: dict) -> dict:
        """Get timeline."""
        return {"tweets": [], "message": "Connect session to Twitter first"}


def main():
    server = TwitterMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
