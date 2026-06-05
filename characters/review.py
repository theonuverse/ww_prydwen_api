from playwright.sync_api import Page

_TAB_SELECTOR = ".tabs .single-tab"
_TIER_LIST_SELECTOR = ".detailed-ratings.ww"
_TAB_PROCON_REVIEW_SELECTOR = ".tab-inside.active .section-analysis"


class ModeRatings:
    """Scrapes the individual mode tier ratings for a designated role block."""

    def __init__(self, page: Page, list_selector: str, role_name: str, list_index: int) -> None:
        self._page = page
        self._list_selector = list_selector
        self._role_name = role_name
        self._list_index = list_index

    def _get_tier(self, container_index: int) -> str | None:
        """Extracts the inner tier text from the container at the specified index."""
        target_blocks = self._page.locator(f"h5:has-text('{self._role_name}') + {self._list_selector}")

        if target_blocks.count() <= self._list_index:
            return None

        target_block = target_blocks.nth(self._list_index)

        container = target_block.locator(".rating-box-container").nth(container_index)

        if container.count() == 0:
            return None

        return container.locator("div[class*='rating-box']").inner_text()

    @property
    def toa(self) -> str | None:
        """Retrieves the Tower of Adversity tier rating."""
        return self._get_tier(0)

    @property
    def whiwa(self) -> str | None:
        """Retrieves the Whimpering Wastes tier rating."""
        return self._get_tier(1)


class RoleCategories:
    """Dispatches mode rating queries to the corresponding role block position."""

    def __init__(self, page: Page, list_selector: str, list_index: int) -> None:
        self._page = page
        self._list_selector = list_selector
        self._list_index = list_index

    @property
    def dps(self) -> ModeRatings:
        """Accesses the ratings for the DPS role layout block."""
        return ModeRatings(self._page, self._list_selector, "DPS", self._list_index)

    @property
    def hybrid(self) -> ModeRatings:
        """Accesses the ratings for the Hybrid role layout block."""
        return ModeRatings(self._page, self._list_selector, "Hybrid", self._list_index)

    @property
    def support(self) -> ModeRatings:
        """Accesses the ratings for the Support role layout block."""
        return ModeRatings(self._page, self._list_selector, "Support", self._list_index)


class Ratings:
    """Interface to switch between the standard tier list and the value tier list."""

    def __init__(self, page: Page) -> None:
        self._page = page

    @property
    def tier_list(self) -> RoleCategories:
        """Accesses the standard character tier list category (1st occurrence)."""
        return RoleCategories(self._page, _TIER_LIST_SELECTOR, list_index=0)

    @property
    def value_tier_list(self) -> RoleCategories:
        """Accesses the pull value tier list category (2nd occurrence)."""
        return RoleCategories(self._page, _TIER_LIST_SELECTOR, list_index=1)


class ReviewPoints:
    """Interface to interact with and scrape specific review points (e.g., Pros or Cons)."""

    def __init__(self, page: Page, box_selector: str) -> None:
        self._page = page
        self._box_selector = box_selector

    def get(self, index: int) -> str:
        """Retrieves a specific point by index (1-based)."""
        box = self._page.locator(_TAB_PROCON_REVIEW_SELECTOR).locator(self._box_selector)
        return box.locator(".raw.list li").nth(index - 1).inner_text()

    @property
    def all(self) -> dict[int, str]:
        """Retrieves all points in this section."""
        box = self._page.locator(_TAB_PROCON_REVIEW_SELECTOR).locator(self._box_selector)
        return {i: item.inner_text() for i, item in enumerate(box.locator(".raw.list li").all(), 1)}


class Review:
    def __init__(self, page: Page) -> None:
        self._page = page
        self._page.locator(_TAB_SELECTOR).nth(1).click()

    @property
    def pros(self) -> ReviewPoints:
        """Retrieve pros."""
        return ReviewPoints(self._page, ".box.pros")

    @property
    def cons(self) -> ReviewPoints:
        """Retrieve cons."""
        return ReviewPoints(self._page, ".box.cons")

    @property
    def full_review(self) -> str:
        """Retrieves the full review."""
        return self._page.locator(f"{_TAB_PROCON_REVIEW_SELECTOR} .review.raw").inner_text()

    @property
    def ratings(self) -> Ratings:
        """Access the character's tier list ratings across roles and modes."""
        return Ratings(self._page)
