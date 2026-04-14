#!/usr/bin/env python3
"""
LinkedIn MCP Server for Personal AI Employee (Silver Tier)

Provides tools for posting to LinkedIn to generate business leads.

Configuration:
- Set LINKEDIN_ACCESS_TOKEN environment variable
- Set VAULT_PATH environment variable to vault directory

Run:
    python mcp/linkedin/server.py

LinkedIn API Setup:
1. Go to https://www.linkedin.com/developers/apps
2. Create a new app
3. Get your Access Token
4. Set LINKEDIN_ACCESS_TOKEN environment variable
"""

import os
import sys
import logging
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("linkedin-mcp")

# Create FastMCP server
server = FastMCP(
    "linkedin",
    instructions="LinkedIn integration for posting business updates and generating leads"
)

# LinkedIn API endpoints
LINKEDIN_API_BASE = "https://api.linkedin.com/v2"


def get_access_token() -> Optional[str]:
    """Get LinkedIn access token from environment."""
    token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    if not token:
        # Try loading from vault secrets
        vault_path = os.getenv('VAULT_PATH', './vault')
        token_file = Path(vault_path) / 'secrets' / 'linkedin_token.txt'
        if token_file.exists():
            token = token_file.read_text().strip()

    return token


def is_dry_run() -> bool:
    """Check if dry_run mode is enabled."""
    return os.getenv('DRY_RUN', 'true').lower() == 'true'


