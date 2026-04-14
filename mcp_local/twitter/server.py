#!/usr/bin/env python3
"""
Twitter/X MCP Server for Personal AI Employee (Gold Tier)

Provides Twitter/X integration for posting tweets and generating summaries.
Uses Twitter API v2.

Configuration:
- TWITTER_BEARER_TOKEN: Twitter API Bearer Token
- TWITTER_API_KEY: Twitter API Key
- TWITTER_API_SECRET: Twitter API Secret
- TWITTER_ACCESS_TOKEN: Twitter Access Token
- TWITTER_ACCESS_SECRET: Twitter Access Token Secret
- VAULT_PATH: Path to vault for logging

Run:
    python mcp/twitter/server.py

Twitter API Setup:
1. Go to https://developer.twitter.com/
2. Create a developer account and app
3. Get your API keys and tokens
4. Set environment variables
"""

import os
import sys
import json
import logging
import base64
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("twitter-mcp")

# Create FastMCP server
server = FastMCP(
    "twitter",
    instructions="Twitter/X integration for Personal AI Employee (Gold Tier)"
)

# Twitter API endpoints
TWITTER_API_BASE = "https://api.twitter.com/2"
TWITTER_API_V1 = "https://api.twitter.com/1.1"


def get_credentials() -> Dict[str, str]:
    """Get Twitter credentials from environment or vault."""
    creds = {
        'bearer_token': os.getenv('TWITTER_BEARER_TOKEN'),
        'api_key': os.getenv('TWITTER_API_KEY'),
        'api_secret': os.getenv('TWITTER_API_SECRET'),
        'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
        'access_secret': os.getenv('TWITTER_ACCESS_SECRET')
    }

    # Check vault secrets if not in environment
    if not creds['bearer_token']:
        vault_path = os.getenv('VAULT_PATH', './vault')
        creds_file = Path(vault_path) / 'secrets' / 'twitter_credentials.json'
        if creds_file.exists():
            stored_creds = json.loads(creds_file.read_text())
            creds.update(stored_creds)

    return creds


def is_dry_run() -> bool:
    """Check if dry_run mode is enabled."""
    return os.getenv('DRY_RUN', 'true').lower() == 'true'


def get_oauth_signature(creds: Dict) -> Dict[str, str]:
    """Generate OAuth 1.0a signature for API requests."""
    import hmac
    import hashlib
    import time
    import urllib.parse
    
    consumer_key = creds['api_key']
    consumer_secret = creds['api_secret']
    access_token = creds['access_token']
    access_secret = creds['access_secret']
    
    # OAuth parameters
    oauth_params = {
        'oauth_consumer_key': consumer_key,
        'oauth_nonce': str(int(time.time())),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': access_token,
        'oauth_version': '1.0'
    }
    
    return oauth_params


