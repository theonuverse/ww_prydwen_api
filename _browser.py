from playwright.sync_api import sync_playwright, Page, Browser, Playwright


class _WWBrowser:
    def __init__(self, headless: bool = True) -> None:
        self._playwright: Playwright = sync_playwright().start()
        self._browser: Browser = self._playwright.chromium.launch(headless=headless)

    def _open(self, url: str) -> Page:
        page = self._browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        return page

    def close(self) -> None:
        self._browser.close()
        self._playwright.stop()

    def __enter__(self):
        return self

    def __exit__(self, *_) -> None:
        self.close()
