#!/usr/bin/env python3
"""
Twitter/X Automated Authentication with Better Error Handling

This script attempts to login to Twitter with improved selectors and error handling.
It handles Twitter's two-step login flow (username first, then password).

Usage:
    python scripts/twitter_auth_auto.py --username YOUR_USERNAME --password YOUR_PASSWORD
"""

import sys
import argparse
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp.twitter.browser import TwitterBrowserSync


def twitter_auth_auto(username: str, password: str, session_path: str = "./vault/secrets/twitter_session", headless: bool = False):
    """
    Automated Twitter authentication with detailed logging.
    """
    print("="*70)
    print("  Twitter/X Automated Authentication")
    print("="*70)
    print()
    print(f"Username: {username}")
    print(f"Headless: {headless}")
    print(f"Session: {session_path}")
    print()
    
    browser = TwitterBrowserSync(session_path)
    
    try:
        # Start browser
        print("🌐 Opening browser...")
        browser.start(headless=headless)
        
        # Navigate to login
        print("📍 Navigating to Twitter login...")
        page = browser.browser.page
        
        page.goto("https://twitter.com/i/flow/login", wait_until="networkidle", timeout=30000)
        time.sleep(3)
        
        # Check if already logged in
        current_url = page.url
        if "home" in current_url or "timeline" in current_url:
            print("✅ Already logged in!")
            browser.save_storage_state()
            result = browser.check_session()
            print_result(result)
            return result.get("status") == "authenticated"
        
        print("📝 Step 1: Entering username...")
        
        # Find username field - try multiple approaches
        username_entered = False
        for selector in ['input[autocomplete="username"]', 'input[name="text"]', 'input[type="text"]']:
            try:
                field = page.wait_for_selector(selector, timeout=5000)
                if field:
                    field.click()
                    time.sleep(0.5)
                    field.fill(username)
                    time.sleep(1)
                    username_entered = True
                    print(f"   ✓ Used selector: {selector}")
                    break
            except Exception as e:
                continue
        
        if not username_entered:
            print("❌ Could not find username field")
            print(f"   Current URL: {page.url}")
            return False
        
        # Click Next
        print("📝 Clicking Next...")
        next_clicked = False
        for selector in ['button:has-text("Next")', 'div[role="button"]:has-text("Next")']:
            try:
                btn = page.wait_for_selector(selector, timeout=5000)
                if btn:
                    btn.click()
                    next_clicked = True
                    print(f"   ✓ Used selector: {selector}")
                    break
            except:
                continue
        
        if not next_clicked:
            print("⚠️  Next button not found, trying Enter key...")
            try:
                page.keyboard.press("Enter")
                next_clicked = True
            except:
                pass
        
        time.sleep(3)
        
        # Check for verification
        current_url = page.url
        if "challenge" in current_url or "verification" in current_url:
            print("⚠️  Verification required")
            print(f"   URL: {current_url}")
            print("   Please complete verification manually")
            return False
        
        # Wait for password field
        print("📝 Step 2: Entering password...")
        
        # Wait for password field to load
        time.sleep(2)
        
        password_entered = False
        for selector in ['input[name="password"]', 'input[type="password"]', 'input[autocomplete="current-password"]']:
            try:
                field = page.wait_for_selector(selector, timeout=10000)
                if field:
                    field.click()
                    time.sleep(0.5)
                    field.fill(password)
                    time.sleep(1)
                    password_entered = True
                    print(f"   ✓ Used selector: {selector}")
                    break
            except Exception as e:
                print(f"   ✗ Selector failed: {selector}")
                continue
        
        if not password_entered:
            print("❌ Could not find password field")
            print(f"   Current URL: {page.url}")
            print("   Twitter may have changed the login flow")
            return False
        
        # Click Login
        print("📝 Clicking Login...")
        login_clicked = False
        for selector in ['button[data-testid="LoginForm_Login_Button"]', 'button:has-text("Log in")', 'button[type="submit"]']:
            try:
                btn = page.wait_for_selector(selector, timeout=5000)
                if btn:
                    btn.click()
                    login_clicked = True
                    print(f"   ✓ Used selector: {selector}")
                    break
            except:
                continue
        
        if not login_clicked:
            print("⚠️  Login button not found, trying Enter key...")
            try:
                page.keyboard.press("Enter")
                login_clicked = True
            except:
                pass
        
        # Wait for login to complete
        print("⏳ Waiting for login to complete...")
        time.sleep(5)
        
        # Check result
        current_url = page.url
        print(f"   Current URL: {current_url}")
        
        if "home" in current_url or "timeline" in current_url:
            print("✅ Login successful!")
            browser.save_storage_state()
            result = browser.check_session()
            print_result(result)
            return result.get("status") == "authenticated"
        elif "challenge" in current_url or "verification" in current_url:
            print("⚠️  Verification required")
            print(f"   URL: {current_url}")
            return False
        else:
            print("❌ Login may have failed")
            print(f"   URL: {current_url}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("\n🚪 Closing browser...")
        browser.close()


def print_result(result):
    """Print authentication result."""
    print()
    print("="*70)
    print("  Result")
    print("="*70)
    print()
    
    status = result.get("status", "unknown")
    
    if status == "authenticated":
        print("✅ SUCCESS!")
        print(f"   Username: {result.get('username', 'Unknown')}")
        print(f"   Session saved")
    elif status == "needs_verification":
        print("⚠️  VERIFICATION REQUIRED")
        print(f"   {result.get('message', '')}")
    else:
        print(f"❌ Status: {status}")
        print(f"   {result.get('message', '')}")
    
    print()


def main():
    parser = argparse.ArgumentParser(description="Twitter automated authentication")
    parser.add_argument("--username", required=True, help="Twitter username")
    parser.add_argument("--password", required=True, help="Twitter password")
    parser.add_argument("--session-path", default="./vault/secrets/twitter_session", help="Session storage path")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    args = parser.parse_args()
    
    success = twitter_auth_auto(
        username=args.username,
        password=args.password,
        session_path=args.session_path,
        headless=args.headless
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
