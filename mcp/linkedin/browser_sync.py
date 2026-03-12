"""
LinkedIn Browser Automation - Playwright-based LinkedIn automation (Sync version)
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


class LinkedInBrowser:
    """Browser automation for LinkedIn operations."""

    def __init__(self, session_path: str = "./vault/secrets/linkedin_session"):
        self.session_path = Path(session_path)
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self, headless: bool = True):
        """Start the browser with persisted session."""
        self.playwright = sync_playwright().start()
        
        # Create session directory if needed
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Launch browser
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )

        # Load or create context
        storage_state = self._get_storage_state()
        
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            storage_state=storage_state,
        )

        self.page = self.context.new_page()
        
        # Add stealth scripts
        self._add_stealth_scripts()

    def _add_stealth_scripts(self):
        """Add scripts to avoid detection."""
        self.page.add_init_script("""
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

    def save_storage_state(self):
        """Save current storage state."""
        if self.context:
            state = self.context.storage_state()
            storage_file = self.session_path / "storage.json"
            with open(storage_file, "w") as f:
                json.dump(state, f, indent=2)

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login to LinkedIn."""
        if not self.page:
            self.start(headless=False)

        try:
            # Navigate to login page
            self.page.goto("https://www.linkedin.com/login", wait_until="networkidle", timeout=30000)
            self.page.wait_for_timeout(3000)

            # Check if already logged in
            if "feed" in self.page.url or "/in/" in self.page.url:
                self.save_storage_state()
                return {"status": "already_logged_in", "profile_url": self.page.url}

            # Fill email
            email_field = self.page.wait_for_selector('input[id="username"]', timeout=10000)
            email_field.click()
            self.page.wait_for_timeout(500)
            email_field.fill(email)
            self.page.wait_for_timeout(1000)

            # Fill password
            password_field = self.page.wait_for_selector('input[type="password"]', timeout=5000)
            password_field.click()
            self.page.wait_for_timeout(500)
            password_field.fill(password)
            self.page.wait_for_timeout(1000)

            # Press Enter to submit
            password_field.press("Enter")
            self.page.wait_for_timeout(2000)

            # Wait for navigation
            try:
                self.page.wait_for_url("https://www.linkedin.com/feed/*", timeout=45000)
            except:
                if "linkedin.com" in self.page.url and "login" not in self.page.url:
                    pass  # Likely successful
                else:
                    return {"status": "login_failed", "error": "Navigation timeout - may need 2FA verification"}

            self.page.wait_for_timeout(5000)

            # Save session
            self.save_storage_state()

            return {"status": "logged_in", "profile_url": self.page.url}

        except Exception as e:
            return {"status": "login_failed", "error": str(e)}

    def check_session(self) -> Dict[str, Any]:
        """Check if session is valid."""
        if not self.page:
            self.start()

        try:
            # First check if we have storage state
            storage_file = self.session_path / "storage.json"
            if not storage_file.exists():
                return {"status": "not_authenticated", "message": "No session file found"}

            # Navigate with longer timeout
            self.page.goto("https://www.linkedin.com/feed", wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(5000)

            # Check if redirected to login
            if "login" in self.page.url or "checkpoint" in self.page.url:
                return {"status": "not_authenticated", "message": "Session expired or needs verification"}

            # If we're on feed page, we're authenticated
            if "feed" in self.page.url:
                return {"status": "authenticated", "profile_name": "User", "profile_url": "https://linkedin.com/in/user"}
            
            return {"status": "not_authenticated", "message": "Not on feed page"}

        except Exception as e:
            return {"status": "not_authenticated", "error": str(e)}

    def create_post(self, content: str, media_path: Optional[str] = None) -> Dict[str, Any]:
        """Create a LinkedIn post."""
        if not self.page:
            self.start()

        try:
            # Navigate to feed
            self.page.goto("https://www.linkedin.com/feed", wait_until="domcontentloaded")
            self.page.wait_for_timeout(10000)  # Wait for JS to load

            # Click on "Start a post" button - use text content since class names are obfuscated
            post_button = None
            try:
                # Find div containing "Start a post" text
                post_areas = self.page.query_selector_all("div")
                for div in post_areas:
                    try:
                        text = div.inner_text().strip()
                        if text.startswith("Start a post"):
                            post_button = div
                            break
                    except:
                        continue
                
                if post_button:
                    post_button.click()
                    self.page.wait_for_timeout(3000)
                else:
                    return {"status": "post_failed", "error": "Could not find 'Start a post' button"}
            except Exception as e:
                return {"status": "post_failed", "error": f"Failed to click post button: {str(e)}"}

            # Wait for modal to open and find the text editor
            self.page.wait_for_timeout(2000)
            
            # Find the text editor (contenteditable div in the modal)
            text_editor = None
            try:
                text_editor = self.page.wait_for_selector('div[contenteditable="true"]', timeout=5000)
            except:
                pass
            
            if not text_editor:
                return {"status": "post_failed", "error": "Could not find text editor"}
            
            # Clear and fill using keyboard
            text_editor.click()
            self.page.wait_for_timeout(500)
            
            # Select all and delete
            self.page.keyboard.press("Control+A")
            self.page.wait_for_timeout(200)
            self.page.keyboard.press("Delete")
            self.page.wait_for_timeout(200)
            
            # Type content in chunks to avoid issues
            self.page.keyboard.type(content, delay=30)
            self.page.wait_for_timeout(2000)

            # Add media if provided
            if media_path:
                media_file = Path(media_path)
                if media_file.exists():
                    try:
                        # Look for photo/video buttons by text
                        all_buttons = self.page.query_selector_all("button")
                        for btn in all_buttons:
                            try:
                                aria = btn.get_attribute("aria-label") or ""
                                if "Photo" in aria or "Video" in aria:
                                    btn.click()
                                    self.page.wait_for_timeout(1000)
                                    break
                            except:
                                continue
                        
                        # Upload file
                        file_input = self.page.wait_for_selector('input[type="file"]', timeout=3000)
                        if file_input:
                            file_input.set_input_files(str(media_file.absolute()))
                            self.page.wait_for_timeout(3000)
                    except Exception as e:
                        print(f"Media upload warning: {e}")

            # Click post button - look for button with "Post" text
            post_btn = None
            try:
                all_buttons = self.page.query_selector_all("button")
                for btn in all_buttons:
                    try:
                        text = btn.inner_text().strip()
                        if text == "Post":
                            post_btn = btn
                            break
                    except:
                        continue
                
                if post_btn:
                    post_btn.click()
                    self.page.wait_for_timeout(5000)
                    
                    if "feed" in self.page.url:
                        return {"status": "posted", "message": "Successfully posted to LinkedIn"}
                    else:
                        return {"status": "posted", "message": "Post submitted"}
                else:
                    return {"status": "post_failed", "error": "Could not find Post button"}
            except Exception as e:
                return {"status": "post_failed", "error": f"Post button error: {str(e)}"}

        except Exception as e:
            return {"status": "post_failed", "error": str(e)}

    def close(self):
        """Close browser."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
