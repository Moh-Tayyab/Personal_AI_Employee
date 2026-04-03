#!/usr/bin/env python3
"""
LinkedIn MCP Server Test Script

Tests the LinkedIn integration to verify it's working correctly.

Usage:
    python scripts/test_linkedin.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

def test_linkedin():
    """Test LinkedIn MCP server functionality."""
    print("========================================")
    print("  LinkedIn MCP Server - Test")
    print("========================================")
    print("")
    
    # Check environment
    print("Checking configuration...")
    
    token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    if not token:
        # Try vault secrets
        vault_path = os.getenv('VAULT_PATH', './vault')
        token_file = Path(vault_path) / 'secrets' / 'linkedin_token.txt'
        if token_file.exists():
            token = token_file.read_text().strip()
            print(f"{GREEN}✓ Token found in vault secrets{NC}")
        else:
            print(f"{YELLOW}⚠ LINKEDIN_ACCESS_TOKEN not set{NC}")
            print("")
            print("To configure LinkedIn:")
            print("1. Go to https://www.linkedin.com/developers/apps")
            print("2. Create a new app")
            print("3. Get your Access Token")
            print("4. Set environment variable:")
            print("   export LINKEDIN_ACCESS_TOKEN=your_token")
            print("")
            print("   OR create vault/secrets/linkedin_token.txt")
            return False
    else:
        print(f"{GREEN}✓ LINKEDIN_ACCESS_TOKEN found{NC}")
    
    # Test API connection
    print("")
    print("Testing LinkedIn API connection...")
    
    try:
        import requests
        
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        response = requests.get(
            "https://api.linkedin.com/v2/me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            profile = response.json()
            print(f"{GREEN}✓ Connected to LinkedIn{NC}")
            print(f"  Profile ID: {profile.get('id', 'Unknown')}")
            return True
        else:
            print(f"{RED}✗ API Error: {response.status_code}{NC}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"{RED}✗ Connection timeout{NC}")
        return False
    except Exception as e:
        print(f"{RED}✗ Error: {e}{NC}")
        return False


def test_post():
    """Test posting to LinkedIn (dry run)."""
    print("")
    print("========================================")
    print("  Test Post (Dry Run)")
    print("========================================")
    print("")
    
    token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    if not token:
        print(f"{YELLOW}Skipping post test - no token configured{NC}")
        return
    
    print("This would post the following content:")
    print("")
    print("---")
    print("🚀 Personal AI Employee - Silver Tier Complete!")
    print("")
    print("• 24/7 autonomous operation")
    print("• Email, WhatsApp, and file monitoring")
    print("• Human-in-the-loop approval workflow")
    print("• Qwen Code reasoning engine")
    print("")
    print("Built with @Panaversity Hackathon")
    print("")
    print("#AI #Automation #Business")
    print("---")
    print("")
    
    response = input("Post this to LinkedIn? (y/n): ")
    if response.lower() == 'y':
        # Import and call the MCP function
        from mcp.linkedin.server import post_to_linkedin
        
        content = """🚀 Personal AI Employee - Silver Tier Complete!

• 24/7 autonomous operation
• Email, WhatsApp, and file monitoring
• Human-in-the-loop approval workflow
• Qwen Code reasoning engine

Built with @Panaversity Hackathon

#AI #Automation #Business"""
        
        result = post_to_linkedin(content)
        
        if result.get('success'):
            print(f"{GREEN}✓ Post successful!{NC}")
            print(f"  Post ID: {result.get('post_id')}")
            print(f"  URL: {result.get('post_url')}")
        else:
            print(f"{RED}✗ Post failed: {result.get('error')}{NC}")


if __name__ == "__main__":
    success = test_linkedin()
    
    if success:
        test_post()
    
    print("")
    print("========================================")
    print("  Test Complete")
    print("========================================")
