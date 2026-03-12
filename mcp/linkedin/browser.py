"""
LinkedIn Browser Automation - Playwright-based LinkedIn automation
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class LinkedInBrowser:
    """Browser automation for LinkedIn operations."""

    def __init__(self, session_path: str = "./vault/secrets/linkedin_session"):
        self.session_path = Path(session_path)
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._playwright = None

    async def start(self, headless: bool = True):
        """Start the browser with persisted session."""
        self._playwright = await async_playwright().start()
        
        # Create session directory if needed
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Launch browser
        self.browser = await self._playwright.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )

        # Load or create context
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            storage_state=self._get_storage_state(),
        )

        self.page = await self.context.new_page()
        
        # Add stealth scripts
        await self._add_stealth_scripts()

    async def _add_stealth_scripts(self):
        """Add scripts to avoid detection."""
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US'] });
        """)

    def _get_storage_state(self) -> Optional[Dict]:
        """Load storage state from session file."""
        storage_file = self.session_path / "storage.json"
        if storage_file.exists():
            try:
                with open(storage_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None

    async def save_storage_state(self):
        """Save current storage state."""
        if self.context:
            state = await self.context.storage_state()
            storage_file = self.session_path / "storage.json"
            with open(storage_file, "w") as f:
                json.dump(state, f, indent=2)

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login to LinkedIn."""
        if not self.page:
            await self.start(headless=False)

        try:
            # Navigate to login page
            await self.page.goto("https://www.linkedin.com/login", wait_until="networkidle", timeout=30000)
            await self.page.wait_for_timeout(3000)

            # Check if already logged in
            if "feed" in self.page.url or "/in/" in self.page.url:
                await self.save_storage_state()
                return {"status": "already_logged_in", "profile_url": self.page.url}

            # Fill email - try multiple selectors
            email_field = None
            for selector in ['input[id="username"]', 'input[name="session_key_or_email"]', 'input[type="email"]']:
                try:
                    email_field = await self.page.wait_for_selector(selector, timeout=5000)
                    break
                except:
                    continue
            
            if not email_field:
                return {"status": "login_failed", "error": "Email field not found"}
                
            await email_field.click()
            await self.page.wait_for_timeout(500)
            await email_field.fill(email)
            await self.page.wait_for_timeout(1000)

            # Fill password
            password_field = None
            for selector in ['input[type="password"]', 'input[name="session_password"]']:
                try:
                    password_field = await self.page.wait_for_selector(selector, timeout=5000)
                    break
                except:
                    continue
            
            if not password_field:
                return {"status": "login_failed", "error": "Password field not found"}
                
            await password_field.click()
            await self.page.wait_for_timeout(500)
            await password_field.fill(password)
            await self.page.wait_for_timeout(1000)

            # Click sign in button - try multiple selectors
            sign_in_button = None
            for selector in ['button[type="submit"]', 'button[data-litms-control*="submit"]', 'input[type="submit"]']:
                try:
                    sign_in_button = await self.page.wait_for_selector(selector, timeout=5000)
                    break
                except:
                    continue
            
            if not sign_in_button:
                return {"status": "login_failed", "error": "Sign in button not found"}
                
            # Use keyboard Enter instead of click for better reliability
            await password_field.press("Enter")
            await self.page.wait_for_timeout(2000)

            # Wait for navigation with longer timeout
            try:
                await self.page.wait_for_url("https://www.linkedin.com/feed/*", timeout=45000)
            except:
                # Check if we're on any LinkedIn page that indicates success
                if "linkedin.com" in self.page.url and "login" not in self.page.url:
                    pass  # Likely successful
                else:
                    return {"status": "login_failed", "error": "Navigation timeout - may need 2FA verification"}

            await self.page.wait_for_timeout(5000)

            # Save session
            await self.save_storage_state()

            return {"status": "logged_in", "profile_url": self.page.url}

        except Exception as e:
            return {"status": "login_failed", "error": str(e)}

    async def check_session(self) -> Dict[str, Any]:
        """Check if session is valid."""
        if not self.page:
            await self.start()

        try:
            # First check if we have storage state
            storage_file = self.session_path / "storage.json"
            if not storage_file.exists():
                return {"status": "not_authenticated", "message": "No session file found"}

            # Navigate with longer timeout and more lenient wait
            await self.page.goto("https://www.linkedin.com/feed", wait_until="domcontentloaded", timeout=30000)
            await self.page.wait_for_timeout(5000)

            # Check if redirected to login
            if "login" in self.page.url or "checkpoint" in self.page.url:
                return {"status": "not_authenticated", "message": "Session expired or needs verification"}

            # Try to get profile name from nav
            try:
                profile_element = await self.page.wait_for_selector(
                    'img[alt*="Profile"], img[data-delayed-url*="/in/"]',
                    timeout=5000
                )
                profile_name = await profile_element.get_attribute("alt")
                
                # Get profile URL
                profile_link = await self.page.query_selector('a[href*="/in/"]')
                profile_url = await profile_link.get_attribute("href") if profile_link else None

                return {
                    "status": "authenticated",
                    "profile_name": profile_name or "Unknown",
                    "profile_url": profile_url or "https://linkedin.com/in/unknown"
                }
            except Exception:
                # If we're on feed page, we're authenticated
                if "feed" in self.page.url:
                    return {"status": "authenticated", "profile_name": "User", "profile_url": "https://linkedin.com/in/user"}
                return {"status": "not_authenticated", "message": "Could not verify profile"}

        except Exception as e:
            return {"status": "not_authenticated", "error": str(e)}

    async def create_post(self, content: str, media_path: Optional[str] = None) -> Dict[str, Any]:
        """Create a LinkedIn post."""
        if not self.page:
            await self.start()

        try:
            # Navigate to feed
            await self.page.goto("https://www.linkedin.com/feed", wait_until="domcontentloaded")
            await self.page.wait_for_timeout(5000)

            # Click on the post creation box - try multiple selectors
            post_trigger = None
            selectors = [
                'button:has-text("Start a post")',
                'div[role="button"]:has-text("Start a post")',
                'button:has-text("Start a post") img',
                'div[class*="share-box-feed-entry"]',
                '[data-control-name="share-box-feed-entry"]',
            ]
            
            for selector in selectors:
                try:
                    post_trigger = await self.page.wait_for_selector(selector, timeout=3000)
                    break
                except:
                    continue
            
            if not post_trigger:
                # Try to find by aria-label
                post_trigger = await self.page.query_selector('[aria-label*="Create a post"]')
            
            if post_trigger:
                await post_trigger.click()
                await self.page.wait_for_timeout(2000)
            else:
                return {"status": "post_failed", "error": "Could not find post creation button"}

            # Find the text editor and fill content
            text_editor = None
            editor_selectors = [
                'div[contenteditable="true"][role="textbox"]',
                'div[contenteditable="true"]',
                '[data-placeholder*="What do you"]',
            ]
            
            for selector in editor_selectors:
                try:
                    text_editor = await self.page.wait_for_selector(selector, timeout=3000)
                    break
                except:
                    continue
            
            if not text_editor:
                return {"status": "post_failed", "error": "Could not find text editor"}
            
            # Clear and fill using keyboard for better reliability
            await text_editor.click()
            await self.page.wait_for_timeout(500)
            
            # Select all and delete
            await self.page.keyboard.press("Control+A")
            await self.page.wait_for_timeout(200)
            await self.page.keyboard.press("Delete")
            await self.page.wait_for_timeout(200)
            
            # Type content in chunks to avoid issues
            await self.page.keyboard.type(content, delay=30)
            await self.page.wait_for_timeout(2000)

            # Add media if provided
            if media_path:
                media_file = Path(media_path)
                if media_file.exists():
                    # Click media button first
                    media_buttons = await self.page.query_selector_all('button[aria-label*="Photo"], button[aria-label*="Media"], button[title*="Photo"]')
                    if media_buttons:
                        await media_buttons[0].click()
                        await self.page.wait_for_timeout(1000)
                    
                    # Upload file
                    file_input = await self.page.query_selector('input[type="file"]')
                    if file_input:
                        await file_input.set_input_files(str(media_file.absolute()))
                        await self.page.wait_for_timeout(3000)

            # Click post button - try multiple selectors
            post_button = None
            post_selectors = [
                'button:has-text("Post")',
                'button[data-control-name*="post"]',
                'button[class*="share-box-submit"]',
            ]
            
            for selector in post_selectors:
                try:
                    post_button = await self.page.wait_for_selector(selector, timeout=3000)
                    break
                except:
                    continue
            
            if post_button:
                await post_button.click()
                await self.page.wait_for_timeout(5000)
                
                # Check if post was successful
                if "feed" in self.page.url:
                    return {"status": "posted", "message": "Successfully posted to LinkedIn"}
                else:
                    return {"status": "posted", "message": "Post submitted"}
            else:
                return {"status": "post_failed", "error": "Could not find Post button"}

        except Exception as e:
            return {"status": "post_failed", "error": str(e)}

    async def get_profile(self) -> Dict[str, Any]:
        """Get current user's profile information."""
        if not self.page:
            await self.start()

        try:
            # Navigate to profile
            await self.page.goto("https://www.linkedin.com/in/me", wait_until="networkidle")
            await self.page.wait_for_timeout(2000)

            # Get name
            name_element = await self.page.query_selector('h1')
            name = await name_element.inner_text() if name_element else "Unknown"

            # Get headline
            headline_element = await self.page.query_selector('div[data-view-name="profile-component-entity"] div:nth-child(2)')
            headline = await headline_element.inner_text() if headline_element else ""

            # Get profile URL
            profile_url = self.page.url

            return {
                "status": "success",
                "name": name.strip(),
                "headline": headline.strip(),
                "profile_url": profile_url
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def close(self):
        """Close browser."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Sync wrapper for use in synchronous context
class LinkedInBrowserSync:
    """Synchronous wrapper for LinkedInBrowser."""

    def __init__(self, session_path: str = "./vault/secrets/linkedin_session"):
        self.browser = LinkedInBrowser(session_path)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def start(self, headless: bool = True):
        return self.loop.run_until_complete(self.browser.start(headless))

    def login(self, email: str, password: str) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.login(email, password))

    def check_session(self) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.check_session())

    def create_post(self, content: str, media_path: Optional[str] = None) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.create_post(content, media_path))

    def get_profile(self) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.get_profile())

    def close(self):
        return self.loop.run_until_complete(self.browser.close())

    def save_storage_state(self):
        return self.loop.run_until_complete(self.browser.save_storage_state())
