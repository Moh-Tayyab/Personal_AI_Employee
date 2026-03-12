#!/usr/bin/env python3
"""Debug LinkedIn post creation area with more selectors"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.linkedin.browser_sync import LinkedInBrowser

browser = LinkedInBrowser("./vault/secrets/linkedin_session")

try:
    print("Starting browser...")
    browser.start(headless=False)
    
    print("Going to LinkedIn feed...")
    browser.page.goto("https://www.linkedin.com/feed", wait_until="networkidle")
    browser.page.wait_for_timeout(15000)  # Wait longer for JS to load
    
    print(f"Current URL: {browser.page.url}")
    
    # Take screenshot
    browser.page.screenshot(path="linkedin_feed_full.png", full_page=True)
    print("Screenshot saved to linkedin_feed_full.png")
    
    # Try many different selectors for post creation
    selectors = [
        # Text-based
        'button:has-text("Start a post")',
        'button:has-text("Create a post")',
        '[aria-label*="Start a post"]',
        '[aria-label*="Create a post"]',
        
        # Class-based
        'div[class*="share-box"]',
        'div[class*="ShareBox"]',
        'div[class*="update-v2"]',
        
        # Data attributes
        '[data-control-name="share-box-feed-entry"]',
        '[data-id="share-box-feed-entry"]',
        
        # Placeholder based
        '[data-placeholder*="What"]',
        '[placeholder*="What"]',
        
        # Generic
        'div[contenteditable]',
        '[role="textbox"]',
        
        # By ID
        '[id*="share-box"]',
        '[id*="post-creation"]',
    ]
    
    print("\n--- Searching for post creation elements ---")
    for selector in selectors:
        try:
            element = browser.page.query_selector(selector, timeout=2000)
            if element:
                text = element.inner_text().strip()[:100] if element else "N/A"
                tag = element.tag_name() if element else "N/A"
                classes = element.get_attribute("class") if element else "N/A"
                print(f"  ✓ FOUND: {selector}")
                print(f"      Tag: {tag}, Class: {classes[:50] if classes else 'N/A'}")
                print(f"      Text: {text}")
                
                # Try to scroll into view and click
                try:
                    element.scroll_into_view_if_needed()
                    element.click()
                    print("      Clicked! Waiting...")
                    browser.page.wait_for_timeout(3000)
                    
                    # Check if modal opened
                    modal = browser.page.query_selector('div[role="dialog"]', timeout=2000)
                    if modal:
                        print("      Modal opened!")
                        
                        # Look for editable area now
                        editables = browser.page.query_selector_all('div[contenteditable="true"]')
                        print(f"      Found {len(editables)} editable divs in modal")
                        
                        if editables:
                            print("      SUCCESS! Found the editor!")
                            break
                except Exception as e:
                    print(f"      Click error: {e}")
                print()
        except:
            pass
    
    # If still not found, let's look at the HTML structure
    if True:
        print("\n--- Looking at page structure ---")
        # Get the main content area
        main = browser.page.query_selector('main')
        if main:
            html = main.inner_html()[:3000]
            print(f"Main content HTML (first 3000 chars):\n{html}")
    
    print("\nWaiting 5 seconds...")
    browser.page.wait_for_timeout(5000)
    
finally:
    browser.close()
    print("Done!")
