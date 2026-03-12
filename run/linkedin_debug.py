#!/usr/bin/env python3
"""Debug LinkedIn page to see available elements"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.linkedin.browser import LinkedInBrowserSync

browser = LinkedInBrowserSync("./vault/secrets/linkedin_session")

try:
    print("Checking session and navigating to feed...")
    status = browser.check_session()
    print(f"Session: {json.dumps(status, indent=2)}")
    
    if status.get('status') == 'authenticated':
        print("\nTaking snapshot of the page...")
        # Get page HTML to see what's available
        from mcp.linkedin.browser import LinkedInBrowser
        import asyncio
        
        async def debug_page():
            lb = LinkedInBrowser("./vault/secrets/linkedin_session")
            await lb.start(headless=False)
            
            # Load storage state
            storage_file = Path("./vault/secrets/linkedin_session/storage.json")
            if storage_file.exists():
                await lb.context.storage_state()
            
            await lb.page.goto("https://www.linkedin.com/feed", wait_until="domcontentloaded")
            await lb.page.wait_for_timeout(8000)
            
            # Take screenshot
            await lb.page.screenshot(path="linkedin_debug.png", full_page=True)
            print("Screenshot saved to linkedin_debug.png")
            
            # Get page content
            content = await lb.page.content()
            print(f"\nPage URL: {lb.page.url}")
            print(f"Page title: {await lb.page.title()}")
            
            # Look for post creation elements
            selectors_to_try = [
                'button:has-text("Start a post")',
                'div[role="button"]:has-text("Start a post")',
                'button:has-text("Start a post")',
                '[aria-label*="Create a post"]',
                'div[class*="share-box"]',
                'button[class*="share"]',
            ]
            
            print("\n\nSearching for post creation elements:")
            for selector in selectors_to_try:
                try:
                    element = await lb.page.wait_for_selector(selector, timeout=2000)
                    if element:
                        print(f"  ✓ Found: {selector}")
                        box = await element.bounding_box()
                        print(f"    Position: {box}")
                except Exception as e:
                    print(f"  ✗ Not found: {selector}")
            
            await lb.close()
        
        asyncio.run(debug_page())
        
finally:
    browser.close()
