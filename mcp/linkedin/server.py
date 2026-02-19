"""
LinkedIn MCP Server - Post to LinkedIn using Playwright

Requirements:
    pip install playwright

Usage:
    python -m mcp.linkedin.server
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.base import BaseMCPServer, MCPTool


class LinkedInMCPServer(BaseMCPServer):
    """MCP server for LinkedIn operations."""

    def __init__(self, config: dict = None):
        super().__init__("linkedin", config)
        self.session_path = os.getenv('LINKEDIN_SESSION_PATH', './vault/secrets/linkedin_session')
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

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
                        "media_url": {"type": "string", "description": "URL to media (image/video)"}
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
                        "media_url": {"type": "string", "description": "URL to media"}
                    },
                    "required": ["content", "scheduled_time"]
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
        elif method == "list_tools":
            return [t.to_dict() for t in self.get_tools()]
        else:
            return {"error": f"Unknown method: {method}"}

    def create_post(self, params: dict) -> dict:
        """Create a LinkedIn post."""
        content = params.get('content', '')

        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would post to LinkedIn: {content[:50]}...")
            return {"status": "dry_run", "message": "Post not sent (dry-run mode)"}

        try:
            # In production, use Playwright to post
            # For now, save as draft
            drafts_dir = Path('./vault/Drafts')
            drafts_dir.mkdir(parents=True, exist_ok=True)

            from datetime import datetime
            filename = f"linkedin_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

            draft_content = f"""---
type: linkedin_draft
created: {datetime.now().isoformat()}
status: draft
platform: linkedin
---

{content}
"""
            (drafts_dir / filename).write_text(draft_content)

            return {"status": "draft_created", "file": str(drafts_dir / filename)}

        except Exception as e:
            self.logger.error(f"Error creating LinkedIn post: {e}")
            return {"error": str(e)}

    def get_profile(self, params: dict) -> dict:
        """Get LinkedIn profile info."""
        return {
            "name": "Not connected",
            "message": "Connect session to LinkedIn first"
        }

    def schedule_post(self, params: dict) -> dict:
        """Schedule a LinkedIn post."""
        content = params.get('content', '')
        scheduled_time = params.get('scheduled_time', '')

        # Save to scheduled posts
        scheduled_dir = Path('./vault/Scheduled')
        scheduled_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime
        filename = f"linkedin_scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        scheduled_content = f"""---
type: scheduled_post
platform: linkedin
scheduled_time: {scheduled_time}
created: {datetime.now().isoformat()}
status: pending
---

{content}
"""
        (scheduled_dir / filename).write_text(scheduled_content)

        return {"status": "scheduled", "file": str(scheduled_dir / filename)}


def main():
    """Main entry point."""
    server = LinkedInMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
