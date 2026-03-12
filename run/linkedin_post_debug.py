#!/usr/bin/env python3
"""Simple LinkedIn post with verbose debugging"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.linkedin.browser import LinkedInBrowser, LinkedInBrowserSync
import asyncio

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

async def post_to_linkedin():
    browser = LinkedInBrowser("./vault/secrets/linkedin_session")
    
    try:
        print("Starting browser...")
        await browser.start(headless=False)
        
        print("Navigating to LinkedIn feed...")
        await browser.page.goto("https://www.linkedin.com/feed", wait_until="domcontentloaded")
        await browser.page.wait_for_timeout(8000)
        
        print(f"Current URL: {browser.page.url}")
        
        # Take screenshot
        await browser.page.screenshot(path="linkedin_feed.png")
        print("Screenshot saved to linkedin_feed.png")
        
        # Get all buttons on the page
        buttons = await browser.page.query_selector_all('button')
        print(f"\nFound {len(buttons)} buttons on page")
        
        for i, btn in enumerate(buttons[:20]):  # First 20 buttons
            try:
                text = await btn.inner_text()
                aria = await btn.get_attribute('aria-label')
                print(f"  Button {i}: '{text[:50]}' aria='{aria}'")
            except:
                pass
        
        # Try to find post creation area
        print("\n\nLooking for post creation area...")
        
        # Common LinkedIn post button selectors
        selectors = [
            'button:has-text("Start a post")',
            'button:has-text("Create a post")',
            '[aria-label*="Create a post"]',
            '[aria-label*="Start a post"]',
            'div[class*="share-box"] button',
            'div[class*="share-box-feed"]',
        ]
        
        for selector in selectors:
            try:
                element = await browser.page.query_selector(selector)
                if element:
                    text = await element.inner_text() if element else "N/A"
                    print(f"  ✓ Found with: {selector}")
                    print(f"    Text: {text[:100]}")
                    
                    # Try to click
                    try:
                        await element.click()
                        print("    Clicked successfully!")
                        await browser.page.wait_for_timeout(3000)
                        
                        # Now look for text editor
                        print("\nLooking for text editor...")
                        editors = await browser.page.query_selector_all('div[contenteditable="true"]')
                        print(f"Found {len(editors)} editable divs")
                        
                        if editors:
                            # Fill content
                            await editors[0].click()
                            await browser.page.wait_for_timeout(500)
                            await browser.page.keyboard.type(POST_CONTENT[:500], delay=50)
                            await browser.page.wait_for_timeout(2000)
                            
                            # Look for Post button
                            print("\nLooking for Post button...")
                            post_btn = await browser.page.query_selector('button:has-text("Post")')
                            if post_btn:
                                print("Found Post button!")
                                # Don't actually post in debug mode
                                # await post_btn.click()
                            else:
                                print("Post button not found")
                        
                        break
                    except Exception as e:
                        print(f"    Click failed: {e}")
            except Exception as e:
                print(f"  ✗ Selector failed: {selector} - {e}")
        
        await browser.page.wait_for_timeout(5000)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(post_to_linkedin())
