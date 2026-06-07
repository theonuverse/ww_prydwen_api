from playwright.sync_api import Page

# Navigation
_MAIN_TAB_SELECTOR = ".tabs .single-tab"
_ACTIVE_TAB_SELECTOR = ".tab-inside.active:visible"

_SKILL_PRIORITY_BLOCK_SELECTOR = ".skill-priority"
_SKILL_SELECTOR = ".skill"


class BuildRole:
    """Handles fetching skills for a specific role block."""

    def __init__(self, page: Page, role_keyword: str) -> None:
        self._page = page
        self._role_keyword = role_keyword

    def get(self, index: int) -> str | None:
        """Get skill at index sorted by priority."""
        if index > 5 or index < 1:
            return None
            
        active_tab = self._page.locator(_ACTIVE_TAB_SELECTOR)
        
        target_block = active_tab.locator(f"h5:has-text('{self._role_keyword}') + {_SKILL_PRIORITY_BLOCK_SELECTOR}")
        
        if not target_block.is_visible():
            return None
            
        return target_block.locator(_SKILL_SELECTOR).nth(index - 1).inner_text().strip()

    @property
    def all(self) -> dict[int, str | None]:
        """Get all skills sorted by priority."""
        if not self.get(1):
            return {}
        return {i: self.get(i) for i in range(1, 6)}


class SkillPriority:
    """Container mapping properties to the BuildRole subclass."""
    def __init__(self, page: Page) -> None:
        self.dps = BuildRole(page, "DPS")
        self.hybrid = BuildRole(page, "Hybrid")
        self.support = BuildRole(page, "Support")


class Build:
    def __init__(self, page: Page) -> None:
        self._page = page
        self._page.locator(_MAIN_TAB_SELECTOR).nth(2).click()
        self.skill_priority = SkillPriority(self._page)
