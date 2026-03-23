"""
Professional LinkedIn MCP Server - Advanced LinkedIn automation with MCP protocol

This server provides professional-grade LinkedIn automation capabilities
with enhanced stealth, error handling, and reliability.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List

# Import the professional LinkedIn browser
from .professional_browser import ProfessionalLinkedInBrowser

def linkedin_login_tool(email: str, password: str) -> Dict[str, Any]:
    """
    MCP Tool: Login to LinkedIn account

    Args:
        email: LinkedIn account email
        password: LinkedIn account password

    Returns:
        Dict with login result
    """
    session_path = os.getenv("LINKEDIN_SESSION_PATH", "./vault/secrets/linkedin_session")
    browser = ProfessionalLinkedInBrowser(session_path)

    try:
        result = browser.login(email, password)
        return result
    finally:
        browser.close()


def linkedin_check_session_tool() -> Dict[str, Any]:
    """
    MCP Tool: Check if LinkedIn session is valid

    Returns:
        Dict with session status
    """
    session_path = os.getenv("LINKEDIN_SESSION_PATH", "./vault/secrets/linkedin_session")
    browser = ProfessionalLinkedInBrowser(session_path)

    try:
        result = browser.check_session()
        return result
    finally:
        browser.close()


def linkedin_create_post_tool(content: str, headline: str = "", media_path: str = None) -> Dict[str, Any]:
    """
    MCP Tool: Create a LinkedIn post

    Args:
        content: Post content
        headline: Post headline (optional)
        media_path: Path to media file to attach (optional)

    Returns:
        Dict with post result
    """
    session_path = os.getenv("LINKEDIN_SESSION_PATH", "./vault/secrets/linkedin_session")
    browser = ProfessionalLinkedInBrowser(session_path)

    try:
        result = browser.create_post(content, headline, media_path)
        return result
    finally:
        browser.close()


def linkedin_get_profile_info_tool() -> Dict[str, Any]:
    """
    MCP Tool: Get current LinkedIn profile information

    Returns:
        Dict with profile info
    """
    session_path = os.getenv("LINKEDIN_SESSION_PATH", "./vault/secrets/linkedin_session")
    browser = ProfessionalLinkedInBrowser(session_path)

    try:
        result = browser.get_current_profile_info()
        return result
    finally:
        browser.close()


def linkedin_logout_tool() -> Dict[str, Any]:
    """
    MCP Tool: Logout from LinkedIn (clear session)

    Returns:
        Dict with logout result
    """
    session_path = Path(os.getenv("LINKEDIN_SESSION_PATH", "./vault/secrets/linkedin_session"))

    try:
        # Remove session storage files
        storage_file = session_path / "storage.json"
        if storage_file.exists():
            storage_file.unlink()

        # Remove any cookies files
        for file in session_path.glob("cookies-*.json"):
            file.unlink()

        return {
            "status": "logged_out",
            "message": "LinkedIn session cleared"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error clearing session: {str(e)}"
        }


def linkedin_post_status_tool(post_id: str) -> Dict[str, Any]:
    """
    MCP Tool: Check status of a LinkedIn post (not implemented yet)

    Args:
        post_id: ID of the post to check

    Returns:
        Dict with post status
    """
    # Note: This is a limitation as LinkedIn doesn't provide a direct API to check post status
    # We could implement this by navigating to the user's profile/posts and searching
    return {
        "status": "not_implemented",
        "message": "Post status checking not implemented yet"
    }


# Standard MCP server interface
def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute LinkedIn MCP tool

    Args:
        tool_name: Name of the tool to execute
        arguments: Arguments for the tool

    Returns:
        Result of the tool execution
    """
    tools = {
        "linkedin_login": linkedin_login_tool,
        "linkedin_check_session": linkedin_check_session_tool,
        "linkedin_create_post": linkedin_create_post_tool,
        "linkedin_get_profile_info": linkedin_get_profile_info_tool,
        "linkedin_logout": linkedin_logout_tool,
        "linkedin_post_status": linkedin_post_status_tool,
    }

    if tool_name not in tools:
        return {
            "status": "error",
            "error": f"Tool '{tool_name}' not found"
        }

    tool_func = tools[tool_name]

    try:
        # Call the tool with the provided arguments
        # Handle different argument patterns for each tool
        if tool_name == "linkedin_login":
            return tool_func(arguments.get("email"), arguments.get("password"))
        elif tool_name == "linkedin_create_post":
            return tool_func(
                arguments.get("content", ""),
                arguments.get("headline", ""),
                arguments.get("media_path")
            )
        elif tool_name == "linkedin_post_status":
            return tool_func(arguments.get("post_id"))
        else:
            # For other tools that don't require specific arguments
            return tool_func()
    except Exception as e:
        return {
            "status": "error",
            "error": f"Tool execution failed: {str(e)}"
        }


def get_available_tools() -> List[Dict[str, Any]]:
    """
    Get list of available LinkedIn MCP tools

    Returns:
        List of tool definitions
    """
    return [
        {
            "name": "linkedin_login",
            "description": "Login to LinkedIn account with email and password",
            "arguments": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "LinkedIn account email"},
                    "password": {"type": "string", "description": "LinkedIn account password"}
                },
                "required": ["email", "password"]
            }
        },
        {
            "name": "linkedin_check_session",
            "description": "Check if LinkedIn session is valid",
            "arguments": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "linkedin_create_post",
            "description": "Create a LinkedIn post with content and optional media",
            "arguments": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Post content"},
                    "headline": {"type": "string", "description": "Post headline (optional)"},
                    "media_path": {"type": "string", "description": "Path to media file to attach (optional)"}
                },
                "required": ["content"]
            }
        },
        {
            "name": "linkedin_get_profile_info",
            "description": "Get current LinkedIn profile information",
            "arguments": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "linkedin_logout",
            "description": "Logout from LinkedIn (clear session)",
            "arguments": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "linkedin_post_status",
            "description": "Check status of a LinkedIn post (not implemented)",
            "arguments": {
                "type": "object",
                "properties": {
                    "post_id": {"type": "string", "description": "ID of the post to check"}
                },
                "required": ["post_id"]
            }
        }
    ]


# Example usage when running as a standalone script
if __name__ == "__main__":
    # This would be called by the MCP server
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Professional LinkedIn MCP Server')
    parser.add_argument('--tool', required=True, help='Tool name to execute')
    parser.add_argument('--args', help='JSON string of arguments')

    args = parser.parse_args()

    arguments = json.loads(args.args) if args.args else {}
    result = execute_tool(args.tool, arguments)

    print(json.dumps(result, indent=2))