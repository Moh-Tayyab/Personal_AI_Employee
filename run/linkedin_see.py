#!/usr/bin/env python3
"""Debug LinkedIn page"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.linkedin.browser_sync import LinkedInBrowser

browser = LinkedInBrowser("./vault/secrets/linkedin_session")

try:
    print("Starting browser and navigating to feed...")
    browser.start(headless=False)
    
    print("Going to LinkedIn feed...")
    browser.page.goto("https://www.linkedin.com/feed", wait_until="domcontentloaded")
    browser.page.wait_for_timeout(10000)
    
    print(f"Current URL: {browser.page.url}")
    print(f"Page title: {browser.page.title()}")
    
    # Take screenshot
    browser.page.screenshot(path="linkedin_debug.png", full_page=True)
    print("Screenshot saved to linkedin_debug.png")
    
    # Get all text on page
    print("\n--- Page Content (first 2000 chars) ---")
    content = browser.page.content()
    print(content[:2000])
    
    # Find all buttons with text
    print("\n--- Buttons on page ---")
    buttons = browser.page.query_selector_all("button")
    for i, btn in enumerate(buttons[:30]):
        try:
            text = btn.inner_text().strip()
            if text:
                print(f"  {i}: '{text[:60]}'")
        except:
            pass
    
    # Find all editable areas
    print("\n--- Editable areas ---")
    editables = browser.page.query_selector_all('div[contenteditable="true"]')
    print(f"Found {len(editables)} editable divs")
    
    # Find share box
    print("\n--- Share/Post areas ---")
    share_boxes = browser.page.query_selector_all('div[class*="share"]')
    print(f"Found {len(share_boxes)} share-related divs")
    for i, box in enumerate(share_boxes[:10]):
        try:
            text = box.inner_text().strip()[:50]
            print(f"  {i}: '{text}'")
        except:
            pass
    
    print("\nWaiting 10 seconds for you to see the page...")
    browser.page.wait_for_timeout(10000)
    
finally:
    browser.close()
    print("Done!")
