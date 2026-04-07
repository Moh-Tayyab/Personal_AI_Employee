#!/usr/bin/env python3
"""
WhatsApp Browser Manager - Shared Browser Instance Manager
Provides a singleton browser instance that can be shared between Watcher and MCP Server.
Supports both Sync (for Watcher) and Async (for MCP Server) APIs.
"""

import os
import time
import logging
import asyncio
from pathlib import Path
from typing import Optional
from playwright.sync_api import sync_playwright, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright, BrowserContext as AsyncBrowserContext, Page as AsyncPage


logger = logging.getLogger('WhatsAppBrowserManager')


class WhatsAppBrowserManager:
    """
    Singleton manager for WhatsApp Web browser instance.
    
    This ensures:
    - Only ONE browser session runs at a time
    - Both Watcher and MCP Server share the same session
    - Automatic reconnection if browser crashes
    - Session persistence across restarts
    """
    
    _instance: Optional['WhatsAppBrowserManager'] = None
    _sync_playwright = None
    _async_playwright = None
    _sync_browser: Optional[BrowserContext] = None
    _async_browser: Optional[AsyncBrowserContext] = None
    _sync_page: Optional[Page] = None
    _async_page: Optional[AsyncPage] = None
    _is_initialized = False
    _session_path: Optional[Path] = None
    _headless = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, session_path: str = None, headless: bool = False):
        """Initialize browser manager (only runs once due to singleton)"""
        if self._is_initialized:
            return
        
        if session_path:
            self._session_path = Path(session_path)
            self._session_path.mkdir(parents=True, exist_ok=True)
        
        self._headless = headless
        self.whatsapp_url = "https://web.whatsapp.com"
        self._is_initialized = True
        
        logger.info(f"WhatsAppBrowserManager initialized")
        logger.info(f"Session path: {self._session_path}")
    
    @property
    def session_path(self) -> Path:
        return self._session_path or Path('.whatsapp_session')
    
    async def get_async_browser(self) -> tuple[AsyncBrowserContext, AsyncPage]:
        """
        Get or create async browser instance (for MCP Server).
        Returns (browser_context, page) tuple.
        """
        try:
            # Check if async browser is still alive
            if self._async_browser and self._async_page:
                try:
                    await self._async_page.wait_for_selector('[data-testid="chat-list"]', timeout=2000)
                    return self._async_browser, self._async_page
                except Exception:
                    logger.warning("WhatsApp Web not responding, attempting reconnect...")
                    await self._close_async_browser()
            
            # Create new async browser
            return await self._initialize_async_browser()
            
        except Exception as e:
            logger.error(f"Failed to get async browser: {e}")
            raise RuntimeError(f"Browser initialization failed: {e}")
    
    def get_browser(self) -> tuple[BrowserContext, Page]:
        """
        Get or create sync browser instance (for Watcher).
        Returns (browser_context, page) tuple.
        """
        try:
            # Check if sync browser is still alive
            if self._sync_browser and self._sync_page and not self._sync_page.is_closed():
                try:
                    self._sync_page.wait_for_selector('[data-testid="chat-list"]', timeout=2000)
                    return self._sync_browser, self._sync_page
                except Exception:
                    logger.warning("WhatsApp Web not responding, attempting reconnect...")
                    self._close_sync_browser()
            
            # Create new sync browser
            return self._initialize_sync_browser()
            
        except Exception as e:
            logger.error(f"Failed to get browser: {e}")
            raise RuntimeError(f"Browser initialization failed: {e}")
    
    async def _initialize_async_browser(self) -> tuple[AsyncBrowserContext, AsyncPage]:
        """Create new async browser instance"""
        logger.info("Initializing async WhatsApp Web browser...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Start async Playwright if not running
                if not self._async_playwright:
                    self._async_playwright = await async_playwright().start()
                    logger.info("Async Playwright started")
                
                # Launch browser with persistent context
                self._async_browser = await self._async_playwright.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=self._headless,
                    viewport={'width': 1280, 'height': 720},
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                )
                
                # Get or create page
                if self._async_browser.pages:
                    self._async_page = self._async_browser.pages[0]
                else:
                    self._async_page = await self._async_browser.new_page()
                
                # Navigate to WhatsApp Web
                logger.info("Loading WhatsApp Web...")
                await self._async_page.goto(self.whatsapp_url, timeout=60000)
                
                # Wait for WhatsApp to load
                await self._async_wait_for_whatsapp_load()
                
                logger.info("Async browser initialized successfully")
                return self._async_browser, self._async_page
                
            except Exception as e:
                logger.warning(f"Async browser initialization attempt {attempt + 1}/{max_retries} failed: {e}")
                await self._close_async_browser()
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to initialize async browser after {max_retries} attempts: {e}")
                await asyncio.sleep(2)
    
    def _initialize_sync_browser(self) -> tuple[BrowserContext, Page]:
        """Create new sync browser instance"""
        logger.info("Initializing sync WhatsApp Web browser...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Start sync Playwright if not running
                if not self._sync_playwright:
                    self._sync_playwright = sync_playwright().start()
                    logger.info("Sync Playwright started")
                
                # Launch browser with persistent context
                self._sync_browser = self._sync_playwright.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=self._headless,
                    viewport={'width': 1280, 'height': 720},
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                )
                
                # Get or create page
                if self._sync_browser.pages:
                    self._sync_page = self._sync_browser.pages[0]
                else:
                    self._sync_page = self._sync_browser.new_page()
                
                # Navigate to WhatsApp Web
                logger.info("Loading WhatsApp Web...")
                self._sync_page.goto(self.whatsapp_url, timeout=60000)
                
                # Wait for WhatsApp to load
                self._sync_wait_for_whatsapp_load()
                
                logger.info("Sync browser initialized successfully")
                return self._sync_browser, self._sync_page
                
            except Exception as e:
                logger.warning(f"Sync browser initialization attempt {attempt + 1}/{max_retries} failed: {e}")
                self._close_sync_browser()
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to initialize sync browser after {max_retries} attempts: {e}")
                time.sleep(2)
    
    async def _async_wait_for_whatsapp_load(self, timeout: int = 90000) -> None:
        """Wait for WhatsApp Web to load (async version)"""
        logger.info("Waiting for WhatsApp Web to load...")
        
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            try:
                # Check if logged in
                chat_list = await self._async_page.query_selector('[data-testid="chat-list"]')
                if chat_list:
                    logger.info("WhatsApp Web loaded - User is logged in")
                    return
                
                # Check if showing QR code
                qr_code = await self._async_page.query_selector('canvas[aria-label*="QR"]')
                if qr_code:
                    elapsed = time.time() - start_time
                    if elapsed > 120:
                        raise RuntimeError("QR code scan timeout (120s)")
                    await asyncio.sleep(2)
                    continue
                
                # Check for search box
                search_box = await self._async_page.query_selector('[data-testid="chat-list-search"]')
                if search_box:
                    logger.info("WhatsApp Web loaded - Search box detected")
                    return
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.warning(f"WhatsApp load check error: {e}")
                await asyncio.sleep(2)
        
        raise RuntimeError("WhatsApp Web load timeout")
    
    def _sync_wait_for_whatsapp_load(self, timeout: int = 90000) -> None:
        """Wait for WhatsApp Web to load (sync version)"""
        logger.info("Waiting for WhatsApp Web to load...")
        
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            try:
                chat_list = self._sync_page.query_selector('[data-testid="chat-list"]')
                if chat_list:
                    logger.info("WhatsApp Web loaded - User is logged in")
                    return
                
                qr_code = self._sync_page.query_selector('canvas[aria-label*="QR"]')
                if qr_code:
                    elapsed = time.time() - start_time
                    if elapsed > 120:
                        raise RuntimeError("QR code scan timeout (120s)")
                    time.sleep(2)
                    continue
                
                search_box = self._sync_page.query_selector('[data-testid="chat-list-search"]')
                if search_box:
                    logger.info("WhatsApp Web loaded - Search box detected")
                    return
                
                time.sleep(1)
                
            except Exception as e:
                logger.warning(f"WhatsApp load check error: {e}")
                time.sleep(2)
        
        raise RuntimeError("WhatsApp Web load timeout")
    
    async def _close_async_browser(self) -> None:
        """Close async browser and cleanup"""
        try:
            if self._async_browser:
                await self._async_browser.close()
                logger.info("Async browser closed")
        except Exception as e:
            logger.warning(f"Error closing async browser: {e}")
        finally:
            self._async_browser = None
            self._async_page = None
    
    def _close_sync_browser(self) -> None:
        """Close sync browser and cleanup"""
        try:
            if self._sync_browser:
                self._sync_browser.close()
                logger.info("Sync browser closed")
        except Exception as e:
            logger.warning(f"Error closing sync browser: {e}")
        finally:
            self._sync_browser = None
            self._sync_page = None
    
    def shutdown(self) -> None:
        """Completely shutdown browser and Playwright"""
        self._close_sync_browser()
        if self._sync_playwright:
            try:
                self._sync_playwright.stop()
                logger.info("Sync Playwright stopped")
            except Exception as e:
                logger.warning(f"Error stopping sync Playwright: {e}")
            finally:
                self._sync_playwright = None
    
    async def async_shutdown(self) -> None:
        """Completely shutdown async browser and Playwright"""
        await self._close_async_browser()
        if self._async_playwright:
            try:
                await self._async_playwright.stop()
                logger.info("Async Playwright stopped")
            except Exception as e:
                logger.warning(f"Error stopping async Playwright: {e}")
            finally:
                self._async_playwright = None
    
    def is_logged_in(self) -> bool:
        """Check if WhatsApp Web is logged in (sync)"""
        try:
            if not self._sync_page or self._sync_page.is_closed():
                return False
            
            chat_list = self._sync_page.query_selector('[data-testid="chat-list"]')
            return chat_list is not None
            
        except Exception:
            return False
    
    async def is_logged_in_async(self) -> bool:
        """Check if WhatsApp Web is logged in (async)"""
        try:
            if not self._async_page or self._async_page.is_closed():
                return False
            
            chat_list = await self._async_page.query_selector('[data-testid="chat-list"]')
            return chat_list is not None
            
        except Exception:
            return False
    
    def reload_whatsapp(self) -> bool:
        """Reload WhatsApp Web page"""
        try:
            if self._sync_page and not self._sync_page.is_closed():
                self._sync_page.reload(wait_until='networkidle')
                self._sync_wait_for_whatsapp_load()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to reload WhatsApp: {e}")
            return False


def get_browser_manager(session_path: str = None, headless: bool = False) -> WhatsAppBrowserManager:
    """
    Factory function to get or create browser manager.
    This is the main entry point for both Watcher and MCP Server.
    """
    if session_path is None:
        session_path = os.path.join(os.getcwd(), '.whatsapp_session')
    
    # Get singleton instance
    manager = WhatsAppBrowserManager(
        session_path=session_path,
        headless=headless
    )
    
    return manager
