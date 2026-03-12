"""
Instagram Browser Automation - Playwright-based Instagram automation

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    from mcp.instagram.browser import InstagramBrowserSync
    browser = InstagramBrowserSync()
    browser.login(username, password)
    browser.create_post("Hello World!", image_path="./image.jpg")
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class InstagramBrowser:
    """Browser automation for Instagram operations."""

    def __init__(self, session_path: str = "./vault/secrets/instagram_session"):
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

        # Load or create context - Instagram mobile viewport
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

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login to Instagram."""
        if not self.page:
            await self.start(headless=False)

        try:
            # Navigate to login page
            await self.page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle", timeout=30000)
            await self.page.wait_for_timeout(3000)

            # Check if already logged in
            if "instagram.com" in self.page.url and "login" not in self.page.url and "accounts" not in self.page.url:
                await self.save_storage_state()
                return {"status": "already_logged_in", "message": "Already logged into Instagram"}

            # Accept cookies if prompted
            try:
                accept_btn = await self.page.wait_for_selector(
                    'button:has-text("Accept"), button:has-text("Allow"), button:has-text("Accept All")',
                    timeout=5000
                )
                if accept_btn:
                    await accept_btn.click()
                    await self.page.wait_for_timeout(1000)
            except:
                pass

            # Fill username
            username_field = None
            for selector in ['input[name="username"]', 'input[type="text"]', 'input[aria-label*="Phone number, username, or email"]']:
                try:
                    username_field = await self.page.wait_for_selector(selector, timeout=5000)
                    break
                except:
                    continue

            if not username_field:
                return {"status": "login_failed", "error": "Username field not found"}

            await username_field.click()
            await self.page.wait_for_timeout(500)
            await username_field.fill(username)
            await self.page.wait_for_timeout(1000)

            # Fill password
            password_field = None
            for selector in ['input[name="password"]', 'input[type="password"]', 'input[aria-label*="Password"]']:
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

            # Click login button
            login_button = None
            for selector in ['button[type="submit"]', 'button:has-text("Log in")', 'div[role="button"]:has-text("Log in")']:
                try:
                    login_button = await self.page.wait_for_selector(selector, timeout=5000)
                    break
                except:
                    continue

            if not login_button:
                return {"status": "login_failed", "error": "Login button not found"}

            await login_button.click()
            await self.page.wait_for_timeout(5000)

            # Wait for navigation
            try:
                await self.page.wait_for_url("**/*instagram.com/**", timeout=30000)
            except:
                pass

            await self.page.wait_for_timeout(5000)

            # Check for 2FA or security checkpoint
            current_url = self.page.url
            if "challenge" in current_url or "two_factor" in current_url.lower():
                return {
                    "status": "needs_verification",
                    "message": "Two-factor authentication or security checkpoint required. Please complete manually.",
                    "url": current_url
                }

            # Handle "Save Info" popup
            try:
                not_now_btn = await self.page.wait_for_selector('button:has-text("Not now"), div[role="button"]:has-text("Not now")', timeout=5000)
                if not_now_btn:
                    await not_now_btn.click()
                    await self.page.wait_for_timeout(2000)
            except:
                pass

            # Handle "Turn on Notifications" popup
            try:
                not_now_btn = await self.page.wait_for_selector('button:has-text("Not Now")', timeout=5000)
                if not_now_btn:
                    await not_now_btn.click()
                    await self.page.wait_for_timeout(2000)
            except:
                pass

            # Check if logged in
            home_indicator = await self.page.query_selector('svg[aria-label="Home"], a[href="/"], nav')
            if home_indicator or ("instagram.com" in current_url and "login" not in current_url and "accounts" not in current_url):
                await self.save_storage_state()
                return {"status": "logged_in", "message": "Successfully logged into Instagram", "url": current_url}

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

            # Navigate to Instagram
            await self.page.goto("https://www.instagram.com", wait_until="domcontentloaded", timeout=30000)
            await self.page.wait_for_timeout(5000)

            # Check if redirected to login
            current_url = self.page.url
            if "login" in current_url or "accounts" in current_url:
                return {"status": "not_authenticated", "message": "Session expired"}

            # Try to find profile indicator
            try:
                profile_link = await self.page.wait_for_selector('a[href*="/accounts/"], svg[aria-label="Profile"]', timeout=5000)
                if profile_link:
                    # Get username from URL
                    username = current_url.rstrip('/').split('/')[-1] if '/' in current_url else "user"
                    return {
                        "status": "authenticated",
                        "message": "Instagram session is valid",
                        "username": username
                    }
            except:
                pass

            # Check if we're on the main feed
            feed_indicator = await self.page.query_selector('svg[aria-label="Home"], section[role="main"]')
            if feed_indicator:
                return {
                    "status": "authenticated",
                    "message": "Instagram session is valid"
                }

            return {"status": "not_authenticated", "message": "Could not verify session"}

        except Exception as e:
            return {"status": "not_authenticated", "error": str(e)}

    async def create_post(self, caption: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """Create an Instagram post (requires image)."""
        if not self.page:
            await self.start()

        try:
            # Check session
            session_status = await self.check_session()
            if session_status.get("status") != "authenticated":
                return {
                    "status": "not_authenticated",
                    "message": "Please login first using the login method"
                }

            # Navigate to Instagram home
            await self.page.goto("https://www.instagram.com", wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)

            # Click create (+) button
            create_button = None
            for selector in [
                'svg[aria-label="New post"]',
                'a[href="/create/"]',
                'div[role="button"]:has(svg[aria-label="New post"])',
                'div[style*="cursor: pointer"]:has(svg)',
            ]:
                try:
                    create_button = await self.page.wait_for_selector(selector, timeout=3000)
                    break
                except:
                    continue

            if not create_button:
                return {"status": "post_failed", "error": "Could not find create post button"}

            await create_button.click()
            await self.page.wait_for_timeout(2000)

            # If image is provided, upload it
            if image_path:
                media_file = Path(image_path)
                if not media_file.exists():
                    return {"status": "post_failed", "error": f"Image file not found: {image_path}"}

                # Find file input
                file_input = await self.page.query_selector('input[type="file"][accept*="image"], input[type="file"][accept*="video"]')
                if not file_input:
                    # Try clicking to open file dialog first
                    file_buttons = await self.page.query_selector_all('button, div[role="button"]')
                    for btn in file_buttons:
                        text = await btn.inner_text()
                        if "Select from computer" in text or "Browse" in text:
                            await btn.click()
                            await self.page.wait_for_timeout(1000)
                            break

                    file_input = await self.page.query_selector('input[type="file"]')

                if file_input:
                    await file_input.set_input_files(str(media_file.absolute()))
                    await self.page.wait_for_timeout(5000)
                else:
                    return {"status": "post_failed", "error": "Could not find file upload input"}

                # Click next after upload
                next_button = await self.page.wait_for_selector('button:has-text("Next"), div[role="button"]:has-text("Next")', timeout=10000)
                if next_button:
                    await next_button.click()
                    await self.page.wait_for_timeout(3000)

                # Click next again (filter step)
                next_button = await self.page.query_selector('button:has-text("Next"), div[role="button"]:has-text("Next")')
                if next_button:
                    await next_button.click()
                    await self.page.wait_for_timeout(3000)

            # Enter caption
            caption_field = None
            for selector in [
                'div[contenteditable="true"][aria-label*="Write a caption"]',
                'textarea[aria-label*="caption"]',
                'div[contenteditable="true"]',
            ]:
                try:
                    caption_field = await self.page.wait_for_selector(selector, timeout=3000)
                    break
                except:
                    continue

            if caption_field and caption:
                await caption_field.click()
                await self.page.wait_for_timeout(500)
                await self.page.keyboard.type(caption, delay=30)
                await self.page.wait_for_timeout(2000)

            # Click Share button
            share_button = None
            for selector in ['button:has-text("Share")', 'div[role="button"]:has-text("Share")']:
                try:
                    share_button = await self.page.wait_for_selector(selector, timeout=3000)
                    break
                except:
                    continue

            if share_button:
                await share_button.click()
                await self.page.wait_for_timeout(5000)

                # Check for success
                success_indicator = await self.page.query_selector('svg[aria-label="Home"], div[role="dialog"]:has-text("Your post has been shared")')
                if success_indicator or "instagram.com" in self.page.url:
                    return {"status": "posted", "message": "Successfully posted to Instagram"}
                else:
                    return {"status": "posted", "message": "Post submitted (verify manually)"}
            else:
                return {"status": "post_failed", "error": "Could not find Share button"}

        except Exception as e:
            return {"status": "post_failed", "error": str(e)}

    async def get_feed(self, count: int = 10) -> Dict[str, Any]:
        """Get recent feed posts."""
        if not self.page:
            await self.start()

        try:
            await self.page.goto("https://www.instagram.com", wait_until="domcontentloaded")
            await self.page.wait_for_timeout(5000)

            posts = []
            feed_items = await self.page.query_selector_all('article')

            for item in feed_items[:count]:
                try:
                    # Get caption/text
                    text_content = await item.inner_text()
                    # Get image URL
                    img = await item.query_selector('img')
                    img_url = await img.get_attribute('src') if img else None

                    posts.append({
                        "content": text_content[:500] if text_content else "",
                        "image_url": img_url
                    })
                except:
                    continue

            return {"status": "success", "posts": posts}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_profile(self) -> Dict[str, Any]:
        """Get current user's profile information."""
        if not self.page:
            await self.start()

        try:
            # Navigate to profile
            await self.page.goto("https://www.instagram.com/accounts/edit/", wait_until="networkidle")
            await self.page.wait_for_timeout(3000)

            # Try to get username from URL or page
            current_url = self.page.url
            username = current_url.rstrip('/').split('/')[-1] if '/' in current_url else "user"

            # Get profile info from page
            name_element = await self.page.query_selector('input[name="first_name"]')
            name = await name_element.get_attribute('value') if name_element else username

            return {
                "status": "success",
                "username": username,
                "name": name or username,
                "profile_url": f"https://www.instagram.com/{username}/"
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


class InstagramBrowserSync:
    """Synchronous wrapper for InstagramBrowser."""

    def __init__(self, session_path: str = "./vault/secrets/instagram_session"):
        self.browser = InstagramBrowser(session_path)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def start(self, headless: bool = True):
        return self.loop.run_until_complete(self.browser.start(headless))

    def login(self, username: str, password: str) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.login(username, password))

    def check_session(self) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.check_session())

    def create_post(self, caption: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.create_post(caption, image_path))

    def get_feed(self, count: int = 10) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.get_feed(count))

    def get_profile(self) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.get_profile())

    def close(self):
        return self.loop.run_until_complete(self.browser.close())

    def save_storage_state(self):
        return self.loop.run_until_complete(self.browser.save_storage_state())