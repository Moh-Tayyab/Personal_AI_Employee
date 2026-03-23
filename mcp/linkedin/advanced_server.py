"""
Advanced LinkedIn MCP Server - Enterprise-grade LinkedIn automation with smart security handling

This server provides advanced LinkedIn automation capabilities
with enhanced stealth, intelligent security challenge handling, and reliability.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List
import tempfile

# Import the advanced LinkedIn browser
from .professional_browser import ProfessionalLinkedInBrowser


def linkedin_login_tool(email: str, password: str, handle_verification: bool = True) -> Dict[str, Any]:
    """
    MCP Tool: Login to LinkedIn account with smart security handling

    Args:
        email: LinkedIn account email
        password: LinkedIn account password
        handle_verification: Whether to attempt handling verification challenges

    Returns:
        Dict with login result
    """
    session_path = os.getenv("LINKEDIN_SESSION_PATH", "./vault/secrets/linkedin_session")
    browser = ProfessionalLinkedInBrowser(session_path)

    try:
        result = browser.login(email, password)

        # If verification is needed, handle it appropriately
        if result.get('error') and ('verification' in result.get('error', '').lower() or
                                   'checkpoint' in result.get('error', '').lower() or
                                   'challenge' in result.get('error', '').lower()):

            if handle_verification:
                print("⚠️ Security challenge detected. Manual verification may be required.")
                print("ℹ️  This is a security measure by LinkedIn to prevent automated access.")
                result['needs_manual_verification'] = True
                result['verification_url'] = result.get('error', '').split('at: ')[-1] if 'at:' in result.get('error', '') else None
                result['recommendation'] = "Please manually log in to LinkedIn to verify your account, then try again."
            else:
                print("⚠️ Security challenge detected but verification handling disabled.")

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
    MCP Tool: Create a LinkedIn post with advanced reliability

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


def linkedin_bypass_security_tool(method: str = "manual") -> Dict[str, Any]:
    """
    MCP Tool: Attempt to bypass security challenges (advisory only)

    Args:
        method: How to bypass ('manual', 'delay', 'rotate_ip')

    Returns:
        Dict with guidance for bypassing security
    """
    if method == "manual":
        return {
            "status": "advisory",
            "action": "manual_verification",
            "message": "Manually log in to LinkedIn to verify your account identity.",
            "steps": [
                "1. Open LinkedIn in a regular browser",
                "2. Log in with your credentials",
                "3. Complete any required verification steps",
                "4. Wait 24 hours before attempting automated access again"
            ],
            "reason": "LinkedIn implements rate limiting and anti-bot measures that require manual verification"
        }
    elif method == "delay":
        return {
            "status": "advisory",
            "action": "implement_delay",
            "message": "Add delays between LinkedIn operations to appear more human-like.",
            "recommendation": "Wait 1-2 minutes between operations, vary timing randomly"
        }
    elif method == "rotate_ip":
        return {
            "status": "advisory",
            "action": "ip_rotation",
            "message": "Consider rotating your IP address to appear as different users.",
            "options": [
                "Use residential proxy services",
                "Use VPN services that rotate IPs",
                "Access LinkedIn from different physical locations"
            ]
        }
    else:
        return {
            "status": "error",
            "message": f"Unknown bypass method: {method}"
        }


def linkedin_delay_operation_tool(seconds: int = 30) -> Dict[str, Any]:
    """
    MCP Tool: Introduce delay to appear more human-like

    Args:
        seconds: Number of seconds to wait

    Returns:
        Dict with delay confirmation
    """
    print(f"Delaying for {seconds} seconds to appear more human-like...")
    time.sleep(seconds)
    return {
        "status": "delay_complete",
        "seconds": seconds,
        "message": f"Delayed for {seconds} seconds"
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
        "linkedin_bypass_security": linkedin_bypass_security_tool,
        "linkedin_delay_operation": linkedin_delay_operation_tool,
    }

    if tool_name not in tools:
        return {
            "status": "error",
            "error": f"Tool '{tool_name}' not found"
        }

    tool_func = tools[tool_name]

    try:
        # Call the tool with the provided arguments
        if tool_name == "linkedin_login":
            return tool_func(
                arguments.get("email"),
                arguments.get("password"),
                arguments.get("handle_verification", True)
            )
        elif tool_name == "linkedin_create_post":
            return tool_func(
                arguments.get("content", ""),
                arguments.get("headline", ""),
                arguments.get("media_path")
            )
        elif tool_name == "linkedin_bypass_security":
            return tool_func(arguments.get("method", "manual"))
        elif tool_name == "linkedin_delay_operation":
            return tool_func(arguments.get("seconds", 30))
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
            "description": "Login to LinkedIn account with smart security handling",
            "arguments": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "LinkedIn account email"},
                    "password": {"type": "string", "description": "LinkedIn account password"},
                    "handle_verification": {
                        "type": "boolean",
                        "description": "Whether to attempt handling verification challenges",
                        "default": True
                    }
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
            "name": "linkedin_bypass_security",
            "description": "Get advice on bypassing LinkedIn security measures (advisory only)",
            "arguments": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["manual", "delay", "rotate_ip"],
                        "description": "Method to suggest for bypassing security",
                        "default": "manual"
                    }
                },
                "required": []
            }
        },
        {
            "name": "linkedin_delay_operation",
            "description": "Introduce delay to appear more human-like",
            "arguments": {
                "type": "object",
                "properties": {
                    "seconds": {
                        "type": "integer",
                        "description": "Number of seconds to wait",
                        "default": 30,
                        "minimum": 1,
                        "maximum": 300
                    }
                },
                "required": []
            }
        }
    ]


# Example usage when running as a standalone script
if __name__ == "__main__":
    # This would be called by the MCP server
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Advanced LinkedIn MCP Server')
    parser.add_argument('--tool', required=True, help='Tool name to execute')
    parser.add_argument('--args', help='JSON string of arguments')

    args = parser.parse_args()

    arguments = json.loads(args.args) if args.args else {}
    result = execute_tool(args.tool, arguments)

    print(json.dumps(result, indent=2))