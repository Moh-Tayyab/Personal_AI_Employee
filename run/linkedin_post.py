#!/usr/bin/env python3
"""
LinkedIn Post Script - Post about Muhammad Tayyab to LinkedIn

Usage:
    python3 run/linkedin_post.py
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.linkedin.browser_sync import LinkedInBrowser

# Post content about Muhammad Tayyab
POST_CONTENT = """🚀 Excited to share my journey as a Full Stack Developer!

I'm Muhammad Tayyab, a passionate developer working on innovative AI solutions. Currently building a Personal AI Employee - an autonomous digital FTE that automates daily tasks and workflows.

💡 What it does:
- Automates email & social media posting
- Integrates with Odoo ERP
- Uses AI agents for autonomous task execution
- MCP-based architecture for extensibility

#FullStackDeveloper #AI #Automation #Innovation #PersonalAI #SoftwareEngineering #LinkedInCommunity

What's your take on AI-powered automation? Let's connect and discuss! 👇
"""

def main():
    session_path = Path("./vault/secrets/linkedin_session")
    session_path.mkdir(parents=True, exist_ok=True)
    
    browser = LinkedInBrowser(str(session_path))
    
    try:
        # Check session first
        print("Checking LinkedIn session...")
        status = browser.check_session()
        print(f"Session status: {json.dumps(status, indent=2)}")
        
        if status.get('status') != 'authenticated':
            print("\n❌ Not authenticated. Please login first.")
            print("\nRun this command to login:")
            print('python3 run/linkedin_login.py "your_email" "your_password"')
            return
        
        # Create post
        print("\n📝 Posting to LinkedIn...")
        result = browser.create_post(POST_CONTENT)
        print(f"\nResult: {json.dumps(result, indent=2)}")
        
        if result.get('status') == 'posted':
            print("\n✅ Successfully posted to LinkedIn!")
        else:
            print(f"\n⚠️ Post may not have succeeded: {result}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()

if __name__ == "__main__":
    main()
