"""
Twitter/X Browser Automation - Playwright-based Twitter automation

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    from mcp.twitter.browser import TwitterBrowserSync
    browser = TwitterBrowserSync()
    browser.login(username, password)
    browser.post_tweet("Hello World!")
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class TwitterBrowser:
    """Browser automation for Twitter/X operations."""

    def __init__(self, session_path: str = "./vault/secrets/twitter_session"):
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

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login to Twitter/X."""
        if not self.page:
            await self.start(headless=False)

        try:
            # Navigate to login page
            await self.page.goto("https://twitter.com/i/flow/login", wait_until="networkidle", timeout=30000)
            await self.page.wait_for_timeout(3000)

            # Check if already logged in
            if "twitter.com/home" in self.page.url or "x.com/home" in self.page.url:
                await self.save_storage_state()
                return {"status": "already_logged_in", "message": "Already logged into Twitter/X"}

            # Wait for and fill username
            username_field = None
            for selector in [
                'input[autocomplete="username"]',
                'input[name="text"]',
                'input[type="text"]',
            ]:
                try:
                    username_field = await self.page.wait_for_selector(selector, timeout=10000)
                    break
                except:
                    continue

            if not username_field:
                return {"status": "login_failed", "error": "Username field not found"}

            await username_field.click()
            await self.page.wait_for_timeout(500)
            await username_field.fill(username)
            await self.page.wait_for_timeout(1000)

            # Click next button
            next_button = None
            for selector in [
                'button:has-text("Next")',
                'div[role="button"]:has-text("Next")',
                'span:has-text("Next")',
            ]:
                try:
                    next_button = await self.page.wait_for_selector(selector, timeout=5000)
                    break
                except:
                    continue

            if next_button:
                await next_button.click()
                await self.page.wait_for_timeout(3000)

            await self.page.wait_for_timeout(3000)

            # Check for unusual activity / phone verification
            unusual_activity = await self.page.query_selector('input[data-testid="ocfEnterTextTextInput"], input[name="text"]:not([autocomplete="username"])')
            if unusual_activity:
                return {
                    "status": "needs_verification",
                    "message": "Twitter requires additional verification (phone/email). Please complete manually or provide verification code.",
                    "url": self.page.url
                }

            # Fill password - try more selectors and wait for page transition
            password_field = None
            
            # First, wait for the password field to appear (Twitter loads it dynamically)
            try:
                await self.page.wait_for_selector('input[type="password"]', timeout=15000)
            except:
                pass
            
            for selector in [
                'input[name="password"]',
                'input[type="password"]',
                'input[autocomplete="current-password"]',
                'input[data-testid="LoginForm_Login_Password"]',
            ]:
                try:
                    password_field = await self.page.wait_for_selector(selector, timeout=5000)
                    if password_field:
                        break
                except:
                    continue

            if not password_field:
                # Check if we were redirected to verification page
                current_url = self.page.url
                if "challenge" in current_url or "verification" in current_url:
                    return {
                        "status": "needs_verification",
                        "message": "Twitter security verification required. Complete manually.",
                        "url": current_url
                    }
                return {"status": "login_failed", "error": "Password field not found. Twitter may have changed login flow.", "url": current_url}

            await password_field.click()
            await self.page.wait_for_timeout(500)
            await password_field.fill(password)
            await self.page.wait_for_timeout(1000)

            # Click login button
            login_button = None
            for selector in [
                'button[data-testid="LoginForm_Login_Button"]',
                'button:has-text("Log in")',
                'div[role="button"]:has-text("Log in")',
            ]:
                try:
                    login_button = await self.page.wait_for_selector(selector, timeout=5000)
                    break
                except:
                    continue

            if not login_button:
                return {"status": "login_failed", "error": "Login button not found"}

            await login_button.click()
            await self.page.wait_for_timeout(5000)

            # Wait for navigation to home
            try:
                await self.page.wait_for_url("**/home**", timeout=30000)
            except:
                pass

            await self.page.wait_for_timeout(5000)

            # Check if logged in
            current_url = self.page.url
            if "home" in current_url:
                await self.save_storage_state()
                return {"status": "logged_in", "message": "Successfully logged into Twitter/X", "url": current_url}

            # Check for 2FA
            if "challenge" in current_url or "login_challenge" in current_url:
                return {
                    "status": "needs_verification",
                    "message": "Two-factor authentication required. Please complete manually.",
                    "url": current_url
                }

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

            # Navigate to Twitter
            await self.page.goto("https://twitter.com/home", wait_until="domcontentloaded", timeout=30000)
            await self.page.wait_for_timeout(5000)

            # Check if redirected to login
            current_url = self.page.url
            if "login" in current_url or "i/flow" in current_url:
                return {"status": "not_authenticated", "message": "Session expired"}

            # Try to find home timeline
            try:
                home_indicator = await self.page.wait_for_selector(
                    'div[data-testid="primaryColumn"], div[role="main"], a[data-testid="AppTabBar_Home_Link"]',
                    timeout=10000
                )
                if home_indicator:
                    # Get username from profile link
                    profile_link = await self.page.query_selector('a[data-testid="AppTabBar_Profile_Link"]')
                    username = "user"
                    if profile_link:
                        href = await profile_link.get_attribute('href')
                        if href:
                            username = href.rstrip('/').split('/')[-1]

                    return {
                        "status": "authenticated",
                        "message": "Twitter/X session is valid",
                        "username": username
                    }
            except:
                pass

            return {"status": "not_authenticated", "message": "Could not verify session"}

        except Exception as e:
            return {"status": "not_authenticated", "error": str(e)}

    async def post_tweet(self, content: str) -> Dict[str, Any]:
        """Post a tweet."""
        if not self.page:
            await self.start()

        if len(content) > 280:
            return {"error": "Tweet exceeds 280 characters"}

        try:
            # Check session
            session_status = await self.check_session()
            if session_status.get("status") != "authenticated":
                return {
                    "status": "not_authenticated",
                    "message": "Please login first using the login method"
                }

            # Navigate to home
            await self.page.goto("https://twitter.com/home", wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)

            # Click tweet compose button
            tweet_button = None
            for selector in [
                'a[data-testid="SideNav_NewTweet_Button"]',
                'a[href="/compose/tweet"]',
                'div[role="button"][data-testid="SideNav_NewTweet_Button"]',
            ]:
                try:
                    tweet_button = await self.page.wait_for_selector(selector, timeout=5000)
                    break
                except:
                    continue

            if tweet_button:
                await tweet_button.click()
                await self.page.wait_for_timeout(2000)

            # Find tweet text area
            tweet_textarea = None
            for selector in [
                'div[data-testid="tweetTextarea_0"]',
                'div[contenteditable="true"][data-testid="tweetTextarea_0"]',
                'div[role="textbox"][data-testid="tweetTextarea_0"]',
            ]:
                try:
                    tweet_textarea = await self.page.wait_for_selector(selector, timeout=5000)
                    break
                except:
                    continue

            if not tweet_textarea:
                return {"status": "tweet_failed", "error": "Could not find tweet text area"}

            # Type the tweet
            await tweet_textarea.click()
            await self.page.wait_for_timeout(500)
            await self.page.keyboard.type(content, delay=30)
            await self.page.wait_for_timeout(2000)

            # Click the tweet/post button
            post_button = None
            for selector in [
                'button[data-testid="tweetButton"]',
                'button[data-testid="tweetButtonInline"]',
                'div[role="button"][data-testid="tweetButton"]',
            ]:
                try:
                    post_button = await self.page.wait_for_selector(selector, timeout=5000)
                    break
                except:
                    continue

            if not post_button:
                return {"status": "tweet_failed", "error": "Could not find post button"}

            await post_button.click()
            await self.page.wait_for_timeout(5000)

            # Check for success
            # After posting, we should see the tweet or return to home
            await self.page.wait_for_timeout(3000)
            return {"status": "posted", "message": "Successfully posted tweet", "content": content}

        except Exception as e:
            return {"status": "tweet_failed", "error": str(e)}

    async def get_timeline(self, count: int = 10) -> Dict[str, Any]:
        """Get recent tweets from timeline."""
        if not self.page:
            await self.start()

        try:
            await self.page.goto("https://twitter.com/home", wait_until="domcontentloaded")
            await self.page.wait_for_timeout(5000)

            tweets = []
            tweet_elements = await self.page.query_selector_all('article[data-testid="tweet"]')

            for element in tweet_elements[:count]:
                try:
                    # Get tweet text
                    text_element = await element.query_selector('div[data-testid="tweetText"]')
                    text = await text_element.inner_text() if text_element else ""

                    # Get author
                    author_element = await element.query_selector('div[data-testid="User-Name"]')
                    author = await author_element.inner_text() if author_element else ""

                    tweets.append({
                        "author": author.split('\n')[0] if author else "Unknown",
                        "content": text[:500] if text else ""
                    })
                except:
                    continue

            return {"status": "success", "tweets": tweets}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_profile(self) -> Dict[str, Any]:
        """Get current user's profile information."""
        if not self.page:
            await self.start()

        try:
            # Navigate to profile
            await self.page.goto("https://twitter.com/home", wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)

            # Click on profile link
            profile_link = await self.page.query_selector('a[data-testid="AppTabBar_Profile_Link"]')
            if profile_link:
                await profile_link.click()
                await self.page.wait_for_timeout(3000)

            # Get profile info
            name_element = await self.page.query_selector('h2[role="heading"]')
            name = await name_element.inner_text() if name_element else "Unknown"

            handle_element = await self.page.query_selector('span:has-text("@")')
            handle = await handle_element.inner_text() if handle_element else "@unknown"

            # Get profile URL
            profile_url = self.page.url

            return {
                "status": "success",
                "name": name.strip(),
                "handle": handle.strip(),
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


class TwitterBrowserSync:
    """Synchronous wrapper for TwitterBrowser."""

    def __init__(self, session_path: str = "./vault/secrets/twitter_session"):
        self.browser = TwitterBrowser(session_path)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def start(self, headless: bool = True):
        return self.loop.run_until_complete(self.browser.start(headless))

    def login(self, username: str, password: str) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.login(username, password))

    def check_session(self) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.check_session())

    def post_tweet(self, content: str) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.post_tweet(content))

    def get_timeline(self, count: int = 10) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.get_timeline(count))

    def get_profile(self) -> Dict[str, Any]:
        return self.loop.run_until_complete(self.browser.get_profile())

    def close(self):
        return self.loop.run_until_complete(self.browser.close())

    def save_storage_state(self):
        return self.loop.run_until_complete(self.browser.save_storage_state())