#!/usr/bin/env python3
"""
Approval Workflow MCP Server for Personal AI Employee

Provides tools for managing approval workflow: list pending approvals, approve/reject items, move files between vault folders.

Configuration:
- Set VAULT_PATH environment variable to vault directory

Run:
    python mcp/approval/server.py
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("approval-mcp")

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

def move_file_safe(source: Path, dest: Path) -> bool:
    """
    Safely move a file within vault, ensuring directories exist.
    Returns True on success, False on error.
    """
    try:
        if not ensure_within_vault(source) or not ensure_within_vault(dest):
            logger.error(f"Cannot move file outside vault: {source} -> {dest}")
            return False

        if not source.exists():
            logger.error(f"Source file does not exist: {source}")
            return False

        # Ensure destination directory exists
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Move the file
        source.rename(dest)
        logger.info(f"Moved file: {source.name} -> {dest.parent.name}")
        return True
    except Exception as e:
        logger.error(f"Error moving file {source} to {dest}: {e}")
        return False

# Create FastMCP server
server = FastMCP("approval", instructions="Approval workflow management for Personal AI Employee")

@server.tool()
def list_pending_approvals() -> Dict[str, Any]:
    """
    List all items in Pending_Approval folder.

    Returns:
        Dict with list of pending items and metadata
    """
    try:
        vault_path = get_vault_path()
        pending_dir = vault_path / "Pending_Approval"

        if not pending_dir.exists():
            pending_dir.mkdir(parents=True, exist_ok=True)
            return {"count": 0, "items": [], "message": "Pending_Approval directory created"}

        items = []
        for item in pending_dir.iterdir():
            if item.is_file():
                stat = item.stat()
                items.append({
                    "id": item.name,
                    "name": item.name,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "path": str(item.relative_to(vault_path))
                })

        items.sort(key=lambda x: x["modified"], reverse=True)
        return {
            "count": len(items),
            "items": items,
            "folder": "Pending_Approval"
        }
    except Exception as e:
        logger.error(f"Error listing pending approvals: {e}")
        return {"error": str(e)}

@server.tool()
def get_approval_item(item_id: str) -> Dict[str, Any]:
    """
    Get details of a specific pending approval item.

    Args:
        item_id: Filename in Pending_Approval folder

    Returns:
        Dict with item content and metadata
    """
    try:
        vault_path = get_vault_path()
        item_file = vault_path / "Pending_Approval" / item_id

        if not ensure_within_vault(item_file):
            return {"error": f"Access outside vault not allowed: {item_id}"}

        if not item_file.exists():
            return {"error": f"Item not found: {item_id}"}
        if not item_file.is_file():
            return {"error": f"Not a file: {item_id}"}

        # Read file content
        content = item_file.read_text(encoding='utf-8', errors='ignore')
        stat = item_file.stat()

        # Try to find associated plan
        plan_path = vault_path / "Plans" / item_id.replace(".md", "_PLAN.md")
        has_plan = plan_path.exists() and plan_path.is_file()

        result = {
            "id": item_id,
            "content": content,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "has_plan": has_plan,
            "path": str(item_file.relative_to(vault_path))
        }

        if has_plan:
            plan_content = plan_path.read_text(encoding='utf-8', errors='ignore')
            result["plan_content"] = plan_content
            result["plan_path"] = str(plan_path.relative_to(vault_path))

        return result
    except Exception as e:
        logger.error(f"Error getting approval item: {e}")
        return {"error": str(e)}

@server.tool()
def approve_item(item_id: str, notes: str = "") -> Dict[str, Any]:
    """
    Approve an item by moving it from Pending_Approval to Approved folder.

    Args:
        item_id: Filename in Pending_Approval folder
        notes: Optional approval notes

    Returns:
        Dict with success status and details
    """
    try:
        vault_path = get_vault_path()
        source = vault_path / "Pending_Approval" / item_id
        dest = vault_path / "Approved" / item_id

        if not source.exists():
            return {"error": f"Item not found in Pending_Approval: {item_id}"}

        # Move the file
        success = move_file_safe(source, dest)
        if not success:
            return {"error": f"Failed to move item {item_id} to Approved"}

        # Create approval log entry
        log_dir = vault_path / "Logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"APPROVAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        log_content = f"""# Approval Log

## Item Approved
- **Item**: {item_id}
- **Approved**: {datetime.now().isoformat()}
- **From**: Pending_Approval
- **To**: Approved
- **Notes**: {notes if notes else "No notes provided"}

## Item Content Preview
{source.read_text(encoding='utf-8', errors='ignore')[:500]}...
"""
        log_file.write_text(log_content)

        logger.info(f"Approved item: {item_id}")
        return {
            "success": True,
            "item_id": item_id,
            "action": "approved",
            "timestamp": datetime.now().isoformat(),
            "notes": notes,
            "log_file": str(log_file.relative_to(vault_path))
        }
    except Exception as e:
        logger.error(f"Error approving item: {e}")
        return {"error": str(e)}

@server.tool()
def reject_item(item_id: str, reason: str = "") -> Dict[str, Any]:
    """
    Reject an item by moving it from Pending_Approval to Done folder.

    Args:
        item_id: Filename in Pending_Approval folder
        reason: Optional rejection reason

    Returns:
        Dict with success status and details
    """
    try:
        vault_path = get_vault_path()
        source = vault_path / "Pending_Approval" / item_id
        dest = vault_path / "Done" / item_id

        if not source.exists():
            return {"error": f"Item not found in Pending_Approval: {item_id}"}

        # Move the file
        success = move_file_safe(source, dest)
        if not success:
            return {"error": f"Failed to move item {item_id} to Done"}

        # Create rejection log entry
        log_dir = vault_path / "Logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"REJECTION_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        log_content = f"""# Rejection Log

