"""
Filesystem MCP Server - File operations for Claude Code

This MCP server provides file system operations for Claude Code.

Usage:
    python -m mcp.filesystem.server
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.base import BaseMCPServer, MCPTool


class FilesystemMCPServer(BaseMCPServer):
    """MCP server for filesystem operations."""

    def __init__(self, config: dict = None):
        super().__init__("filesystem", config)
        self.vault_path = Path(os.getenv('VAULT_PATH', './vault'))

    def get_tools(self):
        """Return available tools."""
        return [
            MCPTool(
                name="list_files",
                description="List files in a directory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path (relative to vault)"},
                        "pattern": {"type": "string", "description": "Glob pattern (e.g., *.md)"}
                    }
                }
            ),
            MCPTool(
                name="read_file",
                description="Read a file's contents",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path (relative to vault)"}
                    },
                    "required": ["path"]
                }
            ),
            MCPTool(
                name="write_file",
                description="Write content to a file",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path (relative to vault)"},
                        "content": {"type": "string", "description": "Content to write"}
                    },
                    "required": ["path", "content"]
                }
            ),
            MCPTool(
                name="move_file",
                description="Move a file to another location",
                input_schema={
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "description": "Source path"},
                        "destination": {"type": "string", "description": "Destination path"}
                    },
                    "required": ["source", "destination"]
                }
            ),
            MCPTool(
                name="create_directory",
                description="Create a directory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path (relative to vault)"}
                    },
                    "required": ["path"]
                }
            )
        ]

    def handle_request(self, method: str, params: dict = None):
        """Handle MCP request."""
        params = params or {}

        if method == "list_files":
            return self.list_files(params)
        elif method == "read_file":
            return self.read_file(params)
        elif method == "write_file":
            return self.write_file(params)
        elif method == "move_file":
            return self.move_file(params)
        elif method == "create_directory":
            return self.create_directory(params)
        elif method == "list_tools":
            return [t.to_dict() for t in self.get_tools()]
        else:
            return {"error": f"Unknown method: {method}"}

    def list_files(self, params: dict) -> dict:
        """List files in a directory."""
        rel_path = params.get('path', '')
        full_path = self.vault_path / rel_path

        if not full_path.exists():
            return {"error": f"Path does not exist: {rel_path}"}

        pattern = params.get('pattern', '*')
        files = [str(f.relative_to(self.vault_path)) for f in full_path.glob(pattern)]

        return {"files": files, "path": str(full_path.relative_to(self.vault_path))}

    def read_file(self, params: dict) -> dict:
        """Read a file."""
        rel_path = params.get('path', '')
        full_path = self.vault_path / rel_path

        if not full_path.exists():
            return {"error": f"File does not exist: {rel_path}"}

        try:
            content = full_path.read_text()
            return {"content": content, "path": rel_path}
        except Exception as e:
            return {"error": str(e)}

    def write_file(self, params: dict) -> dict:
        """Write to a file."""
        rel_path = params.get('path', '')
        content = params.get('content', '')
        full_path = self.vault_path / rel_path

        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            full_path.write_text(content)
            return {"status": "success", "path": rel_path}
        except Exception as e:
            return {"error": str(e)}

    def move_file(self, params: dict) -> dict:
        """Move a file."""
        source = params.get('source', '')
        destination = params.get('destination', '')

        source_path = self.vault_path / source
        dest_path = self.vault_path / destination

        if not source_path.exists():
            return {"error": f"Source does not exist: {source}"}

        # Ensure destination parent exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            source_path.rename(dest_path)
            return {"status": "success", "from": source, "to": destination}
        except Exception as e:
            return {"error": str(e)}

    def create_directory(self, params: dict) -> dict:
        """Create a directory."""
        rel_path = params.get('path', '')
        full_path = self.vault_path / rel_path

        try:
            full_path.mkdir(parents=True, exist_ok=True)
            return {"status": "success", "path": rel_path}
        except Exception as e:
            return {"error": str(e)}


def main():
    """Main entry point."""
    server = FilesystemMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
