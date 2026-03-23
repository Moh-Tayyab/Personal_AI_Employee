#!/usr/bin/env python3
"""
Twitter/X Simple Authentication Script

Uses the existing TwitterBrowserSync synchronous wrapper properly.

Usage:
    python scripts/twitter_auth_simple.py --username YOUR_USERNAME --password YOUR_PASSWORD
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp.twitter.browser import TwitterBrowserSync


def main():
    parser = argparse.ArgumentParser(description="Twitter authentication")
    parser.add_argument("--username", required=True, help="Twitter username")
    parser.add_argument("--password", required=True, help="Twitter password")
    parser.add_argument("--session-path", default="./vault/secrets/twitter_session", help="Session storage path")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    args = parser.parse_args()
    
    print("="*70)
    print("  Twitter/X Authentication")
    print("="*70)
    print()
    print(f"Username: {args.username}")
    print(f"Headless: {args.headless}")
    print()
    
    # Create browser (sync wrapper handles async internally)
    browser = TwitterBrowserSync(args.session_path)
    
    try:
        # Login (this is synchronous)
        print("🔐 Attempting login...")
        result = browser.login(args.username, args.password)
        
        print()
        print("="*70)
        print("  Result")
        print("="*70)
        print()
        
        status = result.get("status", "unknown")
        
        if status == "logged_in" or status == "already_logged_in":
            print("✅ SUCCESS!")
            print(f"   Status: {status}")
            if "profile_url" in result:
                print(f"   Profile: {result['profile_url']}")
            print()
            print("Session saved to:", args.session_path)
            return 0
        elif status == "needs_verification":
            print("⚠️  VERIFICATION REQUIRED")
            print(f"   {result.get('message', '')}")
            print(f"   URL: {result.get('url', '')}")
            print()
            print("Please complete verification and re-run.")
            return 1
        else:
            print("❌ FAILED")
            print(f"   Status: {status}")
            print(f"   Error: {result.get('error', 'Unknown')}")
            print()
            print("Possible reasons:")
            print("   - Wrong username/password")
            print("   - Twitter requires verification")
            print("   - Account locked/suspended")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        print()
        print("🚪 Closing browser...")
        browser.close()
        print("Done!\n")


if __name__ == "__main__":
    sys.exit(main())
