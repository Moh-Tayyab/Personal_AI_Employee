"""
Email MCP Server - Send emails via Claude Code

This MCP server allows Claude Code to send emails through Gmail.

Usage:
    python -m mcp.email.server
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.base import BaseMCPServer, MCPTool


class EmailMCPServer(BaseMCPServer):
    """MCP server for email operations."""

    def __init__(self, config: dict = None):
        super().__init__("email", config)
        self.vault_path = Path(os.getenv('VAULT_PATH', './vault'))

    def get_tools(self):
        """Return available tools."""
        return [
            MCPTool(
                name="send_email",
                description="Send an email to a recipient",
                input_schema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body"},
                        "cc": {"type": "string", "description": "CC recipients"},
                        "attachments": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File paths to attach"
                        }
                    },
                    "required": ["to", "subject", "body"]
                }
            ),
            MCPTool(
                name="draft_email",
                description="Create a draft email (doesn't send)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body"}
                    },
                    "required": ["to", "subject", "body"]
                }
            ),
            MCPTool(
                name="search_emails",
                description="Search emails in Gmail",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Gmail search query"},
                        "max_results": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                }
            )
        ]

    def handle_request(self, method: str, params: dict = None):
        """Handle MCP request."""
        params = params or {}

        if method == "send_email":
            return self.send_email(params)
        elif method == "draft_email":
            return self.draft_email(params)
        elif method == "search_emails":
            return self.search_emails(params)
        elif method == "list_tools":
            return [t.to_dict() for t in self.get_tools()]
        else:
            return {"error": f"Unknown method: {method}"}

    def send_email(self, params: dict) -> dict:
        """Send an email."""
        self.logger.info(f"Sending email to: {params.get('to')}")

        # Check dry-run mode
        dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

        if dry_run:
            self.logger.info(f"[DRY RUN] Would send email: {params}")
            return {
                "status": "dry_run",
                "message": "Email not sent (dry-run mode)",
                "params": params
            }

        # Actual send logic would go here
        # For now, create a draft instead
        return self.draft_email(params)

    def draft_email(self, params: dict) -> dict:
        """Create a draft email."""
        drafts_folder = self.vault_path / 'Drafts'
        drafts_folder.mkdir(parents=True, exist_ok=True)

        from datetime import datetime
        filename = f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""---
type: email_draft
to: {params.get('to')}
subject: {params.get('subject')}
created: {datetime.now().isoformat()}
status: draft
---

{params.get('body')}
"""

        draft_path = drafts_folder / filename
        draft_path.write_text(content)

        return {
            "status": "created",
            "draft_path": str(draft_path)
        }

    def search_emails(self, params: dict) -> dict:
        """Search emails."""
        # Placeholder - would use Gmail API
        return {
            "status": "not_implemented",
            "message": "Search not yet implemented"
        }


def main():
    """Main entry point."""
    server = EmailMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