def get_person_urn(token: str) -> Optional[str]:
    """Get the person URN for the authenticated user."""
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        response = requests.get(
            f"{LINKEDIN_API_BASE}/me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('id')
        else:
            logger.error(f"Failed to get person URN: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting person URN: {e}")
        return None


@server.tool()
def linkedin_status() -> Dict[str, Any]:
    """
    Get LinkedIn integration status and connection info.

    Returns:
        Dict with status information including connection state
    """
    token = get_access_token()
    person_urn = None
    connected = False
    
    if token:
        person_urn = get_person_urn(token)
        connected = person_urn is not None
    
    return {
        "status": "active" if connected else "needs_authentication",
        "connected": connected,
        "person_urn": person_urn,
        "tier": "silver",
        "implemented": True,
        "capabilities": [
            "post_text",
            "post_with_image",
            "get_profile"
        ]
    }


@server.tool()
def post_to_linkedin(
    content: str,
    visibility: str = "PUBLIC"
) -> Dict[str, Any]:
    """
    Post a text update to LinkedIn.

    Args:
        content: The text content to post (max 3000 characters)
        visibility: Post visibility - PUBLIC, CONNECTIONS, or ANYONE (default: PUBLIC)

    Returns:
        Dict with post result including post ID and URL
    """
    token = get_access_token()

    if not token:
        # In dry_run mode, still allow for testing
        if is_dry_run():
            logger.info(f"[DRY RUN] Would post to LinkedIn (no token configured): {content[:100]}...")
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would post to LinkedIn ({len(content)} chars) — no token configured",
                "content_preview": content[:200],
                "visibility": visibility,
                "note": "Set LINKEDIN_ACCESS_TOKEN and DRY_RUN=false to actually post"
            }
        return {
            "success": False,
            "error": "LINKEDIN_ACCESS_TOKEN not set",
            "message": "Please set LINKEDIN_ACCESS_TOKEN environment variable or create vault/secrets/linkedin_token.txt"
        }

    # Check dry_run mode (token exists but still dry_run)
    if is_dry_run():
        logger.info(f"[DRY RUN] Would post to LinkedIn: {content[:100]}...")
        return {
            "success": True,
            "dry_run": True,
            "message": f"Would post to LinkedIn ({len(content)} chars)",
            "content_preview": content[:200],
            "visibility": visibility,
            "note": "Set DRY_RUN=false to actually post"
        }

    person_urn = get_person_urn(token)

    if not person_urn:
        return {
            "success": False,
            "error": "Authentication failed",
            "message": "Could not authenticate with LinkedIn. Check your access token."
        }
    
    # Truncate content if too long
    if len(content) > 3000:
        content = content[:2997] + "..."
        logger.warning("Content truncated to 3000 characters")
    
    try:
        # LinkedIn Share API payload
        payload = {
            "author": f"urn:li:person:{person_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{LINKEDIN_API_BASE}/ugcPosts",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 201:
            # Extract post ID from response
            post_id = response.json().get('id', 'unknown')
            
            # Log to vault
            _log_post_to_vault(content, post_id, visibility)
            
            return {
                "success": True,
                "post_id": post_id,
                "post_url": f"https://www.linkedin.com/feed/update/{post_id}",
                "visibility": visibility,
                "content_length": len(content),
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"LinkedIn API error: {response.status_code} - {response.text}")
            return {
                "success": False,
                "error": f"LinkedIn API error: {response.status_code}",
                "message": response.text[:200] if response.text else "Unknown error"
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return {
            "success": False,
            "error": "Network error",
            "message": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": "Unexpected error",
            "message": str(e)
        }


@server.tool()
def post_business_update(
    topic: str,
    key_points: List[str],
    call_to_action: str = ""
) -> Dict[str, Any]:
    """
    Create and post a structured business update to LinkedIn.

    This formats a professional business update with:
    - Attention-grabbing headline
    - Key points as bullet list
    - Optional call-to-action
    - Relevant hashtags

    Args:
        topic: Main topic/title of the update
        key_points: List of key points to highlight
        call_to_action: Optional call-to-action text

    Returns:
        Dict with post result
    """
    # Format the post
    content = f"🚀 {topic}\n\n"

    for point in key_points:
        content += f"• {point}\n"

    if call_to_action:
        content += f"\n{call_to_action}\n"

    # Add hashtags
    content += "\n#Business #Innovation #AI #Automation"

    return post_to_linkedin(content)


@server.tool()
def post_with_image(
    content: str,
    image_url: str,
    visibility: str = "PUBLIC"
) -> Dict[str, Any]:
    """
    Post a text update with an image to LinkedIn.

    Args:
        content: The text content (max 3000 characters)
        image_url: URL of the image to attach
        visibility: Post visibility (default: PUBLIC)

    Returns:
        Dict with post result
    """
    token = get_access_token()

    if not token:
        if is_dry_run():
            logger.info(f"[DRY RUN] Would post to LinkedIn with image (no token): {content[:100]}...")
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would post to LinkedIn with image ({len(content)} chars) — no token",
                "content_preview": content[:200],
                "image_url": image_url,
                "visibility": visibility,
                "note": "Set LINKEDIN_ACCESS_TOKEN and DRY_RUN=false to actually post"
            }
        return {
            "success": False,
            "error": "LINKEDIN_ACCESS_TOKEN not set"
        }

    if is_dry_run():
        logger.info(f"[DRY RUN] Would post to LinkedIn with image: {content[:100]}...")
        return {
            "success": True,
            "dry_run": True,
            "message": f"Would post to LinkedIn with image ({len(content)} chars)",
            "content_preview": content[:200],
            "image_url": image_url,
            "visibility": visibility,
            "note": "Set DRY_RUN=false to actually post"
        }

    person_urn = get_person_urn(token)
    if not person_urn:
        return {
            "success": False,
            "error": "Authentication failed",
            "message": "Could not authenticate with LinkedIn."
        }

    if len(content) > 3000:
        content = content[:2997] + "..."

    try:
        # Step 1: Register upload (request upload URL)
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json'
        }

        register_payload = {
            "registerUploadRequest": {
                "owner": f"urn:li:person:{person_urn}",
                "recipes": ["urn:li:digitalmediaRecipe:feedimage"],
                "serviceRelationships": [{
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }]
            }
        }

        register_resp = requests.post(
            f"{LINKEDIN_API_BASE}/assets?action=registerUpload",
            headers=headers,
            json=register_payload,
            timeout=30
        )

        if register_resp.status_code != 200:
            return {
                "success": False,
                "error": f"Failed to register upload: {register_resp.status_code}",
                "message": register_resp.text[:200]
            }

        upload_data = register_resp.json()
        upload_url = upload_data['value']['uploadInstructions'][0]['uploadUrl']
        asset_urn = upload_data['value']['asset']

        # Step 2: Upload image (binary upload to upload_url)
        img_resp = requests.put(
            upload_url,
            headers={'Authorization': f'Bearer {token}'},
            data=requests.get(image_url, timeout=30).content,
            timeout=60
        )

        if img_resp.status_code not in (200, 201):
            return {
                "success": False,
                "error": f"Failed to upload image: {img_resp.status_code}"
            }

        # Step 3: Create share with image
        payload = {
            "author": f"urn:li:person:{person_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content},
                    "shareMediaCategory": "IMAGE",
                    "media": [{
                        "status": "READY",
                        "description": {"text": content[:100]},
                        "media": asset_urn,
                        "title": {"text": "Business Update"}
                    }]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }

        response = requests.post(
            f"{LINKEDIN_API_BASE}/ugcPosts",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 201:
            post_id = response.json().get('id', 'unknown')
            _log_post_to_vault(content, post_id, visibility)
            return {
                "success": True,
                "post_id": post_id,
                "post_url": f"https://www.linkedin.com/feed/update/{post_id}",
                "visibility": visibility,
                "content_length": len(content),
                "image_asset": asset_urn,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": f"LinkedIn API error: {response.status_code}",
                "message": response.text[:200]
            }

    except Exception as e:
        logger.error(f"Error posting with image: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@server.tool()
def get_linkedin_profile() -> Dict[str, Any]:
    """
    Get basic profile information from LinkedIn.

    Returns:
        Dict with profile information
    """
    token = get_access_token()
    
    if not token:
        return {
            "success": False,
            "error": "LINKEDIN_ACCESS_TOKEN not set"
        }
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        response = requests.get(
            f"{LINKEDIN_API_BASE}/me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "profile": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"API error: {response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _log_post_to_vault(content: str, post_id: str, visibility: str):
    """Log the post to the vault for record keeping."""
    try:
        vault_path = os.getenv('VAULT_PATH', './vault')
        logs_dir = Path(vault_path) / 'Logs'
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Append to daily log
        log_file = logs_dir / f"linkedin_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "post_id": post_id,
            "content": content,
            "visibility": visibility,
            "status": "posted"
        }
        
        # Read existing logs or create new
        if log_file.exists():
            import json
            logs = json.loads(log_file.read_text())
            if not isinstance(logs, list):
                logs = [logs]
            logs.append(log_entry)
        else:
            logs = [log_entry]
        
        import json
        log_file.write_text(json.dumps(logs, indent=2))
        
        logger.info(f"Logged LinkedIn post to {log_file}")
        
    except Exception as e:
        logger.warning(f"Failed to log post to vault: {e}")


if __name__ == "__main__":
    # Run the server over stdio (default for MCP)
    logger.info("Starting LinkedIn MCP Server...")
    logger.info(f"Token configured: {'Yes' if get_access_token() else 'No'}")
    server.run()
