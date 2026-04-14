#!/usr/bin/env python3
"""
Facebook/Instagram MCP Server for Personal AI Employee (Gold Tier)

Provides Facebook and Instagram integration for posting content and generating summaries.
Uses Meta Graph API.

Configuration:
- META_ACCESS_TOKEN: Meta/Facebook Page Access Token
- META_APP_ID: Facebook App ID
- META_APP_SECRET: Facebook App Secret
- INSTAGRAM_ACCOUNT_ID: Instagram Business Account ID
- VAULT_PATH: Path to vault for logging

Run:
    python mcp/social/server.py

Meta API Setup:
1. Go to https://developers.facebook.com/
2. Create a Facebook App
3. Add Facebook Login and Instagram Graph API products
4. Get Page Access Token with required permissions
5. Set environment variables
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("social-mcp")

# Create FastMCP server
server = FastMCP(
    "social",
    instructions="Facebook/Instagram integration for Personal AI Employee (Gold Tier)"
)

# Meta Graph API endpoints
META_GRAPH_API = "https://graph.facebook.com/v18.0"


def get_credentials() -> Dict[str, str]:
    """Get Meta credentials from environment or vault."""
    creds = {
        'access_token': os.getenv('META_ACCESS_TOKEN'),
        'app_id': os.getenv('META_APP_ID'),
        'app_secret': os.getenv('META_APP_SECRET'),
        'instagram_account_id': os.getenv('INSTAGRAM_ACCOUNT_ID')
    }

    # Check vault secrets if not in environment
    if not creds['access_token']:
        vault_path = os.getenv('VAULT_PATH', './vault')
        creds_file = Path(vault_path) / 'secrets' / 'meta_credentials.json'
        if creds_file.exists():
            stored_creds = json.loads(creds_file.read_text())
            creds.update(stored_creds)

    return creds


def is_dry_run() -> bool:
    """Check if dry_run mode is enabled."""
    return os.getenv('DRY_RUN', 'true').lower() == 'true'


@server.tool()
def social_status() -> Dict[str, Any]:
    """
    Check Facebook/Instagram API connection status.
    
    Returns:
        Dict with connection status and capabilities
    """
    creds = get_credentials()
    
    status = {
        "status": "needs_configuration",
        "configured": bool(creds['access_token']),
        "tier": "gold",
        "capabilities": [
            "post_to_facebook",
            "post_to_instagram",
            "get_facebook_insights",
            "get_instagram_insights",
            "list_pages",
            "list_instagram_accounts"
        ]
    }
    
    if creds['access_token']:
        try:
            # Test connection by getting me endpoint
            response = requests.get(
                f"{META_GRAPH_API}/me",
                params={'access_token': creds['access_token']},
                timeout=10
            )
            
            if response.status_code == 200:
                user = response.json()
                status["status"] = "connected"
                status["user_id"] = user.get('id')
                status["user_name"] = user.get('name')
            else:
                status["status"] = "auth_error"
                status["error"] = f"API error: {response.status_code}"
                
        except Exception as e:
            status["status"] = "connection_error"
            status["error"] = str(e)
    
    return status


@server.tool()
def post_to_facebook(
    content: str,
    page_id: str = None,
    link: str = None,
    photo_url: str = None
) -> Dict[str, Any]:
    """
    Post content to Facebook Page.

    Args:
        content: Post text content
        page_id: Facebook Page ID (default: user's default page)
        link: URL to share (optional)
        photo_url: URL of photo to post (optional)

    Returns:
        Dict with post details including ID and URL
    """
    creds = get_credentials()

    if not creds['access_token']:
        if is_dry_run():
            logger.info(f"[DRY RUN] Would post to Facebook (no token): {content[:100]}...")
            return {
                "success": True,
                "dry_run": True,
                "platform": "facebook",
                "message": f"Would post to Facebook ({len(content)} chars) — no token",
                "content_preview": content[:200],
                "link": link,
                "photo_url": photo_url,
                "note": "Set META_ACCESS_TOKEN and DRY_RUN=false to actually post"
            }
        return {
            "success": False,
            "error": "Facebook access token not configured"
        }

    if is_dry_run():
        logger.info(f"[DRY RUN] Would post to Facebook: {content[:100]}...")
        return {
            "success": True,
            "dry_run": True,
            "platform": "facebook",
            "message": f"Would post to Facebook ({len(content)} chars)",
            "content_preview": content[:200],
            "link": link,
            "photo_url": photo_url,
            "note": "Set DRY_RUN=false to actually post"
        }
    
    try:
        # Use user's feed if no page_id
        target_id = page_id or 'me'
        
        # Prepare payload
        payload = {
            'message': content,
            'access_token': creds['access_token']
        }
        
        if link:
            payload['link'] = link
        
        if photo_url:
            # Post photo instead of text
            endpoint = f"{META_GRAPH_API}/{target_id}/photos"
            payload['url'] = photo_url
        else:
            endpoint = f"{META_GRAPH_API}/{target_id}/feed"
        
        response = requests.post(endpoint, data=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            post_id = result.get('id')
            
            # Log to vault
            _log_social_post_to_vault('facebook', {
                'id': post_id,
                'content': content,
                'link': link
            })
            
            return {
                "success": True,
                "platform": "facebook",
                "post_id": post_id,
                "post_url": f"https://facebook.com/{post_id}",
                "content": content,
                "link": link,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"Facebook API error: {response.status_code} - {response.text}")
            return {
                "success": False,
                "error": f"Facebook API error: {response.status_code}",
                "message": response.text[:200]
            }
            
    except Exception as e:
        logger.error(f"Error posting to Facebook: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@server.tool()
def post_to_instagram(
    caption: str,
    image_url: str,
    account_id: str = None
) -> Dict[str, Any]:
    """
    Post content to Instagram Business Account.

    Instagram requires an image URL along with the caption.

    Args:
        caption: Instagram caption
        image_url: URL of image to post
        account_id: Instagram Business Account ID (optional)

    Returns:
        Dict with post details
    """
    creds = get_credentials()

    if not creds['access_token']:
        if is_dry_run():
            logger.info(f"[DRY RUN] Would post to Instagram (no token): {caption[:100]}...")
            return {
                "success": True,
                "dry_run": True,
                "platform": "instagram",
                "message": f"Would post to Instagram ({len(caption)} chars) — no token",
                "caption_preview": caption[:200],
                "image_url": image_url,
                "note": "Set META_ACCESS_TOKEN and DRY_RUN=false to actually post"
            }
        return {
            "success": False,
            "error": "Facebook access token not configured"
        }

    if is_dry_run():
        logger.info(f"[DRY RUN] Would post to Instagram: {caption[:100]}...")
        return {
            "success": True,
            "dry_run": True,
            "platform": "instagram",
            "message": f"Would post to Instagram ({len(caption)} chars)",
            "caption_preview": caption[:200],
            "image_url": image_url,
            "note": "Set DRY_RUN=false to actually post"
        }
    
    # Use configured account ID if not provided
    ig_account_id = account_id or creds.get('instagram_account_id')
    
    if not ig_account_id:
        return {
            "success": False,
            "error": "Instagram Account ID not configured. Set INSTAGRAM_ACCOUNT_ID"
        }
    
    try:
        # Step 1: Create media container
        container_response = requests.post(
            f"{META_GRAPH_API}/{ig_account_id}/media",
            data={
                'image_url': image_url,
                'caption': caption,
                'access_token': creds['access_token']
            },
            timeout=30
        )
        
        if container_response.status_code != 200:
            return {
                "success": False,
                "error": f"Container creation failed: {container_response.status_code}",
                "message": container_response.text[:200]
            }
        
        container_id = container_response.json().get('id')
        
        # Step 2: Publish the media
        publish_response = requests.post(
            f"{META_GRAPH_API}/{ig_account_id}/media_publish",
            data={
                'creation_id': container_id,
                'access_token': creds['access_token']
            },
            timeout=30
        )
        
        if publish_response.status_code == 200:
            result = publish_response.json()
            media_id = result.get('id')
            
            # Log to vault
            _log_social_post_to_vault('instagram', {
                'id': media_id,
                'caption': caption,
                'image_url': image_url
            })
            
            return {
                "success": True,
                "platform": "instagram",
                "media_id": media_id,
                "media_url": f"https://instagram.com/p/{media_id}",
                "caption": caption,
                "image_url": image_url,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": f"Publish failed: {publish_response.status_code}",
                "message": publish_response.text[:200]
            }
            
    except Exception as e:
        logger.error(f"Error posting to Instagram: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@server.tool()
def post_cross_platform(
    content: str,
    platforms: List[str] = None,
    image_url: str = None,
    link: str = None
) -> Dict[str, Any]:
    """
    Post content to multiple platforms simultaneously.

    Args:
        content: Post content/caption
        platforms: List of platforms ['facebook', 'instagram'] (default: all configured)
        image_url: Image URL for Instagram (optional)
        link: Link to share on Facebook (optional)

    Returns:
        Dict with results from each platform
    """
    if platforms is None:
        platforms = ['facebook', 'instagram']

    if is_dry_run():
        logger.info(f"[DRY RUN] Would post cross-platform to {platforms}")
        results = {}
        for platform in platforms:
            results[platform] = {
                "success": True,
                "dry_run": True,
                "message": f"Would post to {platform}",
                "content_preview": content[:200]
            }
        return {
            "success": True,
            "dry_run": True,
            "platforms_attempted": len(platforms),
            "platforms_successful": len(platforms),
            "results": results,
            "note": "Set DRY_RUN=false to actually post",
            "timestamp": datetime.now().isoformat()
        }
    
    results = {}

    for platform in platforms:
        if platform == 'facebook':
            # Facebook: no strict char limit, but keep under 5000
            fb_content = content[:5000] if len(content) > 5000 else content
            result = post_to_facebook(fb_content, link=link)
            results['facebook'] = result
        elif platform == 'instagram':
            if not image_url:
                results['instagram'] = {
                    "success": False,
                    "error": "Image URL required for Instagram"
                }
            else:
                # Instagram: 2200 char limit
                ig_content = content[:2200] if len(content) > 2200 else content
                result = post_to_instagram(ig_content, image_url)
                results['instagram'] = result
    
    # Summary
    successful = sum(1 for r in results.values() if r.get('success'))
    
    return {
        "success": successful > 0,
        "platforms_attempted": len(platforms),
        "platforms_successful": successful,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


@server.tool()
def get_facebook_insights(
    page_id: str = None,
    metric_names: List[str] = None
) -> Dict[str, Any]:
    """
    Get Facebook Page insights/analytics.
    
    Args:
        page_id: Facebook Page ID (default: user's default page)
        metric_names: List of metrics to retrieve
    
    Returns:
        Dict with insights data
    """
    creds = get_credentials()
    
    if not creds['access_token']:
        return {
            "success": False,
            "error": "Facebook access token not configured"
        }
    
    default_metrics = [
        'page_impressions_unique',
        'page_engaged_users',
        'page_post_engagements',
        'page_likes',
        'page_follows'
    ]
    
    metrics = metric_names or default_metrics
    target_id = page_id or 'me'
    
    try:
        response = requests.get(
            f"{META_GRAPH_API}/{target_id}/insights",
            params={
                'metric': ','.join(metrics),
                'access_token': creds['access_token']
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "platform": "facebook",
                "insights": response.json().get('data', [])
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


@server.tool()
def get_instagram_insights(
    account_id: str = None,
    metric_names: List[str] = None
) -> Dict[str, Any]:
    """
    Get Instagram Business Account insights/analytics.
    
    Args:
        account_id: Instagram Account ID
        metric_names: List of metrics to retrieve
    
    Returns:
        Dict with insights data
    """
    creds = get_credentials()
    
    if not creds['access_token']:
        return {
            "success": False,
            "error": "Facebook access token not configured"
        }
    
    ig_account_id = account_id or creds.get('instagram_account_id')
    
    if not ig_account_id:
        return {
            "success": False,
            "error": "Instagram Account ID not configured"
        }
    
    default_metrics = [
        'impressions',
        'reach',
        'profile_views',
        'follower_count',
        'engagement'
    ]
    
    metrics = metric_names or default_metrics
    
    try:
        response = requests.get(
            f"{META_GRAPH_API}/{ig_account_id}/insights",
            params={
                'metric': ','.join(metrics),
                'access_token': creds['access_token']
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "platform": "instagram",
                "insights": response.json().get('data', [])
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


@server.tool()
def list_pages() -> Dict[str, Any]:
    """
    List Facebook Pages accessible with the token.
    
    Returns:
        Dict with list of pages
    """
    creds = get_credentials()
    
    if not creds['access_token']:
        return {
            "success": False,
            "error": "Facebook access token not configured"
        }
    
    try:
        response = requests.get(
            f"{META_GRAPH_API}/me/accounts",
            params={'access_token': creds['access_token']},
            timeout=30
        )
        
        if response.status_code == 200:
            pages = response.json().get('data', [])
            return {
                "success": True,
                "count": len(pages),
                "pages": pages
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


@server.tool()
def list_instagram_accounts() -> Dict[str, Any]:
    """
    List Instagram Business Accounts accessible with the token.
    
    Returns:
        Dict with list of accounts
    """
    creds = get_credentials()
    
    if not creds['access_token']:
        return {
            "success": False,
            "error": "Facebook access token not configured"
        }
    
    try:
        response = requests.get(
            f"{META_GRAPH_API}/me/instagram_business_accounts",
            params={'access_token': creds['access_token']},
            timeout=30
        )
        
        if response.status_code == 200:
            accounts = response.json().get('data', [])
            return {
                "success": True,
                "count": len(accounts),
                "accounts": accounts
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


def _log_social_post_to_vault(platform: str, post_data: Dict):
    """Log social media post to vault for audit trail."""
    try:
        vault_path = os.getenv('VAULT_PATH', './vault')
        logs_dir = Path(vault_path) / 'Logs'
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = logs_dir / f"social_{platform}_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "social_post",
            "platform": platform,
            "data": post_data
        }
        
        if log_file.exists():
            logs = json.loads(log_file.read_text())
            if not isinstance(logs, list):
                logs = [logs]
            logs.append(log_entry)
        else:
            logs = [log_entry]
        
        log_file.write_text(json.dumps(logs, indent=2))
        
    except Exception as e:
        logger.warning(f"Failed to log {platform} post to vault: {e}")


if __name__ == "__main__":
    logger.info("Starting Facebook/Instagram MCP Server...")
    
    # Test connection
    status = social_status()
    logger.info(f"Social Media Status: {status['status']}")
    
    server.run()
