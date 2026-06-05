import os
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, Playwright
from playwright_stealth import Stealth


class _WWBrowser:
    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self.debug_mode = os.getenv("WW_DEBUG") == "1"

        self._stealth_manager = Stealth().use_sync(sync_playwright())
        self._playwright: Playwright = self._stealth_manager.__enter__()

        self._browser: Browser = self._playwright.chromium.launch(headless=headless)
        self._context: BrowserContext = self._browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )

        if self.headless and self.debug_mode:
            self._context.tracing.start(snapshots=True, screenshots=True, sources=True)

    def _open(self, url: str) -> Page:
        page = self._context.new_page()
        page.set_extra_http_headers({"Referer": "https://www.google.com/"})
        page.goto(url, wait_until="domcontentloaded")
        return page

    def close(self) -> None:
        if self.headless and self.debug_mode:
            try:
                self._context.tracing.stop(path="headless_trace.zip")
            except Exception:
                pass

        self._context.close()
        self._browser.close()
        self._stealth_manager.__exit__(None, None, None)

    def __enter__(self):
        return self

    def __exit__(self, *_) -> None:
        self.close()
