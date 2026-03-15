"""
Browser base class for e-commerce platforms
"""

import asyncio
import base64
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class EcommerceBrowser:
    """Base browser class for e-commerce platforms"""
    
    def __init__(self, platform: str, headless: bool = False):
        """
        Initialize browser for a specific platform
        
        Args:
            platform: Platform identifier (e.g., 'jd', 'taobao')
            headless: Run browser in headless mode
        """
        self.platform = platform
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._data_dir = Path.home() / '.openclaw' / 'data' / 'ecommerce'
        self._data_dir.mkdir(parents=True, exist_ok=True)
        
    @property
    def page(self) -> Optional[Page]:
        """Get current page"""
        return self._page
        
    async def init(self) -> bool:
        """
        Initialize browser instance
        
        Returns:
            True if initialization successful
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed. Run: pip install playwright && playwright install")
            
        self._playwright = await async_playwright().start()
        
        # Launch browser with user data directory for persistence
        user_data_dir = self._data_dir / f'{self.platform}_profile'
        
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        self._context = await self._browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self._page = await self._context.new_page()
        
        # Inject anti-detection script
        await self._page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        return True
        
    async def close(self):
        """Close browser and cleanup"""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
            
    async def goto(self, url: str, wait_until: str = 'networkidle') -> bool:
        """
        Navigate to URL
        
        Args:
            url: Target URL
            wait_until: When to consider navigation complete
            
        Returns:
            True if navigation successful
        """
        if not self._page:
            raise RuntimeError("Browser not initialized. Call init() first.")
            
        try:
            await self._page.goto(url, wait_until=wait_until, timeout=30000)
            return True
        except Exception as e:
            print(f"Navigation failed: {e}")
            return False
            
    async def screenshot(self, path: Optional[str] = None) -> str:
        """
        Take screenshot
        
        Args:
            path: Save path (optional, auto-generated if not provided)
            
        Returns:
            Path to screenshot file
        """
        if not self._page:
            raise RuntimeError("Browser not initialized")
            
        if path is None:
            timestamp = asyncio.get_event_loop().time()
            path = self._data_dir / f'{self.platform}_{int(timestamp)}.png'
        else:
            path = Path(path)
            
        await self._page.screenshot(path=str(path), full_page=True)
        return str(path)
        
    async def get_qr_code(self, selector: str) -> Optional[str]:
        """
        Extract QR code from page
        
        Args:
            selector: CSS selector for QR code image element
            
        Returns:
            Base64 encoded QR code image or None
        """
        if not self._page:
            raise RuntimeError("Browser not initialized")
            
        try:
            element = await self._page.query_selector(selector)
            if element:
                # Try to get src attribute
                src = await element.get_attribute('src')
                if src and src.startswith('data:image'):
                    return src
                    
                # Take element screenshot
                screenshot = await element.screenshot()
                return f"data:image/png;base64,{base64.b64encode(screenshot).decode()}"
        except Exception as e:
            print(f"Failed to extract QR code: {e}")
            
        return None
        
    async def wait_for_login(self, check_selector: str, timeout: int = 120) -> bool:
        """
        Wait for user to complete login
        
        Args:
            check_selector: Element that appears after login
            timeout: Maximum wait time in seconds
            
        Returns:
            True if login detected
        """
        if not self._page:
            raise RuntimeError("Browser not initialized")
            
        try:
            await self._page.wait_for_selector(check_selector, timeout=timeout * 1000)
            return True
        except Exception:
            return False
            
    async def search(self, keyword: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Generic search interface - to be implemented by subclasses
        
        Args:
            keyword: Search term
            **kwargs: Platform-specific options
            
        Returns:
            List of search results
        """
        raise NotImplementedError("Subclasses must implement search()")
        
    async def login_qr(self) -> Optional[str]:
        """
        QR code login - to be implemented by subclasses
        
        Returns:
            QR code image data or None
        """
        raise NotImplementedError("Subclasses must implement login_qr()")
        
    def save_cookies(self) -> bool:
        """Save current session cookies"""
        if not self._context:
            return False
            
        try:
            import asyncio
            cookies = asyncio.get_event_loop().run_until_complete(self._context.cookies())
            cookie_file = self._data_dir / f'{self.platform}_cookies.json'
            with open(cookie_file, 'w') as f:
                json.dump(cookies, f)
            return True
        except Exception as e:
            print(f"Failed to save cookies: {e}")
            return False
            
    def load_cookies(self) -> bool:
        """Load saved session cookies"""
        if not self._context:
            return False
            
        cookie_file = self._data_dir / f'{self.platform}_cookies.json'
        if not cookie_file.exists():
            return False
            
        try:
            import asyncio
            with open(cookie_file, 'r') as f:
                cookies = json.load(f)
            asyncio.get_event_loop().run_until_complete(self._context.add_cookies(cookies))
            return True
        except Exception as e:
            print(f"Failed to load cookies: {e}")
            return False