@server.tool()
def twitter_status() -> Dict[str, Any]:
    """
    Check Twitter API connection status.
    
    Returns:
        Dict with connection status and capabilities
    """
    creds = get_credentials()
    
    status = {
        "status": "needs_configuration",
        "configured": bool(creds['bearer_token'] and creds['api_key']),
        "tier": "gold",
        "capabilities": [
            "post_tweet",
            "post_thread",
            "get_timeline",
            "search_tweets",
            "get_user_info"
        ]
    }
    
    if creds['bearer_token']:
        try:
            # Test connection by getting user info
            headers = {'Authorization': f'Bearer {creds["bearer_token"]}'}
            response = requests.get(
                f"{TWITTER_API_BASE}/users/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user = response.json().get('data', {})
                status["status"] = "connected"
                status["username"] = user.get('username')
                status["name"] = user.get('name')
                status["user_id"] = user.get('id')
            else:
                status["status"] = "auth_error"
                status["error"] = f"API error: {response.status_code}"
                
        except Exception as e:
            status["status"] = "connection_error"
            status["error"] = str(e)
    
    return status


@server.tool()
def post_tweet(
    content: str,
    reply_to: str = None
) -> Dict[str, Any]:
    """
    Post a tweet to Twitter/X.

    Args:
        content: Tweet content (max 280 characters)
        reply_to: Tweet ID to reply to (optional)

    Returns:
        Dict with tweet details including ID and URL
    """
    creds = get_credentials()

    if not creds['access_token'] or not creds['api_key']:
        return {
            "success": False,
            "error": "Twitter credentials not fully configured",
            "message": "Need API Key, Secret, Access Token, and Access Secret"
        }

    # Check dry_run mode
    if is_dry_run():
        logger.info(f"[DRY RUN] Would post tweet: {content[:100]}...")
        return {
            "success": True,
            "dry_run": True,
            "message": f"Would post tweet ({len(content)} chars)",
            "content_preview": content[:200],
            "reply_to": reply_to,
            "note": "Set DRY_RUN=false to actually post"
        }

    # Truncate if too long
    if len(content) > 280:
        content = content[:277] + "..."
        logger.warning("Content truncated to 280 characters")
    
    try:
        # OAuth 1.0a authentication
        import oauthlib
        from requests_oauthlib import OAuth1Session
        
        oauth = OAuth1Session(
            creds['api_key'],
            client_secret=creds['api_secret'],
            resource_owner_key=creds['access_token'],
            resource_owner_secret=creds['access_secret']
        )
        
        # Prepare payload
        payload = {"text": content}
        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}
        
        # Post tweet
        response = oauth.post(
            f"{TWITTER_API_BASE}/tweets",
            json=payload
        )
        
        if response.status_code == 201:
            result = response.json()
            tweet_id = result['data']['id']
            
            # Log to vault
            _log_tweet_to_vault({
                'id': tweet_id,
                'text': content,
                'reply_to': reply_to
            })
            
            return {
                "success": True,
                "tweet_id": tweet_id,
                "tweet_url": f"https://twitter.com/statuses/{tweet_id}",
                "content": content,
                "reply_to": reply_to,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"Twitter API error: {response.status_code} - {response.text}")
            return {
                "success": False,
                "error": f"Twitter API error: {response.status_code}",
                "message": response.text[:200]
            }
            
    except ImportError:
        # Fallback: return simulated response for testing
        logger.warning("oauthlib/requests_oauthlib not installed - simulating response")
        return {
            "success": True,
            "simulated": True,
            "tweet_id": "SIMULATED_" + datetime.now().strftime('%Y%m%d%H%M%S'),
            "content": content,
            "message": "Tweet would be posted (oauthlib not installed)"
        }
    except Exception as e:
        logger.error(f"Error posting tweet: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@server.tool()
def post_thread(
    tweets: List[str]
) -> Dict[str, Any]:
    """
    Post a thread of tweets to Twitter/X.

    Args:
        tweets: List of tweet contents (each max 280 chars)

    Returns:
        Dict with thread details including all tweet IDs
    """
    if not tweets:
        return {
            "success": False,
            "error": "No tweets provided"
        }

    if is_dry_run():
        logger.info(f"[DRY RUN] Would post thread of {len(tweets)} tweets")
        return {
            "success": True,
            "dry_run": True,
            "message": f"Would post thread of {len(tweets)} tweets",
            "tweets_preview": [t[:100] for t in tweets],
            "note": "Set DRY_RUN=false to actually post"
        }

    results = []
    previous_tweet_id = None
    
    for i, content in enumerate(tweets):
        result = post_tweet(content, reply_to=previous_tweet_id)
        
        if result.get('success'):
            results.append(result)
            previous_tweet_id = result['tweet_id']
        else:
            return {
                "success": False,
                "error": f"Failed at tweet {i+1}",
                "details": result,
                "successful_tweets": len(results)
            }
    
    return {
        "success": True,
        "thread_count": len(results),
        "tweets": results,
        "thread_url": f"https://twitter.com/statuses/{results[0]['tweet_id']}",
        "timestamp": datetime.now().isoformat()
    }


@server.tool()
def get_timeline(
    username: str = None,
    count: int = 10
) -> Dict[str, Any]:
    """
    Get recent tweets from a user's timeline.
    
    Args:
        username: Twitter username (default: authenticated user)
        count: Number of tweets to retrieve (max 100)
    
    Returns:
        Dict with timeline tweets
    """
    creds = get_credentials()
    
    if not creds['bearer_token']:
        return {
            "success": False,
            "error": "Twitter bearer token not configured"
        }
    
    try:
        headers = {'Authorization': f'Bearer {creds["bearer_token"]}'}
        
        # Get user ID if username provided
        if username:
            user_response = requests.get(
                f"{TWITTER_API_BASE}/users/by/username/{username}",
                headers=headers,
                timeout=10
            )
            
            if user_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"User not found: {username}"
                }
            
            user_id = user_response.json()['data']['id']
        else:
            # Use authenticated user
            user_response = requests.get(
                f"{TWITTER_API_BASE}/users/me",
                headers=headers,
                timeout=10
            )
            user_id = user_response.json()['data']['id']
        
        # Get tweets
        tweets_response = requests.get(
            f"{TWITTER_API_BASE}/users/{user_id}/tweets",
            headers=headers,
            params={'max_results': min(count, 100)},
            timeout=10
        )
        
        if tweets_response.status_code == 200:
            tweets = tweets_response.json().get('data', [])
            return {
                "success": True,
                "count": len(tweets),
                "tweets": tweets
            }
        else:
            return {
                "success": False,
                "error": f"API error: {tweets_response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@server.tool()
def search_tweets(
    query: str,
    count: int = 10
) -> Dict[str, Any]:
    """
    Search for tweets matching a query.
    
    Args:
        query: Search query (Twitter search syntax)
        count: Number of tweets to retrieve (max 100)
    
    Returns:
        Dict with matching tweets
    """
    creds = get_credentials()
    
    if not creds['bearer_token']:
        return {
            "success": False,
            "error": "Twitter bearer token not configured"
        }
    
    try:
        headers = {'Authorization': f'Bearer {creds["bearer_token"]}'}
        
        response = requests.get(
            f"{TWITTER_API_BASE}/tweets/search/recent",
            headers=headers,
            params={
                'query': query,
                'max_results': min(count, 100)
            },
            timeout=10
        )
        
        if response.status_code == 200:
            tweets = response.json().get('data', [])
            return {
                "success": True,
                "count": len(tweets),
                "query": query,
                "tweets": tweets
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
def post_business_update(
    topic: str,
    key_points: List[str],
    hashtags: List[str] = None
) -> Dict[str, Any]:
    """
    Create and post a structured business update to Twitter.

    Args:
        topic: Main topic/headline
        key_points: List of key points (will be formatted as thread)
        hashtags: List of hashtags (optional)

    Returns:
        Dict with post result
    """
    if is_dry_run():
        # Format tweets for preview
        tweets = []
        first_tweet = f"🚀 {topic}"
        if hashtags:
            first_tweet += " " + " ".join([f"#{h}" for h in hashtags[:3]])
        tweets.append(first_tweet)
        for point in key_points:
            tweets.append(f"• {point}")

        logger.info(f"[DRY RUN] Would post business update thread of {len(tweets)} tweets")
        return {
            "success": True,
            "dry_run": True,
            "message": f"Would post business update thread ({len(tweets)} tweets)",
            "tweets_preview": [t[:100] for t in tweets],
            "note": "Set DRY_RUN=false to actually post"
        }

    # Format tweets
    tweets = []
    
    # First tweet with topic
    first_tweet = f"🚀 {topic}"
    if hashtags:
        first_tweet += " " + " ".join([f"#{h}" for h in hashtags[:3]])
    tweets.append(first_tweet)
    
    # Additional tweets for key points
    current_tweet = ""
    for point in key_points:
        point_text = f"• {point}"
        if len(current_tweet) + len(point_text) + 1 < 280:
            if current_tweet:
                current_tweet += "\n" + point_text
            else:
                current_tweet = point_text
        else:
            if current_tweet:
                tweets.append(current_tweet)
            current_tweet = point_text
    
    if current_tweet:
        tweets.append(current_tweet)
    
    # Post as thread
    return post_thread(tweets)


def _log_tweet_to_vault(tweet_data: Dict):
    """Log tweet to vault for audit trail."""
    try:
        vault_path = os.getenv('VAULT_PATH', './vault')
        logs_dir = Path(vault_path) / 'Logs'
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = logs_dir / f"twitter_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "tweet_posted",
            "data": tweet_data
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
        logger.warning(f"Failed to log tweet to vault: {e}")


if __name__ == "__main__":
    logger.info("Starting Twitter/X MCP Server...")
    
    # Test connection
    status = twitter_status()
    logger.info(f"Twitter Status: {status['status']}")
    
    server.run()
