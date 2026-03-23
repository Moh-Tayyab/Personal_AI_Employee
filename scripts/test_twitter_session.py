#!/usr/bin/env python3
"""
Test Twitter Session

Checks if the saved Twitter session is valid and working.

Usage:
    python scripts/test_twitter_session.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp.twitter.browser import TwitterBrowserSync


def main():
    session_path = "./vault/secrets/twitter_session"
    
    print("="*70)
    print("  Twitter Session Test")
    print("="*70)
    print()
    
    # Check if session file exists
    storage_file = Path(session_path) / "storage.json"
    
    if not storage_file.exists():
        print("❌ No session file found")
        print(f"   Path: {storage_file}")
        print()
        print("You need to authenticate first:")
        print("  python scripts/authenticate_social_media.py --platform twitter")
        return 1
    
    print("✓ Session file exists")
    print(f"  Path: {storage_file}")
    
    import os
    file_size = storage_file.stat().st_size
    print(f"  Size: {file_size:,} bytes")
    print()
    
    # Try to load and check session
    print("🔍 Checking session validity...")
    browser = TwitterBrowserSync(session_path)
    
    try:
        result = browser.check_session()
        
        print()
        print("="*70)
        print("  Result")
        print("="*70)
        print()
        
        status = result.get("status", "unknown")
        
        if status == "authenticated":
            print("✅ Session is VALID!")
            print(f"   Username: {result.get('username', 'Unknown')}")
            print(f"   You can now post tweets using the Social Media Manager")
            return 0
        else:
            print("⚠️  Session is INVALID or EXPIRED")
            print(f"   Status: {status}")
            print(f"   Message: {result.get('message', 'Unknown')}")
            print()
            print("Re-authenticate with:")
            print("  python scripts/authenticate_social_media.py --platform twitter")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        browser.close()


if __name__ == "__main__":
    sys.exit(main())
