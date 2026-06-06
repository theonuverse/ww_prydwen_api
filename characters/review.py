from playwright.sync_api import Page

# Navigation (top level: KIT, REVIEW, BUILD, ...)
_TAB_SELECTOR = ".tabs .single-tab"

# Tier list blocks (standard and value)
_TIER_LIST_SELECTOR = ".detailed-ratings.ww"

# Review tab content panel
_REVIEW_PANEL_SELECTOR = ".tab-inside.active:visible"

# ReviewPoints
_REVIEW_LIST_CSS = ".raw.list li"
_REVIEW_TEXT_CSS = ".review.raw"

# ModeRatings
_RATING_BOX_CONTAINER_CSS = ".rating-box-container"
_RATING_BOX_CSS = "div[class*='rating-box']"


class ModeRatings:
    """Provides tier ratings for a specific game mode (e.g., TOA, Whimpering Wastes)."""

    def __init__(self, page: Page, list_selector: str, role_name: str, list_index: int) -> None:
        """Initialize ModeRatings for a specific role and mode."""
        self._page = page
        self._list_selector = list_selector
        self._role_name = role_name
        self._list_index = list_index

    def _get_tier(self, container_index: int) -> str | None:
        """Extract tier text from a specific mode container."""
        target_blocks = self._page.locator(f"h5:has-text('{self._role_name}') + {self._list_selector}")
        if target_blocks.count() <= self._list_index:
            return None
        target_block = target_blocks.nth(self._list_index)
        container = target_block.locator(_RATING_BOX_CONTAINER_CSS).nth(container_index)
        if container.count() == 0:
            return None
        return container.locator(_RATING_BOX_CSS).inner_text()

    @property
    def toa(self) -> str | None:
        """Retrieve the character's Tower of Adversity tier rating."""
        return self._get_tier(0)

    @property
    def whiwa(self) -> str | None:
        """Retrieve the character's Whimpering Wastes tier rating."""
        return self._get_tier(1)


class RoleCategories:
    """Dispatches tier rating queries to the appropriate role category block."""

    def __init__(self, page: Page, list_selector: str, list_index: int) -> None:
        """Initialize RoleCategories for tier list access."""
        self.dps = ModeRatings(page, list_selector, "DPS", list_index)
        self.hybrid = ModeRatings(page, list_selector, "Hybrid", list_index)
        self.support = ModeRatings(page, list_selector, "Support", list_index)


class Ratings:
    """Interface to access different tier list variations (standard vs value)."""

    def __init__(self, page: Page) -> None:
        """Initialize Ratings interface with both tier list variants."""
        self.tier_list = RoleCategories(page, _TIER_LIST_SELECTOR, list_index=0)
        self.value_tier_list = RoleCategories(page, _TIER_LIST_SELECTOR, list_index=1)


class ReviewPoints:
    """Interface to interact with specific review point sections (e.g., Pros or Cons)."""

    def __init__(self, page: Page, box_selector: str) -> None:
        """Initialize ReviewPoints for a specific review section."""
        self._page = page
        self._box_selector = box_selector

    def _panel(self):
        """Get the active review panel locator."""
        return self._page.locator(_REVIEW_PANEL_SELECTOR)

    def get(self, index: int) -> str:
        """Retrieve a specific review point by 1-based index."""
        box = self._panel().locator(self._box_selector)
        return box.locator(_REVIEW_LIST_CSS).nth(index - 1).inner_text()

    @property
    def all(self) -> dict[int, str]:
        """Retrieve all review points in this section as a 1-based dictionary."""
        box = self._panel().locator(self._box_selector)
        return {i: item.inner_text() for i, item in enumerate(box.locator(_REVIEW_LIST_CSS).all(), 1)}


class Review:
    """Primary interface for accessing character review and tier rating data."""

    def __init__(self, page: Page) -> None:
        """Initialize Review interface and navigate to the review tab."""
        self._page = page
        self._page.locator(_TAB_SELECTOR).nth(1).click()
        self.pros = ReviewPoints(page, ".box.pros")
        self.cons = ReviewPoints(page, ".box.cons")
        self.ratings = Ratings(page)

    @property
    def full_review(self) -> str:
        """Retrieve the complete written review text."""
        return self._page.locator(_REVIEW_PANEL_SELECTOR).locator(_REVIEW_TEXT_CSS).inner_text()