## Item Rejected
- **Item**: {item_id}
- **Rejected**: {datetime.now().isoformat()}
- **From**: Pending_Approval
- **To**: Done
- **Reason**: {reason if reason else "No reason provided"}

## Item Content Preview
{source.read_text(encoding='utf-8', errors='ignore')[:500]}...
"""
        log_file.write_text(log_content)

        logger.info(f"Rejected item: {item_id}")
        return {
            "success": True,
            "item_id": item_id,
            "action": "rejected",
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "log_file": str(log_file.relative_to(vault_path))
        }
    except Exception as e:
        logger.error(f"Error rejecting item: {e}")
        return {"error": str(e)}

@server.tool()
def request_more_info(item_id: str, info_request: str) -> Dict[str, Any]:
    """
    Request more information for an item by moving it back to Needs_Action with a note.

    Args:
        item_id: Filename in Pending_Approval folder
        info_request: Information needed from the user

    Returns:
        Dict with success status and details
    """
    try:
        vault_path = get_vault_path()
        source = vault_path / "Pending_Approval" / item_id
        dest = vault_path / "Needs_Action" / item_id

        if not source.exists():
            return {"error": f"Item not found in Pending_Approval: {item_id}"}

        # Read current content
        content = source.read_text(encoding='utf-8', errors='ignore')

        # Add info request note
        updated_content = f"""{content}

---
## INFORMATION REQUESTED
**Requested**: {datetime.now().isoformat()}
**Information Needed**: {info_request}

Please provide the requested information and move this item back to Pending_Approval when ready.
"""

        # Write updated content to destination
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(updated_content)

        # Delete original (or move it to Done as backup?)
        source.unlink()

        # Create info request log
        log_dir = vault_path / "Logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"INFO_REQUEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        log_content = f"""# Information Request Log

## Item Needs More Information
- **Item**: {item_id}
- **Requested**: {datetime.now().isoformat()}
- **From**: Pending_Approval
- **To**: Needs_Action
- **Information Needed**: {info_request}

## Original Item Preview
{content[:500]}...
"""
        log_file.write_text(log_content)

        logger.info(f"Requested more info for item: {item_id}")
        return {
            "success": True,
            "item_id": item_id,
            "action": "info_requested",
            "timestamp": datetime.now().isoformat(),
            "info_request": info_request,
            "log_file": str(log_file.relative_to(vault_path))
        }
    except Exception as e:
        logger.error(f"Error requesting more info: {e}")
        return {"error": str(e)}

@server.tool()
def get_approval_stats() -> Dict[str, Any]:
    """
    Get statistics about approval workflow.

    Returns:
        Dict with counts for each folder and recent activity
    """
    try:
        vault_path = get_vault_path()
        folders = ["Needs_Action", "Pending_Approval", "Approved", "Done", "Logs"]
        stats = {}

        for folder in folders:
            folder_path = vault_path / folder
            if folder_path.exists() and folder_path.is_dir():
                items = [item for item in folder_path.iterdir() if item.is_file()]
                stats[folder] = len(items)
            else:
                stats[folder] = 0

        # Get recent approval/rejection logs
        logs_dir = vault_path / "Logs"
        recent_logs = []
        if logs_dir.exists() and logs_dir.is_dir():
            log_files = sorted(logs_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
            for log_file in log_files[:5]:  # Last 5 logs
                if log_file.is_file():
                    recent_logs.append({
                        "name": log_file.name,
                        "modified": log_file.stat().st_mtime,
                        "size": log_file.stat().st_size
                    })

        stats["recent_logs"] = recent_logs
        stats["timestamp"] = datetime.now().isoformat()
        stats["vault_path"] = str(vault_path)

        return stats
    except Exception as e:
        logger.error(f"Error getting approval stats: {e}")
        return {"error": str(e)}

@server.tool()
def move_to_pending_approval(item_id: str, source_folder: str = "Needs_Action") -> Dict[str, Any]:
    """
    Move an item from source folder to Pending_Approval (for testing or manual workflow).

    Args:
        item_id: Filename in source folder
        source_folder: Source folder (default: Needs_Action)

    Returns:
        Dict with success status
    """
    try:
        vault_path = get_vault_path()
        source = vault_path / source_folder / item_id
        dest = vault_path / "Pending_Approval" / item_id

        if not source.exists():
            return {"error": f"Item not found in {source_folder}: {item_id}"}

        success = move_file_safe(source, dest)
        if not success:
            return {"error": f"Failed to move item {item_id} to Pending_Approval"}

        logger.info(f"Moved item to Pending_Approval: {item_id}")
        return {
            "success": True,
            "item_id": item_id,
            "from": source_folder,
            "to": "Pending_Approval",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error moving to pending approval: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Run the server over stdio (default for MCP)
    logger.info("Starting Approval Workflow MCP Server...")
    server.run()