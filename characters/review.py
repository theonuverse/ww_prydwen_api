from playwright.sync_api import Page


_TAB_SELECTOR = ".tabs .single-tab"
_TAB_INSIDE_SELECTOR = ".tab-inside .section-analysis"
_PROSCONS_SECTION_SELECTOR = f"{_TAB_INSIDE_SELECTOR}"
_REVIEW_SECTION_SELECTOR = f"{_TAB_INSIDE_SELECTOR} .review.raw"


class ReviewPoints:
    """Interface to interact with and scrape specific review points (e.g., Pros or Cons)."""

    def __init__(self, page: Page, box_selector: str) -> None:
        self._page = page
        self._box_selector = box_selector

    def get(self, index: int) -> str:
        """
        Retrieves a specific point by index (1-based).
        """
        box = self._page.locator(_PROSCONS_SECTION_SELECTOR).locator(self._box_selector)
        return box.locator(".raw.list li").nth(index - 1).inner_text()

    @property
    def all(self) -> dict[int, str]:
        """
        Retrieves all points in this section.
        """
        box = self._page.locator(_PROSCONS_SECTION_SELECTOR).locator(self._box_selector)
        return {i: item.inner_text() for i, item in enumerate(box.locator(".raw.list li").all(), 1)}


class Review:
    def __init__(self, page: Page) -> None:
        self._page = page
        self._page.locator(_TAB_SELECTOR).nth(1).click()

    @property
    def pros(self) -> ReviewPoints:
        """
        Retrieve pros.
        """
        return ReviewPoints(self._page, ".box.pros")

    @property
    def cons(self) -> ReviewPoints:
        """
        Retrieve cons.
        """
        return ReviewPoints(self._page, ".box.cons")

    @property
    def full_review(self) -> str:
        """
        Retrieves the full review.
        """
        return self._page.locator(_REVIEW_SECTION_SELECTOR).inner_text()
