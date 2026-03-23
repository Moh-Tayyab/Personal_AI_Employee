"""
Enhanced LinkedIn Browser Automation - Professional-grade LinkedIn automation with advanced stealth
"""

import json
import time
import random
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
import asyncio


class ProfessionalLinkedInBrowser:
    """Professional-grade browser automation for LinkedIn operations with advanced stealth capabilities."""

    def __init__(self, session_path: str = "./vault/secrets/linkedin_session"):
        self.session_path = Path(session_path)
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self, headless: bool = True):
        """Start the browser with persisted session and advanced stealth."""
        self.playwright = sync_playwright().start()

        # Create session directory if needed
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Launch browser with professional stealth settings
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--ignore-certificate-errors",
                "--ignore-certificate-errors-spki-list",
                "--disable-extensions",
                "--disable-plugins-discovery",
                "--enable-automation",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-translate",
                "--disable-popup-blocking",
                "--disable-infobars",
                "--disable-images",  # Optional: disable images to reduce bandwidth
            ]
        )

        # Load or create context with advanced stealth settings
        storage_state = self._get_storage_state()

        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            storage_state=storage_state,
            locale="en-US,en;q=0.9",
            timezone_id="America/New_York",
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
        )

        self.page = self.context.new_page()

        # Add advanced stealth scripts to avoid detection
        self._add_advanced_stealth_scripts()

        # Remove webdriver property
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });

            // Remove webdriver from navigator properties
            delete navigator.__proto__.webdriver;

            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({state: 'denied'}) :
                originalQuery(parameters)
            );

            // Mock webgl
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Google Inc.';
                if (parameter === 37446) return 'ANGLE (Google, Vulkan 1.0.42 (SwiftShader Device) Direct3D11)';
                return getParameter(parameter);
            };

            // Mock audio context
            AudioContext.prototype.audioWorklet = undefined;
        """)

    def _add_advanced_stealth_scripts(self):
        """Add advanced scripts to avoid bot detection."""
        # These scripts help mask the browser as legitimate
        self.page.add_init_script("""
            // Hide all signs of automation
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;

            // Spoof chrome object
            Object.defineProperty(window, 'chrome', {
                writable: true,
                enumerable: true,
                value: {
                    runtime: {}
                },
            });

            // Remove headless indicators
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const pluginArray = [
                        {
                            name: 'Chrome PDF Plugin',
                            filename: 'internal-pdf-viewer',
                            description: 'Portable Document Format'
                        },
                        {
                            name: 'Chrome PDF Viewer',
                            filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                            description: ''
                        },
                        {
                            name: 'Native Client',
                            filename: 'internal-nacl-plugin',
                            description: ''
                        }
                    ];
                    pluginArray.length = 3;
                    return pluginArray;
                }
            });

            // Spoof permissions
            const originalPermissonsQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => {
                if (parameters.name === 'notifications') {
                    return Promise.resolve({
                        state: 'denied',
                        onchange: null
                    });
                }
                return originalPermissonsQuery(parameters);
            };
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

    def save_storage_state(self):
        """Save current storage state."""
        if self.context:
            state = self.context.storage_state()
            storage_file = self.session_path / "storage.json"
            with open(storage_file, "w") as f:
                json.dump(state, f, indent=2)

    def _human_like_delay(self, min_delay=0.5, max_delay=2.0):
        """Introduce random human-like delays."""
        delay = random.uniform(min_delay, max_delay)
        self.page.wait_for_timeout(delay * 1000)

    def _random_mouse_movement(self):
        """Perform random mouse movements to appear human-like."""
        width = 1920
        height = 1080

        # Random mouse movement
        x = random.randint(0, width)
        y = random.randint(0, height)
        self.page.mouse.move(x, y)

        # Small pause after movement
        self._human_like_delay(0.1, 0.5)

    def login(self, email: str, password: str, force_new_session: bool = False) -> Dict[str, Any]:
        """Professional-grade LinkedIn login with anti-detection measures."""
        if not self.page:
            self.start(headless=False)  # Start in non-headless for better compatibility initially

        try:
            print("Navigating to LinkedIn login page...")

            # Navigate to login page
            self.page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded", timeout=30000)
            print(f"Page loaded. Current URL: {self.page.url}")

            # Perform random mouse movements to simulate human activity
            self._random_mouse_movement()
            self._human_like_delay(1, 3)

            # Check if already logged in
            if "feed" in self.page.url or "/in/" in self.page.url:
                self.save_storage_state()
                return {"status": "already_logged_in", "profile_url": self.page.url}

            # Wait for page elements to be ready
            print("Waiting for page elements...")
            self.page.wait_for_load_state("networkidle")

            # Sometimes LinkedIn serves a different version of the page, try multiple selectors
            email_field = None
            email_selectors = [
                'input#username',
                'input#session_key',  # LinkedIn's current common selector
                'input[name="session_key"]',  # LinkedIn's current form field name
                'input[name="login-email"]',
                'input[name="email"]',
                'input[type="email"]',
                'input[placeholder*="email" i]',
                'input[placeholder*="Email" i]',
                'input[placeholder*="username" i]',
                'input[placeholder*="Username" i]',
                'input[autocomplete="username"]',  # Modern form autocomplete
                'input[autocomplete="email"]',  # Modern form autocomplete
                'input#email',  # Alternative common ID
                'input[id^="\\:r"][type="text"]',  # LinkedIn's dynamic ID pattern for text inputs
                'input[id^="\\:r"][type="email"]',  # LinkedIn's dynamic ID pattern for email inputs
            ]

            for selector in email_selectors:
                try:
                    print(f"Trying selector: {selector}")
                    email_field = self.page.wait_for_selector(selector, timeout=5000)
                    if email_field:
                        print(f"Found email field with selector: {selector}")
                        break
                except:
                    continue

            # If still not found, try to find the first text input on the page based on our inspection
            if not email_field:
                print("Trying to find first text input as fallback based on inspection data...")
                try:
                    # According to our inspection, LinkedIn login page has inputs with specific patterns
                    all_inputs = self.page.query_selector_all('input[type="text"], input[type="email"], input:not([type="password"]):not([type="hidden"]):not([type="submit"]):not([type="button"])')

                    # Look for inputs with dynamic IDs (LinkedIn's pattern)
                    for inp in all_inputs:
                        try:
                            inp_id = inp.get_attribute('id')
                            inp_type = inp.get_attribute('type')

                            # Check if it matches LinkedIn's dynamic pattern (like :r0:) and is text/email type
                            if inp_id and inp_id.startswith(':r') and inp_type in ['text', 'email']:
                                email_field = inp
                                print(f"Found email field with dynamic ID: {inp_id}")
                                break
                        except:
                            continue

                    # If still not found, take the first text/email input
                    if not email_field:
                        for inp in all_inputs:
                            if inp.is_visible():
                                email_field = inp
                                print("Found email field as first visible text input")
                                break
                except Exception as e:
                    print(f"Error finding fallback email field: {e}")
                    pass

            if not email_field:
                # If we can't find the email field, try clicking "Sign in" button first
                try:
                    sign_in_button = self.page.wait_for_selector('button:text("Sign in")', timeout=5000)
                    if sign_in_button:
                        print("Found Sign in button, clicking...")
                        sign_in_button.click()
                        self._human_like_delay(1, 2)
                        # Try looking for email field again after clicking
                        for selector in email_selectors:
                            try:
                                email_field = self.page.wait_for_selector(selector, timeout=3000)
                                if email_field:
                                    break
                            except:
                                continue
                except:
                    pass

            if not email_field:
                return {
                    "status": "login_failed",
                    "error": "Could not find email field. LinkedIn may have updated their login page."
                }

            # Fill email with human-like typing
            print("Filling email...")
            self._random_mouse_movement()
            email_field.click()
            self._human_like_delay(0.5, 1)

            # Clear the field first
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Delete")
            self._human_like_delay(0.2, 0.5)

            # Type email with human-like delays
            for char in email:
                self.page.keyboard.type(char)
                time.sleep(random.uniform(0.05, 0.2))  # Random typing delay

            self._human_like_delay(1, 2)

            # Now find and fill the password field
            password_selectors = [
                'input#password',
                'input#session_password',  # LinkedIn's current common selector
                'input[name="session_password"]',  # LinkedIn's current form field name
                'input[name="password"]',
                'input[type="password"]',
                'input[placeholder*="password" i]',
                'input[placeholder*="Password" i]',
                'input[autocomplete="current-password"]',  # Modern form autocomplete
                'input#password-input',  # Alternative common ID
                'input[id^="\\:r"][type="password"]',  # LinkedIn's dynamic ID pattern for password inputs
            ]

            password_field = None
            for selector in password_selectors:
                try:
                    print(f"Trying password selector: {selector}")
                    password_field = self.page.wait_for_selector(selector, timeout=5000)
                    if password_field:
                        print(f"Found password field with selector: {selector}")
                        break
                except:
                    continue

            # If still not found, try to find the first password input on the page based on our inspection
            if not password_field:
                print("Trying to find first password input as fallback based on inspection data...")
                try:
                    password_inputs = self.page.query_selector_all('input[type="password"]')
                    # Look for inputs with dynamic IDs (LinkedIn's pattern)
                    for inp in password_inputs:
                        try:
                            inp_id = inp.get_attribute('id')

                            # Check if it matches LinkedIn's dynamic pattern (like :r1:)
                            if inp_id and inp_id.startswith(':r'):
                                password_field = inp
                                print(f"Found password field with dynamic ID: {inp_id}")
                                break
                        except:
                            continue

                    # If still not found, take the first password input
                    if not password_field:
                        for inp in password_inputs:
                            if inp.is_visible():
                                password_field = inp
                                print("Found password field as first visible password input")
                                break
                except Exception as e:
                    print(f"Error finding fallback password field: {e}")
                    pass

            if not password_field:
                return {
                    "status": "login_failed",
                    "error": "Could not find password field."
                }

            # Fill password with human-like typing
            print("Filling password...")
            self._random_mouse_movement()
            password_field.click()
            self._human_like_delay(0.5, 1)

            # Clear the field first
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Delete")
            self._human_like_delay(0.2, 0.5)

            # Type password with human-like delays
            for char in password:
                self.page.keyboard.type(char)
                time.sleep(random.uniform(0.05, 0.15))  # Random typing delay

            self._human_like_delay(1, 2)

            # Submit the form by pressing Enter in the password field
            print("Submitting login form...")
            password_field.press("Enter")

            # Wait for potential redirects, 2FA, etc.
            self._human_like_delay(3, 5)

            # Wait up to 90 seconds for navigation to succeed, as LinkedIn sometimes has additional verification
            try:
                self.page.wait_for_url(re.compile(r"https://www\.linkedin\.com/(feed|in/|home/)"), timeout=90000)
                print("✅ Appears to be logged in successfully!")
            except Exception as e:
                print(f"Potential timeout during navigation: {e}")
                # Check if we're on a different page but still logged in
                current_url = self.page.url
                if "linkedin.com" in current_url and "login" not in current_url and "checkpoint" not in current_url and "authwall" not in current_url:
                    print("✅ Appears to be logged in (different page detected)!")
                elif "checkpoint" in current_url or "challenge" in current_url or "verification" in current_url:
                    return {
                        "status": "login_failed",
                        "error": f"Additional verification required. Current URL: {current_url}"
                    }
                else:
                    print(f"⚠️ Still on login/checkpoint page. Current URL: {current_url}")
                    return {
                        "status": "login_failed",
                        "error": f"Login failed, still on login page. URL: {current_url}"
                    }

            # Additional wait for page to fully load
            self._human_like_delay(3, 5)

            # Final check to ensure we're on the feed page
            if "linkedin.com/feed" in self.page.url or "linkedin.com/home" in self.page.url:
                print("✅ Successfully logged in to LinkedIn!")
            else:
                print(f"ℹ️ Current page after login attempt: {self.page.url}")

            # Save session
            self.save_storage_state()

            return {
                "status": "logged_in",
                "profile_url": self.page.url,
                "success": True
            }

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Login failed with error: {error_msg}")

            # Take a screenshot for debugging if there's an error
            try:
                timestamp = int(time.time())
                screenshot_path = f"linkedin_login_debug_{timestamp}.png"
                self.page.screenshot(path=screenshot_path)
                print(f"Screenshot saved as {screenshot_path}")
            except:
                pass

            return {"status": "login_failed", "error": error_msg}

    def check_session(self) -> Dict[str, Any]:
        """Check if session is valid with enhanced checks."""
        if not self.page:
            self.start(headless=True)

        try:
            # First check if we have storage state
            storage_file = self.session_path / "storage.json"
            if not storage_file.exists():
                return {"status": "not_authenticated", "message": "No session file found"}

            # Navigate to home page to check authentication
            self.page.goto("https://www.linkedin.com/", wait_until="domcontentloaded", timeout=30000)
            self._human_like_delay(2, 4)

            # Check if redirected to login or if we're properly authenticated
            current_url = self.page.url

            if "login" in current_url or "checkpoint" in current_url or "authwall" in current_url:
                return {"status": "not_authenticated", "message": "Session expired or needs verification"}
            elif "feed" in current_url or "home" in current_url or "/in/" in current_url:
                return {"status": "authenticated", "profile_url": current_url}
            else:
                # Check for elements that indicate we're logged in
                try:
                    # Look for elements that exist only when logged in
                    nav_element = self.page.query_selector('[data-test-id="nav.home.tab"]')
                    if nav_element:
                        return {"status": "authenticated", "profile_url": current_url}

                    # Try another common logged-in indicator
                    search_input = self.page.query_selector('input[placeholder*="Search"]')
                    if search_input:
                        return {"status": "authenticated", "profile_url": current_url}
                except:
                    pass

                return {"status": "not_authenticated", "message": "Not on authenticated page"}

        except Exception as e:
            return {"status": "not_authenticated", "error": str(e)}

    def create_post(self, content: str, headline: str = "", media_path: Optional[str] = None) -> Dict[str, Any]:
        """Create a professional LinkedIn post with enhanced capabilities."""
        if not self.page:
            self.start(headless=False)

        try:
            print("Navigating to LinkedIn feed...")
            # Go to the home page to ensure we're properly authenticated
            self.page.goto("https://www.linkedin.com/feed", wait_until="domcontentloaded", timeout=30000)
            self._human_like_delay(2, 4)

            # Verify we're on the feed page
            if "linkedin.com/feed" not in self.page.url and "linkedin.com/home" not in self.page.url:
                return {"status": "post_failed", "error": f"Not on feed page. Current URL: {self.page.url}"}

            # Perform random mouse movements to appear human-like
            self._random_mouse_movement()
            self._human_like_delay(1, 2)

            print("Looking for 'Start a post' button...")
            # Try multiple selectors for the "Start a post" button
            post_button_selectors = [
                'button[aria-label*="share" i]',
                'button[aria-label*="Share" i]',
                'button[aria-label*="create" i]',
                'button[aria-label*="Create" i]',
                'button[aria-label*="post" i]',
                'button[aria-label*="Post" i]',
                'button[data-control-name*="share" i]',
                'div[role="button"]:has-text("Start a post")',
                'button:has-text("Start a post")',
                'button:has-text("Post")',
                'button:has-text("Share an update")',
                'button[aria-label="Create a post"]',
                'button[data-test-id="profile-create-share-ubertext"]',
                'button[data-testid*="create" i]',
                'button[data-testid*="post" i]',
                '[data-test-id="nav.create_feed_shared_content-actor"]',
            ]

            post_button = None
            for selector in post_button_selectors:
                try:
                    post_button = self.page.wait_for_selector(selector, timeout=5000)
                    if post_button:
                        print(f"Found post button with selector: {selector}")
                        break
                except:
                    continue

            # If no button found, try to find the button by its visible text or role
            if not post_button:
                try:
                    # Try finding by text content in any element that behaves like a button
                    all_elements = self.page.query_selector_all('div, span, button, a')
                    for elem in all_elements:
                        try:
                            if elem.is_visible():
                                text = elem.inner_text().strip().lower()
                                if any(keyword in text for keyword in ["start a post", "post", "create", "share"]):
                                    # Check if this element is clickable
                                    post_button = elem
                                    print(f"Found potential post button by text content: '{text}'")
                                    break
                        except:
                            continue
                except:
                    pass

            if not post_button:
                return {"status": "post_failed", "error": "Could not find 'Start a post' button after trying multiple selectors"}

            # Click the post button with human-like behavior
            print("Clicking post button...")
            self._random_mouse_movement()
            post_button.click()
            self._human_like_delay(2, 4)

            # Wait for the post editor to appear
            print("Waiting for post editor...")
            text_editor_selectors = [
                'div[contenteditable="true"][data-testid="post-text-editor"]',
                'div[contenteditable="true"][data-lexical-editor="true"]',
                'div[contenteditable="true"]:not([tabindex="-1"])',
                'div[role="textbox"][contenteditable="true"]',
                'div[contenteditable="true"][data-placeholder*="post" i]',
                'div[contenteditable="true"][data-test-id*="share" i]',
                'div[contenteditable="true"][data-test-id*="post" i]',
                'div[contenteditable="true"]',
                '[data-test-id="artdeco-text-input__textarea"]',
                'div[aria-label="Write your post..."]',
                'div[aria-label="Share your post..."]',
                'div[aria-label="Create a post..."]',
                'div[aria-describedby*="post" i]',
            ]

            text_editor = None
            for selector in text_editor_selectors:
                try:
                    text_editor = self.page.wait_for_selector(selector, timeout=5000)
                    if text_editor:
                        print(f"Found text editor with selector: {selector}")
                        break
                except:
                    continue

            # If not found, try to identify the editor by other means
            if not text_editor:
                try:
                    # Try to find any contenteditable div
                    all_editables = self.page.query_selector_all('div[contenteditable="true"], span[contenteditable="true"]')
                    for elem in all_editables:
                        if elem.is_visible():
                            # Check if it's likely the post editor
                            class_attr = elem.get_attribute('class') or ""
                            if any(keyword in class_attr.lower() for keyword in ['editor', 'post', 'share', 'text', 'content']):
                                text_editor = elem
                                print("Found text editor by class pattern matching")
                                break
                except:
                    pass

            if not text_editor:
                return {"status": "post_failed", "error": "Could not find text editor after trying multiple selectors"}

            # Clear and fill content with human-like typing
            print("Filling post content...")
            self._random_mouse_movement()
            text_editor.click()
            self._human_like_delay(0.5, 1)

            # Select all and delete
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Delete")
            self._human_like_delay(0.5, 1)

            # Type content with human-like delays
            for char in content:
                if char == '\n':
                    self.page.keyboard.press("Enter")
                    self._human_like_delay(0.2, 0.5)
                else:
                    self.page.keyboard.type(char, delay=random.randint(30, 100))

            self._human_like_delay(2, 4)

            # Add media if provided
            if media_path:
                media_file = Path(media_path)
                if media_file.exists():
                    print("Adding media to post...")
                    try:
                        # Look for photo/video attachment buttons
                        media_button_selectors = [
                            'button[aria-label*="photo" i]',
                            'button[aria-label*="image" i]',
                            'button[aria-label*="media" i]',
                            'button:has-text("Photo")',
                            'button:has-text("Image")',
                            'button[data-test-id*="image" i]'
                        ]

                        media_button = None
                        for selector in media_button_selectors:
                            try:
                                media_button = self.page.wait_for_selector(selector, timeout=3000)
                                if media_button:
                                    break
                            except:
                                continue

                        if media_button:
                            media_button.click()
                            self._human_like_delay(1, 2)

                            # Find file input and upload
                            file_input = self.page.wait_for_selector('input[type="file"]', timeout=3000)
                            if file_input:
                                file_input.set_input_files(str(media_file.absolute()))
                                self._human_like_delay(3, 5)
                        else:
                            print("Media button not found, continuing without media")
                    except Exception as e:
                        print(f"Media upload warning: {e}")

            # Find and click the post button
            print("Looking for post button...")
            post_confirm_selectors = [
                'button[aria-label*="post" i]:not([disabled])',
                'button:has-text("Post"):not([disabled])',
                'button:has-text("Share"):not([disabled])',
                'button[data-test-id*="share" i]:not([disabled])'
            ]

            post_confirm_button = None
            for selector in post_confirm_selectors:
                try:
                    post_confirm_button = self.page.wait_for_selector(selector, timeout=5000)
                    if post_confirm_button and not post_confirm_button.is_disabled():
                        print(f"Found post confirm button with selector: {selector}")
                        break
                except:
                    continue

            if not post_confirm_button:
                return {"status": "post_failed", "error": "Could not find active Post button"}

            # Click post button with human-like behavior
            print("Publishing post...")
            self._random_mouse_movement()
            post_confirm_button.click()
            self._human_like_delay(3, 6)

            # Check if post was successful
            try:
                # Wait to see if we return to the feed
                self.page.wait_for_url(re.compile(r"https://www\.linkedin\.com/(feed|home)/"), timeout=15000)
                print("✅ Post appears to have been published successfully!")
                return {
                    "status": "posted",
                    "message": "Successfully posted to LinkedIn",
                    "success": True
                }
            except:
                # Even if URL doesn't change, the post might still be successful
                print("Post submitted, but couldn't confirm return to feed. May have succeeded.")
                return {
                    "status": "posted",
                    "message": "Post submitted to LinkedIn (may still be processing)",
                    "success": True
                }

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Post creation failed: {error_msg}")

            # Take a screenshot for debugging if there's an error
            try:
                timestamp = int(time.time())
                screenshot_path = f"linkedin_post_debug_{timestamp}.png"
                self.page.screenshot(path=screenshot_path)
                print(f"Screenshot saved as {screenshot_path}")
            except:
                pass

            return {"status": "post_failed", "error": error_msg}

    def close(self):
        """Close browser with cleanup."""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except:
            pass  # Ignore errors during cleanup

    def get_current_profile_info(self) -> Dict[str, Any]:
        """Get current logged-in user profile info."""
        if not self.page:
            self.start(headless=True)

        try:
            self.page.goto("https://www.linkedin.com/in/", wait_until="domcontentloaded", timeout=30000)
            self._human_like_delay(2, 4)

            # Extract profile info
            profile_url = self.page.url
            try:
                profile_name = self.page.query_selector('h1.text-heading-xlarge').inner_text().strip()
            except:
                profile_name = "Unknown"

            return {
                "status": "success",
                "profile_url": profile_url,
                "profile_name": profile_name
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}