#!/usr/bin/env python3
"""
Twitter/X Interactive Authentication

This script opens a browser and lets you manually login to Twitter.
It will save the session automatically after you complete login.

This is more reliable than automated login because:
- Handles any 2FA/captcha automatically
- Works with Twitter's changing login flow
- You control the credentials (never typed into script)

Usage:
    python scripts/twitter_interactive_auth.py
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp.twitter.browser import TwitterBrowserSync


def interactive_twitter_auth(session_path: str = "./vault/secrets/twitter_session"):
    """
    Interactive Twitter authentication.
    Opens browser, user logs in manually, session is saved automatically.
    """
    print("="*70)
    print("  Twitter/X Interactive Authentication")
    print("="*70)
    print()
    print("INSTRUCTIONS:")
    print()
    print("1. A browser window will open and navigate to Twitter login")
    print("2. Login to Twitter manually (enter username, password, 2FA, etc.)")
    print("3. After login, navigate to your home feed (twitter.com/home)")
    print("4. Press Enter in this terminal to save the session")
    print("5. The browser will close and session will be saved")
    print()
    print("OR:")
    print("- If already logged in, just press Enter after browser opens")
    print()
    
    input("\nPress Enter to open the browser...")
    
    print("\n🌐 Opening browser...")
    browser = TwitterBrowserSync(session_path)
    
    try:
        # Start browser (not headless so user can see and interact)
        browser.start(headless=False)
        
        # Navigate to Twitter
        print("📍 Navigating to Twitter...")
        browser.browser.page.goto("https://twitter.com/login", wait_until="networkidle", timeout=30000)
        
        print("\n" + "="*70)
        print("  BROWSER IS OPEN")
        print("="*70)
        print()
        print("👉 If NOT logged in:")
        print("   - Enter your username and password")
        print("   - Complete any 2FA/captcha if prompted")
        print("   - Wait until you see your home feed")
        print()
        print("👉 If ALREADY logged in:")
        print("   - You should see your Twitter home feed")
        print()
        print("✅ When you see your home feed, press Enter below to save session")
        print()
        
        input("Press Enter after you're logged in and see your home feed...")
        
        # Save the session
        print("\n💾 Saving session...")
        browser.save_storage_state()
        
        # Verify session
        print("🔍 Verifying session...")
        result = browser.check_session()
        
        print("\n" + "="*70)
        print("  Authentication Result")
        print("="*70)
        print()
        
        if result.get("status") == "authenticated":
            print("✅ SUCCESS! Twitter session saved.")
            print(f"   Username: {result.get('username', 'Unknown')}")
            print(f"   Session: {session_path}/storage.json")
            print()
            print("You can now use the Social Media Manager agent to post tweets!")
            return True
        else:
            print("⚠️  Session may not be valid")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Message: {result.get('message', 'Unknown error')}")
            print()
            print("Try again and make sure you're logged in before pressing Enter.")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please try again.")
        return False
    finally:
        print("\n🚪 Closing browser...")
        browser.close()
        print("Done!\n")


def main():
    session_path = "./vault/secrets/twitter_session"
    
    # Check if session already exists
    storage_file = Path(session_path) / "storage.json"
    if storage_file.exists():
        print("⚠️  Existing session found!")
        print(f"   Location: {storage_file}")
        print()
        print("Options:")
        print("  1. Keep existing session (exit)")
        print("  2. Overwrite with new session")
        print()
        
        choice = input("Enter choice (1 or 2): ").strip()
        if choice != "2":
            print("Exiting...")
            sys.exit(0)
        print("\nOverwriting existing session...\n")
    
    # Run interactive auth
    success = interactive_twitter_auth(session_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
