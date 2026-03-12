#!/usr/bin/env python3
"""
LinkedIn Login Script - Authenticate with LinkedIn

Usage:
    python3 run/linkedin_login.py your_email your_password
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.linkedin.browser_sync import LinkedInBrowser

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 run/linkedin_login.py <email> <password>")
        print("\nExample:")
        print('python3 run/linkedin_login.py "user@example.com" "mypassword"')
        return
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    session_path = Path("./vault/secrets/linkedin_session")
    session_path.mkdir(parents=True, exist_ok=True)
    
    browser = LinkedInBrowser(str(session_path))
    
    try:
        print(f"Logging in as {email}...")
        result = browser.login(email, password)
        print(f"\nResult: {json.dumps(result, indent=2)}")
        
        if result.get('status') in ['logged_in', 'already_logged_in']:
            print("\n✅ Login successful! Session saved.")
            print("\nYou can now post to LinkedIn using:")
            print("python3 run/linkedin_post.py")
        else:
            print(f"\n⚠️ Login may have failed: {result}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()

if __name__ == "__main__":
    main()
