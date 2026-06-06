from typing import Self
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, Playwright
from playwright_stealth import Stealth


class _WWBrowser:
    def __init__(self, headless: bool = True, trace: bool = False) -> None:
        self.headless = headless
        self.trace = trace
        self._stealth_ctx = Stealth().use_sync(sync_playwright())
        self._pw: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    def __enter__(self) -> Self:
        self._pw = self._stealth_ctx.__enter__()
        self._browser = self._pw.chromium.launch(headless=self.headless)
        self._context = self._browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        if self.trace:
            self._context.tracing.start(snapshots=True, screenshots=True, sources=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.trace and self._context:
            try:
                self._context.tracing.stop(path="trace.zip")
            except Exception:
                pass
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        self._stealth_ctx.__exit__(exc_type, exc_val, exc_tb)

    def _open(self, url: str) -> Page:
        assert self._context is not None, "_WWBrowser must be used as a context manager"
        page = self._context.new_page()
        page.set_extra_http_headers({"Referer": "https://www.google.com/"})
        page.goto(url, wait_until="load")
        return page
