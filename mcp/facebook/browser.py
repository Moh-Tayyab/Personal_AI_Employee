"""
Facebook Browser Automation - Playwright-based Facebook automation

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    from mcp.facebook.browser import FacebookBrowserSync
    browser = FacebookBrowserSync()
    browser.login(email, password)
    browser.create_post("Hello World!")
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class FacebookBrowser:
    """Browser automation for Facebook operations."""

    def __init__(self, session_path: str = "./vault/secrets/facebook_session"):
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
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
            window.chrome = { runtime: {} };
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
        """Login to Facebook."""
        if not self.page:
            await self.start(headless=False)

        try:
            # Navigate to login page
            await self.page.goto("https://www.facebook.com", wait_until="networkidle", timeout=30000)
            await self.page.wait_for_timeout(3000)

            # Check if already logged in
            if "facebook.com" in self.page.url and "login" not in self.page.url:
                # Check for home indicator
                home_indicator = await self.page.query_selector('[aria-label="Home"], a[href*="/home"]')
                if home_indicator:
                    await self.save_storage_state()
                    return {"status": "already_logged_in", "message": "Already logged into Facebook"}

            # Accept cookies if prompted
            try:
                accept_btn = await self.page.wait_for_selector('button[data-cookiebanner="accept"], button:has-text("Accept"), button:has-text("Allow")', timeout=5000)
                if accept_btn:
                    await accept_btn.click()
                    await self.page.wait_for_timeout(1000)
            except:
                pass

            # Fill email
            email_field = None
            for selector in ['input[id="email"]', 'input[name="email"]', 'input[type="email"]', 'input[autocomplete="email"]']:
                try:
                    email_field = await self.page.wait_for_selector(selector, timeout=3000)
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
            for selector in ['input[id="pass"]', 'input[name="pass"]', 'input[type="password"]']:
                try:
                    password_field = await self.page.wait_for_selector(selector, timeout=3000)
                    break
                except:
                    continue

            if not password_field:
                return {"status": "login_failed", "error": "Password field not found"}

            await password_field.click()
            await self.page.wait_for_timeout(500)
            await password_field.fill(password)
            await self.page.wait_for_timeout(1000)

            # Click login button
            login_button = None
            for selector in ['button[name="login"]', 'button[type="submit"]', 'input[type="submit"][value*="Log"]']:
                try:
                    login_button = await self.page.wait_for_selector(selector, timeout=3000)
                    break
                except:
                    continue

            if not login_button:
                return {"status": "login_failed", "error": "Login button not found"}

            await login_button.click()
            await self.page.wait_for_timeout(5000)

            # Wait for navigation
            try:
                await self.page.wait_for_url("**/*facebook.com/**", timeout=30000)
            except:
                pass

            await self.page.wait_for_timeout(5000)

            # Check for login success indicators
            current_url = self.page.url

            # Check for 2FA or security checkpoint
            if "checkpoint" in current_url or "two-factor" in current_url.lower():
                return {
                    "status": "needs_verification",
                    "message": "Two-factor authentication or security checkpoint required. Please complete manually.",
                    "url": current_url
                }

            # Check if logged in
            home_indicator = await self.page.query_selector('[aria-label="Home"], a[href*="/home"], div[role="navigation"]')
            if home_indicator or ("facebook.com" in current_url and "login" not in current_url):
                await self.save_storage_state()
                return {"status": "logged_in", "message": "Successfully logged into Facebook", "url": current_url}

            return {"status": "login_failed", "error": "Could not verify login success", "url": current_url}

        except Exception as e:
            return {"status": "login_failed", "error": str(e)}

    async def check_session(self) -> Dict[str, Any]:
        """Check if session is valid."""
        if not self.page:
            await self.start()

        try:
            # Check if we have storage state
            storage_file = self.session_path / "storage.json"
            if not storage_file.exists():
                return {"status": "not_authenticated", "message": "No session file found"}

            # Navigate to Facebook
            await self.page.goto("https://www.facebook.com", wait_until="domcontentloaded", timeout=30000)
            await self.page.wait_for_timeout(5000)

            # Check if redirected to login
            current_url = self.page.url
            if "login" in current_url or "login.php" in current_url:
                return {"status": "not_authenticated", "message": "Session expired"}

            # Try to find profile indicator
            try:
                profile_menu = await self.page.wait_for_selector(
                    '[aria-label="Account"], [aria-label="Your profile"], div[aria-label*="Account"]',
                    timeout=5000
                )
                if profile_menu:
                    return {
                        "status": "authenticated",
                        "message": "Facebook session is valid"
                    }
            except:
                pass

            # Check if we're on the main feed
            feed_indicator = await self.page.query_selector('div[role="feed"], div[data-pagelet="FeedSection"]')
            if feed_indicator:
                return {
                    "status": "authenticated",
                    "message": "Facebook session is valid"
                }

            return {"status": "not_authenticated", "message": "Could not verify session"}

        except Exception as e:
            return {"status": "not_authenticated", "error": str(e)}

    async def create_post(self, content: str, page_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a Facebook post."""
        if not self.page:
            await self.start()

        try:
            # Navigate to appropriate page
            if page_id:
                url = f"https://www.facebook.com/{page_id}"
            else:
                url = "https://www.facebook.com"

            await self.page.goto(url, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)

            # Check if logged in
            session_status = await self.check_session()
            if session_status.get("status") != "authenticated":
                return {
                    "status": "not_authenticated",
                    "message": "Please login first using the login method"
                }

            # Click on "Create post" or find the post input
            post_trigger = None
            selectors = [
                'div[role="button"]:has-text("Create a post")',
                'span:has-text("Create a post")',
                'div[aria-label="Create a post"]',
                'div[data-pagelet="FeedUnit_0"] div[role="button"]',
                'div[role="textbox"][aria-label*="on your mind"]',
            ]

            for selector in selectors:
                try:
                    post_trigger = await self.page.wait_for_selector(selector, timeout=3000)
                    break
                except:
                    continue

            if not post_trigger:
                # Try to find the main post input directly
                post_trigger = await self.page.query_selector('div[role="textbox"]')

            if post_trigger:
                await post_trigger.click()
                await self.page.wait_for_timeout(2000)
            else:
                return {"status": "post_failed", "error": "Could not find post creation area"}

            # Find the text editor
            text_editor = None
            editor_selectors = [
                'div[role="textbox"][contenteditable="true"]',
                'div[contenteditable="true"][aria-label*="mind"]',
                'div[contenteditable="true"][data-lexical-editor="true"]',
            ]

            for selector in editor_selectors:
                try:
                    text_editor = await self.page.wait_for_selector(selector, timeout=3000)
                    break
                except:
                    continue

            if not text_editor:
                return {"status": "post_failed", "error": "Could not find text editor"}

            # Clear and fill content
            await text_editor.click()
            await self.page.wait_for_timeout(500)

            # Type the content
            await self.page.keyboard.type(content, delay=30)
            await self.page.wait_for_timeout(2000)

            # Click the Post button
            post_button = None
            post_selectors = [
                'div[role="button"]:has-text("Post")',
                'button:has-text("Post")',
                'span:has-text("Post")',
                'div[aria-label="Post"]',
            ]

            for selector in post_selectors:
                try:
                    # Wait a bit for the button to appear
                    await self.page.wait_for_timeout(1000)
                    post_button = await self.page.wait_for_selector(selector, timeout=3000)
                    if post_button:
                        break
                except:
                    continue

            if post_button:
                await post_button.click()
                await self.page.wait_for_timeout(5000)

                # Check if post was successful
                await self.page.wait_for_timeout(3000)
                return {"status": "posted", "message": "Successfully posted to Facebook"}
            else:
                return {"status": "post_failed", "error": "Could not find Post button"}

        except Exception as e:
            return {"status": "post_failed", "error": str(e)}

    async def get_feed(self, count: int = 10) -> Dict[str, Any]:
        """Get recent feed posts."""
        if not self.page:
            await self.start()

        try:
            await self.page.goto("https://www.facebook.com", wait_until="domcontentloaded")
            await self.page.wait_for_timeout(5000)

            posts = []
            feed_items = await self.page.query_selector_all('div[role="article"]')

            for item in feed_items[:count]:
                try:
                    text_content = await item.inner_text()
                    posts.append({"content": text_content[:500]})
                except:
                    continue

            return {"status": "success", "posts": posts}

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


class FacebookBrowserSync:
    """Synchronous wrapper for FacebookBrowser."""

    def __init__(self, session_path: str = "./vault/secrets/facebook_session"):
        self.browser = FacebookBrowser(session_path)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def start(self, headless: bool = True):
        return self.loop.run_until_complete(self.browser.start(headless))

    def login(self, email: str, password: str) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.login(email, password))

    def check_session(self) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.check_session())

    def create_post(self, content: str, page_id: Optional[str] = None) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.create_post(content, page_id))

    def get_feed(self, count: int = 10) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.get_feed(count))

    def close(self):
        return self.loop.run_until_complete(self.browser.close())

    def save_storage_state(self):
        return self.loop.run_until_complete(self.browser.save_storage_state())