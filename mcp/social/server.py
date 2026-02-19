"""
Facebook/Instagram MCP Server - Post to social media

Requirements:
    pip install playwright

Usage:
    python -m mcp.social.server
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.base import BaseMCPServer, MCPTool


class SocialMCPServer(BaseMCPServer):
    """MCP server for Facebook/Instagram operations."""

    def __init__(self, config: dict = None):
        super().__init__("social", config)
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

    def get_tools(self):
        return [
            MCPTool(
                name="post_facebook",
                description="Post to Facebook",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Post content"},
                        "page_id": {"type": "string", "description": "Facebook page ID"}
                    },
                    "required": ["content"]
                }
            ),
            MCPTool(
                name="post_instagram",
                description="Post to Instagram",
                input_schema={
                    "type": "object",
                    "properties": {
                        "caption": {"type": "string", "description": "Image caption"},
                        "image_path": {"type": "string", "description": "Path to image"}
                    },
                    "required": ["caption"]
                }
            ),
            MCPTool(
                name="schedule_social",
                description="Schedule a social media post",
                input_schema={
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": ["facebook", "instagram", "linkedin", "twitter"]},
                        "content": {"type": "string", "description": "Post content"},
                        "scheduled_time": {"type": "string", "description": "ISO timestamp"}
                    },
                    "required": ["platform", "content", "scheduled_time"]
                }
            )
        ]

    def handle_request(self, method: str, params: dict = None):
        params = params or {}

        if method == "post_facebook":
            return self.post_facebook(params)
        elif method == "post_instagram":
            return self.post_instagram(params)
        elif method == "schedule_social":
            return self.schedule_social(params)
        elif method == "list_tools":
            return [t.to_dict() for t in self.get_tools()]
        else:
            return {"error": f"Unknown method: {method}"}

    def post_facebook(self, params: dict) -> dict:
        content = params.get('content', '')

        if self.dry_run:
            return {"status": "dry_run", "message": f"[DRY RUN] Would post to Facebook: {content[:50]}..."}

        # Save as draft
        drafts_dir = Path('./vault/Drafts')
        drafts_dir.mkdir(parents=True, exist_ok=True)

        filename = f"facebook_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        (drafts_dir / filename).write_text(f"""---
type: facebook_draft
created: {datetime.now().isoformat()}
status: draft
platform: facebook
---

{content}
""")

        return {"status": "draft_created", "file": str(drafts_dir / filename)}

    def post_instagram(self, params: dict) -> dict:
        caption = params.get('caption', '')
        image_path = params.get('image_path', '')

        if self.dry_run:
            return {"status": "dry_run", "message": f"[DRY RUN] Would post to Instagram: {caption[:50]}..."}

        drafts_dir = Path('./vault/Drafts')
        drafts_dir.mkdir(parents=True, exist_ok=True)

        filename = f"instagram_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        (drafts_dir / filename).write_text(f"""---
type: instagram_draft
created: {datetime.now().isoformat()}
status: draft
platform: instagram
image: {image_path}
---

{caption}
""")

        return {"status": "draft_created", "file": str(drafts_dir / filename)}

    def schedule_social(self, params: dict) -> dict:
        platform = params.get('platform', '')
        content = params.get('content', '')
        scheduled_time = params.get('scheduled_time', '')

        scheduled_dir = Path('./vault/Scheduled')
        scheduled_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{platform}_scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        (scheduled_dir / filename).write_text(f"""---
type: scheduled_post
platform: {platform}
scheduled_time: {scheduled_time}
created: {datetime.now().isoformat()}
status: pending
---

{content}
""")

        return {"status": "scheduled", "file": str(scheduled_dir / filename)}


def main():
    server = SocialMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
