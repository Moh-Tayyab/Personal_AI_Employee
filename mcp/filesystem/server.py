#!/usr/bin/env python3
"""
Filesystem MCP Server for Personal AI Employee

Provides tools for file and directory operations, integrated with vault.

Configuration:
- Set VAULT_PATH environment variable to vault directory

Run:
    python mcp/filesystem/server.py
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("filesystem-mcp")

def get_vault_path() -> Path:
    """Get vault path from environment or default."""
    vault_path = os.getenv('VAULT_PATH')
    if not vault_path:
        # Default to parent of project root
        vault_path = Path(__file__).parent.parent.parent / 'vault'
    vault_path = Path(vault_path)
    vault_path.mkdir(parents=True, exist_ok=True)
    return vault_path

def ensure_within_vault(path: Path) -> bool:
    """
    Ensure that the given path is within the vault directory for security.
    Returns True if safe, False otherwise.
    """
    vault_path = get_vault_path()
    try:
        resolved = path.resolve()
        return str(resolved).startswith(str(vault_path.resolve()))
    except Exception:
        return False

# Create FastMCP server
server = FastMCP("filesystem", instructions="File system operations for Personal AI Employee")

@server.tool()
def list_files(directory: str = "") -> Dict[str, Any]:
    """
    List files and directories in a given directory (relative to vault).

    Args:
        directory: Directory path relative to vault root (empty for root)

    Returns:
        Dict with 'files' (list of file names) and 'directories' (list of dir names)
    """
    try:
        vault_path = get_vault_path()
        target_dir = vault_path / directory if directory else vault_path
        target_dir = target_dir.resolve()

        if not ensure_within_vault(target_dir):
            return {"error": f"Access outside vault not allowed: {directory}"}

        if not target_dir.exists():
            return {"error": f"Directory does not exist: {directory}"}
        if not target_dir.is_dir():
            return {"error": f"Not a directory: {directory}"}

        items = []
        for item in target_dir.iterdir():
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0,
                "modified": item.stat().st_mtime
            })

        return {
            "path": str(target_dir.relative_to(vault_path)),
            "items": items,
            "count": len(items)
        }
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return {"error": str(e)}

@server.tool()
def read_file(file_path: str) -> Dict[str, Any]:
    """
    Read contents of a file (relative to vault).

    Args:
        file_path: File path relative to vault root

    Returns:
        Dict with 'content' (string) and metadata
    """
    try:
        vault_path = get_vault_path()
        target_file = vault_path / file_path
        target_file = target_file.resolve()

        if not ensure_within_vault(target_file):
            return {"error": f"Access outside vault not allowed: {file_path}"}

        if not target_file.exists():
            return {"error": f"File does not exist: {file_path}"}
        if not target_file.is_file():
            return {"error": f"Not a file: {file_path}"}

        # Limit file size for safety
        max_size = 10 * 1024 * 1024  # 10 MB
        file_size = target_file.stat().st_size
        if file_size > max_size:
            return {"error": f"File too large ({file_size} bytes > {max_size} bytes limit)"}

        content = target_file.read_text(encoding='utf-8', errors='ignore')

        return {
            "path": str(target_file.relative_to(vault_path)),
            "content": content,
            "size": file_size,
            "modified": target_file.stat().st_mtime
        }
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return {"error": str(e)}

@server.tool()
def write_file(file_path: str, content: str, append: bool = False) -> Dict[str, Any]:
    """
    Write content to a file (relative to vault).

    Args:
        file_path: File path relative to vault root
        content: Content to write
        append: If True, append to existing file; otherwise overwrite

    Returns:
        Dict with success status
    """
    try:
        vault_path = get_vault_path()
        target_file = vault_path / file_path
        target_file = target_file.resolve()

        if not ensure_within_vault(target_file):
            return {"error": f"Access outside vault not allowed: {file_path}"}

        # Ensure parent directory exists
        target_file.parent.mkdir(parents=True, exist_ok=True)

        mode = 'a' if append else 'w'
        with open(target_file, mode, encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Written to file: {file_path}")
        return {
            "success": True,
            "path": str(target_file.relative_to(vault_path)),
            "size": target_file.stat().st_size,
            "modified": target_file.stat().st_mtime
        }
    except Exception as e:
        logger.error(f"Error writing file: {e}")
        return {"error": str(e)}

@server.tool()
def delete_file(file_path: str) -> Dict[str, Any]:
    """
    Delete a file (relative to vault).

    Args:
        file_path: File path relative to vault root

    Returns:
        Dict with success status
    """
    try:
        vault_path = get_vault_path()
        target_file = vault_path / file_path
        target_file = target_file.resolve()

        if not ensure_within_vault(target_file):
            return {"error": f"Access outside vault not allowed: {file_path}"}

        if not target_file.exists():
            return {"error": f"File does not exist: {file_path}"}
        if not target_file.is_file():
            return {"error": f"Not a file: {file_path}"}

        # Extra safety: don't delete important directories
        protected_dirs = ["Needs_Action", "Plans", "Done", "Pending_Approval", "Approved", "Logs", "Briefings"]
        for protected in protected_dirs:
            if protected in str(target_file.relative_to(vault_path)):
                return {"error": f"Cannot delete protected directory file: {protected}"}

        target_file.unlink()
        logger.info(f"Deleted file: {file_path}")
        return {"success": True, "path": str(target_file.relative_to(vault_path))}
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return {"error": str(e)}

@server.tool()
def create_directory(directory_path: str) -> Dict[str, Any]:
    """
    Create a directory (relative to vault).

    Args:
        directory_path: Directory path relative to vault root

    Returns:
        Dict with success status
    """
    try:
        vault_path = get_vault_path()
        target_dir = vault_path / directory_path
        target_dir = target_dir.resolve()

        if not ensure_within_vault(target_dir):
            return {"error": f"Access outside vault not allowed: {directory_path}"}

        target_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory_path}")
        return {"success": True, "path": str(target_dir.relative_to(vault_path))}
    except Exception as e:
        logger.error(f"Error creating directory: {e}")
        return {"error": str(e)}

@server.tool()
def file_exists(file_path: str) -> Dict[str, Any]:
    """
    Check if a file exists (relative to vault).

    Args:
        file_path: File path relative to vault root

    Returns:
        Dict with exists boolean and metadata
    """
    try:
        vault_path = get_vault_path()
        target_file = vault_path / file_path
        target_file = target_file.resolve()

        if not ensure_within_vault(target_file):
            return {"error": f"Access outside vault not allowed: {file_path}"}

        exists = target_file.exists() and target_file.is_file()
        result = {"exists": exists, "path": str(target_file.relative_to(vault_path))}
        if exists:
            result["size"] = target_file.stat().st_size
            result["modified"] = target_file.stat().st_mtime
        return result
    except Exception as e:
        logger.error(f"Error checking file existence: {e}")
        return {"error": str(e)}

@server.tool()
def move_file(source_path: str, dest_path: str) -> Dict[str, Any]:
    """
    Move/rename a file within vault.

    Args:
        source_path: Source file path relative to vault root
        dest_path: Destination file path relative to vault root

    Returns:
        Dict with success status
    """
    try:
        vault_path = get_vault_path()
        source_file = vault_path / source_path
        dest_file = vault_path / dest_path
        source_file = source_file.resolve()
        dest_file = dest_file.resolve()

        if not ensure_within_vault(source_file) or not ensure_within_vault(dest_file):
            return {"error": "Access outside vault not allowed"}

        if not source_file.exists():
            return {"error": f"Source file does not exist: {source_path}"}
        if not source_file.is_file():
            return {"error": f"Source is not a file: {source_path}"}

        # Ensure parent directory exists
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        source_file.rename(dest_file)
        logger.info(f"Moved file from {source_path} to {dest_path}")
        return {
            "success": True,
            "source": str(source_file.relative_to(vault_path)),
            "destination": str(dest_file.relative_to(vault_path))
        }
    except Exception as e:
        logger.error(f"Error moving file: {e}")
        return {"error": str(e)}

@server.tool()
def get_vault_status() -> Dict[str, Any]:
    """
    Get status of vault directories (counts of items in each folder).

    Returns:
        Dict with counts for each vault folder
    """
    try:
        vault_path = get_vault_path()
        folders = ["Needs_Action", "Plans", "Done", "Pending_Approval", "Approved", "Logs", "Briefings"]
        status = {}

        for folder in folders:
            folder_path = vault_path / folder
            if folder_path.exists() and folder_path.is_dir():
                items = list(folder_path.iterdir())
                status[folder] = len([item for item in items if item.is_file()])
            else:
                status[folder] = 0

        # Total files in vault root (excluding directories)
        root_files = [item for item in vault_path.iterdir() if item.is_file()]
        status["root"] = len(root_files)
        status["vault_path"] = str(vault_path)

        return status
    except Exception as e:
        logger.error(f"Error getting vault status: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Run the server over stdio (default for MCP)
    logger.info("Starting Filesystem MCP Server...")
    server.run()